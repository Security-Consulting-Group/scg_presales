/**
 * Prospect Form JavaScript functionality
 */

class ProspectForm {
    constructor() {
        this.form = null;
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.initializeForm();
            this.setupEmailFormatting();
            this.setupStatusChangeWarnings();
            this.setupEngagementScore();
        });
    }

    initializeForm() {
        this.form = document.querySelector('.prospect-form');
        if (!this.form) return;

        // Add real-time validation
        const requiredFields = this.form.querySelectorAll('input[required], select[required]');
        requiredFields.forEach(field => {
            field.addEventListener('blur', (e) => this.validateField(e));
            field.addEventListener('input', (e) => this.clearFieldError(e));
        });
    }

    setupEmailFormatting() {
        const emailField = document.querySelector('input[type="email"]');
        if (emailField) {
            emailField.addEventListener('blur', function() {
                this.value = this.value.toLowerCase().trim();
            });
        }
    }

    setupStatusChangeWarnings() {
        const statusField = document.querySelector('select[name="status"]');
        if (statusField) {
            const originalValue = statusField.value;
            statusField.addEventListener('change', function() {
                if (this.value === 'CLOSED_LOST') {
                    if (!confirm('¿Está seguro de marcar este prospect como "Closed Lost"? Esta acción indica que se perdió la oportunidad.')) {
                        this.value = originalValue;
                    }
                }
            });
        }
    }

    validateField(event) {
        const field = event.target;
        const value = field.value.trim();
        
        // Clear previous errors
        this.clearFieldError(event);
        
        // Validate based on field type
        if (field.type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                this.showFieldError(field, 'Por favor ingrese un email válido');
                return false;
            }
        }
        
        if (field.required && !value) {
            this.showFieldError(field, 'Este campo es obligatorio');
            return false;
        }
        
        return true;
    }

    showFieldError(field, message) {
        const formGroup = field.closest('.admin-form-group');
        const existingError = formGroup.querySelector('.form-error');
        
        if (!existingError) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'form-error';
            errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle me-1"></i>${message}`;
            field.parentNode.insertBefore(errorDiv, field.nextSibling);
        }
        
        field.classList.add('is-invalid');
    }

    clearFieldError(event) {
        const field = event.target;
        const formGroup = field.closest('.admin-form-group');
        const existingError = formGroup.querySelector('.form-error');
        
        if (existingError && !existingError.textContent.includes('Este campo es obligatorio')) {
            existingError.remove();
        }
        
        field.classList.remove('is-invalid');
    }

    setupEngagementScore() {
        // Setup engagement badge colors
        const engagementBadge = document.querySelector('.engagement-badge');
        if (engagementBadge) {
            const surveys = parseInt(engagementBadge.dataset.surveys) || 0;
            const inquiries = parseInt(engagementBadge.dataset.inquiries) || 0;
            
            if (surveys > 0) {
                engagementBadge.classList.add('bg-success');
            } else if (inquiries > 1) {
                engagementBadge.classList.add('bg-warning');
            } else {
                engagementBadge.classList.add('bg-secondary');
            }
        }

        // Setup engagement progress bar
        const engagementProgress = document.querySelector('.engagement-progress');
        if (engagementProgress) {
            const surveys = parseInt(engagementProgress.dataset.surveys) || 0;
            const inquiries = parseInt(engagementProgress.dataset.inquiries) || 0;
            
            let percentage = 25; // default
            let colorClass = 'bg-secondary';
            
            if (surveys > 0) {
                percentage = 85;
                colorClass = 'bg-success';
            } else if (inquiries > 1) {
                percentage = 60;
                colorClass = 'bg-warning';
            }
            
            engagementProgress.classList.add(colorClass);
            engagementProgress.style.width = percentage + '%';
        }
    }

    // Additional actions for existing prospects
    scheduleFollowUp(prospectId) {
        if (window.scgAdmin && window.scgAdmin.showNotification) {
            window.scgAdmin.showNotification('Función en desarrollo', 'info');
        } else {
            alert('Función en desarrollo');
        }
    }

    exportProspectData(prospectId) {
        if (window.scgAdmin && window.scgAdmin.showNotification) {
            window.scgAdmin.showNotification('Exportación iniciada', 'success');
        } else {
            alert('Exportación iniciada');
        }
    }

    mergeProspect(prospectId) {
        if (window.scgAdmin && window.scgAdmin.showNotification) {
            window.scgAdmin.showNotification('Función en desarrollo', 'info');
        } else {
            alert('Función en desarrollo');
        }
    }

    archiveProspect(prospectId) {
        if (confirm('¿Está seguro de que desea archivar este prospect? Esta acción se puede revertir pero el prospect no aparecerá en las listas principales.')) {
            if (window.scgAdmin && window.scgAdmin.showNotification) {
                window.scgAdmin.showNotification('Función en desarrollo', 'info');
            } else {
                alert('Función en desarrollo');
            }
        }
    }
}

// Initialize prospect form functionality
const prospectForm = new ProspectForm();

// Export functions for global access (for onclick handlers)
window.scheduleFollowUp = (prospectId) => prospectForm.scheduleFollowUp(prospectId);
window.exportProspectData = (prospectId) => prospectForm.exportProspectData(prospectId);
window.mergeProspect = (prospectId) => prospectForm.mergeProspect(prospectId);
window.archiveProspect = (prospectId) => prospectForm.archiveProspect(prospectId); 