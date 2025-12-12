/**
 * Grocery Parser - Parse natural language grocery lists
 */

/**
 * Parse grocery list from natural language text
 * Supports formats:
 * - "2kg rice, 1kg sugar, 500g salt"
 * - "Rice 2kg, Sugar 1kg"
 * - "2 rice, 1 sugar"
 * - "2 x rice, 1 x sugar"
 * 
 * @param {string} text - Grocery list text
 * @returns {Array} - Parsed items: [{ name, quantity, unit }]
 */
function parseGroceryList(text) {
  const items = [];
  
  // Normalize text: remove extra spaces, lowercase
  let normalized = text.trim().toLowerCase();
  
  // Split by common delimiters: comma, newline, semicolon, "and"
  const parts = normalized.split(/[,;\n]|(?:\s+and\s+)/i).map(p => p.trim()).filter(p => p);
  
  for (const part of parts) {
    const item = parseItem(part);
    if (item) {
      items.push(item);
    }
  }
  
  return items;
}

/**
 * Parse a single grocery item
 * @param {string} text - Item text (e.g., "2kg rice", "rice 2kg", "2 rice")
 * @returns {object|null} - { name, quantity, unit } or null
 */
function parseItem(text) {
  // Patterns to match:
  // 1. "2kg rice" or "2 kg rice" - quantity + unit + name
  // 2. "rice 2kg" or "rice 2 kg" - name + quantity + unit
  // 3. "2 rice" - quantity + name (no unit)
  // 4. "2 x rice" or "2x rice" - quantity + x + name
  
  // Remove "x" markers
  text = text.replace(/\s*x\s*/gi, ' ');
  
  // Pattern 1: quantity + unit + name
  let match = text.match(/^(\d+(?:\.\d+)?)\s*(kg|g|gm|gram|grams|kilo|kilogram|kilograms|piece|pieces|pcs|pc|pack|packs|bottle|bottles|packet|packets|box|boxes|dozen|dozens|litre|litres|liter|liters|l|ml)\s+(.+)$/i);
  if (match) {
    return {
      name: match[3].trim(),
      quantity: parseFloat(match[1]),
      unit: normalizeUnit(match[2])
    };
  }
  
  // Pattern 2: name + quantity + unit
  match = text.match(/^(.+?)\s+(\d+(?:\.\d+)?)\s*(kg|g|gm|gram|grams|kilo|kilogram|kilograms|piece|pieces|pcs|pc|pack|packs|bottle|bottles|packet|packets|box|boxes|dozen|dozens|litre|litres|liter|liters|l|ml)$/i);
  if (match) {
    return {
      name: match[1].trim(),
      quantity: parseFloat(match[2]),
      unit: normalizeUnit(match[3])
    };
  }
  
  // Pattern 3: quantity + name (no unit, assume pieces)
  match = text.match(/^(\d+(?:\.\d+)?)\s+(.+)$/);
  if (match) {
    return {
      name: match[2].trim(),
      quantity: parseFloat(match[1]),
      unit: 'piece'
    };
  }
  
  // Pattern 4: just name (assume quantity 1)
  if (text.length > 0 && !text.match(/^\d/)) {
    return {
      name: text.trim(),
      quantity: 1,
      unit: 'piece'
    };
  }
  
  return null;
}

/**
 * Normalize unit to standard format
 * @param {string} unit - Unit string
 * @returns {string} - Normalized unit
 */
function normalizeUnit(unit) {
  const normalized = unit.toLowerCase().trim();
  
  // Weight units
  if (['kg', 'kilo', 'kilogram', 'kilograms'].includes(normalized)) {
    return 'kg';
  }
  if (['g', 'gm', 'gram', 'grams'].includes(normalized)) {
    return 'g';
  }
  
  // Volume units
  if (['l', 'litre', 'litres', 'liter', 'liters'].includes(normalized)) {
    return 'l';
  }
  if (['ml', 'millilitre', 'millilitres', 'milliliter', 'milliliters'].includes(normalized)) {
    return 'ml';
  }
  
  // Count units
  if (['piece', 'pieces', 'pc', 'pcs'].includes(normalized)) {
    return 'piece';
  }
  if (['pack', 'packs', 'packet', 'packets'].includes(normalized)) {
    return 'pack';
  }
  if (['bottle', 'bottles'].includes(normalized)) {
    return 'bottle';
  }
  if (['box', 'boxes'].includes(normalized)) {
    return 'box';
  }
  if (['dozen', 'dozens'].includes(normalized)) {
    return 'dozen';
  }
  
  // Default to piece
  return 'piece';
}

/**
 * Convert quantity to base unit for comparison
 * @param {number} quantity - Quantity
 * @param {string} unit - Unit
 * @returns {number} - Quantity in base unit (kg for weight, l for volume, count for pieces)
 */
function convertToBaseUnit(quantity, unit) {
  switch (unit) {
    case 'g':
      return quantity / 1000; // Convert to kg
    case 'kg':
      return quantity;
    case 'ml':
      return quantity / 1000; // Convert to l
    case 'l':
      return quantity;
    case 'dozen':
      return quantity * 12; // Convert to pieces
    default:
      return quantity; // Pieces, packs, etc. stay as is
  }
}

module.exports = {
  parseGroceryList,
  parseItem,
  normalizeUnit,
  convertToBaseUnit
};

