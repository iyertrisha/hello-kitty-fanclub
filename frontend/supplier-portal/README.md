# Supplier Portal

A React-based dashboard for suppliers to manage bulk orders to kirana stores.

## Features

- **Authentication**: Sign up and login for suppliers
- **Service Area Management**: Set and update your service area (location + radius)
- **Store Discovery**: View all kirana stores within your service area
- **Store Performance Metrics**: See credit scores, sales data, and inventory status
- **Bulk Ordering**: Create bulk orders to multiple stores with product details
- **Map View**: Visualize stores on an interactive map
- **Low Stock Alerts**: Identify stores that need inventory replenishment

## Setup

1. Install dependencies:
```bash
npm install
```

2. Set environment variables (create `.env` file):
```
REACT_APP_API_URL=http://localhost:5000/api
```

3. Start the development server:
```bash
npm start
```

The app will run on `http://localhost:3001`

## Usage

### Registration
1. Navigate to `/register`
2. Fill in your details (name, email, phone, password)
3. Optionally add company name and address
4. After registration, you'll be logged in automatically

### Setting Service Area
1. After login, click "Set Service Area" in the header
2. Click on the map to set the center of your service area
3. Adjust the radius slider (1-50 km)
4. Enter an address (optional)
5. Click "Save Service Area"

### Viewing Stores
- Stores are automatically loaded based on your service area
- Use the search bar to filter by store name or address
- Filter by:
  - All Stores
  - High Credit Score (700+)
  - Low Stock Stores
- Toggle between List and Map view

### Creating Bulk Orders
1. Click "Create Bulk Order" on any store card
2. Add products with name, quantity, and unit price
3. Use suggested products from low stock items
4. Review total amount
5. Click "Create Order" to submit

## API Endpoints Used

- `POST /api/supplier/register` - Register new supplier
- `POST /api/supplier/login` - Login supplier
- `GET /api/supplier/:id` - Get supplier details
- `PUT /api/supplier/:id/service-area` - Update service area
- `GET /api/supplier/:id/stores` - Get stores in service area
- `POST /api/supplier/:id/orders` - Create bulk order
- `GET /api/supplier/:id/orders` - Get all orders

## Technologies

- React 18
- React Router DOM
- React Leaflet (for maps)
- Axios (for API calls)
- CSS3

