// ============================================
// AUTH MODAL FUNCTIONALITY - COMPLETE VERSION
// ============================================

// Modal Control Functions
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        // Add touch event listener for mobile
        if ('ontouchstart' in window) {
            document.addEventListener('touchmove', preventScroll, { passive: false });
        }
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = 'auto';
        
        // Remove touch event listener
        if ('ontouchstart' in window) {
            document.removeEventListener('touchmove', preventScroll);
        }
        
        // Clear any messages when closing modal
        const messageContainer = modal.querySelector('.message-container');
        if (messageContainer) {
            messageContainer.remove();
        }
        
        // Reset form if exists
        const form = modal.querySelector('.auth-form');
        if (form) {
            form.reset();
            // Reset button state
            const button = form.querySelector('.btn-auth');
            if (button) {
                button.disabled = false;
                const spans = button.querySelectorAll('span');
                const icons = button.querySelectorAll('i');
                if (spans.length && icons.length) {
                    if (modalId.includes('login')) {
                        spans[0].textContent = 'Sign In';
                        icons[0].className = 'fas fa-arrow-right';
                    } else if (modalId.includes('signup')) {
                        spans[0].textContent = 'Sign Up';
                        icons[0].className = 'fas fa-user-plus';
                    }
                }
            }
        }
    }
}

// Prevent scroll on mobile when modal is open
function preventScroll(e) {
    e.preventDefault();
}

function switchAuthModal(targetModalId) {
    // Close all modals first
    document.querySelectorAll('.auth-modal').forEach(modal => {
        modal.classList.remove('active');
    });
    // Open the target modal after a short delay
    setTimeout(() => {
        openModal(targetModalId);
    }, 300);
}

// Enhanced password strength checker
function checkPasswordStrength(password) {
    const strengthBars = [
        document.getElementById('bar-1'),
        document.getElementById('bar-2'),
        document.getElementById('bar-3'),
        document.getElementById('bar-4')
    ];
    
    const strengthText = document.getElementById('strength-value');
    const strengthIcon = document.querySelector('.strength-icon');
    
    if (!strengthBars[0] || !strengthText) return;
    
    // Reset bars
    strengthBars.forEach(bar => {
        bar.style.background = 'rgba(179, 224, 255, 0.2)';
        bar.classList.remove('pulse-animation');
    });
    
    // Check individual requirements
    const hasMinLength = password.length >= 8;
    const hasLowerCase = /[a-z]/.test(password);
    const hasUpperCase = /[A-Z]/.test(password);
    const hasNumbers = /\d/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
    
    // Update requirement indicators
    updateRequirement('req-length', hasMinLength);
    updateRequirement('req-lowercase', hasLowerCase);
    updateRequirement('req-uppercase', hasUpperCase);
    updateRequirement('req-number', hasNumbers);
    updateRequirement('req-special', hasSpecialChar);
    
    // Calculate strength score (0-4)
    let strengthScore = 0;
    if (hasMinLength) strengthScore += 1;
    if (hasLowerCase && hasUpperCase) strengthScore += 1;
    if (hasNumbers) strengthScore += 1;
    if (hasSpecialChar) strengthScore += 1;
    
    // Adjust score based on length
    if (password.length >= 12) strengthScore = Math.min(strengthScore + 1, 4);
    
    // Update UI based on strength
    let strengthLevel = '';
    let color = '';
    
    switch(strengthScore) {
        case 0:
            strengthLevel = 'Very Weak';
            color = 'var(--weak-color)';
            break;
        case 1:
            strengthLevel = 'Weak';
            color = 'var(--weak-color)';
            break;
        case 2:
            strengthLevel = 'Medium';
            color = 'var(--medium-color)';
            break;
        case 3:
            strengthLevel = 'Strong';
            color = 'var(--strong-color)';
            break;
        case 4:
            strengthLevel = 'Very Strong';
            color = 'var(--very-strong-color)';
            break;
    }
    
    // Update bars
    for (let i = 0; i < strengthBars.length; i++) {
        if (i < strengthScore) {
            strengthBars[i].style.background = color;
            strengthBars[i].classList.add('pulse-animation');
            strengthBars[i].style.animationDelay = `${i * 0.1}s`;
        }
    }
    
    // Update text and icon
    strengthText.textContent = strengthLevel;
    strengthText.className = '';
    strengthText.classList.add(`strength-value-${strengthLevel.toLowerCase().replace(' ', '-')}`);
    
    // Update icon
    if (strengthIcon) {
        strengthIcon.className = 'strength-icon fas';
        if (strengthScore <= 1) {
            strengthIcon.classList.add('fa-lock-open');
        } else if (strengthScore <= 3) {
            strengthIcon.classList.add('fa-lock');
        } else {
            strengthIcon.classList.add('fa-lock', 'fa-beat');
        }
    }
}

function updateRequirement(elementId, isMet) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    if (isMet) {
        element.classList.add('met');
        const icon = element.querySelector('i');
        if (icon) {
            icon.className = 'fas fa-check-circle';
        }
    } else {
        element.classList.remove('met');
        const icon = element.querySelector('i');
        if (icon) {
            icon.className = 'fas fa-circle';
        }
    }
}

// ============================================
// DJANGO BACKEND INTEGRATION
// ============================================

// Form Handler Function
function handleAuthForm(config) {
    const form = config.form;
    const button = form.querySelector('.btn-auth');
    
    if (!form || !button) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get form data
        const formData = new FormData(form);
        
        // Basic validation
        const requiredFields = form.querySelectorAll('input[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
            }
        });
        
        if (!isValid) {
            showMessage(form, 'Please fill in all required fields', 'error');
            return;
        }
        
        // Special validation for signup form
        if (config.isSignup) {
            const email = form.querySelector('input[name="email"]').value;
            const password = form.querySelector('input[name="password"]').value;
            const confirmPassword = form.querySelector('input[name="confirm_password"]').value;
            
            // Email validation
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                showMessage(form, 'Please enter a valid email address', 'error');
                return;
            }
            
            // Password validation
            if (password.length < 6) {
                showMessage(form, 'Password must be at least 6 characters', 'error');
                return;
            }
            
            if (password !== confirmPassword) {
                showMessage(form, 'Passwords do not match', 'error');
                return;
            }
        }

        // Show loading state
        setLoadingState(button, true, config.loadingText);
        
        // Make AJAX request
        fetch(config.submitUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showMessage(form, data.message, 'success');
                
                // Close modal and handle redirect after success
                setTimeout(() => {
                    closeModal(config.modalId);
                    
                    // For both login and signup, refresh to update navbar
                    window.location.reload();
                }, 1500);
                
            } else {
                showMessage(form, data.message, 'error');
                setLoadingState(button, false, config.defaultText, config.defaultIcon);
            }
        })
        .catch(error => {
            console.error('Form submission error:', error);
            showMessage(form, 'An error occurred. Please try again.', 'error');
            setLoadingState(button, false, config.defaultText, config.defaultIcon);
        });
    });
}

// Show Message Function
function showMessage(container, message, type) {
    // Remove existing messages
    const existingMessage = container.querySelector('.message-container');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    // Create new message
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message-container';
    messageDiv.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
    
    // Insert message appropriately
    if (container === document.body) {
        // For logout messages, show at top of page
         const navbar = document.querySelector('.navbar');
        const navbarHeight = navbar ? navbar.offsetHeight : 0;
        
        messageDiv.style.position = 'absolute';
        messageDiv.style.top = `${navbarHeight + 20}px`; 
        
        messageDiv.style.right = `${0}px`;
        messageDiv.style.transform = 'translateX(-50%)';
        messageDiv.style.zIndex = '9999';
        messageDiv.style.width = '90%';
        messageDiv.style.maxWidth = '600px';
        messageDiv.style.color = 'yellow';
        document.body.appendChild(messageDiv);
    } else {
        // For form messages, insert after button
        const button = container.querySelector('.btn-auth');
        if (button) {
            button.parentNode.insertBefore(messageDiv, button.nextSibling);
        } else {
            container.appendChild(messageDiv);
        }
    }
    
    // Auto-hide messages after 4 seconds
    setTimeout(() => {
        if (messageDiv && messageDiv.parentNode) {
            messageDiv.remove();
        }
    }, 4000);
}

// Loading State Function
function setLoadingState(button, loading, text, icon = 'fas fa-spinner fa-spin') {
    button.disabled = loading;
    if (loading) {
        button.innerHTML = `<span>${text}</span><i class="fas fa-spinner fa-spin"></i>`;
    } else {
        button.innerHTML = `<span>${text}</span><i class="${icon}"></i>`;
    }
}

// ============================================
// LOGOUT FUNCTIONALITY
// ============================================

function initLogoutHandler() {
    const logoutBtn = document.getElementById("logout-btn");
    if (!logoutBtn) return;

    logoutBtn.addEventListener("click", async function(e) {
        e.preventDefault();

        // Show loading state
        setLoadingState(logoutBtn, true, 'Logging out...');

        try {
            // Get CSRF token from meta tag
            const csrfTokenMeta = document.querySelector('meta[name="csrf-token"]');
            if (!csrfTokenMeta) {
                throw new Error('CSRF token not found. Please refresh the page.');
            }
            const csrfToken = csrfTokenMeta.getAttribute('content');

            const response = await fetch("/auth/logout/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "X-Requested-With": "XMLHttpRequest"
                }
            });

            const data = await response.json();

            if (data.status === "success") {
                // Show success message
                showMessage(document.body, data.message, 'success');
                
                // Update navbar dynamically
                updateNavbarAfterLogout();
                
            } else {
                showMessage(document.body, data.message || 'Logout failed', 'error');
                setLoadingState(logoutBtn, false, 'Logout');
            }
        } catch (error) {
            console.error("Logout failed:", error);
            showMessage(document.body, error.message || "Something went wrong. Please try again.", 'error');
            setLoadingState(logoutBtn, false, 'Logout');
        }
    });
}

// Update navbar after successful logout
function updateNavbarAfterLogout() {
    // Hide logout button
    const logoutBtn = document.getElementById("logout-btn");
    if (logoutBtn) {
        logoutBtn.style.display = "none";
    }

    // Show login/signup buttons
    const authButtons = document.querySelector('.auth-buttons');
    if (authButtons) {
        authButtons.innerHTML = `
            <button class="btn btn-login" onclick="openModal('login-modal'); closeSidebar();">Login</button>
            <button class="btn btn-signin" onclick="openModal('signup-modal'); closeSidebar();">Sign Up</button>
        `;
    }

    // Hide authenticated content
    document.querySelectorAll('.auth-required').forEach(el => {
        el.style.display = 'none';
    });

    // Show guest content
    document.querySelectorAll('.guest-only').forEach(el => {
        el.style.display = 'inline-block';
    });
}

// ============================================
// INITIALIZATION FUNCTIONS
// ============================================

// Initialize auth functionality
function initAuth() {
    // Close modal when clicking on backdrop
    document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
        backdrop.addEventListener('click', function() {
            const modal = this.parentElement;
            const modalId = modal.id;
            closeModal(modalId);
        });
    });

    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.auth-modal.active').forEach(modal => {
                closeModal(modal.id);
            });
        }
    });

    // Initialize form field interactions
    const formInputs = document.querySelectorAll('.form-group input');
    
    formInputs.forEach(input => {
        // Check if input has value on page load
        if (input.value) {
            input.parentElement.classList.add('filled');
        }
        
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
            if (this.value) {
                this.parentElement.classList.add('filled');
            } else {
                this.parentElement.classList.remove('filled');
            }
        });
        
        // For password field, add strength checking
        if (input.type === 'password' && input.id === 'signup-password') {
            input.addEventListener('input', function() {
                checkPasswordStrength(this.value);
            });
        }
    });
    
    // Close buttons functionality
    document.querySelectorAll('.modal-close').forEach(closeBtn => {
        closeBtn.addEventListener('click', function() {
            const modal = this.closest('.auth-modal');
            if (modal) {
                closeModal(modal.id);
            }
        });
    });
    
    // Improve mobile experience
    if ('ontouchstart' in window) {
        // Add touch-friendly styles
        document.querySelectorAll('.btn-auth, .modal-close').forEach(element => {
            element.style.minHeight = '44px';
        });
        
        document.querySelectorAll('input').forEach(input => {
            input.style.minHeight = '44px';
        });
    }
}

// Initialize form handlers
function initFormHandlers() {
    // Handle Login Form
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        handleAuthForm({
            form: loginForm,
            submitUrl: '/auth/login/',
            loadingText: 'Signing In...',
            defaultText: 'Sign In',
            defaultIcon: 'fas fa-arrow-right',
            modalId: 'login-modal'
        });
    }
    
    // Handle Signup Form  
    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        handleAuthForm({
            form: signupForm,
            submitUrl: '/auth/register/',
            loadingText: 'Creating Account...',
            defaultText: 'Sign Up',
            defaultIcon: 'fas fa-user-plus',
            isSignup: true,
            modalId: 'signup-modal'
        });
    }
}

// ============================================
// GLOBAL EXPORTS AND INITIALIZATION
// ============================================

// Make functions globally available
window.openModal = openModal;
window.closeModal = closeModal;
window.switchAuthModal = switchAuthModal;
window.checkPasswordStrength = checkPasswordStrength;

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize basic auth functionality
    initAuth();
    
    // Initialize form handlers with Django backend
    initFormHandlers();
    
    // Initialize logout handler
    initLogoutHandler();
});

// ============================================
// EVENT DELEGATION FOR DYNAMIC CONTENT
// ============================================

// Handle dynamically added modals or forms
document.addEventListener('click', function(e) {
    // Handle login/signup buttons
    if (e.target.matches('[data-modal]')) {
        e.preventDefault();
        const modalId = e.target.getAttribute('data-modal');
        openModal(modalId);
    }
    
    // Handle close buttons
    if (e.target.matches('.modal-close, .modal-close *')) {
        e.preventDefault();
        const modal = e.target.closest('.auth-modal');
        if (modal) {
            closeModal(modal.id);
        }
    }
});

// ============================================
// END OF AUTH.JS - COMPLETE & PERFECT VERSION
// ============================================
