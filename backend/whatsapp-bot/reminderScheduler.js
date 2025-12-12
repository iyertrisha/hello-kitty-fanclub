/**
 * Reminder Scheduler - Send scheduled debt reminders
 */
const cron = require('node-cron');
const axios = require('axios');
const config = require('./config');

let reminderJob = null;

/**
 * Send reminder to a customer
 * @param {object} client - WhatsApp client
 * @param {object} customer - Customer data from API
 */
async function sendReminder(client, customer) {
  try {
    const phone = customer.phone;
    // Add @s.whatsapp.net suffix for WhatsApp
    const whatsappPhone = phone.includes('@') ? phone : `${phone}@s.whatsapp.net`;
    
    const message = `📢 *Reminder: Outstanding Debt*\n\n` +
      `Your current outstanding balance is *₹${customer.total_debt.toFixed(2)}*.\n\n` +
      `Please make a payment at your earliest convenience.\n\n` +
      `Thank you for your business!`;
    
    await client.sendMessage(whatsappPhone, message);
    console.log(`✅ Reminder sent to ${phone}`);
    
    return true;
  } catch (error) {
    console.error(`❌ Failed to send reminder to ${customer.phone}:`, error);
    return false;
  }
}

/**
 * Process reminders for all customers
 * @param {object} client - WhatsApp client
 */
async function processReminders(client) {
  try {
    console.log('⏰ Processing scheduled reminders...');
    
    // Get list of customers needing reminders
    const response = await axios.get(
      `${config.flaskApiUrl}/api/debt/reminders`,
      {
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 10000
      }
    );
    
    if (response.data && response.data.success) {
      const customers = response.data.customers || [];
      console.log(`📋 Found ${customers.length} customers needing reminders`);
      
      // Send reminders
      let successCount = 0;
      for (const customer of customers) {
        const success = await sendReminder(client, customer);
        if (success) {
          successCount++;
        }
        
        // Small delay between messages to avoid rate limiting
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
      
      console.log(`✅ Sent ${successCount}/${customers.length} reminders successfully`);
    } else {
      console.log('⚠️ No customers found for reminders');
    }
  } catch (error) {
    console.error('❌ Error processing reminders:', error);
    
    if (error.response) {
      console.error('API Error:', error.response.status, error.response.data);
    } else {
      console.error('Network Error:', error.message);
    }
  }
}

/**
 * Start the reminder scheduler
 * @param {object} client - WhatsApp client
 * @param {object} config - Configuration
 */
function start(client, config) {
  if (reminderJob) {
    console.log('⚠️ Reminder scheduler already running');
    return;
  }
  
  console.log(`📅 Starting reminder scheduler with schedule: ${config.reminderSchedule}`);
  
  // Schedule reminders
  reminderJob = cron.schedule(config.reminderSchedule, async () => {
    await processReminders(client);
  }, {
    scheduled: true,
    timezone: "Asia/Kolkata" // Indian timezone
  });
  
  console.log('✅ Reminder scheduler started');
  
  // Also run immediately on startup (for testing)
  // Uncomment for testing:
  // processReminders(client);
}

/**
 * Stop the reminder scheduler
 */
function stop() {
  if (reminderJob) {
    reminderJob.stop();
    reminderJob = null;
    console.log('🛑 Reminder scheduler stopped');
  }
}

module.exports = {
  start,
  stop,
  processReminders,
  sendReminder
};

