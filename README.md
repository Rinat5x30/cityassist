# CityAssist - City Issue Reporting System

A Django web application for citizens to report urban issues with photo upload, AI classification (mock), and department tracking.

## Features

- **Report Submission**: Upload photos, add address/description, auto GPS detection
- **AI Classification**: Mock AI categorizes issues (road damage, trash overflow, etc.)
- **Department Assignment**: Automatic routing to relevant city departments
- **Status Tracking**: Citizens can track report status via unique link
- **Department Portal**: Departments can update status and add comments
- **Admin Dashboard**: Full Django admin with filters and search

## Project Structure

```
cityassist/
├── cityassist/          # Django project settings
├── reports/             # Main application
│   ├── models.py        # Department, Category, Report, StatusHistory, AIClassification
│   ├── views.py         # Home, tracking, department views
│   ├── urls.py          # URL routing
│   ├── admin.py         # Admin configuration
│   ├── utils.py         # Mock AI, email, token generation
│   └── management/      # Custom commands
├── templates/           # Django templates
│   ├── base.html
│   └── reports/
│       ├── home.html
│       ├── tracking.html
│       └── department.html
├── static/              # CSS, JS
└── media/               # Uploaded photos
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Migrations

```bash
python manage.py migrate
```

### 3. Seed Initial Data (Departments & Categories)

```bash
python manage.py seed_data
```

### 4. Create Superuser

```bash
python manage.py createsuperuser
```

### 5. Run Development Server

```bash
python manage.py runserver
```

### 6. Access the Application

- **Home Page (Submit Report)**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
  - Username: `admin`
  - Password: `admin123`

### 7. Secure the Environment

- Copy `.env.example` to `.env` and keep the real `.env` out of git.
- Set `SECRET_KEY`, `OPENAI_API_KEY`, `ALLOWED_HOSTS`, and `CSRF_TRUSTED_ORIGINS` before publishing.
- Do not commit `db.sqlite3` or uploaded files in `media/`.

## Usage Flow

1. **Citizen submits report** via home page (`/`)
   - Upload photo, enter address & description
   - Optional: Get GPS coordinates
   - AI mock classification assigns category & department

2. **Redirect to tracking page** (`/track/<citizen_token>/`)
   - View report status, photo, location map
   - See AI classification results
   - View status history

3. **Department updates status** via department page (`/r/<dept_token>/`)
   - View full report details
   - Update status (Accept → In Progress → Resolved/Rejected)
   - Add status change comments

## Database

Defaults to **SQLite** for easy local development.

To use **PostgreSQL**:
1. Set `USE_POSTGRES=true` in environment
2. Configure `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
3. Run migrations

## Models

- **Department**: City departments with email/phone
- **Category**: Issue types linked to departments
- **Report**: Core model with UUID, tokens, status, priority, GPS
- **StatusHistory**: Audit trail of status changes
- **AIClassification**: Mock AI results

## API Endpoints

| Route | Description |
|-------|-------------|
| `/` | Report submission form |
| `/submit/` | POST: Submit new report |
| `/track/<citizen_token>/` | Citizen tracking page |
| `/r/<dept_token>/` | Department view page |
| `/r/<dept_token>/update/` | POST: Update status |
| `/api/mock-classify/` | Test: Get mock AI classification |
| `/admin/` | Django admin panel |

## Technology Stack

- **Backend**: Django 6.0+
- **Database**: SQLite (default) / PostgreSQL (optional)
- **Frontend**: Django Templates, Bootstrap 5, Leaflet.js
- **Maps**: OpenStreetMap via Leaflet.js
- **Images**: Pillow for image handling

## License

MIT License
