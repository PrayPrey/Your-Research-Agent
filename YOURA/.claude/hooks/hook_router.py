#!/usr/bin/env python3
"""
Hook Router

Routes Stop events to phase-specific auto-responder when active_phase.json is present.
When no phase is active, allows the Stop event to proceed.

Author: Anonymous
"""

import json
import sys
from pathlib import Path

# Load .env file for API keys
try:
    from dotenv import load_dotenv
    for env_path in (
        Path(__file__).parent.parent.parent / ".env",
        Path(__file__).parent.parent.parent.parent / ".env",
    ):
        if env_path.exists():
            load_dotenv(env_path)
            break
except ImportError:
    pass

# ============================================================
# Path Configuration
# ============================================================
SCRIPT_DIR = Path(__file__).parent
ACTIVE_PHASE_FILE = SCRIPT_DIR / ".cache" / "active_phase.json"


# ============================================================
# Main Entry Point
# ============================================================
def main():
    """Main entry point for hook router."""
    # Read hook info from stdin
    hook_info = {}
    try:
        if not sys.stdin.isatty():
            stdin_data = sys.stdin.read()
            if stdin_data.strip():
                hook_info = json.loads(stdin_data)
    except Exception:
        pass

    # Phase-specific routing (check active_phase.json before default)
    if ACTIVE_PHASE_FILE.exists():
        try:
            with open(ACTIVE_PHASE_FILE) as f:
                phase_info = json.load(f)
            if phase_info.get("enabled", False):
                sys.path.insert(0, str(SCRIPT_DIR))
                from phase_auto_responder import main as phase_main
                phase_main(hook_info)
                return
        except Exception as e:
            print(json.dumps({
                "decision": "approve",
                "reason": f"[HOOK-ROUTER] Phase responder error: {e}"
            }))
            return

    # No active phase — allow stop (phase-specific responders handle continuation)
    print(json.dumps({
        "decision": "approve",
        "reason": "[HOOK-ROUTER] No active phase — allowing stop"
    }))


if __name__ == "__main__":
    main()
