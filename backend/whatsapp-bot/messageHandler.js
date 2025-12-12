/**
 * Message Handler - Routes incoming messages to appropriate handlers
 */
const axios = require('axios');
const config = require('./config');
const debtQueryHandler = require('./handlers/debtQuery');
const debtRecordHandler = require('./handlers/debtRecord');
const paymentHandler = require('./handlers/payment');
const menuState = require('./utils/menuState');
const menuRenderer = require('./utils/menuRenderer');

// Message deduplication
const processedMessages = new Set();
const MESSAGE_TIMEOUT = 60000; // 1 minute

// Rate limiting per phone number
const messageCounts = new Map();
const RATE_LIMIT = 10; // Max 10 messages per minute per number
const RATE_WINDOW = 60000; // 1 minute

/**
 * Normalize phone number to format expected by backend
 * @param {string} phone - Phone number from WhatsApp
 * @returns {string} - Normalized phone number
 */
function normalizePhone(phone) {
  // Remove both @s.whatsapp.net and @c.us suffixes
  let normalized = phone.replace('@s.whatsapp.net', '').replace('@c.us', '');
  
  // Add + prefix if not present
  if (!normalized.startsWith('+')) {
    // Assume Indian number if no country code
    if (normalized.length === 10) {
      normalized = '+91' + normalized;
    } else {
      normalized = '+' + normalized;
    }
  }
  
  return normalized;
}

/**
 * Detect intent from message text
 * @param {string} text - Message text
 * @returns {string} - Detected intent
 */
function detectIntent(text) {
  const lowerText = text.toLowerCase().trim();
  
  // Skip intent detection for single digits (these are menu selections)
  if (/^\d$/.test(lowerText)) {
    return 'unknown';
  }
  
  // Debt query keywords
  if (lowerText.match(/\b(balance|owe|debt|outstanding|due|how much)\b/)) {
    return 'debt_query';
  }
  
  // Payment keywords
  if (lowerText.match(/\b(paid|payment|repay|repaid|settled)\b/)) {
    return 'payment';
  }
  
  // Debt recording - check for numbers/amounts with context
  // Require currency symbols or keywords along with numbers
  if (lowerText.match(/\b(₹|rs|rupees?|bought|purchase|credit)\b/i) || 
      (lowerText.match(/\d+/) && lowerText.match(/\b(₹|rs|rupees?|bought|purchase|credit|for|milk|rice|sugar|salt|oil|groceries)\b/i))) {
    return 'debt_record';
  }
  
  // Default to debt query for greeting
  if (lowerText.match(/\b(hi|hello|hey|start)\b/)) {
    return 'greeting';
  }
  
  return 'unknown';
}

/**
 * Extract amount from message text
 * @param {string} text - Message text
 * @returns {number|null} - Extracted amount or null
 */
function extractAmount(text) {
  // Match currency symbols and numbers
  const patterns = [
    /₹\s*(\d+(?:\.\d+)?)/i,
    /rs\.?\s*(\d+(?:\.\d+)?)/i,
    /rupees?\s*(\d+(?:\.\d+)?)/i,
    /(\d+(?:\.\d+)?)\s*(?:rupees?|rs|₹)/i,
    /\b(\d+(?:\.\d+)?)\b/
  ];
  
  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (match) {
      const amount = parseFloat(match[1]);
      if (amount > 0 && amount < 1000000) { // Reasonable range
        return amount;
      }
    }
  }
  
  return null;
}

/**
 * Check if text is a menu selection (single digit 0-9)
 * @param {string} text - Message text
 * @returns {boolean}
 */
function isMenuSelection(text) {
  const trimmed = text.trim();
  return /^[0-9]$/.test(trimmed);
}

/**
 * Check if current state expects context input
 * @param {object} state - Menu state
 * @returns {boolean}
 */
function isContextInput(state) {
  return state.currentMenu === 'grocery_list_input' || 
         state.currentMenu === 'grocery_confirm' ||
         state.currentMenu === 'debt_record_input' ||
         state.currentMenu === 'payment_input';
}

/**
 * Handle menu selection
 * @param {object} client - WhatsApp client
 * @param {object} message - Message object
 * @param {string} phone - Normalized phone
 * @param {string} selection - Selected option
 * @param {object} state - Current menu state
 */
async function handleMenuSelection(client, message, phone, selection, state) {
  const selectionNum = parseInt(selection);
  
  // Import handlers dynamically to avoid circular dependencies
  const groceryOrderHandler = require('./handlers/groceryOrder');
  const debtManagementHandler = require('./handlers/debtManagement');
  const productCatalogHandler = require('./handlers/productCatalog');
  const noticeboardHandler = require('./handlers/noticeboard');
  
  try {
    switch (state.currentMenu) {
      case 'main':
        if (selectionNum === 1) {
          // Order Groceries
          menuState.setState(phone, 'grocery_list_input');
          await groceryOrderHandler.handleGroceryMenu(client, message, phone, selectionNum);
        } else if (selectionNum === 2) {
          // Debt Management
          menuState.setState(phone, 'debt_management');
          await client.sendMessage(message.from, menuRenderer.renderDebtManagementMenu());
        } else if (selectionNum === 3) {
          // More Details
          menuState.setState(phone, 'more_details');
          await client.sendMessage(message.from, menuRenderer.renderMoreDetailsMenu());
        } else {
          await client.sendMessage(message.from, 
            menuRenderer.renderError('Invalid selection. Please choose 1, 2, or 3.') + '\n\n' + 
            menuRenderer.renderMainMenu()
          );
        }
        break;
        
      case 'debt_management':
        await debtManagementHandler.handleDebtMenu(client, message, phone, selectionNum);
        break;
        
      case 'more_details':
        if (selectionNum === 1) {
          // Product Catalog
          menuState.setState(phone, 'product_catalog');
          await productCatalogHandler.handleCatalogMenu(client, message, phone, selectionNum);
        } else if (selectionNum === 2) {
          // Noticeboard
          menuState.setState(phone, 'noticeboard');
          await noticeboardHandler.handleNoticeboardMenu(client, message, phone);
        } else if (selectionNum === 3) {
          // Back to Main Menu
          menuState.setState(phone, 'main');
          await client.sendMessage(message.from, menuRenderer.renderMainMenu());
        } else {
          await client.sendMessage(message.from, 
            menuRenderer.renderError('Invalid selection. Please choose 1-3.') + '\n\n' + 
            menuRenderer.renderMoreDetailsMenu()
          );
        }
        break;
        
      default:
        await client.sendMessage(message.from, 
          menuRenderer.renderError('Invalid menu state.') + '\n\n' + 
          menuRenderer.renderMainMenu()
        );
        menuState.clearState(phone);
    }
  } catch (error) {
    console.error('Error handling menu selection:', error);
    await client.sendMessage(message.from, 
      menuRenderer.renderError('An error occurred. Please try again.') + '\n\n' + 
      menuRenderer.renderMainMenu()
    );
    menuState.clearState(phone);
  }
}

/**
 * Handle context input (grocery list, confirmations, etc.)
 * @param {object} client - WhatsApp client
 * @param {object} message - Message object
 * @param {string} phone - Normalized phone
 * @param {string} text - Input text
 * @param {object} state - Current menu state
 */
async function handleContextInput(client, message, phone, text, state) {
  const groceryOrderHandler = require('./handlers/groceryOrder');
  const debtRecordHandler = require('./handlers/debtRecord');
  const paymentHandler = require('./handlers/payment');
  const lowerText = text.toLowerCase().trim();
  
  // Handle cancel/back
  if (lowerText === 'cancel' || lowerText === 'back' || lowerText === '0') {
    if (state.currentMenu === 'debt_management') {
      menuState.setState(phone, 'debt_management');
      await client.sendMessage(message.from, menuRenderer.renderDebtManagementMenu());
    } else {
      menuState.clearState(phone);
      await client.sendMessage(message.from, menuRenderer.renderMainMenu());
    }
    return;
  }
  
  try {
    if (state.currentMenu === 'grocery_list_input') {
      await groceryOrderHandler.handleGroceryList(client, message, phone, text);
    } else if (state.currentMenu === 'grocery_confirm') {
      await groceryOrderHandler.handleGroceryConfirm(client, message, phone, text);
    } else if (state.currentMenu === 'debt_record_input') {
      // Handle debt record input
      const amount = extractAmount(text);
      if (amount) {
        await debtRecordHandler.handle(client, message, phone, amount, text, config);
        // Return to debt management menu after recording debt
        setTimeout(async () => {
          menuState.setState(phone, 'debt_management');
          await client.sendMessage(message.from, 
            '\n' + menuRenderer.renderDebtManagementMenu()
          );
        }, 2000);
      } else {
        await client.sendMessage(message.from, 
          'I couldn\'t find an amount in your message. Please send something like "Bought milk for ₹120" or "Credit ₹500".\n\n' +
          'Reply "cancel" to go back.'
        );
      }
    } else if (state.currentMenu === 'payment_input') {
      // Handle payment input
      const paymentAmount = extractAmount(text);
      if (paymentAmount) {
        await paymentHandler.handle(client, message, phone, paymentAmount, config);
        // Return to debt management menu after payment
        setTimeout(async () => {
          menuState.setState(phone, 'debt_management');
          await client.sendMessage(message.from, 
            '\n' + menuRenderer.renderDebtManagementMenu()
          );
        }, 2000);
      } else {
        await client.sendMessage(message.from, 
          'I couldn\'t find an amount in your message. Please send something like "Paid ₹500" or "Payment ₹1000".\n\n' +
          'Reply "cancel" to go back.'
        );
      }
    } else {
      // Unknown context - return to main menu
      menuState.clearState(phone);
      await client.sendMessage(message.from, menuRenderer.renderMainMenu());
    }
  } catch (error) {
    console.error('Error handling context input:', error);
    await client.sendMessage(message.from, 
      menuRenderer.renderError('An error occurred. Please try again.') + '\n\n' + 
      menuRenderer.renderMainMenu()
    );
    menuState.clearState(phone);
  }
}

/**
 * Handle incoming message
 * @param {object} client - WhatsApp client
 * @param {object} message - WhatsApp message object
 * @param {object} config - Configuration
 */
async function handleMessage(client, message, config) {
  // Skip if message is empty or just whitespace
  const text = (message.body || '').trim();
  if (!text || text.length === 0) {
    return; // Skip empty messages
  }
  
  // Normalize phone number
  const phone = normalizePhone(message.from);
  
  // Create unique message ID for deduplication
  // Use message.id if available (most reliable), otherwise create a composite ID
  const messageId = message.id || `${message.from}_${message.timestamp || Date.now()}_${text.substring(0, 20)}`;
  
  // Skip if we've already processed this message
  if (processedMessages.has(messageId)) {
    console.log(`⏭️ Skipping duplicate message: ${messageId}`);
    return;
  }
  
  // Add to processed set
  processedMessages.add(messageId);
  
  // Clean up old messages after timeout
  setTimeout(() => {
    processedMessages.delete(messageId);
  }, MESSAGE_TIMEOUT);
  
  // Rate limiting
  const now = Date.now();
  if (!messageCounts.has(phone)) {
    messageCounts.set(phone, { count: 0, resetTime: now + RATE_WINDOW });
  }
  const rateLimit = messageCounts.get(phone);
  if (now > rateLimit.resetTime) {
    rateLimit.count = 0;
    rateLimit.resetTime = now + RATE_WINDOW;
  }
  if (rateLimit.count >= RATE_LIMIT) {
    console.log(`⚠️ Rate limit exceeded for ${phone}`);
    await client.sendMessage(message.from, 
      'You\'re sending messages too quickly. Please wait a moment and try again.'
    );
    return;
  }
  rateLimit.count++;
  
  const hasMedia = message.hasMedia;
  
  // Improved logging with full message content
  console.log(`📨 Message from ${phone}: "${text}"`);

  // Handle media messages (photos) - future enhancement
  if (hasMedia) {
    await client.sendMessage(message.from, 
      'Photo support is coming soon! For now, please send the amount as text (e.g., "Bought milk for ₹120").'
    );
    return;
  }

  // Check for menu navigation commands
  const lowerText = text.toLowerCase().trim();
  if (lowerText === 'menu' || lowerText === 'start' || lowerText === 'help') {
    menuState.setState(phone, 'main');
    await client.sendMessage(message.from, menuRenderer.renderMainMenu());
    return;
  }

  // Check if user is in menu state
  if (menuState.isInMenuState(phone)) {
    const state = menuState.getState(phone);
    console.log(`📋 User ${phone} is in menu state: ${state.currentMenu}`);
    
    // Handle back/cancel commands
    if (lowerText === 'back' || lowerText === 'cancel' || lowerText === '0') {
      if (state.currentMenu === 'main') {
        await client.sendMessage(message.from, menuRenderer.renderMainMenu());
      } else {
        menuState.setState(phone, 'main');
        await client.sendMessage(message.from, menuRenderer.renderMainMenu());
      }
      return;
    }
    
    // Handle menu selection (numbers)
    if (isMenuSelection(text)) {
      console.log(`🔢 Menu selection detected: "${text}" in menu "${state.currentMenu}"`);
      await handleMenuSelection(client, message, phone, text, state);
      return;
    }
    
    // Handle context input (e.g., grocery list, confirmation)
    if (isContextInput(state)) {
      await handleContextInput(client, message, phone, text, state);
      return;
    }
    
    // Invalid input in menu state - show menu again
    await client.sendMessage(message.from, 
      menuRenderer.renderError('Invalid selection. Please choose a valid option.') + '\n\n' + 
      menuRenderer.renderSubMenu(state.currentMenu)
    );
    return;
  }
  
  // If not in menu state but user sends a single digit, show main menu
  if (isMenuSelection(text)) {
    console.log(`🔢 Single digit "${text}" detected but not in menu state. Showing main menu.`);
    menuState.setState(phone, 'main');
    await client.sendMessage(message.from, menuRenderer.renderMainMenu());
    return;
  }

  // Detect intent for non-menu interactions
  const intent = detectIntent(text);
  console.log(`🎯 Detected intent: ${intent}`);
  
  // Route to appropriate handler
  switch (intent) {
    case 'greeting':
      console.log(`👋 Greeting detected for ${phone}, setting menu state to 'main'`);
      menuState.setState(phone, 'main');
      const stateAfterGreeting = menuState.getState(phone);
      console.log(`✅ Menu state set:`, stateAfterGreeting);
      await client.sendMessage(message.from, menuRenderer.renderMainMenu());
      break;
      
    case 'debt_query':
      await debtQueryHandler.handle(client, message, phone, config);
      break;
      
    case 'debt_record':
      const amount = extractAmount(text);
      if (amount) {
        await debtRecordHandler.handle(client, message, phone, amount, text, config);
      } else {
        await client.sendMessage(message.from, 
          'I couldn\'t find an amount in your message. Please send something like "Bought milk for ₹120" or "Credit ₹500".'
        );
      }
      break;
      
    case 'payment':
      const paymentAmount = extractAmount(text);
      if (paymentAmount) {
        await paymentHandler.handle(client, message, phone, paymentAmount, config);
      } else {
        await client.sendMessage(message.from, 
          'I couldn\'t find an amount in your message. Please send something like "Paid ₹500" or "Payment ₹1000".'
        );
      }
      break;
      
    default:
      // Only respond if message has meaningful content
      if (text.length > 3 && text.match(/[a-zA-Z]/)) {
        await client.sendMessage(message.from, 
          'I didn\'t understand that. You can:\n' +
          '• Ask "How much do I owe?"\n' +
          '• Send "Bought milk for ₹120"\n' +
          '• Send "Paid ₹500"\n\n' +
          'Or type "help" for more options.'
        );
      } else {
        // Skip very short or non-text messages
        console.log(`⏭️ Skipping suspicious message: "${text}"`);
      }
      break;
  }
}

module.exports = {
  handleMessage,
  normalizePhone,
  detectIntent,
  extractAmount
};

