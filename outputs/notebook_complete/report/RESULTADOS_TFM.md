# Resultados reproducibles — TFM SAF

Fecha: 2026-09-17T08:35:40
Python 3.11.9 | MySQL 8.0.43 | config 2cfdcecdf3323eae

## 1. Integridad del dataset
- Fuentes: 96
- Biomasas residuales registradas: 183
- Mediciones de composición: 306
- Moléculas: 173
- Reacciones: 82
- Participantes de reacción: 164
- Propiedades de combustible: 64
- Fallos críticos de integridad: 0

## 2. Biomasa y estadística
- Registros de composición en dry_basis: 73
- Outliers robustos marcados (no eliminados): 1
- Alternativas del frente Pareto bioquímico: 9
- Alternativas del frente Pareto termoquímico: 1

## 3. Química molecular
- Moléculas con SMILES: 18 / 173
- Descriptores RDKit 2D distintos: 217
- Moléculas con conformero 3D válido: 18

## 4. Química cuántica
- Modo de ejecución: full
- xTB terminados/minimos: 18 / 18
- ORCA terminados/mínimos: 18 / 18
- Registros quantum_calculation en MySQL: 54
- Registros quantum_property en MySQL: 666

## 5. Machine Learning
- Mejor combinación HHV por RMSE OOF: ElasticNet / ultimate
- Nivel de interpretación: exploratory. Bases de medida: dry_basis | unknown.
- n=21, MAE=0.582 MJ/kg, RMSE=0.798 MJ/kg, R²=0.902.
- Y-scrambling (Ridge nested GroupCV, prueba independiente de señal): p=0.0050.
- Targets moleculares con modelo ejecutado: 0

## 6. Red y optimización
- Aristas moleculares: 82
- Rutas biomasa→combustible: 55
- Soluciones Pareto: 2

## 7. Limitaciones que deben declararse
- Las moléculas sin SMILES no pueden entrar en RDKit/xTB/ORCA hasta que su estructura se documente con una fuente fiable.
- Muchos targets de combustible siguen teniendo pocas moléculas: los modelos de bajo n son exploratorios y no equivalen a validación externa.
- HOMO/LUMO y energías dependen del nivel teórico; no son observables experimentales exactos.
- Las frecuencias imaginarias se usan como control de mínimo; un cálculo `completed_nonminimum` no debe usarse como geometría de equilibrio definitiva.
- No se multiplican rendimientos cuya unidad o base no sean comparables.
- El modelo HHV es exploratorio si mezcla bases de medida desconocidas/no homogéneas o si el tamaño muestral es <30.