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
| **Orchestration** | Python 3.8+ | Pipeline coordination |
| **Runtime** | Docker | MySQL containerization |
| **Connectivity** | JDBC | Spark-MySQL communication |
| **Logging** | Python logging | Execution tracking |

---

## 📁 Project Structure

```
RetailAnalyticsProject/
│
├── docs/                      # Documentation
│   └── phase-1/               # Phase 1 detailed docs
│       ├── README.md          # Full Phase 1 documentation
│       ├── problems_faced.md  # Challenges & solutions
│       └── architecture.md    # Technical architecture
│
├── data/                      # Raw input CSV files
├── etl/                       # PySpark ETL modules
│   ├── transformations.py     # Data cleaning & transformation
│   ├── dimension_loader.py    # Dimension table loaders
│   └── fact_loader.py         # Fact table loader
├── warehouse/                 # MySQL DDL scripts
│   ├── schema.sql             # Star schema DDL
│   └── init_db.py             # Database initialization
├── config/                    # Configuration files
│   └── config.py              # DB credentials, Spark settings
├── logs/                      # Pipeline execution logs
├── jars/                      # JDBC drivers
├── main.py                    # Main orchestration script
└── requirements.txt           # Python dependencies
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

### Phase 2 – ML Layer (Coming Soon) 🔜

**Status:** Planned

Future enhancement to add machine learning capabilities for sales forecasting and customer segmentation.

**Planned Features:**
- Sales forecasting models
- Customer segmentation analysis
- Product affinity recommendations
- Time-series anomaly detection

---

## 🎯 Key Achievements

| Metric | Value |
|--------|-------|
| **Total Rows Processed** | 9,994 |
| **Fact Table Rows** | 9,994 (100% retention) |
| **Date Parsing Success** | 100% |
| **Pipeline Duration** | ~90 seconds |
| **Data Quality Issues Resolved** | 3,850 rows saved |
| **Dimension Tables** | 5 (4,750 total rows) |
| **Foreign Key Integrity** | 100% verified |

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
pip install -r requirements.txt

# 2. Start MySQL in Docker
docker run -d --name mysql_retail \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=retail_db \
  -p 3306:3306 \
  mysql:8.0

# 3. Place dataset at data/superstore.csv

# 4. Run the pipeline
python main.py
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
Place the Superstore CSV at: data/superstore.csv
```

### Spark Memory Error
```python
# Increase memory in config/config.py
SPARK_CONFIG = {
    "executorMemory": "4g",
    "driverMemory": "4g"
}
```

---

## 📈 Lessons Learned

1. **Always use `try_cast()`** for CSV data - real-world data is dirty
2. **Never use `toPandas()`** in production Spark pipelines on Windows
3. **Single-partition writes** for small dimension tables prevent race conditions
4. **Truncate + append** is safer than upsert for batch ETL
5. **NULLable columns** > lost rows (log data quality issues, don't drop data)
6. **Spark 4.x strict typing** requires explicit casts at every stage
7. **Test with full dataset early** - sampling hides data quality issues

---

## 📄 License

MIT License - Feel free to use this pipeline for your projects!

---

## 👥 Author

**Retail Analytics Data Engineering Team**

Built with ❤️ using PySpark, MySQL, and extensive debugging of real-world data challenges.
