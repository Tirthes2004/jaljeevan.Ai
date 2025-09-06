// Auth Modal Functionality
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

// Initialize auth functionality
function initAuth() {
    // Close modal when clicking on backdrop
    document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
        backdrop.addEventListener('click', function() {
            const modal = this.parentElement;
            modal.classList.remove('active');
            document.body.style.overflow = 'auto';
            
            // Remove touch event listener
            if ('ontouchstart' in window) {
                document.removeEventListener('touchmove', preventScroll);
            }
        });
    });

    // Prevent form submission for demo
    document.querySelectorAll('.auth-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const submitBtn = this.querySelector('.btn-auth');
            const originalText = submitBtn.querySelector('span').textContent;
            const originalIcon = submitBtn.querySelector('i').className;
            
            // Show loading state
            submitBtn.querySelector('span').textContent = 'Processing...';
            submitBtn.querySelector('i').className = 'fas fa-spinner fa-spin';
            submitBtn.disabled = true;
            
            // Simulate API call
            setTimeout(() => {
                // Reset button state
                submitBtn.querySelector('span').textContent = originalText;
                submitBtn.querySelector('i').className = originalIcon;
                submitBtn.disabled = false;
                
                // Close modal
                const modal = this.closest('.auth-modal');
                modal.classList.remove('active');
                document.body.style.overflow = 'auto';
                
                // Remove touch event listener
                if ('ontouchstart' in window) {
                    document.removeEventListener('touchmove', preventScroll);
                }
                
                // Show success message
                alert('Authentication successful!');
            }, 1500);
        });
    });

    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.auth-modal').forEach(modal => {
                if (modal.classList.contains('active')) {
                    modal.classList.remove('active');
                    document.body.style.overflow = 'auto';
                    
                    // Remove touch event listener
                    if ('ontouchstart' in window) {
                        document.removeEventListener('touchmove', preventScroll);
                    }
                }
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

// Make functions globally available
window.openModal = openModal;
window.closeModal = closeModal;
window.switchAuthModal = switchAuthModal;
window.checkPasswordStrength = checkPasswordStrength;

// Initialize auth when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initAuth();
});