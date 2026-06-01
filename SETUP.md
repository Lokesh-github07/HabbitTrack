# 🎯 HabitTrack - Complete Setup Guide

Welcome to HabitTrack! This guide will help you set up the complete application with all features.

## 📋 System Requirements

- **Python**: 3.8 or higher
- **PostgreSQL**: 12 or higher
- **Node.js**: Optional (for local server)
- **Git**: For version control
- **Browser**: Modern web browser (Chrome, Firefox, Safari, Edge)

## 🚀 Quick Start (5 minutes)

### Step 1: Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment file
cp .env.example .env
```

**Edit `.env` file with:**
```env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-random-secret-key-here
DATABASE_URL=postgresql://postgres:password@localhost:5432/habittrack
```

### Step 2: Database Setup

```bash
# Create PostgreSQL database
psql -U postgres
CREATE DATABASE habittrack;
\q
```

### Step 3: Start Backend

```bash
# From backend directory
python app.py
```

Backend will run at `http://localhost:5000`

### Step 4: Open Frontend

Navigate to `frontend/login.html` in your browser

## 📦 Installation Details

### Backend Installation

1. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   Packages installed:
   - Flask 2.3.3
   - PostgreSQL driver (psycopg2)
   - SQLAlchemy ORM
   - Flask-Login
   - CORS support
   - OAuth2 libraries

2. **Create PostgreSQL Database**
   ```bash
   psql -U postgres -c "CREATE DATABASE habittrack;"
   ```

3. **Configure Environment Variables**
   - Copy `.env.example` to `.env`
   - Update database connection string
   - Add OAuth credentials (see below)

4. **Start Flask Server**
   ```bash
   python app.py
   ```

### Frontend Setup

The frontend is static HTML/CSS/JS and doesn't require installation.

**Option 1: Open directly**
- Open `frontend/index.html` in browser

**Option 2: Use local server (recommended)**
   ```bash
   # Python
   cd frontend
   python -m http.server 3000
   
   # Node.js
   npx http-server -p 3000
   ```

Then open `http://localhost:3000`

## 🔐 OAuth Setup

### Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project: "HabitTrack"
3. Enable OAuth 2.0:
   - Click "Create Credentials"
   - Choose "OAuth client ID"
   - Application type: "Web application"
4. Add authorized redirect URIs:
   ```
   http://localhost:5000/api/auth/google/callback
   ```
5. Copy Client ID and Secret to `.env`:
   ```env
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   ```

### Microsoft OAuth

1. Go to [Azure Portal](https://portal.azure.com/)
2. Register application: "HabitTrack"
3. Create client secret:
   - Certificates & secrets → New client secret
4. Add redirect URI:
   ```
   http://localhost:5000/api/auth/microsoft/callback
   ```
5. Copy to `.env`:
   ```env
   MICROSOFT_CLIENT_ID=your-client-id
   MICROSOFT_CLIENT_SECRET=your-client-secret
   ```

## 📁 Project Structure

```
HabitTrack/
├── backend/
│   ├── app.py                  # Main Flask application
│   ├── config.py               # Configuration settings
│   ├── models.py               # Database models
│   ├── requirements.txt         # Python dependencies
│   ├── .env.example             # Environment template
│   ├── .env                     # Your configuration (don't commit)
│   ├── routes/
│   │   ├── auth.py             # Authentication routes
│   │   ├── habits.py           # Habit CRUD routes
│   │   └── social.py           # Social sharing routes
│   ├── README.md               # Backend documentation
│   └── __init__.py
│
├── frontend/
│   ├── index.html              # Main dashboard
│   ├── login.html              # Login page
│   ├── register.html           # Registration page
│   ├── styles.css              # Main stylesheet
│   ├── styles-auth.css         # Auth pages stylesheet
│   ├── js/
│   │   └── auth.js             # Authentication logic
│   ├── README.md               # Frontend documentation
│   └── assets/
│       └── (future images, icons)
│
└── README.md                   # Project overview
```

## 🎨 Design Overview

### Color Palette
```css
Primary Black:    #000000
Primary White:    #FFFFFF
Primary Green:    #00D084
Secondary Green:  #00B366
Dark Green:       #009950
Light Green:      #E8F5EE
```

### Layout
- Responsive design for all screen sizes
- Sidebar navigation with user profile
- Modern card-based UI
- Grid-based habit tracker
- Chart-based analytics

## 🔑 Key Features Walkthrough

### 1. Authentication Flow

**Registration:**
1. User visits `login.html`
2. Clicks "Sign up here" link
3. Fills registration form
4. Backend validates and creates account
5. Auto-login and redirect to dashboard

**Login:**
1. Enter email and password
2. Backend verifies credentials
3. Session created and stored
4. Redirect to dashboard with user data

**OAuth:**
1. Click Google or Microsoft button
2. Redirected to provider
3. User authenticates
4. Returned to backend callback
5. User created/logged in automatically

### 2. Habit Tracking

**Add Habit:**
1. Enter habit name in tracker
2. Click "+ Add Habit"
3. Backend stores in database
4. Appears in tracker grid

**Track Daily:**
1. Check boxes for each day
2. Frontend saves to localStorage
3. Backend syncs on page load

**View Progress:**
1. See completion rate
2. Track streaks
3. View statistics

### 3. Social Sharing

**Share Achievement:**
1. Go to Analytics
2. Click social platform
3. Pre-filled message generated
4. Opens share dialog
5. User completes post

**Supported Platforms:**
- Twitter/X
- Facebook
- LinkedIn
- Reddit
- WhatsApp
- Telegram

## 🔒 Security Features

✅ Password hashing (Werkzeug)
✅ JWT authentication
✅ CORS protection  
✅ SQL injection prevention
✅ Session management
✅ OAuth 2.0 compliance
✅ Environment variable isolation
✅ Secure cookies (production)

## 💾 Database Schema

### Users Table
```sql
id, username, email, password_hash
google_id, microsoft_id
first_name, last_name, avatar_url
is_active, email_verified
created_at, updated_at
```

### Habits Table
```sql
id, user_id, name, description
created_at, updated_at
```

### Completions Table
```sql
id, habit_id, date, completed, created_at
```

### OAuth Tokens Table
```sql
id, user_id, provider
access_token, refresh_token, expires_at
created_at, updated_at
```

## 🧪 Testing

### Test Registration
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### Test Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Test Habit Creation
```bash
curl -X POST http://localhost:5000/api/habits \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Morning Exercise",
    "description": "30 minutes of cardio"
  }'
```

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| Backend won't start | Check Python version (3.8+), PostgreSQL running |
| Database connection error | Verify DATABASE_URL, check psycopg2 installed |
| CORS errors | Ensure backend running, check API_BASE_URL in frontend |
| OAuth errors | Verify redirect URIs in provider settings |
| Stuck on login | Clear localStorage, check network tab |
| Habit not saving | Check backend logs for errors |

## 📊 Performance Tips

- Minimize CSS/JS in production
- Cache static assets
- Lazy load images
- Optimize database queries
- Use CDN for external libraries
- Compress responses

## 🚀 Deployment

### Heroku (Backend)
```bash
heroku login
heroku create habittrack-backend
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
```

### Netlify (Frontend)
- Connect GitHub repo
- Build command: (empty for static)
- Deploy directory: `frontend`
- Click Deploy

### Docker
```bash
docker build -t habittrack .
docker run -p 5000:5000 -e DATABASE_URL=... habittrack
```

## 📚 Documentation

- [Backend Docs](backend/README.md)
- [Frontend Docs](frontend/README.md)
- [API Reference](backend/README.md#api-endpoints)

## 🆘 Getting Help

1. Check [Troubleshooting](#-common-issues)
2. Review backend logs: `FLASK_DEBUG=True`
3. Check browser console: F12
4. Review GitHub issues
5. Contact support

## ✅ Verification Checklist

After setup, verify:
- [ ] Backend running at http://localhost:5000
- [ ] Frontend accessible at http://localhost:3000
- [ ] Can access `/api/health`
- [ ] Can navigate to login page
- [ ] OAuth buttons visible
- [ ] Can register new account
- [ ] Can login with email/password
- [ ] Dashboard displays correctly
- [ ] Can add habits
- [ ] Can check off completions
- [ ] Can view analytics
- [ ] Can share to social media

## 🎓 Next Steps

1. Customize color scheme if desired
2. Add your OAuth credentials
3. Test all features thoroughly
4. Customize habit templates
5. Deploy to production

## 📞 Support

For issues, questions, or suggestions:
- Email: support@habittrack.local
- GitHub: Issues tab
- Documentation: See backend/README.md and frontend/README.md

---

**Happy habit tracking!** 🎯
