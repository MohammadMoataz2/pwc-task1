"""GenAI Analysis page"""

import streamlit as st
import json
from utils.auth import require_auth, get_current_user
from utils.api_client import APIClient, handle_api_response

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
    st.markdown("Upload a PDF contract for immediate AI analysis")

    with st.form("analyze_contract"):
        contract_file = st.file_uploader(
            "Choose PDF file for analysis",
            type=['pdf'],
            help="Upload a PDF contract for AI analysis"
        )

        analyze_btn = st.form_submit_button("Analyze Contract", type="primary", use_container_width=True)

    if analyze_btn and contract_file:
        with st.spinner("Analyzing contract with AI..."):
            try:
                file_data = contract_file.read()
                response = APIClient.upload_file(
                    "/genai/analyze-contract",
                    file_data,
                    contract_file.name
                )

                analysis_data = handle_api_response(response)
                if analysis_data:
                    st.success("Analysis completed!")

                    # Display results
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

                        # Clause type distribution
                        if clauses:
                            import pandas as pd
                            clause_types = [c.get('type', 'unknown') for c in clauses]
                            clause_counts = pd.Series(clause_types).value_counts()

                            st.subheader("Clause Distribution")
                            st.bar_chart(clause_counts)

                    # Download results
                    if st.button("Download Results as JSON"):
                        st.download_button(
                            label="Download Analysis Results",
                            data=json.dumps(analysis_data, indent=2),
                            file_name=f"analysis_{contract_file.name}.json",
                            mime="application/json"
                        )

            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")

    elif analyze_btn:
        st.error("Please upload a PDF file for analysis")

with tab2:
    st.header("Contract Evaluation")
    st.markdown("Evaluate contract health and get approval recommendations")

    # Method selection
    evaluation_method = st.radio(
        "Choose evaluation method:",
        ["Upload PDF for Direct Evaluation", "Evaluate Using Clause Data"]
    )

    if evaluation_method == "Upload PDF for Direct Evaluation":
        with st.form("evaluate_contract_pdf"):
            contract_file = st.file_uploader(
                "Choose PDF file for evaluation",
                type=['pdf'],
                help="Upload a PDF contract for AI evaluation"
            )

            evaluate_btn = st.form_submit_button("Evaluate Contract", type="primary", use_container_width=True)

        if evaluate_btn and contract_file:
            with st.spinner("Evaluating contract with AI..."):
                try:
                    file_data = contract_file.read()
                    response = APIClient.upload_file(
                        "/genai/evaluate-contract",
                        file_data,
                        contract_file.name
                    )

                    evaluation_data = handle_api_response(response)
                    if evaluation_data:
                        st.success("Evaluation completed!")

                        # Display results
                        st.subheader("📊 Evaluation Results")

                        approved = evaluation_data.get("approved", False)
                        reasoning = evaluation_data.get("reasoning", "No reasoning provided")
                        score = evaluation_data.get("score", 0)

                        col1, col2 = st.columns(2)

                        with col1:
                            if approved:
                                st.success("✅ **Contract Approved**")
                            else:
                                st.error("❌ **Contract Not Approved**")

                            st.write(f"**Risk Score:** {score}")

                        with col2:
                            # Score gauge
                            import plotly.graph_objects as go

                            fig = go.Figure(go.Indicator(
                                mode = "gauge+number",
                                value = score,
                                domain = {'x': [0, 1], 'y': [0, 1]},
                                title = {'text': "Risk Score"},
                                gauge = {
                                    'axis': {'range': [None, 1]},
                                    'bar': {'color': "darkblue"},
                                    'steps': [
                                        {'range': [0, 0.3], 'color': "lightgreen"},
                                        {'range': [0.3, 0.7], 'color': "yellow"},
                                        {'range': [0.7, 1], 'color': "lightcoral"}
                                    ],
                                    'threshold': {
                                        'line': {'color': "red", 'width': 4},
                                        'thickness': 0.75,
                                        'value': 0.7
                                    }
                                }
                            ))

                            st.plotly_chart(fig, use_container_width=True)

                        st.subheader("📝 Reasoning")
                        st.write(reasoning)

                        # Download results
                        if st.button("Download Evaluation Results"):
                            st.download_button(
                                label="Download Evaluation Results",
                                data=json.dumps(evaluation_data, indent=2),
                                file_name=f"evaluation_{contract_file.name}.json",
                                mime="application/json"
                            )

                except Exception as e:
                    st.error(f"Evaluation failed: {str(e)}")

        elif evaluate_btn:
            st.error("Please upload a PDF file for evaluation")

    else:
        st.info("Manual clause evaluation feature coming soon...")
        st.markdown("""
        This feature will allow you to:
        - Input contract clauses manually
        - Evaluate based on predefined clause types
        - Get detailed risk assessments for each clause type
        """)

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