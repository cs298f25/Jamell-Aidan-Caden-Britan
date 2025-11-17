"""
In-memory database implementation using Python lists and dictionaries.
"""

_users = []  # List of user dictionaries
_images = []  # List of image dictionaries

def addUser(username):
    """
    Add a new user to the database.
    """
    # Check if user already exists
    if getUser(username) is not None:
        return False
    
    # Add new user
    _users.append({"username": username})
    return True

def getUser(username):
    """
    Get a user by username.
    """
    for user in _users:
        if user["username"] == username:
            return user
    return None

def deleteUser(username):
    """
    Delete a user and all their images from the database.
    """
    # Check if user exists
    user = getUser(username)
    if user is None:
        return False
    
    # Remove user
    _users.remove(user)
    
    # Remove all images for this user
    _images[:] = [img for img in _images if img["username"] != username]
    
    return True

def addImages(username, category, imageurl):
    """
    Add an image URL for a user in a specific category.
    """
    # Add the image
    _images.append({
        "username": username,
        "category": category,
        "imageurl": imageurl
    })
    return True

def getImages(username, category):
    """
    Get all image URLs for a user in a specific category.
    """
    # Filter images by username and category
    matching_images = [
        img["imageurl"] 
        for img in _images 
        if img["username"] == username and img["category"] == category
    ]
    return matching_images

def deleteImage(username, category):
    """
    Delete all images for a user in a specific category.
    """
    # Count images before deletion
    initial_count = len(_images)
    
    # Remove images matching username and category
    _images[:] = [
        img 
        for img in _images 
        if not (img["username"] == username and img["category"] == category)
    ]
    
    # Return True if any images were deleted
    return len(_images) < initial_count

def clear_all():
    """
    Clear all data from the in-memory database.
    """
    global _users, _images
    _users.clear()
    _images.clear()

