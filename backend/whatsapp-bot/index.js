/**
 * WhatsApp Bot - Main Entry Point
 * Free WhatsApp bot for debt tracking using whatsapp-web.js
 */
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const fs = require('fs');
const path = require('path');
const config = require('./config');
const messageHandler = require('./messageHandler');
const reminderScheduler = require('./reminderScheduler');

// Initialize WhatsApp client with improved error handling
const client = new Client({
  authStrategy: new LocalAuth({
    dataPath: config.sessionPath
  }),
  puppeteer: {
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-accelerated-2d-canvas',
      '--no-first-run',
      '--no-zygote',
      '--single-process',
      '--disable-gpu',
      '--disable-software-rasterizer',
      '--disable-extensions',
      '--disable-background-networking',
      '--disable-background-timer-throttling',
      '--disable-backgrounding-occluded-windows',
      '--disable-breakpad',
      '--disable-component-extensions-with-background-page',
      '--disable-features=TranslateUI',
      '--disable-ipc-flooding-protection',
      '--disable-renderer-backgrounding',
      '--enable-features=NetworkService,NetworkServiceInProcess',
      '--force-color-profile=srgb',
      '--hide-scrollbars',
      '--metrics-recording-only',
      '--mute-audio',
      '--no-default-browser-check',
      '--no-pings',
      '--use-mock-keychain'
    ],
    // Add timeout settings
    timeout: 60000,
    // Use system Chrome if available
    executablePath: process.env.CHROME_PATH || undefined
  },
  // Add web version cache
  webVersionCache: {
    type: 'remote',
    remotePath: 'https://raw.githubusercontent.com/wppconnect-team/wa-version/main/html/2.2413.51.html',
  }
});

// QR Code generation
client.on('qr', (qr) => {
  console.log('📱 Scan this QR code with WhatsApp to connect:');
  qrcode.generate(qr, { small: true });
  console.log('\nOr visit the URL above to scan the QR code');
});

// Ready event
client.on('ready', () => {
  console.log('✅ WhatsApp Bot is ready!');
  console.log(`📡 Connected to Flask API: ${config.flaskApiUrl}`);
  
  // Start reminder scheduler
  reminderScheduler.start(client, config);
});

// Authentication events
client.on('authenticated', () => {
  console.log('✅ WhatsApp authenticated');
});

client.on('auth_failure', (msg) => {
  console.error('❌ Authentication failed:', msg);
});

client.on('disconnected', async (reason) => {
  console.log('⚠️ WhatsApp disconnected:', reason);
  
  if (reason === 'LOGOUT') {
    console.log('🔄 Logged out. Cleaning up session...');
    
    // Give it a moment before trying to reconnect
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Try to destroy client gracefully
    try {
      await client.destroy();
    } catch (error) {
      console.log('⚠️ Error during cleanup (this is usually okay):', error.message);
    }
    
    console.log('💡 Please restart the bot manually: npm start');
    console.log('💡 Or run cleanup.ps1 if you see file lock errors');
    process.exit(0);
  } else {
    console.log('Reconnecting...');
    // Let the client handle reconnection automatically
  }
});

// Message handling
client.on('message', async (message) => {
  // Ignore messages from groups and status
  if (message.from === 'status@broadcast') {
    return;
  }
  
  // Ignore messages sent by the bot itself (unless in test mode)
  if (message.fromMe && !config.testMode) {
    return;
  }
  
  // In test mode, handle self-messages but skip the fromMe check
  if (message.fromMe && config.testMode) {
    console.log('🧪 TEST MODE: Processing self-message for testing');
  }
  
  try {
    await messageHandler.handleMessage(client, message, config);
  } catch (error) {
    console.error('Error handling message:', error);
    
    // Send error message to user
    try {
      await client.sendMessage(message.from, 
        'Sorry, I encountered an error processing your message. Please try again later.'
      );
    } catch (sendError) {
      console.error('Error sending error message:', sendError);
    }
  }
});

// Error handling
client.on('error', (error) => {
  console.error('WhatsApp client error:', error);
});

// Start the client with retry logic
let retryCount = 0;
const MAX_RETRIES = 3;

async function startClient() {
  try {
    console.log('🚀 Starting WhatsApp Bot...');
    await client.initialize();
    retryCount = 0; // Reset on success
  } catch (error) {
    retryCount++;
    console.error(`❌ Failed to initialize (Attempt ${retryCount}/${MAX_RETRIES}):`, error.message);
    
    if (retryCount < MAX_RETRIES) {
      console.log(`⏳ Retrying in 5 seconds...`);
      
      // Clean up before retry
      try {
        await client.destroy();
      } catch (e) {
        // Ignore cleanup errors
      }
      
      // Clear session on first retry
      if (retryCount === 1) {
        const sessionPath = path.join(__dirname, config.sessionPath || '.wwebjs_auth');
        if (fs.existsSync(sessionPath)) {
          console.log('🧹 Clearing corrupted session...');
          try {
            fs.rmSync(sessionPath, { recursive: true, force: true });
            console.log('✅ Session cleared');
          } catch (rmError) {
            console.error('⚠️ Could not clear session:', rmError.message);
          }
        }
      }
      
      setTimeout(() => {
        startClient();
      }, 5000);
    } else {
      console.error('❌ Max retries reached. Please check your setup.');
      console.error('💡 Try: Delete .wwebjs_auth folder and restart');
      console.error('💡 Or run: .\\cleanup.ps1');
      process.exit(1);
    }
  }
}

startClient();

// Handle uncaught exceptions
process.on('uncaughtException', async (error) => {
  console.error('❌ Uncaught Exception:', error);
  
  if (error.message && error.message.includes('EBUSY')) {
    console.error('💡 File lock error detected. This usually means:');
    console.error('   1. Chrome/Chromium is still running');
    console.error('   2. Another bot instance is running');
    console.error('   Solution: Run cleanup.ps1 or manually close Chrome processes');
  }
  
  try {
    await client.destroy();
  } catch (e) {
    // Ignore cleanup errors
  }
  
  process.exit(1);
});

// Handle unhandled promise rejections
process.on('unhandledRejection', async (reason, promise) => {
  console.error('❌ Unhandled Rejection at:', promise, 'reason:', reason);
  
  if (reason && reason.message && reason.message.includes('EBUSY')) {
    console.error('💡 File lock error. Run cleanup.ps1 to fix.');
  }
  
  // Don't exit on unhandled rejection, just log it
  // The process will continue running
});

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('\n🛑 Shutting down WhatsApp Bot...');
  try {
    await client.destroy();
  } catch (error) {
    console.error('Error during shutdown:', error.message);
  }
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.log('\n🛑 Shutting down WhatsApp Bot...');
  try {
    await client.destroy();
  } catch (error) {
    console.error('Error during shutdown:', error.message);
  }
  process.exit(0);
});

