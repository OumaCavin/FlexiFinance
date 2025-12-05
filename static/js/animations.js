/**
 * FlexiFinance Animations
 * Handles smooth animations and interactive effects
 */

(function() {
    'use strict';

    // Initialize animations when DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        initAnimations();
        initInteractiveEffects();
        initLoadingAnimations();
        initScrollAnimations();
    });

    function initAnimations() {
        // Initialize AOS (Animate On Scroll) with custom settings
        AOS.init({
            duration: 800,
            easing: 'ease-in-out',
            once: true,
            offset: 100,
            delay: 0,
            disable: 'mobile' // Disable on mobile for better performance
        });

        // Custom animations for different elements
        initHeroAnimations();
        initCardAnimations();
        initButtonAnimations();
        initCounterAnimations();
        initProgressAnimations();
    }

    function initHeroAnimations() {
        const hero = document.querySelector('.hero');
        if (!hero) return;

        // Animate hero content with stagger effect
        const heroTitle = hero.querySelector('h1');
        const heroSubtitle = hero.querySelector('p');
        const heroButtons = hero.querySelectorAll('.btn');
        const heroFeatures = hero.querySelectorAll('.hero-feature');

        if (heroTitle) {
            heroTitle.style.opacity = '0';
            heroTitle.style.transform = 'translateY(50px)';
            
            setTimeout(() => {
                heroTitle.style.transition = 'all 1s ease-out';
                heroTitle.style.opacity = '1';
                heroTitle.style.transform = 'translateY(0)';
            }, 200);
        }

        if (heroSubtitle) {
            heroSubtitle.style.opacity = '0';
            heroSubtitle.style.transform = 'translateY(30px)';
            
            setTimeout(() => {
                heroSubtitle.style.transition = 'all 1s ease-out';
                heroSubtitle.style.opacity = '1';
                heroSubtitle.style.transform = 'translateY(0)';
            }, 400);
        }

        heroButtons.forEach((button, index) => {
            button.style.opacity = '0';
            button.style.transform = 'translateY(30px)';
            
            setTimeout(() => {
                button.style.transition = 'all 0.8s ease-out';
                button.style.opacity = '1';
                button.style.transform = 'translateY(0)';
            }, 600 + (index * 100));
        });

        // Floating animation for hero elements
        heroFeatures.forEach((feature, index) => {
            feature.style.animation = `float 3s ease-in-out infinite`;
            feature.style.animationDelay = `${index * 0.5}s`;
        });
    }

    function initCardAnimations() {
        const cards = document.querySelectorAll('.card');
        
        cards.forEach(card => {
            // Add hover effects
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-8px) scale(1.02)';
                this.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
            });

            // Staggered animation on page load
            if (card.dataset.animate === 'stagger') {
                card.style.opacity = '0';
                card.style.transform = 'translateY(30px)';
            }
        });

        // Animate cards that are marked for stagger animation
        const staggerCards = document.querySelectorAll('.card[data-animate="stagger"]');
        staggerCards.forEach((card, index) => {
            setTimeout(() => {
                card.style.transition = 'all 0.6s ease-out';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }

    function initButtonAnimations() {
        const buttons = document.querySelectorAll('.btn');
        
        buttons.forEach(button => {
            // Ripple effect on click
            button.addEventListener('click', function(e) {
                const ripple = document.createElement('span');
                const rect = this.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.cssText = `
                    position: absolute;
                    border-radius: 50%;
                    background: rgba(255, 255, 255, 0.6);
                    transform: scale(0);
                    animation: ripple 0.6s linear;
                    width: ${size}px;
                    height: ${size}px;
                    left: ${x}px;
                    top: ${y}px;
                    pointer-events: none;
                `;
                
                this.style.position = 'relative';
                this.style.overflow = 'hidden';
                this.appendChild(ripple);
                
                setTimeout(() => ripple.remove(), 600);
            });

            // Loading animation for submit buttons
            const originalClick = button.onclick;
            button.addEventListener('click', function(e) {
                if (this.type === 'submit' && !this.disabled) {
                    const originalText = this.textContent;
                    this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                    this.disabled = true;
                    
                    // Restore after 2 seconds (adjust as needed)
                    setTimeout(() => {
                        this.innerHTML = originalText;
                        this.disabled = false;
                    }, 2000);
                }
            });
        });
    }

    function initCounterAnimations() {
        const counters = document.querySelectorAll('[data-counter]');
        
        const observerOptions = {
            threshold: 0.5,
            rootMargin: '0px 0px -100px 0px'
        };

        const counterObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    counterObserver.unobserve(entry.target);
                }
            });
        }, observerOptions);

        counters.forEach(counter => {
            counterObserver.observe(counter);
        });
    }

    function animateCounter(element) {
        const target = parseInt(element.dataset.counter);
        const duration = parseInt(element.dataset.duration) || 2000;
        const start = parseInt(element.textContent) || 0;
        const startTime = performance.now();

        function updateCounter(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function for smooth animation
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const current = Math.floor(start + (target - start) * easeOutQuart);
            
            element.textContent = current.toLocaleString();
            
            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            } else {
                element.textContent = target.toLocaleString();
            }
        }

        requestAnimationFrame(updateCounter);
    }

    function initProgressAnimations() {
        const progressBars = document.querySelectorAll('.progress-bar');
        
        const observerOptions = {
            threshold: 0.5
        };

        const progressObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const progressBar = entry.target;
                    const targetWidth = progressBar.dataset.width || progressBar.style.width;
                    
                    progressBar.style.width = '0%';
                    progressBar.style.transition = 'width 1.5s ease-out';
                    
                    setTimeout(() => {
                        progressBar.style.width = targetWidth;
                    }, 200);
                    
                    progressObserver.unobserve(progressBar);
                }
            });
        }, observerOptions);

        progressBars.forEach(bar => {
            progressObserver.observe(bar);
        });
    }

    function initInteractiveEffects() {
        // Parallax scrolling effects
        initParallaxEffects();
        
        // Mouse following effects
        initMouseFollowEffects();
        
        // Typing animation
        initTypingAnimation();
        
        // Image lazy loading with fade-in
        initLazyLoading();
    }

    function initParallaxEffects() {
        const parallaxElements = document.querySelectorAll('[data-parallax]');
        
        window.addEventListener('scroll', throttle(() => {
            const scrollTop = window.pageYOffset;
            
            parallaxElements.forEach(element => {
                const speed = parseFloat(element.dataset.parallax) || 0.5;
                const yPos = -(scrollTop * speed);
                element.style.transform = `translateY(${yPos}px)`;
            });
        }, 10));
    }

    function initMouseFollowEffects() {
        const mouseFollowElements = document.querySelectorAll('[data-mouse-follow]');
        
        mouseFollowElements.forEach(element => {
            element.addEventListener('mousemove', throttle((e) => {
                const rect = element.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                
                const moveX = (x - centerX) * 0.1;
                const moveY = (y - centerY) * 0.1;
                
                element.style.transform = `translate(${moveX}px, ${moveY}px)`;
            }, 10));
        });
    }

    function initTypingAnimation() {
        const typingElements = document.querySelectorAll('[data-typing]');
        
        typingElements.forEach(element => {
            const text = element.textContent;
            const speed = parseInt(element.dataset.typingSpeed) || 50;
            const delay = parseInt(element.dataset.typingDelay) || 0;
            
            element.textContent = '';
            element.style.borderRight = '2px solid';
            element.style.animation = 'blink 1s infinite';
            
            setTimeout(() => {
                typeWriter(element, text, speed);
            }, delay);
        });
    }

    function typeWriter(element, text, speed) {
        let i = 0;
        
        function type() {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
                setTimeout(type, speed);
            } else {
                // Remove cursor after typing is complete
                setTimeout(() => {
                    element.style.borderRight = 'none';
                    element.style.animation = 'none';
                }, 1000);
            }
        }
        
        type();
    }

    function initLazyLoading() {
        const lazyImages = document.querySelectorAll('img[data-src]');
        
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    img.classList.add('fade-in');
                    imageObserver.unobserve(img);
                }
            });
        });

        lazyImages.forEach(img => {
            img.classList.add('lazy');
            imageObserver.observe(img);
        });
    }

    function initLoadingAnimations() {
        // Page transition animations
        initPageTransitions();
        
        // Loading spinners
        initLoadingSpinners();
        
        // Skeleton loading
        initSkeletonLoading();
    }

    function initPageTransitions() {
        // Fade out current page before navigation
        const links = document.querySelectorAll('a[href]:not([href^="#"]):not([target="_blank"])');
        
        links.forEach(link => {
            link.addEventListener('click', function(e) {
                if (this.hostname === window.location.hostname) {
                    e.preventDefault();
                    document.body.style.opacity = '0';
                    document.body.style.transform = 'translateY(20px)';
                    document.body.style.transition = 'all 0.3s ease-out';
                    
                    setTimeout(() => {
                        window.location.href = this.href;
                    }, 300);
                }
            });
        });
    }

    function initLoadingSpinners() {
        window.showSpinner = function(container, size = 'md') {
            const spinner = document.createElement('div');
            spinner.className = `spinner spinner-${size}`;
            spinner.innerHTML = `
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            `;
            container.appendChild(spinner);
            return spinner;
        };

        window.hideSpinner = function(spinner) {
            if (spinner && spinner.parentNode) {
                spinner.parentNode.removeChild(spinner);
            }
        };
    }

    function initSkeletonLoading() {
        window.showSkeleton = function(container, rows = 3) {
            const skeleton = document.createElement('div');
            skeleton.className = 'skeleton-loading';
            
            for (let i = 0; i < rows; i++) {
                const row = document.createElement('div');
                row.className = 'skeleton-row';
                row.innerHTML = `
                    <div class="skeleton-avatar"></div>
                    <div class="skeleton-content">
                        <div class="skeleton-line"></div>
                        <div class="skeleton-line short"></div>
                    </div>
                `;
                skeleton.appendChild(row);
            }
            
            container.appendChild(skeleton);
            return skeleton;
        };

        window.hideSkeleton = function(skeleton) {
            if (skeleton && skeleton.parentNode) {
                skeleton.parentNode.removeChild(skeleton);
            }
        };
    }

    function initScrollAnimations() {
        // Scroll-triggered animations
        const scrollElements = document.querySelectorAll('[data-scroll-animate]');
        
        const scrollObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    const animation = element.dataset.scrollAnimate;
                    
                    element.classList.add(`animate-${animation}`);
                    scrollObserver.unobserve(element);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        scrollElements.forEach(element => {
            scrollObserver.observe(element);
        });
    }

    // Utility function for throttling
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
        }
    }

    // CSS for custom animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
        }
        
        @keyframes ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
        
        @keyframes blink {
            0%, 50% { border-color: transparent; }
            51%, 100% { border-color: currentColor; }
        }
        
        .fade-in {
            opacity: 0;
            transition: opacity 0.6s ease-out;
        }
        
        .fade-in.loaded {
            opacity: 1;
        }
        
        .lazy {
            opacity: 0;
            filter: blur(5px);
            transition: all 0.6s ease-out;
        }
        
        .skeleton-loading {
            animation: pulse 2s ease-in-out infinite;
        }
        
        .skeleton-row {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .skeleton-avatar {
            width: 40px;
            height: 40px;
            background: #e0e0e0;
            border-radius: 50%;
            margin-right: 1rem;
        }
        
        .skeleton-content {
            flex: 1;
        }
        
        .skeleton-line {
            height: 12px;
            background: #e0e0e0;
            border-radius: 4px;
            margin-bottom: 8px;
        }
        
        .skeleton-line.short {
            width: 60%;
        }
        
        .spinner-sm .spinner-border {
            width: 1rem;
            height: 1rem;
        }
        
        .spinner-md .spinner-border {
            width: 2rem;
            height: 2rem;
        }
        
        .spinner-lg .spinner-border {
            width: 3rem;
            height: 3rem;
        }
        
        .navbar-scrolled {
            background-color: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
        }
        
        .payment-method.active {
            border-color: var(--primary-color);
            background: var(--primary-color);
            color: white;
            transform: scale(1.05);
        }
    `;
    document.head.appendChild(style);

})();