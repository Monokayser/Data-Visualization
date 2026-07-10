from __future__ import annotations

from pathlib import Path

import pandas as pd

from .preprocessing import clean_dataframe, summarize_quality


def workbook_path(project_root: Path) -> Path:
    return project_root / "data" / "raw" / "edu_institutes.xlsx"


def load_workbook(path: Path) -> dict[str, pd.DataFrame]:
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found at {path}")
    return pd.read_excel(path, sheet_name=None, engine="openpyxl")


def load_clean_sheets(path: Path) -> tuple[dict[str, pd.DataFrame], dict[str, dict]]:
    raw_sheets = load_workbook(path)
    clean_sheets: dict[str, pd.DataFrame] = {}
    quality: dict[str, dict] = {}
    for sheet, raw_df in raw_sheets.items():
        cleaned = clean_dataframe(raw_df, sheet)
        clean_sheets[sheet] = cleaned
        q = summarize_quality(raw_df, cleaned)
        quality[sheet] = {
            "rows": q.rows,
            "duplicate_eiin": q.duplicate_eiin,
            "missing_cells": q.missing_cells,
            "missing_columns": q.missing_columns,
        }
    return clean_sheets, quality

