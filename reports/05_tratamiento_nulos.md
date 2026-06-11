# Tratamiento de nulos — Fase 4

**Fecha**: 2026-06-11  
**Dataset**: `data/raw/ecommerce.csv` (sin modificar)  
**Decisión registrada**: `decisions.md` #3  
**Estado**: Fase 4 cerrada — estrategia definida; implementación post-split en Fase 8.

---

## 1. Resumen ejecutivo

| Decisión global | Veredicto |
|-----------------|-----------|
| ¿Eliminar filas con nulos? | **NO** — se perderían 1.856 filas (33%) |
| ¿Eliminar columnas con nulos? | **NO** — las 7 son features de negocio relevantes |
| ¿Imputar? | **SÍ** — mediana calculada **solo en train** (Fase 8) |
| ¿Indicadores de missing? | **SÍ** — una bandera binaria por cada una de las 7 columnas |

**Hallazgo clave**: cada fila tiene **como máximo 1 nulo** entre las 7 columnas afectadas (nunca se superponen). Eso simplifica el tratamiento: no hay filas con múltiples huecos simultáneos en este grupo.

---

## 2. Inventario de nulos

| Columna | Nulos | % filas | Churn si nulo | Churn si no nulo | Tipo de missing |
|---------|------:|--------:|--------------:|-----------------:|-----------------|
| `DaySinceLastOrder` | 307 | 5,45% | 17,6% | 16,8% | MCAR leve / poco informativo solo |
| `OrderAmountHikeFromlastYear` | 265 | 4,71% | **5,3%** | 17,4% | **MNAR** — nulo ≈ bajo riesgo |
| `Tenure` | 264 | 4,69% | **30,7%** | 16,2% | **MNAR** — nulo ≈ alto riesgo |
| `OrderCount` | 258 | 4,58% | **7,0%** | 17,3% | **MNAR** — nulo ≈ bajo riesgo |
| `CouponUsed` | 256 | 4,55% | **3,1%** | 17,5% | **MNAR** — nulo ≈ muy bajo riesgo |
| `HourSpendOnApp` | 255 | 4,53% | **22,8%** | 16,6% | **MNAR** — nulo ≈ alto riesgo |
| `WarehouseToHome` | 251 | 4,46% | **33,5%** | 16,1% | **MNAR** — nulo ≈ alto riesgo |

**Filas con al menos un nulo**: 1.856 (32,97%).  
**Churn agregado con/sin algún nulo**: 17,1% vs 16,7% — casi igual a nivel global, pero **por columna el nulo es muy informativo** (no tratarlo como ruido aleatorio).

---

## 3. Estrategia por columna

| Columna | Tratamiento del valor | Indicador `{col}_missing` | Lectura de negocio |
|---------|----------------------|---------------------------|-------------------|
| `Tenure` | Mediana en **train** | **Sí (1)** | Sin antigüedad registrada correlaciona con churn alto — cliente nuevo o dato incompleto |
| `WarehouseToHome` | Mediana en **train** | **Sí (1)** | Sin distancia al depósito → 33% churn; posible fricción logística no medida |
| `HourSpendOnApp` | Mediana en **train** | **Sí (1)** | Sin dato de uso de app → más churn; desenganche digital |
| `DaySinceLastOrder` | Mediana en **train** | **Sí (1)** | Diferencia menor pero se mantiene por consistencia y por ser variable clave |
| `OrderAmountHikeFromlastYear` | Mediana en **train** | **Sí (1)** | Nulo suele ser cliente sin historial año a año (bajo churn) |
| `OrderCount` | Mediana en **train** | **Sí (1)** | Nulo asociado a bajo churn — posible cliente sin actividad reciente registrada |
| `CouponUsed` | Mediana en **train** | **Sí (1)** | Nulo con 3% churn — casi “no usó cupones / sin campaña” |

**Convención de nombres** para indicadores: `Tenure_missing`, `WarehouseToHome_missing`, etc. (1 = era nulo antes de imputar, 0 = tenía valor).

---

## 4. Lo que NO hacemos (y por qué)

| Alternativa descartada | Motivo |
|------------------------|--------|
| **Listwise deletion** (borrar filas con cualquier nulo) | Pierde 33% de la base; sesga si el missing es informativo |
| **Imputar con mediana global antes del split** | Filtra información del test al train → leakage |
| **Imputar con 0 en todas** | No tiene sentido de negocio para `Tenure` o `WarehouseToHome` |
| **Imputar usando el target** (ej. mediana por churn) | Leakage directo |
| **KNN / MICE multivariado** | Overkill para ~5% por columna y missing mutuamente excluyente; poca ganancia vs complejidad en un TP |
| **Ignorar el missing** (solo mediana, sin bandera) | En `Tenure` y `WarehouseToHome` el nulo predice churn mejor que muchas features |

---

## 5. Orden de ejecución (Fase 7–8)

```
1. Split estratificado train/test     ← Fase 7 (antes de tocar nulos)
2. En train: calcular medianas por columna
3. En train y test: crear 7 columnas *_missing
4. En train y test: imputar con medianas aprendidas en train
5. Nunca recalcular medianas usando test
```

El CSV en `data/raw/` **no se modifica**. Los datos limpios van a `data/processed/` (gitignored).

---

## 6. Impacto esperado en el modelo

- **7 features nuevas** (indicadores) + 7 columnas imputadas.
- Los árboles y Random Forest pueden usar las banderas `*_missing` como splits — especialmente útil en `Tenure`, `WarehouseToHome` y `CouponUsed`.
- En la defensa oral: *“El missing no es aleatorio; por eso imputamos con mediana del train y agregamos una bandera para que el modelo sepa que el valor era desconocido.”*

---

## 7. Criterio de cierre Fase 4

- [x] Análisis de nulos por columna (tasa, churn si nulo vs no nulo)
- [x] Patrón de exclusividad documentado (máx. 1 nulo por fila)
- [x] Estrategia por columna definida
- [x] Decisión #3 en `decisions.md`
- [x] Implementación diferida a Fase 8 (post-split)

**STATUS Fase 4**: **CERRADA** — próximo paso: **Fase 5** (hipótesis más fuerte del EDA → decisión #4).
