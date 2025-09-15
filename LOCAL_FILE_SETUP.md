# Single Excel File Storage Setup

## Overview
Your chatbot now saves all appointment data to a single Excel file that gets updated with new rows.

## Features

✅ **Single File**: Only one Excel file (`appointments.xlsx`) for all appointments
✅ **Auto-Update**: New appointments are added as new rows to existing file
✅ **Auto-Create**: File is created automatically if it doesn't exist
✅ **Automatic Folder Creation**: Creates `appointments_data` folder automatically
✅ **Email Integration**: Maintains existing email confirmation functionality

## File Structure

When appointments are confirmed, the system creates/updates:

```
appointments_data/
└── appointments.xlsx                    # Single Excel file with all appointments
```

## Data Fields

file contains the following columns:
- **Timestamp**: When the appointment was created
- **Name**: Patient's full name
- **Department**: Medical department
- **Doctor**: Preferred doctor
- **Date**: Appointment date
- **Time**: Appointment time
- **Email**: Patient's email address
- **Mobile**: Patient's mobile number

## How It Works

1. Patient confirms appointment
2. System sends confirmation email
3. System checks if `appointments.xlsx` exists:
   - **If file exists**: Reads existing data and adds new appointment as a new row
   - **If file doesn't exist**: Creates new file with the first appointment
4. Saves updated data to `appointments.xlsx`


## File Location

The appointment file is saved in: `./appointments_data/appointments.xlsx` (relative to your bot.py file)


