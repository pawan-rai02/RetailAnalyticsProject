"""
Static Report Generation Module.

Provides utilities for:
1. Generating static images for documentation
2. Creating PDF reports with key analytics
"""

import os
import sys
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import pandas as pd

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

from analytics.revenue import get_monthly_revenue_trend, get_total_revenue, get_yearly_revenue
from analytics.product import get_top_10_products_by_revenue, get_category_contribution_percentage
from analytics.customer import get_customer_lifetime_value, get_top_10_customers
from analytics.store import get_store_revenue_ranking, get_region_performance

from visualization.plots import (
    plot_monthly_revenue,
    plot_top_products,
    plot_category_contribution,
    plot_clv_distribution,
    plot_top_customers,
    plot_store_ranking,
    plot_region_performance,
    setup_style,
    COLOR_PALETTE
)


# =============================================================================
# STATIC IMAGE GENERATION
# =============================================================================

# Define key visualizations for documentation
KEY_VISUALIZATIONS = {
    "monthly_revenue": {
        "fetch": get_monthly_revenue_trend,
        "plot": plot_monthly_revenue,
        "title": "Monthly Revenue Trend",
        "filename": "monthly_revenue.png"
    },
    "top_products": {
        "fetch": get_top_10_products_by_revenue,
        "plot": plot_top_products,
        "title": "Top 10 Products by Revenue",
        "filename": "top_products.png"
    },
    "store_ranking": {
        "fetch": get_store_revenue_ranking,
        "plot": plot_store_ranking,
        "title": "Store Revenue Ranking",
        "filename": "store_ranking.png"
    },
    "clv_distribution": {
        "fetch": get_customer_lifetime_value,
        "plot": plot_clv_distribution,
        "title": "Customer Lifetime Value Distribution",
        "filename": "clv_distribution.png"
    },
    "category_contribution": {
        "fetch": get_category_contribution_percentage,
        "plot": plot_category_contribution,
        "title": "Category Revenue Contribution",
        "filename": "category_contribution.png"
    },
    "top_customers": {
        "fetch": get_top_10_customers,
        "plot": plot_top_customers,
        "title": "Top 10 Customers",
        "filename": "top_customers.png"
    },
    "region_performance": {
        "fetch": get_region_performance,
        "plot": plot_region_performance,
        "title": "Region Performance",
        "filename": "region_performance.png"
    },
}


def ensure_directory(directory: str) -> str:
    """
    Ensure a directory exists, create if necessary.
    
    Args:
        directory: Path to directory
        
    Returns:
        Absolute path to directory
    """
    abs_path = os.path.abspath(directory)
    os.makedirs(abs_path, exist_ok=True)
    return abs_path


def generate_static_images(
    output_dir: str = "docs/images",
    visualizations: Optional[Dict] = None,
    overwrite: bool = True
) -> Dict[str, str]:
    """
    Generate static images for documentation.
    
    Args:
        output_dir: Directory to save images
        visualizations: Dict of visualization configs (uses KEY_VISUALIZATIONS if None)
        overwrite: Whether to overwrite existing files
        
    Returns:
        Dict mapping visualization names to saved file paths
        
    Raises:
        Exception: If database connection fails or query errors occur
    """
    if visualizations is None:
        visualizations = KEY_VISUALIZATIONS
    
    # Ensure output directory exists
    output_dir = ensure_directory(output_dir)
    
    print("\n" + "=" * 70)
    print("  GENERATING STATIC IMAGES FOR DOCUMENTATION")
    print("=" * 70)
    print(f"\n📁 Output directory: {output_dir}")
    print(f"📊 Visualizations to generate: {len(visualizations)}")
    print("-" * 70)
    
    # Setup matplotlib style
    setup_style()
    
    saved_files = {}
    successful = 0
    failed = 0
    skipped = 0
    
    for viz_name, viz_config in visualizations.items():
        filename = viz_config["filename"]
        filepath = os.path.join(output_dir, filename)
        
        # Check if file exists and overwrite is disabled
        if os.path.exists(filepath) and not overwrite:
            print(f"\n⏭️  Skipping: {viz_name}")
            print(f"   File already exists: {filename}")
            skipped += 1
            continue
        
        print(f"\n▶  Generating: {viz_config['title']}")
        
        try:
            # Fetch data
            fetch_func = viz_config["fetch"]
            df = fetch_func()
            
            if df.empty:
                print(f"   ⚠️  No data returned for {viz_name}")
                failed += 1
                continue
            
            print(f"   ✅ Data fetched: {len(df)} rows")
            
            # Generate plot
            plot_func = viz_config["plot"]
            fig = plot_func(df)
            
            # Save figure
            fig.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close(fig)
            
            print(f"   ✅ Saved: {filename}")
            saved_files[viz_name] = filepath
            successful += 1
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            failed += 1
    
    # Print summary
    print("\n" + "=" * 70)
    print("  GENERATION SUMMARY")
    print("=" * 70)
    print(f"  ✅ Successful: {successful}")
    print(f"  ❌ Failed:     {failed}")
    print(f"  ⏭️  Skipped:    {skipped}")
    print("=" * 70)
    
    if saved_files:
        print("\n📁 Generated files:")
        for name, path in saved_files.items():
            print(f"   - {os.path.basename(path)}")
    
    return saved_files


def get_readme_snippet(image_dir: str = "docs/images") -> str:
    """
    Generate markdown snippet for embedding images in README.
    
    Args:
        image_dir: Relative path to images directory
        
    Returns:
        Markdown string for README embedding
    """
    snippet = """
## 📊 Analytics Visualizations

### 📈 Monthly Revenue Trend

![Monthly Revenue Trend]({image_dir}/monthly_revenue.png)

*Revenue trajectory over time showing growth patterns and seasonal trends.*

---

### 🏆 Top Products by Revenue

![Top Products]({image_dir}/top_products.png)

*Best-selling products ranked by total revenue with category breakdown.*

---

### 🏬 Store Revenue Ranking

![Store Ranking]({image_dir}/store_ranking.png)

*Store performance comparison with regional revenue distribution.*

---

### 👥 Customer Lifetime Value Distribution

![CLV Distribution]({image_dir}/clv_distribution.png)

*Customer value distribution showing segmentation and tier composition.*

---

### 📦 Category Revenue Contribution

![Category Contribution]({image_dir}/category_contribution.png)

*Revenue share by product category with percentage breakdown.*

---

### 🌟 Top 10 Customers

![Top Customers]({image_dir}/top_customers.png)

*VIP customers ranked by total revenue contribution.*

---

### 🗺️ Region Performance Dashboard

![Region Performance]({image_dir}/region_performance.png)

*Multi-metric regional analysis including revenue, profit, and margins.*

""".format(image_dir=image_dir)
    
    return snippet


# =============================================================================
# PDF REPORT GENERATION
# =============================================================================

def create_title_page(
    pdf: PdfPages,
    title: str = "Retail Analytics Report",
    subtitle: str = "Business Intelligence Dashboard",
    generated_date: Optional[str] = None
) -> None:
    """
    Create a professional title page for the PDF report.

    Args:
        pdf: PdfPages object
        title: Main title
        subtitle: Subtitle
        generated_date: Date string (uses current date if None)
    """
    if generated_date is None:
        generated_date = datetime.now().strftime("%B %Y")

    # Use default font for PDF compatibility on Windows
    original_family = plt.rcParams['font.family']
    plt.rcParams['font.family'] = 'DejaVu Sans'
    
    fig = plt.figure(figsize=(8.5, 11))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')

    # Background gradient
    ax.set_facecolor('#F8F9FA')

    # Title
    ax.text(
        0.5, 0.65, title,
        ha='center', va='center',
        fontsize=28, fontweight='bold',
        color=COLOR_PALETTE['primary']
    )

    # Subtitle
    ax.text(
        0.5, 0.55, subtitle,
        ha='center', va='center',
        fontsize=18,
        color=COLOR_PALETTE['secondary']
    )

    # Divider line
    ax.plot([0.2, 0.8], [0.5, 0.5],
            color=COLOR_PALETTE['primary'],
            linewidth=2, alpha=0.5)

    # Generated date
    ax.text(
        0.5, 0.40, f"Generated: {generated_date}",
        ha='center', va='center',
        fontsize=12,
        color=COLOR_PALETTE['neutral']
    )

    # Footer
    ax.text(
        0.5, 0.10, "Retail Analytics Data Engineering Pipeline\nPhase 3: Analytics & Visualization Layer",
        ha='center', va='center',
        fontsize=10,
        color=COLOR_PALETTE['neutral'],
        style='italic'
    )

    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)
    
    # Restore original font
    plt.rcParams['font.family'] = original_family


def create_kpi_summary_page(pdf: PdfPages) -> None:
    """
    Create a KPI summary page with key metrics.

    Args:
        pdf: PdfPages object
    """
    # Use default font for PDF compatibility on Windows
    original_family = plt.rcParams['font.family']
    plt.rcParams['font.family'] = 'DejaVu Sans'
    
    fig = plt.figure(figsize=(8.5, 11))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')

    # Title
    ax.text(
        0.5, 0.92, "Key Performance Indicators Summary",
        ha='center', va='center',
        fontsize=20, fontweight='bold',
        color=COLOR_PALETTE['primary']
    )

    # Divider
    ax.plot([0.15, 0.85], [0.87, 0.87],
            color=COLOR_PALETTE['primary'],
            linewidth=2, alpha=0.5)

    try:
        # Fetch KPIs
        total_rev_df = get_total_revenue()
        yearly_df = get_yearly_revenue()

        # Extract metrics
        total_revenue = total_rev_df['total_revenue'].iloc[0] if not total_rev_df.empty else 0
        total_transactions = total_rev_df['total_transactions'].iloc[0] if not total_rev_df.empty else 0
        avg_order_value = total_rev_df['avg_transaction_value'].iloc[0] if not total_rev_df.empty else 0

        # KPI boxes
        kpis = [
            ("Total Revenue", f"${total_revenue:,.2f}", COLOR_PALETTE['primary']),
            ("Total Transactions", f"{int(total_transactions):,}", COLOR_PALETTE['secondary']),
            ("Avg Order Value", f"${avg_order_value:,.2f}", COLOR_PALETTE['accent']),
        ]

        # Draw KPI boxes
        box_width = 0.25
        box_height = 0.12
        start_x = 0.125

        for i, (label, value, color) in enumerate(kpis):
            x = start_x + i * box_width

            # Box
            rect = plt.Rectangle(
                (x, 0.65), box_width - 0.02, box_height,
                facecolor=color, alpha=0.1,
                edgecolor=color, linewidth=2
            )
            ax.add_patch(rect)

            # Label
            ax.text(
                x + (box_width - 0.02) / 2, 0.72,
                label,
                ha='center', va='center',
                fontsize=11, color=COLOR_PALETTE['neutral']
            )

            # Value
            ax.text(
                x + (box_width - 0.02) / 2, 0.68,
                value,
                ha='center', va='center',
                fontsize=18, fontweight='bold',
                color=color
            )

        # Data quality note
        note_text = """
📊 Data Source: MySQL Star Schema (Phase 1 ETL Pipeline)

This report presents analytics computed from the retail data warehouse
containing transaction data processed through the PySpark ETL pipeline.

Metrics are calculated using SQL queries with proper star schema JOINs
and window functions for accurate business intelligence.
        """

        ax.text(
            0.15, 0.50, note_text.strip(),
            ha='left', va='top',
            fontsize=10,
            color=COLOR_PALETTE['neutral'],
            family='monospace'
        )

        # Report sections preview
        sections = [
            "📈 Revenue Trends",
            "🏆 Product Performance",
            "👥 Customer Analytics",
            "🏬 Store & Regional Analysis"
        ]

        for i, section in enumerate(sections):
            ax.text(
                0.15, 0.35 - i * 0.08,
                section,
                ha='left', va='top',
                fontsize=12,
                color=COLOR_PALETTE['primary']
            )

    except Exception as e:
        ax.text(
            0.5, 0.5,
            f"Error fetching KPIs: {str(e)}",
            ha='center', va='center',
            fontsize=12,
            color=COLOR_PALETTE['danger']
        )

    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)
    
    # Restore original font
    plt.rcParams['font.family'] = original_family


def generate_pdf_report(
    output_path: str = "reports/analytics_report.pdf",
    include_visualizations: Optional[List[str]] = None
) -> str:
    """
    Generate a comprehensive PDF analytics report.

    Args:
        output_path: Path to save the PDF report
        include_visualizations: List of visualization names to include
                               (uses all KEY_VISUALIZATIONS if None)

    Returns:
        Absolute path to saved PDF

    Raises:
        Exception: If report generation fails
    """
    if include_visualizations is None:
        include_visualizations = list(KEY_VISUALIZATIONS.keys())

    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        ensure_directory(output_dir)

    print("\n" + "=" * 70)
    print("  GENERATING PDF ANALYTICS REPORT")
    print("=" * 70)
    print(f"\n📄 Output file: {output_path}")
    print(f"📊 Visualizations to include: {len(include_visualizations)}")
    print("-" * 70)

    # Setup matplotlib style
    setup_style()
    
    # Store original font setting
    original_family = plt.rcParams['font.family']

    try:
        # Create PDF
        with PdfPages(output_path) as pdf:
            # Title page
            print("\n▶  Creating title page...")
            create_title_page(pdf)
            print("   ✅ Title page created")

            # KPI summary page
            print("\n▶  Creating KPI summary page...")
            create_kpi_summary_page(pdf)
            print("   ✅ KPI summary page created")

            # Generate visualization pages
            for viz_name in include_visualizations:
                if viz_name not in KEY_VISUALIZATIONS:
                    print(f"\n⚠️  Unknown visualization: {viz_name}")
                    continue

                viz_config = KEY_VISUALIZATIONS[viz_name]
                print(f"\n▶  Adding: {viz_config['title']}")

                try:
                    # Fetch data
                    df = viz_config["fetch"]()

                    if df.empty:
                        print(f"   ⚠️  No data, skipping...")
                        continue

                    # Temporarily use DejaVu Sans for PDF compatibility
                    plt.rcParams['font.family'] = 'DejaVu Sans'
                    
                    # Generate plot
                    fig = viz_config["plot"](df)

                    # Add to PDF with font embedding
                    pdf.savefig(fig, bbox_inches='tight', facecolor='white')
                    plt.close(fig)
                    
                    # Restore font for next iteration
                    plt.rcParams['font.family'] = original_family

                    print(f"   ✅ Added to report")

                except Exception as e:
                    # Restore font on error
                    plt.rcParams['font.family'] = original_family
                    print(f"   ❌ Error: {str(e)}")

            # Add metadata
            pdf.infodict()['Author'] = 'Retail Analytics Pipeline'
            pdf.infodict()['Subject'] = 'Business Intelligence Report'
            pdf.infodict()['Keywords'] = 'retail, analytics, BI, KPIs'

        abs_path = os.path.abspath(output_path)

        # Print summary
        print("\n" + "=" * 70)
        print("  PDF REPORT GENERATION COMPLETE")
        print("=" * 70)
        print(f"\n✅ Report saved to: {abs_path}")
        print(f"📊 Total pages: {len(include_visualizations) + 2}")  # +2 for title and KPI pages
        print("=" * 70)
        
        return abs_path
        
    except Exception as e:
        print(f"\n❌ Report generation failed: {str(e)}")
        raise


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def generate_all_assets(
    images_dir: str = "docs/images",
    report_path: str = "reports/analytics_report.pdf"
) -> Tuple[Dict[str, str], str]:
    """
    Generate both static images and PDF report.
    
    Args:
        images_dir: Directory for static images
        report_path: Path for PDF report
        
    Returns:
        Tuple of (saved_images_dict, report_path)
    """
    # Generate static images
    images = generate_static_images(output_dir=images_dir)
    
    # Generate PDF report
    report = generate_pdf_report(output_path=report_path)
    
    return images, report


def print_readme_instructions() -> None:
    """Print instructions for embedding visuals in README."""
    print("\n" + "=" * 70)
    print("  README EMBEDDING INSTRUCTIONS")
    print("=" * 70)
    print("""
To embed these visuals in your README.md, add the following markdown:

```markdown
## 📊 Analytics Visualizations

### 📈 Monthly Revenue Trend
![Monthly Revenue](docs/images/monthly_revenue.png)

### 🏆 Top Products
![Top Products](docs/images/top_products.png)

### 🏬 Store Ranking
![Store Ranking](docs/images/store_ranking.png)

### 👥 CLV Distribution
![CLV Distribution](docs/images/clv_distribution.png)
```

Or use the full snippet generator:
    python main.py readme-snippet
""")
    print("=" * 70)
