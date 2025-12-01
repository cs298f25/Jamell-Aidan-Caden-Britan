import sqlite3
from datetime import datetime

DB_NAME = "database.db"


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.executescript('''
         DROP TABLE IF EXISTS images;
         DROP TABLE IF EXISTS categories;
         DROP TABLE IF EXISTS users;

         CREATE TABLE users
         (
             id         INTEGER PRIMARY KEY AUTOINCREMENT,
             username   TEXT NOT NULL UNIQUE,
             password   TEXT      DEFAULT '',
             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
         );

         CREATE TABLE images
         (
             id         INTEGER PRIMARY KEY AUTOINCREMENT,
             user_id    INTEGER NOT NULL,
             image_url  TEXT    NOT NULL,
             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
             FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
         );

         CREATE TABLE categories
         (
             id         INTEGER PRIMARY KEY AUTOINCREMENT,
             user_id    INTEGER NOT NULL,
             name       TEXT    NOT NULL,
             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
             FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
             UNIQUE (user_id, name)
         );
                         ''')
    conn.commit()
    conn.close()


def get_user_id(username):
    conn = get_db_connection()
    res = conn.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = res.fetchone()
    conn.close()
    return user['id'] if user else None


def create_user(username, password_hash=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password_hash))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id


def get_or_create_user(username):
    user_id = get_user_id(username)
    if user_id:
        return user_id
    return create_user(username)


def get_user(username):
    conn = get_db_connection()
    res = conn.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
    user = res.fetchone()
    conn.close()
    return dict(user) if user else None


def add_image(username, image_url):
    user_id = get_or_create_user(username)
    conn = get_db_connection()
    conn.execute("INSERT INTO images (user_id, image_url) VALUES (?, ?)", (user_id, image_url))
    conn.commit()
    conn.close()


def delete_image(user_id, image_url):
    conn = get_db_connection()
    conn.execute("DELETE FROM images WHERE user_id = ? AND image_url = ?", (user_id, image_url))
    conn.commit()
    rows_affected = conn.total_changes
    conn.close()
    return rows_affected > 0


def delete_image_by_username(username, image_url):
    user_id = get_user_id(username)
    if not user_id:
        return False
    return delete_image(user_id, image_url)


def get_images_by_username(username):
    conn = get_db_connection()
    query = '''
            SELECT i.image_url
            FROM images i
                     JOIN users u ON i.user_id = u.id
            WHERE u.username = ?
            ORDER BY i.created_at DESC \
            '''
    rows = conn.execute(query, (username,)).fetchall()
    conn.close()
    return [row['image_url'] for row in rows]


def category_exists(username, category_name):
    user_id = get_user_id(username)
    if not user_id:
        return None
    conn = get_db_connection()
    existing = conn.execute(
        "SELECT id FROM categories WHERE user_id = ? AND name = ?",
        (user_id, category_name)
    ).fetchone()
    conn.close()
    return existing['id'] if existing else None


def create_category_for_user(username, category_name):
    existing_id = category_exists(username, category_name)
    if existing_id:
        return {'success': False, 'message': 'Category already exists', 'category_id': existing_id}

    user_id = get_or_create_user(username)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO categories (user_id, name) VALUES (?, ?)", (user_id, category_name))
    conn.commit()
    category_id = cursor.lastrowid
    conn.close()
    return {'success': True, 'message': 'Category created', 'category_id': category_id}


def get_categories_from_user(username):
    conn = get_db_connection()
    query = '''
            SELECT c.id, c.name, c.created_at
            FROM categories c
                     JOIN users u ON c.user_id = u.id
            WHERE u.username = ?
            ORDER BY c.name \
            '''
    rows = conn.execute(query, (username,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]
