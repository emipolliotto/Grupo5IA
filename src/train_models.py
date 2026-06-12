"""
Comparación árbol vs Random Forest — Fase 10 (decisión #9).
Ejecutar desde la raíz: python src/train_models.py
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier

from metrics import PRIMARY_METRIC, classification_report, load_processed

ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT / "models"
OUT_PATH = ROOT / "reports/model_comparison.json"
FEATURE_NAMES_PATH = ROOT / "data/processed/feature_names.json"

RANDOM_STATE = 42


def build_models() -> dict[str, object]:
    return {
        "decision_tree": DecisionTreeClassifier(
            max_depth=6,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=200,
            max_depth=8,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
    }


def top_importances(model, feature_names: list[str], k: int = 10) -> list[dict]:
    scores = model.feature_importances_
    idx = scores.argsort()[-k:][::-1]
    return [
        {"feature": feature_names[i], "importance": round(float(scores[i]), 4)}
        for i in idx
    ]


def pick_winner(results: dict[str, dict]) -> str:
    ranking = sorted(
        results.items(),
        key=lambda item: (
            item[1]["recall"],
            item[1]["f1"],
            item[1].get("roc_auc", 0),
        ),
        reverse=True,
    )
    return ranking[0][0]


def main() -> None:
    x_train, x_test, y_train, y_test = load_processed()
    feature_names = json.loads(FEATURE_NAMES_PATH.read_text(encoding="utf-8"))

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    fitted: dict[str, object] = {}
    evals: dict[str, dict] = {}

    for name, model in build_models().items():
        model.fit(x_train, y_train)
        y_pred = model.predict(x_test)
        y_proba = model.predict_proba(x_test)[:, 1]
        report = classification_report(y_test, y_pred, y_proba, name=name)
        report["top_importances"] = top_importances(model, feature_names)
        evals[name] = report
        fitted[name] = model
        joblib.dump(model, MODELS_DIR / f"{name}.joblib")

    winner = pick_winner(evals)
    joblib.dump(fitted[winner], MODELS_DIR / "churn_model.joblib")

    output = {
        "primary_metric": PRIMARY_METRIC,
        "winner": winner,
        "models": evals,
        "winner_margin_recall": round(
            evals[winner]["recall"] - evals["decision_tree" if winner == "random_forest" else "random_forest"]["recall"],
            4,
        ),
    }
    OUT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
