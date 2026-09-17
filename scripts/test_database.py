from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from sqlalchemy import text

from src.db.connection import engine
from src.etl.config import EXPECTED_TABLES, LOAD_ORDER, SHEET_CONFIGS


ORPHAN_CHECKS = {
    "composition->biomass": "SELECT COUNT(*) FROM biomass_composition c LEFT JOIN biomass b ON c.biomass_id=b.biomass_id WHERE b.biomass_id IS NULL",
    "composition->source": "SELECT COUNT(*) FROM biomass_composition c LEFT JOIN source s ON c.source_id=s.source_id WHERE s.source_id IS NULL",
    "biomass_molecule->biomass": "SELECT COUNT(*) FROM biomass_molecule bm LEFT JOIN biomass b ON bm.biomass_id=b.biomass_id WHERE b.biomass_id IS NULL",
    "biomass_molecule->molecule": "SELECT COUNT(*) FROM biomass_molecule bm LEFT JOIN molecule m ON bm.molecule_id=m.molecule_id WHERE m.molecule_id IS NULL",
    "biomass_molecule->source": "SELECT COUNT(*) FROM biomass_molecule bm LEFT JOIN source s ON bm.source_id=s.source_id WHERE s.source_id IS NULL",
    "reaction->source": "SELECT COUNT(*) FROM reaction r LEFT JOIN source s ON r.source_id=s.source_id WHERE s.source_id IS NULL",
    "participant->reaction": "SELECT COUNT(*) FROM reaction_participant rp LEFT JOIN reaction r ON rp.reaction_id=r.reaction_id WHERE r.reaction_id IS NULL",
    "participant->molecule": "SELECT COUNT(*) FROM reaction_participant rp LEFT JOIN molecule m ON rp.molecule_id=m.molecule_id WHERE m.molecule_id IS NULL",
    "fuel_property->molecule": "SELECT COUNT(*) FROM fuel_property fp LEFT JOIN molecule m ON fp.molecule_id=m.molecule_id WHERE m.molecule_id IS NULL",
    "fuel_property->source": "SELECT COUNT(*) FROM fuel_property fp LEFT JOIN source s ON fp.source_id=s.source_id WHERE s.source_id IS NULL",
    "descriptor->molecule": "SELECT COUNT(*) FROM molecular_descriptor d LEFT JOIN molecule m ON d.molecule_id=m.molecule_id WHERE m.molecule_id IS NULL",
    "quantum_calculation->molecule": "SELECT COUNT(*) FROM quantum_calculation q LEFT JOIN molecule m ON q.molecule_id=m.molecule_id WHERE m.molecule_id IS NULL",
    "quantum_property->calculation": "SELECT COUNT(*) FROM quantum_property qp LEFT JOIN quantum_calculation qc ON qp.calculation_id=qc.calculation_id WHERE qc.calculation_id IS NULL",
}

PERCENTAGE_CHECKS = {
    "biomass_composition": (
        "cellulose_pct", "hemicellulose_pct", "lignin_total_pct", "acid_insoluble_lignin_pct",
        "acid_soluble_lignin_pct", "glucan_pct", "xylan_pct", "arabinan_pct", "mannan_pct",
        "galactan_pct", "extractives_pct", "ash_pct", "moisture_pct", "protein_pct", "lipids_pct",
        "starch_pct", "pectin_pct", "volatile_matter_pct", "fixed_carbon_pct", "carbon_pct",
        "hydrogen_pct", "oxygen_pct", "nitrogen_pct", "sulfur_pct", "chlorine_pct"
    ),
    "reaction": ("conversion_pct", "selectivity_pct", "yield_pct"),
}


def excel_expected_counts() -> dict[str, int]:
    excel = PROJECT_ROOT / "data" / "plantilla.xlsx"
    counts: dict[str, int] = {}
    for sheet in LOAD_ORDER:
        cfg = SHEET_CONFIGS[sheet]
        df = pd.read_excel(excel, sheet_name=sheet, usecols=[cfg.pk], engine="openpyxl")
        counts[cfg.table] = int(df[cfg.pk].notna().sum())
    return counts


def ok(message: str) -> None:
    print(f"[OK] {message}")


def fail(message: str, failures: list[str]) -> None:
    print(f"[FAIL] {message}")
    failures.append(message)


def main() -> int:
    failures: list[str] = []
    print("========================================")
    print("SAF DATABASE TEST")
    print("========================================")

    expected_counts = excel_expected_counts()

    try:
        with engine.connect() as conn:
            one = conn.execute(text("SELECT 1")).scalar_one()
            if one == 1:
                ok("MySQL connection / SELECT 1")
            else:
                fail("SELECT 1 did not return 1", failures)

            db = conn.execute(text("SELECT DATABASE()" )).scalar_one()
            if db == "saf_biomass":
                ok("Database saf_biomass")
            else:
                fail(f"Connected database is {db!r}, expected 'saf_biomass'", failures)

            rows = conn.execute(text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = DATABASE() AND table_type='BASE TABLE'"
            )).scalars().all()
            found = set(rows)
            missing = [t for t in EXPECTED_TABLES if t not in found]
            if not missing:
                ok(f"{len(EXPECTED_TABLES)} expected tables detected")
            else:
                fail(f"Missing tables: {missing}", failures)

            for table in EXPECTED_TABLES:
                if table not in found:
                    continue
                count = int(conn.execute(text(f"SELECT COUNT(*) FROM `{table}`")).scalar_one())
                expected = expected_counts[table]
                if count == expected:
                    ok(f"{table}: {count} rows (matches Excel)")
                else:
                    fail(f"{table}: {count} rows, Excel expects {expected}", failures)

            orphan_total = 0
            for label, sql in ORPHAN_CHECKS.items():
                orphan_total += int(conn.execute(text(sql)).scalar_one())
            if orphan_total == 0:
                ok("foreign keys / orphan checks = 0")
            else:
                fail(f"orphan foreign keys detected: {orphan_total}", failures)

            dup_doi = int(conn.execute(text(
                "SELECT COUNT(*) FROM (SELECT LOWER(TRIM(doi)) d FROM source "
                "WHERE doi IS NOT NULL GROUP BY LOWER(TRIM(doi)) HAVING COUNT(*) > 1) x"
            )).scalar_one())
            if dup_doi == 0:
                ok("duplicated DOI = 0")
            else:
                fail(f"duplicated DOI groups = {dup_doi}", failures)

            dup_ik = int(conn.execute(text(
                "SELECT COUNT(*) FROM (SELECT UPPER(TRIM(inchikey)) i FROM molecule "
                "WHERE inchikey IS NOT NULL GROUP BY UPPER(TRIM(inchikey)) HAVING COUNT(*) > 1) x"
            )).scalar_one())
            if dup_ik == 0:
                ok("duplicated InChIKey = 0")
            else:
                fail(f"duplicated InChIKey groups = {dup_ik}", failures)

            null_pk_total = 0
            for sheet in LOAD_ORDER:
                cfg = SHEET_CONFIGS[sheet]
                null_pk_total += int(conn.execute(text(
                    f"SELECT COUNT(*) FROM `{cfg.table}` WHERE `{cfg.pk}` IS NULL"
                )).scalar_one())
            if null_pk_total == 0:
                ok("null primary IDs = 0")
            else:
                fail(f"null primary IDs = {null_pk_total}", failures)

            bad_percentages = 0
            for table, columns in PERCENTAGE_CHECKS.items():
                predicate = " OR ".join(f"(`{c}` < 0 OR `{c}` > 100)" for c in columns)
                bad_percentages += int(conn.execute(text(
                    f"SELECT COUNT(*) FROM `{table}` WHERE {predicate}"
                )).scalar_one())
            if bad_percentages == 0:
                ok("percentages outside [0,100] = 0")
            else:
                fail(f"invalid percentage rows = {bad_percentages}", failures)

            bad_trl = int(conn.execute(text(
                "SELECT COUNT(*) FROM reaction WHERE trl IS NOT NULL AND (trl < 1 OR trl > 9)"
            )).scalar_one())
            if bad_trl == 0:
                ok("TRL outside [1,9] = 0")
            else:
                fail(f"invalid TRL rows = {bad_trl}", failures)

        join_df = pd.read_sql(text(
            """
            SELECT b.common_name, b.scientific_name, c.cellulose_pct, c.hemicellulose_pct,
                   c.lignin_total_pct, c.extractives_pct, c.ash_pct, s.title, s.doi
            FROM biomass_composition c
            JOIN biomass b ON c.biomass_id = b.biomass_id
            JOIN source s ON c.source_id = s.source_id
            ORDER BY c.composition_id
            LIMIT 5
            """
        ), engine)
        if not join_df.empty:
            ok("biomass-composition-source JOIN")
            ok("pandas read_sql")
        else:
            fail("scientific JOIN returned no rows", failures)

    except Exception as exc:
        fail(f"database test raised: {exc}", failures)

    print("----------------------------------------")
    if failures:
        print(f"DATABASE NOT READY ({len(failures)} failures)")
        return 1
    print("DATABASE READY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
