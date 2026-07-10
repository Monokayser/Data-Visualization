from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.ai_context import build_dashboard_context
from src.ai_service import ask_ai
from src.config import AISettings
from src.data_loader import load_clean_sheets
from src.preprocessing import clean_dataframe, filter_data
from src.visualizations import bar_count


ROOT = Path(__file__).resolve().parents[1]


def test_load_workbook_all_sheet():
    sheets, quality = load_clean_sheets(ROOT / "data" / "raw" / "edu_institutes.xlsx")
    assert "All" in sheets
    assert len(sheets["All"]) > 30000
    assert quality["All"]["missing_columns"] == []


def test_clean_dataframe_handles_missing_columns():
    raw = pd.DataFrame({"EIIN": [123.0], "MOBAILE": [None], "GEOGRPY": ["Plain"]})
    cleaned = clean_dataframe(raw, "Test")
    assert cleaned.loc[0, "EIIN"] == "123"
    assert "MOBILE" in cleaned.columns
    assert "GEOGRAPHY" in cleaned.columns


def test_filter_empty_result_is_safe():
    sheets, _ = load_clean_sheets(ROOT / "data" / "raw" / "edu_institutes.xlsx")
    result = filter_data(sheets["All"], districts=["NOT A DISTRICT"])
    assert result.empty


def test_visualization_generation():
    sheets, _ = load_clean_sheets(ROOT / "data" / "raw" / "edu_institutes.xlsx")
    fig = bar_count(sheets["All"], "DISTRICT", "Top districts")
    assert fig is not None
    assert len(fig.data) >= 1


def test_ai_context_contains_filter_summary():
    sample = pd.DataFrame(
        {
            "DISTRICT": ["DHAKA", "DHAKA"],
            "UPAZILA/THANA": ["A", "B"],
            "INSTITUTE TYPE": ["SCHOOL", "COLLEGE"],
            "INSTITUTE LEVEL": ["SECONDARY", "HIGHER SECONDARY"],
            "MANAGEMENT": ["PRIVATE", "PUBLIC"],
            "MPO": ["YES", "NO"],
            "STUDY TYPE": ["COMBINED", "COMBINED"],
            "AREA": ["URBAN", "RURAL"],
            "GEOGRAPHY": ["PLAIN", "PLAIN"],
        }
    )
    context = build_dashboard_context(sample, "All", {"districts": ["DHAKA"]}, "AI Assistant")
    assert '"record_count": 2' in context
    assert "DHAKA" in context


def test_ai_missing_key_graceful_failure():
    settings = AISettings("", "openrouter/free", "https://example.invalid", 1, "", "")
    result = ask_ai("What is shown?", "{}", settings)
    assert result.ok is False
    assert result.error_type == "missing_api_key"

