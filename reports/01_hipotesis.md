# Hipótesis de negocio — Fase 5

**TP Churn E-commerce** · Dataset: `data/raw/ecommerce.csv` (5.630 clientes)  
**Fecha**: 2026-06-11  
**Notebook**: `[notebooks/01_eda.ipynb](../notebooks/01_eda.ipynb)` §9–10  
**Decisión registrada**: `decisions.md` #4 y #4b

---

## Cómo leer este documento

Cada hipótesis sigue el formato de la consigna:

1. **H₀ / H₁** en lenguaje de negocio
2. **Gráfico** en el notebook (sección indicada)
3. **Test estadístico** (χ² de independencia para variables categóricas/binarias; Mann-Whitney U para medias continuas)
4. **Interpretación** para el gerente de Retención — sin tecnicismos

**Tasa base de churn**: 16,8% (948 de 5.630 clientes).

---

## H1 — Clientes nuevos churnean más

> **H₀**: No hay diferencia de churn entre clientes con menos de 6 meses y el resto.  
> **H₁**: Los clientes con `Tenure` < 6 meses tienen mayor probabilidad de churn.


| Grupo            | Clientes | % churn   | Lift vs resto |
| ---------------- | -------- | --------- | ------------- |
| Tenure 0–5 meses | 1.967    | **35,0%** | 6,7×          |
| Tenure ≥ 6 meses | 3.399    | **5,2%**  | —             |


- **Gráfico**: notebook §7 — barplot `Tenure_bin` vs churn.  
- **Test**: χ² (binario < 6 vs ≥ 6) → *p* < 0,001.  
- **Interpretación**: El churn no está repartido parejo: se concentra en los **primeros 180 días**. Un cliente que sobrevive el semestre raramente se va (5,2%). La acción no es genérica — es un **programa de onboarding y retención temprana** (check-in 30/60/90 días).

**Veredicto**: ✅ **Confirmada** — hipótesis principal del TP.

---

## H2 — Las quejas predicen churn

> **H₀**: No hay diferencia de churn entre quienes se quejaron y quienes no.  
> **H₁**: Los clientes con `Complain = 1` (queja en el último mes) tienen mayor churn.


| Complain | Clientes | % churn   | Lift |
| -------- | -------- | --------- | ---- |
| No (0)   | 4.026    | 10,9%     | —    |
| Sí (1)   | 1.604    | **31,7%** | 2,9× |


- **Gráfico**: notebook §7 — barplot `Complain` vs churn.  
- **Test**: χ² → *p* < 0,001.  
- **Interpretación**: Una queja no es un reclamo aislado — es señal de que el cliente está evaluando irse. Playbook: resolución prioritaria en 48 h. **Interacción crítica**: tenure < 6 + queja = **58,9%** churn (626 clientes) — casi 6 de cada 10.

**Veredicto**: ✅ **Confirmada** — hipótesis secundaria #1 (accionabilidad inmediata).

---

## H3 — Baja satisfacción implica más churn

> **H₀**: No hay diferencia de churn entre clientes con satisfacción baja y alta.  
> **H₁**: A menor `SatisfactionScore`, mayor churn.


| Grupo            | Clientes | % churn   |
| ---------------- | -------- | --------- |
| Score 1–2 (bajo) | 1.750    | **11,9%** |
| Score 4–5 (alto) | 2.182    | **20,5%** |


Detalle por score entre clientes nuevos (`Tenure` < 6):


| Score | % churn (tenure < 6) |
| ----- | -------------------- |
| 1     | 25,1%                |
| 3     | 35,7%                |
| 5     | **45,5%**            |


- **Gráfico**: notebook §7 y §9.1 — barplot `SatisfactionScore`; heatmap Tenure × Satisfacción.  
- **Test**: χ² (score ≤ 2 vs ≥ 4) → *p* < 0,001 (diferencia en dirección **opuesta** a H₁).  
- **Interpretación**: **Refutada en forma simple.** Un score alto no significa lealtad — puede reflejar satisfacción con la **última compra** (encuesta post-pedido) mientras el cliente aún no construyó hábito. No usar satisfacción como regla “más bajo = más riesgo”; el modelo debe capturar la relación no lineal.

**Veredicto**: ❌ **Refutada** (dirección invertida).

---

## H4 — Más días sin comprar implica más churn

> **H₀**: No hay diferencia de churn entre quienes compraron hace poco y quienes llevan más tiempo sin pedir.  
> **H₁**: A mayor `DaySinceLastOrder`, mayor churn.


| Días sin pedir | Clientes | % churn   |
| -------------- | -------- | --------- |
| 0–7 días       | 4.021    | **19,2%** |
| 8–30 días      | 1.300    | **9,4%**  |


Cruce con antigüedad:


| Perfil                    | % churn   | n     |
| ------------------------- | --------- | ----- |
| Tenure < 6 + compra 0–7 d | **36,0%** | 1.602 |
| Tenure ≥ 6 + compra 0–7 d | 5,4%      | 2.162 |


- **Gráfico**: notebook §7 y §9.2 — barplot `Days_bin`; cruce Tenure × recencia.  
- **Test**: χ² (0–7 d vs 8–30 d) → *p* < 0,001 (dirección opuesta a H₁).  
- **Interpretación**: **Refutada.** En este dataset, churn ≠ inactividad. Hay clientes que **compraron recientemente y aun así se van** — sobre todo si son nuevos. Declarar en defensa oral: la definición de churn no es solo “dejó de comprar hace mucho”.

**Veredicto**: ❌ **Refutada**.

---

## H5 — “Happy churner”: compra reciente, satisfecho, sin queja, pero se va

> **H₀**: No hay diferencia de churn entre clientes nuevos con buena experiencia reciente y clientes veteranos con buena experiencia.  
> **H₁**: Clientes con `Tenure` < 6, `SatisfactionScore` ≥ 4, compra en los últimos 7 días y sin queja tienen churn elevado — patrón de **primera compra OK sin segunda compra**.


| Segmento                                  | Clientes | % churn   |
| ----------------------------------------- | -------- | --------- |
| **Happy churner** (H5)                    | 448      | **33,9%** |
| Control: tenure ≥ 6 + sat ≥ 4 + sin queja | 965      | **2,7%**  |
| Base global                               | 5.630    | 16,8%     |


- **Gráfico**: notebook §9.3 — barplot comparativo de los tres grupos.  
- **Test**: χ² (H5 vs control) → *p* < 0,001.  
- **Interpretación**: ✅ **Confirmada.** No son insatisfechos clásicos: compraron, calificaron bien, no se quejaron — y aun así churnean a 12× la tasa del cliente veterano satisfecho. El problema está en la **segunda compra**, no en salvar la primera. Acción: incentivo de recompra a los 14–30 días post-primer pedido, no solo encuesta de NPS.

**Veredicto**: ✅ **Confirmada** — narrativa de consultoría (decisión #4b).

---

## H6 — Captación promocional sin retención

> **H₀**: No hay diferencia de churn entre clientes nuevos con perfil promocional y otros clientes nuevos.  
> **H₁**: Clientes con `Tenure` < 6, cupones por encima de la mediana y cashback por debajo de la mediana churnean más — perfil de **captación por promo sin lealtad construida**.


| Segmento                                   | Clientes       | % churn   |
| ------------------------------------------ | -------------- | --------- |
| Promo capture (cupón alto + cashback bajo) | 412            | **41,3%** |
| Otros clientes nuevos                      | 1.555          | 33,4%     |
| Cashback medio — activos vs churners       | 180,6 vs 160,4 | —         |


- **Gráfico**: notebook §9.4 — barplot segmento promo vs otros nuevos; boxplot `CashbackAmount` por churn.  
- **Test**: χ² (H6 vs otros nuevos) → *p* < 0,01; Mann-Whitney U (`CashbackAmount` activo > churn) → *p* < 0,001.  
- **Interpretación**: ✅ **Confirmada con matices.** Los promocionales nuevos churnean **8 pp más** que otros nuevos (41% vs 33%). Además, los churners tienen **menos cashback acumulado** (−20 en promedio) — no son clientes “premium que se van felices”, sino compradores con poca profundidad de relación. Acción: revisar calidad de adquisición de campañas con cupón agresivo.

**Veredicto**: ✅ **Confirmada**.

---

## H7 (exploratoria) — Multidispositivo entre clientes nuevos

> **H₁**: Más `NumberOfDeviceRegistered` se asocia a más churn **solo** en tenure < 6.


| Dispositivos | Churn si tenure < 6 | Churn si tenure ≥ 6 |
| ------------ | ------------------- | ------------------- |
| 1            | 20,0%               | 2,9%                |
| 4            | **35,6%**           | 5,0%                |


- **Gráfico**: notebook §9.5 — barplot dispositivos × tenure binario.  
- **Interpretación**: Entre clientes nuevos, 4 dispositivos = 35,6% churn vs 20% con 1 dispositivo. Entre veteranos, el efecto casi desaparece. Lectura de consultoría: multidispositivo en clientes nuevos sugiere **exploración o prueba**, no hábito consolidado. No implica causalidad.

**Veredicto**: ✅ Patrón consistente — apoya la narrativa H5/H6.

---

## Resumen ejecutivo para el gerente


| #   | Hipótesis                    | Resultado | Acción                                      |
| --- | ---------------------------- | --------- | ------------------------------------------- |
| H1  | Clientes nuevos churnean más | ✅         | Programa 0–180 días                         |
| H2  | Quejas predicen churn        | ✅         | Playbook post-queja (urgente si tenure < 6) |
| H3  | Baja satisfacción → churn    | ❌         | No usar NPS como regla simple               |
| H4  | Inactividad → churn          | ❌         | Churn ≠ “hace mucho que no compra”          |
| H5  | Happy churner                | ✅         | Incentivar **segunda compra**               |
| H6  | Promo sin retención          | ✅         | Auditar campañas de cupón                   |


**Historia en una frase**: *El negocio convierte bien la primera compra en clientes nuevos, pero falla en convertirla en hábito — y una buena nota de satisfacción no garantiza que vuelvan.*

---

## Próximos pasos (modelado)

- Priorizar `Tenure`, `Complain`, interacciones tenure × queja en el árbol de decisión.
- No forzar monotonía en `SatisfactionScore` ni `DaySinceLastOrder`.
- Incluir flags `*_missing` (Fase 4) — especialmente `Tenure` y `WarehouseToHome`.
- Métrica principal: **Recall** de churners (Fase 9).

