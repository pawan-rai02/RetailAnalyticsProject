# Phase 1: Architecture & Data Flow

This document details the technical architecture, component design, and data flow of the Phase 1 Batch ETL Pipeline.

---

## Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [Component Overview](#component-overview)
3. [Data Flow](#data-flow)
4. [ETL Module Design](#etl-module-design)
5. [Database Schema](#database-schema)
6. [Configuration Management](#configuration-management)
7. [Execution Flow](#execution-flow)

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        RETAIL ANALYTICS PIPELINE                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │    EXTRACT   │────▶│  TRANSFORM   │────▶│     LOAD     │            │
│  │              │     │              │     │              │            │
│  │  CSV Source  │     │   PySpark    │     │    MySQL     │            │
│  │  (9,994)     │     │  Processing  │     │  Star Schema │            │
│  └──────────────┘     └──────────────┘     └──────────────┘            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Architecture Layers

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Source** | CSV File | Raw retail transaction data |
| **Processing** | Apache Spark 4.1 | Distributed data transformation |
| **Storage** | MySQL 8.0 | Star schema data warehouse |
| **Orchestration** | Python (main.py) | Pipeline coordination |
| **Configuration** | Python (config.py) | Environment settings |

---

## Component Overview

### Directory Structure

```
RetailAnalyticsProject/
│
├── data/                          # Source data layer
│   └── superstore.csv             # 9,994 retail transactions
│
├── etl/                           # ETL processing layer
│   ├── __init__.py                # Package initialization
│   ├── transformations.py         # Data cleaning & transformation logic
│   ├── dimension_loader.py        # Dimension table loading logic
│   └── fact_loader.py             # Fact table loading logic
│
├── warehouse/                     # Data warehouse layer
│   ├── schema.sql                 # Star schema DDL definitions
│   └── init_db.py                 # Database initialization & reset
│
├── config/                        # Configuration layer
│   └── config.py                  # Database & Spark configuration
│
├── logs/                          # Observability layer
│   └── etl_pipeline.log           # Execution logs
│
├── jars/                          # Driver layer
│   └── mysql-connector-j-9.6.0.jar # MySQL JDBC driver
│
├── main.py                        # Orchestration entry point
└── requirements.txt               # Python dependencies
```

### Component Responsibilities

| Component | Responsibility |
|-----------|----------------|
| `main.py` | Orchestrates ETL pipeline execution |
| `transformations.py` | Data cleaning, type casting, date parsing |
| `dimension_loader.py` | Loads 5 dimension tables |
| `fact_loader.py` | Loads fact table with FK relationships |
| `schema.sql` | Defines MySQL star schema DDL |
| `init_db.py` | Initializes/resets database state |
| `config.py` | Centralized configuration management |

---

## Data Flow

### Complete Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA FLOW DIAGRAM                               │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────┐
                              │   CSV File      │
                              │ superstore.csv  │
                              │ (9,994 rows)    │
                              └────────┬────────┘
                                       │
                                       │ Spark reads CSV
                                       ▼
                              ┌─────────────────┐
                              │  Raw DataFrame  │
                              │ (all STRING     │
                              │  columns)       │
                              └────────┬────────┘
                                       │
                                       │ transformations.py
                                       │ - try_cast() numerics
                                       │ - multi-format dates
                                       │ - deduplication
                                       ▼
                              ┌─────────────────┐
                              │ Clean DataFrame │
                              │ (typed columns) │
                              └────────┬────────┘
                                       │
                     ┌─────────────────┼─────────────────┐
                     │                 │                 │
                     ▼                 ▼                 ▼
            ┌────────────────┐ ┌──────────────┐ ┌────────────────┐
            │ dim_product    │ │ dim_customer │ │ dim_location   │
            │ 1,862 rows     │ │ 793 rows     │ │ 632 rows       │
            └───────┬────────┘ └──────┬───────┘ └───────┬────────┘
                    │                 │                 │
            ┌───────▼─────────────────▼─────────────────▼───────┐
            │              dim_store     dim_date               │
            │              5 rows      1,458 rows               │
            └───────────────────────┬───────────────────────────┘
                                    │
                                    │ All dimensions loaded
                                    ▼
                              ┌─────────────────┐
                              │  Join to create │
                              │   fact DataFrame│
                              └────────┬────────┘
                                       │
                                       │ fact_loader.py
                                       │ - FK resolution
                                       │ - type enforcement
                                       ▼
                              ┌─────────────────┐
                              │   sales_fact    │
                              │   9,994 rows    │
                              └────────┬────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │   MySQL DB      │
                              │  (Star Schema)  │
                              └─────────────────┘
```

### Transformation Pipeline

```
┌──────────────────────────────────────────────────────────────────┐
│                    TRANSFORMATION STAGES                          │
└──────────────────────────────────────────────────────────────────┘

  Raw CSV
    │
    │ 1. Load CSV (all STRING types)
    ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ Stage 1: Type Casting                                       │
  │ - try_cast(Sales as DOUBLE)                                 │
  │ - try_cast(Quantity as INT)                                 │
  │ - try_cast(Discount as DOUBLE)                              │
  │ - try_cast(Profit as DOUBLE)                                │
  └─────────────────────────────────────────────────────────────┘
    │
    │ 2. Date Standardization
    ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ Stage 2: Date Parsing                                       │
  │ - coalesce(try_to_date with 7 formats)                      │
  │ - order_date, ship_date                                     │
  └─────────────────────────────────────────────────────────────┘
    │
    │ 3. Deduplication
    ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ Stage 3: Data Quality                                       │
  │ - dropDuplicates on business keys                           │
  │ - NULL handling                                             │
  └─────────────────────────────────────────────────────────────┘
    │
    ▼
  Clean DataFrame (ready for dimension/fact loading)
```

---

## ETL Module Design

### transformations.py

**Purpose:** Data cleaning and transformation logic

**Key Functions:**

```python
def load_csv(spark, path)
    # Load CSV with inferred schema (all STRING)

def apply_type_casting(df)
    # try_cast() for numeric columns

def standardize_dates(df, columns)
    # Multi-format date parsing with coalesce

def deduplicate(df, keys)
    # Remove duplicate records
```

**Design Principles:**
- Pure functions (no side effects)
- Composable transformations
- Fault-tolerant (try_cast over cast)

---

### dimension_loader.py

**Purpose:** Load dimension tables from transformed DataFrames

**Key Functions:**

```python
def load_dimension(df, table_name, jdbc_url, properties)
    # Generic dimension loader with single-partition write

def load_product_dimension(df, jdbc_url, properties)
    # Product-specific loading logic

def load_customer_dimension(df, jdbc_url, properties)
    # Customer-specific loading logic

# ... similar for location, store, date dimensions
```

**Design Principles:**
- Single-partition writes (coalesce(1))
- Idempotent (truncate before load)
- Deduplication before insert

---

### fact_loader.py

**Purpose:** Load fact table with resolved foreign keys

**Key Functions:**

```python
def create_fact_dataframe(clean_df, jdbc_url, properties)
    # Join clean data with all dimensions to get FKs

def load_fact_table(fact_df, jdbc_url, properties)
    # Write fact table with proper type enforcement
```

**Design Principles:**
- LEFT JOIN with dimensions for FK resolution
- Explicit type casting before write
- Single-partition write for consistency

---

## Database Schema

### Star Schema Design

```
                                    ┌─────────────────┐
                                    │   dim_date      │
                                    │ - date_key (PK) │
                                    │ - full_date     │
                                    │ - year, month   │
                                    │ - quarter, week │
                                    └────────┬────────┘
                                             │
                                             │
┌──────────────┐                    ┌────────▼────────┐                    ┌──────────────┐
│ dim_product  │                    │   sales_fact    │                    │dim_customer  │
│- product_id  │◀───────────────────│- sales_key (PK) │───────────────────▶│- customer_id │
│- name        │   FK               │- product_key (FK)│   FK              │- name        │
│- category    │                    │- customer_key(FK)│                  │- segment     │
│- sub_category│                    │- location_key(FK)│                  └──────────────┘
└──────────────┘                    │- store_key (FK) │
                                    │- date_key (FK)  │
┌──────────────┐                    │- order_date     │         ┌──────────────┐
│ dim_location │                    │- ship_date      │         │  dim_store   │
│- location_id │◀───────────────────│- sales (measure)│────────▶│- store_id    │
│- country     │   FK               │- quantity       │   FK    │- store_name  │
│- state       │                    │- discount       │         └──────────────┘
│- city        │                    │- profit         │
│- region      │                    └─────────────────┘
└──────────────┘
```

### Table Specifications

#### Dimension Tables

| Table | Primary Key | Columns | Row Count |
|-------|-------------|---------|-----------|
| `dim_product` | `product_id` | product_id, product_name, category, sub_category | 1,862 |
| `dim_customer` | `customer_id` | customer_id, customer_name, segment | 793 |
| `dim_location` | `location_id` | location_id, country, state, city, region | 632 |
| `dim_store` | `store_id` | store_id, store_name | 5 |
| `dim_date` | `date_key` | date_key, full_date, year, month, day, quarter, week | 1,458 |

#### Fact Table

| Table | Primary Key | Foreign Keys | Measures | Row Count |
|-------|-------------|--------------|----------|-----------|
| `sales_fact` | `sales_key` | product_key, customer_key, location_key, store_key, date_key | sales, quantity, discount, profit | 9,994 |

---

## Configuration Management

### config.py Structure

```python
# Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "port": "3306",
    "database": "retail_db",
    "user": "root",
    "password": "root"
}

# Spark Configuration
SPARK_CONFIG = {
    "appName": "RetailAnalyticsETL",
    "master": "local[*]",
    "executorMemory": "2g",
    "driverMemory": "2g",
    "sql.shuffle.partitions": "200",
    "sql.adaptive.enabled": "true"
}

# JDBC Configuration
JDBC_DRIVER = "com.mysql.cj.jdbc.Driver"
JDBC_PREFIX = "jdbc:mysql://"

# File Paths
DATA_PATH = "data/superstore.csv"
LOG_PATH = "logs/etl_pipeline.log"
JAR_PATH = "jars/mysql-connector-j-9.6.0.jar"
```

### Configuration Principles

- Centralized configuration (single source of truth)
- Environment-specific overrides supported
- Sensitive credentials externalizable via environment variables

---

## Execution Flow

### Pipeline Orchestration (main.py)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PIPELINE EXECUTION FLOW                           │
└─────────────────────────────────────────────────────────────────────────┘

  START
    │
    ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │ 1. Initialize Spark Session                                         │
  │    - Load config from config.py                                     │
  │    - Configure memory, parallelism                                  │
  │    - Add JDBC driver to classpath                                   │
  └─────────────────────────────────────────────────────────────────────┘
    │
    ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │ 2. Initialize Database                                              │
  │    - Connect to MySQL                                               │
  │    - SET FOREIGN_KEY_CHECKS=0                                       │
  │    - TRUNCATE all tables                                            │
  │    - SET FOREIGN_KEY_CHECKS=1                                       │
  └─────────────────────────────────────────────────────────────────────┘
    │
    ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │ 3. Extract & Transform                                              │
  │    - Load CSV into Spark DataFrame                                  │
  │    - Apply type casting (try_cast)                                  │
  │    - Standardize dates (multi-format parsing)                       │
  │    - Deduplicate records                                            │
  └─────────────────────────────────────────────────────────────────────┘
    │
    ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │ 4. Load Dimensions (in parallel where possible)                     │
  │    - load_product_dimension()  → 1,862 rows                         │
  │    - load_customer_dimension() → 793 rows                           │
  │    - load_location_dimension() → 632 rows                           │
  │    - load_store_dimension()    → 5 rows                             │
  │    - load_date_dimension()     → 1,458 rows                         │
  └─────────────────────────────────────────────────────────────────────┘
    │
    ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │ 5. Load Fact Table                                                  │
  │    - Create fact DataFrame (join with all dimensions)               │
  │    - Resolve foreign keys                                           │
  │    - Enforce final types                                            │
  │    - Write to sales_fact (9,994 rows)                               │
  └─────────────────────────────────────────────────────────────────────┘
    │
    ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │ 6. Verification & Logging                                           │
  │    - Count rows in each table                                       │
  │    - Verify FK relationships                                        │
  │    - Log summary statistics                                         │
  └─────────────────────────────────────────────────────────────────────┘
    │
    ▼
  END (Pipeline Complete)
```

### Execution Timeline

| Stage | Duration | Description |
|-------|----------|-------------|
| Spark Initialization | ~5 seconds | Session creation, driver loading |
| Database Reset | ~2 seconds | Truncate all tables |
| CSV Load & Transform | ~15 seconds | Read, cast, parse, dedupe |
| Dimension Loads | ~30 seconds | 5 dimensions (sequential) |
| Fact Load | ~35 seconds | Join, resolve FKs, write |
| Verification | ~3 seconds | Row counts, FK validation |
| **Total** | **~90 seconds** | Full pipeline execution |

---

## Key Design Decisions

| Decision | Rationale | Trade-offs |
|----------|-----------|------------|
| **Pure Spark writes** | Avoids Windows worker crashes | Slightly slower than pandas for small data |
| **try_cast() for numerics** | Tolerates malformed CSV data | NULL values for truly invalid data |
| **Single-partition writes** | Prevents duplicate key violations | Sequential (not parallel) writes |
| **Truncate before load** | Ensures idempotent pipeline | No historical data retention |
| **NULLable date columns** | Preserves rows with quality issues | NULLs in fact table |
| **Explicit type casting** | Spark 4.x ANSI compliance | More verbose code |
| **LEFT JOIN for FKs** | Preserves all fact records | Potential NULL FKs (handled) |

---

## 🔗 Related Documentation

- [Phase 1 README](README.md) - Full Phase 1 overview
- [Problems Faced](problems_faced.md) - Challenges and solutions
