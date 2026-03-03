# Phase 2: ML Layer - Global Daily Sales Forecasting

## Overview

Phase 2 implements a **machine learning pipeline** that builds on the Phase 1 data warehouse to forecast future daily sales. This phase demonstrates end-to-end ML engineering including data extraction, feature engineering, model training, evaluation, and prediction.

### What This Pipeline Does

1. **Extract**: Loads aggregated daily sales from MySQL data warehouse (1,237 days of data)
2. **Transform**: Creates time-series features (lag, rolling statistics, date features)
3. **Train**: Trains Linear Regression and Random Forest models, auto-selects best by RMSE
4. **Evaluate**: Computes MAE, RMSE, R² metrics on test data
5. **Predict**: Generates multi-day sales forecasts using recursive prediction

### Why It Matters

This pipeline solves authentic **time-series forecasting challenges**:
- Chronological train-test splits (no random shuffle to prevent data leakage)
- Lag feature engineering for temporal dependencies
- Rolling window statistics for trend capture
- Recursive multi-step forecasting
- Model comparison and automatic selection

---

## 📁 Project Structure

```
phases/phase-2-ml/
│
├── ml/                          # ML pipeline source code
│   ├── __init__.py              # Package initialization
│   ├── config.py                # Configuration & paths
│   ├── data_loader.py           # MySQL data extraction
│   ├── feature_engineering.py   # Time-series feature creation
│   ├── main.py                  # CLI entry point
│   │
│   ├── modeling/                # Model implementations
│   │   ├── __init__.py
│   │   ├── linear_model.py      # Linear Regression wrapper
│   │   └── random_forest_model.py # Random Forest wrapper
│   │
│   ├── tasks/                   # ML task implementations
│   │   ├── __init__.py
│   │   ├── train.py             # Model training logic
│   │   ├── evaluate.py          # Model evaluation logic
│   │   └── predict.py           # Sales forecasting logic
│   │
│   ├── models/                  # Trained model artifacts
│   │   └── global_best_model.pkl # Best performing model
│   │
│   └── logs/                    # Pipeline execution logs
│       └── ml_pipeline_*.log    # Detailed execution logs
│
└── requirements.txt             # Python dependencies
```

---

## ⚡ Quick Start

### Prerequisites

- **Python 3.8+**
- **Phase 1 ETL completed** (MySQL data warehouse populated)
- **scikit-learn, pandas, numpy, sqlalchemy**

### Setup

```bash
# 1. Navigate to Phase 2 directory
cd phases/phase-2-ml

# 2. Install dependencies
pip install -r requirements.txt

# 3. Ensure MySQL from Phase 1 is running
docker ps | grep mysql_retail

# 4. Train the model
python ml/main.py train global

# 5. Evaluate the model
python ml/main.py evaluate global

# 6. Generate 7-day forecast
python ml/main.py predict global -d 7
```

---

## 🏗️ ML Pipeline Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     PHASE 2 ML PIPELINE FLOW                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │    EXTRACT   │────▶│  TRANSFORM   │────▶│    MODEL     │            │
│  │              │     │              │     │              │            │
│  │  MySQL DW    │     │  Feature     │     │  Train &     │            │
│  │  1,237 days  │     │  Engineering │     │  Evaluate    │            │
│  └──────────────┘     └──────────────┘     └──────┬───────┘            │
│                                                    │                     │
│                                                    ▼                     │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │   FORECAST   │◀────│    PREDICT   │◀────│    SELECT    │            │
│  │              │     │              │     │              │            │
│  │  N days      │     │  Recursive   │     │  Best Model  │            │
│  │  ahead       │     │  Prediction  │     │  (by RMSE)   │            │
│  └──────────────┘     └──────────────┘     └──────────────┘            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Component Overview

| Component | Responsibility |
|-----------|----------------|
| `data_loader.py` | Extract daily sales from MySQL warehouse |
| `feature_engineering.py` | Create lag, rolling, and date features |
| `linear_model.py` | Linear Regression baseline model |
| `random_forest_model.py` | Random Forest advanced model |
| `train.py` | Train both models, select best by RMSE |
| `evaluate.py` | Evaluate model on full dataset |
| `predict.py` | Generate multi-day forecasts |

---

## 🎯 Pipeline Results

### Training Results

| Metric | Value |
|--------|-------|
| **Data Loaded** | 1,237 days of sales (2014-2017) |
| **Training Samples** | 965 days (80%) |
| **Test Samples** | 242 days (20%) |
| **Best Model** | Linear Regression |
| **MAE** | $1,695.27 |
| **RMSE** | $2,430.97 |
| **R²** | 0.0184 |

### Model Comparison

| Model | MAE | RMSE | R² |
|-------|-----|------|-----|
| **Linear Regression** ✅ | $1,695.27 | $2,430.97 | 0.0184 |
| Random Forest | $1,679.53 | $2,435.01 | 0.0151 |

### Sample 14-Day Forecast

| Date | Predicted Sales |
|------|-----------------|
| 2017-12-31 (Sun) | $2,301.95 |
| 2018-01-01 (Mon) | $2,377.10 |
| 2018-01-02 (Tue) | $1,094.03 |
| 2018-01-03 (Wed) | $1,068.75 |
| 2018-01-04 (Thu) | $1,007.96 |
| 2018-01-05 (Fri) | $1,028.15 |
| 2018-01-06 (Sat) | $1,049.47 |
| ... | ... |

---

## 🔧 Feature Engineering

### Features Created

| Feature | Type | Description |
|---------|------|-------------|
| `lag_1` | Lag | Sales from 1 day ago |
| `lag_7` | Lag | Sales from 7 days ago (weekly seasonality) |
| `rolling_7_mean` | Rolling | 7-day moving average (trend) |
| `rolling_30_mean` | Rolling | 30-day moving average (long-term trend) |
| `month` | Date | Month of year (1-12) |
| `day_of_week` | Date | Day of week (0=Monday, 6=Sunday) |
| `is_weekend` | Date | Weekend flag (1 if Sat/Sun, 0 otherwise) |

### Feature Engineering Code

```python
from ml.feature_engineering import FeatureEngineer

engineer = FeatureEngineer(
    lag_features=[1, 7],
    rolling_windows=[7, 30]
)

features_df = engineer.create_features(daily_sales_df)
X, y = engineer.get_feature_matrix(features_df)
```

### Why These Features?

- **Lag features**: Capture temporal dependencies (yesterday's sales predict today's)
- **Weekly lag**: Retail has strong weekly seasonality (weekends vs weekdays)
- **Rolling means**: Smooth out noise, capture trends
- **Date features**: Capture monthly and weekly patterns

---

## 📊 Model Training

### Chronological Split (80-20)

```
┌────────────────────────────────────────────────────────────┐
│           TIME-SERIES TRAIN-TEST SPLIT                      │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  2014-01-03 ────────────────────── 2017-05-15 ─────────── │
│  │                              │  │                     │
│  │    TRAINING SET (80%)        │  │  TEST SET (20%)     │
│  │    965 samples               │  │  242 samples        │
│  │                              │  │                     │
│  └──────────────────────────────┘  └─────────────────────┘
│                                                            │
│  ⚠️ NO RANDOM SHUFFLE - prevents data leakage             │
└────────────────────────────────────────────────────────────┘
```

### Training Process

```python
from ml.tasks.train import train_global_model

results = train_global_model()

# Results include:
# - linear_regression: {'mae', 'rmse', 'r2'}
# - random_forest: {'mae', 'rmse', 'r2'}
# - best_model: selected by lowest RMSE
# - model_path: path to saved model
```

### Model Selection Logic

1. Train **Linear Regression** (baseline, interpretable)
2. Train **Random Forest** (non-linear, captures interactions)
3. Compare **RMSE** on test set
4. Save model with **lowest RMSE**

---

## 🔮 Prediction Strategy

### Recursive Multi-Day Forecasting

```
┌─────────────────────────────────────────────────────────────────┐
│              RECURSIVE PREDICTION STRATEGY                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Day 1: Predict using known features → pred_1                   │
│         │                                                       │
│         ▼                                                       │
│  Day 2: Update lag_1 = pred_1, lag_7 = lag_6 → pred_2           │
│         │                                                       │
│         ▼                                                       │
│  Day 3: Update lag_1 = pred_2, lag_7 = lag_5 → pred_3           │
│         │                                                       │
│         ▼                                                       │
│  ... continue for N forecast days                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Prediction Command

```bash
# Forecast next 7 days
python ml/main.py predict global -d 7

# Forecast next 30 days
python ml/main.py predict global -d 30

# Use custom model path
python ml/main.py predict global -d 14 -m models/my_model.pkl
```

---

## 🛠️ CLI Reference

### Commands

| Command | Description |
|---------|-------------|
| `train global` | Train Linear Regression + Random Forest, save best |
| `evaluate global` | Evaluate trained model on full dataset |
| `predict global` | Generate N-day sales forecast |

### Options

```bash
# Train command
python ml/main.py train global

# Evaluate command
python ml/main.py evaluate global
python ml/main.py evaluate global -m models/custom_model.pkl

# Predict command
python ml/main.py predict global -d 7
python ml/main.py predict global -d 30 -m models/my_model.pkl
```

### Examples

```bash
# Full workflow
python ml/main.py train global      # Train models
python ml/main.py evaluate global   # Evaluate best model
python ml/main.py predict global -d 14  # 14-day forecast
```

---

## 📝 Configuration

### Database Configuration

Edit environment variables or `ml/config.py`:

```python
DB_CONFIG = {
    "host": "localhost",
    "port": "3306",
    "database": "retail_db",
    "user": "root",
    "password": "root"
}
```

### Model Configuration

```python
MODEL_CONFIG = {
    "test_size": 0.2,  # 80-20 chronological split
    "random_state": 42,
    "lag_features": [1, 7],
    "rolling_windows": [7, 30]
}
```

### Feature Columns

```python
FEATURE_COLUMNS = [
    "lag_1",
    "lag_7",
    "rolling_7_mean",
    "rolling_30_mean",
    "month",
    "day_of_week",
    "is_weekend"
]
```

---

## 🐛 Troubleshooting

### Database Connection Error

```bash
# Ensure MySQL container is running
docker ps | grep mysql_retail

# Test connection
docker exec mysql_retail mysql -uroot -proot -e "SELECT 1"
```

### Model Not Found

```
Error: Model file not found: ml/models/global_best_model.pkl
Solution: Run 'python ml/main.py train global' first
```

### No Data Loaded

```
Error: No data loaded from warehouse
Solution: Ensure Phase 1 ETL has been run successfully
```

### Feature Columns Missing

```
ValueError: Missing feature columns: [...]
Solution: Re-run feature engineering or check data_loader query
```

---

## 📈 Model Performance Analysis

### Current Performance

| Metric | Value | Interpretation |
|--------|-------|----------------|
| **MAE** | $1,695 | Average error of ~$1.7K/day |
| **RMSE** | $2,431 | Penalizes large errors |
| **R²** | 0.018 | Explains ~2% of variance |

### Why Low R²?

The low R² is expected for this baseline model:

1. **Simple features**: Only 7 features, no external data
2. **No holidays/promotions**: Major sales drivers not included
3. **Linear assumptions**: Complex retail patterns not captured
4. **High variance**: Daily sales naturally volatile

### Improvement Strategies

| Strategy | Expected Impact | Effort |
|----------|-----------------|--------|
| Add holiday flags | High | Low |
| Add promotion data | High | Medium |
| More lag features (30, 60, 90) | Medium | Low |
| Hyperparameter tuning | Medium | Medium |
| XGBoost/LightGBM | Medium | Medium |
| Prophet (Facebook) | High | Low |
| LSTM neural network | High | High |
| Customer segmentation | Medium | High |

---

## 📊 Output Artifacts

After successful execution:

- ✅ **Trained model**: `ml/models/global_best_model.pkl`
- ✅ **Execution logs**: `ml/logs/ml_pipeline_*.log`
- ✅ **Evaluation metrics**: MAE, RMSE, R² printed to console
- ✅ **Forecast output**: N-day predictions with dates

---

## 🔗 Integration with Phase 1

### Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│              PHASE 1 → PHASE 2 INTEGRATION                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Phase 1: ETL Pipeline                                      │
│  ┌──────────────┐                                          │
│  │  CSV → Spark │                                          │
│  │  → MySQL DW  │                                          │
│  └──────┬───────┘                                          │
│         │                                                   │
│         │ sales_fact table                                  │
│         │ (9,994 transactions)                              │
│         ▼                                                   │
│  Phase 2: ML Pipeline                                       │
│  ┌──────────────┐                                          │
│  │  MySQL DW →  │                                          │
│  │  Aggregation │                                          │
│  │  → Features  │                                          │
│  │  → Model     │                                          │
│  └──────────────┘                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### SQL Aggregation Query

```sql
SELECT
    d.full_date,
    SUM(f.sales) as total_sales
FROM sales_fact f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.full_date
ORDER BY d.full_date
```

---

## 📈 Lessons Learned

1. **Chronological splits are critical** - Random shuffle causes data leakage in time-series
2. **Lag before rolling** - Shift lag features before computing rolling statistics
3. **Recursive prediction complexity** - Each prediction compounds errors
4. **Feature importance > accuracy** - Linear models provide interpretable coefficients
5. **Baseline first** - Start simple (Linear Regression) before complex models
6. **Data quality matters** - Phase 1 ETL quality directly impacts ML performance

---

## 🔗 Related Documentation

- [Phase 1: Batch ETL](../phase-1/readme_phase1.md) - Data warehouse setup
- [Phase 1 Architecture](../phase-1/architecture.md) - Star schema design
- [Phase 1 Problems Faced](../phase-1/problems_faced.md) - ETL challenges

---

## 📄 License

MIT License - Feel free to use this pipeline for your projects!

---

## 👥 Author

**Retail Analytics Data Engineering Team**

Built with ❤️ using scikit-learn, pandas, and MySQL.
