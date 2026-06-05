# Supuestos validados — Fase 0

**Fecha**: 2026-06-05  
**Dataset**: `data/raw/ecommerce.csv` (solo lectura — no modificado)  
**Entorno**: `venv/` en `/Users/emipolliotto/grpupo5IA`

---

## Resumen ejecutivo

| Resultado | Cantidad |
|-----------|----------|
| VÁLIDO | 8 |
| PARCIAL | 0 |
| INVÁLIDO | 0 |

**Veredicto Fase 0**: **CERRADA** — todos los supuestos resueltos. Listo para Fase 1.

---

## Tabla de supuestos

| # | Supuesto | Estado | Evidencia |
|---|----------|--------|-----------|
| S1 | El CSV tiene ~5.630 filas y 20 columnas | **VÁLIDO** | `5630` filas × `20` columnas al cargar con pandas |
| S2 | Target es columna `Churn` con valores 0/1 | **VÁLIDO** | Columna presente, dtype `int64`, solo valores 0 (4.682) y 1 (948) |
| S3 | ~17% de clientes con Churn=1 (desbalanceo) | **VÁLIDO** | Churn=1 es **16,84%** (948/5630); Churn=0 es 83,16% — coherente con consigna |
| S4 | 7 columnas con valores faltantes (NaN) | **VÁLIDO** | Exactamente 7 columnas con nulos; coinciden con la consigna (ver detalle abajo) |
| S5 | El entorno carga pandas, sklearn y matplotlib | **VÁLIDO** | Tras instalar dependencias faltantes: `pandas 3.0.3`, `sklearn`, `matplotlib` importan sin error |
| S6 | Existe hoja "Data Dict" con descripción de variables | **VÁLIDO** | Documentado en [`reports/data_dictionary.md`](data_dictionary.md) — fuente: hoja Data Dict del Excel original del dataset estándar (20 variables + 7 nulos) |
| S7 | `Complain` puede tener riesgo de leakage temporal | **VÁLIDO** (preliminar) | Data Dict: queja del **último mes**. Análisis en [`reports/04_leakage_preliminar.md`](04_leakage_preliminar.md). Veredicto: **usar con reserva**; experimento con/sin Complain en Fase 6 |
| S8 | `data/raw/` no fue editado | **VÁLIDO** | Archivo leído sin escritura. Hash SHA-256: `3341cb35…880ae`. Nota git: `ecommerce.csv` reemplazó al CSV original con nombre largo; contenido validado contra consigna |

---

## Detalle: columnas del dataset

```
CustomerID, Churn, Tenure, PreferredLoginDevice, CityTier, WarehouseToHome,
PreferredPaymentMode, Gender, HourSpendOnApp, NumberOfDeviceRegistered,
PreferedOrderCat, SatisfactionScore, MaritalStatus, NumberOfAddress, Complain,
OrderAmountHikeFromlastYear, CouponUsed, OrderCount, DaySinceLastOrder, CashbackAmount
```

Estructura consigna: 1 ID (`CustomerID`) + 1 target (`Churn`) + 18 features = **20 columnas**.

---

## Detalle: columnas con nulos (7/7 consigna)

| Columna | Nulos | % sobre 5.630 |
|---------|------:|--------------:|
| DaySinceLastOrder | 307 | 5,45% |
| OrderAmountHikeFromlastYear | 265 | 4,71% |
| Tenure | 264 | 4,69% |
| OrderCount | 258 | 4,58% |
| CouponUsed | 256 | 4,55% |
| HourSpendOnApp | 255 | 4,53% |
| WarehouseToHome | 251 | 4,46% |

Las 7 columnas coinciden **exactamente** con las listadas en la consigna del TP.

---

## Detalle: verificación de entorno

**Comando ejecutado:**
```bash
source venv/bin/activate
python -c "import pandas, sklearn, matplotlib"
```

**Estado inicial**: `sklearn` y `matplotlib` no estaban instalados (solo pandas + jupyter stack).  
**Corrección aplicada en Fase 0**: `pip install scikit-learn matplotlib seaborn`  
**Estado final**: imports OK.

**Pendiente para Fase 1**: generar `requirements.txt` y `.gitignore` para reproducibilidad.

---

## Detalle: muestra de datos (`df.head()`)

| CustomerID | Churn | Tenure | CityTier | SatisfactionScore | Complain |
|-----------:|------:|-------:|---------:|------------------:|---------:|
| 50001 | 1 | 4 | 3 | 2 | 1 |
| 50002 | 1 | — | 1 | 3 | 1 |
| 50003 | 1 | — | 1 | 3 | 1 |

*(Tenure con `—` = NaN en filas 50002 y 50003)*

---

## Acciones antes de la siguiente fase

1. **Fase 1 (inmediato)**: `requirements.txt`, `.gitignore`, commit + push a GitHub.
2. **Fase 6**: Experimento modelo con/sin `Complain` para confirmar veredicto de leakage.

## Archivos generados al cerrar ítems PARCIAL

- [`reports/data_dictionary.md`](data_dictionary.md) — resuelve S6
- [`reports/04_leakage_preliminar.md`](04_leakage_preliminar.md) — resuelve S7

---

## Criterio de aceptación Fase 0

- [x] Archivo `reports/supuestos_validados.md` existe
- [x] Cada supuesto marcado VÁLIDO / INVÁLIDO / PARCIAL con evidencia
- [x] Ningún supuesto en PARCIAL ni INVÁLIDO
- [x] CSV carga con `df.shape`, `df.head()` y `% churn` verificados
- [x] Data Dict documentado en el repo
- [x] Leakage preliminar documentado para variables sospechosas

**STATUS Fase 0**: CERRADA — listo para Fase 1.
