#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import create_app
from models import db, User, Habit, HabitCompletion

def create_database():
    """Create all database tables"""
    app = create_app()
    with app.app_context():
        db.create_all()
        print("✓ Database tables created successfully")

def create_demo_user():
    """Create a demo user for testing"""
    app = create_app()
    with app.app_context():
        # Check if demo user exists
        demo_user = User.query.filter_by(email='demo@habittrack.com').first()
        if demo_user:
            print("✓ Demo user already exists")
            return
        
        # Create demo user
        user = User(
            username='demouser',
            email='demo@habittrack.com',
            first_name='Demo',
            last_name='User'
        )
        user.set_password('Demo@123456')
        
        db.session.add(user)
        db.session.commit()
        
        print("✓ Demo user created")
        print(f"  Email: demo@habittrack.com")
        print(f"  Password: Demo@123456")

def seed_demo_data():
    """Add demo habits for testing"""
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(email='demo@habittrack.com').first()
        if not user:
            print("✗ Demo user not found. Create it first with --create-demo")
            return
        
        # Check if habits already exist
        if user.habits:
            print("✓ Demo habits already exist")
            return
        
        habits_data = [
            {'name': 'Morning Exercise', 'description': '30 minutes of physical activity'},
            {'name': 'Read a Book', 'description': 'Read at least 30 pages'},
            {'name': 'Meditate', 'description': '10 minutes of meditation'},
            {'name': 'Drink Water', 'description': '8 glasses of water'},
            {'name': 'Sleep 8 Hours', 'description': 'Get quality sleep'}
        ]
        
        from datetime import date, timedelta
        
        for habit_data in habits_data:
            habit = Habit(
                user_id=user.id,
                name=habit_data['name'],
                description=habit_data['description']
            )
            db.session.add(habit)
            db.session.flush()
            
            # Add some completion data for the last 14 days
            for i in range(14):
                completion_date = date.today() - timedelta(days=i)
                # Random completion pattern
                if i % 2 == 0:
                    completion = HabitCompletion(
                        habit_id=habit.id,
                        date=completion_date,
                        completed=True
                    )
                    db.session.add(completion)
        
        db.session.commit()
        print("✓ Demo habits created successfully")

if __name__ == '__main__':
    # Create the Flask app
    app = create_app()
    
    # Create database and tables
    with app.app_context():
        db.create_all()
        print("✓ Database initialized")
    
    # Print startup info
    print("\n" + "="*50)
    print("HabitTrack Server Starting")
    print("="*50)
    print(f"Environment: {app.config.get('FLASK_ENV', 'production')}")
    print(f"Debug Mode: {app.debug}")
    print(f"Database: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    print("\nServer running on http://localhost:5000")
    print("\nFrontend: http://localhost (serve index.html)")
    print("\nDemo Credentials:")
    print("  Email: demo@habittrack.com")
    print("  Password: Demo@123456")
    print("="*50 + "\n")
    
    # Run the Flask app
    app.run(
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 5000)),
        debug=True
    )
