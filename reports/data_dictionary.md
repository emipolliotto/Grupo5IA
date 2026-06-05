# Data Dictionary — E-Commerce Customer Churn

**Fuente**: Hoja "Data Dict" del archivo original `E Commerce Dataset.xlsx` (dataset estándar del TP, 5.630 clientes).  
**Tabla de datos**: `data/raw/ecommerce.csv` (hoja "E Comm" — solo lectura).  
**Verificado**: hash SHA-256 idéntico al CSV de referencia en Downloads (`3341cb35…880ae`).

---

## Variables (20 columnas)

| # | Columna | Descripción | Tipo | Notas de negocio |
|---|---------|-------------|------|------------------|
| 1 | `CustomerID` | ID único del cliente | Numérico | No usar en modelado — es identificador |
| 2 | `Churn` | ¿El cliente se fue? (1 = sí, 0 = sigue activo) | Numérico | **Variable objetivo** (~17% = 1) |
| 3 | `Tenure` | Meses que lleva el cliente en la empresa | Numérico | Tiene nulos (~4,7%) — sospechosa predictora |
| 4 | `PreferredLoginDevice` | Dispositivo preferido para iniciar sesión | Texto | Mobile Phone, Phone, Computer, etc. |
| 5 | `CityTier` | Nivel/tier de la ciudad (1, 2 o 3) | Numérico | Segmentación geográfica |
| 6 | `WarehouseToHome` | Distancia entre depósito y domicilio del cliente | Numérico | Tiene nulos (~4,5%) |
| 7 | `PreferredPaymentMode` | Método de pago preferido | Texto | Debit Card, UPI, Credit Card, etc. |
| 8 | `Gender` | Género del cliente | Texto | Male / Female |
| 9 | `HourSpendOnApp` | Horas de uso de app o web en el último periodo | Numérico | Tiene nulos (~4,5%) |
| 10 | `NumberOfDeviceRegistered` | Cantidad de dispositivos registrados | Numérico | |
| 11 | `PreferedOrderCat` | Categoría de pedido preferida el último mes | Texto | Mobile, Laptop & Accessory, etc. |
| 12 | `SatisfactionScore` | Puntaje de satisfacción con el servicio (1–5) | Numérico | Hipótesis obvia: bajo → más churn |
| 13 | `MaritalStatus` | Estado civil | Texto | Single, Married, Divorced |
| 14 | `NumberOfAddress` | Cantidad de direcciones cargadas | Numérico | |
| 15 | `Complain` | ¿Hubo queja en el último mes? (1 = sí, 0 = no) | Numérico | **Revisar leakage** — ver `04_leakage_preliminar.md` |
| 16 | `OrderAmountHikeFromlastYear` | % de aumento en monto de pedidos vs año anterior | Numérico | Tiene nulos (~4,7%) |
| 17 | `CouponUsed` | Cupones usados en el último mes | Numérico | Tiene nulos (~4,6%) |
| 18 | `OrderCount` | Pedidos realizados en el último mes | Numérico | Tiene nulos (~4,6%) — comportamiento reciente |
| 19 | `DaySinceLastOrder` | Días desde el último pedido | Numérico | Tiene nulos (~5,5%) — **sospechosa** de churn |
| 20 | `CashbackAmount` | Cashback promedio en el último mes | Numérico | Comportamiento transaccional |

---

## Columnas con valores faltantes (7)

| Columna | Nulos | % |
|---------|------:|--:|
| `DaySinceLastOrder` | 307 | 5,45% |
| `OrderAmountHikeFromlastYear` | 265 | 4,71% |
| `Tenure` | 264 | 4,69% |
| `OrderCount` | 258 | 4,58% |
| `CouponUsed` | 256 | 4,55% |
| `HourSpendOnApp` | 255 | 4,53% |
| `WarehouseToHome` | 251 | 4,46% |

---

## Lectura temporal del dataset (importante)

Este dataset es una **foto en un momento dado**: cada fila resume el comportamiento del cliente en el **último mes** (quejas, pedidos, cupones, cashback) y si **eventualmente churneó**.

Las variables con "last month" en la descripción son señales del periodo previo a la etiqueta de churn — en principio **legítimas para predecir**, siempre que la etiqueta `Churn` no se haya definido usando información posterior a esas variables.
