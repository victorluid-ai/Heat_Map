import streamlit as st
import time
from datetime import datetime, timedelta
from ..components.heatmap_widget import show_historical_heatmap
from ..components.chart_helpers import traffic_line_chart
import requests


def render(api_base_url: str, camera_ids: list[str] | None = None) -> None:
    st.title("Historical Analysis")

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From", value=datetime.now() - timedelta(days=1))
    with col2:
        end_date = st.date_input("To", value=datetime.now())

    if camera_ids:
        camera_id = st.selectbox("Camera", ["All cameras"] + camera_ids)
        if camera_id == "All cameras":
            camera_id = None
    else:
        camera_id = st.text_input("Camera ID (leave blank for all)", value="")
        if not camera_id:
            camera_id = None

    start_ts = float(datetime.combine(start_date, datetime.min.time()).timestamp())
    end_ts = float(datetime.combine(end_date, datetime.max.time()).timestamp())

    if st.button("Generate Heat Map"):
        with st.spinner("Rendering heat map..."):
            show_historical_heatmap(api_base_url, start_ts, end_ts, camera_id)

    st.divider()
    st.subheader("Traffic Over Time")
    try:
        resp = requests.get(
            f"{api_base_url}/analytics/traffic",
            params={"start": start_ts, "end": end_ts, **({"camera_id": camera_id} if camera_id else {})},
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data:
                st.altair_chart(traffic_line_chart(data), use_container_width=True)
            else:
                st.info("No traffic data for the selected period.")
    except Exception as e:
        st.warning(f"Could not load traffic data: {e}")
