// Sidebar functionality
function initSidebar() {
    const leftSidebarToggle = document.querySelector('.left-sidebar-toggle');
    const sidebarClose = document.querySelector('.sidebar-close');
    const sidebar = document.querySelector('.sidebar');
    
    if (leftSidebarToggle) {
        leftSidebarToggle.addEventListener('click', function() {
            // Toggle sidebar instead of just opening it
            if (sidebar.classList.contains('open')) {
                sidebar.classList.remove('open');
                document.body.style.overflow = 'auto';
                
                // Remove touch event listener for mobile
                if ('ontouchstart' in window) {
                    document.removeEventListener('touchmove', preventScroll);
                }
            } else {
                sidebar.classList.add('open');
                document.body.style.overflow = 'hidden';
                
                // Add touch event listener for mobile
                if ('ontouchstart' in window) {
                    document.addEventListener('touchmove', preventScroll, { passive: false });
                }
            }
        });
    }

    if (sidebarClose) {
        sidebarClose.addEventListener('click', function() {
            closeSidebar();
        });
    }

    // Close sidebar when clicking outside
    document.addEventListener('click', function(event) {
        if (sidebar.classList.contains('open') && 
            !sidebar.contains(event.target) && 
            (!leftSidebarToggle || !leftSidebarToggle.contains(event.target))) {
            closeSidebar();
        }
    });
    
    // Add event listeners for sidebar auth buttons
    const sidebarSignupButtons = document.querySelectorAll('.sidebar-auth .btn-signin');
    const sidebarLoginButtons = document.querySelectorAll('.sidebar-auth .btn-login');
    
    sidebarSignupButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            openModal('signup-modal');
            closeSidebar();
        });
    });
    
    sidebarLoginButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            openModal('login-modal');
            closeSidebar();
        });
    });
}

// Close sidebar function
function closeSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        sidebar.classList.remove('open');
        document.body.style.overflow = 'auto';
        
        // Remove touch event listener for mobile
        if ('ontouchstart' in window) {
            document.removeEventListener('touchmove', preventScroll);
        }
    }
}

// Prevent scroll on mobile when sidebar is open
function preventScroll(e) {
    e.preventDefault();
}

// Initialize sidebar when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // If sidebar is already loaded, initialize it
    if (document.querySelector('.sidebar')) {
        initSidebar();
    }
});
