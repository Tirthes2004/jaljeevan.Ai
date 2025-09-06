// Function to flip the card
        function flipCard(card) {
            const inner = card.querySelector('.team-card-inner');
            inner.classList.toggle('flipped');
        }

        // Add event listeners to all cards
        document.addEventListener('DOMContentLoaded', function() {
            const cards = document.querySelectorAll('.team-card');
            cards.forEach(card => {
                card.addEventListener('click', function() {
                    flipCard(this);
                });
                
                // Add fade-in animation
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
            });

            // Animate cards in sequence
            setTimeout(() => {
                cards.forEach((card, index) => {
                    setTimeout(() => {
                        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, 100 * index);
                });
            }, 100);

            // Create water drop animations
            createWaterDrops();
        });

        // Function to create water drop animations
        function createWaterDrops() {
            const container = document.getElementById('water-drops');
            const dropsCount = 15;
            
            for (let i = 0; i < dropsCount; i++) {
                const drop = document.createElement('div');
                drop.className = 'water-drop';
                
                // Random properties for each drop
                const left = Math.random() * 100;
                const size = Math.random() * 4 + 2;
                const duration = Math.random() * 5 + 5;
                const delay = Math.random() * 5;
                
                drop.style.left = `${left}vw`;
                drop.style.width = `${size}px`;
                drop.style.height = `${size}px`;
                drop.style.animationDuration = `${duration}s`;
                drop.style.animationDelay = `${delay}s`;
                
                container.appendChild(drop);
            }
        }