# HabitTrack authentication fixes

## Fixed
- JavaScript startup error caused by using `monday()` before declaration.
- Login/register event handlers now bind safely.
- Google buttons use `/api/auth/google`.
- Forgot-password flow added for local development.
- Password reset tokens are hashed, expire after 30 minutes, and are single-use.
- Flask-Login user loader keeps UUID IDs as strings.
- UUIDs are generated when model objects are constructed.
- Habit/task/social routes accept UUID strings instead of integers.
- Frontend no longer coerces UUIDs with unary `+`.
- OAuth callback redirects to `/`, which exists.
- Google/Microsoft OAuth URLs use proper URL encoding.
- Added `pymongo` to backend requirements.

## Run
1. Start MongoDB.
2. `cd backend`
3. Create/activate a virtual environment.
4. `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and fill values.
6. `python app.py`
7. Open `http://localhost:5000`
