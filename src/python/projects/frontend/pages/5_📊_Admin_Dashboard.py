"""Admin dashboard page"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.auth import require_auth, get_current_user
from utils.api_client import APIClient, handle_api_response

st.set_page_config(
    page_title="Admin Dashboard - PWC Contract Analysis",
    page_icon="📊",
    layout="wide"
)

require_auth()

st.title("📊 Admin Dashboard")
st.markdown("System metrics, logs, and monitoring")

# User info in sidebar
with st.sidebar:
    user = get_current_user()
    if user:
        st.success(f"Welcome, {user['username']}!")

    if st.button("Logout", type="secondary", use_container_width=True):
        from utils.auth import logout
        logout()

    st.markdown("---")
    st.subheader("🔧 Dashboard Settings")

    # Refresh interval
    auto_refresh = st.checkbox("Auto Refresh", value=False)
    if auto_refresh:
        refresh_interval = st.selectbox("Refresh Interval", [30, 60, 120, 300], index=1)
        st.info(f"Auto-refreshing every {refresh_interval} seconds")

    # Manual refresh
    if st.button("🔄 Refresh Now", use_container_width=True):
        st.rerun()

# Main dashboard tabs
tab1, tab2, tab3 = st.tabs(["📈 Metrics", "📋 Logs", "🏥 Health"])

with tab1:
    st.header("System Metrics")

    # Metrics view toggle
    metrics_view = st.radio(
        "Select View:",
        ["User Metrics", "System Metrics (Admin)"],
        horizontal=True
    )

    try:
        if metrics_view == "User Metrics":
            # Fetch user metrics
            response = APIClient.get("/metrics/user")
            metrics_data = handle_api_response(response)

            if metrics_data:
                st.subheader("👤 Your Activity Dashboard")

                # User overview metrics
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        label="My Requests (24h)",
                        value=f"{metrics_data.get('user_request_count', 0):,}"
                    )

                with col2:
                    st.metric(
                        label="My Avg Latency (ms)",
                        value=f"{metrics_data.get('user_avg_latency', 0):.2f}"
                    )

                with col3:
                    st.metric(
                        label="My Contracts",
                        value=f"{metrics_data.get('user_contract_count', 0):,}"
                    )

                with col4:
                    st.metric(
                        label="My Clients",
                        value=f"{metrics_data.get('user_client_count', 0):,}"
                    )

                # User contract status
                col1, col2 = st.columns(2)

                with col1:
                    processed = metrics_data.get('user_processed_contracts', 0)
                    failed = metrics_data.get('user_failed_contracts', 0)
                    total = metrics_data.get('user_contract_count', 0)

                    contract_status = {
                        'Processed': processed,
                        'Failed': failed,
                        'Other': max(0, total - processed - failed)
                    }

                    if total > 0:
                        fig_status = px.pie(
                            values=list(contract_status.values()),
                            names=list(contract_status.keys()),
                            title="My Contract Status Distribution"
                        )
                        st.plotly_chart(fig_status, use_container_width=True)

                with col2:
                    # Top endpoints for user
                    top_endpoints = metrics_data.get('top_endpoints', [])
                    if top_endpoints:
                        st.subheader("My Top Endpoints")
                        for i, endpoint in enumerate(top_endpoints[:5], 1):
                            st.write(f"{i}. **{endpoint['endpoint']}**: {endpoint['count']} requests")

        else:
            # Fetch system metrics
            response = APIClient.get("/metrics/system")
            metrics_data = handle_api_response(response)

            if metrics_data:
                st.subheader("🌐 System-Wide Dashboard")

                # System overview metrics
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        label="Total Requests (24h)",
                        value=f"{metrics_data.get('total_request_count', 0):,}"
                    )

                with col2:
                    st.metric(
                        label="System Avg Latency (ms)",
                        value=f"{metrics_data.get('system_avg_latency', 0):.2f}"
                    )

                with col3:
                    error_rate = metrics_data.get('error_rate', 0)
                    st.metric(
                        label="Error Rate",
                        value=f"{error_rate:.1f}%",
                        delta=None if error_rate < 5 else "⚠️ High"
                    )

                with col4:
                    st.metric(
                        label="Total Contracts",
                        value=f"{metrics_data.get('total_contract_count', 0):,}"
                    )

                # System contract status
                col1, col2 = st.columns(2)

                with col1:
                    processed = metrics_data.get('total_processed_contracts', 0)
                    failed = metrics_data.get('total_failed_contracts', 0)
                    total = metrics_data.get('total_contract_count', 0)

                    contract_status = {
                        'Processed': processed,
                        'Failed': failed,
                        'Other': max(0, total - processed - failed)
                    }

                    if total > 0:
                        fig_status = px.pie(
                            values=list(contract_status.values()),
                            names=list(contract_status.keys()),
                            title="System Contract Status Distribution"
                        )
                        st.plotly_chart(fig_status, use_container_width=True)

                with col2:
                    # Top users
                    top_users = metrics_data.get('top_users', [])
                    if top_users:
                        st.subheader("Most Active Users")
                        for i, user_data in enumerate(top_users[:5], 1):
                            st.write(f"{i}. **{user_data['user']}**: {user_data['request_count']} requests")

                # Endpoint statistics
                endpoint_stats = metrics_data.get('endpoint_stats', [])
                if endpoint_stats:
                    st.subheader("Endpoint Performance")
                    df_endpoints = pd.DataFrame(endpoint_stats)
                    st.dataframe(df_endpoints, use_container_width=True)

            st.markdown("---")

            # Charts
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Request Volume Over Time")
                # Sample data - replace with actual metrics
                dates = pd.date_range(start=datetime.now() - timedelta(days=7), end=datetime.now(), freq='D')
                request_counts = [120, 140, 110, 180, 160, 200, 190]

                df_requests = pd.DataFrame({
                    'Date': dates,
                    'Requests': request_counts
                })

                fig_requests = px.line(df_requests, x='Date', y='Requests', title='Daily Request Count')
                st.plotly_chart(fig_requests, use_container_width=True)

            with col2:
                st.subheader("Response Time Distribution")
                # Sample data - replace with actual metrics
                response_times = [50, 75, 100, 125, 150, 80, 90, 110, 95, 85]

                fig_response = px.histogram(
                    x=response_times,
                    title='Response Time Distribution',
                    labels={'x': 'Response Time (ms)', 'y': 'Frequency'}
                )
                st.plotly_chart(fig_response, use_container_width=True)

            # Endpoint metrics
            st.subheader("Endpoint Performance")
            endpoint_data = metrics_data.get("endpoints", {})

            if endpoint_data:
                df_endpoints = pd.DataFrame([
                    {
                        "Endpoint": endpoint,
                        "Requests": data.get("count", 0),
                        "Avg Latency (ms)": data.get("avg_latency", 0),
                        "Success Rate (%)": data.get("success_rate", 0) * 100
                    }
                    for endpoint, data in endpoint_data.items()
                ])

                st.dataframe(df_endpoints, use_container_width=True)

            # Contract analysis metrics
            st.subheader("Contract Analysis Statistics")

            analysis_metrics = metrics_data.get("analysis", {})
            if analysis_metrics:
                col1, col2, col3 = st.columns(3)

                with col1:
                    total_analyzed = analysis_metrics.get("total_analyzed", 0)
                    st.metric("Contracts Analyzed", total_analyzed)

                with col2:
                    avg_clauses = analysis_metrics.get("avg_clauses", 0)
                    st.metric("Avg Clauses per Contract", f"{avg_clauses:.1f}")

                with col3:
                    approval_rate = analysis_metrics.get("approval_rate", 0)
                    st.metric("Approval Rate", f"{approval_rate:.1f}%")

    except Exception as e:
        st.error(f"Failed to fetch metrics: {str(e)}")

with tab2:
    st.header("System Logs")

    # Log filters
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        user_filter = st.text_input("User Filter", placeholder="Username")

    with col2:
        endpoint_filter = st.selectbox(
            "Endpoint Filter",
            ["All", "/auth/login", "/auth/register", "/contracts", "/genai", "/metrics", "/logs"]
        )

    with col3:
        status_filter = st.selectbox(
            "Status Filter",
            ["All", "200", "400", "401", "404", "422", "500"]
        )

    with col4:
        limit = st.selectbox("Limit", [10, 25, 50, 100], index=1)

    # Fetch logs
    try:
        params = {
            "limit": limit,
            "skip": 0
        }

        if user_filter:
            params["user"] = user_filter
        if endpoint_filter != "All":
            params["endpoint"] = endpoint_filter
        if status_filter != "All":
            params["status"] = int(status_filter)

        response = APIClient.get("/logs", params=params)
        logs_data = handle_api_response(response)

        if logs_data:
            logs = logs_data if isinstance(logs_data, list) else logs_data.get("items", [])

            # Display logs
            st.subheader(f"Recent Logs ({len(logs)} entries)")

            if logs:
                for log in logs:
                    timestamp = log.get("timestamp", "Unknown")
                    if timestamp != "Unknown":
                        # Format timestamp for display
                        try:
                            from datetime import datetime
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
                        except:
                            pass

                    method = log.get("method", "GET")
                    endpoint = log.get("endpoint", "Unknown")
                    status_code = log.get("status_code", 200)
                    user = log.get("user", "Anonymous")
                    latency = log.get("response_time_ms", 0)
                    ip_address = log.get("ip_address", "Unknown")

                    # Color code by status
                    if status_code >= 500:
                        status_color = "🔴"
                    elif status_code >= 400:
                        status_color = "🟡"
                    else:
                        status_color = "🟢"

                    with st.expander(f"{status_color} {timestamp} - {method} {endpoint} ({status_code})"):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.write(f"**User:** {user}")
                            st.write(f"**Method:** {method}")
                            st.write(f"**Endpoint:** {endpoint}")
                            st.write(f"**IP Address:** {ip_address}")

                        with col2:
                            st.write(f"**Status Code:** {status_code}")
                            st.write(f"**Response Time:** {latency:.2f}ms")
                            st.write(f"**Timestamp:** {timestamp}")

                            # Show error message if present
                            if log.get("error_message"):
                                st.write(f"**Error:** {log['error_message']}")

                # Logs summary
                st.markdown("---")
                col1, col2, col3 = st.columns(3)

                with col1:
                    success_logs = [log for log in logs if log.get("status_code", 200) < 400]
                    st.metric("Success Requests", len(success_logs))

                with col2:
                    error_logs = [log for log in logs if log.get("status_code", 200) >= 400]
                    st.metric("Error Requests", len(error_logs))

                with col3:
                    if logs:
                        avg_latency = sum(log.get("response_time_ms", 0) for log in logs) / len(logs)
                        st.metric("Avg Response Time", f"{avg_latency:.2f}ms")
            else:
                st.info("No logs found for the current filters.")

        else:
            st.info("No logs found matching the criteria")

    except Exception as e:
        st.error(f"Failed to fetch logs: {str(e)}")

with tab3:
    st.header("System Health")

    # Health checks
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏥 Liveness Check")
        try:
            response = APIClient.get("/healthz")
            if response.status_code == 200:
                st.success("✅ System is alive and running")
                health_data = response.json()
                st.json(health_data)
            else:
                st.error("❌ System health check failed")
        except Exception as e:
            st.error(f"❌ Health check failed: {str(e)}")

    with col2:
        st.subheader("🔧 Readiness Check")
        try:
            response = APIClient.get("/readyz")
            if response.status_code == 200:
                st.success("✅ System is ready to serve requests")
                readiness_data = response.json()
                st.json(readiness_data)
            else:
                st.error("❌ System readiness check failed")
        except Exception as e:
            st.error(f"❌ Readiness check failed: {str(e)}")

    st.markdown("---")

    # Resource usage (mock data - would need real monitoring)
    st.subheader("📊 Resource Usage")

    col1, col2, col3 = st.columns(3)

    with col1:
        # CPU usage gauge
        cpu_usage = 65  # Mock data
        fig_cpu = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = cpu_usage,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "CPU Usage (%)"},
            delta = {'reference': 80},
            gauge = {'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps' : [{'range': [0, 50], 'color': "lightgray"},
                              {'range': [50, 80], 'color': "gray"}],
                    'threshold' : {'line': {'color': "red", 'width': 4},
                                  'thickness': 0.75, 'value': 90}}))

        st.plotly_chart(fig_cpu, use_container_width=True)

    with col2:
        # Memory usage gauge
        memory_usage = 45  # Mock data
        fig_memory = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = memory_usage,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Memory Usage (%)"},
            delta = {'reference': 60},
            gauge = {'axis': {'range': [None, 100]},
                    'bar': {'color': "darkgreen"},
                    'steps' : [{'range': [0, 50], 'color': "lightgray"},
                              {'range': [50, 80], 'color': "gray"}],
                    'threshold' : {'line': {'color': "red", 'width': 4},
                                  'thickness': 0.75, 'value': 90}}))

        st.plotly_chart(fig_memory, use_container_width=True)

    with col3:
        # Disk usage gauge
        disk_usage = 30  # Mock data
        fig_disk = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = disk_usage,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Disk Usage (%)"},
            delta = {'reference': 40},
            gauge = {'axis': {'range': [None, 100]},
                    'bar': {'color': "darkorange"},
                    'steps' : [{'range': [0, 50], 'color': "lightgray"},
                              {'range': [50, 80], 'color': "gray"}],
                    'threshold' : {'line': {'color': "red", 'width': 4},
                                  'thickness': 0.75, 'value': 90}}))

        st.plotly_chart(fig_disk, use_container_width=True)

# Auto-refresh logic
if auto_refresh:
    import time
    time.sleep(refresh_interval)
    st.rerun()