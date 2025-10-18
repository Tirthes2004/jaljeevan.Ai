class RainwaterCalculatorDemo {
    constructor() {
        this.baseURL = 'http://127.0.0.1:8000';
        this.apiURL = '/api/v1';
        this.currentCalculationData = null;
        this.isSaved = false;
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
                this.isSaved = false;
                
                this.displayResults(result.data);
                
                // Add chart monitoring
                this.monitorChartLoading();
                
                // Use preloading for better reliability
                this.preloadCharts(
                    result.data.district_name,
                    result.data.roof_area_sqm,
                    result.data.roof_type,
                    result.data.number_of_dwellers
                );
                
                this.updateSaveButtonState();
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
        return true;
    }

    displayResults(data) {
        try {
            console.log('📊 Displaying results with data:', data);

            // Basic Information
            document.getElementById('resultDistrict').textContent = data.district_name || 'Unknown';
            document.getElementById('resultState').textContent = data.state || 'Not specified';
            document.getElementById('resultRainfall').textContent = `${this.formatNumber(data.annual_rainfall_mm || 0)} mm/year`;
            document.getElementById('resultDwellers').textContent = data.number_of_dwellers || 0;

            // Roof Specifications
            document.getElementById('resultRoofArea').textContent = `${this.formatNumber(data.roof_area_sqm || 0)} m²`;
            document.getElementById('resultRoofType').textContent = data.roof_type || 'Unknown';
            document.getElementById('resultRunoffCoeff').textContent = data.runoff_coefficient || 0;

            // Water Harvest Results
            document.getElementById('resultWaterLiters').textContent = `${this.formatNumber(data.water_harvested_liters || 0)} L/year`;
            document.getElementById('resultWaterGallons').textContent = `${this.formatNumber(data.water_harvested_gallons || 0)} gal/year`;
            
            // Efficiency Display
            const efficiency = data.efficiency_percent || 0;
            document.getElementById('resultEfficiency').textContent = `${efficiency.toFixed(1)}%`;
            
            // Color-code efficiency
            const efficiencyElement = document.getElementById('resultEfficiency');
            if (efficiencyElement) {
                if (efficiency >= 80) {
                    efficiencyElement.className = 'value efficiency excellent';
                } else if (efficiency >= 50) {
                    efficiencyElement.className = 'value efficiency good';
                } else {
                    efficiencyElement.className = 'value efficiency limited';
                }
            }

            // Usage Analysis
            document.getElementById('resultDailyUsage').textContent = `${this.formatNumber(data.daily_requirement_liters || 0)} L/day`;
            document.getElementById('resultAnnualUsage').textContent = `${this.formatNumber(data.annual_requirement_liters || 0)} L/year`;
            
            // Water security level
            const securityLevel = this.getWaterSecurityLevel(efficiency);
            const securityElement = document.getElementById('resultWaterSecurity');
            if (securityElement) {
                securityElement.textContent = securityLevel.text;
                securityElement.className = `value security-level ${securityLevel.class}`;
            }

            // Recommendation
            const recommendationElement = document.getElementById('resultRecommendation');
            if (recommendationElement) {
                recommendationElement.textContent = data.recommendation || 'No recommendation available';
            }

            // Metadata Display
            if (data.user) {
                const metaElement = document.getElementById('calculationMeta');
                if (metaElement) {
                    metaElement.style.display = 'block';
                    
                    const calcIdElement = document.getElementById('resultCalculationId');
                    if (calcIdElement) {
                        calcIdElement.textContent = data.calculation_id ? data.calculation_id : 'Not saved yet';
                    }
                    
                    const userElement = document.getElementById('resultUser');
                    if (userElement) {
                        userElement.textContent = data.user;
                    }
                    
                    const timestampElement = document.getElementById('resultTimestamp');
                    if (timestampElement) {
                        timestampElement.textContent = new Date().toLocaleString();
                    }
                }
            } else {
                const metaElement = document.getElementById('calculationMeta');
                if (metaElement) {
                    metaElement.style.display = 'none';
                }
            }

            // Cost Analysis Display
            if (data.costs) {
                console.log('💰 Displaying cost analysis:', data.costs);
                
                const installCostEl = document.getElementById('resultInstallCost');
                if (installCostEl) {
                    installCostEl.textContent = `₹${this.formatNumber(data.costs.total_install_cost || 0)}`;
                }
                
                const annualSavingsEl = document.getElementById('resultAnnualSavings');
                if (annualSavingsEl) {
                    annualSavingsEl.textContent = `₹${this.formatNumber(data.costs.net_annual_savings || 0)}`;
                }
                
                const paybackEl = document.getElementById('resultPayback');
                if (paybackEl) {
                    paybackEl.textContent = data.costs.payback_years ? `${data.costs.payback_years} years` : 'Long-term benefits';
                }
                
                const roiEl = document.getElementById('resultROI');
                if (roiEl) {
                    roiEl.textContent = `${data.costs.roi_percentage || 0}%`;
                }
                
                // Cost breakdown
                const costBreakdownEl = document.getElementById('resultCostBreakdown');
                if (costBreakdownEl) {
                    costBreakdownEl.innerHTML = `
                        Tank: ₹${this.formatNumber(data.costs.tank_construction_cost || 0)} | 
                        Pit: ₹${this.formatNumber(data.costs.pit_construction_cost || 0)} | 
                        Installation: ₹${this.formatNumber(data.costs.installation_fixed_costs || 0)}
                    `;
                }
            } else {
                console.log('ℹ️ No cost analysis data available');
            }

            // Technical Specifications Display
            if (data.tank_volume_liters) {
                console.log('🔧 Displaying technical specifications');
                
                const tankVolumeEl = document.getElementById('resultTankVolume');
                if (tankVolumeEl) {
                    tankVolumeEl.textContent = `${this.formatNumber(data.tank_volume_liters)} L (${data.tank_volume_m3 || 0} m³)`;
                }
                
                const firstFlushEl = document.getElementById('resultFirstFlush');
                if (firstFlushEl) {
                    firstFlushEl.textContent = `${this.formatNumber(data.first_flush_liters || 0)} L`;
                }
                
                const pitDiameterEl = document.getElementById('resultPitDiameter');
                if (pitDiameterEl) {
                    pitDiameterEl.textContent = `${data.pit_diameter_m || 0} m`;
                }
                
                const rechargeVolumeEl = document.getElementById('resultRechargeVolume');
                if (rechargeVolumeEl) {
                    rechargeVolumeEl.textContent = `${this.formatNumber(data.available_recharge_liters || 0)} L`;
                }
            } else {
                console.log('ℹ️ No technical specifications data available');
            }

            // Enhanced Recommendations Display
            if (data.enhanced_recommendations && Array.isArray(data.enhanced_recommendations)) {
                console.log('Displaying enhanced recommendations:', data.enhanced_recommendations);
                
                const enhancedRecEl = document.getElementById('resultEnhancedRecommendations');
                if (enhancedRecEl) {
                    enhancedRecEl.innerHTML = '<ul>' + 
                        data.enhanced_recommendations.map(rec => `<li>${rec}</li>`).join('') + 
                        '</ul>';
                }
            } else {
                console.log('ℹ️ No enhanced recommendations available');
            }

            // Water visualization and display
            this.updateWaterVisualization(efficiency);
            this.showResults();

            // Scroll behavior
            const resultsSection = document.getElementById('resultsSection');
            if (resultsSection) {
                resultsSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }

            console.log('✅ Results displayed successfully with enhanced features!');

        } catch (error) {
            console.error('❌ Error in displayResults:', error);
            console.log('📊 Failed with data:', data);
            
            // Show error but still try to display basic results
            this.showError('Results calculated successfully, but some display features encountered issues.');
            
            // Fallback: Show at least basic results
            try {
                const districtEl = document.getElementById('resultDistrict');
                if (districtEl) districtEl.textContent = data.district_name || 'Unknown';
                
                const waterEl = document.getElementById('resultWaterLiters');
                if (waterEl) waterEl.textContent = `${this.formatNumber(data.water_harvested_liters || 0)} L/year`;
                
                const efficiencyEl = document.getElementById('resultEfficiency');
                if (efficiencyEl) efficiencyEl.textContent = `${(data.efficiency_percent || 0).toFixed(1)}%`;
                
                this.showResults();
            } catch (fallbackError) {
                console.error('❌ Fallback display also failed:', fallbackError);
            }
        }
    }

    // ✅ IMPROVED CHART LOADING WITH TIMEOUT AND RETRY
    preloadCharts(districtName, roofArea, roofType, dwellers) {
        console.log('🔄 Preloading charts...');
        
        // Preload both chart URLs to warm up the server
        const rainfallUrl = `${this.baseURL}${this.apiURL}/chart/${encodeURIComponent(districtName)}/?t=${Date.now()}`;
        const harvestUrl = `${this.baseURL}${this.apiURL}/chart/line/${encodeURIComponent(districtName)}/?area=${roofArea}&roof_type=${encodeURIComponent(roofType)}&people=${dwellers}&t=${Date.now()}`;
        
        // Create invisible img elements to preload
        const preloadRainfall = new Image();
        const preloadHarvest = new Image();
        
        preloadRainfall.onload = () => console.log('✅ Rainfall chart preloaded');
        preloadRainfall.onerror = () => console.warn('⚠️ Rainfall chart preload failed');
        preloadRainfall.src = rainfallUrl;
        
        preloadHarvest.onload = () => console.log('✅ Harvest chart preloaded');
        preloadHarvest.onerror = () => console.warn('⚠️ Harvest chart preload failed');
        preloadHarvest.src = harvestUrl;
        
        // Load actual charts after a short delay
        setTimeout(() => {
            this.loadRainfallChart(districtName);
            this.loadHarvestConsumptionChart(districtName, roofArea, roofType, dwellers);
        }, 1000);
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
        
        // Set chart source URL with cache busting
        const chartUrl = `${this.baseURL}${this.apiURL}/chart/${encodeURIComponent(districtName)}/?t=${Date.now()}`;
        chartImg.src = chartUrl;
        
        // ✅ Add timeout fallback
        const timeout = setTimeout(() => {
            console.warn('⏰ Rainfall chart loading timeout');
            if (chartLoading) chartLoading.style.display = 'none';
            if (chartError) {
                chartError.style.display = 'block';
                chartError.innerHTML = `
                    <i class="fas fa-exclamation-triangle"></i>
                    <span>Chart loading timeout. <button onclick="calculator.loadRainfallChart('${districtName}')" style="margin-left: 10px; padding: 5px 10px; cursor: pointer; border: 1px solid #ccc; background: #f8f9fa; border-radius: 4px;">Retry</button></span>
                `;
            }
            chartImg.style.display = 'none';
        }, 15000); // 15 second timeout
        
        // Handle successful load
        chartImg.onload = () => {
            clearTimeout(timeout);
            if (chartLoading) chartLoading.style.display = 'none';
            if (chartError) chartError.style.display = 'none';
            chartImg.style.display = 'block';
            console.log('✅ Rainfall chart loaded successfully');
        };
        
        // Handle load error
        chartImg.onerror = () => {
            clearTimeout(timeout);
            console.error('❌ Rainfall chart failed to load');
            if (chartLoading) chartLoading.style.display = 'none';
            if (chartError) {
                chartError.style.display = 'block';
                chartError.innerHTML = `
                    <i class="fas fa-exclamation-triangle"></i>
                    <span>Chart not available. <button onclick="calculator.loadRainfallChart('${districtName}')" style="margin-left: 10px; padding: 5px 10px; cursor: pointer; border: 1px solid #ccc; background: #f8f9fa; border-radius: 4px;">Retry</button></span>
                `;
            }
            chartImg.style.display = 'none';
        };
    }

    loadHarvestConsumptionChart(districtName, roofArea, roofType, dwellers) {
        const chartImg = document.getElementById('harvestConsumptionChart');
        const chartLoading = document.getElementById('harvestConsumptionChartLoading');
        const chartError = document.getElementById('harvestConsumptionChartError');
        
        if (!chartImg || !chartLoading || !chartError) {
            console.error('❌ Harvest chart elements not found in DOM');
            return;
        }
        
        // Show loading state
        chartLoading.style.display = 'block';
        chartError.style.display = 'none';
        chartImg.style.display = 'none';
        
        // Set chart source URL with cache busting
        const chartUrl = `${this.baseURL}${this.apiURL}/chart/line/${encodeURIComponent(districtName)}/?area=${roofArea}&roof_type=${encodeURIComponent(roofType)}&people=${dwellers}&t=${Date.now()}`;
        
        console.log('🔍 Loading harvest chart URL:', chartUrl);
        
        // ✅ Add timeout fallback
        const timeout = setTimeout(() => {
            console.warn('⏰ Harvest chart loading timeout');
            chartLoading.style.display = 'none';
            chartError.style.display = 'block';
            chartError.innerHTML = `
                <i class="fas fa-exclamation-triangle"></i>
                <span>Chart loading timeout. <button onclick="calculator.loadHarvestConsumptionChart('${districtName}', ${roofArea}, '${roofType}', ${dwellers})" style="margin-left: 10px; padding: 5px 10px; cursor: pointer; border: 1px solid #ccc; background: #f8f9fa; border-radius: 4px;">Retry</button></span>
            `;
            chartImg.style.display = 'none';
        }, 15000); // 15 second timeout
        
        chartImg.src = chartUrl;
        
        // Handle successful load
        chartImg.onload = () => {
            clearTimeout(timeout);
            console.log('✅ Harvest chart loaded successfully');
            chartLoading.style.display = 'none';
            chartError.style.display = 'none';
            chartImg.style.display = 'block';
        };
        
        // Handle load error
        chartImg.onerror = () => {
            clearTimeout(timeout);
            console.error('❌ Harvest chart failed to load');
            chartLoading.style.display = 'none';
            chartError.style.display = 'block';
            chartError.innerHTML = `
                <i class="fas fa-exclamation-triangle"></i>
                <span>Chart not available. <button onclick="calculator.loadHarvestConsumptionChart('${districtName}', ${roofArea}, '${roofType}', ${dwellers})" style="margin-left: 10px; padding: 5px 10px; cursor: pointer; border: 1px solid #ccc; background: #f8f9fa; border-radius: 4px;">Retry</button></span>
            `;
            chartImg.style.display = 'none';
        };
    }

    monitorChartLoading() {
        // Check if both charts are loading for too long
        setTimeout(() => {
            const rainfallLoading = document.getElementById('chartLoading');
            const harvestLoading = document.getElementById('harvestConsumptionChartLoading');
            
            if (rainfallLoading && rainfallLoading.style.display !== 'none') {
                console.warn('🚨 Rainfall chart still loading after 10 seconds');
            }
            
            if (harvestLoading && harvestLoading.style.display !== 'none') {
                console.warn('🚨 Harvest chart still loading after 10 seconds');
            }
        }, 10000);
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
        
        // Reset save state
        this.currentCalculationData = null;
        this.isSaved = false;
        this.updateSaveButtonState();
        
        // Hide metadata
        const metaDiv = document.getElementById('calculationMeta');
        if (metaDiv) metaDiv.style.display = 'none';
        
        // Reset rainfall chart
        const chartImg = document.getElementById('rainfallChart');
        const chartLoading = document.getElementById('chartLoading');
        const chartError = document.getElementById('chartError');
        
        if (chartImg) chartImg.src = '';
        if (chartLoading) chartLoading.style.display = 'none';
        if (chartError) chartError.style.display = 'none';
        
        // Reset harvest vs consumption chart
        const harvestChartImg = document.getElementById('harvestConsumptionChart');
        const harvestChartLoading = document.getElementById('harvestConsumptionChartLoading');
        const harvestChartError = document.getElementById('harvestConsumptionChartError');

        if (harvestChartImg) harvestChartImg.src = '';
        if (harvestChartLoading) harvestChartLoading.style.display = 'none';
        if (harvestChartError) harvestChartError.style.display = 'none';
        
        // Focus on district input
        document.getElementById('district')?.focus();
    }

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
                this.isSaved = true;
                this.currentCalculationData.calculation_id = result.calculation_id;
                this.currentCalculationData.is_saved = true;
                
                this.updateSaveButtonState();
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

    try {
        if (typeof window.jspdf === 'undefined') {
            this.showNotification('PDF library not loaded. Please refresh the page.', 'warning');
            return;
        }

        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        
        const data = this.currentCalculationData;
        
        // ✅ EXTRACT CORRECT VALUES FROM ENHANCED RECOMMENDATIONS
        const costData = this.extractCostFromEnhanced(data);
        
        console.log('📊 Using cost data:', costData);
        
        const currentDate = new Date().toLocaleDateString('en-IN', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });

        doc.setProperties({
            title: 'Rainwater Harvesting Report',
            subject: 'Calculation Results',
            author: 'JalJeevan.AI',
            keywords: 'rainwater, harvesting, calculator',
            creator: 'JalJeevan.AI'
        });

        // ============ HEADER - CENTERED WITHOUT LOGO ============
        doc.setFillColor(30, 60, 114);
        doc.rect(0, 0, 210, 40, 'F');

        doc.setTextColor(255, 255, 255);
        doc.setFontSize(32);
        doc.setFont('helvetica', 'bold');
        doc.text('JALJEEVAN.AI', 105, 20, { align: 'center' });

        doc.setFontSize(11);
        doc.setFont('helvetica', 'normal');
        doc.text('Smart Rainwater Harvesting Calculator', 105, 32, { align: 'center' });


        doc.setTextColor(0, 0, 0);
        doc.setFontSize(9);
        doc.setFont('helvetica', 'italic');
        doc.text(`Report Generated: ${currentDate}`, 14, 50);

        let yPos = 60;

        // ============ LOCATION ============
        this.addSectionHeader(doc, 'LOCATION INFORMATION', yPos);
        yPos += 8;

        doc.autoTable({
            startY: yPos,
            body: [
                ['District:', data.district_name || 'Not specified'],
                ['State:', data.state || 'Not specified'],
                ['Annual Rainfall:', `${this.formatNumber(data.annual_rainfall_mm)} mm/year`],
                ['Number of Dwellers:', `${data.number_of_dwellers} persons`]
            ],
            theme: 'plain',
            styles: { fontSize: 10, cellPadding: 4 },
            columnStyles: {
                0: { fontStyle: 'bold', cellWidth: 70 },
                1: { cellWidth: 110 }
            },
            margin: { left: 18 }
        });

        yPos = doc.lastAutoTable.finalY + 12;

        // ============ ROOF ============
        this.addSectionHeader(doc, 'ROOF SPECIFICATIONS', yPos);
        yPos += 8;

        doc.autoTable({
            startY: yPos,
            body: [
                ['Roof Area:', `${this.formatNumber(data.roof_area_sqm)} m²`],
                ['Roof Type:', data.roof_type || 'Not specified'],
                ['Runoff Coefficient:', data.runoff_coefficient || 'Not specified']
            ],
            theme: 'plain',
            styles: { fontSize: 10, cellPadding: 4 },
            columnStyles: {
                0: { fontStyle: 'bold', cellWidth: 70 },
                1: { cellWidth: 110 }
            },
            margin: { left: 18 }
        });

        yPos = doc.lastAutoTable.finalY + 12;

        // ============ WATER HARVESTING ============
        doc.setFillColor(46, 125, 50);
        doc.rect(14, yPos - 6, 182, 10, 'F');
        doc.setFontSize(14);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(255, 255, 255);
        doc.text('WATER HARVESTING RESULTS', 105, yPos, { align: 'center' });
        yPos += 8;

        doc.autoTable({
            startY: yPos,
            body: [
                ['Annual Water Harvest:', `${this.formatNumber(data.water_harvested_liters)} L/year`],
                ['In Gallons:', `${this.formatNumber(data.water_harvested_gallons)} gal/year`],
                ['System Efficiency:', `${(data.efficiency_percent || 0).toFixed(1)}%`]
            ],
            theme: 'striped',
            styles: { fontSize: 11, cellPadding: 5, fillColor: [232, 245, 233] },
            columnStyles: {
                0: { fontStyle: 'bold', cellWidth: 70, fillColor: [200, 230, 201] },
                1: { fontStyle: 'bold', cellWidth: 110, fontSize: 13 }
            },
            margin: { left: 18 }
        });

        yPos = doc.lastAutoTable.finalY + 12;

        // Page break check
        if (yPos > 200) {
            doc.addPage();
            yPos = 20;
        }

        // ============ COST ANALYSIS (USE EXTRACTED DATA) ============
        if (costData.installCost) {
            doc.setFillColor(255, 152, 0);
            doc.rect(14, yPos - 6, 182, 10, 'F');
            doc.setFontSize(14);
            doc.setFont('helvetica', 'bold');
            doc.setTextColor(255, 255, 255);
            doc.text('COST ANALYSIS & ROI', 105, yPos, { align: 'center' });
            yPos += 8;

            doc.autoTable({
                startY: yPos,
                body: [
                    ['Total Installation Cost:', `Rs ${this.formatNumber(costData.installCost)}`],
                    ['Annual Water Savings:', `Rs ${this.formatNumber(costData.annualSavings)}`],
                    ['Payback Period:', `${costData.paybackYears} years`],
                    ['30-Year ROI:', `${costData.roi}%`]
                ],
                theme: 'striped',
                styles: { fontSize: 10, cellPadding: 5, fillColor: [255, 248, 225] },
                columnStyles: {
                    0: { fontStyle: 'bold', cellWidth: 70, fillColor: [255, 243, 224] },
                    1: { fontStyle: 'bold', cellWidth: 110 }
                },
                margin: { left: 18 }
            });

            yPos = doc.lastAutoTable.finalY + 5;

            // Cost breakdown
            if (data.costs) {
                doc.setFontSize(8);
                doc.setFont('helvetica', 'italic');
                doc.setTextColor(100, 100, 100);
                doc.text(
                    `Breakdown: Tank Rs ${this.formatNumber(data.costs.tank_construction_cost || 0)}, ` +
                    `Pit Rs ${this.formatNumber(data.costs.pit_construction_cost || 0)}, ` +
                    `Installation Rs ${this.formatNumber(data.costs.installation_fixed_costs || 0)}`,
                    20, yPos
                );
                yPos += 12;
            }
        }

        // Page break check
        if (yPos > 210) {
            doc.addPage();
            yPos = 20;
        }

        // ============ WATER USAGE ============
        this.addSectionHeader(doc, 'WATER USAGE ANALYSIS', yPos);
        yPos += 8;

        doc.autoTable({
            startY: yPos,
            body: [
                ['Daily Requirement:', `${this.formatNumber(data.daily_requirement_liters)} L/day`],
                ['Annual Requirement:', `${this.formatNumber(data.annual_requirement_liters)} L/year`],
                ['Available Recharge:', `${this.formatNumber(data.available_recharge_liters)} L/year`],
                ['Water Security Level:', this.getWaterSecurityLevel(data.efficiency_percent || 0).text]
            ],
            theme: 'plain',
            styles: { fontSize: 10, cellPadding: 4 },
            columnStyles: {
                0: { fontStyle: 'bold', cellWidth: 70 },
                1: { cellWidth: 110 }
            },
            margin: { left: 18 }
        });

        yPos = doc.lastAutoTable.finalY + 12;

        // Page break check
        if (yPos > 210) {
            doc.addPage();
            yPos = 20;
        }

        // ============ TECHNICAL SPECS ============
        if (data.tank_volume_liters) {
            this.addSectionHeader(doc, 'TECHNICAL SPECIFICATIONS', yPos);
            yPos += 8;

            const techData = [
                ['Recommended Tank Volume:', `${this.formatNumber(data.tank_volume_liters)} L (${data.tank_volume_m3} m³)`],
                ['First Flush Diversion:', `${data.first_flush_liters} L`],
                ['Pit Specifications:', `${data.pit_diameter_m}m diameter, ${data.pit_depth_m}m depth`],
                ['Required Pit Volume:', `${this.formatNumber(data.required_pit_volume_liters)} L`]
            ];

            doc.autoTable({
                startY: yPos,
                body: techData,
                theme: 'plain',
                styles: { fontSize: 10, cellPadding: 4 },
                columnStyles: {
                    0: { fontStyle: 'bold', cellWidth: 70 },
                    1: { cellWidth: 110 }
                },
                margin: { left: 18 }
            });

            yPos = doc.lastAutoTable.finalY + 12;
        }

        // Page break check
        if (yPos > 230) {
            doc.addPage();
            yPos = 20;
        }

        // ============ RECOMMENDATION ============
        this.addSectionHeader(doc, 'EXPERT RECOMMENDATION', yPos);
        yPos += 8;

        doc.setFontSize(10);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(0, 0, 0);
        
        let recommendation = data.recommendation || 'No recommendation available';
        recommendation = recommendation.replace(/[\u{1F300}-\u{1F9FF}]/gu, '').replace(/[^\x00-\x7F]/g, ' ').trim();
        
        const splitRecommendation = doc.splitTextToSize(recommendation, 168);
        
        const recHeight = splitRecommendation.length * 6 + 8;
        doc.setFillColor(255, 248, 225);
        doc.setDrawColor(255, 193, 7);
        doc.setLineWidth(0.5);
        doc.rect(18, yPos - 3, 174, recHeight, 'FD');
        doc.text(splitRecommendation, 22, yPos + 2);
        yPos += recHeight + 10;

        // ============ CALCULATION DETAILS ============
        if (data.user || data.calculation_id) {
            if (yPos > 260) {
                doc.addPage();
                yPos = 20;
            }

            this.addSectionHeader(doc, 'CALCULATION DETAILS', yPos);
            yPos += 10;

            doc.setFontSize(9);
            doc.setFont('helvetica', 'normal');
            doc.setTextColor(80, 80, 80);
            
            if (data.calculation_id) {
                doc.text(`Calculation ID: ${data.calculation_id}`, 20, yPos);
                yPos += 5;
            }
            if (data.user) {
                doc.text(`Saved for User: ${data.user}`, 20, yPos);
                yPos += 5;
            }
            doc.text(`Generated: ${currentDate}`, 20, yPos);
        }

        // ============ FOOTER ============
        const pageCount = doc.internal.getNumberOfPages();
        for (let i = 1; i <= pageCount; i++) {
            doc.setPage(i);
            
            doc.setDrawColor(200, 200, 200);
            doc.line(14, 282, 196, 282);
            
            doc.setFontSize(8);
            doc.setTextColor(120, 120, 120);
            doc.setFont('helvetica', 'italic');
            doc.text(
                'JalJeevan.AI - Empowering Sustainable Water Management',
                105,
                287,
                { align: 'center' }
            );
            doc.text(
                `Page ${i} of ${pageCount}`,
                105,
                292,
                { align: 'center' }
            );
        }

        const filename = `Rainwater_Report_${data.district_name}_${new Date().toISOString().split('T')[0]}.pdf`;
        doc.save(filename);
        
        this.showNotification('PDF report downloaded successfully!', 'success');

    } catch (error) {
        console.error('PDF generation error:', error);
        this.showNotification('Failed to generate PDF: ' + error.message, 'warning');
    }
}

// ✅ NEW HELPER: Extract correct cost data from enhanced_recommendations string
// ✅ FIXED: Extract correct cost data with proper type checking
extractCostFromEnhanced(data) {
    // Convert enhanced_recommendations to string if it's not
    let enhanced = '';
    if (data.enhanced_recommendations) {
        if (typeof data.enhanced_recommendations === 'string') {
            enhanced = data.enhanced_recommendations;
        } else if (typeof data.enhanced_recommendations === 'object') {
            enhanced = JSON.stringify(data.enhanced_recommendations);
        } else {
            enhanced = String(data.enhanced_recommendations);
        }
    }
    
    console.log('🔍 Enhanced type:', typeof data.enhanced_recommendations);
    console.log('🔍 Enhanced value:', enhanced);
    
    // Extract using regex
    const costMatch = enhanced.match(/Total system cost:\s*[₹Rs.]*\s*([\d,]+)/i);
    const savingsMatch = enhanced.match(/Annual water savings:\s*[₹Rs.]*\s*([\d,]+)/i);
    const paybackMatch = enhanced.match(/Payback period:\s*([\d.]+)\s*years/i);
    
    const installCost = costMatch 
        ? parseInt(costMatch[1].replace(/,/g, '')) 
        : (data.costs?.total_install_cost || 0);
    
    const annualSavings = savingsMatch 
        ? parseInt(savingsMatch[1].replace(/,/g, '')) 
        : (data.costs?.annual_water_savings || 0);
    
    const paybackYears = paybackMatch 
        ? paybackMatch[1] 
        : (installCost && annualSavings ? (installCost / annualSavings).toFixed(1) : 'N/A');
    
    // Calculate ROI
    const roi = annualSavings > 0 && installCost > 0
        ? (((annualSavings * 30) - installCost) / installCost * 100).toFixed(1)
        : '0.0';
    
    console.log('💰 Extracted cost data:', { installCost, annualSavings, paybackYears, roi });
    
    return {
        installCost,
        annualSavings,
        paybackYears,
        roi
    };
}


// Helper method for section headers
addSectionHeader(doc, title, yPos) {
    doc.setFillColor(240, 248, 255);
    doc.rect(14, yPos - 6, 182, 9, 'F');
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(30, 60, 114);
    doc.text(title, 18, yPos);
}

// Helper method for section headers
addSectionHeader(doc, title, yPos) {
    doc.setFillColor(240, 248, 255);
    doc.rect(14, yPos - 6, 182, 9, 'F');
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(30, 60, 114);
    doc.text(title, 18, yPos);
}


// ============ FALLBACK TEXT DOWNLOAD (Keep your old method as backup) ============
downloadTextReport() {
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
    
    this.showNotification('📄 Text report downloaded successfully!', 'success');
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

${data.costs ? `
COST ANALYSIS:
- Installation Cost: ₹${this.formatNumber(data.costs.total_install_cost)}
- Annual Savings: ₹${this.formatNumber(data.costs.net_annual_savings)}
- Payback Period: ${data.costs.payback_years || 'N/A'} years
- 10-Year ROI: ${data.costs.roi_percentage}%
` : ''}

${data.tank_volume_liters ? `
TECHNICAL SPECIFICATIONS:
- Tank Volume: ${this.formatNumber(data.tank_volume_liters)} L (${data.tank_volume_m3} m³)
- First Flush Diversion: ${this.formatNumber(data.first_flush_liters)} L
- Pit Diameter: ${data.pit_diameter_m} m
- Recharge Volume: ${this.formatNumber(data.available_recharge_liters)} L
` : ''}

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
document.addEventListener('DOMContentLoaded', function() {
    const calculator = new RainwaterCalculatorDemo();
    window.calculator = calculator;
    console.log('🌧️ RainwaterCalculatorDemo fully loaded with reliable chart loading! 💧');
});

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
    
    #rainfallChart, #harvestConsumptionChart {
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

console.log('🌧️ RainwaterCalculatorDemo fully loaded with reliable dual-chart functionality! 💧');
