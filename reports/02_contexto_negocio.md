# Contexto de negocio — Fase 2

**Fecha**: 2026-06-11  
**Dataset**: `data/raw/ecommerce.csv` (5.630 clientes, snapshot único)  
**Estado**: Fase 2 cerrada — pregunta de negocio definida y documentada en `decisions.md` (#2).

---

## 1. Situación del negocio

Somos un **e-commerce de retail** con base de clientes registrados que compran por app/web. Cada fila del dataset es un cliente con su historial resumido (tenure, pedidos del último mes, satisfacción, quejas, cashback, etc.) y una etiqueta final: **¿se fue (`Churn = 1`) o sigue activo (`Churn = 0`)?**

| Indicador | Valor |
|-----------|------:|
| Clientes en la base | 5.630 |
| Clientes que churnearon | 948 (**16,84%**) |
| Clientes activos | 4.682 (**83,16%**) |

**Problema de negocio**: casi **1 de cada 6 clientes** se va. En un negocio de volumen, eso implica pérdida de ingresos recurrentes, mayor costo de adquisición para reemplazarlos y desgaste de marca (especialmente si se van tras una mala experiencia).

Hoy, sin un modelo, el equipo comercial reacciona **después** del churn: el cliente ya no compra y recién ahí se intenta recuperarlo. Eso es caro y poco efectivo.

---

## 2. Stakeholder y decisión que importa

| Rol | Quién decide con esto |
|-----|------------------------|
| **Stakeholder principal** | Gerente de Retención / CRM del e-commerce |
| **Usuario del output** | Equipo de marketing y atención al cliente |
| **Decisión operativa** | A quién contactar primero, con qué tipo de intervención (cashback, cupón, llamada post-queja, etc.) |

No buscamos un paper académico: buscamos una **lista priorizada de clientes en riesgo** y una **explicación legible** de por qué están en riesgo, para actuar **antes** de que se vayan.

---

## 3. Pregunta de negocio central

> **¿Qué clientes tienen mayor probabilidad de irse (churn) y qué señales de comportamiento reciente explican ese riesgo, para que el equipo de retención pueda intervenir de forma proactiva?**

Desglose en tres sub-preguntas que guían el resto del TP:

| # | Sub-pregunta | Para qué sirve |
|---|--------------|----------------|
| A | ¿Quiénes están en mayor riesgo de churn? | Priorizar contactos (lista de alerta) |
| B | ¿Qué variables se asocian más al riesgo? | Diseñar la intervención (ej. queja → atención; baja satisfacción → encuesta) |
| C | ¿Podemos detectar riesgo **antes** de que el churn sea obvio? | Justificar el modelo frente a un simple reporte de "días sin comprar" |

---

## 4. Definición operativa del target

| Concepto | Definición en este proyecto |
|----------|----------------------------|
| **Churn = 1** | El cliente **se fue** (dejó de ser cliente activo según la etiqueta del dataset) |
| **Churn = 0** | El cliente **sigue activo** |
| **Horizonte temporal** | Snapshot único: variables del **último mes** + etiqueta de churn al cierre del periodo observado |
| **Tipo de problema** | Clasificación binaria supervisada (desbalanceada: ~17% positivos) |

**Importante para la defensa oral**: el dataset es retrospectivo (ya sabemos quién se fue). En producción, el modelo se usaría igual: con datos del mes en curso, estimar probabilidad de irse en el **próximo** periodo. La lógica de negocio es la misma; cambia solo el momento en que mirás los datos.

---

## 5. Señales de negocio disponibles (mapa rápido)

Agrupamos las 18 features (sin `CustomerID`) por tipo de señal que el gerente entiende:

| Grupo | Variables | Lectura de negocio |
|-------|-----------|-------------------|
| **Relación con la marca** | `Tenure` | Clientes nuevos vs. veteranos — ¿la lealtad protege? |
| **Experiencia / satisfacción** | `SatisfactionScore`, `Complain` | Mala experiencia y quejas como alerta temprana |
| **Engagement digital** | `PreferredLoginDevice`, `HourSpendOnApp`, `NumberOfDeviceRegistered` | ¿Cuánto interactúa con la plataforma? |
| **Comportamiento de compra** | `OrderCount`, `DaySinceLastOrder`, `OrderAmountHikeFromlastYear`, `PreferedOrderCat`, `CouponUsed`, `CashbackAmount` | Frecuencia, recencia y valor del cliente |
| **Perfil / logística** | `CityTier`, `WarehouseToHome`, `PreferredPaymentMode`, `Gender`, `MaritalStatus`, `NumberOfAddress` | Segmentación y fricción operativa (distancia al depósito) |

Variables con mayor sospecha de impacto (a validar en EDA, Fase 3–5): `SatisfactionScore`, `Complain`, `DaySinceLastOrder`, `Tenure`.

---

## 6. Criterios de éxito (negocio, no solo ML)

El proyecto es exitoso si logramos:

| Criterio | Métrica / evidencia esperada |
|----------|------------------------------|
| **Detectar riesgo** | Modelo que supere un baseline ingenuo (ej. "predecir siempre 0") en **Recall** de churners — no nos sirve un modelo que ignora a los que se van |
| **Explicar el porqué** | Top factores interpretables para el gerente (importancia de variables, no solo probabilidad) |
| **Ser accionable** | Cada factor fuerte debe traducirse a una acción posible (ej. queja → escalamiento; bajo cashback → oferta) |
| **Honestidad** | Decir en la defensa qué variables son proxy de inactividad (`DaySinceLastOrder`) y cuáles tienen riesgo de leakage (`Complain` — ver `04_leakage_preliminar.md`) |

La métrica técnica principal se formaliza en Fase 9; por ahora acordamos que **no usaremos accuracy** como métrica guía (clase minoritaria).

---

## 7. Acciones de retención que el modelo habilita

Si el modelo funciona, el CRM podría:

1. **Alerta temprana**: exportar top N clientes con mayor probabilidad de churn cada mes.
2. **Playbooks por causa**:
   - Alta prob. + `Complain = 1` → contacto de atención en 48 h.
   - Alta prob. + `SatisfactionScore` bajo → encuesta + beneficio.
   - Alta prob. + `DaySinceLastOrder` alto → campaña de reactivación / cupón.
3. **Priorización de presupuesto**: enfocar cashback y cupones en quienes el modelo marca como riesgo alto (no en toda la base).

---

## 8. Alcance y límites (qué NO prometemos)

| Dentro del alcance | Fuera del alcance |
|--------------------|-------------------|
| Predecir probabilidad de churn con variables del dataset | Predecir **cuándo** exactamente se irá (no es survival analysis) |
| Rankear clientes por riesgo | Calcular LTV o revenue perdido en pesos (no tenemos ticket promedio) |
| Explicar asociaciones (importancia de features) | Afirmar causalidad ("esto **causa** churn") — eso va en decisión #10 |
| Trabajar con 5.630 clientes del CSV | Generalizar a otros mercados sin re-entrenar |

---

## 9. Criterio de cierre Fase 2

- [x] Stakeholder y problema de negocio definidos
- [x] Pregunta central redactada y desglosada
- [x] Target (`Churn`) y horizonte temporal aclarados
- [x] Criterios de éxito desde la perspectiva del gerente
- [x] Decisión #2 registrada en `decisions.md`

**STATUS Fase 2**: **CERRADA** — listo para Fase 3 (EDA exploratorio en `notebooks/01_eda.ipynb`).
