// Animation on page load
document.addEventListener('DOMContentLoaded', function() {
    const heroText = document.querySelector('.hero-text');
    const heroVisual = document.querySelector('.hero-visual');
    
    heroText.style.opacity = '1';
    heroVisual.style.opacity = '1';
    
    // Create rain drops
    createRainDrops();
});

// Create rain drops animation
function createRainDrops() {
    const rainContainer = document.querySelector('.rain-container');
    const dropCount = 100;
    
    for (let i = 0; i < dropCount; i++) {
        const drop = document.createElement('div');
        drop.classList.add('rain-drop');
        
        // Random properties for each drop
        const left = Math.random() * 100;
        const animationDuration = 0.5 + Math.random() * 0.5;
        const animationDelay = Math.random() * 5;
        const height = 10 + Math.random() * 20;
        const opacity = 0.2 + Math.random() * 0.5;
        
        drop.style.left = `${left}%`;
        drop.style.animationDuration = `${animationDuration}s`;
        drop.style.animationDelay = `${animationDelay}s`;
        drop.style.height = `${height}px`;
        drop.style.opacity = opacity;
        
        rainContainer.appendChild(drop);
    }
}