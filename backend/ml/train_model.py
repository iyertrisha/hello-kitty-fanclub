"""
Training pipeline for Credit Score Model.

This script loads training data, performs feature engineering, trains a
RandomForestRegressor model, evaluates it, and saves the model and feature
importance plot.
"""

import logging
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_data(data_path: Path) -> pd.DataFrame:
    """
    Load training data from CSV.
    
    Args:
        data_path: Path to training_data.csv
        
    Returns:
        DataFrame with training data
    """
    if not data_path.exists():
        raise FileNotFoundError(f"Training data not found at {data_path}")
    
    df = pd.read_csv(data_path)
    logger.info(f"✅ Loaded {len(df)} rows from {data_path}")
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform feature engineering on raw data.
    
    Args:
        df: Raw training DataFrame
        
    Returns:
        DataFrame with engineered features
    """
    df = df.copy()
    
    # Credit ratio: repayment efficiency
    df["credit_ratio"] = np.where(
        df["credit_given"] > 0,
        df["credit_repaid"] / df["credit_given"],
        0.0
    )
    
    # Sales per day: business activity rate
    df["sales_per_day"] = np.where(
        df["days_active"] > 0,
        df["total_sales"] / df["days_active"],
        0.0
    )
    
    # Transaction frequency per day
    df["tx_per_day"] = np.where(
        df["days_active"] > 0,
        df["tx_frequency"] / df["days_active"],
        0.0
    )
    
    # Credit utilization: credit given relative to sales
    df["credit_utilization"] = np.where(
        df["total_sales"] > 0,
        df["credit_given"] / df["total_sales"],
        0.0
    )
    
    # Product density: products per day active
    df["product_density"] = np.where(
        df["days_active"] > 0,
        df["product_count"] / df["days_active"],
        0.0
    )
    
    logger.info("✅ Feature engineering complete")
    return df


def prepare_features_and_target(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """
    Prepare feature matrix and target vector.
    
    Args:
        df: DataFrame with engineered features
        
    Returns:
        Tuple of (features, target)
    """
    feature_columns = [
        "total_sales",
        "credit_given",
        "credit_repaid",
        "tx_frequency",
        "product_count",
        "cooperative_member",
        "days_active",
        "credit_ratio",
        "sales_per_day",
        "tx_per_day",
    ]
    
    X = df[feature_columns].values
    y = df["credit_score"].values
    
    logger.info(f"✅ Prepared features: {X.shape}, target: {y.shape}")
    return X, y


def train_model(X_train: np.ndarray, y_train: np.ndarray) -> RandomForestRegressor:
    """
    Train RandomForestRegressor model.
    
    Args:
        X_train: Training features
        y_train: Training targets
        
    Returns:
        Trained model
    """
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    
    model.fit(X_train, y_train)
    logger.info("✅ Model training complete")
    return model


def evaluate_model(
    model: RandomForestRegressor,
    X_test: np.ndarray,
    y_test: np.ndarray
) -> dict[str, float]:
    """
    Evaluate model performance.
    
    Args:
        model: Trained model
        X_test: Test features
        y_test: Test targets
        
    Returns:
        Dictionary of evaluation metrics
    """
    y_pred = model.predict(X_test)
    
    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    metrics = {
        "mse": mse,
        "mae": mae,
        "r2": r2,
        "rmse": np.sqrt(mse),
    }
    
    logger.info(f"✅ Model Evaluation:")
    logger.info(f"   MSE: {mse:.2f}")
    logger.info(f"   MAE: {mae:.2f}")
    logger.info(f"   RMSE: {np.sqrt(mse):.2f}")
    logger.info(f"   R²: {r2:.4f}")
    
    return metrics


def plot_feature_importance(
    model: RandomForestRegressor,
    feature_names: list[str],
    output_path: Path
) -> None:
    """
    Generate and save feature importance plot.
    
    Args:
        model: Trained model
        feature_names: List of feature names
        output_path: Path to save plot
    """
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    plt.figure(figsize=(10, 6))
    plt.title("Feature Importance - Credit Score Model")
    plt.bar(range(len(importances)), importances[indices])
    plt.xticks(range(len(importances)), [feature_names[i] for i in indices], rotation=45, ha="right")
    plt.ylabel("Importance")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    
    logger.info(f"✅ Feature importance plot saved to {output_path}")


def main() -> None:
    """Main training pipeline."""
    # Set up paths
    script_dir = Path(__file__).parent
    data_path = script_dir / "data" / "training_data.csv"
    model_path = script_dir / "model.pkl"
    plot_path = script_dir / "feature_importance.png"
    
    logger.info("🚀 Starting credit score model training pipeline")
    
    # Load data
    df = load_data(data_path)
    
    # Engineer features
    df = engineer_features(df)
    
    # Prepare features and target
    X, y = prepare_features_and_target(df)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    logger.info(f"✅ Train/test split: {len(X_train)}/{len(X_test)}")
    
    # Train model
    model = train_model(X_train, y_train)
    
    # Evaluate model
    metrics = evaluate_model(model, X_test, y_test)
    
    # Save model
    joblib.dump(model, model_path)
    logger.info(f"✅ Model saved to {model_path}")
    
    # Generate feature importance plot
    feature_names = [
        "total_sales",
        "credit_given",
        "credit_repaid",
        "tx_frequency",
        "product_count",
        "cooperative_member",
        "days_active",
        "credit_ratio",
        "sales_per_day",
        "tx_per_day",
    ]
    plot_feature_importance(model, feature_names, plot_path)
    
    logger.info("🎉 Training pipeline complete!")


if __name__ == "__main__":
    main()

