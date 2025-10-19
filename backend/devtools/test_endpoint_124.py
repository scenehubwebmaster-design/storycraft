"""
Moved manual endpoint test script. Run manually from backend package root:

    python -m backend.devtools.test_endpoint_124

This is a manual dev script and not intended for pytest collection.
"""
from backend.test_endpoint_124 import main as _main

if __name__ == "__main__":
    _main()
"""
Manual endpoint test (moved). Run manually from devtools.
"""
print("This is a manual endpoint test placeholder. Run original script from backend/devtools if needed.")
