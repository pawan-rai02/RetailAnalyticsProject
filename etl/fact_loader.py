"""
ETL Module: Fact Table Loader
Handles loading of sales_fact table to MySQL.
Pure Spark implementation - no pandas conversions.
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, concat, lit, to_date, year, month, dayofmonth, dayofweek, when, format_string, floor, isnull
from pyspark.sql.types import IntegerType, DoubleType, StringType, TimestampType, BooleanType
from config.config import DB_CONFIG
import logging

logger = logging.getLogger(__name__)


class FactLoader:
    """
    Handles loading of fact table to MySQL.
    Pure Spark implementation for scalability.
    """

    def __init__(self, spark, jdbc_url: str, jdbc_properties: dict):
        self.spark = spark
        self.jdbc_url = jdbc_url
        self.jdbc_properties = jdbc_properties

    def prepare_fact_data(self, df: DataFrame, dim_mappings: dict) -> DataFrame:
        """
        Prepare fact table data by joining with dimension keys.
        Enforces explicit types at each step.
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
            col("dim.product_key").cast(IntegerType()).alias("product_key")
        )

        # Join with customer dimension
        fact_df = fact_df.alias("src").join(
            dim_customer.alias("dim"),
            col("src.customer_id") == col("dim.customer_id"),
            how="left"
        ).select(
            col("src.*"),
            col("dim.customer_key").cast(IntegerType()).alias("customer_key")
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
            col("dim.location_key").cast(IntegerType()).alias("location_key")
        )

        # Join with store dimension
        fact_df = fact_df.alias("src").join(
            dim_store.alias("dim"),
            col("src.store_id") == col("dim.store_id"),
            how="left"
        ).select(
            col("src.*"),
            col("dim.store_key").cast(IntegerType()).alias("store_key")
        )

        # Join with date dimension - create date_key from order_date using integer arithmetic
        fact_df = fact_df.withColumn(
            "calc_date_key",
            (year(col("order_date")) * 10000 + 
             month(col("order_date")) * 100 + 
             dayofmonth(col("order_date"))).cast(IntegerType())
        )

        fact_df = fact_df.alias("src").join(
            dim_date.alias("dim"),
            col("src.calc_date_key") == col("dim.date_key"),
            how="left"
        ).select(
            col("src.*"),
            col("dim.date_key").cast(IntegerType()).alias("date_key")
        )

        # Drop intermediate column
        fact_df = fact_df.drop("calc_date_key")

        return fact_df

    def create_fact_table_schema(self, df: DataFrame) -> DataFrame:
        """
        Create final fact table with explicit schema enforcement.
        All numeric types explicitly defined.
        """
        logger.info("Creating fact table with explicit schema...")

        # Explicit type casting for all columns
        fact_df = df.select(
            col("order_id").cast(StringType()).alias("order_id"),
            col("order_date").cast(TimestampType()).alias("order_date"),
            col("ship_date").cast(TimestampType()).alias("ship_date"),
            col("ship_mode").cast(StringType()).alias("ship_mode"),
            
            # Surrogate keys - IntegerType
            col("product_key").cast(IntegerType()).alias("product_key"),
            col("customer_key").cast(IntegerType()).alias("customer_key"),
            col("location_key").cast(IntegerType()).alias("location_key"),
            col("date_key").cast(IntegerType()).alias("date_key"),
            col("store_key").cast(IntegerType()).alias("store_key"),
            
            # Measures - DoubleType for decimals
            col("sales").cast(DoubleType()).alias("sales"),
            col("quantity").cast(DoubleType()).alias("quantity"),
            col("discount").cast(DoubleType()).alias("discount"),
            col("profit").cast(DoubleType()).alias("profit"),
            col("revenue").cast(DoubleType()).alias("revenue"),
            
            # Derived fields - IntegerType
            col("order_year").cast(IntegerType()).alias("order_year"),
            col("order_month").cast(IntegerType()).alias("order_month"),
            col("order_day").cast(IntegerType()).alias("order_day"),
            col("day_of_week").cast(IntegerType()).alias("day_of_week"),
            
            # Boolean field
            col("is_weekend").cast(BooleanType()).alias("is_weekend")
        )

        return fact_df

    def drop_null_foreign_keys(self, df: DataFrame) -> tuple:
        """
        Drop rows where any foreign key is null.
        Returns tuple of (cleaned_df, dropped_count).
        """
        logger.info("Checking for null foreign keys...")

        original_count = df.count()

        # Filter out rows with null FKs
        cleaned_df = df.filter(
            col("product_key").isNotNull() &
            col("customer_key").isNotNull() &
            col("location_key").isNotNull() &
            col("store_key").isNotNull() &
            col("date_key").isNotNull()
        )

        cleaned_count = cleaned_df.count()
        dropped_count = original_count - cleaned_count

        if dropped_count > 0:
            logger.warning(f"Dropped {dropped_count} rows due to null foreign keys")
            
            # Log breakdown of which FKs are null
            null_counts = {
                "product_key": df.filter(col("product_key").isNull()).count(),
                "customer_key": df.filter(col("customer_key").isNull()).count(),
                "location_key": df.filter(col("location_key").isNull()).count(),
                "store_key": df.filter(col("store_key").isNull()).count(),
                "date_key": df.filter(col("date_key").isNull()).count()
            }
            
            for fk, count in null_counts.items():
                if count > 0:
                    logger.warning(f"  - {fk}: {count} null values")
        else:
            logger.info("No null foreign keys found")

        return cleaned_df, dropped_count

    def load_fact_table(self, df: DataFrame, dim_mappings: dict) -> int:
        """
        Load fact table to MySQL.
        Pure Spark implementation - no pandas conversions.
        Returns the number of rows loaded.
        """
        logger.info("=" * 60)
        logger.info("Loading sales_fact table...")
        logger.info("=" * 60)

        # Prepare fact data with dimension keys
        fact_df = self.prepare_fact_data(df, dim_mappings)

        # Create final schema with explicit types
        fact_df = self.create_fact_table_schema(fact_df)

        # Drop rows with null foreign keys
        fact_df, dropped_count = self.drop_null_foreign_keys(fact_df)

        # Get count before writing
        row_count = fact_df.count()
        logger.info(f"Fact table row count after filtering: {row_count}")

        # Print schema for verification
        logger.info("Fact table schema:")
        fact_df.printSchema()

        # Repartition to 1 partition for stable write on Windows
        # This prevents parallel insert conflicts
        fact_df_single = fact_df.repartition(1)
        
        # Write to MySQL using pure Spark JDBC
        # No pandas, no collect(), no toPandas()
        fact_df_single.write.jdbc(
            url=self.jdbc_url,
            table="sales_fact",
            mode="append",
            properties={
                **self.jdbc_properties,
                "batchSize": "500"
            }
        )
        
        logger.info(f"Written {row_count} rows to sales_fact")
        
        logger.info("=" * 60)
        logger.info(f"sales_fact loaded with {row_count} rows!")
        logger.info(f"Dropped {dropped_count} rows due to null foreign keys")
        logger.info("=" * 60)

        return row_count
