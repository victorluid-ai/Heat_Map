import streamlit as st
import requests


def render(api_url: str) -> None:
    st.markdown(
        """
        <div class="hm-login-card">
            <div class="hm-login-brand">
                <span class="hm-icon" style="font-size:2.5rem;display:block;margin-bottom:0.5rem;">map</span>
                <h1>Heat Map</h1>
                <p style="color:#94a3b8;margin:0;">Retail foot-traffic analytics platform</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_left, col_center, col_right = st.columns([1, 1.2, 1])
    with col_center:
        tab_login, tab_register = st.tabs(["Login", "Create Account"])

        with tab_login:
            with st.form("login_form"):
                st.markdown(
                    '<p style="color:#94a3b8;font-size:0.85rem;margin-bottom:1rem;">'
                    '<span class="hm-icon">login</span> Sign in to your account</p>',
                    unsafe_allow_html=True,
                )
                email = st.text_input("Email", placeholder="you@company.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")
            if submitted:
                _do_login(api_url, email, password)

        with tab_register:
            with st.form("register_form"):
                st.markdown(
                    '<p style="color:#94a3b8;font-size:0.85rem;margin-bottom:1rem;">'
                    '<span class="hm-icon">person_add</span> Create a new account</p>',
                    unsafe_allow_html=True,
                )
                new_email = st.text_input("Email", key="reg_email", placeholder="you@company.com")
                new_pass = st.text_input("Password", type="password", key="reg_pass", placeholder="••••••••")
                confirm = st.text_input("Confirm Password", type="password", key="reg_confirm", placeholder="••••••••")
                submitted_reg = st.form_submit_button("Create Account", use_container_width=True, type="primary")
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
