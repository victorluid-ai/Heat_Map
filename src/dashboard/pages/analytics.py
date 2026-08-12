import streamlit as st
import requests
import time
from datetime import datetime, timedelta

from ..components.chart_helpers import traffic_line_chart, zone_dwell_bar
from ..components.theme import filter_bar_end, filter_bar_start, page_header, panel_title


def render(api_base_url: str, camera_ids: list[str] | None = None) -> None:
    page_header("Analytics & Insights", "Traffic patterns and zone dwell-time analysis", "analytics")

    filter_bar_start()
    col1, col2 = st.columns(2)
    with col1:
        camera_id: str | None = None
        if camera_ids:
            chosen = st.selectbox("Camera", ["All cameras"] + camera_ids)
            if chosen != "All cameras":
                camera_id = chosen
    with col2:
        period = st.selectbox("Period", ["Last 24 hours", "Last 7 days", "Last 30 days"])
    filter_bar_end()

    hours_map = {"Last 24 hours": 24, "Last 7 days": 168, "Last 30 days": 720}
    hours = hours_map[period]
    end_ts = time.time()
    start_ts = end_ts - hours * 3600

    panel_title("Hourly Traffic", "timeline")
    try:
        params = {"start": start_ts, "end": end_ts}
        if camera_id:
            params["camera_id"] = camera_id
        resp = requests.get(f"{api_base_url}/analytics/traffic", params=params, timeout=5)
        if resp.status_code == 200 and resp.json():
            st.altair_chart(traffic_line_chart(resp.json()), use_container_width=True)
        else:
            st.info("No traffic data yet. Run the pipeline to collect data.")
    except Exception as e:
        st.warning(f"Traffic data unavailable: {e}")

    st.divider()
    panel_title("Zone Dwell Times", "place")
    zones = st.text_input("Zone IDs (comma-separated)", value="entrance,checkout,aisle_1")
    zone_list = [z.strip() for z in zones.split(",") if z.strip()]
    summaries = []
    for zone in zone_list:
        try:
            resp = requests.get(
                f"{api_base_url}/analytics/dwell",
                params={"zone_id": zone, "start": start_ts, "end": end_ts},
                timeout=3,
            )
            if resp.status_code == 200:
                summaries.append(resp.json())
        except Exception:
            pass
    if summaries:
        st.plotly_chart(zone_dwell_bar(summaries), use_container_width=True)
    else:
        st.info("No dwell data yet.")
