/**
 * Message Handler - Routes incoming messages to appropriate handlers
 */
const axios = require('axios');
const config = require('./config');
const debtQueryHandler = require('./handlers/debtQuery');
const debtRecordHandler = require('./handlers/debtRecord');
const paymentHandler = require('./handlers/payment');

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
  
  // Debt query keywords
  if (lowerText.match(/\b(balance|owe|debt|outstanding|due|how much)\b/)) {
    return 'debt_query';
  }
  
  // Payment keywords
  if (lowerText.match(/\b(paid|payment|repay|repaid|settled)\b/)) {
    return 'payment';
  }
  
  // Debt recording - check for numbers/amounts
  if (lowerText.match(/\b(₹|rs|rupees?|bought|purchase|credit)\b/i) || 
      lowerText.match(/\d+/)) {
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
  
  // Detect intent
  const intent = detectIntent(text);
  console.log(`🎯 Detected intent: ${intent}`);
  
  // Route to appropriate handler
  switch (intent) {
    case 'greeting':
      await client.sendMessage(message.from, 
        '👋 Hello! I\'m your KiranaChain debt tracking assistant.\n\n' +
        'You can:\n' +
        '• Ask "How much do I owe?" to check your balance\n' +
        '• Send "Bought milk for ₹120" to record a debt\n' +
        '• Send "Paid ₹500" to record a payment\n\n' +
        'How can I help you today?'
      );
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

