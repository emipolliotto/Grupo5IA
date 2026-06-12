# Preprocesamiento — Fase 8

**Fecha**: 2026-06-11  
**Script**: `src/preprocess.py`  
**Manifest**: `data/processed/preprocess_manifest.json`  
**Decisión registrada**: `decisions.md` #7  
**Estado**: Fase 8 cerrada — pipeline ajustado en train y aplicado a test.

---

## 1. Objetivo

Implementar la estrategia de Fase 4 sobre los splits de Fase 7: **indicadores de missing + imputación + encoding**, aprendiendo parámetros **solo en train** y transformando test sin leakage.

---

## 2. Pipeline (orden fijo)

```
train.csv / test.csv (crudos, con nulos)
        │
        ▼
1. Crear 7 columnas {col}_missing     (antes de imputar)
        │
        ▼
2. Separar X (18 features + 7 flags) e y (Churn)
        │
        ▼
3. Ajustar ColumnTransformer en TRAIN:
   · Numéricas (20 cols): SimpleImputer(strategy="median")
   · Categóricas (5 cols): moda + OneHotEncoder(handle_unknown="ignore")
        │
        ▼
4. transform(train) y transform(test)
        │
        ▼
X_train.npy (4504 × 41), X_test.npy (1126 × 41), preprocessor.joblib
```

`CustomerID` se excluye en todo el pipeline.

---

## 3. Decisiones de transformación

| Tipo | Columnas | Transformación | Ajuste |
|------|----------|----------------|--------|
| Numéricas originales | 13 | Mediana | Solo train |
| Flags missing | 7 | Mediana* | Solo train |
| Categóricas | 5 | Moda → one-hot | Solo train |

\*Las banderas son 0/1; la mediana en train es 0 — no altera los flags, cumple el contrato del imputer.

### Categóricas (one-hot)

| Columna | Moda aprendida en train |
|---------|-------------------------|
| `PreferredLoginDevice` | Mobile Phone |
| `PreferredPaymentMode` | Debit Card |
| `Gender` | Male |
| `PreferedOrderCat` | Laptop & Accessory |
| `MaritalStatus` | Married |

`handle_unknown="ignore"` permite categorías nuevas en test sin romper el pipeline.

### Sin escalado (StandardScaler)

Los modelos previstos son **árbol de decisión** y **Random Forest** — no requieren normalización. Evitamos un paso extra que no aporta para estos algoritmos.

---

## 4. Medianas aprendidas en train (muestra)

| Variable | Mediana |
|----------|--------:|
| `Tenure` | 9,0 |
| `DaySinceLastOrder` | 3,0 |
| `CashbackAmount` | 164,0 |
| `Complain` | 0,0 |
| `SatisfactionScore` | 3,0 |

Listado completo en `data/processed/preprocess_manifest.json`.

---

## 5. Salida del pipeline

| Artefacto | Descripción |
|-----------|-------------|
| `X_train.npy` | Matriz de features train (4504 × **41**) |
| `X_test.npy` | Matriz de features test (1126 × 41) |
| `y_train.npy` / `y_test.npy` | Target |
| `preprocessor.joblib` | Transformer ajustado (reutilizable en inferencia) |
| `feature_names.json` | Nombres de las 41 columnas de salida |
| `preprocess_manifest.json` | Metadatos y medianas |

**Composición de las 41 features**: 20 numéricas (13 + 7 flags) + 21 dummies one-hot.

**Verificación**: 0 nulos en `X_train` y `X_test` después del transform.

---

## 6. Reproducir

```bash
# Requiere train.csv y test.csv (Fase 7)
python src/preprocess.py
```

Si faltan los splits, el script ejecuta `split.py` automáticamente.

---

## 7. Criterio de cierre Fase 8

- [x] Indicadores `*_missing` creados antes de imputar
- [x] Medianas y modas aprendidas **solo en train**
- [x] One-hot para categóricas con unknown ignorado
- [x] Test transformado sin re-ajustar
- [x] Artefactos guardados en `data/processed/`
- [x] Decisión #7 en `decisions.md`

**STATUS Fase 8**: **CERRADA** — próximo paso: **Fase 9** (métrica principal → decisión #8).
