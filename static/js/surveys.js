/**
 * Survey Management JavaScript functionality
 */

class SurveyManager {
    constructor() {
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.setupSurveyManager();
            this.setupFormValidation();
            this.setupRowClickHandlers();
            this.setupDeleteHandlers();
            this.loadSurveyData();
        });
    }

    setupSurveyManager() {
        console.log('📋 Survey manager initialized');
    }

    setupFormValidation() {
        // Form validation for survey forms
        const surveyForms = document.querySelectorAll('form[data-loading]');
        surveyForms.forEach(form => {
            form.addEventListener('submit', (e) => this.validateSurveyForm(e, form));
        });

        // Featured checkbox warning
        const featuredCheckbox = document.getElementById('id_is_featured');
        if (featuredCheckbox) {
            featuredCheckbox.addEventListener('change', function() {
                if (this.checked) {
                    window.scgAdmin.showNotification(
                        'Solo un survey puede estar featured a la vez.',
                        'info'
                    );
                }
            });
        }
    }

    validateSurveyForm(e, form) {
        // Check if it's a section form (has order but no version)
        if (document.getElementById('id_order') && !document.getElementById('id_version')) {
            this.validateSectionForm(e);
            return;
        }
        
        // Survey form validation
        const title = document.getElementById('id_title')?.value.trim();
        const version = document.getElementById('id_version')?.value.trim();
        const maxScore = document.getElementById('id_max_score')?.value;
        
        if (!title || !version || !maxScore) {
            e.preventDefault();
            window.scgAdmin.showNotification('Por favor completa todos los campos requeridos', 'error');
            return;
        }
        
        if (parseInt(maxScore) < 1) {
            e.preventDefault();
            window.scgAdmin.showNotification('La puntuación máxima debe ser mayor a 0', 'error');
            return;
        }
    }

    validateSectionForm(e) {
        const title = document.getElementById('id_title')?.value.trim();
        const order = document.getElementById('id_order')?.value;
        const maxPoints = document.getElementById('id_max_points')?.value;
        
        if (!title || !order || !maxPoints) {
            e.preventDefault();
            window.scgAdmin.showNotification('Por favor completa todos los campos requeridos', 'error');
            return;
        }
        
        if (parseInt(order) < 1) {
            e.preventDefault();
            window.scgAdmin.showNotification('El orden debe ser mayor a 0', 'error');
            return;
        }
        
        if (parseInt(maxPoints) < 0) {
            e.preventDefault();
            window.scgAdmin.showNotification('Los puntos máximos no pueden ser negativos', 'error');
            return;
        }
    }

    setupRowClickHandlers() {
        // Make table rows clickable
        document.querySelectorAll('tr[data-href]').forEach(row => {
            row.addEventListener('click', function(e) {
                if (!e.target.closest('.dropdown, button, a, .action-buttons')) {
                    window.location.href = this.dataset.href;
                }
            });
        });

        // Enhanced search with keyboard shortcut
        document.addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.getElementById('searchInput');
                if (searchInput) {
                    searchInput.focus();
                }
            }
        });
    }

    setupDeleteHandlers() {
        // Handle delete buttons for sections and questions
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('delete-section-btn')) {
                const actionUrl = e.target.dataset.actionUrl;
                const confirmMsg = e.target.dataset.confirm;
                if (confirm(confirmMsg)) {
                    console.log('🗑️ Eliminando sección via:', actionUrl);
                    // TODO: Implement actual deletion
                }
            }
            
            if (e.target.classList.contains('delete-question-btn')) {
                const actionUrl = e.target.dataset.actionUrl;
                const confirmMsg = e.target.dataset.confirm;
                if (confirm(confirmMsg)) {
                    console.log('🗑️ Eliminando pregunta via:', actionUrl);
                    // TODO: Implement actual deletion
                }
            }
        });
    }

    loadSurveyData() {
        const dataElement = document.querySelector('[data-survey-code]');
        if (dataElement) {
            const surveyCode = dataElement.getAttribute('data-survey-code');
            console.log('📋 Survey Detail loaded:', surveyCode);
        }

        // Auto-suggest order for section forms
        const nextOrderElement = document.querySelector('[data-next-order]');
        if (nextOrderElement) {
            const orderInput = document.getElementById('id_order');
            if (orderInput && !orderInput.value) {
                const nextOrder = parseInt(nextOrderElement.getAttribute('data-next-order'));
                orderInput.value = nextOrder;
            }
        }
    }

    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(function() {
            window.scgAdmin.showNotification('URL copiada al portapapeles', 'success');
        }).catch(function(err) {
            console.error('Error copiando al portapapeles:', err);
            window.scgAdmin.showNotification('Error copiando al portapapeles', 'error');
        });
    }
}

// Initialize the survey manager
window.surveyManager = new SurveyManager();

// Global functions for templates
window.copyToClipboard = function(text) {
    window.surveyManager.copyToClipboard(text);
};

window.showTab = function(tabName) {
    const tab = document.getElementById(tabName + '-tab');
    if (tab) {
        tab.click();
    }
}; 