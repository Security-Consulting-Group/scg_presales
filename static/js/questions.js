/**
 * Question Management JavaScript functionality
 */

class QuestionManager {
    constructor() {
        this.optionsList = null;
        this.optionTemplate = null;
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.setupQuestionManager();
            this.setupFormValidation();
            this.setupOptionManagement();
        });
    }

    setupQuestionManager() {
        console.log('📝 Question manager initialized');
        
        this.optionsList = document.getElementById('optionsList');
        this.optionTemplate = document.getElementById('optionTemplate');
    }

    setupFormValidation() {
        const form = document.querySelector('form[data-loading]');
        if (form) {
            form.addEventListener('submit', (e) => this.validateQuestionForm(e));
        }
    }

    validateQuestionForm(e) {
        const section = document.getElementById('id_section')?.value;
        const questionText = document.getElementById('id_question_text')?.value.trim();
        const questionType = document.getElementById('id_question_type')?.value;
        const order = document.getElementById('id_order')?.value;
        const maxPoints = document.getElementById('id_max_points')?.value;
        
        if (!section || !questionText || !questionType || !order || !maxPoints) {
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

    setupOptionManagement() {
        const addNewOptionBtn = document.getElementById('addNewOptionBtn');
        const addMultipleBtn = document.getElementById('addMultipleBtn');
        const reorderBtn = document.getElementById('reorderBtn');
        const saveAllOptionsBtn = document.getElementById('saveAllOptionsBtn');
        
        if (addNewOptionBtn) {
            addNewOptionBtn.addEventListener('click', () => this.addNewOption());
        }
        
        if (addMultipleBtn) {
            addMultipleBtn.addEventListener('click', () => this.addMultipleOptions(5));
        }
        
        if (reorderBtn) {
            reorderBtn.addEventListener('click', () => this.reorderOptions());
        }
        
        if (saveAllOptionsBtn) {
            saveAllOptionsBtn.addEventListener('click', () => this.saveAllOptions());
        }
        
        // Event delegation for dynamic option controls
        if (this.optionsList) {
            this.optionsList.addEventListener('click', (e) => this.handleOptionAction(e));
            this.optionsList.addEventListener('input', (e) => this.handleOptionInput(e));
            
            // Initialize order on page load
            this.updateVisualOrder();
        }
    }

    handleOptionAction(e) {
        const optionRow = e.target.closest('.option-row');
        if (!optionRow) return;
        
        if (e.target.closest('.remove-option-btn')) {
            this.removeOption(optionRow);
        } else if (e.target.closest('.move-up-btn')) {
            this.moveOptionUp(optionRow);
        } else if (e.target.closest('.move-down-btn')) {
            this.moveOptionDown(optionRow);
        }
    }

    handleOptionInput(e) {
        if (e.target.classList.contains('option-order')) {
            this.updateVisualOrder();
        }
    }

    addNewOption(text = '', points = 0) {
        if (!this.optionTemplate || !this.optionsList) return;
        
        const clone = this.optionTemplate.content.cloneNode(true);
        const optionRow = clone.querySelector('.option-row');
        
        // Set values
        const textInput = clone.querySelector('.option-text');
        const pointsInput = clone.querySelector('.option-points');
        const orderInput = clone.querySelector('.option-order');
        
        textInput.value = text;
        pointsInput.value = points;
        orderInput.value = this.getNextOrder();
        
        // Add to list
        this.optionsList.appendChild(clone);
        
        // Focus on the new text input
        setTimeout(() => textInput.focus(), 100);
        
        this.updateVisualOrder();
    }

    addMultipleOptions(count) {
        for (let i = 0; i < count; i++) {
            this.addNewOption();
        }
        window.scgAdmin.showNotification(`${count} opciones agregadas`, 'success');
    }

    removeOption(optionRow) {
        if (confirm('¿Eliminar esta opción?')) {
            optionRow.remove();
            this.updateVisualOrder();
            window.scgAdmin.showNotification('Opción eliminada', 'success');
        }
    }

    moveOptionUp(optionRow) {
        const prev = optionRow.previousElementSibling;
        if (prev) {
            this.optionsList.insertBefore(optionRow, prev);
            this.updateVisualOrder();
        }
    }

    moveOptionDown(optionRow) {
        const next = optionRow.nextElementSibling;
        if (next) {
            this.optionsList.insertBefore(next, optionRow);
            this.updateVisualOrder();
        }
    }

    reorderOptions() {
        if (!this.optionsList) return;
        
        const options = Array.from(this.optionsList.querySelectorAll('.option-row'));
        options.forEach((option, index) => {
            const orderInput = option.querySelector('.option-order');
            orderInput.value = index + 1;
        });
        window.scgAdmin.showNotification('Opciones reordenadas automáticamente', 'success');
    }

    updateVisualOrder() {
        if (!this.optionsList) return;
        
        const options = Array.from(this.optionsList.querySelectorAll('.option-row'));
        options.forEach((option, index) => {
            const orderInput = option.querySelector('.option-order');
            if (!orderInput.value || orderInput.value <= 0) {
                orderInput.value = index + 1;
            }
        });
    }

    getNextOrder() {
        if (!this.optionsList) return 1;
        
        const existingOrders = Array.from(this.optionsList.querySelectorAll('.option-order'))
            .map(input => parseInt(input.value) || 0);
        return Math.max(0, ...existingOrders) + 1;
    }

    async saveAllOptions() {
        // Get question ID from page data
        const questionId = this.getQuestionId();
        if (!questionId) {
            window.scgAdmin.showNotification('Error: Guarda la pregunta primero antes de agregar opciones', 'error');
            return;
        }
        
        if (!this.optionsList) {
            window.scgAdmin.showNotification('No hay opciones para guardar', 'warning');
            return;
        }
        
        const optionRows = this.optionsList.querySelectorAll('.option-row');
        if (optionRows.length === 0) {
            window.scgAdmin.showNotification('No hay opciones para guardar', 'warning');
            return;
        }
        
        // Validate all options
        let hasErrors = false;
        optionRows.forEach(row => {
            const textInput = row.querySelector('.option-text');
            if (!textInput.value.trim()) {
                textInput.classList.add('is-invalid');
                hasErrors = true;
            } else {
                textInput.classList.remove('is-invalid');
            }
        });
        
        if (hasErrors) {
            window.scgAdmin.showNotification('Por favor completa el texto de todas las opciones', 'error');
            return;
        }
        
        // Show loading
        const saveAllOptionsBtn = document.getElementById('saveAllOptionsBtn');
        const originalText = saveAllOptionsBtn.innerHTML;
        saveAllOptionsBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Guardando...';
        saveAllOptionsBtn.disabled = true;
        
        try {
            // Prepare data
            const optionsData = Array.from(optionRows).map(row => ({
                id: row.dataset.optionId || null,
                text: row.querySelector('.option-text').value.trim(),
                order: parseInt(row.querySelector('.option-order').value) || 1,
                points: parseInt(row.querySelector('.option-points').value) || 0,
                isExisting: row.dataset.isExisting === 'true'
            }));
            
            // Send to backend
            const response = await fetch(`/admin-panel/ajax/questions/${questionId}/options/bulk-save/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: JSON.stringify({ options: optionsData })
            });
            
            const data = await response.json();
            
            if (data.success) {
                window.scgAdmin.showNotification(data.message, 'success');
                // Reload page to show updated options
                setTimeout(() => window.location.reload(), 1000);
            } else {
                window.scgAdmin.showNotification(data.message, 'error');
            }
            
        } catch (error) {
            console.error('Error saving options:', error);
            window.scgAdmin.showNotification('Error de conexión', 'error');
        } finally {
            // Restore button
            saveAllOptionsBtn.innerHTML = originalText;
            saveAllOptionsBtn.disabled = false;
        }
    }

    getQuestionId() {
        // Try to get question ID from various sources
        const questionIdElement = document.querySelector('[data-question-id]');
        if (questionIdElement) {
            return questionIdElement.getAttribute('data-question-id');
        }
        
        // Try to extract from URL pattern
        const urlMatch = window.location.pathname.match(/\/questions\/(\d+)\//);
        if (urlMatch) {
            return urlMatch[1];
        }
        
        // Try to get from a global variable set by template
        if (window.questionId) {
            return window.questionId;
        }
        
        return null;
    }

    getCSRFToken() {
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');
        if (csrfMeta) {
            return csrfMeta.getAttribute('content');
        }
        
        const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (csrfInput) {
            return csrfInput.value;
        }
        
        return '';
    }

    setNextOrder(nextOrder) {
        const orderInput = document.getElementById('id_order');
        if (orderInput && !orderInput.value) {
            orderInput.value = nextOrder;
        }
    }
}

// Initialize the question manager
window.questionManager = new QuestionManager();

// Global functions for templates
window.setNextOrder = function(nextOrder) {
    window.questionManager.setNextOrder(nextOrder);
}; 