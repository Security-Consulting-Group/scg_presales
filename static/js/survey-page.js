/**
 * Survey Page JavaScript functionality
 */

class SurveyPage {
    constructor() {
        this.surveyCode = null;
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.initializeAOS();
            this.extractSurveyCode();
            this.setupSurveyPage();
        });
    }

    initializeAOS() {
        // Initialize AOS (Animate On Scroll)
        if (typeof AOS !== 'undefined') {
            AOS.init({
                duration: 800,
                easing: 'ease-in-out',
                once: true,
                offset: 50
            });
            console.log('✨ AOS animations initialized');
        } else {
            console.warn('⚠️ AOS library not found');
        }
    }

    extractSurveyCode() {
        // Extract survey code from meta tag or URL
        const metaTag = document.querySelector('meta[name="survey-code"]');
        if (metaTag) {
            this.surveyCode = metaTag.getAttribute('content');
        } else {
            // Fallback: extract from URL or other source
            const urlParams = new URLSearchParams(window.location.search);
            this.surveyCode = urlParams.get('code') || 'unknown';
        }
        
        console.log('Survey loaded:', this.surveyCode);
    }

    setupSurveyPage() {
        // Additional survey page setup can go here
        this.setupProgressIndicators();
        this.setupSmoothScrolling();
        this.setupFormInteractions();
    }

    setupProgressIndicators() {
        // Add progress indicators if needed
        const questionGroups = document.querySelectorAll('.question-group');
        if (questionGroups.length > 1) {
            console.log(`📋 Survey has ${questionGroups.length} question groups`);
        }
    }

    setupSmoothScrolling() {
        // Smooth scroll to survey section
        const surveySection = document.querySelector('.survey-section');
        if (surveySection) {
            // Add smooth scroll behavior
            surveySection.style.scrollBehavior = 'smooth';
        }
    }

    setupFormInteractions() {
        // Add any additional form interaction enhancements
        const surveyForm = document.getElementById('surveyForm');
        if (surveyForm) {
            console.log('📝 Survey form found and ready');
        }
    }

    // Utility method to get survey code
    getSurveyCode() {
        return this.surveyCode;
    }

    // Method to refresh AOS animations (useful for dynamic content)
    refreshAnimations() {
        if (typeof AOS !== 'undefined') {
            AOS.refresh();
        }
    }
}

// Initialize survey page
const surveyPage = new SurveyPage();

// Export for global access
window.surveyPage = surveyPage; 