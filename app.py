from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from src.ai_context import build_dashboard_context
from src.ai_service import ask_ai
from src.config import load_ai_settings
from src.data_loader import load_clean_sheets, workbook_path
from src.map_utils import district_summary
from src.preprocessing import filter_data, unique_sorted
from src.utils import DISPLAY_COLUMNS, count_unique, download_csv, download_excel, top_value
from src.visualizations import bar_count, district_bubble, donut, public_private


PROJECT_ROOT = Path(__file__).resolve().parent


st.set_page_config(
    page_title="Bangladesh Educational Institutes Explorer",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(show_spinner="Loading and cleaning workbook...")
def cached_sheets(path_text: str):
    return load_clean_sheets(Path(path_text))


def inject_css() -> None:
    css_path = PROJECT_ROOT / "assets" / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def kpi(label: str, value: str, note: str) -> str:
    return (
        f'<div class="kpi-card">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-note">{note}</div>'
        f"</div>"
    )


def hero(sheet_name: str, loaded_at: str) -> None:
    st.markdown(
        f"""
        <div class="hero">
          <div class="topbar">
            <div class="brand"><span class="logo-mark">ED</span><span>edura</span></div>
            <div class="status-pill">Version 2.0 — AI-Enhanced Data Visualization Dashboard</div>
          </div>
          <h1>Bangladesh Educational Institutes Explorer</h1>
          <p>
            A dark, presentation-ready dashboard for exploring Bangladesh educational institute records by district,
            upazila/thana, institute type, level, management, MPO status, study type, area, and geography.
            District visuals are aggregated because the source dataset does not include latitude or longitude.
            Loaded {loaded_at} · Active sheet: {sheet_name}
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_filters(sheets: dict[str, pd.DataFrame]):
    with st.sidebar:
        st.markdown("### edura command")
        st.caption("Use filters together to focus the national education dataset.")
        if st.button("Reset filters", use_container_width=True):
            st.session_state.clear()
            st.rerun()

        sheet = st.selectbox("Dataset sheet / category", list(sheets.keys()), index=0)
        base = sheets[sheet]

        districts = st.multiselect("District", unique_sorted(base, "DISTRICT"), placeholder="All districts")
        scoped = base[base["DISTRICT"].isin(districts)] if districts else base
        upazilas = st.multiselect("Upazila / Thana", unique_sorted(scoped, "UPAZILA/THANA"), placeholder="All upazilas")
        institute_types = st.multiselect("Institute Type", unique_sorted(base, "INSTITUTE TYPE"), placeholder="All types")
        levels = st.multiselect("Institute Level", unique_sorted(base, "INSTITUTE LEVEL"), placeholder="All levels")

        def select_all(label: str, column: str):
            return st.selectbox(label, ["All"] + unique_sorted(base, column))

        management = select_all("Management", "MANAGEMENT")
        mpo = select_all("MPO Status", "MPO")
        study_type = select_all("Study Type", "STUDY TYPE")
        area = select_all("Area", "AREA")
        geography = select_all("Geography", "GEOGRAPHY")
        search = st.text_input("Search", placeholder="Institute name, EIIN, address, post...")

    active_filters = {
        "districts": districts or "All",
        "upazilas": upazilas or "All",
        "institute_types": institute_types or "All",
        "levels": levels or "All",
        "management": management,
        "mpo": mpo,
        "study_type": study_type,
        "area": area,
        "geography": geography,
        "search": search or "",
    }
    return sheet, active_filters, filter_data(
        base,
        districts=districts,
        upazilas=upazilas,
        institute_types=institute_types,
        levels=levels,
        management=management,
        mpo=mpo,
        study_type=study_type,
        area=area,
        geography=geography,
        search=search,
    )


def ai_assistant_panel(df: pd.DataFrame, sheet_name: str, active_filters: dict, visible_view: str) -> None:
    settings = load_ai_settings()
    if "ai_messages" not in st.session_state:
        st.session_state.ai_messages = [
            {
                "role": "assistant",
                "content": "Hello. Ask me about the current filters, charts, district rankings, institute types, or dataset summary.",
            }
        ]

    st.markdown(
        '<div class="panel-card"><div class="section-title"><h2>AI Data Assistant</h2><span class="hint">Context-aware answers from summarized dashboard data</span></div>',
        unsafe_allow_html=True,
    )
    if settings.enabled:
        st.success(f"AI service configured. Model: {settings.model}")
    else:
        st.warning("AI API key is not configured. Add `OPENROUTER_API_KEY` to `.env` or deployment secrets to enable API responses.")

    examples = [
        "What are the main patterns in the current filtered data?",
        "Which districts have the highest institute counts?",
        "Explain the MPO distribution in simple language.",
        "What limitations should I mention about the district visualization?",
    ]
    st.caption("Example questions")
    cols = st.columns(2)
    for index, example in enumerate(examples):
        with cols[index % 2]:
            if st.button(example, key=f"example_{index}", use_container_width=True):
                st.session_state.pending_ai_question = example

    for message in st.session_state.ai_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    prompt = st.chat_input("Ask about the current data, chart, filters, trends, or limitations...")
    question = st.session_state.pop("pending_ai_question", None) or prompt

    clear_col, info_col = st.columns([1, 3])
    with clear_col:
        if st.button("Clear chat", use_container_width=True):
            st.session_state.ai_messages = []
            st.rerun()
    with info_col:
        st.caption("The assistant receives summarized context only, not the full workbook.")

    if question:
        st.session_state.ai_messages.append({"role": "user", "content": question})
        context = build_dashboard_context(df, sheet_name, active_filters, visible_view)
        with st.chat_message("user"):
            st.write(question)
        with st.chat_message("assistant"):
            with st.spinner("Analyzing the current dashboard context..."):
                result = ask_ai(question, context, settings)
            st.write(result.message)
        st.session_state.ai_messages.append({"role": "assistant", "content": result.message})
    st.markdown("</div>", unsafe_allow_html=True)


def detail_card(df: pd.DataFrame) -> None:
    st.markdown('<div class="section-title"><h3>Institute Detail</h3><span class="hint">Select a record from filtered data</span></div>', unsafe_allow_html=True)
    if df.empty:
        st.info("No institute is available for the current filter set.")
        return
    options = (df["EIIN"].fillna("") + " · " + df["INSTITUTE NAME"].fillna("")).head(5000).tolist()
    selected = st.selectbox("Institute", options, label_visibility="collapsed")
    index = options.index(selected)
    row = df.iloc[index]
    st.markdown(
        f"""
        <div class="info-card" style="padding:20px">
          <h3 style="margin:0 0 6px 0">{row['INSTITUTE NAME']}</h3>
          <p class="hint" style="margin:0 0 16px 0">EIIN {row['EIIN']} · {row['INSTITUTE TYPE']} · {row['INSTITUTE LEVEL']}</p>
          <p><b>Location:</b> {row['DISTRICT']}, {row['UPAZILA/THANA']}</p>
          <p><b>Address:</b> {row['ADDRESS']} · <b>Post:</b> {row['POST']}</p>
          <p><b>Mobile:</b> {row['MOBILE'] or 'Not available'}</p>
          <p><b>Management:</b> {row['MANAGEMENT']} · <b>MPO:</b> {row['MPO']} · <b>Study:</b> {row['STUDY TYPE']}</p>
          <p><b>Area:</b> {row['AREA']} · <b>Geography:</b> {row['GEOGRAPHY']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    inject_css()
    path = workbook_path(PROJECT_ROOT)
    try:
        sheets, quality = cached_sheets(str(path))
    except Exception as exc:
        st.error(f"Could not load dataset. Please check data/raw/edu_institutes.xlsx. Details: {exc}")
        st.stop()

    sheet_name, active_filters, filtered = sidebar_filters(sheets)
    all_df = sheets[sheet_name]
    loaded_at = datetime.now().strftime("%d %b %Y, %I:%M %p")
    hero(sheet_name, loaded_at)

    st.markdown(
        '<div class="kpi-grid">'
        + kpi("Filtered Institutes", f"{len(filtered):,}", f"from {len(all_df):,} records")
        + kpi("Districts", f"{count_unique(filtered, 'DISTRICT'):,}", f"top: {top_value(filtered, 'DISTRICT')}")
        + kpi("Upazila / Thana", f"{count_unique(filtered, 'UPAZILA/THANA'):,}", f"top: {top_value(filtered, 'UPAZILA/THANA')}")
        + kpi("Institute Types", f"{count_unique(filtered, 'INSTITUTE TYPE'):,}", f"top: {top_value(filtered, 'INSTITUTE TYPE')}")
        + "</div>",
        unsafe_allow_html=True,
    )

    tab_overview, tab_analytics, tab_ai, tab_records, tab_method = st.tabs(["Overview", "Analytics", "AI Assistant", "Records", "Methodology & About"])

    with tab_overview:
        st.markdown('<div class="panel-card"><div class="section-title"><h2>District Intelligence</h2><span class="hint">Aggregated district-level view, not exact institute locations</span></div>', unsafe_allow_html=True)
        summary = district_summary(filtered)
        st.plotly_chart(district_bubble(summary), use_container_width=True, config={"displayModeBar": True, "responsive": True})
        st.markdown("</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="panel-card">', unsafe_allow_html=True)
            st.plotly_chart(bar_count(filtered, "DISTRICT", "Top 15 districts by institute count"), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="panel-card">', unsafe_allow_html=True)
            st.plotly_chart(public_private(filtered), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    with tab_analytics:
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            st.markdown('<div class="panel-card">', unsafe_allow_html=True)
            st.plotly_chart(bar_count(filtered, "INSTITUTE TYPE", "Institute count by type", top_n=12), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with r1c2:
            st.markdown('<div class="panel-card">', unsafe_allow_html=True)
            st.plotly_chart(bar_count(filtered, "INSTITUTE LEVEL", "Institute level distribution", top_n=12), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        r2c1, r2c2 = st.columns(2)
        with r2c1:
            st.markdown('<div class="panel-card">', unsafe_allow_html=True)
            st.plotly_chart(donut(filtered, "MANAGEMENT", "Management distribution"), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with r2c2:
            st.markdown('<div class="panel-card">', unsafe_allow_html=True)
            st.plotly_chart(donut(filtered, "MPO", "MPO status distribution"), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        r3c1, r3c2, r3c3 = st.columns(3)
        for col, column, title in [
            (r3c1, "STUDY TYPE", "Study type"),
            (r3c2, "AREA", "Area type"),
            (r3c3, "GEOGRAPHY", "Geography type"),
        ]:
            with col:
                st.markdown('<div class="panel-card">', unsafe_allow_html=True)
                st.plotly_chart(donut(filtered, column, title), use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
        selected_district = st.selectbox("Focus district for upazila ranking", ["All"] + unique_sorted(filtered, "DISTRICT"))
        district_df = filtered if selected_district == "All" else filtered[filtered["DISTRICT"].eq(selected_district)]
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.plotly_chart(bar_count(district_df, "UPAZILA/THANA", "Upazila/Thana institute count", top_n=18), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_ai:
        ai_assistant_panel(filtered, sheet_name, active_filters, "AI Assistant")

    with tab_records:
        table_df = filtered[DISPLAY_COLUMNS].copy()
        st.markdown('<div class="section-title"><h2>Filtered Records</h2><span class="hint">Optimized table with export options</span></div>', unsafe_allow_html=True)
        d1, d2 = st.columns([1, 1])
        d1.download_button("Download CSV", download_csv(table_df), "filtered_edu_institutes.csv", "text/csv", use_container_width=True)
        d2.download_button(
            "Download Excel",
            download_excel(table_df),
            "filtered_edu_institutes.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
        st.dataframe(table_df, use_container_width=True, height=520, hide_index=True)
        detail_card(table_df)

    with tab_method:
        q = quality[sheet_name]
        st.markdown(
            f"""
            <div class="panel-card">
              <div class="section-title"><h2>Dataset Summary</h2><span class="hint">{sheet_name}</span></div>
              <p>The workbook contains ten sheets. The app uses <b>All</b> by default and allows switching category sheets from the sidebar.</p>
              <p><b>Rows in selected sheet:</b> {q['rows']:,} · <b>Duplicate EIIN values:</b> {q['duplicate_eiin']:,} · <b>Blank cells after cleaning:</b> {q['missing_cells']:,}</p>
              <p><b>Missing required columns:</b> {', '.join(q['missing_columns']) if q['missing_columns'] else 'None'}</p>
            </div>
            <div class="panel-card">
              <div class="section-title"><h2>Methodology</h2></div>
              <p>Data is loaded once with Streamlit caching, standardized into display-safe column names, cleaned with vectorized Pandas operations, and filtered interactively. The geovisual section is district-level aggregation only because the source file does not provide latitude and longitude.</p>
              <p>Charts use Plotly for hover tooltips, zooming, mode-bar exports, and responsive rendering. Filtered records can be downloaded as CSV or Excel for further academic analysis.</p>
            </div>
            <div class="panel-card">
              <div class="section-title"><h2>Project Information</h2></div>
              <p><b>Author:</b> S. M. Monowar Kayser · <b>University:</b> Daffodil International University</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<p class='hint' style='text-align:center;padding:24px'>Data Visualization Web Application · Built with Streamlit, Pandas, and Plotly</p>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
