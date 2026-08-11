import streamlit as st
import requests


def render(api_url: str) -> None:
    st.title("Retail Heat Map")
    st.markdown("Please log in to view your shop analytics.")

    tab_login, tab_register = st.tabs(["Login", "Create Account"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
        if submitted:
            _do_login(api_url, email, password)

    with tab_register:
        with st.form("register_form"):
            new_email = st.text_input("Email", key="reg_email")
            new_pass = st.text_input("Password", type="password", key="reg_pass")
            confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")
            submitted_reg = st.form_submit_button("Create Account", use_container_width=True)
        if submitted_reg:
            if new_pass != confirm:
                st.error("Passwords do not match")
            else:
                _do_register(api_url, new_email, new_pass)


def _do_login(api_url: str, email: str, password: str) -> None:
    try:
        resp = requests.post(f"{api_url}/auth/login", json={"email": email, "password": password}, timeout=5)
    except Exception as e:
        st.error(f"Could not reach API: {e}")
        return
    if resp.status_code == 200:
        st.session_state["token"] = resp.json()["access_token"]
        st.session_state["email"] = email
        st.rerun()
    else:
        st.error(resp.json().get("detail", "Login failed"))


def _do_register(api_url: str, email: str, password: str) -> None:
    try:
        resp = requests.post(f"{api_url}/auth/register", json={"email": email, "password": password}, timeout=5)
    except Exception as e:
        st.error(f"Could not reach API: {e}")
        return
    if resp.status_code == 201:
        st.session_state["token"] = resp.json()["access_token"]
        st.session_state["email"] = email
        st.rerun()
    else:
        st.error(resp.json().get("detail", "Registration failed"))
