import sys
import platform
import os
import site
import subprocess

def get_pip_list():
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list"], 
            capture_output=True, 
            text=True
        )
        return result.stdout
    except Exception as e:
        return f"Error getting pip list: {e}"

print("\n===== Python Environment Information =====\n")
print(f"Python Version: {platform.python_version()}")
print(f"Python Executable: {sys.executable}")
print(f"Python Path: {sys.path}")
print(f"\nSite Packages: {site.getsitepackages()}")
print(f"\nPlatform: {platform.platform()}")
print(f"\nEnvironment Variables:")
for key, value in os.environ.items():
    if "PYTHON" in key or "PATH" in key or "VIRTUAL" in key or "CONDA" in key:
        print(f"  {key}: {value}")