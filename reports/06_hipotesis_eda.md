# Hipótesis del EDA — Fase 5

**Fecha**: 2026-06-11  
**Fuentes**: `notebooks/01_eda.ipynb`, `reports/03_eda_exploratorio.md`  
**Decisión registrada**: `decisions.md` #4  
**Estado**: Fase 5 cerrada — hipótesis principal elegida y rankeadas.

---

## 1. Objetivo

Convertir los hallazgos exploratorios (Fase 3) en **hipótesis testeables** y elegir la **más fuerte** para guiar el modelado, la defensa oral y las acciones de retención.

Formato de cada hipótesis:
- **H₀**: no hay diferencia de churn entre grupos.
- **H₁**: sí hay diferencia (dirección indicada).
- **Evidencia**: datos del EDA (tasa de churn, lift, correlación).

---

## 2. Ranking de hipótesis candidatas

| Rank | Hipótesis (H₁) | Churn si condición | Churn si no | Lift | |corr| | Accionable |
|:----:|----------------|-------------------:|------------:|-----:|------:|:----------:|
| **1** | **Tenure < 6 meses → más churn** | **35,0%** | 5,2% | **6,7×** | **0,35** | ✅ Onboarding |
| 2 | `Complain = 1` → más churn | 31,7% | 10,9% | 2,9× | 0,25 | ✅ Atención post-queja |
| 3 | `Tenure` nulo → más churn | 30,7% | 16,2% | 1,9× | — | ✅ (vía flag Fase 4) |
| 4 | `MaritalStatus = Single` → más churn | 26,7% | ~13%* | 2,0× | — | ⚠️ Segmento |
| 5 | `PreferedOrderCat = Mobile Phone` → más churn | 27,5% | ~14%* | 2,0× | — | ⚠️ Segmento |
| 6 | `SatisfactionScore = 5` → más churn que bajo | 23,8% | 11,5%† | 2,1× | 0,11 | ❌ Contra-intuitiva |
| 7 | `DaySinceLastOrder` bajo (0–7 d) → más churn | 19,2% | 9,4%‡ | 2,0× | 0,16 | ⚠️ Cerca de definición |

\*Promedio ponderado de los otros grupos.  
†Score 1–2.  
‡Bin 8–30 días.

**Criterios de desempate** (además del lift):
1. Magnitud de correlación con `Churn`
2. Significado de negocio claro para el gerente de Retención
3. Robustez (no depender de una definición circular del target)

---

## 3. Hipótesis ganadora — Tenure corto

### Enunciado formal

> **H₁**: Los clientes con **menos de 6 meses** de antigüedad (`Tenure` < 6) tienen una probabilidad de churn **significativamente mayor** que los clientes con 6 o más meses.
>
> **H₀**: No hay diferencia en la tasa de churn entre clientes nuevos (< 6 meses) y el resto.

### Evidencia

| Grupo | Clientes | % churn |
|-------|---------:|--------:|
| `Tenure` 0–5 meses | 1.967 | **35,0%** |
| `Tenure` 6+ meses | 3.399 | **5,2%** |
| `Tenure` nulo | 264 | **30,7%** |

- **Lift**: 6,7× (el más alto de todas las candidatas).
- **Correlación** `Tenure`–`Churn`: **−0,35** (la más fuerte en valor absoluto).
- **Test χ²** (binario < 6 vs ≥ 6): *p* < 0,001 — diferencia estadísticamente significativa en la muestra.

### Lectura de negocio

El churn no está repartido parejo: se concentra en la **etapa temprana** de la relación. Un cliente que sobrevive el primer semestre raramente se va en este snapshot (5,2% churn; en el bin 24+ meses, 0%).

**Acción concreta**: programa de retención en los **primeros 180 días** — onboarding, cashback de bienvenida, check-in a los 30/60/90 días.

### Interacción notable (no es la hipótesis principal, pero refuerza)

| Tenure | Complain | % churn | n |
|--------|:--------:|--------:|--:|
| < 6 meses | Sí | **59,0%** | 626 |
| < 6 meses | No | 23,9% | 1.341 |
| ≥ 6 meses | Sí | 10,1% | 907 |
| ≥ 6 meses | No | 3,5% | 2.492 |

Cliente **nuevo + queja** es el segmento más peligroso (casi 6 de cada 10 se van). El playbook de atención post-queja (hipótesis #2) aplica con máxima urgencia en clientes de tenure corto.

---

## 4. Hipótesis secundarias (para el modelo y la defensa)

### H2 — Quejas (`Complain`)

> **H₁**: Quienes elevaron una queja en el último mes tienen mayor churn.

| Complain | % churn | n |
|:--------:|--------:|--:|
| 0 | 10,9% | 4.026 |
| 1 | 31,7% | 1.604 |

- Lift 2,9×; Cohen *h* ≈ 0,52 (efecto medio-grande).
- Segunda hipótesis más fuerte y la **más accionable** de forma inmediata (llamada / resolución en 48 h).
- Validar leakage en Fase 6.

### H3 — Satisfacción no lineal (`SatisfactionScore`)

> **H₁ original (descartada)**: A menor satisfacción, mayor churn.

**Refutada por el EDA**: score 5 tiene **23,8%** churn vs **11,5%** en score 1. No usar la satisfacción como variable monótona "más bajo = más riesgo". El modelo debe capturar la relación no lineal (árboles lo hacen bien).

### H4 — Inactividad reciente (`DaySinceLastOrder`)

> **H₁ tentativa**: Más días sin pedir → más churn.

**Parcialmente refutada**: quien compró hace 0–7 días tiene **más** churn (19,2%) que quien lleva 8–30 días sin pedir (9,4%). El churn en este dataset **no es solo inactividad** — hay clientes activos que se van. Declararlo en la defensa oral.

---

## 5. Implicancias para el modelado (Fase 6+)

| Decisión | Motivo |
|----------|--------|
| Incluir `Tenure` como feature prioritaria | Hipótesis #1 — mayor poder explicativo |
| Incluir `Complain` con experimento sin ella | Hipótesis #2 + auditoría de leakage |
| No forzar monotonía en `SatisfactionScore` | H3 refutada en forma simple |
| Crear bin o dejar que el árbol corte en ~6 meses | El salto 35% → 5% ocurre en ese umbral |
| Priorizar Recall en clientes tenure < 6 | Es donde está el negocio perdido |

---

## 6. Criterio de cierre Fase 5

- [x] Hipótesis candidatas listadas y rankeadas con evidencia cuantitativa
- [x] Hipótesis principal formalizada (H₀ / H₁)
- [x] Hipótesis refutadas o matizadas documentadas (`SatisfactionScore`, `DaySinceLastOrder`)
- [x] Decisión #4 en `decisions.md`
- [x] Puente a Fase 6 (leakage de `Complain`) y modelado

**STATUS Fase 5**: **CERRADA** — próximo paso: **Fase 6** (veredicto formal de `Complain` y leakage → decisión #5).
