# HabitTrack Frontend

## Overview
Modern, responsive web frontend for HabitTrack with authentication and social sharing features.

## Features
- ✨ Black, white, and green aesthetic design
- 🔐 Email/Password authentication
- 🔗 OAuth integration (Google, Microsoft)
- 📊 Analytics and insights dashboard
- 📱 Social media sharing (Twitter, Facebook, LinkedIn, Reddit, WhatsApp, Telegram)
- 📅 Weekly habit tracker
- 🎯 Progress tracking and statistics

## Project Structure
```
frontend/
├── index.html              # Main dashboard
├── login.html              # Login page
├── register.html           # Registration page
├── styles.css              # Main stylesheet (dark theme)
├── styles-auth.css         # Authentication pages stylesheet
├── js/
│   └── auth.js             # Authentication JavaScript
└── assets/
    └── (images, icons, etc)
```

## Setup

### 1. Ensure Backend is Running
The frontend expects the backend API at `http://localhost:5000`

### 2. Open in Browser
Simply open `index.html` in your web browser, or use a local server:

```bash
# Using Python
python -m http.server 3000

# Using Node.js
npx http-server -p 3000
```

Then navigate to `http://localhost:3000`

## Color Theme
- **Primary Black**: #000000
- **Primary White**: #FFFFFF
- **Primary Green**: #00D084
- **Secondary Green**: #00B366
- **Dark Green**: #009950
- **Light Green**: #E8F5EE

## Pages

### Login Page (`login.html`)
- Email/Password login form
- Google OAuth button
- Microsoft OAuth button
- Link to registration

### Registration Page (`register.html`)
- Full registration form
- Email verification
- OAuth integration
- Terms of service checkbox

### Dashboard (`index.html`)
- Sidebar with user profile
- Weekly habit tracker
- Analytics section with charts
- Contribution graph
- Social sharing options

## Features Explanation

### Authentication Flow
1. User registers or logs in
2. User data stored in localStorage
3. API tokens managed server-side
4. OAuth redirects handled by backend

### Social Sharing
Share habit progress to:
- **Twitter/X**: Tweet your achievements
- **Facebook**: Post to Facebook
- **LinkedIn**: Share professional progress
- **Reddit**: Post to subreddits
- **WhatsApp**: Send to contacts
- **Telegram**: Share with channels

### Habit Tracking
- Add daily habits to track
- Check off completions
- View weekly overview
- Track long-term progress

### Analytics
- Habit completion rates
- Weekly trends
- Performance metrics
- Contribution calendar
- Statistics dashboard

## API Integration

The frontend communicates with the backend at:
```
http://localhost:5000/api
```

### Key Endpoints Used
- `/auth/register` - New user registration
- `/auth/login` - User login
- `/auth/logout` - User logout
- `/auth/google` - Google OAuth
- `/auth/microsoft` - Microsoft OAuth
- `/habits` - Habit management
- `/social/share/<habit_id>/<platform>` - Share habit
- `/social/platforms` - Get sharing platforms

## Responsive Design
- Desktop: Full layout with sidebar
- Tablet: Optimized grid layout
- Mobile: Simplified mobile-friendly interface

## Browser Support
- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile browsers: iOS Safari, Chrome Mobile

## Troubleshooting

### Can't Connect to Backend
- Ensure backend is running on `http://localhost:5000`
- Check browser console for CORS errors
- Verify API_BASE_URL in auth.js

### Stuck on Login Page
- Clear localStorage: `localStorage.clear()`
- Check user data: `localStorage.getItem('user')`
- Verify backend connection

### Social Sharing Not Working
- Allow pop-ups in browser
- Check internet connection
- Verify platform is enabled in backend

## Development

### Modifying Styles
Edit `styles.css` for main theme and `styles-auth.css` for authentication pages.

### Adding New Features
1. Create new page in frontend
2. Add API endpoint in backend
3. Call endpoint from JavaScript
4. Update UI accordingly

### Local Testing
Use browser DevTools:
- F12 to open developer tools
- Console tab for JavaScript errors
- Network tab for API calls
- Application tab for localStorage

## Security Notes
- Never commit `.env` file with secrets
- Clear localStorage on logout
- Use HTTPS in production
- Enable secure cookies for production
- Validate all user input server-side

## Performance
- Lazy load images
- Minimize CSS/JS files
- Cache static assets
- Optimize database queries
- Use CDN for libraries

## Future Enhancements
- Dark/Light theme toggle
- Mobile app (React Native/Flutter)
- Email notifications
- Advanced analytics
- Habit templates
- Team challenges
- Habit syncing across devices

## Support
For issues or feature requests, contact the development team.
