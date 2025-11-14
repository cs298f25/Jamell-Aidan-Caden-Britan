import sqlite3
from typing import Optional, List, Dict


class DatabaseStorage:
    """SQLite-backed storage for user images."""
    
    def __init__(self, database_path):
        self._database_path = str(database_path)
        self._initialize_database()
    
    def _initialize_database(self):
        """Create tables if they don't exist."""
        with sqlite3.connect(self._database_path) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            connection.execute("""
                CREATE TABLE IF NOT EXISTS images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    image_url TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            connection.commit()
    
    def add_user(self, username: str) -> Optional[int]:
        """Add a new user and return their ID."""
        query = "INSERT INTO users (username) VALUES (?)"
        try:
            with sqlite3.connect(self._database_path) as connection:
                cursor = connection.execute(query, (username,))
                connection.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Retrieve user information by username."""
        query = """
            SELECT id, username, created_at
            FROM users
            WHERE username = ?
            LIMIT 1
        """
        with sqlite3.connect(self._database_path) as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute(query, (username,)).fetchone()
            return dict(row) if row else None
    
    def delete_user(self, username: str) -> bool:
        """Delete a user and all associated images."""
        query = "DELETE FROM users WHERE username = ?"
        with sqlite3.connect(self._database_path) as connection:
            cursor = connection.execute(query, (username,))
            connection.commit()
            return cursor.rowcount > 0
    
    def add_image(self, username: str, image_url: str) -> Optional[int]:
        """Add an image for a user."""
        # Get user_id
        user = self.get_user(username)
        if not user:
            return None
        
        user_id = user['id']
        
        query = "INSERT INTO images (user_id, image_url) VALUES (?, ?)"
        with sqlite3.connect(self._database_path) as connection:
            cursor = connection.execute(query, (user_id, image_url))
            connection.commit()
            return cursor.lastrowid
    
    def get_images(self, username: str) -> List[Dict]:
        """Get all images for a user."""
        query = """
            SELECT images.id, images.image_url, images.created_at
            FROM images
            INNER JOIN users ON users.id = images.user_id
            WHERE users.username = ?
            ORDER BY images.created_at DESC
        """
        with sqlite3.connect(self._database_path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(query, (username,)).fetchall()
            return [dict(row) for row in rows]
    
    def delete_image(self, username: str, image_id: int) -> bool:
        """Delete a specific image for a user."""
        query = """
            DELETE FROM images
            WHERE id = ?
              AND user_id = (SELECT id FROM users WHERE username = ?)
        """
        with sqlite3.connect(self._database_path) as connection:
            cursor = connection.execute(query, (image_id, username))
            connection.commit()
            return cursor.rowcount > 0


class UserManager:
    """Manages user operations and image storage."""
    
    def __init__(self, storage: DatabaseStorage):
        self.storage = storage
    
    def login_user(self, username: str) -> Dict:
        """Login or create a user if they don't exist."""
        user = self.storage.get_user(username)
        
        if not user:
            # User doesn't exist, create them
            user_id = self.storage.add_user(username)
            user = self.storage.get_user(username)
        
        return user
    
    def add_image(self, username: str, image_url: str) -> Optional[int]:
        """Add an image for a user."""
        return self.storage.add_image(username, image_url)
    
    def list_images(self, username: str) -> List[Dict]:
        """Get all images for a user."""
        return self.storage.get_images(username)