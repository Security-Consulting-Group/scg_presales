/**
 * Dashboard JavaScript functionality
 */

class Dashboard {
    constructor() {
        this.autoRefreshInterval = null;
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.setupDashboard();
            this.setupAutoRefresh();
        });
    }

    setupDashboard() {
        console.log('📊 Dashboard cargado');
        
        // Dashboard-specific initialization can go here
        this.initializeWidgets();
        this.setupInteractiveElements();
    }

    initializeWidgets() {
        // Initialize any dashboard widgets
        const statCards = document.querySelectorAll('.stat-card');
        statCards.forEach(card => {
            card.addEventListener('click', this.handleStatCardClick.bind(this));
        });
    }

    setupInteractiveElements() {
        // Add any interactive functionality
        const quickActionBtns = document.querySelectorAll('.admin-card .btn');
        quickActionBtns.forEach(btn => {
            if (!btn.disabled) {
                btn.addEventListener('click', this.handleQuickActionClick.bind(this));
            }
        });
    }

    handleStatCardClick(event) {
        const card = event.currentTarget;
        const label = card.querySelector('.stat-card-label')?.textContent;
        console.log('📈 Stat card clicked:', label);
        
        // Add visual feedback
        card.style.transform = 'scale(0.98)';
        setTimeout(() => {
            card.style.transform = 'scale(1)';
        }, 150);
    }

    handleQuickActionClick(event) {
        const btn = event.currentTarget;
        const action = btn.textContent.trim();
        console.log('⚡ Quick action clicked:', action);
    }

    setupAutoRefresh() {
        // Auto-refresh every 5 minutes
        this.autoRefreshInterval = setInterval(() => {
            this.refreshStats();
        }, 300000); // 5 minutes
    }

    refreshStats() {
        // Only refresh stats, not the whole page
        console.log('🔄 Auto-refresh stats (placeholder)');
        
        // Future implementation: AJAX call to refresh dashboard stats
        // fetch('/admin-panel/dashboard/stats/')
        //     .then(response => response.json())
        //     .then(data => this.updateStats(data))
        //     .catch(error => console.error('Error refreshing stats:', error));
    }

    updateStats(data) {
        // Update stat cards with new data
        console.log('📊 Updating dashboard stats:', data);
    }

    destroy() {
        // Cleanup when leaving dashboard
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
    }
}

// Initialize dashboard
const dashboard = new Dashboard();

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    dashboard.destroy();
}); 