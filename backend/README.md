# HabitTrack Backend Setup Guide

## Overview
This is a Flask-based backend for the HabitTrack application with authentication (email, Google OAuth, Microsoft OAuth) and social sharing features.

## Prerequisites
- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)

## Installation Steps

### 1. Clone and Navigate to Backend Directory
```bash
cd backend
```

### 2. Create a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up PostgreSQL Database
```bash
# Create database
psql -U postgres
CREATE DATABASE habittrack;
\q
```

### 5. Configure Environment Variables
Copy `.env.example` to `.env` and update with your values:

```bash
cp .env.example .env
```

Edit `.env`:
```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-unique-secret-key-change-in-production

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/habittrack

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5000/api/auth/google/callback

# Microsoft OAuth
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
MICROSOFT_REDIRECT_URI=http://localhost:5000/api/auth/microsoft/callback

# Server
PORT=5000
HOST=0.0.0.0
FRONTEND_URL=http://localhost:3000
```

### 6. Setting Up OAuth Credentials

#### Google OAuth
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable OAuth 2.0
4. Create OAuth 2.0 credentials (Web application)
5. Add authorized redirect URIs:
   - `http://localhost:5000/api/auth/google/callback`
6. Copy Client ID and Client Secret to `.env`

#### Microsoft OAuth
1. Go to [Azure Portal](https://portal.azure.com/)
2. Register a new application
3. Create a client secret
4. Add redirect URIs:
   - `http://localhost:5000/api/auth/microsoft/callback`
5. Copy Application (client) ID and client secret to `.env`

### 7. Initialize Database
```bash
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

### 8. Run the Backend Server
```bash
python app.py
```

The backend will be available at `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login with email/password
- `POST /api/auth/logout` - Logout
- `GET /api/auth/google` - Start Google OAuth
- `GET /api/auth/google/callback` - Google OAuth callback
- `GET /api/auth/microsoft` - Start Microsoft OAuth
- `GET /api/auth/microsoft/callback` - Microsoft OAuth callback
- `GET /api/auth/me` - Get current user
- `POST /api/auth/verify-email` - Verify email

### Habits
- `GET /api/habits` - Get all habits
- `POST /api/habits` - Create habit
- `GET /api/habits/<id>` - Get habit
- `PUT /api/habits/<id>` - Update habit
- `DELETE /api/habits/<id>` - Delete habit
- `POST /api/habits/<id>/toggle` - Toggle completion
- `GET /api/habits/<id>/stats` - Get habit stats

### Social Sharing
- `POST /api/social/share/<habit_id>/<platform>` - Share habit
- `GET /api/social/share/stats` - Get sharing stats
- `GET /api/social/platforms` - Get available platforms

## Database Models

### User
- id, username, email, password_hash
- google_id, microsoft_id (for OAuth)
- first_name, last_name, avatar_url
- is_active, email_verified
- created_at, updated_at

### Habit
- id, user_id, name, description
- created_at, updated_at

### HabitCompletion
- id, habit_id, date, completed
- created_at

### OAuthToken
- id, user_id, provider, access_token, refresh_token, expires_at

### SocialShare
- id, user_id, habit_id, platform, message, shared_at

## Development Tips

### Reset Database
```bash
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.drop_all()
...     db.create_all()
>>> exit()
```

### View Logs
Enable debug mode in `.env`:
```env
FLASK_DEBUG=True
```

### Test API Endpoints
Use Postman or curl:
```bash
# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

## Deployment

### For Production
1. Set `FLASK_ENV=production`
2. Generate a secure `SECRET_KEY`
3. Use a production database (PostgreSQL)
4. Use a WSGI server (Gunicorn)
5. Configure HTTPS
6. Set `SESSION_COOKIE_SECURE=True`

### Deploy with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:create_app()
```

## Troubleshooting

### Database Connection Error
- Check PostgreSQL is running
- Verify DATABASE_URL in .env
- Ensure database exists

### OAuth Redirect URI Mismatch
- Verify redirect URIs match in OAuth provider settings
- Check .env REDIRECT_URI values

### CORS Errors
- Frontend and backend must have compatible CORS settings
- Check FRONTEND_URL in backend .env
- Ensure credentials are included in frontend requests

## Support
For issues, check the logs or review the API documentation.
