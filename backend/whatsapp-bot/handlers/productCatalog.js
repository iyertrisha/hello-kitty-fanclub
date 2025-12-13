/**
 * Product Catalog Handler - Display product catalog
 */
const axios = require('axios');
const config = require('../config');
const menuState = require('../utils/menuState');
const menuRenderer = require('../utils/menuRenderer');

/**
 * Handle catalog menu selection
 * @param {object} client - WhatsApp client
 * @param {object} message - Message object
 * @param {string} phone - Normalized phone
 * @param {number} selection - Menu selection
 */
async function handleCatalogMenu(client, message, phone, selection) {
  try {
    // Get shopkeeper (use first shopkeeper)
    const shopkeeperResponse = await axios.get(
      `${config.flaskApiUrl}/api/shopkeeper`,
      { timeout: 10000 }
    );
    
    let shopkeeperId = null;
    if (shopkeeperResponse.data && shopkeeperResponse.data.shopkeepers && shopkeeperResponse.data.shopkeepers.length > 0) {
      shopkeeperId = shopkeeperResponse.data.shopkeepers[0].id;
    } else {
      await client.sendMessage(message.from, 
        menuRenderer.renderError('No shopkeeper found. Please contact support.')
      );
      menuState.clearState(phone);
      return;
    }
    
    // Get products
    const productsResponse = await axios.get(
      `${config.flaskApiUrl}/api/grocery/products?shopkeeper_id=${shopkeeperId}`,
      { timeout: 10000 }
    );
    
    if (productsResponse.data && productsResponse.data.products) {
      const products = productsResponse.data.products;
      
      // Store products in context for pagination
      menuState.setContext(phone, 'products', products);
      menuState.setContext(phone, 'currentPage', 1);
      
      // Display first page
      const catalogMessage = menuRenderer.renderProductList(products, 1, 10);
      await client.sendMessage(message.from, catalogMessage);
    } else {
      await client.sendMessage(message.from, 
        menuRenderer.renderError('No products available.')
      );
      menuState.clearState(phone);
    }
  } catch (error) {
    console.error('Error displaying catalog:', error);
    
    let errorMsg = 'Failed to load product catalog. Please try again later.';
    
    // Check for connection errors
    if (error.code === 'ECONNREFUSED' || error.code === 'ETIMEDOUT' || error.message?.includes('ECONNREFUSED')) {
      errorMsg = '⚠️ Backend server is not available. Please ensure the Flask backend is running on port 5000.';
      console.error('Backend connection error - Flask server may not be running');
    } else if (error.response) {
      errorMsg = error.response.data?.error || errorMsg;
    }
    
    await client.sendMessage(message.from, menuRenderer.renderError(errorMsg));
    menuState.clearState(phone);
  }
}

/**
 * Display catalog with pagination
 * @param {object} client - WhatsApp client
 * @param {object} message - Message object
 * @param {string} phone - Normalized phone
 * @param {string} category - Category filter (optional)
 */
async function displayCatalog(client, message, phone, category) {
  // This can be enhanced later for category filtering
  await handleCatalogMenu(client, message, phone, 1);
}

/**
 * Search products
 * @param {object} client - WhatsApp client
 * @param {object} message - Message object
 * @param {string} phone - Normalized phone
 * @param {string} query - Search query
 */
async function searchProducts(client, message, phone, query) {
  try {
    // Get shopkeeper
    const shopkeeperResponse = await axios.get(
      `${config.flaskApiUrl}/api/shopkeeper`,
      { timeout: 10000 }
    );
    
    let shopkeeperId = null;
    if (shopkeeperResponse.data && shopkeeperResponse.data.shopkeepers && shopkeeperResponse.data.shopkeepers.length > 0) {
      shopkeeperId = shopkeeperResponse.data.shopkeepers[0].id;
    } else {
      await client.sendMessage(message.from, 
        menuRenderer.renderError('No shopkeeper found.')
      );
      return;
    }
    
    // Get products
    const productsResponse = await axios.get(
      `${config.flaskApiUrl}/api/grocery/products?shopkeeper_id=${shopkeeperId}`,
      { timeout: 10000 }
    );
    
    if (productsResponse.data && productsResponse.data.products) {
      const allProducts = productsResponse.data.products;
      
      // Filter products by query (case insensitive)
      const queryLower = query.toLowerCase();
      const filtered = allProducts.filter(p => 
        p.name.toLowerCase().includes(queryLower) ||
        (p.category && p.category.toLowerCase().includes(queryLower))
      );
      
      if (filtered.length > 0) {
        const catalogMessage = menuRenderer.renderProductList(filtered, 1, 10);
        await client.sendMessage(message.from, catalogMessage);
      } else {
        await client.sendMessage(message.from, 
          `No products found matching "${query}".\n\nReply "0" to go back.`
        );
      }
    }
  } catch (error) {
    console.error('Error searching products:', error);
    await client.sendMessage(message.from, 
      menuRenderer.renderError('Failed to search products.')
    );
  }
}

module.exports = {
  handleCatalogMenu,
  displayCatalog,
  searchProducts
};

