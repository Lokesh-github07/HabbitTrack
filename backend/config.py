import os
from datetime import timedelta
from dotenv import load_dotenv


# Load environment variables from .env
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))


class Config:
    """Base configuration"""

    # Flask
    SECRET_KEY = os.getenv(
        'SECRET_KEY',
        'dev-secret-key-change-in-production'
    )

    # MongoDB
    MONGODB_URI = os.getenv(
        'MONGODB_URI',
        'mongodb://localhost:27017/habbittrack'
    )

    MONGODB_DATABASE = os.getenv(
        'MONGODB_DATABASE',
        'habbittrack'
    )

    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Google OAuth
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI = os.getenv(
        'GOOGLE_REDIRECT_URI',
        'http://localhost:5000/api/auth/google/callback'
    )

    # Microsoft OAuth
    MICROSOFT_CLIENT_ID = os.getenv('MICROSOFT_CLIENT_ID')
    MICROSOFT_CLIENT_SECRET = os.getenv('MICROSOFT_CLIENT_SECRET')
    MICROSOFT_REDIRECT_URI = os.getenv(
        'MICROSOFT_REDIRECT_URI',
        'http://localhost:5000/api/auth/microsoft/callback'
    )


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True

    # Use the same MongoDB configuration as the base Config.
    # You can use a separate test database if required.
    MONGODB_DATABASE = os.getenv(
        'MONGODB_TEST_DATABASE',
        'habbittrack_test'
    )


# Configuration mapping
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}