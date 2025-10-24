// ============================================
// OFFICER DASHBOARD - COMPLETE STANDALONE JS
// All functionality including backdrop fix
// ============================================

(function() {
    'use strict';

    // ============================================
    // MODAL CONTROL FUNCTIONS (FIXED)
    // ============================================

    function openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'flex';
            modal.setAttribute('aria-hidden', 'false');
            document.body.style.overflow = 'hidden';
            
            // Re-enable backdrop clicks for THIS modal
            const backdrop = modal.querySelector('.modal-backdrop');
            if (backdrop) {
                backdrop.style.pointerEvents = 'auto';
            }
            
            // Prevent mobile scroll
            if ('ontouchstart' in window) {
                document.addEventListener('touchmove', preventScroll, { passive: false });
            }
        }
    }

    function closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            // Hide modal
            modal.style.display = 'none';
            modal.setAttribute('aria-hidden', 'true');
            
            // Restore body scroll
            document.body.style.overflow = 'auto';
            document.body.classList.remove('modal-open');
            
            // Remove touch event listener
            if ('ontouchstart' in window) {
                document.removeEventListener('touchmove', preventScroll);
            }
            
            // ✅ CRITICAL FIX: Disable ALL modal backdrops from blocking clicks
            document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
                backdrop.style.pointerEvents = 'none';
            });
            
            // Clear messages
            const messageContainer = modal.querySelector('.message-container');
            if (messageContainer) {
                messageContainer.remove();
            }
            
            // Reset form
            const form = modal.querySelector('.auth-form');
            if (form) {
                form.reset();
                const button = form.querySelector('.btn-auth');
                if (button) {
                    resetButton(button, modalId);
                }
            }
        }
    }

    function switchAuthModal(targetModalId) {
        // Get current open modal using more reliable method
        const currentModal = document.querySelector('.auth-modal[style*="display: flex"], .auth-modal[aria-hidden="false"]');
        
        if (currentModal && currentModal.id !== targetModalId) {
            // Close current modal and open target modal
            closeModal(currentModal.id);
            
            // Small delay to ensure smooth transition
            setTimeout(() => {
                openModal(targetModalId);
            }, 350);
        } else if (!currentModal) {
            // No modal open, just open target
            openModal(targetModalId);
        }
    }

    function preventScroll(e) {
        e.preventDefault();
    }

    function resetButton(button, modalId) {
        button.disabled = false;
        if (modalId.includes('login')) {
            button.innerHTML = '<span>Sign In</span><i class="fas fa-arrow-right"></i>';
        } else {
            button.innerHTML = '<span>Register Officer</span><i class="fas fa-user-check"></i>';
        }
    }

    // ============================================
    // MESSAGE DISPLAY FUNCTIONS
    // ============================================

    function showMessage(container, message, type) {
        // Remove existing messages
        const existingMessage = container.querySelector('.message-container');
        if (existingMessage) {
            existingMessage.remove();
        }
        
        // Create new message
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message-container';
        messageDiv.innerHTML = `
            <div style="padding: 15px; margin: 15px 0; border-radius: 8px; 
                        background: ${type === 'success' ? '#d4edda' : '#f8d7da'}; 
                        color: ${type === 'success' ? '#155724' : '#721c24'}; 
                        border: 1px solid ${type === 'success' ? '#c3e6cb' : '#f5c6cb'};">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
                ${message}
            </div>
        `;
        
        // Insert message
        const button = container.querySelector('.btn-auth');
        if (button) {
            button.parentNode.insertBefore(messageDiv, button.nextSibling);
        } else {
            container.appendChild(messageDiv);
        }
        
        // Auto-hide after 4 seconds
        setTimeout(() => {
            if (messageDiv && messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 4000);
    }

    function setLoadingState(button, loading, text, icon = 'fas fa-spinner fa-spin') {
        button.disabled = loading;
        button.innerHTML = `<span>${text}</span><i class="${icon}"></i>`;
    }

    // ============================================
    // FORM VALIDATION FUNCTIONS
    // ============================================

    function validateOfficerSignup(formData) {
        const email = formData.get('officer_email');
        const phone = formData.get('officer_phone');
        const govtId = formData.get('govt_id');
        const password = formData.get('password');
        const confirmPassword = formData.get('confirm_password');
        
        // Email validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            return { valid: false, message: 'Please enter a valid email address' };
        }
        
        // Phone validation
        const phoneRegex = /^\d{10}$/;
        if (!phoneRegex.test(phone)) {
            return { valid: false, message: 'Phone number must be exactly 10 digits' };
        }
        
        // Govt ID validation
        if (govtId.length !== 10) {
            return { valid: false, message: 'Government ID must be exactly 10 characters' };
        }
        
        // Password validation
        if (password.length < 6) {
            return { valid: false, message: 'Password must be at least 6 characters' };
        }
        
        if (password !== confirmPassword) {
            return { valid: false, message: 'Passwords do not match' };
        }
        
        return { valid: true };
    }

    function validateRequiredFields(form) {
        const requiredFields = form.querySelectorAll('input[required]');
        for (let field of requiredFields) {
            if (!field.value.trim()) {
                return false;
            }
        }
        return true;
    }

    // ============================================
    // FORM SUBMISSION HANDLERS
    // ============================================

    function handleOfficerAuth(form, config) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const button = form.querySelector('.btn-auth');
            const formData = new FormData(form);
            
            // Validate required fields
            if (!validateRequiredFields(form)) {
                showMessage(form, 'Please fill in all required fields', 'error');
                return;
            }
            
            // Special validation for signup
            if (config.isSignup) {
                const validation = validateOfficerSignup(formData);
                if (!validation.valid) {
                    showMessage(form, validation.message, 'error');
                    return;
                }
            }
            
            // Show loading state
            setLoadingState(button, true, config.loadingText);
            
            try {
                const response = await fetch(config.submitUrl, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showMessage(form, data.message, 'success');
                    
                    setTimeout(() => {
                        closeModal(config.modalId);
                        if (data.redirect_url) {
                            window.location.href = data.redirect_url;
                        }
                    }, 1500);
                } else {
                    showMessage(form, data.message, 'error');
                    setLoadingState(button, false, config.defaultText, config.defaultIcon);
                }
            } catch (error) {
                console.error('Form submission error:', error);
                showMessage(form, 'An error occurred. Please try again.', 'error');
                setLoadingState(button, false, config.defaultText, config.defaultIcon);
            }
        });
    }

    // ============================================
    // APPLICATION ACTION HANDLERS
    // ============================================

    function viewApplication(appId) {
    // Get the hidden details div
    const detailsDiv = document.getElementById('applicationDetails_' + appId);
    
    if (!detailsDiv) {
        alert('Application details not found!');
        return;
    }
    
    // Get the content from hidden div
    const detailsContent = detailsDiv.innerHTML;
    
    // Create modal
    const modal = document.createElement('div');
    modal.innerHTML = `
         <div style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; 
                        background: rgba(0,0,0,0.9); z-index: 99999; display: flex; 
                        align-items: center; justify-content: center; padding: 20px;
                        backdrop-filter: blur(4px);">
                <div style="background: linear-gradient(135deg, #0a1929 0%, #0d2337 50%, #143d66 100%); 
                            padding: 30px; border-radius: 15px; border: 1px solid #2196f3;
                            max-width: 900px; width: 100%; max-height: 90vh; overflow-y: auto;
                            box-shadow: 0 20px 60px rgba(0,0,0,0.5); color: #e6f7ff;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;
                                border-bottom: 1px solid rgba(33, 150, 243, 0.3); padding-bottom: 15px;">
                        <h3 style="margin: 0; color: #00e5ff; font-size: 24px; font-family: 'Orbitron', sans-serif;">
                            <i class="fas fa-file-alt"></i> Application: ${appId}
                        </h3>
                        <button onclick="this.closest('div[style*=\\'position: fixed\\']').remove()" 
                                style="border: none; background: rgba(0, 229, 255, 0.2); font-size: 28px; 
                                       cursor: pointer; color: #00e5ff; transition: all 0.3s; width: 40px; height: 40px;
                                       border-radius: 50%; display: flex; align-items: center; justify-content: center;"
                                onmouseover="this.style.background='rgba(0, 229, 255, 0.4)'; this.style.color='#ffffff'" 
                                onmouseout="this.style.background='rgba(0, 229, 255, 0.2)'; this.style.color='#00e5ff'">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div style="padding: 20px; background: rgba(255,255,255,0.05); border-radius: 10px; border: 1px solid rgba(33, 150, 243, 0.2);">
                        ${detailsContent}
                    </div>
                </div>
            </div>
    `;
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');
    
    // Close modal when clicking backdrop
    modal.querySelector('div[style*="background: rgba"]').addEventListener('click', function(e) {
        if (e.target === this) {
            modal.remove();
        }
    });
    
    // Close modal with Escape key
    document.addEventListener('keydown', function closeOnEscape(e) {
        if (e.key === 'Escape') {
            modal.remove();
            document.removeEventListener('keydown', closeOnEscape);
        }
    });
    
    document.body.appendChild(modal);
}

async function approveApplication(appId) {
    if (!confirm('Are you sure you want to approve this application?')) {
        return;
    }
    
    try {
        // Get CSRF token from cookie or meta tag
        const csrfToken = getCookie('csrftoken') || document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        
        if (!csrfToken) {
            alert('❌ Security token missing. Please refresh the page.');
            return;
        }
        
        const response = await fetch('/officer/approve/', {  // ✅ Changed from /api/approve/
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: 'application_id=' + encodeURIComponent(appId)
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✅ Application approved successfully!');
            location.reload();
        } else {
            alert('❌ ' + (data.message || 'Failed to approve application'));
        }
    } catch (error) {
        console.error('Approval error:', error);
        alert('❌ An error occurred. Please try again.');
    }
}

async function rejectApplication(appId) {
    const reason = prompt('Enter rejection reason:');
    if (!reason || !reason.trim()) {
        return;
    }
    
    try {
        // Get CSRF token from cookie or meta tag
        const csrfToken = getCookie('csrftoken') || document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        
        if (!csrfToken) {
            alert('❌ Security token missing. Please refresh the page.');
            return;
        }
        
        const response = await fetch('/officer/reject/', {  // ✅ Changed from /api/reject/
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: 'application_id=' + encodeURIComponent(appId) + '&reason=' + encodeURIComponent(reason)
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✅ Application rejected.');
            location.reload();
        } else {
            alert('❌ ' + (data.message || 'Failed to reject application'));
        }
    } catch (error) {
        console.error('Rejection error:', error);
        alert('❌ An error occurred. Please try again.');
    }
}

async function underReviewApplication(appId) {
    if (!confirm('Are you sure you want to mark this application as under review?')) {
        return;
    }

    try {
        // Get CSRF token from cookie or meta tag
        const csrfToken = getCookie('csrftoken') || document.querySelector('[name=csrfmiddlewaretoken]')?.value;

        if (!csrfToken) {
            alert('❌ Security token missing. Please refresh the page.');
            return;
        }

        const response = await fetch('/officer/under-review/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: 'application_id=' + encodeURIComponent(appId)
        });

        const data = await response.json();

        if (data.success) {
            alert('✅ Application marked as under review.');
            location.reload();
        } else {
            alert('❌ ' + (data.message || 'Failed to mark application as under review'));
        }
    } catch (error) {
        console.error('Under review error:', error);
        alert('❌ An error occurred. Please try again.');
    }
}

// Helper function to get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


    // ============================================
    // FILTER FUNCTIONALITY
    // ============================================

    function initFilters() {
        const filterButtons = document.querySelectorAll('.filter-btn');
        const applicationCards = document.querySelectorAll('.application-card');
        
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Update active state
                filterButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                const filter = this.textContent.trim().toLowerCase();
                
                // Filter applications (for now just show all)
                applicationCards.forEach(card => {
                    card.style.display = 'block';
                });
            });
        });
    }
    // ============================================
// APPLICATION FILTERING FUNCTIONALITY
// ============================================

function filterApplications(filterType) {
    currentFilter = filterType;
    
    // Update active state of stat cards
    document.querySelectorAll('.stat-card').forEach(card => {
        card.classList.remove('active');
    });
    
    // Activate the clicked stat card
    event.currentTarget.classList.add('active');
    
    // Update table title based on filter
    const tableTitle = document.querySelector('.table-header h3');
    const applicationsContainer = document.getElementById('applications-container');
    const emptyState = document.querySelector('.empty-state');
    
    switch(filterType) {
        case 'pending':
            tableTitle.innerHTML = '<i class="fas fa-list"></i> Submitted Applications';
            // Show all pending applications
            if (applicationsContainer) {
                applicationsContainer.style.display = 'block';
                document.querySelectorAll('.application-card').forEach(card => {
                    card.style.display = 'block';
                });
            }
            if (emptyState) emptyState.style.display = 'none';
            break;
            
        case 'approved':
            tableTitle.innerHTML = '<i class="fas fa-check-circle"></i> Approved Applications (This Month)';
            // Fetch and show approved applications
            fetchApprovedApplications();
            break;
            
        case 'rejected':
            tableTitle.innerHTML = '<i class="fas fa-times-circle"></i> Rejected Applications (This Month)';
            // Fetch and show rejected applications
            fetchRejectedApplications();
            break;
    }
}

async function fetchApprovedApplications() {
    try {
        const csrfToken = getCookie('csrftoken') || document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        const response = await fetch('/officer/get-approved-applications/', {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest',
            }
        });
        
        const data = await response.json();
        displayFilteredApplications(data.applications, 'approved');
    } catch (error) {
        console.error('Error fetching approved applications:', error);
        showEmptyState('approved');
    }
}

async function fetchRejectedApplications() {
    try {
        const csrfToken = getCookie('csrftoken') || document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        const response = await fetch('/officer/get-rejected-applications/', {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest',
            }
        });
        
        const data = await response.json();
        displayFilteredApplications(data.applications, 'rejected');
    } catch (error) {
        console.error('Error fetching rejected applications:', error);
        showEmptyState('rejected');
    }
}

function displayFilteredApplications(applications, filterType) {
    const applicationsContainer = document.getElementById('applications-container');
    const emptyState = document.querySelector('.empty-state');
    
    if (!applications || applications.length === 0) {
        showEmptyState(filterType);
        return;
    }
    
    // Hide the original applications container
    if (applicationsContainer) {
        applicationsContainer.style.display = 'none';
    }
    
    // Create or update filtered applications container
    let filteredContainer = document.getElementById('filtered-applications-container');
    if (!filteredContainer) {
        filteredContainer = document.createElement('div');
        filteredContainer.id = 'filtered-applications-container';
        document.querySelector('.applications-table').appendChild(filteredContainer);
    }
    
    // Clear existing content
    filteredContainer.innerHTML = '';
    
    // Add filtered applications
    applications.forEach(app => {
        const appCard = createApplicationCard(app, filterType);
        filteredContainer.appendChild(appCard);
    });
    
    if (emptyState) emptyState.style.display = 'none';
}

function showEmptyState(filterType) {
    const applicationsContainer = document.getElementById('applications-container');
    const filteredContainer = document.getElementById('filtered-applications-container');
    const emptyState = document.querySelector('.empty-state');
    
    if (applicationsContainer) applicationsContainer.style.display = 'none';
    if (filteredContainer) filteredContainer.style.display = 'none';
    
    if (emptyState) {
        emptyState.style.display = 'block';
        const icon = filterType === 'approved' ? 'fa-check-circle' : 'fa-times-circle';
        const title = filterType === 'approved' ? 'No Approved Applications This Month' : 'No Rejected Applications This Month';
        const message = filterType === 'approved' 
            ? 'There are no approved applications for your district this month.' 
            : 'There are no rejected applications for your district this month.';
        
        emptyState.innerHTML = `
            <i class="fas ${icon}"></i>
            <h4>${title}</h4>
            <p>${message}</p>
        `;
    }
}

// Initialize with pending applications active
document.addEventListener('DOMContentLoaded', function() {
    // Set pending stat card as active by default
    const pendingStatCard = document.querySelector('.stat-card');
    if (pendingStatCard) {
        pendingStatCard.classList.add('active');
    }
});

// Make function global
window.filterApplications = filterApplications;

    // ============================================
    // INITIALIZATION
    // ============================================

    function init() {
        // Initialize modal close buttons
        document.querySelectorAll('.modal-backdrop, .modal-close').forEach(element => {
            element.addEventListener('click', function(e) {
                if (e.target === this || e.target.closest('.modal-close')) {
                    const modal = this.closest('.auth-modal');
                    if (modal) {
                        closeModal(modal.id);
                    }
                }
            });
        });
        
        // Close modals with Escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                document.querySelectorAll('.auth-modal[style*="display: flex"]').forEach(modal => {
                    closeModal(modal.id);
                });
            }
        });
        
        // Initialize officer registration form
        const officerSignupForm = document.getElementById('officer-signup-form');
        if (officerSignupForm) {
            handleOfficerAuth(officerSignupForm, {
                submitUrl: officerSignupForm.getAttribute('action'),
                loadingText: 'Creating Account...',
                defaultText: 'Register Officer',
                defaultIcon: 'fas fa-user-check',
                isSignup: true,
                modalId: 'officer-signup-modal'
            });
        }
        
        // Initialize officer login form
        const officerLoginForm = document.getElementById('officer-login-form');
        if (officerLoginForm) {
            handleOfficerAuth(officerLoginForm, {
                submitUrl: officerLoginForm.getAttribute('action'),
                loadingText: 'Signing In...',
                defaultText: 'Sign In',
                defaultIcon: 'fas fa-arrow-right',
                isSignup: false,
                modalId: 'officer-login-modal'
            });
        }
        
        // Initialize form field interactions
        const formInputs = document.querySelectorAll('.form-group input');
        formInputs.forEach(input => {
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
        });
        
        // Initialize filters
        initFilters();
    }

    // ============================================
    // EXPOSE GLOBAL FUNCTIONS
    // ============================================

    window.openModal = openModal;
    window.closeModal = closeModal;
    window.switchAuthModal = switchAuthModal;
    window.viewApplication = viewApplication;
    window.approveApplication = approveApplication;
    window.rejectApplication = rejectApplication;
    window.underReviewApplication = underReviewApplication; 
    // ============================================
    // START APPLICATION
    // ============================================

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
