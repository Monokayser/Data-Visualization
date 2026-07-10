from __future__ import annotations

from io import BytesIO

import pandas as pd


DISPLAY_COLUMNS = [
    "EIIN",
    "INSTITUTE NAME",
    "DISTRICT",
    "UPAZILA/THANA",
    "INSTITUTE TYPE",
    "INSTITUTE LEVEL",
    "MANAGEMENT",
    "MPO",
    "STUDY TYPE",
    "AREA",
    "GEOGRAPHY",
    "ADDRESS",
    "POST",
    "MOBILE",
]


def count_unique(df: pd.DataFrame, column: str) -> int:
    if column not in df.columns:
        return 0
    return int(df[column].replace("", pd.NA).dropna().nunique())


def download_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")


def download_excel(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Filtered Data")
        workbook = writer.book
        worksheet = writer.sheets["Filtered Data"]
        header_format = workbook.add_format({"bold": True, "bg_color": "#D6FF5B", "font_color": "#102017"})
        for col_num, value in enumerate(df.columns):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, min(max(len(str(value)) + 4, 14), 34))
    return buffer.getvalue()


def top_value(df: pd.DataFrame, column: str) -> str:
    if df.empty or column not in df.columns:
        return "N/A"
    counts = df[column].replace("", pd.NA).dropna().value_counts()
    return str(counts.index[0]) if not counts.empty else "N/A"

