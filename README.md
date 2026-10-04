# Hospital Appointment and Patient Tracking System

A Python learning project by Ela Turhan, built with Streamlit, SQLite and pandas.

## Features

- View appointments, prescriptions, doctors and patients in a dashboard.
- Create appointments for existing patients and doctors.
- Update patient age and phone number.
- Delete scheduled appointments and their related prescriptions.
- Explore relational tables, SQL joins and parameterized queries.

## Run locally

Install Python, then run these commands from the project folder:

```sh
python -m venv .venv
```

Activate the environment on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```sh
source .venv/bin/activate
```

Install dependencies and start the application:

```sh
python -m pip install -r requirements.txt
python -m streamlit run ElaTurhan_Code.py
```

The application creates `hospital.db` and seeds sample records on first launch. The local database is excluded from version control.

## Scope

This is an educational prototype, not a production hospital system. It does not implement user authentication or appointment conflict checking. Use sample data only.
