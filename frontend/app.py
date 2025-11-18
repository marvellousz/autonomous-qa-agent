"""
Streamlit UI for Autonomous QA Agent.
"""
import streamlit as st
import requests
import os
from pathlib import Path

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Autonomous QA Agent",
    layout="wide"
)

st.title("Autonomous QA Agent")
st.markdown("Upload documents and ask questions!")


# Sidebar for navigation
page = st.sidebar.selectbox(
    "Navigation",
    ["Document Ingestion", "Question Answering", "Selenium Script Generator", "Statistics"]
)


# Document Ingestion Page
if page == "Document Ingestion":
    st.header("Document Ingestion")
    
    uploaded_files = st.file_uploader(
        "Upload documents",
        type=["pdf", "html", "htm", "json", "txt"],
        accept_multiple_files=True
    )
    
    if st.button("Ingest Documents", type="primary"):
        if uploaded_files:
            with st.spinner("Processing documents..."):
                files_data = []
                for uploaded_file in uploaded_files:
                    files_data.append(("files", (uploaded_file.name, uploaded_file.read(), uploaded_file.type)))
                    uploaded_file.seek(0)  # Reset file pointer
                
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/api/ingestion/upload-multiple",
                        files=files_data
                    )
                    response.raise_for_status()
                    result = response.json()
                    
                    st.success(f"Successfully ingested {result['total_files']} file(s)!")
                    st.json(result)
                except requests.exceptions.RequestException as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please upload at least one document.")


# Question Answering Page
elif page == "Question Answering":
    st.header("Question Answering")
    
    question = st.text_input("Enter your question:", placeholder="What is this document about?")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        max_tokens = st.slider("Max tokens:", min_value=100, max_value=2000, value=500)
    
    if st.button("Get Answer", type="primary"):
        if question:
            with st.spinner("Generating answer..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/api/generation/qa",
                        json={
                            "question": question,
                            "max_tokens": max_tokens
                        }
                    )
                    response.raise_for_status()
                    result = response.json()
                    
                    st.subheader("Answer:")
                    st.write(result["answer"])
                    
                    if result.get("sources"):
                        with st.expander("View Sources"):
                            for i, source in enumerate(result["sources"], 1):
                                st.write(f"**Source {i}:** {source.get('source', 'Unknown')}")
                                if source.get('page'):
                                    st.write(f"Page: {source['page']}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a question.")


# Selenium Script Generator Page
elif page == "Selenium Script Generator":
    st.header("Selenium Script Generator")
    
    description = st.text_area(
        "Describe the automation task:",
        placeholder="e.g., Login to website, fill form, submit"
    )
    
    url = st.text_input("URL (optional):", placeholder="https://example.com")
    
    actions = st.text_area(
        "Specific actions (one per line, optional):",
        placeholder="Click login button\nEnter username\nEnter password"
    )
    
    if st.button("Generate Script", type="primary"):
        if description:
            with st.spinner("Generating Selenium script..."):
                try:
                    action_list = [a.strip() for a in actions.split("\n") if a.strip()] if actions else None
                    
                    response = requests.post(
                        f"{API_BASE_URL}/api/generation/selenium-script",
                        json={
                            "description": description,
                            "url": url if url else None,
                            "actions": action_list
                        }
                    )
                    response.raise_for_status()
                    result = response.json()
                    
                    st.subheader("Generated Script:")
                    st.code(result["script"], language="python")
                    
                    st.download_button(
                        label="Download Script",
                        data=result["script"],
                        file_name="selenium_script.py",
                        mime="text/x-python"
                    )
                except requests.exceptions.RequestException as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a task description.")


# Statistics Page
elif page == "Statistics":
    st.header("Statistics")
    
    if st.button("Refresh Stats", type="primary"):
        try:
            response = requests.get(f"{API_BASE_URL}/api/ingestion/stats")
            response.raise_for_status()
            stats = response.json()
            
            st.metric("Total Documents", stats.get("total_documents", 0))
            st.metric("Embedding Dimension", stats.get("dimension", 0))
            
            st.json(stats)
        except requests.exceptions.RequestException as e:
            st.error(f"Error: {str(e)}")
    
    # Health check
    try:
        health_response = requests.get(f"{API_BASE_URL}/health")
        if health_response.status_code == 200:
            st.success("API is healthy")
        else:
            st.warning("API health check failed")
    except:
        st.error("Cannot connect to API. Make sure the backend is running.")

