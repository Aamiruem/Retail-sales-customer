# Power BI Build Kit

This folder contains everything needed to assemble the Power BI version of the dashboard from the validated star-schema extracts in `../data/processed/`.

## Included

- `power_query/Load_Star_Schema.m`: Power Query M functions and queries for every fact and dimension CSV.
- `dax/Measures.dax`: KPI, time-intelligence, target, customer and return measures.
- `dax/Validation_Queries.dax`: DAX queries that reconcile the headline KPIs.
- `theme/Retail_Insights_Theme.json`: importable Power BI theme.
- `model/star_schema.md`: table grain, relationships, cardinality and filter direction.
- `model/relationships.csv`: compact relationship checklist.
- `report_page_plan.md`: page-by-page visual and slicer specification.
- `KPI_Definitions.md`: business definitions and denominators.

## Build in Power BI Desktop

1. Open Power BI Desktop and create a blank report.
2. Import `theme/Retail_Insights_Theme.json` from **View → Themes → Browse for themes**.
3. Open **Transform data → New Source → Blank Query → Advanced Editor**.
4. Copy the shared function and each query from `power_query/Load_Star_Schema.m`.
5. Change the `ProjectRoot` parameter to the absolute path of this project folder.
6. Rename the imported tables exactly as documented in `model/star_schema.md`.
7. Create the relationships with single-direction filtering from dimensions to `Fact Sales`.
8. Mark `Dim Date[Date]` as the date table.
9. Add all measures in `dax/Measures.dax` to a dedicated measures table.
10. Build the five report pages from `report_page_plan.md` and run the validation queries.

## Why no compiled PBIX is included

PBIX is a compiled Power BI Desktop artifact and cannot be authored or visually verified in this Linux build environment. The supplied inputs are the complete, auditable source kit; compile the report in Power BI Desktop and save it as `.pbix` or `.pbip` after verification.

Microsoft references:

- https://learn.microsoft.com/en-us/power-query/power-query-what-is-power-query
- https://learn.microsoft.com/en-us/dax/dax-overview
- https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview

