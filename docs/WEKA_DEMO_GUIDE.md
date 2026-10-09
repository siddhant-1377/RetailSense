# WEKA Demonstration Guide

Use WEKA as the academic experimentation tool alongside RetailSense.

## Preprocess

1. Open WEKA Explorer.
2. Go to **Preprocess**.
3. Load `backend/data/retail_transactions.csv`.
4. Inspect attributes and missing values.
5. Apply a filter such as RemoveDuplicates or an appropriate missing-value filter where required.

## J48

1. Go to **Classify**.
2. Select `trees → J48`.
3. Select `CustomerType` as the class attribute.
4. Use a test option such as 10-fold cross-validation.
5. Record accuracy, precision, recall and the confusion matrix.

## Naive Bayes

1. Stay in **Classify**.
2. Select `bayes → NaiveBayes`.
3. Use the same class attribute and evaluation method.
4. Record the metrics.

## Regression

1. Choose a numerical class attribute such as `TotalAmount`.
2. Use the **Classify** tab with a regression learner such as `functions → LinearRegression`.
3. Record R²/correlation-related output and error measures provided by WEKA.

## Clustering

1. Open **Cluster**.
2. Select `SimpleKMeans`.
3. Choose a suitable number of clusters (for example 3).
4. Run clustering and inspect cluster sizes.

## Association Rules

1. Open **Associate**.
2. Use an association-rule learner available in your installed WEKA version, such as `Apriori`.
3. Inspect support/confidence/lift-related results.

## Report usage

Screenshots from these WEKA steps can be inserted into the Assignment 10 report as evidence of the experimentation workflow. RetailSense then demonstrates the integrated application implementation.
