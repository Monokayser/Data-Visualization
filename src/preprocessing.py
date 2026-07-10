from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd


DISPLAY_RENAMES = {
    "MOBAILE": "MOBILE",
    "GEOGRPY": "GEOGRAPHY",
}

REQUIRED_COLUMNS = [
    "DISTRICT",
    "UPAZILA/THANA",
    "INSTITUTE TYPE",
    "INSTITUTE LEVEL",
    "EIIN",
    "INSTITUTE NAME",
    "ADDRESS",
    "POST",
    "MOBILE",
    "MANAGEMENT",
    "MPO",
    "STUDY TYPE",
    "AREA",
    "GEOGRAPHY",
]


@dataclass(frozen=True)
class DataQuality:
    rows: int
    duplicate_eiin: int
    missing_cells: int
    missing_columns: list[str]


def normalize_column_name(name: object) -> str:
    return str(name).strip().upper().replace("\n", " ")


def clean_text_series(series: pd.Series, uppercase: bool = False) -> pd.Series:
    cleaned = (
        series.fillna("")
        .astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )
    cleaned = cleaned.mask(cleaned.str.lower().isin(["nan", "none", "null"]), "")
    return cleaned.str.upper() if uppercase else cleaned


def clean_eiin(series: pd.Series) -> pd.Series:
    values = series.fillna("").astype(str).str.strip()
    values = values.str.replace(r"\.0$", "", regex=True)
    values = values.mask(values.str.lower().isin(["nan", "none", "null"]), "")
    return values


def clean_dataframe(df: pd.DataFrame, sheet_name: str = "All") -> pd.DataFrame:
    df = df.copy()
    df.columns = [normalize_column_name(c) for c in df.columns]
    df = df.rename(columns=DISPLAY_RENAMES)
    df = df.dropna(how="all")

    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    for col in REQUIRED_COLUMNS:
        if col == "EIIN":
            df[col] = clean_eiin(df[col])
        elif col == "MOBILE":
            df[col] = clean_text_series(df[col])
        elif col in {"DISTRICT", "UPAZILA/THANA", "INSTITUTE TYPE", "INSTITUTE LEVEL", "MANAGEMENT", "MPO", "STUDY TYPE", "AREA", "GEOGRAPHY"}:
            df[col] = clean_text_series(df[col], uppercase=True)
        else:
            df[col] = clean_text_series(df[col])

    df["SOURCE SHEET"] = sheet_name
    df["SEARCH_TEXT"] = (
        df[["EIIN", "INSTITUTE NAME", "ADDRESS", "POST", "DISTRICT", "UPAZILA/THANA"]]
        .agg(" ".join, axis=1)
        .str.lower()
    )
    return df[REQUIRED_COLUMNS + ["SOURCE SHEET", "SEARCH_TEXT"]]


def summarize_quality(raw_df: pd.DataFrame, clean_df: pd.DataFrame) -> DataQuality:
    raw_columns = {normalize_column_name(c) for c in raw_df.columns}
    raw_columns = {DISPLAY_RENAMES.get(c, c) for c in raw_columns}
    missing_columns = [c for c in REQUIRED_COLUMNS if c not in raw_columns]
    duplicate_eiin = int(clean_df.loc[clean_df["EIIN"].ne(""), "EIIN"].duplicated().sum())
    return DataQuality(
        rows=int(len(clean_df)),
        duplicate_eiin=duplicate_eiin,
        missing_cells=int(clean_df[REQUIRED_COLUMNS].eq("").sum().sum()),
        missing_columns=missing_columns,
    )


def unique_sorted(df: pd.DataFrame, column: str, depends_on: Iterable[str] | None = None) -> list[str]:
    if column not in df.columns:
        return []
    values = df[column].dropna().astype(str).str.strip()
    return sorted([v for v in values.unique().tolist() if v])


def filter_data(
    df: pd.DataFrame,
    districts: list[str] | None = None,
    upazilas: list[str] | None = None,
    institute_types: list[str] | None = None,
    levels: list[str] | None = None,
    management: str | None = None,
    mpo: str | None = None,
    study_type: str | None = None,
    area: str | None = None,
    geography: str | None = None,
    search: str | None = None,
) -> pd.DataFrame:
    mask = pd.Series(True, index=df.index)
    multi_filters = {
        "DISTRICT": districts,
        "UPAZILA/THANA": upazilas,
        "INSTITUTE TYPE": institute_types,
        "INSTITUTE LEVEL": levels,
    }
    for column, values in multi_filters.items():
        if values:
            mask &= df[column].isin(values)

    single_filters = {
        "MANAGEMENT": management,
        "MPO": mpo,
        "STUDY TYPE": study_type,
        "AREA": area,
        "GEOGRAPHY": geography,
    }
    for column, value in single_filters.items():
        if value and value != "All":
            mask &= df[column].eq(value)

    if search:
        terms = search.strip().lower().split()
        for term in terms:
            mask &= df["SEARCH_TEXT"].str.contains(term, regex=False, na=False)

    return df.loc[mask].copy()

