import streamlit as st
import requests
from PIL import Image
import io


def show_heatmap(api_base_url: str, camera_id: str = "cam_0", caption: str = "Live Heat Map") -> None:
    url = f"{api_base_url}/heatmap/live?camera_id={camera_id}"
    try:
        resp = requests.get(url, timeout=3)
        if resp.status_code == 200:
            img = Image.open(io.BytesIO(resp.content))
            st.image(img, caption=caption, use_container_width=True)
        else:
            st.warning(f"Heat map unavailable (HTTP {resp.status_code})")
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to API. Is the pipeline running?")


def show_historical_heatmap(api_base_url: str, start: float, end: float,
                             camera_id: str | None = None, caption: str = "Historical Heat Map") -> None:
    params = f"start={start:.0f}&end={end:.0f}"
    if camera_id:
        params += f"&camera_id={camera_id}"
    url = f"{api_base_url}/heatmap/historical?{params}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            img = Image.open(io.BytesIO(resp.content))
            st.image(img, caption=caption, use_container_width=True)
        else:
            st.warning(f"Historical heat map unavailable (HTTP {resp.status_code})")
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to API. Is the pipeline running?")
