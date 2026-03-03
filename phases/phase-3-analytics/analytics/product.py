"""
Product Analytics Module.
Provides product-related KPIs and performance metrics.

Note: Uses actual Phase 1 schema column names:
- sales_fact.sales (not sales_amount)
- sales_fact.date_key (not date_id)
- dim_product.product_key (not product_id for FK)
"""

import pandas as pd
from db.connection import execute_query


def get_top_10_products_by_revenue() -> pd.DataFrame:
    """Get top 10 products by total revenue generated."""
    query = """
    SELECT 
        p.product_id,
        p.product_name,
        p.category,
        p.sub_category,
        ROUND(SUM(sf.sales), 2) AS total_revenue,
        SUM(sf.quantity) AS total_quantity_sold,
        COUNT(DISTINCT sf.customer_key) AS unique_customers,
        ROUND(SUM(sf.sales) / NULLIF(SUM(sf.quantity), 0), 2) AS avg_unit_price,
        ROUND(SUM(sf.profit), 2) AS total_profit,
        ROUND(AVG(sf.profit) / NULLIF(AVG(sf.sales), 0) * 100, 2) AS avg_profit_margin_pct
    FROM sales_fact sf
    INNER JOIN dim_product p ON sf.product_key = p.product_key
    GROUP BY p.product_id, p.product_name, p.category, p.sub_category
    ORDER BY total_revenue DESC
    LIMIT 10
    """
    return execute_query(query)


def get_top_10_products_by_quantity() -> pd.DataFrame:
    """Get top 10 products by total quantity sold."""
    query = """
    SELECT 
        p.product_id,
        p.product_name,
        p.category,
        p.sub_category,
        SUM(sf.quantity) AS total_quantity_sold,
        ROUND(SUM(sf.sales), 2) AS total_revenue,
        COUNT(DISTINCT sf.order_id) AS order_count,
        ROUND(SUM(sf.profit), 2) AS total_profit,
        ROUND(AVG(sf.profit) / NULLIF(AVG(sf.sales), 0) * 100, 2) AS avg_profit_margin_pct
    FROM sales_fact sf
    INNER JOIN dim_product p ON sf.product_key = p.product_key
    GROUP BY p.product_id, p.product_name, p.category, p.sub_category
    ORDER BY total_quantity_sold DESC
    LIMIT 10
    """
    return execute_query(query)


def get_category_contribution_percentage() -> pd.DataFrame:
    """Calculate each category's contribution to total revenue."""
    query = """
    WITH category_totals AS (
        SELECT 
            p.category,
            ROUND(SUM(sf.sales), 2) AS category_revenue,
            SUM(sf.quantity) AS total_quantity,
            COUNT(*) AS transaction_count,
            ROUND(SUM(sf.profit), 2) AS total_profit
        FROM sales_fact sf
        INNER JOIN dim_product p ON sf.product_key = p.product_key
        GROUP BY p.category
    ),
    total_revenue AS (
        SELECT SUM(category_revenue) AS grand_total FROM category_totals
    )
    SELECT 
        ct.category,
        ct.category_revenue,
        ct.total_quantity,
        ct.transaction_count,
        ct.total_profit,
        ROUND(ct.category_revenue * 100.0 / tr.grand_total, 2) AS revenue_contribution_pct,
        RANK() OVER (ORDER BY ct.category_revenue DESC) AS revenue_rank
    FROM category_totals ct
    CROSS JOIN total_revenue tr
    ORDER BY ct.category_revenue DESC
    """
    return execute_query(query)


def get_worst_10_products() -> pd.DataFrame:
    """Get bottom 10 products by revenue."""
    query = """
    SELECT 
        p.product_id,
        p.product_name,
        p.category,
        p.sub_category,
        ROUND(SUM(sf.sales), 2) AS total_revenue,
        SUM(sf.quantity) AS total_quantity_sold,
        COUNT(DISTINCT sf.order_id) AS order_count,
        ROUND(SUM(sf.profit), 2) AS total_profit,
        ROUND(AVG(sf.profit) / NULLIF(AVG(sf.sales), 0) * 100, 2) AS avg_profit_margin_pct,
        COUNT(*) AS transaction_count
    FROM sales_fact sf
    INNER JOIN dim_product p ON sf.product_key = p.product_key
    GROUP BY p.product_id, p.product_name, p.category, p.sub_category
    HAVING SUM(sf.sales) > 0
    ORDER BY total_revenue ASC
    LIMIT 10
    """
    return execute_query(query)


def get_subcategory_performance() -> pd.DataFrame:
    """Analyze performance at subcategory level."""
    query = """
    SELECT 
        p.category, p.sub_category,
        ROUND(SUM(sf.sales), 2) AS total_revenue,
        SUM(sf.quantity) AS total_quantity,
        COUNT(*) AS transaction_count,
        ROUND(SUM(sf.profit), 2) AS total_profit,
        ROUND(AVG(sf.sales), 2) AS avg_transaction_value,
        ROUND(SUM(sf.profit) * 100.0 / NULLIF(SUM(sf.sales), 0), 2) AS profit_margin_pct,
        COUNT(DISTINCT p.product_id) AS product_count
    FROM sales_fact sf
    INNER JOIN dim_product p ON sf.product_key = p.product_key
    GROUP BY p.category, p.sub_category
    ORDER BY p.category, total_revenue DESC
    """
    return execute_query(query)


def get_product_profit_analysis() -> pd.DataFrame:
    """Analyze products by profitability."""
    query = """
    SELECT 
        p.product_id, p.product_name, p.category, p.sub_category,
        ROUND(SUM(sf.sales), 2) AS total_revenue,
        ROUND(SUM(sf.profit), 2) AS total_profit,
        SUM(sf.quantity) AS total_quantity,
        ROUND(SUM(sf.profit) * 100.0 / NULLIF(SUM(sf.sales), 0), 2) AS profit_margin_pct,
        CASE 
            WHEN SUM(sf.profit) < 0 THEN 'Loss Maker'
            WHEN SUM(sf.profit) = 0 THEN 'Break Even'
            ELSE 'Profitable'
        END AS profitability_status
    FROM sales_fact sf
    INNER JOIN dim_product p ON sf.product_key = p.product_key
    GROUP BY p.product_id, p.product_name, p.category, p.sub_category
    ORDER BY profit_margin_pct ASC
    """
    return execute_query(query)


def get_category_trend_over_time() -> pd.DataFrame:
    """Track category performance over time."""
    query = """
    SELECT 
        d.year, d.month, d.month_name, p.category,
        ROUND(SUM(sf.sales), 2) AS category_revenue,
        SUM(sf.quantity) AS quantity_sold,
        ROUND(SUM(sf.profit), 2) AS category_profit
    FROM sales_fact sf
    INNER JOIN dim_product p ON sf.product_key = p.product_key
    INNER JOIN dim_date d ON sf.date_key = d.date_key
    GROUP BY d.year, d.month, d.month_name, p.category
    ORDER BY d.year, d.month, category_revenue DESC
    """
    return execute_query(query)


def get_product_affinity_analysis() -> pd.DataFrame:
    """Analyze products frequently bought together."""
    query = """
    SELECT 
        p1.product_name AS product_1,
        p2.product_name AS product_2,
        p1.category AS category_1,
        p2.category AS category_2,
        COUNT(DISTINCT sf1.order_id) AS times_bought_together,
        ROUND(SUM(sf1.sales + sf2.sales), 2) AS combined_revenue
    FROM sales_fact sf1
    INNER JOIN sales_fact sf2 ON sf1.order_id = sf2.order_id 
        AND sf1.product_key < sf2.product_key
    INNER JOIN dim_product p1 ON sf1.product_key = p1.product_key
    INNER JOIN dim_product p2 ON sf2.product_key = p2.product_key
    GROUP BY p1.product_name, p2.product_name, p1.category, p2.category
    HAVING COUNT(DISTINCT sf1.order_id) >= 2
    ORDER BY times_bought_together DESC
    LIMIT 20
    """
    return execute_query(query)
