from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from numbers import Integral, Real
from typing import Any
import logging
import math

import pandas as pd

from .config import LOAD_ORDER, SHEET_CONFIGS

logger = logging.getLogger(__name__)
EXCEL_EPOCH = datetime(1899, 12, 30)


@dataclass(frozen=True)
class TransformIssue:
    sheet: str
    excel_row: int
    column: str
    reason: str
    value: Any


@dataclass
class TransformResult:
    frames: dict[str, pd.DataFrame]
    issues: list[TransformIssue]
    blank_rows_removed: dict[str, int]


def _is_null(value: Any) -> bool:
    if value is None or value is pd.NA:
        return True
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def _normalize_scalar(value: Any) -> Any:
    if _is_null(value):
        return pd.NA
    if isinstance(value, str):
        stripped = value.strip()
        return pd.NA if stripped == "" else stripped
    return value


def _to_integer(value: Any) -> int:
    if isinstance(value, bool):
        raise ValueError("boolean_is_not_integer")
    if isinstance(value, Integral):
        return int(value)
    if isinstance(value, Real):
        numeric = float(value)
        if not math.isfinite(numeric) or not numeric.is_integer():
            raise ValueError("not_an_integer")
        return int(numeric)
    numeric = float(str(value).strip())
    if not math.isfinite(numeric) or not numeric.is_integer():
        raise ValueError("not_an_integer")
    return int(numeric)


def _to_float(value: Any) -> float:
    if isinstance(value, bool):
        raise ValueError("boolean_is_not_numeric")
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError("not_finite")
    return numeric


def _to_datetime(value: Any) -> datetime:
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime().replace(tzinfo=None)
    if isinstance(value, datetime):
        return value.replace(tzinfo=None)
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    if isinstance(value, Real) and not isinstance(value, bool):
        numeric = float(value)
        if not math.isfinite(numeric):
            raise ValueError("invalid_excel_serial_date")
        return EXCEL_EPOCH + timedelta(days=numeric)
    parsed = pd.to_datetime(str(value).strip(), errors="raise")
    if isinstance(parsed, pd.Timestamp):
        return parsed.to_pydatetime().replace(tzinfo=None)
    raise ValueError("invalid_date")


def _convert_column(
    df: pd.DataFrame,
    sheet: str,
    column: str,
    converter,
    issues: list[TransformIssue],
    as_date: bool = False,
) -> None:
    converted = []
    for _, row in df[["_excel_row", column]].iterrows():
        excel_row = int(row["_excel_row"])
        value = row[column]
        if _is_null(value):
            converted.append(pd.NA)
            continue
        try:
            result = converter(value)
            if as_date:
                result = result.date()
            converted.append(result)
        except Exception:
            issues.append(TransformIssue(sheet, excel_row, column, "invalid_type", value))
            converted.append(value)
    df[column] = converted


def transform_workbook(raw_frames: dict[str, pd.DataFrame]) -> TransformResult:
    frames: dict[str, pd.DataFrame] = {}
    issues: list[TransformIssue] = []
    blank_rows_removed: dict[str, int] = {}

    for sheet in LOAD_ORDER:
        cfg = SHEET_CONFIGS[sheet]
        df = raw_frames[sheet].copy(deep=True)

        for column in cfg.columns:
            df[column] = df[column].map(_normalize_scalar)

        payload_columns = list(cfg.columns)
        blank_mask = df[payload_columns].isna().all(axis=1)
        blank_rows_removed[sheet] = int(blank_mask.sum())
        if blank_mask.any():
            df = df.loc[~blank_mask].copy()

        for column in cfg.integer_columns:
            _convert_column(df, sheet, column, _to_integer, issues)
        for column in cfg.float_columns:
            _convert_column(df, sheet, column, _to_float, issues)
        for column in cfg.date_columns:
            _convert_column(df, sheet, column, _to_datetime, issues, as_date=True)
        for column in cfg.datetime_columns:
            _convert_column(df, sheet, column, _to_datetime, issues)

        frames[sheet] = df
        logger.info(
            "table=%s transformed=%d blank_rows_removed=%d",
            cfg.table,
            len(df),
            blank_rows_removed[sheet],
        )

    return TransformResult(frames=frames, issues=issues, blank_rows_removed=blank_rows_removed)
