"""Streamlit entry point for the Lifecycle Intelligence Engine."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# Ensure src modules are importable when running from repository root.
ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from data_loader import configure_logging, get_duckdb_connection  # noqa: E402


def main() -> None:
    """Render a minimal Streamlit interface for future lifecycle workflows."""
    logger = configure_logging()

    st.set_page_config(page_title="Lifecycle Intelligence Engine", layout="wide")
    st.title("Lifecycle Intelligence Engine")
    st.caption("Scaffolded UI for DuckDB-powered, large-scale lifecycle analytics.")

    st.write(
        "This is a project scaffold. Data ingestion, feature engineering, and "
        "insight-generation logic will be added in later iterations."
    )

    if st.button("Test DuckDB Connection"):
        conn = get_duckdb_connection()
        conn.execute("SELECT 1")
        conn.close()
        logger.info("DuckDB connection test executed from Streamlit")
        st.success("DuckDB connection initialized successfully.")


if __name__ == "__main__":
    main()
