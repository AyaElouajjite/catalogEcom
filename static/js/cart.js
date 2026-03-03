// Cart management JavaScript

// Add to cart with AJAX (optional enhancement)
function addToCart(productId, variationId, quantity) {
    // This could be implemented with AJAX for better UX
    // For now, the form submission handles it
}

// Update cart quantity
function updateQuantity(productId, variationId, quantity) {
    if (quantity <= 0) {
        if (confirm('Voulez-vous supprimer cet article du panier ?')) {
            removeFromCart(productId, variationId);
        }
    } else {
        // Submit form to update
        var form = document.createElement('form');
        form.method = 'POST';
        form.action = '/panier/modifier';
        
        var productInput = document.createElement('input');
        productInput.type = 'hidden';
        productInput.name = 'product_id';
        productInput.value = productId;
        
        var variationInput = document.createElement('input');
        variationInput.type = 'hidden';
        variationInput.name = 'variation_id';
        variationInput.value = variationId || '';
        
        var quantityInput = document.createElement('input');
        quantityInput.type = 'hidden';
        quantityInput.name = 'quantity';
        quantityInput.value = quantity;
        
        form.appendChild(productInput);
        form.appendChild(variationInput);
        form.appendChild(quantityInput);
        
        document.body.appendChild(form);
        form.submit();
    }
}

// Remove from cart
function removeFromCart(productId, variationId) {
    var form = document.createElement('form');
    form.method = 'POST';
    form.action = '/panier/supprimer';
    
    var productInput = document.createElement('input');
    productInput.type = 'hidden';
    productInput.name = 'product_id';
    productInput.value = productId;
    
    var variationInput = document.createElement('input');
    variationInput.type = 'hidden';
    variationInput.name = 'variation_id';
    variationInput.value = variationId || '';
    
    form.appendChild(productInput);
    form.appendChild(variationInput);
    
    document.body.appendChild(form);
    form.submit();
}


