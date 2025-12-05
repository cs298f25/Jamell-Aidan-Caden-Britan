// Get elements
const uploadBtn = document.getElementById('upload-btn');
const fileInput = document.getElementById('file-input');
const viewBtn = document.getElementById('view-btn');
const limitInput = document.getElementById('limit-input');
const categorySelect = document.getElementById('category-select');
const newCategoryInput = document.getElementById('new-category-input');
const createCategoryBtn = document.getElementById('create-category-btn');
const categoryFeedback = document.getElementById('category-feedback');
const logoutBtn = document.querySelector('.logout-btn');

// Get username from URL
const urlParams = new URLSearchParams(window.location.search);
const username = urlParams.get('username');

// Store username in sessionStorage after successful login (when password was provided)
const passwordFromUrl = urlParams.get('password');
if (username && passwordFromUrl) {
    sessionStorage.setItem('username', username);
    // Remove password from the URL so it isn't exposed in the address bar or history
    const cleanUrl = new URL(window.location.href);
    cleanUrl.searchParams.delete('password');
    window.history.replaceState({}, '', cleanUrl);
}

// Load categories on page load
async function loadCategories() {
    if (!username) return;
    try {
        const response = await fetch(`/api/categories?username=${encodeURIComponent(username)}`);
        const categories = await response.json();
        // Clear existing options except "Uncategorized"
        categorySelect.innerHTML = '<option value="uncategorized">Uncategorized</option>';
        // Add categories from database
        categories.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat.name;
            option.textContent = cat.name;
            categorySelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

// Create new category
createCategoryBtn.onclick = async () => {
    const categoryName = newCategoryInput.value.trim();
    if (!categoryName) {
        showFeedback('Please enter a category name', 'error');
        return;
    }
    if (!username) {
        showFeedback('Username is required', 'error');
        return;
    }
    try {
        const response = await fetch('/api/categories', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                category_name: categoryName
            })
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            showFeedback('Category created successfully!', 'success');
            newCategoryInput.value = '';
            await loadCategories();
            categorySelect.value = categoryName;
        } else {
            showFeedback(result.message || 'Failed to create category', 'error');
        }
    } catch (error) {
        console.error('Error creating category:', error);
        showFeedback('An error occurred while creating category', 'error');
    }
};

// Show feedback message
function showFeedback(message, type) {
    categoryFeedback.textContent = message;
    categoryFeedback.className = `feedback ${type}`;
    setTimeout(() => {
        categoryFeedback.textContent = '';
        categoryFeedback.className = 'feedback';
    }, 3000);
}

// Load categories when page loads
loadCategories();

// Upload button - open file input
uploadBtn.onclick = () => {
    fileInput.click();
};

// Handle File Selection and Upload
fileInput.onchange = async () => {
    if (fileInput.files.length > 0) {
        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);
        formData.append('username', username);
        
        // Get selected category
        const category = categorySelect.value || 'uncategorized';
        formData.append('category', category);

        // Change button text to indicate loading (Optional UX)
        const originalText = uploadBtn.innerText;
        uploadBtn.innerText = "Uploading...";

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                alert('Image uploaded successfully!');
            } else {
                alert('Upload failed.');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred during upload.');
        } finally {
            uploadBtn.innerText = originalText;
            fileInput.value = ''; // Clear input
        }
    }
};

// View button - show limit input and navigate to gallery page with username and limit
viewBtn.onclick = () => {
    // Show limit input if it's hidden
    if (limitInput.style.display === 'none' || limitInput.style.display === '') {
        limitInput.style.display = 'block';
        return; // Show input first, wait for second click
    }
    // On second click, navigate to gallery
    const limit = limitInput.value.trim();
    // Store username in sessionStorage for later use
    if (username) {
        sessionStorage.setItem('username', username);
    }
    let url = `/gallery?username=${encodeURIComponent(username)}`;
    if (limit) {
        url += `&limit=${encodeURIComponent(limit)}`;
    }
    window.location.href = url;
};

// Logout button - navigate back to login page and clear session
if (logoutBtn) {
    logoutBtn.onclick = () => {
        sessionStorage.removeItem('username');
        window.location.href = '/';
    };
}

