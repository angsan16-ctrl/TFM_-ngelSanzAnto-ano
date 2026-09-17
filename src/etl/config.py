from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


@dataclass(frozen=True)
class SheetConfig:
    sheet: str
    table: str
    columns: tuple[str, ...]
    pk: str
    required: frozenset[str] = field(default_factory=frozenset)
    integer_columns: frozenset[str] = field(default_factory=frozenset)
    float_columns: frozenset[str] = field(default_factory=frozenset)
    date_columns: frozenset[str] = field(default_factory=frozenset)
    datetime_columns: frozenset[str] = field(default_factory=frozenset)
    percent_columns: frozenset[str] = field(default_factory=frozenset)
    foreign_keys: Mapping[str, tuple[str, str]] = field(default_factory=dict)


SHEET_CONFIGS: dict[str, SheetConfig] = {
    "01_Sources": SheetConfig(
        sheet="01_Sources", table="source",
        columns=("source_id", "source_type", "title", "authors", "journal_or_org", "year", "doi", "url", "access_date", "license_notes", "peer_reviewed", "evidence_quality", "primary_or_secondary", "notes"),
        pk="source_id",
        required=frozenset({"source_id", "source_type", "title"}),
        integer_columns=frozenset({"source_id", "year"}),
        date_columns=frozenset({"access_date"}),
    ),
    "02_Biomass": SheetConfig(
        sheet="02_Biomass", table="biomass",
        columns=("biomass_id", "common_name", "scientific_name", "species", "genus", "family", "biomass_category", "residue_type", "plant_part", "country", "region", "origin_notes", "description", "created_at"),
        pk="biomass_id",
        required=frozenset({"biomass_id", "common_name", "biomass_category", "residue_type"}),
        integer_columns=frozenset({"biomass_id"}),
        datetime_columns=frozenset({"created_at"}),
    ),
    "03_Composition": SheetConfig(
        sheet="03_Composition", table="biomass_composition",
        columns=("composition_id", "biomass_id", "source_id", "sample_label", "measurement_basis", "analytical_method", "cellulose_pct", "hemicellulose_pct", "lignin_total_pct", "acid_insoluble_lignin_pct", "acid_soluble_lignin_pct", "glucan_pct", "xylan_pct", "arabinan_pct", "mannan_pct", "galactan_pct", "extractives_pct", "ash_pct", "moisture_pct", "protein_pct", "lipids_pct", "starch_pct", "pectin_pct", "volatile_matter_pct", "fixed_carbon_pct", "carbon_pct", "hydrogen_pct", "oxygen_pct", "nitrogen_pct", "sulfur_pct", "chlorine_pct", "hhv_value", "hhv_unit", "lhv_value", "lhv_unit", "uncertainty_text", "n_replicates", "country", "region", "page_table_figure", "notes"),
        pk="composition_id",
        required=frozenset({"composition_id", "biomass_id", "source_id", "sample_label", "measurement_basis"}),
        integer_columns=frozenset({"composition_id", "biomass_id", "source_id", "n_replicates"}),
        float_columns=frozenset({"cellulose_pct", "hemicellulose_pct", "lignin_total_pct", "acid_insoluble_lignin_pct", "acid_soluble_lignin_pct", "glucan_pct", "xylan_pct", "arabinan_pct", "mannan_pct", "galactan_pct", "extractives_pct", "ash_pct", "moisture_pct", "protein_pct", "lipids_pct", "starch_pct", "pectin_pct", "volatile_matter_pct", "fixed_carbon_pct", "carbon_pct", "hydrogen_pct", "oxygen_pct", "nitrogen_pct", "sulfur_pct", "chlorine_pct", "hhv_value", "lhv_value"}),
        percent_columns=frozenset({"cellulose_pct", "hemicellulose_pct", "lignin_total_pct", "acid_insoluble_lignin_pct", "acid_soluble_lignin_pct", "glucan_pct", "xylan_pct", "arabinan_pct", "mannan_pct", "galactan_pct", "extractives_pct", "ash_pct", "moisture_pct", "protein_pct", "lipids_pct", "starch_pct", "pectin_pct", "volatile_matter_pct", "fixed_carbon_pct", "carbon_pct", "hydrogen_pct", "oxygen_pct", "nitrogen_pct", "sulfur_pct", "chlorine_pct"}),
        foreign_keys={"biomass_id": ("02_Biomass", "biomass_id"), "source_id": ("01_Sources", "source_id")},
    ),
    "04_Molecules": SheetConfig(
        sheet="04_Molecules", table="molecule",
        columns=("molecule_id", "preferred_name", "synonyms", "canonical_smiles", "inchi", "inchikey", "cas_number", "molecular_formula", "charge", "multiplicity", "molecule_role", "renewable_origin", "notes"),
        pk="molecule_id",
        required=frozenset({"molecule_id", "preferred_name", "molecule_role"}),
        integer_columns=frozenset({"molecule_id", "charge", "multiplicity"}),
    ),
    "05_Biomass_Molecule": SheetConfig(
        sheet="05_Biomass_Molecule", table="biomass_molecule",
        columns=("biomass_molecule_id", "biomass_id", "molecule_id", "source_id", "fraction_origin", "conversion_process", "reported_yield", "yield_unit", "temperature_c", "pressure_bar", "reaction_time_h", "evidence_level", "page_table_figure", "notes"),
        pk="biomass_molecule_id",
        required=frozenset({"biomass_molecule_id", "biomass_id", "molecule_id", "source_id", "fraction_origin", "conversion_process"}),
        integer_columns=frozenset({"biomass_molecule_id", "biomass_id", "molecule_id", "source_id"}),
        float_columns=frozenset({"reported_yield", "temperature_c", "pressure_bar", "reaction_time_h"}),
        foreign_keys={"biomass_id": ("02_Biomass", "biomass_id"), "molecule_id": ("04_Molecules", "molecule_id"), "source_id": ("01_Sources", "source_id")},
    ),
    "06_Reactions": SheetConfig(
        sheet="06_Reactions", table="reaction",
        columns=("reaction_id", "source_id", "reaction_name", "reaction_class", "temperature_c", "pressure_bar", "reaction_time_h", "catalyst_text", "solvent_text", "conversion_pct", "selectivity_pct", "yield_pct", "yield_basis", "h2_consumption", "h2_unit", "trl", "reactor_type", "page_table_figure", "notes"),
        pk="reaction_id",
        required=frozenset({"reaction_id", "source_id", "reaction_name", "reaction_class"}),
        integer_columns=frozenset({"reaction_id", "source_id", "trl"}),
        float_columns=frozenset({"temperature_c", "pressure_bar", "reaction_time_h", "conversion_pct", "selectivity_pct", "yield_pct", "h2_consumption"}),
        percent_columns=frozenset({"conversion_pct", "selectivity_pct", "yield_pct"}),
        foreign_keys={"source_id": ("01_Sources", "source_id")},
    ),
    "07_Reaction_Participants": SheetConfig(
        sheet="07_Reaction_Participants", table="reaction_participant",
        columns=("participant_id", "reaction_id", "molecule_id", "participant_role", "stoichiometric_coefficient", "notes"),
        pk="participant_id",
        required=frozenset({"participant_id", "reaction_id", "molecule_id", "participant_role"}),
        integer_columns=frozenset({"participant_id", "reaction_id", "molecule_id"}),
        float_columns=frozenset({"stoichiometric_coefficient"}),
        foreign_keys={"reaction_id": ("06_Reactions", "reaction_id"), "molecule_id": ("04_Molecules", "molecule_id")},
    ),
    "08_Fuel_Properties": SheetConfig(
        sheet="08_Fuel_Properties", table="fuel_property",
        columns=("fuel_property_id", "molecule_id", "source_id", "property_name", "value", "unit", "temperature_c", "pressure_bar", "uncertainty", "measurement_method", "value_origin", "page_table_figure", "notes"),
        pk="fuel_property_id",
        required=frozenset({"fuel_property_id", "molecule_id", "source_id", "property_name", "value", "value_origin"}),
        integer_columns=frozenset({"fuel_property_id", "molecule_id", "source_id"}),
        float_columns=frozenset({"value", "temperature_c", "pressure_bar"}),
        foreign_keys={"molecule_id": ("04_Molecules", "molecule_id"), "source_id": ("01_Sources", "source_id")},
    ),
    "09_Descriptors": SheetConfig(
        sheet="09_Descriptors", table="molecular_descriptor",
        columns=("descriptor_id", "molecule_id", "descriptor_name", "descriptor_value", "unit", "software", "software_version", "calculation_date", "config_hash", "notes"),
        pk="descriptor_id",
        required=frozenset({"descriptor_id", "molecule_id", "descriptor_name", "descriptor_value"}),
        integer_columns=frozenset({"descriptor_id", "molecule_id"}),
        float_columns=frozenset({"descriptor_value"}),
        date_columns=frozenset({"calculation_date"}),
        foreign_keys={"molecule_id": ("04_Molecules", "molecule_id")},
    ),
    "10_Quantum_Calc": SheetConfig(
        sheet="10_Quantum_Calc", table="quantum_calculation",
        columns=("calculation_id", "molecule_id", "conformer_id", "software", "software_version", "method", "basis_set", "dispersion_correction", "solvent_model", "charge", "multiplicity", "status", "started_at", "finished_at", "input_path", "output_path", "geometry_path", "file_hash", "runtime_seconds", "hardware_notes"),
        pk="calculation_id",
        required=frozenset({"calculation_id", "molecule_id", "software", "status"}),
        integer_columns=frozenset({"calculation_id", "molecule_id", "conformer_id", "charge", "multiplicity"}),
        float_columns=frozenset({"runtime_seconds"}),
        datetime_columns=frozenset({"started_at", "finished_at"}),
        foreign_keys={"molecule_id": ("04_Molecules", "molecule_id")},
    ),
    "11_Quantum_Properties": SheetConfig(
        sheet="11_Quantum_Properties", table="quantum_property",
        columns=("quantum_property_id", "calculation_id", "property_name", "value", "unit", "notes"),
        pk="quantum_property_id",
        required=frozenset({"quantum_property_id", "calculation_id", "property_name", "value"}),
        integer_columns=frozenset({"quantum_property_id", "calculation_id"}),
        float_columns=frozenset({"value"}),
        foreign_keys={"calculation_id": ("10_Quantum_Calc", "calculation_id")},
    ),
}

LOAD_ORDER = (
    "01_Sources",
    "02_Biomass",
    "03_Composition",
    "04_Molecules",
    "05_Biomass_Molecule",
    "06_Reactions",
    "07_Reaction_Participants",
    "08_Fuel_Properties",
    "09_Descriptors",
    "10_Quantum_Calc",
    "11_Quantum_Properties",
)

REVERSE_LOAD_ORDER = tuple(reversed(LOAD_ORDER))
TABLE_TO_SHEET = {cfg.table: sheet for sheet, cfg in SHEET_CONFIGS.items()}
EXPECTED_TABLES = tuple(cfg.table for cfg in SHEET_CONFIGS.values())
