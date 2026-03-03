# Phase 2: Challenges & Solutions

This document details the technical challenges faced during Phase 2 ML Pipeline implementation and the solutions applied.

---

## Table of Contents

1. [Time-Series Data Leakage](#time-series-data-leakage)
2. [Chronological Train-Test Split](#chronological-train-test-split)
3. [Recursive Multi-Step Forecasting](#recursive-multi-step-forecasting)
4. [Database Connection Management](#database-connection-management)
5. [Feature Engineering Order](#feature-engineering-order)
6. [Model Persistence & Versioning](#model-persistence--versioning)
7. [Low R² Interpretation](#low-r²-interpretation)

---

## Time-Series Data Leakage

### 🐛 Problem

**Symptom:** Model shows excellent training metrics but fails in production.

**Root Cause:** Using future information in feature engineering.

```python
# ❌ WRONG - Data leakage!
df['rolling_7_mean'] = df['total_sales'].rolling(window=7).mean()
```

This includes **today's sales** in the rolling mean, which would be unavailable when predicting tomorrow's sales.

### ✅ Solution

**Shift before rolling** to ensure only past data is used:

```python
# ✅ CORRECT - No leakage
df['rolling_7_mean'] = df['total_sales'].shift(1).rolling(window=7).mean()
```

**Key Principle:** All features must be computable using **only historical data** at prediction time.

### Implementation

```python
def _create_rolling_features(self, df: pd.DataFrame) -> pd.DataFrame:
    for window in self.rolling_windows:
        col_name = f"rolling_{window}_mean"
        # Use shifted sales for rolling to prevent data leakage
        df[col_name] = df['total_sales'].shift(1).rolling(window=window).mean()
    return df
```

---

## Chronological Train-Test Split

### 🐛 Problem

**Symptom:** Inflated model performance, poor generalization.

**Root Cause:** Random shuffle in train-test split for time-series data.

```python
# ❌ WRONG - Random shuffle causes data leakage!
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42  # Shuffles data!
)
```

This allows **future data** (test set) to leak into **past data** (training set), violating temporal causality.

### ✅ Solution

**Chronological split** without shuffling:

```python
# ✅ CORRECT - Chronological split
split_idx = int(len(X) * 0.8)  # 80-20 split

X_train = X.iloc[:split_idx]
X_test = X.iloc[split_idx:]
y_train = y.iloc[:split_idx]
y_test = y.iloc[split_idx:]
```

**Key Principle:** Training data must be **temporally before** test data.

### Implementation

```python
def train_global_model():
    # Chronological train-test split (80-20, no shuffle)
    logger.info("Step 3: Performing chronological train-test split (80-20)...")
    split_idx = int(len(X) * (1 - MODEL_CONFIG['test_size']))

    X_train = X.iloc[:split_idx]
    X_test = X.iloc[split_idx:]
    y_train = y.iloc[:split_idx]
    y_test = y.iloc[split_idx:]

    logger.info(f"Training samples: {len(X_train)}, Test samples: {len(X_test)}")
```

---

## Recursive Multi-Step Forecasting

### 🐛 Problem

**Symptom:** Can't predict multiple days ahead because features depend on unknown future values.

**Root Cause:** Lag features require previous day's sales, which don't exist for future dates.

```python
# Day 1 prediction needs lag_1 = yesterday's sales (known)
# Day 2 prediction needs lag_1 = Day 1's sales (unknown!)
# Day 3 prediction needs lag_1 = Day 2's sales (unknown!)
```

### ✅ Solution

**Recursive prediction:** Use each prediction as input for the next prediction.

```python
# ✅ CORRECT - Recursive forecasting
current_features = features_df.iloc[-1:].copy()

for i in range(forecast_days):
    # Make prediction
    pred_value = model.predict(X_pred)[0]
    
    # Update features for next iteration
    current_features['lag_7'] = current_features['lag_1'].values[0]
    current_features['lag_1'] = pred_value  # Use prediction as next lag
    
    # Update date features
    next_date = last_date + timedelta(days=i+1)
    current_features['month'] = next_date.month
    current_features['day_of_week'] = next_date.dayofweek
    current_features['is_weekend'] = 1 if next_date.dayofweek >= 5 else 0
```

**Trade-off:** Prediction errors **accumulate** over time (error propagation).

### Visualization

```
┌─────────────────────────────────────────────────────────────────┐
│              RECURSIVE PREDICTION CHAIN                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Historical:  [Day-7] [Day-6] ... [Day-1] [Day 0]               │
│                          │         │                            │
│                          ▼         ▼                            │
│  Predict:                └────► pred_1 (uses Day 0 as lag_1)    │
│                                    │                            │
│                                    ▼                            │
│                          └────► pred_2 (uses pred_1 as lag_1)   │
│                                              │                  │
│                                              ▼                  │
│                                    └────► pred_3 (uses pred_2)  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Database Connection Management

### 🐛 Problem

**Symptom:** Connection errors, resource leaks, "too many connections" errors.

**Root Cause:** Not properly closing database connections after use.

```python
# ❌ WRONG - Connection may not be closed on error
loader = DataLoader()
loader.connect()
df = loader.load_global_daily_sales()
# If error occurs here, connection is never closed!
loader.disconnect()
```

### ✅ Solution

**Context manager** pattern for automatic resource cleanup:

```python
# ✅ CORRECT - Context manager ensures cleanup
class DataLoader:
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

# Usage
with DataLoader() as loader:
    df = loader.load_global_daily_sales()
# Connection automatically closed, even if error occurred
```

### Implementation

```python
def load_global_daily_sales() -> pd.DataFrame:
    query = text("""
        SELECT
            d.full_date,
            SUM(f.sales) as total_sales
        FROM sales_fact f
        JOIN dim_date d ON f.date_key = d.date_key
        GROUP BY d.full_date
        ORDER BY d.full_date
    """)

    try:
        if not self.engine:
            if not self.connect():
                raise ConnectionError("Cannot connect to database")

        df = pd.read_sql_query(query, self.engine)
        df['full_date'] = pd.to_datetime(df['full_date'])

        row_count = len(df)
        logger.info(f"Loaded {row_count} days of sales data")

        return df

    except SQLAlchemyError as e:
        logger.error(f"Failed to load sales data: {e}")
        raise
```

---

## Feature Engineering Order

### 🐛 Problem

**Symptom:** Incorrect feature values, data leakage, model performs poorly.

**Root Cause:** Applying transformations in wrong order.

```python
# ❌ WRONG - Rolling before lag causes leakage!
df['rolling_7_mean'] = df['total_sales'].rolling(7).mean()  # Includes today
df['lag_1'] = df['total_sales'].shift(1)  # Correct, but too late
```

### ✅ Solution

**Correct order:** Lag first, then rolling on shifted data.

```python
# ✅ CORRECT - Proper ordering
def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
    # 1. Sort by date (ensure temporal ordering)
    df = df.sort_values('full_date').reset_index(drop=True)
    
    # 2. Create lag features FIRST
    df = self._create_lag_features(df)
    
    # 3. Create rolling features on SHIFTED data
    df = self._create_rolling_features(df)
    
    # 4. Create date features
    df = self._create_date_features(df)
    
    # 5. Drop NaN rows (from lag/rolling)
    df = df.dropna().reset_index(drop=True)
    
    return df
```

### Execution Order

```
┌─────────────────────────────────────────────────────────────┐
│           FEATURE ENGINEERING EXECUTION ORDER                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Sort by date         (ensure temporal ordering)         │
│         │                                                   │
│         ▼                                                   │
│  2. Lag features         (shift(1), shift(7))               │
│         │                                                   │
│         ▼                                                   │
│  3. Rolling features     (rolling on shifted data)          │
│         │                                                   │
│         ▼                                                   │
│  4. Date features        (month, day_of_week, is_weekend)   │
│         │                                                   │
│         ▼                                                   │
│  5. Drop NaN rows        (remove rows with null features)   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Model Persistence & Versioning

### 🐛 Problem

**Symptom:** Can't reload trained models, model files corrupted, wrong model loaded.

**Root Cause:** Inconsistent model saving/loading, no version tracking.

```python
# ❌ WRONG - No error handling, no metadata
joblib.dump(model, 'model.pkl')
# Later...
model = joblib.load('model.pkl')  # What if file doesn't exist?
```

### ✅ Solution

**Robust model persistence** with error handling and metadata:

```python
# ✅ CORRECT - Robust persistence
def save(self, filepath: Path):
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(self.model, filepath)
    logger.info(f"Model saved to {filepath}")

def load(self, filepath: Path):
    if not Path(filepath).exists():
        raise FileNotFoundError(f"Model file not found: {filepath}")
    self.model = joblib.load(filepath)
    self.is_trained = True
    logger.info(f"Model loaded from {filepath}")
```

### Model Selection Logic

```python
# Select best model based on lowest RMSE
if lr_metrics['rmse'] <= rf_metrics['rmse']:
    best_model = lr_model
    best_metrics = lr_metrics
    logger.info(f"Linear Regression selected (RMSE: {lr_metrics['rmse']:.2f})")
else:
    best_model = rf_model
    best_metrics = rf_metrics
    logger.info(f"Random Forest selected (RMSE: {rf_metrics['rmse']:.2f})")

# Save best model
best_model.save(MODEL_PATH)
```

---

## Low R² Interpretation

### 🐛 Problem

**Symptom:** Model R² = 0.018 (explains only 2% of variance). Stakeholders question model value.

**Root Cause:** Simple baseline model with limited features on volatile retail data.

### ✅ Solution

**Proper interpretation** and improvement roadmap:

#### Why Low R² is Expected

1. **Simple features:** Only 7 time-series features, no external data
2. **No holidays/promotions:** Major sales drivers not included
3. **High variance:** Daily retail sales are inherently volatile
4. **Linear assumptions:** Complex patterns not captured

#### Business Context

| Metric | Value | Interpretation |
|--------|-------|----------------|
| MAE | $1,695 | Average error ~$1.7K/day |
| RMSE | $2,431 | Large errors penalized |
| R² | 0.018 | 2% variance explained |

**Baseline Value:** This model provides a **starting point** for improvement. Even simple forecasts are better than none.

#### Improvement Roadmap

| Priority | Improvement | Expected R² Gain | Effort |
|----------|-------------|------------------|--------|
| 🔴 High | Add holiday flags | +5-10% | Low |
| 🔴 High | Add promotion data | +10-15% | Medium |
| 🟡 Medium | More lag features (30, 60, 90) | +2-5% | Low |
| 🟡 Medium | Hyperparameter tuning | +3-5% | Medium |
| 🟡 Medium | XGBoost/LightGBM | +5-10% | Medium |
| 🟢 Low | Prophet (Facebook) | +10-20% | Low |
| 🟢 Low | LSTM neural network | +15-25% | High |
| 🟢 Low | Customer segmentation | +5-10% | High |

---

## Summary of Solutions

| Challenge | Solution | Key Code Pattern |
|-----------|----------|------------------|
| Data leakage | Shift before rolling | `df.shift(1).rolling(window)` |
| Random shuffle | Chronological split | `iloc[:split_idx]` |
| Multi-step forecast | Recursive prediction | `lag_1 = pred_value` |
| Connection leaks | Context manager | `with DataLoader() as loader:` |
| Feature order | Lag → Rolling → Date | Sequential method calls |
| Model persistence | joblib + error handling | `joblib.dump/load()` |
| Low R² | Improvement roadmap | Add features, advanced models |

---

## 🔗 Related Documentation

- [Phase 2 README](readme_phase2.md) - Full Phase 2 overview
- [Phase 2 Architecture](architecture.md) - Technical architecture details
- [Phase 1 Problems Faced](../phase-1/problems_faced.md) - ETL challenges

---

## 📄 License

MIT License - Feel free to use this pipeline for your projects!
