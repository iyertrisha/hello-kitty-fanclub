/**
 * Debt Query Handler - Handle "How much do I owe?" queries
 */
const axios = require('axios');
const config = require('../config');

/**
 * Handle debt query
 * @param {object} client - WhatsApp client
 * @param {object} message - WhatsApp message object
 * @param {string} phone - Normalized phone number
 * @param {object} config - Configuration
 */
async function handle(client, message, phone, config) {
  try {
    console.log(`🔍 Querying debt for ${phone}`);
    
    // Call Flask API
    const response = await axios.post(
      `${config.flaskApiUrl}/api/debt/query`,
      { phone },
      {
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 10000
      }
    );
    
    if (response.data && response.data.success) {
      const summary = response.data.summary;
      
      // Format response message
      let reply = `💰 *Your Debt Summary*\n\n`;
      reply += `Total Outstanding: ₹${summary.total_debt.toFixed(2)}\n`;
      
      if (summary.recent_transactions && summary.recent_transactions.length > 0) {
        reply += `\nRecent Transactions:\n`;
        summary.recent_transactions.slice(0, 5).forEach(tx => {
          const date = new Date(tx.timestamp).toLocaleDateString('en-IN');
          const type = tx.type === 'credit' ? '➕' : '➖';
          reply += `${type} ₹${tx.amount.toFixed(2)} - ${date}\n`;
        });
      }
      
      if (summary.next_reminder_date) {
        reply += `\n📅 Next reminder: ${summary.next_reminder_date}`;
      }
      
      await client.sendMessage(message.from, reply);
    } else {
      await client.sendMessage(message.from, 
        'Sorry, I couldn\'t retrieve your debt information. Please try again later.'
      );
    }
  } catch (error) {
    console.error('Error querying debt:', error);
    
    if (error.response && error.response.status === 404) {
      await client.sendMessage(message.from, 
        'I couldn\'t find your account. Please make sure you\'re registered with us.'
      );
    } else {
      await client.sendMessage(message.from, 
        'Sorry, I encountered an error. Please try again later.'
      );
    }
  }
}

module.exports = { handle };

