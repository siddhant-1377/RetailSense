# RetailSense — Data Warehousing & Data Mining Analytics Platform

RetailSense is a college DWM (Data Warehousing and Data Mining) Mini Project / Assignment 10 that integrates the concepts studied across Assignments 1–9 into a practical retail analytics application.

## What is included

- React + TypeScript + Tailwind CSS + Recharts frontend
- FastAPI + Pandas + NumPy + scikit-learn backend
- CSV and XLSX/XLS upload
- Synthetic demo dataset with 4,000+ retail transactions
- Dataset profiling and validation
- Missing-value handling, duplicate removal, IQR outlier scan, normalization
- Apriori association rule mining
- J48 / C4.5-style decision tree classification (entropy-based)
- Naive Bayes classification
- Linear regression
- K-Means customer clustering + silhouette score
- Dashboard charts and KPI cards
- One-click Algorithm Comparison for Apriori, J48, Naive Bayes, Linear Regression and K-Means
- Dynamic insights page
- Download current clean dataset
- HTML report export
- DWM assignment mapping and data warehouse star schema explanation
- WEKA academic workflow explanation

> **Important academic note:** Demo data is synthetic. The decision-tree implementation is labeled **J48 / C4.5-style** because the backend uses an entropy-based scikit-learn decision tree rather than the WEKA J48 implementation itself. Metrics shown after running analysis are calculated from the active dataset and held-out test split.

## Project structure

```text
RetailSense/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py
│   ├── data/
│   │   └── retail_transactions.csv
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── api.ts
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── styles.css
│   │   └── types.ts
│   ├── package.json
│   └── vite.config.ts
├── docs/
│   ├── DWM_ASSIGNMENT_10_REPORT.md
│   ├── VIVA_QUESTIONS.md
│   └── PROJECT_FLOW.md
└── README.md
```

## 1. Run the whole project with one command

From the project root:

```bash
npm install
npm run dev
```

`npm install` installs the frontend dependencies and automatically creates `backend/.venv` and installs the Python requirements. `npm run dev` starts both FastAPI and Vite together, so you do **not** need separate backend/frontend terminals.

Open:

`http://127.0.0.1:5173`

API health check:

`http://127.0.0.1:8000/api/health`

On Windows, you can also double-click `start.bat` after the first `npm install`.

The Vite development server proxies `/api` requests to the FastAPI backend, so the frontend does not need a hard-coded backend URL in development.

## 2. Algorithm Comparison

Open **Analytics → Comparison** and click **Run comparison**. The page benchmarks the algorithms used in the project on the active dataset:

- Apriori: best rule confidence, with rule count and strongest lift as supporting measures.
- J48 / C4.5-style vs Naive Bayes: weighted F1 on the same held-out test split.
- Linear Regression: R² with MAE and RMSE shown as supporting error measures.
- K-Means: silhouette score with the selected customer-level feature set.

The normalized 0–100 bars are for visual comparison only. Algorithms from different task types are not interchangeable, so the meaningful head-to-head comparison is J48 vs Naive Bayes for classification, while the other algorithms are evaluated using their own task-appropriate metrics.

## 3. Recommended demo flow

1. Open Dashboard and show the KPIs/charts.
2. Open Dataset Management and show profile, preview and quality checks.
3. Run Data Preprocessing and show before/after metrics + IQR outlier scan.
4. Open Analytics → Association Rules and generate Apriori rules.
5. Open Classification and run both J48/C4.5-style and Naive Bayes.
6. Open Regression and train Linear Regression; use the prediction form.
7. Open Clustering and run K-Means; explain cluster summaries and silhouette score.
8. Open Analytics → Comparison and benchmark all five algorithms in one place.
9. Open Insights & Reports and export the HTML report.
10. Open About / DWM Concepts and explain how Assignments 1–9 map into Assignment 10.

## Dataset format for uploads

The built-in demo uses:

`TransactionID, CustomerID, Date, Age, Gender, Income, City, ProductID, ProductName, Category, Quantity, UnitPrice, Discount, TotalAmount, PaymentMethod, PurchaseFrequency, CustomerType`

The app can also analyze many similarly shaped CSV/XLSX datasets. The association module lets you choose the transaction and item columns; classification lets you choose a categorical target; regression requires a numerical target; clustering requires at least two numerical features.

## Academic mapping

| DWM Assignment | RetailSense implementation |
|---|---|
| 1 | Data warehouse workflow + fact/dimension star schema |
| 2 | WEKA experimentation workflow documentation |
| 3 | Synthetic retail dataset creation |
| 4 | Preprocessing: missing values, duplicates, outliers, encoding, normalization |
| 5 | Apriori association rules |
| 6 | J48 / C4.5-style decision tree |
| 7 | Naive Bayes |
| 8 | Linear regression |
| 9 | K-Means clustering |
| 10 | Integrated web application |

## Limitations

- Sessions are kept in backend memory; restarting the backend resets uploaded datasets.
- The backend is a local academic prototype, not a production deployment.
- J48 is represented by an entropy-based C4.5-style decision tree rather than directly embedding WEKA's Java implementation.
- The report export is HTML so it can be printed/saved as PDF from the browser.
