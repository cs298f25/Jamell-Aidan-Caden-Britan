const loginButton = document.getElementById('login-btn');
const usernameInput = document.getElementById('username-input');
const passwordInput = document.getElementById('password-input');

// Handle login button click
loginButton.addEventListener('click', function() {
    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();

    // Check if username or password is empty
    if (!username || !password) {
        alert('Username and password are required');
        return;
    }
    // Go to auth page with username and password
    window.location.href = `/auth?username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`;
});