"""
Database Initialization Script
Creates the MySQL database and star schema tables.
"""

import mysql.connector
from config.config import DB_CONFIG, WAREHOUSE_DIR
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def init_database(truncate_existing=False):
    """Initialize the database and create tables."""

    # First, connect without database to create it
    logger.info("Connecting to MySQL server...")

    try:
        # Connect to MySQL server (without specific database)
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        cursor = conn.cursor()

        # Create database if not exists
        logger.info(f"Creating database '{DB_CONFIG['database']}' if not exists...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        logger.info("Database created/verified successfully.")

        cursor.close()
        conn.close()

        # Now connect to the specific database
        logger.info(f"Connecting to database '{DB_CONFIG['database']}'...")
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"]
        )
        cursor = conn.cursor()

        # Truncate existing tables if requested (for reruns)
        if truncate_existing:
            logger.info("Truncating existing tables...")
            try:
                cursor.execute("SET FOREIGN_KEY_CHECKS=0")
                cursor.execute("TRUNCATE TABLE sales_fact")
                cursor.execute("TRUNCATE TABLE dim_product")
                cursor.execute("TRUNCATE TABLE dim_customer")
                cursor.execute("TRUNCATE TABLE dim_location")
                cursor.execute("TRUNCATE TABLE dim_store")
                cursor.execute("TRUNCATE TABLE dim_date")
                cursor.execute("SET FOREIGN_KEY_CHECKS=1")
                conn.commit()
                logger.info("Tables truncated successfully.")
            except mysql.connector.Error as e:
                # Tables don't exist yet - this is fine for first run
                logger.info(f"Tables don't exist yet, will create them. ({e})")
                conn.rollback()

        # Read and execute schema SQL
        schema_path = WAREHOUSE_DIR / "schema.sql"
        logger.info(f"Reading schema from {schema_path}...")
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Split by semicolons and execute each statement
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip() and not stmt.strip().startswith('--')]
        
        logger.info(f"Executing {len(statements)} SQL statements...")
        
        for i, stmt in enumerate(statements, 1):
            if stmt:
                try:
                    cursor.execute(stmt)
                    if i % 5 == 0:
                        logger.info(f"Executed {i}/{len(statements)} statements...")
                except mysql.connector.Error as e:
                    logger.warning(f"Statement {i} warning: {e}")
        
        conn.commit()
        logger.info("Schema creation completed successfully!")
        
        # Verify tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        logger.info(f"Tables created: {[t[0] for t in tables]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except mysql.connector.Error as e:
        logger.error(f"MySQL Error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Starting Database Initialization")
    logger.info("=" * 60)
    
    success = init_database()
    
    if success:
        logger.info("=" * 60)
        logger.info("Database initialization completed successfully!")
        logger.info("=" * 60)
    else:
        logger.error("=" * 60)
        logger.error("Database initialization failed!")
        logger.error("=" * 60)
