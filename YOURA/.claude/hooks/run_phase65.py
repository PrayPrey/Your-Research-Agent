#!/usr/bin/env python3
"""
Phase 6.5 Launcher — Runs /phase65-adversarial-review Unattended

Launches Claude CLI with the /phase65-adversarial-review command and configures
the phase-specific auto-responder hook for fully unattended execution.
Requires --research-folder pointing to the folder containing Phase 6 output.

Phase 6.5 is a 7-step adversarial review workflow (Step 01 ~ Step 07):
  Step 01: Initialize (validate inputs, extract ground truth, create checkpoint)
  Step 02: Adversary Round 1 (3-persona review: Accuracy Checker, Bored Reviewer, Skeptical Expert)
  Step 03: Revision Round 1 (fix FATAL/MAJOR, collect MINOR to human_review_notes)
  Step 04: Convergence Check (FATAL=0, MAJOR=0, persuasiveness_passed, round>=2)
  Step 05: Adversary Round 2 (numerical verification with Serena MCP)
  Step 06: Revision Round 2 (fix numerical issues)
  Step 07: Finalize (06_paper_final.md, review summary, changelog, state update)

Maximum 3 rounds. Steps 5-6 are conditional (only if R1 didn't converge).

Usage:
  python run_phase65.py --research-folder docs/youra_research/20260304_scsl
  python run_phase65.py --research-folder <path> --timeout 7200

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
PHASE_CONFIG_FILE = SCRIPT_DIR / "phase65_auto_config.yaml"
AUTO_RESPONDER_CONFIG = SCRIPT_DIR / "auto_responder_config.yaml"
PROJECT_DIR = SCRIPT_DIR.parent.parent
CLAUDE_CLI = Path.home() / ".local" / "bin" / "claude"

LOG_FILE = CACHE_DIR / "run_phase65.log"


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
    """Validate research folder and Phase 6 prerequisites."""
    folder = Path(research_folder)
    paper_dir = folder / "paper"
    result = {
        "valid": False,
        "files": [],
        "has_verification_state": False,
        "has_paper": False,
        "has_ground_truth": False,
        "has_narrative_blueprint": False,
        "has_references": False,
        "has_sections": False,
        "section_count": 0,
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

    # Check Phase 6 paper output
    paper = paper_dir / "06_paper.md"
    if paper.exists():
        result["has_paper"] = True
        result["files"].append(f"  - paper/06_paper.md ({paper.stat().st_size} bytes)")

    # Check ground truth (from Phase 6 Step 7)
    gt = paper_dir / "065_ground_truth.yaml"
    if gt.exists():
        result["has_ground_truth"] = True
        result["files"].append(f"  - paper/065_ground_truth.yaml ({gt.stat().st_size} bytes)")

    # Check narrative blueprint (for persuasiveness checks)
    nb = paper_dir / "06_narrative_blueprint.yaml"
    if nb.exists():
        result["has_narrative_blueprint"] = True
        result["files"].append(f"  - paper/06_narrative_blueprint.yaml ({nb.stat().st_size} bytes)")

    # Check references
    refs = paper_dir / "06_references.bib"
    if refs.exists():
        result["has_references"] = True
        result["files"].append(f"  - paper/06_references.bib ({refs.stat().st_size} bytes)")

    # Check sections folder
    sections_dir = paper_dir / "sections"
    if sections_dir.exists() and sections_dir.is_dir():
        sec_files = sorted(sections_dir.glob("*.md"))
        result["section_count"] = len(sec_files)
        if len(sec_files) >= 8:
            result["has_sections"] = True
        for sf in sec_files:
            result["files"].append(f"  - paper/sections/{sf.name} ({sf.stat().st_size} bytes)")

    # Check for existing review folder (for resume)
    review_dir = paper_dir / "review"
    if review_dir.exists():
        for rf in sorted(review_dir.iterdir()):
            if rf.is_file():
                result["files"].append(f"  - paper/review/{rf.name} ({rf.stat().st_size} bytes)")

    # Check h-* folders with Phase 4 validation (for cross-reference)
    for h_folder in sorted(folder.glob("h-*")):
        if h_folder.is_dir():
            val = h_folder / "04_validation.md"
            if val.exists():
                result["files"].append(f"  - {h_folder.name}/04_validation.md ({val.stat().st_size} bytes)")

    # Check 045_validated_hypothesis.md
    vh = folder / "045_validated_hypothesis.md"
    if vh.exists():
        result["files"].append(f"  - 045_validated_hypothesis.md ({vh.stat().st_size} bytes)")

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
        "phase": "phase65",
        "enabled": True,
        "config_file": str(PHASE_CONFIG_FILE),
        "pid": os.getpid(),
        "started_at": datetime.now().isoformat(),
        "research_folder": research_folder or "",
    }

    with open(ACTIVE_PHASE_FILE, "w", encoding="utf-8") as f:
        json.dump(phase_info, f, indent=2)

    log(f"Created active_phase.json: phase=phase65, pid={os.getpid()}, research_folder={research_folder or 'NONE'}")


def cleanup():
    """Cleanup on exit: remove active_phase.json, restore auto_responder_config."""
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
def build_phase65_prompt(research_folder: str, validation: dict) -> str:
    """Build the initial prompt for Phase 6.5 unattended execution."""
    files_str = "\n".join(validation["files"]) if validation["files"] else "  (no files found)"

    prompt = f"""/phase65-adversarial-review

#batch-mode

Proceed in Unattended mode. Research folder is located at:

  {research_folder}

Available files:
{files_str}

Execute all Phase 6.5 steps automatically (Step 01 through Step 07).
Do NOT ask for user confirmation — proceed through all steps without stopping.

Key instructions:
- Step 01: Initialize — validate inputs, extract ground truth from 065_ground_truth.yaml
  and Phase 4/5 result files (use Serena MCP for discovery), create checkpoint
- Step 02: Adversary R1 — run 3-persona review (Accuracy Checker, Bored Reviewer, Skeptical Expert)
  - Accuracy Checker: verify numbers against ground truth
  - Bored Reviewer: check engagement (abstract compelling? novelty clear in 2 min?)
  - Skeptical Expert: check novelty claims, baseline fairness, missing limitations
- Step 03: Revision R1 — fix ALL FATAL issues, fix MAJOR issues, collect MINOR in human_review_notes
  - Do NOT auto-fix MINOR issues (typos, grammar, style) — collect in 065_human_review_notes.md
- Step 04: Convergence Check — converge if FATAL=0, MAJOR=0, persuasiveness_passed, round>=2
  - If not converged and round < max_rounds → continue to Step 05
- Step 05: Adversary R2 — numerical verification with Serena MCP (MANDATORY)
  - Search for actual metrics in Phase 4/5 result files
- Step 06: Revision R2 — fix numerical discrepancies from R2
- Step 07: Finalize — generate 06_paper_final.md, 065_review_summary.md,
  065_changelog.md, update verification_state.yaml
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
        description="Phase 6.5 Launcher — Run /phase65-adversarial-review unattended",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --research-folder docs/youra_research/20260304_scsl
  %(prog)s --research-folder /absolute/path --timeout 7200
        """,
    )

    parser.add_argument("--research-folder", type=str, required=True,
                        help="Path to research folder containing paper/06_paper.md")
    parser.add_argument("--timeout", type=int, default=14400,
                        help="Max runtime in seconds (default: 7200 = 2 hours)")

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
        phase_name="phase65",
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
    clear_phase_complete_lock("phase65")  # Clear any stale PHASE_COMPLETE lock from previous run

    research_folder = str(Path(args.research_folder).resolve())

    validation = validate_inputs(research_folder)

    log("=" * 60)
    log("Phase 6.5 Launcher starting")
    log(f"  Research folder: {research_folder}")
    log(f"  Folder valid: {validation['valid']}")
    log(f"  Has verification_state: {validation['has_verification_state']}")
    log(f"  Has paper/06_paper.md: {validation['has_paper']}")
    log(f"  Has paper/065_ground_truth.yaml: {validation['has_ground_truth']}")
    log(f"  Has narrative blueprint: {validation['has_narrative_blueprint']}")
    log(f"  Has sections ({validation['section_count']}): {validation['has_sections']}")
    log(f"  Timeout: {args.timeout}s")
    log("=" * 60)

    if not validation["valid"]:
        log("ERROR: Research folder does not exist. Aborting.")
        sys.exit(1)

    if not validation["has_paper"]:
        log("ERROR: paper/06_paper.md not found — Phase 6 must complete first. Aborting.")
        sys.exit(1)

    if not validation["has_verification_state"]:
        log("ERROR: verification_state.yaml not found. Aborting.")
        sys.exit(1)

    if not validation["has_ground_truth"]:
        log("WARNING: paper/065_ground_truth.yaml not found — adversary accuracy checks may be limited.")

    if not validation["has_narrative_blueprint"]:
        log("WARNING: paper/06_narrative_blueprint.yaml not found — persuasiveness checks may be limited.")

    atexit.register(cleanup)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    set_auto_responder_enabled(True)
    create_active_phase(research_folder=research_folder)

    prompt = build_phase65_prompt(research_folder, validation)

    log(f"Launching Claude CLI with prompt ({len(prompt)} chars)")
    output_log = CACHE_DIR / "phase65_output.log"
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
            phase_name="phase65",
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
        log_timeout_marker(log, "phase65", elapsed, attempt="initial")

    if main_timed_out:
        cleanup()
        rc = post_timeout_exit_code(research_folder, "phase65", log)
        sys.exit(rc)

    # Check for MUST_STOP signal from hook
    must_stop_reason = check_must_stop()
    if must_stop_reason:
        log(f"MUST_STOP detected — aborting phase65: {must_stop_reason}")
        cleanup()
        sys.exit(1)

    # Verify outputs; retry with corrective prompt if needed
    verify_and_write_json("phase65", research_folder, exit_code)
    clear_phase_complete_lock("phase65")  # Clear lock so retry session is not immediately approved
    for _attempt in range(MAX_RETRIES):
        if exit_code != 0 or _check_passed("phase65"):
            break
        log(f"Phase 6.5 verification FAILED — retry {_attempt + 1}/{MAX_RETRIES}")
        _retry_prompt = build_retry_prompt("phase65", research_folder)
        exit_code = _run_claude(_retry_prompt, args.timeout,
                                CACHE_DIR / "phase65_output.log")
        if exit_code == 124:
            cleanup()
            rc = post_timeout_exit_code(research_folder, "phase65", log)
            sys.exit(rc)
        must_stop_reason = check_must_stop()
        if must_stop_reason:
            log(f"MUST_STOP during retry — aborting phase65: {must_stop_reason}")
            exit_code = 1
            break
        verify_and_write_json("phase65", research_folder, exit_code)

    cleanup()

    print(research_folder)

    log("Phase 6.5 Launcher complete")
    log("=" * 60)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
