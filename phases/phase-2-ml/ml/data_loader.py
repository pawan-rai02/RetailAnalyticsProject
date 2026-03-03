"""
Data Loader for Phase 2 ML Pipeline.
Handles loading data from MySQL data warehouse using SQLAlchemy.
"""

import logging
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from ml.config import get_connection_string, LOG_FORMAT, LOG_LEVEL

logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class DataLoader:
    """
    Handles loading data from MySQL data warehouse.
    """
    
    def __init__(self):
        """Initialize database connection."""
        self.connection_string = get_connection_string()
        self.engine = None
    
    def connect(self):
        """
        Establish connection to MySQL database.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.engine = create_engine(self.connection_string)
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Successfully connected to MySQL database")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def disconnect(self):
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")
    
    def load_global_daily_sales(self) -> pd.DataFrame:
        """
        Load global daily sales from warehouse.
        
        Query aggregates sales_fact by date using dim_date.
        
        Returns:
            DataFrame: Daily sales data with columns [full_date, total_sales]
        """
        logger.info("Loading global daily sales from warehouse...")
        
        query = text("""
            SELECT 
                d.full_date,
                SUM(f.sales) as total_sales
            FROM sales_fact f
            JOIN dim_date d ON f.date_key = d.date_key
            GROUP BY d.full_date
            ORDER BY d.full_date
        """)
        
        try:
            if not self.engine:
                if not self.connect():
                    raise ConnectionError("Cannot connect to database")
            
            df = pd.read_sql_query(query, self.engine)
            
            # Convert date column to datetime
            df['full_date'] = pd.to_datetime(df['full_date'])
            
            row_count = len(df)
            logger.info(f"Loaded {row_count} days of sales data")
            
            return df
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to load sales data: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading data: {e}")
            raise
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
