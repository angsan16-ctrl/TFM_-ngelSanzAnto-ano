from __future__ import annotations

from collections.abc import Mapping
import logging

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from .config import LOAD_ORDER, REVERSE_LOAD_ORDER, SHEET_CONFIGS

logger = logging.getLogger(__name__)


def table_counts(engine: Engine) -> dict[str, int]:
    counts: dict[str, int] = {}
    with engine.connect() as conn:
        for sheet in LOAD_ORDER:
            table = SHEET_CONFIGS[sheet].table
            counts[table] = int(conn.execute(text(f"SELECT COUNT(*) FROM `{table}`")).scalar_one())
    return counts


def _assert_empty_or_replace(engine: Engine, replace_data: bool) -> None:
    counts = table_counts(engine)
    populated = {table: count for table, count in counts.items() if count > 0}
    if populated and not replace_data:
        details = ", ".join(f"{k}={v}" for k, v in populated.items())
        raise RuntimeError(
            "La base ya contiene datos y la carga se ha detenido para evitar duplicados. "
            f"Tablas no vacías: {details}. Usa --replace-data solo si quieres sustituir la carga existente."
        )


def _delete_existing_rows(conn) -> None:
    for sheet in REVERSE_LOAD_ORDER:
        table = SHEET_CONFIGS[sheet].table
        conn.execute(text(f"DELETE FROM `{table}`"))
        logger.info("table=%s existing_rows_deleted", table)


def load_frames(
    engine: Engine,
    frames: Mapping[str, pd.DataFrame],
    *,
    replace_data: bool = False,
    chunksize: int = 500,
) -> dict[str, int]:
    _assert_empty_or_replace(engine, replace_data)
    loaded: dict[str, int] = {}

    # Una única transacción InnoDB para toda la carga. DELETE también es transaccional.
    with engine.begin() as conn:
        if replace_data:
            _delete_existing_rows(conn)

        for sheet in LOAD_ORDER:
            cfg = SHEET_CONFIGS[sheet]
            df = frames[sheet]
            if df.empty:
                loaded[cfg.table] = 0
                logger.info("table=%s loaded=0", cfg.table)
                continue

            df.to_sql(
                cfg.table,
                con=conn,
                if_exists="append",
                index=False,
                method="multi",
                chunksize=chunksize,
            )
            loaded[cfg.table] = len(df)
            logger.info("table=%s loaded=%d", cfg.table, len(df))

    return loaded
