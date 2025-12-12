# ML Credit Scoring Setup Instructions

## Model Training

To generate the trained model file (`model.pkl`), run the training script:

```bash
# Activate virtual environment first
cd backend
python ml/train_model.py
```

This will:
1. Load training data from `ml/data/training_data.csv`
2. Train a RandomForestRegressor model
3. Save the model to `ml/model.pkl`
4. Generate feature importance plot to `ml/feature_importance.png`

**Note:** The ML credit scoring system will work even without `model.pkl` - it will use a weighted baseline scoring method as a fallback.

## Dependencies

Make sure all dependencies are installed:

```bash
pip install -r requirements.txt
```

Required ML dependencies (already added to requirements.txt):
- scikit-learn>=1.3.0
- joblib>=1.3.0
- matplotlib>=3.7.0
- numpy>=1.24.0

## Testing the ML API

Once the server is running, you can test the endpoints:

1. **GET endpoint (fetch from database):**
   ```bash
   GET http://localhost:8000/ml/predict-credit-score/{shopkeeper_id}
   ```

2. **POST endpoint (manual input):**
   ```bash
   POST http://localhost:8000/ml/predict-credit-score
   Content-Type: application/json
   
   {
     "total_sales": 100000,
     "credit_given": 5000,
     "credit_repaid": 4500,
     "tx_frequency": 50,
     "product_count": 25,
     "cooperative_member": 1,
     "days_active": 90
   }
   ```

3. **Health check:**
   ```bash
   GET http://localhost:8000/ml/health
   ```

## Expected Behavior

- Credit scores will be in the range 300-900
- GET endpoint fetches shopkeeper data from MongoDB
- POST endpoint accepts manual input
- Health endpoint shows model, database, and blockchain status
- System handles missing shopkeepers gracefully (404 error)
- System handles missing model file gracefully (uses weighted baseline)

