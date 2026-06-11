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
| 4b | Narrativa consultoría — segunda compra | 5 | ✅ |
| 5 | Veredicto Complain y leakage | 6 | ✅ |
| 6 | Split antes de limpiar + estratificado | 7 | ✅ |
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

1. **Qué decidí**: Seis hipótesis formales en `reports/01_hipotesis.md` (formato consigna: H₀/H₁, gráfico, test, interpretación). **Hipótesis principal (H1)**: clientes con `Tenure` < 6 churnean significativamente más (35,0% vs 5,2%; lift 6,7×; corr. −0,35). **Hipótesis secundaria (H2)**: `Complain = 1` aumenta el churn (31,7% vs 10,9%; lift 2,9×). **Refutadas (H3, H4)**: “menor satisfacción → más churn” (score alto = 20,5% vs bajo = 11,9%) y “más días sin pedir → más churn” (0–7 d = 19,2% vs 8–30 d = 9,4%). **Confirmadas en cruces (H5, H6)**: perfil “happy churner” (tenure < 6 + sat ≥ 4 + compra reciente + sin queja = 33,9% churn) y captación promocional sin retención (cupón alto + cashback bajo + tenure < 6 = 41,3% churn).

2. **Por qué**: La consigna exige hipótesis con lógica de negocio **validadas** con gráfico y test — no solo correlaciones sueltas. `Tenure` concentra el mayor contraste y es accionable (onboarding 0–180 días). `Complain` es la segunda palanca por urgencia operativa. Refutar H3 y H4 evita recomendaciones falsas (“bajá el NPS” o “solo retengan inactivos”). H5 y H6 explican las paradojas del EDA (satisfacción alta + compra reciente + churn) con una narrativa de consultoría: **falla la segunda compra, no la primera**.

3. **Alternativas que descarté**:
   - **`Complain` como hipótesis #1**: lift menor (2,9× vs 6,7×); queda H2.
   - **Mantener H3/H4 sin refutar**: llevaría a acciones incorrectas ante el gerente.
   - **Solo segmentos categóricos** (Single, Mobile Phone): lift ~2× sin narrativa causal fuerte ni test de interacción.
   - **H5 como hipótesis principal**: lift menor que H1 y aplica a un subsegmento (n = 448); enriquece la historia pero no reemplaza a Tenure.

4. **Consecuencias**: Detalle en `reports/01_hipotesis.md` y `reports/06_hipotesis_eda.md`. Cruces en `notebooks/01_eda.ipynb` §9–10. Modelado: priorizar `Tenure` y `Complain`; no forzar monotonía en `SatisfactionScore` ni `DaySinceLastOrder`. Interacción crítica: tenure < 6 + queja = 58,9% churn.

---

## Decisión — Narrativa consultoría — segunda compra

1. **Qué decidí**: La historia que le cuento al gerente comercial no es “los clientes están insatisfechos” sino: **el churn es un problema de supervivencia temprana (H1) dentro del cual hay compradores que tienen buena primera experiencia pero no vuelven (H5)**. Las palancas son: (a) onboarding 30/60/90 días, (b) incentivo de segunda compra a los 14–30 días post-primer pedido, (c) playbook post-queja urgente en clientes nuevos, (d) auditar campañas de cupón que traen volumen sin retención (H6).

2. **Por qué**: Los datos muestran señales aparentemente contradictorias — antigüedad baja, compra reciente, satisfacción alta y churn elevado coexisten. Eso no es ruido: es el perfil del **comprador eventual**. Un consultor no presenta cuatro gráficos sueltos; presenta un mecanismo: primera compra OK → sin hábito → churn. Esto cumple la consigna (“entender por qué nos dejan”) y diferencia el TP de un ejercicio técnico.

3. **Alternativas que descarté**:
   - **“Mejorar satisfacción general”**: H3 refutada — score 5 entre nuevos tiene 45,5% churn.
   - **“Retener solo inactivos”**: H4 refutada — el riesgo está en quien compró hace 0–7 días (19,2% global; 36% si es nuevo).
   - **“Más dispositivos = más lealtad”**: entre nuevos, 4 dispositivos = 35,6% churn vs 20% con 1 dispositivo — sugiere prueba, no hábito.
   - **Ignorar cashback/cupón**: H6 muestra 41,3% churn en captación promocional vs 33,4% en otros nuevos.

4. **Consecuencias**: Narrativa lista para reporte ejecutivo (19/06) y defensa oral. Limitación explícita: dataset es snapshot — no prueba estacionalidad ni causalidad. Correlación ≠ “cupón causa churn”; la recomendación es **auditar** campañas, no eliminarlas sin experimento.

---

## Decisión — Veredicto Complain y leakage

1. **Qué decidí**: Incluir `Complain` en el modelo final (**USAR**). Experimento A/B (RF y árbol, split 80/20 estratificado): sin `Complain`, Recall baja de 0,868 a 0,800 (−6,8 pp) pero el modelo sigue fuerte; `Tenure` domina la importancia (33–36%). `DaySinceLastOrder` y `OrderCount` se mantienen (**USAR** / **USAR CON TRANSPARENCIA**).

2. **Por qué**: Leakage haría colapsar las métricas sin la variable o concentraría toda la importancia en ella. Ninguno de los dos ocurre. `Complain` aporta señal incremental accionable (playbook post-queja) sobre una base ya explicada por `Tenure`. El Data Dict la define como queja del último mes — coherente con uso predictivo.

3. **Alternativas que descarté**:
   - **Excluir `Complain` por precaución**: pierde 6,8 pp de Recall sin beneficio claro de robustez.
   - **Usar solo `Complain` como feature de riesgo**: ignora que `Tenure` explica más y que el modelo funciona sin ella.
   - **Descartar `DaySinceLastOrder`**: no hay evidencia de leakage técnico; solo proxy de actividad reciente a declarar en defensa.

4. **Consecuencias**: Experimento reproducible en `src/leakage_experiment.py` y `reports/07_veredicto_complain_leakage.md`. Supuesto S7 cerrado. Modelo final incluye `Complain`.

---

## Decisión — Split antes de limpiar + estratificado

1. **Qué decidí**: Partir `data/raw/ecommerce.csv` en **80% train / 20% test** con `train_test_split(..., stratify=Churn, random_state=42)` **antes** de imputar, crear flags `*_missing` o encodear. Guardar en `data/processed/train.csv` y `test.csv` (crudos, con nulos). Manifest en `data/processed/split_manifest.json`.

2. **Por qué**: Imputar o calcular estadísticas sobre el dataset completo filtra información del test al entrenamiento (leakage). Con ~17% de churn, un split aleatorio sin estratificar podría dejar el test con muy pocos positivos (~190 en test con estratificación). `random_state=42` alinea este split con el experimento de Fase 6.

3. **Alternativas que descarté**:
   - **Split después de imputar**: mediana global contamina el test.
   - **K-fold como único esquema**: útil para tuning pero no reemplaza un hold-out final para el reporte.
   - **70/30 o 90/10**: 80/20 balancea suficientes churners en test (~190) con train robusto (4.504 filas).
   - **Estratificar por otra variable** (ej. `Tenure`): no es el target; el desbalance crítico es `Churn`.

4. **Consecuencias**: Script `src/split.py`. Train 16,83% churn / test 16,87% churn. Fase 8 aprende medianas y encoders **solo en train**. Próximo paso: Fase 8 (pipeline de preprocesamiento).
