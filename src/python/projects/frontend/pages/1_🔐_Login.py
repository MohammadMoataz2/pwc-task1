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

# Add info about session persistence
st.info("💡 **Note:** Due to Streamlit's architecture, you'll need to log in again after refreshing the page. We recommend avoiding page refreshes during your session.")

with st.form("login_form"):
    st.subheader("Sign In")

    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")

    remember_me = st.checkbox("Remember me (keeps you logged in after page refresh)", value=False)

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
            login_success = login(username, password, remember_me)
            if login_success:
                st.success("Login successful! Redirecting...")
                st.rerun()
            else:
                st.error("❌ **Login Failed!** Invalid username or password. Please try again.")
                st.info("💡 Check your credentials and try again. If you don't have an account, please register first.")

# Demo credentials info
with st.expander("Demo Credentials"):
    st.info("""
    **Demo Account:**
    - Username: `admin`
    - Password: `admin123`

    Or register a new account using the Register page.
    """)