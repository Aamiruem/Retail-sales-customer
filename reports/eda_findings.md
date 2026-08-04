# Exploratory Data Analysis Findings

## Revenue, Profit and Seasonality

Revenue totals ₹160.1M and profit totals ₹41.3M. Monthly revenue is higher around October–December, reflecting the deliberate seasonal weights in the synthetic generator. The pattern demonstrates time-series filtering and target comparison, not real retail seasonality.

## Category Mix

| Category | Revenue | Profit | Margin | Return Rate |
|---|---:|---:|---:|---:|
| Electronics | ₹70.6M | ₹14.8M | 21.0% | 8.5% |
| Home & Kitchen | ₹47.4M | ₹11.6M | 24.4% | 8.2% |
| Sports & Outdoors | ₹19.7M | ₹6.3M | 31.8% | 8.8% |
| Fashion | ₹14.8M | ₹5.5M | 37.4% | 9.1% |
| Beauty & Personal Care | ₹7.6M | ₹3.1M | 40.4% | 9.8% |

## Channel Performance

Online contributed ₹76.8M revenue, Retail Store ₹53.3M and Marketplace ₹30.1M. Retail Store had the lowest channel return rate at 7.8%.

## Customer RFM

Champions generated the largest segment revenue at ₹45.7M. At-Risk customers contributed ₹29.5M, making them an important retention audience. Hibernating was the largest segment by count at 268 customers.

## Discount Analysis

| Discount Band | Revenue | Profit Margin |
|---|---:|---:|
| No Discount | ₹32.3M | 34.5% |
| 1–10% | ₹68.5M | 28.4% |
| 11–20% | ₹45.9M | 20.4% |
| Above 20% | ₹13.4M | 10.1% |

The descriptive relationship is consistent with margin compression at deeper discounts. Because discount and cost behavior are generated together, the result should not be described as causal.

## Supporting Figures

- `charts/01_monthly_revenue_profit.png`
- `charts/02_category_performance.png`
- `charts/03_rfm_segments.png`
- `charts/04_discount_profit_relationship.png`
- `charts/05_return_rate_by_category.png`
- `charts/06_region_category_heatmap.png`
- `charts/07_target_attainment.png`

