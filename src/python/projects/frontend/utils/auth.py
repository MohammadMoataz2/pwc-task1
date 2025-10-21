"""Authentication utilities"""

import streamlit as st
import json
import base64
from typing import Optional, Dict, Any
from config import SESSION_TOKEN_KEY, SESSION_USER_KEY
from utils.api_client import APIClient, handle_api_response


def check_persistent_auth():
    """Check and restore persistent authentication if available"""
    if SESSION_TOKEN_KEY not in st.session_state and "persistent_auth" in st.session_state:
        try:
            # Decode stored auth data
            encoded_data = st.session_state["persistent_auth"]
            auth_data = json.loads(base64.b64decode(encoded_data.encode()).decode())

            # Verify token is still valid by making a test API call
            import requests
            from config import API_BASE_URL

            headers = {"Authorization": f"Bearer {auth_data['token']}"}
            # Health endpoint is at root level, not /api/v1
            test_response = requests.get(f"{API_BASE_URL}/healthz", headers=headers)

            if test_response.status_code == 200:
                # Token is still valid, restore session
                st.session_state[SESSION_TOKEN_KEY] = auth_data["token"]
                st.session_state[SESSION_USER_KEY] = {
                    "username": auth_data["username"],
                    "token_type": "bearer"
                }
                return True
            else:
                # Token expired, clear persistent auth
                del st.session_state["persistent_auth"]
                return False

        except Exception as e:
            # Clear invalid persistent auth
            if "persistent_auth" in st.session_state:
                del st.session_state["persistent_auth"]
            return False
    return False


def is_authenticated() -> bool:
    """Check if user is authenticated"""
    # First check current session
    if SESSION_TOKEN_KEY in st.session_state and st.session_state[SESSION_TOKEN_KEY] is not None:
        return True

    # Try to restore from persistent auth
    return check_persistent_auth()


def get_current_user() -> Optional[Dict[str, Any]]:
    """Get current user information"""
    return st.session_state.get(SESSION_USER_KEY)


def login(username: str, password: str, remember_me: bool = False) -> bool:
    """Login user and store token"""
    try:
        # OAuth2PasswordRequestForm expects form data, not JSON
        import requests
        from config import get_api_url

        url = get_api_url("/auth/login")
        form_data = {
            "username": username,
            "password": password,
            "grant_type": "password"
        }

        response = requests.post(url, data=form_data)

        if response.status_code == 200:
            data = response.json()
            token = data["access_token"]
            user_info = {
                "username": username,
                "token_type": data.get("token_type", "bearer")
            }

            # Store in session state
            st.session_state[SESSION_TOKEN_KEY] = token
            st.session_state[SESSION_USER_KEY] = user_info

            # If remember me is checked, store credentials in a more persistent way
            if remember_me:
                # Store encoded auth data in session state with a special key
                auth_data = {
                    "username": username,
                    "token": token
                }
                # Encode to avoid direct password storage
                encoded_data = base64.b64encode(json.dumps(auth_data).encode()).decode()
                st.session_state["persistent_auth"] = encoded_data

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
    if "persistent_auth" in st.session_state:
        del st.session_state["persistent_auth"]
    st.success("Logged out successfully!")
    st.rerun()


def require_auth():
    """Decorator/function to require authentication"""
    if not is_authenticated():
        st.warning("Please login to access this page.")
        st.stop()