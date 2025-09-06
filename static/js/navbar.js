// Navbar scroll effect
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// Initialize navbar functionality
function initNavbar() {
    // Language dropdown functionality
    const languageSelectors = document.querySelectorAll('.language-selector');
    languageSelectors.forEach(selector => {
        selector.addEventListener('mouseenter', function() {
            const dropdown = this.querySelector('.language-dropdown');
            const icon = this.querySelector('.language-btn i');
            
            dropdown.style.opacity = '1';
            dropdown.style.visibility = 'visible';
            dropdown.style.transform = 'translateY(5px)';
            icon.style.transform = 'rotate(180deg)';
        });
        
        selector.addEventListener('mouseleave', function() {
            const dropdown = this.querySelector('.language-dropdown');
            const icon = this.querySelector('.language-btn i');
            
            dropdown.style.opacity = '0';
            dropdown.style.visibility = 'hidden';
            dropdown.style.transform = 'translateY(10px)';
            icon.style.transform = 'rotate(0deg)';
        });
    });

    // Add event listeners for auth buttons
    const signupButtons = document.querySelectorAll('.btn-signin');
    const loginButtons = document.querySelectorAll('.btn-login');
    
    signupButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            openModal('signup-modal');
        });
    });
    
    loginButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            openModal('login-modal');
        });
    });
}

// Initialize navbar when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // If navbar is already loaded, initialize it
    if (document.querySelector('.navbar')) {
        initNavbar();
    }
});