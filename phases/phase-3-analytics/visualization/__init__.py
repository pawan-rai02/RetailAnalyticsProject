"""Visualization module for retail analytics."""

from .plots import (
    setup_style,
    plot_monthly_revenue,
    plot_yearly_revenue,
    plot_weekend_vs_weekday,
    plot_top_products,
    plot_category_contribution,
    plot_clv_distribution,
    plot_top_customers,
    plot_store_ranking,
    plot_region_performance,
    save_plot,
    show_plot,
    COLOR_PALETTE,
    REVENUE_COLORS,
    CATEGORY_COLORS
)

__all__ = [
    "setup_style",
    "plot_monthly_revenue",
    "plot_yearly_revenue",
    "plot_weekend_vs_weekday",
    "plot_top_products",
    "plot_category_contribution",
    "plot_clv_distribution",
    "plot_top_customers",
    "plot_store_ranking",
    "plot_region_performance",
    "save_plot",
    "show_plot",
    "COLOR_PALETTE",
    "REVENUE_COLORS",
    "CATEGORY_COLORS"
]
