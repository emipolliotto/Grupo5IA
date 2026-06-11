"""
Split estratificado train/test — Fase 7.
Ejecutar desde la raíz: python src/split.py

Parte el CSV crudo SIN imputar, encodear ni crear flags de missing.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/raw/ecommerce.csv"
OUT_DIR = ROOT / "data/processed"

TARGET = "Churn"
ID_COL = "CustomerID"
RANDOM_STATE = 42
TEST_SIZE = 0.2


def load_raw() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


def stratified_split(
    df: pd.DataFrame | None = None,
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_STATE,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split estratificado sobre datos crudos (nulos intactos)."""
    if df is None:
        df = load_raw()
    train, test = train_test_split(
        df,
        test_size=test_size,
        random_state=random_state,
        stratify=df[TARGET],
    )
    return train.copy(), test.copy()


def split_summary(train: pd.DataFrame, test: pd.DataFrame) -> dict:
    null_cols = train.columns[train.isnull().any()].tolist()
    return {
        "random_state": RANDOM_STATE,
        "test_size": TEST_SIZE,
        "stratify_column": TARGET,
        "train_rows": len(train),
        "test_rows": len(test),
        "train_churn_rate": round(float(train[TARGET].mean()), 4),
        "test_churn_rate": round(float(test[TARGET].mean()), 4),
        "train_churn_count": int(train[TARGET].sum()),
        "test_churn_count": int(test[TARGET].sum()),
        "columns_with_nulls_in_train": null_cols,
        "train_null_rows": int(train[null_cols].isnull().any(axis=1).sum()) if null_cols else 0,
        "test_null_rows": int(test[null_cols].isnull().any(axis=1).sum()) if null_cols else 0,
    }


def save_splits(train: pd.DataFrame, test: pd.DataFrame, out_dir: Path | None = None) -> dict:
    out = out_dir or OUT_DIR
    out.mkdir(parents=True, exist_ok=True)

    train_path = out / "train.csv"
    test_path = out / "test.csv"
    manifest_path = out / "split_manifest.json"

    train.to_csv(train_path, index=False)
    test.to_csv(test_path, index=False)

    manifest = split_summary(train, test)
    manifest["train_path"] = str(train_path.relative_to(ROOT))
    manifest["test_path"] = str(test_path.relative_to(ROOT))
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return manifest


def main() -> None:
    train, test = stratified_split()
    manifest = save_splits(train, test)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
