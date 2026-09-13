#!/usr/bin/env python3
"""
Phase 4.5 Launcher — Runs /phase45-hypothesis-synthesis Unattended

Launches Claude CLI with the /phase45-hypothesis-synthesis command.
Configures the phase-specific auto-responder hook for fully unattended execution.

Requires --research-folder pointing to the folder containing verification_state.yaml
and h-*/04_validation.md files from completed hypothesis experiments.

Phase 4.5 is an 8-step workflow (Step 01 ~ Step 08):
  Step 01: Initialize (state load, precondition check, original hypothesis read)
  Step 02: Prediction-Result Alignment (P1/P2/P3 → experiment results mapping)
  Step 03: Hypothesis Refinement (overclaim removal, refined core statement)
  Step 04: Theoretical Interpretation (literature connection, unexpected findings)
  Step 05: Limitations & Scope Boundaries
  Step 06: Future Work (results-grounded directions)
  Step 07: Generate 045_validated_hypothesis.md
  Step 08: Finalize (state update, completion summary)

Usage:
  python run_phase45.py --research-folder docs/youra_research/20260304_scsl
  python run_phase45.py --research-folder <path> --timeout 5400

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
PHASE_CONFIG_FILE = SCRIPT_DIR / "phase45_auto_config.yaml"
AUTO_RESPONDER_CONFIG = SCRIPT_DIR / "auto_responder_config.yaml"
PROJECT_DIR = SCRIPT_DIR.parent.parent
CLAUDE_CLI = Path.home() / ".local" / "bin" / "claude"

LOG_FILE = CACHE_DIR / "run_phase45.log"


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
def validate_inputs(research_folder: str) -> dict:
    """Validate research folder and Phase 4 prerequisites."""
    folder = Path(research_folder)
    result = {
        "valid": False,
        "files": [],
        "has_verification_state": False,
        "has_refinement": False,
        "hypothesis_count": 0,
        "sub_hypotheses_complete": False,
    }

    if not folder.exists() or not folder.is_dir():
        log(f"ERROR: Research folder does not exist: {research_folder}")
        return result

    result["valid"] = True

    # Check verification_state.yaml
    vs = folder / "verification_state.yaml"
    if vs.exists():
        result["has_verification_state"] = True
        result["files"].append(f"  - verification_state.yaml ({vs.stat().st_size} bytes)")
        # Check sub_hypotheses_complete
        try:
            content = vs.read_text(encoding="utf-8")
            if "sub_hypotheses_complete: true" in content or "sub_hypotheses_complete: True" in content:
                result["sub_hypotheses_complete"] = True
        except Exception:
            pass

    # Check 03_refinement.yaml (original hypothesis)
    ref = folder / "03_refinement.yaml"
    if ref.exists():
        result["has_refinement"] = True
        result["files"].append(f"  - 03_refinement.yaml ({ref.stat().st_size} bytes)")

    # Check h-* folders with Phase 4 outputs + Phase 3/2C inputs
    for h_folder in sorted(folder.glob("h-*")):
        if h_folder.is_dir():
            val = h_folder / "04_validation.md"
            chk = h_folder / "04_checkpoint.yaml"
            tasks = h_folder / "03_tasks.yaml"
            brief = h_folder / "02c_experiment_brief.md"
            if val.exists() or chk.exists():
                result["hypothesis_count"] += 1
                if val.exists():
                    result["files"].append(f"  - {h_folder.name}/04_validation.md ({val.stat().st_size} bytes)")
                if chk.exists():
                    result["files"].append(f"  - {h_folder.name}/04_checkpoint.yaml ({chk.stat().st_size} bytes)")
                if tasks.exists():
                    result["files"].append(f"  - {h_folder.name}/03_tasks.yaml ({tasks.stat().st_size} bytes)")
                if brief.exists():
                    result["files"].append(f"  - {h_folder.name}/02c_experiment_brief.md ({brief.stat().st_size} bytes)")

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


def create_active_phase(research_folder: str = None):
    """Create .cache/active_phase.json for hook routing."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    phase_info = {
        "phase": "phase45",
        "enabled": True,
        "config_file": str(PHASE_CONFIG_FILE),
        "pid": os.getpid(),
        "started_at": datetime.now().isoformat(),
        "research_folder": research_folder or "",
    }

    with open(ACTIVE_PHASE_FILE, "w", encoding="utf-8") as f:
        json.dump(phase_info, f, indent=2)

    log(f"Created active_phase.json: phase=phase45, pid={os.getpid()}, research_folder={research_folder or 'NONE'}")


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
def build_phase45_prompt(research_folder: str, validation: dict) -> str:
    """Build the initial prompt for Phase 4.5 unattended execution."""
    files_str = "\n".join(validation["files"]) if validation["files"] else "  (no files found)"

    prompt = f"""/phase45-hypothesis-synthesis

#batch-mode

Proceed in Unattended mode. Research folder is located at:

  {research_folder}

Available files:
{files_str}

Execute all Phase 4.5 steps automatically (Step 01 through Step 08).
Do NOT ask for user confirmation — proceed through all steps without stopping.

Key instructions:
- Read verification_state.yaml and verify sub_hypotheses_complete = true
- Read 03_refinement.yaml for original hypothesis (predictions, mechanism, assumptions)
- Read ALL h-*/04_validation.md and h-*/04_checkpoint.yaml files
- Read ALL h-*/03_tasks.yaml files (planned metrics, success criteria for planned-vs-actual comparison)
- Read ALL h-*/02c_experiment_brief.md files (experiment design, variables, controls for result interpretation)
- Step 02: Map predictions P1/P2/P3 to experiment results (SUPPORTED/PARTIALLY_SUPPORTED/REFUTED/INCONCLUSIVE)
- Step 02: Build planned-vs-actual comparison (03_tasks.yaml vs 04_validation.md)
- Step 02: Validate experiment design integrity (02c_experiment_brief.md vs actual execution)
- Step 03: Refine hypothesis — remove overclaims, generate refined core statement
- Step 04: Connect to literature, analyze unexpected findings with competing explanations
- Step 05: Define principled limitations with root cause analysis
- Step 06: Derive results-grounded future work directions
- Step 07: Generate 045_validated_hypothesis.md with ALL 8 sections filled
- Step 08: Update verification_state.yaml with synthesis_completed = true
- When presented with any menu, automatically select [C] Continue"""

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
        description="Phase 4.5 Launcher — Run /phase45-hypothesis-synthesis unattended",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --research-folder docs/youra_research/20260304_scsl
  %(prog)s --research-folder /absolute/path --timeout 5400
        """,
    )

    parser.add_argument("--research-folder", type=str, required=True,
                        help="Path to research folder containing verification_state.yaml")
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
        phase_name="phase45",
        log_fn=log,
        process_setter=_set_proc,
        echo_to_stdout=True,
        monitor_complete_lock=False,
    )


def _check_passed(phase: str) -> bool:
    import json as _json
    p = CACHE_DIR / f"{phase}_output_verify.json"
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
    clear_must_stop()
    clear_phase_complete_lock("phase45")  # Clear any stale PHASE_COMPLETE lock from previous run

    research_folder = str(Path(args.research_folder).resolve())

    validation = validate_inputs(research_folder)

    log("=" * 60)
    log("Phase 4.5 Launcher starting")
    log(f"  Research folder: {research_folder}")
    log(f"  Folder valid: {validation['valid']}")
    log(f"  Has verification_state: {validation['has_verification_state']}")
    log(f"  Has 03_refinement.yaml: {validation['has_refinement']}")
    log(f"  Hypothesis folders: {validation['hypothesis_count']}")
    log(f"  Sub-hypotheses complete: {validation['sub_hypotheses_complete']}")
    log(f"  Timeout: {args.timeout}s")
    log("=" * 60)

    if not validation["valid"]:
        log("ERROR: Research folder does not exist. Aborting.")
        sys.exit(1)

    if not validation["has_verification_state"]:
        log("ERROR: verification_state.yaml not found. Aborting.")
        sys.exit(1)

    if not validation["sub_hypotheses_complete"]:
        log("WARNING: sub_hypotheses_complete is not true — Phase 4.5 may fail.")

    if validation["hypothesis_count"] == 0:
        log("ERROR: No h-*/04_validation.md files found. Aborting.")
        sys.exit(1)

    atexit.register(cleanup)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    set_auto_responder_enabled(True)
    create_active_phase(research_folder=research_folder)

    prompt = build_phase45_prompt(research_folder, validation)

    log(f"Launching Claude CLI with prompt ({len(prompt)} chars)")
    output_log = CACHE_DIR / "phase45_output.log"
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
            phase_name="phase45",
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
        log_timeout_marker(log, "phase45", elapsed, attempt="initial")

    if main_timed_out:
        cleanup()
        rc = post_timeout_exit_code(research_folder, "phase45", log)
        sys.exit(rc)

    # Check for MUST_STOP signal from hook
    must_stop_reason = check_must_stop()
    if must_stop_reason:
        log(f"MUST_STOP detected — aborting phase45: {must_stop_reason}")
        cleanup()
        sys.exit(1)

    # Verify outputs; retry with corrective prompt if needed
    verify_and_write_json("phase45", research_folder, exit_code)
    clear_phase_complete_lock("phase45")  # Clear lock so retry session is not immediately approved
    for _attempt in range(MAX_RETRIES):
        if exit_code != 0 or _check_passed("phase45"):
            break
        log(f"Phase 4.5 verification FAILED — retry {_attempt + 1}/{MAX_RETRIES}")
        _retry_prompt = build_retry_prompt("phase45", research_folder)
        exit_code = _run_claude(_retry_prompt, args.timeout,
                                CACHE_DIR / "phase45_output.log")
        if exit_code == 124:
            cleanup()
            rc = post_timeout_exit_code(research_folder, "phase45", log)
            sys.exit(rc)
        must_stop_reason = check_must_stop()
        if must_stop_reason:
            log(f"MUST_STOP during retry — aborting phase45: {must_stop_reason}")
            exit_code = 1
            break
        verify_and_write_json("phase45", research_folder, exit_code)

    cleanup()

    print(research_folder)

    log("Phase 4.5 Launcher complete")
    log("=" * 60)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
