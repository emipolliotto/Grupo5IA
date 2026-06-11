# decisions.md — TP Churn E-commerce

Registro de decisiones importantes del proyecto. Formato consigna: qué / por qué / alternativas / consecuencias.

---

## Índice de decisiones (mínimo 10 para el 19/06)

| # | Título | Fase | Estado |
|---|--------|------|--------|
| 1 | Stack y estructura del repo | 1 | ✅ |
| 2 | Pregunta de negocio central | 2 | ✅ |
| 3 | Tratamiento de nulos por columna | 4 | pendiente |
| 4 | Hipótesis más fuerte del EDA | 5 | pendiente |
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
