// Function to flip the card
        function flipCard(card) {
            card.classList.toggle('flipped');
        }

        // Add fade-in animation to cards when page loads
        document.addEventListener('DOMContentLoaded', function() {
            const cards = document.querySelectorAll('.team-card');
            cards.forEach(card => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
            });

            setTimeout(() => {
                cards.forEach((card, index) => {
                    setTimeout(() => {
                        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, 100 * index);
                });
            }, 100);
        });