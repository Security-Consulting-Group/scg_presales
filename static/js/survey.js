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
        this.exclusiveOptions = this.getExclusiveOptions();
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.validateCurrentGroup();
    }

    getSurveyCode() {
        const pathParts = window.location.pathname.split('/');
        return pathParts[pathParts.indexOf('survey') + 1];
    }

    getCSRFToken() {
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');
        return csrfMeta ? csrfMeta.getAttribute('content') : '';
    }

    getExclusiveOptions() {
        const exclusiveOptions = {};
        
        // Encontrar todas las opciones marcadas como exclusivas
        document.querySelectorAll('input[data-exclusive="true"]').forEach(input => {
            const questionId = input.getAttribute('data-question');
            const optionId = input.value;
            
            if (!exclusiveOptions[questionId]) {
                exclusiveOptions[questionId] = [];
            }
            exclusiveOptions[questionId].push(optionId);
        });
        
        return exclusiveOptions;
    }

    setupEventListeners() {
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

        document.addEventListener('change', (e) => {
            if (e.target.hasAttribute('data-question')) {
                this.captureResponse(e.target);
                
                if (e.target.getAttribute('data-type') === 'multiple') {
                    this.handleExclusiveLogic(e.target);
                }
                
                this.validateCurrentGroup();
            }
        });

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

        this.updateProgress();
    }

    handleExclusiveLogic(changedElement) {
        const questionId = changedElement.getAttribute('data-question');
        const changedOptionId = changedElement.value;
        const isExclusive = changedElement.getAttribute('data-exclusive') === 'true';
        
        // Obtener todas las opciones de esta pregunta
        const allCheckboxes = document.querySelectorAll(`input[data-question="${questionId}"][type="checkbox"]`);
        
        if (isExclusive && changedElement.checked) {
            // Si se seleccionó una opción exclusiva, deseleccionar todas las demás
            allCheckboxes.forEach(checkbox => {
                if (checkbox !== changedElement) {
                    checkbox.checked = false;
                }
            });
        } else if (!isExclusive && changedElement.checked) {
            // Si se seleccionó una opción no exclusiva, deseleccionar todas las exclusivas
            allCheckboxes.forEach(checkbox => {
                if (checkbox.getAttribute('data-exclusive') === 'true') {
                    checkbox.checked = false;
                }
            });
        }
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
                const radioGroup = currentGroupElement.querySelectorAll(`input[data-question="${questionId}"]`);
                const isChecked = Array.from(radioGroup).some(radio => radio.checked);
                if (!isChecked) isValid = false;
            } else if (type === 'multiple') {
                const checkboxGroup = currentGroupElement.querySelectorAll(`input[data-question="${questionId}"]`);
                const isChecked = Array.from(checkboxGroup).some(checkbox => checkbox.checked);
                if (!isChecked) isValid = false;
            } else if (type === 'text' || type === 'email') {
                if (!input.value.trim()) isValid = false;
            }
        });

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

        this.hideGroup(this.currentGroup);
        
        const contactGroup = document.getElementById('contact-group');
        if (contactGroup) {
            contactGroup.style.display = 'block';
            
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        }

        this.updateProgress(90);
    }

    backToSurvey() {
        const contactGroup = document.getElementById('contact-group');
        if (contactGroup) {
            contactGroup.style.display = 'none';
        }

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
            
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
            
            setTimeout(() => {
                this.validateCurrentGroup();
            }, 500);
        }
    }

    updateProgress(customPercent = null) {
        let percentage;
        
        if (customPercent !== null) {
            percentage = customPercent;
        } else {
            const answeredQuestions = Object.keys(this.responses).length;
            percentage = Math.round((answeredQuestions / this.totalQuestions) * 85);
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
        
        const closeButton = document.createElement('button');
        closeButton.type = 'button';
        closeButton.className = 'btn-close';
        closeButton.onclick = () => notification.remove();
        
        const icon = document.createElement('i');
        icon.className = 'fas fa-exclamation-triangle me-2';
        
        notification.appendChild(icon);
        notification.appendChild(document.createTextNode(message));
        notification.appendChild(closeButton);

        document.body.appendChild(notification);

        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    async submitSurvey() {
        const prospectName = document.getElementById('prospectName').value.trim();
        const prospectCompany = document.getElementById('prospectCompany').value.trim();
        const prospectEmail = document.getElementById('prospectEmail').value.trim();

        if (!prospectName || !prospectCompany || !prospectEmail) {
            this.showValidationMessage('Por favor complete todos los campos del formulario.');
            return;
        }

        if (!this.validateEmail(prospectEmail)) {
            this.showValidationMessage('Por favor ingrese un email válido.');
            return;
        }

        const submitData = {
            responses: this.responses,
            prospect: {
                nombre: prospectName,
                empresa: prospectCompany,
                email: prospectEmail
            }
        };

        const submitBtn = document.getElementById('submitSurveyBtn');
        const originalText = submitBtn.innerHTML;
        const spinner = document.createElement('i');
        spinner.className = 'fas fa-spinner fa-spin me-2';
        
        submitBtn.innerHTML = '';
        submitBtn.appendChild(spinner);
        submitBtn.appendChild(document.createTextNode('Enviando...'));
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
                this.showThankYouMessage();
            } else {
                this.showValidationMessage(result.message || 'Error procesando su solicitud.');
            }

        } catch (error) {
            this.showValidationMessage('Error de conexión. Por favor intente nuevamente.');
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    showThankYouMessage() {
        const contactGroup = document.getElementById('contact-group');
        if (contactGroup) {
            contactGroup.style.display = 'none';
        }

        const thankYouMessage = document.getElementById('thankYouMessage');
        if (thankYouMessage) {
            thankYouMessage.style.display = 'block';
            
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        }

        this.updateProgress(100);
    }

    validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    window.scgSurvey = new SCGSurvey();
});