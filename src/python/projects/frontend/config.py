"""Frontend configuration"""

import os
from typing import Optional

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://api:8000")
API_V1_PREFIX = "/api/v1"

# Page Configuration
PAGE_TITLE = "PWC Contract Analysis System"
PAGE_ICON = "📋"
LAYOUT = "wide"

# Session State Keys
SESSION_TOKEN_KEY = "auth_token"
SESSION_USER_KEY = "user_info"

def get_api_url(endpoint: str) -> str:
    """Get full API URL for endpoint"""
    return f"{API_BASE_URL}{API_V1_PREFIX}{endpoint}"

def get_auth_headers() -> dict:
    """Get authentication headers from session state"""
    import streamlit as st

    token = st.session_state.get(SESSION_TOKEN_KEY)
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}