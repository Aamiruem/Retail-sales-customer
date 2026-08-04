# Data Quality Report

## Dataset and Grain

- Dataset: synthetic Indian retail transactions.
- Raw grain: intended one row per order line across CSV, Excel and SQLite sources.
- Analytical grain: one validated row per unique `line_id`.
- Date coverage: 1 January 2024 through 31 December 2025.

## Quality Result

**Overall assessment: Ready.** All 15 automated checks passed.

| Measure | Result |
|---|---:|
| Raw rows | 4,224 |
| Validated rows | 4,180 |
| Rejected rows | 44 |
| Acceptance rate | 98.96% |
| Imputed optional ratings | 31 |
| Duplicate rate in raw data | 0.24% |

## Rejections

| Reason | Evidence | Severity | Treatment |
|---|---:|---|---|
| Duplicate `line_id` | 10 | Critical | Keep first occurrence and reject duplicate |
| Missing `customer_id` | 8 | Critical | Reject; customer relationship cannot be trusted |
| Invalid date | 8 | High | Reject; time analysis and shipping interval are invalid |
| Non-positive quantity | 6 | High | Reject; violates fact-domain rule |
| Invalid discount | 6 | High | Reject; outside accepted 0%–60% range |
| Invalid product key | 6 | Critical | Reject; breaks product referential integrity |

## Validations Performed

- Completeness: required identifiers populated after cleaning.
- Uniqueness: 4,180 unique `line_id` values for 4,180 fact rows.
- Validity: dates parse; ship date is not before order date; quantity is positive; discounts are valid.
- Integrity: all product, customer, date and store foreign keys resolve.
- Arithmetic: Revenue = Sales After Discount − Return Amount; Profit = Revenue − Cost.
- Reconciliation: ₹160.1M revenue, ₹41.3M profit, 3,922 orders and 345 returned orders.
- Join safety: the enriched SQL view has the same row count as the fact table.

## Automated Monitoring

Stable rules are implemented in `tests/`, `src/data_quality.py` and `sql/06_data_quality_checks.sql`. The CI workflow rebuilds the pipeline and reruns the quality contract on each push and pull request.

## Assumptions

- Optional missing ratings are acceptable and imputed with the observed median.
- Revenue is recognized net of discounts and full return amounts.
- Multi-line order metrics use first-line flags to prevent double counting.
- Currency is INR and calendar dates are treated in Asia/Kolkata business context.

