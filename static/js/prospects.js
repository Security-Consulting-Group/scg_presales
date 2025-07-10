// ====================================
// SCG PROSPECTS FUNCTIONALITY
// ====================================

class SCGProspects {
    constructor() {
        this.currentView = 'table';
        this.init();
    }

    init() {
        // Initialize components
        this.initViewToggle();
        this.initFilters();
        this.initSearch();
        this.initTableInteractions();
        this.initDetailTabs();
        this.initFormValidation();
    }

    // ====================================
    // VIEW TOGGLE (TABLE/CARD)
    // ====================================

    initViewToggle() {
        const tableViewBtn = document.getElementById('tableView');
        const cardViewBtn = document.getElementById('cardView');
        const prospectsTable = document.getElementById('prospectsTable');
        const prospectsCards = document.getElementById('prospectsCards');

        if (tableViewBtn && cardViewBtn && prospectsTable && prospectsCards) {
            tableViewBtn.addEventListener('click', () => {
                this.switchToTableView();
            });

            cardViewBtn.addEventListener('click', () => {
                this.switchToCardView();
            });
        }
    }

    switchToTableView() {
        const tableViewBtn = document.getElementById('tableView');
        const cardViewBtn = document.getElementById('cardView');
        const prospectsTable = document.getElementById('prospectsTable');
        const prospectsCards = document.getElementById('prospectsCards');

        if (tableViewBtn && cardViewBtn && prospectsTable && prospectsCards) {
            // Update buttons
            tableViewBtn.classList.add('active');
            cardViewBtn.classList.remove('active');

            // Show/hide views
            prospectsTable.classList.remove('d-none');
            prospectsCards.classList.add('d-none');

            this.currentView = 'table';
            
            // Store preference
            localStorage.setItem('prospects_view', 'table');
        }
    }

    switchToCardView() {
        const tableViewBtn = document.getElementById('tableView');
        const cardViewBtn = document.getElementById('cardView');
        const prospectsTable = document.getElementById('prospectsTable');
        const prospectsCards = document.getElementById('prospectsCards');

        if (tableViewBtn && cardViewBtn && prospectsTable && prospectsCards) {
            // Update buttons
            cardViewBtn.classList.add('active');
            tableViewBtn.classList.remove('active');

            // Show/hide views
            prospectsCards.classList.remove('d-none');
            prospectsTable.classList.add('d-none');

            this.currentView = 'card';
            
            // Store preference
            localStorage.setItem('prospects_view', 'card');
        }
    }

    // ====================================
    // FILTERS AND SEARCH
    // ====================================

    initFilters() {
        const filterForm = document.getElementById('filterForm');
        const clearFiltersBtn = document.getElementById('clearFilters');

        if (filterForm) {
            // Auto-submit on filter change
            const filterInputs = filterForm.querySelectorAll('select[name="status"], select[name="source"], select[name="industry"]');
            filterInputs.forEach(input => {
                input.addEventListener('change', () => {
                    this.applyFilters();
                });
            });
        }

        if (clearFiltersBtn) {
            clearFiltersBtn.addEventListener('click', () => {
                this.clearFilters();
            });
        }

        // Restore view preference
        const savedView = localStorage.getItem('prospects_view');
        if (savedView === 'card') {
            this.switchToCardView();
        }
    }

    initSearch() {
        const searchInput = document.getElementById('searchInput');
        
        if (searchInput) {
            let searchTimeout;

            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                
                // Debounce search to avoid too many requests
                searchTimeout = setTimeout(() => {
                    this.applyFilters();
                }, 500);
            });

            // Clear search on Escape key
            searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    searchInput.value = '';
                    this.applyFilters();
                }
            });
        }
    }

    applyFilters() {
        const filterForm = document.getElementById('filterForm');
        if (filterForm) {
            filterForm.submit();
        }
    }

    clearFilters() {
        const filterForm = document.getElementById('filterForm');
        
        if (filterForm) {
            // Clear all form inputs
            filterForm.querySelectorAll('input, select').forEach(input => {
                if (input.type === 'checkbox' || input.type === 'radio') {
                    input.checked = false;
                } else {
                    input.value = '';
                }
            });
            
            // Submit form to apply cleared filters
            filterForm.submit();
        }
    }

    // ====================================
    // TABLE INTERACTIONS
    // ====================================

    initTableInteractions() {
        // Handle row clicks for navigation
        const prospectRows = document.querySelectorAll('.prospect-row');
        
        prospectRows.forEach(row => {
            row.addEventListener('click', (e) => {
                // Don't navigate if clicking on buttons or links
                if (e.target.closest('button, a, .dropdown')) {
                    return;
                }
                
                const href = row.dataset.href;
                if (href) {
                    window.location.href = href;
                }
            });
        });

        // Initialize tooltips for action buttons
        this.initTooltips();
    }

    initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // ====================================
    // DETAIL PAGE TABS
    // ====================================

    initDetailTabs() {
        const tabTriggers = document.querySelectorAll('#prospectDetailTabs button[data-bs-toggle="tab"]');
        
        tabTriggers.forEach(trigger => {
            trigger.addEventListener('shown.bs.tab', (event) => {
                const targetTab = event.target.getAttribute('data-bs-target');
                
                // Lazy load content if needed
                this.loadTabContent(targetTab);
            });
        });
    }

    loadTabContent(tabId) {
        // Placeholder for lazy loading tab content
        // Can be expanded to load data via AJAX when switching tabs
        switch(tabId) {
            case '#inquiries':
                break;
            case '#surveys':
                break;
            case '#notes':
                break;
            default:
                break;
        }
    }

    // ====================================
    // FORM VALIDATION
    // ====================================

    initFormValidation() {
        const prospectForm = document.querySelector('.prospect-form');
        
        if (prospectForm) {
            prospectForm.addEventListener('submit', (e) => {
                if (!this.validateProspectForm(prospectForm)) {
                    e.preventDefault();
                    this.showValidationErrors();
                }
            });

            // Real-time validation
            const formInputs = prospectForm.querySelectorAll('input, select, textarea');
            formInputs.forEach(input => {
                input.addEventListener('blur', () => {
                    this.validateField(input);
                });

                input.addEventListener('input', () => {
                    this.clearFieldValidation(input);
                });
            });
        }
    }

    validateProspectForm(form) {
        let isValid = true;
        const requiredFields = form.querySelectorAll('input[required], select[required], textarea[required]');

        requiredFields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });

        return isValid;
    }

    validateField(field) {
        const value = field.value.trim();
        let isValid = true;
        let errorMessage = '';

        // Clear previous validation
        this.clearFieldValidation(field);

        // Required field validation
        if (field.hasAttribute('required') && !value) {
            isValid = false;
            errorMessage = 'Este campo es obligatorio';
        }

        // Email validation
        if (field.type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Por favor ingrese un email válido';
            }
        }

        // Show validation state
        if (!isValid) {
            this.showFieldError(field, errorMessage);
        } else {
            this.showFieldSuccess(field);
        }

        return isValid;
    }

    showFieldError(field, message) {
        field.classList.add('is-invalid');
        field.classList.remove('is-valid');

        // Add error message if not exists
        const formGroup = field.closest('.admin-form-group');
        let errorElement = formGroup.querySelector('.field-error');
        
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'field-error text-danger mt-1';
            errorElement.innerHTML = `<i class="fas fa-exclamation-triangle me-1"></i><small>${message}</small>`;
            field.parentNode.insertBefore(errorElement, field.nextSibling);
        } else {
            errorElement.innerHTML = `<i class="fas fa-exclamation-triangle me-1"></i><small>${message}</small>`;
        }
    }

    showFieldSuccess(field) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        
        // Remove error message
        const formGroup = field.closest('.admin-form-group');
        const errorElement = formGroup.querySelector('.field-error');
        if (errorElement) {
            errorElement.remove();
        }
    }

    clearFieldValidation(field) {
        field.classList.remove('is-invalid', 'is-valid');
        
        const formGroup = field.closest('.admin-form-group');
        const errorElement = formGroup.querySelector('.field-error');
        if (errorElement) {
            errorElement.remove();
        }
    }

    showValidationErrors() {
        window.scgAdmin.showNotification('Por favor corrija los errores en el formulario', 'error');
    }

    // ====================================
    // PROSPECT ACTIONS
    // ====================================

    async markInquiryResponded(inquiryId, button) {
        const confirmMessage = button.dataset.confirm;
        
        if (confirmMessage && !confirm(confirmMessage)) {
            return;
        }

        // Show loading state
        const originalContent = button.innerHTML;
        button.innerHTML = '<span class="loading-spinner"></span>';
        button.disabled = true;

        try {
            const response = await fetch(button.dataset.actionUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest',
                },
            });

            const data = await response.json();

            if (data.success) {
                window.scgAdmin.showNotification(data.message, 'success');
                
                // Update UI to show as responded
                const inquiryItem = button.closest('.inquiry-item');
                if (inquiryItem) {
                    inquiryItem.classList.remove('unresponded');
                    
                    // Replace button with success badge
                    const statusDiv = button.closest('.inquiry-status');
                    statusDiv.innerHTML = '<span class="badge bg-success"><i class="fas fa-check me-1"></i>Respondido</span>';
                }
            } else {
                window.scgAdmin.showNotification(data.message || 'Error procesando la acción', 'error');
                // Restore button
                button.innerHTML = originalContent;
                button.disabled = false;
            }
        } catch {
            window.scgAdmin.showNotification('Error de conexión', 'error');
            // Restore button
            button.innerHTML = originalContent;
            button.disabled = false;
        }
    }

    // ====================================
    // UTILITY FUNCTIONS
    // ====================================

    getCSRFToken() {
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');
        return csrfMeta ? csrfMeta.getAttribute('content') : '';
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    // ====================================
    // EXPORT FUNCTIONALITY
    // ====================================

    exportProspectsData() {
        // Get current filters
        const filterForm = document.getElementById('filterForm');
        const params = new URLSearchParams();
        
        if (filterForm) {
            const formData = new FormData(filterForm);
            for (let [key, value] of formData.entries()) {
                if (value) {
                    params.append(key, value);
                }
            }
        }
        
        // Add export parameter
        params.append('export', 'csv');
        
        // Create download link
        const exportUrl = `${window.location.pathname}?${params.toString()}`;
        
        // Create temporary link and trigger download
        const link = document.createElement('a');
        link.href = exportUrl;
        link.download = `prospects_export_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        window.scgAdmin.showNotification('Exportación iniciada', 'success');
    }

    // ====================================
    // KEYBOARD SHORTCUTS
    // ====================================

    initKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + F to focus search
            if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
                e.preventDefault();
                const searchInput = document.getElementById('searchInput');
                if (searchInput) {
                    searchInput.focus();
                }
            }
            
            // Escape to clear search
            if (e.key === 'Escape') {
                const searchInput = document.getElementById('searchInput');
                if (searchInput && searchInput === document.activeElement) {
                    searchInput.value = '';
                    this.applyFilters();
                }
            }
        });
    }
}

// ====================================
// GLOBAL FUNCTIONS
// ====================================

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.scgProspects = new SCGProspects();
    
    // Initialize keyboard shortcuts
    window.scgProspects.initKeyboardShortcuts();
});

// Global export function
function exportProspects() {
    if (window.scgProspects) {
        window.scgProspects.exportProspectsData();
    }
}

// Handle inquiry response buttons
document.addEventListener('click', function(e) {
    if (e.target.matches('[data-action-url]') || e.target.closest('[data-action-url]')) {
        e.preventDefault();
        const button = e.target.matches('[data-action-url]') ? e.target : e.target.closest('[data-action-url]');
        
        if (button.dataset.actionUrl.includes('mark-inquiry-responded')) {
            const inquiryId = button.dataset.actionUrl.split('/').slice(-2, -1)[0];
            window.scgProspects.markInquiryResponded(inquiryId, button);
        }
    }
});

// Make functions available globally
window.SCGProspects = {
    exportData: function() {
        if (window.scgProspects) {
            window.scgProspects.exportProspectsData();
        }
    },
    
    switchView: function(view) {
        if (window.scgProspects) {
            if (view === 'table') {
                window.scgProspects.switchToTableView();
            } else if (view === 'card') {
                window.scgProspects.switchToCardView();
            }
        }
    },
    
    markInquiryResponded: function(inquiryId, button) {
        if (window.scgProspects) {
            window.scgProspects.markInquiryResponded(inquiryId, button);
        }
    }
};

// Error handling
window.addEventListener('error', function(e) {
});

function changeProspectStatus(prospectId) {
    // Verificar si el elemento modal existe
    const modalElement = document.getElementById('changeStatusModal');
    if (!modalElement) {
        window.scgAdmin.showNotification('Error al abrir el modal: Elemento no encontrado', 'error');
        return;
    }
    
    try {
        // Intentar varias formas de mostrar el modal, en orden de preferencia
        
        // 1. Intentar con Bootstrap directamente
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        } 
        // 2. Intentar con jQuery si está disponible
        else if (typeof $ !== 'undefined') {
            $(modalElement).modal('show');
        } 
        // 3. Intentar con la función Modal directamente sobre el elemento
        else if (typeof modalElement.Modal === 'function') {
            modalElement.Modal();
        } 
        // 4. Intentar activarlo por atributo data
        else {
            // Establecer data-attribute para modal
            modalElement.setAttribute('data-bs-toggle', 'modal');
            modalElement.setAttribute('data-bs-show', 'true');
            // Disparar un evento click para activarlo
            const event = new MouseEvent('click', {
                bubbles: true,
                cancelable: true,
                view: window
            });
            modalElement.dispatchEvent(event);
        }
        
        // Preseleccionar el estado actual si es posible
        const statusBadge = document.querySelector('.status-badge');
        if (statusBadge) {
            const currentStatus = Array.from(statusBadge.classList)
                .find(cls => cls.startsWith('status-'))
                ?.replace('status-', '')
                ?.toUpperCase();
                
            if (currentStatus) {
                const selectElement = document.getElementById('prospectStatusSelect');
                // Buscar y seleccionar la opción que coincida con el estado actual
                for (let i = 0; i < selectElement.options.length; i++) {
                    if (selectElement.options[i].value === currentStatus) {
                        selectElement.selectedIndex = i;
                        break;
                    }
                }
            }
        }
        
        // Limpiar handler previo para evitar múltiples subscripciones
        const confirmButton = document.getElementById('confirmStatusChange');
        const oldClickHandler = confirmButton.onclick;
        if (oldClickHandler) {
            confirmButton.removeEventListener('click', oldClickHandler);
        }
        
        // Manejar confirmación
        confirmButton.addEventListener('click', async () => {
            const selectedStatus = document.getElementById('prospectStatusSelect').value;
            
            try {
                // Obtener CSRF token desde la meta tag que está en base.html
                const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
                
                // Enviar petición AJAX
                const response = await fetch(`/admin-panel/ajax/prospects/${prospectId}/change-status/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrfToken
                    },
                    body: `status=${selectedStatus}`
                });
                
                const data = await response.json();
                
                if (response.ok && data.success) {
                    // Actualizar UI
                    const statusBadge = document.querySelector('.status-badge');
                    if (statusBadge) {
                        // Quitar clases anteriores
                        statusBadge.classList.forEach(cls => {
                            if (cls.startsWith('status-')) {
                                statusBadge.classList.remove(cls);
                            }
                        });
                        
                        // Añadir nueva clase
                        statusBadge.classList.add(`status-${data.status.toLowerCase()}`);
                        statusBadge.textContent = data.status_display;
                    }
                    
                    // Cerrar modal (intentar diferentes formas de cerrarlo)
                    if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                        const modal = bootstrap.Modal.getInstance(modalElement);
                        if (modal) modal.hide();
                    } else if (typeof $ !== 'undefined') {
                        $(modalElement).modal('hide');
                    }
                    
                    // Mostrar notificación
                    window.scgAdmin.showNotification(data.message, 'success');
                } else {
                    throw new Error(data.message || 'Error al cambiar estado');
                }
            } catch (error) {
                window.scgAdmin.showNotification(error.message || 'Error al cambiar estado', 'error');
            }
        });
    } catch {
        window.scgAdmin.showNotification('Error al abrir el modal', 'error');
    }
}

// ====================================
// PROSPECT DETAIL PAGE FUNCTIONS
// ====================================

// Function to view survey details
function viewSurveyDetails(submissionId) {
    // Usar el modal que ya existe en el HTML
    const modal = new bootstrap.Modal(document.getElementById('surveyDetailsModal'));
    
    // Mostrar el modal con el spinner de carga
    modal.show();
    
    // En una implementación real, aquí se haría una petición AJAX para obtener los detalles
    // Por ahora, simulamos una carga y mostramos un mensaje
    setTimeout(() => {
        document.getElementById('surveyDetailsContent').innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                Funcionalidad en desarrollo. Survey ID: ${submissionId}
            </div>
            <p class="text-muted">Aquí se mostrarán las respuestas del survey.</p>
        `;
    }, 1000);
}

// Function to disable survey submission
function disableSurveySubmission(submissionId) {
    // Usar el modal que ya existe en el HTML
    const modal = new bootstrap.Modal(document.getElementById('disableSurveyModal'));
    
    // Mostrar el modal
    modal.show();
    
    // Limpiar handler previo para evitar múltiples subscripciones
    const confirmButton = document.getElementById('confirmDisableSurvey');
    const oldClickHandler = confirmButton.onclick;
    if (oldClickHandler) {
        confirmButton.removeEventListener('click', oldClickHandler);
    }
    
    // Manejar confirmación
    confirmButton.addEventListener('click', async () => {
        try {
            // En una implementación real, aquí se haría una petición AJAX
            // Por ahora, simulamos una respuesta exitosa
            
            // Cerrar modal
            modal.hide();
            
            // Mostrar notificación
            window.scgAdmin.showNotification('Survey deshabilitado correctamente', 'success');
            
            // Opcional: Actualizar UI para reflejar el cambio
            const surveyItem = document.querySelector(`.survey-item[data-id="${submissionId}"]`);
            if (surveyItem) {
                surveyItem.classList.add('disabled');
            }
            
        } catch {
            window.scgAdmin.showNotification('Error al deshabilitar el survey', 'error');
        }
    });
}

// Function to invite prospect to survey
function inviteToSurvey(prospectId) {
    // Usar el modal que ya existe en el HTML
    const modal = new bootstrap.Modal(document.getElementById('inviteToSurveyModal'));
    
    // En una implementación real, aquí cargaríamos la lista de surveys disponibles
    // Por ahora, agregamos algunas opciones de ejemplo
    const surveySelect = document.getElementById('surveySelectInvite');
    surveySelect.innerHTML = `
        <option value="" selected disabled>Seleccione un survey</option>
        <option value="1">Diagnóstico de Seguridad</option>
        <option value="2">Evaluación de Riesgos</option>
        <option value="3">Análisis de Cumplimiento</option>
    `;
    
    // Mostrar el modal
    modal.show();
    
    // Limpiar handler previo para evitar múltiples subscripciones
    const confirmButton = document.getElementById('confirmInviteToSurvey');
    const oldClickHandler = confirmButton.onclick;
    if (oldClickHandler) {
        confirmButton.removeEventListener('click', oldClickHandler);
    }
    
    // Manejar confirmación
    confirmButton.addEventListener('click', async () => {
        const selectedSurvey = document.getElementById('surveySelectInvite').value;
        const inviteMessage = document.getElementById('inviteMessage').value;
        
        if (!selectedSurvey) {
            window.scgAdmin.showNotification('Por favor seleccione un survey', 'error');
            return;
        }
        
        try {
            // En una implementación real, aquí se haría una petición AJAX
            // Por ahora, simulamos una respuesta exitosa
            
            // Cerrar modal
            modal.hide();
            
            // Mostrar notificación
            window.scgAdmin.showNotification('Invitación enviada correctamente', 'success');
            
        } catch {
            window.scgAdmin.showNotification('Error al enviar la invitación', 'error');
        }
    });
}

// Function to add interaction note
function addInteractionNote(prospectId) {
    // Usar el modal que ya existe en el HTML
    const modal = new bootstrap.Modal(document.getElementById('addNoteModal'));
    
    // Limpiar campos del formulario
    document.getElementById('noteTitle').value = '';
    document.getElementById('noteType').value = 'PHONE_CALL';
    document.getElementById('noteContent').value = '';
    document.getElementById('nextSteps').value = '';
    document.getElementById('followUpDate').value = '';
    
    // Mostrar el modal
    modal.show();
    
    // Limpiar handler previo para evitar múltiples subscripciones
    const confirmButton = document.getElementById('confirmAddNote');
    const oldClickHandler = confirmButton.onclick;
    if (oldClickHandler) {
        confirmButton.removeEventListener('click', oldClickHandler);
    }
    
    // Manejar confirmación
    confirmButton.addEventListener('click', async () => {
        const title = document.getElementById('noteTitle').value;
        const noteType = document.getElementById('noteType').value;
        const content = document.getElementById('noteContent').value;
        const nextSteps = document.getElementById('nextSteps').value;
        const followUpDate = document.getElementById('followUpDate').value;
        
        if (!title || !content) {
            window.scgAdmin.showNotification('Por favor complete los campos requeridos', 'error');
            return;
        }
        
        try {
            // En una implementación real, aquí se haría una petición AJAX
            // Por ahora, simulamos una respuesta exitosa
            
            // Cerrar modal
            modal.hide();
            
            // Mostrar notificación
            window.scgAdmin.showNotification('Nota agregada correctamente', 'success');
            
            // En una implementación real, aquí actualizaríamos la UI para mostrar la nueva nota
            
        } catch {
            window.scgAdmin.showNotification('Error al agregar la nota', 'error');
        }
    });
}

// Function to schedule follow up
function scheduleFollowUp(prospectId) {
    // Usar el modal que ya existe en el HTML
    const modal = new bootstrap.Modal(document.getElementById('scheduleFollowUpModal'));
    
    // Limpiar campos del formulario
    document.getElementById('followUpTitle').value = '';
    document.getElementById('followUpType').value = 'PHONE_CALL';
    document.getElementById('followUpDate').value = '';
    document.getElementById('followUpNotes').value = '';
    
    // Mostrar el modal
    modal.show();
    
    // Limpiar handler previo para evitar múltiples subscripciones
    const confirmButton = document.getElementById('confirmScheduleFollowUp');
    const oldClickHandler = confirmButton.onclick;
    if (oldClickHandler) {
        confirmButton.removeEventListener('click', oldClickHandler);
    }
    
    // Manejar confirmación
    confirmButton.addEventListener('click', async () => {
        const title = document.getElementById('followUpTitle').value;
        const followUpType = document.getElementById('followUpType').value;
        const followUpDate = document.getElementById('followUpDate').value;
        const notes = document.getElementById('followUpNotes').value;
        
        if (!title || !followUpDate) {
            window.scgAdmin.showNotification('Por favor complete los campos requeridos', 'error');
            return;
        }
        
        try {
            // En una implementación real, aquí se haría una petición AJAX
            // Por ahora, simulamos una respuesta exitosa
            
            // Cerrar modal
            modal.hide();
            
            // Mostrar notificación
            window.scgAdmin.showNotification('Seguimiento programado correctamente', 'success');
            
            // En una implementación real, aquí actualizaríamos la UI
            
        } catch {
            window.scgAdmin.showNotification('Error al programar el seguimiento', 'error');
        }
    });
}

// Function to export prospect data
function exportProspectData(prospectId) {
    // Usar el modal que ya existe en el HTML
    const modal = new bootstrap.Modal(document.getElementById('exportDataModal'));
    
    // Mostrar el modal
    modal.show();
    
    // Limpiar handler previo para evitar múltiples subscripciones
    const confirmButton = document.getElementById('confirmExportData');
    const oldClickHandler = confirmButton.onclick;
    if (oldClickHandler) {
        confirmButton.removeEventListener('click', oldClickHandler);
    }
    
    // Manejar confirmación
    confirmButton.addEventListener('click', async () => {
        const exportBasicInfo = document.getElementById('exportBasicInfo').checked;
        const exportInquiries = document.getElementById('exportInquiries').checked;
        const exportSurveys = document.getElementById('exportSurveys').checked;
        const exportNotes = document.getElementById('exportNotes').checked;
        const format = document.getElementById('exportFormat').value;
        
        if (!exportBasicInfo && !exportInquiries && !exportSurveys && !exportNotes) {
            window.scgAdmin.showNotification('Por favor seleccione al menos un tipo de dato para exportar', 'error');
            return;
        }
        
        try {
            // En una implementación real, aquí se haría una petición AJAX
            // Por ahora, simulamos una respuesta exitosa
            
            // Cerrar modal
            modal.hide();
            
            // Mostrar notificación
            window.scgAdmin.showNotification('Exportación iniciada. Se descargará en breve.', 'success');
            
        } catch {
            window.scgAdmin.showNotification('Error al exportar los datos', 'error');
        }
    });
}

// Function to export all prospects
function exportProspects() {
    // Get current filters
    const filterForm = document.getElementById('filterForm');
    const params = new URLSearchParams();
    
    if (filterForm) {
        const formData = new FormData(filterForm);
        for (let [key, value] of formData.entries()) {
            if (value) {
                params.append(key, value);
            }
        }
    }
    
    // Add export parameter
    params.append('export', 'csv');
    
    // Create download link
    const exportUrl = `${window.location.pathname}?${params.toString()}`;
    
    // Create temporary link and trigger download
    const link = document.createElement('a');
    link.href = exportUrl;
    link.download = `prospects_export_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    window.scgAdmin.showNotification('Exportación iniciada', 'success');
}