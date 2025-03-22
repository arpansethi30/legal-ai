# streamlit_app/utils.py
import httpx
import os
import tempfile
from typing import Dict, Any, Optional

def send_request_to_api(endpoint: str, data: Dict[str, Any], files: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Send a request to the API
    
    Args:
        endpoint: API endpoint
        data: Form data
        files: Optional file data
        
    Returns:
        API response
    """
    try:
        response = httpx.post(endpoint, data=data, files=files)
        return {
            "status_code": response.status_code,
            "data": response.json() if response.status_code == 200 else {},
            "error": None if response.status_code == 200 else response.text
        }
    except Exception as e:
        return {
            "status_code": 500,
            "data": {},
            "error": str(e)
        }

def create_temp_file(uploaded_file) -> Optional[str]:
    """
    Create a temporary file from uploaded file content
    
    Args:
        uploaded_file: Streamlit uploaded file
        
    Returns:
        Path to temporary file or None if failed
    """
    try:
        if not uploaded_file:
            return None
            
        suffix = f".{uploaded_file.name.split('.')[-1]}"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(uploaded_file.getvalue())
            return temp_file.name
    except Exception as e:
        print(f"Error creating temp file: {e}")
        return None

def cleanup_temp_file(file_path: str) -> None:
    """
    Remove a temporary file
    
    Args:
        file_path: Path to file
    """
    try:
        if file_path and os.path.exists(file_path):
            os.unlink(file_path)
    except Exception as e:
        print(f"Error removing temp file: {e}")