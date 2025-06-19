// Cascadia Watershed Lookup - Frontend JavaScript

class WatershedApp {
    constructor() {
        this.form = document.getElementById('watershed-form');
        this.addressInput = document.getElementById('address');
        this.searchBtn = document.getElementById('search-btn');
        this.btnText = document.querySelector('.btn-text');
        this.btnLoading = document.querySelector('.btn-loading');
        this.resultsSection = document.getElementById('results-section');
        this.resultsContent = document.getElementById('results-content');
        this.errorSection = document.getElementById('error-section');
        this.errorMessage = document.getElementById('error-message');
        this.retryBtn = document.getElementById('retry-btn');
        
        this.initEventListeners();
    }
    
    initEventListeners() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        this.retryBtn.addEventListener('click', () => this.hideError());
        this.addressInput.addEventListener('input', () => this.hideError());
    }
    
    async handleSubmit(e) {
        e.preventDefault();
        
        const address = this.addressInput.value.trim();
        if (!address) {
            this.showError('Please enter a valid street address');
            return;
        }
        
        this.setLoading(true);
        this.hideResults();
        this.hideError();
        
        try {
            const result = await this.lookupWatershed(address);
            this.showResults(result.data);
        } catch (error) {
            this.showError(error.message);
        } finally {
            this.setLoading(false);
        }
    }
    
    async lookupWatershed(address) {
        const response = await fetch('/api/lookup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ address: address })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Failed to lookup watershed');
        }
        
        return data;
    }
    
    showResults(data) {
        const { input_address, coordinates, watershed_info } = data;
        const { immediate_watershed, hierarchy } = watershed_info;
        
        this.resultsContent.innerHTML = `
            <div class="watershed-info">
                <div class="watershed-header">
                    <h2>${this.escapeHtml(immediate_watershed.name)}</h2>
                    <div class="watershed-meta">
                        <span><strong>Address:</strong> ${this.escapeHtml(input_address)}</span>
                        <span><strong>Country:</strong> ${immediate_watershed.country}</span>
                        <span><strong>Area:</strong> ${immediate_watershed.area_sqkm.toFixed(1)} km²</span>
                        <span><strong>Coordinates:</strong> ${coordinates.latitude.toFixed(4)}, ${coordinates.longitude.toFixed(4)}</span>
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
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new WatershedApp();
});

// Add some example address functionality
document.addEventListener('DOMContentLoaded', () => {
    const exampleItems = document.querySelectorAll('.examples li');
    const addressInput = document.getElementById('address');
    
    exampleItems.forEach(item => {
        item.style.cursor = 'pointer';
        item.style.transition = 'color 0.2s ease';
        
        item.addEventListener('click', () => {
            addressInput.value = item.textContent;
            addressInput.focus();
            addressInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
        });
        
        item.addEventListener('mouseenter', () => {
            item.style.color = 'var(--water-color)';
        });
        
        item.addEventListener('mouseleave', () => {
            item.style.color = 'var(--text-secondary)';
        });
    });
});