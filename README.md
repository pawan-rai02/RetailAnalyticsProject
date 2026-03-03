# 🚀 Retail Analytics Data Engineering Pipeline

A production-grade data engineering pipeline built with **PySpark** that transforms raw retail data into a MySQL star schema data warehouse. This project demonstrates real-world ETL challenges and their solutions.

---

## 📋 Project Overview

### What This System Does

This pipeline extracts raw retail transaction data from CSV files, transforms it through rigorous data cleaning and standardization, and loads it into a MySQL star schema data warehouse optimized for analytics queries.

### High-Level Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   EXTRACT   │────▶│  TRANSFORM   │────▶│    LOAD     │
│  CSV (9,994)│     │   PySpark    │     │   MySQL     │
└─────────────┘     └──────────────┘     └─────────────┘
```

### Technologies Used

| Layer | Technology | Version |
|-------|------------|---------|
| **Processing Engine** | Apache Spark (PySpark) | 4.1+ |
| **Data Warehouse** | MySQL | 8.0 |
| **Orchestration** | Python | 3.8+ |
| **Containerization** | Docker | Latest |
| **JDBC Driver** | MySQL Connector/J | 9.6.0 |

### Why It Matters

This pipeline solves authentic production data engineering challenges:

- **Date format inconsistency** - 38.5% of rows had unparseable dates (7 different formats)
- **Windows-specific Spark bugs** - Python worker crashes during `toPandas()` conversions
- **Spark 4.x strict typing** - ANSI SQL compliance requiring explicit type casting
- **Parallel write race conditions** - Duplicate key violations during dimension loads
- **Foreign key constraint management** - Database reset complications

---

## 🏗️ Architecture Summary

The pipeline follows a classic **Extract-Transform-Load (ETL)** pattern:

1. **Extract**: Read raw CSV data (9,994 retail transactions)
2. **Transform**: Apply type casting, multi-format date parsing, deduplication
3. **Load**: Populate 5 dimension tables + 1 fact table in MySQL star schema

### Star Schema Design

| Table Type | Tables | Total Rows |
|------------|--------|------------|
| **Dimensions** | `dim_product`, `dim_customer`, `dim_location`, `dim_store`, `dim_date` | 4,750 |
| **Fact** | `sales_fact` | **9,994** |

For detailed architecture documentation, see [docs/phase-1/architecture.md](docs/phase-1/architecture.md).

---

## 🛠️ Tech Stack Summary

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Data Processing** | PySpark 4.1 | Distributed ETL transformations |
| **Data Warehouse** | MySQL 8.0 | Star schema storage |
| **Machine Learning** | scikit-learn 1.6+ | Time-series forecasting |
| **Orchestration** | Python 3.8+ | Pipeline coordination |
| **Runtime** | Docker | MySQL containerization |
| **Connectivity** | JDBC, SQLAlchemy | Database connections |
| **Logging** | Python logging | Execution tracking |
| **CLI** | Typer | User-friendly commands |

---

## 📁 Project Structure

```
RetailAnalyticsProject/
│
├── docs/                      # Documentation
│   ├── phase-1/               # Phase 1 detailed docs
│   │   ├── README.md          # Full Phase 1 documentation
│   │   ├── problems_faced.md  # Challenges & solutions
│   │   └── architecture.md    # Technical architecture
│   └── phase-2/               # Phase 2 detailed docs
│       ├── README.md          # Full Phase 2 documentation
│       ├── problems_faced.md  # ML challenges & solutions
│       └── architecture.md    # ML pipeline architecture
│
├── phases/
│   ├── phase-1-etl/           # Phase 1: Batch ETL with PySpark
│   │   ├── main.py            # ETL orchestration
│   │   ├── etl/               # PySpark transformations
│   │   ├── warehouse/         # MySQL schema
│   │   └── config/            # Configuration
│   └── phase-2-ml/            # Phase 2: ML Forecasting
│       ├── ml/                # ML pipeline source
│       │   ├── modeling/      # Model implementations
│       │   ├── tasks/         # Train/Evaluate/Predict
│       │   └── models/        # Trained model artifacts
│       └── requirements.txt   # ML dependencies
│
├── data/                      # Raw input CSV files
└── jars/                      # JDBC drivers
```

---

## 📊 Project Phases

### Phase 1 – Batch ETL with PySpark ✅

**Status:** Complete

A production-grade batch ETL pipeline that processes 9,994 retail transactions through PySpark transformations into a MySQL star schema.

**Key Metrics:**
- **Total Rows Processed:** 9,994
- **Fact Table Retention:** 100% (zero data loss)
- **Date Parsing Success:** 100% (7 formats handled)
- **Pipeline Duration:** ~90 seconds
- **Data Quality Issues Resolved:** 3,850 rows saved

**Documentation:**
- [Full Phase 1 Details](docs/phase-1/readme_phase1.md)
- [Problems & Solutions](docs/phase-1/problems_faced.md)
- [Architecture Deep Dive](docs/phase-1/architecture.md)

---

### Phase 2 – ML Forecasting Layer ✅

**Status:** Complete

A machine learning pipeline that builds on the Phase 1 data warehouse to forecast future daily sales using time-series features.

**Key Metrics:**
- **Data Loaded:** 1,237 days of sales (2014-2017)
- **Training Samples:** 965 days (80%)
- **Test Samples:** 242 days (20%)
- **Best Model:** Linear Regression
- **MAE:** $1,695.27
- **RMSE:** $2,430.97
- **R²:** 0.0184

**Features:**
- Time-series feature engineering (lag, rolling, date features)
- Chronological train-test split (no data leakage)
- Model comparison (Linear Regression vs Random Forest)
- Recursive multi-day forecasting
- CLI interface for train/evaluate/predict

**Documentation:**
- [Full Phase 2 Details](docs/phase-2/readme_phase2.md)
- [ML Challenges & Solutions](docs/phase-2/problems_faced.md)
- [ML Pipeline Architecture](docs/phase-2/architecture.md)

**Quick Start:**
```bash
cd phases/phase-2-ml
pip install -r requirements.txt

# Train models
python ml/main.py train global

# Evaluate
python ml/main.py evaluate global

# Forecast 7 days
python ml/main.py predict global -d 7
```

---

## 🎯 Key Achievements

### Phase 1: ETL Pipeline

| Metric | Value |
|--------|-------|
| **Total Rows Processed** | 9,994 |
| **Fact Table Rows** | 9,994 (100% retention) |
| **Date Parsing Success** | 100% |
| **Pipeline Duration** | ~90 seconds |
| **Data Quality Issues Resolved** | 3,850 rows saved |
| **Dimension Tables** | 5 (4,750 total rows) |
| **Foreign Key Integrity** | 100% verified |

### Phase 2: ML Forecasting

| Metric | Value |
|--------|-------|
| **Days of Data** | 1,237 (2014-2017) |
| **Features Engineered** | 7 (lag, rolling, date) |
| **Models Trained** | 2 (Linear Regression, Random Forest) |
| **Best Model** | Linear Regression |
| **MAE** | $1,695.27 |
| **RMSE** | $2,430.97 |
| **Training Time** | ~1.5 seconds |

---

## ⚡ Quick Start

### Prerequisites

- **Python 3.8+**
- **Apache Spark 4.1+** (with PySpark)
- **MySQL 8.0** (running in Docker)
- **Docker Desktop**

### Setup

```bash
# 1. Install dependencies
pip install -r phases/phase-1-etl/requirements.txt
pip install -r phases/phase-2-ml/requirements.txt

# 2. Start MySQL in Docker
docker run -d --name mysql_retail \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=retail_db \
  -p 3306:3306 \
  mysql:8.0

# 3. Place dataset at phases/phase-1-etl/data/superstore.csv

# 4. Run Phase 1 ETL pipeline
cd phases/phase-1-etl
python main.py

# 5. Run Phase 2 ML pipeline
cd ../phase-2-ml
python ml/main.py train global
python ml/main.py evaluate global
python ml/main.py predict global -d 7
```

---

## 🐛 Troubleshooting

### JDBC Connection Error
```bash
# Ensure MySQL is running
docker ps | grep mysql_retail

# Test connection
docker exec mysql_retail mysql -uroot -proot -e "SELECT 1"
```

### CSV Not Found
```
Place the Superstore CSV at: phases/phase-1-etl/data/superstore.csv
```

### Spark Memory Error
```python
# Increase memory in phases/phase-1-etl/config/config.py
SPARK_CONFIG = {
    "executorMemory": "4g",
    "driverMemory": "4g"
}
```

### ML Model Not Found
```
Error: Model file not found
Solution: Run Phase 1 ETL first, then run:
  cd phases/phase-2-ml
  python ml/main.py train global
```

---

## 📈 Lessons Learned

### Phase 1: ETL

1. **Always use `try_cast()`** for CSV data - real-world data is dirty
2. **Never use `toPandas()`** in production Spark pipelines on Windows
3. **Single-partition writes** for small dimension tables prevent race conditions
4. **Truncate + append** is safer than upsert for batch ETL
5. **NULLable columns** > lost rows (log data quality issues, don't drop data)
6. **Spark 4.x strict typing** requires explicit casts at every stage
7. **Test with full dataset early** - sampling hides data quality issues

### Phase 2: ML

1. **Chronological splits are critical** - Random shuffle causes data leakage in time-series
2. **Shift before rolling** - Prevents future data from leaking into features
3. **Recursive prediction complexity** - Each prediction compounds errors
4. **Feature importance > accuracy** - Linear models provide interpretable coefficients
5. **Baseline first** - Start simple (Linear Regression) before complex models
6. **Data quality matters** - Phase 1 ETL quality directly impacts ML performance

---

## 📄 License

MIT License - Feel free to use this pipeline for your projects!

---

## 👥 Author

**Retail Analytics Data Engineering Team**

Built with ❤️ using PySpark, MySQL, and extensive debugging of real-world data challenges.
