import subprocess
import sys

def install(package_name):
    # Calls pip install via the active Python executable
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

# Example usage:
if __name__ == "__main__":
    install("orjson")