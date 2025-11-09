// Get elements
const uploadBtn = document.getElementById('upload-btn');
const fileInput = document.getElementById('file-input');
const viewBtn = document.getElementById('view-btn');
const deleteBtn = document.getElementById('delete-btn');
const limitInput = document.getElementById('limit-input');

// Get username from URL
const urlParams = new URLSearchParams(window.location.search);
const username = urlParams.get('username');

// Upload button - open file input
uploadBtn.onclick = () => {
    fileInput.click();
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
    let url = `/gallery?username=${encodeURIComponent(username)}`;
    if (limit) {
        url += `&limit=${encodeURIComponent(limit)}`;
    }
    window.location.href = url;
};

// Delete button - navigate to auth page with username
deleteBtn.onclick = () => {
    window.location.href = `/auth?username=${encodeURIComponent(username)}`;
};
