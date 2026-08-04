# GitHub Setup

Create an empty repository, then run from this project folder:

```bash
git init
git add .
git commit -m "Build retail sales and customer insights analytics dashboard"
git branch -M main
git remote add origin https://github.com/Aamiruem/Retail-Sales-Customer-Insights-Analytics.git
git push -u origin main
```

Before pushing, review the remote URL and repository name. The included GitHub Actions workflow rebuilds the analytics outputs, runs unit tests and checks the project contract on each push and pull request.

Suggested repository description:

> End-to-end retail analytics project using Python, SQL, SQLite, Excel, Power BI, DAX, Power Query, Matplotlib, Seaborn and Streamlit with RFM segmentation and automated data-quality tests.

