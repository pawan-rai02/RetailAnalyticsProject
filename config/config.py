"""
Configuration settings for the Retail Analytics ETL Pipeline.
Centralized configuration for database connections, Spark settings, and file paths.
"""

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "port": "3306",
    "database": "retail_db",
    "user": "root",
    "password": "root",
    "driver": "com.mysql.cj.jdbc.Driver"
}

# JDBC URL construction
JDBC_URL = f"jdbc:mysql://{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

# JDBC Properties for Spark
JDBC_PROPERTIES = {
    "user": DB_CONFIG["user"],
    "password": DB_CONFIG["password"],
    "driver": DB_CONFIG["driver"]
}

# File Paths
DATA_DIR = PROJECT_ROOT / "data"
ETL_DIR = PROJECT_ROOT / "etl"
WAREHOUSE_DIR = PROJECT_ROOT / "warehouse"
LOGS_DIR = PROJECT_ROOT / "logs"
JARS_DIR = PROJECT_ROOT / "jars"

# Input CSV file
INPUT_CSV = DATA_DIR / "superstore.csv"

# JDBC Driver
JDBC_DRIVER_JAR = JARS_DIR / "mysql-connector-j-9.6.0.jar"

# Spark Configuration
SPARK_CONFIG = {
    "appName": "RetailAnalyticsETL",
    "master": "local[*]",
    "executorMemory": "2g",
    "driverMemory": "2g",
    "sql.shuffle.partitions": "4",
    "sql.adaptive.enabled": "true"
}

# Logging Configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"
LOG_FILE = LOGS_DIR / "etl_pipeline.log"

# Data Processing Settings
PROCESSING_CONFIG = {
    "batch_size": 1000,
    "null_replacement": "Unknown",
    "store_count": 5  # Number of synthetic stores to create
}

# Table Names (Star Schema)
TABLES = {
    "fact": "sales_fact",
    "dimensions": {
        "product": "dim_product",
        "customer": "dim_customer",
        "location": "dim_location",
        "date": "dim_date",
        "store": "dim_store"
    }
}
