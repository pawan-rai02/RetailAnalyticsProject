# 🚀 Retail Analytics Data Engineering Pipeline

> **📊 END-TO-END DATA ENGINEERING SOLUTION**
> 
> A production-grade 3-phase pipeline that transforms raw retail data into actionable business intelligence. Built with **PySpark** for ETL, **MySQL** for warehousing, **scikit-learn** for forecasting, and **Matplotlib** for analytics dashboards. Processes **9,994 transactions** across **5 dimension tables**, delivers **25+ KPIs**, **7 visualizations**, and **automated PDF reports**.
> 
> **🎯 Skills Demonstrated:** PySpark | SQL | MySQL | Data Warehousing | Star Schema | ETL/ELT | Machine Learning | Time-Series Forecasting | Data Visualization | Python | scikit-learn | Matplotlib | Seaborn | Docker | CI/CD

---

## ⚡ Quick Stats (30-Second Overview)

| Metric | Value | Business Impact |
|--------|-------|-----------------|
| **Data Processed** | 9,994 transactions | 100% data retention, 0 loss |
| **Data Quality** | 7 date formats parsed | 3,850 rows saved from rejection |
| **Warehouse Tables** | 5 dimensions + 1 fact | Optimized for analytics queries |
| **ML Forecasting** | 1,237 days of data | MAE: $1,695, RMSE: $2,430 |
| **Analytics KPIs** | 31 pre-built functions | Revenue, Product, Customer, Store |
| **Visualizations** | 7 charts + PDF reports | Auto-generated for stakeholders |
| **Pipeline Duration** | ~90 seconds (Phase 1) | Production-ready performance |

---

## 🚀 Quick Start (Run in 5 Minutes)

```bash
# 1. Start MySQL
docker run -d --name mysql_retail -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=retail_db -p 3306:3306 mysql:8.0

# 2. Run Phase 1: ETL Pipeline
cd phases/phase-1-etl && pip install -r requirements.txt && python main.py

# 3. Run Phase 2: ML Forecasting
cd ../phase-2-ml && pip install -r requirements.txt && python ml/main.py train global

# 4. Run Phase 3: Analytics & Visualizations
cd ../phase-3-analytics && pip install -r requirements.txt && python main.py generate-all
```

**📄 Generated Outputs:** 7 PNG charts in `docs/images/` + PDF report in `reports/`

---

## 📋 Project Overview

### What This System Does

This pipeline extracts raw retail transaction data from CSV files, transforms it through rigorous data cleaning and standardization, and loads it into a MySQL star schema data warehouse optimized for analytics queries.

### High-Level Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   EXTRACT   │────▶│  TRANSFORM   │────▶│    LOAD     │────▶│   ANALYZE   │────▶│  VISUALIZE  │
│  CSV (9,994)│     │   PySpark    │     │   MySQL     │     │   SQL KPIs  │     │  Matplotlib │
└─────────────┘     └──────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
     Phase 1              Phase 1           Phase 1            Phase 3             Phase 3
                                              │
                                              ▼
                                         ┌─────────────┐
                                         │  FORECAST   │
                                         │   scikit    │
                                         │   learn     │
                                         └─────────────┘
                                              Phase 2
```

### Technologies Used

| Layer | Technology | Version |
|-------|------------|---------|
| **Processing Engine** | Apache Spark (PySpark) | 4.1+ |
| **Data Warehouse** | MySQL | 8.0 |
| **Machine Learning** | scikit-learn | 1.6+ |
| **Analytics Layer** | SQLAlchemy, Pandas | Latest |
| **Visualization** | Matplotlib, Seaborn | Latest |
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
| **Analytics Layer** | SQLAlchemy, Pandas | SQL-based KPI computation |
| **Visualization** | Matplotlib, Seaborn | Professional chart generation |
| **Orchestration** | Python 3.8+ | Pipeline coordination |
| **Runtime** | Docker | MySQL containerization |
| **Connectivity** | JDBC, SQLAlchemy | Database connections |
| **Logging** | Python logging | Execution tracking |
| **CLI** | argparse | User-friendly commands |

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
│   ├── phase-2/               # Phase 2 detailed docs
│   │   ├── README.md          # Full Phase 2 documentation
│   │   ├── problems_faced.md  # ML challenges & solutions
│   │   └── architecture.md    # ML pipeline architecture
│   └── phase-3/               # Phase 3 detailed docs
│       ├── architecture.md    # Analytics layer architecture
│       └── visuals/           # Generated visualization samples
│
├── phases/
│   ├── phase-1-etl/           # Phase 1: Batch ETL with PySpark
│   │   ├── main.py            # ETL orchestration
│   │   ├── etl/               # PySpark transformations
│   │   ├── warehouse/         # MySQL schema
│   │   ├── config/            # Configuration
│   │   └── data/              # Input CSV files
│   │
│   ├── phase-2-ml/            # Phase 2: ML Forecasting
│   │   ├── ml/                # ML pipeline source
│   │   │   ├── modeling/      # Model implementations
│   │   │   ├── tasks/         # Train/Evaluate/Predict
│   │   │   └── models/        # Trained model artifacts
│   │   └── requirements.txt   # ML dependencies
│   │
│   └── phase-3-analytics/     # Phase 3: Analytics & Visualization
│       ├── main.py            # CLI entry point
│       ├── analytics/         # KPI computation modules
│       │   ├── revenue.py     # Revenue analytics
│       │   ├── product.py     # Product analytics
│       │   ├── customer.py    # Customer analytics
│       │   └── store.py       # Store & region analytics
│       ├── db/                # Database layer
│       │   └── connection.py  # SQLAlchemy connection
│       ├── visualization/     # Plot generation
│       │   └── plots.py       # Matplotlib/Seaborn charts
│       └── requirements.txt   # Analytics dependencies
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

### Phase 3 – Analytics & Visualization Layer ✅

**Status:** Complete

A business intelligence analytics layer that queries the MySQL star schema using SQL, computes retail KPIs, and generates professional visualizations.

**Key Features:**
- **25+ Pre-built Analytics** across Revenue, Product, Customer, and Store domains
- **Professional Visualizations** with publication-quality styling
- **CLI Interface** for easy execution
- **Modular Architecture** with separation of concerns
- **Window Functions** for advanced analytics (MoM growth, rankings, cohorts)
- **PDF Report Generation** - Automatic analytics reports

**Analytics Modules:**

| Module | Functions | Visualizations |
|--------|-----------|----------------|
| **Revenue** | 8 functions | Monthly trend, Yearly comparison, Weekend vs Weekday |
| **Product** | 8 functions | Top products, Category contribution |
| **Customer** | 7 functions | CLV distribution, Top customers, RFM segmentation |
| **Store** | 8 functions | Store ranking, Region performance |

**Generated Visualizations:**

📊 **Monthly Revenue Trend**
```bash
python main.py revenue monthly --plot
```
![Monthly Revenue Trend](docs/images/monthly_revenue.png)
*Revenue trajectory over time showing growth patterns and seasonal trends.*

---

🏆 **Top Products by Revenue**
```bash
python main.py product top10 --plot
```
![Top Products](docs/images/top_products.png)
*Best-selling products ranked by total revenue with category breakdown.*

---

🏬 **Store Revenue Ranking**
```bash
python main.py store ranking --plot
```
![Store Ranking](docs/images/store_ranking.png)
*Store performance comparison with regional revenue distribution.*

---

👥 **Customer Lifetime Value Distribution**
```bash
python main.py customer clv --plot
```
![CLV Distribution](docs/images/clv_distribution.png)
*Customer value distribution showing segmentation and tier composition.*

---

📦 **Category Revenue Contribution**
```bash
python main.py product category --plot
```
![Category Contribution](docs/images/category_contribution.png)
*Revenue share by product category with percentage breakdown.*

---

🌟 **Top 10 Customers**
```bash
python main.py customer top10 --plot
```
![Top Customers](docs/images/top_customers.png)
*VIP customers ranked by total revenue contribution.*

---

🗺️ **Region Performance Dashboard**
```bash
python main.py store region --plot
```
![Region Performance](docs/images/region_performance.png)
*Multi-metric regional analysis including revenue, profit, and margins.*

---

**Quick Start:**
```bash
cd phases/phase-3-analytics
pip install -r requirements.txt

# List all available commands
python main.py list

# Generate documentation images
python main.py generate-static

# Generate PDF analytics report
python main.py generate-report

# Revenue analytics
python main.py revenue monthly
python main.py revenue monthly --plot

# Product analytics
python main.py product top10 --plot
python main.py product category

# Customer analytics
python main.py customer clv --plot
python main.py customer top10

# Store analytics
python main.py store ranking --plot
python main.py store region

# Run all analytics with plots
python main.py all --plot
```

**Documentation:**
- [Phase 3 Architecture](docs/phase-3/architecture.md)
- [Phase 3 README](docs/phase-3/readme_phase3.md)
- [Static Report Generation](docs/phase-3/static_report_generation.md)

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
pip install -r phases/phase-3-analytics/requirements.txt

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

# 6. Run Phase 3 Analytics
cd ../phase-3-analytics
python main.py list
python main.py revenue monthly --plot
python main.py product top10 --plot
python main.py customer clv --plot
python main.py store ranking --plot
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

### Phase 3: Analytics & Visualization

1. **Separation of concerns** - Keep SQL, analytics logic, and visualization completely separate
2. **No SQL in visualization layer** - Visualizations should only accept DataFrames
3. **Window functions are powerful** - Use for MoM growth, rankings, and cohort analysis
4. **Professional styling matters** - Invest time in making charts publication-ready
5. **CLI usability** - Make commands intuitive and provide helpful error messages
6. **Modular design** - Each analytics module should be independently testable
7. **Documentation first** - Write clear docstrings for every function

---

## 📄 License

MIT License - Feel free to use this pipeline for your projects!

---

## 👥 Author

**Retail Analytics Data Engineering Team**

Built with ❤️ using PySpark, MySQL, and extensive debugging of real-world data challenges.
