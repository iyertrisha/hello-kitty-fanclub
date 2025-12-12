/**
 * Debt Management Handler - Handle debt management sub-menu
 */
const menuState = require('../utils/menuState');
const menuRenderer = require('../utils/menuRenderer');
const debtQueryHandler = require('./debtQuery');
const debtRecordHandler = require('./debtRecord');
const paymentHandler = require('./payment');

/**
 * Handle debt management menu selection
 * @param {object} client - WhatsApp client
 * @param {object} message - Message object
 * @param {string} phone - Normalized phone
 * @param {number} selection - Menu selection
 */
async function handleDebtMenu(client, message, phone, selection) {
  const config = require('../config');
  
  console.log(`💰 Debt Management menu - selection: ${selection} for ${phone}`);
  
  try {
    switch (selection) {
      case 1:
        // Check Balance
        await debtQueryHandler.handle(client, message, phone, config);
        // Return to debt management menu after showing balance
        setTimeout(async () => {
          menuState.setState(phone, 'debt_management');
          await client.sendMessage(message.from, 
            '\n' + menuRenderer.renderDebtManagementMenu()
          );
        }, 2000);
        break;
        
      case 2:
        // Record Debt
        console.log(`📝 Setting state to debt_record_input for ${phone}`);
        menuState.setState(phone, 'debt_record_input');
        await client.sendMessage(message.from, 
          '📝 *Record Debt*\n\n' +
          'Please send the amount and description.\n\n' +
          'Example: "Bought milk for ₹120"\n\n' +
          'Reply "cancel" to go back.'
        );
        break;
        
      case 3:
        // Make Payment
        await client.sendMessage(message.from, 
          '💳 *Make Payment*\n\n' +
          'Please send the payment amount.\n\n' +
          'Example: "Paid ₹50"\n\n' +
          'Reply "cancel" to go back.'
        );
        menuState.setState(phone, 'payment_input');
        break;
        
      case 4:
        // Back to Main Menu
        menuState.setState(phone, 'main');
        await client.sendMessage(message.from, menuRenderer.renderMainMenu());
        break;
        
      default:
        await client.sendMessage(message.from, 
          menuRenderer.renderError('Invalid selection. Please choose 1-4.') + '\n\n' + 
          menuRenderer.renderDebtManagementMenu()
        );
    }
  } catch (error) {
    console.error('Error handling debt menu:', error);
    await client.sendMessage(message.from, 
      menuRenderer.renderError('An error occurred. Please try again.') + '\n\n' + 
      menuRenderer.renderMainMenu()
    );
    menuState.clearState(phone);
  }
}

module.exports = {
  handleDebtMenu
};

