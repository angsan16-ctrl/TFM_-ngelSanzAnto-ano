# Anexo de interpretación estadística y computacional

## Validación del modelo HHV
- El modelo seleccionado se evaluó mediante predicciones out-of-fold con separación por biomass_id.
- RMSE OOF: 0.7981 MJ/kg; MAE OOF: 0.5821 MJ/kg; R² OOF: 0.9016.
- Baseline de media por fold: RMSE 2.7636 MJ/kg.
- Y-scrambling con reentrenamiento Ridge: p=0.004975 (n=200 permutaciones).
- Variables con mayor importancia por permutación en folds externos: carbon_pct, hydrogen_pct, nitrogen_pct, oxygen_pct, sulfur_pct.
## Energética de reacción
- Reacciones con ΔE electrónico completo: 0.
- Reacciones con ΔG(298 K) completo: 0.
## Criterios de interpretación
- Un p-valor no mide magnitud del efecto; se interpreta junto con tamaños de efecto e intervalos de incertidumbre.
- Un R² negativo en validación significa que el modelo generaliza peor que una predicción constante en esas particiones.
- Las propiedades cuánticas son dependientes del nivel teórico y deben compararse dentro del mismo método.
- El frente de Pareto no implica una única solución óptima; identifica alternativas no dominadas bajo los objetivos declarados.