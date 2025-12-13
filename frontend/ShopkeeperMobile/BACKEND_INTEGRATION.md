# Backend Integration Guide

This guide explains how to switch from mock API data to real backend endpoints.

## Current State

The app currently uses mock data from `src/services/mockApi.js` for development and testing. All API calls in `src/services/api.js` are commented out and use mock data instead.

## Steps to Integrate Real Backend

### 1. Update API Base URL

**File:** `src/services/api.js`

Update the `API_BASE_URL` constant:

```javascript
// For local development (emulator)
const API_BASE_URL = 'http://10.0.2.2:5000/api';

// For physical device testing
const API_BASE_URL = 'http://192.168.1.XXX:5000/api'; // Replace XXX with your computer's IP

// For production
const API_BASE_URL = 'https://your-backend-domain.com/api';
```

### 2. Switch API Calls from Mock to Real

For each API method in `src/services/api.js`:

**Before (Mock):**
```javascript
getTransactions: async (params = {}) => {
  return await mockApiService.getTransactions(params);
  
  // Real API call (uncomment when backend is ready):
  // const response = await api.get('/transactions', { params });
  // return response.data;
},
```

**After (Real):**
```javascript
getTransactions: async (params = {}) => {
  // Real API call
  const response = await api.get('/transactions', { params });
  return response.data;
  
  // Mock data for testing (comment out when backend is ready):
  // return await mockApiService.getTransactions(params);
},
```

### 3. Required Backend Endpoints

Ensure your backend implements these endpoints:

#### Transactions
- `GET /api/transactions` - List transactions
- `POST /api/transactions` - Create transaction
- `GET /api/transactions/:id` - Get transaction details
- `PUT /api/transactions/:id` - Update transaction
- `POST /api/transactions/transcribe` - Upload audio for transcription

#### Shopkeeper
- `GET /api/shopkeeper/:id` - Get shopkeeper profile
- `GET /api/shopkeeper/:id/credit-score` - Get credit score
- `GET /api/shopkeeper/:id/inventory` - Get inventory
- `POST /api/shopkeeper/:id/inventory` - Add product
- `PUT /api/shopkeeper/:id/inventory/:product_id` - Update product
- `DELETE /api/shopkeeper/:id/inventory/:product_id` - Delete product

#### Cooperatives
- `GET /api/cooperative` - List cooperatives
- `GET /api/cooperative/:id` - Get cooperative details
- `POST /api/cooperative/:id/join` - Join cooperative
- `POST /api/cooperative/:id/leave` - Leave cooperative
- `GET /api/cooperative/:id/members` - Get members list

#### Blockchain
- `GET /api/blockchain/credit-score/:shopkeeper_id` - Get verification status

### 4. Request/Response Formats

#### Create Transaction
**Request:**
```json
{
  "type": "sale|credit|repay",
  "amount": 500.00,
  "customer_id": "123",
  "shopkeeper_id": "1",
  "transcript": "Customer purchased items worth 500 rupees"
}
```

**Response:**
```json
{
  "id": 1,
  "status": "pending",
  "blockchain_hash": "0x..."
}
```

#### Upload Audio (Transcription)
**Request:**
```json
{
  "audio": "base64_encoded_audio_string",
  "mimeType": "audio/m4a",
  "filename": "recording_1234567890.m4a"
}
```

**Response:**
```json
{
  "transcript": "Customer purchased items worth 500 rupees",
  "confidence": 0.95,
  "language": "hi-IN"
}
```

#### Credit Score
**Response:**
```json
{
  "score": 725,
  "blockchain_verified": true,
  "factors": {
    "transaction_history": 85,
    "credit_repayment": 90,
    "blockchain_verification": 95,
    "cooperative_participation": 75,
    "payment_timeliness": 88,
    "transaction_volume": 82
  },
  "explanation": "Your score is based on...",
  "last_updated": "2024-01-15T10:30:00Z",
  "previous_score": 710,
  "score_trend": [
    { "month": "Jan", "score": 680 },
    { "month": "Feb", "score": 695 }
  ]
}
```

### 5. Error Handling

The app includes error handling in:
- `src/services/api.js` - Response interceptors
- Individual API methods - Try-catch blocks
- Screens - Error alerts and fallback to offline storage

### 6. Testing Backend Integration

1. **Start Backend:**
   ```bash
   cd backend
   python app.py  # Or however you start Flask
   ```

2. **Update API_BASE_URL** in `src/services/api.js`

3. **Uncomment real API calls** in `src/services/api.js`

4. **Comment out mock calls**

5. **Test each feature:**
   - Voice recording → Transcription
   - Transaction creation
   - Credit score display
   - Inventory management
   - Cooperative join/leave

6. **Test offline mode:**
   - Turn off WiFi/data
   - Create transaction/product
   - Verify saves locally
   - Turn on WiFi/data
   - Verify sync happens automatically

### 7. CORS Configuration

Ensure your Flask backend has CORS enabled:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

### 8. Authentication (If Required)

If your backend requires authentication:

1. Update request interceptor in `src/services/api.js`:
   ```javascript
   api.interceptors.request.use(async (config) => {
     const token = await AsyncStorage.getItem('auth_token');
     if (token) {
       config.headers.Authorization = `Bearer ${token}`;
     }
     return config;
   });
   ```

2. Add login screen to handle authentication
3. Store auth token in AsyncStorage
4. Handle 401 errors and redirect to login

## Troubleshooting

**Issue: "Network request failed"**
- Verify backend is running
- Check API_BASE_URL is correct
- Ensure backend accepts connections from your network (use `0.0.0.0` not `localhost`)
- Check firewall settings

**Issue: "CORS error"**
- Enable CORS in Flask backend
- Add mobile app origin to allowed origins

**Issue: "401 Unauthorized"**
- Check if authentication is required
- Verify auth token is being sent
- Check token expiration

**Issue: "404 Not Found"**
- Verify endpoint URLs match backend routes
- Check API versioning (e.g., `/api/v1/` vs `/api/`)



