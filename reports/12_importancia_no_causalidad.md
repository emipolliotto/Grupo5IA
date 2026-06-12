# Importancia ≠ causalidad — Fase 11

**Fecha**: 2026-06-11  
**Modelo**: Random Forest (`models/churn_model.joblib`)  
**Importancias**: `reports/model_comparison.json`  
**Decisión registrada**: `decisions.md` #10  
**Estado**: Fase 11 cerrada — límites de interpretación definidos para defensa oral y reporte ejecutivo.

---

## 1. Mensaje central (para el gerente)

> El modelo **rankea** clientes en riesgo y señala **qué variables se asocian** al churn en los datos históricos.  
> **No demuestra** que cambiar una variable **cause** que el cliente se quede.

**Importancia de feature** = cuánto ayuda esa variable a **predecir** en este dataset.  
**Causalidad** = si una **intervención** (ej. “dar más cashback”) **provoca** un cambio en el churn.

Confundir ambas cosas lleva a políticas costosas y equivocadas.

---

## 2. Qué SÍ podemos decir

| Afirmación permitida | Evidencia en el TP |
|---------------------|-------------------|
| “Clientes nuevos (`Tenure` bajo) están **asociados** a más churn” | H1 confirmada: 35% vs 5,2%; importancia #1 en RF (32,9%) |
| “Quienes se quejaron tienen **más probabilidad** de irse” | H2: 31,7% vs 10,9%; importancia #2 (9,4%) |
| “El modelo detecta ~87% de los churners en test” | Recall 86,8% (Fase 10) |
| “Nuevo + queja es el segmento más peligroso” | ~59% churn (Fase 5) — **asociación**, no experimento |
| “Conviene **priorizar** alertas en esos perfiles” | Decisión operativa basada en riesgo predictivo |

---

## 3. Qué NO podemos decir

| Afirmación prohibida | Por qué |
|---------------------|---------|
| “Si alargamos el `Tenure`, el cliente no se va” | `Tenure` es etapa de vida del cliente, no palanca directa |
| “Si eliminamos las quejas, baja el churn” | `Complain` puede ser **síntoma** de mala experiencia ya ocurrida |
| “Subir `SatisfactionScore` reduce churn” | H3 **refutada**: score 5 tiene más churn que score 1 |
| “Dar más `CashbackAmount` retiene clientes” | Churners tienen menos cashback — puede ser **consecuencia** de desenganche |
| “Los solteros churnean **porque** son solteros” | `MaritalStatus_Single` es proxy demográfico, no palanca de política |
| “Cortar cupones reduce churn” | H6 muestra asociación promo–churn; hace falta **experimento** (A/B) |

---

## 4. Casos del modelo — importancia vs causalidad

### `Tenure` (importancia 0,329 — #1)

| Lectura correcta | Lectura incorrecta |
|----------------|-------------------|
| “Los primeros 6 meses son la **ventana crítica** de riesgo” | “Hacer que el cliente cumpla 6 meses **causa** retención” |
| Acción: **programa de onboarding** en etapa temprana | Acción: manipular la variable en el CRM |

El tiempo en la empresa **marca la etapa** del ciclo de vida; no es una perilla que el gerente sube o baja.

### `Complain` (importancia 0,094 — #2)

| Lectura correcta | Lectura incorrecta |
|----------------|-------------------|
| “Una queja es **señal de alerta** para contacto urgente” | “Sin quejas no habría churn” |
| Acción: playbook de **resolución** post-queja | Acción: ocultar el canal de quejas |

Fase 6 validó que no es leakage puro, pero **causa vs efecto** sigue abierto: la mala experiencia puede preceder tanto a la queja como al churn.

### `CashbackAmount` (importancia 0,077 — #3)

Churners promedian **160** vs **181** en activos (H6).  
**Asociación**: menos cashback acompaña al churn.  
**No causal**: puede reflejar menos compras → menos cashback acumulado, no al revés.

### `DaySinceLastOrder` (importancia 0,057 — #4)

H4 **refutó** “más días sin pedir → más churn”. La variable ayuda al modelo pero **no** significa que empujar compras recientes retenga — el churn en este dataset no es solo inactividad.

### `SatisfactionScore` (importancia 0,036 — #7)

Relación **no lineal** (H3 refutada). Alta importancia predictiva **no** revive la narrativa “mejorar NPS salva clientes”.

### `MaritalStatus_Single` (importancia 0,028 — #9)

Segmento de riesgo para **priorizar contactos**, no para campañas “anti-soltero”. Variable demográfica — asociación estadística sin mecanismo causal identificado.

---

## 5. Tipos de confusión (glosario rápido)

| Concepto | En criollo | Ejemplo en el TP |
|----------|------------|------------------|
| **Asociación** | A y B van juntos en los datos | Tenure corto + churn alto |
| **Predicción** | El modelo usa A para acertar B | RF usa `Complain` para Recall |
| **Causalidad** | Cambiar A **provoca** cambio en B | No probado en este TP |
| **Confounder** | Z explica A y B | Cliente nuevo → poca profundidad → poco cashback **y** churn |
| **Reverse causality** | B causa A, no al revés | Churn → deja de comprar → baja `CashbackAmount` |

---

## 6. Cómo lo decimos en la defensa oral (frases modelo)

**Bien:**
- “`Tenure` es el predictor más fuerte: el riesgo se concentra en los primeros meses.”
- “`Complain` nos sirve para **priorizar** atención, no para afirmar que la queja es la única causa.”
- “Recomendamos un programa de retención temprana **basado en el patrón histórico**; validar impacto con un piloto A/B.”

**Mal:**
- “Si mejoramos satisfacción, el churn cae.”
- “El modelo prueba que el cashback funciona.”
- “La importancia 33% de Tenure significa que Tenure **causa** el 33% del churn.”

---

## 7. Recomendaciones honestas para el CRM

| Prioridad | Acción | Tipo de evidencia |
|:---------:|--------|-------------------|
| 1 | Programa 0–180 días para clientes nuevos | Asociación fuerte (H1) + importancia #1 |
| 2 | Escalamiento post-queja (urgente si tenure < 6) | Asociación (H2) + segmento 59% churn |
| 3 | Empujar **segunda compra** en ventana temprana (H5) | Narrativa consultoría — hipótesis, no RCT |
| 4 | Auditar campañas cupón agresivo (H6) | Asociación promo–churn — requiere experimento |
| 5 | **No** usar NPS alto como “cliente seguro” | H3 refutada |

Todas las acciones 1–4 son **apuestas razonables** basadas en asociación y predicción; la **causalidad** requeriría tests controlados fuera del alcance del TP.

---

## 8. Criterio de cierre Fase 11

- [x] Distinción importancia / asociación / causalidad documentada
- [x] Ejemplos con variables reales del RF (top importancias)
- [x] Frases permitidas y prohibidas para defensa oral
- [x] Coherencia con hipótesis H1–H7 y Fase 6 (Complain)
- [x] Decisión #10 en `decisions.md`
- [x] **10/10 decisiones** del índice completadas

**STATUS Fase 11**: **CERRADA** — TP listo para reporte ejecutivo y defensa del **19/06**.
