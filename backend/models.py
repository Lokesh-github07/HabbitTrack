import os
from datetime import datetime, date
from urllib.parse import urlparse

import mysql.connector
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Database:
    def __init__(self):
        self.app = None
        self._config = {}
        self._mysql_ready = False
        self.session = _Session(self)

    def init_app(self, app):
        self.app = app
        self._config = self._build_config(app.config.get('DATABASE_URL') or os.getenv('DATABASE_URL'))
        try:
            self.create_all()
            self._mysql_ready = True
        except Exception as exc:
            self._mysql_ready = False
            app.logger.warning('MySQL initialization failed: %s', exc)

    def _build_config(self, database_url):
        if not database_url:
            database_url = os.getenv('DATABASE_URL', 'mysql+mysqlconnector://root:password@localhost:3306/habittrack')

        parsed = urlparse(database_url.replace('mysql+mysqlconnector://', 'mysql://').replace('mysql+pymysql://', 'mysql://'))
        return {
            'host': parsed.hostname or os.getenv('MYSQL_HOST', 'localhost'),
            'port': parsed.port or int(os.getenv('MYSQL_PORT', '3306')),
            'user': parsed.username or os.getenv('MYSQL_USER', 'root'),
            'password': parsed.password or os.getenv('MYSQL_PASSWORD', 'Root12345'),
            'database': parsed.path.lstrip('/') or os.getenv('MYSQL_DATABASE', 'habittrack'),
            'use_unicode': True,
            'charset': 'utf8mb4',
        }

    def get_connection(self):
        if not self._config:
            raise RuntimeError('Database configuration is not initialized')
        try:
            return mysql.connector.connect(**self._config)
        except Exception as exc:
            raise RuntimeError(f'MySQL connection failed for {self._config["user"]}@{self._config["host"]}: {exc}') from exc

    def create_all(self):
        if not self._config:
            return

        create_db_config = dict(self._config)
        create_db_config.pop('database', None)
        conn = mysql.connector.connect(**create_db_config)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self._config['database']}`")
        conn.close()

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(80) NOT NULL UNIQUE,
            email VARCHAR(120) NOT NULL UNIQUE,
            password_hash VARCHAR(255),
            google_id VARCHAR(255) UNIQUE,
            microsoft_id VARCHAR(255) UNIQUE,
            first_name VARCHAR(80),
            last_name VARCHAR(80),
            avatar_url VARCHAR(500),
            is_active BOOLEAN DEFAULT TRUE,
            email_verified BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            name VARCHAR(200) NOT NULL,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS habit_completions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            habit_id INT NOT NULL,
            date DATE NOT NULL,
            completed BOOLEAN DEFAULT TRUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS oauth_tokens (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            provider VARCHAR(50) NOT NULL,
            access_token TEXT NOT NULL,
            refresh_token TEXT,
            expires_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS social_shares (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            habit_id INT,
            platform VARCHAR(50) NOT NULL,
            message TEXT NOT NULL,
            shared_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            share_url VARCHAR(500)
        )
        """)
        conn.commit()
        cursor.close()
        conn.close()


class _Session:
    def __init__(self, database):
        self.database = database
        self.pending = []

    def add(self, obj):
        self.pending.append(("add", obj))

    def delete(self, obj):
        self.pending.append(("delete", obj))

    def commit(self):
        if not self.pending:
            return

        conn = self.database.get_connection()
        cursor = conn.cursor()
        try:
            for action, obj in self.pending:
                if action == "delete":
                    obj._delete(cursor)
                else:
                    obj._save(cursor)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
        self.pending = []

    def rollback(self):
        self.pending = []


class Query:
    def __init__(self, model_cls):
        self.model_cls = model_cls
        self.filters = {}

    def filter_by(self, **kwargs):
        self.filters.update(kwargs)
        return self

    def all(self):
        return self.model_cls._fetch_all(self.filters)

    def first(self):
        rows = self.all()
        return rows[0] if rows else None

    def count(self):
        return len(self.all())

    def get(self, value):
        return self.filter_by(id=value).first()


class BaseModel:
    __tablename__ = None

    @classmethod
    def _fetch_all(cls, filters=None):
        filters = filters or {}
        conn = db.get_connection()
        cursor = conn.cursor(dictionary=True)
        if filters:
            clause = " AND ".join([f"{key} = %s" for key in filters.keys()])
            params = tuple(filters.values())
            cursor.execute(f"SELECT * FROM `{cls.__tablename__}` WHERE {clause}", params)
        else:
            cursor.execute(f"SELECT * FROM `{cls.__tablename__}`")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [cls._from_row(row) for row in rows]

    @classmethod
    def _from_row(cls, row):
        if not row:
            return None
        obj = cls.__new__(cls)
        for key, value in row.items():
            setattr(obj, key, value)
        return obj

    def _save(self, cursor):
        raise NotImplementedError

    def _delete(self, cursor):
        raise NotImplementedError


class User(UserMixin, BaseModel):
    __tablename__ = 'users'

    def __init__(self, username='', email='', first_name='', last_name='', **kwargs):
        self.id = kwargs.get('id')
        self.username = username
        self.email = email
        self.password_hash = kwargs.get('password_hash')
        self.google_id = kwargs.get('google_id')
        self.microsoft_id = kwargs.get('microsoft_id')
        self.first_name = first_name
        self.last_name = last_name
        self.avatar_url = kwargs.get('avatar_url')
        self._is_active = kwargs.get('is_active', True)
        self._email_verified = kwargs.get('email_verified', False)
        self.created_at = kwargs.get('created_at') or datetime.utcnow()
        self.updated_at = kwargs.get('updated_at') or datetime.utcnow()

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, value):
        self._is_active = bool(value)

    @property
    def email_verified(self):
        return self._email_verified

    @email_verified.setter
    def email_verified(self, value):
        self._email_verified = bool(value)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        created = self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else self.created_at
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'avatar_url': self.avatar_url,
            'created_at': created,
        }

    def _save(self, cursor):
        if self.id:
            cursor.execute(
                """
                UPDATE users SET username=%s, email=%s, password_hash=%s, google_id=%s, microsoft_id=%s,
                first_name=%s, last_name=%s, avatar_url=%s, is_active=%s, email_verified=%s, updated_at=%s
                WHERE id=%s
                """,
                (
                    self.username,
                    self.email,
                    self.password_hash,
                    self.google_id,
                    self.microsoft_id,
                    self.first_name,
                    self.last_name,
                    self.avatar_url,
                    self.is_active,
                    self.email_verified,
                    datetime.utcnow(),
                    self.id,
                ),
            )
            return

        cursor.execute(
            """
            INSERT INTO users (username, email, password_hash, google_id, microsoft_id, first_name, last_name, avatar_url, is_active, email_verified, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                self.username,
                self.email,
                self.password_hash,
                self.google_id,
                self.microsoft_id,
                self.first_name,
                self.last_name,
                self.avatar_url,
                self.is_active,
                self.email_verified,
                datetime.utcnow(),
                datetime.utcnow(),
            ),
        )
        self.id = cursor.lastrowid

    def _delete(self, cursor):
        cursor.execute("DELETE FROM users WHERE id=%s", (self.id,))

    @classmethod
    def get_by_id(cls, user_id):
        return cls.query.get(user_id)

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_google_id(cls, google_id):
        return cls.query.filter_by(google_id=google_id).first()


class Habit(BaseModel):
    __tablename__ = 'habits'

    def __init__(self, user_id=0, name='', description='', **kwargs):
        self.id = kwargs.get('id')
        self.user_id = user_id
        self.name = name
        self.description = description
        self.created_at = kwargs.get('created_at') or datetime.utcnow()
        self.updated_at = kwargs.get('updated_at') or datetime.utcnow()

    def to_dict(self):
        created = self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else self.created_at
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': created,
            'completions': [],
        }

    def _save(self, cursor):
        if self.id:
            cursor.execute(
                "UPDATE habits SET user_id=%s, name=%s, description=%s, updated_at=%s WHERE id=%s",
                (self.user_id, self.name, self.description, datetime.utcnow(), self.id),
            )
            return
        cursor.execute(
            "INSERT INTO habits (user_id, name, description, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)",
            (self.user_id, self.name, self.description, datetime.utcnow(), datetime.utcnow()),
        )
        self.id = cursor.lastrowid

    def _delete(self, cursor):
        cursor.execute("DELETE FROM habits WHERE id=%s", (self.id,))


class HabitCompletion(BaseModel):
    __tablename__ = 'habit_completions'

    def __init__(self, habit_id=0, date=None, completed=True, **kwargs):
        self.id = kwargs.get('id')
        self.habit_id = habit_id
        self.date = date or date.today()
        self.completed = completed
        self.created_at = kwargs.get('created_at') or datetime.utcnow()

    def to_dict(self):
        date_value = self.date.isoformat() if hasattr(self.date, 'isoformat') else self.date
        return {
            'id': self.id,
            'habit_id': self.habit_id,
            'date': date_value,
            'completed': self.completed,
        }

    def _save(self, cursor):
        if self.id:
            cursor.execute(
                "UPDATE habit_completions SET habit_id=%s, date=%s, completed=%s WHERE id=%s",
                (self.habit_id, self.date, self.completed, self.id),
            )
            return
        cursor.execute(
            "INSERT INTO habit_completions (habit_id, date, completed, created_at) VALUES (%s, %s, %s, %s)",
            (self.habit_id, self.date, self.completed, datetime.utcnow()),
        )
        self.id = cursor.lastrowid

    def _delete(self, cursor):
        cursor.execute("DELETE FROM habit_completions WHERE id=%s", (self.id,))


class OAuthToken(BaseModel):
    __tablename__ = 'oauth_tokens'

    def __init__(self, user_id=0, provider='', access_token='', refresh_token=None, expires_at=None, **kwargs):
        self.id = kwargs.get('id')
        self.user_id = user_id
        self.provider = provider
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at = expires_at
        self.created_at = kwargs.get('created_at') or datetime.utcnow()
        self.updated_at = kwargs.get('updated_at') or datetime.utcnow()

    def _save(self, cursor):
        if self.id:
            cursor.execute(
                "UPDATE oauth_tokens SET user_id=%s, provider=%s, access_token=%s, refresh_token=%s, expires_at=%s, updated_at=%s WHERE id=%s",
                (self.user_id, self.provider, self.access_token, self.refresh_token, self.expires_at, datetime.utcnow(), self.id),
            )
            return
        cursor.execute(
            "INSERT INTO oauth_tokens (user_id, provider, access_token, refresh_token, expires_at, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (self.user_id, self.provider, self.access_token, self.refresh_token, self.expires_at, datetime.utcnow(), datetime.utcnow()),
        )
        self.id = cursor.lastrowid

    def _delete(self, cursor):
        cursor.execute("DELETE FROM oauth_tokens WHERE id=%s", (self.id,))


class SocialShare(BaseModel):
    __tablename__ = 'social_shares'

    def __init__(self, user_id=0, habit_id=None, platform='', message='', share_url=None, **kwargs):
        self.id = kwargs.get('id')
        self.user_id = user_id
        self.habit_id = habit_id
        self.platform = platform
        self.message = message
        self.shared_at = kwargs.get('shared_at') or datetime.utcnow()
        self.share_url = share_url

    def _save(self, cursor):
        if self.id:
            cursor.execute(
                "UPDATE social_shares SET user_id=%s, habit_id=%s, platform=%s, message=%s, share_url=%s WHERE id=%s",
                (self.user_id, self.habit_id, self.platform, self.message, self.share_url, self.id),
            )
            return
        cursor.execute(
            "INSERT INTO social_shares (user_id, habit_id, platform, message, shared_at, share_url) VALUES (%s, %s, %s, %s, %s, %s)",
            (self.user_id, self.habit_id, self.platform, self.message, datetime.utcnow(), self.share_url),
        )
        self.id = cursor.lastrowid

    def _delete(self, cursor):
        cursor.execute("DELETE FROM social_shares WHERE id=%s", (self.id,))


# Query entry points
User.query = Query(User)
Habit.query = Query(Habit)
HabitCompletion.query = Query(HabitCompletion)
OAuthToken.query = Query(OAuthToken)
SocialShare.query = Query(SocialShare)

db = Database()
