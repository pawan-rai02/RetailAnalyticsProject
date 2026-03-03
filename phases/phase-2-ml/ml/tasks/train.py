"""
Training Task for Phase 2 ML Pipeline.
Handles training of global sales forecasting models.
"""

import logging
import pandas as pd
from datetime import datetime
from ml.config import (
    LOG_FORMAT, LOG_LEVEL, MODEL_CONFIG, MODEL_PATH,
    get_connection_string
)
from ml.data_loader import DataLoader
from ml.feature_engineering import FeatureEngineer
from ml.modeling.linear_model import LinearRegressionModel
from ml.modeling.random_forest_model import RandomForestModel

logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)


def train_global_model():
    """
    Train global sales forecasting models and save the best one.
    
    Uses chronological 80-20 split (no random shuffle to prevent data leakage).
    Trains both Linear Regression and Random Forest, selects best by RMSE.
    
    Returns:
        dict: Training results including best model metrics
    """
    logger.info("=" * 60)
    logger.info("PHASE 2: GLOBAL SALES FORECASTING - MODEL TRAINING")
    logger.info("=" * 60)
    
    # Load data from warehouse
    logger.info("Step 1: Loading data from MySQL warehouse...")
    with DataLoader() as loader:
        df = loader.load_global_daily_sales()
    
    if len(df) == 0:
        logger.error("No data loaded from warehouse. Exiting.")
        return None
    
    # Feature engineering
    logger.info("Step 2: Creating features...")
    engineer = FeatureEngineer(
        lag_features=MODEL_CONFIG['lag_features'],
        rolling_windows=MODEL_CONFIG['rolling_windows']
    )
    features_df = engineer.create_features(df)
    
    if len(features_df) == 0:
        logger.error("No data remaining after feature engineering. Exiting.")
        return None
    
    # Get feature matrix and target
    X, y = engineer.get_feature_matrix(features_df)
    
    # Chronological train-test split (80-20, no shuffle)
    logger.info("Step 3: Performing chronological train-test split (80-20)...")
    split_idx = int(len(X) * (1 - MODEL_CONFIG['test_size']))
    
    X_train = X.iloc[:split_idx]
    X_test = X.iloc[split_idx:]
    y_train = y.iloc[:split_idx]
    y_test = y.iloc[split_idx:]
    
    logger.info(f"Training samples: {len(X_train)}, Test samples: {len(X_test)}")
    
    # Train Linear Regression (baseline)
    logger.info("Step 4: Training Linear Regression (baseline)...")
    lr_model = LinearRegressionModel()
    lr_model.train(X_train, y_train)
    lr_metrics = lr_model.evaluate(X_test, y_test)
    
    # Train Random Forest
    logger.info("Step 5: Training Random Forest...")
    rf_model = RandomForestModel(
        n_estimators=100,
        random_state=MODEL_CONFIG['random_state']
    )
    rf_model.train(X_train, y_train)
    rf_metrics = rf_model.evaluate(X_test, y_test)
    
    # Select best model based on lowest RMSE
    logger.info("Step 6: Selecting best model (lowest RMSE)...")
    
    if lr_metrics['rmse'] <= rf_metrics['rmse']:
        best_model = lr_model
        best_metrics = lr_metrics
        logger.info(f"Linear Regression selected (RMSE: {lr_metrics['rmse']:.2f})")
    else:
        best_model = rf_model
        best_metrics = rf_metrics
        logger.info(f"Random Forest selected (RMSE: {rf_metrics['rmse']:.2f})")
    
    # Save best model
    logger.info("Step 7: Saving best model...")
    best_model.save(MODEL_PATH)
    
    # Print evaluation comparison table
    logger.info("=" * 60)
    logger.info("MODEL EVALUATION COMPARISON")
    logger.info("=" * 60)
    
    print("\n")
    print("=" * 60)
    print("MODEL EVALUATION COMPARISON")
    print("=" * 60)
    print(f"{'Model':<25} {'MAE':>12} {'RMSE':>12} {'R²':>12}")
    print("-" * 60)
    print(f"{'Linear Regression':<25} {lr_metrics['mae']:>12.2f} {lr_metrics['rmse']:>12.2f} {lr_metrics['r2']:>12.4f}")
    print(f"{'Random Forest':<25} {rf_metrics['mae']:>12.2f} {rf_metrics['rmse']:>12.2f} {rf_metrics['r2']:>12.4f}")
    print("-" * 60)
    print(f"{'BEST MODEL:':<25} {best_metrics['mae']:>12.2f} {best_metrics['rmse']:>12.2f} {best_metrics['r2']:>12.4f}")
    print("=" * 60)
    print(f"\nBest model saved to: {MODEL_PATH}")
    print("=" * 60)
    
    results = {
        'linear_regression': lr_metrics,
        'random_forest': rf_metrics,
        'best_model': best_metrics,
        'best_model_name': best_metrics['model_name'],
        'model_path': str(MODEL_PATH),
        'train_samples': len(X_train),
        'test_samples': len(X_test),
        'timestamp': datetime.now().isoformat()
    }
    
    logger.info("Training completed successfully!")
    
    return results


if __name__ == "__main__":
    train_global_model()
