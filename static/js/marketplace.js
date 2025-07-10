// Marketplace JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize marketplace functionality
    initFilters();
    initPagination();
    initProductCards();
    initCustomization();
});

function initFilters() {
    // Auto-submit form when sort dropdown changes
    const sortSelect = document.querySelector('select[name="sort"]');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            const form = this.closest('form') || document.querySelector('form');
            if (form) {
                form.submit();
            }
        });
    }

    // Price range validation
    const minPriceInput = document.querySelector('input[name="min_price"]');
    const maxPriceInput = document.querySelector('input[name="max_price"]');
    
    if (minPriceInput && maxPriceInput) {
        minPriceInput.addEventListener('input', function() {
            const minVal = parseFloat(this.value);
            const maxVal = parseFloat(maxPriceInput.value);
            
            if (maxVal && minVal > maxVal) {
                maxPriceInput.value = minVal;
            }
        });
        
        maxPriceInput.addEventListener('input', function() {
            const minVal = parseFloat(minPriceInput.value);
            const maxVal = parseFloat(this.value);
            
            if (minVal && maxVal < minVal) {
                minPriceInput.value = maxVal;
            }
        });
    }
}

function initPagination() {
    // Add loading state to pagination links
    const paginationLinks = document.querySelectorAll('.pagination a');
    paginationLinks.forEach(link => {
        link.addEventListener('click', function() {
            showLoading();
        });
    });
}

function initProductCards() {
    // Add hover effects and interaction to product cards
    const productCards = document.querySelectorAll('.card');
    productCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

function initCustomization() {
    // Handle customization form changes
    const customizationInputs = document.querySelectorAll('#customizationForm input, #customizationForm select');
    customizationInputs.forEach(input => {
        input.addEventListener('change', function() {
            updateCustomizationPreview();
            calculateTotalPrice();
        });
    });
}

function updateCustomizationPreview() {
    // Update customization preview (placeholder for future implementation)
    const previewContainer = document.querySelector('.customization-preview');
    if (previewContainer) {
        // Implementation would depend on specific customization types
        console.log('Updating customization preview...');
    }
}

function calculateTotalPrice() {
    // Calculate total price including customizations
    const basePrice = parseFloat(document.querySelector('.price-display')?.textContent.replace('$', '')) || 0;
    let totalAdditionalCost = 0;
    
    const customizationInputs = document.querySelectorAll('#customizationForm input, #customizationForm select');
    customizationInputs.forEach(input => {
        if (input.value && input.dataset.additionalCost) {
            totalAdditionalCost += parseFloat(input.dataset.additionalCost);
        }
    });
    
    const quantity = parseInt(document.querySelector('#quantity')?.value) || 1;
    const totalPrice = (basePrice + totalAdditionalCost) * quantity;
    
    // Update price display if element exists
    const totalPriceElement = document.querySelector('#totalPrice');
    if (totalPriceElement) {
        totalPriceElement.textContent = `$${totalPrice.toFixed(2)}`;
    }
}

function showLoading() {
    // Show loading state
    const body = document.body;
    body.classList.add('loading');
    
    // Create loading overlay
    const loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'loading-overlay';
    loadingOverlay.innerHTML = `
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    `;
    loadingOverlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.8);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    `;
    
    body.appendChild(loadingOverlay);
}

function hideLoading() {
    // Hide loading state
    const body = document.body;
    body.classList.remove('loading');
    
    const loadingOverlay = document.querySelector('.loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.remove();
    }
}

// Filter functionality
function clearFilters() {
    const form = document.querySelector('form');
    if (form) {
        const inputs = form.querySelectorAll('input, select');
        inputs.forEach(input => {
            if (input.type === 'checkbox') {
                input.checked = false;
            } else {
                input.value = '';
            }
        });
        form.submit();
    }
}

// Search functionality
function performSearch() {
    const searchForm = document.querySelector('form');
    if (searchForm) {
        showLoading();
        searchForm.submit();
    }
}

// Product image gallery
function changeMainImage(imageUrl) {
    const mainImage = document.getElementById('mainImage');
    if (mainImage) {
        mainImage.src = imageUrl;
        
        // Update active thumbnail
        const thumbnails = document.querySelectorAll('.thumbnail-img');
        thumbnails.forEach(thumb => {
            thumb.style.borderColor = thumb.src === imageUrl ? '#007bff' : 'transparent';
        });
    }
}

// Add to cart functionality
function addToCart(productId, quantity = 1, customizations = {}) {
    // This would integrate with your cart system
    const cartData = {
        product_id: productId,
        quantity: quantity,
        customizations: customizations
    };
    
    // Show success message
    showMessage('Product added to cart!', 'success');
    
    // Update cart count in navigation (if implemented)
    updateCartCount();
}

// Contact seller functionality
function contactSeller(sellerId) {
    // This would open a contact form or redirect to messaging system
    showMessage('Contact seller functionality would be implemented here', 'info');
}

// Utility functions
function showMessage(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

function updateCartCount() {
    // Update cart count in navigation
    const cartCountElement = document.querySelector('.cart-count');
    if (cartCountElement) {
        const currentCount = parseInt(cartCountElement.textContent) || 0;
        cartCountElement.textContent = currentCount + 1;
    }
}

// Export functions for global use
window.MarketplaceJS = {
    clearFilters,
    performSearch,
    changeMainImage,
    addToCart,
    contactSeller,
    showMessage,
    showLoading,
    hideLoading
};
