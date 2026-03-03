# Phase 2: ML Pipeline Architecture & Data Flow

This document details the technical architecture, component design, and data flow of the Phase 2 ML Pipeline for global daily sales forecasting.

---

## Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [Component Overview](#component-overview)
3. [Data Flow](#data-flow)
4. [Feature Engineering Design](#feature-engineering-design)
5. [Model Architecture](#model-architecture)
6. [Prediction Strategy](#prediction-strategy)
7. [Configuration Management](#configuration-management)
8. [Execution Flow](#execution-flow)

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PHASE 2 ML PIPELINE ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      DATA LAYER                                  │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │   │
│  │  │  MySQL DW    │  │  DataLoader  │  │  Pandas DF   │          │   │
│  │  │  sales_fact  │─▶│  (SQLAlchemy)│─▶│  (Daily Sales)│          │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                           │                                             │
│                           ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                   FEATURE ENGINEERING LAYER                      │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │   │
│  │  │  Lag Features│  │Rolling Stats │  │ Date Features│          │   │
│  │  │  (1, 7 days) │  │ (7, 30 days) │  │(month, dow)  │          │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                           │                                             │
│                           ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                       MODEL LAYER                                │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │   │
│  │  │   Linear     │  │  Random      │  │   Model      │          │   │
│  │  │  Regression  │  │   Forest     │  │  Selector    │          │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                           │                                             │
│                           ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    PREDICTION LAYER                              │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │   │
│  │  │  Recursive   │  │   Forecast   │  │   Results    │          │   │
│  │  │  Prediction  │─▶│   Output     │─▶│   (Console)  │          │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Architecture Layers

| Layer | Components | Technology |
|-------|------------|------------|
| **Data** | MySQL DW, DataLoader, Pandas | SQLAlchemy, pandas |
| **Feature Engineering** | Lag, Rolling, Date features | pandas, numpy |
| **Model** | Linear Regression, Random Forest | scikit-learn |
| **Prediction** | Recursive forecasting | scikit-learn, pandas |
| **Orchestration** | CLI (Typer), task runners | typer, logging |

---

## Component Overview

### Directory Structure

```
phases/phase-2-ml/
│
├── ml/
│   ├── __init__.py                 # Package initialization
│   ├── config.py                   # Configuration & constants
│   ├── data_loader.py              # MySQL data extraction
│   ├── feature_engineering.py      # Feature creation
│   ├── main.py                     # CLI entry point
│   │
│   ├── modeling/                   # Model implementations
│   │   ├── __init__.py
│   │   ├── linear_model.py         # Linear Regression wrapper
│   │   └── random_forest_model.py  # Random Forest wrapper
│   │
│   ├── tasks/                      # ML task implementations
│   │   ├── __init__.py
│   │   ├── train.py                # Training orchestration
│   │   ├── evaluate.py             # Evaluation logic
│   │   └── predict.py              # Forecasting logic
│   │
│   ├── models/                     # Trained model artifacts
│   │   └── global_best_model.pkl   # Best model (joblib)
│   │
│   └── logs/                       # Execution logs
│       └── ml_pipeline_*.log
│
└── requirements.txt
```

### Component Responsibilities

| Component | Responsibility |
|-----------|----------------|
| `config.py` | Database config, paths, feature columns, logging settings |
| `data_loader.py` | Connect to MySQL, aggregate daily sales |
| `feature_engineering.py` | Create lag, rolling, and date features |
| `linear_model.py` | Linear Regression model wrapper |
| `random_forest_model.py` | Random Forest model wrapper |
| `train.py` | Train both models, compare, save best |
| `evaluate.py` | Load model, compute metrics on full data |
| `predict.py` | Recursive multi-day forecasting |
| `main.py` | Typer CLI with train/evaluate/predict commands |

---

## Data Flow

### Complete Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA FLOW DIAGRAM                               │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────┐
                              │   MySQL DW      │
                              │   sales_fact    │
                              │   (9,994 rows)  │
                              └────────┬────────┘
                                       │
                                       │ DataLoader
                                       │ SQL: GROUP BY date
                                       ▼
                              ┌─────────────────┐
                              │  Daily Sales DF │
                              │  full_date,     │
                              │  total_sales    │
                              │  (1,237 rows)   │
                              └────────┬────────┘
                                       │
                                       │ FeatureEngineer
                                       │ - shift() for lags
                                       │ - rolling().mean()
                                       │ - dt.month, dt.dayofweek
                                       ▼
                              ┌─────────────────┐
                              │  Features DF    │
                              │  lag_1, lag_7,  │
                              │  rolling_*,     │
                              │  month, dow,    │
                              │  is_weekend     │
                              │  (1,207 rows)   │
                              └────────┬────────┘
                                       │
                     ┌─────────────────┼─────────────────┐
                     │                 │                 │
                     ▼                 ▼                 ▼
            ┌────────────────┐ ┌──────────────┐ ┌────────────────┐
            │  Train Set     │ │  Test Set    │ │  Full Data     │
            │  (965 rows)    │ │  (242 rows)  │ │  (1,207 rows)  │
            │  80%           │ │  20%         │ │                │
            └───────┬────────┘ └──────┬───────┘ └───────┬────────┘
                    │                 │                 │
            ┌───────▼─────────────────▼─────────────────▼───────┐
            │              Model Training & Evaluation          │
            │  - Linear Regression: train, predict, evaluate    │
            │  - Random Forest: train, predict, evaluate        │
            │  - Select best by lowest RMSE                     │
            └───────────────────────┬───────────────────────────┘
                                    │
                                    │ Best model saved
                                    ▼
                              ┌─────────────────┐
                              │  Model File     │
                              │  .pkl (joblib)  │
                              └────────┬────────┘
                                       │
                                       │ Load for prediction
                                       ▼
                              ┌─────────────────┐
                              │  Recursive      │
                              │  Forecasting    │
                              └────────┬────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │  N-day Forecast │
                              │  (console out)  │
                              └─────────────────┘
```

### Feature Engineering Pipeline

```
┌──────────────────────────────────────────────────────────────────┐
│                    FEATURE ENGINEERING STAGES                     │
└──────────────────────────────────────────────────────────────────┘

  Daily Sales Data (full_date, total_sales)
    │
    │ 1. Sort by date
    ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ Stage 1: Lag Features                                       │
  │ - lag_1 = total_sales.shift(1)                              │
  │ - lag_7 = total_sales.shift(7)                              │
  └─────────────────────────────────────────────────────────────┘
    │
    │ 2. Rolling Statistics (on shifted data)
    ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ Stage 2: Rolling Features                                   │
  │ - rolling_7_mean = total_sales.shift(1).rolling(7).mean()   │
  │ - rolling_30_mean = total_sales.shift(1).rolling(30).mean() │
  └─────────────────────────────────────────────────────────────┘
    │
    │ 3. Date Extraction
    ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ Stage 3: Date Features                                      │
  │ - month = full_date.dt.month                                │
  │ - day_of_week = full_date.dt.dayofweek                      │
  │ - is_weekend = (day_of_week >= 5).astype(int)               │
  └─────────────────────────────────────────────────────────────┘
    │
    │ 4. Drop NaN rows (from lag/rolling)
    ▼
  Final Feature Matrix (1,207 rows × 7 features)
```

---

## Feature Engineering Design

### Lag Features

**Purpose:** Capture temporal dependencies (autocorrelation)

```python
def _create_lag_features(self, df: pd.DataFrame) -> pd.DataFrame:
    for lag in self.lag_features:  # [1, 7]
        col_name = f"lag_{lag}"
        df[col_name] = df['total_sales'].shift(lag)
    return df
```

**Rationale:**
- `lag_1`: Yesterday's sales strongly predict today's
- `lag_7`: Same day last week captures weekly seasonality

### Rolling Features

**Purpose:** Capture trends and smooth out noise

```python
def _create_rolling_features(self, df: pd.DataFrame) -> pd.DataFrame:
    for window in self.rolling_windows:  # [7, 30]
        col_name = f"rolling_{window}_mean"
        # Use shifted sales to prevent data leakage
        df[col_name] = df['total_sales'].shift(1).rolling(window=window).mean()
    return df
```

**Rationale:**
- `rolling_7_mean`: Weekly moving average (short-term trend)
- `rolling_30_mean`: Monthly moving average (long-term trend)

**Critical Design Decision:** Rolling is computed on **shifted** sales to prevent data leakage. Using unshifted sales would include today's value in the rolling mean, which would be unavailable at prediction time.

### Date Features

**Purpose:** Capture calendar-based patterns

```python
def _create_date_features(self, df: pd.DataFrame) -> pd.DataFrame:
    df['month'] = df['full_date'].dt.month
    df['day_of_week'] = df['full_date'].dt.dayofweek
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    return df
```

**Rationale:**
- `month`: Seasonal patterns (holiday shopping, back-to-school)
- `day_of_week`: Weekday vs weekend patterns
- `is_weekend`: Binary flag for weekend effect

---

## Model Architecture

### Linear Regression

**Class:** `ml.modeling.linear_model.LinearRegressionModel`

```python
from sklearn.linear_model import LinearRegression

class LinearRegressionModel:
    def __init__(self):
        self.model = LinearRegression()
    
    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)
    
    def predict(self, X):
        return self.model.predict(X)
    
    def evaluate(self, X_test, y_test):
        predictions = self.predict(X_test)
        return {
            'mae': mean_absolute_error(y_test, predictions),
            'rmse': np.sqrt(mean_squared_error(y_test, predictions)),
            'r2': r2_score(y_test, predictions)
        }
```

**Characteristics:**
- Interpretable (feature coefficients)
- Fast training
- Baseline model
- Assumes linear relationships

### Random Forest

**Class:** `ml.modeling.random_forest_model.RandomForestModel`

```python
from sklearn.ensemble import RandomForestRegressor

class RandomForestModel:
    def __init__(self, n_estimators=100, random_state=42):
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            random_state=random_state
        )
    
    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)
    
    def predict(self, X):
        return self.model.predict(X)
    
    def evaluate(self, X_test, y_test):
        # Same metrics as Linear Regression
        ...
    
    def get_feature_importance(self) -> dict:
        return dict(zip(self.feature_names, self.model.feature_importances_))
```

**Characteristics:**
- Non-linear relationships
- Handles feature interactions
- Robust to outliers
- Provides feature importance

### Model Selection Logic

```python
# Compare RMSE, select lowest
if lr_metrics['rmse'] <= rf_metrics['rmse']:
    best_model = lr_model
    best_metrics = lr_metrics
else:
    best_model = rf_model
    best_metrics = rf_metrics

# Save best model
best_model.save(MODEL_PATH)
```

---

## Prediction Strategy

### Recursive Multi-Day Forecasting

**Challenge:** How to predict multiple days ahead when features depend on previous predictions?

**Solution:** Recursive prediction - use each prediction to compute features for the next day.

```python
def predict_global_sales(model_path: str = None, forecast_days: int = 7):
    # Load historical data
    df = loader.load_global_daily_sales()
    
    # Create features
    features_df = engineer.create_features(df)
    
    # Get last row for initial prediction
    current_features = features_df.iloc[-1:].copy()
    
    predictions = []
    for i in range(forecast_days):
        # Prepare feature vector
        X_pred = current_features[feature_cols]
        
        # Make prediction
        pred_value = model.predict(X_pred)[0]
        
        # Calculate next date
        next_date = last_date + timedelta(days=i+1)
        predictions.append({'full_date': next_date, 'predicted_sales': pred_value})
        
        # Update features for next iteration (recursive step)
        current_features['lag_7'] = current_features['lag_1'].values[0]
        current_features['lag_1'] = pred_value
        # Update rolling means (simplified)
        current_features['rolling_7_mean'] = current_features['rolling_7_mean'].values[0]
        current_features['rolling_30_mean'] = current_features['rolling_30_mean'].values[0]
        # Update date features
        current_features['month'] = next_date.month
        current_features['day_of_week'] = next_date.dayofweek
        current_features['is_weekend'] = 1 if next_date.dayofweek >= 5 else 0
    
    return pd.DataFrame(predictions)
```

### Recursive Update Logic

```
┌─────────────────────────────────────────────────────────────────┐
│              RECURSIVE FEATURE UPDATE STRATEGY                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Iteration 1 (Day 1):                                          │
│  - Use known lag_1, lag_7 from historical data                 │
│  - Predict: pred_1                                             │
│  - Update: lag_7 = old_lag_1, lag_1 = pred_1                   │
│                                                                 │
│  Iteration 2 (Day 2):                                          │
│  - Use updated lag_1 (=pred_1), lag_7 (=old_lag_1)             │
│  - Predict: pred_2                                             │
│  - Update: lag_7 = lag_1, lag_1 = pred_2                       │
│                                                                 │
│  Iteration 3 (Day 3):                                          │
│  - Use updated lag_1 (=pred_2), lag_7 (=pred_1)                │
│  - Predict: pred_3                                             │
│  - Update: lag_7 = lag_1, lag_1 = pred_3                       │
│                                                                 │
│  ... continue for N days                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Limitation:** Rolling means are kept constant (simplified). In production, maintain a rolling window of predictions.

---

## Configuration Management

### config.py Structure

```python
# Project root directory (phase-2-ml)
PROJECT_ROOT = Path(__file__).parent.parent

# Paths
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "ml" / "models"
LOGS_DIR = PROJECT_ROOT / "ml" / "logs"

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
```

### Configuration Principles

- **Environment variables** for sensitive credentials (DB passwords)
- **Constants** for model hyperparameters
- **Centralized paths** for models, logs, data
- **Feature column list** ensures consistency across modules

---

## Execution Flow

### Training Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        TRAINING EXECUTION FLOW                           │
└─────────────────────────────────────────────────────────────────────────┘

  START (python ml/main.py train global)
    │
    ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │ 1. Load Data from MySQL                                             │
  │    - Connect via SQLAlchemy                                         │
  │    - Execute: SELECT DATE, SUM(sales) GROUP BY DATE                 │
  │    - Result: 1,237 days of daily sales                              │
  └─────────────────────────────────────────────────────────────────────┘
    │
    ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │ 2. Feature Engineering                                              │
  │    - Create lag features (1, 7 days)                                │
  │    - Create rolling features (7, 30 days)                           │
  │    - Create date features (month, dow, weekend)                     │
  │    - Drop NaN rows: 1,237 → 1,207                                   │
  └─────────────────────────────────────────────────────────────────────┘
    │
    ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │ 3. Chronological Train-Test Split (80-20)                           │
  │    - Training: 965 samples (first 80%)                              │
  │    - Test: 242 samples (last 20%)                                   │
  │    - NO SHUFFLE (time-series)                                       │
  └─────────────────────────────────────────────────────────────────────┘
    │
    ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │ 4. Train Linear Regression                                          │
  │    - fit(X_train, y_train)                                          │
  │    - predict(X_test)                                                │
  │    - Evaluate: MAE, RMSE, R²                                        │
  └─────────────────────────────────────────────────────────────────────┘
    │
    ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │ 5. Train Random Forest                                              │
  │    - fit(X_train, y_train)                                          │
  │    - predict(X_test)                                                │
  │    - Evaluate: MAE, RMSE, R²                                        │
  └─────────────────────────────────────────────────────────────────────┘
    │
    ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │ 6. Select Best Model (lowest RMSE)                                  │
  │    - Compare LR RMSE vs RF RMSE                                     │
  │    - Select winner                                                  │
  └─────────────────────────────────────────────────────────────────────┘
    │
    ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │ 7. Save Best Model                                                  │
  │    - joblib.dump(model, 'ml/models/global_best_model.pkl')          │
  │    - Print evaluation comparison table                              │
  └─────────────────────────────────────────────────────────────────────┘
    │
    ▼
  END (Training Complete)
```

### Prediction Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PREDICTION EXECUTION FLOW                         │
└─────────────────────────────────────────────────────────────────────────┘

  START (python ml/main.py predict global -d 7)
    │
    ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │ 1. Load Historical Data                                             │
  │    - Same query as training                                         │
  │    - 1,237 days of daily sales                                      │
  └─────────────────────────────────────────────────────────────────────┘
    │
    ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │ 2. Load Trained Model                                               │
  │    - joblib.load('ml/models/global_best_model.pkl')                 │
  └─────────────────────────────────────────────────────────────────────┘
    │
    ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │ 3. Create Features from Historical Data                             │
  │    - Same feature engineering as training                           │
  │    - Get last row for initial prediction                            │
  └─────────────────────────────────────────────────────────────────────┘
    │
    ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │ 4. Recursive Prediction Loop (N days)                               │
  │    For each forecast day:                                           │
  │      a. Prepare feature vector                                      │
  │      b. model.predict(X)                                            │
  │      c. Store prediction with date                                  │
  │      d. Update lag features with prediction                         │
  │      e. Update date features for next date                          │
  └─────────────────────────────────────────────────────────────────────┘
    │
    ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │ 5. Print Forecast Table                                             │
  │    - Date | Predicted Sales                                         │
  │    - Formatted as currency                                          │
  └─────────────────────────────────────────────────────────────────────┘
    │
    ▼
  END (Forecast Complete)
```

### Execution Timeline

| Stage | Duration | Description |
|-------|----------|-------------|
| Data Loading | ~0.1 seconds | SQL query, pandas DataFrame |
| Feature Engineering | ~0.05 seconds | Lag, rolling, date features |
| Train-Test Split | ~0.01 seconds | Chronological split |
| Linear Regression Training | ~0.5 seconds | fit() on 965 samples |
| Random Forest Training | ~0.8 seconds | fit() on 965 samples |
| Model Evaluation | ~0.1 seconds | predict() + metrics |
| Model Save | ~0.05 seconds | joblib.dump() |
| **Total Training** | **~1.5 seconds** | Full training pipeline |
| **Total Prediction** | **~0.5 seconds** | 7-day forecast |

---

## Key Design Decisions

| Decision | Rationale | Trade-offs |
|----------|-----------|------------|
| **Chronological split** | Prevents data leakage in time-series | Can't use cross-validation |
| **Lag before rolling** | Correct temporal ordering | Slightly more complex code |
| **Shifted rolling mean** | Prevents data leakage | Loses first N rows |
| **Two-model comparison** | Baseline + advanced | More training time |
| **RMSE for selection** | Penalizes large errors | May not align with business goals |
| **Recursive prediction** | Simple multi-step forecasting | Error accumulation |
| **joblib for persistence** | Faster than pickle for sklearn | Additional dependency |
| **Typer CLI** | User-friendly interface | Learning curve |

---

## 🔗 Related Documentation

- [Phase 2 README](readme_phase2.md) - Full Phase 2 overview
- [Phase 1 Architecture](../phase-1/architecture.md) - Data warehouse design
- [Phase 1 README](../phase-1/readme_phase1.md) - ETL pipeline details

---

## 📄 License

MIT License - Feel free to use this pipeline for your projects!
