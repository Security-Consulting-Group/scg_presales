/**
 * Risk Configuration JavaScript functionality
 */

class RiskConfigPage {
    constructor() {
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.setupRiskConfigPage();
            this.initializeDataWidths();
            this.setupPreviewForm();
            this.loadRiskConfigData();
            this.setupRowClickHandlers();
        });
    }

    setupRiskConfigPage() {
        console.log('⚙️ Risk config page initialized');
    }

    loadRiskConfigData() {
        const dataElement = document.querySelector('[data-risk-config]');
        if (dataElement) {
            try {
                window.riskConfigData = JSON.parse(dataElement.getAttribute('data-risk-config'));
            } catch (error) {
                console.error('Error parsing risk config data:', error);
            }
        }
    }

    initializeDataWidths() {
        // Apply widths from data attributes to avoid CSS linter errors
        document.querySelectorAll('[data-width]').forEach(element => {
            const width = element.getAttribute('data-width');
            if (width) {
                element.style.width = width + '%';
            }
        });

        document.querySelectorAll('[data-position]').forEach(element => {
            const position = element.getAttribute('data-position');
            if (position) {
                element.style.left = position + '%';
            }
        });

        // Handle calculated widths for mini range bars
        document.querySelectorAll('[data-width-calc]').forEach(element => {
            const calc = element.getAttribute('data-width-calc');
            let width = 0;
            
            switch(calc) {
                case 'high':
                    const high = parseInt(element.getAttribute('data-high')) || 0;
                    const critical = parseInt(element.getAttribute('data-critical')) || 0;
                    width = high - critical;
                    break;
                case 'moderate':
                    const moderate = parseInt(element.getAttribute('data-moderate')) || 0;
                    const highVal = parseInt(element.getAttribute('data-high')) || 0;
                    width = moderate - highVal;
                    break;
                case 'good':
                    const good = parseInt(element.getAttribute('data-good')) || 0;
                    const moderateVal = parseInt(element.getAttribute('data-moderate')) || 0;
                    width = good - moderateVal;
                    break;
                case 'excellent':
                    const goodVal = parseInt(element.getAttribute('data-good')) || 0;
                    width = 100 - goodVal;
                    break;
            }
            
            if (width > 0) {
                element.style.width = width + '%';
            }
        });
    }

    setupPreviewForm() {
        // Setup real-time preview updates for form inputs
        const inputs = ['id_critical_max', 'id_high_max', 'id_moderate_max', 'id_good_max'];
        inputs.forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                input.addEventListener('input', () => this.updatePreview());
            }
        });
        
        // Initial preview update
        setTimeout(() => this.updatePreview(), 100);
    }

    updatePreview() {
        const critical = parseInt(document.getElementById('id_critical_max')?.value) || 0;
        const high = parseInt(document.getElementById('id_high_max')?.value) || 0;
        const moderate = parseInt(document.getElementById('id_moderate_max')?.value) || 0;
        const good = parseInt(document.getElementById('id_good_max')?.value) || 0;
        
        // Validate that values are in ascending order
        if (critical >= high || high >= moderate || moderate >= good || good >= 100) {
            const preview = document.getElementById('rangePreview');
            if (preview) {
                preview.style.display = 'none';
            }
            return;
        }
        
        const preview = document.getElementById('rangePreview');
        if (preview) {
            preview.style.display = 'block';
        }
        
        // Calculate widths
        const criticalWidth = critical;
        const highWidth = high - critical;
        const moderateWidth = moderate - high;
        const goodWidth = good - moderate;
        const excellentWidth = 100 - good;
        
        // Update segment widths
        this.updateSegmentWidth('criticalSegment', criticalWidth);
        this.updateSegmentWidth('highSegment', highWidth);
        this.updateSegmentWidth('moderateSegment', moderateWidth);
        this.updateSegmentWidth('goodSegment', goodWidth);
        this.updateSegmentWidth('excellentSegment', excellentWidth);
        
        // Update range text
        this.updateRangeText('criticalRange', `0% - ${critical}%`);
        this.updateRangeText('highRange', `${critical + 1}% - ${high}%`);
        this.updateRangeText('moderateRange', `${high + 1}% - ${moderate}%`);
        this.updateRangeText('goodRange', `${moderate + 1}% - ${good}%`);
        this.updateRangeText('excellentRange', `${good + 1}% - 100%`);
    }

    updateSegmentWidth(segmentId, width) {
        const segment = document.getElementById(segmentId);
        if (segment) {
            segment.style.width = width + '%';
        }
    }

    updateRangeText(rangeId, text) {
        const range = document.getElementById(rangeId);
        if (range) {
            range.textContent = text;
        }
    }

    setDefaults() {
        const inputs = {
            'id_critical_max': 20,
            'id_high_max': 40,
            'id_moderate_max': 60,
            'id_good_max': 80
        };
        
        Object.entries(inputs).forEach(([id, value]) => {
            const input = document.getElementById(id);
            if (input) {
                input.value = value;
            }
        });
        
        this.updatePreview();
    }

    exportConfig(configData) {
        const config = {
            survey: configData.surveyTitle,
            survey_code: configData.surveyCode,
            critical_max: configData.criticalMax,
            high_max: configData.highMax,
            moderate_max: configData.moderateMax,
            good_max: configData.goodMax,
            created_at: configData.createdAt,
            is_active: configData.isActive
        };
        
        const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `risk_config_${configData.surveyCode}_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        window.scgAdmin.showNotification('Configuración exportada', 'success');
    }

    async createQuickConfigs(selectedSurveyIds, csrfToken) {
        window.scgAdmin.showNotification(`Creando ${selectedSurveyIds.length} configuraciones...`, 'info');
        
        let created = 0;
        let errors = 0;
        
        for (let i = 0; i < selectedSurveyIds.length; i++) {
            try {
                const response = await fetch('/admin-panel/ajax/risk-config/quick-create/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrfToken
                    },
                    body: `survey_id=${selectedSurveyIds[i]}`
                });
                
                const data = await response.json();
                if (data.success) {
                    created++;
                } else {
                    errors++;
                }
            } catch (error) {
                errors++;
            }
        }
        
        if (errors === 0) {
            window.scgAdmin.showNotification(`✅ ${created} configuraciones creadas exitosamente`, 'success');
        } else {
            window.scgAdmin.showNotification(`⚠️ ${created} creadas, ${errors} errores`, 'warning');
        }
        
        setTimeout(() => window.location.reload(), 2000);
    }

    setupRowClickHandlers() {
        // Make config rows clickable
        document.querySelectorAll('.config-row').forEach(row => {
            row.addEventListener('click', function(e) {
                if (!e.target.closest('.action-buttons')) {
                    window.location.href = this.dataset.href;
                }
            });
        });
    }
}

// Initialize the risk config page
window.riskConfigPage = new RiskConfigPage();

// Global functions for templates
window.setDefaults = function() {
    window.riskConfigPage.setDefaults();
};

window.exportRiskConfig = function() {
    if (window.riskConfigData) {
        window.riskConfigPage.exportConfig(window.riskConfigData);
    }
};

window.createQuickConfig = function(surveyId, surveyTitle) {
    if (!confirm(`¿Crear configuración de riesgo con valores por defecto para "${surveyTitle}"?\n\nRangos:\n• Crítico: 0-20%\n• Alto: 21-40%\n• Moderado: 41-60%\n• Bueno: 61-80%\n• Excelente: 81-100%`)) {
        return;
    }

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    if (csrfToken) {
        window.riskConfigPage.createQuickConfigs([surveyId], csrfToken);
    }
};

window.showQuickCreateModal = function() {
    const modal = new bootstrap.Modal(document.getElementById('quickCreateModal'));
    modal.show();
};

window.createMultipleConfigs = function() {
    const selectedSurveys = Array.from(document.querySelectorAll('#quickCreateModal input[type="checkbox"]:checked'))
                                .map(cb => cb.value);
    
    if (selectedSurveys.length === 0) {
        alert('Selecciona al menos un survey');
        return;
    }
    
    const modal = bootstrap.Modal.getInstance(document.getElementById('quickCreateModal'));
    modal.hide();
    
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    if (csrfToken) {
        window.riskConfigPage.createQuickConfigs(selectedSurveys, csrfToken);
    }
};

window.recalculateAllScores = function() {
    if (!window.riskConfigData) {
        console.error('Risk config data not loaded');
        return;
    }
    
    const { surveyTitle, surveyId } = window.riskConfigData;
    if (confirm(`¿Recalcular TODOS los scores para el survey "${surveyTitle}"?`)) {
        window.scgScoring.recalculateScores(surveyId, true);
    }
};

window.duplicateConfig = function() {
    window.scgAdmin.showNotification('Función de duplicación en desarrollo', 'info');
};

window.resetConfiguration = function() {
    if (confirm('¿Restaurar la configuración por defecto?')) {
        window.scgAdmin.showNotification('Función de reset en desarrollo', 'info');
    }
}; 