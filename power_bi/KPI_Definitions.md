# KPI Definitions

| KPI | Definition | DAX basis | Expected all-data value |
|---|---|---|---:|
| Revenue | Sales after discount less return amount | `SUM(Fact Sales[revenue])` | ₹160.1M |
| Profit | Revenue less recognized cost | `SUM(Fact Sales[profit])` | ₹41.3M |
| Profit Margin | Profit divided by Revenue | `[Profit] / [Revenue]` | 25.8% |
| Orders | Sum of the first-line order flag | `SUM(Fact Sales[order_flag])` | 3,922 |
| Returned Orders | Sum of the first-line returned-order flag | `SUM(Fact Sales[return_order_flag])` | 345 |
| Return Rate | Returned Orders divided by Orders | `[Returned Orders] / [Orders]` | 8.8% |
| Average Order Value | Revenue divided by Orders | `[Revenue] / [Orders]` | Context dependent |
| Target Attainment | Revenue divided by Revenue Target | `[Revenue] / [Revenue Target]` | Context dependent |

All rate denominators use order flags or additive numerators to prevent double counting in multi-line orders. Currency is Indian rupees. Data covers 1 January 2024 through 31 December 2025 and is synthetic.

