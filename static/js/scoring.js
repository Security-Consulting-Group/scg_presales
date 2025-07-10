/**
 * Scoring System JavaScript functionality
 */

class ScgScoring {
    constructor() {
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.setupScoringSystem();
            this.initializeCharts();
            this.setupModalHandlers();
        });
    }

    setupScoringSystem() {
        // Initialize tooltips
        if (typeof bootstrap !== 'undefined') {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    }

    initializeCharts() {
        // Initialize any charts or visual elements
        this.initializeScoreCircles();
        this.initializeProgressBars();
    }

    initializeScoreCircles() {
        // Animate score circles if present
        const scoreCircles = document.querySelectorAll('.score-circle');
        scoreCircles.forEach(circle => {
            this.animateScoreCircle(circle);
        });
    }

    initializeProgressBars() {
        // Animate progress bars
        const progressBars = document.querySelectorAll('.progress-bar');
        progressBars.forEach((bar, index) => {
            setTimeout(() => {
                const width = bar.getAttribute('aria-valuenow');
                if (width) {
                    bar.style.width = width + '%';
                }
            }, index * 200);
        });
    }

    animateScoreCircle(circle) {
        // Add animation to score circles
        if (circle) {
            circle.style.opacity = '0';
            circle.style.transform = 'scale(0.8)';
            
            setTimeout(() => {
                circle.style.transition = 'all 0.5s ease';
                circle.style.opacity = '1';
                circle.style.transform = 'scale(1)';
            }, 100);
        }
    }

    setupModalHandlers() {
        // Setup modal event handlers
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.addEventListener('shown.bs.modal', () => {
                const firstInput = modal.querySelector('input, select, textarea');
                if (firstInput) {
                    firstInput.focus();
                }
            });
        });
    }

    // Recalculate scores functionality
    async recalculateScores(surveyId, force = false) {
        try {
            const action = force ? 'recalculate_all' : 'recalculate_single';
            
            // Show loading notification
            window.scgAdmin.showNotification('Recalculando scores...', 'info');
            
            // This would be implemented when the backend endpoint is ready
            // For now, just show a placeholder message
            setTimeout(() => {
                window.scgAdmin.showNotification('Funcionalidad de recálculo en desarrollo', 'info');
            }, 1000);
            
        } catch {
            window.scgAdmin.showNotification('Error al recalcular scores', 'error');
        }
    }

    // Export scores functionality
    exportScores(filters = {}) {
        window.scgAdmin.showNotification('Función de exportación en desarrollo', 'info');
    }

    // PDF generation tracking
    trackPDFGeneration(action, scoreResultId) {
        if (action === 'download') {
            setTimeout(() => {
                this.showPDFNotification('success', 'Reporte PDF descargado exitosamente');
            }, 1000);
        } else if (action === 'preview') {
            this.showPDFNotification('info', 'Abriendo vista previa del reporte PDF...');
        }
    }

    showPDFNotification(type, message) {
        const notification = document.getElementById('pdf-notifications');
        const messageSpan = document.getElementById('pdf-success-message');
        
        if (notification && messageSpan) {
            messageSpan.textContent = message;
            notification.style.display = 'block';
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                notification.style.display = 'none';
            }, 5000);
        } else {
            // Fallback to admin notification
            window.scgAdmin.showNotification(message, type);
        }
    }
}

// Risk Configuration Management
class RiskConfigManager {
    constructor() {
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.setupRiskConfigSystem();
            this.setupPreviewUpdates();
        });
    }

    setupRiskConfigSystem() {
    }

    setupPreviewUpdates() {
        // Setup real-time preview updates for risk configuration forms
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

    exportRiskConfig(config) {
        const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `risk_config_${config.survey_code}_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        window.scgAdmin.showNotification('Configuración exportada', 'success');
    }

    async createQuickConfig(surveyId, surveyTitle) {
        if (!confirm(`¿Crear configuración de riesgo con valores por defecto para "${surveyTitle}"?\n\nRangos:\n• Crítico: 0-20%\n• Alto: 21-40%\n• Moderado: 41-60%\n• Bueno: 61-80%\n• Excelente: 81-100%`)) {
            return;
        }

        try {
            // This would be implemented when the backend endpoint is ready
            window.scgAdmin.showNotification('Función de creación rápida en desarrollo', 'info');
        } catch {
            window.scgAdmin.showNotification('Error al crear configuración', 'error');
        }
    }
}

// Initialize global instances
window.scgScoring = new ScgScoring();

// Global functions for templates
window.exportScores = function() {
    const form = document.getElementById('filterForm');
    if (!form) return;
    
    const formData = new FormData(form);
    const params = new URLSearchParams(formData);
    
    const exportUrlElement = document.querySelector('[data-export-url]');
    const exportUrl = exportUrlElement ? exportUrlElement.getAttribute('data-export-url') : '/admin-panel/scores/export/';
    
    window.location.href = exportUrl + '?' + params.toString();
};

window.recalculateScore = function(surveyId, prospectName) {
    if (confirm(`¿Recalcular el score para ${prospectName}?`)) {
        window.scgScoring.recalculateScores(surveyId, false);
    }
};

window.executeRecalculation = function() {
    const form = document.getElementById('recalculateForm');
    if (!form) return;
    
    const formData = new FormData(form);
    
    if (!formData.get('survey_id')) {
        alert('Por favor selecciona un survey');
        return;
    }
    
    const surveyId = formData.get('survey_id');
    const force = formData.get('force') === 'on';
    
    const modal = bootstrap.Modal.getInstance(document.getElementById('recalculateModal'));
    if (modal) {
        modal.hide();
    }
    
    window.scgScoring.recalculateScores(surveyId, force);
};
window.riskConfigManager = new RiskConfigManager();

// Global functions for backward compatibility
window.recalculateThisScore = function(surveyId, prospectName) {
    if (confirm(`¿Recalcular el score para ${prospectName}?`)) {
        window.scgScoring.recalculateScores(surveyId, false);
    }
};

window.exportScoreDetail = function() {
    window.scgAdmin.showNotification('Función de exportación en desarrollo', 'info');
};

window.trackPDFGeneration = function(action, scoreResultId) {
    window.scgScoring.trackPDFGeneration(action, scoreResultId);
};

window.setDefaults = function() {
    window.riskConfigManager.setDefaults();
};

window.createQuickConfig = function(surveyId, surveyTitle) {
    window.riskConfigManager.createQuickConfig(surveyId, surveyTitle);
};