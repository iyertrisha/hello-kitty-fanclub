# Debugging Cooperatives Not Showing in Frontend

## Issues Fixed

1. **Query Issue**: Simplified the MongoEngine query to reliably get all cooperatives where `is_active != False`
2. **Error Handling**: Added better error handling for member processing
3. **Logging**: Added logging to track how many cooperatives are being returned

## How to Debug

### Step 1: Check Database
```powershell
cd helloKittyFanclub\backend
.\venv\Scripts\Activate.ps1
python check_cooperatives.py
```

### Step 2: Test API Endpoint
```powershell
# Make sure Flask server is running first
python test_cooperatives_api.py
```

Or manually:
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/admin/cooperatives" -Method GET | ConvertTo-Json -Depth 5
```

### Step 3: Check Frontend Console
1. Open browser DevTools (F12)
2. Go to Network tab
3. Navigate to Cooperatives page
4. Check for:
   - API call to `/api/admin/cooperatives`
   - Response status (should be 200)
   - Response data structure
   - Console errors

### Step 4: Verify Data Format
The backend should return:
```json
{
  "cooperatives": [
    {
      "id": "...",
      "name": "...",
      "description": "...",
      "revenue_split_percent": 10.0,
      "revenue_split": 10.0,
      "members": [...],
      "member_count": 3,
      "is_active": true
    }
  ]
}
```

The frontend expects:
- `data.cooperatives` (array)
- Each cooperative should have: `id`, `name`, `revenue_split`, `members`

## Common Issues

1. **No cooperatives in database**: Run `python database/seeders/seed_data.py`
2. **is_active=False**: Run `python database/seeders/fix_cooperatives.py`
3. **CORS error**: Check `CORS_ORIGINS` in `.env` includes frontend URL
4. **API endpoint not found**: Check Flask server is running and routes are registered
5. **Empty response**: Check backend logs for errors

## Next Steps

If cooperatives still don't show:
1. Check browser console for JavaScript errors
2. Check Network tab for failed API calls
3. Verify Flask server logs for errors
4. Test API endpoint directly with curl/Postman

