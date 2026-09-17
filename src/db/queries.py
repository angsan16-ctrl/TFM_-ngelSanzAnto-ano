from __future__ import annotations

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from .connection import engine as default_engine


def _read(sql: str, params: dict | None = None, engine: Engine = default_engine) -> pd.DataFrame:
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params or {})


def get_all_biomass(engine: Engine = default_engine) -> pd.DataFrame:
    return _read("SELECT * FROM biomass ORDER BY biomass_id", engine=engine)


def get_biomass_by_id(biomass_id: int, engine: Engine = default_engine) -> pd.DataFrame:
    return _read(
        "SELECT * FROM biomass WHERE biomass_id = :biomass_id",
        {"biomass_id": biomass_id},
        engine,
    )


def get_biomass_composition(biomass_id: int | None = None, engine: Engine = default_engine) -> pd.DataFrame:
    if biomass_id is None:
        return _read("SELECT * FROM biomass_composition ORDER BY composition_id", engine=engine)
    return _read(
        "SELECT * FROM biomass_composition WHERE biomass_id = :biomass_id ORDER BY composition_id",
        {"biomass_id": biomass_id},
        engine,
    )


def get_molecules(engine: Engine = default_engine) -> pd.DataFrame:
    return _read("SELECT * FROM molecule ORDER BY molecule_id", engine=engine)


def get_molecule_by_inchikey(inchikey: str, engine: Engine = default_engine) -> pd.DataFrame:
    return _read(
        "SELECT * FROM molecule WHERE inchikey = :inchikey",
        {"inchikey": inchikey},
        engine,
    )


def get_reactions(engine: Engine = default_engine) -> pd.DataFrame:
    return _read("SELECT * FROM reaction ORDER BY reaction_id", engine=engine)


def get_reactions_for_molecule(molecule_id: int, engine: Engine = default_engine) -> pd.DataFrame:
    return _read(
        """
        SELECT DISTINCT r.*
        FROM reaction r
        JOIN reaction_participant rp ON rp.reaction_id = r.reaction_id
        WHERE rp.molecule_id = :molecule_id
        ORDER BY r.reaction_id
        """,
        {"molecule_id": molecule_id},
        engine,
    )


def get_fuel_properties(molecule_id: int | None = None, engine: Engine = default_engine) -> pd.DataFrame:
    if molecule_id is None:
        return _read("SELECT * FROM fuel_property ORDER BY fuel_property_id", engine=engine)
    return _read(
        "SELECT * FROM fuel_property WHERE molecule_id = :molecule_id ORDER BY fuel_property_id",
        {"molecule_id": molecule_id},
        engine,
    )


def get_biomass_composition_with_source(engine: Engine = default_engine) -> pd.DataFrame:
    return _read(
        """
        SELECT
            b.common_name,
            b.scientific_name,
            c.cellulose_pct,
            c.hemicellulose_pct,
            c.lignin_total_pct,
            c.extractives_pct,
            c.ash_pct,
            s.title,
            s.doi
        FROM biomass_composition c
        JOIN biomass b ON c.biomass_id = b.biomass_id
        JOIN source s ON c.source_id = s.source_id
        ORDER BY c.composition_id
        """,
        engine=engine,
    )


def get_rdkit_input(engine: Engine = default_engine) -> pd.DataFrame:
    return _read(
        """
        SELECT molecule_id, canonical_smiles
        FROM molecule
        WHERE canonical_smiles IS NOT NULL
          AND TRIM(canonical_smiles) <> ''
        ORDER BY molecule_id
        """,
        engine=engine,
    )
