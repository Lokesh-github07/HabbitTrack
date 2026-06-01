#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Database Setup Script for HabitTrack
Run this to initialize your database with tables
"""

import os
import sys
import mysql.connector
from mysql.connector import Error

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from dotenv import load_dotenv

load_dotenv('backend/.env')

def get_db_connection():
    """Get MySQL connection"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=os.getenv('DB_PASSWORD', 'root'),
            database='habittrack'
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def create_database():
    """Create database if it doesn't exist"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=os.getenv('DB_PASSWORD', 'root')
        )
        cursor = connection.cursor()
        
        cursor.execute("CREATE DATABASE IF NOT EXISTS habittrack")
        print("✓ Database 'habittrack' created/verified")
        
        cursor.close()
        connection.close()
        return True
    except Error as e:
        print(f"✗ Error creating database: {e}")
        return False

def create_tables():
    """Create all necessary tables"""
    connection = get_db_connection()
    if not connection:
        return False
    
    cursor = connection.cursor()
    
    try:
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(255),
                google_id VARCHAR(255) UNIQUE,
                microsoft_id VARCHAR(255) UNIQUE,
                first_name VARCHAR(80),
                last_name VARCHAR(80),
                avatar_url VARCHAR(500),
                is_active BOOLEAN DEFAULT TRUE,
                email_verified BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_email (email)
            )
        """)
        print("✓ Users table created")
        
        # Create habits table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS habits (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id)
            )
        """)
        print("✓ Habits table created")
        
        # Create habit_completions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS habit_completions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                habit_id INT NOT NULL,
                date DATE NOT NULL,
                completed BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
                INDEX idx_habit_id (habit_id),
                INDEX idx_date (date),
                UNIQUE KEY unique_habit_date (habit_id, date)
            )
        """)
        print("✓ Habit Completions table created")
        
        # Create oauth_tokens table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS oauth_tokens (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                provider VARCHAR(50) NOT NULL,
                access_token TEXT NOT NULL,
                refresh_token TEXT,
                expires_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_provider (user_id, provider)
            )
        """)
        print("✓ OAuth Tokens table created")
        
        connection.commit()
        print("\n✓ All tables created successfully!")
        return True
        
    except Error as e:
        print(f"✗ Error creating tables: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()

def verify_tables():
    """Verify all tables exist"""
    connection = get_db_connection()
    if not connection:
        return False
    
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
            SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = 'habittrack'
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        required_tables = ['users', 'habits', 'habit_completions', 'oauth_tokens']
        
        print("\nDatabase Tables:")
        for table in required_tables:
            if table in tables:
                print(f"  ✓ {table}")
            else:
                print(f"  ✗ {table} (Missing)")
        
        return all(table in tables for table in required_tables)
        
    except Error as e:
        print(f"✗ Error verifying tables: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    print("\n" + "="*50)
    print("HabitTrack Database Setup")
    print("="*50 + "\n")
    
    print("Step 1: Creating database...")
    if not create_database():
        print("✗ Failed to create database. Check your MySQL configuration.")
        sys.exit(1)
    
    print("\nStep 2: Creating tables...")
    if not create_tables():
        print("✗ Failed to create tables.")
        sys.exit(1)
    
    print("\nStep 3: Verifying setup...")
    if verify_tables():
        print("\n" + "="*50)
        print("✓ Database setup completed successfully!")
        print("="*50)
        print("\nYou can now run: python run.py")
    else:
        print("\n✗ Database verification failed.")
        sys.exit(1)
