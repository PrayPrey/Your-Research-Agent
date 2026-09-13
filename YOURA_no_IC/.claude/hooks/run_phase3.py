#!/usr/bin/env python3
"""
Phase 3 Launcher — Runs /phase3-implementation-planning Unattended

Launches Claude CLI with the /phase3-implementation-planning command for a
specific hypothesis. Configures the phase-specific auto-responder hook for
fully unattended execution.

Requires --research-folder and --hypothesis.

Phase 3 is a 10-step workflow (Step 01 ~ Step 10):
  Step 01: Initialize (Phase 2C completion check)
  Step 02: PRD Generation
  Step 03: Architecture Agent (Task tool sub-agent)
  Step 04: Budget Allocation
  Step 05: Parallel Agents (Logic + Config, Task tool sub-agents)
  Step 06: Complexity Assessment
  Step 07: Document Verification
  Step 08: Archon Project Update
  Step 09: Task Generation (03_tasks.yaml)
  Step 10: Validation + state update

Usage:
  python run_phase3.py --research-folder docs/youra_research/20260304_scsl --hypothesis h-e1
  python run_phase3.py --research-folder <path> --hypothesis h-e1 --timeout 5400

Author: Anonymous
"""

import argparse
import atexit
import json
import os
import re
import select
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from phase_output_verifier import (
    clear_must_stop, check_must_stop,
    verify_and_write_json, build_retry_prompt, MAX_RETRIES,
    build_claude_cmd, clear_phase_complete_lock,
)
from timeout_policy import log_timeout_marker, post_timeout_exit_code, core_artifacts_exist

# ============================================================
# Path Configuration
# ============================================================
SCRIPT_DIR = Path(__file__).parent
CACHE_DIR = SCRIPT_DIR / ".cache"
ACTIVE_PHASE_FILE = CACHE_DIR / "active_phase.json"
PHASE_CONFIG_FILE = SCRIPT_DIR / "phase3_auto_config.yaml"
AUTO_RESPONDER_CONFIG = SCRIPT_DIR / "auto_responder_config.yaml"
PROJECT_DIR = SCRIPT_DIR.parent.parent
CLAUDE_CLI = Path.home() / ".local" / "bin" / "claude"

LOG_FILE = CACHE_DIR / "run_phase3.log"


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
# Input Validation
# ============================================================
def validate_inputs(research_folder: str, hypothesis: str) -> dict:
    """Validate research folder and Phase 2C prerequisites."""
    folder = Path(research_folder)
    result = {
        "valid": False,
        "files": [],
        "has_verification_state": False,
        "has_experiment_brief": False,
    }

    if not folder.exists() or not folder.is_dir():
        log(f"ERROR: Research folder does not exist: {research_folder}")
        return result

    result["valid"] = True

    vs = folder / "verification_state.yaml"
    if vs.exists():
        result["has_verification_state"] = True
        result["files"].append(f"  - verification_state.yaml ({vs.stat().st_size} bytes)")

    # Check Phase 2C output
    h_folder = folder / hypothesis
    brief = h_folder / "02c_experiment_brief.md"
    if brief.exists():
        result["has_experiment_brief"] = True
        result["files"].append(f"  - {hypothesis}/02c_experiment_brief.md ({brief.stat().st_size} bytes)")

    # List other hypothesis files
    if h_folder.exists():
        for fname in h_folder.iterdir():
            if fname.is_file() and fname.name != "02c_experiment_brief.md":
                result["files"].append(f"  - {hypothesis}/{fname.name} ({fname.stat().st_size} bytes)")

    return result


# ============================================================
# Config Management
# ============================================================
def set_auto_responder_enabled(enabled: bool):
    """Set enabled flag in auto_responder_config.yaml."""
    if not AUTO_RESPONDER_CONFIG.exists():
        log("WARNING: auto_responder_config.yaml not found, skipping")
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


def create_active_phase(research_folder: str = None, hypothesis: str = None):
    """Create .cache/active_phase.json for hook routing."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    phase_info = {
        "phase": "phase3",
        "enabled": True,
        "config_file": str(PHASE_CONFIG_FILE),
        "pid": os.getpid(),
        "started_at": datetime.now().isoformat(),
        "research_folder": research_folder or "",
        "hypothesis": hypothesis or "",
    }

    with open(ACTIVE_PHASE_FILE, "w", encoding="utf-8") as f:
        json.dump(phase_info, f, indent=2)

    log(f"Created active_phase.json: phase=phase3, pid={os.getpid()}, research_folder={research_folder or 'NONE'}")


def cleanup():
    """Cleanup on exit."""
    try:
        if ACTIVE_PHASE_FILE.exists():
            ACTIVE_PHASE_FILE.unlink()
            log("Removed active_phase.json")
    except Exception as e:
        log(f"WARNING: Failed to remove active_phase.json: {e}")

    set_auto_responder_enabled(False)
    log("Cleanup complete")


# ============================================================
# Prompt Generation
# ============================================================
def build_phase3_prompt(research_folder: str, hypothesis: str, validation: dict) -> str:
    """Build the initial prompt for Phase 3 unattended execution."""
    files_str = "\n".join(validation["files"]) if validation["files"] else "  (no files found)"

    prompt = f"""/phase3-implementation-planning

#batch-mode

Proceed in Unattended mode. Research folder is located at:

  {research_folder}

Target hypothesis: {hypothesis}

Available files:
{files_str}

Execute all Phase 3 steps automatically for hypothesis {hypothesis}.
Do NOT ask for user confirmation — proceed through all steps (Step 01 through Step 10) without stopping.

Key instructions:
- Verify Phase 2C completion for {hypothesis}
- Generate PRD (03_prd.md)
- Launch architecture-agent, logic-agent, and configuration-agent
- Allocate implementation budget
- Verify all 4 documents (03_prd.md, 03_architecture.md, 03_logic.md, 03_config.md)
- Generate 03_tasks.yaml with implementation tasks
- Update verification_state.yaml with implementation_planning.status = "COMPLETED"
- When presented with any menu, automatically select [C] Continue

Experiment scale guidance:
- Do NOT design experiments with trivially small sample sizes (e.g., 10-50 samples)
- Use statistically meaningful sample counts: full standard test sets or at minimum 500+ evaluation samples
- Prefer standard dataset splits (full train/val/test) over arbitrary small subsets"""

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
        description="Phase 3 Launcher — Run /phase3-implementation-planning unattended",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --research-folder docs/youra_research/20260304_scsl --hypothesis h-e1
  %(prog)s --research-folder /absolute/path --hypothesis h-e1 --timeout 5400
        """,
    )

    parser.add_argument("--research-folder", type=str, required=True,
                        help="Path to research folder containing verification_state.yaml")
    parser.add_argument("--hypothesis", type=str, required=True,
                        help="Hypothesis ID to process (e.g., h-e1)")
    parser.add_argument("--timeout", type=int, default=5400,
                        help="Max runtime in seconds (default: 5400 = 90 min)")

    return parser.parse_args()


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
        phase_name="phase3",
        log_fn=log,
        process_setter=_set_proc,
        echo_to_stdout=True,
        monitor_complete_lock=False,
    )


def _check_passed(phase: str, h_id: str) -> bool:
    import json as _json
    p = CACHE_DIR / f"{phase}_{h_id}_output_verify.json"
    if not p.exists():
        return False
    try:
        return _json.load(open(p)).get("passed", False)
    except Exception:
        return False


def main():
    global _claude_process

    args = parse_args()

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    clear_must_stop()  # Clear any stale MUST_STOP flag from previous run
    clear_phase_complete_lock("phase3")  # Clear any stale PHASE_COMPLETE lock from previous run

    research_folder = str(Path(args.research_folder).resolve())

    validation = validate_inputs(research_folder, args.hypothesis)

    log("=" * 60)
    log("Phase 3 Launcher starting")
    log(f"  Research folder: {research_folder}")
    log(f"  Hypothesis: {args.hypothesis}")
    log(f"  Folder valid: {validation['valid']}")
    log(f"  Has experiment brief: {validation['has_experiment_brief']}")
    log(f"  Timeout: {args.timeout}s")
    log("=" * 60)

    if not validation["valid"]:
        log("ERROR: Research folder does not exist. Aborting.")
        sys.exit(1)

    if not validation["has_verification_state"]:
        log("ERROR: verification_state.yaml not found. Aborting.")
        sys.exit(1)

    if not validation["has_experiment_brief"]:
        log("WARNING: 02c_experiment_brief.md not found — Phase 3 may fail.")

    atexit.register(cleanup)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    set_auto_responder_enabled(True)
    create_active_phase(research_folder=research_folder, hypothesis=args.hypothesis)

    prompt = build_phase3_prompt(research_folder, args.hypothesis, validation)

    log(f"Launching Claude CLI with prompt ({len(prompt)} chars)")
    output_log = CACHE_DIR / f"phase3_{args.hypothesis}_output.log"
    # Truncate fresh — _run_claude opens in append mode for retries.
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
            phase_name="phase3",
            log_fn=log,
            process_setter=_set_proc,
            echo_to_stdout=True,
            monitor_complete_lock=False,
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
        log_timeout_marker(log, "phase3", elapsed, attempt="initial", hypothesis_id=args.hypothesis)

    if main_timed_out:
        cleanup()
        rc = post_timeout_exit_code(research_folder, "phase3", log, hypothesis_id=args.hypothesis)
        sys.exit(rc)

    # Check for MUST_STOP signal from hook (fatal error — abort immediately)
    must_stop_reason = check_must_stop()
    if must_stop_reason:
        log(f"MUST_STOP detected — aborting phase3: {must_stop_reason}")
        cleanup()
        sys.exit(1)

    # Verify outputs; retry with corrective prompt if needed
    verify_and_write_json("phase3", research_folder, exit_code, hypothesis_id=args.hypothesis)
    clear_phase_complete_lock("phase3")  # Clear lock so retry session is not immediately approved
    for _attempt in range(MAX_RETRIES):
        if exit_code != 0 or _check_passed("phase3", args.hypothesis):
            break
        log(f"Phase 3 verification FAILED — retry {_attempt + 1}/{MAX_RETRIES}")
        _retry_prompt = build_retry_prompt("phase3", research_folder, hypothesis_id=args.hypothesis)
        exit_code = _run_claude(_retry_prompt, args.timeout,
                                CACHE_DIR / f"phase3_{args.hypothesis}_output.log")
        if exit_code == 124:
            cleanup()
            rc = post_timeout_exit_code(research_folder, "phase3", log, hypothesis_id=args.hypothesis)
            sys.exit(rc)
        must_stop_reason = check_must_stop()
        if must_stop_reason:
            log(f"MUST_STOP during retry — aborting phase3: {must_stop_reason}")
            exit_code = 1
            break
        verify_and_write_json("phase3", research_folder, exit_code, hypothesis_id=args.hypothesis)

    cleanup()

    print(research_folder)

    log("Phase 3 Launcher complete")
    log("=" * 60)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
