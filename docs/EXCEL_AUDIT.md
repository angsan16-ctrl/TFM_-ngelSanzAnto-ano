# Auditoría del Excel fuente de verdad

Archivo auditado: `data/plantilla.xlsx`

## Resultado ejecutivo

Los detalles por columna (tipo aparente, nulos, no nulos, cardinalidad y longitud máxima) están en `docs/COLUMN_AUDIT.csv`. La matriz de claves foráneas auditadas está en `docs/FK_AUDIT.csv`.

- 17 hojas detectadas: 11 hojas de datos y 6 hojas documentales/auxiliares.
- 11 tablas SQL propuestas, mapeadas 1:1 con las hojas de datos.
- No se detectaron claves primarias duplicadas ni nulas en las hojas con filas.
- No se detectaron claves foráneas rotas en las relaciones previstas.
- DOI duplicados: 0.
- InChIKey duplicados: 0.
- Filas completamente duplicadas: 0 en todas las hojas de datos.
- Valores porcentuales fuera de 0–100: 0.
- Valores TRL fuera de 1–9: 0; actualmente la columna `trl` está completamente vacía.
- No se detectaron números almacenados como texto en las columnas numéricas inspeccionadas.
- Se detectaron 25 celdas de texto con espacios iniciales/finales, todas en `06_Reactions.notes`; el ETL aplica `strip()` sin cambiar el contenido científico.
- `access_date` y `created_at` aparecen en la representación cruda como serial Excel `46280`, equivalente a 2026-09-15; el ETL acepta tanto serial Excel como fechas/datetimes.
- En `08_Fuel_Properties`, la propiedad `density` usa dos unidades válidamente separadas por la columna `unit`: 7 filas `kg/m3` y 4 filas `g/cm3`. No se realiza conversión automática.
- Las hojas `09_Descriptors`, `10_Quantum_Calc` y `11_Quantum_Properties` tienen cabeceras pero 0 filas. Se crean sus tablas para la fase futura, sin inventar datos.

## Clasificación de hojas

| Hoja | Tipo | Filas de datos | Columnas | Tabla MySQL |
|---|---:|---:|---:|---|
| 00_README | auxiliar | 15 filas usadas | 8 | no importar |
| 01_Source_Catalog | auxiliar | 7 filas usadas | 8 | no importar |
| 01_Sources | datos | 92 | 14 | source |
| 02_Biomass | datos | 182 | 14 | biomass |
| 03_Composition | datos | 305 | 41 | biomass_composition |
| 04_Molecules | datos | 170 | 13 | molecule |
| 05_Biomass_Molecule | datos | 13 | 14 | biomass_molecule |
| 06_Reactions | datos | 82 | 19 | reaction |
| 07_Reaction_Participants | datos | 164 | 6 | reaction_participant |
| 08_Fuel_Properties | datos | 61 | 13 | fuel_property |
| 09_Descriptors | datos/futuro | 0 | 10 | molecular_descriptor |
| 10_Quantum_Calc | datos/futuro | 0 | 20 | quantum_calculation |
| 11_Quantum_Properties | datos/futuro | 0 | 6 | quantum_property |
| 12_Data_Dictionary | auxiliar | 12 filas usadas | 8 | no importar |
| 13_MySQL_Setup | auxiliar | 13 filas usadas | 4 | no importar |
| 14_Import_Order | auxiliar | 12 filas usadas | 5 | no importar |
| 15_Dashboard | auxiliar | 9 filas usadas | 6 | no importar |

## Claves primarias

Los IDs existentes son secuenciales y se conservan durante la carga:

| Hoja | PK | Rango existente | Duplicados | Nulos |
|---|---|---:|---:|---:|
| 01_Sources | source_id | 1–92 | 0 | 0 |
| 02_Biomass | biomass_id | 1–182 | 0 | 0 |
| 03_Composition | composition_id | 1–305 | 0 | 0 |
| 04_Molecules | molecule_id | 1–170 | 0 | 0 |
| 05_Biomass_Molecule | biomass_molecule_id | 1–13 | 0 | 0 |
| 06_Reactions | reaction_id | 1–82 | 0 | 0 |
| 07_Reaction_Participants | participant_id | 1–164 | 0 | 0 |
| 08_Fuel_Properties | fuel_property_id | 1–61 | 0 | 0 |
| 09_Descriptors | descriptor_id | sin filas | — | — |
| 10_Quantum_Calc | calculation_id | sin filas | — | — |
| 11_Quantum_Properties | quantum_property_id | sin filas | — | — |

## Integridad referencial comprobada

Todas estas relaciones tienen 0 referencias rotas en el Excel actual:

- `biomass_composition.biomass_id -> biomass.biomass_id`
- `biomass_composition.source_id -> source.source_id`
- `biomass_molecule.biomass_id -> biomass.biomass_id`
- `biomass_molecule.molecule_id -> molecule.molecule_id`
- `biomass_molecule.source_id -> source.source_id`
- `reaction.source_id -> source.source_id`
- `reaction_participant.reaction_id -> reaction.reaction_id`
- `reaction_participant.molecule_id -> molecule.molecule_id`
- `fuel_property.molecule_id -> molecule.molecule_id`
- `fuel_property.source_id -> source.source_id`
- `molecular_descriptor.molecule_id -> molecule.molecule_id` (sin filas actualmente)
- `quantum_calculation.molecule_id -> molecule.molecule_id` (sin filas actualmente)
- `quantum_property.calculation_id -> quantum_calculation.calculation_id` (sin filas actualmente)

## Columnas completamente vacías en hojas con datos

- `02_Biomass`: `scientific_name`, `species`, `genus`, `family`, `country`, `region`, `origin_notes`.
- `03_Composition`: `chlorine_pct`.
- `04_Molecules`: `multiplicity`.
- `05_Biomass_Molecule`: `pressure_bar`.
- `06_Reactions`: `yield_basis`, `h2_consumption`, `h2_unit`, `trl`.
- `07_Reaction_Participants`: `stoichiometric_coefficient`.
- `08_Fuel_Properties`: `pressure_bar`.

Estas columnas se conservan en el esquema porque forman parte del diseño científico del Excel y son útiles para futuras cargas; no se rellenan artificialmente.

## Observaciones de modelado

1. `reaction_name` se repite deliberadamente entre experimentos/condiciones. No se trata como clave única: hay 4 nombres repetidos y cada fila mantiene su `reaction_id`, `source_id` y condiciones.
2. En `04_Molecules`, la mayoría de moléculas todavía no tiene `canonical_smiles`; esto no invalida el catálogo. La consulta `get_rdkit_input()` selecciona solo filas con SMILES disponible.
3. `reported_yield` en `05_Biomass_Molecule` puede expresarse en `%` o `g/L`; por ello se guarda como `DOUBLE` con unidad separada y no se aplica un CHECK universal 0–100.
4. Los porcentajes de composición y los porcentajes de reacción sí reciben restricciones 0–100.
5. Los outputs grandes de xTB/ORCA no se almacenan en MySQL; `quantum_calculation` guarda rutas, hash y metadatos, tal como define el Excel.
6. No se realizó ninguna búsqueda externa ni sustitución de valores. Esta auditoría se basa exclusivamente en el Excel adjunto.
