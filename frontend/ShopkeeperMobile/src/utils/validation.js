/**
 * Validation utility functions
 */

export const validateRequired = (value, fieldName = 'Field') => {
  if (!value || (typeof value === 'string' && value.trim() === '')) {
    return `${fieldName} is required`;
  }
  return null;
};

export const validateEmail = (email) => {
  if (!email) return 'Email is required';
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return 'Invalid email format';
  }
  return null;
};

export const validatePhone = (phone) => {
  if (!phone) return 'Phone number is required';
  const phoneRegex = /^[6-9]\d{9}$/;
  const cleaned = phone.replace(/\D/g, '');
  if (!phoneRegex.test(cleaned)) {
    return 'Invalid phone number (should be 10 digits starting with 6-9)';
  }
  return null;
};

export const validateAmount = (amount) => {
  if (!amount) return 'Amount is required';
  const numAmount = parseFloat(amount);
  if (isNaN(numAmount)) {
    return 'Amount must be a valid number';
  }
  if (numAmount <= 0) {
    return 'Amount must be greater than 0';
  }
  return null;
};

export const validateStock = (stock) => {
  if (stock === null || stock === undefined) return 'Stock quantity is required';
  const numStock = parseInt(stock);
  if (isNaN(numStock)) {
    return 'Stock must be a valid number';
  }
  if (numStock < 0) {
    return 'Stock cannot be negative';
  }
  return null;
};

export const validateTransaction = (data) => {
  const errors = {};
  
  const typeError = validateRequired(data.type, 'Transaction type');
  if (typeError) errors.type = typeError;
  
  const amountError = validateAmount(data.amount);
  if (amountError) errors.amount = amountError;
  
  const customerError = validateRequired(data.customer_id, 'Customer ID');
  if (customerError) errors.customer_id = customerError;
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};

export const validateProduct = (data) => {
  const errors = {};
  
  const nameError = validateRequired(data.name, 'Product name');
  if (nameError) errors.name = nameError;
  
  const priceError = validateAmount(data.price);
  if (priceError) errors.price = priceError;
  
  const stockError = validateStock(data.stock_quantity);
  if (stockError) errors.stock_quantity = stockError;
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};



