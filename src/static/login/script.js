const loginButton = document.getElementById('login-btn');
const usernameInput = document.getElementById('username-input');

// Variable to store username
let username = '';

// Update username variable when input changes
usernameInput.addEventListener('input', function() {
    username = usernameInput.value;
});

// event listener to handle login
loginButton.addEventListener('click', function() {
    // Save username to variable (in case it wasn't captured by input event)
    username = usernameInput.value;
    // You can replace this URL with actual login endpoint
    window.location.href = '/auth';
});
