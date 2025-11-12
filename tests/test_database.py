import os
import sys
import sqlite3
from pathlib import Path

# Add the project root to the Python path so we can import from src/
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database import DatabaseStorage


def test_add_user():
    """Test that a user can be added to the database using insert.sql."""
    # Use a temporary test database
    test_db_path = "test_database.db"
    
    # Remove test database if it exists
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Create database instance (this initializes tables)
    db = DatabaseStorage(test_db_path)
    
    # Read and execute the insert.sql file
    insert_sql_path = project_root / "src" / "insert.sql"
    assert insert_sql_path.exists(), f"insert.sql file not found at {insert_sql_path}"
    
    with open(insert_sql_path, 'r') as f:
        insert_sql = f.read().strip()
    
    # Execute the SQL from insert.sql
    with sqlite3.connect(test_db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(insert_sql)
        connection.commit()
    print(f"✓ Executed SQL from insert.sql: {insert_sql}")
    
    # Verify the user exists in the database using DatabaseStorage methods
    user = db.get_user("testuser")
    assert user is not None, "User should exist in database"
    assert user['username'] == "testuser", "Username should match"
    print(f"✓ User retrieved via DatabaseStorage: {user}")
    
    # Verify directly in the database with raw SQL
    with sqlite3.connect(test_db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        cursor = connection.execute("SELECT id, username, created_at FROM users WHERE username = ?", ("testuser",))
        result = cursor.fetchone()
        assert result is not None, "User should exist in database table"
        assert result[1] == "testuser", "Username in database should match"
        print(f"✓ User verified in database table - ID: {result[0]}, Username: {result[1]}, Created: {result[2]}")
    
    # Clean up
    os.remove(test_db_path)
    print("✓ Test passed! User from insert.sql was successfully added to the table.")


if __name__ == "__main__":
    test_add_user()