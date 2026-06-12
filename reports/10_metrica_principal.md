# Métrica principal — Fase 9

**Fecha**: 2026-06-11  
**Script**: `src/metrics.py`  
**Resultados**: `reports/metrics_baseline.json`  
**Decisión registrada**: `decisions.md` #8  
**Estado**: Fase 9 cerrada — **Recall** como métrica guía del TP.

---

## 1. Decisión

| Rol | Métrica |
|-----|---------|
| **Principal (optimizar / comparar modelos)** | **Recall** de la clase 1 (`Churn = 1`) |
| Secundarias (reportar, no elegir ganador) | F1, Precision, ROC-AUC |
| **Descartada como guía** | **Accuracy** |

**Recall** = de todos los clientes que **sí** se fueron, ¿qué proporción detectamos?

\[
\text{Recall} = \frac{TP}{TP + FN}
\]

---

## 2. Por qué no accuracy

En test tenemos **16,87%** de churners (190 de 1.126). Un modelo que predice **siempre "no churn"** obtiene:

| Métrica | Valor |
|---------|------:|
| **Accuracy** | **83,1%** |
| **Recall** | **0%** |
| Churners perdidos | **190 / 190 (100%)** |

Ese baseline parece "bueno" en accuracy pero es **inútil para retención**: no alerta a nadie que se va. El gerente de CRM necesita **encontrar** a los que churnean, no acertar masivamente la clase mayoritaria.

---

## 3. Comparación de baselines (test)

| Estrategia | Accuracy | **Recall** | Precision | F1 | Churners perdidos |
|------------|----------:|-----------:|----------:|---:|------------------:|
| Siempre activo (0) | 83,1% | **0,0%** | — | 0,00 | 100% |
| Azar (~17%) | 71,3% | 19,5% | 17,9% | 0,19 | 80,5% |
| Siempre churn (1) | 16,9% | 100% | 16,9% | 0,29 | 0% |
| **Random Forest** | 89,7% | **86,8%** | 64,5% | 0,74 | **13,2%** |

**Lectura**: el RF gana donde importa — detecta **165 de 190** churners reales. La accuracy alta del modelo es consecuencia, no el objetivo.

### Matriz de confusión — Random Forest (test)

|  | Pred: Activo | Pred: Churn |
|--|-------------:|------------:|
| **Real: Activo** | TN 845 | FP 91 |
| **Real: Churn** | FN **25** | TP **165** |

Costo de negocio implícito: **25 falsos negativos** (clientes que se van sin alerta) vs **91 falsos positivos** (alertas a quienes se quedan). Para retención proactiva, perder un churner suele ser **peor** que contactar de más — por eso priorizamos Recall.

---

## 4. Métricas secundarias (para el reporte ejecutivo)

| Métrica | Para qué sirve | No la usamos para elegir ganador porque… |
|---------|----------------|------------------------------------------|
| **Precision** | ¿De las alertas, cuántas son reales? | Optimizarla sola ignora churners no detectados |
| **F1** | Balance precision–recall | Oculta si fallamos en uno de los dos extremos |
| **ROC-AUC** | Capacidad de ranking global | No refleja el costo asimétrico FN vs FP |
| **Accuracy** | % de aciertos totales | Engaña con clases desbalanceadas |

Reportaremos F1, Precision y ROC-AUC en el informe del 19/06, pero **el criterio de desempate entre árbol y RF es Recall** (Fase 11).

---

## 5. Implicancias operativas

1. **`class_weight="balanced"`** en modelos sklearn — alinea entrenamiento con Recall.
2. **Umbral de decisión**: por defecto 0,5; si en el futuro Precision cae mucho, se puede bajar el umbral para subir Recall (trade-off explícito en defensa).
3. **Baseline mínimo a superar**: Recall > 0% (siempre activo) y claramente > azar (~20%).
4. **Meta aspiracional del RF actual**: Recall ≈ **0,87** en test como referencia.

---

## 6. Criterio de cierre Fase 9

- [x] Métrica principal definida y justificada con negocio
- [x] Baselines calculados (`metrics_baseline.json`)
- [x] Accuracy descartada como guía con ejemplo numérico
- [x] Métricas secundarias documentadas
- [x] Decisión #8 en `decisions.md`

**STATUS Fase 9**: **CERRADA** — próximo paso: **Fase 10** (árbol vs Random Forest → decisión #9).
