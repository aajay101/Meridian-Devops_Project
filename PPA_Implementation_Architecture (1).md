# Placement Portal Application — Complete Implementation Architecture
### Gap-Filling & Feature Completion Guide
**Project:** Placement Portal Application V2 (24BEDAS / App Dev II)**  
**Stack:** Flask · VueJS · Bootstrap · SQLite · Redis · Celery · Jinja2 (entry point only)  
**Purpose:** This document is the authoritative architecture reference for completing all pending features. It picks up exactly where the current codebase leaves off.

---

## Table of Contents

1. [Current State Summary](#1-current-state-summary)
2. [Target Final Folder Structure](#2-target-final-folder-structure)
3. [Environment & Dependency Setup](#3-environment--dependency-setup)
4. [Redis Setup](#4-redis-setup)
5. [Celery Setup & Configuration](#5-celery-setup--configuration)
6. [VueJS Frontend Architecture](#6-vuejs-frontend-architecture)
7. [Flask API Layer (JSON Endpoints)](#7-flask-api-layer-json-endpoints)
8. [Unified Auth Model (Session-Based Only)](#8-unified-auth-model-session-based-only)
9. [Backend Job 1 — Daily Deadline Reminders](#9-backend-job-1--daily-deadline-reminders)
10. [Backend Job 2 — Monthly Activity Report](#10-backend-job-2--monthly-activity-report)
11. [Backend Job 3 — Async CSV Export](#11-backend-job-3--async-csv-export)
12. [Caching Strategy](#12-caching-strategy)
13. [Eligibility Validation Fix](#13-eligibility-validation-fix)
14. [Student Drive Search](#14-student-drive-search)
15. [Company Reject Route Fix](#15-company-reject-route-fix)
16. [ChartJS Dashboard Analytics (OPTIONAL)](#16-chartjs-dashboard-analytics-optional)
17. [Optional Enhancements (Not Required For Marks)](#17-optional-enhancements-not-required-for-marks)
18. [Resume Upload in Profile](#18-resume-upload-in-profile)
19. [config.py — Full Updated Version](#19-configpy--full-updated-version)
20. [Updated requirements.txt](#20-updated-requirementstxt)
21. [Integration Checklist (Historical Planning Reference)](#21-integration-checklist-historical-planning-reference)
22. [.gitignore](#22-gitignore)
23. [Logging](#23-logging)
24. [Final PDF Compliance Amendment](#24-final-pdf-compliance-amendment)
25. [Complete Cache Invalidation Matrix](#25-complete-cache-invalidation-matrix)
26. [Avoid Unnecessary Refactoring](#26-avoid-unnecessary-refactoring)
27. [Corrected Final Priority Order](#27-corrected-final-priority-order)
28. [Architecture Status](#28-architecture-status)

---

## 1. Current State Summary

| Area | Status | Gap |
|---|---|---|
| Authentication | ✅ Flask-Login session | No unified user model |
| Admin features | ✅ Mostly complete | No explicit company reject route |
| Company features | ✅ Complete | — |
| Student features | ⚠️ Partial | No drive search, no profile resume upload |
| Eligibility validation | ⚠️ Partial | CGPA/branch not validated at apply time |
| Daily reminders | ❌ Missing | No Celery, no email/webhook |
| Monthly report | ❌ Missing | No scheduler, no email |
| CSV export | ❌ Missing | No async task, no download |
| Caching | ❌ Missing | No Redis cache, no flask-caching |
| VueJS frontend | ❌ Missing | All templates are Jinja2 only |
| ChartJS charts (OPTIONAL) | ❌ Missing | No chart rendering anywhere |
| PDF reports (OPTIONAL) | ❌ Missing | No PDF library |

---

## 2. Target Final Folder Structure

```
placement-portal/
│
├── app.py                          # Flask app (factory pattern RECOMMENDED for Celery — see Section 5.4)
├── config.py                       # All config classes
├── models.py                       # SQLAlchemy models
├── celery_worker.py                # Celery app entry point
├── requirements.txt
├── .env                            # Secrets (never commit)
│
├── routes/
│   ├── __init__.py
│   ├── auth_routes.py              # Login/register (existing)
│   ├── admin_routes.py             # Admin (existing + fixes)
│   ├── company_routes.py           # Company (existing)
│   ├── student_routes.py           # Student (existing + search + resume)
│   └── api/                        # ← NEW: JSON API for VueJS
│       ├── __init__.py
│       ├── auth_api.py             # login/register endpoints
│       ├── admin_api.py            # Admin JSON endpoints
│       ├── company_api.py          # Company JSON endpoints
│       ├── student_api.py          # Student JSON endpoints
│       └── jobs_api.py             # Trigger CSV export, check job status
│
├── tasks/                          # ← NEW: Celery tasks
│   ├── __init__.py
│   ├── reminders.py                # Daily deadline reminder task
│   ├── reports.py                  # Monthly report task
│   └── exports.py                  # CSV export async task
│
├── services/                       # ← RECOMMENDED code organization (OPTIONAL — see Section 24.4)
│   ├── __init__.py
│   ├── application_service.py      # Core application logic
│   ├── drive_service.py            # Drive-related services
│   ├── auth_service.py             # Authentication services
│   └── report_service.py           # Monthly report generation
│
├── utils/                          # ← NEW: Shared utilities
│   ├── __init__.py
│   ├── email_utils.py              # SMTP email helper
│   ├── pdf_utils.py                # WeasyPrint PDF generation (OPTIONAL — see Section 17)
│   ├── cache_utils.py              # Redis cache helpers
│   └── validators.py               # Eligibility validation logic
│
├── static/
│   ├── css/
│   │   └── style.css               # (existing)
│   ├── exports/                    # ← NEW: Generated CSV files land here
│   └── vue/                        # ← NEW: VueJS built assets
│       ├── dist/
│       │   ├── js/
│       │   └── css/
│
├── vite-frontend/                  # ← NEW: VueJS source (Vite + Vue 3)
│   ├── package.json
│   ├── vite.config.js              # ← Vite is the ONLY frontend build tool (no vue.config.js)
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── router/
│   │   │   └── index.js
│   │   ├── store/
│   │   │   └── index.js            # Pinia or Vuex store (OPTIONAL)
│   │   ├── api/
│   │   │   └── axios.js            # HTTP client (OPTIONAL — fetch API is sufficient)
│   │   ├── views/
│   │   │   ├── auth/
│   │   │   ├── admin/
│   │   │   ├── company/
│   │   │   └── student/
│   │   └── components/
│   │       └── charts/             # ChartJS components (OPTIONAL — see Section 16)
│
├── templates/
│   └── vue_app.html                # ← Single Jinja2 entry point for VueJS
│
└── uploads/
    └── applications/               # (existing)
```

> **Note on `services/`:** This directory is **recommended code organization only**, not required architecture. Existing route business logic may remain in routes. Service extraction is optional and should be performed only when code reuse becomes necessary (see Section 24.4).

---

## 3. Environment & Dependency Setup

### 3.1 Install system dependencies (Ubuntu/Debian)

```bash
# Redis server
sudo apt update
sudo apt install redis-server -y
sudo systemctl enable redis
sudo systemctl start redis

# WeasyPrint system dependencies (OPTIONAL — for PDF only, see Section 17)
sudo apt install python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0 -y

# Verify Redis
redis-cli ping   # Should return: PONG
```

### 3.2 Python dependencies

#### Core (required for submission)
```bash
pip install flask flask-login flask-sqlalchemy        # existing
pip install flask-caching redis                       # caching
pip install celery redis                               # task queue
```

#### Optional (only if needed)
```bash
pip install weasyprint                                # PDF report generation (OPTIONAL — see Section 17)
pip install flower                                    # Celery monitoring (OPTIONAL)
pip install python-dotenv                             # environment variables
```

#### Email (use built-in smtplib instead of flask-mail)
The project statement allows email for reminders/reports. Use Python's built-in `smtplib` and `email.message` modules instead of `flask-mail` to stay within the allowed framework list. **Do not install or use `flask-mail` anywhere in the project.**

#### CSV export (use built-in csv module)
The built-in Python `csv` module provides all required CSV export functionality. No additional library needed.

### 3.3 Node / VueJS (Vite) Setup

```bash
# Install Node (if not present)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Create Vite project inside the repo
npm create @vitejs/create-vue@latest vite-frontend
cd vite-frontend
npm install

# Core packages (required for Vue app)
npm install vue-router@4 bootstrap

# Optional packages (only if needed for specific features)
# npm install axios               # Use browser's fetch API instead (OPTIONAL)
# npm install pinia               # Use Vue 3 reactivity instead (OPTIONAL)
# npm install chart.js vue-chartjs # ChartJS is OPTIONAL per project statement (see Section 16)
```

> **Vite is the sole frontend build tool.** There is no `vue.config.js` and no Vue CLI. All build configuration lives in `vite.config.js` (see Section 6.2).

---

## 4. Redis Setup

Redis serves two purposes here: **Celery message broker** and **Flask-Caching backend**.

### 4.1 redis.conf (local dev — no password needed)

```bash
# /etc/redis/redis.conf — key settings to verify
bind 127.0.0.1
port 6379
maxmemory 256mb
maxmemory-policy allkeys-lru
```

### 4.2 Verify connection from Python

```python
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
r.ping()  # True
r.set('test', 'ok')
r.get('test')  # b'ok'
```

### 4.3 Two Redis databases (recommended)

Use separate logical databases to avoid key collisions:

| Purpose | Redis DB | URL |
|---|---|---|
| Celery broker | DB 0 | `redis://localhost:6379/0` |
| Flask-Caching | DB 1 | `redis://localhost:6379/1` |

---

## 5. Celery Setup & Configuration

### 5.1 celery_worker.py — entry point

Create this file at project root.

> **Factory pattern is optional (see Section 24.3).** The example below assumes you are using the factory pattern from Section 5.4. **If you are NOT using the factory pattern**, use the alternative snippet below this one — do not refactor `app.py` just to make Celery work.

#### Option A — With factory pattern (Section 5.4 implemented)

```python
# celery_worker.py
from app import create_app
from celery import Celery

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

flask_app = create_app()
celery = make_celery(flask_app)

# Import tasks so Celery discovers them
import tasks.reminders
import tasks.reports
import tasks.exports
```

#### Option B — Without factory pattern (existing module-level `app` in `app.py`)

Use this if your `app.py` already exposes a module-level `app = Flask(__name__)`. **No refactor required.**

```python
# celery_worker.py
from app import app as flask_app
from celery import Celery

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

celery = make_celery(flask_app)

# Import tasks so Celery discovers them
import tasks.reminders
import tasks.reports
import tasks.exports
```

> **Note:** Both options are fully supported. Pick ONE based on whether your `app.py` exposes `create_app()` (Option A) or a module-level `app` (Option B). Do not mix the two.

### 5.2 config.py additions for Celery

> **Note on Celery config key naming:** The uppercase keys (`CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`, `CELERY_TIMEZONE`, `CELERYBEAT_SCHEDULE`) work because `celery.conf.update(app.config)` in `celery_worker.py` copies them straight into Celery's config namespace, and Celery accepts uppercase keys for backwards compatibility. Modern Celery (5.x) prefers the lowercase forms (`broker_url`, `result_backend`, `timezone`, `beat_schedule`). Both forms work with the code in this document; nothing here will fail. If you start a brand-new project, prefer the lowercase forms. Do not mix uppercase and lowercase for the same setting.

```python
# Add to Config class in config.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Celery Beat schedule (periodic tasks)
from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'daily-deadline-reminders': {
        'task': 'tasks.reminders.send_deadline_reminders',
        'schedule': crontab(hour=8, minute=0),   # Runs every day at 8:00 AM
    },
    'monthly-activity-report': {
        'task': 'tasks.reports.send_monthly_report',
        'schedule': crontab(day_of_month=1, hour=7, minute=0),  # 1st of month, 7 AM
    },
}
CELERY_TIMEZONE = 'Asia/Kolkata'
```

### 5.3 Running Celery

```bash
# Terminal 1 — Celery worker
celery -A celery_worker.celery worker --loglevel=info

# Terminal 2 — Celery beat scheduler (periodic tasks)
celery -A celery_worker.celery beat --loglevel=info

# Terminal 3 — Flower monitoring dashboard (OPTIONAL — not required for submission)
celery -A celery_worker.celery flower --port=5555
# Visit: http://localhost:5555
```

### 5.4 app.py — Factory Pattern (RECOMMENDED, Not Mandatory)

> **Compliance Note:** The project statement does **not** require a Flask factory pattern. The factory pattern is **recommended only if required for Celery integration, testing, or blueprint organization**. If you are not using Celery or do not need the factory pattern, the existing module-level app may work with minor adjustments. The example below is a **recommended implementation strategy**, not a project requirement.

**Recommended factory pattern for Celery support:**

```python
# app.py
from flask import Flask, send_from_directory, render_template
from flask_login import LoginManager
from config import Config
from models import db
import os

login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login_student"
    login_manager.login_message_category = "info"

    # Initialize Flask-Caching
    from utils.cache_utils import cache
    cache.init_app(app)

    with app.app_context():
        from models import Student, Company, Admin, PlacementDrive, Application, ApplicationStatusLog
        db.create_all()
        _seed_admin()

    # Register Jinja2 blueprints (existing)
    from routes.auth_routes import auth_bp
    from routes.admin_routes import admin_bp
    from routes.company_routes import company_bp
    from routes.student_routes import student_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(company_bp, url_prefix='/company')
    app.register_blueprint(student_bp, url_prefix='/student')

    # Register JSON API blueprints (new)
    from routes.api.auth_api import auth_api_bp
    from routes.api.admin_api import admin_api_bp
    from routes.api.company_api import company_api_bp
    from routes.api.student_api import student_api_bp
    from routes.api.jobs_api import jobs_api_bp
    app.register_blueprint(auth_api_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_api_bp, url_prefix='/api/admin')
    app.register_blueprint(company_api_bp, url_prefix='/api/company')
    app.register_blueprint(student_api_bp, url_prefix='/api/student')
    app.register_blueprint(jobs_api_bp, url_prefix='/api/jobs')

    @login_manager.user_loader
    def load_user(user_id):
        from models import Student, Company, Admin
        return (Student.query.get(int(user_id)) or
                Company.query.get(int(user_id)) or
                Admin.query.get(int(user_id)))

    @app.route('/uploads/applications/<path:filename>')
    def uploaded_application_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # Serve VueJS SPA entry point
    @app.route('/app')
    @app.route('/app/<path:path>')
    def vue_app(path=None):
        return render_template('vue_app.html')

    return app

def _seed_admin():
    from models import Admin
    if not Admin.query.filter_by(username='admin').first():
        admin = Admin(username='admin', email='admin@placement.edu')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
```

> **Note:** The factory pattern enables Celery workers to create their own app context. Without it, you must ensure the Celery worker can access the Flask app context correctly. **This is a recommended implementation strategy, not a PDF requirement.**

---

## 6. VueJS Frontend Architecture

> **Requirement from PDF:** VueJS for UI · Bootstrap for styling · Jinja2 only for entry point

The strategy is: Flask serves a single Jinja2 entry point (`vue_app.html`) for the VueJS application, and VueJS becomes the primary UI layer. Existing Jinja2 templates remain as transitional fallback during development but are not intended for final submission. The Vue frontend is mounted at `/app/*` and consumes the Flask JSON API layer.

### 6.1 vue_app.html — Jinja2 entry point for Vue

```html
<!-- templates/vue_app.html -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Placement Portal</title>
  <!-- Bootstrap CDN -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
  <!-- Vue built CSS -->
  <link rel="stylesheet" href="{{ url_for('static', filename='vue/dist/assets/index.css') }}">
</head>
<body>
  <div id="app"></div>
  <!-- Vue built JS -->
  <script src="{{ url_for('static', filename='vue/dist/assets/index.js') }}"></script>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

### 6.2 vite.config.js — Output to Flask Static Folder

```javascript
// vite-frontend/vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  build: {
    outDir: '../static/vue/dist',
    assetsDir: 'assets'
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
})
```

> **Note:** This project uses **Vite** as the sole frontend build tool. There is **no `vue.config.js`** and no Vue CLI. All build configuration is in `vite.config.js`. The Vite dev server proxy (`/api` → Flask) allows the browser session cookie to propagate naturally — **no JWT or token mechanism is required** for the Vue API layer.

### 6.3 vite-frontend/src/api/axios.js — HTTP client (OPTIONAL)

> This file is optional. Vue 3 can use the browser's built-in `fetch` API directly. Use Axios only if you prefer its interceptor ergonomics.

```javascript
// vite-frontend/src/api/axios.js
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' }
})

export default api
```

### 6.4 vite-frontend/src/router/index.js

```javascript
// vite-frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/app/login',    component: () => import('@/views/auth/LoginView.vue') },
  { path: '/app/register', component: () => import('@/views/auth/RegisterView.vue') },

  // Admin routes — guarded
  { path: '/app/admin/dashboard',   component: () => import('@/views/admin/AdminDashboard.vue'),   meta: { role: 'admin' } },
  { path: '/app/admin/companies',   component: () => import('@/views/admin/ManageCompanies.vue'),  meta: { role: 'admin' } },
  { path: '/app/admin/students',    component: () => import('@/views/admin/ManageStudents.vue'),   meta: { role: 'admin' } },
  { path: '/app/admin/drives',      component: () => import('@/views/admin/ManageDrives.vue'),     meta: { role: 'admin' } },
  { path: '/app/admin/applications',component: () => import('@/views/admin/AllApplications.vue'), meta: { role: 'admin' } },

  // Company routes
  { path: '/app/company/dashboard', component: () => import('@/views/company/CompanyDashboard.vue'), meta: { role: 'company' } },
  { path: '/app/company/create',    component: () => import('@/views/company/CreateDrive.vue'),      meta: { role: 'company' } },
  { path: '/app/company/drives/:id/applicants', component: () => import('@/views/company/Applicants.vue'), meta: { role: 'company' } },

  // Student routes
  { path: '/app/student/dashboard',    component: () => import('@/views/student/StudentDashboard.vue'), meta: { role: 'student' } },
  { path: '/app/student/drives',       component: () => import('@/views/student/AvailableDrives.vue'),  meta: { role: 'student' } },
  { path: '/app/student/applications', component: () => import('@/views/student/ApplicationHistory.vue'), meta: { role: 'student' } },
  { path: '/app/student/history',      component: () => import('@/views/student/PlacementHistory.vue'), meta: { role: 'student' } },
  { path: '/app/student/profile',      component: () => import('@/views/student/Profile.vue'),           meta: { role: 'student' } },

  { path: '/:pathMatch(.*)*', redirect: '/app/login' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
```

### 6.5 Example Vue component — StudentDashboard.vue

```vue
<!-- vite-frontend/src/views/student/StudentDashboard.vue -->
<template>
  <div class="student-dashboard">
    <Navbar />
    <div class="container mt-4">
      <h2 class="dashboard-title">Student Dashboard</h2>
      <p class="welcome-text">Welcome, <strong>{{ user.name }}</strong>!</p>

      <!-- Stat Cards -->
      <div class="stats-grid">
        <StatCard label="Total Applications" :value="stats.total"    color="primary" icon="bi-file-earmark-text" />
        <StatCard label="Selected"           :value="stats.selected" color="success" icon="bi-check-circle-fill" />
        <StatCard label="Accepted"           :value="stats.accepted" color="info"    icon="bi-check2-all" />
        <StatCard label="Rejected"           :value="stats.rejected" color="danger"  icon="bi-x-circle-fill" />
        <StatCard label="Selection Rate"     :value="stats.rate+'%'" color="purple"  icon="bi-percent" />
        <StatCard label="Available Drives"   :value="stats.drives"   color="warning" icon="bi-briefcase-fill" />
      </div>

      <!-- ChartJS Bar Chart (OPTIONAL — see Section 16) -->
      <div class="chart-container mt-4" v-if="chartData">
        <ApplicationPieChart :data="chartData" />
      </div>

      <!-- Export CSV Button -->
      <div class="mt-3">
        <button class="btn btn-outline-primary" @click="triggerCSVExport" :disabled="exportLoading">
          <span v-if="exportLoading"><i class="bi bi-hourglass-split"></i> Exporting...</span>
          <span v-else><i class="bi bi-download"></i> Export My Applications as CSV</span>
        </button>
        <div v-if="exportReady" class="mt-2">
          <a :href="exportUrl" class="btn btn-success btn-sm" download>
            <i class="bi bi-file-earmark-spreadsheet"></i> Download CSV
          </a>
        </div>
      </div>

      <!-- Recent Applications Table -->
      <div class="mt-4" v-if="recentApps.length">
        <div class="section-header">
          <h3 class="section-title">Recent Applications</h3>
          <router-link to="/app/student/applications" class="view-all-btn">View All</router-link>
        </div>
        <DriveTable :applications="recentApps" />
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/api/axios'
import Navbar from '@/components/Navbar.vue'
import StatCard from '@/components/StatCard.vue'
import DriveTable from '@/components/DriveTable.vue'
// ChartJS component is OPTIONAL — remove import if not implementing charts (see Section 16)
import ApplicationPieChart from '@/components/charts/ApplicationPieChart.vue'

export default {
  name: 'StudentDashboard',
  components: { Navbar, StatCard, DriveTable, ApplicationPieChart },
  data() {
    return {
      user: {},
      stats: { total: 0, selected: 0, accepted: 0, rejected: 0, rate: 0, drives: 0 },
      recentApps: [],
      chartData: null,
      exportLoading: false,
      exportReady: false,
      exportUrl: '',
      jobId: null
    }
  },
  async mounted() {
    const res = await api.get('/student/dashboard')
    this.user = res.data.user
    this.stats = res.data.stats
    this.recentApps = res.data.recent_applications
    // Chart data is OPTIONAL — remove this block if not implementing ChartJS (see Section 16)
    this.chartData = {
      labels: ['Applied', 'Shortlisted', 'Selected', 'Accepted', 'Rejected'],
      datasets: [{
        data: [res.data.stats.applied, res.data.stats.shortlisted,
               res.data.stats.selected, res.data.stats.accepted, res.data.stats.rejected],
        backgroundColor: ['#6c757d','#0dcaf0','#198754','#0d6efd','#dc3545']
      }]
    }
  },
  methods: {
    async triggerCSVExport() {
      this.exportLoading = true
      this.exportReady = false
      const res = await api.post('/jobs/export-csv')
      this.jobId = res.data.job_id
      this.pollExportJob()
    },
    async pollExportJob() {
      const res = await api.get(`/jobs/status/${this.jobId}`)
      if (res.data.state === 'SUCCESS') {
        this.exportLoading = false
        this.exportReady = true
        this.exportUrl = res.data.result_url
      } else if (res.data.state === 'FAILURE') {
        this.exportLoading = false
        alert('Export failed. Please try again.')
      } else {
        setTimeout(() => this.pollExportJob(), 2000)  // Poll every 2 seconds
      }
    }
  }
}
</script>
```

### 6.6 ChartJS component (OPTIONAL)

> **This entire subsection is OPTIONAL.** ChartJS is listed under "Recommended and/or Optional functionalities" in the project statement. Skip this subsection if you are not implementing charts.

```vue
<!-- vite-frontend/src/components/charts/ApplicationPieChart.vue -->
<!-- OPTIONAL — only build this component if you are implementing ChartJS (see Section 16) -->
<template>
  <div class="chart-wrapper">
    <h5 class="section-title">Application Breakdown</h5>
    <Pie :data="data" :options="options" />
  </div>
</template>

<script>
import { Pie } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
ChartJS.register(ArcElement, Tooltip, Legend)

export default {
  name: 'ApplicationPieChart',
  components: { Pie },
  props: { data: Object },
  data() {
    return {
      options: {
        responsive: true,
        plugins: { legend: { position: 'bottom' } }
      }
    }
  }
}
</script>
```

---

## 7. Flask API Layer (JSON Endpoints)

These are new endpoints under `/api/*` that the VueJS frontend consumes via Axios or `fetch`.

> **Authentication for API layer (authoritative — see Section 24.1):** API routes use **Flask-Login sessions and `current_user`**, exactly the same mechanism as the Jinja2 routes. The Vue dev server proxies `/api` requests to Flask (see Section 6.2), so the browser session cookie propagates naturally and Flask-Login populates `current_user` on every API request.
>
> **Do NOT trust client-supplied headers** such as `X-User-ID`. A client can spoof any header value, which would let one student impersonate another. Instead:
> - Use `@login_required` on every protected API route (same decorator as Jinja2 routes).
> - Read the authenticated user from `from flask_login import current_user`.
> - Enforce role with `isinstance(current_user, Student)` / `Company` / `Admin` checks, or via a small `role_required` helper.
>
> The existing Flask-Login session authentication is fully compliant — no JWT or token mechanism is required. See Section 24.1 for the authoritative authentication rule.

### 7.1 routes/api/auth_api.py

> The login endpoint below performs credential verification and then calls `flask_login.login_user(user)` to establish the server-side session. After this, all subsequent `/api/*` requests carry the session cookie and `current_user` is populated automatically by Flask-Login — no token is issued, no `X-User-ID` header is read.

```python
# routes/api/auth_api.py
from flask import Blueprint, request, jsonify
from flask_login import login_user
from models import db, Student, Company, Admin

auth_api_bp = Blueprint('auth_api', __name__)

@auth_api_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    role = data.get('role', '')   # 'student' | 'company' | 'admin'

    user = None
    if role == 'student':
        user = Student.query.filter_by(email=email).first()
    elif role == 'company':
        user = Company.query.filter_by(email=email).first()
    elif role == 'admin':
        user = Admin.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401

    if hasattr(user, 'is_enabled') and not user.is_enabled:
        return jsonify({'error': 'Account is deactivated'}), 403

    # Establish the server-side session — this sets the session cookie
    # that the browser will send on every subsequent /api/* request.
    login_user(user)

    return jsonify({
        'role': role,
        'name': getattr(user, 'name', getattr(user, 'username', '')),
        'id': user.id
    })

@auth_api_bp.route('/logout', methods=['POST'])
def logout():
    from flask_login import logout_user
    logout_user()
    return jsonify({'message': 'Logged out'})

@auth_api_bp.route('/me', methods=['GET'])
def me():
    """Return the currently authenticated user (or null)."""
    from flask_login import current_user
    if not current_user.is_authenticated:
        return jsonify({'user': None})
    role = type(current_user).__name__.lower()  # 'student' | 'company' | 'admin'
    return jsonify({
        'user': {
            'id': current_user.id,
            'role': role,
            'name': getattr(current_user, 'name', getattr(current_user, 'username', '')),
            'email': current_user.email,
        }
    })

@auth_api_bp.route('/register/student', methods=['POST'])
def register_student():
    data = request.get_json()
    required = ['name','email','password','roll_number','department','batch','cgpa','phone']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    if Student.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409

    if Student.query.filter_by(roll_number=data['roll_number']).first():
        return jsonify({'error': 'Roll number already registered'}), 409

    student = Student(
        name=data['name'], email=data['email'],
        roll_number=data['roll_number'], department=data['department'],
        batch=data['batch'], cgpa=float(data['cgpa']), phone=data['phone']
    )
    student.set_password(data['password'])
    db.session.add(student)
    db.session.commit()
    return jsonify({'message': 'Registered successfully'}), 201
```

### 7.2 routes/api/student_api.py

> Uses `@login_required` + `current_user` — same Flask-Login mechanism as the Jinja2 routes. The student identity is taken from the server-side session, **never** from a client-supplied header.

```python
# routes/api/student_api.py
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import or_
from models import db, Student, Application, PlacementDrive, ApplicationStatusLog, Company
from utils.cache_utils import cache
from datetime import datetime

student_api_bp = Blueprint('student_api', __name__)

@student_api_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    # Identity comes from the session — never from a request header.
    if not isinstance(current_user, Student):
        return jsonify({'error': 'Forbidden'}), 403
    student = current_user

    applications = Application.query.filter_by(student_id=student.id).all()
    total      = len(applications)
    applied    = sum(1 for a in applications if a.status == 'Applied')
    shortlisted= sum(1 for a in applications if a.status == 'Shortlisted')
    selected   = sum(1 for a in applications if a.status == 'Selected')
    accepted   = sum(1 for a in applications if a.status == 'Accepted')
    rejected   = sum(1 for a in applications if a.status == 'Rejected')
    rate       = round(((selected + accepted) / total * 100), 1) if total > 0 else 0

    today = datetime.now()
    available_drives = PlacementDrive.query.filter(
        PlacementDrive.status == 'Approved',
        PlacementDrive.is_active == True,
        PlacementDrive.is_deleted == False,
        PlacementDrive.application_deadline >= today
    ).count()

    recent = applications[:3]

    return jsonify({
        'user': {'name': student.name, 'email': student.email,
                 'roll_number': student.roll_number, 'cgpa': student.cgpa},
        'stats': {'total': total, 'applied': applied, 'shortlisted': shortlisted,
                   'selected': selected, 'accepted': accepted, 'rejected': rejected,
                   'rate': rate, 'drives': available_drives},
        'recent_applications': [{
            'company': a.drive.company.name,
            'role': a.drive.job_title,
            'status': a.status,
            'applied_at': a.applied_at.strftime('%Y-%m-%d') if a.applied_at else None
        } for a in recent]
    })

@student_api_bp.route('/drives', methods=['GET'])
@login_required
def drives():
    if not isinstance(current_user, Student):
        return jsonify({'error': 'Forbidden'}), 403
    student = current_user

    query = request.args.get('q', '').strip()
    today = datetime.now()

    drives_query = PlacementDrive.query.filter(
        PlacementDrive.status == 'Approved',
        PlacementDrive.is_active == True,
        PlacementDrive.is_deleted == False,
        PlacementDrive.application_deadline >= today
    )

    # ─── Student drive search (was missing) ───
    if query:
        drives_query = drives_query.join(PlacementDrive.company).filter(
            or_(
                PlacementDrive.job_title.ilike(f'%{query}%'),
                PlacementDrive.location.ilike(f'%{query}%'),
                PlacementDrive.allowed_branches.ilike(f'%{query}%'),
                Company.name.ilike(f'%{query}%'),
            )
        )

    all_drives = drives_query.order_by(PlacementDrive.application_deadline).all()
    applied_ids = {a.drive_id for a in Application.query.filter_by(student_id=student.id).all()}

    return jsonify({'drives': [{
        'id': d.id,
        'company': d.company.name,
        'job_title': d.job_title,
        'ctc_lpa': d.ctc_lpa,
        'location': d.location,
        'deadline': d.application_deadline.strftime('%Y-%m-%d') if d.application_deadline else None,
        'interview_date': d.interview_date.strftime('%Y-%m-%d') if d.interview_date else None,
        'min_cgpa': d.min_cgpa,
        'allowed_branches': d.allowed_branches,
        'already_applied': d.id in applied_ids
    } for d in all_drives]})
```

### 7.3 routes/api/admin_api.py (key endpoints)

> Same pattern: `@login_required` + `current_user` + `isinstance` role check. No client-supplied identity headers.

```python
# routes/api/admin_api.py
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, Admin, Student, Company, PlacementDrive, Application
from utils.cache_utils import cache

admin_api_bp = Blueprint('admin_api', __name__)

@admin_api_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    if not isinstance(current_user, Admin):
        return jsonify({'error': 'Forbidden'}), 403

    return jsonify({
        'companies': Company.query.count(),
        'students': Student.query.count(),
        'drives': PlacementDrive.query.count(),
        'applications': Application.query.count(),
        'accepted': Application.query.filter_by(status='Accepted').count(),
        'selected': Application.query.filter_by(status='Selected').count(),
        'pending_companies': Company.query.filter_by(is_approved=False).count(),
        'pending_drives': PlacementDrive.query.filter_by(status='Pending').count(),
    })

@admin_api_bp.route('/reject-company/<int:company_id>', methods=['POST'])
@login_required
def reject_company(company_id):
    """Explicit reject route — was missing from original codebase"""
    if not isinstance(current_user, Admin):
        return jsonify({'error': 'Forbidden'}), 403

    company = Company.query.get_or_404(company_id)
    # Mark as rejected: disapproved + disabled
    company.is_approved = False
    company.is_enabled = False
    db.session.commit()
    # Invalidate cache per the matrix in Section 25
    cache.delete('admin_dashboard')
    cache.delete(f'company_dashboard_{company_id}')
    cache.delete('drives_list')
    return jsonify({'message': f'Company {company.name} rejected'})
```

---

## 8. Unified Auth Model (Session-Based Only)

The PDF requires a "unified user model to differentiate all types of user roles." The existing Flask-Login session-based authentication already satisfies this requirement.

> **Authoritative authentication rule (see Section 24.1):** Flask-Login session authentication is fully compliant. JWT is optional. Existing authentication logic must remain unchanged.

### 8.1 Add a role discriminator to models.py (OPTIONAL)

> Adding a `role` column is **optional** and is not required by the project statement. It is only useful if your route logic needs to switch on a string role. Skip this if your existing `isinstance(current_user, Admin)` checks already work.

```python
# Add to models.py — existing models get a type tag
# No new table needed; use existing separate tables

# In Admin model, add (OPTIONAL):
role = db.Column(db.String(10), default='admin')

# In Student model, add (OPTIONAL):
role = db.Column(db.String(10), default='student')

# In Company model, add (OPTIONAL):
role = db.Column(db.String(10), default='company')
```

### 8.2 Role-based authentication

The existing Flask-Login session-based authentication provides role-based access control through:
- `@login_required` decorators for Jinja2 routes
- Authentication decorators for API routes
- Role checking in route logic using the `role` column (if added) or `isinstance(current_user, <Model>)` checks

This satisfies the project statement requirement for "role-based access control and authentication using Flask security (session or token)."

---

## 9. Backend Job 1 — Daily Deadline Reminders

### 9.1 utils/email_utils.py

> **HTML email correctness note:** `EmailMessage.set_content(html, subtype='html')` works but is not the recommended pattern. The clean approach is to set a plain-text body first with `set_content(...)` and then attach the HTML version with `add_alternative(html, subtype='html')`. This produces a proper `multipart/alternative` message that mail clients can render as rich HTML while still showing readable text on clients that don't support HTML. Using `set_content(html_body)` alone (without `subtype='html'`) treats the HTML as plain text, and many mail clients will display raw `<html>` tags instead of rendering the message — the bug this section previously had.

```python
# utils/email_utils.py
import smtplib
from email.message import EmailMessage
from flask import current_app

def _build_message(subject, to, html_body):
    """Build a multipart/alternative EmailMessage with text + HTML parts."""
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = current_app.config['EMAIL_DEFAULT_SENDER']
    msg['To'] = to if isinstance(to, str) else ', '.join(to)

    # Plain-text fallback (shown by clients that cannot render HTML).
    # A minimal text version is fine — keep it short, the HTML is the primary view.
    msg.set_content("This message requires an HTML-capable email client.")

    # Attach the HTML body as an alternative part. Mail clients that support
    # HTML will render this; the plain-text part above is the fallback.
    msg.add_alternative(html_body, subtype='html')
    return msg

def send_email(to, subject, html_body):
    """Send a single HTML email using built-in smtplib."""
    msg = _build_message(subject, to, html_body)

    # Use SMTP connection
    with smtplib.SMTP(current_app.config['EMAIL_SERVER'], current_app.config['EMAIL_PORT']) as server:
        if current_app.config['EMAIL_USE_TLS']:
            server.starttls()
        if current_app.config['EMAIL_USERNAME'] and current_app.config['EMAIL_PASSWORD']:
            server.login(current_app.config['EMAIL_USERNAME'], current_app.config['EMAIL_PASSWORD'])
        server.send_message(msg)

def send_bulk_emails(messages):
    """
    messages: list of dicts: [{'to': str, 'subject': str, 'html': str}]
    Uses a single SMTP connection for all.
    """
    with smtplib.SMTP(current_app.config['EMAIL_SERVER'], current_app.config['EMAIL_PORT']) as server:
        if current_app.config['EMAIL_USE_TLS']:
            server.starttls()
        if current_app.config['EMAIL_USERNAME'] and current_app.config['EMAIL_PASSWORD']:
            server.login(current_app.config['EMAIL_USERNAME'], current_app.config['EMAIL_PASSWORD'])

        for m in messages:
            msg = _build_message(m['subject'], m['to'], m['html'])
            server.send_message(msg)
```

### 9.2 config.py — email configuration (using smtplib)

```python
# Add to Config class - email settings for smtplib
EMAIL_SERVER   = 'smtp.gmail.com'
EMAIL_PORT     = 587
EMAIL_USE_TLS  = True
EMAIL_USERNAME = os.environ.get('EMAIL_USERNAME')       # from .env
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')       # App password from Gmail
EMAIL_DEFAULT_SENDER = ('Placement Portal', os.environ.get('EMAIL_USERNAME'))
```

### 9.3 tasks/reminders.py

```python
# tasks/reminders.py
from celery_worker import celery
from models import Student, PlacementDrive, Application
from utils.email_utils import send_bulk_emails
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@celery.task(name='tasks.reminders.send_deadline_reminders')
def send_deadline_reminders():
    """
    Scheduled daily at 8:00 AM IST.
    Sends email reminders to students about drives with deadlines
    in the next 3 days that they haven't applied to yet.
    """
    today = datetime.utcnow()
    three_days_later = today + timedelta(days=3)

    # Drives expiring in next 3 days
    upcoming_drives = PlacementDrive.query.filter(
        PlacementDrive.status == 'Approved',
        PlacementDrive.is_active == True,
        PlacementDrive.is_deleted == False,
        PlacementDrive.application_deadline >= today,
        PlacementDrive.application_deadline <= three_days_later
    ).all()

    if not upcoming_drives:
        logger.info("No upcoming drives — no reminders sent")
        return {'sent': 0}

    # All active students
    students = Student.query.filter_by(is_enabled=True).all()

    messages = []
    for student in students:
        # Drives this student has NOT applied to
        applied_ids = {a.drive_id for a in
                       Application.query.filter_by(student_id=student.id).all()}

        not_applied = [d for d in upcoming_drives if d.id not in applied_ids]
        if not not_applied:
            continue

        drive_rows = ''.join([f"""
            <tr>
              <td>{d.company.name}</td>
              <td>{d.job_title}</td>
              <td>{d.application_deadline.strftime('%d %b %Y')}</td>
            </tr>""" for d in not_applied])

        html = f"""
        <html><body>
        <h2>Placement Portal — Deadline Reminder</h2>
        <p>Hi <strong>{student.name}</strong>,</p>
        <p>The following placement drives are closing soon. Don't miss out!</p>
        <table border="1" cellpadding="8" style="border-collapse:collapse;">
          <thead>
            <tr><th>Company</th><th>Role</th><th>Deadline</th></tr>
          </thead>
          <tbody>{drive_rows}</tbody>
        </table>
        <p>Login to apply: <a href="http://localhost:5000/student/dashboard">Placement Portal</a></p>
        <p>— Placement Cell</p>
        </body></html>
        """

        messages.append({'to': student.email,
                         'subject': '⏰ Placement Drive Deadline Reminder',
                         'html': html})

    if messages:
        send_bulk_emails(messages)
        logger.info(f"Sent {len(messages)} deadline reminder emails")

    return {'sent': len(messages)}
```

---

## 10. Backend Job 2 — Monthly Activity Report

> The monthly report must be sent as **HTML email** (mandatory). PDF attachment is **OPTIONAL** — see Section 17.

### 10.1 tasks/reports.py

```python
# tasks/reports.py
from celery_worker import celery
from models import Admin, Application, PlacementDrive, Company, Student
from utils.email_utils import send_email
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@celery.task(name='tasks.reports.send_monthly_report')
def send_monthly_report():
    """
    Runs on the 1st of every month at 7:00 AM.
    Generates an HTML report (+ optional PDF) of last month's activity.
    Sends to admin email.
    """
    today = datetime.utcnow()
    # Last month's date range
    first_of_this_month = today.replace(day=1, hour=0, minute=0, second=0)
    last_month_end = first_of_this_month - timedelta(seconds=1)
    last_month_start = last_month_end.replace(day=1, hour=0, minute=0, second=0)

    # Stats for last month
    drives_this_month = PlacementDrive.query.filter(
        PlacementDrive.created_at >= last_month_start,
        PlacementDrive.created_at <= last_month_end
    ).count()

    apps_this_month = Application.query.filter(
        Application.applied_at >= last_month_start,
        Application.applied_at <= last_month_end
    ).all()

    total_apps  = len(apps_this_month)
    selected    = sum(1 for a in apps_this_month if a.status in ['Selected', 'Accepted'])
    selection_rate = round((selected / total_apps * 100), 1) if total_apps > 0 else 0

    month_label = last_month_end.strftime('%B %Y')

    html = f"""
    <html>
    <head>
      <style>
        body {{ font-family: Arial, sans-serif; color: #333; }}
        h1   {{ color: #0d6efd; }}
        .stat-box {{ display: inline-block; padding: 20px; margin: 10px;
                     background: #f8f9fa; border-radius: 8px; text-align: center; }}
        .stat-number {{ font-size: 2rem; font-weight: bold; color: #0d6efd; }}
      </style>
    </head>
    <body>
      <h1>Monthly Placement Activity Report</h1>
      <h3>{month_label}</h3>
      <hr>
      <div>
        <div class="stat-box">
          <div class="stat-number">{drives_this_month}</div>
          <div>Drives Conducted</div>
        </div>
        <div class="stat-box">
          <div class="stat-number">{total_apps}</div>
          <div>Students Applied</div>
        </div>
        <div class="stat-box">
          <div class="stat-number">{selected}</div>
          <div>Students Selected</div>
        </div>
      </div>
      <p style="color:#999; font-size:12px;">
        Generated on {today.strftime('%d %b %Y at %H:%M')} UTC — Placement Portal
      </p>
    </body>
    </html>
    """

    # Get admin email
    admin = Admin.query.first()
    if not admin:
        logger.error("No admin found — cannot send monthly report")
        return

    send_email(
        to=admin.email,
        subject=f'📊 Monthly Placement Report — {month_label}',
        html_body=html
    )
    logger.info(f"Monthly report sent to {admin.email}")
    return {'month': month_label, 'drives': drives_this_month, 'apps': total_apps}
```

---

## 11. Backend Job 3 — Async CSV Export

### 11.1 tasks/exports.py

```python
# tasks/exports.py
from celery_worker import celery
from models import Application, Student
import csv
import os
import logging
from flask import current_app
from datetime import datetime

logger = logging.getLogger(__name__)

@celery.task(name='tasks.exports.export_student_csv', bind=True)
def export_student_csv(self, student_id):
    """
    User-triggered async task.
    Exports all application history for a student to a CSV file.
    Returns the file path on completion.
    """
    try:
        applications = Application.query.filter_by(student_id=student_id).all()

        # Save to static/exports/
        export_dir = os.path.join(current_app.root_path, 'static', 'exports')
        os.makedirs(export_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"student_{student_id}_{timestamp}.csv"
        filepath = os.path.join(export_dir, filename)

        # Write CSV with required columns only
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Student ID', 'Company Name', 'Drive Title', 'Application Status', 'Dates']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for app in applications:
                writer.writerow({
                    'Student ID': app.student.roll_number,
                    'Company Name': app.drive.company.name,
                    'Drive Title': app.drive.job_title,
                    'Application Status': app.status,
                    'Dates': f"Applied: {app.applied_at.strftime('%Y-%m-%d') if app.applied_at else 'N/A'}, Last Updated: {app.updated_at.strftime('%Y-%m-%d') if app.updated_at else 'N/A'}"
                })

        logger.info(f"CSV export complete for student {student_id}: {filepath}")
        return {'filename': filename, 'url': f'/static/exports/{filename}'}

    except Exception as exc:
        logger.error(f"CSV export failed for student {student_id}: {exc}")
        raise self.retry(exc=exc, countdown=5, max_retries=3)
```

### 11.2 routes/api/jobs_api.py — trigger + poll

> Uses `@login_required` + `current_user`. The student identity is taken from the session, never from a header.

```python
# routes/api/jobs_api.py
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import Student
from tasks.exports import export_student_csv

jobs_api_bp = Blueprint('jobs_api', __name__)

@jobs_api_bp.route('/export-csv', methods=['POST'])
@login_required
def trigger_export():
    if not isinstance(current_user, Student):
        return jsonify({'error': 'Forbidden'}), 403

    # Dispatch async task — pass the authenticated student's id from the session.
    task = export_student_csv.delay(current_user.id)
    return jsonify({'job_id': task.id, 'state': 'PENDING'}), 202

@jobs_api_bp.route('/status/<job_id>', methods=['GET'])
@login_required
def job_status(job_id):
    if not isinstance(current_user, Student):
        return jsonify({'error': 'Forbidden'}), 403
    from celery.result import AsyncResult
    result = AsyncResult(job_id)
    if result.state == 'PENDING':
        return jsonify({'state': 'PENDING'})
    elif result.state == 'SUCCESS':
        return jsonify({'state': 'SUCCESS', 'result_url': result.result.get('url')})
    elif result.state == 'FAILURE':
        return jsonify({'state': 'FAILURE', 'error': str(result.info)})
    else:
        return jsonify({'state': result.state})
```

---

## 12. Caching Strategy

### 12.1 utils/cache_utils.py

```python
# utils/cache_utils.py
from flask_caching import Cache

cache = Cache()
```

### 12.2 config.py — cache config

```python
# Add to Config class
CACHE_TYPE    = 'RedisCache'
CACHE_REDIS_URL = 'redis://localhost:6379/1'   # DB 1 separate from Celery
CACHE_DEFAULT_TIMEOUT = 300                    # 5 minutes default
```

### 12.3 What to cache and for how long

| Endpoint | TTL | Cache Key Pattern | Invalidate On |
|---|---|---|---|
| Admin dashboard stats | 120s | `admin_dashboard` | Any application status change |
| Student dashboard | 60s | `student_dashboard_{id}` | Student applies / status changes |
| Available drives list | 300s | `drives_list` | Drive created / approved / closed |
| Company dashboard | 60s | `company_dashboard_{id}` | Application updated |
| Search results | 30s | `search_{query}` | Student/company created/deleted |

> **Authoritative source:** The complete cache invalidation matrix in **Section 25** is the single source of truth for invalidation rules. All cache invalidation examples in this document must conform to that matrix.

### 12.4 Cache invalidation pattern

> These examples conform to the authoritative matrix in Section 25.

```python
# In any route that modifies data, invalidate related cache keys
from utils.cache_utils import cache

# After admin approves a drive (per Section 25 matrix):
cache.delete('admin_dashboard')
cache.delete('drives_list')
cache.delete(f'drive_{drive_id}_details')   # if cached

# After student applies (per Section 25 matrix):
cache.delete(f'student_dashboard_{student.id}')
cache.delete('drives_list')
cache.delete('admin_dashboard')
```

### 12.5 Concrete `@cache.cached` decorator examples

> The matrix in Section 12.3 defines *what* to cache and the key pattern, but does not show the actual decorator usage. The examples below fill that gap. Each one matches a row in the Section 25 invalidation matrix — the cache key produced here is exactly the key the matrix tells you to delete on writes.

#### Admin dashboard (single shared key)

```python
# routes/admin_routes.py  (or routes/api/admin_api.py)
from flask_login import login_required, current_user
from utils.cache_utils import cache
from models import Admin, Student, Company, PlacementDrive, Application

@admin_bp.route('/dashboard')
@login_required
@cache.cached(timeout=120, key_prefix='admin_dashboard')
def dashboard():
    if not isinstance(current_user, Admin):
        return "Forbidden", 403
    return render_template('admin/dashboard.html',
        companies=Company.query.count(),
        students=Student.query.count(),
        drives=PlacementDrive.query.count(),
        applications=Application.query.count(),
    )
```

#### Student dashboard (per-student key)

> The `key_prefix` must be a callable so it can read `current_user.id` at request time, not at decoration time. `@login_required` runs before the cache lookup, so `current_user` is already populated when the key function is called.

```python
# routes/student_routes.py  (or routes/api/student_api.py)
from flask_login import login_required, current_user
from utils.cache_utils import cache
from models import Student, Application, PlacementDrive

@student_bp.route('/dashboard')
@login_required
@cache.cached(
    timeout=60,
    key_prefix=lambda: f'student_dashboard_{current_user.id}'
)
def dashboard():
    if not isinstance(current_user, Student):
        return "Forbidden", 403
    student = current_user
    applications = Application.query.filter_by(student_id=student.id).all()
    # ... build stats dict ...
    return render_template('student/dashboard.html', stats=stats, applications=applications)
```

#### Available drives list (single shared key)

```python
# routes/student_routes.py
@student_bp.route('/drives')
@login_required
@cache.cached(timeout=300, key_prefix='drives_list')
def drives():
    if not isinstance(current_user, Student):
        return "Forbidden", 403
    # ... existing drives query ...
    return render_template('student/available_drives.html', drives=filtered_drives)
```

> **Caveat — search queries:** The shared `drives_list` cache key works only when the route returns the same data for every student. If the route accepts a `?q=` search parameter (see Section 14), the cache will return the first cached result for *any* query. For the searchable variant, either (a) skip `@cache.cached` and rely on the per-query `search_{query}` key with a manual `cache.get` / `cache.set` pattern, or (b) include the query in the key prefix:
>
> ```python
> @cache.cached(
>     timeout=30,
>     key_prefix=lambda: f"search_{request.args.get('q', '').strip().lower()}"
> )
> ```
>
> Do not combine the shared `drives_list` key with a search route — they conflict.

#### Company dashboard (per-company key)

```python
# routes/company_routes.py
@company_bp.route('/dashboard')
@login_required
@cache.cached(
    timeout=60,
    key_prefix=lambda: f'company_dashboard_{current_user.id}'
)
def dashboard():
    if not isinstance(current_user, Company):
        return "Forbidden", 403
    # ... build company dashboard data ...
    return render_template('company/dashboard.html', ...)
```

#### Summary of decorator patterns

| Endpoint | Decorator | Key prefix |
|---|---|---|
| Admin dashboard | `@cache.cached(timeout=120, key_prefix='admin_dashboard')` | Static string |
| Student dashboard | `@cache.cached(timeout=60, key_prefix=lambda: f'student_dashboard_{current_user.id}')` | Callable — per-user |
| Drives list (no search) | `@cache.cached(timeout=300, key_prefix='drives_list')` | Static string |
| Drives list (with search) | `@cache.cached(timeout=30, key_prefix=lambda: f"search_{request.args.get('q','').strip().lower()}")` | Callable — per-query |
| Company dashboard | `@cache.cached(timeout=60, key_prefix=lambda: f'company_dashboard_{current_user.id}')` | Callable — per-user |

---

## 13. Eligibility Validation Fix

This fixes the missing CGPA/branch validation in `student_routes.py`.

### 13.1 utils/validators.py

```python
# utils/validators.py

def check_eligibility(student, drive):
    """
    Returns (is_eligible: bool, reason: str)
    Called before allowing a student to apply to a drive.
    """
    # CGPA check
    if drive.min_cgpa and student.cgpa < drive.min_cgpa:
        return False, f"Minimum CGPA required is {drive.min_cgpa}. Your CGPA: {student.cgpa}"

    # Branch/department check
    if drive.allowed_branches:
        allowed = [b.strip().lower() for b in drive.allowed_branches.split(',')]
        student_dept = student.department.strip().lower()
        # Check if any allowed branch matches (partial match for flexibility)
        if not any(b in student_dept or student_dept in b for b in allowed):
            return False, f"Your department ({student.department}) is not eligible. Allowed: {drive.allowed_branches}"

    # Batch check
    if drive.batch and student.batch and drive.batch.strip() != student.batch.strip():
        return False, f"This drive is for batch {drive.batch}. You are batch {student.batch}"

    return True, "Eligible"
```

### 13.2 Apply to apply_drive route in student_routes.py

```python
# In student_routes.py — add after the deadline check inside apply_drive()

from utils.validators import check_eligibility

# After existing deadline check, add:
eligible, reason = check_eligibility(current_user, drive)
if not eligible:
    flash(f'Not eligible: {reason}', 'danger')
    return redirect(url_for('student.drives'))
```

---

## 14. Student Drive Search

Add to `routes/student_routes.py` — the existing `/drives` route, add query filtering:

```python
# In student_routes.py — modify the drives() function

@student_bp.route('/drives')
@login_required
def drives():
    cleanup_expired_offers()
    query = request.args.get('q', '').strip()   # ← NEW: read search param
    today = datetime.now()
    all_applications = Application.query.filter_by(student_id=current_user.id).all()
    app_map = {app.drive_id: app.status for app in all_applications}

    is_accepted = any(app.status == "Accepted" for app in all_applications)
    is_selected = any(app.status == "Selected" for app in all_applications)
    active_count = sum(1 for app in all_applications if app.status in ACTIVE_STATUSES)
    max_active_reached = active_count >= 3

    drives_query = PlacementDrive.query.filter(
        PlacementDrive.status == 'Approved',
        PlacementDrive.is_active == True,
        PlacementDrive.is_deleted == False,
        PlacementDrive.application_deadline >= today
    )

    # ─── NEW: text search ───
    if query:
        from sqlalchemy import or_
        from models import Company
        drives_query = drives_query.join(Company, PlacementDrive.company_id == Company.id).filter(
            or_(
                PlacementDrive.job_title.ilike(f'%{query}%'),
                PlacementDrive.location.ilike(f'%{query}%'),
                PlacementDrive.allowed_branches.ilike(f'%{query}%'),
                Company.name.ilike(f'%{query}%')
            )
        )

    approved_drives = drives_query.order_by(PlacementDrive.application_deadline).all()

    filtered_drives = [d for d in approved_drives
                       if app_map.get(d.id) not in ["Selected", "Rejected", "Accepted"]]
    applied_drive_ids = [app.drive_id for app in all_applications]

    return render_template('student/available_drives.html',
                           drives=filtered_drives,
                           applied_drive_ids=applied_drive_ids,
                           is_selected=is_selected, is_accepted=is_accepted,
                           max_active_reached=max_active_reached,
                           search_query=query)   # ← pass back to template
```

Also update `templates/student/available_drives.html` — add search bar above the table:

```html
<!-- Add inside <div class="dashboard-page"> before the table-container -->
<div class="filter-bar mb-3">
  <form method="GET" action="{{ url_for('student.drives') }}" class="row g-2 align-items-center">
    <div class="col-auto">
      <input type="text" name="q" class="form-control"
             placeholder="Search by company, role, location, branch..."
             value="{{ search_query or '' }}" style="min-width: 350px;">
    </div>
    <div class="col-auto">
      <button type="submit" class="btn btn-primary">Search</button>
    </div>
    {% if search_query %}
    <div class="col-auto">
      <a href="{{ url_for('student.drives') }}" class="btn btn-secondary">Clear</a>
    </div>
    {% endif %}
  </form>
</div>
```

---

## 15. Company Reject Route Fix

Add explicit reject route to `admin_routes.py`:

```python
# In admin_routes.py — add after approve_company()

@admin_bp.route('/reject-company/<int:company_id>', methods=['POST'])
@login_required
def reject_company(company_id):
    """
    Explicit reject: disapproves registration and disables the account.
    Different from blacklist — this is for initial registration rejection.
    """
    from models import Admin
    if not isinstance(current_user, Admin):
        flash('Access denied', 'danger')
        return redirect(url_for('auth.index'))
    company = Company.query.get_or_404(company_id)
    company.is_approved = False
    company.is_enabled = False
    db.session.commit()
    # Invalidate cache per Section 25 matrix
    from utils.cache_utils import cache
    cache.delete('admin_dashboard')
    cache.delete(f'company_dashboard_{company_id}')
    cache.delete('drives_list')
    flash(f'Company {company.name} registration rejected.', 'warning')
    return redirect(url_for('admin.manage_companies'))
```

Update `templates/admin/manage_companies.html` — add Reject button next to Approve:

```html
<!-- Replace the Approve-only section with: -->
{% if not company.is_approved and company.is_enabled %}
<a href="{{ url_for('admin.approve_company', company_id=company.id) }}"
   class="btn btn-sm btn-success">Approve</a>
<form method="POST"
      action="{{ url_for('admin.reject_company', company_id=company.id) }}"
      style="display:inline;">
  <button type="submit" class="btn btn-sm btn-danger"
          onclick="return confirm('Reject this company registration?')">Reject</button>
</form>
{% endif %}
```

---

## 16. ChartJS Dashboard Analytics (OPTIONAL)

> **This entire section is OPTIONAL.** ChartJS is listed under "Recommended and/or Optional functionalities" in the project statement. Do not implement this section unless all mandatory items in Section 27 (Corrected Final Priority Order) are complete.

For the Jinja2 templates (no VueJS), add ChartJS directly in templates.

### 16.1 In admin_dashboard.html — add below stat cards (OPTIONAL)

```html
<!-- Add CDN in base.html <head> (OPTIONAL) -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>

<!-- In admin_dashboard.html — add a charts section (OPTIONAL) -->
<div class="row mt-4">
  <div class="col-md-6">
    <div class="card p-3">
      <h5 class="card-title">Application Status Breakdown</h5>
      <canvas id="statusChart" height="200"></canvas>
    </div>
  </div>
  <div class="col-md-6">
    <div class="card p-3">
      <h5 class="card-title">Drives Over Time</h5>
      <canvas id="drivesChart" height="200"></canvas>
    </div>
  </div>
</div>

<script>
// Application status pie chart
new Chart(document.getElementById('statusChart'), {
  type: 'doughnut',
  data: {
    labels: ['Accepted', 'Selected', 'Shortlisted', 'Rejected'],
    datasets: [{
      data: [{{ accepted_count }}, {{ selected_count }}, {{ shortlisted_count }}, {{ rejected_count }}],
      backgroundColor: ['#198754', '#0d6efd', '#0dcaf0', '#dc3545']
    }]
  },
  options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
});
</script>
```

### 16.2 In student_dashboard.html — add mini chart (OPTIONAL)

```html
<div class="card p-3 mt-4">
  <h5 class="section-title">My Application Summary</h5>
  <canvas id="myChart" style="max-height:250px;"></canvas>
</div>

<script>
new Chart(document.getElementById('myChart'), {
  type: 'bar',
  data: {
    labels: ['Applied', 'Shortlisted', 'Selected', 'Accepted', 'Rejected'],
    datasets: [{
      label: 'Applications',
      data: [{{ total - selected - rejected }}, 0, {{ selected }}, {{ accepted }}, {{ rejected }}],
      backgroundColor: ['#6c757d','#0dcaf0','#198754','#0d6efd','#dc3545']
    }]
  },
  options: {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } }
  }
});
</script>
```

---

## 17. Optional Enhancements (Not Required For Marks)

The following items appear in the earlier sections of this architecture document. They are **not required** by the project statement and should only be implemented after all mandatory items above are complete.

### 17.1 PDF Monthly Report Generation (OPTIONAL)

**Why Optional:** Project statement lists PDF reports under "Recommended and/or Optional functionalities": "Well-designed PDF reports for Monthly activity reports (Students can choose between HTML and PDF reports)."

#### 17.1.1 utils/pdf_utils.py (OPTIONAL)

```python
# utils/pdf_utils.py
from weasyprint import HTML
import os

def generate_pdf_from_html(html_string, output_path):
    """
    Converts an HTML string to a PDF file at output_path.
    Uses WeasyPrint (no external binaries needed beyond system libs).
    """
    HTML(string=html_string).write_pdf(output_path)
    return output_path
```

#### 17.1.2 Optional PDF endpoint for admin (OPTIONAL)

```python
# In admin_routes.py — add monthly report download (OPTIONAL)

@admin_bp.route('/monthly-report-pdf')
@login_required
def monthly_report_pdf():
    from utils.pdf_utils import generate_pdf_from_html
    from flask import send_file
    import tempfile

    # Reuse report HTML generation logic (extract from tasks/reports.py into a helper)
    html = generate_monthly_report_html()

    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        generate_pdf_from_html(html, f.name)
        return send_file(f.name, download_name='monthly_report.pdf',
                         as_attachment=True, mimetype='application/pdf')
```

---

## 18. Resume Upload in Profile

Add standalone resume field to student profile.

### 18.1 models.py — add resume_path to Student

```python
# In Student model, add:
resume_path = db.Column(db.String(200), nullable=True)
```

### 18.2 student_routes.py — update profile() to accept file

```python
# Modified profile route in student_routes.py
@student_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.name       = request.form.get('name')
        current_user.department = request.form.get('department')
        current_user.batch      = request.form.get('batch')
        current_user.cgpa       = float(request.form.get('cgpa', 0))

        # ─── NEW: handle resume upload ───
        resume = request.files.get('resume')
        if resume and resume.filename.lower().endswith('.pdf'):
            from werkzeug.utils import secure_filename
            upload_folder = os.path.join(current_app.root_path, 'uploads', 'resumes')
            os.makedirs(upload_folder, exist_ok=True)
            filename = f"resume_student_{current_user.id}.pdf"
            resume.save(os.path.join(upload_folder, filename))
            current_user.resume_path = filename
            flash('Resume updated successfully!', 'info')

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('student.profile'))

    return render_template('student/profile.html')
```

### 18.3 templates/student/profile.html — add resume field

```html
<!-- Add enctype to form tag -->
<form method="POST" enctype="multipart/form-data">

  <!-- Add below the existing fields -->
  <div class="row">
    <div class="col-md-12 mb-3">
      <label class="form-label">Upload / Update Resume (PDF)</label>
      <input type="file" class="form-control" name="resume" accept=".pdf">
      {% if current_user.resume_path %}
        <div class="form-text">
          Current resume:
          <a href="{{ url_for('uploaded_resume', filename=current_user.resume_path) }}"
             target="_blank">View Resume</a>
        </div>
      {% endif %}
    </div>
  </div>

  <button type="submit" class="btn btn-primary">Update Profile</button>
</form>
```

---

## 19. config.py — Full Updated Version

```python
# config.py
import os
from celery.schedules import crontab

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Core Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "placement.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'applications')
    RESUME_FOLDER = os.path.join(BASE_DIR, 'uploads', 'resumes')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024   # 16 MB

    # Redis / Celery
    CELERY_BROKER_URL     = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    CELERY_TIMEZONE       = 'Asia/Kolkata'

    CELERYBEAT_SCHEDULE = {
        'daily-deadline-reminders': {
            'task': 'tasks.reminders.send_deadline_reminders',
            'schedule': crontab(hour=8, minute=0),
        },
        'monthly-activity-report': {
            'task': 'tasks.reports.send_monthly_report',
            'schedule': crontab(day_of_month=1, hour=7, minute=0),
        },
    }

    # Flask-Caching
    CACHE_TYPE      = 'RedisCache'
    CACHE_REDIS_URL = os.environ.get('CACHE_REDIS_URL', 'redis://localhost:6379/1')
    CACHE_DEFAULT_TIMEOUT = 300

    # Email (using smtplib — NOT flask-mail)
    EMAIL_SERVER         = 'smtp.gmail.com'
    EMAIL_PORT           = 587
    EMAIL_USE_TLS        = True
    EMAIL_USERNAME       = os.environ.get('EMAIL_USERNAME')
    EMAIL_PASSWORD       = os.environ.get('EMAIL_PASSWORD')
    EMAIL_DEFAULT_SENDER = ('Placement Portal', os.environ.get('EMAIL_USERNAME'))
```

---

## 20. Updated requirements.txt

> Split into **Required** and **Optional** sections. Only the Required block needs to be installed for project statement compliance. The Optional block can be commented out or omitted entirely.

### Required dependencies (install for submission)

```txt
# Core Flask
flask
flask-login
flask-sqlalchemy

# Caching
flask-caching
redis

# Task Queue
celery[redis]

# Email (using built-in smtplib — NOT flask-mail)
# No additional package needed - use built-in smtplib

# Dev / util
python-dotenv
```

### Optional dependencies (install only if implementing the related optional feature)

```txt
# --- OPTIONAL: PDF monthly report generation (see Section 17) ---
# Uncomment the line below ONLY if you are implementing PDF reports.
# Otherwise leave it commented so WeasyPrint is not pulled in by default.
# weasyprint

# --- OPTIONAL: Celery monitoring dashboard (see Section 5.3) ---
# Uncomment the line below ONLY if you want the Flower monitoring UI.
# flower
```

---

## 21. Integration Checklist (Historical Planning Reference)

> **Compliance Note:** This checklist is preserved as a **historical planning reference only**. The **authoritative implementation order** is in **Section 27 — Corrected Final Priority Order**. Do not use this checklist as the source of truth for sequencing. Where this checklist conflicts with Section 27, Section 27 wins.

Use this as your step-by-step implementation order:

```
OPTIONAL FOUNDATION STEP — App Factory Refactor (SKIP if not needed)
  [ ] Refactor app.py to factory pattern (Section 5.4) — OPTIONAL
      Skip this entirely if you are not using Celery or do not need it.
      If you skip it, use "Option B" in Section 5.1 for celery_worker.py.
      This is NOT required for any other Phase below.

PHASE 1 — Foundation (Redis + Celery + config)
  [ ] Update config.py with all new settings (Section 19)
  [ ] Update requirements.txt and pip install (Section 20)
  [ ] Install and start Redis (Section 3.1)
  [ ] Create celery_worker.py (Section 5.1 — use Option A if you did the
      OPTIONAL FOUNDATION STEP above, otherwise Option B)
  [ ] Create utils/ folder with cache_utils.py and email_utils.py (Sections 12.1, 9.1)

PHASE 2 — Bug Fixes (quick wins on existing Jinja2 app)
  [ ] Add company reject route to admin_routes.py (Section 15)
  [ ] Add student drive search to student_routes.py (Section 14)
  [ ] Add eligibility validation in apply_drive (Section 13.2)
  [ ] Add resume upload to student profile (Section 18)

PHASE 3 — Caching
  [ ] Apply @cache.cached to admin dashboard route (Section 12)
  [ ] Apply @cache.cached to student dashboard route (Section 12)
  [ ] Apply @cache.cached to drives list route (Section 12)
  [ ] Add cache.delete() calls in all write routes (Section 12.4 + Section 25 matrix)

PHASE 4 — Celery Jobs
  [ ] Create tasks/reminders.py (Section 9.3)
  [ ] Create tasks/reports.py (Section 10.1)
  [ ] Create tasks/exports.py (Section 11.1)
  [ ] Create routes/api/jobs_api.py (Section 11.2)
  [ ] Test: celery worker + beat running, trigger manually via python shell
  [ ] Set up .env with EMAIL_USERNAME and EMAIL_PASSWORD

PHASE 5 — ChartJS (Jinja2 templates) — OPTIONAL
  [ ] Add Chart.js CDN to base.html (Section 16) — OPTIONAL
  [ ] Add donut chart to admin_dashboard.html (Section 16.1) — OPTIONAL
  [ ] Add bar chart to student_dashboard.html (Section 16.2) — OPTIONAL

PHASE 6 — Flask JSON API
  [ ] Create routes/api/ folder with __init__.py
  [ ] Implement auth_api.py (Section 7.1) — uses Flask-Login login_user() + current_user
  [ ] Implement student_api.py (Section 7.2) — @login_required + current_user
  [ ] Implement admin_api.py (Section 7.3) — @login_required + isinstance role check
  [ ] Test all API endpoints with curl or Postman

PHASE 7 — VueJS Frontend (Vite)
  [ ] npm create @vitejs/create-vue@latest vite-frontend
  [ ] npm install vue-router@4 bootstrap
  [ ] Configure vite.config.js to output to static/vue/dist (Section 6.2)
  [ ] Create src/api/axios.js (Section 6.3) — OPTIONAL, fetch is sufficient
  [ ] Create src/router/index.js (Section 6.4)
  [ ] Build views: LoginView, StudentDashboard, AdminDashboard, etc.
  [ ] Add ChartJS components (Section 6.6) — OPTIONAL
  [ ] npm run build → output lands in static/vue/dist
  [ ] Add /app route in Flask to serve vue_app.html (Section 5.4 — only required
      if you did the OPTIONAL FOUNDATION STEP; otherwise add the route to the
      existing module-level app)

PHASE 8 — PDF Reports — OPTIONAL
  [ ] pip install weasyprint — OPTIONAL (see Section 20)
  [ ] Create utils/pdf_utils.py (Section 17.1) — OPTIONAL
  [ ] Add admin monthly-report-pdf route (Section 17.2) — OPTIONAL
```

---

*Document generated for Placement Portal Application V2 — App Dev II (Jan 2026)*  
*Author: Aajay | Sapthagiri NPS University*

---

## 22. .gitignore

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
*.egg-info/
dist/
build/

# Node/Vue/Vite
node_modules/
vite-frontend/node_modules/
vite-frontend/dist/
vite-frontend/.vite/

# Environment
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Logs
logs/
*.log

# Database
sqlite.db
placement.db

# Uploads
uploads/applications/*.pdf
uploads/resumes/*.pdf

# Temporary files
*.tmp
*.temp

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
```

---

## 23. Logging

### Minimal logging setup

```python
# In config.py
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# In app.py
import logging
from logging.handlers import RotatingFileHandler

# Application logger
app_logger = logging.getLogger('placement_portal')
app_logger.setLevel(logging.INFO)
app_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, 'app.log'),
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
app_logger.addHandler(app_handler)
app_logger.addHandler(logging.StreamHandler())

# Celery logger
celery_logger = logging.getLogger('celery')
celery_logger.setLevel(logging.INFO)
celery_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, 'celery.log'),
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
celery_logger.addHandler(celery_handler)
```

### Log file locations

- `logs/app.log` — Application logs (info, warning, error)
- `logs/celery.log` — Celery worker logs (info, warning, error)

---

## 24. Final PDF Compliance Amendment

> **Authoritative Compliance Section:** This single amendment consolidates and supersedes all previously scattered compliance sections (including the prior "Architecture Corrections & PDF Compliance Update", "Final Compliance Corrections", and the earlier "PDF Compliance Amendment" drafts). Where any earlier section in this document conflicts with this amendment, **this amendment takes precedence**. The goal is 100% compliance with the Placement Portal Application V2 project statement with the minimum necessary changes.

---

### 24.1 Authentication (Session-Based is Fully Compliant)

The project statement reads: *"Role-based access control and authentication using Flask Security (session or token) or JWT based Token."*

**Authoritative rule:**
- Flask-Login session authentication is **fully compliant** and is the recommended approach.
- JWT is **optional** and should only be added if your chosen Vue integration strategy genuinely requires stateless tokens.
- The existing Flask-Login implementation (login routes, `@login_required` decorators, `load_user` function) must remain **unchanged**.
- For the Vue API layer, configure the Vite dev server to proxy `/api` requests to Flask (see Section 6.2). The browser session cookie propagates naturally through the proxy — **no token mechanism is required**.
- If JWT is used for any reason, it must be confined entirely to `routes/api/` and must not touch the Jinja2 routes.
- Do **not** implement a JWT + session hybrid on the same endpoint.

---

### 24.2 User Model — Do Not Redesign

The existing three-table structure (`Admin`, `Student`, `Company`) already satisfies the project statement requirement for "a unified user model to differentiate all types of user roles." The word "unified" means *one authentication system that handles all roles*, not one database table.

**Authoritative rule:**
- Do **not** create a `User` base table.
- Do **not** introduce inheritance hierarchies or polymorphic mappings.
- Only two additive model changes are permitted:
  1. `resume_path` on `Student` (Section 18) — required for profile resume management.
  2. `contact_person` on `Company` (Section 24.5 below) — required for HR contact per project statement.
- No other model changes are required or permitted.

---

### 24.3 App Factory Pattern — Recommended, Not Mandatory

The project statement does **not** require a Flask application factory pattern.

**Authoritative rule:**
- The factory pattern is **recommended only if required** for Celery integration, testing, or blueprint organization.
- If you are not using Celery or do not need the factory pattern, the existing module-level app may work with minor adjustments.
- The example factory implementation in Section 5.4 is a **recommended implementation strategy**, not a project requirement.
- Do not block other work on factory conversion.

---

### 24.4 Service Layer — Recommended Code Organization

The project statement does **not** require a service layer.

**Authoritative rule:**
- The `services/` directory is **recommended code organization**, not required architecture.
- Existing route business logic may remain in routes — do not force a large-scale rewrite of working logic.
- Service extraction is **optional** and should be performed only when code reuse becomes necessary (e.g., when the Vue API layer duplicates route logic, or when Celery tasks need to call the same logic).
- Migration approach: extract one service at a time, starting with the most duplicated logic. After each extraction, verify existing Jinja2 routes still work before building on top.

**Suggested service layer structure (OPTIONAL):**

```
services/
├── __init__.py
├── application_service.py   # apply, update status, accept offer, cleanup_expired_offers
├── drive_service.py         # create, edit, approve, close, search drives
├── auth_service.py          # register student, register company, validate login
└── report_service.py        # generate monthly report HTML, gather stats
```

**What to extract (only if code reuse becomes necessary):**

```python
# services/application_service.py — extract from student_routes.apply_drive,
# company_routes.update_application, student_routes.accept_offer, and
# cleanup_expired_offers (duplicated in 3 files)

def apply_to_drive(student, drive, resume_filename):
    """Called by student_routes.apply_drive and student_api.apply_drive."""
    ...

def update_application_status(application, new_status):
    """Status transition + ApplicationStatusLog creation."""
    ...

def accept_offer(application, student):
    """Mark as Accepted, reject all other active applications."""
    ...

def cleanup_expired_offers():
    """Currently duplicated in 3 route files — extract here, import in all three."""
    ...
```

```python
# services/drive_service.py

def get_available_drives(student=None, search_query=None):
    """Returns approved, active, non-expired drives, optionally filtered."""
    ...

def create_drive(company, form_data):
    """Called by company_routes.create_drive and company_api.create_drive."""
    ...
```

```python
# services/report_service.py

def generate_monthly_report_html(year, month):
    """Called by tasks/reports.py (Celery) and optionally admin_routes (on-demand)."""
    ...

def get_admin_dashboard_stats():
    """Called by admin_routes.dashboard and admin_api.dashboard.
    Cached at the route level, not inside the service."""
    ...
```

```python
# services/auth_service.py

def register_student(form_data):
    """Called by auth_routes and auth_api. Returns (student, error)."""
    ...

def register_company(form_data):
    """Called by auth_routes and auth_api. Returns (company, error)."""
    ...

def validate_login(email, password, role):
    """Returns (user_object, error). Role is 'student'|'company'|'admin'."""
    ...
```

**Migration rule:** A route function should ideally do three things only: parse request, call service, return response. Do not rewrite routes — refactor them to call service functions.

---

### 24.5 Company Profile Completeness

#### Required fields per project statement
The project statement specifies Company Profile attributes as:
`Company ID, Company Name, HR Contact, Website, Approval Status`

#### Gap analysis
| Field | Current Status | Action |
|---|---|---|
| `name` (Company Name) | ✅ Present | None |
| `email` | ✅ Present | None |
| `website` | ✅ Present | None |
| `description` | ✅ Present | None |
| `is_approved` (Approval Status) | ✅ Present | None |
| `contact_person` (HR Contact) | ❌ Missing | **Add** (required) |
| `industry` | ❌ Missing | Optional — **not required** by project statement |

#### Required model addition

```python
# In models.py — add to Company class:
contact_person = db.Column(db.String(100), nullable=True)   # HR Contact
```

#### Required template addition

Add this field to `templates/company/profile.html`:
```html
<div class="mb-3">
  <label class="form-label">HR Contact Person</label>
  <input type="text" name="contact_person" class="form-control"
         value="{{ current_user.contact_person or '' }}">
</div>
```

Update `company_routes.py` profile POST to save the field:
```python
current_user.contact_person = request.form.get('contact_person')
```

**The `industry` field is optional and not required for project statement compliance. It may be added later as an enhancement only.**

---

### 24.6 Mandatory Backend Items

The following items are **mandatory** for project statement compliance. They are documented in detail in Sections 5–18 of this document and summarized here.

| # | Item | Section | Notes |
|---|---|---|---|
| 1 | Flask JSON API layer under `routes/api/` | Section 7 | Thin JSON wrapper over existing logic — do not rewrite business logic |
| 2 | VueJS frontend (Vite + Vue 3) | Section 6 | Single Jinja2 entry point (`vue_app.html`) loads compiled Vue bundle |
| 3 | Redis caching (`flask-caching` + `RedisCache`) | Section 12 | DB 1 for cache; DB 0 for Celery broker |
| 4 | Celery + Redis task queue | Section 5 | Three mandatory tasks below |
| 5 | Daily deadline reminder task | Section 9 | HTML email via `smtplib`, daily at 8:00 AM IST |
| 6 | Monthly activity report task | Section 10 | HTML email to admin on 1st of month, 7:00 AM IST |
| 7 | Async CSV export task | Section 11 | User-triggered, polling for status, required CSV columns |
| 8 | Eligibility validation in `apply_drive` | Section 13 | CGPA, branch, batch checks |
| 9 | Student drive search | Section 14 | Filter by job title, location, branch, company name |
| 10 | Company reject route | Section 15 | Explicit POST route for admin to reject company registration |
| 11 | Resume upload in student profile | Section 18 | `resume_path` field + file upload handler |
| 12 | `contact_person` on Company model | Section 24.5 | HR contact per project statement |

---

### 24.7 Optional Enhancements

The following items are **explicitly optional** and are not required for project statement compliance. Implement only after all mandatory items are complete and time permits.

| Item | Section | Why Optional |
|---|---|---|
| ChartJS dashboard analytics | Section 16, Section 6.6 | Project statement lists ChartJS under "Recommended and/or Optional functionalities" |
| WeasyPrint PDF reports | Section 17 | Project statement lists PDF reports as optional ("Students can choose between HTML and PDF reports") |
| Flower Celery monitoring | Section 5.3 | Monitoring dashboard, not required |
| ATS resume checker | — | Listed as optional in project statement |
| Offer letter generator | — | Listed as optional in project statement |
| Mobile PWA / "Add to desktop" | — | Listed as optional in project statement |
| `industry` field on Company | Section 24.5 | Not required by project statement |
| Pinia / Vuex state management | Section 2 | Vue 3 reactivity is sufficient |
| Axios HTTP client | Section 6.3 | Browser's `fetch` API is sufficient |
| App factory pattern | Section 5.4 | Recommended only if required for Celery/testing |
| Service layer (`services/`) | Section 24.4 | Recommended code organization only |
| JWT-based authentication | Section 24.1 | Only if Vue strategy genuinely requires stateless tokens |
| `role` column on existing models | Section 8.1 | Only if route logic needs string-role switching |

**Recommendation:** Complete all mandatory items first. Attempt optional items only if time permits before the submission deadline.

---

### 24.8 Conflicts Resolved (Authoritative)

| # | Conflict | Resolution |
|---|---|---|
| 1 | JWT vs Session authentication | Session-only is fully compliant. JWT is optional. Existing Flask-Login implementation must remain unchanged. |
| 2 | Unified user table vs separate tables | Three-table structure (Admin, Student, Company) already satisfies the requirement. Do not create a User base table. |
| 3 | ChartJS priority | ChartJS is optional. Not in any mandatory priority list. |
| 4 | PDF generation mandatory vs optional | PDF is optional. Monthly report must be HTML. |
| 5 | Service layer mandatory vs optional | Service layer is recommended code organization only. Do not force a rewrite. |
| 6 | Factory pattern mandatory vs optional | Factory pattern is recommended only if required for Celery/testing. |
| 7 | `industry` field required vs optional | `industry` is optional. Only `contact_person` is required. |
| 8 | Vue session cookie propagation | The Vite dev server proxy allows session cookies to propagate naturally. No token mechanism required. |
| 9 | `flask-mail` vs `smtplib` | Use Python's built-in `smtplib`. Do not install or use `flask-mail`. |
| 10 | `vue.config.js` vs `vite.config.js` | Vite is the sole frontend build tool. There is no `vue.config.js`. |

---

## 25. Complete Cache Invalidation Matrix

> **Authoritative source for cache invalidation.** All cache invalidation examples elsewhere in this document (e.g., Section 12.4) must conform to this matrix. Where an example conflicts with this matrix, the matrix wins.

### Company Operations

| Operation | Cache Keys to Invalidate | Description |
|-----------|------------------------|-------------|
| `admin_routes.approve_company()` | `admin_dashboard`, `company_dashboard_{company_id}`, `drives_list` | Admin approves company registration |
| `admin_routes.reject_company()` | `admin_dashboard`, `company_dashboard_{company_id}`, `drives_list` | Admin rejects company registration |
| `company_routes.update_company_profile()` | `company_dashboard_{company_id}` | Company updates its own profile |

### Drive Operations

| Operation | Cache Keys to Invalidate | Description |
|-----------|------------------------|-------------|
| `admin_routes.create_drive()` | `admin_dashboard`, `drives_list` | Admin creates new drive |
| `admin_routes.edit_drive()` | `admin_dashboard`, `drives_list`, `drive_{drive_id}_details` | Admin edits existing drive |
| `admin_routes.approve_drive()` | `admin_dashboard`, `drives_list`, `drive_{drive_id}_details` | Admin approves drive |
| `admin_routes.close_drive()` | `admin_dashboard`, `drives_list`, `drive_{drive_id}_details` | Admin closes drive |
| `admin_routes.delete_drive()` | `admin_dashboard`, `drives_list` | Admin deletes drive |
| `company_routes.create_drive()` | `company_dashboard_{company_id}`, `drives_list` | Company creates new drive |
| `company_routes.edit_drive()` | `company_dashboard_{company_id}`, `drives_list`, `drive_{drive_id}_details` | Company edits existing drive |

### Application Operations

| Operation | Cache Keys to Invalidate | Description |
|-----------|------------------------|-------------|
| `student_routes.apply_drive()` | `student_dashboard_{student_id}`, `drives_list`, `admin_dashboard` | Student applies to drive |
| `company_routes.update_application()` | `company_dashboard_{company_id}`, `admin_dashboard`, `student_dashboard_{student_id}`, `drives_list` | Company updates application status |
| `student_routes.accept_offer()` | `student_dashboard_{student_id}`, `company_dashboard_{company_id}`, `admin_dashboard`, `drives_list` | Student accepts offer (rejects others) |
| `company_routes.reject_application()` | `company_dashboard_{company_id}`, `admin_dashboard`, `student_dashboard_{student_id}`, `drives_list` | Company rejects application |

### Search Operations

| Operation | Cache Keys to Invalidate | Description |
|-----------|------------------------|-------------|
| `student_routes.drives()` (search) | `search_{query}` | Student searches drives |
| `admin_routes.search_companies()` | `search_{query}` | Admin searches companies |
| `admin_routes.search_students()` | `search_{query}` | Admin searches students |
| `admin_routes.search_drives()` | `search_{query}` | Admin searches drives |

### Cache Key Patterns

- `admin_dashboard` — Admin dashboard statistics
- `student_dashboard_{student_id}` — Student-specific dashboard
- `company_dashboard_{company_id}` — Company-specific dashboard
- `drives_list` — List of available drives
- `drive_{drive_id}_details` — Specific drive details
- `search_{query}` — Search results for a specific query

### Invalidation Priority

1. **Immediate invalidation** — Delete cache keys that are directly modified
2. **Related cache invalidation** — Delete cache keys that depend on the modified data
3. **Broad cache invalidation** — Delete general cache keys that might contain affected data

### Example: Student Application Flow (conforms to matrix)

```python
@student_bp.route('/apply/<int:drive_id>', methods=['POST'])
@login_required
def apply_drive(drive_id):
    # 1. Validate eligibility, deadline, etc.
    # 2. Create application
    # 3. Invalidate caches per Section 25 matrix:
    cache.delete(f'student_dashboard_{current_user.id}')  # Student dashboard
    cache.delete('drives_list')                            # Available drives list
    cache.delete('admin_dashboard')                        # Admin stats
    # 4. Return response
```

### Example: Admin Approves Drive (conforms to matrix)

```python
@admin_bp.route('/approve-drive/<int:drive_id>', methods=['POST'])
@login_required
def approve_drive(drive_id):
    # ... approval logic ...
    # Invalidate caches per Section 25 matrix:
    cache.delete('admin_dashboard')
    cache.delete('drives_list')
    cache.delete(f'drive_{drive_id}_details')
```

### Example: Admin Rejects Company (conforms to matrix)

```python
@admin_bp.route('/reject-company/<int:company_id>', methods=['POST'])
@login_required
def reject_company(company_id):
    # ... rejection logic ...
    # Invalidate caches per Section 25 matrix:
    cache.delete('admin_dashboard')
    cache.delete(f'company_dashboard_{company_id}')
    cache.delete('drives_list')
```

---

## 26. Avoid Unnecessary Refactoring

### Do Not Rewrite Authentication

The current Flask-Login session-based authentication **fully satisfies** the project statement requirement for "role-based access control and authentication using Flask security (session or token)."

- The existing Jinja2 login routes, `@login_required` decorators, and `load_user` function must **not be touched**.
- The Vite dev server proxy (`/api` → Flask) allows the browser session cookie to propagate naturally to the API layer — **no JWT or token mechanism is required**.
- Do not attempt a hybrid on the same endpoints — they serve different clients (Vue vs browser).
- Do not rewrite the login/register forms or their validation logic.

### Do Not Rebuild Database Models

The existing six models (`Admin`, `Student`, `Company`, `PlacementDrive`, `Application`, `ApplicationStatusLog`) already cover all required entities and relationships from the project statement.

- The only model changes needed are the two permitted additions:
  1. `resume_path` to `Student` (one line)
  2. `contact_person` to `Company` (one line)
- Do **not** create a unified user table — the project statement does not require it, and doing so would invalidate all existing queries, relationships, and route logic.
- Adding a `role` column to each model is acceptable if needed for authentication, but is not mandatory.

### Do Not Rewrite Existing Business Logic

The following logic is already correctly implemented and must be **preserved as-is**:

| Logic | Location | Status |
|---|---|---|
| Duplicate application prevention | `student_routes.apply_drive` | ✅ Keep |
| Status transition (Applied→Shortlisted→Selected) | `company_routes.update_application` | ✅ Keep |
| Offer expiry cleanup | `cleanup_expired_offers()` | ✅ Keep |
| Accept offer + reject other applications | `student_routes.accept_offer` | ✅ Keep |
| Max 3 active applications | `student_routes.apply_drive` | ✅ Keep |
| Drive approval gating for companies | `company_routes.check_company_access` | ✅ Keep |

When building the Vue API layer, **call these existing functions or replicate their logic directly** — do not introduce new parallel implementations that could diverge.

---

## 27. Corrected Final Priority Order

> **Authoritative implementation order.** This is the single source of truth for sequencing. The earlier Section 21 checklist is preserved only as a historical planning reference; where Section 21 conflicts with this section, this section wins.

### Priority 1 — Mandatory Core (complete before submission)

> **Note on dependencies:** The factory pattern (task 1.1) is OPTIONAL — see Section 24.3. None of the tasks below require it. Where a task needs to know how your Flask app is constructed, it works with **either** the factory pattern (`create_app()`) **or** a module-level `app = Flask(__name__)`. Pick whichever shape your `app.py` already has; do not refactor just to satisfy a dependency column.

| # | Task | Depends On |
|---|---|---|
| 1.1 | Refactor `app.py` to factory pattern — OPTIONAL (skip if not using Celery/testing) | Nothing |
| 1.2 | Update `config.py` (Redis, Celery, Email) | Nothing |
| 1.3 | Install all dependencies | 1.2 |
| 1.4 | Start Redis, verify `redis-cli ping` | Nothing |
| 1.5 | Create `celery_worker.py` (Section 5.1 — Option A if 1.1 done, Option B otherwise) | 1.2, 1.4 |
| 1.6 | Create `routes/api/` and register with your Flask app (factory `create_app()` OR module-level `app`) | Nothing |
| 1.7 | Implement `auth_api.py` — login endpoint for Vue | 1.6 |
| 1.8 | Scaffold VueJS, configure Vite proxy + output to Flask static | 1.7 |
| 1.9 | Implement Vue Router with role guards | 1.8 |
| 1.10 | Add Redis cache to admin dashboard and drive listing | 1.4 |
| 1.11 | Create `tasks/reminders.py` — daily deadline email | 1.5 |
| 1.12 | Create `tasks/reports.py` — monthly HTML report | 1.5 |
| 1.13 | Create `tasks/exports.py` — async CSV export | 1.5 |
| 1.14 | Create `routes/api/jobs_api.py` — trigger + poll | 1.6, 1.13 |
| 1.15 | Add `utils/validators.py` + call `check_eligibility()` in `apply_drive` | Nothing |
| 1.16 | Add student drive search to `student_routes.drives()` + template | Nothing |
| 1.17 | Add `resume_path` to `Student` model + profile route + template | Nothing |
| 1.18 | Add explicit `reject_company` route + button in manage_companies.html | Nothing |
| 1.19 | Add `contact_person` to `Company` model + profile template + route | Nothing |

### Priority 2 — Service Layer & Profile Completeness (RECOMMENDED, not mandatory)

> **These items are recommended code organization, not required architecture.** Skip if existing route logic is already working and you do not need code reuse between Jinja2 routes and the Vue API layer. Do not force a rewrite of working logic.

| # | Task | Depends On |
|---|---|---|
| 2.1 | Extract `cleanup_expired_offers()` into `services/application_service.py` (only if duplicated) | Priority 1 done |
| 2.2 | Extract `apply_to_drive` and `update_application_status` into service (only if duplicated) | 2.1 |
| 2.3 | Extract `get_available_drives` into `services/drive_service.py` (only if duplicated) | 2.1 |
| 2.4 | Extract monthly report HTML into `services/report_service.py` (only if duplicated) | 2.1 |
| 2.5 | Add cache invalidation `cache.delete()` calls to all write routes per Section 25 matrix | Priority 1 cache done |

### Priority 3 — Vue Feature Completion

| # | Task |
|---|---|
| 3.1 | Build remaining Vue views (all dashboards, forms, tables) consuming JSON API |
| 3.2 | Wire CSV export trigger + polling into Vue student dashboard |
| 3.3 | Ensure Vue demo covers all three roles end-to-end |

### Priority 4 — Optional Enhancements (only if time permits)

> **All items in this priority are explicitly OPTIONAL.** None are required for project statement compliance.

| Enhancement | Effort | Value |
|---|---|---|
| ChartJS charts in dashboards (Section 16) | Low | Medium |
| WeasyPrint PDF monthly report (Section 17) | Medium | Low |
| Flower Celery monitoring dashboard (Section 5.3) | Low | Low |
| ATS resume checker | High | Low |
| Offer letter generator | High | Low |
| Mobile responsive PWA / "Add to desktop" | Medium | Medium |
| `industry` field on Company model | Low | Low |
| JWT-based authentication | Medium | Low |
| Pinia / Vuex state management | Low | Low |
| Axios HTTP client | Low | Low |

---

## 28. Architecture Status

> **One-page executive summary of the final architecture.**

### COMPLIANT

The following compliance decisions have been completed and are reflected throughout this document:

- ✅ Flask-Login session-based authentication is the primary and compliant authentication mechanism (no JWT required)
- ✅ API routes use `@login_required` + `current_user` (Flask-Login) — never client-supplied identity headers
- ✅ Existing three-table user model (Admin, Student, Company) satisfies the "unified user model" requirement — no User base table created
- ✅ Existing business logic preserved as-is (duplicate application prevention, status transitions, offer expiry, accept-offer logic, max 3 active applications, drive approval gating)
- ✅ Flask JSON API layer (`routes/api/`) added as a thin JSON wrapper over existing logic — no parallel implementation
- ✅ VueJS (Vite + Vue 3) is the primary UI layer; Jinja2 used only for the single entry-point HTML
- ✅ Single Jinja2 entry point (`templates/vue_app.html`) serves the compiled Vue bundle
- ✅ Vite is the sole frontend build tool — no `vue.config.js` references remain
- ✅ Redis caching (`flask-caching` + `RedisCache`) on DB 1 for cache, DB 0 for Celery broker
- ✅ Celery + Redis task queue with three mandatory tasks:
  - Daily deadline reminder (`tasks/reminders.py`)
  - Monthly HTML activity report (`tasks/reports.py`)
  - Async CSV export (`tasks/exports.py`)
- ✅ Celery Beat schedule configured for daily reminders (8:00 AM IST) and monthly reports (1st of month, 7:00 AM IST)
- ✅ Celery worker entry point (`celery_worker.py`) supports both factory-pattern (`create_app()`) and module-level `app` — no refactor forced (Section 5.1)
- ✅ Eligibility validation added to `apply_drive` (CGPA, branch, batch)
- ✅ Student drive search added to `student_routes.drives()` with template search bar
- ✅ Explicit company reject route added to `admin_routes.py`
- ✅ Resume upload added to student profile (`resume_path` field on Student model)
- ✅ `contact_person` field added to Company model for HR contact (required per project statement)
- ✅ Cache invalidation matrix (Section 25) is the authoritative source for cache key invalidation; all examples conform to the matrix, and operation labels point to the correct module (`admin_routes` for admin actions, `company_routes` for company self-service)
- ✅ Single authoritative implementation priority list: "Corrected Final Priority Order" (Section 27)
- ✅ Single authoritative compliance amendment: "Final PDF Compliance Amendment" (Section 24)
- ✅ Email uses Python's built-in `smtplib` (not `flask-mail`)
- ✅ Email messages are sent as proper `multipart/alternative` (plain-text + HTML) — uses `set_content` for the text fallback and `add_alternative(..., subtype='html')` for the HTML body, so mail clients render the HTML instead of showing raw tags (Section 9.1)
- ✅ All ChartJS, WeasyPrint, PDF reports, Flower, ATS checker, and offer generator references clearly marked OPTIONAL
- ✅ `requirements.txt` split into Required vs Optional blocks — WeasyPrint and Flower are commented out by default so they are not pulled in by `pip install`
- ✅ SQLAlchemy `or_()` imported from `sqlalchemy` (not accessed as `db.or_`) in every search query — works regardless of how `db` is exposed
- ✅ Section 27 Priority 1 dependency column no longer references task 1.1 (factory pattern) — factory pattern is genuinely optional and blocks nothing
- ✅ Celery config key naming (`CELERY_BROKER_URL` etc.) documented as backwards-compatible; lowercase `broker_url` form noted as the modern preference (Section 5.2)
- ✅ Concrete `@cache.cached` decorator examples provided for every cached endpoint (admin dashboard, student dashboard, drives list, drives-with-search, company dashboard) including the callable `key_prefix` pattern for per-user keys (Section 12.5)

### OPTIONAL

The following enhancements are explicitly optional and not required for project statement compliance:

- ⚪ Factory pattern for `app.py` — recommended only if required for Celery integration, testing, or blueprint organization
- ⚪ Service layer (`services/`) — recommended code organization; extract only when code reuse becomes necessary
- ⚪ ChartJS dashboard analytics (Sections 6.6 and 16)
- ⚪ WeasyPrint PDF monthly report generation (Section 17)
- ⚪ Flower Celery monitoring dashboard (Section 5.3)
- ⚪ ATS resume checker
- ⚪ Offer letter generator
- ⚪ Mobile responsive PWA / "Add to desktop"
- ⚪ `industry` field on Company model (optional enhancement only)
- ⚪ JWT-based authentication (only if Vue strategy genuinely requires stateless tokens)
- ⚪ Pinia / Vuex state management (Vue 3 reactivity is sufficient)
- ⚪ Axios HTTP client (browser's `fetch` API is sufficient)
- ⚪ `role` column on existing models (only if route logic needs string-role switching)

### NOT REQUIRED

The following items are intentionally **excluded** because the project statement does not require them. They must not be introduced:

- 🚫 User base table / unified user table
- 🚫 Database redesign or schema migrations beyond the two permitted additions (`resume_path`, `contact_person`)
- 🚫 Microservices architecture
- 🚫 Docker / containerization
- 🚫 Kubernetes orchestration
- 🚫 CQRS pattern
- 🚫 Repository pattern
- 🚫 Domain-Driven Design (DDD)
- 🚫 Rewrite of working business logic
- 🚫 JWT + Session hybrid on the same endpoint
- 🚫 Client-supplied identity headers (e.g. `X-User-ID`) used for authentication — this is spoofable and forbidden; use Flask-Login `current_user` instead
- 🚫 `vue.config.js` or Vue CLI (project uses Vite only)
- 🚫 `flask-mail` (project uses Python's built-in `smtplib`)
- 🚫 Default installation of WeasyPrint / Flower (they live in the Optional block of `requirements.txt` and must stay commented out unless the related optional feature is being implemented)
- 🚫 Any change to project scope

---

*End of Architecture Status — Placement Portal Application V2*
