#!/usr/bin/env python3
"""
YouRA Auto-Responder - Disable Hook Script

This script disables the auto-responder by setting enabled: false in the config.
Called when MUST_STOP conditions are detected and human intervention is required.

Usage:
    python disable_hook.py "Reason for disabling"

Author: Anonymous
"""

import sys
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "auto_responder_config.yaml"

# State/log files go to .cache folder for portability
STATE_DIR = SCRIPT_DIR / ".cache"
STATE_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = STATE_DIR / "auto_responder.log"


def log(message: str):
    """Write to log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [DISABLE_HOOK] {message}"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
        print(log_entry, file=sys.stderr)
    except Exception:
        pass


def disable_hook(reason: str) -> bool:
    """Disable the auto-responder by modifying the config file.

    Only modifies the MASTER SWITCH (first 'enabled:' at root level),
    not the nested 'enabled:' fields under openrouter, etc.
    """
    if not CONFIG_FILE.exists():
        log(f"ERROR: Config file not found: {CONFIG_FILE}")
        return False

    try:
        # Read current config
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Find and replace ONLY the first 'enabled: true' (master switch)
        # Master switch is at root level (no indentation)
        modified = False
        new_lines = []

        for line in lines:
            # Only match 'enabled: true' with NO leading whitespace (root level)
            if not modified and line.startswith("enabled: true"):
                new_line = line.replace("enabled: true", "enabled: false")
                new_lines.append(new_line)
                modified = True
                log(f"Changed master switch 'enabled: true' to 'enabled: false'")
            else:
                new_lines.append(line)

        if not modified:
            log("WARNING: Master switch 'enabled: true' not found (may already be disabled)")
            return True  # Not an error, just already disabled

        # Write modified config
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        # Log the reason
        log(f"Hook DISABLED. Reason: {reason}")

        # Create a flag file with details
        flag_file = SCRIPT_DIR / "HOOK_DISABLED.txt"
        with open(flag_file, "w", encoding="utf-8") as f:
            f.write(f"Hook disabled at: {datetime.now().isoformat()}\n")
            f.write(f"Reason: {reason}\n")
            f.write("\nTo re-enable:\n")
            f.write("1. Edit auto_responder_config.yaml\n")
            f.write("2. Set 'enabled: true'\n")
            f.write("3. Delete this HOOK_DISABLED.txt file\n")

        log(f"Created flag file: {flag_file}")
        return True

    except Exception as e:
        log(f"ERROR: Failed to disable hook: {e}")
        return False


def main():
    """Main entry point."""
    reason = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "No reason provided"

    log("=" * 40)
    log("Disable Hook Script - Triggered")

    success = disable_hook(reason)

    if success:
        log("Hook disabled successfully")
        log("=" * 40)
        sys.exit(0)
    else:
        log("Failed to disable hook")
        log("=" * 40)
        sys.exit(1)


if __name__ == "__main__":
    main()
