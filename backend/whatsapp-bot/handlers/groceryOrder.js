/**
 * Grocery Order Handler - Handle grocery ordering flow
 */
const axios = require('axios');
const config = require('../config');
const menuState = require('../utils/menuState');
const menuRenderer = require('../utils/menuRenderer');
const groceryParser = require('../utils/groceryParser');

/**
 * Handle grocery menu selection
 * @param {object} client - WhatsApp client
 * @param {object} message - Message object
 * @param {string} phone - Normalized phone
 * @param {number} selection - Menu selection
 */
async function handleGroceryMenu(client, message, phone, selection) {
  await client.sendMessage(message.from, 
    '🛍️ *Order Groceries*\n\n' +
    'Please send your grocery list.\n\n' +
    'Examples:\n' +
    '• "2kg rice, 1kg sugar, 500g salt"\n' +
    '• "Rice 2kg, Sugar 1kg"\n' +
    '• "2 rice, 1 sugar"\n\n' +
    'Reply "cancel" to go back.'
  );
}

/**
 * Handle grocery list input
 * @param {object} client - WhatsApp client
 * @param {object} message - Message object
 * @param {string} phone - Normalized phone
 * @param {string} listText - Grocery list text
 */
async function handleGroceryList(client, message, phone, listText) {
  try {
    console.log(`🛒 Processing grocery list from ${phone}: "${listText}"`);
    
    // Parse grocery list
    const parsedItems = groceryParser.parseGroceryList(listText);
    
    if (parsedItems.length === 0) {
      await client.sendMessage(message.from, 
        menuRenderer.renderError('I couldn\'t parse your grocery list. Please try again with a clearer format.\n\nExample: "2kg rice, 1kg sugar"')
      );
      return;
    }
    
    // Get shopkeeper (use first shopkeeper for now)
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
    
    // Send to backend for parsing and matching
    const parseResponse = await axios.post(
      `${config.flaskApiUrl}/api/grocery/parse`,
      {
        list: listText,
        shopkeeper_id: shopkeeperId,
        parsed_items: parsedItems
      },
      {
        headers: { 'Content-Type': 'application/json' },
        timeout: 15000
      }
    );
    
    if (parseResponse.data && parseResponse.data.items) {
      const items = parseResponse.data.items;
      const total = parseResponse.data.total || 0;
      const unmatched = parseResponse.data.unmatched || [];
      
      if (items.length === 0) {
        let errorMsg = 'No products matched your list.';
        if (unmatched.length > 0) {
          errorMsg += `\n\nUnmatched items: ${unmatched.join(', ')}`;
        }
        await client.sendMessage(message.from, menuRenderer.renderError(errorMsg));
        return;
      }
      
      // Store order in context
      menuState.setContext(phone, 'orderItems', items);
      menuState.setContext(phone, 'orderTotal', total);
      menuState.setContext(phone, 'shopkeeperId', shopkeeperId);
      menuState.setContext(phone, 'unmatched', unmatched);
      
      // Show bill
      let billMessage = menuRenderer.renderBill(items, total);
      
      if (unmatched.length > 0) {
        billMessage += `\n\n⚠️ Note: Could not match: ${unmatched.join(', ')}`;
      }
      
      // Set state to confirm (preserves existing context)
      menuState.setState(phone, 'grocery_confirm');
      
      await client.sendMessage(message.from, billMessage);
    } else {
      await client.sendMessage(message.from, 
        menuRenderer.renderError('Failed to process your grocery list. Please try again.')
      );
    }
  } catch (error) {
    console.error('Error processing grocery list:', error);
    
    let errorMsg = 'Sorry, I encountered an error processing your grocery list.';
    
    // Check for connection errors
    if (error.code === 'ECONNREFUSED' || error.code === 'ETIMEDOUT' || error.message?.includes('ECONNREFUSED')) {
      errorMsg = '⚠️ Backend server is not available. Please ensure the Flask backend is running on port 5000.';
      console.error('Backend connection error - Flask server may not be running');
    } else if (error.response) {
      errorMsg = error.response.data?.error || errorMsg;
    } else if (error.message) {
      errorMsg = error.message;
    }
    
    await client.sendMessage(message.from, menuRenderer.renderError(errorMsg));
  }
}

/**
 * Handle grocery order confirmation
 * @param {object} client - WhatsApp client
 * @param {object} message - Message object
 * @param {string} phone - Normalized phone
 * @param {string} confirmation - Confirmation text
 */
async function handleGroceryConfirm(client, message, phone, confirmation) {
  const lowerText = confirmation.toLowerCase().trim();
  
  // Handle cancel
  if (lowerText === 'cancel' || lowerText === 'back' || lowerText === '0') {
    menuState.clearState(phone);
    await client.sendMessage(message.from, menuRenderer.renderMainMenu());
    return;
  }
  
  // Handle confirm
  if (lowerText === 'confirm' || lowerText === 'yes' || lowerText === 'y') {
    try {
      const items = menuState.getContext(phone, 'orderItems');
      const total = menuState.getContext(phone, 'orderTotal');
      const shopkeeperId = menuState.getContext(phone, 'shopkeeperId');
      
      console.log(`📦 Confirming order for ${phone}:`, {
        hasItems: !!items,
        itemsCount: items ? items.length : 0,
        total: total,
        shopkeeperId: shopkeeperId
      });
      
      if (!items || !shopkeeperId) {
        console.error(`❌ Order data missing for ${phone}:`, {
          items: items,
          shopkeeperId: shopkeeperId,
          allContext: menuState.getAllContext(phone)
        });
        await client.sendMessage(message.from, 
          menuRenderer.renderError('Order data not found. Please start over.')
        );
        menuState.clearState(phone);
        return;
      }
      
      // Create order
      const orderResponse = await axios.post(
        `${config.flaskApiUrl}/api/grocery/create-order`,
        {
          customer_phone: phone,
          items: items,
          shopkeeper_id: shopkeeperId
        },
        {
          headers: { 'Content-Type': 'application/json' },
          timeout: 20000
        }
      );
      
      if (orderResponse.data && orderResponse.data.success) {
        const orderId = orderResponse.data.order_id;
        const transactionId = orderResponse.data.transaction_id;
        
        let successMsg = `✅ *Order Placed Successfully!*\n\n`;
        successMsg += `Order ID: ${orderId}\n`;
        successMsg += `Total Amount: ₹${total.toFixed(2)}\n`;
        if (transactionId) {
          successMsg += `Transaction ID: ${transactionId}\n`;
        }
        successMsg += `\nYour order has been recorded. Thank you!`;
        
        if (orderResponse.data.blockchain_tx_id) {
          successMsg += `\n\n🔗 Blockchain: ${orderResponse.data.blockchain_tx_id.substring(0, 20)}...`;
        }
        
        await client.sendMessage(message.from, successMsg);
        
        // Clear state and return to main menu
        menuState.clearState(phone);
        setTimeout(async () => {
          await client.sendMessage(message.from, menuRenderer.renderMainMenu());
        }, 2000);
      } else {
        await client.sendMessage(message.from, 
          menuRenderer.renderError('Failed to create order. Please try again.')
        );
      }
    } catch (error) {
      console.error('Error creating order:', error);
      
      let errorMsg = 'Sorry, I encountered an error creating your order.';
      
      // Check for connection errors
      if (error.code === 'ECONNREFUSED' || error.code === 'ETIMEDOUT' || error.message?.includes('ECONNREFUSED')) {
        errorMsg = '⚠️ Backend server is not available. Please ensure the Flask backend is running on port 5000.';
        console.error('Backend connection error - Flask server may not be running');
      } else if (error.response) {
        errorMsg = error.response.data?.error || errorMsg;
      } else if (error.message) {
        errorMsg = error.message;
      }
      
      await client.sendMessage(message.from, menuRenderer.renderError(errorMsg));
    }
  } else {
    // Invalid confirmation
    await client.sendMessage(message.from, 
      'Please reply "confirm" to place the order or "cancel" to cancel.'
    );
  }
}

module.exports = {
  handleGroceryMenu,
  handleGroceryList,
  handleGroceryConfirm
};

