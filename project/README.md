# Lifecycle Intelligence Engine (Scaffold)

## Project Purpose

This project is a scaffold for a **Lifecycle Intelligence Engine** built with **DuckDB** and **Streamlit**.
It is designed for high-volume analytical workflows over large CSV datasets (5-10GB), with a modular architecture
that separates ingestion, staging, feature engineering, scoring, segmentation, insights, and execution orchestration.

## Folder Overview

```text
project/
├── data/
│   ├── raw/                # Raw CSV input files
│   └── db/                 # DuckDB database files
├── src/                    # Pipeline modules (placeholders)
├── app/                    # Streamlit app entry point
├── sql/                    # SQL transformation placeholders
├── outputs/                # Exported reports/artifacts
├── requirements.txt
└── README.md
```

## Expected Input Files

Place source CSV files in:

- `project/data/raw/`

The scaffold assumes large input files and is organized for scalable ingestion and transformation patterns.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r project/requirements.txt
```

## Run the App

From the repository root, run:

```bash
streamlit run project/app/streamlit_app.py
```

The current app provides a basic UI and a DuckDB connection test button.
Business logic is intentionally not implemented yet.
