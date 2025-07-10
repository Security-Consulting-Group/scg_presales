// ====================================
// SCG ADMIN PANEL JAVASCRIPT
// ====================================

class SCGAdmin {
    constructor() {
        this.init();
    }

    init() {
        // Initialize components
        this.initSidebar();
        this.initTables();
        this.initForms();
        this.initAjaxActions();
        this.initTooltips();
    }

    // ====================================
    // SIDEBAR FUNCTIONALITY
    // ====================================

    initSidebar() {
        const sidebarToggle = document.getElementById('sidebarToggle');
        const sidebar = document.querySelector('.admin-sidebar');
        const main = document.querySelector('.admin-main');

        if (sidebarToggle && sidebar) {
            sidebarToggle.addEventListener('click', () => {
                sidebar.classList.toggle('show');
                
                // Close sidebar when clicking outside on mobile
                if (sidebar.classList.contains('show')) {
                    document.addEventListener('click', this.closeSidebarOnOutsideClick.bind(this));
                }
            });
        }

        // Close sidebar on window resize if mobile
        window.addEventListener('resize', () => {
            if (window.innerWidth > 768 && sidebar) {
                sidebar.classList.remove('show');
            }
        });
    }

    closeSidebarOnOutsideClick(event) {
        const sidebar = document.querySelector('.admin-sidebar');
        const sidebarToggle = document.getElementById('sidebarToggle');
        
        if (sidebar && !sidebar.contains(event.target) && !sidebarToggle.contains(event.target)) {
            sidebar.classList.remove('show');
            document.removeEventListener('click', this.closeSidebarOnOutsideClick);
        }
    }

    // ====================================
    // TABLE FUNCTIONALITY
    // ====================================

    initTables() {
        // Add hover effects and selection
        const tables = document.querySelectorAll('.admin-table table');
        
        tables.forEach(table => {
            // Add click handlers for rows
            const rows = table.querySelectorAll('tbody tr[data-href]');
            rows.forEach(row => {
                row.style.cursor = 'pointer';
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
        });

        // Initialize table sorting if needed
        this.initTableSorting();
    }

    initTableSorting() {
        const sortableHeaders = document.querySelectorAll('[data-sort]');
        
        sortableHeaders.forEach(header => {
            header.style.cursor = 'pointer';
            header.innerHTML += ' <i class="fas fa-sort ms-1"></i>';
            
            header.addEventListener('click', () => {
                const sortField = header.dataset.sort;
                const currentUrl = new URL(window.location);
                const currentSort = currentUrl.searchParams.get('sort');
                
                // Toggle sort direction
                if (currentSort === sortField) {
                    currentUrl.searchParams.set('sort', `-${sortField}`);
                } else if (currentSort === `-${sortField}`) {
                    currentUrl.searchParams.delete('sort');
                } else {
                    currentUrl.searchParams.set('sort', sortField);
                }
                
                window.location.href = currentUrl.toString();
            });
        });
    }

    // ====================================
    // FORM FUNCTIONALITY
    // ====================================

    initForms() {
        // Add loading states to form submissions
        const forms = document.querySelectorAll('form[data-loading]');
        
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    const originalText = submitBtn.innerHTML;
                    submitBtn.innerHTML = '<span class="loading-spinner me-2"></span>Procesando...';
                    submitBtn.disabled = true;
                    
                    // Store original text for potential error recovery
                    submitBtn.dataset.originalText = originalText;
                }
            });
        });

        // Initialize filter forms
        this.initFilterForms();
        
        // Initialize search functionality
        this.initSearch();
    }

    initFilterForms() {
        const filterForm = document.getElementById('filterForm');
        if (!filterForm) return;

        // Auto-submit on filter change
        const filterInputs = filterForm.querySelectorAll('select, input[type="checkbox"]');
        filterInputs.forEach(input => {
            input.addEventListener('change', () => {
                filterForm.submit();
            });
        });

        // Clear filters button
        const clearFiltersBtn = document.getElementById('clearFilters');
        if (clearFiltersBtn) {
            clearFiltersBtn.addEventListener('click', (e) => {
                e.preventDefault();
                
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
            });
        }
    }

    initSearch() {
        const searchInput = document.getElementById('searchInput');
        if (!searchInput) return;

        let searchTimeout;
        
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            
            // Debounce search to avoid too many requests
            searchTimeout = setTimeout(() => {
                const form = searchInput.closest('form');
                if (form) {
                    form.submit();
                }
            }, 500);
        });
    }

    // ====================================
    // AJAX ACTIONS
    // ====================================

    initAjaxActions() {
        // Toggle buttons (like activating/deactivating surveys)
        const toggleBtns = document.querySelectorAll('[data-toggle-url]');
        toggleBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleToggleAction(btn);
            });
        });

        // Quick action buttons
        const actionBtns = document.querySelectorAll('[data-action-url]');
        actionBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleQuickAction(btn);
            });
        });
    }

    async handleToggleAction(btn) {
        const url = btn.dataset.toggleUrl;
        const confirmMessage = btn.dataset.confirm;
        
        if (confirmMessage && !confirm(confirmMessage)) {
            return;
        }

        // Show loading state
        const originalContent = btn.innerHTML;
        btn.innerHTML = '<span class="loading-spinner"></span>';
        btn.disabled = true;

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest',
                },
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification(data.message, 'success');
                
                // Update button state if provided
                if (data.new_status !== undefined) {
                    this.updateToggleButton(btn, data.new_status);
                } else {
                    // Reload page to reflect changes
                    setTimeout(() => window.location.reload(), 1000);
                }
            } else {
                this.showNotification(data.message || 'Error procesando la acción', 'error');
            }
        } catch {
            this.showNotification('Error de conexión', 'error');
        } finally {
            // Restore button state
            btn.innerHTML = originalContent;
            btn.disabled = false;
        }
    }

    async handleQuickAction(btn) {
        const url = btn.dataset.actionUrl;
        const confirmMessage = btn.dataset.confirm;
        
        if (confirmMessage && !confirm(confirmMessage)) {
            return;
        }

        // Show loading state
        const originalContent = btn.innerHTML;
        btn.innerHTML = '<span class="loading-spinner"></span>';
        btn.disabled = true;

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest',
                },
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification(data.message, 'success');
                
                // Remove the parent row or update UI
                if (btn.dataset.removeParent) {
                    const parentElement = btn.closest(btn.dataset.removeParent);
                    if (parentElement) {
                        parentElement.style.opacity = '0.5';
                        setTimeout(() => parentElement.remove(), 500);
                    }
                }
            } else {
                this.showNotification(data.message || 'Error procesando la acción', 'error');
            }
        } catch {
            this.showNotification('Error de conexión', 'error');
        } finally {
            // Restore button state
            btn.innerHTML = originalContent;
            btn.disabled = false;
        }
    }

    updateToggleButton(btn, newStatus) {
        if (newStatus) {
            btn.classList.remove('btn-outline-danger');
            btn.classList.add('btn-outline-success');
            btn.innerHTML = '<i class="fas fa-toggle-on me-1"></i>Activo';
        } else {
            btn.classList.remove('btn-outline-success');
            btn.classList.add('btn-outline-danger');
            btn.innerHTML = '<i class="fas fa-toggle-off me-1"></i>Inactivo';
        }
    }

    // ====================================
    // NOTIFICATIONS
    // ====================================

    showNotification(message, type = 'info') {
        // Create notification element
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

        // Add to page
        document.body.appendChild(notification);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    // ====================================
    // UTILITIES
    // ====================================

    initTooltips() {
        // Initialize Bootstrap tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    getCSRFToken() {
        // Get CSRF token from meta tag
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');
        return csrfMeta ? csrfMeta.getAttribute('content') : '';
    }

    // ====================================
    // DATA FORMATTING
    // ====================================

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

    // ====================================
    // EXPORT FUNCTIONALITY
    // ====================================

    exportData(url, filename = 'export.csv') {
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        this.showNotification('Exportación iniciada', 'success');
    }
}

// ====================================
// GLOBAL FUNCTIONS
// ====================================

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.scgAdmin = new SCGAdmin();
});

// Make functions available globally
window.SCGAdmin = {
    showNotification: function(message, type) {
        if (window.scgAdmin) {
            window.scgAdmin.showNotification(message, type);
        }
    },
    
    exportData: function(url, filename) {
        if (window.scgAdmin) {
            window.scgAdmin.exportData(url, filename);
        }
    }
};

// Handle form errors
window.addEventListener('error', function(e) {
    // Restore any loading buttons
    const loadingBtns = document.querySelectorAll('button[data-original-text]');
    loadingBtns.forEach(btn => {
        btn.innerHTML = btn.dataset.originalText;
        btn.disabled = false;
        delete btn.dataset.originalText;
    });
});