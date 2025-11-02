const uploadBtn = document.getElementById('upload-btn');
const viewBtn = document.getElementById('view-btn');
const deleteBtn = document.getElementById('delete-btn');

// Upload button - navigate to user images page
uploadBtn.onclick = () => {
    window.location.href = '/api/user';
};

// View button - navigate to user images page
viewBtn.onclick = () => {
    window.location.href = '/api/user';
};

// Delete button - navigate to user images page (can delete there)
deleteBtn.onclick = () => {
    window.location.href = '/api/user';
};
