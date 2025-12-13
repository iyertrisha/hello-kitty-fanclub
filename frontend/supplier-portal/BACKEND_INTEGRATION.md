# Supplier Portal - Backend Integration Guide

## ✅ Backend Integration Status

The supplier portal is fully integrated with the Flask backend API.

### API Configuration

**Base URL:** `http://localhost:5000/api` (configurable via `REACT_APP_API_URL`)

**Location:** `src/services/api.js`

### Authentication Flow

1. **Request OTP:** `POST /api/supplier/login/request-otp`
   - Sends OTP to supplier email
   - Uses SendGrid email service

2. **Verify OTP:** `POST /api/supplier/login/verify-otp`
   - Verifies OTP code
   - Creates Flask session
   - Auto-creates supplier if first login

3. **Session Check:** `GET /api/supplier/session`
   - Validates existing session
   - Returns supplier data if authenticated

4. **Logout:** `POST /api/supplier/logout`
   - Clears Flask session

### Database Integration

**MongoDB Connection:**
- Database: `kirana_db` (configurable via `MONGODB_DB_NAME`)
- Connection validated on app startup
- Uses MongoEngine ODM

**Models Used:**
- `Supplier` - Supplier accounts
- `Shopkeeper` - Store data
- `SupplierOrder` - Bulk orders
- `Product` - Inventory items
- `Transaction` - Sales/credit transactions
- `Location` - Geographic coordinates

### Seeded Data Usage

**To Use Seeded Data:**

1. **Seed Core Data (Shopkeepers in Delhi):**
   ```bash
   cd backend
   python database/seeders/seed_data.py
   ```
   - Creates 8 shopkeepers in Delhi area
   - Creates products, transactions, customers

2. **Seed Supplier Data:**
   ```bash
   cd backend
   python database/seeders/seed_suppliers.py
   ```
   - Creates 3 suppliers (Delhi supplier is `supplier1@example.com`)
   - Creates 20 sample orders

**Default Login Credentials:**
- **Email:** `supplier1@example.com` (Delhi Grocery Suppliers)
- **Service Area:** Connaught Place, Delhi (35km radius)
- **Stores:** Should see 8 stores in Delhi area

### API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|----------|
| `/api/supplier/login/request-otp` | POST | Request OTP |
| `/api/supplier/login/verify-otp` | POST | Verify OTP & login |
| `/api/supplier/session` | GET | Check session |
| `/api/supplier/logout` | POST | Logout |
| `/api/supplier/service-area` | PUT | Update service area |
| `/api/supplier/stores` | GET | Get stores in service area |
| `/api/supplier/orders` | POST | Create order |
| `/api/supplier/orders` | GET | List orders |
| `/api/supplier/orders/:id` | GET | Get order details |
| `/api/supplier/orders/:id/status` | PUT | Update order status |
| `/api/supplier/orders/:id` | DELETE | Cancel order |
| `/api/supplier/analytics/overview` | GET | Analytics overview |
| `/api/supplier/analytics/orders` | GET | Order analytics |
| `/api/supplier/analytics/stores` | GET | Store analytics |
| `/api/supplier/analytics/revenue` | GET | Revenue analytics |

### Session Management

- Uses Flask sessions (filesystem-based)
- Session stored in cookies (`withCredentials: true`)
- Session lifetime: 7 days
- Session validated on each API call via `@require_supplier_session` decorator

### Error Handling

- 401 Unauthorized → Redirects to login
- API errors logged to console
- User-friendly error messages displayed

### Testing Backend Integration

1. **Start Backend:**
   ```bash
   cd backend
   python run.py
   ```
   Should see: `✅ Connected to MongoDB: kirana_db`

2. **Start Frontend:**
   ```bash
   cd frontend/supplier-portal
   npm start
   ```

3. **Test Login:**
   - Go to login page
   - Enter: `supplier1@example.com`
   - Request OTP (check email or logs)
   - Enter OTP code
   - Should redirect to dashboard

4. **Verify Stores:**
   - After login, should see 8 stores in Delhi
   - Stores appear in list and map view
   - Each store shows performance metrics

### Troubleshooting

**No stores showing:**
- Check if shopkeepers are seeded in Delhi area
- Verify supplier has service area set
- Check browser console for API errors
- Verify MongoDB connection in backend logs

**API connection errors:**
- Verify backend is running on port 5000
- Check CORS settings in backend
- Verify `REACT_APP_API_URL` in frontend

**Session not persisting:**
- Check browser cookies are enabled
- Verify `withCredentials: true` in axios config
- Check Flask session configuration

