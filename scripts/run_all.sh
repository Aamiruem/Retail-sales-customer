#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_dir"

python -m src.run_pipeline
python scripts/build_notebook.py
python scripts/execute_notebook.py notebooks/retail_sales_customer_insights_analysis.ipynb
python -m unittest discover -s tests -v
python scripts/verify_project.py

echo "Retail analytics project rebuilt and verified."

