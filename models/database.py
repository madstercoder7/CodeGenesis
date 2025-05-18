# models/database.py
import sqlite3
import os

# Ensure the instance directory exists
os.makedirs('instance', exist_ok=True)
DATABASE_PATH = os.path.join('instance', 'codegenesis.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create projects table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        skill_level TEXT NOT NULL,
        technologies TEXT NOT NULL,
        project_type TEXT NOT NULL,
        title TEXT,
        content TEXT,
        created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create users table (for future authentication)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        skill_level TEXT,
        created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()