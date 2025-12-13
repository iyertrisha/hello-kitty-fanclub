# How to Run Backend Integration Tests

## Quick Start

### Option 1: Using Python (Unittest) - Recommended

From the `backend` directory:

```powershell
# Windows PowerShell
cd helloKittyFanclub\backend
python test_backend_integration.py
```

```bash
# Linux/Mac
cd helloKittyFanclub/backend
python test_backend_integration.py
```

### Option 2: Using pytest (if installed)

```powershell
# Windows PowerShell
cd helloKittyFanclub\backend
pytest test_backend_integration.py -v
```

```bash
# Linux/Mac
cd helloKittyFanclub/backend
pytest test_backend_integration.py -v
```

## Prerequisites

Make sure you have:

1. **Python dependencies installed:**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Environment variables set:**
   - Create a `.env` file in the `backend` directory
   - At minimum, set `MONGODB_URI` and `MONGODB_DB_NAME`

3. **MongoDB running:**
   - Local MongoDB on `localhost:27017`, OR
   - MongoDB Atlas connection string in `.env`

## What the Tests Check

The test suite validates:

✅ **Environment Variables**
- MongoDB URI exists
- Database name is set
- Blockchain config is accessible

✅ **MongoDB Connection**
- Connection string format is valid
- Can actually connect to MongoDB
- Can write and read data

✅ **Flask Application**
- App can be created
- Routes are registered
- Health endpoint works

✅ **Blockchain Integration**
- Service can be imported
- RPC URL consistency (catches the critical bug!)
- Configuration values exist

✅ **End-to-End Flow**
- Transaction creation via API
- MongoDB persistence
- Blockchain write status

✅ **Critical Issues**
- RPC URL mismatch detection
- Connection validation checks

## Expected Output

If all tests pass, you'll see:
```
✅ All tests passed!
```

If tests fail, you'll see:
```
❌ Some tests failed. Review output above.
```

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'flask'"

**Solution:** Install dependencies
```powershell
pip install -r requirements.txt
```

### Error: "MongoDB connection timeout"

**Solution:** 
1. Make sure MongoDB is running
2. Check your `MONGODB_URI` in `.env` file
3. If using MongoDB Atlas, verify your IP is whitelisted

### Error: "No module named 'pytest'"

**Solution:** 
- This is OK! The test file will automatically use `unittest` instead
- Or install pytest: `pip install pytest`

## Running Specific Test Classes

If you want to run only specific tests:

### With pytest:
```powershell
pytest test_backend_integration.py::TestMongoDBConnection -v
pytest test_backend_integration.py::TestBlockchainIntegration -v
```

### With unittest:
Edit the `test_classes` list in `run_tests()` function to include only what you need.

## Understanding Test Results

- ✅ **PASS** - Test passed
- ❌ **FAIL** - Test failed (check error message)
- ⚠️ **WARNING** - Non-critical issue detected

## Next Steps After Running Tests

1. **If all tests pass:** Your backend is correctly configured! ✅

2. **If tests fail:**
   - Check the error messages
   - Verify your `.env` file has correct values
   - Ensure MongoDB is accessible
   - Review `BACKEND_ARCHITECTURE_ANALYSIS.md` for known issues

3. **Fix any issues** found and re-run tests

---

**Note:** Some tests may fail if:
- MongoDB is not running
- Blockchain credentials are not configured (this is OK if you're not using blockchain yet)
- Environment variables are missing

The test suite is designed to fail loudly when something is wrong, so you know exactly what needs to be fixed!

