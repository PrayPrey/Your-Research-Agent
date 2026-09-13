#!/usr/bin/env python3
"""
Phase 1 Launcher — Runs /phase1-targeted Unattended

Launches Claude CLI with the /phase1-targeted command and configures
the phase-specific auto-responder hook for fully unattended execution.
Uses --research-folder if provided, otherwise auto-detects Phase 0 output folder.

Usage:
  python run_phase1.py --research-folder docs/youra_research/20260304_scsl
  python run_phase1.py                    # auto-detect most recent folder
  python run_phase1.py --timeout 3600

Author: Anonymous
"""

import argparse
import atexit
import glob
import json
import os
import re
import select
import signal
import subprocess
import sys
import time
from datetime import datetime
from phase_output_verifier import verify_and_write_json, build_retry_prompt, MAX_RETRIES, clear_must_stop, check_must_stop, build_claude_cmd, clear_phase_complete_lock
from timeout_policy import log_timeout_marker, post_timeout_exit_code, core_artifacts_exist
from pathlib import Path

# ============================================================
# Path Configuration
# ============================================================
SCRIPT_DIR = Path(__file__).parent
CACHE_DIR = SCRIPT_DIR / ".cache"
ACTIVE_PHASE_FILE = CACHE_DIR / "active_phase.json"
PHASE_CONFIG_FILE = SCRIPT_DIR / "phase1_auto_config.yaml"
AUTO_RESPONDER_CONFIG = SCRIPT_DIR / "auto_responder_config.yaml"
PROJECT_DIR = SCRIPT_DIR.parent.parent  # /home/anonymous/YouRA_result_new_2/scsl
CLAUDE_CLI = Path.home() / ".local" / "bin" / "claude"
RESEARCH_BASE = PROJECT_DIR / "docs" / "youra_research"

LOG_FILE = CACHE_DIR / "run_phase1.log"


def log(message: str):
    """Log to file and stderr."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}"
    print(entry, file=sys.stderr)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except Exception:
        pass


# ============================================================
# Research Folder Detection
# ============================================================
def find_research_folder() -> str:
    """
    Find the research folder with Phase 0 output.

    Checks two patterns:
    1. docs/youra_research/<timestamp>_*/ subfolder containing 00_brainstorm_session.md
    2. docs/youra_research/ itself if 00_brainstorm_session.md exists directly there

    Returns the folder path, or None if not found.
    """
    if not RESEARCH_BASE.exists():
        return None

    # Case 1: Check if brainstorm file exists directly in youra_research/
    direct_brainstorm = RESEARCH_BASE / "00_brainstorm_session.md"
    if direct_brainstorm.exists():
        return str(RESEARCH_BASE)

    # Case 2: Look for timestamped subfolders
    folders = [f.rstrip("/") for f in glob.glob(str(RESEARCH_BASE / "*/"))
               if os.path.isdir(f.rstrip("/"))]
    if not folders:
        return None

    # Filter to folders containing Phase 0 output
    folders_with_phase0 = []
    for folder in folders:
        brainstorm_file = os.path.join(folder, "00_brainstorm_session.md")
        if os.path.exists(brainstorm_file):
            folders_with_phase0.append(folder)

    if folders_with_phase0:
        return max(folders_with_phase0, key=os.path.getmtime)

    # Fallback: return most recent folder
    return max(folders, key=os.path.getmtime)


# ============================================================
# Config Management
# ============================================================
def set_auto_responder_enabled(enabled: bool):
    """Set enabled flag in auto_responder_config.yaml."""
    if not AUTO_RESPONDER_CONFIG.exists():
        log(f"WARNING: auto_responder_config.yaml not found, skipping")
        return

    try:
        with open(AUTO_RESPONDER_CONFIG, "r", encoding="utf-8") as f:
            content = f.read()

        if enabled:
            new_content = re.sub(
                r'^(\s*)enabled\s*:\s*(false|False|FALSE|no|No|NO|off|Off|OFF)\s*$',
                r'\1enabled: true',
                content, count=1, flags=re.MULTILINE
            )
        else:
            new_content = re.sub(
                r'^(\s*)enabled\s*:\s*(true|True|TRUE|yes|Yes|YES|on|On|ON)\s*$',
                r'\1enabled: false',
                content, count=1, flags=re.MULTILINE
            )

        if new_content != content:
            with open(AUTO_RESPONDER_CONFIG, "w", encoding="utf-8") as f:
                f.write(new_content)
            log(f"auto_responder_config.yaml enabled={enabled}")
    except Exception as e:
        log(f"WARNING: Failed to update auto_responder_config: {e}")


def create_active_phase(research_folder: str = None):
    """Create .cache/active_phase.json for hook routing."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    phase_info = {
        "phase": "phase1",
        "enabled": True,
        "config_file": str(PHASE_CONFIG_FILE),
        "pid": os.getpid(),
        "started_at": datetime.now().isoformat(),
        "research_folder": research_folder or "",
    }

    with open(ACTIVE_PHASE_FILE, "w", encoding="utf-8") as f:
        json.dump(phase_info, f, indent=2)

    log(f"Created active_phase.json: phase=phase1, pid={os.getpid()}, research_folder={research_folder or 'NONE'}")


def cleanup():
    """Cleanup on exit: remove active_phase.json, restore auto_responder_config."""
    try:
        if ACTIVE_PHASE_FILE.exists():
            ACTIVE_PHASE_FILE.unlink()
            log("Removed active_phase.json")
    except Exception as e:
        log(f"WARNING: Failed to remove active_phase.json: {e}")

    # Restore auto_responder_config to disabled (safe default)
    set_auto_responder_enabled(False)
    log("Cleanup complete")


# ============================================================
# Prompt Generation
# ============================================================
def build_phase1_prompt(research_folder: str) -> str:
    """
    Build the initial prompt for Phase 1 unattended execution.

    Includes the research folder path so Claude knows where Phase 0 outputs are.
    """
    if research_folder:
        # List key files in the research folder for context
        files_info = []
        for fname in ["00_brainstorm_session.md"]:
            fpath = os.path.join(research_folder, fname)
            if os.path.exists(fpath):
                size = os.path.getsize(fpath)
                files_info.append(f"  - {fname} ({size} bytes)")

        files_str = "\n".join(files_info) if files_info else "  (no Phase 0 files found)"

        prompt = f"""/phase1-targeted

Proceed in Unattended mode. Phase 0 output files are located at:

  {research_folder}

Available files:
{files_str}

Read the Phase 0 output files at the path above and execute all Phase 1 steps automatically.
Do NOT ask for user confirmation — auto-select [C] Continue at every menu.
At Step 9, auto-select [E] Exit to complete."""
    else:
        prompt = """/phase1-targeted

Proceed in Unattended mode. Execute all Phase 1 steps automatically.
Do NOT ask for user confirmation — auto-select [C] Continue at every menu.
At Step 9, auto-select [E] Exit to complete."""

    return prompt


# ============================================================
# Signal Handlers
# ============================================================
_claude_process = None


def signal_handler(signum, frame):
    """Handle SIGINT/SIGTERM gracefully."""
    sig_name = signal.Signals(signum).name
    log(f"Received {sig_name} — shutting down")

    if _claude_process and _claude_process.poll() is None:
        log("Terminating Claude CLI process...")
        _claude_process.terminate()
        try:
            _claude_process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            log("Force killing Claude CLI process...")
            _claude_process.kill()

    cleanup()
    sys.exit(128 + signum)


# ============================================================
# Main Execution
# ============================================================
def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Phase 1 Launcher — Run /phase1-targeted unattended",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --timeout 3600
        """,
    )

    parser.add_argument("--research-folder", type=str, default=None,
                        help="Path to research folder containing Phase 0 output (default: auto-detect)")
    parser.add_argument("--retry-prompt", type=str, default=None,
                        help="Override prompt for retry run (injected by run_early_pipeline.py)")
    parser.add_argument("--timeout", type=int, default=3600,
                        help="Timeout in seconds for Claude CLI subprocess")

    return parser.parse_args()



def _check_passed(phase: str) -> bool:
    """Read last verify JSON and return passed flag."""
    import json as _json
    p = CACHE_DIR / f"{phase}_output_verify.json"
    if not p.exists():
        return False
    try:
        return _json.load(open(p)).get("passed", False)
    except Exception:
        return False


def _set_proc(p):
    global _claude_process
    _claude_process = p


def _run_claude(prompt: str, timeout: int, output_log) -> int:
    """Launch Claude CLI with retry on transient API overload (5xx/Overloaded).

    Delegates to claude_runner.run_claude_with_retry.
    """
    from claude_runner import run_claude_with_retry
    return run_claude_with_retry(
        claude_cli=CLAUDE_CLI,
        project_dir=PROJECT_DIR,
        cache_dir=CACHE_DIR,
        prompt=prompt,
        timeout=timeout,
        output_log=output_log,
        phase_name="phase1",
        log_fn=log,
        process_setter=_set_proc,
        echo_to_stdout=True,
        monitor_complete_lock=False,
    )


def main():
    global _claude_process

    args = parse_args()

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    clear_must_stop()  # Clear any stale MUST_STOP flag from previous run
    clear_phase_complete_lock("phase1")  # Clear any stale PHASE_COMPLETE lock from previous run

    # Resolve research folder: explicit > auto-detect
    if args.research_folder:
        research_folder = str(Path(args.research_folder).resolve())
        if not Path(research_folder).is_dir():
            log(f"ERROR: Specified research folder does not exist: {research_folder}")
            sys.exit(1)
        log(f"Using explicitly specified research folder")
    else:
        research_folder = find_research_folder()
        if research_folder:
            log(f"Auto-detected research folder")

    log("=" * 60)
    log("Phase 1 Launcher starting")
    log(f"  Research folder: {research_folder or 'NOT FOUND'}")
    log(f"  Timeout: {args.timeout}s")

    if not research_folder:
        log("WARNING: No research folder with Phase 0 output found.")
        log("  Phase 1 workflow will attempt to find it on its own.")

    # Register cleanup
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Step 1: Enable auto_responder_config
    set_auto_responder_enabled(True)

    # Step 2: Create active_phase.json (include research_folder for snapshot-based diff)
    create_active_phase(research_folder=research_folder)

    # Step 3: Build prompt and launch Claude CLI
    prompt = args.retry_prompt if args.retry_prompt else build_phase1_prompt(research_folder)

    log(f"Launching Claude CLI with prompt ({len(prompt)} chars)")
    log(f"CWD: {PROJECT_DIR}")

    output_log = CACHE_DIR / "phase1_claude_output.log"
    output_log.write_text("", encoding="utf-8")

    start_time = time.time()
    try:
        from claude_runner import run_claude_with_retry
        exit_code = run_claude_with_retry(
            claude_cli=CLAUDE_CLI,
            project_dir=PROJECT_DIR,
            cache_dir=CACHE_DIR,
            prompt=prompt,
            timeout=args.timeout,
            output_log=output_log,
            phase_name="phase1",
            log_fn=log,
            process_setter=_set_proc,
            echo_to_stdout=False,
            monitor_complete_lock=False,
            extra_cli_args=["--output-format", "stream-json", "--verbose"],
            stream_json=True,
            separate_stderr=True,
        )
    except FileNotFoundError:
        log(f"ERROR: Claude CLI not found at {CLAUDE_CLI}")
        cleanup()
        sys.exit(1)
    except Exception as e:
        log(f"ERROR: {e}")
        cleanup()
        sys.exit(1)

    elapsed = time.time() - start_time
    log(f"Claude CLI exited with code {exit_code} after {elapsed:.0f}s")
    main_timed_out = (exit_code == 124)
    if main_timed_out:
        log_timeout_marker(log, "phase1", elapsed, attempt="initial")

    if main_timed_out:
        cleanup()
        rc = post_timeout_exit_code(research_folder, "phase1", log)
        sys.exit(rc)

    # Check for MUST_STOP signal from hook (fatal error — skip verify/retry)
    must_stop_reason = check_must_stop()
    if must_stop_reason:
        log(f"MUST_STOP detected — aborting phase1: {must_stop_reason}")
        cleanup()
        sys.exit(1)

    # Verify outputs; retry with corrective prompt if needed
    verify_and_write_json("phase1", research_folder, exit_code)
    clear_phase_complete_lock("phase1")  # Clear lock so retry session is not immediately approved
    for _attempt in range(MAX_RETRIES):
        if exit_code != 0 or _check_passed("phase1"):
            break
        log(f"Phase 1 verification FAILED — retry {_attempt + 1}/{MAX_RETRIES}")
        _retry_prompt = build_retry_prompt("phase1", research_folder)
        exit_code = _run_claude(_retry_prompt, args.timeout,
                               CACHE_DIR / "phase1_claude_output.log")
        if exit_code == 124:
            cleanup()
            rc = post_timeout_exit_code(research_folder, "phase1", log)
            sys.exit(rc)
        verify_and_write_json("phase1", research_folder, exit_code)

    # Step 4: Cleanup
    cleanup()

    log("Phase 1 Launcher complete")
    log("=" * 60)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
