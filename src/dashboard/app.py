import streamlit as st
import requests
from .pages import live_view, historical, analytics, login
from .pages.admin import users as admin_users, shops as admin_shops, cameras as admin_cameras
from ..utils.config import load_config


def _fetch_shops(api_url: str, token: str) -> list[dict]:
    try:
        resp = requests.get(
            f"{api_url}/shops",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
        return resp.json() if resp.status_code == 200 else []
    except Exception:
        return []


def _fetch_role(api_url: str, token: str) -> str:
    try:
        resp = requests.get(
            f"{api_url}/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
        if resp.status_code == 200:
            return resp.json().get("role", "customer")
    except Exception:
        pass
    return "customer"


def main() -> None:
    st.set_page_config(
        page_title="Retail Heat Map",
        page_icon="🗺️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    cfg = load_config()
    api_url = cfg["dashboard"]["api_base_url"]
    refresh_ms = cfg["dashboard"]["refresh_interval_ms"]

    if "token" not in st.session_state:
        login.render(api_url)
        return

    token = st.session_state["token"]

    if "role" not in st.session_state:
        st.session_state["role"] = _fetch_role(api_url, token)

    role = st.session_state["role"]

    camera_ids: list[str] = []

    with st.sidebar:
        st.title("Retail Heat Map")

        if role == "customer":
            shops = _fetch_shops(api_url, token)
            if not shops:
                st.warning("No shops assigned to your account yet. Contact an admin.")
            else:
                shop_map = {s["name"]: s for s in shops}
                chosen = st.selectbox("Shop", list(shop_map.keys()))
                camera_ids = shop_map[chosen]["camera_ids"]

            st.divider()
            page = st.radio("Navigation", ["Live View", "Historical Analysis", "Analytics"])

        else:
            st.divider()
            page = st.radio(
                "Navigation",
                ["Users", "Shops", "Cameras", "Live View", "Historical Analysis", "Analytics"],
            )

        st.divider()
        st.caption(f"Logged in as: {st.session_state.get('email', '')}")
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

    if role == "admin":
        if page == "Users":
            admin_users.render(api_url, token=token)
        elif page == "Shops":
            admin_shops.render(api_url, token=token)
        elif page == "Cameras":
            admin_cameras.render(api_url, token=token)
        elif page == "Live View":
            live_view.render(api_url, refresh_ms, camera_ids=camera_ids)
        elif page == "Historical Analysis":
            historical.render(api_url, camera_ids=camera_ids)
        elif page == "Analytics":
            analytics.render(api_url, camera_ids=camera_ids)
    else:
        if page == "Live View":
            live_view.render(api_url, refresh_ms, camera_ids=camera_ids)
        elif page == "Historical Analysis":
            historical.render(api_url, camera_ids=camera_ids)
        elif page == "Analytics":
            analytics.render(api_url, camera_ids=camera_ids)


if __name__ == "__main__":
    main()
