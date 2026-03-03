"""
Feature Engineering for Phase 2 ML Pipeline.
Creates time-series features for sales forecasting.
"""

import logging
import pandas as pd
import numpy as np
from ml.config import LOG_FORMAT, LOG_LEVEL, FEATURE_COLUMNS

logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Handles feature engineering for time-series forecasting.
    """
    
    def __init__(self, lag_features=None, rolling_windows=None):
        """
        Initialize feature engineer.
        
        Args:
            lag_features: List of lag periods to create
            rolling_windows: List of rolling window sizes for mean
        """
        self.lag_features = lag_features or [1, 7]
        self.rolling_windows = rolling_windows or [7, 30]
    
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create all features for the model.
        
        Args:
            df: DataFrame with 'full_date' and 'total_sales' columns
            
        Returns:
            DataFrame: DataFrame with all engineered features
        """
        logger.info("Creating features for forecasting model...")
        
        # Work on a copy to avoid modifying original
        features_df = df.copy()
        
        # Sort by date to ensure proper ordering
        features_df = features_df.sort_values('full_date').reset_index(drop=True)
        
        # Create lag features (shift BEFORE rolling to prevent data leakage)
        features_df = self._create_lag_features(features_df)
        
        # Create rolling statistics
        features_df = self._create_rolling_features(features_df)
        
        # Create date-based features
        features_df = self._create_date_features(features_df)
        
        # Drop rows with NaN values (from lag/rolling)
        initial_rows = len(features_df)
        features_df = features_df.dropna().reset_index(drop=True)
        dropped_rows = initial_rows - len(features_df)
        
        logger.info(f"Created {len(FEATURE_COLUMNS)} features, dropped {dropped_rows} rows with NaN")
        
        return features_df
    
    def _create_lag_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create lag features for target variable.
        
        IMPORTANT: Shift is applied BEFORE rolling to prevent data leakage.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame: DataFrame with lag features
        """
        logger.info(f"Creating lag features: {self.lag_features}")
        
        for lag in self.lag_features:
            col_name = f"lag_{lag}"
            df[col_name] = df['total_sales'].shift(lag)
            logger.debug(f"Created {col_name}")
        
        return df
    
    def _create_rolling_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create rolling window statistics.
        
        Args:
            df: Input DataFrame (should already have lag features applied)
            
        Returns:
            DataFrame: DataFrame with rolling features
        """
        logger.info(f"Creating rolling features: {self.rolling_windows}")
        
        for window in self.rolling_windows:
            col_name = f"rolling_{window}_mean"
            # Use shifted sales for rolling to prevent data leakage
            # Rolling mean of sales up to previous day
            df[col_name] = df['total_sales'].shift(1).rolling(window=window).mean()
            logger.debug(f"Created {col_name}")
        
        return df
    
    def _create_date_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create date-based features.
        
        Args:
            df: Input DataFrame with 'full_date' column
            
        Returns:
            DataFrame: DataFrame with date features
        """
        logger.info("Creating date-based features")
        
        # Extract month (1-12)
        df['month'] = df['full_date'].dt.month
        
        # Extract day of week (0=Monday, 6=Sunday)
        df['day_of_week'] = df['full_date'].dt.dayofweek
        
        # Create weekend flag (Saturday=5, Sunday=6)
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        return df
    
    def get_feature_matrix(self, df: pd.DataFrame) -> tuple:
        """
        Extract feature matrix (X) and target vector (y).
        
        Args:
            df: DataFrame with all features
            
        Returns:
            tuple: (X, y) where X is feature matrix and y is target
        """
        feature_cols = FEATURE_COLUMNS.copy()
        
        # Verify all feature columns exist
        missing_cols = [col for col in feature_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing feature columns: {missing_cols}")
        
        X = df[feature_cols].copy()
        y = df['total_sales'].copy()
        
        logger.info(f"Feature matrix shape: {X.shape}, Target shape: {y.shape}")
        
        return X, y
