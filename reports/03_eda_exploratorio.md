# EDA exploratorio — Fase 3

**Fecha**: 2026-06-11  
**Notebook**: [`notebooks/01_eda.ipynb`](../notebooks/01_eda.ipynb)  
**Dataset**: `data/raw/ecommerce.csv` (5.630 × 20, sin modificar)  
**Estado**: Fase 3 cerrada — exploración completa, sin limpieza ni modelado.

---

## 1. Objetivo de esta fase

Responder con datos la pregunta de Fase 2: **¿qué patrones en la base explican quién se va?** Solo exploración — el tratamiento de nulos queda en Fase 4 y las hipótesis formales en Fase 5.

---

## 2. Panorama del dataset

| Aspecto | Valor |
|---------|-------|
| Filas | 5.630 clientes |
| Columnas | 20 (1 ID, 1 target, 18 features) |
| Target `Churn` | 948 positivos (**16,84%**) — clase minoritaria |
| Categóricas | 5 (`PreferredLoginDevice`, `PreferredPaymentMode`, `Gender`, `PreferedOrderCat`, `MaritalStatus`) |
| Numéricas (features) | 13 |
| Columnas con nulos | 7 (~4,5–5,5% cada una) |

---

## 3. Valores faltantes

| Columna | Nulos | % |
|---------|------:|--:|
| `DaySinceLastOrder` | 307 | 5,45% |
| `OrderAmountHikeFromlastYear` | 265 | 4,71% |
| `Tenure` | 264 | 4,69% |
| `OrderCount` | 258 | 4,58% |
| `CouponUsed` | 256 | 4,55% |
| `HourSpendOnApp` | 255 | 4,53% |
| `WarehouseToHome` | 251 | 4,46% |

**Lectura**: el % de nulos es similar entre churners y activos (no hay un patrón extremo de MNAR obvio). Aun así, hay que decidir imputación **después del split** (Fase 7–8).

---

## 4. Correlaciones más fuertes con Churn

| Variable | Corr. con Churn | Dirección |
|----------|----------------:|-----------|
| `Tenure` | **−0,35** | Menos meses → más churn |
| `Complain` | **+0,25** | Queja → más churn |
| `DaySinceLastOrder` | −0,16 | Más días sin pedir → menos churn* |
| `CashbackAmount` | −0,15 | Menos cashback → más churn |
| `NumberOfDeviceRegistered` | +0,11 | Más dispositivos → más churn |
| `SatisfactionScore` | +0,11 | Score alto → más churn* |

\*Ver secciones 5 y 6 — la relación no es monótona simple.

---

## 5. Deep dive — variables clave

### Tenure (antigüedad)

| Bin | Clientes | % churn |
|-----|---------:|--------:|
| 0–5 meses | 1.967 | **35,0%** |
| 6–11 meses | 1.321 | 5,8% |
| 12–23 meses | 1.574 | 6,5% |
| 24+ meses | 503 | **0,0%** |

**Lectura**: los clientes **nuevos** concentran el churn. Los veteranos (24+ meses) no churnean en este snapshot. Acción de negocio: programa de onboarding / retención temprana.

### Complain (quejas)

| Queja | Clientes | % churn |
|-------|---------:|--------:|
| No (0) | 4.026 | 10,9% |
| Sí (1) | 1.604 | **31,7%** |

**Lectura**: señal fuerte y accionable (playbook de atención post-queja). Riesgo de leakage documentado en `04_leakage_preliminar.md` — validar en Fase 6.

### SatisfactionScore

| Score | Clientes | % churn |
|-------|---------:|--------:|
| 1 | 1.164 | 11,5% |
| 2 | 586 | 12,6% |
| 3 | 1.698 | 17,2% |
| 4 | 1.074 | 17,1% |
| 5 | 1.108 | **23,8%** |

**Lectura**: **contra-intuitivo** — el score más alto tiene la mayor tasa de churn. Posibles explicaciones a testear en Fase 5:
- Clientes muy exigentes califican alto pero igual se van.
- Confusión en la escala o variable mal interpretada.
- Interacción con otras variables (ej. queja + score alto).

No asumir "baja satisfacción → churn" sin más análisis.

### DaySinceLastOrder

| Días sin pedir | Clientes | % churn |
|----------------|---------:|--------:|
| 0–7 | 4.021 | 19,2% |
| 8–30 | 1.300 | 9,4% |
| 31–90 | 2 | 50,0%* |

\*Muestra insignificante.

**Lectura**: quien compró **recientemente** (0–7 días) tiene más churn que quien lleva 8–30 días sin pedir. Sugiere que "churn" en este dataset **no es solo inactividad** — hay clientes activos que igual se van. Hay que explicitarlo en la defensa oral.

---

## 6. Segmentos categóricos con mayor churn

| Dimensión | Grupo con más churn | Tasa |
|-----------|---------------------|-----:|
| `MaritalStatus` | Single | 26,7% |
| `PreferedOrderCat` | Mobile Phone | 27,5% |
| `PreferredLoginDevice` | Phone | 22,4% |
| `PreferredPaymentMode` | COD | 28,8% |
| `Gender` | Male | 17,7% |

**Lectura**: solteros, compradores de celulares y pago contra entrega (COD) son segmentos de riesgo. Útil para campañas, pero el modelo debería capturar esto con features, no solo reglas manuales.

---

## 7. Calidad de datos — alertas para fases siguientes

1. **No eliminar filas con nulos** sin analizar — son ~5% por columna, no masivo.
2. **No usar `CustomerID`** en modelado.
3. **`SatisfactionScore`** no tiene relación lineal simple con churn — no forzar monotonía.
4. **`Tenure` 24+ con 0% churn** — verificar si es señal real o artefacto del snapshot.
5. **Accuracy baseline** = 83,2% prediciendo siempre "no churn" — cualquier métrica debe superar eso en **Recall** de churners.

---

## 8. Criterio de cierre Fase 3

- [x] Notebook `01_eda.ipynb` con carga, target, nulos, numéricas, categóricas, correlaciones y deep dives
- [x] Hallazgos documentados en este reporte
- [x] Sin limpieza ni split (eso es Fase 4+)
- [x] Input listo para hipótesis (Fase 5) y tratamiento de nulos (Fase 4)

**STATUS Fase 3**: **CERRADA** — próximo paso: **Fase 4** (tratamiento de nulos por columna → decisión #3 en `decisions.md`).
