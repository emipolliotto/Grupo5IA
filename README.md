# TP Churn — E-commerce Customer Churn

Proyecto del TP de **Inteligencia Artificial Aplicada a Negocios** (Licenciatura en Negocios y Tecnología).

**Objetivo:** detectar qué clientes están en riesgo de irse (churn) y explicar por qué, para que el equipo comercial pueda actuar antes de perderlos.

---

## Requisitos previos

- Python 3.10 o superior
- Git

---

## Setup rápido (verificar Fase 1)

Abrí una **terminal** y ejecutá estos comandos **uno por uno**:

```bash
# 1. Clonar el repo (solo la primera vez)
git clone https://github.com/emipolliotto/Grupo5IA.git
cd Grupo5IA

# 2. Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate          # Mac/Linux
# venv\Scripts\Activate.ps1       # Windows (PowerShell)

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Verificar que todo funciona
python -c "import pandas as pd; print(pd.read_csv('data/raw/ecommerce.csv').shape)"
```

### Resultado esperado

Si la Fase 1 está bien hecha, el último comando debe imprimir:

```
(5630, 20)
```

- **5630** = cantidad de clientes en el dataset  
- **20** = cantidad de columnas  

Si ves otro número o un error, revisá que estés dentro de la carpeta `Grupo5IA` y que el entorno `(venv)` esté activado.

---

## Estructura del proyecto

```
Grupo5IA/
├── data/
│   └── raw/
│       └── ecommerce.csv      # Dataset original — NO editar
├── notebooks/
│   └── 01_eda.ipynb           # Exploración de datos
├── reports/                   # Reportes y hallazgos
├── decisions.md               # Registro de decisiones del TP
├── requirements.txt           # Dependencias pinneadas
└── src/                       # Código reutilizable (split, preprocess, etc.)
```

---

## Dataset

- **5.630 clientes**, **20 columnas**
- Target: `Churn` (1 = se fue, 0 = sigue activo)
- ~17% de churn (clase minoritaria)
- Diccionario de variables: [`reports/data_dictionary.md`](reports/data_dictionary.md)

---

## Fechas de entrega

| Fecha | Entregables |
|-------|-------------|
| **12/06** | EDA, hipótesis, setup en GitHub, `decisions.md` |
| **19/06** | Modelo, reporte ejecutivo, defensa oral |

---

## Entregables clave

| Documento | Descripción |
|-----------|-------------|
| [`reports/13_reporte_ejecutivo.md`](reports/13_reporte_ejecutivo.md) | **Reporte ejecutivo** para Gerente de Retención / CRM |
| [`decisions.md`](decisions.md) | 10 decisiones metodológicas del TP |
| [`reports/01_hipotesis.md`](reports/01_hipotesis.md) | Hipótesis de negocio H1–H7 |
| [`notebooks/01_eda.ipynb`](notebooks/01_eda.ipynb) | EDA exploratorio |

---

## Links

- Repo: https://github.com/emipolliotto/Grupo5IA
- Setup detallado: [`reports/setup_env_report.md`](reports/setup_env_report.md)
