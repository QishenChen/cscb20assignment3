document.addEventListener('DOMContentLoaded', function() {
    // Find the login form element
    var form = document.getElementById('form_to_submit');

    // Add an event listener for form submission
    form.addEventListener('submit', function(event) {
        // Prevent the default form submission behavior
        event.preventDefault();

        // Get the username and password values from the form
        var username = document.getElementById('username').value;
        var password = document.getElementById('password').value;

        // Send an AJAX request to your Flask backend
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/login', true);
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    // Redirect to home page on successful login
                    window.location.href = '/';
                } else {
                    // Display an error message
                    alert('Invalid username or password');
                }
            }
        };
        xhr.send('username=' + encodeURIComponent(username) + '&password=' + encodeURIComponent(password));
    });
});
