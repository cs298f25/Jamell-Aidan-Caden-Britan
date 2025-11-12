import sqlite3
from typing import Optional, List, Dict
from pathlib import Path


class DatabaseStorage:
    """SQLite-backed storage for user images."""
    
    def __init__(self, database_path):
        self._database_path = str(database_path)
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize the database with required tables from tables.sql file."""
        # Get the path to tables.sql file (same directory as this file)
        sql_file_path = Path(__file__).parent / 'tables.sql'
        
        if not sql_file_path.exists():
            raise FileNotFoundError(f"tables.sql file not found at {sql_file_path}")
        
        # Read the SQL file
        with open(sql_file_path, 'r') as f:
            sql_script = f.read()
        
        with sqlite3.connect(self._database_path) as connection:
            # Enable foreign key constraints (required for CASCADE deletes)
            connection.execute("PRAGMA foreign_keys = ON")
            
            # Process SQL script: remove comments and split into statements
            lines = []
            for line in sql_script.split('\n'):
                # Remove inline comments (-- comment)
                if '--' in line:
                    line = line[:line.index('--')]
                line = line.strip()
                if line:
                    lines.append(line)
            
            # Join all lines and split by semicolon to get individual statements
            full_script = ' '.join(lines)
            statements = [stmt.strip() for stmt in full_script.split(';') if stmt.strip()]
            
            # Execute each statement
            for statement in statements:
                connection.execute(statement)
            
            connection.commit()
    
    def add_user(self, username: str) -> Optional[int]:
        """Add a new user and return their ID."""
        query = "INSERT INTO users (username) VALUES (?)"
        try:
            with sqlite3.connect(self._database_path) as connection:
                connection.execute("PRAGMA foreign_keys = ON")
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
            connection.execute("PRAGMA foreign_keys = ON")
            connection.row_factory = sqlite3.Row
            row = connection.execute(query, (username,)).fetchone()
            return dict(row) if row else None
    
    def delete_user(self, username: str) -> bool:
        """Delete a user and all associated images."""
        query = "DELETE FROM users WHERE username = ?"
        with sqlite3.connect(self._database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
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
            connection.execute("PRAGMA foreign_keys = ON")
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
            connection.execute("PRAGMA foreign_keys = ON")
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
            connection.execute("PRAGMA foreign_keys = ON")
            cursor = connection.execute(query, (image_id, username))
            connection.commit()
            return cursor.rowcount > 0