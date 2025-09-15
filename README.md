# 🏥 Appointment Chatbot

An AI-powered appointment booking chatbot that: - Interacts with users
through a web-based chat UI - Collects appointment details
step-by-step - Sends a confirmation email - Saves all confirmed
appointments to a single Excel file

------------------------------------------------------------------------

## 📂 Project Structure

    .
    ├── index.html          # Frontend UI
    ├── style.css           # Chatbot styling
    ├── api.js              # Frontend logic (speech-to-text, text-to-speech, API calls)
    ├── bot.py              # FastAPI backend (OpenAI + Email + Excel storage)
    ├── .env                # Environment variables (email & OpenAI keys)
    └── LOCAL_FILE_SETUP.md # Details of single Excel file storage

> **Note:** `api.js` should be placed alongside `index.html` and
> `style.css`.

------------------------------------------------------------------------

## 🚀 Features

-   **Conversational Flow:** Guides patients to provide Name,
    Department, Doctor, Date, Time, Email, and Mobile.
-   **Email Confirmation:** Sends appointment details to the patient's
    email via Gmail.
-   **Excel Storage:** Automatically creates/updates a single Excel file
    (`appointments_data/appointments.xlsx`) with all appointments.
-   **Speech Support (Future):** Planned support for multi-language
    Text-to-Speech (TTS) and Speech-to-Text (STT).

------------------------------------------------------------------------

## 🛠️ Setup Instructions

### 1️⃣ Clone the Repository

``` bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

### 2️⃣ Install Python Dependencies

Create a virtual environment and install packages:

``` bash
python3 -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Required packages include: - `fastapi` - `uvicorn` - `python-dotenv` -
`pandas` - `openpyxl` - `openai`

### 3️⃣ Environment Variables

Create a **.env** file in the project root with:

    GMAIL_ADDRESS=your_gmail_address
    GMAIL_APP_PASSWORD=your_gmail_app_password
    OPENAI_API_KEY=your_openai_api_key

See the example provided in the included `.env` file (remove any real
credentials before committing!).

------------------------------------------------------------------------

### 4️⃣ Gmail App Password Setup

To allow the bot to send confirmation emails:

1.  Enable **2-Step Verification** for your Gmail account.\
2.  Go to **Google Account → Security → App Passwords**.\
3.  Create an App Password (select `Mail` as the app, `Other` as
    device).\
4.  Use the generated password as `GMAIL_APP_PASSWORD` in `.env`.

------------------------------------------------------------------------

### 5️⃣ OpenAI API Key

-   Obtain an API key from
    [OpenAI](https://platform.openai.com/account/api-keys).
-   Add it to your `.env` file as `OPENAI_API_KEY`.

------------------------------------------------------------------------

### 6️⃣ Backend (FastAPI)

Run the backend server:

``` bash
uvicorn bot:app --reload
```

This starts the API at: `http://127.0.0.1:8000`

------------------------------------------------------------------------

### 7️⃣ Frontend

-   Open `index.html` in your browser (or serve it using a static
    server).
-   Ensure `api.js` points to the correct backend URL
    (`http://127.0.0.1:8000/chat`).

------------------------------------------------------------------------

## 🔑 How It Works

-   **Frontend**
    -   `index.html` builds the chat interface.\
    -   `api.js` (to be included) manages user input, microphone access,
        TTS/STT, and communicates with the backend.
-   **Backend**
    -   `bot.py` handles conversations with OpenAI GPT, extracts
        appointment details, sends email confirmations, and appends
        appointment data to `appointments_data/appointments.xlsx`.\
    -   Details of the single-file Excel storage are described in
        [LOCAL_FILE_SETUP.md](LOCAL_FILE_SETUP.md).

------------------------------------------------------------------------

## 🧩 Future Enhancements

-   🌐 **Multi-Language Support:** Text-to-Speech & Speech-to-Text in
    various languages.
-   🖥️ **UI Improvements:** Better mobile responsiveness and voice
    commands.

------------------------------------------------------------------------

## ⚠️ Security Notes

-   **Never commit your `.env` file** with real credentials.
-   Use environment variables or secret managers for production
    deployment.

------------------------------------------------------------------------

## 🏃‍♂️ Quick Start

``` bash
# 1. Install dependencies & set .env
pip install -r requirements.txt

# 2. Start FastAPI backend
uvicorn bot:app --reload

# 3. Open index.html in browser
```

------------------------------------------------------------------------

## 📜 License

This project is licensed under the MIT License.
