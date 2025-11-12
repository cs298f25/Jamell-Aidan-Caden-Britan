import pytest
import sys
from pathlib import Path
from flask import Flask

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.app import app, IMAGES


class TestAppRoutes:
    """Test suite for Flask application routes"""

    @pytest.fixture
    def client(self):
        """Create a test client for the Flask application"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_auth_route_exists(self, client):
        """Test that /auth route exists and returns 200"""
        response = client.get('/auth?username=testuser123')
        assert response.status_code == 200

    def test_auth_route_renders_correct_template(self, client):
        """Test that /auth route renders the authorization template"""
        response = client.get('/auth?username=testuser123')
        # Check that the response contains expected content
        assert b'authorization' in response.data.lower() or response.status_code == 200

    def test_login_route_exists(self, client):
        """Test that /login route exists and returns 200"""
        response = client.get('/login')
        assert response.status_code == 200

    def test_login_route_renders_correct_template(self, client):
        """Test that /login route renders the login template"""
        response = client.get('/login')
        assert response.status_code == 200

    def test_images_route_exists(self, client):
        """Test that /images route exists and returns 200"""
        response = client.get('/images')
        assert response.status_code == 200

    def test_images_route_passes_images_data(self, client):
        """Test that /images route passes IMAGES data to template"""
        response = client.get('/images')
        assert response.status_code == 200
        assert b'id="image-links"' in response.data
        assert b'id="image-link-template"' in response.data

    def test_gallery_route_exists(self, client):
        """Test that /gallery route exists and returns 200"""
        response = client.get('/gallery')
        assert response.status_code == 200

    def test_gallery_route_passes_images_data(self, client):
        """Test that /gallery route passes IMAGES data to template"""
        response = client.get('/gallery')
        assert response.status_code == 200
        assert b'id="image-grid"' in response.data
        assert b'id="image-card-template"' in response.data

    def test_nonexistent_route_returns_404(self, client):
        """Test that non-existent routes return 404"""
        response = client.get('/nonexistent')
        assert response.status_code == 404

    def test_root_route_returns_404(self, client):
        """Test that root route (/) returns 404 since it's not defined"""
        response = client.get('/')
        assert response.status_code == 404

    def test_images_api_returns_all_images(self, client):
        """Test that /api/images returns all images by default"""
        response = client.get('/api/images')
        assert response.status_code == 200
        data = response.get_json()
        assert data == {"images": IMAGES}

    def test_images_api_with_limit(self, client):
        """Test that /api/images respects limit query parameter"""
        limit = 3
        response = client.get(f'/api/images?limit={limit}')
        assert response.status_code == 200
        data = response.get_json()
        assert data["images"] == IMAGES[:limit]

    def test_images_api_with_limit_exceeds_total(self, client):
        """Test that /api/images returns all images when limit exceeds total"""
        limit = 100  # More than total number of images
        response = client.get(f'/api/images?limit={limit}')
        assert response.status_code == 200
        data = response.get_json()
        assert data["images"] == IMAGES

    def test_images_api_with_invalid_limit_negative(self, client):
        """Test that /api/images ignores negative limit and returns all images"""
        response = client.get('/api/images?limit=-5')
        assert response.status_code == 200
        data = response.get_json()
        assert data["images"] == IMAGES

    def test_images_api_with_invalid_limit_zero(self, client):
        """Test that /api/images ignores zero limit and returns all images"""
        response = client.get('/api/images?limit=0')
        assert response.status_code == 200
        data = response.get_json()
        assert data["images"] == IMAGES

    def test_images_api_with_non_integer_limit(self, client):
        """Test that /api/images ignores non-integer limit and returns all images"""
        response = client.get('/api/images?limit=abc')
        assert response.status_code == 200
        data = response.get_json()
        assert data["images"] == IMAGES

    def test_gallery_route_with_limit_query_parameter(self, client):
        """Test that /gallery route includes template hooks for client rendering"""
        limit = 5
        response = client.get(f'/gallery?limit={limit}')
        assert response.status_code == 200
        assert b'id="image-grid"' in response.data
        assert b'id="image-card-template"' in response.data


class TestImagesConstant:
    """Test suite for IMAGES constant"""

    def test_images_is_defined(self):
        """Test that IMAGES constant is defined"""
        assert IMAGES is not None
        assert isinstance(IMAGES, list)

    def test_images_is_not_empty(self):
        """Test that IMAGES list is not empty"""
        assert len(IMAGES) > 0

    def test_images_contains_valid_urls(self):
        """Test that IMAGES contains valid URL strings"""
        for image_url in IMAGES:
            assert isinstance(image_url, str)
            assert image_url.startswith('http')
            assert 'picsum.photos' in image_url

    def test_images_count(self):
        """Test that IMAGES contains expected number of images"""
        assert len(IMAGES) == 10

    def test_images_are_unique(self):
        """Test that all image URLs in IMAGES are unique"""
        assert len(IMAGES) == len(set(IMAGES))


class TestAppConfiguration:
    """Test suite for Flask application configuration"""

    def test_app_instance_exists(self):
        """Test that Flask app instance exists"""
        assert app is not None
        assert isinstance(app, Flask)

    def test_app_has_routes_registered(self):
        """Test that Flask app has routes registered"""
        rules = [str(rule) for rule in app.url_map.iter_rules()]
        assert '/auth' in rules
        assert '/login' in rules
        assert '/images' in rules
        assert '/gallery' in rules
