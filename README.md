# Idea Portal 🎓

A centralized web application to manage and handle innovation, research, and idea management for Cummins College of Engineering for Women, Pune.

This platform helps faculty and students track research projects, publications, IPRs/patents, and startups while enabling administration to continuously monitor institutional progress and automatically generate accreditation reports (like NBA/NAAC).

## Features

- **Role-Based Dashboards**: Tailored views for Admins, Faculty, and Students.
- **Project Management**: Faculty can propose projects, add team members, track funding, publications, and patents.
- **Asynchronous Task Queues**: Built with Celery and Redis to handle heavy lifting in the background without slowing down the UI.
- **Automated Notifications**: Email alerts for project approvals, pending registrations, and student join requests.
- **Periodic Reminders**: Weekly automated reminders asking faculty and students to keep their profiles up to date.
- **Automated Report Generation**: Monthly (or on-demand) PDF and CSV generation for institutional accreditation metrics via Celery and WeasyPrint.

## Tech Stack

- **Backend**: Python, Flask, Flask-SQLAlchemy (SQLite)
- **Frontend**: HTML5, Vanilla CSS, Jinja2 Templates
- **Task Queue / Broker**: Celery, Redis
- **Email**: Flask-Mail (SMTP wrapper)
- **PDF Generation**: WeasyPrint

## Project Structure

The project code is split into two logical areas:

```
idea_portal/
├── backend/
│   ├── app.py                # Main Flask application and Celery initialization
│   ├── config.py             # App configuration linking to .env
│   ├── celery_app.py         # CLI shim for Celery Workers
│   ├── celery_beat_schedule.py # Cron schedule for weekly/monthly automations
│   ├── requirements.txt      # Python dependencies
│   ├── tasks/                # Celery background tasks (mail, reports)
│   ├── admin/                # Admin routes
│   ├── auth/                 # Authentication routes and decorators
│   ├── faculty/              # Faculty routes
│   ├── student/              # Student routes
│   ├── ipr/                  # IPR, Publication, Startup modules
│   ├── database/             # SQLAlchemy Models and connection
│   └── accreditation/        # Logic to aggregate metrics
│
├── frontend/
│   └── templates/            # Jinja HTML templates (admin, auth, faculty, etc.)
│
└── .env.example              # Template for environment variables (needs to be copied to backend/.env)
```

## Setup Instructions

### 1. Prerequisites
- **Python 3.10+**
- **Redis Server** (Must be installed and running on your system, usually on `localhost:6379`)
  - Ubuntu/Debian: `sudo apt install redis-server`
  - macOS: `brew install redis`

### 2. Prepare Environment
Navigate to the `backend/` directory, which is the root for all application logic.

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Environment Variables
Copy the `.env.example` file to create your local `.env`.
```bash
cp .env.example .env
```
Open `backend/.env` and fill in your real credentials, particularly your SMTP properties for emails to work correctly:
- `SECRET_KEY`
- `MAIL_USERNAME`
- `MAIL_PASSWORD` (App password if using Gmail)

### 4. Running the Application locally

To have all features working, you need to run **three separate processes**. Open three terminal tabs, activate your virtual environment in each, and run:

**Tab 1: The Web Server**
```bash
cd backend
python3 app.py
```
*The app will run at `http://localhost:8000`.*

**Tab 2: The Celery Worker (Task Executor)**
```bash
cd backend
celery -A celery_app worker --loglevel=info
```
*This picks up tasks like sending emails and generating PDFs in the background.*

**Tab 3: The Celery Beat (Scheduler)**
```bash
cd backend
celery -A celery_app beat --loglevel=info
```
*This triggers the recurring tasks defined in `celery_beat_schedule.py` (weekly reminders, monthly reports).*

---
© Cummins College of Engineering for Women, Pune
