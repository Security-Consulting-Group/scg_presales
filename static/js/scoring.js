// ====================================
// SCG SCORING MODULE JAVASCRIPT
// ====================================

class SCGScoring {
    constructor() {
        this.init();
    }

    init() {
        console.log('🎯 Inicializando SCG Scoring...');
        
        // Initialize components
        this.initScoreCircles();
        this.initTableInteractions();
        this.initFilters();
        this.initTooltips();
        this.initExportFunctionality();
        
        console.log('✅ Scoring inicializado correctamente!');
    }

    // ====================================
    // SCORE CIRCLE ANIMATIONS
    // ====================================

    initScoreCircles() {
        const scoreCircles = document.querySelectorAll('.score-circle');
        
        scoreCircles.forEach(circle => {
            this.animateScoreCircle(circle);
        });
    }

    animateScoreCircle(circle) {
        const scoreText = circle.querySelector('.score-percentage');
        if (!scoreText) return;

        const scoreValue = parseInt(scoreText.textContent);
        const angle = (scoreValue / 100) * 360;

        // Set CSS custom property for the conic gradient
        circle.style.setProperty('--score-angle', `${angle}deg`);

        // Animate the angle from 0 to target
        let currentAngle = 0;
        const increment = angle / 60; // 60 frames for smooth animation
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const animateScore = () => {
                        currentAngle += increment;
                        if (currentAngle <= angle) {
                            circle.style.setProperty('--score-angle', `${currentAngle}deg`);
                            requestAnimationFrame(animateScore);
                        } else {
                            circle.style.setProperty('--score-angle', `${angle}deg`);
                        }
                    };
                    
                    // Start animation after a small delay
                    setTimeout(animateScore, 500);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });

        observer.observe(circle);
    }

    // ====================================
    // TABLE INTERACTIONS
    // ====================================

    initTableInteractions() {
        // Handle row clicks for navigation
        const scoreRows = document.querySelectorAll('.score-row');
        
        scoreRows.forEach(row => {
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

        // Add hover effects to progress bars
        this.initProgressBarAnimations();
    }

    initProgressBarAnimations() {
        const progressBars = document.querySelectorAll('.progress-bar');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const progressBar = entry.target;
                    const targetWidth = progressBar.style.width;
                    
                    // Reset width and animate
                    progressBar.style.width = '0%';
                    progressBar.style.transition = 'width 1s ease-out';
                    
                    setTimeout(() => {
                        progressBar.style.width = targetWidth;
                    }, 100);
                    
                    observer.unobserve(progressBar);
                }
            });
        }, { threshold: 0.3 });

        progressBars.forEach(bar => observer.observe(bar));
    }

    // ====================================
    // FILTERS AND SEARCH
    // ====================================

    initFilters() {
        const filterForm = document.getElementById('filterForm');
        const clearFiltersBtn = document.getElementById('clearFilters');

        if (filterForm) {
            // Auto-submit on filter change
            const filterInputs = filterForm.querySelectorAll('select[name="risk_level"], select[name="survey"]');
            filterInputs.forEach(input => {
                input.addEventListener('change', () => {
                    this.applyFilters();
                });
            });

            // Handle score range inputs with debounce
            const scoreInputs = filterForm.querySelectorAll('input[name="min_score"], input[name="max_score"]');
            scoreInputs.forEach(input => {
                let timeout;
                input.addEventListener('input', () => {
                    clearTimeout(timeout);
                    timeout = setTimeout(() => {
                        this.applyFilters();
                    }, 800);
                });
            });

            // Handle date inputs
            const dateInputs = filterForm.querySelectorAll('input[type="date"]');
            dateInputs.forEach(input => {
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

        // Initialize search with debounce
        this.initSearch();
    }

    initSearch() {
        const searchInput = document.querySelector('input[name="search"]');
        
        if (searchInput) {
            let searchTimeout;

            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                
                // Debounce search to avoid too many requests
                searchTimeout = setTimeout(() => {
                    this.applyFilters();
                }, 600);
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
            // Add loading indicator
            this.showFilterLoading(true);
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
            this.showFilterLoading(true);
            filterForm.submit();
        }
    }

    showFilterLoading(show) {
        const filterForm = document.getElementById('filterForm');
        if (!filterForm) return;

        if (show) {
            // Add loading overlay to filters
            if (!filterForm.querySelector('.filter-loading')) {
                const loading = document.createElement('div');
                loading.className = 'filter-loading';
                loading.innerHTML = `
                    <div class="d-flex align-items-center justify-content-center">
                        <div class="loading-spinner me-2"></div>
                        <span>Aplicando filtros...</span>
                    </div>
                `;
                loading.style.cssText = `
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(255, 255, 255, 0.9);
                    border-radius: 8px;
                    z-index: 10;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                `;
                
                filterForm.style.position = 'relative';
                filterForm.appendChild(loading);
            }
        } else {
            const loading = filterForm.querySelector('.filter-loading');
            if (loading) {
                loading.remove();
            }
        }
    }

    // ====================================
    // TOOLTIPS AND UI ENHANCEMENTS
    // ====================================

    initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });

        // Initialize risk level popovers if any
        this.initRiskLevelPopovers();
    }

    initRiskLevelPopovers() {
        const riskBadges = document.querySelectorAll('.risk-level-badge, .risk-level-badge-large');
        
        riskBadges.forEach(badge => {
            if (!badge.hasAttribute('data-bs-toggle')) {
                badge.setAttribute('data-bs-toggle', 'popover');
                badge.setAttribute('data-bs-trigger', 'hover');
                badge.setAttribute('data-bs-content', this.getRiskLevelDescription(badge));
                
                new bootstrap.Popover(badge);
            }
        });
    }

    getRiskLevelDescription(badge) {
        const riskLevel = badge.textContent.trim().toLowerCase();
        const descriptions = {
            'estado crítico': 'Su empresa presenta vulnerabilidades críticas que requieren atención inmediata.',
            'riesgos significativos': 'Existen riesgos significativos que deben ser abordados con urgencia.',
            'vulnerabilidades moderadas': 'Su empresa tiene una base sólida pero presenta vulnerabilidades moderadas.',
            'buena base': 'Tiene una buena base de seguridad que puede ser optimizada estratégicamente.',
            'postura sólida': 'Su empresa mantiene una postura de seguridad sólida y madura.'
        };
        
        return descriptions[riskLevel] || 'Información del nivel de riesgo';
    }

    // ====================================
    // SCORE ACTIONS
    // ====================================

    async recalculateScores(surveyId, force = false) {
        if (!surveyId) {
            this.showNotification('ID del survey es requerido', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('survey_id', surveyId);
        formData.append('force', force ? 'true' : 'false');

        try {
            this.showNotification('Iniciando recálculo de scores...', 'info');

            const response = await fetch('/admin-panel/ajax/scoring/recalculate/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification(data.message, 'success');
                
                // Reload page after 2 seconds to show updated scores
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            } else {
                this.showNotification(data.message || 'Error en el recálculo', 'error');
            }

        } catch (error) {
            console.error('Error:', error);
            this.showNotification('Error de conexión durante el recálculo', 'error');
        }
    }

    async recalculateIndividualScore(scoreId, prospectName) {
        const confirmMessage = `¿Recalcular el score para ${prospectName}?`;
        
        if (!confirm(confirmMessage)) {
            return;
        }

        try {
            this.showNotification(`Recalculando score para ${prospectName}...`, 'info');

            // Implementation would depend on having an endpoint for individual score recalculation
            // For now, we'll use the bulk recalculation
            
            this.showNotification('Función de recálculo individual en desarrollo', 'info');

        } catch (error) {
            console.error('Error:', error);
            this.showNotification('Error recalculando el score individual', 'error');
        }
    }

    // ====================================
    // EXPORT FUNCTIONALITY
    // ====================================

    initExportFunctionality() {
        // Add export button listeners if they exist
        const exportBtn = document.querySelector('[onclick="exportScores()"]');
        if (exportBtn) {
            exportBtn.removeAttribute('onclick');
            exportBtn.addEventListener('click', () => {
                this.exportScores();
            });
        }
    }

    exportScores() {
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
        
        // Create export URL
        const exportUrl = `/admin-panel/scoring/results/export/?${params.toString()}`;
        
        // Create temporary link and trigger download
        const link = document.createElement('a');
        link.href = exportUrl;
        link.download = `scores_export_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        this.showNotification('Exportación iniciada', 'success');
    }

    exportScoreDetail(scoreId) {
        // Export individual score detail
        const exportUrl = `/admin-panel/scoring/results/${scoreId}/export/`;
        
        const link = document.createElement('a');
        link.href = exportUrl;
        link.download = `score_detail_${scoreId}_${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        this.showNotification('Exportando detalle del score...', 'success');
    }

    // ====================================
    // ANALYTICS AND INSIGHTS
    // ====================================

    initScoreAnalytics() {
        // Calculate and display score distribution
        this.calculateScoreDistribution();
        
        // Add trend indicators
        this.addScoreTrendIndicators();
    }

    calculateScoreDistribution() {
        const scoreRows = document.querySelectorAll('.score-row');
        const distribution = {
            excellent: 0,
            good: 0,
            moderate: 0,
            high: 0,
            critical: 0
        };

        scoreRows.forEach(row => {
            const riskBadge = row.querySelector('.risk-level-badge');
            if (riskBadge) {
                const riskLevel = riskBadge.classList.toString();
                if (riskLevel.includes('excellent')) distribution.excellent++;
                else if (riskLevel.includes('good')) distribution.good++;
                else if (riskLevel.includes('moderate')) distribution.moderate++;
                else if (riskLevel.includes('high')) distribution.high++;
                else if (riskLevel.includes('critical')) distribution.critical++;
            }
        });

        // Display distribution if we have a container for it
        this.displayScoreDistribution(distribution);
    }

    displayScoreDistribution(distribution) {
        const container = document.querySelector('.score-distribution-chart');
        if (!container) return;

        const total = Object.values(distribution).reduce((sum, count) => sum + count, 0);
        if (total === 0) return;

        // Create simple bar chart
        const chart = document.createElement('div');
        chart.className = 'distribution-bars';
        
        Object.entries(distribution).forEach(([level, count]) => {
            const percentage = (count / total) * 100;
            const bar = document.createElement('div');
            bar.className = `distribution-bar risk-${level}`;
            bar.style.width = `${percentage}%`;
            bar.title = `${level}: ${count} (${percentage.toFixed(1)}%)`;
            chart.appendChild(bar);
        });

        container.appendChild(chart);
    }

    addScoreTrendIndicators() {
        // Add trend arrows based on score history
        const scoreRows = document.querySelectorAll('.score-row');
        
        scoreRows.forEach(row => {
            const scoreDisplay = row.querySelector('.score-display');
            if (scoreDisplay && !scoreDisplay.querySelector('.trend-indicator')) {
                // This would require historical data to show trends
                // For now, we'll add a placeholder for future implementation
                const trendIndicator = document.createElement('span');
                trendIndicator.className = 'trend-indicator';
                trendIndicator.innerHTML = '<i class="fas fa-minus text-muted" title="Sin datos históricos"></i>';
                scoreDisplay.appendChild(trendIndicator);
            }
        });
    }

    // ====================================
    // KEYBOARD SHORTCUTS
    // ====================================

    initKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + F to focus search
            if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
                e.preventDefault();
                const searchInput = document.querySelector('input[name="search"]');
                if (searchInput) {
                    searchInput.focus();
                }
            }
            
            // Escape to clear search
            if (e.key === 'Escape') {
                const searchInput = document.querySelector('input[name="search"]');
                if (searchInput && searchInput === document.activeElement) {
                    searchInput.value = '';
                    this.applyFilters();
                }
            }

            // Ctrl/Cmd + E to export
            if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
                e.preventDefault();
                this.exportScores();
            }
        });
    }

    // ====================================
    // UTILITY FUNCTIONS
    // ====================================

    getCSRFToken() {
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');
        if (csrfMeta) {
            return csrfMeta.getAttribute('content');
        }

        // Fallback to form token
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfInput) {
            return csrfInput.value;
        }

        // Last resort: cookie
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    showNotification(message, type = 'info') {
        // Use global admin notification system if available
        if (window.scgAdmin && window.scgAdmin.showNotification) {
            window.scgAdmin.showNotification(message, type);
            return;
        }

        // Fallback notification system
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1060;
            min-width: 300px;
            max-width: 500px;
            box-shadow: 0 8px 25px rgba(0, 45, 116, 0.3);
        `;
        
        const icon = type === 'success' ? 'check-circle' : 
                    type === 'error' ? 'exclamation-circle' : 'info-circle';
        
        notification.innerHTML = `
            <i class="fas fa-${icon} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
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

    formatNumber(number) {
        return new Intl.NumberFormat('es-ES').format(number);
    }

    formatPercentage(number) {
        return `${parseFloat(number).toFixed(1)}%`;
    }

    // ====================================
    // RISK LEVEL UTILITIES
    // ====================================

    getRiskLevelColor(riskLevel) {
        const colors = {
            'EXCELLENT': '#28a745',
            'GOOD': '#20c997',
            'MODERATE': '#ffc107',
            'HIGH': '#fd7e14',
            'CRITICAL': '#dc3545'
        };
        return colors[riskLevel] || '#6c757d';
    }

    getRiskLevelIcon(riskLevel) {
        const icons = {
            'EXCELLENT': 'fas fa-shield-alt',
            'GOOD': 'fas fa-check-shield',
            'MODERATE': 'fas fa-exclamation-triangle',
            'HIGH': 'fas fa-exclamation-circle',
            'CRITICAL': 'fas fa-times-circle'
        };
        return icons[riskLevel] || 'fas fa-question-circle';
    }
}

// ====================================
// GLOBAL FUNCTIONS
// ====================================

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.scgScoring = new SCGScoring();
    
    // Initialize keyboard shortcuts
    window.scgScoring.initKeyboardShortcuts();
    
    // Initialize analytics if on list page
    if (document.querySelector('.score-row')) {
        window.scgScoring.initScoreAnalytics();
    }
});

// Global export function for backward compatibility
function exportScores() {
    if (window.scgScoring) {
        window.scgScoring.exportScores();
    }
}

// Global recalculate function
function recalculateScore(surveyId, prospectName) {
    if (window.scgScoring) {
        window.scgScoring.recalculateIndividualScore(null, prospectName);
    }
}

// Make functions available globally
window.SCGScoring = {
    exportData: function() {
        if (window.scgScoring) {
            window.scgScoring.exportScores();
        }
    },
    
    recalculateScores: function(surveyId, force) {
        if (window.scgScoring) {
            window.scgScoring.recalculateScores(surveyId, force);
        }
    },
    
    showNotification: function(message, type) {
        if (window.scgScoring) {
            window.scgScoring.showNotification(message, type);
        }
    }
};

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript Error in Scoring:', e.error);
});