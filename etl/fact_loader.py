"""
ETL Module: Fact Table Loader
Handles loading of sales_fact table to MySQL.
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, concat, lit, to_date, year, month, dayofmonth, dayofweek, when
import logging

logger = logging.getLogger(__name__)


class FactLoader:
    """
    Handles loading of fact table to MySQL.
    """
    
    def __init__(self, spark, jdbc_url: str, jdbc_properties: dict):
        self.spark = spark
        self.jdbc_url = jdbc_url
        self.jdbc_properties = jdbc_properties
    
    def _write_to_mysql(self, df: DataFrame, table_name: str, mode: str = "append"):
        """Write DataFrame to MySQL table."""
        df.write.jdbc(
            url=self.jdbc_url,
            table=table_name,
            mode=mode,
            properties=self.jdbc_properties
        )
        logger.info(f"Written {df.count()} rows to {table_name}")
    
    def prepare_fact_data(self, df: DataFrame, dim_mappings: dict) -> DataFrame:
        """
        Prepare fact table data by joining with dimension keys.
        """
        logger.info("Preparing fact table data with dimension key lookups...")
        
        # Get dimension DataFrames
        dim_product = dim_mappings["product"]
        dim_customer = dim_mappings["customer"]
        dim_location = dim_mappings["location"]
        dim_store = dim_mappings["store"]
        dim_date = dim_mappings["date"]
        
        # Join with product dimension
        fact_df = df.alias("src").join(
            dim_product.alias("dim"),
            col("src.product_id") == col("dim.product_id"),
            how="left"
        ).select(
            col("src.*"),
            col("dim.product_key")
        )
        
        # Join with customer dimension
        fact_df = fact_df.alias("src").join(
            dim_customer.alias("dim"),
            col("src.customer_id") == col("dim.customer_id"),
            how="left"
        ).select(
            col("src.*"),
            col("dim.customer_key")
        )
        
        # Join with location dimension
        fact_df = fact_df.alias("src").join(
            dim_location.alias("dim"),
            (col("src.country") == col("dim.country")) &
            (col("src.state") == col("dim.state")) &
            (col("src.city") == col("dim.city")) &
            (col("src.postal_code") == col("dim.postal_code")) &
            (col("src.region") == col("dim.region")),
            how="left"
        ).select(
            col("src.*"),
            col("dim.location_key")
        )
        
        # Join with store dimension
        fact_df = fact_df.alias("src").join(
            dim_store.alias("dim"),
            col("src.store_id") == col("dim.store_id"),
            how="left"
        ).select(
            col("src.*"),
            col("dim.store_key")
        )
        
        # Join with date dimension - create date_key from order_date
        fact_df = fact_df.withColumn(
            "calc_date_key",
            concat(
                year(col("order_date")).cast("string"),
                lit(format_string("%02d", month(col("order_date")))),
                lit(format_string("%02d", dayofmonth(col("order_date"))))
            ).cast("int")
        )
        
        fact_df = fact_df.alias("src").join(
            dim_date.alias("dim"),
            col("src.calc_date_key") == col("dim.date_key"),
            how="left"
        ).select(
            col("src.*"),
            col("dim.date_key")
        )
        
        # Check for null keys (data quality issue)
        null_counts = {
            "product_key": fact_df.filter(col("product_key").isNull()).count(),
            "customer_key": fact_df.filter(col("customer_key").isNull()).count(),
            "location_key": fact_df.filter(col("location_key").isNull()).count(),
            "store_key": fact_df.filter(col("store_key").isNull()).count(),
            "date_key": fact_df.filter(col("date_key").isNull()).count()
        }
        
        for key, count in null_counts.items():
            if count > 0:
                logger.warning(f"Found {count} rows with null {key}")
        
        return fact_df
    
    def create_fact_table_schema(self, df: DataFrame) -> DataFrame:
        """
        Create final fact table with proper schema.
        """
        logger.info("Creating fact table with proper schema...")
        
        fact_df = df.select(
            col("order_id"),
            col("order_date"),
            col("ship_date"),
            col("ship_mode"),
            col("product_key").cast("int"),
            col("customer_key").cast("int"),
            col("location_key").cast("int"),
            col("date_key").cast("int"),
            col("store_key").cast("int"),
            col("sales").cast("double"),
            col("quantity").cast("int"),
            col("discount").cast("double"),
            col("profit").cast("double"),
            col("revenue").cast("double"),
            col("order_year").cast("int"),
            col("order_month").cast("int"),
            col("order_day").cast("int"),
            col("day_of_week").cast("int"),
            col("is_weekend").cast("boolean")
        )
        
        return fact_df
    
    def load_fact_table(self, df: DataFrame, dim_mappings: dict) -> int:
        """
        Load fact table to MySQL.
        Returns the number of rows loaded.
        """
        logger.info("=" * 60)
        logger.info("Loading sales_fact table...")
        logger.info("=" * 60)
        
        # Prepare fact data with dimension keys
        fact_df = self.prepare_fact_data(df, dim_mappings)
        
        # Create final schema
        fact_df = self.create_fact_table_schema(fact_df)
        
        # Get count before writing
        row_count = fact_df.count()
        logger.info(f"Fact table row count: {row_count}")
        
        # Write to MySQL
        self._write_to_mysql(fact_df, "sales_fact", mode="append")
        
        logger.info("=" * 60)
        logger.info(f"sales_fact loaded with {row_count} rows!")
        logger.info("=" * 60)
        
        return row_count
