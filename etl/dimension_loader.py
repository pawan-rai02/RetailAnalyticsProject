"""
ETL Module: Dimension Table Loaders
Handles extraction and loading of dimension tables to MySQL.
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, lit, row_number, md5, concat, to_date, year, month, dayofmonth, dayofweek, date_format, when
from pyspark.sql.window import Window
import logging

logger = logging.getLogger(__name__)


class DimensionLoader:
    """
    Handles loading of dimension tables to MySQL.
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
    
    def load_dim_product(self, df: DataFrame) -> DataFrame:
        """
        Extract and load dim_product dimension.
        Returns DataFrame with product_key mappings for fact table.
        """
        logger.info("Loading dim_product dimension...")
        
        # Extract unique products
        dim_product = df.select(
            "product_id", "category", "sub_category", "product_name"
        ).distinct()
        
        initial_count = dim_product.count()
        logger.info(f"Extracted {initial_count} unique products")
        
        # Write to MySQL
        self._write_to_mysql(dim_product, "dim_product", mode="append")
        
        # Read back with generated keys for mapping
        dim_product_with_keys = self.spark.read.jdbc(
            url=self.jdbc_url,
            table="dim_product",
            properties=self.jdbc_properties
        )
        
        logger.info(f"dim_product loaded with {dim_product_with_keys.count()} rows")
        return dim_product_with_keys
    
    def load_dim_customer(self, df: DataFrame) -> DataFrame:
        """
        Extract and load dim_customer dimension.
        Returns DataFrame with customer_key mappings for fact table.
        """
        logger.info("Loading dim_customer dimension...")
        
        # Extract unique customers
        dim_customer = df.select(
            "customer_id", "customer_name", "segment"
        ).distinct()
        
        initial_count = dim_customer.count()
        logger.info(f"Extracted {initial_count} unique customers")
        
        # Write to MySQL
        self._write_to_mysql(dim_customer, "dim_customer", mode="append")
        
        # Read back with generated keys for mapping
        dim_customer_with_keys = self.spark.read.jdbc(
            url=self.jdbc_url,
            table="dim_customer",
            properties=self.jdbc_properties
        )
        
        logger.info(f"dim_customer loaded with {dim_customer_with_keys.count()} rows")
        return dim_customer_with_keys
    
    def load_dim_location(self, df: DataFrame) -> DataFrame:
        """
        Extract and load dim_location dimension.
        Returns DataFrame with location_key mappings for fact table.
        """
        logger.info("Loading dim_location dimension...")
        
        # Extract unique locations
        dim_location = df.select(
            "country", "state", "city", "postal_code", "region"
        ).distinct()
        
        initial_count = dim_location.count()
        logger.info(f"Extracted {initial_count} unique locations")
        
        # Write to MySQL
        self._write_to_mysql(dim_location, "dim_location", mode="append")
        
        # Read back with generated keys for mapping
        dim_location_with_keys = self.spark.read.jdbc(
            url=self.jdbc_url,
            table="dim_location",
            properties=self.jdbc_properties
        )
        
        logger.info(f"dim_location loaded with {dim_location_with_keys.count()} rows")
        return dim_location_with_keys
    
    def load_dim_store(self, df: DataFrame, store_count: int = 5) -> DataFrame:
        """
        Extract and load dim_store dimension.
        Creates synthetic store records.
        Returns DataFrame with store_key mappings for fact table.
        """
        logger.info(f"Loading dim_store dimension with {store_count} stores...")
        
        # Create store records
        stores_data = []
        for i in range(1, store_count + 1):
            stores_data.append((f"Store_{i}", f"Retail Store {i}", "Multi-Region"))
        
        dim_store = self.spark.createDataFrame(
            stores_data,
            ["store_id", "store_name", "region"]
        )
        
        # Write to MySQL
        self._write_to_mysql(dim_store, "dim_store", mode="append")
        
        # Read back with generated keys for mapping
        dim_store_with_keys = self.spark.read.jdbc(
            url=self.jdbc_url,
            table="dim_store",
            properties=self.jdbc_properties
        )
        
        logger.info(f"dim_store loaded with {dim_store_with_keys.count()} rows")
        return dim_store_with_keys
    
    def load_dim_date(self, df: DataFrame) -> DataFrame:
        """
        Extract and load dim_date dimension.
        Generates date dimension from min to max order date.
        Returns DataFrame with date_key mappings for fact table.
        """
        logger.info("Loading dim_date dimension...")
        
        # Get date range
        min_date = df.agg({"order_date": "min"}).collect()[0][0]
        max_date = df.agg({"order_date": "max"}).collect()[0][0]
        
        logger.info(f"Date range: {min_date} to {max_date}")
        
        # Generate date dimension using Spark
        from pyspark.sql.functions import expr, sequence
        
        # Create date range DataFrame
        date_range_df = self.spark.range(1).select(
            expr(f"sequence(to_date('{min_date}'), to_date('{max_date}'), interval 1 day)").alias("dates")
        ).selectExpr("explode(dates) as full_date")
        
        # Add date dimension attributes
        dim_date = date_range_df.select(
            concat(
                year(col("full_date")),
                lit(format_string("%02d", month(col("full_date")))),
                lit(format_string("%02d", dayofmonth(col("full_date"))))
            ).cast("int").alias("date_key"),
            col("full_date"),
            dayofmonth(col("full_date")).alias("day_of_month"),
            month(col("full_date")).alias("month"),
            ((month(col("full_date")) - 1) // 3 + 1).alias("quarter"),
            year(col("full_date")).alias("year"),
            dayofweek(col("full_date")).alias("day_of_week"),
            date_format(col("full_date"), "EEEE").alias("day_name"),
            date_format(col("full_date"), "MMMM").alias("month_name"),
            when(dayofweek(col("full_date")).isin([1, 7]), True).otherwise(False).alias("is_weekend"),
            lit(False).alias("is_holiday")
        )
        
        initial_count = dim_date.count()
        logger.info(f"Generated {initial_count} date records")
        
        # Write to MySQL
        self._write_to_mysql(dim_date, "dim_date", mode="append")
        
        # Read back for mapping
        dim_date_with_keys = self.spark.read.jdbc(
            url=self.jdbc_url,
            table="dim_date",
            properties=self.jdbc_properties
        )
        
        logger.info(f"dim_date loaded with {dim_date_with_keys.count()} rows")
        return dim_date_with_keys
    
    def load_all_dimensions(self, df: DataFrame) -> dict:
        """
        Load all dimension tables and return key mappings.
        """
        logger.info("=" * 60)
        logger.info("Loading all dimension tables...")
        logger.info("=" * 60)
        
        mappings = {}
        
        # Load dimensions
        mappings["product"] = self.load_dim_product(df)
        mappings["customer"] = self.load_dim_customer(df)
        mappings["location"] = self.load_dim_location(df)
        mappings["store"] = self.load_dim_store(df)
        mappings["date"] = self.load_dim_date(df)
        
        logger.info("=" * 60)
        logger.info("All dimension tables loaded successfully!")
        logger.info("=" * 60)
        
        return mappings
