from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from numbers import Integral, Real
import logging

import pandas as pd

from .config import LOAD_ORDER, SHEET_CONFIGS
from .transform import TransformIssue, TransformResult

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    valid_frames: dict[str, pd.DataFrame]
    rejected_frames: dict[str, pd.DataFrame]
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def rejected_count(self) -> int:
        return sum(len(df) for df in self.rejected_frames.values())

    @property
    def ok(self) -> bool:
        return self.rejected_count == 0 and not self.errors


def _is_null(value: Any) -> bool:
    if value is None or value is pd.NA:
        return True
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def _add_reason(reasons: dict[int, list[str]], excel_row: int, reason: str) -> None:
    bucket = reasons.setdefault(int(excel_row), [])
    if reason not in bucket:
        bucket.append(reason)


def _duplicate_rows_casefold(df: pd.DataFrame, column: str) -> set[int]:
    normalized = df[column].map(
        lambda v: None if _is_null(v) else str(v).strip().casefold()
    )
    mask = normalized.notna() & normalized.duplicated(keep=False)
    return set(df.loc[mask, "_excel_row"].astype(int).tolist())


def _intrinsic_reasons(sheet: str, df: pd.DataFrame, issues: list[TransformIssue]) -> dict[int, list[str]]:
    cfg = SHEET_CONFIGS[sheet]
    reasons: dict[int, list[str]] = {}

    for issue in issues:
        if issue.sheet == sheet:
            _add_reason(reasons, issue.excel_row, f"{issue.reason}:{issue.column}")

    for _, row in df.iterrows():
        excel_row = int(row["_excel_row"])
        for column in cfg.required:
            if _is_null(row[column]):
                _add_reason(reasons, excel_row, f"required_value_missing:{column}")

        for column in cfg.integer_columns:
            value = row[column]
            if not _is_null(value) and not isinstance(value, Integral):
                _add_reason(reasons, excel_row, f"invalid_integer:{column}")
            elif column.endswith("_id") and not _is_null(value) and value <= 0:
                _add_reason(reasons, excel_row, f"invalid_unsigned_id:{column}")

        for column in cfg.percent_columns:
            value = row[column]
            if _is_null(value):
                continue
            if not isinstance(value, Real):
                _add_reason(reasons, excel_row, f"invalid_numeric_value:{column}")
            elif not (0 <= float(value) <= 100):
                _add_reason(reasons, excel_row, f"invalid_percentage:{column}")

    if cfg.pk in df.columns:
        pk_non_null = df.loc[df[cfg.pk].notna(), ["_excel_row", cfg.pk]]
        duplicate_mask = pk_non_null[cfg.pk].duplicated(keep=False)
        for excel_row in pk_non_null.loc[duplicate_mask, "_excel_row"]:
            _add_reason(reasons, int(excel_row), "duplicate_primary_key")
        for _, row in pk_non_null.iterrows():
            value = row[cfg.pk]
            if isinstance(value, Integral) and value <= 0:
                _add_reason(reasons, int(row["_excel_row"]), f"invalid_unsigned_id:{cfg.pk}")

    if sheet == "01_Sources":
        for excel_row in _duplicate_rows_casefold(df, "doi"):
            _add_reason(reasons, excel_row, "duplicate_doi")

    if sheet == "04_Molecules":
        for excel_row in _duplicate_rows_casefold(df, "inchikey"):
            _add_reason(reasons, excel_row, "duplicate_inchikey")
        for _, row in df.iterrows():
            value = row["multiplicity"]
            if not _is_null(value) and isinstance(value, Integral) and value < 1:
                _add_reason(reasons, int(row["_excel_row"]), "invalid_multiplicity")

    if sheet == "03_Composition":
        for _, row in df.iterrows():
            n = row["n_replicates"]
            if not _is_null(n) and isinstance(n, Integral) and n <= 0:
                _add_reason(reasons, int(row["_excel_row"]), "invalid_n_replicates")
            for value_col, unit_col in (("hhv_value", "hhv_unit"), ("lhv_value", "lhv_unit")):
                if _is_null(row[value_col]) != _is_null(row[unit_col]):
                    _add_reason(reasons, int(row["_excel_row"]), f"value_unit_mismatch:{value_col}/{unit_col}")

    if sheet == "05_Biomass_Molecule":
        for _, row in df.iterrows():
            if _is_null(row["reported_yield"]) != _is_null(row["yield_unit"]):
                _add_reason(reasons, int(row["_excel_row"]), "value_unit_mismatch:reported_yield/yield_unit")

    if sheet == "06_Reactions":
        for _, row in df.iterrows():
            trl = row["trl"]
            if not _is_null(trl) and (not isinstance(trl, Integral) or not 1 <= trl <= 9):
                _add_reason(reasons, int(row["_excel_row"]), "invalid_trl")
            if _is_null(row["h2_consumption"]) != _is_null(row["h2_unit"]):
                _add_reason(reasons, int(row["_excel_row"]), "value_unit_mismatch:h2_consumption/h2_unit")

    if sheet == "10_Quantum_Calc":
        for _, row in df.iterrows():
            multiplicity = row["multiplicity"]
            runtime = row["runtime_seconds"]
            if not _is_null(multiplicity) and isinstance(multiplicity, Integral) and multiplicity < 1:
                _add_reason(reasons, int(row["_excel_row"]), "invalid_multiplicity")
            if not _is_null(runtime) and isinstance(runtime, Real) and runtime < 0:
                _add_reason(reasons, int(row["_excel_row"]), "invalid_runtime_seconds")

    return reasons


def _make_rejected_raw(raw_df: pd.DataFrame, rejected_rows: dict[int, list[str]]) -> pd.DataFrame:
    if not rejected_rows:
        return pd.DataFrame(columns=[c for c in raw_df.columns if c != "_excel_row"] + ["error_reason"])
    rejected = raw_df[raw_df["_excel_row"].isin(rejected_rows)].copy()
    rejected["error_reason"] = rejected["_excel_row"].map(lambda r: ";".join(rejected_rows[int(r)]))
    return rejected.drop(columns=["_excel_row"])


def validate_workbook(
    raw_frames: dict[str, pd.DataFrame],
    transformed: TransformResult,
) -> ValidationResult:
    valid_frames: dict[str, pd.DataFrame] = {}
    rejected_frames: dict[str, pd.DataFrame] = {}
    errors: list[str] = []
    warnings: list[str] = []

    for sheet in LOAD_ORDER:
        cfg = SHEET_CONFIGS[sheet]
        df = transformed.frames[sheet]
        reasons = _intrinsic_reasons(sheet, df, transformed.issues)

        # Referencias contra las filas PADRE que ya han superado validación.
        for fk_column, (parent_sheet, parent_pk) in cfg.foreign_keys.items():
            parent_df = valid_frames.get(parent_sheet)
            if parent_df is None:
                raise RuntimeError(
                    f"Orden de validación inválido: {sheet}.{fk_column} depende de {parent_sheet}"
                )
            parent_ids = set(parent_df[parent_pk].dropna().tolist())
            for _, row in df.iterrows():
                excel_row = int(row["_excel_row"])
                value = row[fk_column]
                if _is_null(value):
                    continue
                if value not in parent_ids:
                    _add_reason(
                        reasons,
                        excel_row,
                        f"foreign_key_not_found:{fk_column}={value}->{SHEET_CONFIGS[parent_sheet].table}.{parent_pk}",
                    )

        rejected_rows = set(reasons)
        valid = df.loc[~df["_excel_row"].isin(rejected_rows)].copy()
        valid = valid.drop(columns=["_excel_row"])
        valid_frames[sheet] = valid
        rejected_frames[sheet] = _make_rejected_raw(raw_frames[sheet], reasons)

        logger.info(
            "table=%s processed=%d valid=%d rejected=%d",
            cfg.table,
            len(df),
            len(valid),
            len(rejected_frames[sheet]),
        )

        if rejected_rows:
            errors.append(f"{cfg.table}: {len(rejected_rows)} filas rechazadas")

    # Advertencias que no cambian ni invalidan datos científicos.
    molecule_df = transformed.frames["04_Molecules"]
    missing_smiles = int(molecule_df["canonical_smiles"].isna().sum())
    if missing_smiles:
        warnings.append(
            f"molecule: {missing_smiles} filas sin canonical_smiles; no podrán pasar directamente a RDKit hasta completarse en una fase posterior."
        )

    return ValidationResult(
        valid_frames=valid_frames,
        rejected_frames=rejected_frames,
        errors=errors,
        warnings=warnings,
    )


def write_rejected_csvs(result: ValidationResult, output_dir: str | Path) -> list[Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for sheet, rejected in result.rejected_frames.items():
        path = output_dir / f"{sheet}_rejected.csv"
        if rejected.empty:
            if path.exists():
                path.unlink()
            continue
        rejected.to_csv(path, index=False, encoding="utf-8-sig")
        written.append(path)
    return written
