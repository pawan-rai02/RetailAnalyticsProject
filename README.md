# Retail Analytics Data Engineering Pipeline

A production-style Data Engineering pipeline using PySpark to load data into a MySQL star schema.

## Project Structure

```
RetailAnalyticsProject/
│
├── data/              # Raw input CSV files
├── etl/               # PySpark ETL transformation modules
│   ├── __init__.py
│   ├── transformations.py    # Data cleaning & transformation
│   ├── dimension_loader.py   # Dimension table loaders
│   └── fact_loader.py        # Fact table loader
├── warehouse/         # MySQL DDL scripts
│   ├── schema.sql            # Star schema DDL
│   └── init_db.py            # Database initialization
├── config/            # Configuration files
│   └── config.py             # DB credentials, Spark settings
├── logs/              # Pipeline execution logs
├── jars/              # JDBC drivers
├── main.py            # Main orchestration script
└── requirements.txt   # Python dependencies
```

## Prerequisites

1. **Python 3.8+**
2. **Apache Spark 3.4+** (with PySpark)
3. **MySQL 8.0** (running in Docker or locally)
4. **Docker Desktop** (for MySQL container)

## Setup Instructions

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Start MySQL in Docker

```bash
docker run -d --name mysql_retail \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=retail_db \
  -p 3306:3306 \
  mysql:8.0
```

### Step 3: Verify MySQL is Running

```bash
docker ps | grep mysql_retail
```

### Step 4: Place Dataset

Ensure the Kaggle Superstore dataset is at:
```
data/superstore.csv
```

### Step 5: Run the Pipeline

```bash
python main.py
```

## Star Schema Design

### Dimension Tables

| Table | Description | Rows |
|-------|-------------|------|
| `dim_product` | Product master (ID, Category, Sub-Category, Name) | ~100-200 |
| `dim_customer` | Customer master (ID, Name, Segment) | ~500-800 |
| `dim_location` | Geographic hierarchy (Country, State, City, Region) | ~200-300 |
| `dim_store` | Synthetic stores (Store_1 to Store_5) | 5 |
| `dim_date` | Date dimension with time intelligence | ~1000-1500 |

### Fact Table

| Table | Description | Rows |
|-------|-------------|------|
| `sales_fact` | Transactional sales with FKs to all dimensions | ~9000-10000 |

## Configuration

Edit `config/config.py` to change:
- Database credentials
- Spark settings
- File paths
- Processing options

## Output

After successful execution:
- All dimension tables populated
- Fact table with ~10,000 sales records
- Logs in `logs/etl_pipeline.log`

## Troubleshooting

### JDBC Connection Error
Ensure MySQL is running and accessible on port 3306.

### CSV Not Found
Place the Superstore CSV in the `data/` folder.

### Spark Memory Error
Increase `executorMemory` and `driverMemory` in `config/config.py`.

## Data Transformations Applied

1. **Date Standardization**: Handles MM/dd/yyyy, MM-dd-yyyy formats
2. **Synthetic Store Assignment**: Random Store_1 to Store_5
3. **Duplicate Removal**: Based on all columns
4. **Null Handling**: Categorical → "Unknown", Numeric → 0
5. **Derived Fields**: order_year, order_month, order_day, day_of_week, is_weekend, revenue

## Author

Retail Analytics Data Engineering Team
