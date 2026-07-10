from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

PALETTE = ["#d7ff62", "#79c7f2", "#54e0c7", "#f5cc58", "#fb6fae", "#a78bfa", "#f7faf0"]
BG = "#101b16"
PAPER = "rgba(0,0,0,0)"
GRID = "rgba(222,255,218,.14)"
TEXT = "#edf7ee"
MUTED = "#aab8ad"


def themed(fig: go.Figure, height: int = 430, legend: bool = True) -> go.Figure:
    fig.update_layout(
        height=height,
        paper_bgcolor=PAPER,
        plot_bgcolor=PAPER,
        font=dict(family="Inter, Segoe UI, Arial, sans-serif", color=TEXT, size=13),
        margin=dict(l=20, r=20, t=56, b=30),
        legend=dict(orientation="h", y=-0.14, x=0, font=dict(color=MUTED)) if legend else None,
        hoverlabel=dict(bgcolor="#17251f", bordercolor="#d7ff62", font_color=TEXT),
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID, title_font_color=MUTED, tickfont_color=MUTED)
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID, title_font_color=MUTED, tickfont_color=MUTED)
    return fig


def empty_figure(title: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text="No data available for the current filters", showarrow=False, font=dict(color=MUTED, size=16))
    fig.update_layout(title=title)
    return themed(fig)


def bar_count(df: pd.DataFrame, column: str, title: str, top_n: int = 15, horizontal: bool = True) -> go.Figure:
    if df.empty or column not in df.columns:
        return empty_figure(title)
    counts = df[column].replace("", pd.NA).dropna().value_counts().head(top_n).reset_index()
    counts.columns = [column, "Count"]
    if counts.empty:
        return empty_figure(title)
    if horizontal:
        counts = counts.sort_values("Count")
        fig = px.bar(counts, x="Count", y=column, orientation="h", color="Count", color_continuous_scale=["#79c7f2", "#d7ff62"])
        fig.update_traces(text=counts["Count"], textposition="outside", marker_line_width=0)
    else:
        fig = px.bar(counts, x=column, y="Count", color="Count", color_continuous_scale=["#79c7f2", "#d7ff62"], text="Count")
        fig.update_traces(textposition="outside", marker_line_width=0)
    fig.update_layout(title=title, coloraxis_showscale=False)
    return themed(fig, legend=False)


def donut(df: pd.DataFrame, column: str, title: str, top_n: int = 6) -> go.Figure:
    if df.empty or column not in df.columns:
        return empty_figure(title)
    counts = df[column].replace("", pd.NA).dropna().value_counts().head(top_n).reset_index()
    counts.columns = [column, "Count"]
    if counts.empty:
        return empty_figure(title)
    fig = px.pie(counts, names=column, values="Count", hole=0.62, color_discrete_sequence=PALETTE)
    fig.update_traces(
        textposition="inside",
        texttemplate="<b>%{percent:.1%}</b>",
        textfont=dict(color="#102017", size=13),
        marker=dict(line=dict(color=BG, width=2)),
        hovertemplate="<b>%{label}</b><br>Institutes: %{value:,}<br>Share: %{percent}<extra></extra>",
    )
    fig.update_layout(title=title, uniformtext_minsize=11, uniformtext_mode="hide")
    return themed(fig)


def district_bubble(summary: pd.DataFrame) -> go.Figure:
    if summary.empty:
        return empty_figure("District-level institute concentration")
    plot_df = summary.head(64).copy()
    plot_df["Rank"] = range(1, len(plot_df) + 1)
    fig = px.scatter(
        plot_df,
        x="Rank",
        y="TOTAL",
        size="TOTAL",
        color="TOTAL",
        color_continuous_scale=["#79c7f2", "#3047d8", "#d7ff62"],
        hover_name="DISTRICT",
        hover_data={
            "Rank": True,
            "TOTAL": ":,",
            "TOP TYPE": True,
            "PUBLIC PRIVATE RATIO": True,
        },
        size_max=58,
    )
    fig.update_traces(marker=dict(line=dict(color="rgba(237,247,238,.7)", width=1.1), opacity=.86))
    fig.update_layout(
        title="District-level institute concentration",
        xaxis_title="District rank by institute count",
        yaxis_title="Institutes",
        coloraxis_colorbar=dict(title="Count", tickfont=dict(color=TEXT), title_font_color=TEXT),
    )
    return themed(fig, height=490, legend=False)


def public_private(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return empty_figure("Public vs Private comparison")
    public = int(df["MANAGEMENT"].str.contains("PUBLIC|GOVERNMENT", case=False, regex=True, na=False).sum())
    private = int(df["MANAGEMENT"].str.contains("PRIVATE", case=False, regex=False, na=False).sum())
    other = max(int(len(df) - public - private), 0)
    values = pd.DataFrame({"Group": ["Public/Govt", "Private", "Other"], "Count": [public, private, other]})
    fig = px.bar(values, x="Group", y="Count", color="Group", text="Count", color_discrete_sequence=["#79c7f2", "#d7ff62", "#aab8ad"])
    fig.update_traces(textposition="outside", marker_line_width=0)
    fig.update_layout(title="Public vs Private comparison", showlegend=False)
    return themed(fig, legend=False)

