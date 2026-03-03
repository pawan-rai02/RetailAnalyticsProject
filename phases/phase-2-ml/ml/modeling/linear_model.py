"""
Linear Regression Model for Sales Forecasting.
Baseline model for global daily sales prediction.
"""

import logging
import joblib
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
from ml.config import LOG_FORMAT, LOG_LEVEL

logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class LinearRegressionModel:
    """
    Linear Regression wrapper for sales forecasting.
    """
    
    def __init__(self):
        """Initialize the Linear Regression model."""
        self.model = LinearRegression()
        self.is_trained = False
        self.feature_names = None
    
    def train(self, X_train, y_train):
        """
        Train the Linear Regression model.
        
        Args:
            X_train: Training features
            y_train: Training target
        """
        logger.info("Training Linear Regression model...")
        
        self.model.fit(X_train, y_train)
        self.is_trained = True
        self.feature_names = list(X_train.columns) if hasattr(X_train, 'columns') else None
        
        logger.info("Linear Regression model training completed")
    
    def predict(self, X):
        """
        Make predictions.
        
        Args:
            X: Features to predict on
            
        Returns:
            Predictions array
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before prediction")
        
        return self.model.predict(X)
    
    def evaluate(self, X_test, y_test) -> dict:
        """
        Evaluate model performance.
        
        Args:
            X_test: Test features
            y_test: Test target
            
        Returns:
            dict: Evaluation metrics (MAE, RMSE, R2)
        """
        logger.info("Evaluating Linear Regression model...")
        
        predictions = self.predict(X_test)
        
        mae = mean_absolute_error(y_test, predictions)
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        r2 = r2_score(y_test, predictions)
        
        metrics = {
            'model_name': 'LinearRegression',
            'mae': mae,
            'rmse': rmse,
            'r2': r2
        }
        
        logger.info(f"Linear Regression - MAE: {mae:.2f}, RMSE: {rmse:.2f}, R2: {r2:.4f}")
        
        return metrics
    
    def save(self, filepath: Path):
        """
        Save model to disk.
        
        Args:
            filepath: Path to save model
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        joblib.dump(self.model, filepath)
        logger.info(f"Linear Regression model saved to {filepath}")
    
    def load(self, filepath: Path):
        """
        Load model from disk.
        
        Args:
            filepath: Path to load model from
        """
        self.model = joblib.load(filepath)
        self.is_trained = True
        logger.info(f"Linear Regression model loaded from {filepath}")
    
    def get_feature_importance(self) -> dict:
        """
        Get feature coefficients.
        
        Returns:
            dict: Feature names mapped to coefficients
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained first")
        
        if self.feature_names:
            return dict(zip(self.feature_names, self.model.coef_))
        else:
            return dict(enumerate(self.model.coef_))
