"""
Revenue Analytics Module.
Provides revenue-related KPIs and metrics from the retail star schema.

Note: Uses actual Phase 1 schema column names:
- sales_fact.sales (not sales_amount)
- sales_fact.date_key (not date_id)
- dim_date.date_key (not date_id)
"""

import pandas as pd
from db.connection import execute_query


def get_total_revenue() -> pd.DataFrame:
    """Calculate total revenue across all transactions."""
    query = """
    SELECT 
        ROUND(SUM(sf.sales), 2) AS total_revenue,
        COUNT(*) AS total_transactions,
        ROUND(AVG(sf.sales), 2) AS avg_transaction_value
    FROM sales_fact sf
    """
    return execute_query(query)


def get_monthly_revenue_trend() -> pd.DataFrame:
    """Get monthly revenue trend with year-over-year comparison."""
    query = """
    SELECT 
        d.year,
        d.month,
        d.month_name,
        ROUND(SUM(sf.sales), 2) AS monthly_revenue,
        COUNT(*) AS transaction_count,
        ROUND(AVG(sf.sales), 2) AS avg_transaction_value
    FROM sales_fact sf
    INNER JOIN dim_date d ON sf.date_key = d.date_key
    GROUP BY d.year, d.month, d.month_name
    ORDER BY d.year, d.month
    """
    return execute_query(query)


def get_yearly_revenue() -> pd.DataFrame:
    """Get yearly revenue summary with growth metrics."""
    query = """
    SELECT 
        d.year,
        ROUND(SUM(sf.sales), 2) AS yearly_revenue,
        COUNT(*) AS total_transactions,
        ROUND(AVG(sf.sales), 2) AS avg_transaction_value,
        ROUND(SUM(sf.quantity), 0) AS total_units_sold
    FROM sales_fact sf
    INNER JOIN dim_date d ON sf.date_key = d.date_key
    GROUP BY d.year
    ORDER BY d.year
    """
    return execute_query(query)


def get_month_over_month_growth() -> pd.DataFrame:
    """Calculate month-over-month revenue growth using window functions."""
    query = """
    WITH monthly_revenue AS (
        SELECT 
            d.year, d.month, d.month_name,
            ROUND(SUM(sf.sales), 2) AS revenue
        FROM sales_fact sf
        INNER JOIN dim_date d ON sf.date_key = d.date_key
        GROUP BY d.year, d.month, d.month_name
        ORDER BY d.year, d.month
    )
    SELECT 
        year, month, month_name, revenue,
        LAG(revenue) OVER (ORDER BY year, month) AS prev_month_revenue,
        ROUND((revenue - LAG(revenue) OVER (ORDER BY year, month)) / 
              NULLIF(LAG(revenue) OVER (ORDER BY year, month), 0) * 100, 2) AS mom_growth_pct
    FROM monthly_revenue
    """
    return execute_query(query)


def get_weekend_vs_weekday_sales() -> pd.DataFrame:
    """Compare weekend vs weekday sales performance."""
    query = """
    SELECT 
        CASE WHEN d.is_weekend = 1 THEN 'Weekend' ELSE 'Weekday' END AS day_type,
        ROUND(SUM(sf.sales), 2) AS total_revenue,
        COUNT(*) AS transaction_count,
        ROUND(AVG(sf.sales), 2) AS avg_transaction_value,
        ROUND(SUM(sf.quantity), 0) AS total_units_sold,
        ROUND(SUM(sf.sales) * 100.0 / (SELECT SUM(sales) FROM sales_fact), 2) AS revenue_contribution_pct
    FROM sales_fact sf
    INNER JOIN dim_date d ON sf.date_key = d.date_key
    GROUP BY d.is_weekend
    ORDER BY total_revenue DESC
    """
    return execute_query(query)


def get_daily_revenue_summary() -> pd.DataFrame:
    """Get daily revenue summary for detailed analysis."""
    query = """
    SELECT 
        d.full_date AS date_id, d.day_name, d.month_name, d.year,
        ROUND(SUM(sf.sales), 2) AS daily_revenue,
        COUNT(*) AS transaction_count,
        ROUND(AVG(sf.sales), 2) AS avg_transaction_value
    FROM sales_fact sf
    INNER JOIN dim_date d ON sf.date_key = d.date_key
    GROUP BY d.full_date, d.day_name, d.month_name, d.year
    ORDER BY d.full_date
    """
    return execute_query(query)


def get_quarterly_revenue() -> pd.DataFrame:
    """Get quarterly revenue summary with YoY comparison."""
    query = """
    SELECT 
        d.year, d.quarter,
        CONCAT('Q', d.quarter, ' ', d.year) AS quarter_label,
        ROUND(SUM(sf.sales), 2) AS quarterly_revenue,
        COUNT(*) AS transaction_count,
        ROUND(AVG(sf.sales), 2) AS avg_transaction_value,
        ROUND(SUM(sf.quantity), 0) AS total_units_sold
    FROM sales_fact sf
    INNER JOIN dim_date d ON sf.date_key = d.date_key
    GROUP BY d.year, d.quarter
    ORDER BY d.year, d.quarter
    """
    return execute_query(query)


def get_hourly_sales_pattern() -> pd.DataFrame:
    """Analyze sales patterns by hour of day."""
    query = """
    SELECT 
        HOUR(sf.order_date) AS hour_of_day,
        ROUND(SUM(sf.sales), 2) AS hourly_revenue,
        COUNT(*) AS transaction_count,
        ROUND(AVG(sf.sales), 2) AS avg_transaction_value,
        ROUND(SUM(sf.sales) * 100.0 / (SELECT SUM(sales) FROM sales_fact), 2) AS revenue_contribution_pct
    FROM sales_fact sf
    WHERE sf.order_date IS NOT NULL
    GROUP BY HOUR(sf.order_date)
    ORDER BY hour_of_day
    """
    return execute_query(query)
