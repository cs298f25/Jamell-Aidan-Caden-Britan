import pytest
from io import BytesIO
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))
from src.app import app
from src.database import database

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def reset_database():
    database.init_db()
    yield

def test_login_page_loads(client):
    response = client.get('/')
    assert response.status_code == 200

def test_auth_creates_user(client):
    response = client.get('/auth?username=alice&password=testpassword123')
    assert response.status_code == 200
    user_id = database.get_user_id('alice')
    password_hash = database.get_user('alice')['password']
    assert user_id is not None

def test_auth_missing_username_fails(client):
    response = client.get('/auth')
    assert response.status_code == 400

def test_gallery_page_loads(client):
    response = client.get('/gallery')
    assert response.status_code == 200

def test_links_page_loads(client):
    response = client.get('/links')
    assert response.status_code == 200

def test_get_images_empty_username(client):
    response = client.get('/api/images')
    assert response.status_code == 200
    assert response.json == []

def test_get_images_nonexistent_user(client):
    response = client.get('/api/images?username=nobody')
    assert response.status_code == 200
    assert response.json == []

def test_upload_missing_file(client):
    response = client.post('/api/upload', data={'username': 'bob'})
    assert response.status_code == 400
    assert 'error' in response.json

def test_upload_missing_username(client):
    data = {'file': (BytesIO(b'fake image'), 'test.png')}
    response = client.post('/api/upload', data=data)
    assert response.status_code == 400

def test_delete_image_missing_fields(client):
    response = client.delete('/api/images/delete', json={'username': 'bob'})
    assert response.status_code == 400
    assert 'error' in response.json

def test_get_categories_empty_username(client):
    response = client.get('/api/categories')
    assert response.status_code == 200
    assert response.json == []

def test_create_category_success(client):
    response = client.post('/api/categories', json={
        'username': 'charlie',
        'category_name': 'designs'
    })
    assert response.status_code == 200
    assert response.json['success'] == True

def test_create_category_duplicate_fails(client):
    client.post('/api/categories', json={
        'username': 'dave',
        'category_name': 'photos'
    })
    response = client.post('/api/categories', json={
        'username': 'dave',
        'category_name': 'photos'
    })
    assert response.status_code == 400
    assert response.json['success'] == False

def test_create_category_missing_fields(client):
    response = client.post('/api/categories', json={'username': 'eve'})
    assert response.status_code == 400
    assert 'error' in response.json

def test_nonexistent_route(client):
    response = client.get('/fake_route')
    assert response.status_code == 404