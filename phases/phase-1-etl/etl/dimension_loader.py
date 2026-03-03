"""
ETL Module: Dimension Table Loaders
Handles extraction and loading of dimension tables to MySQL.
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, lit, row_number, md5, concat, to_date, year, month, dayofmonth, dayofweek, date_format, when, format_string, floor, count
from pyspark.sql.window import Window
import logging
from config.config import DB_CONFIG

logger = logging.getLogger(__name__)


class DimensionLoader:
    """
    Handles loading of dimension tables to MySQL.
    """

    def __init__(self, spark, jdbc_url: str, jdbc_properties: dict):
        self.spark = spark
        self.jdbc_url = jdbc_url
        self.jdbc_properties = jdbc_properties
    
    def _write_to_mysql(self, df: DataFrame, table_name: str, mode: str = "append", row_count: int = None):
        """Write DataFrame to MySQL table."""
        df.write.jdbc(
            url=self.jdbc_url,
            table=table_name,
            mode=mode,
            properties=self.jdbc_properties
        )
        if row_count is not None:
            logger.info(f"Written {row_count} rows to {table_name}")
        else:
            logger.info(f"Written data to {table_name}")
    
    def load_dim_product(self, df: DataFrame) -> DataFrame:
        """
        Extract and load dim_product dimension.
        Returns DataFrame with product_key mappings for fact table.
        """
        logger.info("Loading dim_product dimension...")

        # Extract unique products - deduplicate on product_id (business key)
        dim_product = df.select(
            "product_id", "category", "sub_category", "product_name"
        ).dropDuplicates(["product_id"])

        initial_count = dim_product.count()
        logger.info(f"Extracted {initial_count} unique products")
        
        # Sanity check: verify no duplicate product_id values
        duplicate_check = df.select("product_id").groupBy("product_id").count().filter(col("count") > 1)
        duplicate_count = duplicate_check.count()
        if duplicate_count > 0:
            logger.warning(f"Found {duplicate_count} product_id values with duplicates in source")
            duplicate_check.show(10)
        else:
            logger.info("No duplicate product_id values found - deduplication successful")
        
        # CRITICAL: Coalesce to 1 partition to prevent parallel insert conflicts
        dim_product_single = dim_product.coalesce(1)
        
        # Write to MySQL using append mode (tables truncated before run)
        self._write_to_mysql(dim_product_single, "dim_product", mode="append", row_count=initial_count)

        # Read back with generated keys for mapping
        dim_product_with_keys = self.spark.read.jdbc(
            url=self.jdbc_url,
            table="dim_product",
            properties=self.jdbc_properties
        )

        # Verification
        verify_count = dim_product_with_keys.count()
        logger.info(f"Verification: dim_product has {verify_count} rows in MySQL")
        if verify_count != initial_count:
            logger.error(f"Row count mismatch! Expected {initial_count}, got {verify_count}")
            raise Exception(f"dim_product load failed: expected {initial_count} rows, got {verify_count}")
        
        logger.info(f"dim_product loaded successfully with {verify_count} rows")
        return dim_product_with_keys

    def load_dim_customer(self, df: DataFrame) -> DataFrame:
        """
        Extract and load dim_customer dimension.
        Returns DataFrame with customer_key mappings for fact table.
        """
        logger.info("Loading dim_customer dimension...")

        # Extract unique customers - deduplicate on customer_id (business key)
        dim_customer = df.select(
            "customer_id", "customer_name", "segment"
        ).dropDuplicates(["customer_id"])

        initial_count = dim_customer.count()
        logger.info(f"Extracted {initial_count} unique customers")
        
        # Sanity check for duplicates
        duplicate_check = df.select("customer_id").groupBy("customer_id").count().filter(col("count") > 1)
        duplicate_count = duplicate_check.count()
        if duplicate_count > 0:
            logger.warning(f"Found {duplicate_count} customer_id values with duplicates in source")
        else:
            logger.info("No duplicate customer_id values found - deduplication successful")
        
        # Coalesce to 1 partition
        dim_customer_single = dim_customer.coalesce(1)
        
        # Write to MySQL
        self._write_to_mysql(dim_customer_single, "dim_customer", mode="append", row_count=initial_count)

        # Read back with generated keys
        dim_customer_with_keys = self.spark.read.jdbc(
            url=self.jdbc_url,
            table="dim_customer",
            properties=self.jdbc_properties
        )

        # Verification
        verify_count = dim_customer_with_keys.count()
        logger.info(f"Verification: dim_customer has {verify_count} rows in MySQL")
        if verify_count != initial_count:
            logger.error(f"Row count mismatch! Expected {initial_count}, got {verify_count}")
            raise Exception(f"dim_customer load failed: expected {initial_count} rows, got {verify_count}")
        
        logger.info(f"dim_customer loaded successfully with {verify_count} rows")
        return dim_customer_with_keys

    def load_dim_location(self, df: DataFrame) -> DataFrame:
        """
        Extract and load dim_location dimension.
        Returns DataFrame with location_key mappings for fact table.
        """
        logger.info("Loading dim_location dimension...")

        # Extract unique locations - deduplicate on all location columns
        dim_location = df.select(
            "country", "state", "city", "postal_code", "region"
        ).dropDuplicates(["country", "state", "city", "postal_code", "region"])

        initial_count = dim_location.count()
        logger.info(f"Extracted {initial_count} unique locations")
        
        # Coalesce to 1 partition
        dim_location_single = dim_location.coalesce(1)
        
        # Write to MySQL
        self._write_to_mysql(dim_location_single, "dim_location", mode="append", row_count=initial_count)

        # Read back with generated keys
        dim_location_with_keys = self.spark.read.jdbc(
            url=self.jdbc_url,
            table="dim_location",
            properties=self.jdbc_properties
        )

        # Verification
        verify_count = dim_location_with_keys.count()
        logger.info(f"Verification: dim_location has {verify_count} rows in MySQL")
        if verify_count != initial_count:
            logger.error(f"Row count mismatch! Expected {initial_count}, got {verify_count}")
            raise Exception(f"dim_location load failed: expected {initial_count} rows, got {verify_count}")
        
        logger.info(f"dim_location loaded successfully with {verify_count} rows")
        return dim_location_with_keys

    def load_dim_store(self, df: DataFrame, store_count: int = 5) -> DataFrame:
        """
        Extract and load dim_store dimension.
        Creates synthetic store records.
        Returns DataFrame with store_key mappings for fact table.
        
        Note: Uses direct MySQL insertion for small tables to avoid Spark Python worker issues on Windows.
        """
        logger.info(f"Loading dim_store dimension with {store_count} stores...")

        # Use direct MySQL insertion for small static tables to avoid Spark worker crashes
        import mysql.connector
        
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"]
        )
        cursor = conn.cursor()
        
        # Insert store records directly
        for i in range(1, store_count + 1):
            cursor.execute(
                "INSERT INTO dim_store (store_id, store_name, region) VALUES (%s, %s, %s)",
                (f"Store_{i}", f"Retail Store {i}", "Multi-Region")
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Written {store_count} rows to dim_store")

        # Read back with generated keys
        dim_store_with_keys = self.spark.read.jdbc(
            url=self.jdbc_url,
            table="dim_store",
            properties=self.jdbc_properties
        )

        # Verification
        verify_count = dim_store_with_keys.count()
        logger.info(f"Verification: dim_store has {verify_count} rows in MySQL")
        if verify_count != store_count:
            logger.error(f"Row count mismatch! Expected {store_count}, got {verify_count}")
            raise Exception(f"dim_store load failed: expected {store_count} rows, got {verify_count}")
        
        logger.info(f"dim_store loaded successfully with {verify_count} rows")
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
            (floor((month(col("full_date")) - 1) / 3) + 1).alias("quarter"),
            year(col("full_date")).alias("year"),
            dayofweek(col("full_date")).alias("day_of_week"),
            date_format(col("full_date"), "EEEE").alias("day_name"),
            date_format(col("full_date"), "MMMM").alias("month_name"),
            when(dayofweek(col("full_date")).isin([1, 7]), True).otherwise(False).alias("is_weekend"),
            lit(False).alias("is_holiday")
        )

        initial_count = dim_date.count()
        logger.info(f"Generated {initial_count} date records")
        
        # Coalesce to 1 partition
        dim_date_single = dim_date.coalesce(1)

        # Write to MySQL
        self._write_to_mysql(dim_date_single, "dim_date", mode="append", row_count=initial_count)

        # Read back for mapping
        dim_date_with_keys = self.spark.read.jdbc(
            url=self.jdbc_url,
            table="dim_date",
            properties=self.jdbc_properties
        )

        # Verification
        verify_count = dim_date_with_keys.count()
        logger.info(f"Verification: dim_date has {verify_count} rows in MySQL")
        if verify_count != initial_count:
            logger.error(f"Row count mismatch! Expected {initial_count}, got {verify_count}")
            raise Exception(f"dim_date load failed: expected {initial_count} rows, got {verify_count}")
        
        logger.info(f"dim_date loaded successfully with {verify_count} rows")
        return dim_date_with_keys

    def load_all_dimensions(self, df: DataFrame) -> dict:
        """
        Load all dimension tables and return key mappings.
        """
        logger.info("=" * 60)
        logger.info("Loading all dimension tables...")
        logger.info("=" * 60)

        mappings = {}

        # Load dimensions sequentially
        mappings["product"] = self.load_dim_product(df)
        mappings["customer"] = self.load_dim_customer(df)
        mappings["location"] = self.load_dim_location(df)
        mappings["store"] = self.load_dim_store(df)
        mappings["date"] = self.load_dim_date(df)

        logger.info("=" * 60)
        logger.info("All dimension tables loaded successfully!")
        logger.info("=" * 60)

        return mappings
