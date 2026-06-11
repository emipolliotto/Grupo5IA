"""
Experimento Fase 6 — modelo con/sin Complain.
Ejecutar desde la raíz del repo: python src/leakage_experiment.py
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/raw/ecommerce.csv"
OUT_PATH = ROOT / "reports/leakage_experiment_results.json"

TARGET = "Churn"
ID_COL = "CustomerID"
LEAKY_COL = "Complain"
NULL_COLS = [
    "DaySinceLastOrder",
    "OrderAmountHikeFromlastYear",
    "Tenure",
    "OrderCount",
    "CouponUsed",
    "HourSpendOnApp",
    "WarehouseToHome",
]
RANDOM_STATE = 42
TEST_SIZE = 0.2


def add_missing_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in NULL_COLS:
        out[f"{col}_missing"] = out[col].isnull().astype(int)
    return out


def build_xy(df: pd.DataFrame, include_complain: bool) -> tuple[pd.DataFrame, pd.Series]:
    drop_cols = [ID_COL, TARGET]
    if not include_complain:
        drop_cols.append(LEAKY_COL)
    x = df.drop(columns=drop_cols)
    y = df[TARGET]
    return x, y


def make_preprocessor(x: pd.DataFrame) -> ColumnTransformer:
    cat_cols = x.select_dtypes(include=["object", "string"]).columns.tolist()
    num_cols = [c for c in x.columns if c not in cat_cols]
    return ColumnTransformer(
        transformers=[
            ("num", SimpleImputer(strategy="median"), num_cols),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                cat_cols,
            ),
        ]
    )


def evaluate_model(name: str, model, x_train, x_test, y_train, y_test) -> dict:
    pipe = Pipeline(steps=[("prep", make_preprocessor(x_train)), ("model", model)])
    pipe.fit(x_train, y_train)
    y_pred = pipe.predict(x_test)
    y_proba = pipe.predict_proba(x_test)[:, 1]

    metrics = {
        "model": name,
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "recall": round(float(recall_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred)), 4),
        "f1": round(float(f1_score(y_test, y_pred)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, y_proba)), 4),
    }

    if isinstance(model, (DecisionTreeClassifier, RandomForestClassifier)):
        feat_names = pipe.named_steps["prep"].get_feature_names_out()
        importances = pipe.named_steps["model"].feature_importances_
        top_idx = importances.argsort()[-5:][::-1]
        metrics["top_features"] = [
            {"feature": feat_names[i], "importance": round(float(importances[i]), 4)}
            for i in top_idx
        ]

    return metrics


def main() -> None:
    df = add_missing_indicators(pd.read_csv(DATA_PATH))
    x_full, y = build_xy(df, include_complain=True)
    x_train, x_test, y_train, y_test = train_test_split(
        x_full,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    x_train_no = x_train.drop(columns=[LEAKY_COL])
    x_test_no = x_test.drop(columns=[LEAKY_COL])

    models = {
        "decision_tree": DecisionTreeClassifier(
            max_depth=6, class_weight="balanced", random_state=RANDOM_STATE
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=200,
            max_depth=8,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
    }

    results = {
        "split": {"train": len(x_train), "test": len(x_test), "test_churn_rate": round(float(y_test.mean()), 4)},
        "with_complain": {},
        "without_complain": {},
    }

    for key, model in models.items():
        results["with_complain"][key] = evaluate_model(
            key, model, x_train, x_test, y_train, y_test
        )
        results["without_complain"][key] = evaluate_model(
            key, model, x_train_no, x_test_no, y_train, y_test
        )

    for key in models:
        w = results["with_complain"][key]
        wo = results["without_complain"][key]
        results[f"delta_{key}"] = {
            "recall_drop": round(wo["recall"] - w["recall"], 4),
            "f1_drop": round(wo["f1"] - w["f1"], 4),
            "roc_auc_drop": round(wo["roc_auc"] - w["roc_auc"], 4),
        }

    OUT_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
