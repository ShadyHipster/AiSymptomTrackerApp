// AI Symptom Tracker JavaScript functionality

// Utility functions
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const container = document.querySelector('main.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-remove alert after 5 seconds
    setTimeout(() => {
        if (alertDiv && alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatDateTime(dateTimeString) {
    if (!dateTimeString) return 'N/A';
    const date = new Date(dateTimeString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Loading state management
function setLoadingState(buttonId, loading = true) {
    const button = document.getElementById(buttonId);
    if (!button) return;
    
    if (loading) {
        button.dataset.originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
        button.disabled = true;
    } else {
        button.innerHTML = button.dataset.originalText || button.innerHTML;
        button.disabled = false;
    }
}

// API request helper
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    const mergedOptions = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(url, mergedOptions);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `HTTP error! status: ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// Symptom suggestions
const commonSymptoms = [
    'fever', 'headache', 'cough', 'fatigue', 'nausea', 'chest pain',
    'shortness of breath', 'dizziness', 'abdominal pain', 'sore throat',
    'muscle aches', 'joint pain', 'back pain', 'runny nose', 'diarrhea'
];

function initSymptomSuggestions() {
    const symptomInput = document.getElementById('symptoms');
    if (!symptomInput) return;
    
    // Create suggestions container
    const suggestionsDiv = document.createElement('div');
    suggestionsDiv.className = 'symptom-suggestions mt-2';
    suggestionsDiv.innerHTML = `
        <small class="text-muted">Common symptoms:</small><br>
        ${commonSymptoms.map(symptom => 
            `<span class="badge bg-light text-dark me-1 mb-1" style="cursor: pointer;" onclick="addSymptom('${symptom}')">${symptom}</span>`
        ).join('')}
    `;
    
    symptomInput.parentNode.appendChild(suggestionsDiv);
}

function addSymptom(symptom) {
    const symptomInput = document.getElementById('symptoms');
    if (!symptomInput) return;
    
    const currentValue = symptomInput.value.trim();
    if (currentValue && !currentValue.endsWith('.') && !currentValue.endsWith(',')) {
        symptomInput.value = currentValue + ', ' + symptom;
    } else {
        symptomInput.value = currentValue + (currentValue ? ' ' : '') + symptom;
    }
    
    symptomInput.focus();
}

// Initialize tooltips
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Copy to clipboard functionality
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showAlert('Copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy text: ', err);
        showAlert('Failed to copy text', 'error');
    });
}

// Print functionality
function printDiagnosis() {
    const diagnosisContent = document.getElementById('diagnosisContent');
    if (!diagnosisContent) return;
    
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <html>
        <head>
            <title>AI Diagnosis Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .alert { padding: 10px; margin: 10px 0; border-radius: 5px; }
                .alert-danger { background-color: #f8d7da; color: #721c24; }
                .alert-warning { background-color: #fff3cd; color: #856404; }
                .alert-success { background-color: #d4edda; color: #155724; }
                .list-group-item { padding: 5px 0; border-bottom: 1px solid #eee; }
            </style>
        </head>
        <body>
            <h1>AI Symptom Diagnosis Report</h1>
            <p><strong>Generated on:</strong> ${new Date().toLocaleString()}</p>
            ${diagnosisContent.innerHTML}
            <p><small><em>This diagnosis was generated by AI and should not replace professional medical advice.</em></small></p>
        </body>
        </html>
    `);
    printWindow.document.close();
    printWindow.print();
}

// Initialize all functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initTooltips();
    
    // Initialize symptom suggestions if on dashboard
    if (window.location.pathname === '/dashboard') {
        initSymptomSuggestions();
    }
    
    // Add smooth scrolling to all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Add confirmation to logout link
    const logoutLink = document.querySelector('a[href*="logout"]');
    if (logoutLink) {
        logoutLink.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to logout?')) {
                e.preventDefault();
            }
        });
    }
    
    // Auto-hide alerts after 5 seconds
    document.querySelectorAll('.alert').forEach(alert => {
        if (!alert.querySelector('.btn-close')) return;
        
        setTimeout(() => {
            if (alert && alert.parentNode) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });
});

// Export functions for global use
window.showAlert = showAlert;
window.formatDate = formatDate;
window.formatDateTime = formatDateTime;
window.validateForm = validateForm;
window.setLoadingState = setLoadingState;
window.apiRequest = apiRequest;
window.addSymptom = addSymptom;
window.copyToClipboard = copyToClipboard;
window.printDiagnosis = printDiagnosis;