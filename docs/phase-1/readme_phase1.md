# Phase 1: Batch ETL with PySpark

## Overview

Phase 1 implements a production-grade batch ETL pipeline using **PySpark** that transforms raw retail sales data from CSV files into a MySQL star schema data warehouse. This phase demonstrates mastery of real-world data engineering challenges including data quality issues, type coercion, constraint handling, and platform-specific bugs.

### What This Pipeline Does

1. **Extract**: Reads raw retail transaction data from CSV (9,994 records)
2. **Transform**: Cleans, standardizes, and validates data with multi-format date parsing, type coercion, and null handling
3. **Load**: Populates a MySQL star schema with 5 dimension tables and 1 fact table

### Why It Matters

This pipeline solves authentic data engineering problems that occur in production environments:
- Inconsistent date formats causing 38.5% data loss risk
- Windows-specific Spark socket handling bugs
- Spark 4.x strict ANSI SQL type compliance
- Race conditions in parallel JDBC writes
- Foreign key constraint management during ETL resets

---

## 📁 Project Structure

```
RetailAnalyticsProject/
│
├── data/                    # Raw input CSV files
│   └── superstore.csv       # 9,994 retail transactions
├── etl/                     # PySpark ETL transformation modules
│   ├── __init__.py
│   ├── transformations.py   # Data cleaning & transformation
│   ├── dimension_loader.py  # Dimension table loaders
│   └── fact_loader.py       # Fact table loader
├── warehouse/               # MySQL DDL scripts
│   ├── schema.sql           # Star schema DDL
│   └── init_db.py           # Database initialization
├── config/                  # Configuration files
│   └── config.py            # DB credentials, Spark settings
├── logs/                    # Pipeline execution logs
│   └── etl_pipeline.log     # Detailed execution logs
├── jars/                    # JDBC drivers
│   └── mysql-connector-j-9.6.0.jar
├── main.py                  # Main orchestration script
└── requirements.txt         # Python dependencies
```

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

## 🏗️ Star Schema Design

### Dimension Tables

| Table | Description | Rows |
|-------|-------------|------|
| `dim_product` | Product master (ID, Category, Sub-Category, Name) | 1,862 |
| `dim_customer` | Customer master (ID, Name, Segment) | 793 |
| `dim_location` | Geographic hierarchy (Country, State, City, Region) | 632 |
| `dim_store` | Synthetic stores (Store_1 to Store_5) | 5 |
| `dim_date` | Date dimension with time intelligence | 1,458 |

### Fact Table

| Table | Description | Rows |
|-------|-------------|------|
| `sales_fact` | Transactional sales with FKs to all dimensions | **9,994** |

---

## 🎯 Final Results

| Metric | Value |
|--------|-------|
| **Total Rows Processed** | 9,994 |
| **Fact Table Rows** | 9,994 (100% retention) |
| **Date Parsing Success** | 100% |
| **Pipeline Duration** | ~90 seconds |
| **Data Quality Issues Resolved** | 3,850 rows saved |

---

## 🔥 Challenges Summary

This project faced several **real-world data engineering challenges** during implementation:

| Challenge | Impact | Result |
|-----------|--------|--------|
| 📅 Date Format Chaos | 38.5% data loss risk | ✅ 100% parsing success |
| 🪟 Windows Spark Worker Crashes | Pipeline failures | ✅ Stable execution |
| 🔢 Spark 4.x Strict Type Casting | Job failures | ✅ Zero errors |
| 🔑 Duplicate Key Violations | Intermittent failures | ✅ Clean loads |
| 🔗 Foreign Key Constraints | Cannot reset DB | ✅ Idempotent runs |
| 📊 NULL Foreign Keys | Data loss risk | ✅ 100% retention |
| 🗄️ NOT NULL Violations | Rows rejected | ✅ All rows loaded |

For detailed explanations of each challenge, root cause analysis, and the solutions implemented, see **[Problems Faced](problems_faced.md)**.

---

## 🛠️ Architecture Summary

The pipeline follows a classic **Extract-Transform-Load (ETL)** pattern with the following data flow:

```
┌─────────────┐     ┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│  CSV File   │────▶│  Transformations│────▶│  Dimensions  │────▶│  Fact Table │
│  (9,994)    │     │  - Date parsing │     │  (5 tables)  │     │  (9,994)    │
│             │     │  - Type casting │     │              │     │             │
└─────────────┘     │  - Deduplication│     └──────────────┘     └──────┬──────┘
                    └─────────────────┘                                 │
                                                                        ▼
                                                               ┌─────────────┐
                                                               │   MySQL     │
                                                               │ Star Schema │
                                                               └─────────────┘
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Pure Spark writes | Avoids Windows Python worker crashes |
| try_cast() for numerics | Tolerates malformed CSV data |
| Single-partition writes | Prevents duplicate key violations |
| Truncate before load | Ensures idempotent pipeline |
| NULLable date columns | Preserves rows with quality issues |
| Explicit type casting | Spark 4.x strict ANSI compliance |

For complete architecture documentation including component design, data flow diagrams, and execution flow, see **[Architecture Details](architecture.md)**.

---

## 📝 Configuration

Edit `config/config.py` to customize:

```python
DB_CONFIG = {
    "host": "localhost",
    "port": "3306",
    "database": "retail_db",
    "user": "root",
    "password": "root"
}

SPARK_CONFIG = {
    "appName": "RetailAnalyticsETL",
    "master": "local[*]",
    "executorMemory": "2g",
    "driverMemory": "2g"
}
```

---

## 📊 Output

After successful execution:

- ✅ All 5 dimension tables populated
- ✅ Fact table with **9,994 sales records** (100% retention)
- ✅ Comprehensive logs in `logs/etl_pipeline.log`
- ✅ Verified foreign key relationships

---

## 🐛 Troubleshooting

### JDBC Connection Error
```bash
# Ensure MySQL is running
docker ps | grep mysql_retail

# Test connection
docker exec retail-mysql mysql -uroot -proot -e "SELECT 1"
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

### Date Parsing Issues
```
Check logs for "Failed to parse (null)" messages
Add new date formats to transformations.py standardize_dates()
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

## 🔗 Related Documentation

- [Problems Faced](problems_faced.md) - Deep dive into challenges and solutions
- [Architecture Details](architecture.md) - Technical architecture and data flow

---

## 📄 License

MIT License - Feel free to use this pipeline for your projects!
