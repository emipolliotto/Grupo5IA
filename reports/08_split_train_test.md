# Split train/test — Fase 7

**Fecha**: 2026-06-11  
**Script**: `src/split.py`  
**Manifest**: `data/processed/split_manifest.json`  
**Decisión registrada**: `decisions.md` #6  
**Estado**: Fase 7 cerrada — partición estratificada sobre datos crudos.

---

## 1. Objetivo

Separar la base en **entrenamiento** y **prueba** antes de cualquier limpieza (imputación, encoding, flags de missing), para evitar leakage de estadísticas del test al train (Fase 4).

---

## 2. Decisión de partición

| Parámetro | Valor | Motivo |
|-----------|-------|--------|
| Proporción | **80% train / 20% test** | Estándar del curso; test con ~190 churners (suficiente para Recall) |
| Estratificación | **`Churn`** | Mantener ~16,8% de positivos en ambos conjuntos (clase minoritaria) |
| `random_state` | **42** | Reproducibilidad; mismo split que experimento Fase 6 |
| Datos de entrada | `data/raw/ecommerce.csv` | Sin transformar — nulos intactos |
| Salida | `data/processed/train.csv`, `test.csv` | Gitignored |

---

## 3. Resultados del split

| Conjunto | Filas | Churn (n) | Tasa churn | Filas con ≥1 nulo* |
|----------|------:|----------:|-----------:|-------------------:|
| **Train** | 4.504 | 758 | **16,83%** | 1.491 |
| **Test** | 1.126 | 190 | **16,87%** | 365 |
| **Total** | 5.630 | 948 | 16,84% | 1.856 |

\*Entre las 7 columnas con nulos documentadas en Fase 4.

**Verificación**: la diferencia de tasa de churn entre train y test es **0,04 pp** — estratificación exitosa.

---

## 4. Qué contienen los archivos

Los CSV en `data/processed/` son **copias parciales del raw**:
- Mismas 20 columnas que `ecommerce.csv`
- **Nulos sin tocar** (ej. `Tenure` conserva sus 264 nulos repartidos ~211 train / ~53 test)
- `CustomerID` incluido (se excluye en modelado, no en el split)

**No incluyen** (eso es Fase 8):
- Indicadores `*_missing`
- Imputación de medianas
- One-hot encoding

---

## 5. Orden del pipeline (confirmado)

```
data/raw/ecommerce.csv
        │
        ▼
  split estratificado (Fase 7)  ← estamos aquí
        │
   ┌────┴────┐
   ▼         ▼
 train.csv  test.csv   (crudos, con nulos)
   │         │
   └────┬────┘
        ▼
  preprocess (Fase 8) — medianas solo de train, flags, encoding
        ▼
  modelado (Fase 9+)
```

---

## 6. Reproducir

```bash
python src/split.py
```

Regenera `train.csv`, `test.csv` y `split_manifest.json`.

---

## 7. Criterio de cierre Fase 7

- [x] Split 80/20 estratificado por `Churn`
- [x] Ejecutado **antes** de imputar o encodear
- [x] Archivos en `data/processed/` con nulos preservados
- [x] Manifest con conteos y tasas para auditoría
- [x] Decisión #6 en `decisions.md`

**STATUS Fase 7**: **CERRADA** — próximo paso: **Fase 8** (implementar imputación + encoding → decisión #7).
