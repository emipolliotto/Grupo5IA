# decisions.md — TP Churn E-commerce

Registro de decisiones importantes del proyecto. Formato consigna: qué / por qué / alternativas / consecuencias.

---

## Índice de decisiones (mínimo 10 para el 19/06)

| # | Título | Fase | Estado |
|---|--------|------|--------|
| 1 | Stack y estructura del repo | 1 | ✅ |
| 2 | Pregunta de negocio central | 2 | ✅ |
| 3 | Tratamiento de nulos por columna | 4 | ✅ |
| 4 | Hipótesis más fuerte del EDA | 5 | ✅ |
| 5 | Veredicto Complain y leakage | 6 | borrador en `04_leakage_preliminar.md` |
| 6 | Split antes de limpiar + estratificado | 7 | pendiente |
| 7 | Estrategia de imputación/encoding | 8 | pendiente |
| 8 | Métrica principal (no accuracy) | 9 | pendiente |
| 9 | Modelo ganador árbol vs RF | 11 | pendiente |
| 10 | Importancia ≠ causalidad | 12 | pendiente |

---

## Decisión — Stack y estructura del repo

1. **Qué decidí**: Python 3 con `venv` local, dependencias pinneadas en `requirements.txt`, dataset crudo en `data/raw/ecommerce.csv` (solo lectura), código en `src/`, notebooks en `notebooks/`, reportes en `reports/`.

2. **Por qué**: La consigna exige repo reproducible en GitHub; otro alumno o el profe debe clonar e instalar sin adivinar versiones. Separar `data/raw/` (intocable) de `data/processed/` (generado después del split) evita mezclar datos originales con transformados.

3. **Alternativas que descarté**:
   - **Google Colab sin repo**: rápido pero no cumple entregable GitHub ni trazabilidad de decisiones.
   - **Anaconda global sin lockfile**: cada máquina instala versiones distintas → notebooks que corren en una PC y fallan en otra.
   - **Commitear `venv/`**: pesa gigas y no es portable entre Windows/Mac/Linux.

4. **Consecuencias**: Setup documentado en `reports/setup_env_report.md`. Skills de data science linkeados desde `data-science-kit/` a `.agents/skills/`. Próximo paso: Fase 3 (EDA).

---

## Decisión — Pregunta de negocio central

1. **Qué decidí**: La pregunta guía del TP es: *¿Qué clientes tienen mayor probabilidad de irse (churn) y qué señales de comportamiento reciente explican ese riesgo, para que el equipo de retención pueda intervenir de forma proactiva?* Stakeholder: Gerente de Retención / CRM. Target: `Churn` binario (1 = se fue, ~17%). Problema: clasificación supervisada desbalanceada sobre snapshot del último mes.

2. **Por qué**: La consigna pide detectar riesgo de churn **y explicar por qué** — no alcanza con un dashboard de ventas. Esta pregunta une predicción (lista priorizada) con interpretación (playbooks de retención) y es testeable con las 18 features del dataset. Evita metas vagas ("entender al cliente") o técnicas sin dueño de negocio.

3. **Alternativas que descarté**:
   - **Solo clustering sin target**: agrupa perfiles pero no responde "¿quién se va?" — el gerente necesita una etiqueta de riesgo.
   - **Predecir LTV / revenue**: no tenemos monto de pedido ni horizonte de ingresos; forzaría supuestos no auditables.
   - **Pregunta solo descriptiva** ("¿cuál es el % de churn?"): ya lo sabemos (16,84%); no justifica modelo ni entrega del 19/06.
   - **Survival analysis** (¿cuándo se va?): el dataset no trae fechas de evento; una foto estática no alcanza para tiempo-hasta-churn.

4. **Consecuencias**: Contexto documentado en `reports/02_contexto_negocio.md`. El EDA (Fase 3–5) debe validar señales sospechosas (`SatisfactionScore`, `Complain`, `DaySinceLastOrder`, `Tenure`). La métrica principal se elige en Fase 9 con foco en **Recall** de churners. En la defensa oral hay que aclarar que el dataset es retrospectivo pero la lógica operativa es prospectiva (intervenir antes del churn).

---

## Decisión — Tratamiento de nulos por columna

1. **Qué decidí**: No eliminar filas ni columnas. Las 7 columnas con nulos (`DaySinceLastOrder`, `OrderAmountHikeFromlastYear`, `Tenure`, `OrderCount`, `CouponUsed`, `HourSpendOnApp`, `WarehouseToHome`) se imputan con **mediana del set de entrenamiento** y se agrega un **indicador binario** `{columna}_missing` por cada una. Cada fila tiene como máximo un nulo entre estas siete (missing mutuamente excluyente). La imputación se ejecuta **después del split** (Fase 7–8); `data/raw/` no se toca.

2. **Por qué**: Borrar filas costaría 1.856 registros (33%). El nulo no es aleatorio: en `Tenure` y `WarehouseToHome` el churn supera el 30% cuando falta el dato; en `CouponUsed` baja al 3%. Solo imputar con mediana sin bandera haría perder esa señal. Mediana en train evita sesgo extremo y no filtra información del test.

3. **Alternativas que descarté**:
   - **Listwise deletion**: pierde un tercio de la base y sesga el modelo.
   - **Imputar antes del split o usando el target**: leakage.
   - **Imputar todo con 0**: sin sentido para `Tenure` o distancia al depósito.
   - **KNN / MICE**: complejidad innecesaria para ~5% de nulos por columna sin solapamiento.
   - **Un solo flag `any_missing`**: pierde el significado distinto del nulo según columna.

4. **Consecuencias**: Detalle en `reports/05_tratamiento_nulos.md`. El pipeline de Fase 8 debe aprender medianas solo en train y generar 7 columnas extra de indicadores. En defensa oral: explicar que el missing es MNAR en varias columnas y por eso las banderas son features legítimas.

---

## Decisión — Hipótesis más fuerte del EDA

1. **Qué decidí**: La hipótesis principal del TP es: **los clientes con menos de 6 meses de antigüedad (`Tenure` < 6) tienen significativamente mayor probabilidad de churn que el resto** (35,0% vs 5,2%; lift 6,7×; correlación −0,35). Hipótesis secundaria más fuerte: **`Complain = 1` aumenta el churn** (31,7% vs 10,9%; lift 2,9×). Se refutan como hipótesis simples: “menor satisfacción → más churn” y “más días sin pedir → más churn”.

2. **Por qué**: `Tenure` concentra el mayor contraste de churn y la correlación más alta con el target. Es interpretable para el gerente (“cliente nuevo = ventana crítica”) y orienta una acción clara (onboarding 0–180 días). `Complain` queda como segunda prioridad por accionabilidad inmediata. Descartar las hipótesis refutadas evita narrativas falsas en el reporte ejecutivo.

3. **Alternativas que descarté**:
   - **`Complain` como hipótesis #1**: lift menor (2,9× vs 6,7×) y riesgo de leakage a validar; queda como H2.
   - **`SatisfactionScore` bajo → churn**: el EDA muestra lo opuesto en extremos (score 5 = 23,8% churn).
   - **`DaySinceLastOrder` alto → churn**: clientes con compra reciente (0–7 d) tienen más churn que los de 8–30 d.
   - **Segmentos categóricos** (Single, Mobile Phone): lift ~2× pero sin correlación fuerte ni narrativa causal clara.

4. **Consecuencias**: Documentado en `reports/06_hipotesis_eda.md`. El modelado debe priorizar `Tenure` y `Complain`; interacción crítica: tenure < 6 + queja ≈ 59% churn. En defensa oral: foco en retención temprana. Próximo paso: Fase 6 (experimento con/sin `Complain`).
