// Get elements
const uploadBtn = document.getElementById('upload-btn');
const fileInput = document.getElementById('file-input');
const viewBtn = document.getElementById('view-btn');
const limitInput = document.getElementById('limit-input');

// Get username from URL
const urlParams = new URLSearchParams(window.location.search);
const username = urlParams.get('username');

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
    let url = `/gallery?username=${encodeURIComponent(username)}`;
    if (limit) {
        url += `&limit=${encodeURIComponent(limit)}`;
    }
    window.location.href = url;
};


