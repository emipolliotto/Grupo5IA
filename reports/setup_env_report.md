# Setup de entorno — Fase 1

**Fecha**: 2026-06-05  
**Entorno**: `venv/` (Python local)

---

## Verificación de imports

```bash
source venv/bin/activate
python -c "import pandas, numpy, sklearn, matplotlib, seaborn, shap; print('OK')"
```

**Resultado**: OK

| Paquete | Versión |
|---------|---------|
| pandas | 3.0.3 |
| numpy | 2.4.6 |
| scikit-learn | 1.9.0 |
| matplotlib | 3.10.9 |
| seaborn | 0.13.2 |
| jupyter | 1.1.1 |
| shap | 0.52.0 |

---

## Reproducir en otra máquina

```bash
git clone https://github.com/emipolliotto/Grupo5IA.git
cd Grupo5IA
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -c "import pandas; pd.read_csv('data/raw/ecommerce.csv').head()"
```

---

## Skills instalados en `.agents/skills/`

- grill-me
- ds-explorer, ds-dq, ds-stats, ds-feature, ds-model, ds-report, ds-reviewer
- ds-planner, ds-env-bootstrap, gentleman

Fuente: `data-science-kit/skills/` (repo clonado en el proyecto).
