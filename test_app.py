#!/usr/bin/env python3
# test_app.py - Test script to verify the API and Streamlit app can run

import os
import sys
import subprocess
import time
import requests
import webbrowser

def test_api():
    """Test if the API is running correctly"""
    try:
        # Check if API is running
        response = requests.get("http://localhost:8000/healthcheck")
        if response.status_code == 200:
            print("✅ API is running correctly!")
            return True
        else:
            print("❌ API is running but returned unexpected status code:", response.status_code)
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure it's running on http://localhost:8000")
        return False

def test_streamlit():
    """Test if Streamlit is running correctly"""
    try:
        # Check if Streamlit is running
        response = requests.get("http://localhost:8501")
        if response.status_code == 200:
            print("✅ Streamlit app is running correctly!")
            return True
        else:
            print("❌ Streamlit is running but returned unexpected status code:", response.status_code)
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Streamlit. Make sure it's running on http://localhost:8501")
        return False

def main():
    """Main test function"""
    print("Testing Legal AI application...")
    
    # Set current directory as PYTHONPATH
    os.environ["PYTHONPATH"] = os.path.dirname(os.path.abspath(__file__))
    
    # Test API
    api_running = test_api()
    
    # Test Streamlit
    streamlit_running = test_streamlit()
    
    if api_running and streamlit_running:
        print("\n✅ All components are running correctly!")
        print("You can access the Streamlit app at: http://localhost:8501")
        
        # Open browser to Streamlit app
        webbrowser.open("http://localhost:8501")
        
        return True
    else:
        print("\n❌ Some components failed the test.")
        print("Please check the error messages above.")
        
        return False

if __name__ == "__main__":
    main() 