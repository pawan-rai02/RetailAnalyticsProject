"""
Evaluation Task for Phase 2 ML Pipeline.
Handles evaluation of trained models.
"""

import logging
import joblib
from pathlib import Path
from ml.config import LOG_FORMAT, LOG_LEVEL, MODEL_PATH, get_connection_string
from ml.data_loader import DataLoader
from ml.feature_engineering import FeatureEngineer
from ml.modeling.linear_model import LinearRegressionModel
from ml.modeling.random_forest_model import RandomForestModel

logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)


def evaluate_global_model(model_path: str = None):
    """
    Evaluate a trained global sales forecasting model.
    
    Args:
        model_path: Path to the trained model file. Defaults to best model path.
        
    Returns:
        dict: Evaluation metrics
    """
    logger.info("=" * 60)
    logger.info("PHASE 2: GLOBAL SALES FORECASTING - MODEL EVALUATION")
    logger.info("=" * 60)
    
    model_path = Path(model_path) if model_path else MODEL_PATH
    
    if not model_path.exists():
        logger.error(f"Model file not found: {model_path}")
        logger.error("Please run 'python main.py train global' first.")
        return None
    
    # Load data from warehouse
    logger.info("Step 1: Loading data from MySQL warehouse...")
    with DataLoader() as loader:
        df = loader.load_global_daily_sales()
    
    if len(df) == 0:
        logger.error("No data loaded from warehouse. Exiting.")
        return None
    
    # Feature engineering
    logger.info("Step 2: Creating features...")
    engineer = FeatureEngineer()
    features_df = engineer.create_features(df)
    
    if len(features_df) == 0:
        logger.error("No data remaining after feature engineering. Exiting.")
        return None
    
    # Get feature matrix and target
    X, y = engineer.get_feature_matrix(features_df)
    
    # Load trained model
    logger.info("Step 3: Loading trained model...")
    model = joblib.load(model_path)
    logger.info(f"Model loaded from: {model_path}")
    
    # Evaluate on full dataset
    logger.info("Step 4: Evaluating model...")
    predictions = model.predict(X)
    
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    import numpy as np
    
    mae = mean_absolute_error(y, predictions)
    rmse = np.sqrt(mean_squared_error(y, predictions))
    r2 = r2_score(y, predictions)
    
    # Print evaluation results
    print("\n")
    print("=" * 60)
    print("MODEL EVALUATION RESULTS")
    print("=" * 60)
    print(f"Model: {model_path.name}")
    print(f"Total samples evaluated: {len(X)}")
    print("-" * 60)
    print(f"{'MAE':>15} {mae:>12.2f}")
    print(f"{'RMSE':>15} {rmse:>12.2f}")
    print(f"{'R²':>15} {r2:>12.4f}")
    print("=" * 60)
    
    metrics = {
        'mae': mae,
        'rmse': rmse,
        'r2': r2,
        'model_path': str(model_path),
        'samples_evaluated': len(X)
    }
    
    logger.info("Evaluation completed successfully!")
    
    return metrics


if __name__ == "__main__":
    evaluate_global_model()
