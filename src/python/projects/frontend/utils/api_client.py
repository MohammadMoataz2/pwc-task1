"""API client utilities"""

import requests
import streamlit as st
from typing import Optional, Dict, Any
from config import get_api_url, get_auth_headers


class APIClient:
    """Client for interacting with the PWC Contract Analysis API"""

    @staticmethod
    def post(endpoint: str, data: Optional[Dict] = None, files: Optional[Dict] = None) -> requests.Response:
        """Make POST request to API"""
        url = get_api_url(endpoint)
        headers = get_auth_headers()

        try:
            response = requests.post(url, json=data, files=files, headers=headers)
            return response
        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {str(e)}")
            raise

    @staticmethod
    def get(endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        """Make GET request to API"""
        url = get_api_url(endpoint)
        headers = get_auth_headers()

        try:
            response = requests.get(url, params=params, headers=headers)
            return response
        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {str(e)}")
            raise

    @staticmethod
    def upload_file(endpoint: str, file_data: bytes, filename: str, additional_data: Optional[Dict] = None) -> requests.Response:
        """Upload file to API"""
        url = get_api_url(endpoint)
        headers = get_auth_headers()

        files = {"file": (filename, file_data, "application/pdf")}
        data = additional_data or {}

        try:
            response = requests.post(url, files=files, data=data, headers=headers)
            return response
        except requests.exceptions.RequestException as e:
            st.error(f"File upload failed: {str(e)}")
            raise


def handle_api_response(response: requests.Response) -> Optional[Dict[str, Any]]:
    """Handle API response and show appropriate messages"""
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        st.error("Authentication failed. Please login again.")
        # Clear session state
        if "auth_token" in st.session_state:
            del st.session_state["auth_token"]
        if "user_info" in st.session_state:
            del st.session_state["user_info"]
        st.rerun()
    elif response.status_code == 422:
        error_detail = response.json().get("detail", "Validation error")
        st.error(f"Validation error: {error_detail}")
    else:
        error_msg = response.json().get("detail", f"Request failed with status {response.status_code}")
        st.error(f"Error: {error_msg}")

    return None