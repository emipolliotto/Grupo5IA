# Veredicto Complain y leakage — Fase 6

**Fecha**: 2026-06-11  
**Experimento**: `src/leakage_experiment.py`  
**Resultados JSON**: `reports/leakage_experiment_results.json`  
**Decisión registrada**: `decisions.md` #5  
**Estado**: Fase 6 cerrada — experimento A/B ejecutado, veredictos formalizados.

---

## 1. Objetivo

Cerrar la auditoría preliminar de Fase 0 (`04_leakage_preliminar.md`): entrenar modelos **con** y **sin** `Complain` y comparar si la variable infla métricas de forma sospechosa (leakage) o aporta señal real.

---

## 2. Diseño del experimento

| Parámetro | Valor |
|-----------|-------|
| Split | 80/20 estratificado (`random_state=42`) |
| Train / test | 4.504 / 1.126 clientes |
| Churn en test | 16,87% |
| Preprocesamiento | Mediana (numéricas) + moda + one-hot (categóricas); indicadores `*_missing` (Fase 4) |
| Modelos | `DecisionTree` (max_depth=6) y `RandomForest` (200 árboles, max_depth=8) |
| Balanceo de clases | `class_weight="balanced"` |
| Métrica foco | **Recall** de churners (clase 1) |

**Criterio de interpretación** (definido en Fase 0):
- Si las métricas **colapsan** sin `Complain` → la señal es real (el modelo la necesita).
- Si **solo con** `Complain` el modelo brilla y sin ella es inútil → revisar leakage.
- Si la caída es **moderada** y otras features (ej. `Tenure`) dominan → **USAR** con confianza.

---

## 3. Resultados — Random Forest (modelo principal del experimento)

| Métrica | Con `Complain` | Sin `Complain` | Δ (sin − con) |
|---------|---------------:|---------------:|--------------:|
| **Recall** | **0,868** | 0,800 | **−0,068** |
| Precision | 0,645 | 0,606 | −0,039 |
| F1 | 0,740 | 0,689 | −0,051 |
| ROC-AUC | 0,960 | 0,942 | −0,018 |
| Accuracy | 0,897 | 0,878 | −0,019 |

### Top 5 importancias — con `Complain`

| Feature | Importancia |
|---------|------------:|
| `Tenure` | 0,329 |
| **`Complain`** | **0,094** |
| `CashbackAmount` | 0,077 |
| `DaySinceLastOrder` | 0,057 |
| `WarehouseToHome` | 0,039 |

### Top 5 importancias — sin `Complain`

| Feature | Importancia |
|---------|------------:|
| `Tenure` | **0,364** (↑) |
| `CashbackAmount` | 0,082 |
| `DaySinceLastOrder` | 0,065 |
| `WarehouseToHome` | 0,045 |
| `NumberOfAddress` | 0,043 |

**Lectura**: sin `Complain`, el modelo **sigue funcionando bien** (Recall 80%, ROC-AUC 94%). `Tenure` asume más peso. `Complain` aporta ~7 pp de Recall adicional pero **no es el pilar del modelo**.

---

## 4. Resultados — Decision Tree (sanity check)

| Métrica | Con `Complain` | Sin `Complain` | Δ |
|---------|---------------:|---------------:|--:|
| Recall | 0,826 | 0,758 | −0,068 |
| F1 | 0,622 | 0,590 | −0,032 |
| ROC-AUC | 0,889 | 0,862 | −0,027 |

Misma dirección que RF: caída moderada, no colapso.

---

## 5. Veredicto por variable

### `Complain` — **USAR**

| Criterio | Evaluación |
|----------|------------|
| Documentación temporal (último mes) | ✅ Data Dict |
| ¿Métricas colapsan sin ella? | ❌ Recall baja 6,8 pp, sigue en 80% |
| ¿Domina sola el modelo? | ❌ Importancia 9,4%; `Tenure` lidera con 33% |
| ¿Accionable para negocio? | ✅ Playbook post-queja (H2, Fase 5) |
| **Veredicto final** | **USAR** — señal legítima complementaria |

### `DaySinceLastOrder` — **USAR CON TRANSPARENCIA**

Sin experimento adicional (no fue la variable bajo sospecha principal). Se mantiene el veredicto de Fase 0: señal legítima pero **cercana al concepto de inactividad**. Declarar en defensa oral que no es “trampa técnica” pero sí proxy de comportamiento reciente.

### `OrderCount` — **USAR**

Sin señales de leakage. Comportamiento del último mes coherente con el diccionario.

---

## 6. Respuesta a la pregunta de leakage

> ¿`Complain` hace trampa?

**No, según la evidencia del experimento.** Una variable con leakage típicamente haría que el modelo sin ella sea inútil o que `Complain` concentre la importancia. Aquí:
- El modelo sin `Complain` mantiene **Recall 80%** y **ROC-AUC 94%**.
- `Tenure` es siempre la feature #1.
- `Complain` mejora el Recall en ~7 puntos — aporta valor incremental, no artificial.

**Matiz para la defensa**: una queja puede ser tanto **causa** como **síntoma** de insatisfacción previa al churn. Eso no es leakage estadístico; es causalidad ambigua (tema decisión #10).

---

## 7. Implicancias para el modelo final

1. **Incluir `Complain`** en el modelo de producción.
2. Reportar en el ejecutivo el **experimento A/B** como evidencia de robustez.
3. Priorizar acciones en **tenure < 6 + complain = 1** (~59% churn, Fase 5).
4. No depender solo de `Complain` para la narrativa — `Tenure` sigue siendo la historia principal.

---

## 8. Criterio de cierre Fase 6

- [x] Experimento con/sin `Complain` ejecutado y reproducible (`src/leakage_experiment.py`)
- [x] Métricas comparadas (Recall, F1, ROC-AUC)
- [x] Importancias analizadas con y sin `Complain`
- [x] Veredicto formal documentado
- [x] Decisión #5 en `decisions.md`
- [x] Supuesto S7 de Fase 0 cerrado

**STATUS Fase 6**: **CERRADA** — próximo paso: **Fase 7** (split estratificado antes de limpiar → decisión #6).
