/**
 * Bootstrap Modal Polyfill
 * Fallback functionality for Bootstrap Modal when it fails to load
 */

(function() {
    'use strict';
    
    // Ensure bootstrap exists as global object
    window.bootstrap = window.bootstrap || {};
    
    // If bootstrap.Modal doesn't exist, create a simple polyfill
    if (!window.bootstrap.Modal) {
        console.warn('Bootstrap Modal not found, using polyfill');
        
        window.bootstrap.Modal = class ModalPolyfill {
            constructor(element, options = {}) {
                this.element = element;
                this.options = options;
                this._backdrop = null;
                console.log("Usando polyfill para Modal");
            }
            
            show() {
                // Show modal
                this.element.style.display = 'block';
                this.element.classList.add('show');
                document.body.classList.add('modal-open');
                
                // Create backdrop if it doesn't exist
                this._backdrop = document.createElement('div');
                this._backdrop.className = 'modal-backdrop fade show';
                document.body.appendChild(this._backdrop);
                
                // Store instance
                this.element._bsModal = this;
                
                // Add click listener to backdrop
                if (this._backdrop) {
                    this._backdrop.addEventListener('click', () => {
                        if (!this.options.backdrop || this.options.backdrop !== 'static') {
                            this.hide();
                        }
                    });
                }
                
                // Add escape key listener
                this._keydownHandler = (e) => {
                    if (e.key === 'Escape' && (!this.options.keyboard || this.options.keyboard !== false)) {
                        this.hide();
                    }
                };
                document.addEventListener('keydown', this._keydownHandler);
                
                // Focus on modal
                this.element.focus();
            }
            
            hide() {
                // Hide modal
                this.element.style.display = 'none';
                this.element.classList.remove('show');
                document.body.classList.remove('modal-open');
                
                // Remove backdrop
                if (this._backdrop && this._backdrop.parentNode) {
                    this._backdrop.parentNode.removeChild(this._backdrop);
                    this._backdrop = null;
                }
                
                // Remove event listeners
                if (this._keydownHandler) {
                    document.removeEventListener('keydown', this._keydownHandler);
                    this._keydownHandler = null;
                }
                
                // Remove instance reference
                delete this.element._bsModal;
            }
            
            toggle() {
                if (this.element.classList.contains('show')) {
                    this.hide();
                } else {
                    this.show();
                }
            }
            
            static getInstance(element) {
                return element._bsModal || null;
            }
            
            static getOrCreateInstance(element, options = {}) {
                let instance = this.getInstance(element);
                if (!instance) {
                    instance = new this(element, options);
                }
                return instance;
            }
        };
        
        // Add data-bs-dismiss functionality
        document.addEventListener('click', function(e) {
            const dismissBtn = e.target.closest('[data-bs-dismiss="modal"]');
            if (dismissBtn) {
                const modal = dismissBtn.closest('.modal');
                if (modal) {
                    const modalInstance = window.bootstrap.Modal.getInstance(modal);
                    if (modalInstance) {
                        modalInstance.hide();
                    }
                }
            }
        });
        
        // Add data-bs-toggle functionality
        document.addEventListener('click', function(e) {
            const toggleBtn = e.target.closest('[data-bs-toggle="modal"]');
            if (toggleBtn) {
                const targetSelector = toggleBtn.getAttribute('data-bs-target') || 
                                     toggleBtn.getAttribute('href');
                if (targetSelector) {
                    const modal = document.querySelector(targetSelector);
                    if (modal) {
                        const modalInstance = window.bootstrap.Modal.getOrCreateInstance(modal);
                        modalInstance.show();
                    }
                }
            }
        });
    }
    
    console.log('✅ Bootstrap Modal polyfill initialized');
})(); 