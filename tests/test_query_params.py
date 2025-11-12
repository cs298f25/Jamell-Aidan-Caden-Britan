import unittest
from src.app import app



class TestUsernameParameter(unittest.TestCase):

    def setUp(self):
        """Set up test client before each test"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_auth_route_requires_username(self):
        """Test that /auth route requires username parameter"""
        response = self.client.get('/auth')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Username parameter is required', response.data)

    def test_auth_route_with_empty_username(self):
        """Test that /auth route rejects empty username parameter"""
        response = self.client.get('/auth?username=')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Username parameter is required', response.data)

    def test_auth_route_with_whitespace_only_username(self):
        """Test that /auth route rejects whitespace-only username parameter"""
        response = self.client.get('/auth?username=   ')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Username parameter is required', response.data)

    def test_auth_route_with_valid_username(self):
        """Test that /auth route accepts valid username parameter"""
        response = self.client.get('/auth?username=testuser123')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'username-display', response.data)
        self.assertIn(b'testuser123', response.data)

    def test_auth_route_with_special_characters(self):
        """Test that /auth route handles special characters in username"""
        response = self.client.get('/auth?username=test%20user')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'username-display', response.data)

    def test_auth_route_with_encoded_username(self):
        """Test that /auth route handles URL-encoded username parameter"""
        response = self.client.get('/auth?username=hello%26world')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'username-display', response.data)

    def test_login_route_no_username_required(self):
        """Test that /login route does not require username parameter"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'username-input', response.data)

    def test_auth_route_username_displayed(self):
        """Test that username parameter is displayed on the auth page"""
        username_value = "john_doe"
        response = self.client.get(f'/auth?username={username_value}')
        self.assertEqual(response.status_code, 200)
        # The username should be displayed in the page
        self.assertIn(b'username-display', response.data)
        self.assertIn(username_value.encode(), response.data)


if __name__ == '__main__':
    unittest.main()

