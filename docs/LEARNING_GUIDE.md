# Complete Learning Guide: Retail Analytics Data Engineering Pipeline

## 📚 Table of Contents

1. [Introduction - What Is This Project?](#introduction---what-is-this-project)
2. [Prerequisites - What You Need to Know](#prerequisites---what-you-need-to-know)
3. [Project Overview - The Big Picture](#project-overview---the-big-picture)
4. [Folder-by-Folder Explanation](#folder-by-folder-explanation)
5. [Phase 1: ETL Pipeline - Deep Dive](#phase-1-etl-pipeline---deep-dive)
6. [Phase 2: ML Pipeline - Deep Dive](#phase-2-ml-pipeline---deep-dive)
7. [Code Walkthrough - Every File Explained](#code-walkthrough---every-file-explained)
8. [How Data Flows Through the System](#how-data-flows-through-the-system)
9. [Running the Project Step-by-Step](#running-the-project-step-by-step)
10. [Common Questions & Troubleshooting](#common-questions--troubleshooting)
11. [Learning Path - What to Study Next](#learning-path---what-to-study-next)

---

## Introduction - What Is This Project?

### The Problem This Project Solves

Imagine you're a data engineer at a retail company. Every day, your stores generate thousands of sales transactions. These transactions are recorded in simple CSV files or Excel sheets. The business team wants to answer questions like:

- "What were our total sales last month?"
- "Which products are selling the most?"
- "Which customers are our best customers?"
- "Can you predict next week's sales?"

**The challenge:** Raw sales data is messy and not organized for analysis. You can't just ask these questions directly from the raw data - it would be too slow and complicated.

**The solution:** This project builds a **data pipeline** that:
1. Takes raw, messy sales data
2. Cleans and organizes it
3. Stores it in a structured database (data warehouse)
4. Uses machine learning to predict future sales

### Real-World Analogy

Think of this like a **restaurant kitchen**:

- **Raw ingredients (CSV files)** = Raw sales data from stores
- **Prep work (ETL)** = Washing, chopping, organizing ingredients
- **Organized kitchen (Data Warehouse)** = Clean, labeled containers ready for cooking
- **Chef making predictions (ML)** = Experienced chef predicting how much food to prepare tomorrow

### What You'll Learn

By studying this project, you'll learn:
- **Data Engineering**: How to build pipelines that move and transform data
- **PySpark**: How to process large datasets using Apache Spark
- **Data Warehousing**: How to design star schema databases
- **Machine Learning**: How to build time-series forecasting models
- **Production Practices**: Logging, error handling, configuration management

---

## Prerequisites - What You Need to Know

### Essential Knowledge (Start Here If You're New)

#### 1. Python Basics
You should understand:
- Variables, data types (strings, integers, lists, dictionaries)
- Functions and classes
- Import statements
- File paths

**If you don't know this:** Study Python basics first (python.org, Codecademy, freeCodeCamp)

#### 2. SQL Basics
You should understand:
- SELECT, FROM, WHERE clauses
- JOIN operations
- GROUP BY and aggregations (SUM, COUNT, AVG)

**If you don't know this:** Study SQL basics (SQLZoo, Khan Academy SQL)

#### 3. Basic Command Line
You should know how to:
- Open a terminal/command prompt
- Navigate directories (cd, ls, dir)
- Run Python scripts

### Helpful But Not Required

- Basic understanding of databases
- Familiarity with pandas (Python data library)
- Basic statistics (mean, median, standard deviation)

---

## Project Overview - The Big Picture

### The Two Phases

This project has **two main parts** that build on each other:

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMPLETE PROJECT FLOW                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PHASE 1: ETL (Extract, Transform, Load)                        │
│  ──────────────────────────────────────                         │
│  Raw CSV → Clean Data → MySQL Database                          │
│                                                                 │
│  Input:  superstore.csv (9,994 sales records)                   │
│  Output: MySQL database with organized tables                   │
│  Tools:  PySpark, MySQL, Docker                                 │
│                                                                 │
│                          │                                      │
│                          ▼                                      │
│                                                                 │
│  PHASE 2: Machine Learning                                      │
│  ───────────────────────                                        │
│  MySQL Data → Features → ML Model → Predictions                 │
│                                                                 │
│  Input:  Sales data from Phase 1 database                       │
│  Output: Sales forecasts for future days                        │
│  Tools:  scikit-learn, pandas, SQLAlchemy                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Why Two Phases?

**Phase 1** answers: "What happened in the past?"
- Organizes historical sales data
- Makes it easy to query and analyze

**Phase 2** answers: "What will happen in the future?"
- Uses historical data to predict future sales
- Helps with inventory planning, staffing, etc.

### Key Technologies Explained

| Technology | What It Is | Why We Use It |
|------------|------------|---------------|
| **PySpark** | Python library for Apache Spark | Process large datasets quickly using distributed computing |
| **MySQL** | Relational database | Store organized data in tables with relationships |
| **Docker** | Container platform | Run MySQL without installing it on your computer |
| **scikit-learn** | Machine learning library | Build and train forecasting models |
| **SQLAlchemy** | SQL toolkit for Python | Connect to MySQL database from Python |
| **pandas** | Data manipulation library | Work with tabular data in Python |

---

## Folder-by-Folder Explanation

### Root Directory Structure

```
RetailAnalyticsProject/
│
├── README.md                    # Project overview (what you're reading now)
├── docs/                        # All documentation
├── phases/                      # Main code for both phases
├── data/                        # Raw CSV data files (Phase 1 input)
└── .git/                        # Git version control (ignore this)
```

### The `docs/` Folder

```
docs/
├── phase-1/                     # Phase 1 documentation
│   ├── readme_phase1.md         # Detailed Phase 1 guide
│   ├── architecture.md          # Technical architecture diagrams
│   └── problems_faced.md        # Challenges and solutions
│
├── phase-2/                     # Phase 2 documentation
│   ├── readme_phase2.md         # Detailed Phase 2 guide
│   ├── architecture.md          # ML pipeline architecture
│   └── problems_faced.md        # ML challenges and solutions
│
└── LEARNING_GUIDE.md            # This file - complete learning guide
```

**Purpose:** All written documentation about how the project works.

### The `phases/` Folder

```
phases/
├── phase-1-etl/                 # Phase 1: Data Pipeline
│   ├── main.py                  # Main entry point - runs the ETL
│   ├── requirements.txt         # Python dependencies for Phase 1
│   ├── config/                  # Configuration settings
│   │   ├── __init__.py
│   │   └── config.py            # Database credentials, Spark settings
│   ├── etl/                     # ETL transformation code
│   │   ├── __init__.py
│   │   ├── transformations.py   # Data cleaning functions
│   │   ├── dimension_loader.py  # Load dimension tables
│   │   └── fact_loader.py       # Load fact table
│   ├── warehouse/               # Database schema
│   │   ├── __init__.py
│   │   ├── schema.sql           # SQL to create tables
│   │   └── init_db.py           # Initialize database
│   ├── data/                    # Input CSV files
│   │   └── superstore.csv       # 9,994 sales records
│   ├── logs/                    # Execution logs
│   │   └── etl_pipeline.log     # Log file from running
│   └── jars/                    # JDBC drivers
│       └── mysql-connector-j-9.6.0.jar  # MySQL driver for Spark
│
└── phase-2-ml/                  # Phase 2: Machine Learning
    ├── main.py                  # CLI entry point
    ├── requirements.txt         # Python dependencies for Phase 2
    └── ml/                      # ML pipeline code
        ├── __init__.py
        ├── config.py            # ML configuration
        ├── data_loader.py       # Load data from MySQL
        ├── feature_engineering.py  # Create ML features
        ├── main.py              # CLI commands (train/evaluate/predict)
        ├── modeling/            # ML model implementations
        │   ├── __init__.py
        │   ├── linear_model.py      # Linear Regression
        │   └── random_forest_model.py # Random Forest
        ├── tasks/               # ML tasks
        │   ├── __init__.py
        │   ├── train.py         # Training logic
        │   ├── evaluate.py      # Evaluation logic
        │   └── predict.py       # Prediction logic
        ├── models/              # Trained models (created after training)
        │   └── global_best_model.pkl
        └── logs/                # ML execution logs
```

### Detailed Folder Purposes

#### `phases/phase-1-etl/config/`
**What:** Configuration settings
**Contains:** Database connection info, Spark settings
**Why:** Central place to change settings without modifying code

#### `phases/phase-1-etl/etl/`
**What:** ETL transformation logic
**Contains:** Code that cleans and transforms data
**Why:** Separates business logic from orchestration

#### `phases/phase-1-etl/warehouse/`
**What:** Database schema definitions
**Contains:** SQL to create tables, Python to initialize DB
**Why:** Version-controlled database structure

#### `phases/phase-2-ml/ml/modeling/`
**What:** Machine learning model wrappers
**Contains:** Linear Regression and Random Forest implementations
**Why:** Encapsulates ML logic for easy swapping

#### `phases/phase-2-ml/ml/tasks/`
**What:** High-level ML operations
**Contains:** Train, evaluate, predict functions
**Why:** Organizes ML workflow into clear steps

---

## Phase 1: ETL Pipeline - Deep Dive

### What is ETL?

**ETL = Extract, Transform, Load**

It's a three-step process to move data from source to destination:

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   EXTRACT   │────▶│  TRANSFORM   │────▶│    LOAD     │
│             │     │              │     │             │
│ Read CSV    │     │ Clean data   │     │ Write to    │
│ 9,994 rows  │     │ Fix dates    │     │ MySQL       │
│             │     │ Remove dups  │     │             │
└─────────────┘     └──────────────┘     └─────────────┘
```

### Real Example: Why ETL is Needed

**Raw CSV Data (Messy):**
```
Order_ID,Order_Date,Sales,Customer
1001,1/15/2014,50.25,John
1002,2014-01-16,invalid,Bob
1003,Jan 17 2014,75.00,John  # Duplicate customer
```

**Problems:**
- Dates in different formats (1/15/2014, 2014-01-16, Jan 17 2014)
- Invalid sales value ("invalid")
- Duplicate customer names

**After ETL (Clean):**
```
order_id | order_date  | sales | customer_id
1001     | 2014-01-15  | 50.25 | 1
1002     | 2014-01-16  | NULL  | 2
1003     | 2014-01-17  | 75.00 | 1
```

### The Star Schema Design

Phase 1 creates a **star schema** - a specific database design optimized for analytics.

```
                         ┌─────────────────┐
                         │   dim_date      │
                         │ (date info)     │
                         └────────┬────────┘
                                  │
                                  │
┌──────────────┐                 │                  ┌──────────────┐
│ dim_product  │◀────────────────┼────────────────▶│ dim_customer │
│(product info)│                 │                 │(customer info)│
└──────────────┘                 │                 └──────────────┘
                                 │
                                 ▼
                         ┌─────────────────┐
                         │   sales_fact    │
                         │ (actual sales)  │
                         └────────┬────────┘
                                 │
                                 │
┌──────────────┐                 │                  ┌──────────────┐
│ dim_location │◀────────────────┼────────────────▶│  dim_store   │
│(location info)│                │                 │ (store info) │
└──────────────┘                 │                 └──────────────┘
                                 │
                         ┌─────────────────┐
                         │   dim_date      │
                         │ (date info)     │
                         └─────────────────┘
```

**Why this design?**
- **Fast queries**: Each dimension is separate, no repetition
- **Easy to understand**: Clear relationships
- **Optimized for analytics**: Perfect for SUM, COUNT, GROUP BY

### Dimension Tables Explained

#### `dim_product` (1,862 rows)
**What:** Information about products
**Columns:**
- `product_id` (Primary Key): Unique ID like "OFF-AR-10002833"
- `product_name`: Name like "Staples"
- `category`: Category like "Office Supplies"
- `sub_category`: Sub-category like "Art"

**Example:**
```
product_id       | product_name    | category        | sub_category
OFF-AR-10002833  | Staples         | Office Supplies | Art
TEC-PH-10002275  | Phone           | Technology      | Phones
```

#### `dim_customer` (793 rows)
**What:** Information about customers
**Columns:**
- `customer_id` (Primary Key): Unique ID like "CG-12520"
- `customer_name`: Name like "Claire Gute"
- `segment`: Customer segment like "Consumer"

**Example:**
```
customer_id | customer_name   | segment
CG-12520    | Claire Gute     | Consumer
DV-13045    | Darrin Van Huff | Corporate
```

#### `dim_location` (632 rows)
**What:** Geographic information
**Columns:**
- `location_id` (Primary Key): Auto-generated ID
- `country`: Country name
- `state`: State name
- `city`: City name
- `region`: Region (Central, East, South, West)

**Example:**
```
location_id | country | state      | city        | region
1           | US      | California | Los Angeles | West
2           | US      | New York   | NYC         | East
```

#### `dim_store` (5 rows)
**What:** Synthetic store assignments
**Columns:**
- `store_id` (Primary Key): 1-5
- `store_name`: Store_1 to Store_5

**Why synthetic?** Original data didn't have store info, so we created 5 fictional stores.

#### `dim_date` (1,458 rows)
**What:** Date dimension for time-based analysis
**Columns:**
- `date_key` (Primary Key): Integer like 20140115
- `full_date`: Full date like 2014-01-15
- `year`, `month`, `day`: Date parts
- `quarter`: Q1, Q2, Q3, Q4
- `week`: Week number
- `is_weekend`: 1 if weekend, 0 if weekday

**Example:**
```
date_key | full_date  | year | month | day | quarter | week | is_weekend
20140115 | 2014-01-15 | 2014 | 1     | 15  | Q1      | 3    | 0
```

### Fact Table Explained

#### `sales_fact` (9,994 rows)
**What:** Actual sales transactions
**Columns:**
- `sales_key` (Primary Key): Auto-generated ID
- `product_key` (Foreign Key): Links to dim_product
- `customer_key` (Foreign Key): Links to dim_customer
- `location_key` (Foreign Key): Links to dim_location
- `store_key` (Foreign Key): Links to dim_store
- `date_key` (Foreign Key): Links to dim_date
- `order_date`: When order was placed
- `ship_date`: When order was shipped
- `sales`: Dollar amount
- `quantity`: Number of items
- `discount`: Discount applied
- `profit`: Profit earned
- `revenue`: Total revenue

**Example:**
```
sales_key | product_key | customer_key | ... | sales  | quantity | profit
1         | 1           | 1            | ... | 50.25  | 2        | 15.50
2         | 5           | 3            | ... | 120.00 | 1        | 45.00
```

**Foreign Keys Explained:**
- Instead of storing "Staples" in every row, we store `product_key = 1`
- This links to `dim_product` where `product_id = 1`
- Saves space, ensures consistency

### The ETL Process Step-by-Step

#### Step 1: Extract (Read CSV)

**File:** `etl/transformations.py`

```python
def load_csv(spark, path):
    """Read CSV file into Spark DataFrame"""
    df = spark.read.csv(path, header=True, inferSchema=True)
    return df
```

**What happens:**
- Spark reads `superstore.csv`
- Creates a DataFrame (table-like structure)
- All columns initially treated as strings

**Result:** 9,994 rows loaded into memory

#### Step 2: Transform - Type Casting

**File:** `etl/transformations.py`

```python
def apply_type_casting(df):
    """Convert string columns to proper types"""
    from pyspark.sql.functions import col, try_cast
    
    df = df.withColumn("Sales", try_cast(col("Sales").cast("double")))
    df = df.withColumn("Quantity", try_cast(col("Quantity").cast("int")))
    df = df.withColumn("Discount", try_cast(col("Discount").cast("double")))
    df = df.withColumn("Profit", try_cast(col("Profit").cast("double")))
    
    return df
```

**Why `try_cast` instead of `cast`?**
- `cast("50.25" as double)` → 50.25 ✓
- `cast("invalid" as double)` → ERROR ❌
- `try_cast("50.25" as double)` → 50.25 ✓
- `try_cast("invalid" as double)` → NULL ✓ (doesn't crash)

**Result:** Numeric columns are now actual numbers, invalid values become NULL

#### Step 3: Transform - Date Parsing

**File:** `etl/transformations.py`

```python
def standardize_dates(df, columns):
    """Parse dates in multiple formats"""
    from pyspark.sql.functions import coalesce, try_to_date
    
    # Try 7 different date formats
    df = df.withColumn("order_date", 
        coalesce(
            try_to_date(col("Order_Date"), "MM/dd/yyyy"),
            try_to_date(col("Order_Date"), "yyyy-MM-dd"),
            try_to_date(col("Order_Date"), "MMM dd yyyy"),
            # ... 4 more formats
        )
    )
    return df
```

**Why multiple formats?**
Real-world data has inconsistent dates:
- "1/15/2014" (MM/dd/yyyy)
- "2014-01-15" (yyyy-MM-dd)
- "Jan 15 2014" (MMM dd yyyy)

**How `coalesce` works:**
```
coalesce(format1, format2, format3)
= Try format1, if NULL try format2, if NULL try format3
```

**Result:** All dates parsed successfully (100% success rate)

#### Step 4: Transform - Deduplication

**File:** `etl/transformations.py`

```python
def deduplicate(df, keys):
    """Remove duplicate rows"""
    df = df.dropDuplicates(keys)
    return df
```

**What it checks:**
- Looks for rows with same business key (e.g., Order_ID + Product_ID)
- Keeps first occurrence, removes duplicates

**Result:** Clean data with no duplicates

#### Step 5: Load Dimensions

**File:** `etl/dimension_loader.py`

```python
def load_dimension(df, table_name, jdbc_url, properties):
    """Load a dimension table"""
    
    # 1. Extract unique values
    unique_df = df.select(columns).distinct()
    
    # 2. Truncate table (clear existing data)
    truncate_table(table_name)
    
    # 3. Write to MySQL (single partition to avoid race conditions)
    unique_df.coalesce(1).write.jdbc(
        url=jdbc_url,
        table=table_name,
        mode="append",
        properties=properties
    )
```

**Why `coalesce(1)`?**
- Spark normally writes in parallel (multiple files)
- Small dimension tables don't need parallelism
- Single writer prevents duplicate key errors

**Result:** 5 dimension tables populated

#### Step 6: Load Fact Table

**File:** `etl/fact_loader.py`

```python
def create_fact_dataframe(clean_df, jdbc_url, properties):
    """Create fact table with foreign key lookups"""
    
    # Join with each dimension to get foreign keys
    fact_df = clean_df.alias("src")
    
    # Join with dim_product
    fact_df = fact_df.join(
        dim_product.alias("p"),
        col("src.product_id") == col("p.product_id"),
        how="left"
    ).select(
        col("p.product_key").alias("product_key"),
        # ... other columns
    )
    
    # Repeat for customer, location, store, date
    
    return fact_df
```

**What happens:**
- For each row in clean data, look up the corresponding dimension key
- Replace "OFF-AR-10002833" with `product_key = 1`
- Create final fact table with all foreign keys

**Result:** `sales_fact` table with 9,994 rows

---

## Phase 2: ML Pipeline - Deep Dive

### What is Machine Learning Forecasting?

**Goal:** Predict future values based on historical patterns.

**Example:**
```
Historical Data:          Model Learns:           Prediction:
Day 1: $1000              Pattern:                Day 8: ?
Day 2: $1200              - Weekends higher       Answer: $1150
Day 3: $900               - Mondays lower
Day 4: $1100              - Trending up
Day 5: $1300
Day 6: $1500 (weekend)
Day 7: $1400 (weekend)
```

### Time-Series Features Explained

#### Lag Features

**Concept:** Yesterday's sales predict today's sales.

```python
# Lag 1: Sales from 1 day ago
lag_1 = sales.shift(1)

# Lag 7: Sales from 7 days ago (same day last week)
lag_7 = sales.shift(7)
```

**Example:**
```
Date       | Sales | lag_1 | lag_7
2024-01-01 | 1000  | NULL  | NULL
2024-01-02 | 1200  | 1000  | NULL
2024-01-03 | 900   | 1200  | NULL
...
2024-01-08 | ?     | 1400  | 1000  # Predict using lag_1=1400, lag_7=1000
```

**Why it works:** Sales have temporal dependencies (autocorrelation)

#### Rolling Features

**Concept:** Average of recent days shows the trend.

```python
# 7-day rolling mean (average of last 7 days)
rolling_7_mean = sales.shift(1).rolling(window=7).mean()

# 30-day rolling mean (average of last 30 days)
rolling_30_mean = sales.shift(1).rolling(window=30).mean()
```

**Why `shift(1)` before rolling?**
- Prevents **data leakage** (using future information)
- At prediction time, you don't know today's sales yet
- Only use sales from BEFORE today

**Example:**
```
Date       | Sales | rolling_7_mean (shifted)
2024-01-01 | 1000  | NULL
2024-01-02 | 1200  | NULL
...
2024-01-08 | 1300  | (1000+1200+900+1100+1300+1500+1400)/7 = 1200
```

#### Date Features

**Concept:** Calendar affects sales (weekends, months, holidays).

```python
# Month of year (1-12)
month = date.month

# Day of week (0=Monday, 6=Sunday)
day_of_week = date.dayofweek

# Weekend flag (1 if Sat/Sun, 0 otherwise)
is_weekend = 1 if day_of_week >= 5 else 0
```

**Example:**
```
Date       | month | day_of_week | is_weekend
2024-01-06 | 1     | 5 (Saturday)| 1
2024-01-07 | 1     | 6 (Sunday)  | 1
2024-01-08 | 1     | 0 (Monday)  | 0
```

### Model Training Process

#### Step 1: Load Data

**File:** `ml/data_loader.py`

```python
def load_global_daily_sales(self):
    """Aggregate sales by date from MySQL"""
    
    query = """
        SELECT
            d.full_date,
            SUM(f.sales) as total_sales
        FROM sales_fact f
        JOIN dim_date d ON f.date_key = d.date_key
        GROUP BY d.full_date
        ORDER BY d.full_date
    """
    
    df = pd.read_sql_query(query, self.engine)
    return df
```

**What it does:**
- Queries Phase 1 database
- Groups all sales by date
- Returns daily totals

**Result:** 1,237 rows (one per day from 2014-2017)

#### Step 2: Create Features

**File:** `ml/feature_engineering.py`

```python
def create_features(self, df):
    """Create all ML features"""
    
    # Sort by date (critical for time-series)
    df = df.sort_values('full_date').reset_index(drop=True)
    
    # Create lag features
    df = self._create_lag_features(df)
    
    # Create rolling features
    df = self._create_rolling_features(df)
    
    # Create date features
    df = self._create_date_features(df)
    
    # Drop rows with NaN (from lag/rolling)
    df = df.dropna().reset_index(drop=True)
    
    return df
```

**Result:** 1,207 rows with 7 features each

#### Step 3: Train-Test Split

**File:** `ml/tasks/train.py`

```python
# Chronological split (NO SHUFFLE!)
split_idx = int(len(X) * 0.8)  # 80-20 split

X_train = X.iloc[:split_idx]  # First 80%
X_test = X.iloc[split_idx:]   # Last 20%
y_train = y.iloc[:split_idx]
y_test = y.iloc[split_idx:]
```

**Why chronological?**
- Time-series data has temporal order
- Can't use future data to predict past
- Random shuffle would cause **data leakage**

**Visual:**
```
2014-01-03 ────────────────────── 2017-05-15 ───────────── 2017-12-30
│                              │  │                    │
│    TRAINING SET (80%)        │  │  TEST SET (20%)    │
│    965 samples               │  │  242 samples       │
│    (past data)               │  │  (future data)     │
└──────────────────────────────┘  └────────────────────┘
```

#### Step 4: Train Models

**File:** `ml/modeling/linear_model.py` and `ml/modeling/random_forest_model.py`

**Linear Regression:**
```python
from sklearn.linear_model import LinearRegression

model = LinearRegression()
model.fit(X_train, y_train)
```

**What it learns:**
```
sales = w1*lag_1 + w2*lag_7 + w3*rolling_7_mean + ... + bias
```

**Random Forest:**
```python
from sklearn.ensemble import RandomForestRegressor

model = RandomForestRegressor(n_estimators=100)
model.fit(X_train, y_train)
```

**What it learns:**
- Multiple decision trees
- Each tree votes on prediction
- Average of votes is final prediction

#### Step 5: Evaluate Models

**File:** `ml/tasks/train.py`

```python
# Evaluate on test set
lr_metrics = lr_model.evaluate(X_test, y_test)
rf_metrics = rf_model.evaluate(X_test, y_test)

# Select best model (lowest RMSE)
if lr_metrics['rmse'] <= rf_metrics['rmse']:
    best_model = lr_model
else:
    best_model = rf_model
```

**Metrics Explained:**

| Metric | Formula | Meaning |
|--------|---------|---------|
| **MAE** | avg(|predicted - actual|) | Average error magnitude |
| **RMSE** | sqrt(avg((predicted - actual)²)) | Penalizes large errors |
| **R²** | 1 - (SS_res / SS_tot) | % of variance explained |

**Results:**
- Linear Regression: MAE=$1,695, RMSE=$2,431, R²=0.018
- Random Forest: MAE=$1,680, RMSE=$2,435, R²=0.015
- **Winner:** Linear Regression (lower RMSE)

#### Step 6: Save Model

**File:** `ml/modeling/linear_model.py`

```python
import joblib

def save(self, filepath):
    joblib.dump(self.model, filepath)
```

**Result:** `ml/models/global_best_model.pkl`

### Prediction Process

#### Recursive Forecasting

**File:** `ml/tasks/predict.py`

**Challenge:** How to predict multiple days when features depend on previous values?

**Solution:** Use each prediction as input for the next prediction.

```python
predictions = []
current_features = last_known_features

for i in range(forecast_days):
    # Make prediction
    pred = model.predict(current_features)[0]
    
    # Store prediction
    predictions.append({'date': next_date, 'sales': pred})
    
    # Update features for next iteration
    current_features['lag_7'] = current_features['lag_1']
    current_features['lag_1'] = pred  # Use prediction as next lag
    
    # Update date features
    next_date = last_date + timedelta(days=1)
    current_features['month'] = next_date.month
    current_features['day_of_week'] = next_date.dayofweek
    current_features['is_weekend'] = 1 if weekend else 0
```

**Visual:**
```
Iteration 1:
  Input: lag_1 = Day 0 sales (known)
  Output: pred_1 = Day 1 prediction
  
Iteration 2:
  Input: lag_1 = pred_1 (from Iteration 1)
  Output: pred_2 = Day 2 prediction
  
Iteration 3:
  Input: lag_1 = pred_2 (from Iteration 2)
  Output: pred_3 = Day 3 prediction
```

---

## Code Walkthrough - Every File Explained

### Phase 1 Files

#### `phases/phase-1-etl/main.py`

**Purpose:** Main entry point - orchestrates the entire ETL pipeline

**Key Code:**
```python
def main():
    # 1. Initialize Spark session
    spark = create_spark_session()
    
    # 2. Initialize database (create tables)
    init_database()
    
    # 3. Load and transform data
    raw_df = load_csv(spark, DATA_PATH)
    clean_df = transform_data(raw_df)
    
    # 4. Load dimension tables
    load_dimensions(clean_df)
    
    # 5. Load fact table
    load_fact(clean_df)
    
    # 6. Verify results
    verify_results()
```

**Execution Flow:**
1. User runs: `python main.py`
2. Spark session created
3. Database initialized
4. CSV loaded and cleaned
5. Dimensions loaded
6. Fact table loaded
7. Results verified

#### `phases/phase-1-etl/etl/transformations.py`

**Purpose:** All data cleaning and transformation logic

**Key Classes/Functions:**

```python
def load_csv(spark, path):
    """Load CSV into Spark DataFrame"""
    return spark.read.csv(path, header=True, inferSchema=True)

def apply_type_casting(df):
    """Convert strings to proper types using try_cast"""
    # Uses try_cast to handle invalid values gracefully

def standardize_dates(df, columns):
    """Parse dates in 7 different formats"""
    # Uses coalesce to try multiple formats

def deduplicate(df, keys):
    """Remove duplicate rows"""
    return df.dropDuplicates(keys)

def create_derived_fields(df):
    """Add year, month, day, is_weekend columns"""
    # Extracts date parts for analytics
```

#### `phases/phase-1-etl/etl/dimension_loader.py`

**Purpose:** Load dimension tables into MySQL

**Key Functions:**

```python
def load_dimension(df, table_name, jdbc_url, properties):
    """Generic dimension loader"""
    # 1. Extract unique values
    # 2. Truncate table
    # 3. Write with coalesce(1)

def load_product_dimension(df, jdbc_url, properties):
    """Load dim_product"""
    unique_df = df.select("product_id", "product_name", ...).distinct()
    load_dimension(unique_df, "dim_product", ...)

def load_customer_dimension(df, jdbc_url, properties):
    """Load dim_customer"""
    # Similar pattern for each dimension
```

#### `phases/phase-1-etl/etl/fact_loader.py`

**Purpose:** Load fact table with foreign key lookups

**Key Functions:**

```python
def create_fact_dataframe(clean_df, jdbc_url, properties):
    """Join with all dimensions to get foreign keys"""
    # LEFT JOIN with each dimension
    # Ensures all rows kept even if FK not found

def load_fact_table(fact_df, jdbc_url, properties):
    """Write fact table to MySQL"""
    fact_df.coalesce(1).write.jdbc(...)
```

#### `phases/phase-1-etl/warehouse/init_db.py`

**Purpose:** Initialize database schema

**Key Functions:**

```python
def init_database():
    """Create database and tables"""
    # 1. Connect to MySQL
    # 2. SET FOREIGN_KEY_CHECKS=0 (allow truncation)
    # 3. TRUNCATE all tables
    # 4. SET FOREIGN_KEY_CHECKS=1
    # 5. Execute schema.sql

def truncate_tables():
    """Clear existing data"""
    # Truncates in correct order (fact first, then dimensions)
```

#### `phases/phase-1-etl/warehouse/schema.sql`

**Purpose:** SQL DDL statements to create tables

**Example:**
```sql
CREATE TABLE dim_product (
    product_key INT AUTO_INCREMENT PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL,
    product_name VARCHAR(255),
    category VARCHAR(100),
    sub_category VARCHAR(100)
);

CREATE TABLE sales_fact (
    sales_key INT AUTO_INCREMENT PRIMARY KEY,
    product_key INT,
    customer_key INT,
    location_key INT,
    store_key INT,
    date_key INT,
    sales DOUBLE NOT NULL,
    quantity DOUBLE,
    discount DOUBLE,
    profit DOUBLE,
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    ...
);
```

#### `phases/phase-1-etl/config/config.py`

**Purpose:** Centralized configuration

**Key Settings:**

```python
# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "port": "3306",
    "database": "retail_db",
    "user": "root",
    "password": "root"
}

# Spark configuration
SPARK_CONFIG = {
    "appName": "RetailAnalyticsETL",
    "master": "local[*]",
    "executorMemory": "2g",
    "driverMemory": "2g"
}

# File paths
DATA_PATH = "data/superstore.csv"
LOG_PATH = "logs/etl_pipeline.log"
JAR_PATH = "jars/mysql-connector-j-9.6.0.jar"
```

### Phase 2 Files

#### `phases/phase-2-ml/ml/main.py`

**Purpose:** CLI entry point with Typer

**Key Code:**

```python
import typer

app = typer.Typer()

@app.command()
def train(model_type: str = "global"):
    """Train ML models"""
    result = train_global_model()

@app.command()
def evaluate(model_type: str = "global"):
    """Evaluate trained model"""
    result = evaluate_global_model()

@app.command()
def predict(model_type: str = "global", days: int = 7):
    """Generate forecasts"""
    result = predict_global_sales(forecast_days=days)
```

**Usage:**
```bash
python ml/main.py train global
python ml/main.py evaluate global
python ml/main.py predict global -d 7
```

#### `phases/phase-2-ml/ml/config.py`

**Purpose:** ML pipeline configuration

**Key Settings:**

```python
# Database configuration
DB_CONFIG = {
    "host": os.getenv("ML_DB_HOST", "localhost"),
    "port": int(os.getenv("ML_DB_PORT", "3306")),
    "database": os.getenv("ML_DB_NAME", "retail_db"),
    "user": os.getenv("ML_DB_USER", "root"),
    "password": os.getenv("ML_DB_PASSWORD", "root")
}

# Model configuration
MODEL_CONFIG = {
    "test_size": 0.2,  # 80-20 split
    "random_state": 42,
    "lag_features": [1, 7],
    "rolling_windows": [7, 30]
}

# Feature columns
FEATURE_COLUMNS = [
    "lag_1", "lag_7",
    "rolling_7_mean", "rolling_30_mean",
    "month", "day_of_week", "is_weekend"
]
```

#### `phases/phase-2-ml/ml/data_loader.py`

**Purpose:** Load data from MySQL

**Key Class:**

```python
class DataLoader:
    def __init__(self):
        self.connection_string = get_connection_string()
        self.engine = None
    
    def connect(self):
        """Create SQLAlchemy engine"""
        self.engine = create_engine(self.connection_string)
    
    def load_global_daily_sales(self):
        """Query and aggregate daily sales"""
        query = """
            SELECT d.full_date, SUM(f.sales) as total_sales
            FROM sales_fact f
            JOIN dim_date d ON f.date_key = d.date_key
            GROUP BY d.full_date
            ORDER BY d.full_date
        """
        df = pd.read_sql_query(query, self.engine)
        return df
    
    def disconnect(self):
        """Close connection"""
        if self.engine:
            self.engine.dispose()
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
```

#### `phases/phase-2-ml/ml/feature_engineering.py`

**Purpose:** Create ML features

**Key Class:**

```python
class FeatureEngineer:
    def __init__(self, lag_features=None, rolling_windows=None):
        self.lag_features = lag_features or [1, 7]
        self.rolling_windows = rolling_windows or [7, 30]
    
    def create_features(self, df):
        """Create all features"""
        df = df.sort_values('full_date').reset_index(drop=True)
        df = self._create_lag_features(df)
        df = self._create_rolling_features(df)
        df = self._create_date_features(df)
        df = df.dropna().reset_index(drop=True)
        return df
    
    def _create_lag_features(self, df):
        """Create lag features"""
        for lag in self.lag_features:
            df[f"lag_{lag}"] = df['total_sales'].shift(lag)
        return df
    
    def _create_rolling_features(self, df):
        """Create rolling features (on shifted data)"""
        for window in self.rolling_windows:
            df[f"rolling_{window}_mean"] = df['total_sales'].shift(1).rolling(window=window).mean()
        return df
    
    def _create_date_features(self, df):
        """Create date features"""
        df['month'] = df['full_date'].dt.month
        df['day_of_week'] = df['full_date'].dt.dayofweek
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        return df
    
    def get_feature_matrix(self, df):
        """Extract X and y"""
        X = df[FEATURE_COLUMNS].copy()
        y = df['total_sales'].copy()
        return X, y
```

#### `phases/phase-2-ml/ml/modeling/linear_model.py`

**Purpose:** Linear Regression wrapper

**Key Class:**

```python
class LinearRegressionModel:
    def __init__(self):
        self.model = LinearRegression()
        self.is_trained = False
        self.feature_names = None
    
    def train(self, X_train, y_train):
        """Train the model"""
        self.model.fit(X_train, y_train)
        self.is_trained = True
        self.feature_names = list(X_train.columns)
    
    def predict(self, X):
        """Make predictions"""
        if not self.is_trained:
            raise RuntimeError("Model must be trained first")
        return self.model.predict(X)
    
    def evaluate(self, X_test, y_test):
        """Calculate metrics"""
        predictions = self.predict(X_test)
        return {
            'mae': mean_absolute_error(y_test, predictions),
            'rmse': np.sqrt(mean_squared_error(y_test, predictions)),
            'r2': r2_score(y_test, predictions)
        }
    
    def save(self, filepath):
        """Save model to disk"""
        joblib.dump(self.model, filepath)
    
    def load(self, filepath):
        """Load model from disk"""
        self.model = joblib.load(filepath)
        self.is_trained = True
```

#### `phases/phase-2-ml/ml/modeling/random_forest_model.py`

**Purpose:** Random Forest wrapper

**Key Class:**

```python
class RandomForestModel:
    def __init__(self, n_estimators=100, random_state=42):
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            random_state=random_state
        )
        self.is_trained = False
        self.feature_names = None
    
    # Same methods as LinearRegressionModel
    # train, predict, evaluate, save, load
    
    def get_feature_importance(self):
        """Get feature importances"""
        if not self.is_trained:
            raise RuntimeError("Model must be trained first")
        return dict(zip(self.feature_names, self.model.feature_importances_))
```

#### `phases/phase-2-ml/ml/tasks/train.py`

**Purpose:** Training orchestration

**Key Function:**

```python
def train_global_model():
    """Train both models and save best"""
    
    # 1. Load data
    with DataLoader() as loader:
        df = loader.load_global_daily_sales()
    
    # 2. Create features
    engineer = FeatureEngineer()
    features_df = engineer.create_features(df)
    
    # 3. Get X and y
    X, y = engineer.get_feature_matrix(features_df)
    
    # 4. Chronological split
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    # 5. Train Linear Regression
    lr_model = LinearRegressionModel()
    lr_model.train(X_train, y_train)
    lr_metrics = lr_model.evaluate(X_test, y_test)
    
    # 6. Train Random Forest
    rf_model = RandomForestModel()
    rf_model.train(X_train, y_train)
    rf_metrics = rf_model.evaluate(X_test, y_test)
    
    # 7. Select best model
    if lr_metrics['rmse'] <= rf_metrics['rmse']:
        best_model = lr_model
        best_metrics = lr_metrics
    else:
        best_model = rf_model
        best_metrics = rf_metrics
    
    # 8. Save best model
    best_model.save(MODEL_PATH)
    
    return {
        'linear_regression': lr_metrics,
        'random_forest': rf_metrics,
        'best_model': best_metrics
    }
```

#### `phases/phase-2-ml/ml/tasks/evaluate.py`

**Purpose:** Model evaluation

**Key Function:**

```python
def evaluate_global_model(model_path=None):
    """Evaluate trained model"""
    
    # 1. Load data
    with DataLoader() as loader:
        df = loader.load_global_daily_sales()
    
    # 2. Create features
    engineer = FeatureEngineer()
    features_df = engineer.create_features(df)
    
    # 3. Get X and y
    X, y = engineer.get_feature_matrix(features_df)
    
    # 4. Load model
    model = joblib.load(model_path)
    
    # 5. Evaluate
    predictions = model.predict(X)
    metrics = {
        'mae': mean_absolute_error(y, predictions),
        'rmse': np.sqrt(mean_squared_error(y, predictions)),
        'r2': r2_score(y, predictions)
    }
    
    return metrics
```

#### `phases/phase-2-ml/ml/tasks/predict.py`

**Purpose:** Generate forecasts

**Key Function:**

```python
def predict_global_sales(model_path=None, forecast_days=7):
    """Generate multi-day forecast"""
    
    # 1. Load historical data
    with DataLoader() as loader:
        df = loader.load_global_daily_sales()
    
    # 2. Load model
    model = joblib.load(model_path)
    
    # 3. Create features
    engineer = FeatureEngineer()
    features_df = engineer.create_features(df)
    
    # 4. Get last row for initial prediction
    last_date = df['full_date'].max()
    current_features = features_df.iloc[-1:].copy()
    
    # 5. Recursive prediction loop
    predictions = []
    for i in range(forecast_days):
        # Prepare features
        X_pred = current_features[FEATURE_COLUMNS]
        
        # Predict
        pred = model.predict(X_pred)[0]
        
        # Store
        next_date = last_date + timedelta(days=i+1)
        predictions.append({'full_date': next_date, 'predicted_sales': pred})
        
        # Update features for next iteration
        current_features['lag_7'] = current_features['lag_1']
        current_features['lag_1'] = pred
        current_features['month'] = next_date.month
        current_features['day_of_week'] = next_date.dayofweek
        current_features['is_weekend'] = 1 if next_date.dayofweek >= 5 else 0
    
    return pd.DataFrame(predictions)
```

---

## How Data Flows Through the System

### Complete Data Journey

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        COMPLETE DATA FLOW                                │
└─────────────────────────────────────────────────────────────────────────┘

STEP 1: Raw Data Generation (Outside System)
─────────────────────────────────────────────
Retail stores make sales → Recorded in CSV file

File: superstore.csv
Rows: 9,994 transactions
Columns: Order_ID, Order_Date, Sales, Customer_Name, Product_Name, ...


STEP 2: Phase 1 - ETL Pipeline
───────────────────────────────

2a. Extract
───────────
Input:  superstore.csv (9,994 rows)
Action: Spark reads CSV
Output: Raw DataFrame (all STRING columns)

2b. Transform
─────────────
Input:  Raw DataFrame
Action: - try_cast() for numerics
        - Multi-format date parsing
        - Deduplication
        - Create derived fields
Output: Clean DataFrame (typed columns)

2c. Load Dimensions
───────────────────
Input:  Clean DataFrame
Action: - Extract unique products → dim_product (1,862 rows)
        - Extract unique customers → dim_customer (793 rows)
        - Extract unique locations → dim_location (632 rows)
        - Create stores → dim_store (5 rows)
        - Generate dates → dim_date (1,458 rows)
Output: 5 dimension tables in MySQL

2d. Load Fact
─────────────
Input:  Clean DataFrame + dimension tables
Action: - JOIN with each dimension to get FKs
        - Write to sales_fact
Output: sales_fact (9,994 rows) in MySQL


STEP 3: Phase 2 - ML Pipeline
──────────────────────────────

3a. Extract
───────────
Input:  sales_fact + dim_date from MySQL
Action: SELECT DATE, SUM(sales) GROUP BY DATE
Output: Daily sales DataFrame (1,237 rows)

3b. Transform (Feature Engineering)
───────────────────────────────────
Input:  Daily sales DataFrame
Action: - Create lag_1, lag_7
        - Create rolling_7_mean, rolling_30_mean
        - Create month, day_of_week, is_weekend
Output: Features DataFrame (1,207 rows, 7 features)

3c. Train
─────────
Input:  Features DataFrame
Action: - Chronological 80-20 split
        - Train Linear Regression
        - Train Random Forest
        - Select best by RMSE
Output: global_best_model.pkl

3d. Predict
───────────
Input:  Trained model + historical features
Action: - Recursive multi-day forecasting
        - Update lag features with each prediction
Output: N-day forecast table


STEP 4: Results
───────────────
Console Output:
- Training metrics (MAE, RMSE, R²)
- Forecast table with dates and predicted sales

Files Created:
- ml/models/global_best_model.pkl (trained model)
- ml/logs/ml_pipeline_*.log (execution logs)
```

### Data State at Each Stage

| Stage | Format | Rows | Columns | Storage |
|-------|--------|------|---------|---------|
| Raw CSV | CSV file | 9,994 | 21 | File system |
| After Extract | Spark DF | 9,994 | 21 (all STRING) | Memory |
| After Transform | Spark DF | 9,994 | 21 (typed) | Memory |
| dim_product | MySQL table | 1,862 | 4 | MySQL |
| dim_customer | MySQL table | 793 | 3 | MySQL |
| dim_location | MySQL table | 632 | 5 | MySQL |
| dim_store | MySQL table | 5 | 2 | MySQL |
| dim_date | MySQL table | 1,458 | 8 | MySQL |
| sales_fact | MySQL table | 9,994 | 13 | MySQL |
| Daily sales | pandas DF | 1,237 | 2 | Memory |
| Features | pandas DF | 1,207 | 8 | Memory |
| Model | pickle file | N/A | N/A | File system |
| Forecast | pandas DF | N (user-specified) | 2 | Memory/Console |

---

## Running the Project Step-by-Step

### Step 1: Prerequisites Installation

```bash
# Install Python 3.8+ (if not installed)
# Download from python.org

# Install Docker Desktop (if not installed)
# Download from docker.com

# Verify installations
python --version
docker --version
```

### Step 2: Clone/Download Project

```bash
# Navigate to project directory
cd c:\Users\pawan\Desktop\RetailAnalyticsProject
```

### Step 3: Start MySQL Database

```bash
# Start MySQL container
docker run -d --name mysql_retail ^
  -e MYSQL_ROOT_PASSWORD=root ^
  -e MYSQL_DATABASE=retail_db ^
  -p 3306:3306 ^
  mysql:8.0

# Verify it's running
docker ps | findstr mysql_retail

# Test connection
docker exec mysql_retail mysql -uroot -proot -e "SELECT 1"
```

### Step 4: Install Phase 1 Dependencies

```bash
cd phases/phase-1-etl
pip install -r requirements.txt
```

**What gets installed:**
- `pyspark>=3.4.0` - Apache Spark Python API
- `mysql-connector-python>=8.0.0` - MySQL driver

### Step 5: Place Data File

```bash
# Ensure superstore.csv exists at:
# phases/phase-1-etl\data\superstore.csv
```

### Step 6: Run Phase 1 ETL

```bash
cd phases/phase-1-etl
python main.py
```

**Expected Output:**
```
2026-03-03 19:09:28 - INFO - RETAIL ANALYTICS ETL PIPELINE
2026-03-03 19:09:28 - INFO - Initializing database schema...
2026-03-03 19:09:29 - INFO - Schema creation completed successfully!
2026-03-03 19:09:50 - INFO - Loading CSV...
2026-03-03 19:09:55 - INFO - Loaded 9994 rows
2026-03-03 19:10:02 - INFO - Transformation complete
2026-03-03 19:10:10 - INFO - dim_product loaded with 1862 rows
2026-03-03 19:10:13 - INFO - dim_customer loaded with 793 rows
2026-03-03 19:10:15 - INFO - dim_location loaded with 632 rows
2026-03-03 19:10:15 - INFO - dim_store loaded with 5 rows
2026-03-03 19:10:19 - INFO - dim_date loaded with 1458 rows
2026-03-03 19:10:41 - INFO - sales_fact loaded with 9994 rows
2026-03-03 19:10:43 - INFO - PIPELINE COMPLETED SUCCESSFULLY!
```

### Step 7: Verify Phase 1 Results

```bash
# Connect to MySQL
docker exec -it mysql_retail mysql -uroot -proot retail_db

# Run verification queries
SELECT COUNT(*) FROM dim_product;   -- Should be 1862
SELECT COUNT(*) FROM dim_customer;  -- Should be 793
SELECT COUNT(*) FROM dim_location;  -- Should be 632
SELECT COUNT(*) FROM dim_store;     -- Should be 5
SELECT COUNT(*) FROM dim_date;      -- Should be 1458
SELECT COUNT(*) FROM sales_fact;    -- Should be 9994

# Exit MySQL
exit;
```

### Step 8: Install Phase 2 Dependencies

```bash
cd phases/phase-2-ml
pip install -r requirements.txt
```

**What gets installed:**
- `scikit-learn>=1.3.0` - Machine learning library
- `pandas>=2.0.0` - Data manipulation
- `numpy>=1.24.0` - Numerical computing
- `sqlalchemy>=2.0.0` - Database connectivity
- `pymysql>=1.1.0` - MySQL driver
- `typer>=0.9.0` - CLI framework
- `joblib>=1.3.0` - Model persistence

### Step 9: Run Phase 2 Training

```bash
cd phases/phase-2-ml
python ml/main.py train global
```

**Expected Output:**
```
============================================================
MODEL EVALUATION COMPARISON
============================================================
Model                     MAE         RMSE           R²
------------------------------------------------------------
Linear Regression      1695.27      2430.97       0.0184
Random Forest          1679.53      2435.01       0.0151
------------------------------------------------------------
BEST MODEL:            1695.27      2430.97       0.0184
============================================================

Training completed successfully!
```

### Step 10: Run Phase 2 Evaluation

```bash
python ml/main.py evaluate global
```

**Expected Output:**
```
============================================================
MODEL EVALUATION RESULTS
============================================================
Model: global_best_model.pkl
Total samples evaluated: 1207
------------------------------------------------------------
            MAE      1471.50
           RMSE      2243.83
             R²       0.0550
============================================================
```

### Step 11: Run Phase 2 Prediction

```bash
# 7-day forecast (default)
python ml/main.py predict global

# 14-day forecast
python ml/main.py predict global -d 14

# 30-day forecast with custom model
python ml/main.py predict global -d 30 -m models/my_model.pkl
```

**Expected Output:**
```
============================================================
SALES FORECAST PREDICTIONS
============================================================
Model: global_best_model.pkl
Forecast Period: 14 days
Base Date: 2017-12-30
------------------------------------------------------------
Date                 Predicted Sales
------------------------------------------------------------
2017-12-31                 $2,301.95
2018-01-01                 $2,377.10
2018-01-02                 $1,094.03
...
============================================================
```

---

## Common Questions & Troubleshooting

### FAQ

**Q: Why use PySpark instead of pandas?**
A: PySpark can handle much larger datasets (millions/billions of rows) by distributing computation. Pandas loads everything into memory. This project uses PySpark for Phase 1 (ETL) to demonstrate production-grade practices.

**Q: Why is R² so low (0.018)?**
A: The baseline model uses only 7 time-series features. Retail sales have many drivers (holidays, promotions, weather) not included. This is expected for a simple model. See `docs/phase-2/problems_faced.md` for improvement strategies.

**Q: Can I use my own data?**
A: Yes! Your CSV should have similar columns: Order_ID, Order_Date, Sales, Customer_Name, Product_Name, etc. Update `config/config.py` with your file path.

**Q: How do I increase Spark memory?**
A: Edit `phases/phase-1-etl/config/config.py`:
```python
SPARK_CONFIG = {
    "executorMemory": "4g",  # Increase from 2g to 4g
    "driverMemory": "4g"
}
```

**Q: Docker won't start - what do I do?**
A: 
1. Ensure virtualization is enabled in BIOS
2. Check if Hyper-V is enabled (Windows)
3. Restart Docker Desktop
4. Check Docker logs: `docker logs mysql_retail`

**Q: MySQL connection refused**
A:
1. Check if container is running: `docker ps`
2. Check port 3306 isn't in use by another MySQL
3. Try: `docker restart mysql_retail`

**Q: "Module not found" error**
A:
1. Ensure you're in the correct directory
2. Run: `pip install -r requirements.txt`
3. Check Python version: `python --version` (need 3.8+)

**Q: How do I reset the database?**
A:
```bash
docker exec mysql_retail mysql -uroot -proot -e "DROP DATABASE retail_db; CREATE DATABASE retail_db;"
```
Then re-run Phase 1 ETL.

### Error Messages and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `JDBC connection refused` | MySQL not running | `docker ps` then `docker start mysql_retail` |
| `CSV not found` | Wrong file path | Check `config.py` DATA_PATH |
| `ModuleNotFoundError: pyspark` | Dependencies not installed | `pip install -r requirements.txt` |
| `Failed to delete temp dir` | Windows file lock | Ignore - Spark cleanup issue, doesn't affect results |
| `Duplicate key violation` | Parallel writes | Already fixed with `coalesce(1)` |
| `Model file not found` | Training not run | Run `python ml/main.py train global` first |
| `No data loaded from warehouse` | Phase 1 not run | Run Phase 1 ETL first |

---

## Learning Path - What to Study Next

### If You're New to Data Engineering

**Step 1: Python Fundamentals** (2-4 weeks)
- Variables, data types, functions
- Lists, dictionaries, loops
- File I/O
- Error handling (try/except)

**Resources:**
- python.org tutorial
- Codecademy Python
- freeCodeCamp Python course

**Step 2: SQL Basics** (2-3 weeks)
- SELECT, FROM, WHERE
- JOINs (INNER, LEFT, RIGHT)
- GROUP BY, aggregations
- Subqueries

**Resources:**
- SQLZoo
- Khan Academy SQL
- Mode Analytics SQL Tutorial

**Step 3: Databases** (2-3 weeks)
- What is a relational database?
- Primary keys, foreign keys
- Normalization
- Indexes

**Resources:**
- MySQL documentation
- "SQL in 10 Minutes a Day" book

**Step 4: Apache Spark** (4-6 weeks)
- What is distributed computing?
- RDDs vs DataFrames
- Transformations vs Actions
- Spark SQL

**Resources:**
- Spark official documentation
- "Learning Spark" book
- Databricks free courses

### If You Know Basics and Want to Master This Project

**Step 1: Deep Dive into PySpark** (2-3 weeks)
- Study `etl/transformations.py` line by line
- Understand `try_cast` vs `cast`
- Learn Spark optimization (partitioning, caching)

**Step 2: Data Warehousing Concepts** (2-3 weeks)
- Star schema vs snowflake schema
- Dimensional modeling
- Fact tables vs dimension tables
- Slowly changing dimensions

**Resources:**
- "The Data Warehouse Toolkit" book
- Kimball Group articles

**Step 3: Machine Learning Fundamentals** (4-6 weeks)
- Supervised vs unsupervised learning
- Regression vs classification
- Train-test split
- Overfitting, underfitting
- Feature engineering

**Resources:**
- Coursera ML by Andrew Ng
- "Hands-On Machine Learning" book
- scikit-learn documentation

**Step 4: Time-Series Forecasting** (3-4 weeks)
- Autocorrelation
- Lag features
- Rolling statistics
- ARIMA, Prophet, LSTM

**Resources:**
- "Forecasting: Principles and Practice" (free online book)
- Facebook Prophet documentation

### Advanced Topics to Explore

**1. Orchestration**
- Apache Airflow for scheduling
- Cron jobs
- Dependency management

**2. Cloud Deployment**
- AWS (S3, EMR, RDS)
- Azure (Data Factory, Synapse)
- GCP (BigQuery, Dataflow)

**3. Streaming**
- Kafka for real-time data
- Spark Streaming
- Real-time vs batch processing

**4. Model Deployment**
- REST APIs with Flask/FastAPI
- Model versioning (MLflow)
- A/B testing

**5. Monitoring**
- Data quality checks
- Model drift detection
- Logging and alerting

### Project Enhancement Ideas

**Beginner:**
1. Add more date formats to handle
2. Create additional features (holidays, seasons)
3. Visualize sales trends with matplotlib

**Intermediate:**
1. Add customer segmentation (clustering)
2. Implement hyperparameter tuning (GridSearchCV)
3. Add data validation (Great Expectations)

**Advanced:**
1. Convert to real-time streaming
2. Deploy model as REST API
3. Add automated retraining pipeline
4. Implement CI/CD with GitHub Actions

---

## Glossary

| Term | Definition |
|------|------------|
| **Batch Processing** | Processing data in groups (batches) at scheduled intervals |
| **Data Lake** | Storage for raw data in any format |
| **Data Warehouse** | Storage for structured, processed data optimized for queries |
| **Dimension Table** | Table containing descriptive attributes (who, what, where) |
| **ETL** | Extract, Transform, Load - process of moving data |
| **Fact Table** | Table containing measurements/metrics (how much, how many) |
| **Feature Engineering** | Creating input variables for ML models |
| **Foreign Key** | Column that references primary key in another table |
| **Lag Feature** | Feature using past values (e.g., sales from 7 days ago) |
| **Primary Key** | Unique identifier for a row in a table |
| **PySpark** | Python API for Apache Spark |
| **Recursive Forecasting** | Using predictions as inputs for future predictions |
| **Rolling Window** | Moving average over a fixed number of periods |
| **Star Schema** | Database design with fact table surrounded by dimensions |
| **Time-Series** | Data points indexed in time order |
| **Train-Test Split** | Dividing data into training and evaluation sets |

---

## Conclusion

Congratulations! You've now learned about:

✅ **Data Engineering**: How to build ETL pipelines with PySpark
✅ **Data Warehousing**: Star schema design with MySQL
✅ **Machine Learning**: Time-series forecasting with scikit-learn
✅ **Production Practices**: Logging, configuration, error handling

### Next Steps

1. **Run the project yourself** - Follow the step-by-step guide
2. **Modify the code** - Change features, try different models
3. **Add new functionality** - Implement one of the enhancement ideas
4. **Share your learnings** - Write a blog post or teach someone else

### Getting Help

- **Project Documentation**: `docs/` folder
- **Phase 1 Details**: `docs/phase-1/readme_phase1.md`
- **Phase 2 Details**: `docs/phase-2/readme_phase2.md`
- **Troubleshooting**: See Common Questions section above

Happy learning! 🚀
