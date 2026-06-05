# Auditoría preliminar de leakage — Fase 0 (cierre)

**Fecha**: 2026-06-05  
**Estado**: Preliminar — experimento con/sin `Complain` queda para Fase 6b del plan.

---

## ¿Qué es leakage en criollo?

Es cuando el modelo "hace trampa" porque ve información que en la vida real **todavía no tendrías** cuando querés predecir si alguien se va. Como estudiar con las respuestas del examen: en el laboratorio va bien, en producción falla.

---

## Variable: `Complain`

### Qué dice el Data Dictionary

> "Any complaint has been raised **in last month**" (¿hubo queja en el último mes?)

No dice "después de irse". Describe comportamiento del mes previo al snapshot.

### Qué muestran los datos

| Complain | Clientes | % que se fueron (churn) |
|:--------:|---------:|------------------------:|
| 0 (no se quejó) | 4.026 | **10,93%** |
| 1 (se quejó) | 1.604 | **31,67%** |
| **Total** | 5.630 | **16,84%** |

Quienes se quejaron tienen casi **3× más churn** que quienes no. Es una señal fuerte — y por eso hay que cuidarla: ¿es causa, consecuencia, o las dos?

### Veredicto preliminar

| Criterio | Evaluación |
|----------|------------|
| ¿Está documentada como dato del último mes? | Sí — Data Dict |
| ¿Parece registrada después del churn? | No hay evidencia en el CSV |
| ¿Correlación sospechosamente alta? | Sí — 31,67% vs 10,93% |
| **Decisión Fase 0** | **USAR CON RESERVA** |

**Recomendación para modelado**: incluir `Complain` en el modelo principal, pero en Fase 6 entrenar también un modelo **sin** `Complain` y comparar Recall. Si las métricas colapsan sin ella, la señal es real; si solo con ella el modelo "brilla", revisar de nuevo.

---

## Variable: `DaySinceLastOrder`

### Qué dice el Data Dictionary

> "Day Since last order by customer"

### Qué muestran los datos (clientes sin nulo en esta columna)

| Días sin pedir | Clientes | % churn |
|----------------|---------:|--------:|
| 0–7 días | 4.021 | 19,17% |
| 8–30 días | 1.300 | 9,38% |
| 31–90 días | 2 | 50,00%* |

\*Muestra diminuta — no interpretar.

### Veredicto preliminar

| **Decisión Fase 0** | **USAR — señal de negocio legítima** |

Muchos días sin comprar suele ir de la mano con irse. Ojo: si "churn" se define justo como "dejó de comprar", esta variable está **muy pegada** a la definición del problema. No es trampa técnica, pero hay que **decirlo en la defensa oral**: "detectamos inactividad reciente, que es justamente lo que el gerente ya podría ver en un reporte de ventas".

---

## Variable: `OrderCount`

### Qué dice el Data Dictionary

> "Total number of orders placed **in last month**"

### Qué muestran los datos

Todos los valores observados son > 0 (no hay clientes con 0 pedidos en el mes en este extracto). Churn global en quienes tienen dato: **17,31%**.

### Veredicto preliminar

| **Decisión Fase 0** | **USAR** — comportamiento del último mes, coherente con el dict |

---

## Resumen para `decisions.md` (borrador — formalizar en Fase 6)

1. **Complain**: se incluye por ahora; riesgo de leakage **bajo** según Data Dict, pero correlación alta → validar con experimento A/B en modelado.
2. **DaySinceLastOrder**: se incluye; explicar en defensa que es proxy de inactividad (cerca del concepto de churn).
3. **OrderCount**: se incluye; sin señales de leakage.

---

## Criterio de cierre Fase 0 — supuesto S7

- [x] Cada variable sospechosa tiene veredicto documentado
- [x] `Complain` tiene argumento temporal basado en Data Dict + datos
- [ ] Experimento modelo con/sin `Complain` — pendiente Fase 6

**S7 pasa de PARCIAL a VÁLIDO (preliminar)** con revisión obligatoria en Fase 6.
