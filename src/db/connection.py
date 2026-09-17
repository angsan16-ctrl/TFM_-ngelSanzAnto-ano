from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, URL
from sqlalchemy.exc import SQLAlchemyError

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def _required(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or value.strip() == "":
        raise RuntimeError(f"Falta la variable de entorno {name} en {PROJECT_ROOT / '.env'}")
    return value.strip()


def build_database_url() -> URL:
    password = _required("MYSQL_PASSWORD")
    if password in {"CHANGE_ME", "CHANGE_ME_BEFORE_RUNNING"}:
        raise RuntimeError("Edita .env y sustituye MYSQL_PASSWORD=CHANGE_ME por la contraseña real de saf_app.")
    return URL.create(
        drivername="mysql+pymysql",
        username=_required("MYSQL_USER", "saf_app"),
        password=password,
        host=_required("MYSQL_HOST", "127.0.0.1"),
        port=int(_required("MYSQL_PORT", "3306")),
        database=_required("MYSQL_DATABASE", "saf_biomass"),
        query={"charset": "utf8mb4"},
    )


def get_engine() -> Engine:
    return create_engine(
        build_database_url(),
        pool_pre_ping=True,
        pool_recycle=1800,
        future=True,
    )


def test_connection(db_engine: Engine | None = None) -> bool:
    db_engine = db_engine or engine
    try:
        with db_engine.connect() as conn:
            return conn.execute(text("SELECT 1")).scalar_one() == 1
    except SQLAlchemyError as exc:
        raise RuntimeError(f"No se pudo conectar a MySQL: {exc}") from exc


@contextmanager
def connection(db_engine: Engine | None = None):
    db_engine = db_engine or engine
    try:
        with db_engine.connect() as conn:
            yield conn
    except SQLAlchemyError as exc:
        raise RuntimeError(f"Error de conexión/consulta MySQL: {exc}") from exc


engine = get_engine()
