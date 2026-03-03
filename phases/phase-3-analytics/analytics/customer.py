"""
Customer Analytics Module.
Provides customer-related KPIs, segmentation, and lifetime value metrics.

Note: Uses actual Phase 1 schema column names:
- sales_fact.sales (not sales_amount)
- sales_fact.date_key (not date_id)
- sales_fact.customer_key (not customer_id for FK)
"""

import pandas as pd
from db.connection import execute_query


def get_customer_lifetime_value() -> pd.DataFrame:
    """Calculate Customer Lifetime Value (CLV) for all customers."""
    query = """
    WITH customer_metrics AS (
        SELECT 
            c.customer_id,
            c.customer_name,
            c.segment,
            COUNT(DISTINCT sf.order_id) AS total_orders,
            SUM(sf.quantity) AS total_items_purchased,
            ROUND(SUM(sf.sales), 2) AS total_revenue,
            ROUND(SUM(sf.profit), 2) AS total_profit_contribution,
            MIN(d.full_date) AS first_purchase_date,
            MAX(d.full_date) AS last_purchase_date,
            ROUND(AVG(sf.sales), 2) AS avg_order_value,
            DATEDIFF(MAX(d.full_date), MIN(d.full_date)) AS customer_tenure_days
        FROM sales_fact sf
        INNER JOIN dim_customer c ON sf.customer_key = c.customer_key
        INNER JOIN dim_date d ON sf.date_key = d.date_key
        GROUP BY c.customer_id, c.customer_name, c.segment
    )
    SELECT 
        customer_id, customer_name, segment,
        total_orders, total_items_purchased, total_revenue, total_profit_contribution,
        first_purchase_date, last_purchase_date, avg_order_value, customer_tenure_days,
        CASE 
            WHEN customer_tenure_days > 0 
            THEN ROUND(total_revenue / (customer_tenure_days / 30.0), 2)
            ELSE total_revenue
        END AS monthly_clv_estimate,
        CASE 
            WHEN total_orders >= 5 AND total_revenue >= 1000 THEN 'Platinum'
            WHEN total_orders >= 3 AND total_revenue >= 500 THEN 'Gold'
            WHEN total_orders >= 2 AND total_revenue >= 200 THEN 'Silver'
            ELSE 'Bronze'
        END AS customer_tier
    FROM customer_metrics
    ORDER BY total_revenue DESC
    """
    return execute_query(query)


def get_top_10_customers() -> pd.DataFrame:
    """Get top 10 customers by total revenue contribution."""
    query = """
    SELECT 
        c.customer_id, c.customer_name, c.segment,
        ROUND(SUM(sf.sales), 2) AS total_revenue,
        COUNT(DISTINCT sf.order_id) AS total_orders,
        SUM(sf.quantity) AS total_items,
        ROUND(AVG(sf.sales), 2) AS avg_order_value,
        ROUND(SUM(sf.profit), 2) AS profit_contribution,
        COUNT(DISTINCT sf.product_key) AS unique_products_bought,
        ROUND(SUM(sf.sales) * 100.0 / (SELECT SUM(sales) FROM sales_fact), 2) AS revenue_contribution_pct,
        MIN(d.full_date) AS first_purchase,
        MAX(d.full_date) AS last_purchase
    FROM sales_fact sf
    INNER JOIN dim_customer c ON sf.customer_key = c.customer_key
    INNER JOIN dim_date d ON sf.date_key = d.date_key
    GROUP BY c.customer_id, c.customer_name, c.segment
    ORDER BY total_revenue DESC
    LIMIT 10
    """
    return execute_query(query)


def get_repeat_vs_new_customer_ratio() -> pd.DataFrame:
    """Analyze repeat customers vs new customers over time."""
    query = """
    WITH customer_first_purchase AS (
        SELECT 
            sf.customer_key,
            MIN(d.full_date) AS first_purchase_date
        FROM sales_fact sf
        INNER JOIN dim_date d ON sf.date_key = d.date_key
        GROUP BY sf.customer_key
    ),
    monthly_customer_type AS (
        SELECT 
            d.year, d.month, d.month_name,
            sf.customer_key,
            CASE 
                WHEN d.full_date = cfp.first_purchase_date THEN 'New'
                ELSE 'Repeat'
            END AS customer_type
        FROM sales_fact sf
        INNER JOIN dim_date d ON sf.date_key = d.date_key
        INNER JOIN customer_first_purchase cfp ON sf.customer_key = cfp.customer_key
    )
    SELECT 
        year, month, month_name, customer_type,
        COUNT(DISTINCT customer_key) AS customer_count
    FROM monthly_customer_type
    GROUP BY year, month, month_name, customer_type
    ORDER BY year, month, customer_type
    """
    return execute_query(query)


def get_average_revenue_per_customer() -> pd.DataFrame:
    """Calculate average revenue per customer with segment breakdown."""
    query = """
    SELECT 
        'Overall' AS segment,
        COUNT(DISTINCT sf.customer_key) AS total_customers,
        ROUND(SUM(sf.sales), 2) AS total_revenue,
        ROUND(SUM(sf.sales) / COUNT(DISTINCT sf.customer_key), 2) AS avg_revenue_per_customer,
        ROUND(AVG(sf.sales), 2) AS avg_order_value,
        COUNT(*) AS total_transactions
    FROM sales_fact sf
    
    UNION ALL
    
    SELECT 
        c.segment,
        COUNT(DISTINCT sf.customer_key) AS total_customers,
        ROUND(SUM(sf.sales), 2) AS total_revenue,
        ROUND(SUM(sf.sales) / COUNT(DISTINCT sf.customer_key), 2) AS avg_revenue_per_customer,
        ROUND(AVG(sf.sales), 2) AS avg_order_value,
        COUNT(*) AS total_transactions
    FROM sales_fact sf
    INNER JOIN dim_customer c ON sf.customer_key = c.customer_key
    GROUP BY c.segment
    ORDER BY avg_revenue_per_customer DESC
    """
    return execute_query(query)


def get_customer_segmentation() -> pd.DataFrame:
    """RFM (Recency, Frequency, Monetary) customer segmentation."""
    query = """
    WITH rfm_base AS (
        SELECT 
            c.customer_id, c.customer_name, c.segment,
            MAX(d.full_date) AS last_purchase_date,
            COUNT(DISTINCT sf.order_id) AS frequency,
            ROUND(SUM(sf.sales), 2) AS monetary
        FROM sales_fact sf
        INNER JOIN dim_customer c ON sf.customer_key = c.customer_key
        INNER JOIN dim_date d ON sf.date_key = d.date_key
        GROUP BY c.customer_id, c.customer_name, c.segment
    ),
    rfm_scores AS (
        SELECT 
            customer_id, customer_name, segment, last_purchase_date, frequency, monetary,
            DATEDIFF(CURDATE(), last_purchase_date) AS recency_days,
            NTILE(4) OVER (ORDER BY DATEDIFF(CURDATE(), last_purchase_date) DESC) AS r_score,
            NTILE(4) OVER (ORDER BY frequency ASC) AS f_score,
            NTILE(4) OVER (ORDER BY monetary ASC) AS m_score
        FROM rfm_base
    )
    SELECT 
        customer_id, customer_name, segment, last_purchase_date, recency_days, frequency, monetary,
        r_score, f_score, m_score,
        (r_score + f_score + m_score) AS rfm_total_score,
        CONCAT(r_score, f_score, m_score) AS rfm_code,
        CASE 
            WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 2 AND m_score >= 2 THEN 'Loyal Customers'
            WHEN r_score >= 3 AND f_score = 1 AND m_score = 1 THEN 'New Customers'
            WHEN r_score = 1 AND f_score >= 2 AND m_score >= 2 THEN 'At Risk'
            WHEN r_score = 1 AND f_score = 1 AND m_score = 1 THEN 'Lost'
            ELSE 'Regular'
        END AS customer_segment
    FROM rfm_scores
    ORDER BY rfm_total_score DESC, monetary DESC
    """
    return execute_query(query)


def get_customer_cohort_analysis() -> pd.DataFrame:
    """Cohort analysis - track customer retention by acquisition month."""
    query = """
    WITH customer_cohort AS (
        SELECT 
            sf.customer_key,
            MIN(d.full_date) AS cohort_date,
            DATE_FORMAT(MIN(d.full_date), '%Y-%m') AS cohort_month
        FROM sales_fact sf
        INNER JOIN dim_date d ON sf.date_key = d.date_key
        GROUP BY sf.customer_key
    ),
    cohort_purchases AS (
        SELECT 
            cc.cohort_month, d.year, d.month,
            COUNT(DISTINCT sf.customer_key) AS active_customers,
            ROUND(SUM(sf.sales), 2) AS cohort_revenue
        FROM customer_cohort cc
        INNER JOIN sales_fact sf ON cc.customer_key = sf.customer_key
        INNER JOIN dim_date d ON sf.date_key = d.date_key
        GROUP BY cc.cohort_month, d.year, d.month
    )
    SELECT 
        cohort_month, year, month, active_customers, cohort_revenue,
        ROW_NUMBER() OVER (PARTITION BY cohort_month ORDER BY year, month) AS months_since_acquisition
    FROM cohort_purchases
    ORDER BY cohort_month, year, month
    """
    return execute_query(query)


def get_customer_churn_indicators() -> pd.DataFrame:
    """Identify customers showing churn indicators."""
    query = """
    WITH customer_activity AS (
        SELECT 
            c.customer_id, c.customer_name, c.segment,
            MAX(d.full_date) AS last_purchase_date,
            DATEDIFF(CURDATE(), MAX(d.full_date)) AS days_since_last_purchase,
            COUNT(DISTINCT sf.order_id) AS total_orders,
            ROUND(SUM(sf.sales), 2) AS total_spent,
            ROUND(AVG(sf.sales), 2) AS avg_order_value
        FROM sales_fact sf
        INNER JOIN dim_customer c ON sf.customer_key = c.customer_key
        INNER JOIN dim_date d ON sf.date_key = d.date_key
        GROUP BY c.customer_id, c.customer_name, c.segment
    )
    SELECT 
        customer_id, customer_name, segment,
        last_purchase_date, days_since_last_purchase,
        total_orders, total_spent, avg_order_value,
        CASE 
            WHEN days_since_last_purchase > 90 THEN 'High Churn Risk'
            WHEN days_since_last_purchase > 60 THEN 'Medium Churn Risk'
            WHEN days_since_last_purchase > 30 THEN 'Low Churn Risk'
            ELSE 'Active'
        END AS churn_risk,
        CASE 
            WHEN days_since_last_purchase > 90 AND total_spent > 500 THEN 'High Value At Risk'
            WHEN days_since_last_purchase > 60 AND total_spent > 200 THEN 'Medium Value At Risk'
            ELSE 'Normal'
        END AS priority_level
    FROM customer_activity
    WHERE days_since_last_purchase > 30
    ORDER BY total_spent DESC, days_since_last_purchase DESC
    """
    return execute_query(query)
