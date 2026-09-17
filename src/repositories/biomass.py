from __future__ import annotations
from src.db.queries import get_all_biomass, get_biomass_by_id, get_biomass_composition

list_all = get_all_biomass
by_id = get_biomass_by_id
composition = get_biomass_composition
