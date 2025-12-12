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
 * Send weekly reminder to a customer with enhanced details
 * @param {object} client - WhatsApp client
 * @param {object} customer - Customer data from API with history
 */
async function sendWeeklyReminder(client, customer) {
  try {
    const phone = customer.phone;
    // Add @s.whatsapp.net suffix for WhatsApp
    const whatsappPhone = phone.includes('@') ? phone : `${phone}@s.whatsapp.net`;
    
    // Format weekly reminder message
    const days = customer.days_since_first || 0;
    const history = customer.history || {};
    
    let daysText = days === 1 ? "1 day ago" : `${days} days ago`;
    
    let lastPaymentText = "Never";
    if (history.last_payment_date) {
      const lastPaymentDate = new Date(history.last_payment_date);
      const daysSincePayment = Math.floor((Date.now() - lastPaymentDate) / (1000 * 60 * 60 * 24));
      if (daysSincePayment === 0) {
        lastPaymentText = "Today";
      } else if (daysSincePayment === 1) {
        lastPaymentText = "1 day ago";
      } else {
        lastPaymentText = `${daysSincePayment} days ago`;
      }
    }
    
    const message = `📢 *Weekly Debt Reminder*\n\n` +
      `Dear ${customer.name || 'Customer'},\n\n` +
      `You have an outstanding balance of *₹${customer.total_debt.toFixed(2)}*\n\n` +
      `*Debt Details:*\n` +
      `• First debt: ${daysText}\n` +
      `• Total transactions: ${history.total_transactions || 0}\n` +
      `• Last payment: ${lastPaymentText}\n\n` +
      `Please clear your dues at your earliest convenience.\n\n` +
      `Thank you!`;
    
    await client.sendMessage(whatsappPhone, message);
    console.log(`✅ Weekly reminder sent to ${phone}`);
    
    return true;
  } catch (error) {
    console.error(`❌ Failed to send weekly reminder to ${customer.phone}:`, error);
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
 * Process weekly reminders
 * @param {object} client - WhatsApp client
 */
async function processWeeklyReminders(client) {
  try {
    console.log('⏰ Processing weekly reminders...');
    
    // Get list of customers needing weekly reminders
    const response = await axios.get(
      `${config.flaskApiUrl}/api/debt/weekly-reminders?days_threshold=7`,
      {
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 10000
      }
    );
    
    if (response.data && response.data.customers) {
      const customers = response.data.customers;
      console.log(`📋 Found ${customers.length} customers for weekly reminders`);
      
      // Send reminders
      let successCount = 0;
      for (const customer of customers) {
        const success = await sendWeeklyReminder(client, customer);
        if (success) {
          successCount++;
        }
        
        // Small delay between messages to avoid rate limiting
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
      
      console.log(`✅ Sent ${successCount}/${customers.length} weekly reminders successfully`);
    } else {
      console.log('⚠️ No customers found for weekly reminders');
    }
  } catch (error) {
    console.error('❌ Error processing weekly reminders:', error);
    
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
  
  // Schedule daily reminders
  reminderJob = cron.schedule(config.reminderSchedule, async () => {
    await processReminders(client);
  }, {
    scheduled: true,
    timezone: "Asia/Kolkata" // Indian timezone
  });
  
  // Schedule weekly reminders (every Monday at 9 AM)
  const weeklyJob = cron.schedule('0 9 * * 1', async () => {
    await processWeeklyReminders(client);
  }, {
    scheduled: true,
    timezone: "Asia/Kolkata"
  });
  
  console.log('✅ Reminder scheduler started (daily and weekly)');
  
  // Also run immediately on startup (for testing)
  // Uncomment for testing:
  // processReminders(client);
  // processWeeklyReminders(client);
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
  sendReminder,
  processWeeklyReminders,
  sendWeeklyReminder
};

