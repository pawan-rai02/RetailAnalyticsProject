"""Analytics modules for retail KPIs."""

from .revenue import (
    get_total_revenue,
    get_monthly_revenue_trend,
    get_yearly_revenue,
    get_month_over_month_growth,
    get_weekend_vs_weekday_sales,
    get_daily_revenue_summary,
    get_quarterly_revenue,
    get_hourly_sales_pattern
)

from .product import (
    get_top_10_products_by_revenue,
    get_top_10_products_by_quantity,
    get_category_contribution_percentage,
    get_worst_10_products,
    get_subcategory_performance,
    get_product_profit_analysis,
    get_category_trend_over_time,
    get_product_affinity_analysis
)

from .customer import (
    get_customer_lifetime_value,
    get_top_10_customers,
    get_repeat_vs_new_customer_ratio,
    get_average_revenue_per_customer,
    get_customer_segmentation,
    get_customer_cohort_analysis,
    get_customer_churn_indicators
)

from .store import (
    get_store_revenue_ranking,
    get_region_performance,
    get_underperforming_stores,
    get_profit_margin_per_store,
    get_store_monthly_trend,
    get_state_performance,
    get_city_analysis,
    get_store_category_performance
)

__all__ = [
    # Revenue
    "get_total_revenue",
    "get_monthly_revenue_trend",
    "get_yearly_revenue",
    "get_month_over_month_growth",
    "get_weekend_vs_weekday_sales",
    "get_daily_revenue_summary",
    "get_quarterly_revenue",
    "get_hourly_sales_pattern",
    # Product
    "get_top_10_products_by_revenue",
    "get_top_10_products_by_quantity",
    "get_category_contribution_percentage",
    "get_worst_10_products",
    "get_subcategory_performance",
    "get_product_profit_analysis",
    "get_category_trend_over_time",
    "get_product_affinity_analysis",
    # Customer
    "get_customer_lifetime_value",
    "get_top_10_customers",
    "get_repeat_vs_new_customer_ratio",
    "get_average_revenue_per_customer",
    "get_customer_segmentation",
    "get_customer_cohort_analysis",
    "get_customer_churn_indicators",
    # Store
    "get_store_revenue_ranking",
    "get_region_performance",
    "get_underperforming_stores",
    "get_profit_margin_per_store",
    "get_store_monthly_trend",
    "get_state_performance",
    "get_city_analysis",
    "get_store_category_performance"
]
