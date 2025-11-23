const loginButton = document.getElementById('login-btn');
const usernameInput = document.getElementById('username-input');

// Handle login button click
loginButton.addEventListener('click', function() {
    const username = usernameInput.value.trim();

    // Check if username is empty
    if (!username) {
        alert('Username is required');
        return;
    }
    // Go to auth page with username
    window.location.href = `/auth?username=${encodeURIComponent(username)}`;
});