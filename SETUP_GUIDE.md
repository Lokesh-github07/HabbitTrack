# HabitTrack Setup Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MySQL Server
- Node.js (optional, for frontend tooling)

### Step 1: Database Setup

1. Open MySQL and create a database:
```sql
CREATE DATABASE habittrack;
```

2. The application will automatically create all tables when you run it.

### Step 2: Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a .env file from .env.example:
```bash
cp .env.example .env
```

3. Update .env with your MySQL credentials:
```
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/habittrack
SECRET_KEY=your-secure-secret-key
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Start the Flask server:
```bash
python -m flask run
```

The server will run on `http://localhost:5000`

### Step 3: Frontend Setup

1. Open `index.html` in your browser or serve it with a local server:
```bash
# Using Python 3
python -m http.server 8000

# Using Python 2
python -m SimpleHTTPServer 8000
```

2. Navigate to `http://localhost:8000`

3. Click "Sign up" to create an account or login with existing credentials

## 📋 Features

### Authentication
- ✅ User registration with email validation
- ✅ Secure password hashing
- ✅ Login/Logout functionality
- ✅ Session management
- 🔄 OAuth integration ready (Google, Microsoft)

### Habit Tracking
- ✅ Add and delete habits
- ✅ Daily completion tracking with checkbox grid
- ✅ 2-week calendar view
- ✅ Streak counting
- ✅ Completion rate calculation

### Analytics
- ✅ Completion rate pie chart
- ✅ Weekly trend line chart
- ✅ Performance bar chart
- ✅ Real-time statistics

### Responsive Design
- ✅ Mobile-friendly interface
- ✅ Tablet optimized
- ✅ Desktop professional layout

## 🗄️ Database Schema

### Users Table
```sql
- id (Primary Key)
- username (Unique)
- email (Unique)
- password_hash
- first_name
- last_name
- avatar_url
- is_active
- email_verified
- created_at
- updated_at
```

### Habits Table
```sql
- id (Primary Key)
- user_id (Foreign Key)
- name
- description
- created_at
- updated_at
```

### Habit Completions Table
```sql
- id (Primary Key)
- habit_id (Foreign Key)
- date
- completed (Boolean)
- created_at
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/current-user` - Get current user info
- `GET /api/auth/verify-token` - Verify session

### Habits
- `GET /api/habits` - Get all user habits
- `POST /api/habits` - Create new habit
- `GET /api/habits/<id>` - Get specific habit
- `PUT /api/habits/<id>` - Update habit
- `DELETE /api/habits/<id>` - Delete habit
- `POST /api/habits/<id>/complete` - Mark habit as complete
- `DELETE /api/habits/<id>/complete/<date>` - Remove completion

## 🎨 Customization

### Colors
Edit the CSS variables in `styles.css`:
```css
:root {
    --primary-color: #00D084;
    --primary-dark: #00A366;
    /* ... other colors ... */
}
```

### Font Family
Update the font-family in `body` selector in CSS files

## 🔒 Security Notes

1. **Password Requirements**: Minimum 8 characters
2. **Session Management**: Cookies are HTTP-only
3. **CORS**: Configure for your domain in production
4. **HTTPS**: Enable in production (SESSION_COOKIE_SECURE = True)

## 🐛 Troubleshooting

### MySQL Connection Error
- Ensure MySQL is running
- Check DATABASE_URL in .env
- Verify credentials

### Port Already in Use
- Flask: `python -m flask run --port 5001`
- Frontend: `python -m http.server 8001`

### CORS Errors
- Ensure Flask-CORS is installed
- Check frontend URL in API_BASE_URL constant

## 📱 Responsive Breakpoints

- Desktop: 1024px and above
- Tablet: 768px - 1023px
- Mobile: Below 768px
- Small Mobile: Below 480px

## 🚀 Deployment

1. Update SECRET_KEY in production
2. Set FLASK_ENV=production
3. Enable HTTPS and secure cookies
4. Configure proper database with backups
5. Use a production WSGI server (Gunicorn, uWSGI)
6. Set up proper logging

## 📞 Support

For issues or questions, refer to the code comments or check the API responses for error messages.

Happy habit tracking! 🎉
