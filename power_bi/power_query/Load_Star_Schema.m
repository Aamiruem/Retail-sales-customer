// Retail Sales & Customer Insights - Power Query M build script
// Create one text parameter named ProjectRoot before pasting these queries.

// Query: fnLoadCsv
(RelativePath as text, TypeMap as list) as table =>
let
    FullPath = ProjectRoot & RelativePath,
    Source = Csv.Document(
        File.Contents(FullPath),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    TrimmedText = Table.TransformColumns(
        PromotedHeaders,
        List.Transform(
            Table.ColumnsOfType(PromotedHeaders, {type text}),
            each {_, Text.Trim, type text}
        )
    ),
    Typed = Table.TransformColumnTypes(TrimmedText, TypeMap, "en-IN")
in
    Typed

// Query: Fact Sales
let
    Source = fnLoadCsv(
        "\\data\\processed\\fact_sales.csv",
        {
            {"sale_key", Int64.Type}, {"line_id", type text}, {"order_id", type text},
            {"date_key", Int64.Type}, {"customer_key", Int64.Type}, {"product_key", Int64.Type},
            {"store_key", Int64.Type}, {"channel", type text}, {"quantity", Int64.Type},
            {"unit_price", Currency.Type}, {"discount_pct", Percentage.Type},
            {"gross_sales", Currency.Type}, {"discount_amount", Currency.Type},
            {"sales_after_discount", Currency.Type}, {"return_flag", Int64.Type},
            {"return_amount", Currency.Type}, {"revenue", Currency.Type},
            {"unit_cost", Currency.Type}, {"cost_amount", Currency.Type}, {"profit", Currency.Type},
            {"payment_method", type text}, {"rating", type number}, {"rating_was_imputed", Int64.Type},
            {"order_flag", Int64.Type}, {"return_order_flag", Int64.Type}, {"ship_days", Int64.Type},
            {"year_month", type text}
        }
    ),
    ValidRows = Table.SelectRows(Source, each [quantity] > 0 and [discount_pct] >= 0 and [discount_pct] <= 0.60),
    AddedProfitMargin = Table.AddColumn(ValidRows, "profit_margin", each if [revenue] = 0 then null else [profit] / [revenue], Percentage.Type),
    AddedDiscountBand = Table.AddColumn(
        AddedProfitMargin,
        "discount_band",
        each if [discount_pct] = 0 then "No Discount"
        else if [discount_pct] <= 0.10 then "1-10%"
        else if [discount_pct] <= 0.20 then "11-20%"
        else "Above 20%",
        type text
    )
in
    AddedDiscountBand

// Query: Dim Date
let
    Source = fnLoadCsv(
        "\\data\\processed\\dim_date.csv",
        {
            {"date_key", Int64.Type}, {"date", type date}, {"year", Int64.Type},
            {"quarter", type text}, {"month_no", Int64.Type}, {"month_name", type text},
            {"year_month", type text}, {"week_of_year", Int64.Type}, {"day_name", type text},
            {"is_weekend", Int64.Type}
        }
    ),
    AddedMonthSort = Table.AddColumn(Source, "year_month_sort", each [year] * 100 + [month_no], Int64.Type)
in
    AddedMonthSort

// Query: Dim Customer
let
    Source = fnLoadCsv(
        "\\data\\processed\\dim_customer.csv",
        {
            {"customer_key", Int64.Type}, {"customer_id", type text}, {"customer_name", type text},
            {"customer_segment", type text}, {"region", type text}, {"state", type text},
            {"city", type text}, {"recency_days", Int64.Type}, {"frequency", Int64.Type},
            {"monetary", Currency.Type}, {"r_score", Int64.Type}, {"f_score", Int64.Type},
            {"m_score", Int64.Type}, {"rfm_score", Int64.Type}, {"rfm_segment", type text}
        }
    )
in
    Source

// Query: Dim Product
let
    Source = fnLoadCsv(
        "\\data\\processed\\dim_product.csv",
        {
            {"product_key", Int64.Type}, {"product_id", type text}, {"product_name", type text},
            {"category", type text}, {"subcategory", type text}
        }
    )
in
    Source

// Query: Dim Store
let
    Source = fnLoadCsv(
        "\\data\\processed\\dim_store.csv",
        {{"store_key", Int64.Type}, {"store_id", type text}, {"channel", type text}}
    )
in
    Source

// Query: Monthly Targets
let
    Source = fnLoadCsv(
        "\\data\\processed\\monthly_targets.csv",
        {{"year_month", type text}, {"target_revenue", Currency.Type}, {"target_profit", Currency.Type}}
    )
in
    Source

