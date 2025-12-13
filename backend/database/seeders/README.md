# Database Seed Scripts

This directory contains scripts to populate the database with sample data for development and testing.

## Available Seed Scripts

### 1. `seed_data.py` - Main Seed Data
Creates sample data for the core system:
- **8 Shopkeepers** - Located in **Delhi area** (Connaught Place, Karol Bagh, Lajpat Nagar, etc.)
- **25 Customers** - With names, phones, and addresses
- **12 Products per Shop** - Common grocery items (Rice, Wheat, Sugar, Oil, etc.)
- **150 Transactions** - Mix of sales, credit, and repay transactions
- **3 Cooperatives** - With members and revenue split configurations

**Usage:**
```bash
cd backend
python database/seeders/seed_data.py
```

### 2. `seed_suppliers.py` - Supplier Portal Data
Creates sample data for the Supplier Portal:
- **3 Suppliers** - First supplier is in Delhi (supplier1@example.com) with 35km radius
- **20 Supplier Orders** - Bulk orders from suppliers to shopkeepers with various statuses

**Usage:**
```bash
cd backend
python database/seeders/seed_suppliers.py
```

**Note:** Requires shopkeepers to exist first. Run `seed_data.py` before this.

### 3. `update_shopkeeper_locations.py` - Update Existing Locations (NEW)
Updates existing shopkeeper locations to Delhi area if they're in the wrong location.

**Usage:**
```bash
cd backend
python database/seeders/update_shopkeeper_locations.py
```

**Use this if:** You already have shopkeepers in Mumbai or other locations and want to move them to Delhi.

## Quick Start

### 1. Seed Core Data (Shopkeepers in Delhi)
```bash
cd backend
python database/seeders/seed_data.py
```

This will create:
- Shopkeepers located in **Delhi area** (around Connaught Place)
- Customers
- Products for each shopkeeper
- Transactions
- Cooperatives

### 2. Seed Supplier Data (Optional - for Supplier Portal)
```bash
cd backend
python database/seeders/seed_suppliers.py
```

This will create:
- 3 suppliers (Delhi supplier is supplier1@example.com)
- 20 supplier orders

### 3. If You Have Existing Data in Wrong Location
```bash
cd backend
python database/seeders/update_shopkeeper_locations.py
```

This will update existing shopkeepers to Delhi area.

## Supplier Login Credentials

After running `seed_suppliers.py`, you can login to the Supplier Portal using:

1. **Delhi Grocery Suppliers** (Primary - covers Delhi area)
   - Email: `supplier1@example.com`
   - Service Area: Connaught Place, Delhi (35km radius)
   - Request OTP via login page

2. **Mumbai Wholesale Distributors**
   - Email: `supplier2@example.com`
   - Request OTP via login page

3. **Bangalore Food Distributors**
   - Email: `supplier3@example.com`
   - Request OTP via login page

## Sample Data Details

### Shopkeepers (8) - All in Delhi Area
- All located in Delhi area (latitude ~28.6, longitude ~77.2)
- Locations: Connaught Place, Karol Bagh, Lajpat Nagar, Janakpuri, Rohini, Dwarka, Saket, Chandni Chowk
- Credit scores: 400-800
- Each has 12 products
- Wallet addresses: `0x1111...` through `0x8888...`

### Suppliers (3)
- **Delhi Grocery Suppliers (supplier1@example.com)**: 
  - Service area centered in Connaught Place, Delhi (28.6139, 77.2090)
  - **35km radius** - Covers all of Delhi
  - This is the default supplier for testing
  
- **Mumbai Wholesale Distributors**: 
  - Service area centered in Andheri, Mumbai (19.1136, 72.8697)
  - 25km radius
  
- **Bangalore Food Distributors**: 
  - Service area centered in Koramangala, Bangalore (12.9352, 77.6245)
  - 20km radius

### Products (Common Items)
- Rice, Wheat Flour, Sugar, Salt, Cooking Oil
- Tea, Coffee, Milk, Bread, Eggs
- Onions, Potatoes, Tomatoes
- Soap, Shampoo

### Orders
- Mix of statuses: pending (15%), confirmed (20%), dispatched (15%), delivered (45%), cancelled (5%)
- Orders from last 60 days
- Each order contains 2-5 products
- Realistic quantities and prices

## Troubleshooting

### Stores Not Showing in Supplier Portal?

1. **Check if supplier has service area set:**
   - Supplier must have `service_area_center` and `service_area_radius_km` set
   - Login as supplier and click "Set Service Area" if needed

2. **Check if shopkeepers are in supplier's service area:**
   - Shopkeepers must be within the supplier's service area radius
   - Run `update_shopkeeper_locations.py` if shopkeepers are in wrong location

3. **Check shopkeeper locations:**
   - Shopkeepers must have `location` field set
   - Run `seed_data.py` to create shopkeepers with locations

4. **Verify supplier is logged in:**
   - The `/api/supplier/stores` endpoint requires authentication
   - Make sure you're logged in with a valid session

5. **Default locations:**
   - Default map center: Delhi (28.6139, 77.2090)
   - Default supplier (supplier1@example.com) covers Delhi with 35km radius
   - All shopkeepers are seeded in Delhi area

## Resetting Data

To clear and reseed data, you can:

1. **Delete specific collections** (via MongoDB shell or Compass):
   ```javascript
   db.shopkeepers.deleteMany({})
   db.customers.deleteMany({})
   db.products.deleteMany({})
   db.transactions.deleteMany({})
   db.cooperatives.deleteMany({})
   db.suppliers.deleteMany({})
   db.supplier_orders.deleteMany({})
   ```

2. **Run seed scripts again**:
   ```bash
   python database/seeders/seed_data.py
   python database/seeders/seed_suppliers.py
   ```

## Notes

- Seed scripts check for existing data and skip duplicates (by unique fields like email, phone, wallet_address)
- **All shopkeepers are now seeded in Delhi area** for easier testing
- Delhi supplier (supplier1@example.com) has 35km radius to cover all of Delhi
- All dates are randomized within reasonable ranges
- Credit scores, prices, and quantities are randomized within realistic ranges
- Orders include realistic product combinations and quantities
