from __future__ import annotations

import json
from typing import Any

import pandas as pd

from .map_utils import district_summary
from .utils import count_unique, top_value


def _top_counts(df: pd.DataFrame, column: str, n: int = 8) -> list[dict[str, Any]]:
    if df.empty or column not in df.columns:
        return []
    counts = df[column].replace("", pd.NA).dropna().value_counts().head(n)
    return [{"label": str(label), "count": int(count)} for label, count in counts.items()]


def build_dashboard_context(
    df: pd.DataFrame,
    sheet_name: str,
    active_filters: dict[str, Any],
    visible_view: str,
) -> str:
    summary = district_summary(df)
    context = {
        "version": "2.0",
        "selected_sheet": sheet_name,
        "active_filters": active_filters,
        "visible_view": visible_view,
        "record_count": int(len(df)),
        "unique_districts": count_unique(df, "DISTRICT"),
        "unique_upazilas": count_unique(df, "UPAZILA/THANA"),
        "unique_institute_types": count_unique(df, "INSTITUTE TYPE"),
        "top_district": top_value(df, "DISTRICT"),
        "top_upazila": top_value(df, "UPAZILA/THANA"),
        "top_institute_type": top_value(df, "INSTITUTE TYPE"),
        "top_districts": _top_counts(df, "DISTRICT", 10),
        "institute_types": _top_counts(df, "INSTITUTE TYPE", 10),
        "institute_levels": _top_counts(df, "INSTITUTE LEVEL", 10),
        "management_distribution": _top_counts(df, "MANAGEMENT", 8),
        "mpo_distribution": _top_counts(df, "MPO", 5),
        "study_type_distribution": _top_counts(df, "STUDY TYPE", 8),
        "area_distribution": _top_counts(df, "AREA", 8),
        "geography_distribution": _top_counts(df, "GEOGRAPHY", 8),
        "district_aggregation_note": "The dataset has no latitude/longitude; all map-like visuals are district-level aggregations, not exact institute locations.",
        "district_summary_top_rows": summary.head(12).to_dict(orient="records") if not summary.empty else [],
    }
    return json.dumps(context, ensure_ascii=False, indent=2)

