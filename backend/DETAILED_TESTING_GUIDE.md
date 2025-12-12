# Detailed Testing Guide

Comprehensive step-by-step guide for testing the backend API.

## Prerequisites

- Python 3.9+
- MongoDB installed and running
- Virtual environment activated
- `.env` file configured

## Step-by-Step Testing

### 1. Environment Setup

```powershell
# Navigate to project
cd D:\whackiest\helloKittyFanclub

# Activate venv
.\venv\Scripts\Activate.ps1

# Navigate to backend
cd backend
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure Environment

Ensure `.env` file exists with:
- `MONGODB_URI`
- `MONGODB_DB_NAME`
- `SECRET_KEY`
- `CORS_ORIGINS`

### 4. Start MongoDB

```powershell
Get-Service MongoDB
Start-Service MongoDB  # If not running
```

### 5. Seed Database

```powershell
python database\seeders\seed_data.py
```

Expected output: Creates 8 shopkeepers, 25 customers, 96 products, 150 transactions, 3 cooperatives

### 6. Start Flask Server

```powershell
python run.py
```

Keep this terminal open. Server runs on `http://localhost:5000`

### 7. Run Automated Tests

Open a **new terminal** and run:

```powershell
cd D:\whackiest\helloKittyFanclub\backend
.\venv\Scripts\Activate.ps1
python test_all_endpoints.py
```

This will test all endpoints and generate a report in `backend_test_report.json`.

## Testing Individual Endpoints

See `MANUAL_STEPS.md` for detailed endpoint testing examples.

## Troubleshooting

- **Import errors**: Make sure venv is activated
- **MongoDB connection errors**: Check MongoDB is running
- **Port already in use**: Change `FLASK_PORT` in `.env`
- **Module not found**: Run `pip install -r requirements.txt`

For more details, see `MANUAL_STEPS.md`.

