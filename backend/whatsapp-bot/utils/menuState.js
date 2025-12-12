/**
 * Menu State Manager - Track user conversation state and menu navigation
 */

// In-memory state storage: phone -> state
const userStates = new Map();

// State timeout: 30 minutes of inactivity
const STATE_TIMEOUT = 30 * 60 * 1000; // 30 minutes

// Cleanup interval: every 10 minutes
const CLEANUP_INTERVAL = 10 * 60 * 1000; // 10 minutes

/**
 * Get current state for a user
 * @param {string} phone - Normalized phone number
 * @returns {object|null} - Current state or null
 */
function getState(phone) {
  const state = userStates.get(phone);
  
  // Check if state is stale
  if (state && Date.now() - state.lastActivity > STATE_TIMEOUT) {
    userStates.delete(phone);
    return null;
  }
  
  return state || null;
}

/**
 * Set state for a user
 * @param {string} phone - Normalized phone number
 * @param {string} currentMenu - Current menu level
 * @param {object} context - Additional context data (if not provided, preserves existing context)
 */
function setState(phone, currentMenu, context = null) {
  const existingState = getState(phone);
  const preservedContext = context !== null ? context : (existingState ? existingState.context : {});
  
  userStates.set(phone, {
    currentMenu: currentMenu,
    context: preservedContext,
    lastActivity: Date.now()
  });
}

/**
 * Clear state for a user (reset to main menu)
 * @param {string} phone - Normalized phone number
 */
function clearState(phone) {
  userStates.delete(phone);
}

/**
 * Set context data for a user
 * @param {string} phone - Normalized phone number
 * @param {string} key - Context key
 * @param {*} value - Context value
 */
function setContext(phone, key, value) {
  const state = getState(phone);
  if (state) {
    state.context[key] = value;
    state.lastActivity = Date.now();
  } else {
    // Create new state if doesn't exist
    setState(phone, 'main', { [key]: value });
  }
}

/**
 * Get context data for a user
 * @param {string} phone - Normalized phone number
 * @param {string} key - Context key
 * @returns {*} - Context value or undefined
 */
function getContext(phone, key) {
  const state = getState(phone);
  return state ? state.context[key] : undefined;
}

/**
 * Get all context for a user
 * @param {string} phone - Normalized phone number
 * @returns {object} - Context object
 */
function getAllContext(phone) {
  const state = getState(phone);
  return state ? state.context : {};
}

/**
 * Check if user is in a specific menu state
 * @param {string} phone - Normalized phone number
 * @param {string} menuType - Menu type to check
 * @returns {boolean}
 */
function isInMenu(phone, menuType) {
  const state = getState(phone);
  return state && state.currentMenu === menuType;
}

/**
 * Check if user is in any menu state
 * @param {string} phone - Normalized phone number
 * @returns {boolean}
 */
function isInMenuState(phone) {
  return getState(phone) !== null;
}

/**
 * Cleanup stale states
 */
function cleanup() {
  const now = Date.now();
  let cleaned = 0;
  
  for (const [phone, state] of userStates.entries()) {
    if (now - state.lastActivity > STATE_TIMEOUT) {
      userStates.delete(phone);
      cleaned++;
    }
  }
  
  if (cleaned > 0) {
    console.log(`🧹 Cleaned up ${cleaned} stale menu states`);
  }
}

// Start periodic cleanup
setInterval(cleanup, CLEANUP_INTERVAL);

// Cleanup on startup
cleanup();

module.exports = {
  getState,
  setState,
  clearState,
  setContext,
  getContext,
  getAllContext,
  isInMenu,
  isInMenuState,
  cleanup
};

