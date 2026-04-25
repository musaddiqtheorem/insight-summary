"""Utilities for loading large CSV files and managing DuckDB connectivity."""

from __future__ import annotations

import logging
from pathlib import Path

import duckdb

LOGGER_NAME = "lifecycle_intelligence"


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure and return a shared application logger.

    This creates a consistent logging format that can be reused across modules.
    """
    logger = logging.getLogger(LOGGER_NAME)
    if not logger.handlers:
        logging.basicConfig(
            level=level,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )
    return logger


def get_duckdb_connection(db_path: Path | str = "project/data/db/lifecycle.duckdb") -> duckdb.DuckDBPyConnection:
    """Return a reusable DuckDB connection.

    Parameters
    ----------
    db_path
        Path to the DuckDB database file used by the application.

    Returns
    -------
    duckdb.DuckDBPyConnection
        Open DuckDB connection object.
    """
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    logger = configure_logging()
    logger.info("Opening DuckDB database at %s", db_file)
    return duckdb.connect(str(db_file))


def load_raw_csv_to_duckdb(csv_path: Path | str, table_name: str) -> None:
    """Placeholder for ingesting a raw CSV file into DuckDB.

    Intended for chunked, memory-conscious ingestion patterns suitable for
    multi-gigabyte datasets.
    """
    logger = configure_logging()
    logger.info("CSV ingest placeholder called for %s -> %s", csv_path, table_name)


def validate_input_files(raw_data_dir: Path | str = "project/data/raw") -> None:
    """Placeholder for validating expected input files before processing."""
    logger = configure_logging()
    logger.info("Input validation placeholder called for %s", raw_data_dir)
