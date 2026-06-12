"""
Métricas de evaluación — Fase 9.
Ejecutar desde la raíz: python src/metrics.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data/processed"
OUT_PATH = ROOT / "reports/metrics_baseline.json"

PRIMARY_METRIC = "recall"
POSITIVE_LABEL = 1  # Churn


def classification_report(y_true: np.ndarray, y_pred: np.ndarray, y_proba=None, name: str = "") -> dict:
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    n_pos = int(fn + tp)
    report = {
        "name": name,
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "recall": round(float(recall_score(y_true, y_pred)), 4),
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_true, y_pred)), 4),
        "confusion": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "churners_missed_pct": round(100 * fn / n_pos, 1) if n_pos else 0.0,
    }
    if y_proba is not None:
        report["roc_auc"] = round(float(roc_auc_score(y_true, y_proba)), 4)
    return report


def load_processed() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    return (
        np.load(PROCESSED_DIR / "X_train.npy"),
        np.load(PROCESSED_DIR / "X_test.npy"),
        np.load(PROCESSED_DIR / "y_train.npy"),
        np.load(PROCESSED_DIR / "y_test.npy"),
    )


def run_baselines() -> dict:
    x_train, x_test, y_train, y_test = load_processed()
    results = []

    results.append(classification_report(y_test, np.zeros_like(y_test), name="siempre_activo"))

    results.append(classification_report(y_test, np.ones_like(y_test), name="siempre_churn"))

    rng = np.random.default_rng(42)
    y_rand = (rng.random(len(y_test)) < y_test.mean()).astype(int)
    results.append(classification_report(y_test, y_rand, name="azar_tasa_base"))

    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    rf.fit(x_train, y_train)
    y_pred = rf.predict(x_test)
    y_proba = rf.predict_proba(x_test)[:, 1]
    results.append(classification_report(y_test, y_pred, y_proba, name="random_forest"))

    return {
        "primary_metric": PRIMARY_METRIC,
        "positive_label": POSITIVE_LABEL,
        "test_size": len(y_test),
        "churn_rate_test": round(float(y_test.mean()), 4),
        "baselines": results,
    }


def main() -> None:
    out = run_baselines()
    OUT_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
