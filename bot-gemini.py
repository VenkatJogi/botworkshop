import os
import smtplib
import json
import csv
import pandas as pd
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# ✅ Gmail credentials (from .env)
FROM_EMAIL = os.getenv("GMAIL_ADDRESS")
APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

# ✅ Gemini client
client = genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ✅ Local file configuration
APPOINTMENTS_FOLDER = "appointments_data"  # Local folder for storing appointment files

app = FastAPI()

# Enable CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Initial context
initial_context = [
    {
        "role": "system",
        "content": """
        You are AppointmentBot, an automated service to issue hospital appointments.
        Ask the patient step by step for:
        - Full Name
        - Department
        - Preferred Doctor
        - Date
        - Time
        - Email
        - Mobile number
        
        IMPORTANT: When collecting information, be explicit about what you're asking for.
        For example:
        - "What is your full name?"
        - "Which department do you need? (e.g., Cardiology, Neurology, Orthopedics)"
        - "Which doctor would you prefer?"
        - "What date would you like for your appointment?"
        - "What time works best for you?"
        - "What is your email address?"
        - "What is your mobile number?"
        
        Once all details are collected, provide a clear summary like:
        "Thank you for providing all the necessary details. Here is the summary of your appointment:
        - Full Name: [name]
        - Department: [department]
        - Preferred Doctor: [doctor]
        - Date: [date]
        - Time: [time]
        - Email: [email]
        - Mobile number: [mobile]
        
        Do you want to confirm this appointment?"
        
        If the patient says "confirm", the system will send them an email and save the data.
        Respond conversationally, one question at a time.
        """
    }
]

# Store conversation + extracted details
global_context = initial_context.copy()
appointment_data = {}  # {name, dept, doctor, date, time, email, mobile}


# === Email Function ===
def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(FROM_EMAIL, APP_PASSWORD)
        server.sendmail(FROM_EMAIL, to_email, msg.as_string())

    return True


# === Local File Functions ===
def ensure_appointments_folder():
    """Create appointments folder if it doesn't exist"""
    if not os.path.exists(APPOINTMENTS_FOLDER):
        os.makedirs(APPOINTMENTS_FOLDER)
        print(f"✅ Created folder: {APPOINTMENTS_FOLDER}")


def save_to_excel(appointment_data):
    """Save appointment data to single Excel file, appending new rows"""
    try:
        ensure_appointments_folder()
        
        # Prepare data
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create data dictionary for new appointment
        new_appointment = {
            "Timestamp": timestamp,
            "Name": appointment_data.get("name", ""),
            "Department": appointment_data.get("department", ""),
            "Doctor": appointment_data.get("doctor", ""),
            "Date": appointment_data.get("date", ""),
            "Time": appointment_data.get("time", ""),
            "Email": appointment_data.get("email", ""),
            "Mobile": appointment_data.get("mobile", "")
        }
        
        # Single Excel file path
        excel_file = os.path.join(APPOINTMENTS_FOLDER, "appointments.xlsx")
        
        # Check if file exists
        if os.path.exists(excel_file):
            # Read existing data
            existing_df = pd.read_excel(excel_file, engine='openpyxl')
            # Append new appointment
            new_df = pd.DataFrame([new_appointment])
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            # Create new file with first appointment
            combined_df = pd.DataFrame([new_appointment])
        
        # Save to Excel file
        combined_df.to_excel(excel_file, index=False, engine='openpyxl')
        print(f"✅ Appointment saved to: {excel_file}")
        return True
        
    except Exception as e:
        print(f"❌ File save error: {e}")
        return False


# === Chat Function ===
def get_completion_from_messages(messages, model="gemini-1.5-flash", temperature=0):
    # Convert OpenAI format to Gemini format
    prompt = ""
    for message in messages:
        if message["role"] == "system":
            prompt += f"System: {message['content']}\n\n"
        elif message["role"] == "user":
            prompt += f"User: {message['content']}\n\n"
        elif message["role"] == "assistant":
            prompt += f"Assistant: {message['content']}\n\n"
    
    # Generate response using Gemini
    model_instance = genai.GenerativeModel(model)
    response = model_instance.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=temperature,
        )
    )
    return response.text


@app.post("/chat")
async def chat(input: str = Form(...), newchat: str = Form(default="no")):
    global global_context, appointment_data

    # Reset chat if requested
    if newchat.lower() == "yes":
        global_context = initial_context.copy()
        appointment_data = {}

    # Append user input
    global_context.append({"role": "user", "content": input})

    # Extract details from user input using AI
    lowered = input.lower()
    
    # Use AI to extract appointment details from the conversation
    extraction_prompt = f"""
    From the following conversation, extract appointment details if any are mentioned:
    
    User input: "{input}"
    
    Previous conversation context: {global_context[-3:] if len(global_context) > 3 else global_context}
    
    Extract and return ONLY the following details if found (return empty string if not found):
    - Name: [full name]
    - Department: [department name]
    - Doctor: [doctor name]
    - Date: [appointment date]
    - Time: [appointment time]
    - Email: [email address]
    - Mobile: [mobile number]
    
    Format as: Name: [value] or Name: (empty if not found)
    """
    
    try:
        extraction_response = get_completion_from_messages([
            {"role": "system", "content": "You are a data extraction assistant. Extract appointment details from conversations."},
            {"role": "user", "content": extraction_prompt}
        ])
        
        # Parse the extraction response
        lines = extraction_response.strip().split('\n')
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                if value and value != '(empty if not found)' and value != '(empty)':
                    if key == 'name':
                        appointment_data["name"] = value
                    elif key == 'department':
                        appointment_data["department"] = value
                    elif key == 'doctor':
                        appointment_data["doctor"] = value
                    elif key == 'date':
                        appointment_data["date"] = value
                    elif key == 'time':
                        appointment_data["time"] = value
                    elif key == 'email':
                        appointment_data["email"] = value
                    elif key == 'mobile':
                        appointment_data["mobile"] = value
    except Exception as e:
        print(f"❌ Data extraction error: {e}")
        # Fallback to simple keyword-based extraction
        if "@" in input and "." in input:
            appointment_data["email"] = input.strip()
        elif lowered.isdigit() and len(lowered) >= 10:
            appointment_data["mobile"] = input.strip()
        elif "department" in lowered or "cardiology" in lowered or "orthopedics" in lowered:
            appointment_data["department"] = input.strip()
        elif "dr" in lowered or "doctor" in lowered:
            appointment_data["doctor"] = input.strip()
        elif any(word in lowered for word in ["am", "pm", ":", "morning", "evening"]):
            appointment_data["time"] = input.strip()
        elif any(char.isdigit() for char in lowered) and "/" in lowered:
            appointment_data["date"] = input.strip()
        elif "name" in lowered or len(input.split()) >= 2:
            appointment_data.setdefault("name", input.strip())

    # Get bot response
    response = get_completion_from_messages(global_context)

    # Append assistant response
    global_context.append({"role": "assistant", "content": response})

    # Debug: Print extracted data
    print(f"🔍 Extracted appointment data: {appointment_data}")
    
    # ✅ If patient confirms appointment
    if "confirm" in lowered:
        # Try to extract data from the summary if appointment_data is incomplete
        if len(appointment_data) < 5:  # If we don't have most of the data
            summary_extraction_prompt = f"""
            Extract appointment details from this summary:
            
            {response}
            
            Extract and return ONLY the following details:
            - Name: [full name]
            - Department: [department name]
            - Doctor: [doctor name]
            - Date: [appointment date]
            - Time: [appointment time]
            - Email: [email address]
            - Mobile: [mobile number]
            
            Format as: Name: [value]
            """
            
            try:
                summary_response = get_completion_from_messages([
                    {"role": "system", "content": "You are a data extraction assistant. Extract appointment details from summaries."},
                    {"role": "user", "content": summary_extraction_prompt}
                ])
                
                # Parse the summary extraction response
                lines = summary_response.strip().split('\n')
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().lower()
                        value = value.strip()
                        if value and value != '(empty if not found)' and value != '(empty)':
                            if key == 'name':
                                appointment_data["name"] = value
                            elif key == 'department':
                                appointment_data["department"] = value
                            elif key == 'doctor':
                                appointment_data["doctor"] = value
                            elif key == 'date':
                                appointment_data["date"] = value
                            elif key == 'time':
                                appointment_data["time"] = value
                            elif key == 'email':
                                appointment_data["email"] = value
                            elif key == 'mobile':
                                appointment_data["mobile"] = value
            except Exception as e:
                print(f"❌ Summary extraction error: {e}")
        
        print(f"🔍 Final appointment data before saving: {appointment_data}")
        
        if "email" in appointment_data:
            details = "\n".join([f"{k.capitalize()}: {v}" for k, v in appointment_data.items()])
            
            # Send email
            email_success = False
            try:
                send_email(
                    to_email=appointment_data["email"],
                    subject="Your Hospital Appointment Confirmation",
                    body = f"""Dear {appointment_data.get('name','Patient')},
                    Your appointment has been confirmed with the following details:

                    Doctor: {appointment_data.get('doctor','N/A').title()}
                    Email: {appointment_data.get('email','N/A')}
                    Mobile: {appointment_data.get('mobile','N/A')}
                    Time: {appointment_data.get('time','N/A')}
                    Date: {appointment_data.get('date','N/A')}
                    Department: {appointment_data.get('department','N/A')}

                    Thank you for choosing our hospital.
                    """     
                )
                email_success = True
                response += "\n\n📧 A confirmation email has been sent."
            except Exception as e:
                print("❌ Email error:", e)
                response += "\n\n⚠️ Failed to send confirmation email."
            
            # Save to Excel file
            file_save_success = False
            try:
                file_save_success = save_to_excel(appointment_data)
                if file_save_success:
                    response += "\n\n💾 Appointment data has been saved to Excel file."
                else:
                    response += "\n\n⚠️ Failed to save data to Excel file."
            except Exception as e:
                print("❌ File save error:", e)
                response += "\n\n⚠️ Failed to save data to Excel file."
                
        else:
            response += "\n\n⚠️ No email address found. Please provide your email."

    return JSONResponse({"response": response, "context": global_context, "data": appointment_data})
