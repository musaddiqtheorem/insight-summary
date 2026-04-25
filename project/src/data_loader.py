"""Data ingestion and validation utilities for the Lifecycle Intelligence Engine."""

from __future__ import annotations

import logging
from pathlib import Path

import duckdb

LOGGER_NAME = "lifecycle_intelligence"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
DB_PATH = PROJECT_ROOT / "data" / "db" / "klaviyo.db"

RAW_TABLE_CONFIG: dict[str, tuple[str, Path]] = {
    "profiles_raw": ("profiles.csv", RAW_DATA_DIR / "profiles.csv"),
    "events_raw": ("events.csv", RAW_DATA_DIR / "events.csv"),
    "campaigns_raw": ("campaigns.csv", RAW_DATA_DIR / "campaigns.csv"),
    "flows_raw": ("flows.csv", RAW_DATA_DIR / "flows.csv"),
}


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure and return a shared application logger."""
    logger = logging.getLogger(LOGGER_NAME)
    if not logger.handlers:
        logging.basicConfig(
            level=level,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )
    return logger


def get_connection(db_path: Path | str = DB_PATH) -> duckdb.DuckDBPyConnection:
    """Return a reusable DuckDB connection for the application database."""
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    logger = configure_logging()
    logger.info("Opening DuckDB database at %s", db_file)
    return duckdb.connect(str(db_file))


def get_duckdb_connection(db_path: Path | str = DB_PATH) -> duckdb.DuckDBPyConnection:
    """Backward-compatible wrapper around :func:`get_connection`."""
    return get_connection(db_path=db_path)


def _ensure_input_files_exist() -> None:
    """Validate required raw CSV files are present before ingestion."""
    missing = [filename for filename, file_path in RAW_TABLE_CONFIG.values() if not file_path.exists()]
    if missing:
        missing_files = ", ".join(missing)
        raise FileNotFoundError(f"Missing required raw input files: {missing_files}")


def load_raw_tables() -> None:
    """Load raw CSV files into DuckDB using native SQL CSV readers.

    This function uses DuckDB's CSV reader directly (no pandas) and creates or
    replaces raw tables, which is suitable for repeated, large-file ingestion.
    """
    logger = configure_logging()
    logger.info("Starting raw data ingestion")
    _ensure_input_files_exist()

    with get_connection() as conn:
        for table_name, (_, file_path) in RAW_TABLE_CONFIG.items():
            logger.info("Loading %s into %s", file_path, table_name)
            conn.execute(
                f"""
                CREATE OR REPLACE TABLE {table_name} AS
                SELECT *
                FROM read_csv_auto(
                    '{file_path.as_posix()}',
                    HEADER=TRUE,
                    ALL_VARCHAR=TRUE,
                    SAMPLE_SIZE=-1
                )
                """
            )

    logger.info("Completed raw data ingestion")


def validate_data() -> None:
    """Print validation summaries for staging tables.

    Validation includes row counts, distinct event types, and null-user checks.
    """
    logger = configure_logging()
    logger.info("Starting validation checks")

    count_tables = [
        "profiles_staging",
        "events_staging",
        "campaigns_staging",
        "flows_staging",
    ]

    with get_connection() as conn:
        print("\n=== Staging Row Counts ===")
        for table in count_tables:
            row_count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            message = f"{table}: {row_count} rows"
            logger.info(message)
            print(message)

        print("\n=== Distinct Event Types ===")
        event_types = conn.execute(
            """
            SELECT DISTINCT event_type
            FROM events_staging
            WHERE event_type IS NOT NULL
            ORDER BY event_type
            """
        ).fetchall()
        for (event_type,) in event_types:
            logger.info("event_type=%s", event_type)
            print(event_type)

        print("\n=== NULL user_id Checks ===")
        null_profiles = conn.execute(
            "SELECT COUNT(*) FROM profiles_staging WHERE user_id IS NULL"
        ).fetchone()[0]
        null_events = conn.execute(
            "SELECT COUNT(*) FROM events_staging WHERE user_id IS NULL"
        ).fetchone()[0]
        logger.info("profiles_staging NULL user_id: %s", null_profiles)
        logger.info("events_staging NULL user_id: %s", null_events)
        print(f"profiles_staging NULL user_id rows: {null_profiles}")
        print(f"events_staging NULL user_id rows: {null_events}")

    logger.info("Validation checks completed")


def main() -> None:
    """Run ingestion, staging, and validation as a single command."""
    from staging import create_staging_tables

    load_raw_tables()
    create_staging_tables()
    validate_data()


if __name__ == "__main__":
    main()
