import pytest
import sys
from pathlib import Path
from flask import Flask

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.app import app

class TestAppRoutes:
    """Test suite for Flask routes (HTML + client-side rendering)"""
    @pytest.fixture
    def client(self):
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_auth_route_exists(self, client):
        response = client.get('/auth?username=testuser123')
        assert response.status_code == 200
        assert b'authorization' in response.data.lower()

    def test_login_route_exists(self, client):
        response = client.get('/')
        assert response.status_code == 200
        assert b'login' in response.data.lower()

    def test_links_route_renders_template(self, client):
        response = client.get('/links')
        assert response.status_code == 200
        # Check for HTML elements that JS will populate
        assert b'id="image-links"' in response.data
        assert b'id="image-link-template"' in response.data
        # Check gallery link exists
        assert b'View gallery' in response.data

    def test_gallery_route_renders_template(self, client):
        response = client.get('/gallery')
        assert response.status_code == 200
        assert b'id="image-grid"' in response.data
        assert b'id="image-card-template"' in response.data

    def test_nonexistent_route_returns_404(self, client):
        response = client.get('/nonexistent')
        assert response.status_code == 404

    def test_root_route_exists(self, client):
        response = client.get('/')
        assert response.status_code == 200

class TestAppConfiguration:
    """Basic sanity checks"""

    def test_app_instance_exists(self):
        assert app is not None
        assert isinstance(app, Flask)

    def test_routes_are_registered(self):
        rules = [str(rule) for rule in app.url_map.iter_rules()]
        assert '/auth' in rules
        assert '/' in rules
        assert '/links' in rules
        assert '/gallery' in rules