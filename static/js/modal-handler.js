document.addEventListener('DOMContentLoaded', function () {
    var loginButton = document.querySelector('button[data-bs-tab="login"]');
    var registerButton = document.querySelector('button[data-bs-tab="register"]');

    if (loginButton) {
        loginButton.addEventListener('click', function () {
            var tabEl = document.getElementById('login-tab');
            if (tabEl) {
                var tab = new bootstrap.Tab(tabEl);
                tab.show();
            }
        });
    }

    if (registerButton) {
        registerButton.addEventListener('click', function () {
            var tabEl = document.getElementById('register-tab');
            if (tabEl) {
                var tab = new bootstrap.Tab(tabEl);
                tab.show();
            }
        });
    }
});