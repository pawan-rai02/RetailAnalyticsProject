"""
Database connection module for the Retail Analytics Layer.
Provides SQLAlchemy engine and query execution utilities.
"""

import os
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
import pandas as pd


class DatabaseConfig:
    """Database configuration loaded from environment or defaults."""
    
    HOST: str = os.getenv("DB_HOST", "localhost")
    PORT: int = int(os.getenv("DB_PORT", "3306"))
    DATABASE: str = os.getenv("DB_NAME", "retail_db")
    USER: str = os.getenv("DB_USER", "root")
    PASSWORD: str = os.getenv("DB_PASSWORD", "root")


class ConnectionManager:
    """
    Manages database connections using SQLAlchemy.
    Provides singleton engine instance for efficient connection pooling.
    """
    
    _engine: Optional[Engine] = None
    
    @classmethod
    def get_engine(cls) -> Engine:
        """
        Get or create the SQLAlchemy engine instance.
        
        Returns:
            Engine: SQLAlchemy engine with connection pooling.
        """
        if cls._engine is None:
            connection_url = (
                f"mysql+pymysql://{DatabaseConfig.USER}:{DatabaseConfig.PASSWORD}"
                f"@{DatabaseConfig.HOST}:{DatabaseConfig.PORT}/{DatabaseConfig.DATABASE}"
            )
            cls._engine = create_engine(
                connection_url,
                pool_size=10,
                max_overflow=20,
                pool_recycle=3600,
                pool_pre_ping=True,
                echo=False
            )
        return cls._engine
    
    @classmethod
    def close_engine(cls) -> None:
        """Dispose of the engine and close all connections."""
        if cls._engine is not None:
            cls._engine.dispose()
            cls._engine = None


def get_engine() -> Engine:
    """
    Get the SQLAlchemy engine instance.
    
    Returns:
        Engine: Configured SQLAlchemy engine.
    """
    return ConnectionManager.get_engine()


def execute_query(query: str, params: Optional[dict] = None) -> pd.DataFrame:
    """
    Execute a SQL query and return results as a Pandas DataFrame.
    
    Args:
        query: SQL query string to execute.
        params: Optional dictionary of query parameters.
        
    Returns:
        pd.DataFrame: Query results as a DataFrame.
        
    Raises:
        Exception: If query execution fails.
    """
    engine = get_engine()
    try:
        with engine.connect() as connection:
            if params:
                result = connection.execute(text(query), params)
            else:
                result = connection.execute(text(query))
            
            columns = result.keys()
            data = result.fetchall()
            
            df = pd.DataFrame(data, columns=columns)
            return df
    except Exception as e:
        raise Exception(f"Query execution failed: {str(e)}")


def execute_query_with_params(query: str, params: dict) -> pd.DataFrame:
    """
    Execute a parameterized SQL query safely.
    
    Args:
        query: SQL query string with named parameters.
        params: Dictionary of parameter values.
        
    Returns:
        pd.DataFrame: Query results as a DataFrame.
    """
    return execute_query(query, params)
