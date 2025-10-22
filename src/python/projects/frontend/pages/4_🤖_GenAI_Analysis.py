"""GenAI Analysis page"""

import streamlit as st
import json
from utils.auth import require_auth, get_current_user
from utils.api_client import APIClient, handle_api_response
import pandas as pd
st.set_page_config(
    page_title="GenAI Analysis - PWC Contract Analysis",
    page_icon="🤖",
    layout="wide"
)

require_auth()

st.title("🤖 GenAI Analysis")
st.markdown("Direct contract analysis and evaluation using AI")

# User info in sidebar
with st.sidebar:
    user = get_current_user()
    if user:
        st.success(f"Welcome, {user['username']}!")

    if st.button("Logout", type="secondary", use_container_width=True):
        from utils.auth import logout
        logout()

# Main content tabs
tab1, tab2 = st.tabs(["📊 Analyze Contract", "🔍 Evaluate Contract"])

with tab1:
    st.header("Contract Analysis")
    st.markdown("Analyze your uploaded contracts or upload a new one with client association")

    # Fetch user's contracts
    try:
        contracts_response = APIClient.get("/contracts/")
        contracts_data = handle_api_response(contracts_response)
        user_contracts = contracts_data if contracts_data else []

        clients_response = APIClient.get("/clients/")
        clients_data = handle_api_response(clients_response)
        user_clients = clients_data if clients_data else []
    except:
        user_contracts = []
        user_clients = []

    # Create two options: analyze existing or upload new
    analysis_option = st.radio(
        "Choose analysis option:",
        ["🔍 Analyze Existing Document", "📤 Upload New Document"],
        key="analysis_option"
    )

    if analysis_option == "🔍 Analyze Existing Document":
        if user_contracts:
            with st.form("analyze_existing"):
                # Create client lookup
                clients_lookup = {client["id"]: client["name"] for client in user_clients}

                contract_options = {}
                for contract in user_contracts:
                    client_name = clients_lookup.get(contract.get("client_id"), "No Client")
                    contract_options[contract["id"]] = f"{contract['filename']} ({client_name})"

                selected_contract = st.selectbox(
                    "Select document to analyze:",
                    options=list(contract_options.keys()),
                    format_func=lambda x: contract_options[x],
                    help="Choose an existing document for analysis"
                )

                analyze_existing_btn = st.form_submit_button("🤖 Analyze Selected Document", type="primary", use_container_width=True)

            if analyze_existing_btn and selected_contract:
                with st.spinner("Analyzing contract with AI..."):
                    try:
                        response = APIClient.post(f"/genai/analyze-document/{selected_contract}")
                        analysis_data = handle_api_response(response)
                        if analysis_data:
                            st.success("🤖 Analysis completed!")
                            st.balloons()

                            # Display results immediately
                            st.subheader("📋 Fresh Analysis Results")
                            clauses = analysis_data.get("clauses", [])
                            metadata = analysis_data.get("metadata", {})

                            col1, col2 = st.columns([2, 1])

                            with col1:
                                st.write(f"**Total Clauses Found:** {len(clauses)}")
                                if clauses:
                                    for i, clause in enumerate(clauses):
                                        with st.expander(f"Clause {i+1}: {clause.get('type', 'Unknown').replace('_', ' ').title()}"):
                                            st.write(f"**Type:** {clause.get('type', 'Unknown')}")
                                            st.write(f"**Confidence:** {clause.get('confidence', 0):.2f}")
                                            st.write(f"**Content:**")
                                            st.write(clause.get('content', 'No content available'))

                            with col2:
                                st.write("**Metadata:**")
                                for key, value in metadata.items():
                                    st.write(f"- **{key.replace('_', ' ').title()}:** {value}")

                                if clauses:
                                    clause_types = [c.get('type', 'unknown') for c in clauses]
                                    clause_counts = pd.Series(clause_types).value_counts()
                                    st.subheader("Clause Distribution")
                                    st.bar_chart(clause_counts)

                    except Exception as e:
                        st.error(f"Analysis failed: {str(e)}")

            # Show existing analysis results if available
            if selected_contract:
                contract = next(c for c in user_contracts if c["id"] == selected_contract)
                if contract.get("analysis_result"):
                    st.subheader("📋 Existing Analysis Results")
                    analysis = contract["analysis_result"]
                    clauses = analysis.get("clauses", [])

                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.write(f"**Total Clauses Found:** {len(clauses)}")
                        if clauses:
                            for i, clause in enumerate(clauses):
                                with st.expander(f"Clause {i+1}: {clause.get('type', 'Unknown').replace('_', ' ').title()}"):
                                    st.write(f"**Type:** {clause.get('type', 'Unknown')}")
                                    st.write(f"**Confidence:** {clause.get('confidence', 0):.2f}")
                                    st.write(f"**Content:**")
                                    st.write(clause.get('content', 'No content available'))

                    with col2:
                        if clauses:
                            clause_types = [c.get('type', 'unknown') for c in clauses]
                            clause_counts = pd.Series(clause_types).value_counts()
                            st.subheader("Clause Distribution")
                            st.bar_chart(clause_counts)
        else:
            st.info("No documents found. Please upload a document first in the 'Contracts' section.")

    else:  # Upload New Document
        if not user_clients:
            st.warning("⚠️ You need to create a client first before uploading contracts.")
            if st.button("Go to Client Creation", type="secondary"):
                st.switch_page("pages/3_📋_Contracts.py")
        else:
            with st.form("analyze_new_contract"):
                col1, col2 = st.columns(2)

                with col1:
                    contract_file = st.file_uploader(
                        "Choose PDF file for analysis",
                        type=['pdf'],
                        help="Upload a PDF contract for AI analysis"
                    )

                with col2:
                    # Client selection
                    client_options = {client["id"]: f"{client['name']} ({client.get('company', 'No company')})" for client in user_clients}

                    selected_client = st.selectbox(
                        "Select Client",
                        options=list(client_options.keys()),
                        format_func=lambda x: client_options[x],
                        help="Choose which client this contract belongs to"
                    )

                analyze_btn = st.form_submit_button("📤 Upload & Analyze", type="primary", use_container_width=True)

            if analyze_btn and contract_file and selected_client:
                with st.spinner("Uploading and analyzing contract..."):
                    try:
                        # First upload the contract
                        file_data = contract_file.read()
                        upload_response = APIClient.upload_file(
                            "/contracts/",
                            file_data,
                            contract_file.name,
                            {"client_id": selected_client}
                        )

                        contract_data = handle_api_response(upload_response)
                        if contract_data:
                            st.success(f"Contract uploaded successfully!")

                            # Immediately analyze the contract
                            analysis_response = APIClient.post(f"/genai/analyze-document/{contract_data['id']}")
                            analysis_data = handle_api_response(analysis_response)
                            if analysis_data:
                                st.success("🤖 Analysis completed!")
                                st.balloons()

                                # Display results immediately
                                st.subheader("📋 Analysis Results")
                                clauses = analysis_data.get("clauses", [])
                                metadata = analysis_data.get("metadata", {})

                                col1, col2 = st.columns([2, 1])

                                with col1:
                                    st.write(f"**Total Clauses Found:** {len(clauses)}")
                                    if clauses:
                                        for i, clause in enumerate(clauses):
                                            with st.expander(f"Clause {i+1}: {clause.get('type', 'Unknown').replace('_', ' ').title()}"):
                                                st.write(f"**Type:** {clause.get('type', 'Unknown')}")
                                                st.write(f"**Confidence:** {clause.get('confidence', 0):.2f}")
                                                st.write(f"**Content:**")
                                                st.write(clause.get('content', 'No content available'))

                                with col2:
                                    st.write("**Metadata:**")
                                    for key, value in metadata.items():
                                        st.write(f"- **{key.replace('_', ' ').title()}:** {value}")

                                    if clauses:
                                        clause_types = [c.get('type', 'unknown') for c in clauses]
                                        clause_counts = pd.Series(clause_types).value_counts()
                                        st.subheader("Clause Distribution")
                                        st.bar_chart(clause_counts)

                    except Exception as e:
                        st.error(f"Upload and analysis failed: {str(e)}")

            elif analyze_btn:
                st.error("Please upload a PDF file and select a client")

with tab2:
    st.header("Contract Evaluation")
    st.markdown("Evaluate your analyzed contracts for health and approval recommendations")

    # Get contracts that have analysis results
    try:
        contracts_response = APIClient.get("/contracts/")
        contracts_data = handle_api_response(contracts_response)

        # Filter contracts that have analysis results
        analyzed_contracts = []
        if contracts_data:
            for contract in contracts_data:
                if contract.get("analysis_result"):
                    analyzed_contracts.append(contract)

        clients_response = APIClient.get("/clients/")
        clients_data = handle_api_response(clients_response)
        clients_lookup = {client["id"]: client["name"] for client in clients_data} if clients_data else {}
    except:
        analyzed_contracts = []
        clients_lookup = {}

    if analyzed_contracts:
        with st.form("evaluate_contract"):
            # Create contract options for analyzed contracts only
            contract_options = {}
            for contract in analyzed_contracts:
                client_name = clients_lookup.get(contract.get("client_id"), "No Client")
                has_evaluation = "✅ Evaluated" if contract.get("evaluation_result") else "❌ Not Evaluated"
                contract_options[contract["id"]] = f"{contract['filename']} ({client_name}) - {has_evaluation}"

            selected_contract = st.selectbox(
                "Select analyzed document to evaluate:",
                options=list(contract_options.keys()),
                format_func=lambda x: contract_options[x],
                help="Choose a document that has been analyzed"
            )

            evaluate_btn = st.form_submit_button("🔍 Evaluate Contract", type="primary", use_container_width=True)

        if evaluate_btn and selected_contract:
            with st.spinner("Evaluating contract..."):
                try:
                    eval_response = APIClient.post(f"/genai/evaluate-document/{selected_contract}")
                    evaluation_data = handle_api_response(eval_response)

                    if evaluation_data:
                        st.success("Evaluation completed!")

                        approved = evaluation_data.get("approved", False)
                        reasoning = evaluation_data.get("reasoning", "No reasoning provided")

                        if approved:
                            st.success("✅ **Contract Approved**")
                        else:
                            st.error("❌ **Contract Not Approved**")

                        st.subheader("📝 Reasoning")
                        st.write(reasoning)

                        # Show the contract's analysis results as well
                        contract = next(c for c in analyzed_contracts if c["id"] == selected_contract)
                        if contract.get("analysis_result"):
                            with st.expander("📋 Analysis Results"):
                                analysis = contract["analysis_result"]
                                clauses = analysis.get("clauses", [])
                                st.write(f"**Total Clauses Found:** {len(clauses)}")

                                if clauses:
                                    clause_types = [c.get("type", "unknown") for c in clauses]
                                    clause_counts = pd.Series(clause_types).value_counts()
                                    st.bar_chart(clause_counts)

                except Exception as e:
                    st.error(f"Evaluation failed: {str(e)}")
    else:
        st.info("📋 No analyzed contracts found. Please analyze some contracts first in the 'Analyze Contract' tab or 'Contracts' section.")

        if st.button("Go to Analysis Section"):
            # Stay on the same page but switch to analysis tab
            st.rerun()

# Quick analysis tips
with st.expander("💡 Analysis Tips"):
    st.markdown("""
    **For Best Results:**
    - Upload clear, text-based PDF files
    - Ensure contracts are in English
    - Files should be under 10MB
    - Standard contract formats work best

    **Supported Clause Types:**
    - Payment Terms
    - Termination Clauses
    - Liability Provisions
    - Confidentiality Agreements
    - Intellectual Property
    - Governing Law
    - Dispute Resolution
    - Force Majeure
    - Warranties
    - Indemnification
    """)