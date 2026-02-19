import subprocess
import sys
import time
import os
import urllib.request
import urllib.error
from threading import Thread
from pathlib import Path

def get_venv_python():
    # Helper to find venv python
    project_root = Path(__file__).parent
    venv_python = project_root / ".venv" / "Scripts" / "python.exe"
    if venv_python.exists():
        return str(venv_python)
    print(f"Warning: .venv not found at {venv_python}. Using system python: {sys.executable}")
    return sys.executable

def wait_for_api(url="http://127.0.0.1:8000/docs", timeout=60):
    start_time = time.time()
    print("Waiting for API to start...")
    while time.time() - start_time < timeout:
        try:
            with urllib.request.urlopen(url) as response:
                if response.status == 200:
                    print("API is ready!")
                    return True
        except (urllib.error.URLError, ConnectionResetError):
            pass
        time.sleep(2)
    print("Timeout waiting for API.")
    return False

if __name__ == "__main__":
    python_exe = get_venv_python()
    print(f"Using Python: {python_exe}")
    
    # Check if streamlit is running to prevent double instance if run_app called twice? no.
    
    print("Starting API...")
    # Added --reload for easier dev
    api_process = subprocess.Popen([python_exe, "-m", "uvicorn", "src.api.api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])
    
    if wait_for_api():
        print("Starting Frontend (Streamlit)...")
        time.sleep(2)
        frontend_process = subprocess.Popen([python_exe, "-m", "streamlit", "run", "app.py"])
        
        try:
            # Keep main script alive
            while True:
                time.sleep(1)
                # Check if processes are still running
                if api_process.poll() is not None:
                    print("API process ended unexpectedly.")
                    break
                if frontend_process.poll() is not None:
                    print("Frontend process ended.")
                    break
        except KeyboardInterrupt:
            print("Stopping services...")
            frontend_process.terminate()
            api_process.terminate()
    else:
        print("Failed to start API. Please check the console for API errors.")
        api_process.terminate()
