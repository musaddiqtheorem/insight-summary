"""Execution layer for generating actionable marketing plans."""

from __future__ import annotations

from pathlib import Path

from data_loader import configure_logging, get_connection

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXECUTION_SQL_PATH = PROJECT_ROOT / "sql" / "execution.sql"


def create_execution_plan(sql_path: Path | str = EXECUTION_SQL_PATH) -> None:
    """Create or replace ``execution_plan`` from ``user_scores`` using SQL."""
    logger = configure_logging()
    logger.info("Starting execution plan generation")

    sql_file = Path(sql_path)
    if not sql_file.exists():
        raise FileNotFoundError(f"Execution SQL file not found: {sql_file}")

    sql_text = sql_file.read_text(encoding="utf-8")
    with get_connection() as conn:
        conn.execute(sql_text)

    logger.info("Completed execution plan generation")


def print_execution_plan_sample(limit: int = 10) -> None:
    """Print a sample of rows from ``execution_plan``."""
    logger = configure_logging()
    logger.info("Printing execution_plan sample (limit=%s)", limit)

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM execution_plan
            LIMIT ?
            """,
            [limit],
        ).fetchall()
        columns = [col[0] for col in conn.description]

    print("\n=== execution_plan Sample ===")
    print(" | ".join(columns))
    for row in rows:
        print(" | ".join(str(value) for value in row))


def run_pipeline() -> None:
    """Run execution-plan generation and print sample output."""
    create_execution_plan()
    print_execution_plan_sample(limit=10)


def main() -> None:
    """Command-line entrypoint for execution plan generation."""
    run_pipeline()


if __name__ == "__main__":
    main()
