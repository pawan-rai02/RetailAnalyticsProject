"""
Visualization Module for Retail Analytics.
Professional, publication-quality charts using Matplotlib and Seaborn.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import seaborn as sns
from typing import Optional, Tuple
import os
from datetime import datetime


# =============================================================================
# STYLE CONFIGURATION
# =============================================================================

def setup_style() -> None:
    """Configure matplotlib and seaborn for professional-looking plots."""
    plt.style.use('seaborn-v0_8-whitegrid')
    
    sns.set_palette("husl")
    sns.set_style("whitegrid")
    
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.facecolor'] = 'white'
    plt.rcParams['axes.edgecolor'] = '#E0E0E0'
    plt.rcParams['grid.color'] = '#F0F0F0'
    plt.rcParams['axes.linewidth'] = 0.8
    
    plt.rcParams['font.family'] = 'Segoe UI' if os.name == 'nt' else 'sans-serif'
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.labelsize'] = 11
    plt.rcParams['xtick.labelsize'] = 9
    plt.rcParams['ytick.labelsize'] = 9
    plt.rcParams['legend.fontsize'] = 9
    
    plt.rcParams['lines.linewidth'] = 2
    plt.rcParams['lines.markersize'] = 6
    plt.rcParams['patch.linewidth'] = 1.5
    
    plt.rcParams['figure.figsize'] = (12, 7)
    plt.rcParams['figure.dpi'] = 120
    plt.rcParams['savefig.dpi'] = 150
    plt.rcParams['savefig.bbox'] = 'tight'


# Color palettes for different chart types
COLOR_PALETTE = {
    'primary': '#2E86AB',
    'secondary': '#A23B72', 
    'accent': '#F18F01',
    'success': '#2ECC71',
    'warning': '#F39C12',
    'danger': '#E74C3C',
    'info': '#3498DB',
    'neutral': '#95A5A6'
}

REVENUE_COLORS = ['#2E86AB', '#A23B72', '#F18F01', '#2ECC71', '#E74C3C', '#3498DB', '#9B59B6', '#1ABC9C']
CATEGORY_COLORS = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9']


# =============================================================================
# REVENUE VISUALIZATIONS
# =============================================================================

def plot_monthly_revenue(df: pd.DataFrame, save_path: Optional[str] = None, 
                         figsize: Tuple[int, int] = (14, 7)) -> plt.Figure:
    """
    Create a professional line chart showing monthly revenue trend.
    
    Args:
        df: DataFrame with columns: year, month, month_name, monthly_revenue
        save_path: Optional path to save the figure
        figsize: Figure dimensions (width, height)
    
    Returns:
        plt.Figure: The created figure
    """
    setup_style()
    
    fig = plt.figure(figsize=figsize)
    gs = GridSpec(2, 2, figure=fig, height_ratios=[1, 0.3])
    ax = fig.add_subplot(gs[0, :])
    
    # Prepare data
    df = df.copy()
    df['period'] = df['month_name'].astype(str) + ' ' + df['year'].astype(str)
    df['period_num'] = range(len(df))
    
    # Create gradient fill
    colors = plt.cm.Blues(np.linspace(0.3, 0.8, len(df)))
    
    # Main line plot with area fill
    ax.plot(df['period_num'], df['monthly_revenue'], 
            color=COLOR_PALETTE['primary'], linewidth=2.5, marker='o', 
            markersize=6, markerfacecolor='white', markeredgewidth=1.5,
            label='Monthly Revenue')
    
    # Fill area under curve with gradient
    ax.fill_between(df['period_num'], df['monthly_revenue'], alpha=0.3, 
                    color=COLOR_PALETTE['primary'])
    
    # Add value labels on points
    for idx, row in df.iterrows():
        ax.annotate(f'${row["monthly_revenue"]:,.0f}', 
                   (row['period_num'], row['monthly_revenue']),
                   ha='center', va='bottom', fontsize=8, 
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                            edgecolor='none', alpha=0.7))
    
    # Styling
    ax.set_xlabel('Period', fontsize=11, fontweight='bold')
    ax.set_ylabel('Revenue ($)', fontsize=11, fontweight='bold')
    ax.set_title('Monthly Revenue Trend Analysis', fontsize=14, fontweight='bold', pad=15)
    
    ax.set_xticks(df['period_num'])
    ax.set_xticklabels(df['period'], rotation=45, ha='right')
    
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#E0E0E0')
    ax.spines['bottom'].set_color('#E0E0E0')
    
    # Add summary stats panel
    stats_ax = fig.add_subplot(gs[1, 0])
    stats_ax.axis('off')
    
    total_revenue = df['monthly_revenue'].sum()
    avg_revenue = df['monthly_revenue'].mean()
    max_revenue = df['monthly_revenue'].max()
    growth = ((df['monthly_revenue'].iloc[-1] - df['monthly_revenue'].iloc[0]) / 
              df['monthly_revenue'].iloc[0] * 100)
    
    stats_text = (
        f"📊 Revenue Summary\n\n"
        f"Total: ${total_revenue:,.0f}\n"
        f"Average: ${avg_revenue:,.0f}/month\n"
        f"Peak: ${max_revenue:,.0f}\n"
        f"Growth: {'+' if growth > 0 else ''}{growth:.1f}%"
    )
    stats_ax.text(0, 0.5, stats_text, fontsize=10, verticalalignment='center',
                 fontfamily='monospace',
                 bbox=dict(boxstyle='round', facecolor='#F8F9FA', edgecolor='#E0E0E0'))
    
    # Trend indicator
    trend_ax = fig.add_subplot(gs[1, 1])
    trend_ax.axis('off')
    
    if growth > 5:
        trend_text = "📈 Strong Growth"
        trend_color = COLOR_PALETTE['success']
    elif growth > 0:
        trend_text = "📈 Positive Growth"
        trend_color = COLOR_PALETTE['info']
    else:
        trend_text = "📉 Declining"
        trend_color = COLOR_PALETTE['danger']
    
    trend_ax.text(0.5, 0.5, trend_text, fontsize=12, fontweight='bold',
                 color=trend_color, ha='center', va='center',
                 bbox=dict(boxstyle='round', facecolor='#F8F9FA', edgecolor=trend_color))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig


def plot_yearly_revenue(df: pd.DataFrame, save_path: Optional[str] = None,
                        figsize: Tuple[int, int] = (12, 6)) -> plt.Figure:
    """
    Create a bar chart showing yearly revenue comparison.
    
    Args:
        df: DataFrame with columns: year, yearly_revenue, total_transactions
        save_path: Optional path to save the figure
        figsize: Figure dimensions
    """
    setup_style()
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Create bars with gradient
    bars = ax.bar(df['year'].astype(str), df['yearly_revenue'],
                  color=REVENUE_COLORS[:len(df)], edgecolor='white', linewidth=2)
    
    # Add value labels
    for bar, revenue in zip(bars, df['yearly_revenue']):
        height = bar.get_height()
        ax.annotate(f'${revenue:,.0f}',
                   xy=(bar.get_x() + bar.get_width() / 2, height),
                   xytext=(0, 3), textcoords='offset points',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('Year', fontsize=11, fontweight='bold')
    ax.set_ylabel('Revenue ($)', fontsize=11, fontweight='bold')
    ax.set_title('Yearly Revenue Comparison', fontsize=14, fontweight='bold', pad=15)
    
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig


def plot_weekend_vs_weekday(df: pd.DataFrame, save_path: Optional[str] = None,
                            figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
    """
    Create a comparison chart for weekend vs weekday sales.
    
    Args:
        df: DataFrame with columns: day_type, total_revenue, revenue_contribution_pct
    """
    setup_style()
    
    fig, axes = plt.subplots(1, 2, figsize=figsize)
    
    # Revenue comparison
    colors = [COLOR_PALETTE['info'], COLOR_PALETTE['accent']]
    bars1 = axes[0].bar(df['day_type'], df['total_revenue'], 
                        color=colors, edgecolor='white', linewidth=2)
    
    for bar, revenue in zip(bars1, df['total_revenue']):
        height = bar.get_height()
        axes[0].annotate(f'${revenue:,.0f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3), textcoords='offset points',
                        ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    axes[0].set_xlabel('Day Type', fontweight='bold')
    axes[0].set_ylabel('Revenue ($)', fontweight='bold')
    axes[0].set_title('Revenue: Weekend vs Weekday', fontweight='bold')
    axes[0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # Contribution percentage (pie chart style)
    wedges, texts, autotexts = axes[1].pie(df['revenue_contribution_pct'],
                                           labels=df['day_type'],
                                           colors=colors,
                                           autopct='%1.1f%%',
                                           explode=(0.05, 0),
                                           shadow=True)
    axes[1].set_title('Revenue Contribution', fontweight='bold')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig


# =============================================================================
# PRODUCT VISUALIZATIONS
# =============================================================================

def plot_top_products(df: pd.DataFrame, save_path: Optional[str] = None,
                      figsize: Tuple[int, int] = (12, 8)) -> plt.Figure:
    """
    Create a horizontal bar chart showing top products by revenue.
    
    Args:
        df: DataFrame with columns: product_name, total_revenue, category
    """
    setup_style()
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Reverse for better visualization (top at top)
    df = df.iloc[::-1].copy()
    
    # Create color mapping by category
    categories = df['category'].unique()
    category_colors = dict(zip(categories, CATEGORY_COLORS[:len(categories)]))
    colors = [category_colors.get(cat, COLOR_PALETTE['neutral']) for cat in df['category']]
    
    # Horizontal bars
    bars = ax.barh(df['product_name'], df['total_revenue'], color=colors, 
                   edgecolor='white', linewidth=1.5)
    
    # Add value labels
    for bar, revenue in zip(bars, df['total_revenue']):
        width = bar.get_width()
        ax.annotate(f'${revenue:,.0f}',
                   xy=(width, bar.get_y() + bar.get_height() / 2),
                   xytext=(5, 0), textcoords='offset points',
                   ha='left', va='center', fontsize=9, fontweight='bold')
    
    ax.set_xlabel('Revenue ($)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Product', fontsize=11, fontweight='bold')
    ax.set_title('Top 10 Products by Revenue', fontsize=14, fontweight='bold', pad=15)

    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Add category legend
    legend_elements = [mpatches.Patch(color=cat_color, label=cat)
                      for cat, cat_color in category_colors.items()]
    ax.legend(handles=legend_elements, loc='lower right', title='Category',
             title_fontsize=11, framealpha=0.9, fontsize=9)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')

    return fig


def plot_category_contribution(df: pd.DataFrame, save_path: Optional[str] = None,
                               figsize: Tuple[int, int] = (12, 7)) -> plt.Figure:
    """
    Create a donut chart with bar overlay showing category contribution.
    
    Args:
        df: DataFrame with columns: category, category_revenue, revenue_contribution_pct
    """
    setup_style()
    
    fig = plt.figure(figsize=figsize)
    gs = GridSpec(1, 2, figure=fig, width_ratios=[1, 1.5])
    
    # Donut chart
    ax1 = fig.add_subplot(gs[0, 0])
    
    df_sorted = df.sort_values('revenue_contribution_pct', ascending=True).copy()
    
    wedges, texts, autotexts = ax1.pie(df_sorted['revenue_contribution_pct'],
                                       labels=df_sorted['category'],
                                       colors=CATEGORY_COLORS[:len(df_sorted)],
                                       autopct='%1.1f%%',
                                       startangle=90,
                                       pctdistance=0.85,
                                       wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2))
    
    # Style the percentage text
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(9)
        autotext.set_fontweight('bold')
    
    # Center circle for donut effect
    centre_circle = plt.Circle((0, 0), 0.4, fc='white', edgecolor='#E0E0E0', linewidth=2)
    ax1.add_artist(centre_circle)
    
    # Add total in center
    total_pct = df_sorted['revenue_contribution_pct'].sum()
    ax1.text(0, 0, f'Total\n100%', ha='center', va='center', fontsize=12, 
            fontweight='bold', color=COLOR_PALETTE['primary'])
    
    ax1.set_title('Category Revenue Share', fontsize=13, fontweight='bold', pad=10)
    
    # Horizontal bar chart
    ax2 = fig.add_subplot(gs[0, 1])
    
    df_bar = df.sort_values('revenue_contribution_pct', ascending=False).copy()
    
    bars = ax2.barh(df_bar['category'], df_bar['category_revenue'],
                    color=CATEGORY_COLORS[:len(df_bar)], edgecolor='white', linewidth=1.5)
    
    # Add percentage labels
    for bar, pct in zip(bars, df_bar['revenue_contribution_pct']):
        width = bar.get_width()
        ax2.annotate(f'{pct:.1f}%',
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(5, 0), textcoords='offset points',
                    ha='left', va='center', fontsize=9, fontweight='bold',
                    color=COLOR_PALETTE['primary'])
    
    ax2.set_xlabel('Revenue ($)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Category', fontsize=11, fontweight='bold')
    ax2.set_title('Revenue by Category', fontsize=13, fontweight='bold', pad=10)
    
    ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig


# =============================================================================
# CUSTOMER VISUALIZATIONS
# =============================================================================

def plot_clv_distribution(df: pd.DataFrame, save_path: Optional[str] = None,
                          figsize: Tuple[int, int] = (14, 7)) -> plt.Figure:
    """
    Create a histogram with KDE overlay showing CLV distribution.

    Args:
        df: DataFrame with columns: customer_name, total_revenue (or monthly_clv_estimate)
    """
    setup_style()

    fig = plt.figure(figsize=figsize)
    gs = GridSpec(2, 2, figure=fig, height_ratios=[1, 0.5])

    ax = fig.add_subplot(gs[0, :])

    # Get CLV data - convert Decimal to float for plotting
    clv_col = 'monthly_clv_estimate' if 'monthly_clv_estimate' in df.columns else 'total_revenue'
    clv_values = df[clv_col].dropna().astype(float)

    # Histogram with KDE
    sns.histplot(clv_values, kde=True, ax=ax, color=COLOR_PALETTE['primary'],
                 bins=30, alpha=0.7, line_kws={'linewidth': 2, 'color': COLOR_PALETTE['secondary']})

    ax.set_xlabel('Customer Lifetime Value ($)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Number of Customers', fontsize=11, fontweight='bold')
    ax.set_title('Customer Lifetime Value Distribution', fontsize=14, fontweight='bold', pad=15)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Add statistics
    stats_ax = fig.add_subplot(gs[1, 0])
    stats_ax.axis('off')

    stats_text = (
        f"📊 CLV Statistics\n\n"
        f"Mean: ${clv_values.mean():,.2f}\n"
        f"Median: ${clv_values.median():,.2f}\n"
        f"Std Dev: ${clv_values.std():,.2f}\n"
        f"Min: ${clv_values.min():,.2f}\n"
        f"Max: ${clv_values.max():,.2f}"
    )
    stats_ax.text(0, 0.5, stats_text, fontsize=10, verticalalignment='center',
                 fontfamily='monospace',
                 bbox=dict(boxstyle='round', facecolor='#F8F9FA', edgecolor='#E0E0E0'))

    # Customer tier breakdown
    tier_ax = fig.add_subplot(gs[1, 1])
    tier_ax.axis('off')

    if 'customer_tier' in df.columns:
        tier_counts = df['customer_tier'].value_counts()
        tier_colors = {'Platinum': '#E5E4E2', 'Gold': '#FFD700',
                      'Silver': '#C0C0C0', 'Bronze': '#CD7F32'}

        wedges, texts, autotexts = tier_ax.pie(tier_counts.values,
                                               labels=tier_counts.index,
                                               colors=[tier_colors.get(t, COLOR_PALETTE['neutral'])
                                                       for t in tier_counts.index],
                                               autopct='%1.1f%%',
                                               shadow=True)
        tier_ax.set_title('Customer Tiers', fontsize=12, fontweight='bold', pad=10)
    else:
        tier_ax.text(0.5, 0.5, 'Customer Tier\nData Not Available',
                    ha='center', va='center', fontsize=11)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')

    return fig


def plot_top_customers(df: pd.DataFrame, save_path: Optional[str] = None,
                       figsize: Tuple[int, int] = (12, 8)) -> plt.Figure:
    """
    Create a horizontal bar chart showing top customers by revenue.
    
    Args:
        df: DataFrame with columns: customer_name, total_revenue, segment
    """
    setup_style()
    
    fig, ax = plt.subplots(figsize=figsize)
    
    df = df.iloc[::-1].copy()
    
    # Color by segment
    segment_colors = {'Consumer': COLOR_PALETTE['primary'], 
                     'Corporate': COLOR_PALETTE['secondary'],
                     'Home Office': COLOR_PALETTE['accent']}
    colors = [segment_colors.get(seg, COLOR_PALETTE['neutral']) 
              for seg in df.get('segment', ['Consumer'] * len(df))]
    
    bars = ax.barh(df['customer_name'], df['total_revenue'], color=colors,
                   edgecolor='white', linewidth=1.5)
    
    for bar, revenue in zip(bars, df['total_revenue']):
        width = bar.get_width()
        ax.annotate(f'${revenue:,.0f}',
                   xy=(width, bar.get_y() + bar.get_height() / 2),
                   xytext=(5, 0), textcoords='offset points',
                   ha='left', va='center', fontsize=9, fontweight='bold')
    
    ax.set_xlabel('Revenue ($)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Customer', fontsize=11, fontweight='bold')
    ax.set_title('Top 10 Customers by Revenue', fontsize=14, fontweight='bold', pad=15)

    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Legend for segments
    legend_elements = [mpatches.Patch(color=color, label=segment)
                      for segment, color in segment_colors.items()]
    ax.legend(handles=legend_elements, loc='lower right', title='Segment',
             title_fontsize=11, framealpha=0.9, fontsize=9)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')

    return fig


# =============================================================================
# STORE VISUALIZATIONS
# =============================================================================

def plot_store_ranking(df: pd.DataFrame, save_path: Optional[str] = None,
                       figsize: Tuple[int, int] = (14, 8)) -> plt.Figure:
    """
    Create a ranked bar chart showing store performance.

    Args:
        df: DataFrame with columns: store_name, total_revenue, region, profit_margin_pct
    """
    setup_style()

    fig = plt.figure(figsize=figsize)
    gs = GridSpec(1, 2, figure=fig, width_ratios=[2, 1])

    ax1 = fig.add_subplot(gs[0, 0])

    df_sorted = df.sort_values('total_revenue', ascending=False).head(15).copy()
    df_sorted = df_sorted.iloc[::-1]

    # Convert Decimal to float for plotting
    df_sorted['total_revenue'] = df_sorted['total_revenue'].astype(float)

    # Color gradient based on revenue
    norm = plt.Normalize(df_sorted['total_revenue'].min(), df_sorted['total_revenue'].max())
    colors = plt.cm.Greens(norm(df_sorted['total_revenue']))

    bars = ax1.barh(df_sorted['store_name'], df_sorted['total_revenue'],
                    color=colors, edgecolor='white', linewidth=1.5)

    for bar, revenue in zip(bars, df_sorted['total_revenue']):
        width = bar.get_width()
        ax1.annotate(f'${revenue:,.0f}',
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(5, 0), textcoords='offset points',
                    ha='left', va='center', fontsize=8, fontweight='bold')

    ax1.set_xlabel('Revenue ($)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Store', fontsize=11, fontweight='bold')
    ax1.set_title('Store Revenue Ranking (Top 15)', fontsize=14, fontweight='bold', pad=15)

    ax1.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    # Region breakdown pie chart
    ax2 = fig.add_subplot(gs[0, 1])

    region_data = df.groupby('region')['total_revenue'].sum().sort_values(ascending=True).astype(float)

    wedges, texts, autotexts = ax2.pie(region_data.values,
                                       labels=region_data.index,
                                       colors=REVENUE_COLORS[:len(region_data)],
                                       autopct='%1.1f%%',
                                       shadow=True)
    ax2.set_title('Revenue by Region', fontsize=13, fontweight='bold', pad=10)

    for autotext in autotexts:
        autotext.set_fontweight('bold')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig


def plot_region_performance(df: pd.DataFrame, save_path: Optional[str] = None,
                            figsize: Tuple[int, int] = (12, 7)) -> plt.Figure:
    """
    Create a multi-metric comparison chart for regions.
    
    Args:
        df: DataFrame with columns: region, total_revenue, total_profit, profit_margin_pct
    """
    setup_style()
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    
    regions = df['region']
    
    # Revenue bar chart
    ax1 = axes[0, 0]
    bars1 = ax1.bar(regions, df['total_revenue'], color=COLOR_PALETTE['primary'],
                    edgecolor='white', linewidth=2)
    for bar, val in zip(bars1, df['total_revenue']):
        ax1.annotate(f'${val:,.0f}', xy=(bar.get_x() + bar.get_width()/2, val),
                    ha='center', va='bottom', fontsize=8, fontweight='bold')
    ax1.set_ylabel('Revenue ($)', fontweight='bold')
    ax1.set_title('Total Revenue by Region', fontweight='bold')
    ax1.tick_params(axis='x', rotation=45)
    
    # Profit bar chart
    ax2 = axes[0, 1]
    colors_profit = [COLOR_PALETTE['success'] if p >= 0 else COLOR_PALETTE['danger'] 
                    for p in df['total_profit']]
    bars2 = ax2.bar(regions, df['total_profit'], color=colors_profit,
                    edgecolor='white', linewidth=2)
    for bar, val in zip(bars2, df['total_profit']):
        ax2.annotate(f'${val:,.0f}', xy=(bar.get_x() + bar.get_width()/2, val),
                    ha='center', va='bottom' if val >= 0 else 'top', fontsize=8, fontweight='bold')
    ax2.set_ylabel('Profit ($)', fontweight='bold')
    ax2.set_title('Total Profit by Region', fontweight='bold')
    ax2.tick_params(axis='x', rotation=45)
    
    # Profit margin
    ax3 = axes[1, 0]
    colors_margin = [COLOR_PALETTE['success'] if m >= 20 else 
                    COLOR_PALETTE['warning'] if m >= 10 else COLOR_PALETTE['danger']
                    for m in df['profit_margin_pct']]
    bars3 = ax3.bar(regions, df['profit_margin_pct'], color=colors_margin,
                    edgecolor='white', linewidth=2)
    for bar, val in zip(bars3, df['profit_margin_pct']):
        ax3.annotate(f'{val:.1f}%', xy=(bar.get_x() + bar.get_width()/2, val),
                    ha='center', va='bottom', fontsize=8, fontweight='bold')
    ax3.set_ylabel('Profit Margin (%)', fontweight='bold')
    ax3.set_title('Profit Margin by Region', fontweight='bold')
    ax3.tick_params(axis='x', rotation=45)
    
    # Revenue per store
    ax4 = axes[1, 1]
    bars4 = ax4.bar(regions, df['revenue_per_store'], color=COLOR_PALETTE['info'],
                    edgecolor='white', linewidth=2)
    for bar, val in zip(bars4, df['revenue_per_store']):
        ax4.annotate(f'${val:,.0f}', xy=(bar.get_x() + bar.get_width()/2, val),
                    ha='center', va='bottom', fontsize=8, fontweight='bold')
    ax4.set_ylabel('Revenue per Store ($)', fontweight='bold')
    ax4.set_title('Efficiency: Revenue per Store', fontweight='bold')
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def save_plot(fig: plt.Figure, filename: str, directory: str = "output") -> str:
    """
    Save a plot to file with timestamp.
    
    Args:
        fig: Matplotlib figure to save
        filename: Base filename (without extension)
        directory: Directory to save the file
    
    Returns:
        str: Full path to saved file
    """
    os.makedirs(directory, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(directory, f"{filename}_{timestamp}.png")
    fig.savefig(filepath, dpi=150, bbox_inches='tight')
    return filepath


def show_plot(fig: plt.Figure) -> None:
    """Display a plot."""
    plt.show()


# Import FuncFormatter for currency formatting
from matplotlib.ticker import FuncFormatter
