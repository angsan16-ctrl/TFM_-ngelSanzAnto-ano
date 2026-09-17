from __future__ import annotations

import argparse
import logging
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.db.connection import engine, test_connection
from src.etl.extract import extract_workbook
from src.etl.transform import transform_workbook
from src.etl.validate import validate_workbook, write_rejected_csvs
from src.etl.load import load_frames


def configure_logging() -> None:
    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    handlers = [
        logging.FileHandler(log_dir / "etl.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ]
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=handlers,
        force=True,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Carga validada Excel -> MySQL para el TFM SAF")
    parser.add_argument(
        "--excel",
        default=str(PROJECT_ROOT / "data" / "plantilla.xlsx"),
        help="Ruta al Excel fuente de verdad",
    )
    parser.add_argument(
        "--replace-data",
        action="store_true",
        help="Borra los datos existentes en orden seguro y vuelve a cargar, todo dentro de una transacción.",
    )
    parser.add_argument(
        "--allow-rejects",
        action="store_true",
        help="Carga solo filas válidas aunque existan rechazadas. Sin esta opción, cualquier rechazo aborta antes de tocar MySQL.",
    )
    return parser.parse_args()


def main() -> int:
    configure_logging()
    args = parse_args()
    log = logging.getLogger("load_excel_to_mysql")

    try:
        excel_path = Path(args.excel).resolve()
        log.info("excel=%s", excel_path)

        raw = extract_workbook(excel_path)
        transformed = transform_workbook(raw)
        validation = validate_workbook(raw, transformed)

        rejected_paths = write_rejected_csvs(validation, PROJECT_ROOT / "data" / "rejected")
        for warning in validation.warnings:
            log.warning(warning)

        if validation.rejected_count:
            log.error("rejected_rows=%d", validation.rejected_count)
            for path in rejected_paths:
                log.error("rejected_file=%s", path)
            if not args.allow_rejects:
                log.error("Carga abortada antes de tocar MySQL. Corrige el Excel o usa --allow-rejects conscientemente.")
                return 2

        if not test_connection(engine):
            log.error("SELECT 1 no devolvió 1")
            return 3

        loaded = load_frames(
            engine,
            validation.valid_frames,
            replace_data=args.replace_data,
        )

        print("\n========================================")
        print("SAF EXCEL -> MYSQL LOAD")
        print("========================================")
        for table, count in loaded.items():
            print(f"[OK] {table}: {count} rows")
        if validation.rejected_count:
            print(f"[WARN] rejected rows: {validation.rejected_count}")
        else:
            print("[OK] rejected rows: 0")
        print("LOAD COMPLETE")
        return 0

    except Exception as exc:
        log.exception("ETL failed: %s", exc)
        print(f"\n[ERROR] {exc}")
        print(f"Revisa: {PROJECT_ROOT / 'logs' / 'etl.log'}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
