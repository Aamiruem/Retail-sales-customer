import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const projectRoot = path.resolve(process.argv[2]);
const previewDir = path.resolve(process.argv[3]);
const payloadPath = path.join(projectRoot, "data", "processed", "excel_dashboard_payload.json");
const outputPath = path.join(projectRoot, "excel", "Retail_Sales_Customer_Insights_Dashboard.xlsx");
const payload = JSON.parse(await fs.readFile(payloadPath, "utf8"));

await fs.mkdir(previewDir, { recursive: true });

const workbook = Workbook.create();
workbook.comments.setSelf({ displayName: "Aamir Husain Azad" });

const dashboard = workbook.worksheets.add("Dashboard");
const transactions = workbook.worksheets.add("Transactions");
const monthly = workbook.worksheets.add("Monthly KPIs");
const category = workbook.worksheets.add("Category Analysis");
const rfm = workbook.worksheets.add("Customer RFM");
const quality = workbook.worksheets.add("Data Quality");
const dictionary = workbook.worksheets.add("Data Dictionary");

const BLUE = "#2563EB";
const NAVY = "#17365D";
const GOLD = "#D4A72C";
const ORANGE = "#E57A32";
const OLIVE = "#7B8B3A";
const PINK = "#C65D8A";
const INK = "#1F2937";
const MUTED = "#64748B";
const PALE = "#F5F7FB";
const GRID = "#DDE3EA";
const WHITE = "#FFFFFF";

function styleHeader(range, fill = NAVY) {
  range.format = {
    fill,
    font: { name: "Aptos Display", bold: true, color: WHITE, size: 10 },
    verticalAlignment: "center",
    horizontalAlignment: "center",
    rowHeight: 26,
  };
}

function writeTable(sheet, startRow, startCol, headers, rows, tableName) {
  const matrix = [headers, ...rows.map((row) => headers.map((header) => row[header] ?? null))];
  const range = sheet.getRangeByIndexes(startRow, startCol, matrix.length, headers.length);
  range.values = matrix;
  styleHeader(sheet.getRangeByIndexes(startRow, startCol, 1, headers.length));
  const table = sheet.tables.add(range, true, tableName);
  table.style = "TableStyleMedium2";
  return { range, table };
}

// Transactions sheet
const transactionColumns = [
  ["line_id", "Line ID"], ["order_id", "Order ID"], ["order_date", "Order Date"], ["ship_date", "Ship Date"],
  ["customer_id", "Customer ID"], ["customer_name", "Customer Name"], ["customer_segment", "Customer Segment"],
  ["region", "Region"], ["state", "State"], ["city", "City"], ["store_id", "Store ID"], ["channel", "Channel"],
  ["product_id", "Product ID"], ["product_name", "Product Name"], ["category", "Category"], ["subcategory", "Subcategory"],
  ["quantity", "Quantity"], ["unit_price", "Unit Price"], ["discount_pct", "Discount %"], ["gross_sales", "Gross Sales"],
  ["discount_amount", "Discount Amount"], ["sales_after_discount", "Sales After Discount"], ["return_flag", "Return Flag"],
  ["return_amount", "Return Amount"], ["revenue", "Revenue"], ["cost_amount", "Cost Amount"], ["profit", "Profit"],
  ["payment_method", "Payment Method"], ["rating", "Rating"], ["year_month", "Year Month"], ["order_flag", "Order Flag"],
  ["return_order_flag", "Return Order Flag"], ["profit_margin", "Profit Margin"], ["discount_band", "Discount Band"],
  ["ship_days", "Ship Days"], ["source_system", "Source System"],
];
const transactionHeaders = transactionColumns.map(([, label]) => label);
const transactionRows = payload.transactions.map((row) => Object.fromEntries(transactionColumns.map(([key, label]) => [label, row[key]])));
writeTable(transactions, 0, 0, transactionHeaders, transactionRows, "TransactionsTable");
transactions.showGridLines = false;
transactions.freezePanes.freezeRows(1);
transactions.getRange(`A1:AJ${transactionRows.length + 1}`).format.font = { name: "Aptos", size: 9 };
transactions.getRange(`C2:D${transactionRows.length + 1}`).format.numberFormat = "yyyy-mm-dd";
transactions.getRange(`Q2:Q${transactionRows.length + 1}`).format.numberFormat = "0";
transactions.getRange(`R2:R${transactionRows.length + 1}`).format.numberFormat = "₹#,##0.00";
transactions.getRange(`S2:S${transactionRows.length + 1}`).format.numberFormat = "0.0%";
transactions.getRange(`T2:AA${transactionRows.length + 1}`).format.numberFormat = "₹#,##0.00";
transactions.getRange(`AC2:AC${transactionRows.length + 1}`).format.numberFormat = "0.0";
transactions.getRange(`AG2:AG${transactionRows.length + 1}`).format.numberFormat = "0.0%";
transactions.getRange(`A1:AJ25`).format.autofitColumns();
for (const col of ["F", "J", "N", "O", "P", "AB", "AH"]) transactions.getRange(`${col}:${col}`).format.columnWidth = 19;

const lastTransactionRow = transactionRows.length + 1;

// Monthly KPI formulas
monthly.showGridLines = false;
monthly.getRange("A1:I1").values = [["Year Month", "Revenue", "Profit", "Profit Margin", "Orders", "Returned Orders", "Return Rate", "Revenue Target", "Target Attainment"]];
styleHeader(monthly.getRange("A1:I1"));
monthly.getRange(`A2:A${payload.monthly.length + 1}`).values = payload.monthly.map((row) => [row.year_month]);
monthly.getRange(`H2:H${payload.monthly.length + 1}`).values = payload.monthly.map((row) => [row.target_revenue]);
monthly.getRange("B2").formulas = [[`=ROUND(SUMIFS('Transactions'!$Y$2:$Y$${lastTransactionRow},'Transactions'!$AD$2:$AD$${lastTransactionRow},$A2),2)`]];
monthly.getRange(`B2:B${payload.monthly.length + 1}`).fillDown();
monthly.getRange("C2").formulas = [[`=ROUND(SUMIFS('Transactions'!$AA$2:$AA$${lastTransactionRow},'Transactions'!$AD$2:$AD$${lastTransactionRow},$A2),2)`]];
monthly.getRange(`C2:C${payload.monthly.length + 1}`).fillDown();
monthly.getRange("D2").formulas = [["=IF(B2=0,0,C2/B2)"]];
monthly.getRange(`D2:D${payload.monthly.length + 1}`).fillDown();
monthly.getRange("E2").formulas = [[`=SUMIFS('Transactions'!$AE$2:$AE$${lastTransactionRow},'Transactions'!$AD$2:$AD$${lastTransactionRow},$A2)`]];
monthly.getRange(`E2:E${payload.monthly.length + 1}`).fillDown();
monthly.getRange("F2").formulas = [[`=SUMIFS('Transactions'!$AF$2:$AF$${lastTransactionRow},'Transactions'!$AD$2:$AD$${lastTransactionRow},$A2)`]];
monthly.getRange(`F2:F${payload.monthly.length + 1}`).fillDown();
monthly.getRange("G2").formulas = [["=IF(E2=0,0,F2/E2)"]];
monthly.getRange(`G2:G${payload.monthly.length + 1}`).fillDown();
monthly.getRange("I2").formulas = [["=IF(H2=0,0,B2/H2)"]];
monthly.getRange(`I2:I${payload.monthly.length + 1}`).fillDown();
monthly.getRange(`B2:C${payload.monthly.length + 1}`).setNumberFormat('"₹"#,##0.00');
monthly.getRange(`D2:D${payload.monthly.length + 1}`).setNumberFormat("0.0%");
monthly.getRange(`E2:F${payload.monthly.length + 1}`).setNumberFormat("#,##0");
monthly.getRange(`G2:G${payload.monthly.length + 1}`).setNumberFormat("0.0%");
monthly.getRange(`H2:H${payload.monthly.length + 1}`).format = { fill: "#E8F0FE", font: { color: BLUE } };
monthly.getRange(`H2:H${payload.monthly.length + 1}`).setNumberFormat('"₹"#,##0.00');
monthly.getRange(`I2:I${payload.monthly.length + 1}`).setNumberFormat("0.0%");
monthly.getRange(`A1:I${payload.monthly.length + 1}`).format.borders = { preset: "insideHorizontal", style: "thin", color: GRID };
monthly.getRange("K1:M1").values = [["Year Month", "Actual Revenue", "Revenue Target"]];
styleHeader(monthly.getRange("K1:M1"), BLUE);
monthly.getRange("K2").formulas = [["=A2"]];
monthly.getRange(`K2:K${payload.monthly.length + 1}`).fillDown();
monthly.getRange("L2").formulas = [["=B2"]];
monthly.getRange(`L2:L${payload.monthly.length + 1}`).fillDown();
monthly.getRange("M2").formulas = [["=H2"]];
monthly.getRange(`M2:M${payload.monthly.length + 1}`).fillDown();
monthly.getRange(`L2:M${payload.monthly.length + 1}`).setNumberFormat('"₹"#,##0.00');
monthly.getRange("A1:M25").format.autofitColumns();
monthly.getRange("A:A").format.columnWidth = 12;
for (const column of ["B", "C", "H", "L", "M"]) monthly.getRange(`${column}:${column}`).format.columnWidth = 17;
for (const column of ["D", "E", "F", "G", "I"]) monthly.getRange(`${column}:${column}`).format.columnWidth = 14;
monthly.getRange("K:K").format.columnWidth = 12;
monthly.freezePanes.freezeRows(1);

// Category and channel analysis
category.showGridLines = false;
category.getRange("A1:H1").values = [["Category", "Revenue", "Profit", "Profit Margin", "Orders", "Returned Orders", "Return Rate", "Discount Amount"]];
styleHeader(category.getRange("A1:H1"));
category.getRange(`A2:A${payload.category.length + 1}`).values = payload.category.map((row) => [row.category]);
category.getRange("B2").formulas = [[`=ROUND(SUMIFS('Transactions'!$Y$2:$Y$${lastTransactionRow},'Transactions'!$O$2:$O$${lastTransactionRow},$A2),2)`]];
category.getRange(`B2:B${payload.category.length + 1}`).fillDown();
category.getRange("C2").formulas = [[`=ROUND(SUMIFS('Transactions'!$AA$2:$AA$${lastTransactionRow},'Transactions'!$O$2:$O$${lastTransactionRow},$A2),2)`]];
category.getRange(`C2:C${payload.category.length + 1}`).fillDown();
category.getRange("D2").formulas = [["=IF(B2=0,0,C2/B2)"]];
category.getRange(`D2:D${payload.category.length + 1}`).fillDown();
category.getRange("E2").formulas = [[`=SUMIFS('Transactions'!$AE$2:$AE$${lastTransactionRow},'Transactions'!$O$2:$O$${lastTransactionRow},$A2)`]];
category.getRange(`E2:E${payload.category.length + 1}`).fillDown();
category.getRange("F2").formulas = [[`=SUMIFS('Transactions'!$AF$2:$AF$${lastTransactionRow},'Transactions'!$O$2:$O$${lastTransactionRow},$A2)`]];
category.getRange(`F2:F${payload.category.length + 1}`).fillDown();
category.getRange("G2").formulas = [["=IF(E2=0,0,F2/E2)"]];
category.getRange(`G2:G${payload.category.length + 1}`).fillDown();
category.getRange("H2").formulas = [[`=ROUND(SUMIFS('Transactions'!$U$2:$U$${lastTransactionRow},'Transactions'!$O$2:$O$${lastTransactionRow},$A2),2)`]];
category.getRange(`H2:H${payload.category.length + 1}`).fillDown();
category.getRange(`B2:C${payload.category.length + 1}`).setNumberFormat('"₹"#,##0.00');
category.getRange(`D2:D${payload.category.length + 1}`).setNumberFormat("0.0%");
category.getRange(`E2:F${payload.category.length + 1}`).setNumberFormat("#,##0");
category.getRange(`G2:G${payload.category.length + 1}`).setNumberFormat("0.0%");
category.getRange(`H2:H${payload.category.length + 1}`).setNumberFormat('"₹"#,##0.00');
category.getRange("J1:K1").values = [["Category", "Return Rate"]];
styleHeader(category.getRange("J1:K1"), ORANGE);
category.getRange("J2").formulas = [["=A2"]];
category.getRange(`J2:J${payload.category.length + 1}`).fillDown();
category.getRange("K2").formulas = [["=G2"]];
category.getRange(`K2:K${payload.category.length + 1}`).fillDown();
category.getRange(`K2:K${payload.category.length + 1}`).setNumberFormat("0.0%");

category.getRange("A10:G10").values = [["Channel", "Revenue", "Profit", "Profit Margin", "Orders", "Returned Orders", "Return Rate"]];
styleHeader(category.getRange("A10:G10"), BLUE);
category.getRange(`A11:A${10 + payload.channel.length}`).values = payload.channel.map((row) => [row.channel]);
category.getRange("B11").formulas = [[`=ROUND(SUMIFS('Transactions'!$Y$2:$Y$${lastTransactionRow},'Transactions'!$L$2:$L$${lastTransactionRow},$A11),2)`]];
category.getRange(`B11:B${10 + payload.channel.length}`).fillDown();
category.getRange("C11").formulas = [[`=ROUND(SUMIFS('Transactions'!$AA$2:$AA$${lastTransactionRow},'Transactions'!$L$2:$L$${lastTransactionRow},$A11),2)`]];
category.getRange(`C11:C${10 + payload.channel.length}`).fillDown();
category.getRange("D11").formulas = [["=IF(B11=0,0,C11/B11)"]];
category.getRange(`D11:D${10 + payload.channel.length}`).fillDown();
category.getRange("E11").formulas = [[`=SUMIFS('Transactions'!$AE$2:$AE$${lastTransactionRow},'Transactions'!$L$2:$L$${lastTransactionRow},$A11)`]];
category.getRange(`E11:E${10 + payload.channel.length}`).fillDown();
category.getRange("F11").formulas = [[`=SUMIFS('Transactions'!$AF$2:$AF$${lastTransactionRow},'Transactions'!$L$2:$L$${lastTransactionRow},$A11)`]];
category.getRange(`F11:F${10 + payload.channel.length}`).fillDown();
category.getRange("G11").formulas = [["=IF(E11=0,0,F11/E11)"]];
category.getRange(`G11:G${10 + payload.channel.length}`).fillDown();
category.getRange(`B11:C${10 + payload.channel.length}`).setNumberFormat('"₹"#,##0.00');
category.getRange(`D11:D${10 + payload.channel.length}`).setNumberFormat("0.0%");
category.getRange(`G11:G${10 + payload.channel.length}`).setNumberFormat("0.0%");
category.getRange("A1:K16").format.autofitColumns();
category.getRange("A:A").format.columnWidth = 25;
for (const column of ["B", "C", "H"]) category.getRange(`${column}:${column}`).format.columnWidth = 18;
for (const column of ["D", "E", "F", "G", "K"]) category.getRange(`${column}:${column}`).format.columnWidth = 14;
category.getRange("J:J").format.columnWidth = 25;

// RFM tables
rfm.showGridLines = false;
const rfmColumns = ["customer_id", "customer_name", "customer_segment", "last_order_date", "frequency", "monetary", "profit", "recency_days", "r_score", "f_score", "m_score", "rfm_score", "rfm_segment"];
const rfmHeaders = ["Customer ID", "Customer Name", "Customer Segment", "Last Order Date", "Frequency", "Monetary", "Profit", "Recency Days", "R Score", "F Score", "M Score", "RFM Score", "RFM Segment"];
const rfmRows = payload.rfm.map((row) => Object.fromEntries(rfmHeaders.map((header, index) => [header, row[rfmColumns[index]]])));
writeTable(rfm, 0, 0, rfmHeaders, rfmRows, "CustomerRFMTable");
rfm.getRange(`D2:D${rfmRows.length + 1}`).format.numberFormat = "yyyy-mm-dd";
rfm.getRange(`F2:G${rfmRows.length + 1}`).setNumberFormat('"₹"#,##0.00');
rfm.getRange("O1:Q1").values = [["RFM Segment", "Customers", "Revenue"]];
styleHeader(rfm.getRange("O1:Q1"), OLIVE);
rfm.getRange(`O2:Q${payload.rfm_summary.length + 1}`).values = payload.rfm_summary.map((row) => [row.rfm_segment, row.customers, row.revenue]);
rfm.getRange(`Q2:Q${payload.rfm_summary.length + 1}`).setNumberFormat('"₹"#,##0.00');
rfm.getRange("A1:Q25").format.autofitColumns();
rfm.getRange("B:B").format.columnWidth = 18;
rfm.getRange("C:C").format.columnWidth = 17;
rfm.getRange("M:M").format.columnWidth = 19;
rfm.freezePanes.freezeRows(1);

// Data quality
quality.showGridLines = false;
quality.getRange("A1:H2").merge();
quality.getRange("A1").values = [["DATA QUALITY & RECONCILIATION"]];
quality.getRange("A1:H2").format = { fill: NAVY, font: { name: "Aptos Display", bold: true, color: WHITE, size: 18 }, horizontalAlignment: "left", verticalAlignment: "center" };
quality.getRange("A4:B8").values = [
  ["Dataset", "Synthetic Indian retail transactions"],
  ["Intended grain", "One row per order line"],
  ["Raw rows", 4224],
  ["Validated rows", 4180],
  ["Rejected rows", 44],
];
quality.getRange("A4:A8").format = { fill: "#E8F0FE", font: { bold: true, color: NAVY } };
const qualityHeaders = ["check_id", "check_name", "actual", "expected", "passed", "severity", "status", "checked_at_utc"];
writeTable(quality, 10, 0, qualityHeaders, payload.quality_checks, "DataQualityChecksTable");
quality.getRange(`G12:G${payload.quality_checks.length + 11}`).conditionalFormats.add("containsText", { text: "PASS", format: { fill: "#E8F0FE", font: { bold: true, color: BLUE } } });
quality.getRange(`H12:H${payload.quality_checks.length + 11}`).setNumberFormat("yyyy-mm-dd hh:mm");
quality.getRange("A1:H30").format.autofitColumns();
quality.getRange("B:B").format.columnWidth = 28;
quality.getRange("H:H").format.columnWidth = 18;
quality.freezePanes.freezeRows(11);

// Data dictionary
dictionary.showGridLines = false;
dictionary.getRange("A1:E2").merge();
dictionary.getRange("A1").values = [["DATA DICTIONARY & KPI DEFINITIONS"]];
dictionary.getRange("A1:E2").format = { fill: NAVY, font: { name: "Aptos Display", bold: true, color: WHITE, size: 18 }, verticalAlignment: "center" };
const dictionaryRows = [
  ["fact_sales", "line_id", "Text", "Unique order-line identifier", "Must be unique and not null"],
  ["fact_sales", "order_id", "Text", "Customer order identifier; may repeat for multi-line orders", "Distinct count is the order KPI"],
  ["fact_sales", "date_key", "Integer", "Foreign key to dim_date in YYYYMMDD format", "Required"],
  ["fact_sales", "quantity", "Integer", "Units on the order line", "Greater than zero"],
  ["fact_sales", "gross_sales", "Currency", "Unit price multiplied by quantity", "Before discounts and returns"],
  ["fact_sales", "discount_amount", "Currency", "Gross sales multiplied by discount rate", "Non-negative"],
  ["fact_sales", "return_amount", "Currency", "Refunded sales-after-discount value", "Zero unless returned"],
  ["fact_sales", "revenue", "Currency", "Sales after discount less return amount", "Headline Revenue = SUM(revenue)"],
  ["fact_sales", "cost_amount", "Currency", "Recognized COGS and return-handling cost", "Used in profit"],
  ["fact_sales", "profit", "Currency", "Revenue less cost amount", "Headline Profit = SUM(profit)"],
  ["fact_sales", "order_flag", "0/1", "One on the first line of each order", "SUM gives distinct orders"],
  ["fact_sales", "return_order_flag", "0/1", "One on the first line of each returned order", "SUM gives returned orders"],
  ["dim_customer", "rfm_segment", "Text", "Segment derived from Recency, Frequency and Monetary quintiles", "Seven controlled segments"],
  ["monthly_targets", "target_revenue", "Currency", "Synthetic monthly revenue target", "Used for attainment"],
  ["KPI", "Profit Margin", "Percent", "Total Profit / Total Revenue", "₹41.3M / ₹160.1M = 25.8%"],
  ["KPI", "Return Rate", "Percent", "Returned Orders / Distinct Orders", "345 / 3,922 = 8.8%"],
  ["KPI", "Average Order Value", "Currency", "Total Revenue / Distinct Orders", "Filter-context aware"],
];
dictionary.getRange("A4:E4").values = [["Table", "Field / KPI", "Type", "Definition", "Rule / Formula"]];
styleHeader(dictionary.getRange("A4:E4"));
dictionary.getRange(`A5:E${dictionaryRows.length + 4}`).values = dictionaryRows;
dictionary.getRange(`A5:E${dictionaryRows.length + 4}`).format = { font: { name: "Aptos", size: 10 }, verticalAlignment: "top", wrapText: true };
dictionary.getRange("A:E").format.autofitColumns();
dictionary.getRange("D:D").format.columnWidth = 38;
dictionary.getRange("E:E").format.columnWidth = 34;
dictionary.freezePanes.freezeRows(4);

// Dashboard layout and formulas
dashboard.showGridLines = false;
dashboard.getRange("A1:P2").merge();
dashboard.getRange("A1").values = [["RETAIL SALES & CUSTOMER INSIGHTS"]];
dashboard.getRange("A1:P2").format = { fill: NAVY, font: { name: "Aptos Display", bold: true, color: WHITE, size: 22 }, horizontalAlignment: "left", verticalAlignment: "center" };
dashboard.getRange("A3:P3").merge();
dashboard.getRange("A3").values = [[`${payload.metadata.dataset_type} dataset | ${payload.metadata.date_range} | 4,180 validated order lines | Quality: ${payload.metadata.quality_status}`]];
dashboard.getRange("A3:P3").format = { fill: "#E8F0FE", font: { name: "Aptos", color: MUTED, italic: true, size: 10 }, verticalAlignment: "center" };

const cards = [
  { labelRange: "A5:C5", valueRange: "A6:C8", label: "REVENUE (₹M)", formula: `=ROUND(SUM('Transactions'!$Y$2:$Y$${lastTransactionRow})/1000000,1)`, format: "0.0", color: BLUE },
  { labelRange: "D5:F5", valueRange: "D6:F8", label: "PROFIT (₹M)", formula: `=ROUND(SUM('Transactions'!$AA$2:$AA$${lastTransactionRow})/1000000,1)`, format: "0.0", color: GOLD },
  { labelRange: "G5:I5", valueRange: "G6:I8", label: "PROFIT MARGIN", formula: "=IF(A6=0,0,D6/A6)", format: "0.0%", color: OLIVE },
  { labelRange: "J5:L5", valueRange: "J6:L8", label: "ORDERS", formula: `=SUM('Transactions'!$AE$2:$AE$${lastTransactionRow})`, format: "#,##0", color: PINK },
  { labelRange: "M5:P5", valueRange: "M6:P8", label: "RETURN RATE", formula: `=IF(J6=0,0,SUM('Transactions'!$AF$2:$AF$${lastTransactionRow})/J6)`, format: "0.0%", color: ORANGE },
];
for (const card of cards) {
  dashboard.getRange(card.labelRange).merge();
  dashboard.getRange(card.labelRange.split(":")[0]).values = [[card.label]];
  dashboard.getRange(card.labelRange).format = { fill: card.color, font: { name: "Aptos", bold: true, color: WHITE, size: 10 }, horizontalAlignment: "center", verticalAlignment: "center" };
  dashboard.getRange(card.valueRange).merge();
  const valueCell = dashboard.getRange(card.valueRange.split(":")[0]);
  valueCell.formulas = [[card.formula]];
  dashboard.getRange(card.valueRange).format = { fill: WHITE, font: { name: "Aptos Display", bold: true, color: INK, size: 22 }, horizontalAlignment: "center", verticalAlignment: "center", borders: { preset: "outside", style: "thin", color: GRID } };
  dashboard.getRange(card.valueRange).setNumberFormat(card.format);
}

const monthlyChart = dashboard.charts.add("line", monthly.getRange(`A1:C${payload.monthly.length + 1}`));
monthlyChart.title = "Monthly Revenue and Profit (₹)";
monthlyChart.hasLegend = true;
monthlyChart.xAxis = { axisType: "textAxis", textStyle: { fontSize: 9 } };
monthlyChart.yAxis = { numberFormatCode: "₹0.0,,\"M\"" };
monthlyChart.setPosition("A10", "H26");

const categoryChart = dashboard.charts.add("bar", category.getRange(`A1:B${payload.category.length + 1}`));
categoryChart.title = "Revenue by Product Category (₹)";
categoryChart.hasLegend = false;
categoryChart.yAxis = { numberFormatCode: "₹0.0,,\"M\"" };
categoryChart.setPosition("I10", "P26");

const targetChart = dashboard.charts.add("line", monthly.getRange(`K1:M${payload.monthly.length + 1}`));
targetChart.title = "Monthly Revenue versus Target (₹)";
targetChart.hasLegend = true;
targetChart.xAxis = { axisType: "textAxis", textStyle: { fontSize: 9 } };
targetChart.yAxis = { numberFormatCode: "₹0.0,,\"M\"" };
targetChart.setPosition("A28", "H44");

const rfmChart = dashboard.charts.add("bar", rfm.getRange(`O1:P${payload.rfm_summary.length + 1}`));
rfmChart.title = "Customers by RFM Segment";
rfmChart.hasLegend = false;
rfmChart.setPosition("I28", "P44");

const returnChart = dashboard.charts.add("bar", category.getRange(`J1:K${payload.category.length + 1}`));
returnChart.title = "Order Return Rate by Category";
returnChart.hasLegend = false;
returnChart.yAxis = { numberFormatCode: "0.0%" };
returnChart.setPosition("A46", "H61");

const channelChart = dashboard.charts.add("bar", category.getRange(`A10:B${10 + payload.channel.length}`));
channelChart.title = "Revenue by Sales Channel (₹)";
channelChart.hasLegend = false;
channelChart.yAxis = { numberFormatCode: "₹0.0,,\"M\"" };
channelChart.setPosition("I46", "P61");

dashboard.getRange("A63:P64").merge();
dashboard.getRange("A63").values = [["Definitions: Revenue is net of discounts and returns. Profit = Revenue − recognized cost. Return Rate = returned orders ÷ distinct orders. Replace the Transactions table and extend formula ranges to refresh."]];
dashboard.getRange("A63:P64").format = { fill: PALE, font: { name: "Aptos", size: 9, color: MUTED }, wrapText: true, verticalAlignment: "center", borders: { preset: "outside", style: "thin", color: GRID } };
dashboard.getRange("A:P").format.columnWidth = 11;
dashboard.freezePanes.freezeRows(3);

// Add comments on the KPI cells for auditability.
workbook.comments.addThread({ cell: dashboard.getRange("A6") }, "Revenue = SUM of Transactions[Revenue], net of discounts and return amounts.");
workbook.comments.addThread({ cell: dashboard.getRange("M6") }, "Return Rate = returned orders divided by distinct orders using first-line flags.");

// Compact inspections before export.
const inspect = await workbook.inspect({ kind: "table", range: "Dashboard!A1:P64", include: "values,formulas", tableMaxRows: 12, tableMaxCols: 16, maxChars: 12000 });
console.log(inspect.ndjson);
const errors = await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 200 }, summary: "final formula error scan" });
console.log(errors.ndjson);

const previewRanges = {
  Dashboard: "A1:P64",
  Transactions: "A1:L25",
  "Monthly KPIs": "A1:M25",
  "Category Analysis": "A1:K16",
  "Customer RFM": "A1:Q25",
  "Data Quality": "A1:H28",
  "Data Dictionary": "A1:E22",
};
for (const [sheetName, range] of Object.entries(previewRanges)) {
  const preview = await workbook.render({ sheetName, range, scale: sheetName === "Dashboard" ? 1.25 : 1.0, format: "png" });
  const safeName = sheetName.toLowerCase().replaceAll(" ", "_");
  await fs.writeFile(path.join(previewDir, `${safeName}.png`), new Uint8Array(await preview.arrayBuffer()));
}

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(`Created ${outputPath}`);
