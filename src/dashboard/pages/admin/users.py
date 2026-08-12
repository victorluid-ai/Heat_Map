import streamlit as st
import requests
import pandas as pd

from ...components.theme import page_header, panel_title


def _api(method: str, path: str, token: str, api_url: str, **kwargs):
    return requests.request(
        method,
        f"{api_url}{path}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=5,
        **kwargs,
    )


def render(api_url: str, token: str) -> None:
    page_header("User Management", "Manage accounts, roles, and access status", "group")

    try:
        resp = _api("GET", "/admin/users", token, api_url)
        resp.raise_for_status()
        users: list[dict] = resp.json()
    except Exception as e:
        st.error(f"Failed to load users: {e}")
        return

    if not users:
        st.info("No users found.")
        return

    panel_title("All Users", "table_rows")
    df = pd.DataFrame(
        [
            {
                "Email": u["email"],
                "Role": u["role"],
                "Active": u["is_active"],
                "Shops": u["shop_count"],
            }
            for u in users
        ]
    )
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()
    panel_title("Toggle User Status", "toggle_on")
    for u in users:
        col_email, col_btn = st.columns([3, 1])
        col_email.write(u["email"])
        label = "Deactivate" if u["is_active"] else "Activate"
        if col_btn.button(label, key=f"toggle_{u['id']}"):
            try:
                r = _api(
                    "PATCH",
                    f"/admin/users/{u['id']}",
                    token,
                    api_url,
                    json={"is_active": not u["is_active"]},
                )
                r.raise_for_status()
                st.rerun()
            except Exception as e:
                st.error(f"Failed to update user {u['email']}: {e}")
