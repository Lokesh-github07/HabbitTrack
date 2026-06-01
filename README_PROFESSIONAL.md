# HabitTrack - Professional Habit Tracking Application

A modern, responsive, and fully functional habit tracking application built with Flask and vanilla JavaScript. Track your daily habits, visualize progress, and build better routines.

## ✨ Features

### 🔐 Authentication & User Management
- **User Registration** - Create account with email and password
- **Secure Login** - Password hashing with Werkzeug
- **Session Management** - Persistent user sessions
- **User Profile** - Store and display user information

### 📊 Habit Tracking
- **Add/Delete Habits** - Easy habit management
- **Daily Checkboxes** - Mark habits as complete
- **14-Day Calendar View** - See your habits for two weeks
- **Streak Counter** - Track your longest streaks
- **Completion Rate** - Calculate habit completion percentage

### 📈 Analytics & Insights
- **Pie Chart** - Overall completion rate visualization
- **Line Chart** - Weekly trend analysis
- **Bar Chart** - Individual habit performance
- **Real-time Statistics** - Instant progress updates

### 🎨 Modern UI/UX
- **Professional Design** - Clean, modern interface
- **Fully Responsive** - Works on desktop, tablet, and mobile
- **Dark Navigation** - Professional sidebar navigation
- **Interactive Elements** - Smooth animations and transitions
- **Intuitive Controls** - User-friendly buttons and forms

### 🔧 Technical Features
- **MySQL Database** - Robust data persistence
- **RESTful API** - Clean API design
- **CORS Enabled** - Cross-origin support
- **Input Validation** - Secure form handling
- **Error Handling** - Comprehensive error management

## 🚀 Quick Start

### Requirements
- Python 3.8+
- MySQL 5.7+
- Modern Web Browser

### Installation

1. **Clone or Download Project**
```bash
cd HabitTrack
```

2. **Backend Setup**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
```

3. **Configure Database**
Edit `backend/.env`:
```
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/habittrack
```

4. **Create Database**
```sql
CREATE DATABASE habittrack;
```

5. **Run Application**
```bash
cd ..
python run.py
```

6. **Access Application**
- Backend: `http://localhost:5000`
- Frontend: Open `index.html` in browser or serve with:
```bash
python -m http.server 8000
```

Then visit `http://localhost:8000`

## 📱 Demo Credentials

After running `python run.py`, use these credentials:
- **Email**: demo@habittrack.com
- **Password**: Demo@123456

## 🗂️ Project Structure

```
HabitTrack/
├── index.html              # Main dashboard
├── styles.css              # Main styles
├── app.js                  # Dashboard logic
├── run.py                  # Application runner
├── SETUP_GUIDE.md          # Detailed setup guide
├── README.md               # This file
│
├── frontend/
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   ├── styles-auth.css     # Auth page styles
│   └── js/
│       └── auth.js         # Authentication logic
│
└── backend/
    ├── app.py              # Flask application
    ├── config.py           # Configuration
    ├── models.py           # Database models
    ├── requirements.txt    # Python dependencies
    ├── .env.example        # Environment template
    └── routes/
        ├── auth.py         # Authentication endpoints
        ├── habits.py       # Habit endpoints
        └── social.py       # Social features (future)
```

## 🔌 API Endpoints

### Authentication
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/auth/register` | Create new account |
| POST | `/api/auth/login` | Login user |
| POST | `/api/auth/logout` | Logout user |
| GET | `/api/auth/current-user` | Get user info |
| GET | `/api/auth/verify-token` | Verify session |

### Habits
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/habits` | Get all habits |
| POST | `/api/habits` | Create habit |
| GET | `/api/habits/<id>` | Get specific habit |
| PUT | `/api/habits/<id>` | Update habit |
| DELETE | `/api/habits/<id>` | Delete habit |

## 🎨 UI Components

### Login Page
- Professional login form
- Registration link
- Social login options (ready)
- Form validation
- Error messages
- Illustration side panel

### Dashboard
- Sidebar navigation
- User profile section
- Weekly habit tracker
- Analytics section
- Real-time charts
- Responsive layout

## 💾 Database Schema

### Users
```sql
- id (INT PRIMARY KEY)
- username (VARCHAR UNIQUE)
- email (VARCHAR UNIQUE)
- password_hash (VARCHAR)
- first_name (VARCHAR)
- last_name (VARCHAR)
- avatar_url (VARCHAR)
- is_active (BOOLEAN)
- created_at (DATETIME)
- updated_at (DATETIME)
```

### Habits
```sql
- id (INT PRIMARY KEY)
- user_id (INT FOREIGN KEY)
- name (VARCHAR)
- description (TEXT)
- created_at (DATETIME)
- updated_at (DATETIME)
```

### Habit Completions
```sql
- id (INT PRIMARY KEY)
- habit_id (INT FOREIGN KEY)
- date (DATE)
- completed (BOOLEAN)
- created_at (DATETIME)
```

## 🛡️ Security Features

- ✅ Password hashing with Werkzeug
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ CSRF protection ready
- ✅ Session-based authentication
- ✅ HTTP-only cookies
- ✅ Input validation
- ✅ CORS configuration
- ✅ Secure password requirements (min 8 chars)

## 📱 Responsive Design

- **Desktop** (1024px+): Full sidebar with calendar grid
- **Tablet** (768px-1023px): Adjusted layout
- **Mobile** (480px-767px): Optimized for small screens
- **Small Mobile** (<480px): Stacked layout

## 🎯 Browser Compatibility

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Mobile Browsers: ✅ Full support

## 🔄 Technologies Used

### Backend
- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **Flask-Login** - User session management
- **Flask-CORS** - Cross-origin support
- **PyMySQL** - MySQL driver
- **Werkzeug** - Security utilities

### Frontend
- **HTML5** - Markup
- **CSS3** - Styling with variables
- **JavaScript (Vanilla)** - Logic
- **Chart.js** - Analytics charts
- **LocalStorage** - Client-side persistence

### Database
- **MySQL** - Primary database

## 🚀 Performance

- Lightweight responsive design
- Efficient database queries
- Client-side caching
- Minimal external dependencies
- Fast page load times
- Optimized animations

## 📚 Learning Resources

This project demonstrates:
- Flask application structure
- RESTful API design
- Database relationships
- Authentication systems
- Responsive web design
- Chart.js integration
- Form validation
- Error handling

## 🐛 Troubleshooting

### Port Already in Use
```bash
python -m flask run --port 5001
```

### MySQL Connection Error
- Verify MySQL is running
- Check credentials in .env
- Ensure database exists

### CORS Errors
- Clear browser cache
- Check API_BASE_URL in frontend code
- Verify Flask-CORS is installed

## 📈 Future Enhancements

- [ ] OAuth integration (Google, Microsoft)
- [ ] Export reports (PDF, CSV)
- [ ] Social features (share, compete)
- [ ] Mobile app (React Native)
- [ ] Dark mode
- [ ] Advanced analytics
- [ ] Email notifications
- [ ] Habit recommendations

## 📄 License

Open source project - Feel free to use and modify

## 💬 Support

For issues or questions:
1. Check SETUP_GUIDE.md
2. Review API documentation
3. Check browser console for errors
4. Verify database configuration

## 🎉 Getting Started

1. Run `python run.py`
2. Open browser to `http://localhost:8000`
3. Register or login with demo@habittrack.com
4. Start tracking habits!

---

**Happy Habit Tracking!** 🚀

Built with ❤️ for productivity and self-improvement.
