"""Registration page"""

import streamlit as st
from utils.auth import register, is_authenticated

st.set_page_config(
    page_title="Register - PWC Contract Analysis",
    page_icon="📝",
    layout="centered"
)

# Redirect if already authenticated
if is_authenticated():
    st.info("You are already logged in!")
    st.switch_page("pages/3_📋_Contracts.py")

st.title("📝 Register")
st.markdown("Create a new account for PWC Contract Analysis System")

with st.form("register_form"):
    st.subheader("Create Account")

    username = st.text_input("Username", placeholder="Choose a username")
    email = st.text_input("Email", placeholder="Enter your email (optional)")
    password = st.text_input("Password", type="password", placeholder="Choose a password")
    confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")

    col1, col2 = st.columns(2)

    with col1:
        register_btn = st.form_submit_button("Register", type="primary", use_container_width=True)

    with col2:
        if st.form_submit_button("Login Instead", use_container_width=True):
            st.switch_page("pages/1_🔐_Login.py")

if register_btn:
    if not username or not password:
        st.error("Please enter both username and password")
    elif password != confirm_password:
        st.error("Passwords do not match")
    elif len(password) < 6:
        st.error("Password must be at least 6 characters long")
    else:
        with st.spinner("Creating account..."):
            if register(username, password, email):
                st.balloons()
                if st.button("Go to Login"):
                    st.switch_page("pages/1_🔐_Login.py")

# Registration guidelines
with st.expander("Registration Guidelines"):
    st.info("""
    **Password Requirements:**
    - Minimum 6 characters
    - Mix of letters and numbers recommended

    **Username Guidelines:**
    - Unique username required
    - Alphanumeric characters preferred
    """)