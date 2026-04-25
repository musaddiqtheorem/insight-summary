"""Staging layer for cleaning and type-normalizing raw DuckDB tables."""

from __future__ import annotations

from data_loader import configure_logging, get_connection, load_raw_tables, validate_data


def create_staging_tables() -> None:
    """Create cleaned staging tables from raw inputs using DuckDB SQL."""
    logger = configure_logging()
    logger.info("Starting staging table creation")

    with get_connection() as conn:
        conn.execute(
            """
            CREATE OR REPLACE TABLE profiles_staging AS
            SELECT
                user_id,
                LOWER(email) AS email,
                total_orders,
                total_revenue,
                CAST(last_open_date AS TIMESTAMP) AS last_open_date,
                CAST(last_click_date AS TIMESTAMP) AS last_click_date
            FROM profiles_raw
            WHERE user_id IS NOT NULL
            """
        )

        conn.execute(
            """
            CREATE OR REPLACE TABLE events_staging AS
            SELECT
                user_id,
                LOWER(event_type) AS event_type,
                CAST(timestamp AS TIMESTAMP) AS timestamp
            FROM events_raw
            WHERE user_id IS NOT NULL
            """
        )

        conn.execute(
            """
            CREATE OR REPLACE TABLE campaigns_staging AS
            SELECT
                campaign_id,
                CAST(send_time AS TIMESTAMP) AS send_time,
                recipients,
                open_rate,
                click_rate,
                revenue
            FROM campaigns_raw
            """
        )

        conn.execute(
            """
            CREATE OR REPLACE TABLE flows_staging AS
            SELECT
                flow_id,
                step_id,
                users_entered,
                conversions,
                delay_hours
            FROM flows_raw
            """
        )

    logger.info("Completed staging table creation")


def main() -> None:
    """Run ingestion + staging + validation from staging entrypoint."""
    load_raw_tables()
    create_staging_tables()
    validate_data()


if __name__ == "__main__":
    main()
