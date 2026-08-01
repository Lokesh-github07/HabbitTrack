from flask import Blueprint, request, jsonify, redirect
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, OAuthToken
import requests
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Email/Password authentication
@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user with email and password"""
    try:
        data = request.get_json()
        
        # Validation
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        if not data.get('username'):
            return jsonify({'error': 'Username required'}), 400
        
        if User.find_by_email(data['email']):
            return jsonify({'error': 'Email already registered'}), 409
        
        if User.find_by_username(data['username']):
            return jsonify({'error': 'Username already taken'}), 409
        
        # Password validation
        if len(data['password']) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', '')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Auto-login after registration
        login_user(user)
        
        return jsonify({
            'message': 'Registration successful',
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login with email and password"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        user = User.find_by_email(data['email'])
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is disabled'}), 403
        
        login_user(user, remember=data.get('remember', False))
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout current user"""
    logout_user()
    return jsonify({'message': 'Logout successful'}), 200

@auth_bp.route('/current-user', methods=['GET'])
@login_required
def current_user_info():
    """Get current user info"""
    return jsonify(current_user.to_dict()), 200

@auth_bp.route('/verify-token', methods=['GET'])
@login_required
def verify_token():
    """Verify if user is authenticated"""
    return jsonify({
        'authenticated': True,
        'user': current_user.to_dict()
    }), 200

# OAuth routes
@auth_bp.route('/google', methods=['GET'])
def google_auth():
    """Initiate Google OAuth flow"""
    from config import Config
    
    client_id = Config.GOOGLE_CLIENT_ID
    redirect_uri = Config.GOOGLE_REDIRECT_URI
    scope = 'openid email profile'
    
    auth_url = (
        f'https://accounts.google.com/o/oauth2/v2/auth?'
        f'client_id={client_id}&'
        f'redirect_uri={redirect_uri}&'
        f'response_type=code&'
        f'scope={scope}'
    )
    
    return redirect(auth_url)

@auth_bp.route('/google/callback', methods=['GET'])
def google_callback():
    """Handle Google OAuth callback"""
    from config import Config
    
    code = request.args.get('code')
    
    if not code:
        return jsonify({'error': 'No authorization code'}), 400
    
    try:
        # Exchange code for token
        token_url = 'https://oauth2.googleapis.com/token'
        token_data = {
            'code': code,
            'client_id': Config.GOOGLE_CLIENT_ID,
            'client_secret': Config.GOOGLE_CLIENT_SECRET,
            'redirect_uri': Config.GOOGLE_REDIRECT_URI,
            'grant_type': 'authorization_code'
        }
        
        token_response = requests.post(token_url, data=token_data)
        tokens = token_response.json()
        
        if 'error' in tokens:
            return jsonify({'error': 'Token exchange failed'}), 400
        
        # Get user info
        user_info_url = 'https://openidconnect.googleapis.com/v1/userinfo'
        headers = {'Authorization': f"Bearer {tokens['access_token']}"}
        user_info = requests.get(user_info_url, headers=headers).json()
        
        # Find or create user
        user = User.find_by_google_id(user_info['sub'])
        
        if not user:
            user = User.find_by_email(user_info['email'])
            if not user:
                user = User(
                    email=user_info['email'],
                    username=user_info['email'].split('@')[0],
                    google_id=user_info['sub'],
                    first_name=user_info.get('given_name', ''),
                    last_name=user_info.get('family_name', ''),
                    avatar_url=user_info.get('picture', ''),
                    email_verified=user_info.get('email_verified', False)
                )
                db.session.add(user)
            else:
                user.google_id = user_info['sub']
        
        # Save OAuth token
        oauth_token = OAuthToken.query.filter_by(
            user_id=user.id, provider='google'
        ).first()
        
        if oauth_token:
            oauth_token.access_token = tokens['access_token']
            oauth_token.refresh_token = tokens.get('refresh_token')
            oauth_token.expires_at = datetime.utcnow() + timedelta(seconds=tokens.get('expires_in', 3600))
        else:
            oauth_token = OAuthToken(
                user_id=user.id,
                provider='google',
                access_token=tokens['access_token'],
                refresh_token=tokens.get('refresh_token'),
                expires_at=datetime.utcnow() + timedelta(seconds=tokens.get('expires_in', 3600))
            )
            db.session.add(oauth_token)
        
        db.session.commit()
        login_user(user)
        
        return redirect('/dashboard')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/microsoft', methods=['GET'])
def microsoft_auth():
    """Initiate Microsoft OAuth flow"""
    from config import Config
    
    client_id = Config.MICROSOFT_CLIENT_ID
    redirect_uri = Config.MICROSOFT_REDIRECT_URI
    scope = 'openid email profile'
    
    auth_url = (
        f'https://login.microsoftonline.com/common/oauth2/v2.0/authorize?'
        f'client_id={client_id}&'
        f'redirect_uri={redirect_uri}&'
        f'response_type=code&'
        f'scope={scope}'
    )
    
    return redirect(auth_url)

@auth_bp.route('/microsoft/callback', methods=['GET'])
def microsoft_callback():
    """Handle Microsoft OAuth callback"""
    from config import Config
    
    code = request.args.get('code')
    
    if not code:
        return jsonify({'error': 'No authorization code'}), 400
    
    try:
        # Exchange code for token
        token_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
        token_data = {
            'code': code,
            'client_id': Config.MICROSOFT_CLIENT_ID,
            'client_secret': Config.MICROSOFT_CLIENT_SECRET,
            'redirect_uri': Config.MICROSOFT_REDIRECT_URI,
            'grant_type': 'authorization_code',
            'scope': 'openid email profile'
        }
        
        token_response = requests.post(token_url, data=token_data)
        tokens = token_response.json()
        
        if 'error' in tokens:
            return jsonify({'error': 'Token exchange failed'}), 400
        
        # Get user info
        user_info_url = 'https://graph.microsoft.com/v1.0/me'
        headers = {'Authorization': f"Bearer {tokens['access_token']}"}
        user_info = requests.get(user_info_url, headers=headers).json()
        
        # Find or create user
        user = User.query.filter_by(microsoft_id=user_info['id']).first()
        
        if not user:
            user = User.query.filter_by(email=user_info['userPrincipalName']).first()
            if not user:
                user = User(
                    email=user_info['userPrincipalName'],
                    username=user_info['userPrincipalName'].split('@')[0],
                    microsoft_id=user_info['id'],
                    first_name=user_info.get('givenName', ''),
                    last_name=user_info.get('surname', ''),
                    email_verified=True
                )
                db.session.add(user)
            else:
                user.microsoft_id = user_info['id']
        
        # Save OAuth token
        oauth_token = OAuthToken.query.filter_by(
            user_id=user.id, provider='microsoft'
        ).first()
        
        if oauth_token:
            oauth_token.access_token = tokens['access_token']
            oauth_token.refresh_token = tokens.get('refresh_token')
            oauth_token.expires_at = datetime.utcnow() + timedelta(seconds=tokens.get('expires_in', 3600))
        else:
            oauth_token = OAuthToken(
                user_id=user.id,
                provider='microsoft',
                access_token=tokens['access_token'],
                refresh_token=tokens.get('refresh_token'),
                expires_at=datetime.utcnow() + timedelta(seconds=tokens.get('expires_in', 3600))
            )
            db.session.add(oauth_token)
        
        db.session.commit()
        login_user(user)
        
        return redirect('/dashboard')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current user info"""
    return jsonify(current_user.to_dict()), 200

@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """Update the current user's profile details."""
    try:
        data = request.get_json() or {}
        user = current_user

        if data.get('username'):
            existing = User.find_by_username(data['username'])
            if existing and existing.id != user.id:
                return jsonify({'error': 'Username already taken'}), 409
            user.username = data['username']

        if data.get('email'):
            existing = User.find_by_email(data['email'])
            if existing and existing.id != user.id:
                return jsonify({'error': 'Email already registered'}), 409
            user.email = data['email']

        if 'first_name' in data:
            user.first_name = data['first_name']

        if 'last_name' in data:
            user.last_name = data['last_name']

        if data.get('password'):
            if len(data['password']) < 8:
                return jsonify({'error': 'Password must be at least 8 characters'}), 400
            user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'Profile updated', 'user': user.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/verify-email', methods=['POST'])
@login_required
def verify_email():
    """Mark email as verified"""
    try:
        current_user.email_verified = True
        db.session.commit()
        return jsonify({'message': 'Email verified'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
