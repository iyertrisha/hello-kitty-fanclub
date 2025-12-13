/**
 * Noticeboard Handler - Display shopkeeper notices
 */
const axios = require('axios');
const config = require('../config');
const menuState = require('../utils/menuState');
const menuRenderer = require('../utils/menuRenderer');

/**
 * Handle noticeboard menu
 * @param {object} client - WhatsApp client
 * @param {object} message - Message object
 * @param {string} phone - Normalized phone
 */
async function handleNoticeboardMenu(client, message, phone) {
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
    
    // Get notices
    const noticesResponse = await axios.get(
      `${config.flaskApiUrl}/api/noticeboard?shopkeeper_id=${shopkeeperId}`,
      { timeout: 10000 }
    );
    
    if (noticesResponse.data && noticesResponse.data.notices) {
      const notices = noticesResponse.data.notices;
      const noticeboardMessage = menuRenderer.renderNoticeboard(notices);
      await client.sendMessage(message.from, noticeboardMessage);
    } else {
      await client.sendMessage(message.from, 
        menuRenderer.renderNoticeboard([])
      );
    }
  } catch (error) {
    console.error('Error displaying noticeboard:', error);
    
    let errorMsg = 'Failed to load noticeboard. Please try again later.';
    
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
 * Format notice for display
 * @param {object} notice - Notice object
 * @returns {string} - Formatted notice
 */
function formatNotice(notice) {
  const priorityEmoji = {
    'urgent': '🔴',
    'high': '🟠',
    'normal': '🟡',
    'low': '🟢'
  }[notice.priority] || '🟡';
  
  let formatted = `${priorityEmoji} *${notice.title}*\n`;
  formatted += `${notice.message}\n`;
  
  if (notice.created_at) {
    const date = new Date(notice.created_at);
    formatted += `📅 ${date.toLocaleDateString('en-IN')}\n`;
  }
  
  return formatted;
}

module.exports = {
  handleNoticeboardMenu,
  formatNotice
};

