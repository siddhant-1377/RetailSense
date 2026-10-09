from __future__ import annotations

import io
import math
import os
import time
import uuid
from collections import Counter
from itertools import combinations
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    root_mean_squared_error,
    precision_score,
    recall_score,
    r2_score,
    silhouette_score,
)
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.cluster import KMeans

APP_TITLE = "RetailSense API"

app = FastAPI(title=APP_TITLE, version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SESSIONS: Dict[str, pd.DataFrame] = {}
MODELS: Dict[str, Dict[str, Any]] = {}

PRODUCTS = [
    ("P001", "Milk", "Dairy", 55),
    ("P002", "Bread", "Bakery", 40),
    ("P003", "Butter", "Dairy", 80),
    ("P004", "Cheese", "Dairy", 140),
    ("P005", "Eggs", "Grocery", 75),
    ("P006", "Rice", "Grocery", 90),
    ("P007", "Dal", "Grocery", 120),
    ("P008", "Flour", "Grocery", 65),
    ("P009", "Cooking Oil", "Grocery", 160),
    ("P010", "Biscuits", "Snacks", 35),
    ("P011", "Chips", "Snacks", 45),
    ("P012", "Chocolate", "Snacks", 60),
    ("P013", "Coke", "Beverages", 55),
    ("P014", "Juice", "Beverages", 90),
    ("P015", "Tea", "Beverages", 130),
    ("P016", "Coffee", "Beverages", 240),
    ("P017", "Shampoo", "Personal Care", 180),
    ("P018", "Soap", "Personal Care", 70),
    ("P019", "Toothpaste", "Personal Care", 120),
    ("P020", "Face Wash", "Personal Care", 220),
    ("P021", "T-Shirt", "Clothing", 550),
    ("P022", "Jeans", "Clothing", 1400),
    ("P023", "Sneakers", "Clothing", 2100),
    ("P024", "Jacket", "Clothing", 2400),
    ("P025", "Phone Case", "Electronics", 350),
    ("P026", "Power Bank", "Electronics", 1200),
    ("P027", "Earbuds", "Electronics", 1800),
    ("P028", "USB Cable", "Electronics", 450),
]
CITIES = ["Pune", "Mumbai", "Nashik", "Nagpur", "Aurangabad", "Kolhapur", "Satara", "Thane"]
PAYMENTS = ["UPI", "Card", "Cash", "Net Banking", "Wallet"]


def generate_demo_data(n: int = 4200, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    customer_count = 850
    customers = []
    for i in range(customer_count):
        age = int(np.clip(rng.normal(34, 12), 18, 70))
        income = float(np.clip(rng.normal(65000 + max(0, age - 30) * 800, 22000), 18000, 220000))
        frequency = int(np.clip(rng.poisson(5 if income > 60000 else 3) + 1, 1, 25))
        if income >= 100000 and frequency >= 8:
            ctype = "Premium"
        elif income >= 45000 or frequency >= 5:
            ctype = "Regular"
        else:
            ctype = "Budget"
        # Add a small amount of realistic label noise so classification is not perfectly separable.
        if rng.random() < 0.08:
            ctype = rng.choice([x for x in ["Premium", "Regular", "Budget"] if x != ctype])
        customers.append({
            "CustomerID": f"C{i+1:04d}",
            "Age": age,
            "Gender": rng.choice(["Male", "Female", "Other"], p=[0.49, 0.49, 0.02]),
            "Income": round(income, 2),
            "City": rng.choice(CITIES),
            "PurchaseFrequency": frequency,
            "CustomerType": ctype,
        })

    product_map = {p[0]: p for p in PRODUCTS}
    rows: List[Dict[str, Any]] = []
    for t in range(1, n + 1):
        c = customers[int(rng.integers(0, customer_count))]
        transaction_id = f"T{t:05d}"
        # Make common association bundles naturally co-occur across transactions.
        bundle_roll = rng.random()
        if bundle_roll < 0.35:
            base_ids = ["P001", "P002", "P003"] if rng.random() < 0.6 else ["P011", "P013"]
        elif bundle_roll < 0.58:
            base_ids = ["P006", "P007"]
        elif bundle_roll < 0.72:
            base_ids = ["P015", "P016"]
        else:
            base_ids = [rng.choice([p[0] for p in PRODUCTS])]
        extra = int(rng.integers(0, 3))
        available = [p[0] for p in PRODUCTS if p[0] not in base_ids]
        ids = base_ids + list(rng.choice(available, size=extra, replace=False))
        if len(ids) > 4:
            ids = ids[:4]
        date = pd.Timestamp("2026-01-01") + pd.Timedelta(days=int(rng.integers(0, 269)))
        payment = rng.choice(PAYMENTS, p=[0.44, 0.28, 0.12, 0.10, 0.06])
        for pid in ids:
            p = product_map[pid]
            unit_price = float(p[3]) * float(np.clip(rng.normal(1.0, 0.05), 0.8, 1.2))
            quantity = int(np.clip(rng.poisson(1.4), 1, 5))
            discount = float(np.clip(rng.normal(0.08 if c["CustomerType"] == "Premium" else 0.05, 0.025), 0, 0.25))
            total = quantity * unit_price * (1 - discount)
            rows.append({
                "TransactionID": transaction_id,
                "CustomerID": c["CustomerID"],
                "Date": date.strftime("%Y-%m-%d"),
                "Age": c["Age"],
                "Gender": c["Gender"],
                "Income": round(c["Income"], 2),
                "City": c["City"],
                "ProductID": p[0],
                "ProductName": p[1],
                "Category": p[2],
                "Quantity": quantity,
                "UnitPrice": round(unit_price, 2),
                "Discount": round(discount, 4),
                "TotalAmount": round(total, 2),
                "PaymentMethod": payment,
                "PurchaseFrequency": c["PurchaseFrequency"],
                "CustomerType": c["CustomerType"],
            })

    df = pd.DataFrame(rows)
    # Introduce a small, controlled amount of data-quality issues for preprocessing demo.
    issue_rng = np.random.default_rng(seed + 1)
    missing_indices = issue_rng.choice(df.index, size=min(45, max(10, len(df)//100)), replace=False)
    for col in ["Income", "Discount", "City"]:
        subset = issue_rng.choice(missing_indices, size=max(3, len(missing_indices)//3), replace=False)
        df.loc[subset, col] = np.nan
    dup_indices = issue_rng.choice(df.index, size=18, replace=False)
    df = pd.concat([df, df.loc[dup_indices]], ignore_index=True)
    return df


SESSIONS["demo"] = generate_demo_data()


def get_df(session_id: str) -> pd.DataFrame:
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Dataset session not found")
    return SESSIONS[session_id].copy()


def json_safe(value: Any) -> Any:
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        if np.isnan(value) or np.isinf(value):
            return None
        return float(value)
    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d")
    if pd.isna(value):
        return None
    return value


def dataframe_preview(df: pd.DataFrame, n: int = 20) -> List[Dict[str, Any]]:
    records = df.head(n).to_dict(orient="records")
    return [{k: json_safe(v) for k, v in r.items()} for r in records]


def profile_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    numeric = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical = [c for c in df.columns if c not in numeric and not pd.api.types.is_datetime64_any_dtype(df[c])]
    date_cols = [c for c in df.columns if "date" in c.lower() or pd.api.types.is_datetime64_any_dtype(df[c])]
    missing = int(df.isna().sum().sum())
    duplicate = int(df.duplicated().sum())
    invalid_numeric = {}
    for col in numeric:
        invalid_numeric[col] = int((~np.isfinite(pd.to_numeric(df[col], errors="coerce").fillna(0))).sum())
    negative_quantity = int((pd.to_numeric(df.get("Quantity", pd.Series(dtype=float)), errors="coerce") < 0).sum()) if "Quantity" in df else 0
    negative_price = int((pd.to_numeric(df.get("UnitPrice", pd.Series(dtype=float)), errors="coerce") < 0).sum()) if "UnitPrice" in df else 0
    invalid_dates = 0
    if date_cols:
        dcol = date_cols[0]
        invalid_dates = int(pd.to_datetime(df[dcol], errors="coerce").isna().sum() - df[dcol].isna().sum())
    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "column_names": df.columns.tolist(),
        "numeric_columns": numeric,
        "categorical_columns": categorical,
        "date_columns": date_cols,
        "missing_values": missing,
        "missing_by_column": {k: int(v) for k, v in df.isna().sum().to_dict().items()},
        "duplicate_records": duplicate,
        "negative_quantities": negative_quantity,
        "negative_prices": negative_price,
        "invalid_dates": max(0, invalid_dates),
        "status": "Dataset Ready for Analysis" if missing == 0 and duplicate == 0 else "Dataset Requires Preprocessing",
        "invalid_numeric": invalid_numeric,
        "preview": dataframe_preview(df, 100),
    }


class PreprocessRequest(BaseModel):
    session_id: str
    missing_method: str = "median"
    remove_duplicates: bool = True
    detect_outliers: bool = True
    normalize_columns: List[str] = Field(default_factory=list)
    encode_categoricals: bool = False


class AssociationRequest(BaseModel):
    session_id: str
    transaction_col: str
    item_col: str
    min_support: float = 0.03
    min_confidence: float = 0.4
    min_lift: float = 1.0
    max_itemset_size: int = 3


class ClassificationRequest(BaseModel):
    session_id: str
    target: str
    features: List[str]
    test_size: float = 0.2
    random_state: int = 42


class RegressionRequest(BaseModel):
    session_id: str
    target: str
    features: List[str]
    test_size: float = 0.2
    random_state: int = 42


class RegressionPredictRequest(BaseModel):
    session_id: str
    target: str
    features: List[str]
    values: Dict[str, Any]


class ClusteringRequest(BaseModel):
    session_id: str
    features: List[str]
    k: int = 3
    random_state: int = 42


def make_transactions(df: pd.DataFrame, transaction_col: str, item_col: str) -> List[set[str]]:
    clean = df[[transaction_col, item_col]].dropna()
    grouped = clean.groupby(transaction_col)[item_col].apply(lambda s: set(map(str, s))).tolist()
    return [x for x in grouped if x]


def apriori(transactions: List[set[str]], min_support: float, max_size: int = 3):
    n = len(transactions)
    if n == 0:
        return [], {}
    support_counts: Dict[frozenset, int] = {}
    item_counts = Counter(item for basket in transactions for item in basket)
    current = {frozenset([item]): count for item, count in item_counts.items() if count / n >= min_support}
    support_counts.update(current)
    size = 2
    while current and size <= max_size:
        prev_keys = sorted(current.keys(), key=lambda x: tuple(sorted(x)))
        candidates = set()
        for i in range(len(prev_keys)):
            for j in range(i + 1, len(prev_keys)):
                union = prev_keys[i] | prev_keys[j]
                if len(union) != size:
                    continue
                # Apriori prune: all subsets must be frequent.
                if all(frozenset(s) in current for s in combinations(union, size - 1)):
                    candidates.add(union)
        next_level = {}
        for cand in candidates:
            count = sum(cand.issubset(basket) for basket in transactions)
            if count / n >= min_support:
                next_level[cand] = count
        support_counts.update(next_level)
        current = next_level
        size += 1
    return list(support_counts.keys()), support_counts


@app.get("/api/health")
def health():
    return {"status": "ok", "service": APP_TITLE}


@app.get("/api/demo")
def demo():
    df = SESSIONS["demo"]
    return {"session_id": "demo", **profile_dataframe(df), "demo": True}


@app.get("/api/summary")
def summary(session_id: str):
    df = get_df(session_id)
    profile = profile_dataframe(df)
    total_customers = int(df["CustomerID"].nunique()) if "CustomerID" in df else 0
    total_transactions = int(df["TransactionID"].nunique()) if "TransactionID" in df else len(df)
    revenue = float(pd.to_numeric(df.get("TotalAmount", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()) if "TotalAmount" in df else 0.0
    avg_value = revenue / total_transactions if total_transactions else 0.0
    charts: Dict[str, Any] = {}
    if "Date" in df and "TotalAmount" in df:
        d = pd.to_datetime(df["Date"], errors="coerce")
        tmp = df.assign(_month=d.dt.to_period("M").astype(str)).groupby("_month", dropna=True)["TotalAmount"].sum().reset_index()
        charts["monthly_sales"] = [{"month": r["_month"], "revenue": round(float(r["TotalAmount"]), 2)} for _, r in tmp.iterrows()]
    if "Category" in df and "TotalAmount" in df:
        tmp = df.groupby("Category", dropna=False)["TotalAmount"].sum().sort_values(ascending=False).reset_index()
        charts["category_sales"] = [{"category": str(r["Category"]), "revenue": round(float(r["TotalAmount"]), 2)} for _, r in tmp.iterrows()]
    if "ProductName" in df and "TotalAmount" in df:
        tmp = df.groupby("ProductName")["TotalAmount"].sum().sort_values(ascending=False).head(10).reset_index()
        charts["top_products"] = [{"product": str(r["ProductName"]), "revenue": round(float(r["TotalAmount"]), 2)} for _, r in tmp.iterrows()]
    for col, key, label in [("CustomerType", "customer_type", "type"), ("PaymentMethod", "payment_method", "method")]:
        if col in df:
            tmp = df[col].fillna("Unknown").value_counts().reset_index()
            tmp.columns = [label, "count"]
            charts[key] = [{label: str(r[label]), "count": int(r["count"])} for _, r in tmp.iterrows()]
    if "City" in df and "TotalAmount" in df:
        tmp = df.groupby("City", dropna=False)["TotalAmount"].sum().sort_values(ascending=False).reset_index()
        charts["city_sales"] = [{"city": "Unknown" if pd.isna(r["City"]) else str(r["City"]), "revenue": round(float(r["TotalAmount"]), 2)} for _, r in tmp.iterrows()]
    return {
        "session_id": session_id,
        "demo": session_id == "demo",
        "metrics": {
            "total_customers": total_customers,
            "total_transactions": total_transactions,
            "total_revenue": round(revenue, 2),
            "avg_transaction_value": round(avg_value, 2),
            "total_products": int(df["ProductID"].nunique()) if "ProductID" in df else int(df["ProductName"].nunique()) if "ProductName" in df else 0,
            "total_records": len(df),
        },
        "charts": charts,
        "profile": profile,
    }


@app.post("/api/upload")
async def upload_dataset(file: UploadFile = File(...)):
    name = (file.filename or "").lower()
    raw = await file.read()
    try:
        if name.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(raw))
        elif name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(raw))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload CSV or XLSX/XLS.")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not read dataset: {exc}") from exc
    if df.empty:
        raise HTTPException(status_code=400, detail="The uploaded dataset is empty.")
    session_id = uuid.uuid4().hex[:12]
    SESSIONS[session_id] = df.copy()
    return {"session_id": session_id, "file_name": file.filename, **profile_dataframe(df), "demo": False}


@app.post("/api/reset")
def reset(session_id: str = "demo"):
    if session_id != "demo":
        # Create a fresh demo copy so later modifications don't affect the canonical demo dataset.
        SESSIONS[session_id] = SESSIONS["demo"].copy()
        MODELS.pop(session_id, None)
        return {"session_id": session_id, **profile_dataframe(SESSIONS[session_id]), "demo": True}
    MODELS.pop("demo", None)
    SESSIONS["demo"] = generate_demo_data()
    return {"session_id": "demo", **profile_dataframe(SESSIONS["demo"]), "demo": True}


@app.post("/api/preprocess")
def preprocess(req: PreprocessRequest):
    df = get_df(req.session_id)
    original_rows = len(df)
    before_missing = int(df.isna().sum().sum())
    before_duplicates = int(df.duplicated().sum())

    outliers = []
    for col in df.select_dtypes(include=[np.number]).columns:
        s = pd.to_numeric(df[col], errors="coerce")
        q1 = s.quantile(0.25)
        q3 = s.quantile(0.75)
        iqr = q3 - q1
        if pd.isna(iqr) or iqr == 0:
            count = 0
        else:
            count = int(((s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)).sum())
        outliers.append({"column": col, "count": count, "min": json_safe(s.min()), "max": json_safe(s.max()), "q1": json_safe(q1), "q3": json_safe(q3)})

    if req.remove_duplicates:
        df = df.drop_duplicates().reset_index(drop=True)

    for col in df.columns:
        if not df[col].isna().any():
            continue
        if req.missing_method == "remove":
            continue
        if pd.api.types.is_numeric_dtype(df[col]):
            if req.missing_method == "mean":
                df[col] = df[col].fillna(df[col].mean())
            else:
                df[col] = df[col].fillna(df[col].median())
        else:
            mode = df[col].mode(dropna=True)
            if len(mode):
                df[col] = df[col].fillna(mode.iloc[0])
    if req.missing_method == "remove":
        df = df.dropna().reset_index(drop=True)

    if req.normalize_columns:
        for col in req.normalize_columns:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                s = df[col].astype(float)
                lo, hi = s.min(), s.max()
                df[col] = 0.0 if hi == lo else (s - lo) / (hi - lo)

    SESSIONS[req.session_id] = df
    after_missing = int(df.isna().sum().sum())
    after_duplicates = int(df.duplicated().sum())
    return {
        "session_id": req.session_id,
        "summary": {
            "original_rows": original_rows,
            "removed_rows": original_rows - len(df),
            "remaining_rows": len(df),
            "missing_values_before": before_missing,
            "missing_values_after": after_missing,
            "duplicate_records_before": before_duplicates,
            "duplicate_records_after": after_duplicates,
            "numeric_columns": len(df.select_dtypes(include=[np.number]).columns),
            "categorical_columns": len(df.select_dtypes(exclude=[np.number]).columns),
        },
        "outliers": outliers,
        "profile": profile_dataframe(df),
        "message": "Preprocessing applied successfully.",
    }


@app.get("/api/download/clean")
def download_clean(session_id: str):
    df = get_df(session_id)
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=retailsense_clean_dataset.csv"})


@app.post("/api/association")
def association(req: AssociationRequest):
    df = get_df(req.session_id)
    if req.transaction_col not in df.columns or req.item_col not in df.columns:
        raise HTTPException(status_code=400, detail="Selected transaction/item columns do not exist.")
    transactions = make_transactions(df, req.transaction_col, req.item_col)
    if not transactions:
        raise HTTPException(status_code=400, detail="No valid transactions were found.")
    itemsets, counts = apriori(transactions, max(0.0001, req.min_support), req.max_itemset_size)
    rules = []
    n = len(transactions)
    for itemset in itemsets:
        if len(itemset) < 2:
            continue
        for r in range(1, len(itemset)):
            for ant_tuple in combinations(sorted(itemset), r):
                antecedent = frozenset(ant_tuple)
                consequent = itemset - antecedent
                support = counts[itemset] / n
                ant_support = counts.get(antecedent, 0) / n
                cons_support = counts.get(consequent, 0) / n
                if ant_support <= 0 or cons_support <= 0:
                    continue
                confidence = support / ant_support
                lift = confidence / cons_support
                if confidence >= req.min_confidence and lift >= req.min_lift:
                    rules.append({
                        "antecedent": ", ".join(sorted(antecedent)),
                        "consequent": ", ".join(sorted(consequent)),
                        "support": round(support, 4),
                        "confidence": round(confidence, 4),
                        "lift": round(lift, 4),
                    })
    rules.sort(key=lambda x: (x["lift"], x["confidence"]), reverse=True)
    top = rules[:100]
    scatter = [{"support": r["support"], "confidence": r["confidence"], "lift": r["lift"], "label": f"{r['antecedent']} → {r['consequent']}"} for r in top]
    return {
        "transaction_count": len(transactions),
        "rules": top,
        "rule_count": len(rules),
        "top_rules": top[:10],
        "scatter": scatter,
        "message": "No rules met the selected thresholds." if not top else "Association rules generated from the current dataset.",
    }


def build_classifier_pipeline(df: pd.DataFrame, features: List[str], categorical_target: bool = True):
    X = df[features].copy()
    for c in X.columns:
        if pd.api.types.is_datetime64_any_dtype(X[c]):
            X[c] = X[c].astype("int64") // 10**9
    y = df[features[0]] if False else None
    numeric = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical = [c for c in X.columns if c not in numeric]
    preprocessor = ColumnTransformer([
        ("num", Pipeline([("imp", SimpleImputer(strategy="median"))]), numeric),
        ("cat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")), ("oh", OneHotEncoder(handle_unknown="ignore"))]), categorical),
    ])
    return X, preprocessor


def prepare_classification(df: pd.DataFrame, target: str, features: List[str]):
    if target not in df.columns:
        raise HTTPException(status_code=400, detail="Target column does not exist.")
    features = [c for c in features if c in df.columns and c != target]
    if not features:
        raise HTTPException(status_code=400, detail="Select at least one feature other than the target.")
    work = df[features + [target]].copy()
    work = work.dropna(subset=[target])
    if work[target].nunique() < 2:
        raise HTTPException(status_code=400, detail="Classification requires at least two target classes.")
    y = work[target].astype(str)
    X = work[features].copy()
    numeric = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical = [c for c in X.columns if c not in numeric]
    pre = ColumnTransformer([
        ("num", Pipeline([("imputer", SimpleImputer(strategy="median"))]), numeric),
        ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical),
    ])
    return X, y, pre, features


def classification_run(df: pd.DataFrame, target: str, features: List[str], algorithm: str, test_size: float, random_state: int):
    X, y, pre, features = prepare_classification(df, target, features)
    try:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)
    except ValueError:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

    if algorithm == "j48":
        model = DecisionTreeClassifier(criterion="entropy", random_state=random_state, max_depth=8, min_samples_leaf=3)
        label = "J48 / C4.5-style Decision Tree"
    else:
        model = Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("model", GaussianNB())])
        # Naive Bayes expects numeric matrix after one-hot encoding; handle sparse -> dense.
        class_counts = y_train.value_counts()
        label = "Naive Bayes"

    if algorithm == "j48":
        X_train_t = pre.fit_transform(X_train)
        X_test_t = pre.transform(X_test)
        try:
            feature_names = pre.get_feature_names_out().tolist()
        except Exception:
            feature_names = features
        model.fit(X_train_t, y_train)
        pred = model.predict(X_test_t)
        tree_rules = export_text(model, feature_names=feature_names, max_depth=5)
    else:
        X_train_t = pre.fit_transform(X_train)
        X_test_t = pre.transform(X_test)
        dense_train = X_train_t.toarray() if hasattr(X_train_t, "toarray") else X_train_t
        dense_test = X_test_t.toarray() if hasattr(X_test_t, "toarray") else X_test_t
        model.fit(dense_train, y_train)
        pred = model.predict(dense_test)
        tree_rules = None

    labels = sorted(set(y_test.astype(str)) | set(pd.Series(pred).astype(str)))
    cm = confusion_matrix(y_test, pred, labels=labels)
    result = {
        "algorithm": algorithm,
        "label": label,
        "target": target,
        "features": features,
        "accuracy": round(float(accuracy_score(y_test, pred)), 4),
        "precision": round(float(precision_score(y_test, pred, average="weighted", zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, pred, average="weighted", zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, pred, average="weighted", zero_division=0)), 4),
        "labels": labels,
        "confusion_matrix": cm.tolist(),
        "tree_rules": tree_rules,
        "test_samples": int(len(y_test)),
    }
    return result, {"pre": pre, "model": model, "algorithm": algorithm}


@app.post("/api/classification")
def classification(req: ClassificationRequest):
    df = get_df(req.session_id)
    j48, j48_art = classification_run(df, req.target, req.features, "j48", req.test_size, req.random_state)
    nb, nb_art = classification_run(df, req.target, req.features, "naive_bayes", req.test_size, req.random_state)
    MODELS.setdefault(req.session_id, {})["classification"] = {"j48": j48_art, "naive_bayes": nb_art}
    return {
        "j48": j48,
        "naive_bayes": nb,
        "comparison": [j48, nb],
    }


def prepare_regression(df: pd.DataFrame, target: str, features: List[str]):
    if target not in df.columns:
        raise HTTPException(status_code=400, detail="Target column does not exist.")
    if not pd.api.types.is_numeric_dtype(df[target]):
        raise HTTPException(status_code=400, detail="Regression target must be numerical.")
    features = [c for c in features if c in df.columns and c != target]
    if not features:
        raise HTTPException(status_code=400, detail="Select at least one predictor feature.")
    work = df[features + [target]].copy()
    work[target] = pd.to_numeric(work[target], errors="coerce")
    work = work.dropna(subset=[target])
    X = work[features].copy()
    y = work[target].astype(float)
    numeric = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical = [c for c in X.columns if c not in numeric]
    pre = ColumnTransformer([
        ("num", Pipeline([("imputer", SimpleImputer(strategy="median"))]), numeric),
        ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical),
    ])
    return X, y, pre, features


@app.post("/api/regression")
def regression(req: RegressionRequest):
    df = get_df(req.session_id)
    X, y, pre, features = prepare_regression(df, req.target, req.features)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=req.test_size, random_state=req.random_state)
    Xt = pre.fit_transform(X_train)
    Xv = pre.transform(X_test)
    model = LinearRegression()
    model.fit(Xt, y_train)
    pred = model.predict(Xv)
    rmse = float(root_mean_squared_error(y_test, pred))
    sample = []
    for actual, p in zip(y_test.iloc[:80].tolist(), pred[:80].tolist()):
        sample.append({"actual": round(float(actual), 2), "predicted": round(float(p), 2)})
    MODELS.setdefault(req.session_id, {})["regression"] = {"pre": pre, "model": model, "target": req.target, "features": features}
    return {
        "target": req.target,
        "features": features,
        "r2": round(float(r2_score(y_test, pred)), 4),
        "mae": round(float(mean_absolute_error(y_test, pred)), 4),
        "rmse": round(float(rmse), 4),
        "samples": sample,
        "coefficients": [round(float(x), 6) for x in np.ravel(model.coef_)[:100]],
        "test_samples": int(len(y_test)),
    }


@app.post("/api/regression/predict")
def regression_predict(req: RegressionPredictRequest):
    df = get_df(req.session_id)
    X, y, pre, features = prepare_regression(df, req.target, req.features)
    model = LinearRegression()
    Xt = pre.fit_transform(X)
    model.fit(Xt, y)
    row = pd.DataFrame([{f: req.values.get(f) for f in features}])
    for f in features:
        if f in row.columns and pd.api.types.is_numeric_dtype(X[f]):
            row[f] = pd.to_numeric(row[f], errors="coerce")
    rt = pre.transform(row)
    pred = float(model.predict(rt)[0])
    return {"prediction": round(pred, 2), "target": req.target, "features": features}


@app.post("/api/clustering")
def clustering(req: ClusteringRequest):
    df = get_df(req.session_id)
    if req.k < 2 or req.k > 8:
        raise HTTPException(status_code=400, detail="K must be between 2 and 8.")
    features = [f for f in req.features if f in df.columns]
    if len(features) < 2:
        raise HTTPException(status_code=400, detail="Select at least two numerical features for clustering.")
    if "CustomerID" in df.columns:
        base_cols = ["CustomerID"] + features
        work = df[base_cols].copy()
        for f in features:
            work[f] = pd.to_numeric(work[f], errors="coerce")
        customer_df = work.groupby("CustomerID", as_index=False)[features].mean()
    else:
        customer_df = df[features].copy()
        for f in features:
            customer_df[f] = pd.to_numeric(customer_df[f], errors="coerce")
    customer_df = customer_df.dropna().reset_index(drop=True)
    if len(customer_df) < req.k + 2:
        raise HTTPException(status_code=400, detail="Not enough valid customer records for the selected K.")
    scaler = StandardScaler()
    X = scaler.fit_transform(customer_df[features])
    model = KMeans(n_clusters=req.k, n_init=10, random_state=req.random_state)
    labels = model.fit_predict(X)
    customer_df["Cluster"] = labels + 1
    sil = silhouette_score(X, labels) if req.k < len(customer_df) else 0.0
    summary_rows = []
    for cluster_id, group in customer_df.groupby("Cluster"):
        row = {"cluster": int(cluster_id), "customers": int(len(group))}
        for f in features:
            row[f"avg_{f}"] = round(float(group[f].mean()), 2)
        summary_rows.append(row)
    # Dynamic descriptions from percentile comparison against all clusters.
    for row in summary_rows:
        cluster = row["cluster"]
        group = customer_df[customer_df["Cluster"] == cluster]
        parts = []
        for f in features[:3]:
            overall = customer_df[f].mean()
            val = group[f].mean()
            if overall == 0 or pd.isna(overall):
                continue
            ratio = val / overall
            direction = "high" if ratio > 1.12 else "low" if ratio < 0.88 else "medium"
            parts.append(f"{direction} {f.replace('_', ' ').lower()}")
        row["description"] = " + ".join(parts) if parts else "Distinct customer profile"
    points = []
    x_feature, y_feature = features[0], features[1]
    for _, r in customer_df.head(500).iterrows():
        points.append({"x": round(float(r[x_feature]), 2), "y": round(float(r[y_feature]), 2), "cluster": int(r["Cluster"])})
    return {
        "features": features,
        "k": req.k,
        "customer_count": len(customer_df),
        "silhouette_score": round(float(sil), 4),
        "summary": summary_rows,
        "points": points,
        "axes": {"x": x_feature, "y": y_feature},
    }




def _choose_association_columns(df: pd.DataFrame):
    transaction_candidates = [
        c for c in ["TransactionID", "InvoiceNo", "OrderID", "Transaction", "CustomerID"]
        if c in df.columns
    ]
    transaction_col = transaction_candidates[0] if transaction_candidates else None
    if transaction_col is None:
        object_cols = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
        if object_cols:
            transaction_col = max(object_cols, key=lambda c: df[c].nunique(dropna=True))

    item_candidates = [
        c for c in ["ProductName", "ProductID", "Item", "ItemName", "Product", "Category"]
        if c in df.columns and c != transaction_col
    ]
    ranked = []
    for c in df.columns:
        if c == transaction_col or pd.api.types.is_numeric_dtype(df[c]):
            continue
        unique_count = int(df[c].nunique(dropna=True))
        if 2 <= unique_count <= 1000:
            ranked.append((c, unique_count))
    item_col = item_candidates[0] if item_candidates else (min(ranked, key=lambda x: x[1])[0] if ranked else None)
    return transaction_col, item_col


def _choose_classification_config(df: pd.DataFrame):
    categorical = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c]) and not pd.api.types.is_datetime64_any_dtype(df[c])]
    valid_targets = [c for c in categorical if 2 <= df[c].nunique(dropna=True) <= 20]
    preferred = ["CustomerType", "Class", "Label", "Target", "Segment", "Gender"]
    target = next((c for c in preferred if c in valid_targets), valid_targets[0] if valid_targets else None)
    numeric = df.select_dtypes(include=[np.number]).columns.tolist()
    preferred_features = ["Age", "Income", "PurchaseFrequency", "TotalAmount", "Quantity"]
    features = [c for c in preferred_features if c in numeric and c != target]
    features += [c for c in numeric if c not in features and c != target]
    return target, features[:5]


def _choose_regression_config(df: pd.DataFrame):
    numeric = df.select_dtypes(include=[np.number]).columns.tolist()
    if not numeric:
        return None, []
    target = "TotalAmount" if "TotalAmount" in numeric else numeric[-1]
    preferred_features = ["Age", "Income", "PurchaseFrequency", "Quantity", "UnitPrice", "Discount"]
    features = [c for c in preferred_features if c in numeric and c != target]
    features += [c for c in numeric if c not in features and c != target]
    return target, features[:5]


def _choose_clustering_config(df: pd.DataFrame):
    numeric = df.select_dtypes(include=[np.number]).columns.tolist()
    preferred = ["Income", "PurchaseFrequency", "TotalAmount", "Quantity"]
    features = [c for c in preferred if c in numeric]
    features += [c for c in numeric if c not in features]
    return features[:4], 3


def _comparison_row(name: str, task: str, metric: str, value: float | None,
                    score: float | None, runtime_ms: float, status: str = "ready",
                    detail: str = ""):
    return {
        "algorithm": name,
        "task": task,
        "metric": metric,
        "value": round(float(value), 4) if value is not None and np.isfinite(value) else None,
        "score": round(float(score), 1) if score is not None and np.isfinite(score) else None,
        "runtime_ms": round(float(runtime_ms), 1),
        "status": status,
        "detail": detail,
    }


@app.post("/api/comparison")
def algorithm_comparison(session_id: str):
    df = get_df(session_id)
    rows = []
    notes = []

    # Apriori
    started = time.perf_counter()
    try:
        transaction_col, item_col = _choose_association_columns(df)
        if not transaction_col or not item_col:
            raise ValueError("Could not automatically identify transaction and item columns.")
        assoc = association(AssociationRequest(
            session_id=session_id,
            transaction_col=transaction_col,
            item_col=item_col,
            min_support=0.03,
            min_confidence=0.4,
            min_lift=1.0,
            max_itemset_size=3,
        ))
        runtime_ms = (time.perf_counter() - started) * 1000
        strongest_lift = max((r["lift"] for r in assoc["rules"]), default=0.0)
        best_conf = max((r["confidence"] for r in assoc["rules"]), default=0.0)
        # Association does not use the same metric as predictive models; score its rule quality on confidence.
        score = min(100.0, best_conf * 100.0) if assoc["rules"] else 0.0
        rows.append(_comparison_row(
            "Apriori", "Association", "Best confidence", best_conf, score, runtime_ms,
            detail=f"{assoc['rule_count']} rules; strongest lift {strongest_lift:.2f}; {transaction_col} → {item_col}"
        ))
        notes.append(f"Apriori used {transaction_col} as transaction and {item_col} as item column.")
    except Exception as exc:
        rows.append(_comparison_row("Apriori", "Association", "Best confidence", None, None, (time.perf_counter()-started)*1000, "unavailable", str(exc)))

    # J48 + Naive Bayes
    target, features = _choose_classification_config(df)
    if target and features:
        started = time.perf_counter()
        try:
            result = classification(ClassificationRequest(session_id=session_id, target=target, features=features))
            runtime_ms = (time.perf_counter() - started) * 1000
            j48 = result["j48"]
            rows.append(_comparison_row("J48 / C4.5-style", "Classification", "Weighted F1", j48["f1"], j48["f1"]*100, runtime_ms, detail=f"Target: {target}"))
            nb = result["naive_bayes"]
            rows.append(_comparison_row("Naive Bayes", "Classification", "Weighted F1", nb["f1"], nb["f1"]*100, runtime_ms, detail=f"Target: {target}"))
            winner = "J48 / C4.5-style" if j48["f1"] >= nb["f1"] else "Naive Bayes"
            notes.append(f"Classification winner by weighted F1: {winner}.")
        except Exception as exc:
            runtime_ms = (time.perf_counter() - started) * 1000
            for name in ["J48 / C4.5-style", "Naive Bayes"]:
                rows.append(_comparison_row(name, "Classification", "Weighted F1", None, None, runtime_ms, "unavailable", str(exc)))
    else:
        detail = "Need a categorical target with at least two classes and at least one usable feature."
        rows.extend([
            _comparison_row("J48 / C4.5-style", "Classification", "Weighted F1", None, None, 0.0, "unavailable", detail),
            _comparison_row("Naive Bayes", "Classification", "Weighted F1", None, None, 0.0, "unavailable", detail),
        ])

    # Linear Regression
    reg_target, reg_features = _choose_regression_config(df)
    if reg_target and reg_features:
        started = time.perf_counter()
        try:
            reg = regression(RegressionRequest(session_id=session_id, target=reg_target, features=reg_features))
            runtime_ms = (time.perf_counter() - started) * 1000
            score = max(0.0, min(100.0, reg["r2"] * 100.0))
            rows.append(_comparison_row("Linear Regression", "Regression", "R²", reg["r2"], score, runtime_ms, detail=f"Target: {reg_target}; MAE {reg['mae']:.2f}; RMSE {reg['rmse']:.2f}"))
            notes.append(f"Regression used {reg_target} as target.")
        except Exception as exc:
            rows.append(_comparison_row("Linear Regression", "Regression", "R²", None, None, (time.perf_counter()-started)*1000, "unavailable", str(exc)))
    else:
        rows.append(_comparison_row("Linear Regression", "Regression", "R²", None, None, 0.0, "unavailable", "Need at least one numerical target and one predictor feature."))

    # K-Means
    cluster_features, k = _choose_clustering_config(df)
    if len(cluster_features) >= 2:
        started = time.perf_counter()
        try:
            cluster = clustering(ClusteringRequest(session_id=session_id, features=cluster_features, k=k))
            runtime_ms = (time.perf_counter() - started) * 1000
            score = max(0.0, min(100.0, (cluster["silhouette_score"] + 1.0) * 50.0))
            rows.append(_comparison_row("K-Means", "Clustering", "Silhouette", cluster["silhouette_score"], score, runtime_ms, detail=f"K={k}; {cluster['customer_count']} customer profiles"))
        except Exception as exc:
            rows.append(_comparison_row("K-Means", "Clustering", "Silhouette", None, None, (time.perf_counter()-started)*1000, "unavailable", str(exc)))
    else:
        rows.append(_comparison_row("K-Means", "Clustering", "Silhouette", None, None, 0.0, "unavailable", "Need at least two numerical features."))

    ready = [r for r in rows if r["status"] == "ready" and r["score"] is not None]
    for row in ready:
        row["rank_within_task"] = 1
    for task in sorted({r["task"] for r in ready}):
        task_rows = [r for r in ready if r["task"] == task]
        task_rows.sort(key=lambda r: r["score"], reverse=True)
        for idx, row in enumerate(task_rows, 1):
            row["rank_within_task"] = idx

    classification_rows = [r for r in ready if r["task"] == "Classification"]
    winner = None
    if classification_rows:
        winner = max(classification_rows, key=lambda r: r["score"])["algorithm"]

    return {
        "session_id": session_id,
        "rows": rows,
        "ready_count": len(ready),
        "algorithm_count": len(rows),
        "classification_winner": winner,
        "notes": notes,
        "methodology": {
            "classification": "Weighted F1; higher is better.",
            "regression": "R²; higher is better; negative values are shown as 0 score for the comparison bar.",
            "clustering": "Silhouette score; higher is better. The bar maps [-1, 1] to a 0–100 display score.",
            "association": "Best rule confidence is used as the display score; lift and rule count remain visible as supporting metrics.",
            "cross_task": "Scores are normalized for visual comparison only; algorithms from different task types should not be treated as interchangeable winners.",
        },
    }

@app.get("/api/insights")
def insights(session_id: str):
    df = get_df(session_id)
    summary_data = summary(session_id)
    metric = summary_data["metrics"]
    insights_list = [
        f"The dataset contains {metric['total_records']:,} records across {metric['total_customers']:,} unique customers.",
        f"Total recorded revenue is ₹{metric['total_revenue']:,.2f}, with an average transaction value of ₹{metric['avg_transaction_value']:,.2f}.",
    ]
    if "ProductName" in df.columns and "TotalAmount" in df.columns:
        p = df.groupby("ProductName")["TotalAmount"].sum().sort_values(ascending=False)
        if len(p):
            insights_list.append(f"{p.index[0]} is the highest-revenue product in the current dataset.")
    if "Category" in df.columns and "TotalAmount" in df.columns:
        c = df.groupby("Category")["TotalAmount"].sum().sort_values(ascending=False)
        if len(c):
            insights_list.append(f"{c.index[0]} is the highest-revenue category in the current dataset.")
    if "CustomerType" in df.columns and "TotalAmount" in df.columns:
        cs = df.groupby("CustomerType")["TotalAmount"].mean().sort_values(ascending=False)
        if len(cs):
            insights_list.append(f"{cs.index[0]} has the highest average transaction amount among customer types.")
    if "Date" in df.columns and "TotalAmount" in df.columns:
        d = pd.to_datetime(df["Date"], errors="coerce")
        monthly = df.assign(_m=d.dt.to_period("M"))["TotalAmount"].groupby(df.assign(_m=d.dt.to_period("M"))["_m"]).sum().dropna()
        if len(monthly) >= 2:
            change = monthly.iloc[-1] - monthly.iloc[-2]
            direction = "increased" if change >= 0 else "decreased"
            insights_list.append(f"Revenue {direction} from the previous recorded month to the latest recorded month.")
    return {"session_id": session_id, "insights": insights_list, "data_quality": profile_dataframe(df)}


@app.get("/api/dwm")
def dwm_concepts():
    return {
        "assignments": [
            {"number": 1, "title": "Data Warehouse & Architecture", "description": "Centralized retail data, fact and dimension concepts, ETL-style flow."},
            {"number": 2, "title": "WEKA Tool", "description": "WEKA experimentation and model-learning workflow."},
            {"number": 3, "title": "Dataset Creation", "description": "Synthetic retail transaction dataset with customer and product attributes."},
            {"number": 4, "title": "Data Preprocessing", "description": "Missing values, duplicates, IQR outliers, encoding and normalization."},
            {"number": 5, "title": "Association Rule Mining", "description": "Apriori-based frequent itemsets and association rules."},
            {"number": 6, "title": "J48 Classification", "description": "Entropy-based decision tree used as a practical J48/C4.5-style classifier."},
            {"number": 7, "title": "Naive Bayes Classification", "description": "Probabilistic classification using Gaussian Naive Bayes after feature preprocessing."},
            {"number": 8, "title": "Regression", "description": "Linear regression for numerical sales/revenue prediction."},
            {"number": 9, "title": "Clustering", "description": "K-Means customer segmentation using scaled behavioral features."},
            {"number": 10, "title": "Integrated DWM Mini Project", "description": "One application bringing the full pipeline together."},
        ],
        "star_schema": {
            "Fact_Sales": ["TransactionID", "CustomerID", "ProductID", "DateID", "Quantity", "Amount"],
            "Dim_Customer": ["CustomerID", "Age", "Gender", "Income", "City"],
            "Dim_Product": ["ProductID", "ProductName", "Category"],
            "Dim_Date": ["DateID", "Date", "Month", "Quarter", "Year"],
            "Dim_Store": ["StoreID", "StoreName", "City"],
        },
        "workflow": ["Data Source", "Data Warehouse", "ETL / Preprocessing", "Clean Data", "Data Mining", "Analytics", "Business Insights"],
    }
