/**
 * Debt Record Handler - Handle debt/bill recording
 */
const axios = require('axios');
const config = require('../config');

/**
 * Handle debt recording
 * @param {object} client - WhatsApp client
 * @param {object} message - WhatsApp message object
 * @param {string} phone - Normalized phone number
 * @param {number} amount - Extracted amount
 * @param {string} description - Original message text
 * @param {object} config - Configuration
 */
async function handle(client, message, phone, amount, description, config) {
  try {
    console.log(`📝 Recording debt: ₹${amount} for ${phone}`);
    
    // Extract description (remove amount and common words)
    let cleanDescription = description
      .replace(/₹\s*\d+(?:\.\d+)?/gi, '')
      .replace(/rs\.?\s*\d+(?:\.\d+)?/gi, '')
      .replace(/rupees?\s*\d+(?:\.\d+)?/gi, '')
      .replace(/\d+(?:\.\d+)?\s*(?:rupees?|rs|₹)/gi, '')
      .replace(/\b(bought|purchase|credit|for|of)\b/gi, '')
      .trim();
    
    if (!cleanDescription || cleanDescription.length < 3) {
      cleanDescription = 'Debt entry';
    }
    
    // Call Flask API
    const response = await axios.post(
      `${config.flaskApiUrl}/api/debt/record`,
      {
        phone,
        amount,
        description: cleanDescription
      },
      {
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 15000 // Longer timeout for blockchain
      }
    );
    
    if (response.data && response.data.success) {
      const result = response.data;
      
      // Format confirmation message
      let reply = `✅ *Debt Recorded*\n\n`;
      reply += `Amount: ₹${amount.toFixed(2)}\n`;
      reply += `Description: ${cleanDescription}\n`;
      reply += `New Balance: ₹${result.new_balance.toFixed(2)}\n`;
      
      if (result.blockchain_tx_id) {
        reply += `\n🔗 Blockchain: ${result.blockchain_tx_id.substring(0, 20)}...`;
      }
      
      await client.sendMessage(message.from, reply);
    } else {
      await client.sendMessage(message.from, 
        'Sorry, I couldn\'t record the debt. Please try again later.'
      );
    }
  } catch (error) {
    console.error('Error recording debt:', error);
    
    if (error.response) {
      const status = error.response.status;
      const errorMsg = error.response.data?.error || 'Unknown error';
      
      if (status === 404) {
        await client.sendMessage(message.from, 
          'I couldn\'t find your account. Please make sure you\'re registered with us.'
        );
      } else if (status === 400) {
        await client.sendMessage(message.from, 
          `Invalid request: ${errorMsg}`
        );
      } else {
        await client.sendMessage(message.from, 
          'Sorry, I encountered an error recording the debt. Please try again later.'
        );
      }
    } else {
      await client.sendMessage(message.from, 
        'Sorry, I couldn\'t connect to the server. Please try again later.'
      );
    }
  }
}

module.exports = { handle };

