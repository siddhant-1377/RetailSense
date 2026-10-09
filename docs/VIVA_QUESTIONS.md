# RetailSense Viva Questions & Short Answers

## 1. Why did you choose retail data?
Retail has both transaction-level and customer-level patterns, so it is suitable for association rules, classification, regression and clustering.

## 2. Why is preprocessing required?
Raw data can contain missing values, duplicates, outliers and categorical values that are not directly suitable for many models.

## 3. What is support in association rules?
Support is the proportion of transactions containing an itemset.

## 4. What is confidence?
Confidence measures how often the consequent occurs when the antecedent occurs.

## 5. What is lift?
Lift compares the observed rule confidence with the consequent's independent frequency. Lift greater than 1 indicates a positive association.

## 6. What is J48?
J48 is the WEKA name for a C4.5-style decision-tree classifier.

## 7. What does Naive Bayes assume?
It assumes conditional independence of features given the class.

## 8. Why split data into train and test sets?
To evaluate the model on unseen records rather than measuring performance only on training data.

## 9. What does R² mean?
R² indicates how much of the variance in the target is explained by the regression model.

## 10. Why standardize before K-Means?
Distance-based clustering can be dominated by large-scale features, so scaling gives features a comparable influence.

## 11. What is silhouette score?
It compares how close a point is to its own cluster versus other clusters; higher values generally indicate better separation.

## 12. Why use a data warehouse?
A warehouse organizes integrated historical data for analysis and reporting rather than day-to-day transaction processing.

## 13. What is a fact table?
A fact table stores measurable business events, such as quantity and sales amount.

## 14. What is a dimension table?
A dimension table stores descriptive context such as customer, product and date attributes.

## 15. How are your nine assignments connected?
Dataset creation provides the data; preprocessing prepares it; association, classification, regression and clustering mine different patterns; data warehouse concepts organize the data; WEKA provides the academic experimentation workflow; Assignment 10 integrates the results in one application.
