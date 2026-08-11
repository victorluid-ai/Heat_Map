import altair as alt
import pandas as pd
import plotly.graph_objects as go
from typing import Sequence


def traffic_line_chart(hourly_data: list[dict]) -> alt.Chart:
    if not hourly_data:
        return alt.Chart(pd.DataFrame({"hour": [], "count": []})).mark_line()
    df = pd.DataFrame(hourly_data)
    df["datetime"] = pd.to_datetime(df["hour"], unit="s")
    return (
        alt.Chart(df)
        .mark_line(point=True, color="#00b4d8")
        .encode(
            x=alt.X("datetime:T", title="Time"),
            y=alt.Y("count:Q", title="People Count"),
            tooltip=["datetime:T", "count:Q"],
        )
        .properties(height=250)
        .interactive()
    )


def zone_dwell_bar(summaries: list[dict]) -> go.Figure:
    if not summaries:
        return go.Figure()
    zones = [s["zone_id"] for s in summaries]
    avg_dwells = [s["avg_dwell_seconds"] for s in summaries]
    fig = go.Figure(go.Bar(x=zones, y=avg_dwells, marker_color="#0077b6"))
    fig.update_layout(
        xaxis_title="Zone",
        yaxis_title="Avg Dwell (seconds)",
        height=300,
        margin=dict(l=40, r=20, t=30, b=40),
    )
    return fig
