/**
 * GME Portal - Main JavaScript
 * Contains common functionality used across the application
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeDropdowns();
    initializeAlerts();
    initializeFormValidation();
    initializeFileInputs();
    initializeDynamicSelects();
});

/**
 * Initialize dropdown menus
 */
function initializeDropdowns() {
    const dropdownToggles = document.querySelectorAll('[data-toggle="dropdown"]');
    
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const target = document.querySelector(this.getAttribute('data-target'));
            if (target) {
                target.classList.toggle('hidden');
                
                // Close other dropdowns
                document.querySelectorAll('.dropdown-menu').forEach(menu => {
                    if (menu !== target && !menu.classList.contains('hidden')) {
                        menu.classList.add('hidden');
                    }
                });
            }
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function() {
        document.querySelectorAll('.dropdown-menu').forEach(menu => {
            if (!menu.classList.contains('hidden')) {
                menu.classList.add('hidden');
            }
        });
    });
}

/**
 * Initialize dismissible alerts
 */
function initializeAlerts() {
    const alertCloseButtons = document.querySelectorAll('.alert .close');
    
    alertCloseButtons.forEach(button => {
        button.addEventListener('click', function() {
            const alert = this.closest('.alert');
            if (alert) {
                alert.classList.add('opacity-0');
                setTimeout(() => {
                    alert.remove();
                }, 300);
            }
        });
    });
    
    // Auto-dismiss alerts after 5 seconds
    document.querySelectorAll('.alert.auto-dismiss').forEach(alert => {
        setTimeout(() => {
            alert.classList.add('opacity-0');
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });
}

/**
 * Initialize form validation
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('form.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
            
            // Highlight invalid fields
            form.querySelectorAll(':invalid').forEach(field => {
                field.closest('.form-group').classList.add('has-error');
            });
            
            // Remove highlight when field becomes valid
            form.querySelectorAll('input, select, textarea').forEach(field => {
                field.addEventListener('input', function() {
                    if (this.checkValidity()) {
                        this.closest('.form-group').classList.remove('has-error');
                    } else {
                        this.closest('.form-group').classList.add('has-error');
                    }
                });
            });
        }, false);
    });
}

/**
 * Initialize custom file inputs
 */
function initializeFileInputs() {
    const fileInputs = document.querySelectorAll('.form-file-input');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const fileName = this.files[0]?.name || 'No file chosen';
            const fileNameDisplay = this.nextElementSibling;
            
            if (fileNameDisplay && fileNameDisplay.classList.contains('file-name')) {
                fileNameDisplay.textContent = fileName;
            }
        });
    });
}

/**
 * Initialize dynamic select fields (e.g., program type affecting program options)
 */
function initializeDynamicSelects() {
    const programTypeSelect = document.getElementById('id_program_type');
    const programSelect = document.getElementById('id_program');
    
    if (programTypeSelect && programSelect) {
        programTypeSelect.addEventListener('change', function() {
            const programType = this.value;
            
            if (programType) {
                // Clear current options
                programSelect.innerHTML = '<option value="">Loading programs...</option>';
                
                // Fetch programs for selected type
                fetch(`/applications/get-programs-by-type/?program_type=${programType}`)
                    .then(response => response.json())
                    .then(data => {
                        programSelect.innerHTML = '<option value="">Select Program</option>';
                        
                        data.programs.forEach(program => {
                            const option = document.createElement('option');
                            option.value = program.id;
                            option.textContent = program.name;
                            programSelect.appendChild(option);
                        });
                        
                        programSelect.disabled = false;
                    })
                    .catch(error => {
                        console.error('Error fetching programs:', error);
                        programSelect.innerHTML = '<option value="">Error loading programs</option>';
                    });
            } else {
                programSelect.innerHTML = '<option value="">Select Program Type first</option>';
                programSelect.disabled = true;
            }
        });
    }
}

/**
 * Format date to a readable string
 * @param {Date|string} date - Date object or date string
 * @param {string} format - Format string (default: 'MMM D, YYYY')
 * @returns {string} Formatted date string
 */
function formatDate(date, format = 'MMM D, YYYY') {
    const d = new Date(date);
    
    if (isNaN(d.getTime())) {
        return 'Invalid date';
    }
    
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const fullMonths = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    
    format = format.replace('YYYY', d.getFullYear());
    format = format.replace('YY', d.getFullYear().toString().slice(-2));
    format = format.replace('MMMM', fullMonths[d.getMonth()]);
    format = format.replace('MMM', months[d.getMonth()]);
    format = format.replace('MM', (d.getMonth() + 1).toString().padStart(2, '0'));
    format = format.replace('M', d.getMonth() + 1);
    format = format.replace('DD', d.getDate().toString().padStart(2, '0'));
    format = format.replace('D', d.getDate());
    
    return format;
}

/**
 * Show a confirmation dialog
 * @param {string} message - Confirmation message
 * @param {Function} onConfirm - Function to call when confirmed
 * @param {Function} onCancel - Function to call when canceled
 */
function confirmAction(message, onConfirm, onCancel = null) {
    if (confirm(message)) {
        if (typeof onConfirm === 'function') {
            onConfirm();
        }
    } else if (typeof onCancel === 'function') {
        onCancel();
    }
}

/**
 * Show a toast notification
 * @param {string} message - Notification message
 * @param {string} type - Notification type (success, error, warning, info)
 * @param {number} duration - Duration in milliseconds
 */
function showNotification(message, type = 'info', duration = 3000) {
    const container = document.getElementById('notification-container') || createNotificationContainer();
    
    const toast = document.createElement('div');
    toast.className = `notification notification-${type} opacity-0 transition-opacity duration-300`;
    toast.innerHTML = `
        <div class="notification-content">
            <span>${message}</span>
            <button type="button" class="notification-close">&times;</button>
        </div>
    `;
    
    container.appendChild(toast);
    
    // Fade in
    setTimeout(() => {
        toast.classList.remove('opacity-0');
    }, 10);
    
    // Add close button functionality
    toast.querySelector('.notification-close').addEventListener('click', () => {
        toast.classList.add('opacity-0');
        setTimeout(() => {
            toast.remove();
        }, 300);
    });
    
    // Auto-dismiss
    setTimeout(() => {
        toast.classList.add('opacity-0');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, duration);
}

/**
 * Create notification container if it doesn't exist
 * @returns {HTMLElement} Notification container
 */
function createNotificationContainer() {
    const container = document.createElement('div');
    container.id = 'notification-container';
    container.className = 'fixed top-4 right-4 z-50 flex flex-col space-y-2';
    document.body.appendChild(container);
    return container;
}

/**
 * Debounce function to limit how often a function can be called
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, wait = 300) {
    let timeout;
    
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Handle AJAX form submission
 * @param {HTMLFormElement} form - Form element
 * @param {Function} onSuccess - Function to call on success
 * @param {Function} onError - Function to call on error
 */
function submitFormAjax(form, onSuccess, onError) {
    const formData = new FormData(form);
    const url = form.getAttribute('action') || window.location.href;
    const method = form.getAttribute('method') || 'POST';
    
    fetch(url, {
        method: method.toUpperCase(),
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (typeof onSuccess === 'function') {
            onSuccess(data);
        }
    })
    .catch(error => {
        console.error('Error submitting form:', error);
        if (typeof onError === 'function') {
            onError(error);
        }
    });
} 