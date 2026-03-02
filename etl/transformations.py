"""
ETL Module: Data Cleaning and Transformation
Handles all data quality issues and transformations for the raw Superstore dataset.
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    col, when, to_date, to_timestamp, year, month, dayofmonth,
    dayofweek, date_format, lit, trim, upper, coalesce, concat, rand
)
from pyspark.sql.types import TimestampType, DateType
import logging
import random

logger = logging.getLogger(__name__)


class DataCleaner:
    """
    Handles data cleaning and transformation operations.
    """
    
    def __init__(self, spark):
        self.spark = spark
        self.store_count = 5
    
    def load_csv(self, file_path: str) -> DataFrame:
        """Load CSV file with proper schema inference."""
        logger.info(f"Loading CSV from {file_path}")
        
        df = self.spark.read.option("header", "true") \
            .option("inferSchema", "true") \
            .option("encoding", "UTF-8") \
            .csv(file_path)
        
        row_count = df.count()
        logger.info(f"Loaded {row_count} rows from CSV")
        return df
    
    def standardize_dates(self, df: DataFrame) -> DataFrame:
        """
        Standardize inconsistent date formats.
        Handles formats like: 11-08-2016, 6/16/2016, MM/dd/yyyy, MM-dd-yyyy
        """
        logger.info("Standardizing date formats...")
        
        # Handle Order Date - try multiple formats
        df = df.withColumn(
            "order_date_parsed",
            coalesce(
                to_date(col("Order Date"), "MM/dd/yyyy"),
                to_date(col("Order Date"), "MM-dd-yyyy"),
                to_date(col("Order Date"), "yyyy-MM-dd"),
                to_date(col("Order Date"), "dd/MM/yyyy"),
                to_date(col("Order Date"), "dd-MM-yyyy")
            )
        )
        
        # Handle Ship Date - try multiple formats
        df = df.withColumn(
            "ship_date_parsed",
            coalesce(
                to_date(col("Ship Date"), "MM/dd/yyyy"),
                to_date(col("Ship Date"), "MM-dd-yyyy"),
                to_date(col("Ship Date"), "yyyy-MM-dd"),
                to_date(col("Ship Date"), "dd/MM/yyyy"),
                to_date(col("Ship Date"), "dd-MM-yyyy")
            )
        )
        
        # Convert to timestamp
        df = df.withColumn("order_timestamp", to_timestamp(col("order_date_parsed")))
        df = df.withColumn("ship_timestamp", to_timestamp(col("ship_date_parsed")))
        
        # Log any null dates
        null_order_dates = df.filter(col("order_timestamp").isNull()).count()
        null_ship_dates = df.filter(col("ship_timestamp").isNull()).count()
        
        if null_order_dates > 0:
            logger.warning(f"Found {null_order_dates} rows with unparseable Order Date")
        if null_ship_dates > 0:
            logger.warning(f"Found {null_ship_dates} rows with unparseable Ship Date")
        
        return df
    
    def add_synthetic_store(self, df: DataFrame) -> DataFrame:
        """
        Add synthetic store_id column (Store_1 to Store_5 randomly assigned).
        Uses a deterministic approach based on row hash for reproducibility.
        """
        logger.info(f"Adding synthetic store assignments (1-{self.store_count})...")
        
        # Use monotonically_increasing_id for deterministic assignment
        df = df.withColumn(
            "store_id",
            concat(
                lit("Store_"),
                (col("Row ID").cast("int") % self.store_count + 1).cast("string")
            )
        )
        
        return df
    
    def remove_duplicates(self, df: DataFrame) -> DataFrame:
        """Remove duplicate rows based on all columns."""
        logger.info("Removing duplicate rows...")
        
        initial_count = df.count()
        df = df.dropDuplicates()
        final_count = df.count()
        
        duplicates_removed = initial_count - final_count
        logger.info(f"Removed {duplicates_removed} duplicate rows")
        
        return df
    
    def handle_nulls(self, df: DataFrame) -> DataFrame:
        """Handle null values safely with appropriate defaults."""
        logger.info("Handling null values...")
        
        # Replace nulls in categorical columns
        categorical_cols = ["Customer Name", "Segment", "Country", "Region", 
                           "Category", "Sub-Category", "Product Name", "Ship Mode"]
        
        for col_name in categorical_cols:
            if col_name in df.columns:
                df = df.withColumn(col_name, coalesce(col(col_name), lit("Unknown")))
        
        # Replace nulls in numeric columns with 0
        numeric_cols = ["Sales", "Quantity", "Discount", "Profit", "Postal Code"]
        for col_name in numeric_cols:
            if col_name in df.columns:
                df = df.withColumn(col_name, coalesce(col(col_name), lit(0)))
        
        return df
    
    def create_derived_fields(self, df: DataFrame) -> DataFrame:
        """Create derived fields for analytics."""
        logger.info("Creating derived fields...")
        
        df = df \
            .withColumn("order_year", year(col("order_timestamp"))) \
            .withColumn("order_month", month(col("order_timestamp"))) \
            .withColumn("order_day", dayofmonth(col("order_timestamp"))) \
            .withColumn("day_of_week", dayofweek(col("order_timestamp"))) \
            .withColumn("is_weekend", when(col("day_of_week").isin([1, 7]), True).otherwise(False)) \
            .withColumn("revenue", col("Sales"))  # Revenue = Sales
        
        return df
    
    def clean_and_transform(self, df: DataFrame) -> DataFrame:
        """
        Main transformation pipeline.
        Applies all cleaning and transformation steps.
        """
        logger.info("Starting data cleaning and transformation pipeline...")
        
        # Step 1: Standardize dates
        df = self.standardize_dates(df)
        
        # Step 2: Add synthetic store
        df = self.add_synthetic_store(df)
        
        # Step 3: Remove duplicates
        df = self.remove_duplicates(df)
        
        # Step 4: Handle nulls
        df = self.handle_nulls(df)
        
        # Step 5: Create derived fields
        df = self.create_derived_fields(df)
        
        # Select and rename columns for star schema
        df = df.select(
            col("Row ID").alias("row_id"),
            col("Order ID").alias("order_id"),
            col("order_timestamp").alias("order_date"),
            col("ship_timestamp").alias("ship_date"),
            col("Ship Mode").alias("ship_mode"),
            col("Customer ID").alias("customer_id"),
            col("Customer Name").alias("customer_name"),
            col("Segment").alias("segment"),
            col("Country").alias("country"),
            col("City").alias("city"),
            col("State").alias("state"),
            col("Postal Code").alias("postal_code"),
            col("Region").alias("region"),
            col("Product ID").alias("product_id"),
            col("Category").alias("category"),
            col("Sub-Category").alias("sub_category"),
            col("Product Name").alias("product_name"),
            col("Sales").alias("sales"),
            col("Quantity").alias("quantity"),
            col("Discount").alias("discount"),
            col("Profit").alias("profit"),
            col("store_id").alias("store_id"),
            col("order_year").alias("order_year"),
            col("order_month").alias("order_month"),
            col("order_day").alias("order_day"),
            col("day_of_week").alias("day_of_week"),
            col("is_weekend").alias("is_weekend"),
            col("revenue").alias("revenue")
        )
        
        final_count = df.count()
        logger.info(f"Transformation complete. Final row count: {final_count}")
        
        return df
