"""Authentication utilities"""

import streamlit as st
from typing import Optional, Dict, Any
from config import SESSION_TOKEN_KEY, SESSION_USER_KEY
from utils.api_client import APIClient, handle_api_response


def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return SESSION_TOKEN_KEY in st.session_state and st.session_state[SESSION_TOKEN_KEY] is not None


def get_current_user() -> Optional[Dict[str, Any]]:
    """Get current user information"""
    return st.session_state.get(SESSION_USER_KEY)


def login(username: str, password: str) -> bool:
    """Login user and store token"""
    try:
        response = APIClient.post("/auth/login", {
            "username": username,
            "password": password
        })

        if response.status_code == 200:
            data = response.json()
            st.session_state[SESSION_TOKEN_KEY] = data["access_token"]
            st.session_state[SESSION_USER_KEY] = {
                "username": username,
                "token_type": data.get("token_type", "bearer")
            }
            st.success("Login successful!")
            return True
        else:
            handle_api_response(response)
            return False

    except Exception as e:
        st.error(f"Login failed: {str(e)}")
        return False


def register(username: str, password: str, email: str = "") -> bool:
    """Register new user"""
    try:
        response = APIClient.post("/auth/register", {
            "username": username,
            "password": password,
            "email": email
        })

        if response.status_code == 200:
            st.success("Registration successful! Please login.")
            return True
        else:
            handle_api_response(response)
            return False

    except Exception as e:
        st.error(f"Registration failed: {str(e)}")
        return False


def logout():
    """Logout user and clear session"""
    if SESSION_TOKEN_KEY in st.session_state:
        del st.session_state[SESSION_TOKEN_KEY]
    if SESSION_USER_KEY in st.session_state:
        del st.session_state[SESSION_USER_KEY]
    st.success("Logged out successfully!")
    st.rerun()


def require_auth():
    """Decorator/function to require authentication"""
    if not is_authenticated():
        st.warning("Please login to access this page.")
        st.stop()