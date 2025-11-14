import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import DatabaseStorage

# Create database directory in the src folder
db_dir = os.path.join(os.path.dirname(__file__), '..', 'src', 'database')
os.makedirs(db_dir, exist_ok=True)

# Create the database
db_path = os.path.join(db_dir, 'app.db')
db = DatabaseStorage(db_path)

print(f"Database created successfully at: {db_path}")

# Optional: Add a test user to verify it works
user_id = db.add_user("testuser")
if user_id:
    print(f"Test user added with ID: {user_id}")
    
    # Retrieve the user to confirm
    user = db.get_user("testuser")
    print(f"Retrieved user: {user}")
else:
    print("Failed to add test user")