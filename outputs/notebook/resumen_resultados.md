# Resumen automático — TFM SAF

Fecha de ejecución: 2026-09-16T22:49:13
Base: saf_biomass | MySQL 8.0.43 | Python 3.11.9

## Integridad y cobertura
- Fuentes: 96
- Biomasas: 183
- Mediciones de composición: 306
- Moléculas: 173
- Reacciones: 82
- Participantes de reacción: 164
- Propiedades de combustible: 64
- Fallos críticos de integridad: 0

## Cribado de biomasa
- Candidatos bioquímicos evaluables con objetivos completos: 16
- Alternativas no dominadas en el frente bioquímico: 8
- Muestras termoquímicas con HHV/ash/moisture comparables: 17

## Química molecular
- Moléculas con canonical_smiles: 18 de 173
- Descriptores RDKit calculados en esta ejecución: 162
- Conformeros 3D preparados: 18

## Machine Learning
- Modelo HHV con menor RMSE medio CV: ExtraTrees (RMSE medio 1.598 MJ/kg).
- El resultado es exploratorio por el tamaño muestral y la coexistencia de bases de medida declaradas/unknown.

## Red y optimización
- Aristas de reacción reconstruidas: 82
- Rutas biomasa→combustible enumeradas: 109
- Rutas Pareto no dominadas por par biomasa-combustible: 7

## Limitaciones explícitas
- Las moléculas sin SMILES no entran en RDKit.
- xTB/ORCA requieren instalación externa y ejecución deliberada; no se simulan resultados cuánticos.
- No se combinan rendimientos con unidades/bases incompatibles.
- Un frente de Pareto es una herramienta de cribado, no una afirmación de superioridad científica absoluta.