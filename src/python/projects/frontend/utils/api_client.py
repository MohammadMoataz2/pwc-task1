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
        try:
            error_detail = response.json().get("detail", "Authentication failed")
            if "Incorrect username or password" in error_detail:
                st.error("❌ **Invalid Credentials!** The username or password you entered is incorrect.")
            else:
                st.error("🔒 **Authentication Required!** Please login again.")
        except:
            st.error("🔒 **Authentication Failed!** Please check your credentials.")

        # Clear session state
        from config import SESSION_TOKEN_KEY, SESSION_USER_KEY
        if SESSION_TOKEN_KEY in st.session_state:
            del st.session_state[SESSION_TOKEN_KEY]
        if SESSION_USER_KEY in st.session_state:
            del st.session_state[SESSION_USER_KEY]
        st.rerun()
    elif response.status_code == 422:
        try:
            error_detail = response.json().get("detail", "Validation error")
            if isinstance(error_detail, list):
                # Handle validation errors from FastAPI
                errors = []
                for error in error_detail:
                    field = " -> ".join(error.get("loc", []))
                    msg = error.get("msg", "Invalid value")
                    errors.append(f"**{field}**: {msg}")
                st.error("❌ **Validation Error:**\n" + "\n".join(errors))
            else:
                st.error(f"❌ **Validation Error:** {error_detail}")
        except:
            st.error("❌ **Validation Error:** Please check your input.")
    elif response.status_code == 404:
        st.error("❌ **Not Found:** The requested resource was not found.")
    elif response.status_code == 500:
        st.error("❌ **Server Error:** Something went wrong on our end. Please try again later.")
    else:
        try:
            error_msg = response.json().get("detail", f"Request failed with status {response.status_code}")
            st.error(f"❌ **Error:** {error_msg}")
        except:
            st.error(f"❌ **Error:** Request failed with status {response.status_code}")

    return None