# 5–7 Minute DWM Demonstration Script

## 1. Introduction (30 seconds)

“RetailSense is our Assignment 10 DWM mini project. It integrates the concepts from our nine laboratory assignments into a retail analytics workflow. The system takes a retail transaction dataset, preprocesses it, applies data mining algorithms and presents the results in an interactive dashboard.”

## 2. Dashboard (45 seconds)

Show:
- Customers
- Transactions
- Revenue
- Monthly sales
- Category revenue
- Customer types

Say: “These KPIs and charts are calculated from the active dataset.”

## 3. Dataset Management (45 seconds)

Show:
- Demo dataset indicator
- Rows/columns
- Missing values
- Duplicates
- Dataset preview

Say: “The application supports CSV/XLSX uploads and keeps the active dataset available across modules.”

## 4. Preprocessing (45 seconds)

Show:
- Missing value methods
- Duplicate removal
- IQR outlier scan
- Normalization
- Before/after summary

Say: “Preprocessing improves data quality before mining and modeling.”

## 5. Association Rules (45 seconds)

Choose TransactionID + ProductName.

Run Apriori.

Explain:
- Support
- Confidence
- Lift

Example interpretation: “A high-confidence rule indicates that the consequent appears frequently when the antecedent is present.”

## 6. Classification (1 minute)

Run both:
- J48 / C4.5-style decision tree
- Naive Bayes

Show:
- Accuracy
- Precision
- Recall
- F1
- Confusion matrix

Explain that J48 is the WEKA name associated with C4.5 decision-tree classification.

## 7. Regression (45 seconds)

Select TotalAmount as target and numeric predictors.

Run Linear Regression.

Explain:
- R²
- MAE
- RMSE

Show actual vs predicted and the prediction form.

## 8. Clustering (45 seconds)

Select:
- Income
- PurchaseFrequency
- TotalAmount
- Quantity

Use K=3.

Explain customer segmentation and silhouette score.

## 9. Insights + DWM Mapping (45 seconds)

Show generated insights and the DWM Concepts page.

Close with:

“The key contribution of Assignment 10 is integration: the same data preparation flow feeds several mining techniques and their results are presented together in one application.”


## Algorithm comparison demo

Open **Analytics → Comparison** and click **Run comparison**. Explain that RetailSense executes all five implemented algorithms on the active dataset and reports task-appropriate metrics.

For the classification pair, compare J48 / C4.5-style Decision Tree and Naive Bayes using weighted F1 on the same held-out split. For Linear Regression use R² with MAE/RMSE, for K-Means use silhouette score, and for Apriori use best rule confidence with rule count and lift as supporting measures.

The 0–100 comparison bar is a normalized presentation score only; it is not a claim that an association-rule miner is inherently “better” than a classifier or clustering algorithm.
