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
    page_header("Shop Management", "Create, view, and manage retail locations", "storefront")

    try:
        shops_resp = _api("GET", "/admin/shops", token, api_url)
        shops_resp.raise_for_status()
        shops: list[dict] = shops_resp.json()
    except Exception as e:
        st.error(f"Failed to load shops: {e}")
        return

    try:
        users_resp = _api("GET", "/admin/users", token, api_url)
        users_resp.raise_for_status()
        users: list[dict] = users_resp.json()
    except Exception as e:
        st.error(f"Failed to load users: {e}")
        return

    if shops:
        panel_title("All Shops", "table_rows")
        df = pd.DataFrame(
            [
                {
                    "Name": s["name"],
                    "Owner": s["owner_email"],
                    "Address": s["address"] or "",
                    "Cameras": s["camera_count"],
                }
                for s in shops
            ]
        )
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()
        panel_title("Delete Shop", "delete")
        for s in shops:
            col_name, col_btn = st.columns([3, 1])
            col_name.write(s["name"])
            if col_btn.button("Delete", key=f"del_shop_{s['id']}"):
                try:
                    r = _api("DELETE", f"/admin/shops/{s['id']}", token, api_url)
                    r.raise_for_status()
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to delete shop '{s['name']}': {e}")
    else:
        st.info("No shops found.")

    owner_map = {u["email"]: u["id"] for u in users}

    with st.expander("Create Shop", icon="➕"):
        with st.form("create_shop_form"):
            name = st.text_input("Shop Name")
            address = st.text_input("Address (optional)")
            owner_email = st.selectbox("Owner", list(owner_map.keys()))
            submitted = st.form_submit_button("Create", use_container_width=True, type="primary")
        if submitted:
            if not name:
                st.error("Shop name is required.")
            else:
                try:
                    r = _api(
                        "POST",
                        "/admin/shops",
                        token,
                        api_url,
                        json={
                            "name": name,
                            "address": address or None,
                            "owner_id": owner_map[owner_email],
                        },
                    )
                    r.raise_for_status()
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to create shop: {e}")
