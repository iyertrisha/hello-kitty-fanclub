import React, { useState } from 'react';
import './BulkOrderModal.css';

const BulkOrderModal = ({ store, onClose, onOrder }) => {
  const [products, setProducts] = useState([
    { name: '', quantity: 1, unit_price: 0 }
  ]);

  const addProduct = () => {
    setProducts([...products, { name: '', quantity: 1, unit_price: 0 }]);
  };

  const removeProduct = (index) => {
    setProducts(products.filter((_, i) => i !== index));
  };

  const updateProduct = (index, field, value) => {
    const updated = [...products];
    updated[index] = {
      ...updated[index],
      [field]: field === 'quantity' || field === 'unit_price' ? parseFloat(value) || 0 : value
    };
    setProducts(updated);
  };

  const calculateTotal = () => {
    return products.reduce((sum, p) => sum + (p.quantity * p.unit_price), 0);
  };

  const handleSubmit = () => {
    // Validate products
    const validProducts = products.filter(p => p.name && p.quantity > 0 && p.unit_price > 0);
    
    if (validProducts.length === 0) {
      alert('Please add at least one product with name, quantity, and price');
      return;
    }

    onOrder({
      shopkeeper_id: store.id,
      products: validProducts.map(p => ({
        name: p.name,
        quantity: p.quantity,
        unit_price: p.unit_price
      }))
    });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content bulk-order-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Create Bulk Order</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          <div className="store-info-section">
            <h3>{store.name}</h3>
            <p>{store.address}</p>
            <p>Phone: {store.phone}</p>
            <div className="store-metrics">
              <span>Credit Score: <strong>{store.credit_score}</strong></span>
              <span>30-Day Sales: <strong>₹{store.performance?.total_sales_30d?.toLocaleString() || 0}</strong></span>
            </div>
          </div>

          {store.performance?.low_stock_products && store.performance.low_stock_products.length > 0 && (
            <div className="suggested-products">
              <h4>Suggested Products (Low Stock)</h4>
              <div className="suggested-list">
                {store.performance.low_stock_products.map(product => (
                  <button
                    key={product.id}
                    className="suggested-item"
                    onClick={() => {
                      const exists = products.find(p => p.name.toLowerCase() === product.name.toLowerCase());
                      if (!exists) {
                        setProducts([...products, {
                          name: product.name,
                          quantity: 10,
                          unit_price: product.price || 0
                        }]);
                      }
                    }}
                  >
                    {product.name} (Current: {product.current_stock})
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="products-section">
            <div className="section-header">
              <h4>Order Products</h4>
              <button onClick={addProduct} className="btn-add">+ Add Product</button>
            </div>

            <div className="products-list">
              {products.map((product, index) => (
                <div key={index} className="product-row">
                  <input
                    type="text"
                    placeholder="Product name"
                    value={product.name}
                    onChange={(e) => updateProduct(index, 'name', e.target.value)}
                    className="product-name"
                  />
                  <input
                    type="number"
                    placeholder="Qty"
                    value={product.quantity}
                    onChange={(e) => updateProduct(index, 'quantity', e.target.value)}
                    min="1"
                    className="product-qty"
                  />
                  <input
                    type="number"
                    placeholder="Unit Price"
                    value={product.unit_price}
                    onChange={(e) => updateProduct(index, 'unit_price', e.target.value)}
                    min="0"
                    step="0.01"
                    className="product-price"
                  />
                  <span className="product-total">
                    ₹{(product.quantity * product.unit_price).toFixed(2)}
                  </span>
                  {products.length > 1 && (
                    <button
                      onClick={() => removeProduct(index)}
                      className="btn-remove"
                    >
                      ×
                    </button>
                  )}
                </div>
              ))}
            </div>

            <div className="order-total">
              <strong>Total Amount: ₹{calculateTotal().toFixed(2)}</strong>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn-cancel" onClick={onClose}>Cancel</button>
          <button className="btn-save" onClick={handleSubmit}>Create Order</button>
        </div>
      </div>
    </div>
  );
};

export default BulkOrderModal;

