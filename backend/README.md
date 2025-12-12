# Backend API - Kirana Store Management System

Flask REST API backend for the blockchain-based Kirana Store Management System.

## Setup

### Prerequisites

- Python 3.9+
- MongoDB (local or remote)
- Node.js (for blockchain module)

### Installation

1. **Install Python dependencies:**

```bash
cd helloKittyFanclub/backend
pip install -r requirements.txt
```

2. **Configure environment variables:**

Create a `.env` file in the `backend` directory (or copy from `.env.template`):

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_PORT=5000
SECRET_KEY=your-secret-key-here

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/kirana_db
MONGODB_DB_NAME=kirana_db

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:8081

# Blockchain Configuration (from blockchain/.env)
POLYGON_AMOY_RPC_URL=https://rpc-amoy.polygon.technology
CONTRACT_ADDRESS=your_contract_address
PRIVATE_KEY=your_private_key
ADMIN_ADDRESS=your_admin_address
```

3. **Start MongoDB:**

Make sure MongoDB is running locally or update `MONGODB_URI` to point to your MongoDB instance.

4. **Seed the database (optional):**

```bash
python database/seeders/seed_data.py
```

5. **Run the Flask server:**

```bash
python run.py
```

The API will be available at `http://localhost:5000`

## Project Structure

```
backend/
├── api/                    # Flask API application
│   ├── __init__.py        # App factory
│   ├── routes/            # API route handlers
│   │   ├── transactions.py
│   │   ├── shopkeeper.py
│   │   ├── customer.py
│   │   ├── cooperative.py
│   │   ├── blockchain.py
│   │   └── admin.py
│   └── middleware/        # Middleware modules
│       ├── auth.py
│       ├── validation.py
│       └── error_handler.py
├── database/
│   ├── models.py          # MongoEngine models
│   └── seeders/
│       └── seed_data.py   # Database seeding script
├── services/              # Business logic services
│   ├── transaction/
│   ├── shopkeeper/
│   ├── customer/
│   ├── cooperative/
│   ├── order-routing/
│   ├── store-clustering/
│   └── admin/
├── blockchain/            # Blockchain integration (Trisha's work)
│   └── utils/
│       └── contract_service.py
├── config.py              # Configuration
├── requirements.txt       # Python dependencies
├── run.py                # Application runner
└── README.md             # This file
```

## Dependencies

- **Flask** - Web framework
- **MongoEngine** - MongoDB ODM
- **Flask-CORS** - CORS handling
- **python-dotenv** - Environment variables
- **pandas** - Data processing
- **requests** - HTTP requests (for ML service)
- **web3** - Blockchain interaction (from blockchain module)

## Integration Points

- **Blockchain**: Uses `blockchain/utils/contract_service.py` for blockchain operations
- **ML Service**: Calls Mohit's credit score endpoint at `POST /api/ml/creditScore`
- **Google Speech API**: Integrates with Trisha's `google_speech.py` for audio transcription
- **WhatsApp**: Mohit updates transaction status via `PUT /api/transactions/<id>/status`

## Testing

### Manual Testing

Use tools like Postman or curl to test endpoints:

```bash
# Get all transactions
curl http://localhost:5000/api/transactions

# Create a transaction
curl -X POST http://localhost:5000/api/transactions \
  -H "Content-Type: application/json" \
  -d '{"type":"sale","amount":100,"shopkeeper_id":"...","customer_id":"..."}'
```

### Automated Testing

Run the comprehensive test suite:

```bash
# Make sure server is running first
python run.py

# In another terminal
python test_all_endpoints.py
```

See `TESTING_GUIDE.md` and `MANUAL_STEPS.md` for detailed testing instructions.

## API Endpoints

### Transactions
- `POST /api/transactions` - Create transaction
- `GET /api/transactions` - List transactions (with filters)
- `GET /api/transactions/<id>` - Get transaction by ID
- `PUT /api/transactions/<id>/status` - Update transaction status
- `POST /api/transactions/transcribe` - Upload audio for transcription

### Shopkeepers
- `POST /api/shopkeeper/register` - Register new shopkeeper
- `GET /api/shopkeeper/<id>` - Get shopkeeper profile
- `PUT /api/shopkeeper/<id>` - Update shopkeeper
- `GET /api/shopkeeper/<id>/credit-score` - Get credit score
- `GET /api/shopkeeper/<id>/inventory` - Get inventory
- `PUT /api/shopkeeper/<id>/inventory/<product_id>` - Update inventory item

### Customers
- `POST /api/customer` - Create customer
- `GET /api/customer/<id>` - Get customer profile
- `GET /api/customer/<id>/orders` - Get customer orders
- `GET /api/customer/<id>/credits` - Get customer credits

### Cooperatives
- `GET /api/cooperative` - List cooperatives
- `GET /api/cooperative/<id>` - Get cooperative details
- `POST /api/cooperative/<id>/join` - Join cooperative
- `GET /api/cooperative/<id>/members` - Get members
- `POST /api/cooperative/<id>/bulk-order` - Create bulk order
- `GET /api/cooperative/<id>/orders` - Get bulk orders

### Admin
- `GET /api/admin/overview` - Dashboard overview
- `GET /api/admin/stores` - List all stores
- `GET /api/admin/cooperatives` - List all cooperatives
- `POST /api/admin/cooperatives` - Create cooperative
- `GET /api/admin/analytics` - Analytics data
- `GET /api/admin/blockchain-logs` - Blockchain logs

### Blockchain
- `POST /api/blockchain/record-transaction` - Record transaction on blockchain
- `GET /api/blockchain/transaction/<id>` - Get blockchain transaction
- `POST /api/blockchain/register-shopkeeper` - Register shopkeeper on blockchain
- `GET /api/blockchain/credit-score/<shopkeeper_id>` - Get blockchain credit score

## Error Handling

The API uses standard HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error
- `503` - Service Unavailable (blockchain service not available)

Error responses follow this format:
```json
{
  "error": "Error message",
  "status_code": 400
}
```

## Development

### Running in Development Mode

```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
python run.py
```

### Running Tests

```bash
# Unit tests (when available)
pytest

# Integration tests
python test_all_endpoints.py
```

## License

MIT

