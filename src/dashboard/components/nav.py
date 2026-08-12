from dataclasses import dataclass

from streamlit_option_menu import option_menu

from ..design.tokens import (
    ACCENT_PRIMARY,
    BG_ELEVATED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


@dataclass(frozen=True)
class NavItem:
    label: str
    icon: str


CUSTOMER_NAV: list[NavItem] = [
    NavItem("Live View", "broadcast"),
    NavItem("Historical Analysis", "history"),
    NavItem("Analytics", "analytics"),
]

ADMIN_NAV: list[NavItem] = [
    NavItem("Users", "group"),
    NavItem("Shops", "storefront"),
    NavItem("Cameras", "videocam"),
    NavItem("Live View", "broadcast"),
    NavItem("Historical Analysis", "history"),
    NavItem("Analytics", "analytics"),
]

_NAV_STYLES = {
    "container": {"padding": "0", "background-color": "transparent"},
    "icon": {"color": ACCENT_PRIMARY, "font-size": "18px"},
    "nav-link": {
        "font-size": "14px",
        "font-weight": "500",
        "color": TEXT_SECONDARY,
        "padding": "10px 14px",
        "margin": "2px 0",
        "border-radius": "8px",
    },
    "nav-link-selected": {
        "background-color": BG_ELEVATED,
        "color": TEXT_PRIMARY,
        "font-weight": "600",
        "border": f"1px solid {ACCENT_PRIMARY}",
    },
}


def _render_menu(title: str, items: list[NavItem], menu_icon: str, key: str) -> str:
    return option_menu(
        menu_title=title,
        options=[item.label for item in items],
        icons=[item.icon for item in items],
        menu_icon=menu_icon,
        default_index=0,
        key=key,
        styles=_NAV_STYLES,
    )


def render_customer_nav() -> str:
    return _render_menu("Navigation", CUSTOMER_NAV, "map", "customer_nav")


def render_admin_nav() -> str:
    return _render_menu("Navigation", ADMIN_NAV, "admin_panel_settings", "admin_nav")


def render_brand() -> None:
    import streamlit as st

    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.25rem;">
            <span class="hm-icon" style="font-size:1.75rem;">map</span>
            <div>
                <div style="font-size:1.25rem;font-weight:700;background:linear-gradient(135deg,#00d4ff,#7c3aed);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;">Heat Map</div>
                <div class="hm-brand-subtitle">Retail Analytics</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_user_badge(email: str) -> None:
    import streamlit as st

    st.markdown(
        f"""
        <div class="hm-user-badge">
            <span class="hm-icon">account_circle</span>
            <span>{email}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
