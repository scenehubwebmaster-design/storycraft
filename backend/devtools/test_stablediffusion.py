"""
Moved manual Stable Diffusion integration test. Run manually from backend package root:

    python -m backend.devtools.test_stablediffusion

This is a manual dev script and not intended for pytest collection.
"""
from backend.test_stablediffusion import main as _main

if __name__ == "__main__":
    _main()
