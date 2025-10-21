import os
import json
from datetime import datetime

AUDIT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.feedback', 'audit')

def ensure_audit_dir():
    os.makedirs(AUDIT_DIR, exist_ok=True)

def write_audit_event(event_type: str, payload: dict):
    """Write a timestamped audit event JSON to .feedback/audit/.

    event_type: short string like 'structured_fallback' or 'validation_failure'
    payload: JSON-serializable dict with details
    """
    ensure_audit_dir()
    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    filename = f"{ts}_{event_type}.json"
    path = os.path.join(AUDIT_DIR, filename)
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({"timestamp": ts, "event": event_type, "payload": payload}, f, indent=2)
    except Exception:
        # Do not propagate audit errors to callers; log to stderr as best-effort
        try:
            import sys
            print(f"Failed to write audit event to {path}", file=sys.stderr)
        except Exception:
            pass
