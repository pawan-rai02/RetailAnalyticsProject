#!/usr/bin/env python3
"""
Retail Analytics Layer - Main Execution Module

A business analytics layer that queries the MySQL star schema,
computes retail KPIs, and generates professional visualizations.

Usage:
    python main.py revenue monthly
    python main.py product top10
    python main.py customer clv
    python main.py store ranking
    python main.py revenue monthly --plot
    python main.py generate-static
    python main.py generate-report
"""

import argparse
import sys
import os
from typing import Callable, Dict, List, Optional, Tuple
import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analytics.revenue import (
    get_total_revenue,
    get_monthly_revenue_trend,
    get_yearly_revenue,
    get_month_over_month_growth,
    get_weekend_vs_weekday_sales,
    get_daily_revenue_summary,
    get_quarterly_revenue
)

from analytics.product import (
    get_top_10_products_by_revenue,
    get_top_10_products_by_quantity,
    get_category_contribution_percentage,
    get_worst_10_products,
    get_subcategory_performance,
    get_product_profit_analysis
)

from analytics.customer import (
    get_customer_lifetime_value,
    get_top_10_customers,
    get_repeat_vs_new_customer_ratio,
    get_average_revenue_per_customer,
    get_customer_segmentation,
    get_customer_churn_indicators
)

from analytics.store import (
    get_store_revenue_ranking,
    get_region_performance,
    get_underperforming_stores,
    get_profit_margin_per_store,
    get_state_performance,
    get_city_analysis
)

from visualization.plots import (
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
    setup_style
)

from reports.static_generator import (
    generate_static_images,
    generate_pdf_report,
    generate_all_assets,
    get_readme_snippet,
    print_readme_instructions,
    KEY_VISUALIZATIONS
)


# =============================================================================
# COMMAND MAPPINGS
# =============================================================================

REVENUE_COMMANDS: Dict[str, Tuple[Callable[[], pd.DataFrame], str, Callable]] = {
    "total": (get_total_revenue, "Total Revenue Overview", None),
    "monthly": (get_monthly_revenue_trend, "Monthly Revenue Trend", plot_monthly_revenue),
    "yearly": (get_yearly_revenue, "Yearly Revenue Summary", plot_yearly_revenue),
    "growth": (get_month_over_month_growth, "Month-over-Month Growth", None),
    "weekend": (get_weekend_vs_weekday_sales, "Weekend vs Weekday Sales", plot_weekend_vs_weekday),
    "daily": (get_daily_revenue_summary, "Daily Revenue Summary", None),
    "quarterly": (get_quarterly_revenue, "Quarterly Revenue", None),
}

PRODUCT_COMMANDS: Dict[str, Tuple[Callable[[], pd.DataFrame], str, Callable]] = {
    "top10": (get_top_10_products_by_revenue, "Top 10 Products by Revenue", plot_top_products),
    "quantity": (get_top_10_products_by_quantity, "Top 10 Products by Quantity", None),
    "category": (get_category_contribution_percentage, "Category Contribution", plot_category_contribution),
    "worst": (get_worst_10_products, "Worst 10 Products", None),
    "subcategory": (get_subcategory_performance, "Subcategory Performance", None),
    "profit": (get_product_profit_analysis, "Product Profit Analysis", None),
}

CUSTOMER_COMMANDS: Dict[str, Tuple[Callable[[], pd.DataFrame], str, Callable]] = {
    "clv": (get_customer_lifetime_value, "Customer Lifetime Value", plot_clv_distribution),
    "top10": (get_top_10_customers, "Top 10 Customers", plot_top_customers),
    "repeat": (get_repeat_vs_new_customer_ratio, "Repeat vs New Customer Ratio", None),
    "arpc": (get_average_revenue_per_customer, "Average Revenue Per Customer", None),
    "segment": (get_customer_segmentation, "Customer Segmentation (RFM)", None),
    "churn": (get_customer_churn_indicators, "Customer Churn Indicators", None),
}

STORE_COMMANDS: Dict[str, Tuple[Callable[[], pd.DataFrame], str, Callable]] = {
    "ranking": (get_store_revenue_ranking, "Store Revenue Ranking", plot_store_ranking),
    "region": (get_region_performance, "Region Performance", plot_region_performance),
    "underperform": (get_underperforming_stores, "Underperforming Stores", None),
    "margin": (get_profit_margin_per_store, "Profit Margin per Store", None),
    "state": (get_state_performance, "State Performance", None),
    "city": (get_city_analysis, "City Analysis", None),
}

COMMAND_CATEGORIES = {
    "revenue": REVENUE_COMMANDS,
    "product": PRODUCT_COMMANDS,
    "customer": CUSTOMER_COMMANDS,
    "store": STORE_COMMANDS,
}


# =============================================================================
# DISPLAY UTILITIES
# =============================================================================

def format_currency(value) -> str:
    """Format a value as currency."""
    if pd.isna(value):
        return "N/A"
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return str(value)


def format_percentage(value) -> str:
    """Format a value as percentage."""
    if pd.isna(value):
        return "N/A"
    try:
        return f"{float(value):.2f}%"
    except (ValueError, TypeError):
        return str(value)


def format_number(value) -> str:
    """Format a number with commas."""
    if pd.isna(value):
        return "N/A"
    try:
        num = float(value)
        if num == int(num):
            return f"{int(num):,}"
        return f"{num:,.2f}"
    except (ValueError, TypeError):
        return str(value)


def print_header(title: str, width: int = 80) -> None:
    """Print a formatted header."""
    print("\n" + "=" * width)
    print(f"  {title}".center(width))
    print("=" * width)


def print_dataframe(df: pd.DataFrame, title: str = "", max_rows: int = 20) -> None:
    """Print a DataFrame with formatting."""
    if df.empty:
        print("No data available.")
        return
    
    # Display settings
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 50)
    pd.set_option('display.precision', 2)
    
    # Format the DataFrame for display
    df_display = df.copy()
    
    # Auto-format numeric columns
    for col in df_display.columns:
        col_lower = col.lower()
        if df_display[col].dtype in ['float64', 'int64']:
            if 'revenue' in col_lower or 'profit' in col_lower or 'value' in col_lower or 'price' in col_lower:
                df_display[col] = df_display[col].apply(format_currency)
            elif 'pct' in col_lower or 'margin' in col_lower or 'growth' in col_lower:
                df_display[col] = df_display[col].apply(format_percentage)
            else:
                df_display[col] = df_display[col].apply(format_number)
    
    # Print title
    if title:
        print(f"\n📊 {title}")
        print("-" * 60)
    
    # Print DataFrame
    if len(df_display) > max_rows:
        print(f"\nShowing first {max_rows} of {len(df_display)} rows:\n")
        print(df_display.head(max_rows).to_string(index=False))
        print(f"\n... and {len(df_display) - max_rows} more rows")
    else:
        print(f"\n({len(df_display)} rows)\n")
        print(df_display.to_string(index=False))
    
    # Print summary statistics
    print("\n" + "-" * 60)
    print("Summary Statistics:")
    
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    for col in numeric_cols[:5]:  # Limit to first 5 numeric columns
        if col in df.columns:
            print(f"  {col}: min={format_number(df[col].min())}, "
                  f"max={format_number(df[col].max())}, "
                  f"avg={format_number(df[col].mean())}")


def print_summary_stats(df: pd.DataFrame) -> None:
    """Print summary statistics for the DataFrame."""
    if df.empty:
        return
    
    print("\n📈 Key Metrics:")
    print("-" * 40)
    
    for col in df.columns[:6]:
        if col in df.columns:
            if df[col].dtype in ['float64', 'int64']:
                non_null = df[col].notna().sum()
                if non_null > 0:
                    print(f"  {col}:")
                    print(f"    Total: {format_number(df[col].sum())}")
                    print(f"    Average: {format_number(df[col].mean())}")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def run_analysis(category: str, command: str, show_plot: bool = False, 
                 output_dir: str = "output") -> Optional[pd.DataFrame]:
    """
    Run an analysis command and optionally display a plot.
    
    Args:
        category: Analysis category (revenue, product, customer, store)
        command: Specific command within the category
        show_plot: Whether to display a plot
        output_dir: Directory to save plots
    
    Returns:
        DataFrame with results, or None if error
    """
    # Validate category
    if category not in COMMAND_CATEGORIES:
        print(f"❌ Error: Unknown category '{category}'")
        print(f"   Valid categories: {', '.join(COMMAND_CATEGORIES.keys())}")
        return None
    
    commands = COMMAND_CATEGORIES[category]
    
    # Validate command
    if command not in commands:
        print(f"❌ Error: Unknown command '{command}' for category '{category}'")
        print(f"   Valid commands: {', '.join(commands.keys())}")
        return None
    
    fetch_func, title, plot_func = commands[command]
    
    # Print header
    print_header(f"{category.upper()} ANALYTICS: {title.upper()}")
    
    # Fetch data
    try:
        print("\n⏳ Fetching data from database...")
        df = fetch_func()
        
        if df.empty:
            print("⚠️  No data returned from query.")
            return None
        
        print(f"✅ Retrieved {len(df)} rows")
        
        # Display results
        print_dataframe(df, title)
        
        # Generate plot if requested
        if show_plot and plot_func is not None:
            print(f"\n🎨 Generating visualization...")
            setup_style()
            
            try:
                fig = plot_func(df)
                filename = f"{category}_{command}"
                filepath = save_plot(fig, filename, output_dir)
                print(f"✅ Plot saved to: {filepath}")
                
                # Also try to display if in interactive environment
                try:
                    import matplotlib.pyplot as plt
                    plt.show()
                except:
                    pass
                    
            except Exception as e:
                print(f"⚠️  Could not generate plot: {str(e)}")
        elif show_plot and plot_func is None:
            print("⚠️  No visualization available for this command.")
        
        return df
        
    except Exception as e:
        print(f"❌ Error executing analysis: {str(e)}")
        return None


def list_commands() -> None:
    """List all available commands."""
    print_header("AVAILABLE ANALYTICS COMMANDS")

    for category, commands in COMMAND_CATEGORIES.items():
        print(f"\n📁 {category.upper()}")
        print("-" * 40)
        for cmd, (_, title, plot_func) in commands.items():
            plot_indicator = " 📊" if plot_func else ""
            print(f"   {cmd:15} - {title}{plot_indicator}")
    
    print("\n" + "=" * 80)
    print("REPORT GENERATION COMMANDS")
    print("=" * 80)
    print("   generate-static  - Generate static images for documentation")
    print("   generate-report  - Generate PDF analytics report")
    print("   readme-snippet   - Generate markdown for README embedding")
    print("\n" + "=" * 80)
    print("USAGE EXAMPLES:")
    print("=" * 80)
    print("  python main.py revenue monthly")
    print("  python main.py product top10 --plot")
    print("  python main.py customer clv --plot")
    print("  python main.py store ranking")
    print("  python main.py revenue monthly --plot --output charts")
    print("  python main.py generate-static")
    print("  python main.py generate-report")
    print("  python main.py readme-snippet")
    print("=" * 80)


def cmd_generate_static(images_dir: str = "docs/images") -> int:
    """
    Generate static images for documentation.
    
    Args:
        images_dir: Directory to save images
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        saved_files = generate_static_images(output_dir=images_dir)
        
        if saved_files:
            print_readme_instructions()
            return 0
        return 1
        
    except Exception as e:
        print(f"\n❌ Static image generation failed: {str(e)}")
        return 1


def cmd_generate_report(report_path: str = "reports/analytics_report.pdf") -> int:
    """
    Generate PDF analytics report.
    
    Args:
        report_path: Path to save the PDF report
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        abs_path = generate_pdf_report(output_path=report_path)
        print(f"\n✅ Report successfully generated at: {abs_path}")
        return 0
        
    except Exception as e:
        print(f"\n❌ Report generation failed: {str(e)}")
        return 1


def cmd_generate_all(
    images_dir: str = "docs/images",
    report_path: str = "reports/analytics_report.pdf"
) -> int:
    """
    Generate both static images and PDF report.
    
    Args:
        images_dir: Directory for static images
        report_path: Path for PDF report
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        print_header("GENERATING ALL ASSETS")
        
        images, report = generate_all_assets(
            images_dir=images_dir,
            report_path=report_path
        )
        
        print("\n" + "=" * 70)
        print("  ALL ASSETS GENERATED SUCCESSFULLY")
        print("=" * 70)
        print(f"\n📁 Images directory: {images_dir}")
        print(f"   Generated: {len(images)} images")
        for name, path in images.items():
            print(f"   - {os.path.basename(path)}")
        
        print(f"\n📄 PDF Report: {report}")
        print("=" * 70)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Asset generation failed: {str(e)}")
        return 1


def cmd_readme_snippet(image_dir: str = "docs/images") -> None:
    """
    Print README markdown snippet for embedding visuals.
    
    Args:
        image_dir: Relative path to images directory
    """
    snippet = get_readme_snippet(image_dir=image_dir)
    print(snippet)
    print("\n" + "=" * 70)
    print("  Copy the above markdown to embed visuals in your README")
    print("=" * 70)


def run_all_analytics(output_dir: str = "output", generate_plots: bool = True) -> Dict[str, pd.DataFrame]:
    """
    Run all analytics and optionally generate all plots.
    
    Args:
        output_dir: Directory to save plots
        generate_plots: Whether to generate plots
    
    Returns:
        Dictionary of results by category and command
    """
    results = {}
    
    print_header("RUNNING ALL ANALYTICS")
    
    for category, commands in COMMAND_CATEGORIES.items():
        results[category] = {}
        print(f"\n{'='*60}")
        print(f"  {category.upper()} ANALYTICS")
        print(f"{'='*60}")
        
        for cmd, (_, title, _) in commands.items():
            print(f"\n▶  Running: {cmd} - {title}")
            df = run_analysis(category, cmd, show_plot=generate_plots, output_dir=output_dir)
            if df is not None:
                results[category][cmd] = df
    
    return results


# =============================================================================
# CLI ARGUMENT PARSER
# =============================================================================

def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="Retail Analytics Layer - Query star schema and generate insights",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py revenue monthly
  python main.py product top10 --plot
  python main.py customer clv --plot --output my_charts
  python main.py store ranking
  python main.py list
  python main.py all --plot
  python main.py generate-static
  python main.py generate-report
  python main.py generate-all
  python main.py readme-snippet
        """
    )

    parser.add_argument(
        "category",
        nargs="?",
        choices=["revenue", "product", "customer", "store", "list", "all", 
                 "generate-static", "generate-report", "generate-all", "readme-snippet"],
        help="Analysis category or report command"
    )

    parser.add_argument(
        "command",
        nargs="?",
        help="Specific analysis command"
    )

    parser.add_argument(
        "--plot", "-p",
        action="store_true",
        help="Generate visualization for the analysis"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        default="output",
        help="Output directory for plots (default: output)"
    )

    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Run all analytics (overrides category/command)"
    )

    parser.add_argument(
        "--images-dir",
        type=str,
        default="docs/images",
        help="Directory for static images (default: docs/images)"
    )

    parser.add_argument(
        "--report-path",
        type=str,
        default="reports/analytics_report.pdf",
        help="Path for PDF report (default: reports/analytics_report.pdf)"
    )

    return parser


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Handle report generation commands
    if args.category == "generate-static":
        return cmd_generate_static(images_dir=args.images_dir)
    
    if args.category == "generate-report":
        return cmd_generate_report(report_path=args.report_path)
    
    if args.category == "generate-all":
        return cmd_generate_all(
            images_dir=args.images_dir,
            report_path=args.report_path
        )
    
    if args.category == "readme-snippet":
        cmd_readme_snippet(image_dir=args.images_dir)
        return 0

    # Handle 'list' command or no arguments
    if args.category is None or args.category == "list":
        list_commands()
        return 0

    # Handle 'all' command
    if args.category == "all" or args.all:
        run_all_analytics(output_dir=args.output, generate_plots=args.plot)
        return 0

    # Require command for specific category
    if args.command is None:
        print(f"❌ Error: Command required for category '{args.category}'")
        print(f"   Run 'python main.py list' to see available commands")
        return 1

    # Run the analysis
    result = run_analysis(
        category=args.category,
        command=args.command,
        show_plot=args.plot,
        output_dir=args.output
    )

    return 0 if result is not None else 1


if __name__ == "__main__":
    sys.exit(main())
