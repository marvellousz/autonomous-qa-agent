"""
Streamlit UI for Autonomous QA Agent.
"""
import streamlit as st
import requests
import os
import json
from pathlib import Path

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Autonomous QA Agent",
    layout="wide"
)

# Initialize session state
if "test_cases" not in st.session_state:
    st.session_state.test_cases = []
if "checkout_html" not in st.session_state:
    st.session_state.checkout_html = ""

st.title("Autonomous QA Agent")
st.markdown("Build knowledge base, generate test cases, and create Selenium scripts!")

# Sidebar for navigation
page = st.sidebar.selectbox(
    "Navigation",
    ["Upload Documents", "Test Case Generation", "Selenium Script Generation"]
)

# Health check indicator
try:
    health_response = requests.get(f"{API_BASE_URL}/health", timeout=2)
    if health_response.status_code == 200:
        st.sidebar.success("API Connected")
    else:
        st.sidebar.warning("API Health Check Failed")
except:
    st.sidebar.error("API Not Connected")


# Page 1: Upload Documents
if page == "Upload Documents":
    st.header("Upload Documents")
    st.markdown("Upload documentation files and checkout HTML to build the knowledge base.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Documentation Files")
        uploaded_docs = st.file_uploader(
            "Upload documentation files",
            type=["pdf", "txt", "md", "json"],
            accept_multiple_files=True,
            help="Upload PDF, TXT, MD, or JSON files"
        )
        
        if uploaded_docs:
            st.info(f"{len(uploaded_docs)} file(s) selected")
            for doc in uploaded_docs:
                st.write(f"- {doc.name}")
    
    with col2:
        st.subheader("Checkout HTML")
        html_option = st.radio(
            "Choose input method:",
            ["Upload HTML file", "Paste HTML content"],
            key="html_input_method"
        )
        
        if html_option == "Upload HTML file":
            uploaded_html = st.file_uploader(
                "Upload checkout.html",
                type=["html", "htm"],
                help="Upload the checkout.html file"
            )
            if uploaded_html:
                st.session_state.checkout_html = uploaded_html.read().decode('utf-8')
                st.success(f"HTML file loaded: {uploaded_html.name}")
        else:
            html_content = st.text_area(
                "Paste HTML content:",
                value=st.session_state.checkout_html,
                height=200,
                help="Paste the checkout.html content here"
            )
            st.session_state.checkout_html = html_content
            if html_content:
                st.success("HTML content saved")
    
    st.divider()
    
    # Build Knowledge Base button
    if st.button("Build Knowledge Base", type="primary", use_container_width=True):
        if not uploaded_docs and not st.session_state.checkout_html:
            st.error("Please upload at least one document or provide HTML content.")
        else:
            with st.spinner("Building knowledge base..."):
                try:
                    files_data = []
                    
                    # Add documentation files
                    if uploaded_docs:
                        for uploaded_file in uploaded_docs:
                            files_data.append(("files", (uploaded_file.name, uploaded_file.read(), uploaded_file.type)))
                            uploaded_file.seek(0)
                    
                    # Add HTML file if provided
                    if st.session_state.checkout_html:
                        html_bytes = st.session_state.checkout_html.encode('utf-8')
                        files_data.append(("files", ("checkout.html", html_bytes, "text/html")))
                    
                    if files_data:
                        response = requests.post(
                            f"{API_BASE_URL}/api/ingestion/build_kb",
                            files=files_data,
                            timeout=120
                        )
                        response.raise_for_status()
                        result = response.json()
                        
                        st.success(f"✅ {result.get('status', 'KB Built Successfully')}")
                        st.info(f"📄 Files processed: {result.get('files_processed', 0)}")
                        st.info(f"📦 Total chunks: {result.get('total_chunks', 0)}")
                        
                        # Show stats
                        try:
                            stats_response = requests.get(f"{API_BASE_URL}/api/ingestion/stats")
                            if stats_response.status_code == 200:
                                stats = stats_response.json()
                                st.metric("Total Documents in KB", stats.get("total_documents", 0))
                        except:
                            pass
                    else:
                        st.error("No files to process.")
                        
                except requests.exceptions.RequestException as e:
                    st.error(f"Error building knowledge base: {str(e)}")
                    if hasattr(e, 'response') and e.response is not None:
                        try:
                            error_detail = e.response.json()
                            st.json(error_detail)
                        except:
                            pass


# Page 2: Test Case Generation
elif page == "Test Case Generation":
    st.header("Test Case Generation")
    st.markdown("Enter a feature description to generate test cases based on your knowledge base.")
    
    feature_input = st.text_input(
        "Enter feature to test:",
        placeholder="e.g., Generate test cases for discount code functionality",
        key="feature_input"
    )
    
    col1, col2 = st.columns([2, 1])
    with col1:
        k_chunks = st.slider("Number of context chunks:", min_value=3, max_value=10, value=5)
    with col2:
        output_format = st.selectbox("Output format:", ["json", "markdown"], index=0)
    
    if st.button("Generate Test Cases", type="primary", use_container_width=True):
        if not feature_input:
            st.warning("Please enter a feature description.")
        else:
            with st.spinner("Generating test cases..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/api/generation/generate_test_cases",
                        json={
                            "query": feature_input,
                            "k": k_chunks,
                            "max_tokens": 2000,
                            "output_format": output_format
                        },
                        timeout=120
                    )
                    response.raise_for_status()
                    result = response.json()
                    
                    if result.get("status") == "success":
                        st.success("Test cases generated successfully!")
                        
                        # Store test cases in session state
                        test_cases_data = result.get("test_cases", {})
                        if isinstance(test_cases_data, dict):
                            # If it's a dict, try to extract test cases
                            if "raw_response" in test_cases_data:
                                # Markdown format stored in raw_response
                                st.session_state.test_cases = [{"raw": test_cases_data["raw_response"]}]
                            else:
                                # JSON format - store as list
                                if isinstance(test_cases_data, list):
                                    st.session_state.test_cases = test_cases_data
                                else:
                                    st.session_state.test_cases = [test_cases_data]
                        else:
                            st.session_state.test_cases = [{"raw": str(test_cases_data)}]
                        
                        # Display test cases in collapsible sections
                        st.subheader("Generated Test Cases")
                        
                        if output_format == "json":
                            # Try to parse and display structured test cases
                            if isinstance(test_cases_data, dict) and "raw_response" not in test_cases_data:
                                # Display each test case in an expander
                                for idx, (key, value) in enumerate(test_cases_data.items(), 1):
                                    with st.expander(f"Test Case {idx}: {key}", expanded=False):
                                        if isinstance(value, dict):
                                            for field, content in value.items():
                                                st.write(f"**{field}:**")
                                                st.write(content)
                                        else:
                                            st.write(value)
                            else:
                                # Display raw response
                                st.json(test_cases_data)
                        else:
                            # Markdown format
                            with st.expander("View Test Cases", expanded=True):
                                st.markdown(test_cases_data.get("raw_response", str(test_cases_data)))
                        
                        # Show grounding information
                        if result.get("grounded_in"):
                            st.info(f"📚 Grounded in: {', '.join(result['grounded_in'])}")
                        
                        # Show sources
                        if result.get("sources"):
                            with st.expander("View Sources"):
                                for i, source in enumerate(result["sources"], 1):
                                    st.write(f"**Source {i}:** {source.get('source', 'Unknown')}")
                                    if source.get('type'):
                                        st.write(f"Type: {source['type']}")
                    else:
                        st.error("Failed to generate test cases.")
                        st.json(result)
                        
                except requests.exceptions.RequestException as e:
                    st.error(f"Error generating test cases: {str(e)}")
                    if hasattr(e, 'response') and e.response is not None:
                        try:
                            error_detail = e.response.json()
                            st.json(error_detail)
                        except:
                            pass


# Page 3: Selenium Script Generation
elif page == "Selenium Script Generation":
    st.header("Selenium Script Generation")
    st.markdown("Select a test case and generate a runnable Selenium script.")
    
    # Check if test cases exist
    if not st.session_state.test_cases:
        st.warning("⚠️ No test cases available. Please generate test cases first.")
        st.info("Go to 'Test Case Generation' page to create test cases.")
    else:
        # Test case selection
        test_case_options = []
        for idx, tc in enumerate(st.session_state.test_cases):
            if isinstance(tc, dict):
                test_id = tc.get("Test_ID", f"TC_{idx+1}")
                feature = tc.get("Feature", "Unknown Feature")
                test_case_options.append(f"{test_id} - {feature}")
            else:
                test_case_options.append(f"Test Case {idx+1}")
        
        selected_idx = st.selectbox(
            "Choose a test case:",
            range(len(test_case_options)),
            format_func=lambda x: test_case_options[x]
        )
        
        selected_test_case = st.session_state.test_cases[selected_idx]
        
        # Display selected test case
        with st.expander("Selected Test Case Details", expanded=True):
            if isinstance(selected_test_case, dict):
                if "raw" in selected_test_case:
                    st.markdown(selected_test_case["raw"])
                else:
                    for key, value in selected_test_case.items():
                        st.write(f"**{key}:** {value}")
            else:
                st.write(selected_test_case)
        
        # HTML content check
        if not st.session_state.checkout_html:
            st.warning("⚠️ No checkout HTML available. Please upload HTML in 'Upload Documents' page.")
            html_input = st.text_area(
                "Or paste HTML content here:",
                height=150,
                help="Paste checkout.html content"
            )
            if html_input:
                st.session_state.checkout_html = html_input
        else:
            st.success("✅ Checkout HTML available")
            with st.expander("View HTML Content"):
                st.code(st.session_state.checkout_html[:500] + "..." if len(st.session_state.checkout_html) > 500 else st.session_state.checkout_html, language="html")
        
        # URL input
        test_url = st.text_input(
            "Test URL (optional):",
            placeholder="https://example.com/checkout",
            help="URL where the test will run"
        )
        
        st.divider()
        
        # Generate script button
        if st.button("Generate Selenium Script", type="primary", use_container_width=True):
            if not st.session_state.checkout_html:
                st.error("Please provide checkout HTML content.")
            else:
                with st.spinner("Generating Selenium script..."):
                    try:
                        # Prepare test case data
                        if isinstance(selected_test_case, dict) and "raw" not in selected_test_case:
                            test_case_data = selected_test_case
                        else:
                            # Create a basic test case structure
                            test_case_data = {
                                "Test_ID": f"TC_{selected_idx+1}",
                                "Feature": "Checkout",
                                "Scenario": "Automated test scenario",
                                "Steps": str(selected_test_case),
                                "Expected_Result": "Test passes"
                            }
                        
                        response = requests.post(
                            f"{API_BASE_URL}/api/generation/generate_script",
                            json={
                                "test_case": test_case_data,
                                "checkout_html": st.session_state.checkout_html,
                                "url": test_url if test_url else None,
                                "k": 5,
                                "max_tokens": 3000
                            },
                            timeout=120
                        )
                        response.raise_for_status()
                        result = response.json()
                        
                        if result.get("status") == "success":
                            st.success("✅ Selenium script generated successfully!")
                            
                            # Display script
                            st.subheader("Generated Python Script")
                            script_code = result.get("script", "")
                            st.code(script_code, language="python")
                            
                            # Copy button (using download button as workaround for copy)
                            st.download_button(
                                label="📋 Copy Script",
                                data=script_code,
                                file_name=f"selenium_script_{result.get('test_id', 'TC')}.py",
                                mime="text/x-python",
                                use_container_width=True
                            )
                            
                            # Show metadata
                            if result.get("selectors_used"):
                                st.info(f"📊 Selectors used: {result['selectors_used'].get('ids_count', 0)} IDs, "
                                       f"{result['selectors_used'].get('names_count', 0)} names, "
                                       f"{result['selectors_used'].get('classes_count', 0)} classes")
                            
                            if result.get("sources"):
                                with st.expander("Documentation Sources Used"):
                                    for source in result["sources"]:
                                        st.write(f"- {source.get('source', 'Unknown')}")
                        else:
                            st.error("Failed to generate script.")
                            st.json(result)
                            
                    except requests.exceptions.RequestException as e:
                        st.error(f"Error generating script: {str(e)}")
                        if hasattr(e, 'response') and e.response is not None:
                            try:
                                error_detail = e.response.json()
                                st.json(error_detail)
                            except:
                                pass
