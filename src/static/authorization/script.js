const uploadBtn = document.getElementById('upload-btn');
const fileInput = document.getElementById('file-input');
const viewBtn = document.getElementById('view-btn');
const deleteBtn = document.getElementById('delete-btn');

// upload button - open file input
uploadBtn.onclick = () => {
    fileInput.click();
};

// View button - navigate to user images page
viewBtn.onclick = () => {
    window.location.href = '/images';
};

// Delete button - navigate to user images page (can delete there)
deleteBtn.onclick = () => {
    window.location.href = '/auth';
};
