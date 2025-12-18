/**
 * FlexiFinance Main JavaScript
 * Handles core functionality and interactions
 */

(function() {
    'use strict';

    // Initialize when DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        initializeApp();
    });

    function initializeApp() {
        // Initialize core modules
        initNavigation();
        initForms();
        initModals();
        initToastNotifications();
        initBackToTop();
        initScrollEffects();
        initPaymentMethods();
        initContactForm();
        initNewsletterForm();
        initAnalytics();
        
        console.log('FlexiFinance app initialized');
    }

    /**
     * Navigation functionality
     */
    function initNavigation() {
        const navbar = document.querySelector('.navbar');
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        
        // Add scroll effect to navbar
        window.addEventListener('scroll', function() {
            if (window.scrollY > 100) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        });

        // Mobile menu toggle
        const navbarToggler = document.querySelector('.navbar-toggler');
        const navbarCollapse = document.querySelector('.navbar-collapse');
        
        if (navbarToggler && navbarCollapse) {
            navbarToggler.addEventListener('click', function() {
                navbarCollapse.classList.toggle('show');
            });

            // Close mobile menu when clicking outside
            document.addEventListener('click', function(e) {
                if (!navbar.contains(e.target)) {
                    navbarCollapse.classList.remove('show');
                }
            });

            // Close mobile menu when clicking nav links
            navLinks.forEach(link => {
                link.addEventListener('click', function() {
                    navbarCollapse.classList.remove('show');
                });
            });
        }

        // Smooth scroll for anchor links
        navLinks.forEach(link => {
            if (link.getAttribute('href').startsWith('#')) {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    const targetId = this.getAttribute('href').substring(1);
                    const targetElement = document.getElementById(targetId);
                    
                    if (targetElement) {
                        const offsetTop = targetElement.offsetTop - 80; // Account for navbar height
                        window.scrollTo({
                            top: offsetTop,
                            behavior: 'smooth'
                        });
                    }
                });
            }
        });

        // Initialize Bootstrap dropdowns for user menu
        const userDropdown = document.getElementById('userDropdown');
        if (userDropdown && typeof bootstrap !== 'undefined') {
            try {
                const dropdown = new bootstrap.Dropdown(userDropdown);
                console.log('User dropdown initialized in main.js');
            } catch (error) {
                console.error('Error initializing user dropdown:', error);
            }
        }

        // Handle dropdowns on mobile
        const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
        dropdownToggles.forEach(toggle => {
            toggle.addEventListener('click', function(e) {
                if (window.innerWidth <= 991) {
                    e.preventDefault();
                    const menu = this.nextElementSibling;
                    if (menu) {
                        menu.classList.toggle('show');
                    }
                }
            });
        });
    }

    /**
     * Form enhancements
     */
    function initForms() {
        // Real-time validation
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            // SKIP VALIDATION if the form has this class (e.g., AllAuth forms)
            if (form.classList.contains('no-js-validate')) {
                return;
            }

            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                input.addEventListener('blur', function() {
                    validateField(this);
                });
                
                input.addEventListener('input', function() {
                    clearFieldError(this);
                });
            });
        });

        // Form submission handling
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                // SKIP VALIDATION if the form has this class (e.g., AllAuth forms)
                if (this.classList.contains('no-js-validate')) {
                    // Still add loading state visually
                    const submitBtn = this.querySelector('button[type="submit"]');
                    if (submitBtn) {
                        submitBtn.classList.add('loading');
                        // Do NOT disable immediately for AllAuth forms, let the post happen
                    }
                    return; // Let the form submit naturally
                }

                if (!validateForm(this)) {
                    e.preventDefault();
                    return false;
                }
                
                // Add loading state
                const submitBtn = this.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.classList.add('loading');
                    submitBtn.disabled = true;
                }
            });
        });
    }

    /**
     * Field validation
     */
    function validateField(field) {
        const value = field.value.trim();
        const type = field.type;
        const required = field.hasAttribute('required');
        
        clearFieldError(field);
        
        // Required field validation
        if (required && !value) {
            showFieldError(field, 'This field is required');
            return false;
        }
        
        // Email validation
        if (type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                showFieldError(field, 'Please enter a valid email address');
                return false;
            }
        }
        
        // Phone validation
        if (field.name === 'phone' || field.type === 'tel') {
            const phoneRegex = /^(\+254|0)[17]\d{8}$/;
            if (value && !phoneRegex.test(value)) {
                showFieldError(field, 'Please enter a valid Kenyan phone number');
                return false;
            }
        }
        
        // Amount validation
        if (field.name === 'amount' || field.classList.contains('amount-input')) {
            const amount = parseFloat(value);
            if (value && (isNaN(amount) || amount <= 0)) {
                showFieldError(field, 'Please enter a valid amount');
                return false;
            }
        }
        
        return true;
    }

    function showFieldError(field, message) {
        field.classList.add('is-invalid');
        
        // Remove existing error message
        const existingError = field.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
        
        // Add new error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
    }

    function clearFieldError(field) {
        field.classList.remove('is-invalid');
        const errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    function validateForm(form) {
        const inputs = form.querySelectorAll('input, textarea, select');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!validateField(input)) {
                isValid = false;
            }
        });
        
        return isValid;
    }

    /**
     * Modal functionality
     */
    function initModals() {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.addEventListener('show.bs.modal', function() {
                // Initialize modal content if needed
                const modalBody = modal.querySelector('.modal-body');
                if (modalBody && modalBody.dataset.load === 'dynamic') {
                    loadModalContent(modalBody);
                }
            });
        });
    }

    function loadModalContent(modalBody) {
        // Load dynamic content for modals
        const url = modalBody.dataset.url;
        if (url) {
            fetch(url)
                .then(response => response.text())
                .then(html => {
                    modalBody.innerHTML = html;
                })
                .catch(error => {
                    modalBody.innerHTML = '<p class="text-center">Error loading content. Please try again.</p>';
                });
        }
    }

    /**
     * Toast notifications
     */
    function initToastNotifications() {
        window.showToast = function(message, type = 'info') {
            const toast = document.createElement('div');
            toast.className = `toast toast-${type}`;
            toast.innerHTML = `
                <div class="d-flex align-items-center">
                    <div class="me-3">
                        <i class="fas ${getToastIcon(type)}"></i>
                    </div>
                    <div class="flex-grow-1">${message}</div>
                    <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()"></button>
                </div>
            `;
            
            document.body.appendChild(toast);
            
            // Show toast
            setTimeout(() => toast.classList.add('show'), 100);
            
            // Auto hide after 5 seconds
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 300);
            }, 5000);
        };
    }

    function getToastIcon(type) {
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    /**
     * Back to top button
     */
    function initBackToTop() {
        const backToTopBtn = document.getElementById('back-to-top');
        
        if (backToTopBtn) {
            window.addEventListener('scroll', function() {
                if (window.scrollY > 500) {
                    backToTopBtn.style.display = 'block';
                } else {
                    backToTopBtn.style.display = 'none';
                }
            });
            
            backToTopBtn.addEventListener('click', function() {
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            });
        }
    }

    /**
     * Scroll effects
     */
    function initScrollEffects() {
        // Parallax effect for hero sections
        const heroSections = document.querySelectorAll('.hero');
        heroSections.forEach(hero => {
            window.addEventListener('scroll', function() {
                const scrolled = window.pageYOffset;
                const rate = scrolled * -0.5;
                hero.style.transform = `translateY(${rate}px)`;
            });
        });

        // Navbar hide/show on scroll
        let lastScrollTop = 0;
        const navbar = document.querySelector('.navbar');
        
        window.addEventListener('scroll', function() {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
            if (scrollTop > lastScrollTop && scrollTop > 100) {
                // Scrolling down
                navbar.style.transform = 'translateY(-100%)';
            } else {
                // Scrolling up
                navbar.style.transform = 'translateY(0)';
            }
            
            lastScrollTop = scrollTop;
        });
    }

    /**
     * Payment method functionality
     */
    function initPaymentMethods() {
        const paymentMethods = document.querySelectorAll('.payment-method');
        paymentMethods.forEach(method => {
            method.addEventListener('click', function() {
                // Remove active class from all methods
                paymentMethods.forEach(m => m.classList.remove('active'));
                
                // Add active class to clicked method
                this.classList.add('active');
                
                // Update payment form
                const paymentType = this.dataset.paymentType;
                updatePaymentForm(paymentType);
            });
        });

        // Initialize first payment method as active
        if (paymentMethods.length > 0) {
            paymentMethods[0].classList.add('active');
        }
    }

    function updatePaymentForm(paymentType) {
        const paymentForm = document.getElementById('payment-form');
        if (paymentForm) {
            const paymentMethodInput = paymentForm.querySelector('input[name="payment_method"]');
            if (paymentMethodInput) {
                paymentMethodInput.value = paymentType;
            }
        }
    }

    /**
     * Contact form functionality
     */
    function initContactForm() {
        const contactForm = document.getElementById('contact-form');
        if (contactForm) {
            contactForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                if (!validateForm(this)) {
                    return;
                }
                
                const formData = new FormData(this);
                const data = Object.fromEntries(formData.entries());
                
                // Submit via AJAX
                submitContactForm(data);
            });
        }
    }

    function submitContactForm(data) {
        fetch('/api/contact/submit/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                showToast('Thank you for your message! We\'ll get back to you soon.', 'success');
                document.getElementById('contact-form').reset();
            } else {
                showToast(result.error || 'Failed to send message. Please try again.', 'error');
            }
        })
        .catch(error => {
            console.error('Contact form error:', error);
            showToast('Failed to send message. Please try again.', 'error');
        });
    }

    /**
     * Newsletter subscription
     */
    function initNewsletterForm() {
        const newsletterForms = document.querySelectorAll('.newsletter-form');
        newsletterForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                const email = this.querySelector('input[type="email"]').value;
                if (!email) {
                    showToast('Please enter your email address', 'warning');
                    return;
                }
                
                const submitBtn = this.querySelector('button[type="submit"]');
                const originalText = submitBtn.textContent;
                submitBtn.textContent = 'Subscribing...';
                submitBtn.disabled = true;
                
                // Simulate newsletter subscription
                setTimeout(() => {
                    showToast('Successfully subscribed to our newsletter!', 'success');
                    this.reset();
                    submitBtn.textContent = originalText;
                    submitBtn.disabled = false;
                }, 1500);
            });
        });
    }

    /**
     * Analytics tracking
     */
    function initAnalytics() {
        // Track page views
        if (typeof gtag !== 'undefined') {
            gtag('config', 'GA_MEASUREMENT_ID', {
                page_title: document.title,
                page_location: window.location.href
            });
        }
        
        // Track button clicks
        document.addEventListener('click', function(e) {
            const button = e.target.closest('button, .btn');
            if (button) {
                trackEvent('button_click', {
                    button_text: button.textContent.trim(),
                    button_id: button.id || '',
                    page_location: window.location.href
                });
            }
        });
        
        // Track form submissions
        document.addEventListener('submit', function(e) {
            const form = e.target;
            if (form.tagName === 'FORM') {
                trackEvent('form_submit', {
                    form_id: form.id || '',
                    form_name: form.name || '',
                    page_location: window.location.href
                });
            }
        });
    }

    function trackEvent(action, parameters) {
        if (typeof gtag !== 'undefined') {
            gtag('event', action, parameters);
        }
        
        // Facebook Pixel tracking
        if (typeof fbq !== 'undefined') {
            fbq('track', action, parameters);
        }
    }

    /**
     * Utility functions
     */
    function getCsrfToken() {
        const cookieMatch = document.cookie.match(/csrftoken=([^;]+)/);
        if (cookieMatch) {
            return cookieMatch[1];
        }
        
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            return metaTag.getAttribute('content');
        }
        
        const inputField = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (inputField) {
            return inputField.value;
        }
        
        return '';
    }

    function formatCurrency(amount, currency = 'KES') {
        const formatter = new Intl.NumberFormat('en-KE', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 2
        });
        return formatter.format(amount);
    }

    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    function throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    // Make utility functions globally available
    window.FlexiFinance = {
        showToast: window.showToast,
        formatCurrency,
        trackEvent,
        validateField,
        validateForm,
        debounce,
        throttle
    };

})();