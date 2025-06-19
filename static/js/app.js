// Cascadia Watershed Lookup - Enhanced Frontend JavaScript

class WatershedApp {
    constructor() {
        this.form = document.getElementById('watershed-form');
        
        // Input mode elements
        this.inputModeRadios = document.querySelectorAll('input[name="input-mode"]');
        this.singleLineMode = document.getElementById('single-line-mode');
        this.multiLineMode = document.getElementById('multi-line-mode');
        this.singleLineAddress = document.getElementById('single-line-address');
        
        // Multi-line form elements
        this.addressLine1 = document.getElementById('address-line1');
        this.addressLine2 = document.getElementById('address-line2');
        this.city = document.getElementById('city');
        this.state = document.getElementById('state');
        this.postalCode = document.getElementById('postal-code');
        this.country = document.getElementById('country');
        
        // UI elements
        this.searchBtn = document.getElementById('search-btn');
        this.btnText = document.querySelector('.btn-text');
        this.btnLoading = document.querySelector('.btn-loading');
        this.resultsSection = document.getElementById('results-section');
        this.resultsContent = document.getElementById('results-content');
        this.errorSection = document.getElementById('error-section');
        this.errorMessage = document.getElementById('error-message');
        this.retryBtn = document.getElementById('retry-btn');
        
        // Current input mode
        this.currentMode = 'single-line';
        
        // Google Places autocomplete
        this.autocomplete = null;
        
        this.initEventListeners();
        this.initInputModeToggle();
    }
    
    initEventListeners() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        if (this.retryBtn) {
            this.retryBtn.addEventListener('click', () => this.hideError());
        }
        
        // Input mode toggle listeners
        this.inputModeRadios.forEach(radio => {
            radio.addEventListener('change', (e) => this.switchInputMode(e.target.value));
        });
        
        // Add event listeners to clear validation on input
        if (this.singleLineAddress) {
            this.singleLineAddress.addEventListener('input', () => this.clearValidation());
        }
        
        [this.addressLine1, this.addressLine2, this.city, this.state, this.postalCode, this.country].forEach(field => {
            if (field) {
                field.addEventListener('input', () => this.clearValidation());
            }
        });
    }
    
    initInputModeToggle() {
        // Set initial mode
        this.switchInputMode('single-line');
    }
    
    switchInputMode(mode) {
        this.currentMode = mode;
        
        if (mode === 'single-line') {
            this.singleLineMode.style.display = 'block';
            this.multiLineMode.style.display = 'none';
        } else {
            this.singleLineMode.style.display = 'none';
            this.multiLineMode.style.display = 'block';
        }
        
        this.clearValidation();
    }
    
    initGooglePlacesAutocomplete() {
        // Only initialize if Google Maps API is loaded and we have an input field
        if (typeof google !== 'undefined' && google.maps && google.maps.places && this.singleLineAddress) {
            // Create autocomplete for single-line input
            this.autocomplete = new google.maps.places.Autocomplete(this.singleLineAddress, {
                types: ['address'],
                componentRestrictions: {
                    country: ['ca', 'us']  // Restrict to Canada and US
                },
                fields: ['formatted_address', 'geometry', 'place_id']
            });
            
            // Listen for place selection
            this.autocomplete.addListener('place_changed', () => {
                const place = this.autocomplete.getPlace();
                if (place.geometry) {
                    // Auto-trigger search when a place is selected
                    setTimeout(() => {
                        this.form.dispatchEvent(new Event('submit'));
                    }, 100);
                }
            });
            
            console.log('Google Places Autocomplete initialized');
        } else {
            console.log('Google Places Autocomplete not available');
        }
    }
    
    async handleSubmit(e) {
        e.preventDefault();
        
        // Get address input based on current mode
        const addressInput = this.getAddressInput();
        
        if (!addressInput || !addressInput.trim()) {
            this.showError('Please enter a valid address');
            return;
        }
        
        this.setLoading(true);
        this.hideResults();
        this.hideError();
        this.clearValidation();
        
        try {
            // Use the enhanced lookup with validation
            const result = await this.lookupWatershedWithValidation(addressInput);
            
            if (result.success) {
                this.showResults(result.data);
            } else if (result.validation_error && result.data.validation.suggestions.length > 0) {
                // Show validation results with suggestions
                this.showValidationResults(result.data);
            } else {
                this.showError(result.message || 'Address could not be validated or is outside the Cascadia region');
            }
        } catch (error) {
            this.showError(error.message);
        } finally {
            this.setLoading(false);
        }
    }
    
    getAddressInput() {
        if (this.currentMode === 'single-line') {
            return this.singleLineAddress ? this.singleLineAddress.value.trim() : '';
        } else {
            return this.buildAddressString();
        }
    }
    
    validateForm() {
        const requiredFields = [
            { field: this.addressLine1, name: 'Street Address' },
            { field: this.city, name: 'City' },
            { field: this.state, name: 'State/Province' },
            { field: this.postalCode, name: 'Postal Code' }
        ];
        
        for (const { field, name } of requiredFields) {
            if (!field.value.trim()) {
                return `Please enter a valid ${name}`;
            }
        }
        
        return null;
    }
    
    buildAddressString() {
        const parts = [];
        
        // Add street address line 1
        if (this.addressLine1.value.trim()) {
            parts.push(this.addressLine1.value.trim());
        }
        
        // Add street address line 2 if provided
        if (this.addressLine2.value.trim()) {
            parts.push(this.addressLine2.value.trim());
        }
        
        // Add city
        if (this.city.value.trim()) {
            parts.push(this.city.value.trim());
        }
        
        // Add state/province
        if (this.state.value.trim()) {
            parts.push(this.state.value.trim());
        }
        
        // Add postal code
        if (this.postalCode.value.trim()) {
            parts.push(this.postalCode.value.trim());
        }
        
        // Add country if it's not US (default)
        if (this.country.value === 'CA') {
            parts.push('Canada');
        }
        
        return parts.join(', ');
    }
    
    async lookupWatershedWithValidation(address) {
        const response = await fetch('/api/lookup-with-validation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ address: address })
        });
        
        const data = await response.json();
        
        // Don't throw errors for validation failures - handle them in the UI
        if (response.status === 422) {
            // Validation error with suggestions
            return { success: false, validation_error: true, ...data };
        } else if (!response.ok && response.status !== 404) {
            // Real errors (not just "not found")
            throw new Error(data.message || 'Failed to lookup watershed');
        }
        
        return data;
    }
    
    async validateAddress(address) {
        const response = await fetch('/api/validate-address', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ address: address })
        });
        
        const data = await response.json();
        return data;
    }
    
    showResults(data) {
        // Handle both old and new data structures
        let input_address, coordinates, immediate_watershed, hierarchy;
        
        if (data.watershed_info) {
            // New structure with validation
            input_address = data.input_address;
            coordinates = data.watershed_info.coordinates;
            immediate_watershed = data.watershed_info.watershed_details.immediate_watershed;
            hierarchy = data.watershed_info.watershed_details.hierarchy;
        } else {
            // Old structure (fallback)
            input_address = data.input_address;
            coordinates = data.coordinates;
            immediate_watershed = data.watershed_info?.immediate_watershed;
            hierarchy = data.watershed_info?.hierarchy;
        }
        
        // Add safety checks for undefined properties
        if (!immediate_watershed || !coordinates) {
            this.showError('Unable to display watershed results - missing data');
            return;
        }

        const watershedName = immediate_watershed.name || 'Unnamed Watershed';
        const country = immediate_watershed.country || 'Unknown';
        const area = immediate_watershed.area_sqkm ? immediate_watershed.area_sqkm.toFixed(1) : 'Unknown';
        const lat = coordinates.latitude ? coordinates.latitude.toFixed(4) : 'Unknown';
        const lon = coordinates.longitude ? coordinates.longitude.toFixed(4) : 'Unknown';

        this.resultsContent.innerHTML = `
            <div class="watershed-info">
                <div class="watershed-header">
                    <h2>${this.escapeHtml(watershedName)}</h2>
                    <div class="watershed-meta">
                        <span><strong>Address:</strong> ${this.escapeHtml(input_address || 'Unknown')}</span>
                        <span><strong>Country:</strong> ${country}</span>
                        <span><strong>Area:</strong> ${area} km²</span>
                        <span><strong>Coordinates:</strong> ${lat}, ${lon}</span>
                    </div>
                </div>
                
                <div class="watershed-details">
                    ${this.renderHierarchy(hierarchy)}
                </div>
            </div>
        `;
        
        this.resultsSection.style.display = 'block';
        this.resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    renderHierarchy(hierarchy) {
        if (!hierarchy) {
            return '<div class="detail-card"><p>No hierarchy information available</p></div>';
        }
        
        let html = '';
        
        if (hierarchy.us) {
            html += `
                <div class="detail-card">
                    <h3>🇺🇸 US Watershed Hierarchy (HUC Codes)</h3>
                    <div class="hierarchy-codes">
                        ${this.renderHucCodes(hierarchy.us)}
                    </div>
                </div>
            `;
        }
        
        if (hierarchy.canada) {
            html += `
                <div class="detail-card">
                    <h3>🇨🇦 Canadian Watershed Hierarchy (SDAC Codes)</h3>
                    <div class="hierarchy-codes">
                        ${this.renderSdacCodes(hierarchy.canada)}
                    </div>
                </div>
            `;
        }
        
        return html;
    }
    
    renderHucCodes(hucData) {
        const levels = [
            { key: 'huc12', label: 'HUC12 (Sub-watershed)', description: 'Finest level watershed' },
            { key: 'huc10', label: 'HUC10 (Watershed)', description: 'Local watershed' },
            { key: 'huc8', label: 'HUC8 (Sub-basin)', description: 'Regional sub-basin' },
            { key: 'huc6', label: 'HUC6 (Basin)', description: 'River basin' },
            { key: 'huc4', label: 'HUC4 (Sub-region)', description: 'Sub-region' },
            { key: 'huc2', label: 'HUC2 (Region)', description: 'Major region' }
        ];
        
        return levels
            .filter(level => hucData[level.key])
            .map(level => `
                <div class="code-item" title="${level.description}">
                    <span class="code-label">${level.label}:</span>
                    <span class="code-value">${hucData[level.key]}</span>
                </div>
            `)
            .join('');
    }
    
    renderSdacCodes(sdacData) {
        const levels = [
            { key: 'ssda', label: 'SSDA (Sub-Sub-Drainage)', description: 'Finest level drainage area' },
            { key: 'sda', label: 'SDA (Sub-Drainage)', description: 'Sub-drainage area' },
            { key: 'mda', label: 'MDA (Major Drainage)', description: 'Major drainage area' }
        ];
        
        return levels
            .filter(level => sdacData[level.key])
            .map(level => `
                <div class="code-item" title="${level.description}">
                    <span class="code-label">${level.label}:</span>
                    <span class="code-value">${sdacData[level.key]}</span>
                </div>
            `)
            .join('');
    }
    
    showError(message) {
        this.errorMessage.textContent = message;
        this.errorSection.style.display = 'block';
        this.errorSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    hideError() {
        this.errorSection.style.display = 'none';
    }
    
    hideResults() {
        this.resultsSection.style.display = 'none';
    }
    
    setLoading(isLoading) {
        this.searchBtn.disabled = isLoading;
        
        if (isLoading) {
            this.btnText.style.display = 'none';
            this.btnLoading.style.display = 'inline-flex';
        } else {
            this.btnText.style.display = 'inline';
            this.btnLoading.style.display = 'none';
        }
    }
    
    showValidationResults(data) {
        const { input_address, parsed_address, validation } = data;
        
        let validationHtml = `
            <div class="validation-results validation-warning">
                <h3>⚠️ Address Validation</h3>
                <p><strong>Original address:</strong> ${this.escapeHtml(input_address)}</p>
                <p><strong>Parsed address:</strong> ${this.escapeHtml(parsed_address)}</p>
                <p>We couldn't validate this exact address, but found some similar addresses:</p>
        `;
        
        if (validation.suggestions && validation.suggestions.length > 0) {
            validationHtml += `
                <div class="address-suggestions">
                    <h4>Did you mean one of these?</h4>
            `;
            
            validation.suggestions.forEach((suggestion, index) => {
                validationHtml += `
                    <div class="suggestion-item" data-suggestion-index="${index}">
                        <span class="suggestion-address">${this.escapeHtml(suggestion.suggested_address)}</span>
                        <span class="suggestion-confidence">${suggestion.confidence}</span>
                        <button class="use-suggestion-btn" data-suggestion="${this.escapeHtml(suggestion.suggested_address)}">
                            Use This
                        </button>
                    </div>
                `;
            });
            
            validationHtml += `</div>`;
        }
        
        validationHtml += `</div>`;
        
        this.resultsContent.innerHTML = validationHtml;
        this.resultsSection.style.display = 'block';
        this.resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        // Add event listeners for suggestion buttons
        const suggestionButtons = this.resultsContent.querySelectorAll('.use-suggestion-btn');
        suggestionButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const suggestedAddress = e.target.getAttribute('data-suggestion');
                this.useSuggestedAddress(suggestedAddress);
            });
        });
    }
    
    useSuggestedAddress(address) {
        if (this.currentMode === 'single-line') {
            this.singleLineAddress.value = address;
        } else {
            // For multi-line mode, try to parse the address into components
            // This is a simplified implementation
            const parts = address.split(',').map(part => part.trim());
            
            if (parts.length >= 1) this.addressLine1.value = parts[0];
            if (parts.length >= 2) this.city.value = parts[1];
            if (parts.length >= 3) this.state.value = parts[2];
            if (parts.length >= 4) this.postalCode.value = parts[3];
            
            // Detect country
            if (address.toLowerCase().includes('canada') || address.toLowerCase().includes('bc') || address.toLowerCase().includes('alberta')) {
                this.country.value = 'CA';
            } else {
                this.country.value = 'US';
            }
        }
        
        // Clear validation and automatically retry the search
        this.clearValidation();
        this.form.dispatchEvent(new Event('submit'));
    }
    
    clearValidation() {
        // Remove any validation results
        const validationResults = document.querySelectorAll('.validation-results');
        validationResults.forEach(result => result.remove());
        
        // Clear any input validation styles
        const inputs = [this.singleLineAddress, this.addressLine1, this.addressLine2, this.city, this.state, this.postalCode];
        inputs.forEach(input => {
            if (input) {
                input.classList.remove('validation-error', 'validation-success');
            }
        });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.watershedApp = new WatershedApp();
});

// Global callback for Google Maps API
function initAutocomplete() {
    // Initialize Google Places Autocomplete when API is ready
    if (window.watershedApp) {
        window.watershedApp.initGooglePlacesAutocomplete();
    } else {
        // If app isn't ready yet, wait a bit and try again
        setTimeout(() => {
            if (window.watershedApp) {
                window.watershedApp.initGooglePlacesAutocomplete();
            }
        }, 100);
    }
}

// Add some example address functionality
document.addEventListener('DOMContentLoaded', () => {
    const exampleItems = document.querySelectorAll('.examples li');
    
    // Define example addresses with parsed components
    const examples = {
        '1600 Amphitheatre Parkway, Mountain View, CA': {
            addressLine1: '1600 Amphitheatre Parkway',
            city: 'Mountain View',
            state: 'CA',
            postalCode: '94043',
            country: 'US'
        },
        '123 Main Street, Seattle, WA': {
            addressLine1: '123 Main Street',
            city: 'Seattle',
            state: 'WA',
            postalCode: '98101',
            country: 'US'
        },
        '456 Oak Avenue, Portland, OR': {
            addressLine1: '456 Oak Avenue',
            city: 'Portland',
            state: 'OR',
            postalCode: '97201',
            country: 'US'
        },
        '789 Maple Drive, Vancouver, BC': {
            addressLine1: '789 Maple Drive',
            city: 'Vancouver',
            state: 'BC',
            postalCode: 'V6B 1A1',
            country: 'CA'
        }
    };
    
    exampleItems.forEach(item => {
        item.style.cursor = 'pointer';
        item.style.transition = 'color 0.2s ease';
        
        item.addEventListener('click', () => {
            const exampleData = examples[item.textContent];
            if (exampleData) {
                document.getElementById('address-line1').value = exampleData.addressLine1;
                document.getElementById('address-line2').value = '';
                document.getElementById('city').value = exampleData.city;
                document.getElementById('state').value = exampleData.state;
                document.getElementById('postal-code').value = exampleData.postalCode;
                document.getElementById('country').value = exampleData.country;
                
                document.getElementById('address-line1').focus();
                document.getElementById('address-line1').scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        });
        
        item.addEventListener('mouseenter', () => {
            item.style.color = 'var(--water-color)';
        });
        
        item.addEventListener('mouseleave', () => {
            item.style.color = 'var(--text-secondary)';
        });
    });
});