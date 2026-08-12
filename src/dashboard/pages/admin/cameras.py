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
    page_header("Camera Management", "Assign cameras to shops and monitor status", "videocam")

    try:
        cams_resp = _api("GET", "/admin/cameras", token, api_url)
        cams_resp.raise_for_status()
        cameras: list[dict] = cams_resp.json()
    except Exception as e:
        st.error(f"Failed to load cameras: {e}")
        return

    try:
        shops_resp = _api("GET", "/admin/shops", token, api_url)
        shops_resp.raise_for_status()
        shops: list[dict] = shops_resp.json()
    except Exception as e:
        st.error(f"Failed to load shops: {e}")
        return

    if cameras:
        panel_title("All Cameras", "table_rows")
        df = pd.DataFrame(
            [
                {
                    "ID": c["id"],
                    "Name": c["name"],
                    "Active": c["is_active"],
                    "Current Shop": c["shop_name"] or "Unassigned",
                }
                for c in cameras
            ]
        )
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No cameras found.")
        return

    shop_options = {"Unassigned": None, **{s["name"]: s["id"] for s in shops}}
    shop_names = list(shop_options.keys())

    st.divider()
    panel_title("Assign Cameras", "link")
    for c in cameras:
        current_label = c["shop_name"] if c["shop_name"] else "Unassigned"
        default_idx = shop_names.index(current_label) if current_label in shop_names else 0

        col_name, col_select, col_btn = st.columns([2, 2, 1])
        col_name.write(f"**{c['name']}** (`{c['id']}`)")
        selected_shop = col_select.selectbox(
            "Shop",
            shop_names,
            index=default_idx,
            key=f"shop_sel_{c['id']}",
            label_visibility="collapsed",
        )
        if col_btn.button("Assign", key=f"assign_{c['id']}"):
            try:
                r = _api(
                    "PATCH",
                    f"/admin/cameras/{c['id']}",
                    token,
                    api_url,
                    json={"shop_id": shop_options[selected_shop]},
                )
                r.raise_for_status()
                st.rerun()
            except Exception as e:
                st.error(f"Failed to assign camera '{c['name']}': {e}")
