"""
Streamlit UI for QA agent.
"""
import streamlit as st
import requests
import os
import json
import re
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Page config must be first
st.set_page_config(
    page_title="Autonomous QA Agent",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Config
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Custom CSS
st.markdown("""
    <style>
    /* Main styling */
    .main {
        padding-top: 2rem;
    }
    
    /* Headers */
    h1 {
        color: #2563eb;
        border-bottom: 3px solid #2563eb;
        padding-bottom: 0.5rem;
    }
    
    h2 {
        color: #1e40af;
        margin-top: 2rem;
    }
    
    /* Cards */
    .card {
        background-color: #f8fafc;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #2563eb;
        margin: 1rem 0;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(37, 99, 235, 0.3);
    }
    
    /* Success messages */
    .success-box {
        background-color: #d1fae5;
        border-left: 4px solid #10b981;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    /* Error messages */
    .error-box {
        background-color: #fee2e2;
        border-left: 4px solid #ef4444;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    /* Info boxes */
    .info-box {
        background-color: #dbeafe;
        border-left: 4px solid #2563eb;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    /* Metrics */
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #f8fafc;
    }
    
    /* Code blocks */
    .stCodeBlock {
        border-radius: 8px;
        border: 1px solid #e5e7eb;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #1e40af;
    }
    
    /* Stepper Navigation Styles */
    .stepper-container {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        margin: 1.5rem 0;
    }
    
    .step-item {
        display: flex;
        align-items: center;
        padding: 0.75rem 1rem;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid transparent;
        background: rgba(255, 255, 255, 0.05);
        margin-bottom: 0.5rem;
    }
    
    .step-item:hover {
        background: rgba(255, 255, 255, 0.15);
        transform: translateX(4px);
        border-color: rgba(102, 126, 234, 0.5);
    }
    
    .step-item.clickable {
        cursor: pointer;
    }
    
    .step-item.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .step-item.completed {
        background: rgba(16, 185, 129, 0.1);
        border-color: #10b981;
    }
    
    .step-number {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.875rem;
        margin-right: 0.75rem;
        background: rgba(255, 255, 255, 0.1);
        color: white;
        border: 2px solid rgba(255, 255, 255, 0.2);
    }
    
    .step-item.active .step-number {
        background: white;
        color: #667eea;
        border-color: white;
    }
    
    .step-item.completed .step-number {
        background: #10b981;
        color: white;
        border-color: #10b981;
    }
    
    .step-content {
        flex: 1;
    }
    
    .step-title {
        font-weight: 600;
        font-size: 0.95rem;
        color: white;
        margin-bottom: 0.25rem;
    }
    
    .step-item.active .step-title {
        color: white;
    }
    
    .step-description {
        font-size: 0.75rem;
        color: rgba(255, 255, 255, 0.7);
        margin: 0;
    }
    
    .step-item.active .step-description {
        color: rgba(255, 255, 255, 0.9);
    }
    
    .step-connector {
        width: 2px;
        height: 24px;
        background: rgba(255, 255, 255, 0.1);
        margin-left: 15px;
        margin-top: 0.25rem;
        margin-bottom: 0.25rem;
    }
    
    .step-item.completed + .step-connector {
        background: #10b981;
    }
    </style>
""", unsafe_allow_html=True)

# Init session state
def init_session_state():
    """Init session state."""
    defaults = {
        "test_cases": [],
        "checkout_html": "",
        "last_save": None,
        "kb_stats": None,
        "current_step": 1
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    # Auto-load checkout.html if exists
    if not st.session_state.checkout_html:
        assets_path = Path(__file__).parent.parent / "assets" / "checkout.html"
        if assets_path.exists():
            try:
                with open(assets_path, 'r', encoding='utf-8') as f:
                    st.session_state.checkout_html = f.read()
            except Exception:
                pass

def autosave_session():
    """Autosave session."""
    try:
        st.session_state.last_save = datetime.now().isoformat()
    except Exception as e:
        pass

def load_session():
    """Load session."""
    try:
        pass
    except Exception:
        pass

def parse_markdown_test_cases(markdown_text: str) -> list:
    """Parse markdown test cases to list of dicts."""
    if not markdown_text or not isinstance(markdown_text, str):
        return []
    
    try:
        test_cases = []
        current_case = {}
        current_field = None
        steps_list = []
        
        lines = markdown_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Parse Test_ID
            if line.startswith('Test_ID:') or line.startswith('**Test_ID:**'):
                if current_case:
                    if steps_list:
                        current_case['Steps'] = steps_list
                    test_cases.append(current_case)
                current_case = {}
                steps_list = []
                parts = re.split(r':\s*', line, 1)
                if len(parts) > 1:
                    test_id = parts[1].strip()
                    test_id = re.sub(r'\*\*', '', test_id)
                    current_case['Test_ID'] = test_id
                else:
                    current_case['Test_ID'] = f"TC-{len(test_cases) + 1:03d}"
            
            # Parse Feature
            elif line.startswith('Feature:') or line.startswith('**Feature:**'):
                parts = re.split(r':\s*', line, 1)
                if len(parts) > 1:
                    feature = parts[1].strip()
                    feature = re.sub(r'\*\*', '', feature)
                    current_case['Feature'] = feature
            
            # Parse Scenario
            elif line.startswith('Scenario:') or line.startswith('**Scenario:**'):
                parts = re.split(r':\s*', line, 1)
                if len(parts) > 1:
                    scenario = parts[1].strip()
                    scenario = re.sub(r'\*\*', '', scenario)
                    current_case['Scenario'] = scenario
            
            # Parse Steps
            elif line.lower().startswith('steps:') or line.startswith('**Steps:**'):
                current_field = 'steps'
                steps_list = []
            
            # Parse Expected_Result
            elif line.startswith('Expected Result:') or line.startswith('Expected_Result:') or line.startswith('**Expected Result:**') or line.startswith('**Expected_Result:**'):
                if steps_list:
                    current_case['Steps'] = steps_list
                    steps_list = []
                parts = re.split(r':\s*', line, 1)
                if len(parts) > 1:
                    expected = parts[1].strip()
                    expected = re.sub(r'\*\*', '', expected)
                    current_case['Expected_Result'] = expected
                current_field = None
            
            # Parse Grounded_In
            elif line.startswith('Grounded In:') or line.startswith('Grounded_In:') or line.startswith('**Grounded In:**') or line.startswith('**Grounded_In:**'):
                parts = re.split(r':\s*', line, 1)
                if len(parts) > 1:
                    grounded = parts[1].strip()
                    grounded = re.sub(r'\*\*', '', grounded)
                    current_case['Grounded_In'] = grounded
            
            # Collect steps
            elif current_field == 'steps':
                # Match numbered steps or bullets
                if (re.match(r'^\d+\.', line) or line.startswith(('-', '*'))):
                    step_text = re.sub(r'^\d+\.\s*', '', line)
                    step_text = re.sub(r'^[-*]\s*', '', step_text)
                    step_text = re.sub(r'\*\*', '', step_text)
                    if step_text.strip():
                        steps_list.append(step_text.strip())
        
        # Add last test case
        if current_case:
            if steps_list:
                current_case['Steps'] = steps_list
            # Ensure required fields
            if 'Test_ID' not in current_case:
                current_case['Test_ID'] = f"TC-{len(test_cases) + 1:03d}"
            if 'Steps' not in current_case:
                current_case['Steps'] = []
            test_cases.append(current_case)
        
        return test_cases if test_cases else []
    
    except Exception as e:
        print(f"Error parsing markdown test cases: {str(e)}")
        return []

def handle_api_error(e, operation="operation"):
    """Handle API errors."""
    error_msg = f"Error during {operation}"
    
    if isinstance(e, requests.exceptions.ConnectionError):
        error_msg = f"Cannot connect to API. Please ensure the backend is running at {API_BASE_URL}"
    elif isinstance(e, requests.exceptions.Timeout):
        error_msg = f"Request timed out. The {operation} is taking too long. Please try again."
    elif isinstance(e, requests.exceptions.HTTPError):
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                if "detail" in error_detail:
                    error_msg = f"{error_msg}: {error_detail['detail']}"
                else:
                    error_msg = f"{error_msg}: {str(error_detail)}"
            except:
                error_msg = f"{error_msg}: HTTP {e.response.status_code}"
    else:
        error_msg = f"{error_msg}: {str(e)}"
    
    return error_msg

# Init session
init_session_state()
load_session()

# Title
st.markdown("<h1>Autonomous QA Agent</h1>", unsafe_allow_html=True)
st.markdown("Build knowledge base, generate test cases, and create Selenium scripts!")

# Sidebar
with st.sidebar:
    st.markdown("### Navigation")
    
    # Define steps
    steps = [
        {
            "number": 1,
            "title": "Upload Documents",
            "description": "Build knowledge base"
        },
        {
            "number": 2,
            "title": "Test Case Generation",
            "description": "Generate test cases"
        },
        {
            "number": 3,
            "title": "Selenium Script",
            "description": "Create scripts"
        }
    ]
    
    # Render visual stepper with clickable buttons
    for idx, step in enumerate(steps):
        step_num = step["number"]
        is_active = st.session_state.current_step == step_num
        is_completed = st.session_state.current_step > step_num
        
        # Create button with step info
        if is_completed:
            button_text = f"✓ Step {step_num}: {step['title']}"
        else:
            button_text = f"{step_num}. {step['title']}"
        
        if st.button(
            button_text,
            key=f"nav_step_{step_num}",
            use_container_width=True,
            type="primary" if is_active else "secondary"
        ):
            st.session_state.current_step = step_num
            st.rerun()
        
        # Show description below button
        desc_text = step['description']
        if is_active:
            st.caption(f"📍 {desc_text}")
        elif is_completed:
            st.caption(f"✓ {desc_text}")
        else:
            st.caption(desc_text)
        
        # Add spacing between steps
        if idx < len(steps) - 1:
            st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation arrows - always show both buttons for consistent sizing
    nav_col1, nav_col2 = st.columns(2)
    with nav_col1:
        prev_enabled = st.session_state.current_step > 1
        if st.button("◄ Prev", key="prev_step", use_container_width=True, disabled=not prev_enabled):
            if prev_enabled:
                st.session_state.current_step -= 1
                st.rerun()
    with nav_col2:
        next_enabled = st.session_state.current_step < len(steps)
        if st.button("Next ►", key="next_step", use_container_width=True, disabled=not next_enabled):
            if next_enabled:
                st.session_state.current_step += 1
                st.rerun()
    
    # Map step to page name for compatibility
    page_map = {
        1: "Upload Documents",
        2: "Test Case Generation",
        3: "Selenium Script Generation"
    }
    page = page_map.get(st.session_state.current_step, "Upload Documents")
    
    st.divider()
    
    # Health check
    st.markdown("### System Status")
    try:
        health_response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if health_response.status_code == 200:
            st.success("API Connected")
            health_data = health_response.json()
            if "vectordb" in health_data:
                st.metric("Documents in KB", health_data["vectordb"].get("total_documents", 0))
        else:
            st.warning("API Health Check Failed")
    except Exception:
        st.error("API Not Connected")
    
    st.divider()
    
    # Session info
    if st.session_state.last_save:
        st.caption(f"Last saved: {st.session_state.last_save[:19] if len(st.session_state.last_save) > 19 else st.session_state.last_save}")

# Upload Documents page
if page == "Upload Documents":
    st.header("Upload Documents")
    st.markdown("Upload documentation files and checkout HTML to build the knowledge base.")
    
    # Knowledge Base Management Section
    with st.expander("Knowledge Base Management", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Refresh Stats", use_container_width=True):
                try:
                    response = requests.get(f"{API_BASE_URL}/api/ingestion/stats", timeout=5)
                    response.raise_for_status()
                    stats = response.json()
                    st.session_state.kb_stats = stats
                    st.success(f"Knowledge Base contains {stats.get('total_documents', 0)} documents")
                    st.json(stats)
                except Exception as e:
                    error_msg = handle_api_error(e, "fetching stats")
                    st.error(error_msg)
        
        with col2:
            if st.button("Clear Knowledge Base", type="secondary", use_container_width=True):
                try:
                    response = requests.delete(f"{API_BASE_URL}/api/ingestion/clear", timeout=10)
                    response.raise_for_status()
                    result = response.json()
                    st.success(f"Knowledge base cleared. {result.get('documents_cleared', 0)} documents removed.")
                    st.session_state.kb_stats = None
                    st.session_state.test_cases = []  # Clear test cases too
                    autosave_session()
                except Exception as e:
                    error_msg = handle_api_error(e, "clearing knowledge base")
                    st.error(error_msg)
    
    # Documentation Files section (first)
    st.subheader("Documentation Files")
    uploaded_docs = st.file_uploader(
        "Upload documentation files",
        type=["pdf", "txt", "md", "json"],
        accept_multiple_files=True,
        help="Upload PDF, TXT, MD, or JSON files",
        label_visibility="collapsed"
    )
    
    if uploaded_docs:
        st.success(f"{len(uploaded_docs)} file(s) selected")
        for doc in uploaded_docs:
            st.markdown(f"**{doc.name}**")
    else:
        st.info("Upload your documentation files here")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Checkout HTML section (second)
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
            help="Upload the checkout.html file",
            key="html_uploader"
        )
        if uploaded_html:
            st.session_state.checkout_html = uploaded_html.read().decode('utf-8')
            st.success(f"HTML file loaded: {uploaded_html.name}")
            autosave_session()
    else:
        html_content = st.text_area(
            "Paste HTML content:",
            value=st.session_state.checkout_html,
            height=200,
            help="Paste the checkout.html content here",
            key="html_textarea"
        )
        if html_content != st.session_state.checkout_html:
            st.session_state.checkout_html = html_content
            autosave_session()
        if html_content:
            st.success("HTML content saved")
    
    st.divider()
    
    # Clear KB option
    clear_before_build = st.checkbox(
        "Clear existing knowledge base before building",
        value=True,
        help="If checked, existing documents will be cleared before adding new ones. Uncheck to append to existing KB."
    )
    
    # Build KB button
    if st.button("Build Knowledge Base", type="primary", use_container_width=True):
        if not uploaded_docs and not st.session_state.checkout_html:
            st.error("Please upload at least one document or provide HTML content.")
        else:
            with st.spinner("Building knowledge base..."):
                try:
                    # Clear KB if requested
                    if clear_before_build:
                        try:
                            clear_response = requests.delete(f"{API_BASE_URL}/api/ingestion/clear", timeout=10)
                            if clear_response.status_code == 200:
                                st.info("Cleared existing knowledge base")
                        except Exception as e:
                            st.warning(f"Could not clear existing KB: {str(e)}. Continuing with append...")
                    
                    files_data = []
                    
                    # Add docs
                    if uploaded_docs:
                        for uploaded_file in uploaded_docs:
                            files_data.append(("files", (uploaded_file.name, uploaded_file.read(), uploaded_file.type)))
                            uploaded_file.seek(0)
                    
                    # Add HTML
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
                        
                        st.success(f"{result.get('status', 'KB Built Successfully')}")
                        st.info(f"Files processed: {result.get('files_processed', 0)}")
                        st.info(f"Total chunks: {result.get('total_chunks', 0)}")
                        
                        # Show stats
                        try:
                            stats_response = requests.get(f"{API_BASE_URL}/api/ingestion/stats", timeout=5)
                            if stats_response.status_code == 200:
                                stats = stats_response.json()
                                st.session_state.kb_stats = stats
                                st.metric("Total Documents in KB", stats.get("total_documents", 0))
                        except Exception:
                            pass
                        
                        autosave_session()
                    else:
                        st.error("No files to process.")
                        
                except requests.exceptions.RequestException as e:
                    error_msg = handle_api_error(e, "building knowledge base")
                    st.error(error_msg)
                    if hasattr(e, 'response') and e.response is not None:
                        try:
                            error_detail = e.response.json()
                            with st.expander("Error Details"):
                                st.json(error_detail)
                        except:
                            pass


# Test Case Generation page
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
                        if isinstance(test_cases_data, list):
                            # Direct list of test cases (most common case for JSON format)
                            st.session_state.test_cases = test_cases_data
                        elif isinstance(test_cases_data, dict):
                            if "raw_response" in test_cases_data:
                                # Try to parse markdown test cases from raw_response
                                parsed = parse_markdown_test_cases(test_cases_data["raw_response"])
                                if parsed:
                                    st.session_state.test_cases = parsed
                                else:
                                    # If parsing fails, store as raw
                                    st.session_state.test_cases = [{"raw": test_cases_data["raw_response"]}]
                            else:
                                # Single test case dict, wrap in list
                                st.session_state.test_cases = [test_cases_data]
                        elif isinstance(test_cases_data, str):
                            # Markdown format string - try to parse it
                            parsed = parse_markdown_test_cases(test_cases_data)
                            if parsed:
                                st.session_state.test_cases = parsed
                            else:
                                # If parsing fails, store as raw
                                st.session_state.test_cases = [{"raw": test_cases_data}]
                        else:
                            # Fallback: treat as raw string/markdown
                            markdown_str = str(test_cases_data)
                            parsed = parse_markdown_test_cases(markdown_str)
                            if parsed:
                                st.session_state.test_cases = parsed
                            else:
                                st.session_state.test_cases = [{"raw": markdown_str}]
                        
                        autosave_session()
                        
                        # Display test cases
                        st.subheader("Generated Test Cases")
                        
                        if output_format == "json":
                            # Handle list of test cases
                            if isinstance(test_cases_data, list):
                                for idx, test_case in enumerate(test_cases_data, 1):
                                    test_id = test_case.get("Test_ID", f"TC-{idx}") if isinstance(test_case, dict) else f"TC-{idx}"
                                    with st.expander(f"Test Case {idx}: {test_id}", expanded=False):
                                        if isinstance(test_case, dict):
                                            for field, content in test_case.items():
                                                if field == "Steps" and isinstance(content, list):
                                                    st.write(f"**{field}:**")
                                                    for step_idx, step in enumerate(content, 1):
                                                        st.write(f"{step_idx}. {step}")
                                                else:
                                                    st.write(f"**{field}:** {content}")
                                        else:
                                            st.write(test_case)
                            # Handle dict with raw_response
                            elif isinstance(test_cases_data, dict):
                                if "raw_response" in test_cases_data:
                                    # Try to parse markdown from raw_response
                                    parsed = parse_markdown_test_cases(test_cases_data["raw_response"])
                                    if parsed:
                                        for idx, test_case in enumerate(parsed, 1):
                                            test_id = test_case.get("Test_ID", f"TC-{idx}")
                                            with st.expander(f"Test Case {idx}: {test_id}", expanded=False):
                                                for field, content in test_case.items():
                                                    if field == "Steps" and isinstance(content, list):
                                                        st.write(f"**{field}:**")
                                                        for step_idx, step in enumerate(content, 1):
                                                            st.write(f"{step_idx}. {step}")
                                                    else:
                                                        st.write(f"**{field}:** {content}")
                                    else:
                                        st.markdown(test_cases_data["raw_response"])
                                else:
                                    # Single test case dict or other dict structure
                                    for idx, (key, value) in enumerate(test_cases_data.items(), 1):
                                        with st.expander(f"Test Case {idx}: {key}", expanded=False):
                                            if isinstance(value, dict):
                                                for field, content in value.items():
                                                    st.write(f"**{field}:**")
                                                    st.write(content)
                                            else:
                                                st.write(value)
                            else:
                                # Fallback: display as JSON
                                st.json(test_cases_data)
                        else:
                            # Markdown format
                            with st.expander("View Test Cases", expanded=True):
                                # Handle both string and dict responses
                                if isinstance(test_cases_data, str):
                                    st.markdown(test_cases_data)
                                elif isinstance(test_cases_data, dict):
                                    # Check if it's a dict with raw_response or just the markdown content
                                    if "raw_response" in test_cases_data:
                                        st.markdown(test_cases_data["raw_response"])
                                    else:
                                        st.markdown(str(test_cases_data))
                                else:
                                    st.markdown(str(test_cases_data))
                        
                        # Show grounding information
                        if result.get("grounded_in"):
                            st.info(f"Grounded in: {', '.join(result['grounded_in'])}")
                        
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
                    error_msg = handle_api_error(e, "generating test cases")
                    st.error(error_msg)
                    if hasattr(e, 'response') and e.response is not None:
                        try:
                            error_detail = e.response.json()
                            with st.expander("Error Details"):
                                st.json(error_detail)
                        except:
                            pass


# Selenium Script Generation page
elif page == "Selenium Script Generation":
    st.header("Selenium Script Generation")
    st.markdown("Select a test case and generate a runnable Selenium script.")
    
    # Check if test cases exist
    if not st.session_state.test_cases:
        st.warning("No test cases available. Please generate test cases first.")
        st.info("Go to 'Test Case Generation' page to create test cases.")
    else:
        # Test case selection
        test_case_options = []
        for idx, tc in enumerate(st.session_state.test_cases):
            if isinstance(tc, dict):
                # Skip raw markdown
                if "raw" in tc:
                    test_case_options.append(f"Test Case {idx+1} (Markdown)")
                else:
                    # Try field variations
                    test_id = tc.get("Test_ID") or tc.get("test_id") or f"TC_{idx+1}"
                    feature = tc.get("Feature") or tc.get("feature") or "Unknown Feature"
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
        
        # HTML check
        if not st.session_state.checkout_html:
            st.warning("No checkout HTML available. Please upload HTML in 'Upload Documents' page.")
            html_input = st.text_area(
                "Or paste HTML content here:",
                height=150,
                help="Paste checkout.html content",
                key="html_fallback"
            )
            if html_input:
                st.session_state.checkout_html = html_input
                autosave_session()
        else:
            st.success("Checkout HTML available")
            with st.expander("View HTML Content"):
                html_preview = st.session_state.checkout_html[:500] + "..." if len(st.session_state.checkout_html) > 500 else st.session_state.checkout_html
                st.code(html_preview, language="html")
        
        # URL input
        test_url = st.text_input(
            "Test URL (optional):",
            placeholder="https://example.com/checkout",
            help="URL where the test will run",
            key="test_url"
        )
        
        st.divider()
        
        # Generate script button
        if st.button("Generate Selenium Script", type="primary", use_container_width=True):
            if not st.session_state.checkout_html:
                st.error("Please provide checkout HTML content.")
            else:
                with st.spinner("Generating Selenium script..."):
                    try:
                        # Prep test case data
                        if isinstance(selected_test_case, dict) and "raw" not in selected_test_case:
                            test_case_data = selected_test_case
                        else:
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
                            st.success("Selenium script generated successfully!")
                            
                            # Store script
                            script_code = result.get("script", "")
                            st.session_state[f"script_{selected_idx}"] = script_code
                            autosave_session()
                            
                            # Display script
                            st.subheader("Generated Python Script")
                            st.code(script_code, language="python")
                            
                            # Download button
                            st.download_button(
                                label="Download Script",
                                data=script_code,
                                file_name=f"selenium_script_{result.get('test_id', 'TC')}.py",
                                mime="text/x-python",
                                use_container_width=True,
                                type="primary"
                            )
                            
                            # Show metadata
                            if result.get("selectors_used"):
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("IDs", result['selectors_used'].get('ids_count', 0))
                                with col2:
                                    st.metric("Names", result['selectors_used'].get('names_count', 0))
                                with col3:
                                    st.metric("Classes", result['selectors_used'].get('classes_count', 0))
                            
                            if result.get("sources"):
                                with st.expander("Documentation Sources Used"):
                                    for source in result["sources"]:
                                        st.write(f"- {source.get('source', 'Unknown')}")
                        else:
                            st.error("Failed to generate script.")
                            st.json(result)
                            
                    except requests.exceptions.RequestException as e:
                        error_msg = handle_api_error(e, "generating script")
                        st.error(error_msg)
                        if hasattr(e, 'response') and e.response is not None:
                            try:
                                error_detail = e.response.json()
                                with st.expander("Error Details"):
                                    st.json(error_detail)
                            except:
                                pass
