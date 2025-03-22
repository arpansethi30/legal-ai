# backend/utils/helpers.py
import os
from typing import Dict, Any, List
import json

def format_error_response(error_message: str, status_code: int = 500) -> Dict[str, Any]:
    """Format a standard error response"""
    return {
        "success": False,
        "error": error_message,
        "status_code": status_code
    }

def get_file_extensions(file_type: str) -> List[str]:
    """Get allowed file extensions for a file type"""
    extension_map = {
        "image": ['.jpg', '.jpeg', '.png', '.tiff', '.bmp'],
        "document": ['.pdf', '.docx', '.doc', '.txt'],
        "all": ['.pdf', '.docx', '.doc', '.txt', '.jpg', '.jpeg', '.png', '.tiff', '.bmp']
    }
    return extension_map.get(file_type, [])

def validate_file_type(filename: str, allowed_types: List[str]) -> bool:
    """Validate if a file has an allowed extension"""
    file_ext = os.path.splitext(filename)[1].lower()
    return file_ext in allowed_types