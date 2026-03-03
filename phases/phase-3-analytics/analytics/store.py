"""
Store & Region Analytics Module.
Provides store performance, regional analysis, and geographic insights.

Note: Uses actual Phase 1 schema column names:
- sales_fact.sales (not sales_amount)
- sales_fact.date_key (not date_id)
- sales_fact.store_key (not store_id for FK)
- dim_store has region directly (no location_key join)
"""

import pandas as pd
from db.connection import execute_query


def get_store_revenue_ranking() -> pd.DataFrame:
    """Rank all stores by total revenue with performance metrics."""
    query = """
    WITH store_metrics AS (
        SELECT 
            s.store_id, s.store_name, s.region,
            ROUND(SUM(sf.sales), 2) AS total_revenue,
            SUM(sf.quantity) AS total_units_sold,
            COUNT(*) AS transaction_count,
            COUNT(DISTINCT sf.order_id) AS order_count,
            COUNT(DISTINCT sf.customer_key) AS unique_customers,
            ROUND(SUM(sf.profit), 2) AS total_profit,
            ROUND(AVG(sf.sales), 2) AS avg_transaction_value,
            ROUND(SUM(sf.profit) * 100.0 / NULLIF(SUM(sf.sales), 0), 2) AS profit_margin_pct
        FROM sales_fact sf
        INNER JOIN dim_store s ON sf.store_key = s.store_key
        GROUP BY s.store_id, s.store_name, s.region
    )
    SELECT 
        store_id, store_name, region,
        total_revenue, total_units_sold, transaction_count, order_count,
        unique_customers, total_profit, avg_transaction_value, profit_margin_pct,
        RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank,
        RANK() OVER (ORDER BY total_profit DESC) AS profit_rank,
        RANK() OVER (ORDER BY profit_margin_pct DESC) AS margin_rank
    FROM store_metrics
    ORDER BY total_revenue DESC
    """
    return execute_query(query)


def get_region_performance() -> pd.DataFrame:
    """Analyze performance by geographic region."""
    query = """
    WITH region_metrics AS (
        SELECT 
            s.region,
            COUNT(DISTINCT s.store_id) AS store_count,
            ROUND(SUM(sf.sales), 2) AS total_revenue,
            SUM(sf.quantity) AS total_units_sold,
            COUNT(*) AS transaction_count,
            COUNT(DISTINCT sf.customer_key) AS unique_customers,
            ROUND(SUM(sf.profit), 2) AS total_profit,
            ROUND(AVG(sf.sales), 2) AS avg_transaction_value,
            ROUND(SUM(sf.profit) * 100.0 / NULLIF(SUM(sf.sales), 0), 2) AS profit_margin_pct
        FROM sales_fact sf
        INNER JOIN dim_store s ON sf.store_key = s.store_key
        GROUP BY s.region
    ),
    total_metrics AS (
        SELECT 
            SUM(total_revenue) AS grand_total_revenue,
            SUM(store_count) AS total_stores
        FROM region_metrics
    )
    SELECT 
        rm.region, rm.store_count, rm.total_revenue, rm.total_units_sold,
        rm.transaction_count, rm.unique_customers, rm.total_profit,
        rm.avg_transaction_value, rm.profit_margin_pct,
        ROUND(rm.total_revenue * 100.0 / tm.grand_total_revenue, 2) AS revenue_share_pct,
        ROUND(rm.total_revenue / rm.store_count, 2) AS revenue_per_store,
        RANK() OVER (ORDER BY rm.total_revenue DESC) AS revenue_rank
    FROM region_metrics rm
    CROSS JOIN total_metrics tm
    ORDER BY rm.total_revenue DESC
    """
    return execute_query(query)


def get_underperforming_stores() -> pd.DataFrame:
    """Identify underperforming stores based on multiple KPIs."""
    query = """
    WITH store_stats AS (
        SELECT 
            s.store_id, s.store_name, s.region,
            ROUND(SUM(sf.sales), 2) AS total_revenue,
            ROUND(SUM(sf.profit), 2) AS total_profit,
            COUNT(*) AS transaction_count,
            ROUND(AVG(sf.sales), 2) AS avg_transaction_value,
            ROUND(SUM(sf.profit) * 100.0 / NULLIF(SUM(sf.sales), 0), 2) AS profit_margin_pct,
            COUNT(DISTINCT sf.customer_key) AS customer_count
        FROM sales_fact sf
        INNER JOIN dim_store s ON sf.store_key = s.store_key
        GROUP BY s.store_id, s.store_name, s.region
    ),
    averages AS (
        SELECT 
            AVG(total_revenue) AS avg_revenue,
            AVG(profit_margin_pct) AS avg_margin,
            AVG(transaction_count) AS avg_transactions,
            AVG(customer_count) AS avg_customers
        FROM store_stats
    )
    SELECT 
        ss.store_id, ss.store_name, ss.region,
        ss.total_revenue, ss.total_profit, ss.transaction_count,
        ss.avg_transaction_value, ss.profit_margin_pct, ss.customer_count,
        ROUND(a.avg_revenue, 2) AS avg_store_revenue,
        ROUND(a.avg_margin, 2) AS avg_store_margin,
        ROUND(ss.total_revenue - a.avg_revenue, 2) AS revenue_vs_avg,
        ROUND(ss.profit_margin_pct - a.avg_margin, 2) AS margin_vs_avg,
        CASE 
            WHEN ss.total_revenue < a.avg_revenue * 0.5 AND ss.profit_margin_pct < a.avg_margin THEN 'Critical'
            WHEN ss.total_revenue < a.avg_revenue * 0.7 THEN 'Underperforming'
            WHEN ss.profit_margin_pct < 0 OR ss.profit_margin_pct < a.avg_margin * 0.5 THEN 'Low Margin'
            WHEN ss.customer_count < a.avg_customers * 0.5 THEN 'Low Traffic'
            ELSE 'Normal'
        END AS performance_flag,
        CASE 
            WHEN ss.total_revenue < a.avg_revenue THEN 'Below Avg Revenue'
            WHEN ss.profit_margin_pct < a.avg_margin THEN 'Below Avg Margin'
            WHEN ss.customer_count < a.avg_customers THEN 'Below Avg Traffic'
            ELSE 'Other'
        END AS primary_issue
    FROM store_stats ss
    CROSS JOIN averages a
    WHERE ss.total_revenue < a.avg_revenue * 0.8 
       OR ss.profit_margin_pct < a.avg_margin * 0.8
       OR ss.profit_margin_pct < 0
    ORDER BY ss.total_revenue ASC
    """
    return execute_query(query)


def get_profit_margin_per_store() -> pd.DataFrame:
    """Analyze profit margins for each store with trend indicators."""
    query = """
    WITH store_profit AS (
        SELECT 
            s.store_id, s.store_name, s.region,
            ROUND(SUM(sf.sales), 2) AS total_revenue,
            ROUND(SUM(sf.profit), 2) AS total_profit,
            SUM(sf.quantity) AS total_units,
            COUNT(*) AS transaction_count,
            ROUND(SUM(sf.profit) * 100.0 / NULLIF(SUM(sf.sales), 0), 2) AS profit_margin_pct,
            ROUND(AVG(sf.profit), 2) AS avg_profit_per_transaction,
            ROUND(SUM(sf.sales) / SUM(sf.quantity), 2) AS avg_unit_price,
            ROUND(SUM(sf.profit) / SUM(sf.quantity), 2) AS avg_profit_per_unit
        FROM sales_fact sf
        INNER JOIN dim_store s ON sf.store_key = s.store_key
        GROUP BY s.store_id, s.store_name, s.region
    ),
    region_avg AS (
        SELECT region, AVG(profit_margin_pct) AS region_avg_margin
        FROM store_profit
        GROUP BY region
    )
    SELECT 
        sp.store_id, sp.store_name, sp.region,
        sp.total_revenue, sp.total_profit, sp.total_units, sp.transaction_count,
        sp.profit_margin_pct, sp.avg_profit_per_transaction,
        sp.avg_unit_price, sp.avg_profit_per_unit,
        ROUND(ra.region_avg_margin, 2) AS region_avg_margin,
        ROUND(sp.profit_margin_pct - ra.region_avg_margin, 2) AS margin_vs_region,
        CASE 
            WHEN sp.profit_margin_pct > ra.region_avg_margin + 5 THEN 'Above Region'
            WHEN sp.profit_margin_pct > ra.region_avg_margin - 5 THEN 'At Region Avg'
            ELSE 'Below Region'
        END AS margin_status,
        CASE 
            WHEN sp.total_profit < 0 THEN 'Loss Making'
            WHEN sp.profit_margin_pct < 10 THEN 'Low Margin'
            WHEN sp.profit_margin_pct < 20 THEN 'Moderate Margin'
            ELSE 'Healthy Margin'
        END AS margin_category
    FROM store_profit sp
    INNER JOIN region_avg ra ON sp.region = ra.region
    ORDER BY sp.profit_margin_pct DESC
    """
    return execute_query(query)


def get_store_monthly_trend() -> pd.DataFrame:
    """Track monthly revenue trend for each store."""
    query = """
    SELECT 
        s.store_id, s.store_name, s.region,
        d.year, d.month, d.month_name,
        ROUND(SUM(sf.sales), 2) AS monthly_revenue,
        SUM(sf.quantity) AS units_sold,
        COUNT(*) AS transaction_count,
        ROUND(SUM(sf.profit), 2) AS monthly_profit,
        ROUND(SUM(sf.profit) * 100.0 / NULLIF(SUM(sf.sales), 0), 2) AS profit_margin_pct
    FROM sales_fact sf
    INNER JOIN dim_store s ON sf.store_key = s.store_key
    INNER JOIN dim_date d ON sf.date_key = d.date_key
    GROUP BY s.store_id, s.store_name, s.region, d.year, d.month, d.month_name
    ORDER BY s.store_id, d.year, d.month
    """
    return execute_query(query)


def get_state_performance() -> pd.DataFrame:
    """Analyze performance at state level using customer location."""
    query = """
    SELECT 
        l.state, l.country,
        COUNT(DISTINCT s.store_id) AS store_count,
        COUNT(DISTINCT sf.customer_key) AS unique_customers,
        ROUND(SUM(sf.sales), 2) AS total_revenue,
        SUM(sf.quantity) AS total_units_sold,
        COUNT(*) AS transaction_count,
        ROUND(SUM(sf.profit), 2) AS total_profit,
        ROUND(AVG(sf.sales), 2) AS avg_transaction_value,
        ROUND(SUM(sf.profit) * 100.0 / NULLIF(SUM(sf.sales), 0), 2) AS profit_margin_pct,
        ROUND(SUM(sf.sales) / COUNT(DISTINCT s.store_id), 2) AS revenue_per_store,
        RANK() OVER (ORDER BY SUM(sf.sales) DESC) AS revenue_rank
    FROM sales_fact sf
    INNER JOIN dim_store s ON sf.store_key = s.store_key
    INNER JOIN dim_location l ON sf.location_key = l.location_key
    GROUP BY l.state, l.country
    ORDER BY total_revenue DESC
    """
    return execute_query(query)


def get_city_analysis() -> pd.DataFrame:
    """Detailed city-level performance analysis."""
    query = """
    SELECT 
        l.city, l.state, l.country,
        COUNT(DISTINCT s.store_id) AS store_count,
        COUNT(DISTINCT sf.customer_key) AS unique_customers,
        ROUND(SUM(sf.sales), 2) AS total_revenue,
        SUM(sf.quantity) AS total_units_sold,
        ROUND(SUM(sf.profit), 2) AS total_profit,
        ROUND(AVG(sf.sales), 2) AS avg_transaction_value,
        ROUND(SUM(sf.profit) * 100.0 / NULLIF(SUM(sf.sales), 0), 2) AS profit_margin_pct,
        ROUND(SUM(sf.sales) / COUNT(DISTINCT sf.customer_key), 2) AS revenue_per_customer
    FROM sales_fact sf
    INNER JOIN dim_store s ON sf.store_key = s.store_key
    INNER JOIN dim_location l ON sf.location_key = l.location_key
    GROUP BY l.city, l.state, l.country
    HAVING COUNT(DISTINCT s.store_id) >= 1
    ORDER BY total_revenue DESC
    LIMIT 50
    """
    return execute_query(query)


def get_store_category_performance() -> pd.DataFrame:
    """Analyze which product categories perform best at each store."""
    query = """
    SELECT 
        s.store_name, s.region, p.category,
        ROUND(SUM(sf.sales), 2) AS category_revenue,
        SUM(sf.quantity) AS category_units,
        ROUND(SUM(sf.profit), 2) AS category_profit,
        COUNT(*) AS transaction_count,
        ROUND(SUM(sf.profit) * 100.0 / NULLIF(SUM(sf.sales), 0), 2) AS category_margin_pct,
        RANK() OVER (PARTITION BY s.store_id ORDER BY SUM(sf.sales) DESC) AS category_rank_in_store
    FROM sales_fact sf
    INNER JOIN dim_store s ON sf.store_key = s.store_key
    INNER JOIN dim_product p ON sf.product_key = p.product_key
    GROUP BY s.store_id, s.store_name, s.region, p.category
    ORDER BY s.store_name, category_revenue DESC
    """
    return execute_query(query)
