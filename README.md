# Placement Portal Application — V2

A full-stack campus placement management system built with Flask, Vue 3, Bootstrap, SQLite, Redis, and Celery.

## Features

### Admin
- Dashboard with student/company/drive counts
- Approve/reject company registrations and placement drives
- View all applications with search and filtering
- Reports with offer response breakdown and placement rate
- CSV export of all application data

### Company
- Register company profile (pending admin approval)
- Create placement drives with eligibility criteria
- View applicants per drive, shortlist and select students
- Manage offer status (Pending/Accepted/Declined)

### Student
- Register, login, and manage profile with resume upload
- Browse approved drives with eligibility filtering
- Apply to drives (with duplicate prevention and offer limit)
- Accept or decline offers (max 3 active pending offers)
- View application history and placement history
- Export application history as CSV

### Backend Jobs
- **Daily reminders** — email notifications for upcoming deadlines (Celery beat)
- **Monthly reports** — HTML report sent to admin on the 1st of each month
- **Async CSV export** — student-triggered batch job with download link

### Offer Management
- Company selects a student → offer status set to `Pending`
- Student accepts → all other pending offers auto-declined
- Student declines → offer status set to `Declined`
- Max active pending offers enforced (default: 3, configurable via `MAX_ACTIVE_OFFERS`)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Flask, SQLAlchemy, Flask-Login, Flask-Caching |
| Frontend | Vue 3 (Vite), Pinia, Bootstrap 5, Bootstrap Icons |
| Database | SQLite |
| Cache | Redis (with SafeRedisCache circuit breaker) |
| Task Queue | Celery + Redis broker |

## Prerequisites

- Python 3.10+
- Node.js 18+
- Redis server

## Setup

### 1. Clone and install dependencies

```bash
pip install -r requirements.txt
cd vite-frontend && npm install && cd ..
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your settings (defaults work for local dev)
```

### 3. Start Redis

```bash
redis-server
```

### 4. Start the Flask backend

```bash
python app.py
```

Backend runs at `http://localhost:5000`.

### 5. Start the Vue frontend

```bash
cd vite-frontend
npm run dev
```

Frontend runs at `http://localhost:5173` with API proxy to Flask.

### 6. Start Celery worker (for background jobs)

```bash
celery -A celery_worker.celery worker --loglevel=info
```

### 7. Start Celery beat (for scheduled tasks)

```bash
celery -A celery_worker.celery beat --loglevel=info
```

## Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@placement.local | admin123 |
| Student | rahul@student.com | Student123 |
| Company | hr@techcorp.com | Company123 |

## API Endpoints

### Auth
- `POST /api/auth/login` — Login
- `POST /api/auth/register/student` — Register student
- `POST /api/auth/register/company` — Register company
- `GET /api/auth/logout` — Logout

### Student
- `GET /api/student/dashboard` — Dashboard data
- `GET /api/student/drives` — Available drives
- `POST /api/student/drives/<id>/apply` — Apply to drive
- `GET /api/student/applications` — List applications
- `POST /api/student/applications/<id>/accept-offer` — Accept offer
- `POST /api/student/applications/<id>/decline-offer` — Decline offer
- `GET /api/student/placement-history` — Placement history
- `PUT /api/student/profile` — Update profile
- `PUT /api/student/resume` — Upload resume
- `POST /api/student/export/trigger` — Trigger CSV export
- `GET /api/student/export/status/<task_id>` — Check export status
- `GET /api/student/export/download/<task_id>` — Download CSV

### Company
- `GET /api/company/profile` — Company profile
- `PUT /api/company/profile` — Update profile
- `GET /api/company/dashboard` — Dashboard data
- `POST /api/company/drives` — Create drive
- `GET /api/company/drives` — List drives
- `GET /api/company/drives/<id>` — Drive detail
- `PUT /api/company/drives/<id>` — Update drive
- `POST /api/company/drives/<id>/close` — Close drive
- `GET /api/company/drives/<drive_id>/applicants` — List applicants
- `POST /api/company/application/<id>/shortlist` — Shortlist
- `POST /api/company/application/<id>/reject` — Reject
- `POST /api/company/application/<id>/select` — Select (offer)
- `POST /api/company/application/<id>/schedule-interview` — Schedule interview

### Admin
- `GET /api/admin/dashboard` — Dashboard
- `GET /api/admin/students` — List students
- `GET /api/admin/companies` — List companies
- `GET /api/admin/drives` — List drives
- `PUT /api/admin/companies/<id>/approve` — Approve company
- `PUT /api/admin/companies/<id>/reject` — Reject company
- `PUT /api/admin/companies/<id>/blacklist` — Blacklist company
- `PUT /api/admin/drives/<id>/approve` — Approve drive
- `PUT /api/admin/drives/<id>/reject` — Reject drive
- `GET /api/admin/applications` — All applications
- `GET /api/admin/reports/summary` — Reports summary
- `POST /api/admin/export/all` — Export all applications CSV

## Project Structure

```
├── app.py                  # Flask app factory and startup
├── config.py               # Configuration (Dev/Test/Prod)
├── constants.py            # Branch sets and migration maps
├── models.py               # SQLAlchemy models
├── celery_worker.py        # Celery app and beat schedule
├── routes/
│   ├── auth.py             # Login/register endpoints
│   ├── student.py          # Student API routes
│   ├── company.py          # Company API routes
│   ├── admin.py            # Admin API routes
│   └── jobs.py             # Async job status/download
├── services/
│   ├── export_service.py   # CSV export logic
│   └── report_service.py   # Monthly report generation
├── tasks/
│   ├── exports.py          # Celery export task
│   ├── reminders.py        # Daily reminder task
│   └── reports.py          # Monthly report task
├── utils/
│   ├── cache_utils.py      # SafeRedisCache and invalidation helpers
│   ├── validators.py       # Input validation and role decorators
│   └── email_utils.py      # Email sending utility
├── templates/              # Jinja2 HTML templates (monthly report)
├── uploads/resumes/        # Student resume uploads
├── static/exports/         # Generated CSV exports
├── vite-frontend/          # Vue 3 frontend
│   ├── src/
│   │   ├── api/            # Axios API modules
│   │   ├── components/     # Reusable Vue components
│   │   ├── views/          # Page-level views (student/company/admin)
│   │   ├── stores/         # Pinia stores
│   │   └── router/         # Vue Router config
│   └── package.json
├── requirements.txt
├── .env.example
└── README.md
```
