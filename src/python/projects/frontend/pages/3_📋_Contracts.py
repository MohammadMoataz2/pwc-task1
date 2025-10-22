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

    # First, fetch user's clients for the dropdown
    try:
        clients_response = APIClient.get("/clients/")
        clients_data = handle_api_response(clients_response)
        user_clients = clients_data if clients_data else []
    except:
        user_clients = []

    with st.form("upload_contract"):
        col1, col2 = st.columns(2)

        with col1:
            contract_file = st.file_uploader(
                "Choose PDF file",
                type=['pdf'],
                help="Upload a PDF contract for analysis"
            )

            # Client selection
            if user_clients:
                client_options = {client["id"]: f"{client['name']} ({client.get('company', 'No company')})" for client in user_clients}
                client_options["new"] = "➕ Create New Client"

                selected_client = st.selectbox(
                    "Select Client",
                    options=list(client_options.keys()),
                    format_func=lambda x: client_options[x],
                    help="Choose an existing client or create a new one"
                )

                # Show new client form if "Create New Client" is selected
                if selected_client == "new":
                    st.markdown("**Create New Client:**")
                    new_client_name = st.text_input("Client Name", placeholder="Enter client name")
                    new_client_company = st.text_input("Company (optional)", placeholder="Company name")
                    new_client_email = st.text_input("Email (optional)", placeholder="client@example.com")
                else:
                    new_client_name = None
                    new_client_company = None
                    new_client_email = None
            else:
                selected_client = "new"
                st.info("No clients found. Please create your first client:")
                new_client_name = st.text_input("Client Name", placeholder="Enter client name")
                new_client_company = st.text_input("Company (optional)", placeholder="Company name")
                new_client_email = st.text_input("Email (optional)", placeholder="client@example.com")

        with col2:
            contract_title = st.text_input(
                "Contract Title (optional)",
                placeholder="Brief title for the contract"
            )

            description = st.text_area(
                "Description (optional)",
                placeholder="Brief description of the contract",
                height=100
            )

        upload_btn = st.form_submit_button("Upload Contract", type="primary", use_container_width=True)

    if upload_btn:
        if not contract_file:
            st.error("Please provide a PDF file")
        elif selected_client == "new" and not new_client_name:
            st.error("Please provide a client name")
        else:
            with st.spinner("Uploading contract..."):
                try:
                    client_id = None

                    # Create new client if needed
                    if selected_client == "new":
                        client_response = APIClient.post("/clients/", {
                            "name": new_client_name,
                            "company": new_client_company,
                            "email": new_client_email
                        })
                        client_data = handle_api_response(client_response)
                        if client_data:
                            client_id = client_data["id"]
                            st.success(f"Created new client: {new_client_name}")
                        else:
                            st.error("Failed to create client")
                            st.stop()
                    else:
                        client_id = selected_client

                    # Upload contract
                    if client_id:
                        file_data = contract_file.read()
                        upload_response = APIClient.upload_file(
                            "/contracts/",
                            file_data,
                            contract_file.name,
                            {"client_id": client_id}
                        )

                        contract_data = handle_api_response(upload_response)
                        if contract_data:
                            st.success(f"Contract uploaded successfully!")
                            st.info(f"Contract ID: {contract_data['id']}")

                            # Automatically start analysis
                            with st.spinner("Starting AI analysis..."):
                                analysis_response = APIClient.post(f"/contracts/{contract_data['id']}/init-genai")
                                if handle_api_response(analysis_response):
                                    st.success("🤖 AI analysis pipeline started! Check the 'My Contracts' tab for results.")
                                    st.balloons()

                except Exception as e:
                    st.error(f"Upload failed: {str(e)}")

with tab2:
    st.header("My Contracts")

    # Fetch contracts and clients
    try:
        contracts_response = APIClient.get("/contracts/")
        contracts_data = handle_api_response(contracts_response)

        clients_response = APIClient.get("/clients/")
        clients_data = handle_api_response(clients_response)

        # Create client lookup dictionary
        clients_lookup = {}
        if clients_data:
            for client in clients_data:
                clients_lookup[client["id"]] = client["name"]

        if contracts_data:
            contracts = contracts_data

            # Display contracts in a table
            df_data = []
            for contract in contracts:
                client_name = "No Client"
                if contract.get("client_id"):
                    client_name = clients_lookup.get(contract["client_id"], "Unknown Client")

                df_data.append({
                    "ID": contract["id"][:8] + "...",  # Shortened ID for display
                    "Filename": contract["filename"],
                    "Client": client_name,
                    "Status": contract["status"],
                    "Uploaded": contract["created_at"][:10] if contract.get("created_at") else "Unknown",
                    "Size": f"{contract.get('file_size', 0) / 1024:.1f} KB"
                })

            if df_data:
                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No contracts found. Upload your first contract using the 'Upload Contract' tab.")

            # Contract details
            if contracts:
                st.subheader("Contract Details")
                selected_contract = st.selectbox(
                    "Select a contract to view details:",
                    options=[c["id"] for c in contracts],
                    format_func=lambda x: f"{next(c['filename'] for c in contracts if c['id'] == x)} ({clients_lookup.get(next(c.get('client_id') for c in contracts if c['id'] == x), 'No Client')})"
                )

                if selected_contract:
                    contract = next(c for c in contracts if c["id"] == selected_contract)
                    client_name = clients_lookup.get(contract.get("client_id"), "No Client")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.write("**Basic Information:**")
                        st.write(f"- **ID:** {contract['id'][:8]}...")
                        st.write(f"- **Filename:** {contract['filename']}")
                        st.write(f"- **Status:** {contract['status']}")
                        st.write(f"- **Client:** {client_name}")
                        st.write(f"- **Size:** {contract.get('file_size', 0) / 1024:.1f} KB")
                        if contract.get("analysis_result"):
                            st.write("**Analysis Results:**")
                            analysis = contract["analysis_result"]
                            clauses = analysis.get("clauses", [])
                            st.write(f"- **Clauses Found:** {len(clauses)}")

                            if clauses:
                                clause_types = [c.get("type", "unknown") for c in clauses]
                                clause_counts = pd.Series(clause_types).value_counts()
                                st.bar_chart(clause_counts)
                                for i, clause in enumerate(clauses):
                                    with st.expander(f"Clause {i+1}: {clause.get('type', 'Unknown').replace('_', ' ').title()}"):
                                        st.write(f"**Type:** {clause.get('type', 'Unknown')}")
                                        st.write(f"**Confidence:** {clause.get('confidence', 0):.2f}")
                                        st.write(f"**Content:**")
                                        st.write(clause.get('content', 'No content available'))

                    with col2:
                        
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
                        if st.button(f"🤖 Start Analysis", key=f"analyze_{selected_contract}"):
                            with st.spinner("Starting analysis..."):
                                response = APIClient.post(f"/contracts/{selected_contract}/init-genai")
                                if handle_api_response(response):
                                    st.success("Analysis started!")
                                    st.rerun()

                    with col2:
                        if st.button(f"🔄 Refresh", key=f"refresh_{selected_contract}"):
                            st.rerun()

                    with col3:
                        if st.button(f"📥 View Details", key=f"details_{selected_contract}"):
                            st.switch_page("pages/4_🤖_GenAI_Analysis.py")

        else:
            st.info("No contracts found. Upload your first contract using the 'Upload Contract' tab.")

    except Exception as e:
        st.error(f"Failed to fetch contracts: {str(e)}")

with tab3:
    st.header("Client Management")

    # Create new client
    with st.expander("➕ Create New Client"):
        with st.form("create_client"):
            col1, col2 = st.columns(2)

            with col1:
                client_name = st.text_input("Client Name*", placeholder="Enter client name")
                client_company = st.text_input("Company (optional)", placeholder="Company name")

            with col2:
                client_email = st.text_input("Email (optional)", placeholder="client@example.com")

            if st.form_submit_button("Create Client", type="primary", use_container_width=True):
                if client_name:
                    response = APIClient.post("/clients/", {
                        "name": client_name,
                        "company": client_company,
                        "email": client_email
                    })
                    if handle_api_response(response):
                        st.success("Client created successfully!")
                        st.rerun()
                else:
                    st.error("Please provide a client name")

    # List existing clients
    try:
        response = APIClient.get("/clients/")
        clients_data = handle_api_response(response)

        if clients_data:
            st.subheader("My Clients")

            # Create a nice table view
            client_data = []
            for client in clients_data:
                # Get contract count for each client
                contracts_response = APIClient.get(f"/clients/{client['id']}/contracts")
                contract_count = 0
                if contracts_response.status_code == 200:
                    client_contracts = contracts_response.json()
                    contract_count = len(client_contracts)

                client_data.append({
                    "Name": client['name'],
                    "Company": client.get('company', 'N/A'),
                    "Email": client.get('email', 'N/A'),
                    "Contracts": contract_count,
                    "Created": client['created_at'][:10] if client.get('created_at') else 'Unknown'
                })

            if client_data:
                df = pd.DataFrame(client_data)
                st.dataframe(df, use_container_width=True)

                # Client details
                st.subheader("Client Details")
                client_names = {client['id']: client['name'] for client in clients_data}

                selected_client_id = st.selectbox(
                    "Select a client to view details:",
                    options=list(client_names.keys()),
                    format_func=lambda x: client_names[x]
                )

                if selected_client_id:
                    selected_client = next(c for c in clients_data if c['id'] == selected_client_id)

                    col1, col2 = st.columns(2)

                    with col1:
                        st.write("**Client Information:**")
                        st.write(f"- **Name:** {selected_client['name']}")
                        st.write(f"- **Company:** {selected_client.get('company', 'N/A')}")
                        st.write(f"- **Email:** {selected_client.get('email', 'N/A')}")
                        st.write(f"- **Created:** {selected_client.get('created_at', 'Unknown')[:10]}")

                    with col2:
                        st.write("**Client Contracts:**")

                        # Get and display client contracts
                        contracts_response = APIClient.get(f"/clients/{selected_client_id}/contracts")
                        if contracts_response.status_code == 200:
                            client_contracts = contracts_response.json()

                            if client_contracts:
                                for contract in client_contracts:
                                    status_icon = "✅" if contract.get('status') == 'completed' else "🔄" if contract.get('status') == 'processing' else "⏳"
                                    st.write(f"{status_icon} **{contract['filename']}** ({contract.get('status', 'unknown')})")
                            else:
                                st.info("No contracts found for this client")
                        else:
                            st.error("Failed to load client contracts")
            else:
                st.info("No clients found. Create your first client above.")
        else:
            st.info("No clients found. Create your first client above.")

    except Exception as e:
        st.error(f"Failed to fetch clients: {str(e)}")