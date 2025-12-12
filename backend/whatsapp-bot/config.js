/**
 * Configuration for WhatsApp Bot
 */
require('dotenv').config();

module.exports = {
  // Flask backend API URL
  flaskApiUrl: process.env.FLASK_API_URL || 'http://localhost:5000',
  
  // Reminder schedule (cron expression)
  // Default: Daily at 9 AM
  reminderSchedule: process.env.REMINDER_SCHEDULE || '0 9 * * *',
  
  // WhatsApp session storage
  sessionPath: process.env.WHATSAPP_SESSION_PATH || './.wwebjs_auth',
  
  // Logging
  logLevel: process.env.LOG_LEVEL || 'info',
  
  // Test mode - allows self-messaging for testing
  testMode: process.env.TEST_MODE === 'true' || false
};

