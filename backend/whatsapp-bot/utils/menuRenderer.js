/**
 * Menu Renderer - Format and render menu messages
 */

/**
 * Render main menu
 * @returns {string} - Formatted menu message
 */
function renderMainMenu() {
  return `🛒 *Welcome to KiranaChain!*

Please choose an option:

*1.* 🛍️ Order Groceries
*2.* 💰 Debt Management
*3.* ℹ️ More Details

Reply with the number (1, 2, or 3)`;
}

/**
 * Render debt management sub-menu
 * @returns {string} - Formatted menu message
 */
function renderDebtManagementMenu() {
  return `💰 *Debt Management*

Choose an option:

*1.* Check Balance
*2.* Record Debt
*3.* Make Payment
*4.* Back to Main Menu

Reply with the number (1-4)`;
}

/**
 * Render "More Details" sub-menu
 * @returns {string} - Formatted menu message
 */
function renderMoreDetailsMenu() {
  return `ℹ️ *More Details*

Choose an option:

*1.* View Products & Prices
*2.* View Noticeboard
*3.* Back to Main Menu

Reply with the number (1-3)`;
}

/**
 * Render sub-menu based on type
 * @param {string} menuType - Menu type
 * @returns {string} - Formatted menu message
 */
function renderSubMenu(menuType) {
  switch (menuType) {
    case 'debt_management':
      return renderDebtManagementMenu();
    case 'more_details':
      return renderMoreDetailsMenu();
    default:
      return renderMainMenu();
  }
}

/**
 * Render order bill
 * @param {Array} items - Order items
 * @param {number} total - Total amount
 * @returns {string} - Formatted bill message
 */
function renderBill(items, total) {
  let bill = `🛒 *Your Order Bill*\n\n`;
  
  items.forEach((item) => {
    const quantity = item.quantity || 1;
    const unit = item.unit || '';
    
    // Use total_price from backend if available (already calculated with unit conversion)
    // Otherwise calculate from price * quantity
    const itemTotal = item.total_price !== undefined 
      ? item.total_price 
      : (item.price || 0) * quantity;
    
    // Format quantity display (convert grams to kg for display if needed)
    let displayQuantity = quantity;
    let displayUnit = unit.toLowerCase();
    
    // Handle unit formatting
    if (displayUnit === 'g' || displayUnit === 'gram' || displayUnit === 'grams') {
      if (quantity >= 1000) {
        displayQuantity = (quantity / 1000).toFixed(2);
        displayUnit = 'kg';
      } else {
        displayUnit = 'g';
      }
    } else if (displayUnit === 'kg' || displayUnit === 'kilogram' || displayUnit === 'kilograms') {
      displayUnit = 'kg';
    }
    
    // Format: "Rice (2kg)        ₹100.00"
    // Calculate spacing to align prices (target width: 20 chars for name+quantity)
    const itemName = `${item.name} (${displayQuantity}${displayUnit})`;
    const priceStr = `₹${itemTotal.toFixed(2)}`;
    const targetWidth = 20;
    const spacing = ' '.repeat(Math.max(1, targetWidth - itemName.length));
    
    bill += `${itemName}${spacing}${priceStr}\n`;
  });
  
  bill += `─────────────────────────\n`;
  // Align "Total:" with item names (target width: 20 chars)
  const totalLabel = 'Total:';
  const totalSpacing = ' '.repeat(Math.max(1, 20 - totalLabel.length));
  bill += `${totalLabel}${totalSpacing}₹${total.toFixed(2)}\n\n`;
  bill += `Reply "confirm" to place order or "cancel" to go back.`;
  
  return bill;
}

/**
 * Render product list grouped by category
 * @param {Array} products - Product array
 * @param {number} page - Page number (1-indexed)
 * @param {number} pageSize - Items per page
 * @returns {string} - Formatted product list
 */
function renderProductList(products, page = 1, pageSize = 50) {
  if (!products || products.length === 0) {
    return `🛍️ *Available Products*\n\nNo products available.`;
  }
  
  // Group products by category
  const productsByCategory = {};
  products.forEach(product => {
    const category = product.category || 'Other';
    if (!productsByCategory[category]) {
      productsByCategory[category] = [];
    }
    productsByCategory[category].push(product);
  });
  
  let catalog = `🛍️ *Available Products*\n\n`;
  
  // Sort categories alphabetically
  const sortedCategories = Object.keys(productsByCategory).sort();
  
  sortedCategories.forEach(category => {
    catalog += `*${category}:*\n`;
    productsByCategory[category].forEach(product => {
      const stockStatus = product.stock_quantity > 0 
        ? '(In Stock)' 
        : '(Out of Stock)';
      
      // Determine unit (kg, litre, etc.)
      let unit = '/kg';
      if (product.name.toLowerCase().includes('oil')) {
        unit = '/litre';
      } else if (product.name.toLowerCase().includes('milk')) {
        unit = '/litre';
      }
      
      catalog += `• ${product.name} - ₹${product.price.toFixed(2)}${unit} ${stockStatus}\n`;
    });
    catalog += `\n`;
  });
  
  catalog += `Reply "0" to go back.`;
  
  return catalog;
}

/**
 * Render noticeboard
 * @param {Array} notices - Notice array
 * @returns {string} - Formatted noticeboard
 */
function renderNoticeboard(notices) {
  if (!notices || notices.length === 0) {
    return `📢 *Noticeboard*\n\nNo notices available at this time.`;
  }
  
  let noticeboard = `📢 *Noticeboard*\n\n`;
  
  notices.forEach((notice, index) => {
    noticeboard += `*${notice.title}*\n`;
    noticeboard += `──────────────\n`;
    noticeboard += `${notice.message}\n`;
    
    if (notice.created_at) {
      const date = new Date(notice.created_at);
      noticeboard += `Posted: ${date.toLocaleDateString('en-IN')}\n`;
    }
    
    noticeboard += `\n`;
  });
  
  noticeboard += `Reply "0" to go back.`;
  
  return noticeboard;
}

/**
 * Render error message
 * @param {string} message - Error message
 * @returns {string} - Formatted error
 */
function renderError(message) {
  return `❌ *Error*\n\n${message}\n\nPlease try again or reply "0" to go back.`;
}

/**
 * Render success message
 * @param {string} message - Success message
 * @returns {string} - Formatted success
 */
function renderSuccess(message) {
  return `✅ *Success*\n\n${message}`;
}

module.exports = {
  renderMainMenu,
  renderDebtManagementMenu,
  renderMoreDetailsMenu,
  renderSubMenu,
  renderBill,
  renderProductList,
  renderNoticeboard,
  renderError,
  renderSuccess
};

