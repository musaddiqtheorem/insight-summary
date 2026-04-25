"""Feature engineering layer for user-level lifecycle features."""

from __future__ import annotations

from pathlib import Path

from data_loader import configure_logging, get_connection

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FEATURE_SQL_PATH = PROJECT_ROOT / "sql" / "features.sql"


def create_user_features(sql_path: Path | str = FEATURE_SQL_PATH) -> None:
    """Create or replace the ``user_features`` table from ``events_staging``.

    SQL is sourced from a dedicated file to keep feature logic modular,
    explainable, and easy to review.
    """
    logger = configure_logging()
    logger.info("Starting user feature engineering")

    sql_file = Path(sql_path)
    if not sql_file.exists():
        raise FileNotFoundError(f"Feature SQL file not found: {sql_file}")

    sql_text = sql_file.read_text(encoding="utf-8")

    with get_connection() as conn:
        conn.execute(sql_text)

    logger.info("Completed user feature engineering")


def print_user_feature_sample(limit: int = 10) -> None:
    """Print a sample of rows from ``user_features`` for quick inspection."""
    logger = configure_logging()
    logger.info("Printing user_features sample (limit=%s)", limit)

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM user_features
            LIMIT ?
            """,
            [limit],
        ).fetchall()
        columns = [col[0] for col in conn.description]

    print("\n=== user_features Sample ===")
    print(" | ".join(columns))
    for row in rows:
        print(" | ".join(str(value) for value in row))


def main() -> None:
    """Run the feature engineering step and display a sample."""
    create_user_features()
    print_user_feature_sample(limit=10)


if __name__ == "__main__":
    main()
