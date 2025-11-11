# src/database.py
import pymysql
import os
import dotenv
from pathlib import Path

dotenv.load_dotenv()

# Database configuration from environment variables
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'image_hosting')
DB_PORT = int(os.getenv('DB_PORT', 3306))


def get_connection():
    """Create and return a database connection."""
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.Error as e:
        print(f"Error connecting to database: {e}")
        return None


def initialize_database():
    """Initialize the database by creating tables from tables.sql file."""
    # First, connect without specifying a database to create it if it doesn't exist
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            cursorclass=pymysql.cursors.DictCursor
        )
        with connection.cursor() as cursor:
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
            cursor.execute(f"USE {DB_NAME}")
        connection.close()
    except pymysql.Error as e:
        print(f"Error creating database: {e}")
        return False
    
    # Now connect to the database and create tables
    connection = get_connection()
    if not connection:
        return False
    
    try:
        # Read the SQL file
        sql_file_path = Path(__file__).parent / 'tables.sql'
        with open(sql_file_path, 'r') as file:
            sql_script = file.read()
        
        # Split the script into individual statements
        statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
        
        with connection.cursor() as cursor:
            for statement in statements:
                if statement:
                    try:
                        cursor.execute(statement)
                    except pymysql.Error as e:
                        # Ignore error if table already exists
                        if "already exists" not in str(e).lower() and "duplicate" not in str(e).lower():
                            print(f"Warning: Error executing statement: {e}")
                            # Continue with other statements
        
        connection.commit()
        print("Database initialized successfully")
        return True
    except pymysql.Error as e:
        print(f"Error initializing database: {e}")
        if connection:
            connection.rollback()
        return False
    except FileNotFoundError:
        print(f"Error: tables.sql file not found at {sql_file_path}")
        return False
    finally:
        connection.close()


def get_images(limit=None, user_id=None):
    """Retrieve images from the database.
    
    Args:
        limit: Maximum number of images to return (optional)
        user_id: Filter images by user_id (optional)
    
    Returns:
        List of image dictionaries
    """
    connection = get_connection()
    if not connection:
        return []
    
    try:
        with connection.cursor() as cursor:
            if user_id:
                query = "SELECT id, user_id, image_url, created_at FROM images WHERE user_id = %s ORDER BY created_at DESC"
                if limit:
                    query += f" LIMIT {int(limit)}"
                cursor.execute(query, (user_id,))
            else:
                query = "SELECT id, user_id, image_url, created_at FROM images ORDER BY created_at DESC"
                if limit:
                    query += f" LIMIT {int(limit)}"
                cursor.execute(query)
            
            images = cursor.fetchall()
            return [dict(img) for img in images]
    except pymysql.Error as e:
        print(f"Error fetching images: {e}")
        return []
    finally:
        connection.close()


def add_image(user_id, image_url):
    """Add an image to the database.
    
    Args:
        user_id: ID of the user who uploaded the image
        image_url: URL of the image
    
    Returns:
        True if successful, False otherwise
    """
    connection = get_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO images (user_id, image_url) VALUES (%s, %s)",
                (user_id, image_url)
            )
        connection.commit()
        return True
    except pymysql.Error as e:
        print(f"Error adding image: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()


def get_user_by_username(username):
    """Get a user by username.
    
    Args:
        username: Username to search for
    
    Returns:
        User dictionary or None if not found
    """
    connection = get_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, username, password, created_at FROM users WHERE username = %s",
                (username,)
            )
            user = cursor.fetchone()
            return dict(user) if user else None
    except pymysql.Error as e:
        print(f"Error fetching user: {e}")
        return None
    finally:
        connection.close()


def create_user(username, password):
    """Create a new user.
    
    Args:
        username: Username for the new user
        password: Password for the new user (should be hashed)
    
    Returns:
        User ID if successful, None otherwise
    """
    connection = get_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, password)
            )
            user_id = cursor.lastrowid
        connection.commit()
        return user_id
    except pymysql.Error as e:
        print(f"Error creating user: {e}")
        connection.rollback()
        return None
    finally:
        connection.close()


def get_categories():
    """Retrieve all categories from the database.
    
    Returns:
        List of category dictionaries
    """
    connection = get_connection()
    if not connection:
        return []
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name FROM categories ORDER BY name")
            categories = cursor.fetchall()
            return [dict(cat) for cat in categories]
    except pymysql.Error as e:
        print(f"Error fetching categories: {e}")
        return []
    finally:
        connection.close()


def add_category(name):
    """Add a category to the database.
    
    Args:
        name: Name of the category
    
    Returns:
        True if successful, False otherwise
    """
    connection = get_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO categories (name) VALUES (%s)", (name,))
        connection.commit()
        return True
    except pymysql.Error as e:
        print(f"Error adding category: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()

