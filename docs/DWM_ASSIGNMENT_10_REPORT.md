# RetailSense — DWM Mini Project / Assignment 10 Report Draft

## 1. Title

**RetailSense – Data Warehousing & Data Mining Analytics Platform**

## 2. Problem Statement

Retail businesses generate large volumes of customer, product and transaction data. Raw data alone does not directly provide actionable information. RetailSense provides an integrated platform for preparing data and applying data mining techniques to discover product relationships, classify customers, predict numerical sales values and segment customers.

## 3. Objectives

- Study and represent a data warehouse structure for retail data.
- Prepare a reusable synthetic retail transaction dataset.
- Apply common data preprocessing techniques.
- Discover association rules using Apriori.
- Perform J48/C4.5-style decision tree classification.
- Perform Naive Bayes classification.
- Predict a numerical target with linear regression.
- Segment customers using K-Means clustering.
- Present the results in an interactive analytics dashboard.

## 4. Technology

Frontend: React, TypeScript, Tailwind CSS, Recharts

Backend: Python, FastAPI, Pandas, NumPy, scikit-learn

Data formats: CSV, XLSX/XLS

## 5. Data Warehouse Architecture

The conceptual star schema consists of a central `Fact_Sales` table connected to `Dim_Customer`, `Dim_Product`, `Dim_Date` and optionally `Dim_Store`.

### Fact_Sales

- TransactionID
- CustomerID
- ProductID
- DateID
- Quantity
- Amount

### Dim_Customer

- CustomerID
- Age
- Gender
- Income
- City

### Dim_Product

- ProductID
- ProductName
- Category

### Dim_Date

- DateID
- Date
- Month
- Quarter
- Year

## 6. Data Preprocessing

RetailSense detects missing values, duplicate records, invalid values, negative quantities/prices and invalid dates. It supports row removal, numerical mean/median imputation, categorical mode imputation, duplicate removal, IQR-based outlier scanning and optional Min-Max normalization.

## 7. Association Rule Mining

Apriori is applied to transaction-item data. The user selects a transaction identifier and item column, then controls minimum support, confidence and lift. The application displays antecedent, consequent, support, confidence and lift.

## 8. Classification

### J48 / C4.5-style

An entropy-based decision tree is used as a practical J48/C4.5-style classifier. Results include accuracy, precision, recall, F1 score, confusion matrix and readable tree rules.

### Naive Bayes

Gaussian Naive Bayes is trained after automatic numerical imputation and categorical one-hot encoding. The same evaluation metrics are reported.

## 9. Regression

Linear Regression predicts a numerical target such as `TotalAmount`. The application reports R², MAE and RMSE and displays actual versus predicted test samples.

## 10. Clustering

K-Means is used for customer segmentation. When `CustomerID` is available, records are aggregated to customer level before clustering. Features are standardized, cluster summaries are displayed and silhouette score is calculated.

## 11. Results

Use screenshots from the live application here. Record the values actually produced for the dataset used during your demonstration. Do not insert made-up metrics.

Suggested screenshots:

1. Dashboard
2. Dataset Management
3. Preprocessing results
4. Apriori rules
5. J48/C4.5-style metrics
6. Naive Bayes metrics
7. Regression chart
8. K-Means scatter plot
9. Insights page
10. DWM architecture page

## 12. Advantages

- One application demonstrates multiple DWM techniques.
- The same dataset flows through the whole pipeline.
- Analytics update after dataset replacement.
- Results are visual and easier to explain in a practical examination.
- Synthetic demo data makes the application immediately runnable.

## 13. Limitations

- Backend stores sessions in memory.
- This is an academic prototype rather than a production retail information system.
- J48 is implemented as an entropy-based C4.5-style decision tree rather than directly embedding WEKA's J48 implementation.

## 14. Future Scope

- Persistent data warehouse in PostgreSQL/MySQL/Supabase.
- Scheduled ETL pipelines.
- Direct WEKA integration through a Java service.
- More advanced forecasting models.
- Role-based access and multi-user dashboards.
- Automated PDF reports and scheduled model refresh.

## 15. Conclusion

RetailSense demonstrates how data warehousing concepts and data mining algorithms can be combined into a single practical retail analytics application. It integrates the learning outcomes of DWM Assignments 1–9 into an interactive Assignment 10 project.
