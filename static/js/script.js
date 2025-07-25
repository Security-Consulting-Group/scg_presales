// Security Consulting Group - Django Integration JavaScript

// Get CSRF token for Django AJAX requests
function getCSRFToken() {
    // Primero intentar obtenerlo del formulario
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfInput) {
        return csrfInput.value;
    }
    
    // Si no está en el formulario, intentar obtenerlo del meta tag
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    if (csrfMeta) {
        return csrfMeta.getAttribute('content');
    }
    
    // Como último recurso, intentar obtenerlo de las cookies
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

// Scroll to any section smoothly
function scrollToSection(sectionId) {
    document.getElementById(sectionId).scrollIntoView({
        behavior: 'smooth'
    });
}

// Navbar scroll effect
function handleNavbarScroll() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.style.background = 'rgba(255, 255, 255, 0.98)';
        navbar.style.boxShadow = '0 2px 20px rgba(0,0,0,0.1)';
    } else {
        navbar.style.background = 'rgba(255, 255, 255, 0.95)';
        navbar.style.boxShadow = 'none';
    }
}

// Django AJAX form submission handler
function handleFormSubmission(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    // Show loading state with animation
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Enviando...';
    submitBtn.disabled = true;
    submitBtn.style.transition = 'all 1s ease';
    submitBtn.style.transform = 'scale(0.98)';
    
    // Send AJAX request to Django
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'X-Requested-With': 'XMLHttpRequest',
        },
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => Promise.reject(data));
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showSuccessMessage(data.message);
            form.reset();
        } else {
            showErrorMessage(data.message);
        }
    })
    .catch(error => {
        const message = error.message || 'Error procesando su solicitud. Por favor intente nuevamente.';
        showErrorMessage(message);
    })
    .finally(() => {
        // Restore button state with animation
        setTimeout(() => {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
            submitBtn.style.transform = 'scale(1)';
        }, 1000);
    });
}

// Show success message positioned above the form (like screenshot 2)
function showSuccessMessage(message = '¡Gracias! Hemos recibido su solicitud. Nos pondremos en contacto con usted pronto.') {
    // Wait 1 second for button animation to finish
    setTimeout(() => {
        const contactForm = document.getElementById('contactForm-1');
        const notification = document.createElement('div');
        notification.className = 'scg-notification scg-notification-success';
        notification.innerHTML = `
            <div class="scg-notification-content">
                <i class="fas fa-check-circle scg-notification-icon"></i>
                <div class="scg-notification-text">
                    <strong>¡Perfecto!</strong>
                    <p>${message}</p>
                </div>
                <button type="button" class="scg-notification-close" onclick="this.closest('.scg-notification').remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        // Insert notification BEFORE the form (above it)
        if (contactForm) {
            contactForm.appendChild(notification);
        }
        
        // Show with animation
        setTimeout(() => notification.classList.add('scg-notification-show'), 10);
        
        // Auto remove after 6 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.classList.remove('scg-notification-show');
                setTimeout(() => notification.remove(), 400);
            }
        }, 6000);
    }, 1000); // Wait 1 second
}

// Show error message positioned above the form
function showErrorMessage(message = 'Ocurrió un error. Por favor intente nuevamente.') {
    // Wait 1 second for button animation to finish
    setTimeout(() => {
        const contactForm = document.getElementById('contactForm-1');
        const notification = document.createElement('div');
        notification.className = 'scg-notification scg-notification-error';
        notification.innerHTML = `
            <div class="scg-notification-content">
                <i class="fas fa-exclamation-circle scg-notification-icon"></i>
                <div class="scg-notification-text">
                    <strong>¡Ups!</strong>
                    <p>${message}</p>
                </div>
                <button type="button" class="scg-notification-close" onclick="this.closest('.scg-notification').remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        // Insert notification BEFORE the form (above it)
        if (contactForm) {
            contactForm.parentNode.insertBefore(notification, contactForm);
        }
        
        // Show with animation
        setTimeout(() => notification.classList.add('scg-notification-show'), 10);
        
        // Auto remove after 6 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.classList.remove('scg-notification-show');
                setTimeout(() => notification.remove(), 400);
            }
        }, 6000);
    }, 1000); // Wait 1 second
}

// Show error message with better styling
function showErrorMessage(message = 'Ocurrió un error. Por favor intente nuevamente.') {
    const notification = document.createElement('div');
    notification.className = 'scg-notification scg-notification-error';
    notification.innerHTML = `
        <div class="scg-notification-content">
            <i class="fas fa-exclamation-circle scg-notification-icon"></i>
            <div class="scg-notification-text">
                <strong>¡Ups!</strong>
                <p>${message}</p>
            </div>
            <button type="button" class="scg-notification-close" onclick="this.closest('.scg-notification').remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Show with animation
    setTimeout(() => notification.classList.add('scg-notification-show'), 10);
    
    // Auto remove after 6 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.classList.remove('scg-notification-show');
            setTimeout(() => notification.remove(), 300);
        }
    }, 6000);
}

// Initialize count-up animation for statistics
function initCountUpAnimation() {
    const stats = document.querySelectorAll('.stat-number');
    const statsPlus = document.querySelectorAll('.stat-number-plus');
    
    const countUp = (element, target) => {
        let current = 0;
        const increment = target / 50;
        const timer = setInterval(() => {
            current += increment;
            element.textContent = Math.floor(current);
            if (current >= target) {
                element.textContent = target;
                clearInterval(timer);
            }
        }, 40);
    };
    
    // Trigger count-up when elements come into view
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = parseInt(entry.target.dataset.target);
                countUp(entry.target, target);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    stats.forEach(stat => observer.observe(stat));
    statsPlus.forEach(stat => observer.observe(stat));
}

// Parallax effect for floating cards
function initFloatingCardsParallax() {
    const floatingCards = document.querySelectorAll('.floating-card');
    
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const rate = scrolled * 0.02;
        
        floatingCards.forEach((card, index) => {
            const speed = (index + 1) * 0.5;
            card.style.transform = `translateY(${rate * speed}px)`;
        });
    });
}

// Initialize smooth navigation links
function initSmoothNavigation() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Initialize navbar toggler for mobile
function initMobileNavigation() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    // Close mobile menu when clicking on a link
    document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
        link.addEventListener('click', () => {
            if (navbarCollapse && navbarCollapse.classList.contains('show')) {
                navbarToggler.click();
            }
        });
    });
}

// Bootstrap FAQ functionality
function initBootstrapFAQ() {
    // Listen for Bootstrap accordion events to change + to −
    document.addEventListener('shown.bs.collapse', function (event) {
        const button = document.querySelector(`[data-bs-target="#faq-accordion .${event.target.classList[event.target.classList.length - 1]}"]`);
        if (button) {
            const icon = button.querySelector('.faq-icon');
            if (icon) icon.textContent = '−';
        }
    });

    document.addEventListener('hidden.bs.collapse', function (event) {
        const button = document.querySelector(`[data-bs-target="#faq-accordion .${event.target.classList[event.target.classList.length - 1]}"]`);
        if (button) {
            const icon = button.querySelector('.faq-icon');
            if (icon) icon.textContent = '+';
        }
    });
}

// Event Listeners - CONSOLIDADO Y LIMPIO
document.addEventListener('DOMContentLoaded', function() {
    // Initialize essential components
    initCountUpAnimation();
    initFloatingCardsParallax();
    initSmoothNavigation();
    initMobileNavigation();
    initBootstrapFAQ();
    
    // 🔥 ÚNICA configuración del formulario de contacto
    const contactForm = document.getElementById('contactForm-1');
    if (contactForm) {
        // Asegurar que solo hay UN event listener
        contactForm.removeEventListener('submit', handleFormSubmission);
        contactForm.addEventListener('submit', handleFormSubmission);
        
    }
});

// Scroll event listeners
window.addEventListener('scroll', function() {
    handleNavbarScroll();
});

// Error handling for images
document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        img.addEventListener('error', function() {
            this.style.display = 'none';
        });
    });
});

// Export functions for global access
window.SCG = {
    scrollToSection,
    showSuccessMessage,
    showErrorMessage
};