# Static Image & PDF Report Generation

## Overview

This module adds documentation and report generation capabilities to Phase 3 of the Retail Analytics Pipeline. It enables automatic generation of:

1. **Static PNG images** for embedding in GitHub README and documentation
2. **PDF analytics reports** with professional formatting

## New Commands

### `generate-static`

Generates key visualization images and saves them to `docs/images/`.

```bash
python main.py generate-static
```

**What it does:**
- Fetches data for 7 key visualizations
- Generates professional charts using existing plot functions
- Saves PNG files to `docs/images/`
- Creates directory if it doesn't exist
- Prints confirmation and README embedding instructions

**Generated files:**
- `monthly_revenue.png`
- `top_products.png`
- `store_ranking.png`
- `clv_distribution.png`
- `category_contribution.png`
- `top_customers.png`
- `region_performance.png`

**Options:**
```bash
python main.py generate-static --images-dir custom/path
```

---

### `generate-report`

Creates a multi-page PDF analytics report.

```bash
python main.py generate-report
```

**What it does:**
- Creates title page with report metadata
- Generates KPI summary page with key metrics
- Adds 7 visualization pages
- Saves to `reports/analytics_report.pdf`
- Uses matplotlib's PdfPages backend (no external dependencies)

**Report structure:**
1. Title page
2. KPI summary page
3. Monthly revenue trend
4. Top products
5. Store ranking
6. CLV distribution
7. Category contribution
8. Top customers
9. Region performance

**Options:**
```bash
python main.py generate-report --report-path custom/path/report.pdf
```

---

### `generate-all`

Runs both static image and PDF report generation.

```bash
python main.py generate-all
```

**Options:**
```bash
python main.py generate-all \
  --images-dir docs/images \
  --report-path reports/analytics_report.pdf
```

---

### `readme-snippet`

Prints markdown snippet for embedding visuals in README.

```bash
python main.py readme-snippet
```

**Output:**
```markdown
## 📊 Analytics Visualizations

### 📈 Monthly Revenue Trend
![Monthly Revenue](docs/images/monthly_revenue.png)

### 🏆 Top Products by Revenue
![Top Products](docs/images/top_products.png)

... (continues for all visualizations)
```

---

## Architecture

### Module Structure

```
phases/phase-3-analytics/
├── main.py                      # CLI entry point (updated)
├── reports/                     # NEW module
│   ├── __init__.py
│   └── static_generator.py      # Report generation logic
├── analytics/                   # Existing analytics
├── db/                          # Existing database layer
└── visualization/               # Existing plots
```

### Design Decisions

#### 1. **Separation of Concerns**

The report generation logic is isolated in `reports/static_generator.py`:
- No modification to existing analytics modules
- Reuses existing `analytics/*` and `visualization/*` functions
- Clean API: `generate_static_images()`, `generate_pdf_report()`

#### 2. **No Code Duplication**

All visualizations reuse existing plot functions:
```python
KEY_VISUALIZATIONS = {
    "monthly_revenue": {
        "fetch": get_monthly_revenue_trend,      # From analytics/revenue.py
        "plot": plot_monthly_revenue,            # From visualization/plots.py
        "title": "Monthly Revenue Trend",
        "filename": "monthly_revenue.png"
    },
    # ... more visualizations
}
```

#### 3. **Configuration-Driven**

Visualizations are defined as a dictionary:
- Easy to add/remove visualizations
- Single source of truth
- No hardcoded logic scattered across functions

#### 4. **PDF Generation Without External Libraries**

Uses `matplotlib.backends.backend_pdf.PdfPages`:
- No additional dependencies (no reportlab, etc.)
- Consistent styling with matplotlib charts
- Professional output with metadata

#### 5. **Directory Management**

Automatic directory creation:
```python
def ensure_directory(directory: str) -> str:
    abs_path = os.path.abspath(directory)
    os.makedirs(abs_path, exist_ok=True)
    return abs_path
```

#### 6. **Error Handling**

Graceful degradation:
- Failed visualizations don't stop entire report
- Clear error messages with row counts
- Success/failure/skip counts in summary

#### 7. **Professional PDF Layout**

Title page includes:
- Report title and subtitle
- Generation date
- Project attribution
- Clean gradient background

KPI summary page includes:
- Key metrics in styled boxes
- Data source documentation
- Report sections preview

---

## File Structure Created

```
RetailAnalyticsProject/
├── docs/
│   └── images/                    # NEW directory
│       ├── .gitkeep
│       ├── monthly_revenue.png
│       ├── top_products.png
│       ├── store_ranking.png
│       └── ...
│
├── reports/                       # NEW directory
│   ├── .gitkeep
│   └── analytics_report.pdf
│
└── phases/phase-3-analytics/
    ├── main.py                    # UPDATED
    └── reports/                   # NEW module
        ├── __init__.py
        └── static_generator.py
```

---

## Usage Examples

### Generate Documentation Images

```bash
cd phases/phase-3-analytics

# Generate all standard images
python main.py generate-static

# Generate to custom directory
python main.py generate-static --images-dir ../../docs/images

# Overwrite existing images
python main.py generate-static  # Overwrites by default
```

### Generate PDF Report

```bash
# Standard report
python main.py generate-report

# Custom path
python main.py generate-report --report-path reports/q4_2024_report.pdf
```

### Generate Everything

```bash
# Generate both images and PDF
python main.py generate-all

# With custom paths
python main.py generate-all \
  --images-dir docs/visuals \
  --report-path reports/full_analytics_report.pdf
```

### Get README Markdown

```bash
# Print markdown snippet
python main.py readme-snippet

# Copy output to clipboard (Linux/Mac)
python main.py readme-snippet | xclip -selection clipboard

# Copy output to clipboard (Windows)
python main.py readme-snippet | clip
```

---

## Programmatic Usage

The functions can also be used programmatically:

```python
from reports.static_generator import (
    generate_static_images,
    generate_pdf_report,
    generate_all_assets,
    get_readme_snippet
)

# Generate static images
images = generate_static_images(output_dir="docs/images")
print(f"Generated {len(images)} images")

# Generate PDF report
report_path = generate_pdf_report(output_path="reports/report.pdf")
print(f"Report saved to: {report_path}")

# Generate both
images, report = generate_all_assets(
    images_dir="docs/images",
    report_path="reports/report.pdf"
)

# Get README snippet
markdown = get_readme_snippet(image_dir="docs/images")
print(markdown)
```

---

## Customization

### Adding New Visualizations

Add to `KEY_VISUALIZATIONS` dictionary:

```python
KEY_VISUALIZATIONS = {
    # ... existing visualizations
    "new_viz": {
        "fetch": get_new_analytics_function,  # From analytics module
        "plot": plot_new_chart,               # From visualization module
        "title": "New Chart Title",
        "filename": "new_chart.png"
    },
}
```

### Customizing PDF Report

Modify `create_title_page()` and `create_kpi_summary_page()`:

```python
def create_title_page(pdf, title="Custom Title", ...):
    # Customize title, colors, layout
    pass
```

### Changing Image Output Format

Modify `generate_static_images()`:

```python
# Change DPID for higher quality
fig.savefig(filepath, dpi=300, bbox_inches='tight')

# Or change format to PDF
filepath = os.path.join(output_dir, filename.replace('.png', '.pdf'))
fig.savefig(filepath, bbox_inches='tight')
```

---

## Troubleshooting

### Database Connection Error

```
❌ Error: Query execution failed: Connection refused
```

**Solution:** Ensure MySQL is running:
```bash
docker ps | grep mysql_retail
docker start mysql_retail  # If stopped
```

### Directory Permission Error

```
❌ Error: [Errno 13] Permission denied
```

**Solution:** Check directory permissions or use a different output path:
```bash
python main.py generate-static --images-dir /tmp/analytics_images
```

### Matplotlib Backend Error

```
Error: Cannot load backend 'TkAgg'
```

**Solution:** Set non-interactive backend:
```python
import matplotlib
matplotlib.use('Agg')
```

Or set environment variable:
```bash
export MPLBACKEND=Agg
```

---

## Performance Notes

- **Image generation:** ~2-5 seconds per visualization
- **PDF report:** ~15-30 seconds for full report
- **Memory usage:** Minimal (plots are closed after saving)
- **Database connections:** Reused via connection pooling

---

## Best Practices

1. **Run after data updates:** Regenerate visuals when underlying data changes
2. **Version control images:** Commit generated PNGs to git for documentation
3. **Don't commit PDFs:** Add `reports/*.pdf` to `.gitignore` (generated artifacts)
4. **Use consistent paths:** Stick to `docs/images` and `reports/` defaults
5. **Test before committing:** Verify images render correctly in README preview

---

## Future Enhancements

Potential additions:

1. **Scheduled generation:** Cron job to update visuals weekly
2. **Email reports:** Send PDF via email automatically
3. **Multiple themes:** Light/dark mode for visualizations
4. **Interactive HTML:** Generate Plotly charts for web dashboards
5. **Custom filters:** Date range, region filters for reports
6. **Comparison reports:** Period-over-period comparison PDFs

---

## Summary

| Feature | Command | Output |
|---------|---------|--------|
| Static images | `generate-static` | `docs/images/*.png` |
| PDF report | `generate-report` | `reports/*.pdf` |
| Both | `generate-all` | Images + PDF |
| README markdown | `readme-snippet` | Console output |

**Key benefits:**
- ✅ Zero new dependencies
- ✅ Reuses existing analytics code
- ✅ Professional output quality
- ✅ Easy to customize and extend
- ✅ Clean modular architecture
