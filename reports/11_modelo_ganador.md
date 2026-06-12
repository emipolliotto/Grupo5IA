# Modelo ganador — Fase 10

**Fecha**: 2026-06-11  
**Script**: `src/train_models.py`  
**Resultados**: `reports/model_comparison.json`  
**Decisión registrada**: `decisions.md` #9  
**Estado**: Fase 10 cerrada — **Random Forest** seleccionado como modelo final.

---

## 1. Objetivo

Entrenar y comparar **árbol de decisión** vs **Random Forest** sobre los datos preprocesados (Fase 8), eligiendo el ganador por **Recall** (Fase 9).

---

## 2. Configuración

| Parámetro | Valor |
|-----------|-------|
| Datos | `X_train.npy` (4.504) / `X_test.npy` (1.126) |
| Métrica de selección | **Recall** (desempate: F1 → ROC-AUC) |
| Árbol | `max_depth=6`, `class_weight="balanced"` |
| Random Forest | `n_estimators=200`, `max_depth=8`, `class_weight="balanced"` |
| `random_state` | 42 |

---

## 3. Resultados en test

| Modelo | **Recall** | Precision | F1 | ROC-AUC | Accuracy | Churners perdidos |
|--------|----------:|----------:|---:|--------:|---------:|------------------:|
| Árbol de decisión | 82,6% | 49,8% | 0,62 | 0,889 | 83,0% | 17,4% (33/190) |
| **Random Forest** | **86,8%** | **64,5%** | **0,74** | **0,960** | **89,7%** | **13,2% (25/190)** |

**Ganador: Random Forest** — +4,2 pp de Recall vs el árbol.

### Matriz de confusión — Random Forest

|  | Pred: Activo | Pred: Churn |
|--|-------------:|------------:|
| **Real: Activo** | 845 | 91 |
| **Real: Churn** | 25 | **165** |

---

## 4. Por qué gana el Random Forest

1. **Recall superior** — detecta 8 churners más que el árbol (165 vs 157).
2. **Mejor Precision** — menos falsas alarmas (91 vs 158 FP).
3. **ROC-AUC 0,96** — mejor ranking global de riesgo.
4. **Misma interpretabilidad de importancias** — ambos exponen `feature_importances_`.

El árbol es más simple y rápido, pero pierde en todas las métricas relevantes para retención.

---

## 5. Top drivers — Random Forest

| Rank | Feature | Importancia |
|:----:|---------|------------:|
| 1 | `Tenure` | 0,329 |
| 2 | `Complain` | 0,094 |
| 3 | `CashbackAmount` | 0,077 |
| 4 | `DaySinceLastOrder` | 0,057 |
| 5 | `WarehouseToHome` | 0,039 |
| 6 | `MaritalStatus_Single` | 0,028 |

**Coherente con hipótesis H1 (tenure corto)** y H2 (quejas). El modelo aprendió la narrativa del EDA.

---

## 6. Artefactos guardados

| Archivo | Descripción |
|---------|-------------|
| `models/random_forest.joblib` | RF entrenado |
| `models/decision_tree.joblib` | Árbol entrenado |
| `models/churn_model.joblib` | **Modelo de producción** (= ganador) |

---

## 7. Criterio de cierre Fase 10

- [x] Dos modelos entrenados con el mismo pipeline de features
- [x] Comparación por Recall (+ secundarias)
- [x] Ganador documentado con importancias
- [x] Modelo final serializado
- [x] Decisión #9 en `decisions.md`

**STATUS Fase 10**: **CERRADA** — ver Fase 11 en `reports/12_importancia_no_causalidad.md`.
