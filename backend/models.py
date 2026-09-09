"""MongoDB-backed data models for HabitTrack."""
import os
from datetime import datetime, date
from uuid import uuid4

from flask_login import UserMixin
from pymongo import MongoClient, ASCENDING
from werkzeug.security import generate_password_hash, check_password_hash

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    MONGODB_URI = os.getenv('MONGODB_URI')
    MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'habbittrack')
class Database:
    def __init__(self):
        self.client = None
        self.database = None
        self.session = Session(self)

    def init_app(self, app):
        uri = app.config['MONGODB_URI']
        self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        self.database = self.client[app.config['MONGODB_DATABASE']]
        self.create_all()

    def create_all(self):
        if self.database is None:
            return
        self.database.users.create_index('email', unique=True)
        self.database.users.create_index('username', unique=True)
        self.database.habits.create_index([('user_id', ASCENDING)])
        self.database.tasks.create_index([('user_id', ASCENDING)])
        self.database.habit_completions.create_index([('habit_id', ASCENDING), ('date', ASCENDING)], unique=True)

    def collection(self, name):
        if self.database is None:
            raise RuntimeError('MongoDB is not initialized. Check MONGODB_URI and start MongoDB.')
        return self.database[name]


class Session:
    def __init__(self, database):
        self.database = database
        self.pending = []

    def add(self, obj): self.pending.append(('save', obj))
    def delete(self, obj): self.pending.append(('delete', obj))
    def commit(self):
        try:
            for action, obj in self.pending:
                obj._delete() if action == 'delete' else obj._save()
        finally:
            self.pending = []
    def rollback(self): self.pending = []


class Query:
    def __init__(self, model): self.model, self.filters = model, {}
    def filter_by(self, **kwargs): self.filters.update(kwargs); return self
    def all(self): return self.model._fetch_all(self.filters)
    def first(self):
        rows = self.all()
        return rows[0] if rows else None
    def count(self): return len(self.all())
    def get(self, value): return self.filter_by(id=str(value)).first()


class BaseModel:
    __tablename__ = ''
    @classmethod
    def _fetch_all(cls, filters=None):
        return [cls._from_document(document) for document in db.collection(cls.__tablename__).find(filters or {})]
    @classmethod
    def _from_document(cls, document):
        document.pop('_id', None)
        return cls(**document)
    def _document(self):
        return {key: value for key, value in self.__dict__.items() if not key.startswith('_')}
    def _save(self):
        if not self.id: self.id = uuid4().hex
        db.collection(self.__tablename__).replace_one({'id': self.id}, self._document(), upsert=True)
    def _delete(self): db.collection(self.__tablename__).delete_one({'id': self.id})


class User(UserMixin, BaseModel):
    __tablename__ = 'users'
    def __init__(self, username='', email='', first_name='', last_name='', **kwargs):
        self.id = str(kwargs.get('id') or '')
        self.username, self.email = username, email
        self.password_hash = kwargs.get('password_hash')
        self.google_id, self.microsoft_id = kwargs.get('google_id'), kwargs.get('microsoft_id')
        self.first_name, self.last_name = first_name, last_name
        self.avatar_url = kwargs.get('avatar_url')
        self._is_active, self._email_verified = kwargs.get('is_active', True), kwargs.get('email_verified', False)
        self.created_at, self.updated_at = kwargs.get('created_at') or datetime.utcnow(), kwargs.get('updated_at') or datetime.utcnow()
    @property
    def is_active(self): return self._is_active
    @is_active.setter
    def is_active(self, value): self._is_active = bool(value)
    @property
    def email_verified(self): return self._email_verified
    @email_verified.setter
    def email_verified(self, value): self._email_verified = bool(value)
    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return bool(self.password_hash) and check_password_hash(self.password_hash, password)
    def _document(self):
        data = super()._document(); data['is_active'] = self.is_active; data['email_verified'] = self.email_verified; return data
    def to_dict(self): return {'id':self.id,'username':self.username,'email':self.email,'first_name':self.first_name,'last_name':self.last_name,'avatar_url':self.avatar_url,'created_at':self.created_at.isoformat()}
    @classmethod
    def get_by_id(cls, user_id): return cls.query.get(user_id)
    @classmethod
    def find_by_email(cls, email): return cls.query.filter_by(email=email).first()
    @classmethod
    def find_by_username(cls, username): return cls.query.filter_by(username=username).first()
    @classmethod
    def find_by_google_id(cls, google_id): return cls.query.filter_by(google_id=google_id).first()


class Habit(BaseModel):
    __tablename__ = 'habits'
    def __init__(self, user_id='', name='', description='', **kwargs):
        self.id=str(kwargs.get('id') or ''); self.user_id=str(user_id); self.name=name; self.description=description
        self.created_at=kwargs.get('created_at') or datetime.utcnow(); self.updated_at=kwargs.get('updated_at') or datetime.utcnow()
    def to_dict(self): return {'id':self.id,'name':self.name,'description':self.description,'created_at':self.created_at.isoformat(),'completions':[]}


class Task(BaseModel):
    __tablename__ = 'tasks'
    def __init__(self, user_id='', title='', due_date=None, completed=False, **kwargs):
        self.id=str(kwargs.get('id') or ''); self.user_id=str(user_id); self.title=title; self.due_date=due_date; self.completed=bool(completed)
        self.created_at=kwargs.get('created_at') or datetime.utcnow(); self.updated_at=kwargs.get('updated_at') or datetime.utcnow()
    def to_dict(self): return {'id':self.id,'title':self.title,'due_date':self.due_date.isoformat() if hasattr(self.due_date,'isoformat') else self.due_date,'completed':self.completed,'created_at':self.created_at.isoformat()}


class HabitCompletion(BaseModel):
    __tablename__ = 'habit_completions'
    def __init__(self, habit_id='', date=None, completed=True, **kwargs):
        self.id=str(kwargs.get('id') or ''); self.habit_id=str(habit_id); self.date=date or datetime.utcnow().date(); self.completed=bool(completed); self.created_at=kwargs.get('created_at') or datetime.utcnow()
    def to_dict(self): return {'id':self.id,'habit_id':self.habit_id,'date':self.date.isoformat() if hasattr(self.date,'isoformat') else self.date,'completed':self.completed}


class OAuthToken(BaseModel):
    __tablename__ = 'oauth_tokens'
    def __init__(self, user_id='', provider='', access_token='', refresh_token=None, expires_at=None, **kwargs):
        self.id=str(kwargs.get('id') or ''); self.user_id=str(user_id); self.provider=provider; self.access_token=access_token; self.refresh_token=refresh_token; self.expires_at=expires_at; self.created_at=kwargs.get('created_at') or datetime.utcnow(); self.updated_at=kwargs.get('updated_at') or datetime.utcnow()


class SocialShare(BaseModel):
    __tablename__ = 'social_shares'
    def __init__(self, user_id='', habit_id=None, platform='', message='', share_url=None, **kwargs):
        self.id=str(kwargs.get('id') or ''); self.user_id=str(user_id); self.habit_id=str(habit_id) if habit_id else None; self.platform=platform; self.message=message; self.share_url=share_url; self.shared_at=kwargs.get('shared_at') or datetime.utcnow()


User.query=Query(User); Habit.query=Query(Habit); Task.query=Query(Task); HabitCompletion.query=Query(HabitCompletion); OAuthToken.query=Query(OAuthToken); SocialShare.query=Query(SocialShare)
db=Database()
