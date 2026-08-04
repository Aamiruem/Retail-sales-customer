import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const projectRoot = path.resolve(process.argv[2]);
const stagingPath = path.join(projectRoot, "data", "raw", "retail_sales_source_b_staging.json");
const outputPath = path.join(projectRoot, "data", "raw", "retail_sales_source_b.xlsx");
const previewPath = path.resolve(process.argv[3]);

const rows = JSON.parse(await fs.readFile(stagingPath, "utf8"));
const headers = Object.keys(rows[0]);
const matrix = [headers, ...rows.map((row) => headers.map((header) => row[header] ?? null))];

const workbook = Workbook.create();
const sheet = workbook.worksheets.add("Raw Sales");
sheet.showGridLines = false;
sheet.getRangeByIndexes(0, 0, matrix.length, headers.length).values = matrix;
sheet.getRangeByIndexes(0, 0, 1, headers.length).format = {
  fill: "#1F4E78",
  font: { bold: true, color: "#FFFFFF" },
  rowHeight: 28,
  verticalAlignment: "center",
};
sheet.getRangeByIndexes(1, 16, rows.length, 1).format.numberFormat = "0";
sheet.getRangeByIndexes(1, 17, rows.length, 9).format.numberFormat = "₹#,##0.00";
sheet.getRangeByIndexes(1, 18, rows.length, 1).format.numberFormat = "0.0%";
sheet.getRangeByIndexes(1, 0, rows.length + 1, headers.length).format.font = { name: "Aptos", size: 9 };
sheet.getRangeByIndexes(0, 0, rows.length + 1, headers.length).format.autofitColumns();
for (let col = 0; col < headers.length; col += 1) {
  const range = sheet.getRangeByIndexes(0, col, rows.length + 1, 1);
  if (range.format.columnWidth > 24) range.format.columnWidth = 24;
}
for (const column of ["C", "D", "E", "G", "K", "L"]) {
  sheet.getRange(`${column}:${column}`).format.columnWidth = 16;
}
sheet.getRange("F:F").format.columnWidth = 18;
sheet.freezePanes.freezeRows(1);
const table = sheet.tables.add(sheet.getRangeByIndexes(0, 0, rows.length + 1, headers.length), true, "RawSalesExcelTable");
table.style = "TableStyleMedium2";

const preview = await workbook.render({ sheetName: "Raw Sales", range: "A1:L25", scale: 1.2, format: "png" });
await fs.writeFile(previewPath, new Uint8Array(await preview.arrayBuffer()));
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
await fs.unlink(stagingPath);

console.log(`Created ${outputPath} with ${rows.length} source rows.`);
