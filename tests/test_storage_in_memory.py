import pytest
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database import storageInMemory


class TestUserOperations:
    """Test suite for user-related operations"""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Clear database before and after each test"""
        storageInMemory.clear_all()
        yield
        storageInMemory.clear_all()

    def test_add_user_success(self):
        """Test adding a new user successfully"""
        result = storageInMemory.addUser("testuser")
        assert result is True
        user = storageInMemory.getUser("testuser")
        assert user is not None
        assert user["username"] == "testuser"

    def test_add_user_duplicate(self):
        """Test adding a duplicate user returns False"""
        storageInMemory.addUser("testuser")
        result = storageInMemory.addUser("testuser")
        assert result is False

    def test_get_user_exists(self):
        """Test getting an existing user"""
        storageInMemory.addUser("testuser")
        user = storageInMemory.getUser("testuser")
        assert user is not None
        assert user["username"] == "testuser"

    def test_get_user_not_exists(self):
        """Test getting a non-existent user returns None"""
        user = storageInMemory.getUser("nonexistent")
        assert user is None

    def test_delete_user_success(self):
        """Test deleting an existing user"""
        storageInMemory.addUser("testuser")
        result = storageInMemory.deleteUser("testuser")
        assert result is True
        user = storageInMemory.getUser("testuser")
        assert user is None

    def test_delete_user_not_exists(self):
        """Test deleting a non-existent user returns False"""
        result = storageInMemory.deleteUser("nonexistent")
        assert result is False

    def test_delete_user_removes_images(self):
        """Test that deleting a user also removes all their images"""
        storageInMemory.addUser("testuser")
        storageInMemory.addImages("testuser", "category1", "url1")
        storageInMemory.addImages("testuser", "category2", "url2")
        
        storageInMemory.deleteUser("testuser")
        
        images = storageInMemory.getImages("testuser", "category1")
        assert images == []
        images = storageInMemory.getImages("testuser", "category2")
        assert images == []


class TestImageOperations:
    """Test suite for image-related operations"""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Clear database and add test user before and after each test"""
        storageInMemory.clear_all()
        storageInMemory.addUser("testuser")
        yield
        storageInMemory.clear_all()

    def test_add_image_success(self):
        """Test adding an image successfully"""
        result = storageInMemory.addImages("testuser", "category1", "http://example.com/image1.jpg")
        assert result is True
        images = storageInMemory.getImages("testuser", "category1")
        assert "http://example.com/image1.jpg" in images

    def test_add_multiple_images_same_category(self):
        """Test adding multiple images to the same category"""
        storageInMemory.addImages("testuser", "category1", "url1")
        storageInMemory.addImages("testuser", "category1", "url2")
        storageInMemory.addImages("testuser", "category1", "url3")
        
        images = storageInMemory.getImages("testuser", "category1")
        assert len(images) == 3
        assert "url1" in images
        assert "url2" in images
        assert "url3" in images

    def test_add_images_different_categories(self):
        """Test adding images to different categories"""
        storageInMemory.addImages("testuser", "category1", "url1")
        storageInMemory.addImages("testuser", "category2", "url2")
        
        images1 = storageInMemory.getImages("testuser", "category1")
        images2 = storageInMemory.getImages("testuser", "category2")
        
        assert "url1" in images1
        assert "url2" not in images1
        assert "url2" in images2
        assert "url1" not in images2

    def test_get_images_empty_category(self):
        """Test getting images from an empty category returns empty list"""
        images = storageInMemory.getImages("testuser", "category1")
        assert images == []

    def test_get_images_different_user(self):
        """Test that images are isolated by username"""
        storageInMemory.addUser("user1")
        storageInMemory.addUser("user2")
        storageInMemory.addImages("user1", "category1", "url1")
        storageInMemory.addImages("user2", "category1", "url2")
        
        images1 = storageInMemory.getImages("user1", "category1")
        images2 = storageInMemory.getImages("user2", "category1")
        
        assert "url1" in images1
        assert "url2" not in images1
        assert "url2" in images2
        assert "url1" not in images2

    def test_delete_image_success(self):
        """Test deleting images from a category"""
        storageInMemory.addImages("testuser", "category1", "url1")
        storageInMemory.addImages("testuser", "category1", "url2")
        storageInMemory.addImages("testuser", "category2", "url3")
        
        result = storageInMemory.deleteImage("testuser", "category1")
        assert result is True
        
        images1 = storageInMemory.getImages("testuser", "category1")
        images2 = storageInMemory.getImages("testuser", "category2")
        
        assert images1 == []
        assert "url3" in images2

    def test_delete_image_not_exists(self):
        """Test deleting images from a non-existent category returns False"""
        result = storageInMemory.deleteImage("testuser", "nonexistent")
        assert result is False

    def test_delete_image_removes_all_in_category(self):
        """Test that deleteImage removes all images in the category"""
        storageInMemory.addImages("testuser", "category1", "url1")
        storageInMemory.addImages("testuser", "category1", "url2")
        storageInMemory.addImages("testuser", "category1", "url3")
        
        storageInMemory.deleteImage("testuser", "category1")
        
        images = storageInMemory.getImages("testuser", "category1")
        assert images == []

    def test_delete_image_only_affects_specified_category(self):
        """Test that deleteImage only affects the specified category"""
        storageInMemory.addImages("testuser", "category1", "url1")
        storageInMemory.addImages("testuser", "category2", "url2")
        storageInMemory.addImages("testuser", "category2", "url3")
        
        storageInMemory.deleteImage("testuser", "category1")
        
        images1 = storageInMemory.getImages("testuser", "category1")
        images2 = storageInMemory.getImages("testuser", "category2")
        
        assert images1 == []
        assert len(images2) == 2
        assert "url2" in images2
        assert "url3" in images2


class TestIntegration:
    """Integration tests combining multiple operations"""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Clear database before and after each test"""
        storageInMemory.clear_all()
        yield
        storageInMemory.clear_all()

    def test_complete_workflow(self):
        """Test a complete workflow: add user, add images, get images, delete images, delete user"""
        # Add user
        assert storageInMemory.addUser("testuser") is True
        
        # Add images
        storageInMemory.addImages("testuser", "pets", "dog.jpg")
        storageInMemory.addImages("testuser", "pets", "cat.jpg")
        storageInMemory.addImages("testuser", "travel", "beach.jpg")
        
        # Get images
        pet_images = storageInMemory.getImages("testuser", "pets")
        assert len(pet_images) == 2
        assert "dog.jpg" in pet_images
        assert "cat.jpg" in pet_images
        
        # Delete images from one category
        assert storageInMemory.deleteImage("testuser", "pets") is True
        pet_images = storageInMemory.getImages("testuser", "pets")
        assert pet_images == []
        
        # Other category should still exist
        travel_images = storageInMemory.getImages("testuser", "travel")
        assert "beach.jpg" in travel_images
        
        # Delete user (should also delete remaining images)
        assert storageInMemory.deleteUser("testuser") is True
        travel_images = storageInMemory.getImages("testuser", "travel")
        assert travel_images == []

    def test_multiple_users_independent(self):
        """Test that operations on one user don't affect another"""
        storageInMemory.addUser("user1")
        storageInMemory.addUser("user2")
        
        storageInMemory.addImages("user1", "category1", "url1")
        storageInMemory.addImages("user2", "category1", "url2")
        
        # Delete images for user1, user2 should be unaffected
        storageInMemory.deleteImage("user1", "category1")
        
        images1 = storageInMemory.getImages("user1", "category1")
        images2 = storageInMemory.getImages("user2", "category1")
        
        assert images1 == []
        assert "url2" in images2
        
        # Delete user1, user2 should be unaffected
        storageInMemory.deleteUser("user1")
        
        user1 = storageInMemory.getUser("user1")
        user2 = storageInMemory.getUser("user2")
        images2 = storageInMemory.getImages("user2", "category1")
        
        assert user1 is None
        assert user2 is not None
        assert "url2" in images2

