import altair as alt
import pandas as pd
import plotly.graph_objects as go

from ..design.tokens import BG_ELEVATED, CHART_BAR, CHART_GRID, CHART_LINE, TEXT_PRIMARY, TEXT_SECONDARY


def traffic_line_chart(hourly_data: list[dict]) -> alt.Chart:
    if not hourly_data:
        return alt.Chart(pd.DataFrame({"hour": [], "count": []})).mark_line()
    df = pd.DataFrame(hourly_data)
    df["datetime"] = pd.to_datetime(df["hour"], unit="s")
    return (
        alt.Chart(df)
        .mark_line(point=True, color=CHART_LINE, strokeWidth=2)
        .encode(
            x=alt.X("datetime:T", title="Time", axis=alt.Axis(labelColor=TEXT_SECONDARY, titleColor=TEXT_SECONDARY)),
            y=alt.Y("count:Q", title="People Count", axis=alt.Axis(labelColor=TEXT_SECONDARY, titleColor=TEXT_SECONDARY)),
            tooltip=["datetime:T", "count:Q"],
        )
        .properties(height=280, background=BG_ELEVATED)
        .configure_view(strokeWidth=0)
        .configure_axis(gridColor=CHART_GRID, domainColor=CHART_GRID)
        .interactive()
    )


def zone_dwell_bar(summaries: list[dict]) -> go.Figure:
    if not summaries:
        return go.Figure()
    zones = [s["zone_id"] for s in summaries]
    avg_dwells = [s["avg_dwell_seconds"] for s in summaries]
    fig = go.Figure(go.Bar(x=zones, y=avg_dwells, marker_color=CHART_BAR, marker_line_width=0))
    fig.update_layout(
        xaxis_title="Zone",
        yaxis_title="Avg Dwell (seconds)",
        height=320,
        margin=dict(l=40, r=20, t=30, b=40),
        paper_bgcolor=BG_ELEVATED,
        plot_bgcolor=BG_ELEVATED,
        font=dict(color=TEXT_PRIMARY),
        xaxis=dict(gridcolor=CHART_GRID, linecolor=CHART_GRID),
        yaxis=dict(gridcolor=CHART_GRID, linecolor=CHART_GRID),
    )
    return fig
