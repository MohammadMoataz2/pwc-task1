"""Login page"""

import streamlit as st
from utils.auth import login, is_authenticated

st.set_page_config(
    page_title="Login - PWC Contract Analysis",
    page_icon="🔐",
    layout="centered"
)

# Redirect if already authenticated
if is_authenticated():
    st.info("You are already logged in!")
    st.switch_page("pages/3_📋_Contracts.py")

st.title("🔐 Login")
st.markdown("Welcome to PWC Contract Analysis System")

with st.form("login_form"):
    st.subheader("Sign In")

    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")

    col1, col2 = st.columns(2)

    with col1:
        login_btn = st.form_submit_button("Login", type="primary", use_container_width=True)

    with col2:
        if st.form_submit_button("Register Instead", use_container_width=True):
            st.switch_page("pages/2_📝_Register.py")

if login_btn:
    if not username or not password:
        st.error("Please enter both username and password")
    else:
        with st.spinner("Logging in..."):
            if login(username, password):
                st.rerun()

# Demo credentials info
with st.expander("Demo Credentials"):
    st.info("""
    **Demo Account:**
    - Username: `admin`
    - Password: `admin123`

    Or register a new account using the Register page.
    """)