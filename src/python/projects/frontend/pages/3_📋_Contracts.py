"""Contracts management page"""

import streamlit as st
import pandas as pd
from datetime import datetime
from utils.auth import require_auth, get_current_user
from utils.api_client import APIClient, handle_api_response

st.set_page_config(
    page_title="Contracts - PWC Contract Analysis",
    page_icon="📋",
    layout="wide"
)

require_auth()

st.title("📋 Contract Management")

# User info in sidebar
with st.sidebar:
    user = get_current_user()
    if user:
        st.success(f"Welcome, {user['username']}!")

    if st.button("Logout", type="secondary", use_container_width=True):
        from utils.auth import logout
        logout()

# Main content tabs
tab1, tab2, tab3 = st.tabs(["📤 Upload Contract", "📄 My Contracts", "👥 Clients"])

with tab1:
    st.header("Upload New Contract")

    with st.form("upload_contract"):
        col1, col2 = st.columns(2)

        with col1:
            contract_file = st.file_uploader(
                "Choose PDF file",
                type=['pdf'],
                help="Upload a PDF contract for analysis"
            )

            client_name = st.text_input("Client Name", placeholder="Enter client name")

        with col2:
            description = st.text_area(
                "Description",
                placeholder="Brief description of the contract",
                height=100
            )

            tags = st.text_input("Tags", placeholder="Enter tags separated by commas")

        upload_btn = st.form_submit_button("Upload Contract", type="primary", use_container_width=True)

    if upload_btn:
        if not contract_file or not client_name:
            st.error("Please provide both a PDF file and client name")
        else:
            with st.spinner("Uploading contract..."):
                try:
                    # First create/get client
                    client_response = APIClient.post("/clients", {
                        "name": client_name,
                        "description": f"Client for {client_name}"
                    })

                    client_data = handle_api_response(client_response)
                    if client_data:
                        # Upload contract
                        file_data = contract_file.read()
                        upload_response = APIClient.upload_file(
                            "/contracts/",
                            file_data,
                            contract_file.name,
                            {
                                "client_id": client_data["id"],
                                "description": description,
                                "tags": tags
                            }
                        )

                        contract_data = handle_api_response(upload_response)
                        if contract_data:
                            st.success(f"Contract uploaded successfully! ID: {contract_data['id']}")

                            # Option to start analysis
                            if st.button("Start AI Analysis", type="primary"):
                                with st.spinner("Triggering AI analysis..."):
                                    analysis_response = APIClient.post(f"/contracts/{contract_data['id']}/init-genai")
                                    if handle_api_response(analysis_response):
                                        st.success("AI analysis started! Check the 'My Contracts' tab for results.")

                except Exception as e:
                    st.error(f"Upload failed: {str(e)}")

with tab2:
    st.header("My Contracts")

    # Fetch contracts
    try:
        response = APIClient.get("/contracts/")
        contracts_data = handle_api_response(response)

        if contracts_data and contracts_data.get("items"):
            contracts = contracts_data["items"]

            # Display contracts in a table
            df_data = []
            for contract in contracts:
                df_data.append({
                    "ID": contract["id"],
                    "Filename": contract["filename"],
                    "Client": contract.get("client_name", "Unknown"),
                    "State": contract["state"],
                    "Uploaded": contract["created_at"][:10] if contract.get("created_at") else "Unknown",
                    "Size": f"{contract.get('file_size', 0) / 1024:.1f} KB"
                })

            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)

            # Contract details
            st.subheader("Contract Details")
            selected_contract = st.selectbox(
                "Select a contract to view details:",
                options=[c["id"] for c in contracts],
                format_func=lambda x: f"{x} - {next(c['filename'] for c in contracts if c['id'] == x)}"
            )

            if selected_contract:
                contract = next(c for c in contracts if c["id"] == selected_contract)

                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Basic Information:**")
                    st.write(f"- **ID:** {contract['id']}")
                    st.write(f"- **Filename:** {contract['filename']}")
                    st.write(f"- **State:** {contract['state']}")
                    st.write(f"- **Client:** {contract.get('client_name', 'Unknown')}")

                with col2:
                    # Analysis results
                    if contract.get("analysis_result"):
                        st.write("**Analysis Results:**")
                        analysis = contract["analysis_result"]
                        clauses = analysis.get("clauses", [])
                        st.write(f"- **Clauses Found:** {len(clauses)}")

                        if clauses:
                            clause_types = [c.get("type", "unknown") for c in clauses]
                            clause_counts = pd.Series(clause_types).value_counts()
                            st.bar_chart(clause_counts)

                    # Evaluation results
                    if contract.get("evaluation_result"):
                        st.write("**Evaluation Results:**")
                        evaluation = contract["evaluation_result"]

                        approved = evaluation.get("approved", False)
                        if approved:
                            st.success("✅ Contract Approved")
                        else:
                            st.error("❌ Contract Not Approved")

                        st.write(f"- **Risk Score:** {evaluation.get('risk_score', 'N/A')}")
                        st.write(f"- **Reasoning:** {evaluation.get('reasoning', 'N/A')}")

                # Action buttons
                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button(f"Start Analysis", key=f"analyze_{selected_contract}"):
                        with st.spinner("Starting analysis..."):
                            response = APIClient.post(f"/contracts/{selected_contract}/init-genai")
                            if handle_api_response(response):
                                st.success("Analysis started!")
                                st.rerun()

                with col2:
                    if st.button(f"Refresh", key=f"refresh_{selected_contract}"):
                        st.rerun()

        else:
            st.info("No contracts found. Upload your first contract using the 'Upload Contract' tab.")

    except Exception as e:
        st.error(f"Failed to fetch contracts: {str(e)}")

with tab3:
    st.header("Client Management")

    # Create new client
    with st.expander("Create New Client"):
        with st.form("create_client"):
            client_name = st.text_input("Client Name")
            client_desc = st.text_area("Description")

            if st.form_submit_button("Create Client"):
                if client_name:
                    response = APIClient.post("/clients", {
                        "name": client_name,
                        "description": client_desc
                    })
                    if handle_api_response(response):
                        st.success("Client created successfully!")
                        st.rerun()

    # List existing clients
    try:
        response = APIClient.get("/clients")
        if response.status_code == 200:
            clients = response.json()
            if clients:
                st.subheader("Existing Clients")
                for client in clients:
                    with st.expander(f"Client: {client['name']}"):
                        st.write(f"**ID:** {client['id']}")
                        st.write(f"**Description:** {client.get('description', 'No description')}")

                        # Get client contracts
                        contracts_response = APIClient.get(f"/clients/{client['id']}/contracts")
                        if contracts_response.status_code == 200:
                            client_contracts = contracts_response.json()
                            st.write(f"**Contracts:** {len(client_contracts)} contracts")
            else:
                st.info("No clients found.")
    except Exception as e:
        st.error(f"Failed to fetch clients: {str(e)}")