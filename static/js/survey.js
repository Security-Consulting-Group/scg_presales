// ====================================
// SCG SURVEY SPA JAVASCRIPT
// ====================================

class SCGSurvey {
    constructor() {
        this.currentGroup = 1;
        this.totalGroups = document.querySelectorAll('.question-group').length;
        this.totalQuestions = parseInt(document.querySelector('.total-questions').textContent.split(' ')[0]);
        this.responses = {};
        this.surveyCode = this.getSurveyCode();
        this.csrfToken = this.getCSRFToken();
        
        this.init();
    }

    init() {
        console.log('🎯 Inicializando SCG Survey...');
        this.setupEventListeners();
        // NO llamar updateProgress() aquí - debe empezar en 0%
        this.validateCurrentGroup();
        console.log('✅ Survey inicializado correctamente!');
    }

    getSurveyCode() {
        // Extraer código del survey de la URL
        const pathParts = window.location.pathname.split('/');
        return pathParts[pathParts.indexOf('survey') + 1];
    }

    getCSRFToken() {
        // Obtener CSRF token del meta tag
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');
        return csrfMeta ? csrfMeta.getAttribute('content') : '';
    }

    setupEventListeners() {
        // Navegación entre grupos
        document.addEventListener('click', (e) => {
            if (e.target.id === 'nextBtn' || e.target.closest('#nextBtn')) {
                e.preventDefault();
                this.nextGroup();
            }
            
            if (e.target.id === 'prevBtn' || e.target.closest('#prevBtn')) {
                e.preventDefault();
                this.prevGroup();
            }
            
            if (e.target.id === 'showContactBtn' || e.target.closest('#showContactBtn')) {
                e.preventDefault();
                this.showContactForm();
            }
            
            if (e.target.id === 'backToSurveyBtn' || e.target.closest('#backToSurveyBtn')) {
                e.preventDefault();
                this.backToSurvey();
            }
        });

        // Capturar respuestas en tiempo real
        document.addEventListener('change', (e) => {
            if (e.target.hasAttribute('data-question')) {
                this.captureResponse(e.target);
                
                // Validación especial para pregunta 3 (datos sensibles)
                if (e.target.getAttribute('data-type') === 'multiple') {
                    this.handleSensitiveDataLogic(e.target);
                }
                
                this.validateCurrentGroup();
            }
        });

        // Envío del formulario
        const surveyForm = document.getElementById('surveyForm');
        if (surveyForm) {
            surveyForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitSurvey();
            });
        }
    }

    captureResponse(element) {
        const questionId = element.getAttribute('data-question');
        const type = element.getAttribute('data-type');

        if (!this.responses[questionId]) {
            this.responses[questionId] = {};
        }

        switch (type) {
            case 'single':
                if (element.checked) {
                    this.responses[questionId] = {
                        type: 'single',
                        option_id: parseInt(element.value)
                    };
                }
                break;

            case 'multiple':
                if (!this.responses[questionId].option_ids) {
                    this.responses[questionId] = {
                        type: 'multiple',
                        option_ids: []
                    };
                }
                
                const optionId = parseInt(element.value);
                if (element.checked) {
                    if (!this.responses[questionId].option_ids.includes(optionId)) {
                        this.responses[questionId].option_ids.push(optionId);
                    }
                } else {
                    this.responses[questionId].option_ids = 
                        this.responses[questionId].option_ids.filter(id => id !== optionId);
                }
                break;

            case 'text':
            case 'email':
                this.responses[questionId] = {
                    type: type,
                    text: element.value.trim()
                };
                break;
        }

        console.log('📝 Respuesta capturada:', questionId, this.responses[questionId]);
        
        // Actualizar progreso cada vez que se responde una pregunta
        this.updateProgress();
    }

    validateCurrentGroup() {
        const currentGroupElement = document.getElementById(`group-${this.currentGroup}`);
        if (!currentGroupElement) return false;

        const requiredInputs = currentGroupElement.querySelectorAll('input[required], textarea[required]');
        let isValid = true;

        requiredInputs.forEach(input => {
            const questionId = input.getAttribute('data-question');
            const type = input.getAttribute('data-type');

            if (type === 'single') {
                // Para radio buttons, verificar si alguno está seleccionado
                const radioGroup = currentGroupElement.querySelectorAll(`input[data-question="${questionId}"]`);
                const isChecked = Array.from(radioGroup).some(radio => radio.checked);
                if (!isChecked) isValid = false;
            } else if (type === 'multiple') {
                // Para checkboxes, verificar si al menos uno está seleccionado
                const checkboxGroup = currentGroupElement.querySelectorAll(`input[data-question="${questionId}"]`);
                const isChecked = Array.from(checkboxGroup).some(checkbox => checkbox.checked);
                if (!isChecked) isValid = false;
            } else if (type === 'text' || type === 'email') {
                // Para text/email, verificar si hay contenido
                if (!input.value.trim()) isValid = false;
            }
        });

        // Habilitar/deshabilitar botón Next
        const nextBtn = currentGroupElement.querySelector('#nextBtn, #showContactBtn');
        if (nextBtn) {
            nextBtn.disabled = !isValid;
            if (isValid) {
                nextBtn.classList.remove('disabled');
            } else {
                nextBtn.classList.add('disabled');
            }
        }

        return isValid;
    }

    nextGroup() {
        if (!this.validateCurrentGroup()) {
            this.showValidationMessage('Por favor complete todas las preguntas requeridas antes de continuar.');
            return;
        }

        if (this.currentGroup < this.totalGroups) {
            this.hideGroup(this.currentGroup);
            this.currentGroup++;
            this.showGroup(this.currentGroup);
            this.updateProgress();
        }
    }

    prevGroup() {
        if (this.currentGroup > 1) {
            this.hideGroup(this.currentGroup);
            this.currentGroup--;
            this.showGroup(this.currentGroup);
            this.updateProgress();
        }
    }

    showContactForm() {
        if (!this.validateCurrentGroup()) {
            this.showValidationMessage('Por favor complete todas las preguntas requeridas antes de continuar.');
            return;
        }

        // Ocultar último grupo de preguntas
        this.hideGroup(this.currentGroup);
        
        // Mostrar formulario de contacto
        const contactGroup = document.getElementById('contact-group');
        if (contactGroup) {
            contactGroup.style.display = 'block';
            
            // Scroll hacia arriba para mostrar el título
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        }

        // Actualizar progress a 90% (casi terminado)
        this.updateProgress(90);
    }

    backToSurvey() {
        // Ocultar formulario de contacto
        const contactGroup = document.getElementById('contact-group');
        if (contactGroup) {
            contactGroup.style.display = 'none';
        }

        // Mostrar último grupo de preguntas
        this.showGroup(this.currentGroup);
        this.updateProgress();
    }

    hideGroup(groupNumber) {
        const group = document.getElementById(`group-${groupNumber}`);
        if (group) {
            group.style.display = 'none';
        }
    }

    showGroup(groupNumber) {
        const group = document.getElementById(`group-${groupNumber}`);
        if (group) {
            group.style.display = 'block';
            
            // Scroll hacia arriba para mostrar el título del survey
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
            
            // Revalidar el grupo actual después del scroll
            setTimeout(() => {
                this.validateCurrentGroup();
            }, 500); // Esperar un poco más para que termine el scroll
        }
    }

    updateProgress(customPercent = null) {
        let percentage;
        
        if (customPercent !== null) {
            percentage = customPercent;
        } else {
            // Calcular progreso basado en preguntas respondidas
            const answeredQuestions = Object.keys(this.responses).length;
            percentage = Math.round((answeredQuestions / this.totalQuestions) * 85); // 85% máximo para las preguntas
        }

        const progressBar = document.querySelector('#surveyProgress');
        const progressText = document.querySelector('.progress-text');
        const currentStep = document.querySelector('.current-step');

        if (progressBar) {
            progressBar.style.width = `${percentage}%`;
        }

        if (progressText) {
            progressText.textContent = `${percentage}%`;
        }

        if (currentStep && customPercent === null) {
            currentStep.textContent = `Paso ${this.currentGroup} de ${this.totalGroups}`;
        } else if (currentStep && customPercent === 90) {
            currentStep.textContent = 'Información de contacto';
        } else if (currentStep && customPercent === 100) {
            currentStep.textContent = '¡Completado!';
        }
        
        // También actualizar la barra fija si existe
        const fixedCurrentStep = document.querySelector('.progress-info-fixed .current-step');
        if (fixedCurrentStep) {
            if (customPercent === null) {
                fixedCurrentStep.textContent = `Paso ${this.currentGroup} de ${this.totalGroups}`;
            } else if (customPercent === 90) {
                fixedCurrentStep.textContent = 'Información de contacto';
            } else if (customPercent === 100) {
                fixedCurrentStep.textContent = '¡Completado!';
            }
        }
    }

    showValidationMessage(message) {
        // Crear notificación temporal
        const notification = document.createElement('div');
        notification.className = 'alert alert-warning alert-dismissible fade show';
        notification.style.cssText = `
            position: fixed;
            top: 120px;
            right: 20px;
            z-index: 1050;
            min-width: 350px;
            box-shadow: 0 8px 25px rgba(245, 158, 11, 0.3);
        `;
        notification.innerHTML = `
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${message}
            <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        `;

        document.body.appendChild(notification);

        // Auto remove después de 5 segundos
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    async submitSurvey() {
        // Validar datos del prospect
        const prospectName = document.getElementById('prospectName').value.trim();
        const prospectCompany = document.getElementById('prospectCompany').value.trim();
        const prospectEmail = document.getElementById('prospectEmail').value.trim();

        if (!prospectName || !prospectCompany || !prospectEmail) {
            this.showValidationMessage('Por favor complete todos los campos del formulario.');
            return;
        }

        // Validar email básico
        if (!this.validateEmail(prospectEmail)) {
            this.showValidationMessage('Por favor ingrese un email válido.');
            return;
        }

        // Preparar datos para envío
        const submitData = {
            responses: this.responses,
            prospect: {
                nombre: prospectName,
                empresa: prospectCompany,
                email: prospectEmail
            }
        };

        console.log('📤 Enviando survey:', submitData);

        // Mostrar loading en botón
        const submitBtn = document.getElementById('submitSurveyBtn');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Enviando...';
        submitBtn.disabled = true;

        try {
            const response = await fetch(`/survey/${this.surveyCode}/submit/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: JSON.stringify(submitData)
            });

            const result = await response.json();

            if (result.success) {
                console.log('✅ Survey enviado exitosamente');
                this.showThankYouMessage();
            } else {
                console.error('❌ Error del servidor:', result.message);
                this.showValidationMessage(result.message || 'Error procesando su solicitud.');
            }

        } catch (error) {
            console.error('❌ Error de red:', error);
            this.showValidationMessage('Error de conexión. Por favor intente nuevamente.');
        } finally {
            // Restaurar botón
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    showThankYouMessage() {
        // Ocultar formulario de contacto
        const contactGroup = document.getElementById('contact-group');
        if (contactGroup) {
            contactGroup.style.display = 'none';
        }

        // Mostrar mensaje de agradecimiento
        const thankYouMessage = document.getElementById('thankYouMessage');
        if (thankYouMessage) {
            thankYouMessage.style.display = 'block';
            
            // Scroll hacia arriba para mostrar el mensaje completo
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        }

        // Progress a 100%
        this.updateProgress(100);
    }

    validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    handleSensitiveDataLogic(changedElement) {
        const questionId = changedElement.getAttribute('data-question');
        const allCheckboxes = document.querySelectorAll(`input[data-question="${questionId}"][type="checkbox"]`);
        
        // Buscar la opción "No manejamos información sensible" (la que tiene valor más alto)
        let noSensitiveDataOption = null;
        let maxOptionId = 0;
        
        allCheckboxes.forEach(checkbox => {
            const optionId = parseInt(checkbox.value);
            if (optionId > maxOptionId) {
                maxOptionId = optionId;
                noSensitiveDataOption = checkbox;
            }
        });
        
        if (noSensitiveDataOption && changedElement === noSensitiveDataOption) {
            // Si seleccionó "No manejamos información sensible", deseleccionar todos los demás
            if (changedElement.checked) {
                allCheckboxes.forEach(checkbox => {
                    if (checkbox !== noSensitiveDataOption) {
                        checkbox.checked = false;
                    }
                });
            }
        } else {
            // Si seleccionó cualquier otro tipo de dato, deseleccionar "No manejamos información sensible"
            if (changedElement.checked && noSensitiveDataOption) {
                noSensitiveDataOption.checked = false;
            }
        }
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 Inicializando SCG Survey...');
    window.scgSurvey = new SCGSurvey();
});