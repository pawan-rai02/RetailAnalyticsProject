"""
Prediction Task for Phase 2 ML Pipeline.
Handles generating sales predictions using trained models.
"""

import logging
import joblib
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from ml.config import LOG_FORMAT, LOG_LEVEL, MODEL_PATH, get_connection_string
from ml.data_loader import DataLoader
from ml.feature_engineering import FeatureEngineer

logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)


def predict_global_sales(model_path: str = None, forecast_days: int = 7):
    """
    Generate sales forecasts for future days.
    
    Uses recursive prediction: each prediction is used to compute
    features for the next day's prediction.
    
    Args:
        model_path: Path to the trained model file. Defaults to best model path.
        forecast_days: Number of days to forecast ahead.
        
    Returns:
        DataFrame: Predictions with dates
    """
    logger.info("=" * 60)
    logger.info("PHASE 2: GLOBAL SALES FORECASTING - PREDICTION")
    logger.info("=" * 60)
    
    model_path = Path(model_path) if model_path else MODEL_PATH
    
    if not model_path.exists():
        logger.error(f"Model file not found: {model_path}")
        logger.error("Please run 'python main.py train global' first.")
        return None
    
    # Load data from warehouse
    logger.info("Step 1: Loading historical data from MySQL warehouse...")
    with DataLoader() as loader:
        df = loader.load_global_daily_sales()
    
    if len(df) == 0:
        logger.error("No data loaded from warehouse. Exiting.")
        return None
    
    # Load trained model
    logger.info("Step 2: Loading trained model...")
    model = joblib.load(model_path)
    logger.info(f"Model loaded from: {model_path}")
    
    # Feature engineering setup
    logger.info("Step 3: Preparing features for prediction...")
    engineer = FeatureEngineer()
    
    # Create features from historical data
    features_df = engineer.create_features(df)
    
    if len(features_df) == 0:
        logger.error("No data remaining after feature engineering. Exiting.")
        return None
    
    # Get the last row for recursive prediction
    last_date = df['full_date'].max()
    last_row = features_df.iloc[-1:].copy()
    
    # Recursive prediction for future days
    logger.info(f"Step 4: Generating predictions for next {forecast_days} days...")
    
    predictions = []
    current_features = last_row.copy()
    
    for i in range(forecast_days):
        # Prepare feature vector
        feature_cols = ['lag_1', 'lag_7', 'rolling_7_mean', 'rolling_30_mean', 
                        'month', 'day_of_week', 'is_weekend']
        X_pred = current_features[feature_cols]
        
        # Make prediction
        pred_value = model.predict(X_pred)[0]
        
        # Calculate next date
        next_date = last_date + timedelta(days=i+1)
        
        predictions.append({
            'full_date': next_date,
            'predicted_sales': pred_value
        })
        
        # Update features for next iteration (recursive)
        # Shift lag features
        current_features['lag_7'] = current_features['lag_1'].values[0]
        current_features['lag_1'] = pred_value
        
        # Update rolling means (simplified - using last known values)
        # In production, this would maintain a proper rolling window
        current_features['rolling_7_mean'] = current_features['rolling_7_mean'].values[0]
        current_features['rolling_30_mean'] = current_features['rolling_30_mean'].values[0]
        
        # Update date features
        current_features['month'] = next_date.month
        current_features['day_of_week'] = next_date.dayofweek
        current_features['is_weekend'] = 1 if next_date.dayofweek >= 5 else 0
    
    # Create predictions DataFrame
    predictions_df = pd.DataFrame(predictions)
    
    # Print predictions
    print("\n")
    print("=" * 60)
    print("SALES FORECAST PREDICTIONS")
    print("=" * 60)
    print(f"Model: {model_path.name}")
    print(f"Forecast Period: {forecast_days} days")
    print(f"Base Date: {last_date.strftime('%Y-%m-%d')}")
    print("-" * 60)
    print(f"{'Date':<15} {'Predicted Sales':>20}")
    print("-" * 60)
    
    for _, row in predictions_df.iterrows():
        date_str = row['full_date'].strftime('%Y-%m-%d')
        sales_str = f"${row['predicted_sales']:,.2f}"
        print(f"{date_str:<15} {sales_str:>20}")
    
    print("=" * 60)
    
    logger.info("Prediction completed successfully!")
    
    return predictions_df


if __name__ == "__main__":
    predict_global_sales()
