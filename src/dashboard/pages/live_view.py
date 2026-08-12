import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh

from ..components.heatmap_widget import show_heatmap
from ..components.theme import page_header, panel_title


def render(api_base_url: str, refresh_ms: int = 1000, camera_ids: list[str] | None = None) -> None:
    page_header("Live Store View", "Real-time camera feeds and heat map overlays", "broadcast")
    st_autorefresh(interval=refresh_ms, key="live_refresh")

    try:
        health = requests.get(f"{api_base_url}/health", timeout=2).json()
        all_cameras = health.get("cameras", [])
        queued = health.get("total_events_queued", 0)
    except Exception:
        st.error("Pipeline API is not running. Start it with: python scripts/run_pipeline.py")
        return

    cameras = [c for c in all_cameras if c in camera_ids] if camera_ids else all_cameras
    if not cameras:
        st.warning("No cameras active for this shop.")
        return

    selected = st.selectbox("Camera", cameras) if len(cameras) > 1 else cameras[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Active Cameras", len(cameras))
    col2.metric("Events Queued", queued)
    col3.metric("Selected Camera", selected)

    left, right = st.columns(2)
    with left:
        panel_title("Camera Feed", "videocam")
        st.markdown(
            f'<div class="hm-stream-frame">'
            f'<img src="{api_base_url}/stream/{selected}" width="100%" alt="Live camera feed">'
            f"</div>",
            unsafe_allow_html=True,
        )
    with right:
        panel_title("Heat Map Overlay", "whatshot")
        show_heatmap(api_base_url, camera_id=selected)
