// Responsive JavaScript for SoundJury

// Mobile menu management
class MobileMenu {
    constructor() {
        this.menuToggle = document.querySelector('.mobile-menu-toggle');
        this.mobileMenu = document.querySelector('.mobile-menu');
        this.overlay = null;
        this.init();
    }

    init() {
        if (this.menuToggle && this.mobileMenu) {
            this.menuToggle.addEventListener('click', () => this.toggle());
            this.createOverlay();
            this.handleResize();
            window.addEventListener('resize', () => this.handleResize());
        }
    }

    createOverlay() {
        this.overlay = document.createElement('div');
        this.overlay.className = 'mobile-menu-overlay';
        this.overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 998;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
        `;
        document.body.appendChild(this.overlay);
        
        this.overlay.addEventListener('click', () => this.close());
    }

    toggle() {
        if (this.mobileMenu.classList.contains('active')) {
            this.close();
        } else {
            this.open();
        }
    }

    open() {
        this.mobileMenu.classList.add('active');
        this.overlay.style.opacity = '1';
        this.overlay.style.pointerEvents = 'auto';
        document.body.style.overflow = 'hidden';
        
        // Change icon
        const icon = this.menuToggle.querySelector('i');
        if (icon) icon.className = 'fas fa-times';
    }

    close() {
        this.mobileMenu.classList.remove('active');
        this.overlay.style.opacity = '0';
        this.overlay.style.pointerEvents = 'none';
        document.body.style.overflow = '';
        
        // Change icon back
        const icon = this.menuToggle.querySelector('i');
        if (icon) icon.className = 'fas fa-bars';
    }

    handleResize() {
        if (window.innerWidth > 768) {
            this.close();
        }
    }
}

// Responsive grid management
class ResponsiveGrid {
    constructor(gridSelector, itemSelector) {
        this.grid = document.querySelector(gridSelector);
        this.itemSelector = itemSelector;
        this.init();
    }

    init() {
        if (this.grid) {
            this.adjustGrid();
            window.addEventListener('resize', () => this.adjustGrid());
        }
    }

    adjustGrid() {
        const width = window.innerWidth;
        const items = this.grid.querySelectorAll(this.itemSelector);
        
        items.forEach(item => {
            if (width <= 480) {
                item.classList.add('mobile-small');
            } else if (width <= 768) {
                item.classList.add('mobile');
                item.classList.remove('mobile-small');
            } else {
                item.classList.remove('mobile', 'mobile-small');
            }
        });
    }
}

// Touch gestures for mobile
class TouchGestures {
    constructor() {
        this.startX = 0;
        this.startY = 0;
        this.init();
    }

    init() {
        document.addEventListener('touchstart', (e) => this.handleTouchStart(e));
        document.addEventListener('touchmove', (e) => this.handleTouchMove(e));
        document.addEventListener('touchend', (e) => this.handleTouchEnd(e));
    }

    handleTouchStart(e) {
        this.startX = e.touches[0].clientX;
        this.startY = e.touches[0].clientY;
    }

    handleTouchMove(e) {
        if (!this.startX || !this.startY) return;

        const currentX = e.touches[0].clientX;
        const currentY = e.touches[0].clientY;
        
        const diffX = this.startX - currentX;
        const diffY = this.startY - currentY;

        // Prevent horizontal scroll on mobile menu
        const mobileMenu = document.querySelector('.mobile-menu');
        if (mobileMenu && mobileMenu.classList.contains('active')) {
            if (Math.abs(diffX) > Math.abs(diffY)) {
                e.preventDefault();
            }
        }
    }

    handleTouchEnd(e) {
        if (!this.startX || !this.startY) return;

        const currentX = e.changedTouches[0].clientX;
        const diffX = this.startX - currentX;

        // Swipe to close menu
        if (Math.abs(diffX) > 50) {
            const mobileMenu = document.querySelector('.mobile-menu');
            if (mobileMenu && mobileMenu.classList.contains('active')) {
                if (diffX > 0) { // Swipe left to close
                    mobileMenu.classList.remove('active');
                }
            }
        }

        this.startX = 0;
        this.startY = 0;
    }
}

// Responsive images
class ResponsiveImages {
    constructor() {
        this.init();
    }

    init() {
        this.loadImages();
        window.addEventListener('resize', () => this.adjustImages());
    }

    loadImages() {
        const images = document.querySelectorAll('img[data-src]');
        
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        observer.unobserve(img);
                    }
                });
            });

            images.forEach(img => observer.observe(img));
        } else {
            // Fallback for older browsers
            images.forEach(img => {
                img.src = img.dataset.src;
                img.classList.remove('lazy');
            });
        }
    }

    adjustImages() {
        const images = document.querySelectorAll('.track-image');
        const isMobile = window.innerWidth <= 768;
        
        images.forEach(img => {
            if (isMobile) {
                img.style.width = '60px';
                img.style.height = '60px';
            } else {
                img.style.width = '80px';
                img.style.height = '80px';
            }
        });
    }
}

// Form validation
class FormValidator {
    constructor() {
        this.init();
    }

    init() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => this.validateForm(e));
        });

        // Real-time validation
        const inputs = document.querySelectorAll('input[required]');
        inputs.forEach(input => {
            input.addEventListener('blur', () => this.validateInput(input));
            input.addEventListener('input', () => this.clearError(input));
        });
    }

    validateForm(e) {
        const form = e.target;
        const inputs = form.querySelectorAll('input[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!this.validateInput(input)) {
                isValid = false;
            }
        });

        if (!isValid) {
            e.preventDefault();
        }
    }

    validateInput(input) {
        const value = input.value.trim();
        const type = input.type;
        let isValid = true;
        let message = '';

        // Required validation
        if (!value) {
            isValid = false;
            message = 'Ce champ est requis';
        }
        // Email validation
        else if (type === 'email' && !this.isValidEmail(value)) {
            isValid = false;
            message = 'Format d\'email invalide';
        }
        // Password validation
        else if (type === 'password' && value.length < 6) {
            isValid = false;
            message = 'Le mot de passe doit contenir au moins 6 caractères';
        }

        if (!isValid) {
            this.showError(input, message);
        } else {
            this.clearError(input);
        }

        return isValid;
    }

    isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    showError(input, message) {
        this.clearError(input);
        
        input.classList.add('error');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        errorDiv.style.cssText = `
            color: var(--error);
            font-size: 0.8rem;
            margin-top: 0.25rem;
            animation: fadeIn 0.3s ease;
        `;
        
        input.parentNode.appendChild(errorDiv);
    }

    clearError(input) {
        input.classList.remove('error');
        const errorMsg = input.parentNode.querySelector('.error-message');
        if (errorMsg) {
            errorMsg.remove();
        }
    }
}

// Search functionality
class SearchManager {
    constructor() {
        this.searchForm = document.getElementById('searchForm');
        this.searchInput = document.getElementById('searchInput');
        this.searchBtn = document.getElementById('searchBtn');
        this.resultsGrid = document.getElementById('results');
        this.currentPage = 1;
        this.totalPages = 1;
        this.init();
    }

    init() {
        if (this.searchForm) {
            this.searchForm.addEventListener('submit', (e) => this.handleSearch(e));
        }

        // Filter chips
        const filterChips = document.querySelectorAll('.filter-chip');
        filterChips.forEach(chip => {
            chip.addEventListener('click', () => this.handleFilterChange(chip));
        });

        // Sort select
        const sortSelect = document.getElementById('sortSelect');
        if (sortSelect) {
            sortSelect.addEventListener('change', () => this.handleSort());
        }
    }

    async handleSearch(e) {
        e.preventDefault();
        
        const query = this.searchInput.value.trim();
        if (!query) return;

        this.setLoading(true);
        
        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query })
            });

            if (response.ok) {
                const data = await response.json();
                this.displayResults(data.tracks || []);
            } else {
                throw new Error('Erreur de recherche');
            }
        } catch (error) {
            console.error('Search error:', error);
            this.showError('Erreur lors de la recherche');
        } finally {
            this.setLoading(false);
        }
    }

    handleFilterChange(chip) {
        // Remove active class from all chips
        document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
        // Add active class to clicked chip
        chip.classList.add('active');
        
        // Re-run search with filter
        if (this.searchInput.value.trim()) {
            this.handleSearch(new Event('submit'));
        }
    }

    handleSort() {
        // Re-run search with new sort order
        if (this.searchInput.value.trim()) {
            this.handleSearch(new Event('submit'));
        }
    }

    displayResults(tracks) {
        if (!tracks || tracks.length === 0) {
            this.resultsGrid.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-search"></i>
                    <h3>Aucun résultat trouvé</h3>
                    <p>Essayez avec d'autres mots-clés ou vérifiez l'orthographe</p>
                </div>
            `;
            return;
        }

        this.resultsGrid.innerHTML = tracks.map(track => this.createTrackCard(track)).join('');
        this.updateResultsHeader(tracks.length);
    }

    createTrackCard(track) {
        return `
            <div class="track-card fade-in">
                <div class="track-header">
                    <img src="${track.image || '/static/default-track.jpg'}" alt="${track.title}" class="track-image">
                    <div class="track-info">
                        <h3>${track.title}</h3>
                        <p>${track.artist}</p>
                        ${track.duration ? `<div class="track-duration">${this.formatDuration(track.duration)}</div>` : ''}
                    </div>
                </div>
                
                <div class="track-source source-${track.source}">
                    <i class="fab fa-${track.source}"></i>
                    ${track.source.charAt(0).toUpperCase() + track.source.slice(1)}
                </div>
                
                <div class="track-actions">
                    <div class="rating-section">
                        <div class="stars" data-track-id="${track.id}">
                            ${this.createStars(track.rating || 0)}
                        </div>
                        <div class="rating-display">
                            <span>${track.rating || 0}/5</span>
                            <span>(${track.rating_count || 0} notes)</span>
                        </div>
                    </div>
                    
                    <div class="track-links">
                        ${track.preview_url ? `<a href="${track.preview_url}" class="link-btn link-preview" target="_blank"><i class="fas fa-play"></i> Écouter</a>` : ''}
                        ${track.external_url ? `<a href="${track.external_url}" class="link-btn link-external" target="_blank"><i class="fas fa-external-link-alt"></i> Voir</a>` : ''}
                    </div>
                </div>
            </div>
        `;
    }

    createStars(rating) {
        let stars = '';
        for (let i = 1; i <= 5; i++) {
            const active = i <= rating ? 'active' : '';
            stars += `<i class="fas fa-star star ${active}" data-rating="${i}"></i>`;
        }
        return stars;
    }

    formatDuration(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    updateResultsHeader(count) {
        const resultsHeader = document.getElementById('resultsHeader');
        const resultsCount = document.getElementById('resultsCount');
        
        if (resultsHeader && resultsCount) {
            resultsHeader.style.display = 'flex';
            resultsCount.textContent = `${count} résultat${count > 1 ? 's' : ''} trouvé${count > 1 ? 's' : ''}`;
        }
    }

    setLoading(isLoading) {
        if (isLoading) {
            this.searchBtn.disabled = true;
            this.searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Recherche...';
            this.resultsGrid.innerHTML = `
                <div class="loading">
                    <i class="fas fa-spinner"></i>
                    <p>Recherche en cours...</p>
                </div>
            `;
        } else {
            this.searchBtn.disabled = false;
            this.searchBtn.innerHTML = '<i class="fas fa-search"></i> <span>Rechercher</span>';
        }
    }

    showError(message) {
        this.resultsGrid.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-exclamation-triangle"></i>
                <h3>Erreur</h3>
                <p>${message}</p>
            </div>
        `;
    }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize responsive components
    new MobileMenu();
    new ResponsiveGrid('.tracks-grid', '.track-card');
    new ResponsiveGrid('.results-grid', '.track-card');
    new TouchGestures();
    new ResponsiveImages();
    new FormValidator();
    new SearchManager();

    // Initialize animations
    const fadeElements = document.querySelectorAll('.fade-in');
    fadeElements.forEach((el, index) => {
        setTimeout(() => {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // Rating stars interaction
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('star')) {
            const rating = parseInt(e.target.dataset.rating);
            const trackId = e.target.closest('.stars').dataset.trackId;
            const stars = e.target.closest('.stars').querySelectorAll('.star');
            
            // Update visual feedback
            stars.forEach((star, index) => {
                if (index < rating) {
                    star.classList.add('active');
                } else {
                    star.classList.remove('active');
                }
            });

            // Send rating to server
            submitRating(trackId, rating);
        }
    });
});

// Rating submission function
async function submitRating(trackId, rating) {
    try {
        const response = await fetch('/api/rate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                track_id: trackId,
                rating: rating
            })
        });

        if (response.ok) {
            const data = await response.json();
            // Update rating display
            const ratingDisplay = document.querySelector(`[data-track-id="${trackId}"]`)
                .closest('.track-actions').querySelector('.rating-display');
            if (ratingDisplay) {
                ratingDisplay.innerHTML = `
                    <span>${data.average_rating}/5</span>
                    <span>(${data.rating_count} notes)</span>
                `;
            }
        }
    } catch (error) {
        console.error('Rating submission error:', error);
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

// Export for use in other scripts
window.SoundJuryResponsive = {
    MobileMenu,
    ResponsiveGrid,
    TouchGestures,
    ResponsiveImages,
    FormValidator,
    SearchManager,
    debounce,
    throttle
};
