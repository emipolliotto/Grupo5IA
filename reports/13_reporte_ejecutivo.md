# Reporte ejecutivo — Retención de clientes e-commerce

**Para:** Gerente de Retención / CRM  
**De:** Grupo 5 — TP Inteligencia Artificial Aplicada a Negocios  
**Fecha:** 11 de junio de 2026  
**Base de análisis:** 5.630 clientes · snapshot histórico (`ecommerce.csv`)

---

## Resumen en 60 segundos

- Casi **1 de cada 6 clientes** se va (**16,8%** de churn).
- El riesgo **no está repartido parejo**: se concentra en los **primeros 6 meses** (35% de churn vs 5% en clientes con más antigüedad).
- Desarrollamos un **modelo de alerta temprana** (Random Forest) que detecta **87 de cada 100** clientes que efectivamente se van, en datos de prueba.
- La historia del negocio: *convertimos bien la primera compra, pero fallamos en convertirla en hábito* — y una buena nota de satisfacción **no garantiza** que vuelvan.
- Las recomendaciones de este documento se basan en **patrones históricos y predicción**; validar impacto con pilotos A/B antes de escalar presupuesto.

---

## 1. El problema de negocio

Hoy el equipo reacciona **después** del churn: el cliente ya no compra y recién ahí se intenta recuperarlo. Eso es caro, tardío y desgasta la marca — especialmente si el cliente se fue tras una mala experiencia o una primera compra que nunca se convirtió en segunda.

**Pregunta que respondimos:** ¿Qué clientes tienen mayor probabilidad de irse y qué señales de comportamiento reciente explican ese riesgo, para intervenir **antes** de perderlos?

---

## 2. Hallazgos de negocio (evidencia del análisis)

| Hallazgo | Dato clave | Implicación |
|----------|------------|-------------|
| **Clientes nuevos son la ventana crítica** | 35% churn si tenure &lt; 6 meses vs 5% si ≥ 6 meses | El programa de retención debe vivir en los **primeros 180 días** |
| **Las quejas son alerta roja** | 32% churn con queja vs 11% sin queja | Playbook de atención en **48 h** post-queja |
| **Nuevo + queja = máximo riesgo** | ~**59%** de churn | Escalamiento inmediato; no esperar al batch mensual |
| **“Happy churner”** | 34% churn en clientes nuevos satisfechos, sin queja, compra reciente | El problema es la **segunda compra**, no salvar la primera |
| **Captación promocional frágil** | 41% churn en nuevos “promo-heavy” vs 33% otros nuevos | Auditar campañas de cupón agresivo |
| **NPS alto no protege** | Score 5 tiene **más** churn que score 1 | No usar satisfacción como regla simple de “cliente seguro” |
| **Churn ≠ inactividad** | Más churn quien compró hace 0–7 días que quien lleva 8–30 sin pedir | No confiar solo en “días sin compra” |

---

## 3. Qué entrega el modelo

| Aspecto | Detalle |
|---------|---------|
| **Algoritmo** | Random Forest (200 árboles) |
| **Uso operativo** | Lista mensual de clientes ordenados por **probabilidad de churn** |
| **Recall (sensibilidad)** | **86,8%** — de 190 churners reales en prueba, detectamos **165** |
| **Precisión** | 64,5% — de cada 10 alertas, ~6–7 son clientes que efectivamente se irían |
| **Ranking global** | ROC-AUC 0,96 — buena separación entre riesgo alto y bajo |

### ¿Qué significa en la práctica?

En un mes con ~190 clientes en riesgo real (escala del test):

- **Sin modelo** (predecir “nadie se va”): se pierden **190** sin alerta — accuracy engañosa del 83%.
- **Con modelo**: quedan **25** sin alerta y **91** contactos a clientes que al final se quedan (costo de “falso positivo”).

Para retención, **perder un churner suele costar más** que contactar de más — por eso priorizamos detectar al máximo de clientes que se van.

---

## 4. Señales que más pesan en el modelo

| Prioridad | Señal | Lectura para CRM |
|:---------:|-------|------------------|
| 1 | **Antigüedad baja** (`Tenure`) | Cliente en etapa de prueba — foco onboarding |
| 2 | **Queja en el último mes** | Experiencia rota — resolver antes de ofertar |
| 3 | **Cashback bajo** | Poca profundidad de relación (no necesariamente “falta de incentivo”) |
| 4 | **Días desde último pedido** | Complementa el perfil; no usarla sola |
| 5 | **Distancia al depósito** | Posible fricción logística |
| 6 | **Estado civil Single** | Segmento de riesgo para priorizar, no para estereotipar |

**Importante:** estas señales **asocian** riesgo en los datos; no prueban que cambiar una variable **cause** retención. Ver sección 6.

---

## 5. Plan de acción recomendado

### Prioridad 1 — Programa “Primeros 180 días”

| Acción | Cuándo | Objetivo |
|--------|--------|----------|
| Check-in automático | Día 7, 30, 60, 90 | Detectar fricción antes del churn |
| Incentivo **segunda compra** | Día 14–30 post-primer pedido | Atacar el “happy churner” (H5) |
| Contenido de hábito | Mes 2–3 | Pasar de transacción única a recurrencia |

### Prioridad 2 — Playbook post-queja

| Condición | Acción | SLA |
|-----------|--------|-----|
| `Complain = 1` y tenure &lt; 6 | Llamada / chat prioritario + resolución | **48 h** |
| `Complain = 1` y tenure ≥ 6 | Ticket estándar + seguimiento | 72 h |
| Queja resuelta | Oferta de retención solo si riesgo sigue alto en modelo | Día 7 post-cierre |

### Prioridad 3 — Auditar captación promocional

- Revisar campañas con **cupón alto + cashback bajo** en clientes nuevos (41% churn).
- Medir no solo CPA de adquisición sino **tasa de segunda compra a 30 días**.
- No cortar promos sin experimento; **ajustar** targeting y secuencia post-compra.

### Prioridad 4 — Operación del modelo en CRM

1. **Mensual:** exportar top N clientes por probabilidad de churn.
2. **Cruzar** con reglas de negocio: tenure &lt; 6, complain, segmento promo.
3. **Asignar** playbooks (sección 5) según perfil dominante.
4. **Medir** contactos realizados vs churn efectivo el mes siguiente.

---

## 6. Límites y honestidad (lo que no prometemos)

| Podemos decir | No podemos decir |
|---------------|------------------|
| “Este cliente tiene **alta probabilidad** de irse” | “Si damos más cashback, **se queda**” |
| “Los nuevos concentran el riesgo” | “Manipular tenure **causa** retención” |
| “Priorizar quien se quejó” | “Eliminar quejas **elimina** churn” |
| “El modelo detecta ~87% de los que se van” | “El modelo **prueba** qué política funciona” |

**Dataset retrospectivo:** aprendimos de clientes que ya churnearon. En producción, el modelo se usa con datos del mes en curso para anticipar el próximo periodo — misma lógica, distinto momento.

**Causalidad:** las acciones propuestas son **apuestas razonables** basadas en asociación; confirmar impacto requiere **pilots A/B** (ej. segunda compra incentivada vs control).

---

## 7. Próximos pasos sugeridos (90 días)

| Plazo | Iniciativa | Responsable sugerido |
|-------|------------|----------------------|
| 0–30 d | Piloto playbook post-queja en clientes nuevos | Atención al cliente + CRM |
| 0–30 d | Integrar scoring mensual del modelo en CRM | TI + CRM |
| 30–60 d | Campaña “segunda compra” día 14–30 (A/B) | Marketing |
| 60–90 d | Revisión de campañas promo-capture | Marketing + Analytics |
| 90 d | Medir churn en cohortes expuestas vs control | Gerencia |

---

## 8. Trazabilidad técnica (para auditoría)

| Documento | Contenido |
|-----------|-----------|
| [`decisions.md`](../decisions.md) | 10 decisiones metodológicas del proyecto |
| [`reports/01_hipotesis.md`](01_hipotesis.md) | Hipótesis H1–H7 con tests estadísticos |
| [`reports/11_modelo_ganador.md`](11_modelo_ganador.md) | Comparación árbol vs Random Forest |
| [`reports/12_importancia_no_causalidad.md`](12_importancia_no_causalidad.md) | Límites de interpretación |
| `src/train_models.py` | Entrenamiento reproducible |
| `models/churn_model.joblib` | Modelo en producción (local) |

---

## Cierre

El e-commerce **no tiene un problema genérico de churn** — tiene un problema de **conversión de la primera compra en relación recurrente**, amplificado por quejas no resueltas y captación promocional sin seguimiento.

El modelo permite **priorizar** a quién contactar y **por qué perfil**; las acciones de las secciones 5 y 7 convierten esa inteligencia en intervención. El siguiente salto de madurez es medir causalidad con experimentos, no solo predicción.

**Contacto del equipo:** repositorio [Grupo5IA](https://github.com/emipolliotto/Grupo5IA)
