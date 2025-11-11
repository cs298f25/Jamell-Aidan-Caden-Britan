# Database Setup Guide

This guide explains how to set up and use the MySQL database with the image hosting platform.

## Prerequisites

1. **MySQL Server**: Make sure MySQL is installed and running on your system
2. **Python Dependencies**: Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Database Configuration

The database configuration is managed through environment variables. Create a `.env` file in the project root with the following variables:

```env
# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=image_hosting
DB_PORT=3306
```

### Default Values

If environment variables are not set, the following defaults are used:
- `DB_HOST`: localhost
- `DB_USER`: root
- `DB_PASSWORD`: (empty string)
- `DB_NAME`: image_hosting
- `DB_PORT`: 3306

## Database Schema

The database uses three main tables defined in `src/tables.sql`:

1. **users**: Stores user accounts
   - `id`: Primary key (auto-increment)
   - `username`: Unique username
   - `password`: Hashed password (should be hashed in production)
   - `created_at`: Timestamp of account creation

2. **images**: Stores image metadata
   - `id`: Primary key (auto-increment)
   - `user_id`: Foreign key to users table
   - `image_url`: URL of the stored image
   - `created_at`: Timestamp of image upload
   - Foreign key constraint: `user_id` references `users(id)` with cascade delete

3. **categories**: Stores image categories
   - `id`: Primary key (auto-increment)
   - `name`: Category name

## Automatic Initialization

The database is automatically initialized when the Flask app starts:

1. **Database Creation**: The database is created if it doesn't exist
2. **Table Creation**: Tables are created from `src/tables.sql`
3. **Data Seeding**: If the database is empty, it's seeded with:
   - A default user account (username: 'default')
   - Placeholder images from the `IMAGES` constant

## Manual Database Initialization

If you need to initialize the database manually, you can do so programmatically:

```python
from src import database

# Initialize database and create tables
database.initialize_database()
```

## Using the Database

### Getting Images

```python
from src import database

# Get all images
images = database.get_images()

# Get limited number of images
images = database.get_images(limit=10)

# Get images for a specific user
images = database.get_images(user_id=1)
```

### Adding Images

```python
from src import database

# Add an image (requires user_id)
user_id = 1
image_url = "https://example.com/image.jpg"
database.add_image(user_id, image_url)
```

### User Management

```python
from src import database

# Create a user
user_id = database.create_user('username', 'password')

# Get user by username
user = database.get_user_by_username('username')
```

### Category Management

```python
from src import database

# Get all categories
categories = database.get_categories()

# Add a category
database.add_category('Nature')
```

## Running the Application

1. **Set up environment variables** in `.env` file
2. **Start MySQL server** (if not already running)
3. **Run the Flask application**:
   ```bash
   cd src
   python app.py
   ```

The database will be automatically initialized on first run.

## Troubleshooting

### Database Connection Errors

If you see connection errors, check:
- MySQL server is running
- Database credentials in `.env` are correct
- MySQL user has permission to create databases
- Firewall settings allow connections to MySQL

### Table Already Exists Errors

The initialization handles existing tables gracefully. If you see warnings about tables already existing, this is normal and can be ignored.

### Empty Image Lists

If images don't appear:
- Check if the database was seeded (should happen automatically)
- Verify that images exist in the database:
  ```python
  from src import database
  images = database.get_images()
  print(f"Found {len(images)} images")
  ```

## Production Considerations

1. **Password Hashing**: The default user creation uses plain text passwords. In production, always hash passwords using a library like `bcrypt` or `werkzeug.security`.

2. **Database Security**: 
   - Use strong database passwords
   - Restrict database user permissions
   - Use SSL connections for remote databases
   - Regularly backup the database

3. **Connection Pooling**: For production, consider using connection pooling to manage database connections more efficiently.

4. **Environment Variables**: Never commit `.env` files to version control. Use environment-specific configuration management.



