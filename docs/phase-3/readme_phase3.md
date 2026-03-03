# Phase 3: Analytics & Visualization Layer

## 📊 Overview

Phase 3 builds a **business intelligence analytics layer** on top of the MySQL star schema created in Phase 1. It provides 25+ pre-built retail KPIs with professional visualizations, all accessible via a clean CLI interface.

## ✨ Features

| Feature | Description |
|---------|-------------|
| **25+ Analytics Functions** | Pre-built KPIs across Revenue, Product, Customer, and Store domains |
| **Professional Visualizations** | Publication-quality charts using Matplotlib and Seaborn |
| **CLI Interface** | Simple command-line access to all analytics |
| **Modular Architecture** | Clean separation of concerns for easy extension |
| **Advanced SQL** | Window functions, CTEs, and star schema JOINs |
| **Pandas Integration** | All results returned as DataFrames for further analysis |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        PHASE 3 ANALYTICS                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────┐    ┌─────────────────────────────────────────┐   │
│   │  CLI    │───▶│           ANALYTICS MODULES              │   │
│   │ main.py │    │  revenue │ product │ customer │ store   │   │
│   └─────────┘    └─────────────────────────────────────────┘   │
│         │                          │                            │
│         │         ┌────────────────┘                            │
│         │         │                                             │
│         ▼         ▼                                             │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │              VISUALIZATION LAYER                         │  │
│   │         Matplotlib + Seaborn Charts                      │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              │                                  │
└──────────────────────────────┼──────────────────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   MySQL Star Schema │
                    │   (Phase 1 Tables)  │
                    └─────────────────────┘
```

## 📁 Module Structure

```
phases/phase-3-analytics/
│
├── main.py                 # CLI entry point
├── requirements.txt        # Dependencies
│
├── db/
│   └── connection.py       # SQLAlchemy connection management
│
├── analytics/
│   ├── revenue.py          # Revenue KPIs (8 functions)
│   ├── product.py          # Product KPIs (8 functions)
│   ├── customer.py         # Customer KPIs (7 functions)
│   └── store.py            # Store KPIs (8 functions)
│
└── visualization/
    └── plots.py            # Chart generation (10+ chart types)
```

## 🚀 Quick Start

### Installation

```bash
cd phases/phase-3-analytics
pip install -r requirements.txt
```

### Basic Usage

```bash
# List all available commands
python main.py list

# Revenue analytics
python main.py revenue total
python main.py revenue monthly --plot
python main.py revenue yearly --plot
python main.py revenue growth
python main.py revenue weekend --plot

# Product analytics
python main.py product top10 --plot
python main.py product quantity
python main.py product category --plot
python main.py product worst
python main.py product profit

# Customer analytics
python main.py customer clv --plot
python main.py customer top10 --plot
python main.py customer repeat
python main.py customer arpc
python main.py customer segment

# Store analytics
python main.py store ranking --plot
python main.py store region --plot
python main.py store underperform
python main.py store margin
python main.py store state

# Run all analytics with plots
python main.py all --plot --output my_charts
```

### Documentation & Report Generation

```bash
# Generate static images for README documentation
python main.py generate-static

# Generate PDF analytics report
python main.py generate-report

# Generate both images and PDF report
python main.py generate-all

# Get README markdown snippet for embedding visuals
python main.py readme-snippet
```

### Custom Output Paths

```bash
# Generate images to custom directory
python main.py generate-static --images-dir my_docs/images

# Generate report to custom path
python main.py generate-report --report-path my_reports/q4_report.pdf

# Generate all with custom paths
python main.py generate-all --images-dir docs/visuals --report-path reports/full_report.pdf
```

## 📊 Analytics Functions Reference

### Revenue Analytics (`analytics/revenue.py`)

| Function | Description | Visualization |
|----------|-------------|---------------|
| `get_total_revenue()` | Total revenue, transactions, avg order value | — |
| `get_monthly_revenue_trend()` | Monthly revenue time series | Line chart with area fill |
| `get_yearly_revenue()` | Yearly revenue comparison | Bar chart |
| `get_month_over_month_growth()` | MoM growth percentage | — |
| `get_weekend_vs_weekday_sales()` | Weekend vs weekday breakdown | Bar + Pie combo |
| `get_quarterly_revenue()` | Quarterly performance | — |
| `get_daily_revenue_summary()` | Daily detailed breakdown | — |

### Product Analytics (`analytics/product.py`)

| Function | Description | Visualization |
|----------|-------------|---------------|
| `get_top_10_products_by_revenue()` | Best selling products | Horizontal bar |
| `get_top_10_products_by_quantity()` | Highest volume products | — |
| `get_category_contribution_percentage()` | Category revenue share | Donut + Bar combo |
| `get_worst_10_products()` | Lowest performing products | — |
| `get_subcategory_performance()` | Subcategory breakdown | — |
| `get_product_profit_analysis()` | Profitability by product | — |
| `get_product_affinity_analysis()` | Products bought together | — |

### Customer Analytics (`analytics/customer.py`)

| Function | Description | Visualization |
|----------|-------------|---------------|
| `get_customer_lifetime_value()` | CLV with tier classification | Histogram + KDE |
| `get_top_10_customers()` | VIP customers | Horizontal bar |
| `get_repeat_vs_new_customer_ratio()` | New vs repeat analysis | — |
| `get_average_revenue_per_customer()` | ARPC by segment | — |
| `get_customer_segmentation()` | RFM scoring | — |
| `get_customer_churn_indicators()` | At-risk customers | — |

### Store Analytics (`analytics/store.py`)

| Function | Description | Visualization |
|----------|-------------|---------------|
| `get_store_revenue_ranking()` | Store performance ranking | Bar + Pie combo |
| `get_region_performance()` | Regional metrics | Multi-panel grid |
| `get_underperforming_stores()` | Problem stores identification | — |
| `get_profit_margin_per_store()` | Store margin analysis | — |
| `get_state_performance()` | State-level metrics | — |
| `get_city_analysis()` | City-level breakdown | — |

## 📈 Visualization Examples

### Monthly Revenue Trend

```bash
python main.py revenue monthly --plot
```

**Chart Type:** Line chart with area fill

**Features:**
- Time series visualization
- Value labels on data points
- Summary statistics panel
- Growth indicator badge
- Gradient color fill

**Use Case:** Track revenue trajectory and identify seasonal patterns.

---

### Top Products by Revenue

```bash
python main.py product top10 --plot
```

**Chart Type:** Horizontal bar chart

**Features:**
- Category color coding
- Value labels on bars
- Category legend
- Sorted ranking

**Use Case:** Identify best-selling products and category performance.

---

### Category Contribution

```bash
python main.py product category --plot
```

**Chart Type:** Donut chart + Horizontal bar combo

**Features:**
- Percentage share visualization
- Dual-view comparison
- Color-coded categories
- Revenue values

**Use Case:** Understand category mix and revenue concentration.

---

### Customer Lifetime Value Distribution

```bash
python main.py customer clv --plot
```

**Chart Type:** Histogram with KDE overlay

**Features:**
- Distribution visualization
- Statistics panel (mean, median, std)
- Customer tier pie chart
- Density curve overlay

**Use Case:** Analyze customer value distribution and segment composition.

---

### Store Revenue Ranking

```bash
python main.py store ranking --plot
```

**Chart Type:** Ranked bar chart + Regional pie

**Features:**
- Gradient coloring by revenue
- Regional breakdown
- Top 15 stores display
- Value annotations

**Use Case:** Compare store performance and regional contribution.

---

### Region Performance Dashboard

```bash
python main.py store region --plot
```

**Chart Type:** Multi-panel grid (2x2)

**Features:**
- Revenue comparison
- Profit analysis
- Margin percentages
- Efficiency metrics

**Use Case:** Comprehensive regional performance review.

---

## 🎨 Visualization Style Guide

All charts follow professional styling standards:

```python
# Figure settings
plt.rcParams['figure.figsize'] = (12, 7)
plt.rcParams['figure.dpi'] = 120
plt.rcParams['savefig.dpi'] = 150

# Typography
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 11

# Colors
COLOR_PALETTE = {
    'primary': '#2E86AB',    # Blue
    'secondary': '#A23B72',  # Purple
    'accent': '#F18F01',     # Orange
    'success': '#2ECC71',    # Green
    'warning': '#F39C12',    # Yellow
    'danger': '#E74C3C',     # Red
    'info': '#3498DB'        # Light Blue
}
```

## 🔧 Configuration

### Database Connection

Set environment variables or use defaults:

```bash
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=retail_db
export DB_USER=root
export DB_PASSWORD=root
```

### Output Directory

```bash
# Save plots to custom directory
python main.py revenue monthly --plot --output my_reports
```

## 📝 SQL Techniques Used

### Window Functions

```sql
-- Month-over-Month Growth
LAG(revenue) OVER (ORDER BY year, month) AS prev_revenue,
(revenue - LAG(revenue) OVER (ORDER BY year, month)) / 
 LAG(revenue) OVER (ORDER BY year, month) * 100 AS growth_pct

-- Ranking
RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank

-- RFM Scoring
NTILE(4) OVER (ORDER BY recency DESC) AS r_score
```

### CTEs (Common Table Expressions)

```sql
WITH category_totals AS (
    SELECT category, SUM(revenue) AS category_revenue
    FROM sales_fact sf
    JOIN dim_product p ON sf.product_id = p.product_id
    GROUP BY category
),
total_revenue AS (
    SELECT SUM(category_revenue) AS grand_total 
    FROM category_totals
)
SELECT 
    ct.category,
    ct.category_revenue,
    ct.category_revenue * 100.0 / tr.grand_total AS contribution_pct
FROM category_totals ct
CROSS JOIN total_revenue tr
```

### Star Schema JOINs

```sql
SELECT 
    d.year, d.month, d.month_name,
    p.category,
    s.store_name, s.region,
    c.segment,
    SUM(sf.sales_amount) AS revenue,
    SUM(sf.profit) AS profit
FROM sales_fact sf
INNER JOIN dim_date d ON sf.date_id = d.date_id
INNER JOIN dim_product p ON sf.product_id = p.product_id
INNER JOIN dim_store s ON sf.store_id = s.store_id
INNER JOIN dim_location l ON s.location_id = l.location_id
INNER JOIN dim_customer c ON sf.customer_id = c.customer_id
GROUP BY d.year, d.month, d.month_name, 
         p.category, s.store_name, s.region, c.segment
```

## 🧪 Testing

```bash
# Test database connection
python -c "from db.connection import execute_query; print(execute_query('SELECT 1'))"

# Test a simple query
python main.py revenue total

# Test visualization generation
python main.py revenue monthly --plot
```

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| SQLAlchemy | 2.0+ | Database connection |
| PyMySQL | 1.1+ | MySQL driver |
| Pandas | 2.0+ | Data manipulation |
| Matplotlib | 3.7+ | Charting |
| Seaborn | 0.12+ | Statistical visualization |
| NumPy | 1.24+ | Numerical operations |

## 🔌 Extending the Analytics Layer

### Adding a New Analytics Function

1. **Add to appropriate module** (e.g., `analytics/revenue.py`):

```python
def get_daily_revenue_by_day_of_week() -> pd.DataFrame:
    """Get revenue breakdown by day of week."""
    query = """
    SELECT 
        d.day_name,
        d.day_of_week,
        ROUND(SUM(sf.sales_amount), 2) AS revenue,
        COUNT(*) AS transactions,
        ROUND(AVG(sf.sales_amount), 2) AS avg_order_value
    FROM sales_fact sf
    INNER JOIN dim_date d ON sf.date_id = d.date_id
    GROUP BY d.day_name, d.day_of_week
    ORDER BY d.day_of_week
    """
    return execute_query(query)
```

2. **Export in `__init__.py`**:

```python
from .revenue import get_daily_revenue_by_day_of_week

__all__ = [
    # ... existing exports
    "get_daily_revenue_by_day_of_week"
]
```

3. **Add to CLI in `main.py`**:

```python
REVENUE_COMMANDS = {
    # ... existing commands
    "day_of_week": (get_daily_revenue_by_day_of_week, "Daily Revenue by Day", None),
}
```

### Adding a New Visualization

1. **Add to `visualization/plots.py`**:

```python
def plot_day_of_week(df: pd.DataFrame, save_path: Optional[str] = None) -> plt.Figure:
    """Create bar chart for day of week revenue."""
    setup_style()
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.bar(df['day_name'], df['revenue'], 
                  color=COLOR_PALETTE['primary'])
    
    ax.set_xlabel('Day of Week')
    ax.set_ylabel('Revenue ($)')
    ax.set_title('Revenue by Day of Week')
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
    return fig
```

2. **Export in `visualization/__init__.py`**

3. **Link to command in `main.py`**:

```python
"day_of_week": (get_daily_revenue_by_day_of_week, "Daily Revenue", plot_day_of_week)
```

## 🎯 Best Practices

### Code Quality

1. **Docstrings**: Every function has a clear docstring
2. **Type hints**: All functions use type annotations
3. **No printing**: Analytics modules return DataFrames, don't print
4. **No SQL in visuals**: Visualization layer only accepts DataFrames
5. **Error handling**: Database errors are caught and reported

### SQL Quality

1. **Use CTEs**: For complex queries, break into readable parts
2. **Window functions**: Leverage for rankings, growth calculations
3. **Proper JOINs**: Always use explicit JOIN syntax
4. **NULL handling**: Use `NULLIF` to avoid division by zero
5. **Rounding**: Always round currency and percentages

### Visualization Quality

1. **Consistent styling**: Use `setup_style()` for all charts
2. **Clear labels**: Always label axes and add titles
3. **Value annotations**: Show values on bars/points
4. **Appropriate sizing**: Use figsize parameter for control
5. **High DPI**: Save at 150 DPI for publication quality

## 📄 License

MIT License - Part of the Retail Analytics Project
