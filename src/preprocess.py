"""
Pipeline de preprocesamiento — Fase 8.
Ejecutar desde la raíz: python src/preprocess.py

Lee train/test crudos (Fase 7), aprende transformaciones solo en train, guarda artefactos.
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data/processed"

TARGET = "Churn"
ID_COL = "CustomerID"

NULL_COLS = [
    "DaySinceLastOrder",
    "OrderAmountHikeFromlastYear",
    "Tenure",
    "OrderCount",
    "CouponUsed",
    "HourSpendOnApp",
    "WarehouseToHome",
]

CAT_COLS = [
    "PreferredLoginDevice",
    "PreferredPaymentMode",
    "Gender",
    "PreferedOrderCat",
    "MaritalStatus",
]


def add_missing_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in NULL_COLS:
        out[f"{col}_missing"] = out[col].isnull().astype(int)
    return out


def feature_columns(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    drop = {ID_COL, TARGET}
    feature_cols = [c for c in df.columns if c not in drop]
    cat_cols = [c for c in CAT_COLS if c in feature_cols]
    num_cols = [c for c in feature_cols if c not in cat_cols]
    return num_cols, cat_cols


def make_preprocessor(num_cols: list[str], cat_cols: list[str]) -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("num", SimpleImputer(strategy="median"), num_cols),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        (
                            "onehot",
                            OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                        ),
                    ]
                ),
                cat_cols,
            ),
        ],
        verbose_feature_names_out=False,
    )


def extract_xy(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    num_cols, cat_cols = feature_columns(df)
    x = df[num_cols + cat_cols]
    y = df[TARGET]
    return x, y


def load_split_frames() -> tuple[pd.DataFrame, pd.DataFrame]:
    train_path = PROCESSED_DIR / "train.csv"
    test_path = PROCESSED_DIR / "test.csv"
    if not train_path.exists() or not test_path.exists():
        from split import save_splits, stratified_split

        train, test = stratified_split()
        save_splits(train, test)
    return pd.read_csv(train_path), pd.read_csv(test_path)


def fit_and_transform(
    train_df: pd.DataFrame, test_df: pd.DataFrame
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, ColumnTransformer, list[str]]:
    train_df = add_missing_indicators(train_df)
    test_df = add_missing_indicators(test_df)

    x_train, y_train = extract_xy(train_df)
    x_test, y_test = extract_xy(test_df)

    num_cols, cat_cols = feature_columns(train_df)
    preprocessor = make_preprocessor(num_cols, cat_cols)
    x_train_t = preprocessor.fit_transform(x_train)
    x_test_t = preprocessor.transform(x_test)

    feature_names = preprocessor.get_feature_names_out().tolist()
    return x_train_t, x_test_t, y_train.to_numpy(), y_test.to_numpy(), preprocessor, feature_names


def preprocess_summary(
    preprocessor: ColumnTransformer,
    feature_names: list[str],
    x_train: np.ndarray,
    x_test: np.ndarray,
) -> dict:
    num_pipe = preprocessor.named_transformers_["num"]
    cat_pipe = preprocessor.named_transformers_["cat"]
    num_cols = preprocessor.transformers_[0][2]
    cat_cols = preprocessor.transformers_[1][2]

    medians = {
        col: round(float(val), 4)
        for col, val in zip(num_cols, num_pipe.statistics_, strict=True)
    }

    return {
        "numeric_imputation": "median (train only)",
        "categorical_imputation": "most_frequent (train only)",
        "categorical_encoding": "one_hot (handle_unknown=ignore)",
        "missing_indicators": [f"{c}_missing" for c in NULL_COLS],
        "numeric_features_in": num_cols,
        "categorical_features_in": cat_cols,
        "train_medians_learned": medians,
        "categorical_modes_learned": {
            col: cat_pipe.named_steps["imputer"].statistics_[i]
            for i, col in enumerate(cat_cols)
        },
        "output_feature_count": len(feature_names),
        "output_feature_names_sample": feature_names[:10],
        "train_shape": list(x_train.shape),
        "test_shape": list(x_test.shape),
        "train_nulls_after_transform": int(np.isnan(x_train).sum()),
        "test_nulls_after_transform": int(np.isnan(x_test).sum()),
    }


def save_artifacts(
    x_train: np.ndarray,
    x_test: np.ndarray,
    y_train: np.ndarray,
    y_test: np.ndarray,
    preprocessor: ColumnTransformer,
    feature_names: list[str],
) -> dict:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    np.save(PROCESSED_DIR / "X_train.npy", x_train)
    np.save(PROCESSED_DIR / "X_test.npy", x_test)
    np.save(PROCESSED_DIR / "y_train.npy", y_train)
    np.save(PROCESSED_DIR / "y_test.npy", y_test)
    joblib.dump(preprocessor, PROCESSED_DIR / "preprocessor.joblib")

    with (PROCESSED_DIR / "feature_names.json").open("w", encoding="utf-8") as f:
        json.dump(feature_names, f, indent=2)

    manifest = preprocess_summary(preprocessor, feature_names, x_train, x_test)
    manifest_path = PROCESSED_DIR / "preprocess_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    train_df, test_df = load_split_frames()
    x_train, x_test, y_train, y_test, preprocessor, feature_names = fit_and_transform(
        train_df, test_df
    )
    manifest = save_artifacts(
        x_train, x_test, y_train, y_test, preprocessor, feature_names
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
