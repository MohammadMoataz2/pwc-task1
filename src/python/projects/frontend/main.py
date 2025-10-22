"""Main Streamlit application"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add the shared library to the Python path
current_dir = Path(__file__).parent
libs_path = current_dir.parent.parent / "libs"
sys.path.insert(0, str(libs_path))

from pwc.settings import settings
from config import PAGE_TITLE, PAGE_ICON, LAYOUT
from utils.auth import is_authenticated

# Print settings
print("=== STREAMLIT FRONTEND SETTINGS ===")
print(settings)
print("=== END STREAMLIT FRONTEND SETTINGS ===")

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }

    .feature-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }

    .metric-card {
        background: #e8f4f8;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown(f"""
<div class="main-header">
    <h1>{PAGE_ICON} {PAGE_TITLE}</h1>
    <p>AI-Powered Contract Analysis and Evaluation Platform</p>
</div>
""", unsafe_allow_html=True)

# Check authentication status
if is_authenticated():
    from utils.auth import get_current_user

    user = get_current_user()
    st.success(f"Welcome back, {user['username']}! 🎉")

    # Navigation guide
    st.markdown("### 🚀 Quick Navigation")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>📋 Contract Management</h4>
            <p>Upload, manage, and track your contracts</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Go to Contracts", key="nav_contracts", use_container_width=True):
            st.switch_page("pages/3_📋_Contracts.py")

    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>🤖 AI Analysis</h4>
            <p>Direct contract analysis and evaluation</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Go to AI Analysis", key="nav_ai", use_container_width=True):
            st.switch_page("pages/4_🤖_GenAI_Analysis.py")

    with col3:
        st.markdown("""
        <div class="feature-card">
            <h4>📊 Admin Dashboard</h4>
            <p>System metrics, logs, and monitoring</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Go to Dashboard", key="nav_dashboard", use_container_width=True):
            st.switch_page("pages/5_📊_Admin_Dashboard.py")

    # Recent activity (mock data)
    st.markdown("### 📈 Recent Activity")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>24</h3>
            <p>Contracts Analyzed Today</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>85%</h3>
            <p>Approval Rate</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>12</h3>
            <p>Active Clients</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>1.2s</h3>
            <p>Avg Response Time</p>
        </div>
        """, unsafe_allow_html=True)

    # Quick actions
    st.markdown("### ⚡ Quick Actions")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📤 Upload Contract")
        uploaded_file = st.file_uploader("Drop a PDF contract here", type=['pdf'], key="quick_upload")

        if uploaded_file:
            st.success(f"File '{uploaded_file.name}' ready for upload!")
            if st.button("Upload & Analyze", type="primary", use_container_width=True):
                st.switch_page("pages/3_📋_Contracts.py")

    with col2:
        st.subheader("🔍 System Status")

        # Quick health check
        try:
            import requests
            from config import API_BASE_URL

            # Health endpoints are at root level, not /api/v1
            health_response = requests.get(f"{API_BASE_URL}/healthz")
            if health_response.status_code == 200:
                st.success("✅ System Healthy")
            else:
                st.error("❌ System Issues Detected")

            ready_response = requests.get(f"{API_BASE_URL}/readyz")
            if ready_response.status_code == 200:
                st.success("✅ System Ready")
            else:
                st.warning("⚠️ System Not Ready")

        except Exception as e:
            st.error(f"❌ Cannot connect to API: {str(e)}")

        if st.button("View Full Dashboard", use_container_width=True):
            st.switch_page("pages/5_📊_Admin_Dashboard.py")

else:
    # Not authenticated - show welcome screen
    st.markdown("### 👋 Welcome to PWC Contract Analysis System")

    st.markdown("""
    This platform provides AI-powered contract analysis and evaluation services.
    Please login or register to get started.
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>🔐 Login</h4>
            <p>Access your existing account</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Login", type="primary", use_container_width=True):
            st.switch_page("pages/1_🔐_Login.py")

    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>📝 Register</h4>
            <p>Create a new account</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Register", use_container_width=True):
            st.switch_page("pages/2_📝_Register.py")

    # Features overview
    st.markdown("### ✨ Platform Features")

    features = [
        ("🤖 AI-Powered Analysis", "Advanced GenAI models extract and classify contract clauses"),
        ("📊 Risk Evaluation", "Comprehensive contract health assessment and approval recommendations"),
        ("👥 Client Management", "Organize contracts by clients with full CRUD operations"),
        ("📈 Real-time Monitoring", "System metrics, logs, and health monitoring dashboard"),
        ("🔒 Secure Authentication", "JWT-based authentication with secure password storage"),
        ("🚀 Async Processing", "Background processing for large contracts with real-time updates")
    ]

    for title, description in features:
        st.markdown(f"""
        <div class="feature-card">
            <h5>{title}</h5>
            <p>{description}</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    PWC Contract Analysis System | Powered by OpenAI & Streamlit
</div>
""", unsafe_allow_html=True)