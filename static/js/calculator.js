class RainwaterCalculatorDemo {
    constructor() {
        this.baseURL = 'http://127.0.0.1:8000';
        this.apiURL = '/api/v1';
        this.currentCalculationData = null;
        this.isSaved = false;  // ✅ NEW: Track save state
        this.init();
    }

    init() {
        this.bindEvents();
        this.setupRoofTypeDropdown();
        this.setupDistrictSearch();
        this.checkAPIStatus();
        console.log('🚀 Rainwater Calculator initialized');
    }

    setupDistrictSearch() {
        const searchInput = document.getElementById('districtSearch');
        if (searchInput) {
            searchInput.addEventListener('input', async () => {
                const searchTerm = searchInput.value.trim();
                if (searchTerm.length < 1) {
                    this.clearSearchResults();
                    return;
                }

                try {
                    const response = await fetch(`${this.baseURL}${this.apiURL}/districts/?search=${encodeURIComponent(searchTerm)}`);
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

    setupRoofTypeDropdown() {
        const toggle = document.getElementById('roofTypeToggle');
        const menu = document.querySelector('.dropdown-menu');
        const options = document.querySelectorAll('.dropdown-option');
        const hiddenInput = document.getElementById('roofType');
        const selectedOption = document.querySelector('.selected-option');
        
        if (!toggle) return;
        
        // Toggle dropdown
        toggle.addEventListener('click', (e) => {
            e.stopPropagation();
            menu.classList.toggle('show');
            toggle.classList.toggle('active');
        });
        
        // Select option
        options.forEach(option => {
            option.addEventListener('click', () => {
                const value = option.getAttribute('data-value');
                const text = option.textContent;
                
                hiddenInput.value = value;
                selectedOption.textContent = text;
                
                menu.classList.remove('show');
                toggle.classList.remove('active');
                
                hiddenInput.setCustomValidity('');
            });
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!toggle.contains(e.target) && !menu.contains(e.target)) {
                menu.classList.remove('show');
                toggle.classList.remove('active');
            }
        });
    }

    bindEvents() {
        // Search functionality
        document.getElementById('searchBtn')?.addEventListener('click', () => this.performSearch());
        
        // Form submission
        document.getElementById('calculatorForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.calculateHarvest();
        });
        
        // Action buttons
        document.getElementById('newCalculation')?.addEventListener('click', () => this.resetCalculator());
        document.getElementById('saveResults')?.addEventListener('click', () => this.saveResults());
        document.getElementById('downloadResults')?.addEventListener('click', () => this.downloadResults());
        document.getElementById('shareResults')?.addEventListener('click', () => this.shareResults());
    }

    async performSearch() {
        const searchTerm = document.getElementById('districtSearch')?.value.trim();
        if (!searchTerm || searchTerm.length < 2) {
            this.showSearchError('Please enter at least 2 characters to search');
            return;
        }
        
        try {
            const response = await fetch(`${this.baseURL}${this.apiURL}/districts/?search=${encodeURIComponent(searchTerm)}`);
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
    }

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
            district_name: formData.get('district_name')?.trim(),
            length: parseFloat(formData.get('length')),
            width: parseFloat(formData.get('width')),
            roof_type: formData.get('roof_type'),
            number_of_dwellers: parseInt(formData.get('number_of_dwellers'))
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

            // ✅ MODIFIED: Only calculate, don't auto-save
            const response = await fetch(`${this.baseURL}${this.apiURL}/calculate/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken || '',
                },
                credentials: 'same-origin',
                body: JSON.stringify(data)
            });

            const result = await response.json();
            console.log('📥 API Response:', result);

            if (response.ok && result.success) {
                this.currentCalculationData = result.data;
                this.isSaved = false;  // ✅ Mark as not saved
                
                // ✅ REMOVED: Auto-save notification (no longer auto-saves)
                
                this.displayResults(result.data);
                this.loadRainfallChart(result.data.district_name);
                this.updateSaveButtonState();  // ✅ Update save button
                this.setAPIStatus('online', 'Connected');
            } else {
                let errorMessage = result.error || 'Calculation failed';
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
        if (isNaN(data.number_of_dwellers) || data.number_of_dwellers <= 0) {
            this.showError('Please enter a valid number of dwellers (at least 1).');
            return false;
        }
        if (!data.roof_type) {
            this.showError('Please select a roof type.');
            return false;
        }

<<<<<<< HEAD
        if (isNaN(data.tank_cost_per_liter) || data.tank_cost_per_liter < 0) {
            this.showError('Please enter a valid tank cost per liter.');
            return false;
        }

        if (isNaN(data.installation_fixed_costs) || data.installation_fixed_costs < 0) {
            this.showError('Please enter valid installation fixed costs.');
            return false;
        }

        if (isNaN(data.cost_per_kiloliter) || data.cost_per_kiloliter < 0) {
            this.showError('Please enter a valid cost per kiloliter.');
            return false;
        }

=======
>>>>>>> parent of 74879fa (calculator page new 4 inputs)
        return true;
    }

    displayResults(data) {
        // Basic information
        document.getElementById('resultDistrict').textContent = data.district_name;
        document.getElementById('resultState').textContent = data.state;
        document.getElementById('resultRainfall').textContent = `${this.formatNumber(data.annual_rainfall_mm)} mm/year`;
        document.getElementById('resultDwellers').textContent = data.number_of_dwellers;

        // Roof specifications
        document.getElementById('resultRoofArea').textContent = `${this.formatNumber(data.roof_area_sqm)} m²`;
        document.getElementById('resultRoofType').textContent = data.roof_type;
        document.getElementById('resultRunoffCoeff').textContent = data.runoff_coefficient;

        // Water harvest results
        document.getElementById('resultWaterLiters').textContent = `${this.formatNumber(data.water_harvested_liters)} L/year`;
        document.getElementById('resultWaterGallons').textContent = `${this.formatNumber(data.water_harvested_gallons)} gal/year`;
        
        // Efficiency display
        const efficiency = data.efficiency_percent || 0;
        document.getElementById('resultEfficiency').textContent = `${efficiency.toFixed(1)}%`;
        
        // Color-code efficiency
        const efficiencyElement = document.getElementById('resultEfficiency');
        if (efficiency >= 80) {
            efficiencyElement.className = 'value efficiency excellent';
        } else if (efficiency >= 50) {
            efficiencyElement.className = 'value efficiency good';
        } else {
            efficiencyElement.className = 'value efficiency limited';
        }

        // Usage analysis  
        document.getElementById('resultDailyUsage').textContent = `${this.formatNumber(data.daily_requirement_liters)} L/day`;
        document.getElementById('resultAnnualUsage').textContent = `${this.formatNumber(data.annual_requirement_liters)} L/year`;
        
        // Water security level
        const securityLevel = this.getWaterSecurityLevel(efficiency);
        document.getElementById('resultWaterSecurity').textContent = securityLevel.text;
        document.getElementById('resultWaterSecurity').className = `value security-level ${securityLevel.class}`;

        // Recommendation
        document.getElementById('resultRecommendation').textContent = data.recommendation;

        // ✅ MODIFIED: Only show metadata if actually saved
        // ✅ Show metadata if user exists (saved or not)
        if (data.user) {  // Changed from: if (data.calculation_id && data.is_saved)
            document.getElementById('calculationMeta').style.display = 'block';
            
            // Only show calculation ID if it exists
            if (data.calculation_id) {
                document.getElementById('resultCalculationId').textContent = data.calculation_id;
            } else {
                document.getElementById('resultCalculationId').textContent = 'Not saved yet';
            }
            
            // Always show username for authenticated users
            if (data.user) {
                document.getElementById('resultUser').textContent = data.user;
            }
            
            document.getElementById('resultTimestamp').textContent = new Date().toLocaleString();
        } else {
            document.getElementById('calculationMeta').style.display = 'none';
        }


        // Update water level visualization
        this.updateWaterVisualization(efficiency);

        // Show results section
        this.showResults();

        // Scroll to results
        document.getElementById('resultsSection')?.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }

    loadRainfallChart(districtName) {
        const chartImg = document.getElementById('rainfallChart');
        const chartLoading = document.getElementById('chartLoading');
        const chartError = document.getElementById('chartError');
        
        if (!chartImg) return;
        
        // Show loading state
        if (chartLoading) chartLoading.style.display = 'block';
        if (chartError) chartError.style.display = 'none';
        chartImg.style.display = 'none';
        
        // Set chart source URL
        const chartUrl = `${this.baseURL}${this.apiURL}/chart/${encodeURIComponent(districtName)}/`;
        chartImg.src = chartUrl;
        
        // Handle successful load
        chartImg.onload = () => {
            if (chartLoading) chartLoading.style.display = 'none';
            if (chartError) chartError.style.display = 'none';
            chartImg.style.display = 'block';
            console.log('✅ Rainfall chart loaded successfully');
        };
        
        // Handle load error
        chartImg.onerror = () => {
            if (chartLoading) chartLoading.style.display = 'none';
            if (chartError) chartError.style.display = 'block';
            chartImg.style.display = 'none';
            console.warn('⚠️ Failed to load rainfall chart for:', districtName);
        };
    }

    getWaterSecurityLevel(efficiency) {
        if (efficiency >= 100) {
            return { text: 'Complete Water Independence', class: 'excellent' };
        } else if (efficiency >= 70) {
            return { text: 'High Water Security', class: 'good' };
        } else if (efficiency >= 40) {
            return { text: 'Moderate Water Security', class: 'moderate' };
        } else if (efficiency >= 20) {
            return { text: 'Limited Water Security', class: 'limited' };
        } else {
            return { text: 'Low Water Security', class: 'low' };
        }
    }

    updateWaterVisualization(efficiencyPercent) {
        const waterLevel = document.getElementById('waterLevel');
        if (waterLevel) {
            const level = Math.min(100, Math.max(0, efficiencyPercent));
            waterLevel.style.height = `${level}%`;
            
            // Color coding based on efficiency
            if (level >= 80) {
                waterLevel.style.backgroundColor = '#4CAF50'; // Green
            } else if (level >= 50) {
                waterLevel.style.backgroundColor = '#FF9800'; // Orange
            } else {
                waterLevel.style.backgroundColor = '#2196F3'; // Blue
            }
        }
    }

    formatNumber(num) {
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 2
        }).format(num);
    }

    async checkAPIStatus() {
        try {
            const response = await fetch(`${this.baseURL}${this.apiURL}/districts/`);
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

    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return decodeURIComponent(value);
            }
        }
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute('content') : null;
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="notification-close">×</button>
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
            animation: 'slideInRight 0.3s ease'
        });
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 6000);
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
        
        setTimeout(() => this.hideError(), 10000);
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
        const form = document.getElementById('calculatorForm');
        if (form) {
            form.reset();
            
            // Reset custom dropdown
            const selectedOption = document.querySelector('.selected-option');
            const hiddenInput = document.getElementById('roofType');
            if (selectedOption) selectedOption.textContent = 'Select Roof Type';
            if (hiddenInput) hiddenInput.value = '';
        }
        
        // Clear search
        const searchInput = document.getElementById('districtSearch');
        if (searchInput) searchInput.value = '';
        this.clearSearchResults();
        
        // Hide results and errors
        this.hideResults();
        this.hideError();
        
        // ✅ MODIFIED: Reset save state
        this.currentCalculationData = null;
        this.isSaved = false;
        this.updateSaveButtonState();
        
        // Hide metadata
        const metaDiv = document.getElementById('calculationMeta');
        if (metaDiv) metaDiv.style.display = 'none';
        
        // Reset chart
        const chartImg = document.getElementById('rainfallChart');
        const chartLoading = document.getElementById('chartLoading');
        const chartError = document.getElementById('chartError');
        
        if (chartImg) chartImg.src = '';
        if (chartLoading) chartLoading.style.display = 'none';
        if (chartError) chartError.style.display = 'none';
        
        // Focus on district input
        document.getElementById('district')?.focus();
    }

    // ✅ COMPLETELY REWRITTEN: New save logic that prevents duplicates
    async saveResults() {
        if (!this.currentCalculationData) {
            this.showNotification('No calculation data to save. Please perform a calculation first.', 'warning');
            return;
        }

        if (this.isSaved) {
            this.showNotification('Results already saved! ✅', 'info');
            return;
        }

        try {
            const response = await fetch(`${this.baseURL}${this.apiURL}/save/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                credentials: 'same-origin',
                body: JSON.stringify(this.currentCalculationData)
            });

            const result = await response.json();

            if (result.success) {
                this.isSaved = true;  // ✅ Mark as saved
                this.currentCalculationData.calculation_id = result.calculation_id;
                this.currentCalculationData.is_saved = true;
                
                this.updateSaveButtonState();  // ✅ Update button state
                this.showNotification('✅ Results saved successfully! 📁', 'success');
                
                // Update metadata display
                document.getElementById('calculationMeta').style.display = 'block';
                document.getElementById('resultCalculationId').textContent = result.calculation_id;
                document.getElementById('resultTimestamp').textContent = new Date().toLocaleString();
            } else {
                this.showNotification(result.error || 'Failed to save results. Please try again.', 'warning');
            }
        } catch (error) {
            console.error('Save error:', error);
            this.showNotification('Connection error. Please try again later.', 'warning');
        }
    }

    // ✅ NEW: Update save button state based on isSaved
    updateSaveButtonState() {
        const saveBtn = document.getElementById('saveResults');
        if (saveBtn) {
            if (this.isSaved) {
                saveBtn.innerHTML = '<i class="fas fa-check"></i> Saved';
                saveBtn.disabled = true;
                saveBtn.classList.add('saved');
                saveBtn.style.background = '#28a745';
                saveBtn.style.cursor = 'not-allowed';
            } else if (this.currentCalculationData) {
                saveBtn.innerHTML = '<i class="fas fa-save"></i> Save Results';
                saveBtn.disabled = false;
                saveBtn.classList.remove('saved');
                saveBtn.style.background = '';
                saveBtn.style.cursor = '';
            }
        }
    }

    downloadResults() {
        if (!this.currentCalculationData) {
            this.showNotification('No data to download. Please perform a calculation first.', 'warning');
            return;
        }

        // Create downloadable content
        const content = this.generateReportContent();
        const blob = new Blob([content], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `Rainwater_Harvest_Report_${this.currentCalculationData.district_name}_${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        this.showNotification('📄 Report downloaded successfully!', 'success');
    }

    generateReportContent() {
        const data = this.currentCalculationData;
        return `
RAINWATER HARVESTING CALCULATION REPORT
=======================================

Location Information:
- District: ${data.district_name}
- State: ${data.state}
- Annual Rainfall: ${data.annual_rainfall_mm} mm/year

Roof Specifications:
- Roof Area: ${data.roof_area_sqm} m²
- Roof Type: ${data.roof_type}
- Runoff Coefficient: ${data.runoff_coefficient}

Household Information:
- Number of Dwellers: ${data.number_of_dwellers}

Water Harvesting Results:
- Annual Water Harvest: ${this.formatNumber(data.water_harvested_liters)} L/year
- In Gallons: ${this.formatNumber(data.water_harvested_gallons)} gal/year
- System Efficiency: ${(data.efficiency_percent || 0).toFixed(1)}%

Water Usage Analysis:
- Daily Requirement: ${this.formatNumber(data.daily_requirement_liters)} L/day
- Annual Requirement: ${this.formatNumber(data.annual_requirement_liters)} L/year

Expert Recommendation:
${data.recommendation}

Report Generated: ${new Date().toLocaleString()}
Generated by: JalJeevan.AI - Rainwater Harvesting Calculator
        `.trim();
    }

    shareResults() {
        if (!this.currentCalculationData) {
            this.showNotification('No data to share. Please perform a calculation first.', 'warning');
            return;
        }

        const shareData = {
            title: 'JalJeevan.AI - My Rainwater Harvesting Results',
            text: `I can harvest ${this.formatNumber(this.currentCalculationData.water_harvested_liters)}L of rainwater annually from my ${this.formatNumber(this.currentCalculationData.roof_area_sqm)}m² roof in ${this.currentCalculationData.district_name}!`,
            url: window.location.href
        };

        if (navigator.share) {
            navigator.share(shareData);
        } else {
            // Fallback: Copy to clipboard
            const shareText = `${shareData.text}\n\nCalculate your rainwater harvesting potential at: ${shareData.url}`;
            navigator.clipboard.writeText(shareText).then(() => {
                this.showNotification('📋 Results copied to clipboard!', 'success');
            }).catch(() => {
                this.showNotification('Unable to share. Please copy the URL manually.', 'warning');
            });
        }
    }
}

// Initialize calculator when page loads
const calculator = new RainwaterCalculatorDemo();

// Make calculator available globally for onclick functions
window.calculator = calculator;

// Add CSS animations and styling
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    .hidden { display: none !important; }
    .notification { font-family: 'Exo 2', sans-serif; }
    .notification-close {
        background: none;
        border: none;
        color: white;
        font-size: 18px;
        cursor: pointer;
        margin-left: 10px;
    }
    
    .status-indicator.online { color: #4caf50; }
    .status-indicator.offline { color: #f44336; }
    
    /* Efficiency color coding */
    .efficiency.excellent { color: #4CAF50; font-weight: bold; }
    .efficiency.good { color: #FF9800; font-weight: bold; }
    .efficiency.limited { color: #f44336; font-weight: bold; }
    
    /* Security level color coding */
    .security-level.excellent { color: #4CAF50; }
    .security-level.good { color: #8BC34A; }
    .security-level.moderate { color: #FF9800; }
    .security-level.limited { color: #FF5722; }
    .security-level.low { color: #f44336; }
    
    /* Chart styling */
    .chart-container {
        position: relative;
        min-height: 300px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .chart-loading, .chart-error {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 10px;
        color: #6c757d;
        font-size: 0.9em;
    }
    
    .chart-loading i {
        font-size: 1.5em;
        color: #007bff;
    }
    
    .chart-error i {
        font-size: 1.5em;
        color: #dc3545;
    }
    
    #rainfallChart {
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: opacity 0.3s ease;
    }
    
    /* Save button states */
    .btn.saved {
        background: #28a745 !important;
        cursor: not-allowed !important;
        opacity: 0.8;
    }
    
    .btn.saved:hover {
        transform: none !important;
        box-shadow: none !important;
    }
`;
document.head.appendChild(style);

console.log('🌧️ RainwaterCalculatorDemo fully loaded with separate calculate/save logic! 💧');
