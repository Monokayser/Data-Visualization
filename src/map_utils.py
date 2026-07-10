from __future__ import annotations

import pandas as pd


def district_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["DISTRICT", "TOTAL", "TOP TYPE", "PUBLIC", "PRIVATE", "PUBLIC PRIVATE RATIO"])

    counts = df.groupby("DISTRICT", dropna=False).size().rename("TOTAL")
    top_type = (
        df[df["INSTITUTE TYPE"].ne("")]
        .groupby("DISTRICT")["INSTITUTE TYPE"]
        .agg(lambda s: s.value_counts().index[0] if not s.empty else "N/A")
        .rename("TOP TYPE")
    )
    management = df.assign(
        IS_PUBLIC=df["MANAGEMENT"].str.contains("PUBLIC|GOVERNMENT", case=False, regex=True, na=False),
        IS_PRIVATE=df["MANAGEMENT"].str.contains("PRIVATE", case=False, regex=False, na=False),
    )
    public = management.groupby("DISTRICT")["IS_PUBLIC"].sum().rename("PUBLIC")
    private = management.groupby("DISTRICT")["IS_PRIVATE"].sum().rename("PRIVATE")
    summary = pd.concat([counts, top_type, public, private], axis=1).fillna(0).reset_index()
    summary["TOP TYPE"] = summary["TOP TYPE"].replace(0, "N/A")
    summary["PUBLIC PRIVATE RATIO"] = summary.apply(
        lambda r: f"{int(r['PUBLIC'])}:{int(r['PRIVATE'])}" if int(r["PRIVATE"]) else f"{int(r['PUBLIC'])}:0",
        axis=1,
    )
    return summary.sort_values("TOTAL", ascending=False)

