"""Scoring engine for lifecycle intent and recommended actions."""

from __future__ import annotations

from pathlib import Path

from data_loader import configure_logging, get_connection

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCORING_SQL_PATH = PROJECT_ROOT / "sql" / "scoring.sql"


def create_user_scores(sql_path: Path | str = SCORING_SQL_PATH) -> None:
    """Create or replace ``user_scores`` from ``user_features`` using DuckDB SQL."""
    logger = configure_logging()
    logger.info("Starting score generation")

    sql_file = Path(sql_path)
    if not sql_file.exists():
        raise FileNotFoundError(f"Scoring SQL file not found: {sql_file}")

    sql_text = sql_file.read_text(encoding="utf-8")
    with get_connection() as conn:
        conn.execute(sql_text)

    logger.info("Completed score generation")


def print_user_scores_sample(limit: int = 10) -> None:
    """Print sample rows from ``user_scores`` for inspection."""
    logger = configure_logging()
    logger.info("Printing user_scores sample (limit=%s)", limit)

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM user_scores
            LIMIT ?
            """,
            [limit],
        ).fetchall()
        columns = [col[0] for col in conn.description]

    print("\n=== user_scores Sample ===")
    print(" | ".join(columns))
    for row in rows:
        print(" | ".join(str(value) for value in row))


def main() -> None:
    """Run scoring and print sample output."""
    create_user_scores()
    print_user_scores_sample(limit=10)


if __name__ == "__main__":
    main()
