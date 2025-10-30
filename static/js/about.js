// Slider State
let currentSlide = 0;
const totalSlides = 13; // Updated from 9 to 13
let autoplayEnabled = true;
let autoplayInterval;

// Elements
const cards = document.querySelectorAll('.card');
const dots = document.querySelectorAll('.dot');
const cardCounter = document.getElementById('cardCounter');
const autoplayIndicator = document.getElementById('autoplayIndicator');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');

// Card position classes
const positionClasses = ['far-prev', 'prev', 'active', 'next', 'far-next'];

function updateCardPositions() {
    cards.forEach((card, index) => {
        // Remove all position classes
        card.classList.remove('active', 'next', 'prev', 'far-next', 'far-prev', 'hidden');
        
        const relativeIndex = (index - currentSlide + totalSlides) % totalSlides;
        
        if (relativeIndex === 0) {
            card.classList.add('active');
        } else if (relativeIndex === 1) {
            card.classList.add('next');
        } else if (relativeIndex === 2) {
            card.classList.add('far-next');
        } else if (relativeIndex === totalSlides - 1) {
            card.classList.add('prev');
        } else if (relativeIndex === totalSlides - 2) {
            card.classList.add('far-prev');
        } else {
            card.classList.add('hidden');
        }
    });

    // Update dots
    dots.forEach((dot, index) => {
        dot.classList.toggle('active', index === currentSlide);
    });

    // Update counter
    cardCounter.textContent = `Card ${currentSlide + 1} of ${totalSlides}`;
}

function nextSlide() {
    currentSlide = (currentSlide + 1) % totalSlides;
    updateCardPositions();
}

function prevSlide() {
    currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
    updateCardPositions();
}

function goToSlide(index) {
    currentSlide = index;
    updateCardPositions();
}

function startAutoplay() {
    if (autoplayInterval) clearInterval(autoplayInterval);
    autoplayInterval = setInterval(nextSlide, 3000);
}

function stopAutoplay() {
    if (autoplayInterval) {
        clearInterval(autoplayInterval);
        autoplayInterval = null;
    }
}

function toggleAutoplay() {
    autoplayEnabled = !autoplayEnabled;
    const toggleBtn = document.getElementById('toggleBtn');
    
    if (autoplayEnabled) {
        autoplayIndicator.textContent = 'Auto-play: ON';
        autoplayIndicator.classList.remove('paused');
        toggleBtn.textContent = 'Pause Auto-play';
        toggleBtn.style.background = 'linear-gradient(135deg, #ff6b6b, #ee5a52)';
        startAutoplay();
    } else {
        autoplayIndicator.textContent = 'Auto-play: OFF';
        autoplayIndicator.classList.add('paused');
        toggleBtn.textContent = 'Resume Auto-play';
        toggleBtn.style.background = 'linear-gradient(135deg, #51cf66, #40c057)';
        stopAutoplay();
    }
}

function resetSlider() {
    currentSlide = 0;
    updateCardPositions();
    
    // Visual feedback for reset
    const resetBtn = document.getElementById('resetBtn');
    const originalText = resetBtn.textContent;
    resetBtn.textContent = 'Reset ✓';
    resetBtn.style.background = 'linear-gradient(135deg, #51cf66, #40c057)';
    
    setTimeout(() => {
        resetBtn.textContent = originalText;
        resetBtn.style.background = 'linear-gradient(135deg, var(--accent), #00f2fe)';
    }, 1000);
}

// Event Listeners
prevBtn.addEventListener('click', prevSlide);
nextBtn.addEventListener('click', nextSlide);

// Keyboard navigation
document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft') prevSlide();
    if (e.key === 'ArrowRight') nextSlide();
    if (e.key === ' ') {
        e.preventDefault();
        toggleAutoplay();
    }
});

// Touch/Swipe support
let startX = 0;
let endX = 0;

document.addEventListener('touchstart', (e) => {
    startX = e.touches[0].clientX;
});

document.addEventListener('touchend', (e) => {
    endX = e.changedTouches[0].clientX;
    const diff = startX - endX;
    
    if (Math.abs(diff) > 50) { // Minimum swipe distance
        if (diff > 0) {
            nextSlide();
        } else {
            prevSlide();
        }
    }
});

// Pause autoplay on hover
const sliderContainer = document.querySelector('.slider-container');
sliderContainer.addEventListener('mouseenter', () => {
    if (autoplayEnabled) stopAutoplay();
});

sliderContainer.addEventListener('mouseleave', () => {
    if (autoplayEnabled) startAutoplay();
});

// Background Particles
function createParticles() {
    const particlesContainer = document.getElementById('particles');
    const particleCount = 75;
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.width = Math.random() * 6 + 2 + 'px';
        particle.style.height = particle.style.width;
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 6 + 's';
        particle.style.animationDuration = (Math.random() * 3 + 4) + 's';
        particlesContainer.appendChild(particle);
    }
}

// Initialize
function initializeSlider() {
    updateCardPositions();
    if (autoplayEnabled) startAutoplay();
    createParticles();
}

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeSlider();
});

// If DOM is already loaded, initialize immediately
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeSlider);
} else {
    initializeSlider();
}

// Add sparkle effects on mouse move
document.addEventListener('mousemove', (e) => {
    if (Math.random() > 0.10) {
        const sparkle = document.createElement('div');
        sparkle.style.position = 'fixed';
        sparkle.style.left = e.clientX + 'px';
        sparkle.style.top = e.clientY + 'px';
        sparkle.style.width = '5px';
        sparkle.style.height = '5px';
        sparkle.style.background = 'var(--accent)';
        sparkle.style.borderRadius = '50%';
        sparkle.style.pointerEvents = 'none';
        sparkle.style.zIndex = '100';
        sparkle.style.animation = 'sparkle 0.8s ease-out forwards';
        document.body.appendChild(sparkle);
        
        setTimeout(() => sparkle.remove(), 800);
    }
});

// Sparkle animation
const sparkleStyle = document.createElement('style');
sparkleStyle.textContent = `
    @keyframes sparkle {
        0% { transform: scale(0) rotate(0deg); opacity: 1; }
        100% { transform: scale(1) rotate(180deg); opacity: 0; }
    }
`;
document.head.appendChild(sparkleStyle);
//bb gg