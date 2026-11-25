import hashlib
import hmac
import streamlit as st

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "123"

_SALT = "80c3b64bbf3cb810"
_HASH = hashlib.sha256((_SALT + ADMIN_PASSWORD).encode()).hexdigest()


def is_admin_authenticated() -> bool:
    return bool(st.session_state.get("admin_ok", False))


def logout_admin():
    st.session_state["admin_ok"] = False
    st.session_state.pop("admin_user", None)
    st.rerun()


def render_logout_button():
    if is_admin_authenticated():
        with st.sidebar:
            st.markdown("---")
            current_user = st.session_state.get("admin_user", ADMIN_USERNAME)
            st.caption(f"👤 Signed in as: **{current_user}**")
            if st.button("🚪 Log Out", use_container_width=True, key="admin_logout_btn"):
                logout_admin()


def require_admin():
    """Block the page until valid admin username and password are entered."""
    if is_admin_authenticated():
        return

    st.markdown("## 🔒 Admin access")
    st.write("This page is for administrators only. Enter your username and password to continue.")

    with st.form("admin_login"):
        username = st.text_input("Username")
        pw = st.text_input("Admin password", type="password")
        go = st.form_submit_button("Sign in")

    if go:
        digest = hashlib.sha256((_SALT + pw).encode()).hexdigest()
        valid_user = username.strip() == ADMIN_USERNAME
        valid_pw = hmac.compare_digest(digest, _HASH)

        if valid_user and valid_pw:
            st.session_state["admin_ok"] = True
            st.session_state["admin_user"] = ADMIN_USERNAME
            st.rerun()
        else:
            st.error("Wrong username or password.")

    st.stop()