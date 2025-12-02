import pytest
from src.app import app
from database import database

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def reset_database():
    database.init_db()
    yield

def test_auth_requires_username(client):
    response = client.get('/auth')
    assert response.status_code == 400
    assert b'Username parameter is required' in response.data

def test_auth_rejects_empty_username(client):
    response = client.get('/auth?username=&password=testpassword123')
    assert response.status_code == 400
    assert b'Username parameter is required' in response.data

def test_auth_rejects_whitespace_username(client):
    response = client.get('/auth?username=   &password=testpassword123')
    assert response.status_code == 400
    assert b'Username parameter is required' in response.data

def test_auth_accepts_valid_username(client):
    response = client.get('/auth?username=testuser123&password=testpassword123')
    assert response.status_code == 200
    assert b'username-display' in response.data
    assert b'testuser123' in response.data

def test_auth_handles_special_characters(client):
    response = client.get('/auth?username=test%20user&password=testpassword123')
    assert response.status_code == 200
    assert b'username-display' in response.data

def test_auth_handles_encoded_username(client):
    response = client.get('/auth?username=hello%26world&password=testpassword123')
    assert response.status_code == 200
    assert b'username-display' in response.data

def test_login_no_username_required(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'username-input' in response.data

def test_auth_displays_username(client):
    response = client.get('/auth?username=john_doe&password=testpassword123')
    assert response.status_code == 200
    assert b'username-display' in response.data
    assert b'john_doe' in response.data

def test_auth_without_password_for_nonexistent_user(client):
    """Test that username without password fails if user doesn't exist"""
    response = client.get('/auth?username=nonexistentuser')
    assert response.status_code == 404
    assert b'User not found' in response.data

def test_auth_without_password_for_existing_user(client):
    """Test that username without password works if user exists (for returning users)"""
    # First create the user with password
    client.get('/auth?username=returninguser&password=testpassword123')
    # Then access auth page without password (simulating return from gallery/links)
    response = client.get('/auth?username=returninguser')
    assert response.status_code == 200
    assert b'username-display' in response.data
    assert b'returninguser' in response.data

def test_auth_rejects_empty_password_string(client):
    """Test that empty password string is treated as no password"""
    # Empty password string should be treated same as missing password
    response = client.get('/auth?username=nonexistentuser&password=')
    assert response.status_code == 404
    assert b'User not found' in response.data

