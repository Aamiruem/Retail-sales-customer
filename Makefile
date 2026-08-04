.PHONY: pipeline test app verify notebook

pipeline:
	python -m src.run_pipeline

test:
	python -m unittest discover -s tests -v

app:
	streamlit run streamlit_app/app.py

verify:
	python scripts/verify_project.py

notebook:
	python scripts/build_notebook.py
	python scripts/execute_notebook.py notebooks/retail_sales_customer_insights_analysis.ipynb

