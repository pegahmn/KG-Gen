from io import StringIO, BytesIO
import pandas as pd
import json
import streamlit as st

def extract_text_from_file(uploaded_file, file_type: str) -> str:
    """Extracts plain text content from various uploaded file types."""
    content = ""
    try:
        if file_type == "text/plain": # Handles .txt files
            content = StringIO(uploaded_file.getvalue().decode("utf-8")).read()
        else:
            # Fallback for now - warn if not .txt but still try to read as text
            st.warning(f"Unsupported file type '{file_type}'. Currently only .txt files are fully supported. Attempting to read as plain text, results may vary.")
            content = uploaded_file.getvalue().decode("utf-8", errors="ignore") # Try to decode anyway
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return ""
    return content