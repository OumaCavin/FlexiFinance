/**
 * FlexiFinance Responsive JavaScript
 * Handles mobile interactions and responsive behavior
 */

(function() {
    'use strict';

    // Initialize responsive features when DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        initResponsiveFeatures();
        initTouchInteractions();
        initMobileNavigation();
        initResponsiveForms();
        initMobilePayment();
        initViewportHandling();
    });

    function initResponsiveFeatures() {
        // Detect device type
        const deviceType = detectDeviceType();
        document.body.setAttribute('data-device', deviceType);
        
        // Initialize responsive components
        initResponsiveCards();
        initResponsiveTables();
        initResponsiveImages();
        initResponsiveModals();
        
        console.log('Responsive features initialized for:', deviceType);
    }

    function detectDeviceType() {
        const userAgent = navigator.userAgent;
        const width = window.innerWidth;
        
        if (/tablet|ipad|playbook|silk/i.test(userAgent)) {
            return 'tablet';
        }
        
        if (/Mobile|iP(hone|od)|Android|BlackBerry|IEMobile|Kindle|Silk-Accelerated|(hpw|web)OS|Opera M(obi|ini)/.test(userAgent)) {
            return 'mobile';
        }
        
        return 'desktop';
    }

    function initResponsiveCards() {
        const cards = document.querySelectorAll('.card');
        
        cards.forEach(card => {
            // Stack cards vertically on mobile
            if (window.innerWidth <= 768) {
                card.classList.add('card-mobile-stack');
            }
            
            // Adjust card height on mobile
            const adjustCardHeight = () => {
                if (window.innerWidth <= 768) {
                    const cardBody = card.querySelector('.card-body');
                    if (cardBody) {
                        cardBody.style.minHeight = 'auto';
                    }
                }
            };
            
            adjustCardHeight();
            window.addEventListener('resize', debounce(adjustCardHeight, 250));
        });
    }

    function initResponsiveTables() {
        const tables = document.querySelectorAll('.table-responsive');
        
        tables.forEach(tableWrapper => {
            // Add swipe indicators for mobile
            if (window.innerWidth <= 768) {
                const swipeIndicator = document.createElement('div');
                swipeIndicator.className = 'table-swipe-indicator';
                swipeIndicator.innerHTML = '<i class="fas fa-hand-point-right"></i> Swipe to see more';
                tableWrapper.parentNode.insertBefore(swipeIndicator, tableWrapper);
            }
            
            // Touch swipe functionality
            let startX, startY, startTime;
            const threshold = 100;
            const restraint = 1000;
            
            tableWrapper.addEventListener('touchstart', function(e) {
                const touch = e.touches[0];
                startX = touch.pageX - tableWrapper.offsetLeft;
                startY = touch.pageY - tableWrapper.offsetTop;
                startTime = Date.now();
            }, { passive: true });
            
            tableWrapper.addEventListener('touchmove', function(e) {
                if (!startX || !startY) return;
                
                const touch = e.touches[0];
                const diffX = startX - (touch.pageX - tableWrapper.offsetLeft);
                const diffY = startY - (touch.pageY - tableWrapper.offsetTop);
                
                if (Math.abs(diffX) > Math.abs(diffY)) {
                    if (Math.abs(diffX) > threshold && Math.abs(diffY) < restraint) {
                        if (diffX > 0) {
                            // Swiped left - scroll right
                            tableWrapper.scrollLeft += 100;
                        } else {
                            // Swiped right - scroll left
                            tableWrapper.scrollLeft -= 100;
                        }
                        startX = startY = null; // Reset values
                    }
                }
            }, { passive: true });
            
            tableWrapper.addEventListener('touchend', function() {
                startX = startY = null;
            });
        });
    }

    function initResponsiveImages() {
        const images = document.querySelectorAll('img');
        
        images.forEach(img => {
            // Add lazy loading support
            if (!img.hasAttribute('loading')) {
                img.setAttribute('loading', 'lazy');
            }
            
            // Responsive image handling
            const handleResponsiveImage = () => {
                const container = img.parentNode;
                if (container && container.classList.contains('img-container')) {
                    const containerWidth = container.offsetWidth;
                    const containerHeight = container.offsetHeight;
                    
                    img.style.maxWidth = '100%';
                    img.style.height = 'auto';
                    img.style.objectFit = 'contain';
                }
            };
            
            img.addEventListener('load', handleResponsiveImage);
            window.addEventListener('resize', debounce(handleResponsiveImage, 250));
        });
    }

    function initResponsiveModals() {
        const modals = document.querySelectorAll('.modal');
        
        modals.forEach(modal => {
            // Fullscreen modal on mobile
            modal.addEventListener('show.bs.modal', function() {
                if (window.innerWidth <= 768) {
                    this.classList.add('modal-fullscreen-mobile');
                }
            });
            
            // Adjust modal size on resize
            const adjustModalSize = () => {
                if (modal.classList.contains('show')) {
                    if (window.innerWidth <= 768) {
                        modal.classList.add('modal-fullscreen-mobile');
                    } else {
                        modal.classList.remove('modal-fullscreen-mobile');
                    }
                }
            };
            
            window.addEventListener('resize', debounce(adjustModalSize, 250));
        });
    }

    function initTouchInteractions() {
        // Touch-friendly interactions
        initTouchGestures();
        initTouchFeedback();
        initTouchNavigation();
    }

    function initTouchGestures() {
        // Swipe gestures for mobile
        let startX, startY, startTime;
        const threshold = 100;
        const restraint = 1000;
        
        document.addEventListener('touchstart', function(e) {
            const touch = e.touches[0];
            startX = touch.pageX;
            startY = touch.pageY;
            startTime = Date.now();
        }, { passive: true });
        
        document.addEventListener('touchend', function(e) {
            if (!startX || !startY) return;
            
            const touch = e.changedTouches[0];
            const diffX = startX - touch.pageX;
            const diffY = startY - touch.pageY;
            const diffTime = Date.now() - startTime;
            
            // Determine if it's a valid swipe
            if (Math.abs(diffX) >= threshold && Math.abs(diffY) <= restraint && diffTime <= 300) {
                if (diffX > 0) {
                    // Swiped left
                    handleSwipeLeft();
                } else {
                    // Swiped right
                    handleSwipeRight();
                }
            }
            
            startX = startY = null;
        }, { passive: true });
    }

    function handleSwipeLeft() {
        // Close mobile menu if open
        const navbarCollapse = document.querySelector('.navbar-collapse');
        if (navbarCollapse && navbarCollapse.classList.contains('show')) {
            navbarCollapse.classList.remove('show');
        }
        
        // Navigate to next section if available
        const nextSection = document.querySelector('.section.active + .section');
        if (nextSection) {
            nextSection.scrollIntoView({ behavior: 'smooth' });
            nextSection.classList.add('active');
            document.querySelector('.section.active')?.classList.remove('active');
        }
    }

    function handleSwipeRight() {
        // Navigate to previous section if available
        const activeSection = document.querySelector('.section.active');
        if (activeSection && activeSection.previousElementSibling?.classList.contains('section')) {
            const prevSection = activeSection.previousElementSibling;
            prevSection.scrollIntoView({ behavior: 'smooth' });
            prevSection.classList.add('active');
            activeSection.classList.remove('active');
        }
    }

    function initTouchFeedback() {
        // Provide visual feedback for touch interactions
        const touchElements = document.querySelectorAll('button, .btn, .card, .nav-link');
        
        touchElements.forEach(element => {
            element.addEventListener('touchstart', function(e) {
                this.classList.add('touch-active');
            }, { passive: true });
            
            element.addEventListener('touchend', function() {
                setTimeout(() => {
                    this.classList.remove('touch-active');
                }, 150);
            }, { passive: true });
            
            element.addEventListener('touchcancel', function() {
                this.classList.remove('touch-active');
            }, { passive: true });
        });
    }

    function initTouchNavigation() {
        // Bottom navigation for mobile
        const bottomNav = document.querySelector('.bottom-navigation');
        if (bottomNav) {
            const navItems = bottomNav.querySelectorAll('.nav-item');
            
            navItems.forEach(item => {
                item.addEventListener('click', function(e) {
                    e.preventDefault();
                    
                    // Remove active class from all items
                    navItems.forEach(navItem => navItem.classList.remove('active'));
                    
                    // Add active class to clicked item
                    this.classList.add('active');
                    
                    // Handle navigation
                    const href = this.querySelector('.nav-link')?.getAttribute('href');
                    if (href && href.startsWith('#')) {
                        const target = document.querySelector(href);
                        if (target) {
                            target.scrollIntoView({ behavior: 'smooth' });
                        }
                    }
                });
            });
        }
    }

    function initMobileNavigation() {
        // Enhanced mobile navigation
        const navbar = document.querySelector('.navbar');
        const navbarToggle = document.querySelector('.navbar-toggler');
        const navbarCollapse = document.querySelector('.navbar-collapse');
        
        if (navbarToggle && navbarCollapse) {
            // Improved mobile menu toggle
            navbarToggle.addEventListener('click', function() {
                const isOpen = navbarCollapse.classList.contains('show');
                
                if (isOpen) {
                    navbarCollapse.classList.remove('show');
                    navbar.classList.remove('navbar-mobile-open');
                } else {
                    navbarCollapse.classList.add('show');
                    navbar.classList.add('navbar-mobile-open');
                    
                    // Add overlay
                    const overlay = document.createElement('div');
                    overlay.className = 'mobile-menu-overlay';
                    overlay.addEventListener('click', closeMobileMenu);
                    document.body.appendChild(overlay);
                }
            });
            
            // Close mobile menu function
            window.closeMobileMenu = function() {
                navbarCollapse.classList.remove('show');
                navbar.classList.remove('navbar-mobile-open');
                const overlay = document.querySelector('.mobile-menu-overlay');
                if (overlay) {
                    overlay.remove();
                }
            };
            
            // Close menu when clicking nav links
            const navLinks = navbarCollapse.querySelectorAll('.nav-link');
            navLinks.forEach(link => {
                link.addEventListener('click', closeMobileMenu);
            });
        }
    }

    function initResponsiveForms() {
        // Mobile-optimized forms
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            // Adjust form layout for mobile
            const adjustFormLayout = () => {
                if (window.innerWidth <= 768) {
                    form.classList.add('form-mobile');
                    
                    // Stack form groups vertically
                    const formGroups = form.querySelectorAll('.form-group');
                    formGroups.forEach(group => {
                        group.style.marginBottom = '1rem';
                    });
                    
                    // Adjust input sizes
                    const inputs = form.querySelectorAll('input, textarea, select');
                    inputs.forEach(input => {
                        input.style.fontSize = '16px'; // Prevent zoom on iOS
                    });
                } else {
                    form.classList.remove('form-mobile');
                }
            };
            
            adjustFormLayout();
            window.addEventListener('resize', debounce(adjustFormLayout, 250));
            
            // Mobile-specific form validation
            const validateMobileForm = () => {
                if (window.innerWidth <= 768) {
                    // Add mobile-specific validation logic
                    const inputs = form.querySelectorAll('input[required], textarea[required]');
                    inputs.forEach(input => {
                        if (!input.value.trim()) {
                            input.classList.add('is-invalid-mobile');
                        } else {
                            input.classList.remove('is-invalid-mobile');
                        }
                    });
                }
            };
            
            form.addEventListener('submit', validateMobileForm);
        });
    }

    function initMobilePayment() {
        // Mobile payment optimization
        const paymentMethods = document.querySelectorAll('.payment-method');
        
        paymentMethods.forEach(method => {
            method.addEventListener('click', function() {
                if (window.innerWidth <= 768) {
                    // Optimize for mobile payment
                    const paymentType = this.dataset.paymentType;
                    
                    if (paymentType === 'mpesa') {
                        showMobilePaymentInstructions('mpesa');
                    } else if (paymentType === 'stripe') {
                        showMobilePaymentInstructions('card');
                    }
                }
            });
        });
    }

    function showMobilePaymentInstructions(type) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${type === 'mpesa' ? 'M-PESA Payment' : 'Card Payment'} Instructions</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${type === 'mpesa' ? `
                            <div class="payment-instructions">
                                <ol>
                                    <li>Open your M-PESA menu on your phone</li>
                                    <li>Select "Pay Bill" or "Buy Goods"</li>
                                    <li>Enter business number: 174379</li>
                                    <li>Enter the amount you want to pay</li>
                                    <li>Enter your M-PESA PIN</li>
                                    <li>Confirm the transaction</li>
                                </ol>
                                <div class="alert alert-info">
                                    <i class="fas fa-info-circle"></i>
                                    You will receive an STK push notification on your phone to complete the payment.
                                </div>
                            </div>
                        ` : `
                            <div class="payment-instructions">
                                <p>Please use the card payment form below to complete your payment securely.</p>
                                <div class="alert alert-info">
                                    <i class="fas fa-shield-alt"></i>
                                    Your payment information is encrypted and secure.
                                </div>
                            </div>
                        `}
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        // Remove modal from DOM when closed
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }

    function initViewportHandling() {
        // Handle viewport changes
        let viewportHeight = window.innerHeight;
        let viewportWidth = window.innerWidth;
        
        // Update CSS custom properties for viewport size
        const updateViewportVars = () => {
            document.documentElement.style.setProperty('--vh', `${window.innerHeight * 0.01}px`);
            document.documentElement.style.setProperty('--vw', `${window.innerWidth * 0.01}px`);
        };
        
        updateViewportVars();
        window.addEventListener('resize', debounce(updateViewportVars, 100));
        
        // Handle orientation change
        window.addEventListener('orientationchange', function() {
            setTimeout(() => {
                viewportHeight = window.innerHeight;
                viewportWidth = window.innerWidth;
                updateViewportVars();
                
                // Close mobile menu on orientation change
                if (window.innerWidth > 768) {
                    const navbarCollapse = document.querySelector('.navbar-collapse');
                    if (navbarCollapse) {
                        navbarCollapse.classList.remove('show');
                    }
                }
            }, 500);
        });
        
        // Handle iOS viewport issues
        if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {
            document.body.classList.add('ios-device');
            
            // Fix viewport height issues on iOS
            const setVH = () => {
                const vh = window.innerHeight * 0.01;
                document.documentElement.style.setProperty('--vh', `${vh}px`);
            };
            
            setVH();
            window.addEventListener('resize', setVH);
            window.addEventListener('orientationchange', setVH);
        }
    }

    // Utility functions
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

    // CSS for responsive behavior
    const responsiveStyle = document.createElement('style');
    responsiveStyle.textContent = `
        .card-mobile-stack {
            margin-bottom: 1rem !important;
        }
        
        .table-swipe-indicator {
            text-align: center;
            font-size: 0.875rem;
            color: #6c757d;
            margin-bottom: 0.5rem;
            animation: pulse 2s ease-in-out infinite;
        }
        
        .touch-active {
            transform: scale(0.98);
            transition: transform 0.1s ease;
        }
        
        .mobile-menu-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1040;
        }
        
        .navbar-mobile-open {
            background: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .form-mobile .form-group {
            margin-bottom: 1.5rem;
        }
        
        .form-mobile input,
        .form-mobile textarea,
        .form-mobile select {
            font-size: 16px !important; /* Prevent zoom on iOS */
            padding: 0.75rem !important;
        }
        
        .is-invalid-mobile {
            border-color: #dc3545 !important;
            box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25) !important;
        }
        
        .modal-fullscreen-mobile .modal-dialog {
            margin: 0;
            max-width: 100%;
            height: 100vh;
        }
        
        .modal-fullscreen-mobile .modal-content {
            height: 100%;
            border: none;
            border-radius: 0;
        }
        
        .payment-instructions ol {
            padding-left: 1.5rem;
        }
        
        .payment-instructions li {
            margin-bottom: 0.5rem;
            line-height: 1.6;
        }
        
        .ios-device {
            -webkit-overflow-scrolling: touch;
        }
        
        /* Bottom navigation styles */
        .bottom-navigation {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: white;
            border-top: 1px solid #e9ecef;
            padding: 0.5rem 0;
            z-index: 1000;
            display: none;
        }
        
        @media (max-width: 767.98px) {
            .bottom-navigation {
                display: flex;
                justify-content: space-around;
            }
            
            .bottom-navigation .nav-item {
                flex: 1;
                text-align: center;
            }
            
            .bottom-navigation .nav-link {
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 0.5rem;
                color: #6c757d;
                text-decoration: none;
                transition: color 0.2s ease;
            }
            
            .bottom-navigation .nav-link i {
                font-size: 1.25rem;
                margin-bottom: 0.25rem;
            }
            
            .bottom-navigation .nav-link.active {
                color: var(--primary-color);
            }
        }
        
        /* Safe area handling for devices with notches */
        @supports (padding: max(0px)) {
            .bottom-navigation {
                padding-bottom: max(0.5rem, env(safe-area-inset-bottom));
            }
        }
    `;
    document.head.appendChild(responsiveStyle);

})();