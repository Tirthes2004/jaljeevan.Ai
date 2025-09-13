        // Dummy data for demonstration
        const leaderboardData = [
            { 
                id: 1,
                name: "AquaWarrior", 
                location: "Bangalore, India",
                credits: 12500, 
                progress: 92,
                badges: [
                    { type: "trophy", tooltip: "Top Contributor" },
                    { type: "leaf", tooltip: "Eco Champion" },
                    { type: "water", tooltip: "Water Savior" },
                    { type: "energy", tooltip: "Energy Saver" }
                ] 
            },
            { 
                id: 2,
                name: "RainGuardian", 
                location: "Mumbai, India",
                credits: 9800, 
                progress: 85,
                badges: [
                    { type: "trophy", tooltip: "Top Contributor" },
                    { type: "leaf", tooltip: "Eco Champion" },
                    { type: "water", tooltip: "Water Savior" }
                ] 
            },
            { 
                id: 3,
                name: "HydroHero", 
                location: "Delhi, India",
                credits: 8750, 
                progress: 78,
                badges: [
                    { type: "leaf", tooltip: "Eco Champion" },
                    { type: "water", tooltip: "Water Savior" },
                    { type: "energy", tooltip: "Energy Saver" }
                ] 
            },
            { 
                id: 4,
                name: "EcoSaver", 
                location: "Chennai, India",
                credits: 7600, 
                progress: 68,
                badges: [
                    { type: "water", tooltip: "Water Savior" },
                    { type: "energy", tooltip: "Energy Saver" }
                ] 
            },
            { 
                id: 5,
                name: "GreenThumb", 
                location: "Hyderabad, India",
                credits: 6400, 
                progress: 60,
                badges: [
                    { type: "leaf", tooltip: "Eco Champion" },
                    { type: "energy", tooltip: "Energy Saver" }
                ] 
            },
            { 
                id: 6,
                name: "WaterWizard", 
                location: "Pune, India",
                credits: 5800, 
                progress: 55,
                badges: [
                    { type: "water", tooltip: "Water Savior" }
                ] 
            },
            { 
                id: 7,
                name: "EcoWarrior", 
                location: "Kolkata, India",
                credits: 5200, 
                progress: 48,
                badges: [
                    { type: "leaf", tooltip: "Eco Champion" }
                ] 
            },
            { 
                id: 8,
                name: "SustainableSam", 
                location: "Ahmedabad, India",
                credits: 4700, 
                progress: 42,
                badges: [
                    { type: "energy", tooltip: "Energy Saver" }
                ] 
            },
            { 
                id: 9,
                name: "PlanetProtector", 
                location: "Jaipur, India",
                credits: 4100, 
                progress: 38,
                badges: [] 
            },
            { 
                id: 10,
                name: "EcoEnthusiast", 
                location: "Lucknow, India",
                credits: 3800, 
                progress: 35,
                badges: [] 
            }
        ];

        // Check if user is logged in (for demo purposes, we'll simulate a logged-in user)
        const currentUser = {
            id: 15,
            name: "WaterSaver",
            credits: 2850,
            rank: 15,
            progress: 26
        };

        // Function to render leaderboard
        function renderLeaderboard() {
            const leaderboardList = document.getElementById('leaderboard-list');
            leaderboardList.innerHTML = '';
            
            // Render top users
            leaderboardData.forEach((user, index) => {
                const rankItem = document.createElement('div');
                rankItem.className = `rank-item rank-${index + 1}`;
                rankItem.id = `user-${user.id}`;
                
                rankItem.innerHTML = `
                    <div class="rank-number">${index + 1}</div>
                    <div class="user-info">
                        <div class="user-avatar">
                            <i class="fas fa-user"></i>
                        </div>
                        <div class="user-details">
                            <div class="user-name">${user.name}</div>
                            <div class="user-location">${user.location}</div>
                        </div>
                    </div>
                    <div class="user-credits">${user.credits.toLocaleString()}</div>
                    <div class="progress-container">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${user.progress}%"></div>
                        </div>
                        <div class="progress-text">${user.progress}%</div>
                    </div>
                    <div class="user-badges">
                        ${user.badges.map(badge => 
                            `<div class="badge ${badge.type}" data-tooltip="${badge.tooltip}">
                                <i class="fas fa-${badge.type === 'trophy' ? 'trophy' : badge.type === 'leaf' ? 'leaf' : badge.type === 'water' ? 'tint' : 'bolt'}"></i>
                            </div>`
                        ).join('')}
                    </div>
                `;
                
                leaderboardList.appendChild(rankItem);
            });
            
            // Render user's rank if not in top 10
            renderUserRankCard();
        }
        
        // Function to render user's rank card
        function renderUserRankCard() {
            const userRankCard = document.getElementById('user-rank-card');
            
            userRankCard.innerHTML = `
                <div class="rank-number">${currentUser.rank}</div>
                <div class="user-info">
                    <div class="user-avatar">
                        <i class="fas fa-user"></i>
                    </div>
                    <div class="user-details">
                        <div class="user-name">${currentUser.name} (You)</div>
                        <div class="user-location">See your profile</div>
                    </div>
                </div>
                <div class="user-credits">${currentUser.credits.toLocaleString()}</div>
                <div class="progress-container">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${currentUser.progress}%"></div>
                    </div>
                    <div class="progress-text">${currentUser.progress}%</div>
                </div>
                <div class="user-badges">
                    <div class="badge water" data-tooltip="Water Saver">
                        <i class="fas fa-tint"></i>
                    </div>
                </div>
            `;
        }
        
        // Initialize leaderboard when page loads
        document.addEventListener('DOMContentLoaded', function() {
            renderLeaderboard();
            
            // Add event listeners to filter buttons
            const filterButtons = document.querySelectorAll('.filter-btn');
            filterButtons.forEach(button => {
                button.addEventListener('click', function() {
                    filterButtons.forEach(btn => btn.classList.remove('active'));
                    this.classList.add('active');
                    // In a real app, this would filter the leaderboard data
                });
            });
            
            // Simulate rank changes for demo purposes
            setTimeout(() => {
                const userItem = document.getElementById('user-4');
                if (userItem) {
                    userItem.classList.add('rank-change');
                }
            }, 2000);
        });
