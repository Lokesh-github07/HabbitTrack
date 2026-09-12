from flask import Blueprint, request, jsonify, redirect
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, OAuthToken
from urllib.parse import urlencode
from werkzeug.exceptions import BadRequest
import hashlib
import secrets
import requests
from datetime import datetime, timedelta


auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def normalize_email(value):
    return (value or '').strip().lower()


def json_error(message, status=400):
    return jsonify({'error': message}), status


@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json() or {}
        email = normalize_email(data.get('email'))
        username = (data.get('username') or '').strip()
        password = data.get('password') or ''

        if not email or not password:
            return json_error('Email and password required')
        if not username:
            return json_error('Username required')
        if len(password) < 8:
            return json_error('Password must be at least 8 characters')
        if User.find_by_email(email):
            return json_error('Email already registered', 409)
        if User.find_by_username(username):
            return json_error('Username already taken', 409)

        user = User(
            username=username,
            email=email,
            first_name=(data.get('first_name') or '').strip(),
            last_name=(data.get('last_name') or '').strip()
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=bool(data.get('remember', False)))

        return jsonify({'message': 'Registration successful', 'user': user.to_dict()}), 201
    except Exception as exc:
        db.session.rollback()
        return json_error(str(exc), 500)


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json() or {}
        email = normalize_email(data.get('email'))
        password = data.get('password') or ''

        if not email or not password:
            return json_error('Email and password required')

        user = User.find_by_email(email)
        if not user or not user.check_password(password):
            return json_error('Invalid email or password', 401)
        if not user.is_active:
            return json_error('Account is disabled', 403)

        login_user(user, remember=bool(data.get('remember', False)))
        return jsonify({'message': 'Login successful', 'user': user.to_dict()}), 200
    except Exception as exc:
        return json_error(str(exc), 500)


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logout successful'}), 200


@auth_bp.route('/current-user', methods=['GET'])
@login_required
def current_user_info():
    return jsonify(current_user.to_dict()), 200


@auth_bp.route('/verify-token', methods=['GET'])
@login_required
def verify_token():
    return jsonify({'authenticated': True, 'user': current_user.to_dict()}), 200


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Create a short-lived password reset token.

    In development the raw token is returned so the flow can be tested without
    an email provider. In production, send the tokenized URL by email instead.
    """
    try:
        data = request.get_json() or {}
        email = normalize_email(data.get('email'))
        if not email:
            return json_error('Email address is required')

        generic_message = 'If an account exists for this email, a reset link has been generated.'
        user = User.find_by_email(email)
        if not user:
            return jsonify({'message': generic_message}), 200

        raw_token = secrets.token_urlsafe(32)
        user.reset_token_hash = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()
        user.reset_token_expires_at = datetime.utcnow() + timedelta(minutes=30)
        user.updated_at = datetime.utcnow()
        db.session.add(user)
        db.session.commit()

        response = {'message': generic_message}
        if request.host.startswith(('localhost', '127.0.0.1')):
            response['reset_token'] = raw_token
            response['reset_url'] = f'{request.host_url}?reset_token={raw_token}'
        return jsonify(response), 200
    except Exception as exc:
        db.session.rollback()
        return json_error(str(exc), 500)


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json() or {}
        token = data.get('token') or ''
        password = data.get('password') or ''
        if not token or not password:
            return json_error('Token and password are required')
        if len(password) < 8:
            return json_error('Password must be at least 8 characters')

        token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
        user = User.query.filter_by(reset_token_hash=token_hash).first()
        if not user or not user.reset_token_expires_at:
            return json_error('Invalid or expired reset link')

        expires = user.reset_token_expires_at
        if hasattr(expires, 'replace') and expires < datetime.utcnow():
            return json_error('This reset link has expired')

        user.set_password(password)
        user.reset_token_hash = None
        user.reset_token_expires_at = None
        user.updated_at = datetime.utcnow()
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'Password reset successfully'}), 200
    except Exception as exc:
        db.session.rollback()
        return json_error(str(exc), 500)


@auth_bp.route('/google', methods=['GET'])
def google_auth():
    from config import Config
    if not Config.GOOGLE_CLIENT_ID or not Config.GOOGLE_CLIENT_SECRET:
        return json_error('Google OAuth is not configured. Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to backend/.env.', 503)

    params = {
        'client_id': Config.GOOGLE_CLIENT_ID,
        'redirect_uri': Config.GOOGLE_REDIRECT_URI,
        'response_type': 'code',
        'scope': 'openid email profile',
        'access_type': 'offline',
        'prompt': 'select_account'
    }
    return redirect('https://accounts.google.com/o/oauth2/v2/auth?' + urlencode(params))


@auth_bp.route('/google/callback', methods=['GET'])
def google_callback():
    from config import Config
    code = request.args.get('code')
    if not code:
        return json_error('No authorization code')
    if not Config.GOOGLE_CLIENT_ID or not Config.GOOGLE_CLIENT_SECRET:
        return json_error('Google OAuth is not configured', 503)

    try:
        token_response = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'code': code,
                'client_id': Config.GOOGLE_CLIENT_ID,
                'client_secret': Config.GOOGLE_CLIENT_SECRET,
                'redirect_uri': Config.GOOGLE_REDIRECT_URI,
                'grant_type': 'authorization_code'
            },
            timeout=15
        )
        tokens = token_response.json()
        if token_response.status_code >= 400 or 'error' in tokens:
            return json_error('Google token exchange failed', 400)

        user_response = requests.get(
            'https://openidconnect.googleapis.com/v1/userinfo',
            headers={'Authorization': f"Bearer {tokens['access_token']}"},
            timeout=15
        )
        user_info = user_response.json()
        if user_response.status_code >= 400 or not user_info.get('sub') or not user_info.get('email'):
            return json_error('Could not read Google account information', 400)

        email = normalize_email(user_info['email'])
        user = User.find_by_google_id(user_info['sub']) or User.find_by_email(email)
        if not user:
            base_username = email.split('@')[0]
            username = base_username
            suffix = 1
            while User.find_by_username(username):
                username = f'{base_username}{suffix}'
                suffix += 1
            user = User(
                email=email,
                username=username,
                google_id=user_info['sub'],
                first_name=user_info.get('given_name', ''),
                last_name=user_info.get('family_name', ''),
                avatar_url=user_info.get('picture', ''),
                email_verified=bool(user_info.get('email_verified', False))
            )
            db.session.add(user)
            db.session.commit()
        else:
            user.google_id = user_info['sub']
            if user_info.get('picture'):
                user.avatar_url = user_info['picture']
            db.session.add(user)
            db.session.commit()

        oauth_token = OAuthToken.query.filter_by(user_id=user.id, provider='google').first()
        expires_at = datetime.utcnow() + timedelta(seconds=int(tokens.get('expires_in', 3600)))
        if oauth_token:
            oauth_token.access_token = tokens['access_token']
            oauth_token.refresh_token = tokens.get('refresh_token') or oauth_token.refresh_token
            oauth_token.expires_at = expires_at
        else:
            oauth_token = OAuthToken(
                user_id=user.id,
                provider='google',
                access_token=tokens['access_token'],
                refresh_token=tokens.get('refresh_token'),
                expires_at=expires_at
            )
            db.session.add(oauth_token)
        db.session.commit()
        login_user(user, remember=True)
        return redirect('/')
    except Exception as exc:
        db.session.rollback()
        return json_error(str(exc), 500)


@auth_bp.route('/microsoft', methods=['GET'])
def microsoft_auth():
    from config import Config
    if not Config.MICROSOFT_CLIENT_ID or not Config.MICROSOFT_CLIENT_SECRET:
        return json_error('Microsoft OAuth is not configured.', 503)
    params = {
        'client_id': Config.MICROSOFT_CLIENT_ID,
        'redirect_uri': Config.MICROSOFT_REDIRECT_URI,
        'response_type': 'code',
        'scope': 'openid email profile offline_access',
        'response_mode': 'query'
    }
    return redirect('https://login.microsoftonline.com/common/oauth2/v2.0/authorize?' + urlencode(params))


@auth_bp.route('/microsoft/callback', methods=['GET'])
def microsoft_callback():
    from config import Config
    code = request.args.get('code')
    if not code:
        return json_error('No authorization code')
    if not Config.MICROSOFT_CLIENT_ID or not Config.MICROSOFT_CLIENT_SECRET:
        return json_error('Microsoft OAuth is not configured', 503)

    try:
        token_response = requests.post(
            'https://login.microsoftonline.com/common/oauth2/v2.0/token',
            data={
                'code': code,
                'client_id': Config.MICROSOFT_CLIENT_ID,
                'client_secret': Config.MICROSOFT_CLIENT_SECRET,
                'redirect_uri': Config.MICROSOFT_REDIRECT_URI,
                'grant_type': 'authorization_code',
                'scope': 'openid email profile offline_access'
            },
            timeout=15
        )
        tokens = token_response.json()
        if token_response.status_code >= 400 or 'error' in tokens:
            return json_error('Microsoft token exchange failed', 400)

        user_response = requests.get(
            'https://graph.microsoft.com/v1.0/me',
            headers={'Authorization': f"Bearer {tokens['access_token']}"},
            timeout=15
        )
        user_info = user_response.json()
        if user_response.status_code >= 400 or not user_info.get('id'):
            return json_error('Could not read Microsoft account information', 400)

        email = normalize_email(user_info.get('mail') or user_info.get('userPrincipalName'))
        if not email:
            return json_error('Microsoft account did not provide an email address', 400)
        user = User.query.filter_by(microsoft_id=user_info['id']).first() or User.find_by_email(email)
        if not user:
            base_username = email.split('@')[0]
            username = base_username
            suffix = 1
            while User.find_by_username(username):
                username = f'{base_username}{suffix}'
                suffix += 1
            user = User(
                email=email,
                username=username,
                microsoft_id=user_info['id'],
                first_name=user_info.get('givenName', ''),
                last_name=user_info.get('surname', ''),
                email_verified=True
            )
            db.session.add(user)
            db.session.commit()
        else:
            user.microsoft_id = user_info['id']
            db.session.add(user)
            db.session.commit()

        oauth_token = OAuthToken.query.filter_by(user_id=user.id, provider='microsoft').first()
        expires_at = datetime.utcnow() + timedelta(seconds=int(tokens.get('expires_in', 3600)))
        if oauth_token:
            oauth_token.access_token = tokens['access_token']
            oauth_token.refresh_token = tokens.get('refresh_token') or oauth_token.refresh_token
            oauth_token.expires_at = expires_at
        else:
            db.session.add(OAuthToken(
                user_id=user.id,
                provider='microsoft',
                access_token=tokens['access_token'],
                refresh_token=tokens.get('refresh_token'),
                expires_at=expires_at
            ))
        db.session.commit()
        login_user(user, remember=True)
        return redirect('/')
    except Exception as exc:
        db.session.rollback()
        return json_error(str(exc), 500)


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    return jsonify(current_user.to_dict()), 200


@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    try:
        data = request.get_json() or {}
        user = current_user
        username = (data.get('username') or '').strip()
        email = normalize_email(data.get('email'))
        if username:
            existing = User.find_by_username(username)
            if existing and existing.id != user.id:
                return json_error('Username already taken', 409)
            user.username = username
        if email:
            existing = User.find_by_email(email)
            if existing and existing.id != user.id:
                return json_error('Email already registered', 409)
            user.email = email
        if 'first_name' in data:
            user.first_name = (data.get('first_name') or '').strip()
        if 'last_name' in data:
            user.last_name = (data.get('last_name') or '').strip()
        if data.get('password'):
            if len(data['password']) < 8:
                return json_error('Password must be at least 8 characters')
            user.set_password(data['password'])
        user.updated_at = datetime.utcnow()
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'Profile updated', 'user': user.to_dict()}), 200
    except Exception as exc:
        db.session.rollback()
        return json_error(str(exc), 500)


@auth_bp.route('/verify-email', methods=['POST'])
@login_required
def verify_email():
    try:
        current_user.email_verified = True
        db.session.add(current_user)
        db.session.commit()
        return jsonify({'message': 'Email verified'}), 200
    except Exception as exc:
        db.session.rollback()
        return json_error(str(exc), 500)
