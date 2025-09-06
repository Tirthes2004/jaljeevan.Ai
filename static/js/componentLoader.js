// Component loader to dynamically load navbar, sidebar, and auth modals
document.addEventListener('DOMContentLoaded', function() {
    // Load navbar
    fetch('/templates/navbar.html')
        .then(response => response.text())
        .then(data => {
            document.getElementById('navbar-container').innerHTML = data;
            // Reinitialize navbar functionality after loading
            if (typeof initNavbar === 'function') {
                initNavbar();
            }
        })
        .catch(error => console.error('Error loading navbar:', error));

    // Load sidebar
    fetch('/templates/sidebar.html')
        .then(response => response.text())
        .then(data => {
            document.getElementById('sidebar-container').innerHTML = data;
            // Reinitialize sidebar functionality after loading
            if (typeof initSidebar === 'function') {
                initSidebar();
            }
        })
        .catch(error => console.error('Error loading sidebar:', error));

    // Load auth modals
    fetch('/templates/auth.html')
        .then(response => response.text())
        .then(data => {
            document.getElementById('auth-modals-container').innerHTML = data;
            // Reinitialize auth functionality after loading
            if (typeof initAuth === 'function') {
                initAuth();
            }
            
            // Ensure modals are closed on page load
            closeModal('signup-modal');
            closeModal('login-modal');
        })
        .catch(error => console.error('Error loading auth modals:', error));
});