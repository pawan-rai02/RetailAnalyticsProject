"""
Configuration settings for Phase 2 ML Pipeline.
Uses environment variables for database credentials.
"""

import os
from pathlib import Path
from datetime import datetime

# Project root directory (phase-2-ml)
PROJECT_ROOT = Path(__file__).parent.parent

# Paths
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "ml" / "models"
LOGS_DIR = PROJECT_ROOT / "ml" / "logs"

# Ensure directories exist
MODELS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Database Configuration (from environment variables)
DB_CONFIG = {
    "host": os.getenv("ML_DB_HOST", "localhost"),
    "port": int(os.getenv("ML_DB_PORT", "3306")),
    "database": os.getenv("ML_DB_NAME", "retail_db"),
    "user": os.getenv("ML_DB_USER", "root"),
    "password": os.getenv("ML_DB_PASSWORD", "root")
}

# SQLAlchemy connection string
def get_connection_string():
    """Build SQLAlchemy connection string from config."""
    return (
        f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )

# Model Configuration
MODEL_CONFIG = {
    "test_size": 0.2,  # 80-20 chronological split
    "random_state": 42,
    "lag_features": [1, 7],
    "rolling_windows": [7, 30]
}

# Feature columns
FEATURE_COLUMNS = [
    "lag_1",
    "lag_7",
    "rolling_7_mean",
    "rolling_30_mean",
    "month",
    "day_of_week",
    "is_weekend"
]

# Logging Configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"
LOG_FILE = LOGS_DIR / f"ml_pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Model file names
MODEL_FILENAME = "global_best_model.pkl"
MODEL_PATH = MODELS_DIR / MODEL_FILENAME
