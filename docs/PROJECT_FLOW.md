# RetailSense Project Flow

```text
Raw Retail Dataset
      ↓
Data Validation
      ↓
Data Preprocessing
 ┌───────────────┐
 │ Missing values│
 │ Duplicates    │
 │ IQR outliers  │
 │ Encoding      │
 │ Normalization │
 └───────┬───────┘
         ↓
Clean Dataset
         ↓
Data Warehouse-style Organization
         ↓
 ┌────────────┬──────────────┬──────────────┬─────────────┐
 ↓            ↓              ↓              ↓             ↓
Apriori      J48/C4.5      Naive Bayes   Regression   K-Means
 ↓            ↓              ↓              ↓             ↓
Product      Customer       Customer       Sales        Customer
relations    class          class          prediction   segments
 └────────────┴──────────────┴──────────────┴─────────────┘
                      ↓
                 Visualization
                      ↓
                 Key Insights
```
