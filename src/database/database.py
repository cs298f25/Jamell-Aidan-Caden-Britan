import sqlite3
from datetime import datetime

DB_NAME = "database.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database with the provided schema."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Adapted schema for SQLite (AUTOINCREMENT syntax differs from MySQL)
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT DEFAULT '', 
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            image_url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()

def get_or_create_user(username):
    """Gets a user's ID, or creates them if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if user exists
    res = cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = res.fetchone()
    
    if user:
        user_id = user['id']
    else:
        # Create new user (No password required per logic, storing empty string)
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, ""))
        conn.commit()
        user_id = cursor.lastrowid
        
    conn.close()
    return user_id

def add_image(user_id, image_url):
    """Logs an uploaded image URL to the database."""
    conn = get_db_connection()
    conn.execute("INSERT INTO images (user_id, image_url) VALUES (?, ?)", (user_id, image_url))
    conn.commit()
    conn.close()

def get_images_by_username(username):
    """Retrieves all image URLs for a specific username."""
    conn = get_db_connection()
    query = '''
        SELECT i.image_url 
        FROM images i
        JOIN users u ON i.user_id = u.id
        WHERE u.username = ?
        ORDER BY i.created_at DESC
    '''
    rows = conn.execute(query, (username,)).fetchall()
    conn.close()
    return [row['image_url'] for row in rows]