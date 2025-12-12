/**
 * Payment Handler - Handle payment confirmations
 */
const axios = require('axios');
const config = require('../config');

/**
 * Handle payment recording
 * @param {object} client - WhatsApp client
 * @param {object} message - WhatsApp message object
 * @param {string} phone - Normalized phone number
 * @param {number} amount - Payment amount
 * @param {object} config - Configuration
 */
async function handle(client, message, phone, amount, config) {
  try {
    console.log(`💳 Recording payment: ₹${amount} from ${phone}`);
    
    // Call Flask API
    const response = await axios.post(
      `${config.flaskApiUrl}/api/debt/payment`,
      {
        phone,
        amount
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
      let reply = `✅ *Payment Recorded*\n\n`;
      reply += `Amount: ₹${amount.toFixed(2)}\n`;
      reply += `Previous Balance: ₹${result.previous_balance.toFixed(2)}\n`;
      reply += `New Balance: ₹${result.new_balance.toFixed(2)}\n`;
      
      if (result.new_balance === 0) {
        reply += `\n🎉 Your account is now fully paid!`;
      }
      
      if (result.blockchain_tx_id) {
        reply += `\n🔗 Blockchain: ${result.blockchain_tx_id.substring(0, 20)}...`;
      }
      
      await client.sendMessage(message.from, reply);
    } else {
      await client.sendMessage(message.from, 
        'Sorry, I couldn\'t record the payment. Please try again later.'
      );
    }
  } catch (error) {
    console.error('Error recording payment:', error);
    
    if (error.response) {
      const status = error.response.status;
      const errorMsg = error.response.data?.error || 'Unknown error';
      
      if (status === 404) {
        await client.sendMessage(message.from, 
          'I couldn\'t find your account. Please make sure you\'re registered with us.'
        );
      } else if (status === 400) {
        if (errorMsg.includes('exceeds')) {
          await client.sendMessage(message.from, 
            `Payment amount (₹${amount}) exceeds your outstanding balance. Please check your balance first.`
          );
        } else {
          await client.sendMessage(message.from, 
            `Invalid request: ${errorMsg}`
          );
        }
      } else {
        await client.sendMessage(message.from, 
          'Sorry, I encountered an error recording the payment. Please try again later.'
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

