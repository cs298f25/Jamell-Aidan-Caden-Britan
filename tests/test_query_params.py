import pytest
from src.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

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

def test_auth_requires_password(client):
    response = client.get('/auth?username=testuser123')
    assert response.status_code == 400
    assert b'Password parameter is required' in response.data

def test_auth_rejects_empty_password(client):
    response = client.get('/auth?username=testuser123&password=')
    assert response.status_code == 400
    assert b'Password parameter is required' in response.data

