from __future__ import annotations
from src.db.queries import get_molecules, get_molecule_by_inchikey, get_fuel_properties, get_rdkit_input

list_all = get_molecules
by_inchikey = get_molecule_by_inchikey
fuel_properties = get_fuel_properties
rdkit_input = get_rdkit_input
