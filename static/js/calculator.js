class RainwaterCalculatorDemo {
    constructor() {
        this.baseURL = 'http://127.0.0.1:8000/api/v1';
        this.init();
    }

    init() {
        this.bindEvents();
        this.checkAPIStatus();
        console.log('🚀 Rainwater Calculator Demo initialized');
        // Inside bindEvents() or init() instead of searchDistricts()
        const searchInput = document.getElementById('districtSearch');
        if (searchInput) {
            searchInput.addEventListener('input', async () => {
                const searchTerm = searchInput.value.trim();

                // show results starting from first character
                if (searchTerm.length < 1) {
                    this.clearSearchResults();
                    return;
                }

                try {
                    const response = await fetch(`${this.baseURL}/districts/?search=${encodeURIComponent(searchTerm)}`);
                    const data = await response.json();

                    if (response.ok && data.success) {
                        this.displaySearchResults(data.districts);
                    } else {
                        this.showSearchError('No districts found matching your search.');
                    }
                } catch (error) {
                    console.error('Search error:', error);
                    this.showSearchError('Error searching districts. Please check your connection.');
                }
            });
        }

    }

    bindEvents() {
        // Search functionality
        document.getElementById('searchBtn')?.addEventListener('click', () => this.searchDistricts());
        document.getElementById('districtSearch')?.addEventListener('input', (e) => {
            if (e.target.value.length > 2) {
                this.searchDistricts();
            } else {
                this.clearSearchResults();
            }
        });

        // Form submission
        document.getElementById('calculatorForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.calculateHarvest();
        });

        // Action buttons
        document.getElementById('newCalculation')?.addEventListener('click', () => this.resetCalculator());
        document.getElementById('saveResults')?.addEventListener('click', () => this.saveResults());
    }

    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }

        // Try meta tag fallback
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute('content') : null;
    }

    async checkAPIStatus() {
        try {
            const response = await fetch(`${this.baseURL}/districts/`);
            if (response.ok) {
                this.setAPIStatus('online', 'Connected');
            } else {
                this.setAPIStatus('offline', 'API Error');
            }
        } catch (error) {
            this.setAPIStatus('offline', 'Disconnected');
        }
    }

    setAPIStatus(status, text) {
        const statusElement = document.getElementById('apiStatus');
        const statusText = document.getElementById('statusText');
        if (statusElement && statusText) {
            statusElement.className = `status-indicator ${status}`;
            statusText.textContent = text;
        }
    }

    // async searchDistricts() {
    //     const searchTerm = document.getElementById('districtSearch').value.trim();

    //     if (searchTerm.length < 1) {
    //         this.clearSearchResults();
    //         return;
    //     }

    //     try {
    //         const response = await fetch(`${this.baseURL}/districts/?search=${encodeURIComponent(searchTerm)}`);
    //         const data = await response.json();

    //         if (response.ok && data.success) {
    //             this.displaySearchResults(data.districts);
    //         } else {
    //             this.showSearchError('No districts found matching your search.');
    //         }
    //     } catch (error) {
    //         console.error('Search error:', error);
    //         this.showSearchError('Error searching districts. Please check your connection.');
    //     }
    // }

    // async searchDistricts() {
    //     // Attach event listener so API calls happen on typing
    //     document.getElementById('districtSearch').addEventListener('input', async () => {
    //         const searchTerm = document.getElementById('districtSearch').value.trim();

    //         // show results starting from first character
    //         if (searchTerm.length < 1) {
    //             this.clearSearchResults();
    //             return;
    //         }

    //         try {
    //             const response = await fetch(`${this.baseURL}/districts/?search=${encodeURIComponent(searchTerm)}`);
    //             const data = await response.json();

    //             if (response.ok && data.success) {
    //                 this.displaySearchResults(data.districts);
    //             } else {
    //                 this.showSearchError('No districts found matching your search.');
    //             }
    //         } catch (error) {
    //             console.error('Search error:', error);
    //             this.showSearchError('Error searching districts. Please check your connection.');
    //         }
    //     });

    // }

    displaySearchResults(districts) {
        const resultsDiv = document.getElementById('searchResults');

        if (!resultsDiv) return;

        if (districts.length === 0) {
            resultsDiv.innerHTML = `
                <div class="no-results">
                    <i class="fas fa-info-circle"></i>
                    <span>No districts found. Try a different search term.</span>
                </div>
            `;
            return;
        }

        const resultsHTML = districts.map(district => `
            <div class="search-result-item" onclick="calculator.selectDistrict('${district.district_name}')">
                <div class="district-info">
                    <div class="district-name">${district.district_name}</div>
                    <div class="district-state">${district.state || 'State not specified'}</div>
                </div>
                <div class="rainfall-info">
                    ${district.annual_rainfall_mm} mm/year
                </div>
            </div>
        `).join('');

        resultsDiv.innerHTML = resultsHTML;
    }

    showSearchError(message) {
        const resultsDiv = document.getElementById('searchResults');
        if (resultsDiv) {
            resultsDiv.innerHTML = `
                <div style="padding: 15px; text-align: center; color: #f44336;">
                    <i class="fas fa-exclamation-triangle"></i>
                    <span>${message}</span>
                </div>
            `;
        }
    }

    clearSearchResults() {
        const resultsDiv = document.getElementById('searchResults');
        if (resultsDiv) {
            resultsDiv.innerHTML = '';
        }
    }

    selectDistrict(districtName) {
        const districtInput = document.getElementById('district');
        const searchInput = document.getElementById('districtSearch');
        const lengthInput = document.getElementById('length');

        if (districtInput) districtInput.value = districtName;
        if (searchInput) searchInput.value = '';
        this.clearSearchResults();
        if (lengthInput) lengthInput.focus();
    }

    async calculateHarvest() {
        const formData = new FormData(document.getElementById('calculatorForm'));
        const data = {
            district_name: formData.get('district_name').trim(),
            length: parseFloat(formData.get('length')),
            width: parseFloat(formData.get('width'))
        };

        console.log('🔍 Sending calculation data:', data);

        // Validate form data
        if (!this.validateFormData(data)) {
            return;
        }

        try {
            this.showLoading();
            this.hideError();
            this.hideResults();

            const csrfToken = this.getCSRFToken();
            console.log('🔐 CSRF Token:', csrfToken ? 'Found' : 'Not found');

            // Make POST request to Django API
            const response = await fetch(`${this.baseURL}/calculate/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken || '',
                },
                credentials: 'same-origin',  // Include cookies for authentication
                body: JSON.stringify(data)
            });

            console.log('📡 Response status:', response.status);
            const result = await response.json();
            console.log('📥 API Response:', result);

            if (response.ok && result.success) {
                // Check if calculation was saved with user info
                if (result.data.calculation_id) {
                    console.log(`✅ Calculation saved to database with ID: ${result.data.calculation_id}`);
                    if (result.data.user) {
                        console.log(`✅ Linked to user: ${result.data.user}`);
                        this.showNotification(`Calculation saved for ${result.data.user}! 🎉`, 'success');
                    } else {
                        this.showNotification('Calculation saved successfully! 📊', 'success');
                    }
                } else {
                    console.warn('⚠️ Calculation succeeded but no database ID returned');
                }

                this.displayResults(result.data);
                this.setAPIStatus('online', 'Connected');
            } else {
                let errorMessage = result.error || 'Calculation failed';
                if (result.details) {
                    const errors = Object.values(result.details).flat().join(', ');
                    errorMessage = `${errorMessage}: ${errors}`;
                }
                this.showError(errorMessage);
            }
        } catch (error) {
            console.error('💥 Calculation error:', error);
            this.showError('Network error. Please check if your Django server is running.');
            this.setAPIStatus('offline', 'Connection Error');
        } finally {
            this.hideLoading();
        }
    }

    validateFormData(data) {
        if (!data.district_name || data.district_name.length < 2) {
            this.showError('Please enter a valid district name.');
            return false;
        }

        if (isNaN(data.length) || data.length <= 0) {
            this.showError('Please enter a valid roof length (greater than 0).');
            return false;
        }

        if (isNaN(data.width) || data.width <= 0) {
            this.showError('Please enter a valid roof width (greater than 0).');
            return false;
        }

        return true;
    }

    displayResults(data) {
        // Update result values
        document.getElementById('resultDistrict').textContent = data.district_name;
        document.getElementById('resultState').textContent = data.state;
        document.getElementById('resultRainfall').textContent = `${this.formatNumber(data.annual_rainfall_mm)} mm/year`;
        document.getElementById('resultRoofArea').textContent = `${this.formatNumber(data.roof_area_sqm)} m²`;
        document.getElementById('resultRunoffCoeff').textContent = data.runoff_coefficient;
        document.getElementById('resultWaterLiters').textContent = `${this.formatNumber(data.water_harvested_liters)} L/year`;
        document.getElementById('resultWaterGallons').textContent = `${this.formatNumber(data.water_harvested_gallons)} gal/year`;
        document.getElementById('resultRecommendation').textContent = data.recommendation;

        // Show user info if available
        const userInfoDiv = document.getElementById('resultUserInfo');
        if (userInfoDiv && data.user) {
            userInfoDiv.innerHTML = `
                <div class="calculation-meta">
                    <div class="user-badge">
                        <i class="fas fa-user"></i>
                        <span>Calculated by: <strong>${data.user}</strong></span>
                    </div>
                    ${data.calculation_id ? `
                        <div class="calculation-id">
                            <i class="fas fa-database"></i>
                            <span>Saved as ID: <strong>${data.calculation_id}</strong></span>
                        </div>
                    ` : ''}
                </div>
            `;
        }

        // Show results section
        this.showResults();

        // Scroll to results
        document.getElementById('resultsSection')?.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }

    formatNumber(num) {
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 2
        }).format(num);
    }

    // Show notification without forcing login
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
        `;

        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '15px 20px',
            borderRadius: '10px',
            color: 'white',
            fontWeight: 'bold',
            zIndex: '10000',
            maxWidth: '400px',
            background: type === 'success' ? '#4CAF50' : type === 'warning' ? '#FF9800' : '#2196F3',
            boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
            animation: 'slideIn 0.3s ease'
        });

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    showLoading() {
        const loading = document.getElementById('loading');
        const calcBtn = document.getElementById('calculateBtn');

        if (loading) loading.classList.remove('hidden');
        if (calcBtn) {
            calcBtn.disabled = true;
            calcBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Calculating...';
        }
    }

    hideLoading() {
        const loading = document.getElementById('loading');
        const calcBtn = document.getElementById('calculateBtn');

        if (loading) loading.classList.add('hidden');
        if (calcBtn) {
            calcBtn.disabled = false;
            calcBtn.innerHTML = '<i class="fas fa-calculator"></i> Calculate Water Harvest';
        }
    }

    showError(message) {
        const errorText = document.getElementById('errorText');
        const errorMessage = document.getElementById('errorMessage');

        if (errorText) errorText.textContent = message;
        if (errorMessage) errorMessage.classList.remove('hidden');

        // Auto-hide error after 8 seconds
        setTimeout(() => this.hideError(), 8000);
    }

    hideError() {
        const errorMessage = document.getElementById('errorMessage');
        if (errorMessage) errorMessage.classList.add('hidden');
    }

    showResults() {
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) resultsSection.classList.remove('hidden');
    }

    hideResults() {
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) resultsSection.classList.add('hidden');
    }

    resetCalculator() {
        // Clear form
        document.getElementById('calculatorForm')?.reset();

        // Clear search
        const searchInput = document.getElementById('districtSearch');
        if (searchInput) searchInput.value = '';
        this.clearSearchResults();

        // Hide results and errors
        this.hideResults();
        this.hideError();

        // Focus on district input
        document.getElementById('district')?.focus();
    }

    saveResults() {
        // Simple save functionality
        const resultData = {
            district: document.getElementById('resultDistrict')?.textContent,
            water_harvest: document.getElementById('resultWaterLiters')?.textContent,
            timestamp: new Date().toISOString()
        };

        console.log('💾 Saving results:', resultData);
        localStorage.setItem('jaljeevai_last_calculation', JSON.stringify(resultData));

        this.showNotification('Results saved to local storage! 📁', 'success');
    }
}

// Initialize calculator when page loads
const calculator = new RainwaterCalculatorDemo();

// Make calculator available globally for onclick functions
window.calculator = calculator;

// Add CSS for animations and styling
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    .hidden { display: none; }
    .error { color: red; font-weight: bold; }
    .status-indicator.online { background-color: #4caf50; }
    .status-indicator.offline { background-color: #f44336; }
    
    .calculation-meta {
        background: #f5f5f5;
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
        display: flex;
        gap: 20px;
        align-items: center;
    }
    
    .user-badge, .calculation-id {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.9em;
    }
`;
document.head.appendChild(style);

console.log('🌧️ RainwaterCalculatorDemo loaded (without login status checks)');
