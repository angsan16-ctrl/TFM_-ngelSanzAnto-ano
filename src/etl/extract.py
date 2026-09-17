from __future__ import annotations

from pathlib import Path
import logging

import pandas as pd

from .config import LOAD_ORDER, SHEET_CONFIGS

logger = logging.getLogger(__name__)


def _read_sheet(excel_path: Path, sheet_name: str) -> pd.DataFrame:
    cfg = SHEET_CONFIGS[sheet_name]
    df = pd.read_excel(
        excel_path,
        sheet_name=sheet_name,
        dtype=object,
        engine="openpyxl",
        keep_default_na=False,
        na_filter=False,
    )
    actual = tuple(str(c).strip() for c in df.columns)
    if actual != cfg.columns:
        missing = [c for c in cfg.columns if c not in actual]
        unexpected = [c for c in actual if c not in cfg.columns]
        raise ValueError(
            f"Columnas inesperadas en {sheet_name}. "
            f"Faltan={missing}; sobran={unexpected}; orden_actual={actual}"
        )
    df.columns = list(cfg.columns)
    df.insert(0, "_excel_row", range(2, len(df) + 2))
    logger.info("table=%s extracted=%d", cfg.table, len(df))
    return df


def extract_workbook(excel_path: str | Path) -> dict[str, pd.DataFrame]:
    excel_path = Path(excel_path).resolve()
    if not excel_path.exists():
        raise FileNotFoundError(f"No existe el Excel: {excel_path}")

    available = set(pd.ExcelFile(excel_path, engine="openpyxl").sheet_names)
    missing_sheets = [s for s in LOAD_ORDER if s not in available]
    if missing_sheets:
        raise ValueError(f"Faltan hojas obligatorias: {missing_sheets}")

    return {sheet: _read_sheet(excel_path, sheet) for sheet in LOAD_ORDER}
