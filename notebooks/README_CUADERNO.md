# Cuaderno científico TFM SAF

Archivo principal: `notebooks/TFM_SAF_pipeline_cientifico.ipynb`

## Preparación

Desde PowerShell, situado en la raíz de `TFM_SAF` y con `.venv` activado:

```powershell
python -m pip install -r requirements_science.txt
python -m jupyter lab
```

Abre `notebooks/TFM_SAF_pipeline_cientifico.ipynb` y ejecuta **Run All**.

El notebook lee exclusivamente `saf_biomass` a través de `src/db/connection.py`. Los artefactos se generan en `outputs/notebook/`.

## Fases

0. Entorno reproducible y conexión MySQL.
1. Extracción de las 11 tablas y tests de integridad.
2. Calidad, cobertura y cardinalidad.
3. EDA avanzado de composición de biomasa.
4. Cribado multiobjetivo con frentes de Pareto.
5. Moléculas y propiedades de combustible con control de unidades.
6. RDKit: validación de SMILES, descriptores 2D y conformeros 3D.
7. xTB/ORCA: manifiesto reproducible, generación de inputs y ejecución opcional.
8. Machine Learning exploratorio de HHV y control de tamaño muestral molecular.
9. NetworkX: red de reacciones, centralidad y alcanzabilidad.
10. Rutas biomasa → combustible y optimización multiobjetivo.
11. Síntesis final y exportación de tablas/figuras.

## Nota sobre xTB y ORCA

La fase está implementada, pero `RUN_XTB=False` y `RUN_ORCA=False` por defecto. Solo deben activarse después de instalar/configurar los ejecutables externos. El notebook nunca simula energías cuánticas.
