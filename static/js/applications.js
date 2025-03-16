/**
 * GME Portal - Applications JavaScript
 * Contains functionality specific to application pages
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeApplicationForm();
    initializeDocumentUpload();
    initializeApplicationFilters();
    initializeApplicationStatusUpdates();
});

/**
 * Initialize application form functionality
 */
function initializeApplicationForm() {
    const applicationForm = document.getElementById('application-form');
    
    if (applicationForm) {
        // Handle program type change
        const programTypeSelect = document.getElementById('id_program_type');
        const programSelect = document.getElementById('id_program');
        
        if (programTypeSelect && programSelect) {
            programTypeSelect.addEventListener('change', function() {
                const programType = this.value;
                
                if (programType) {
                    // Clear current options
                    programSelect.innerHTML = '<option value="">Loading programs...</option>';
                    programSelect.disabled = true;
                    
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
        
        // Handle GPA type toggle
        const gpaInput = document.getElementById('id_gpa');
        const gpaTypeCheckbox = document.getElementById('id_is_gpa_percentage');
        const gpaHint = document.getElementById('gpa-hint');
        
        if (gpaInput && gpaTypeCheckbox && gpaHint) {
            function updateGpaHint() {
                if (gpaTypeCheckbox.checked) {
                    gpaHint.textContent = 'Enter GPA as a percentage (e.g., 85.5)';
                    gpaInput.setAttribute('max', '100');
                } else {
                    gpaHint.textContent = 'Enter GPA on a scale of 4.0 (e.g., 3.5)';
                    gpaInput.setAttribute('max', '4.0');
                }
            }
            
            updateGpaHint();
            gpaTypeCheckbox.addEventListener('change', updateGpaHint);
        }
    }
}

/**
 * Initialize document upload functionality
 */
function initializeDocumentUpload() {
    const documentUploadForm = document.getElementById('document-upload-form');
    
    if (documentUploadForm) {
        const fileInputs = documentUploadForm.querySelectorAll('input[type="file"]');
        
        fileInputs.forEach(input => {
            const fileNameDisplay = document.createElement('div');
            fileNameDisplay.className = 'file-name mt-2 text-sm text-gray-600';
            fileNameDisplay.textContent = 'No file chosen';
            input.parentNode.appendChild(fileNameDisplay);
            
            input.addEventListener('change', function() {
                const fileName = this.files[0]?.name || 'No file chosen';
                fileNameDisplay.textContent = fileName;
                
                // Show upload button if file is selected
                const uploadButton = this.closest('.document-upload-item')?.querySelector('.upload-button');
                if (uploadButton) {
                    uploadButton.classList.remove('hidden');
                }
            });
        });
        
        // Handle document deletion
        const deleteButtons = document.querySelectorAll('.delete-document');
        deleteButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                
                const documentId = this.dataset.documentId;
                const documentName = this.dataset.documentName;
                
                if (confirm(`Are you sure you want to delete the document "${documentName}"?`)) {
                    // Create a form and submit it
                    const form = document.createElement('form');
                    form.method = 'POST';
                    form.action = `/applications/delete-document/${documentId}/`;
                    
                    const csrfInput = document.createElement('input');
                    csrfInput.type = 'hidden';
                    csrfInput.name = 'csrfmiddlewaretoken';
                    csrfInput.value = document.querySelector('[name=csrfmiddlewaretoken]').value;
                    
                    form.appendChild(csrfInput);
                    document.body.appendChild(form);
                    form.submit();
                }
            });
        });
    }
}

/**
 * Initialize application filters
 */
function initializeApplicationFilters() {
    const filterForm = document.getElementById('application-filter-form');
    
    if (filterForm) {
        const programFilter = document.getElementById('program-filter');
        const statusFilter = document.getElementById('status-filter');
        const searchInput = document.getElementById('search-input');
        
        // Apply filters on change
        [programFilter, statusFilter].forEach(filter => {
            if (filter) {
                filter.addEventListener('change', () => {
                    filterForm.submit();
                });
            }
        });
        
        // Debounce search input
        if (searchInput) {
            searchInput.addEventListener('input', debounce(() => {
                filterForm.submit();
            }, 500));
        }
        
        // Clear filters button
        const clearFiltersButton = document.getElementById('clear-filters');
        if (clearFiltersButton) {
            clearFiltersButton.addEventListener('click', () => {
                if (programFilter) programFilter.value = '';
                if (statusFilter) statusFilter.value = '';
                if (searchInput) searchInput.value = '';
                filterForm.submit();
            });
        }
    }
}

/**
 * Initialize application status update functionality
 */
function initializeApplicationStatusUpdates() {
    const statusUpdateButtons = document.querySelectorAll('.status-update-btn');
    
    statusUpdateButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const applicationId = this.dataset.applicationId;
            const newStatus = this.dataset.status;
            const statusText = this.dataset.statusText;
            
            if (confirm(`Are you sure you want to mark this application as "${statusText}"?`)) {
                // Create a form and submit it
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = `/applications/${applicationId}/update-status/`;
                
                const csrfInput = document.createElement('input');
                csrfInput.type = 'hidden';
                csrfInput.name = 'csrfmiddlewaretoken';
                csrfInput.value = document.querySelector('[name=csrfmiddlewaretoken]').value;
                
                const statusInput = document.createElement('input');
                statusInput.type = 'hidden';
                statusInput.name = 'status';
                statusInput.value = newStatus;
                
                form.appendChild(csrfInput);
                form.appendChild(statusInput);
                document.body.appendChild(form);
                form.submit();
            }
        });
    });
}

/**
 * Debounce function to limit how often a function can be called
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, wait) {
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