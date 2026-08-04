PRAGMA foreign_keys = ON;

CREATE TABLE dim_date (
    date_key       INTEGER PRIMARY KEY,
    date           TEXT NOT NULL UNIQUE,
    year           INTEGER NOT NULL,
    quarter        TEXT NOT NULL,
    month_no       INTEGER NOT NULL CHECK (month_no BETWEEN 1 AND 12),
    month_name     TEXT NOT NULL,
    year_month     TEXT NOT NULL,
    week_of_year   INTEGER NOT NULL,
    day_name       TEXT NOT NULL,
    is_weekend     INTEGER NOT NULL CHECK (is_weekend IN (0, 1))
);

CREATE TABLE dim_customer (
    customer_key       INTEGER PRIMARY KEY,
    customer_id        TEXT NOT NULL UNIQUE,
    customer_name      TEXT NOT NULL,
    customer_segment   TEXT NOT NULL,
    region             TEXT NOT NULL,
    state              TEXT NOT NULL,
    city               TEXT NOT NULL,
    recency_days       INTEGER NOT NULL,
    frequency          INTEGER NOT NULL,
    monetary           REAL NOT NULL,
    r_score            INTEGER NOT NULL,
    f_score            INTEGER NOT NULL,
    m_score            INTEGER NOT NULL,
    rfm_score          INTEGER NOT NULL,
    rfm_segment        TEXT NOT NULL
);

CREATE TABLE dim_product (
    product_key    INTEGER PRIMARY KEY,
    product_id     TEXT NOT NULL UNIQUE,
    product_name   TEXT NOT NULL,
    category       TEXT NOT NULL,
    subcategory    TEXT NOT NULL
);

CREATE TABLE dim_store (
    store_key   INTEGER PRIMARY KEY,
    store_id    TEXT NOT NULL UNIQUE,
    channel     TEXT NOT NULL
);

CREATE TABLE monthly_targets (
    year_month       TEXT PRIMARY KEY,
    target_revenue   REAL NOT NULL,
    target_profit    REAL NOT NULL
);

CREATE TABLE fact_sales (
    sale_key             INTEGER PRIMARY KEY,
    line_id              TEXT NOT NULL UNIQUE,
    order_id             TEXT NOT NULL,
    date_key             INTEGER NOT NULL,
    customer_key         INTEGER NOT NULL,
    product_key          INTEGER NOT NULL,
    store_key            INTEGER NOT NULL,
    channel              TEXT NOT NULL,
    quantity             INTEGER NOT NULL CHECK (quantity > 0),
    unit_price           REAL NOT NULL,
    discount_pct         REAL NOT NULL CHECK (discount_pct BETWEEN 0 AND 0.60),
    gross_sales          REAL NOT NULL,
    discount_amount      REAL NOT NULL,
    sales_after_discount REAL NOT NULL,
    return_flag          INTEGER NOT NULL CHECK (return_flag IN (0, 1)),
    return_amount        REAL NOT NULL,
    revenue              REAL NOT NULL,
    unit_cost            REAL NOT NULL,
    cost_amount          REAL NOT NULL,
    profit               REAL NOT NULL,
    payment_method       TEXT NOT NULL,
    rating               REAL NOT NULL,
    rating_was_imputed   INTEGER NOT NULL CHECK (rating_was_imputed IN (0, 1)),
    order_flag           INTEGER NOT NULL CHECK (order_flag IN (0, 1)),
    return_order_flag    INTEGER NOT NULL CHECK (return_order_flag IN (0, 1)),
    ship_days            INTEGER NOT NULL CHECK (ship_days >= 0),
    year_month           TEXT NOT NULL,
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
    FOREIGN KEY (store_key) REFERENCES dim_store(store_key),
    FOREIGN KEY (year_month) REFERENCES monthly_targets(year_month)
);

CREATE TABLE customer_rfm (
    customer_id        TEXT PRIMARY KEY,
    customer_name      TEXT NOT NULL,
    customer_segment   TEXT NOT NULL,
    last_order_date    TEXT NOT NULL,
    frequency          INTEGER NOT NULL,
    monetary           REAL NOT NULL,
    profit             REAL NOT NULL,
    returned_orders    INTEGER NOT NULL,
    recency_days       INTEGER NOT NULL,
    r_score            INTEGER NOT NULL,
    f_score            INTEGER NOT NULL,
    m_score            INTEGER NOT NULL,
    rfm_score          INTEGER NOT NULL,
    rfm_segment        TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id)
);

CREATE INDEX idx_fact_sales_order_id ON fact_sales(order_id);
CREATE INDEX idx_fact_sales_date_key ON fact_sales(date_key);
CREATE INDEX idx_fact_sales_customer_key ON fact_sales(customer_key);
CREATE INDEX idx_fact_sales_product_key ON fact_sales(product_key);
CREATE INDEX idx_fact_sales_store_key ON fact_sales(store_key);
CREATE INDEX idx_fact_sales_year_month ON fact_sales(year_month);

CREATE VIEW vw_sales_enriched AS
SELECT
    f.sale_key,
    f.line_id,
    f.order_id,
    d.date,
    d.year,
    d.quarter,
    d.year_month,
    c.customer_id,
    c.customer_name,
    c.customer_segment,
    c.rfm_segment,
    c.region,
    c.state,
    c.city,
    p.product_id,
    p.product_name,
    p.category,
    p.subcategory,
    s.store_id,
    f.channel,
    f.quantity,
    f.discount_pct,
    f.return_flag,
    f.revenue,
    f.profit,
    f.order_flag,
    f.return_order_flag
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
JOIN dim_customer c ON f.customer_key = c.customer_key
JOIN dim_product p ON f.product_key = p.product_key
JOIN dim_store s ON f.store_key = s.store_key;

