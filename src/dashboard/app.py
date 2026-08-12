import streamlit as st
import requests

from .components.nav import render_brand, render_customer_nav, render_admin_nav, render_user_badge
from .components.theme import inject_global_styles
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
        page_title="Heat Map — Retail Analytics",
        page_icon="🗺️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_global_styles()

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
        render_brand()

        if role == "customer":
            shops = _fetch_shops(api_url, token)
            if not shops:
                st.warning("No shops assigned to your account yet. Contact an admin.")
            else:
                shop_map = {s["name"]: s for s in shops}
                st.markdown(
                    '<p style="font-size:0.75rem;color:#64748b;text-transform:uppercase;'
                    'letter-spacing:0.05em;margin-bottom:0.25rem;">'
                    '<span class="hm-icon" style="font-size:1rem;">store</span> Shop</p>',
                    unsafe_allow_html=True,
                )
                chosen = st.selectbox("Shop", list(shop_map.keys()), label_visibility="collapsed")
                camera_ids = shop_map[chosen]["camera_ids"]

            st.divider()
            page = render_customer_nav()
        else:
            st.divider()
            page = render_admin_nav()

        st.divider()
        render_user_badge(st.session_state.get("email", ""))
        if st.button("Logout", use_container_width=True, type="primary"):
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
