# update_docs.py
import os
from pathlib import Path

root = Path(r"c:\Users\Lokesh\OneDrive\Desktop\PROJECT\HabbitTrack")

docs = {}

docs["README.md"] = """# HabitTrack

HabitTrack is a modern, full-stack habit tracking application built with a Flask backend, MySQL database persistence, and a responsive vanilla JavaScript frontend with glassmorphism UI styling.

## Features

### 📊 Weekly Habit Tracker
- **14-Day Calendar Grid View**: Track habits across 14 consecutive days (2-week view) with date and weekday headers.
- **Interactive Checkboxes**: Toggle daily completions with real-time UI updates and optimistic backend synchronization.
- **Habit Management**: Create and delete habits easily.
- **Streak & Rate Tracking**: Displays current streak counts (🔥) and completion percentages for each habit.
- **Week Navigation**: Effortlessly navigate backward and forward through weeks.

### 📈 Analytics & Insights
- **Completion Rate Chart**: Doughnut chart showing overall completed vs. pending tasks.
- **Weekly Trend Chart**: Line chart displaying completion trends across days.
- **Performance Chart**: Bar chart highlighting completion rates per habit.

### 🔐 Authentication & Profiles
- **User Registration & Login**: Account creation with secure password hashing (Werkzeug).
- **Session Management**: Session-based authentication via Flask-Login with HTTP-only cookies.
- **Profile & Settings**: Update user details and toggle preferences (Neon mode, streak reminders, weekly insights).
- **OAuth Ready**: Backend support for Google and Microsoft OAuth login flows.

---

## Technical Stack

- **Backend**: Python, Flask, Flask-Login, Flask-CORS, mysql-connector-python
- **Database**: MySQL (tables: `users`, `habits`, `habit_completions`, `oauth_tokens`, `social_shares`)
- **Frontend**: HTML5, CSS3 (Glassmorphism & CSS Grid), Vanilla JavaScript (ES6+)
- **Visualization**: Chart.js

---

## Quick Start

### 1. Prerequisites
- Python 3.8+
- MySQL Server (running on `localhost:3306`)

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows PowerShell:
.\\venv\\Scripts\\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Database & Environment Configuration
Ensure MySQL is running and create the database:
```sql
CREATE DATABASE habittrack;
```

Copy `.env.example` to `.env` in the `backend/` directory:
```env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/habittrack
SECRET_KEY=your-secret-key-here
```

### 4. Run Application
From the repository root:
```bash
python run.py
```
This automatically initializes the MySQL database tables if they do not exist and starts the server at `http://localhost:5000`.

---

## Project Structure

```
HabitTrack/
├── index.html                  # Main application dashboard
├── styles.css                  # Dashboard glassmorphism styles
├── run.py                      # Application runner and DB initializer
├── README.md                   # Main project overview
├── README_PROFESSIONAL.md      # Professional overview
├── SETUP.md                    # Quick setup reference
├── SETUP_GUIDE.md              # Detailed setup guide
├── DEPLOYMENT.md               # Production deployment guide
├── IMPLEMENTATION_SUMMARY.md   # System architecture & feature summary
├── frontend/
│   ├── app.js                  # Main dashboard logic & habit tracker client
│   ├── login.html              # Standalone login page
│   ├── register.html           # Standalone registration page
│   ├── styles-auth.css         # Auth page styling
│   ├── js/
│   │   └── auth.js             # Standalone auth form handling
│   └── README.md               # Frontend documentation
└── backend/
    ├── app.py                  # Flask app factory and file routing
    ├── config.py               # Configuration settings
    ├── models.py               # Custom MySQL database persistence layer
    ├── requirements.txt        # Python package dependencies
    ├── routes/
    │   ├── auth.py             # User auth & OAuth endpoints
    │   ├── habits.py           # Habit CRUD & completion toggle endpoints
    │   └── social.py           # Social sharing endpoints
    └── README.md               # Backend documentation
```

---

## API Endpoints Summary

### Authentication (`/api/auth`)
- `POST /api/auth/register` — Register a new account
- `POST /api/auth/login` — Sign in user
- `POST /api/auth/logout` — Logout user
- `GET /api/auth/current-user` — Get logged-in user profile
- `GET /api/auth/verify-token` — Verify active session
- `GET /api/auth/google` — Initiate Google OAuth
- `GET /api/auth/google/callback` — Google OAuth callback
- `GET /api/auth/microsoft` — Initiate Microsoft OAuth
- `GET /api/auth/microsoft/callback` — Microsoft OAuth callback

### Habits (`/api/habits`)
- `GET /api/habits` — Fetch user habits & completion history
- `POST /api/habits` — Create new habit
- `GET /api/habits/<id>` — Get specific habit
- `PUT /api/habits/<id>` — Update habit details
- `DELETE /api/habits/<id>` — Delete habit
- `POST /api/habits/<id>/toggle` — Toggle completion state for a given date
- `GET /api/habits/<id>/stats` — Fetch habit statistics

### Social Sharing (`/api/social`)
- `POST /api/social/share/<habit_id>/<platform>` — Prepare social share URL
- `GET /api/social/share/stats` — Get sharing stats
- `GET /api/social/platforms` — Get supported social platforms

---

## License & Usage

Free to use for personal habit tracking and software development learning.
"""

docs["README_PROFESSIONAL.md"] = """# HabitTrack - Professional Full-Stack Application

HabitTrack is a production-ready, full-stack web application designed for tracking daily habits, visualizing user progress, and encouraging personal consistency.

## Highlights & Features

- **Full-Stack Flask & MySQL Architecture**: Custom lightweight MySQL persistence layer supporting relational user models, habit entries, daily completions, OAuth tokens, and share logs.
- **Glassmorphism UI/UX**: Fluid desktop and mobile interfaces with ambient glowing backgrounds and high-contrast typography.
- **14-Day Calendar Tracker**: Grid-aligned weekly habit view with date headers and smooth checkbox interactions.
- **Interactive Analytics**: Integrated Chart.js charts for completion rates, weekly trends, and habit comparison.
- **Robust Security**: Password hashing with Werkzeug, HTTP-only session cookies, input validation, and CORS setup.

## Getting Started

1. **Backend Dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
2. **Environment Configuration**:
   Configure `backend/.env` with your MySQL connection string (`DATABASE_URL`) and `SECRET_KEY`.
3. **Database Setup**:
   Create a MySQL database named `habittrack`.
4. **Run Application**:
   Execute `python run.py` from the root directory and visit `http://localhost:5000`.

## Directory Structure Overview

- `index.html` — Main dashboard
- `styles.css` — Global design tokens & glassmorphism layout
- `frontend/app.js` — Client application state, calendar rendering, charts, & auth handlers
- `backend/app.py` — Flask app creation and static asset serving
- `backend/models.py` — Database connector and models (`User`, `Habit`, `HabitCompletion`, `OAuthToken`, `SocialShare`)
- `backend/routes/` — Modular Flask blueprints (`auth.py`, `habits.py`, `social.py`)
"""

docs["SETUP.md"] = """# HabitTrack Setup Guide

Quick reference for setting up HabitTrack locally.

## Prerequisites
- **Python**: 3.8 or higher
- **MySQL Server**: 5.7+ or 8.0+

## Installation Steps

1. **Navigate to backend and create virtual environment**:
   ```bash
   cd backend
   python -m venv venv
   ```

2. **Activate environment**:
   - Windows PowerShell: `.\\venv\\Scripts\\activate`
   - Linux / macOS: `source venv/bin/activate`

3. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Prepare Database**:
   Log into MySQL and execute:
   ```sql
   CREATE DATABASE habittrack;
   ```

5. **Configure environment variables**:
   Copy `.env.example` to `.env` in `backend/` and update `DATABASE_URL`:
   ```env
   DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/habittrack
   SECRET_KEY=your-secret-key
   ```

6. **Start the application**:
   Return to root folder and run:
   ```bash
   python run.py
   ```

7. **Access the Application**:
   Open `http://localhost:5000` in your browser.
"""

docs["SETUP_GUIDE.md"] = """# HabitTrack Complete Setup & Operations Guide

This guide provides detailed instructions for configuring, running, and testing HabitTrack.

## 1. System Requirements
- Python 3.8+
- MySQL Server 5.7+ / 8.0+
- Modern Browser (Chrome, Firefox, Edge, Safari)

## 2. Environment Setup

### Virtual Environment
```bash
cd backend
python -m venv venv
```
Activate the virtual environment for your platform and install packages:
```bash
pip install -r requirements.txt
```

### Database Configuration
Ensure MySQL is active. Create the database:
```sql
CREATE DATABASE habittrack;
```

Update `backend/.env` with your database credentials:
```env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/habittrack
SECRET_KEY=your-custom-secret-key
```

## 3. Running the Application

Launch the application runner:
```bash
python run.py
```
The runner will:
1. Initialize database tables automatically (`users`, `habits`, `habit_completions`, `oauth_tokens`, `social_shares`).
2. Start the Flask server at `http://localhost:5000`.

## 4. Features & Functionality

- **Dashboard**: `http://localhost:5000/`
- **Habit Calendar**: 14-day tracking view with instant checkbox sync.
- **Analytics View**: Visual charts showing progress, completion percentages, and trends.
- **Profile & Settings**: Account details and UI preference toggles.
- **Standalone Auth Pages**: `http://localhost:5000/frontend/login.html` and `http://localhost:5000/frontend/register.html`.
"""

docs["DEPLOYMENT.md"] = """# HabitTrack Production Deployment Guide

Guide for deploying HabitTrack to production environments.

## Production Checklist

1. **Security**:
   - Set `FLASK_ENV=production` in environment.
   - Use a strong, randomly generated `SECRET_KEY`.
   - Set `SESSION_COOKIE_SECURE=True` when serving over HTTPS.
2. **Database**:
   - Provision a managed MySQL instance (e.g. AWS RDS, GCP Cloud SQL, or DigitalOcean MySQL).
   - Update `DATABASE_URL` with production credentials and SSL options.
3. **WSGI Server**:
   - Run Flask with a production WSGI server such as Gunicorn:
     ```bash
     gunicorn "backend.app:create_app('production')" -b 0.0.0.0:5000 -w 4
     ```
4. **Reverse Proxy & SSL**:
   - Use Nginx or Caddy as a reverse proxy to terminate SSL/TLS and forward requests to Gunicorn.

## Deployment Architecture

```
Client Browser -> HTTPS -> Nginx Reverse Proxy -> Gunicorn (Flask App) -> MySQL Database
```
"""

docs["IMPLEMENTATION_SUMMARY.md"] = """# HabitTrack Implementation Summary

## Overview

HabitTrack has been updated to a complete, full-stack habit tracking application with a Flask backend, MySQL database persistence, and a liquid glassmorphism responsive frontend.

## Key Changes & Enhancements

1. **Backend Integration**:
   - Flask application factory in `backend/app.py`.
   - Custom MySQL database persistence layer in `backend/models.py`.
   - Blueprint routes for `/api/auth`, `/api/habits`, and `/api/social`.
2. **Frontend Features**:
   - 14-day calendar grid view with dates and weekdays.
   - Optimistic daily habit completion toggles with server rollback protection.
   - Habit statistics (streaks, completion percentages).
   - Chart.js analytics for completion rate, trend lines, and habit performance.
   - User profile settings form and theme preference toggles.
3. **Database Schema**:
   - `users`: User profiles and authentication.
   - `habits`: User-created habits.
   - `habit_completions`: Daily completion logs.
   - `oauth_tokens`: OAuth provider integrations.
   - `social_shares`: Social media share history.
"""

docs["backend/README.md"] = """# HabitTrack Backend Documentation

## Overview

The HabitTrack backend is built with Python and Flask. It provides RESTful API endpoints for authentication, habit management, and social media sharing integration.

## Folder Structure

```
backend/
├── app.py              # Application factory and static asset routing
├── config.py           # Application configurations (Dev, Prod, Test)
├── models.py           # MySQL database connection and custom ORM layer
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
└── routes/
    ├── auth.py         # Authentication & OAuth endpoints
    ├── habits.py       # Habit CRUD & completion toggle endpoints
    └── social.py       # Social sharing endpoints
```

## Setup & Running

1. Install dependencies: `pip install -r requirements.txt`
2. Configure `backend/.env` with `DATABASE_URL` and `SECRET_KEY`.
3. Start via root runner: `python run.py` or direct backend start: `python app.py`.
"""

docs["frontend/README.md"] = """# HabitTrack Frontend Documentation

## Overview

The HabitTrack frontend is built using standard web technologies (HTML5, CSS3, Vanilla JavaScript) and features a modern liquid glassmorphism visual design.

## Folder Structure

```
frontend/
├── app.js              # Main dashboard script (calendar grid, habits, charts, settings)
├── login.html          # Standalone login page
├── register.html       # Standalone registration page
├── styles-auth.css     # Standalone auth page styling
└── js/
    └── auth.js         # Standalone auth form handling
```

## Features

- **Dashboard**: Served at `/` or `/index.html`.
- **Habit Calendar**: 14-day tracking view with instant checkbox toggles.
- **Analytics**: Doughnut, line, and bar charts powered by Chart.js.
- **Settings**: Profile update form and local preference toggles.
"""

for rel_path, content in docs.items():
    file_path = root / rel_path
    file_path.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"Successfully updated {rel_path}")

print("All documentation files updated successfully!")
