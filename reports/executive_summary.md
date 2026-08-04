# Executive Summary

## Outcome

The synthetic retail analytics model is ready for portfolio use. The pipeline integrated 4,224 raw rows from CSV, Excel and SQLite, rejected 44 isolated invalid/duplicate rows, retained 4,180 validated order lines and passed 15 of 15 automated quality checks.

## KPI Scorecard

| KPI | Result |
|---|---:|
| Revenue | ₹160,100,000 |
| Profit | ₹41,300,000 |
| Profit Margin | 25.8% |
| Orders | 3,922 |
| Returned Orders | 345 |
| Return Rate | 8.8% |

## Key Findings

1. **Electronics drove scale.** It contributed ₹70.6M revenue, 44.1% of the total, with ₹14.8M profit and a 21.0% margin.
2. **Beauty & Personal Care led margin but carried return risk.** Its margin was 40.4%, while its order return rate was the highest category rate at 9.8%.
3. **Online was the primary channel.** It generated ₹76.8M revenue across 1,876 allocated orders. Retail Store had the lowest channel return rate at 7.8%.
4. **West was the largest region.** It generated ₹37.9M revenue and ₹9.7M profit.
5. **High-value retention deserves focus.** Champions represented 176 customers and ₹45.7M revenue; 194 At-Risk customers represented ₹29.5M revenue.
6. **Deep discounts compressed margin.** Margin decreased from 34.5% with no discount to 10.1% for discounts above 20%.
7. **Target attainment varied by month.** January exceeded target by 4.2%, while December reached 92.6% in both years because the synthetic targets use the same seasonal factor pattern.

## Suggested Actions

- Protect Electronics volume while reviewing product-level cost and discount rules to improve its 21.0% margin.
- Investigate Beauty & Personal Care return reasons before expanding promotions in that category.
- Create a retention campaign for high-monetary At-Risk customers and measure reactivation rate.
- Require approval for discounts above 20% and monitor contribution margin by product/channel.
- Use monthly target-attainment alerts with region and channel drill-downs.

## Caveat

The dataset is deterministic and synthetic. Findings demonstrate analytical methods and dashboard design; they should not be interpreted as real-market evidence or causal effects.

