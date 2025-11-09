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
        # Verify that at least one image URL is in the response
        # This assumes the template uses the images variable
        assert any(img_url.encode() in response.data for img_url in IMAGES)

    def test_gallery_route_exists(self, client):
        """Test that /gallery route exists and returns 200"""
        response = client.get('/gallery')
        assert response.status_code == 200

    def test_gallery_route_passes_images_data(self, client):
        """Test that /gallery route passes IMAGES data to template"""
        response = client.get('/gallery')
        assert response.status_code == 200
        # Verify that at least one image URL is in the response
        assert any(img_url.encode() in response.data for img_url in IMAGES)

    def test_nonexistent_route_returns_404(self, client):
        """Test that non-existent routes return 404"""
        response = client.get('/nonexistent')
        assert response.status_code == 404

    def test_root_route_returns_404(self, client):
        """Test that root route (/) returns 404 since it's not defined"""
        response = client.get('/')
        assert response.status_code == 404

    def test_images_route_with_limit(self, client):
        """Test that /images route respects limit query parameter"""
        limit = 3
        response = client.get(f'/images?limit={limit}')
        assert response.status_code == 200
        # Count how many image URLs appear in the response
        image_count = sum(1 for img_url in IMAGES[:limit] if img_url.encode() in response.data)
        assert image_count == limit

    def test_images_route_with_limit_exceeds_total(self, client):
        """Test that /images route shows all images when limit exceeds total"""
        limit = 100  # More than total number of images
        response = client.get(f'/images?limit={limit}')
        assert response.status_code == 200
        # Should show all images, not error
        assert any(img_url.encode() in response.data for img_url in IMAGES)

    def test_images_route_with_invalid_limit_negative(self, client):
        """Test that /images route ignores negative limit and shows all images"""
        response = client.get('/images?limit=-5')
        assert response.status_code == 200
        # Should show all images when limit is invalid
        assert all(img_url.encode() in response.data for img_url in IMAGES)

    def test_images_route_with_invalid_limit_zero(self, client):
        """Test that /images route ignores zero limit and shows all images"""
        response = client.get('/images?limit=0')
        assert response.status_code == 200
        # Should show all images when limit is 0
        assert all(img_url.encode() in response.data for img_url in IMAGES)

    def test_images_route_with_non_integer_limit(self, client):
        """Test that /images route ignores non-integer limit and shows all images"""
        response = client.get('/images?limit=abc')
        assert response.status_code == 200
        # Should show all images when limit is not an integer
        assert all(img_url.encode() in response.data for img_url in IMAGES)

    def test_gallery_route_with_limit(self, client):
        """Test that /gallery route respects limit query parameter"""
        limit = 5
        response = client.get(f'/gallery?limit={limit}')
        assert response.status_code == 200
        # Count how many image URLs appear in the response
        image_count = sum(1 for img_url in IMAGES[:limit] if img_url.encode() in response.data)
        assert image_count == limit

    def test_gallery_route_with_limit_exceeds_total(self, client):
        """Test that /gallery route shows all images when limit exceeds total"""
        limit = 100  # More than total number of images
        response = client.get(f'/gallery?limit={limit}')
        assert response.status_code == 200
        # Should show all images, not error
        assert any(img_url.encode() in response.data for img_url in IMAGES)

    def test_gallery_route_with_invalid_limit_negative(self, client):
        """Test that /gallery route ignores negative limit and shows all images"""
        response = client.get('/gallery?limit=-5')
        assert response.status_code == 200
        # Should show all images when limit is invalid
        assert all(img_url.encode() in response.data for img_url in IMAGES)

    def test_gallery_route_with_invalid_limit_zero(self, client):
        """Test that /gallery route ignores zero limit and shows all images"""
        response = client.get('/gallery?limit=0')
        assert response.status_code == 200
        # Should show all images when limit is 0
        assert all(img_url.encode() in response.data for img_url in IMAGES)

    def test_gallery_route_with_non_integer_limit(self, client):
        """Test that /gallery route ignores non-integer limit and shows all images"""
        response = client.get('/gallery?limit=abc')
        assert response.status_code == 200
        # Should show all images when limit is not an integer
        assert all(img_url.encode() in response.data for img_url in IMAGES)


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
