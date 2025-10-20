import subprocess
import shlex
import sys
from typing import Tuple, Dict, Any

# Simple allowlist of low-risk commands (exact prefixes)
ALLOWED_PREFIXES = [
    "npm run lint",
    "npm run test",
    "pytest",
    sys.executable,  # allow python commands
]


def is_low_risk(cmd: str) -> bool:
    """Return True if the command is considered low-risk according to allowlist."""
    c = cmd.strip()
    for p in ALLOWED_PREFIXES:
        if isinstance(p, str) and c.startswith(p):
            return True
    return False


def run_command(cmd: str, timeout: int = 120) -> Dict[str, Any]:
    """Run a shell command safely and return a dict with stdout/stderr/rc.

    Accepts a command string; uses shell for convenience.
    """
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return {
            "cmd": cmd,
            "returncode": res.returncode,
            "stdout": res.stdout,
            "stderr": res.stderr,
        }
    except subprocess.TimeoutExpired as e:
        return {"cmd": cmd, "returncode": None, "stdout": "", "stderr": f"Timeout: {e}"}
    except Exception as e:
        return {"cmd": cmd, "returncode": None, "stdout": "", "stderr": str(e)}
