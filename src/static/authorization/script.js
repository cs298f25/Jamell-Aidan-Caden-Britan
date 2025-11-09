// Get elements
const uploadBtn = document.getElementById('upload-btn');
const fileInput = document.getElementById('file-input');
const viewBtn = document.getElementById('view-btn');
const deleteBtn = document.getElementById('delete-btn');

// Get username from URL
const urlParams = new URLSearchParams(window.location.search);
const username = urlParams.get('username');

// Upload button - open file input
uploadBtn.onclick = () => {
    fileInput.click();
};

// View button - navigate to auth page with username
viewBtn.onclick = () => {
    window.location.href = `/auth?username=${encodeURIComponent(username)}`;
};

// Delete button - navigate to auth page with username
deleteBtn.onclick = () => {
    window.location.href = `/auth?username=${encodeURIComponent(username)}`;
};
