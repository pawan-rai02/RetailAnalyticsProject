# Phase 3: Analytics & Visualization Layer - Architecture

## Overview

Phase 3 builds a business intelligence analytics layer on top of the MySQL star schema created in Phase 1. It provides 25+ pre-built retail KPIs with professional visualizations, all accessible via a clean CLI interface.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PHASE 3 ANALYTICS LAYER                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐     ┌──────────────────────────────────────────────────┐   │
│  │   CLI       │     │              ANALYTICS MODULES                    │   │
│  │   main.py   │────▶│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────┐│   │
│  │             │     │  │ Revenue  │ │ Product  │ │ Customer │ │Store ││   │
│  │  - parse    │     │  │  8 funcs │ │  8 funcs │ │  7 funcs │ │8 func││   │
│  │  - dispatch │     │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └──┬───┘│   │
│  │  - display  │     │       │            │            │          │     │   │
│  └─────────────┘     └───────┼────────────┼────────────┼──────────┼─────┘   │
│         │                    │            │            │          │          │
│         │              ┌─────┴────────────┴────────────┴──────────┴─────┐   │
│         │              │           DB CONNECTION LAYER                   │   │
│         │              │        db/connection.py (SQLAlchemy)            │   │
│         │              │         - get_engine()                          │   │
│         │              │         - execute_query()                       │   │
│         │              └─────────────────────┬───────────────────────────┘   │
│         │                                    │                               │
│         │         ┌──────────────────────────┘                               │
│         │         │                                                          │
│         ▼         ▼                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    VISUALIZATION LAYER                               │    │
│  │              visualization/plots.py (Matplotlib/Seaborn)             │    │
│  │                                                                      │    │
│  │   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │    │
│  │   │ Line Charts │  Bar Charts  │  Pie/Donut   │  Histogram   │   │    │
│  │   │             │  Horizontal  │  Combined    │  + KDE       │   │    │
│  │   └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                          ┌───────────────────────┐
                          │   MySQL Star Schema   │
                          │   (Phase 1 Tables)    │
                          │                       │
                          │  - sales_fact         │
                          │  - dim_product        │
                          │  - dim_customer       │
                          │  - dim_store          │
                          │  - dim_location       │
                          │  - dim_date           │
                          └───────────────────────┘
```

## Design Principles

### 1. Separation of Concerns

Each layer has a single, well-defined responsibility:

| Layer | Responsibility | Files |
|-------|---------------|-------|
| **CLI** | Command parsing, result display | `main.py` |
| **Analytics** | SQL queries, KPI computation | `analytics/*.py` |
| **Database** | Connection management, query execution | `db/connection.py` |
| **Visualization** | Chart generation from DataFrames | `visualization/plots.py` |

### 2. No SQL in Visualization Layer

Visualizations accept only Pandas DataFrames - they have no knowledge of the database:

```python
# ✅ Correct: Visualization accepts DataFrame
def plot_monthly_revenue(df: pd.DataFrame) -> plt.Figure:
    # No SQL here - just plotting
    pass

# ❌ Wrong: Don't do this
def plot_monthly_revenue() -> plt.Figure:
    query = "SELECT ..."  # Never do this in visualization layer
    df = execute_query(query)
    pass
```

### 3. Modular Analytics Functions

Each analytics function:
- Is self-contained
- Returns a Pandas DataFrame
- Has a clear docstring
- Uses proper SQL (JOINs, window functions, aggregations)

```python
def get_month_over_month_growth() -> pd.DataFrame:
    """
    Calculate month-over-month revenue growth using window functions.
    
    Returns:
        pd.DataFrame: Monthly revenue with MoM growth percentage.
    """
    query = """
    WITH monthly_revenue AS (
        SELECT 
            d.year, d.month, d.month_name,
            ROUND(SUM(sf.sales_amount), 2) AS revenue
        FROM sales_fact sf
        INNER JOIN dim_date d ON sf.date_id = d.date_id
        GROUP BY d.year, d.month, d.month_name
    )
    SELECT 
        year, month, month_name, revenue,
        LAG(revenue) OVER (ORDER BY year, month) AS prev_month_revenue,
        ROUND((revenue - LAG(revenue) OVER (ORDER BY year, month)) / 
              NULLIF(LAG(revenue) OVER (ORDER BY year, month), 0) * 100, 2) 
              AS mom_growth_pct
    FROM monthly_revenue
    """
    return execute_query(query)
```

### 4. Professional Visualization Standards

All charts follow these standards:
- Consistent color palette
- Clear labels and titles
- Appropriate figure sizes
- Value annotations where helpful
- Summary statistics panels
- Publication-quality DPI (150+)

## Module Details

### Database Layer (`db/connection.py`)

```python
# Connection Manager with singleton pattern
class ConnectionManager:
    _engine: Optional[Engine] = None
    
    @classmethod
    def get_engine(cls) -> Engine:
        if cls._engine is None:
            # Create engine with connection pooling
            cls._engine = create_engine(
                f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}",
                pool_size=10,
                max_overflow=20,
                pool_recycle=3600,
                pool_pre_ping=True
            )
        return cls._engine

# Simple query execution
def execute_query(query: str) -> pd.DataFrame:
    engine = get_engine()
    with engine.connect() as connection:
        result = connection.execute(text(query))
        return pd.DataFrame(result.fetchall(), columns=result.keys())
```

### Analytics Layer

#### Revenue Analytics (`analytics/revenue.py`)

| Function | Description | SQL Techniques |
|----------|-------------|----------------|
| `get_total_revenue()` | Overall revenue KPIs | SUM, COUNT, AVG |
| `get_monthly_revenue_trend()` | Monthly time series | GROUP BY date dimensions |
| `get_yearly_revenue()` | Annual comparison | GROUP BY year |
| `get_month_over_month_growth()` | MoM growth % | LAG window function |
| `get_weekend_vs_weekday_sales()` | Day type analysis | CASE, percentage calc |
| `get_quarterly_revenue()` | Quarterly breakdown | GROUP BY quarter |

#### Product Analytics (`analytics/product.py`)

| Function | Description | SQL Techniques |
|----------|-------------|----------------|
| `get_top_10_products_by_revenue()` | Best sellers | ORDER BY, LIMIT |
| `get_top_10_products_by_quantity()` | Volume leaders | SUM quantity |
| `get_category_contribution_percentage()` | Category share | CTE, percentage |
| `get_worst_10_products()` | Underperformers | HAVING, ASC order |
| `get_product_affinity_analysis()` | Basket analysis | Self-join on order_id |

#### Customer Analytics (`analytics/customer.py`)

| Function | Description | SQL Techniques |
|----------|-------------|----------------|
| `get_customer_lifetime_value()` | CLV calculation | Aggregations, tier CASE |
| `get_top_10_customers()` | VIP customers | Multiple metrics |
| `get_customer_segmentation()` | RFM scoring | NTILE window function |
| `get_customer_cohort_analysis()` | Retention cohorts | CTE, date math |
| `get_customer_churn_indicators()` | At-risk customers | DATEDIFF, risk flags |

#### Store Analytics (`analytics/store.py`)

| Function | Description | SQL Techniques |
|----------|-------------|----------------|
| `get_store_revenue_ranking()` | Store performance | RANK window function |
| `get_region_performance()` | Regional analysis | Multiple aggregations |
| `get_underperforming_stores()` | Problem stores | CROSS JOIN averages |
| `get_profit_margin_per_store()` | Margin analysis | Percentage calculations |
| `get_state_performance()` | State-level metrics | GROUP BY state |

### Visualization Layer (`visualization/plots.py`)

#### Chart Types

| Chart | Use Case | Example |
|-------|----------|---------|
| **Line with Area Fill** | Time series trends | Monthly revenue |
| **Horizontal Bar** | Ranked comparisons | Top products |
| **Donut + Bar Combo** | Category breakdown | Category contribution |
| **Histogram + KDE** | Distribution analysis | CLV distribution |
| **Multi-panel Grid** | Multi-metric views | Region performance |

#### Style Configuration

```python
# Professional styling
plt.rcParams['figure.figsize'] = (12, 7)
plt.rcParams['figure.dpi'] = 120
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 14

# Color palette
COLOR_PALETTE = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'accent': '#F18F01',
    'success': '#2ECC71',
    'danger': '#E74C3C'
}
```

## CLI Usage

### Command Structure

```bash
python main.py <category> <command> [--plot] [--output <dir>]
```

### Available Commands

```bash
# List all commands
python main.py list

# Revenue analytics
python main.py revenue monthly
python main.py revenue monthly --plot
python main.py revenue yearly --plot

# Product analytics
python main.py product top10 --plot
python main.py product category --plot

# Customer analytics
python main.py customer clv --plot
python main.py customer top10

# Store analytics
python main.py store ranking --plot
python main.py store region --plot

# Run all analytics
python main.py all --plot
```

## SQL Best Practices Used

### 1. Proper Star Schema JOINs

```sql
SELECT 
    d.year, d.month,
    p.category,
    s.region,
    SUM(sf.sales_amount) AS revenue
FROM sales_fact sf
INNER JOIN dim_date d ON sf.date_id = d.date_id
INNER JOIN dim_product p ON sf.product_id = p.product_id
INNER JOIN dim_store s ON sf.store_id = s.store_id
GROUP BY d.year, d.month, p.category, s.region
```

### 2. Window Functions for Analytics

```sql
-- Month-over-Month Growth
LAG(revenue) OVER (ORDER BY year, month) AS prev_revenue,
(revenue - LAG(revenue) OVER (ORDER BY year, month)) / 
LAG(revenue) OVER (ORDER BY year, month) * 100 AS growth_pct

-- Ranking
RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank

-- RFM Segmentation
NTILE(4) OVER (ORDER BY recency DESC) AS r_score,
NTILE(4) OVER (ORDER BY frequency ASC) AS f_score,
NTILE(4) OVER (ORDER BY monetary ASC) AS m_score
```

### 3. CTEs for Complex Queries

```sql
WITH category_totals AS (
    SELECT category, SUM(revenue) AS category_revenue
    FROM ...
    GROUP BY category
),
total_revenue AS (
    SELECT SUM(category_revenue) AS grand_total FROM category_totals
)
SELECT 
    ct.category,
    ct.category_revenue,
    ct.category_revenue * 100.0 / tr.grand_total AS contribution_pct
FROM category_totals ct
CROSS JOIN total_revenue tr
```

## File Structure

```
phases/phase-3-analytics/
│
├── main.py                 # CLI entry point
├── requirements.txt        # Dependencies
│
├── db/
│   ├── __init__.py
│   └── connection.py       # SQLAlchemy connection
│
├── analytics/
│   ├── __init__.py
│   ├── revenue.py          # Revenue KPIs
│   ├── product.py          # Product KPIs
│   ├── customer.py         # Customer KPIs
│   └── store.py            # Store KPIs
│
└── visualization/
    ├── __init__.py
    └── plots.py            # Chart generation
```

## Testing the Layer

```bash
# 1. Ensure MySQL is running with Phase 1 data
docker ps | grep mysql_retail

# 2. Install dependencies
cd phases/phase-3-analytics
pip install -r requirements.txt

# 3. Test database connection
python -c "from db.connection import execute_query; print(execute_query('SELECT 1'))"

# 4. Run a simple query
python main.py revenue total

# 5. Generate a visualization
python main.py revenue monthly --plot
```

## Performance Considerations

1. **Connection Pooling**: SQLAlchemy engine reuses connections
2. **Efficient SQL**: Uses appropriate indexes via star schema
3. **LIMIT clauses**: Prevents large result sets
4. **Aggregations in SQL**: Done in database, not Python
5. **Single queries**: No N+1 query patterns

## Extension Points

To add new analytics:

1. **Add function to appropriate module** (`analytics/revenue.py`, etc.)
2. **Add to `__init__.py` exports**
3. **Add command mapping in `main.py`**
4. **(Optional) Add visualization in `visualization/plots.py`**

Example:

```python
# analytics/revenue.py
def get_daily_revenue_by_day_of_week() -> pd.DataFrame:
    query = """
    SELECT 
        d.day_name,
        ROUND(SUM(sf.sales_amount), 2) AS revenue,
        COUNT(*) AS transactions
    FROM sales_fact sf
    INNER JOIN dim_date d ON sf.date_id = d.date_id
    GROUP BY d.day_name, d.day_of_week
    ORDER BY d.day_of_week
    """
    return execute_query(query)

# main.py - add to REVENUE_COMMANDS
"daily_week": (get_daily_revenue_by_day_of_week, "Daily Revenue by Day", plot_daily_week)
```

## Summary

Phase 3 provides a production-ready analytics layer with:

- ✅ **25+ pre-built retail KPIs**
- ✅ **Professional visualizations**
- ✅ **Clean modular architecture**
- ✅ **Separation of concerns**
- ✅ **CLI interface**
- ✅ **Extensible design**
