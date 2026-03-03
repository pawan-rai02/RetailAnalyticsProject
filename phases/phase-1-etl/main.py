"""
Main Orchestration Script for Retail Analytics ETL Pipeline
Entry point for the production-style data engineering pipeline.
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from pyspark.sql import SparkSession
from config.config import (
    SPARK_CONFIG, JDBC_URL, JDBC_PROPERTIES, JDBC_DRIVER_JAR,
    INPUT_CSV, LOG_FILE, LOG_FORMAT, LOG_LEVEL, TABLES, PROCESSING_CONFIG
)
from etl.transformations import DataCleaner
from etl.dimension_loader import DimensionLoader
from etl.fact_loader import FactLoader
from warehouse.init_db import init_database


def setup_logging():
    """Configure logging for the ETL pipeline."""
    # Ensure logs directory exists
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


def create_spark_session():
    """Create and configure Spark session."""
    logger = logging.getLogger(__name__)
    logger.info("Creating Spark session...")

    # Build Spark session with JDBC driver and Windows-compatible settings
    spark = SparkSession.builder \
        .appName(SPARK_CONFIG["appName"]) \
        .master(SPARK_CONFIG["master"]) \
        .config("spark.executor.memory", SPARK_CONFIG["executorMemory"]) \
        .config("spark.driver.memory", SPARK_CONFIG["driverMemory"]) \
        .config("spark.sql.shuffle.partitions", SPARK_CONFIG["sql.shuffle.partitions"]) \
        .config("spark.sql.adaptive.enabled", SPARK_CONFIG["sql.adaptive.enabled"]) \
        .config("spark.jars", str(JDBC_DRIVER_JAR)) \
        .config("spark.python.worker.timeout", "600") \
        .config("spark.sql.execution.pyspark.udf.faulthandler.enabled", "true") \
        .config("spark.python.worker.faulthandler.enabled", "true") \
        .config("spark.sql.sources.parallelPartitionDiscovery.parallelism", "1") \
        .getOrCreate()

    # Set log level
    spark.sparkContext.setLogLevel("WARN")

    logger.info(f"Spark session created: {spark.sparkContext.appName}")
    logger.info(f"Spark version: {spark.version}")

    return spark


def run_etl_pipeline(spark):
    """
    Execute the complete ETL pipeline.
    """
    logger = logging.getLogger(__name__)
    
    # Initialize data cleaner
    cleaner = DataCleaner(spark)
    
    # Load and clean data
    logger.info("=" * 60)
    logger.info("PHASE 1: Loading and Cleaning Data")
    logger.info("=" * 60)
    
    raw_df = cleaner.load_csv(str(INPUT_CSV))
    cleaned_df = cleaner.clean_and_transform(raw_df)
    
    # Initialize dimension loader
    dim_loader = DimensionLoader(spark, JDBC_URL, JDBC_PROPERTIES)
    
    # Load dimension tables
    logger.info("=" * 60)
    logger.info("PHASE 2: Loading Dimension Tables")
    logger.info("=" * 60)
    
    dim_mappings = dim_loader.load_all_dimensions(cleaned_df)
    
    # Initialize fact loader
    fact_loader = FactLoader(spark, JDBC_URL, JDBC_PROPERTIES)
    
    # Load fact table
    logger.info("=" * 60)
    logger.info("PHASE 3: Loading Fact Table")
    logger.info("=" * 60)
    
    fact_row_count = fact_loader.load_fact_table(cleaned_df, dim_mappings)
    
    return {
        "cleaned_rows": cleaned_df.count(),
        "fact_rows": fact_row_count,
        "dim_product": dim_mappings["product"].count(),
        "dim_customer": dim_mappings["customer"].count(),
        "dim_location": dim_mappings["location"].count(),
        "dim_store": dim_mappings["store"].count(),
        "dim_date": dim_mappings["date"].count()
    }


def verify_results(spark):
    """Verify the loaded data in MySQL."""
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("Verifying Results")
    logger.info("=" * 60)

    # Read back from MySQL to verify
    tables = TABLES["dimensions"]
    fact_table = TABLES["fact"]

    results = {}
    for table_name, table_full in [("dim_product", tables["product"]),
                                    ("dim_customer", tables["customer"]),
                                    ("dim_location", tables["location"]),
                                    ("dim_store", tables["store"]),
                                    ("dim_date", tables["date"]),
                                    ("sales_fact", fact_table)]:
        try:
            df = spark.read.jdbc(url=JDBC_URL, table=table_full, properties=JDBC_PROPERTIES)
            count = df.count()
            results[table_name] = count
            logger.info(f"{table_name}: {count} rows")
        except Exception as e:
            logger.error(f"Error reading {table_name}: {e}")
            results[table_name] = -1

    return results


def main():
    """Main entry point for the ETL pipeline."""
    start_time = datetime.now()
    
    # Setup logging
    logger = setup_logging()
    
    logger.info("=" * 60)
    logger.info("RETAIL ANALYTICS ETL PIPELINE")
    logger.info(f"Started at: {start_time}")
    logger.info("=" * 60)
    
    # Check if input file exists
    if not INPUT_CSV.exists():
        logger.error(f"Input file not found: {INPUT_CSV}")
        logger.error("Please copy the Superstore CSV to the data/ folder")
        sys.exit(1)
    
    # Check if JDBC driver exists
    if not JDBC_DRIVER_JAR.exists():
        logger.error(f"JDBC driver not found: {JDBC_DRIVER_JAR}")
        sys.exit(1)
    
    try:
        # Initialize database schema and truncate existing tables
        logger.info("Initializing database schema...")
        if not init_database(truncate_existing=True):
            logger.error("Database initialization failed!")
            sys.exit(1)
        
        # Create Spark session
        spark = create_spark_session()
        
        # Run ETL pipeline
        results = run_etl_pipeline(spark)
        
        # Verify results
        verification = verify_results(spark)
        
        # Stop Spark session
        spark.stop()
        
        # Print summary
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info("=" * 60)
        logger.info("PIPELINE EXECUTION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Start Time: {start_time}")
        logger.info(f"End Time: {end_time}")
        logger.info(f"Duration: {duration}")
        logger.info("-" * 60)
        logger.info("Rows Processed:")
        for key, value in results.items():
            logger.info(f"  {key}: {value}")
        logger.info("-" * 60)
        logger.info("Verification Results:")
        for key, value in verification.items():
            status = "✓" if value > 0 else "✗"
            logger.info(f"  {status} {key}: {value} rows")
        logger.info("=" * 60)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info("=" * 60)
        
        return 0
        
    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
