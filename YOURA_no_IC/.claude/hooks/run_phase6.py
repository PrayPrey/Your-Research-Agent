#!/usr/bin/env python3
"""
Phase 6 Launcher — Runs /phase6-paper-writing Unattended

Launches Claude CLI with the /phase6-paper-writing command and configures
the phase-specific auto-responder hook for fully unattended execution.
Requires --research-folder pointing to the folder containing Phase 4.5 output.

Phase 6 is a 7-step workflow (Step 01 ~ Step 07):
  Step 01: Initialize (folder setup, collect figures, verify prerequisites)
  Step 02: Narrative Design (design paper story structure → 06_narrative_blueprint.yaml)
  Step 03: Story Group A — Foundation (Introduction, Related Work, Methodology)
  Step 04: Story Group B — Evidence (Experiments, Results, Discussion)
  Step 05: Story Group C — Closure (Conclusion, Abstract — generated LAST)
  Step 06: References (citation compilation, Semantic Scholar verification → 06_references.bib)
  Step 07: Final Merge & Ground Truth (06_paper.md, 065_ground_truth.yaml)

Usage:
  python run_phase6.py --research-folder docs/youra_research/20260304_scsl
  python run_phase6.py --research-folder <path> --timeout 7200

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
PHASE_CONFIG_FILE = SCRIPT_DIR / "phase6_auto_config.yaml"
AUTO_RESPONDER_CONFIG = SCRIPT_DIR / "auto_responder_config.yaml"
PROJECT_DIR = SCRIPT_DIR.parent.parent
CLAUDE_CLI = Path.home() / ".local" / "bin" / "claude"

LOG_FILE = CACHE_DIR / "run_phase6.log"


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
    """Validate research folder and Phase 4.5 prerequisites."""
    folder = Path(research_folder)
    result = {
        "valid": False,
        "files": [],
        "has_verification_state": False,
        "has_validated_hypothesis": False,
        "has_refinement": False,
        "has_verification_plan": False,
        "synthesis_completed": False,
        "hypothesis_count": 0,
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
        try:
            content = vs.read_text(encoding="utf-8")
            if "synthesis_completed: true" in content or "synthesis_completed: True" in content:
                result["synthesis_completed"] = True
        except Exception:
            pass

    # Check 045_validated_hypothesis.md (Phase 4.5 PRIMARY output)
    vh = folder / "045_validated_hypothesis.md"
    if vh.exists():
        result["has_validated_hypothesis"] = True
        result["files"].append(f"  - 045_validated_hypothesis.md ({vh.stat().st_size} bytes)")

    # Check 03_refinement.yaml (original hypothesis)
    ref = folder / "03_refinement.yaml"
    if ref.exists():
        result["has_refinement"] = True
        result["files"].append(f"  - 03_refinement.yaml ({ref.stat().st_size} bytes)")

    # Check 02b_verification_plan.md
    vp = folder / "02b_verification_plan.md"
    if vp.exists():
        result["has_verification_plan"] = True
        result["files"].append(f"  - 02b_verification_plan.md ({vp.stat().st_size} bytes)")

    # Check h-* folders with experiment artifacts
    for h_folder in sorted(folder.glob("h-*")):
        if h_folder.is_dir():
            val = h_folder / "04_validation.md"
            brief = h_folder / "02c_experiment_brief.md"
            arch = h_folder / "03_architecture.md"
            prd = h_folder / "03_prd.md"
            if val.exists():
                result["hypothesis_count"] += 1
                result["files"].append(f"  - {h_folder.name}/04_validation.md ({val.stat().st_size} bytes)")
            if brief.exists():
                result["files"].append(f"  - {h_folder.name}/02c_experiment_brief.md ({brief.stat().st_size} bytes)")
            if arch.exists():
                result["files"].append(f"  - {h_folder.name}/03_architecture.md ({arch.stat().st_size} bytes)")
            if prd.exists():
                result["files"].append(f"  - {h_folder.name}/03_prd.md ({prd.stat().st_size} bytes)")

    # Check existing paper folder (for resume)
    paper_dir = folder / "paper"
    if paper_dir.exists():
        for pf in sorted(paper_dir.iterdir()):
            if pf.is_file():
                result["files"].append(f"  - paper/{pf.name} ({pf.stat().st_size} bytes)")

    # Check Phase 1 research (for Related Work)
    p1 = folder / "01_targeted_research.md"
    if p1.exists():
        result["files"].append(f"  - 01_targeted_research.md ({p1.stat().st_size} bytes)")

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
        "phase": "phase6",
        "enabled": True,
        "config_file": str(PHASE_CONFIG_FILE),
        "pid": os.getpid(),
        "started_at": datetime.now().isoformat(),
        "research_folder": research_folder or "",
    }

    with open(ACTIVE_PHASE_FILE, "w", encoding="utf-8") as f:
        json.dump(phase_info, f, indent=2)

    log(f"Created active_phase.json: phase=phase6, pid={os.getpid()}, research_folder={research_folder or 'NONE'}")


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
def build_phase6_prompt(research_folder: str, validation: dict) -> str:
    """Build the initial prompt for Phase 6 unattended execution."""
    files_str = "\n".join(validation["files"]) if validation["files"] else "  (no files found)"

    prompt = f"""/phase6-paper-writing

#batch-mode

Proceed in Unattended mode. Research folder is located at:

  {research_folder}

Available files:
{files_str}

Execute all Phase 6 steps automatically (Step 01 through Step 07).
Do NOT ask for user confirmation — proceed through all steps without stopping.

Key instructions:
- Step 01: Initialize paper folder, collect figures, verify prerequisites
  - PRIMARY input: 045_validated_hypothesis.md (Phase 4.5 synthesis)
  - Also read: verification_state.yaml, 03_refinement.yaml, h-*/04_validation.md
- Step 02: Design narrative structure → 06_narrative_blueprint.yaml
  - Create hook strategy, problem framing (3 levels), key insight, evidence structure
- Step 03: Story Group A — Foundation sections
  - Generate 01_introduction.md, 02_related_work.md, 03_methodology.md
- Step 04: Story Group B — Evidence sections
  - Generate 04_experiments.md, 05_results.md, 06_discussion.md
- Step 05: Story Group C — Closure sections
  - Generate 07_conclusion.md (with callbacks to Introduction hook)
  - Generate 00_abstract.md (written LAST with actual quantitative results)
- Step 06: Compile references → 06_references.bib
  - Use Semantic Scholar MCP for citation verification
- Step 07: Final merge → 06_paper.md, 065_ground_truth.yaml
  - Merge all sections, coherence check, extract ground truth for Phase 6.5
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
        description="Phase 6 Launcher — Run /phase6-paper-writing unattended",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --research-folder docs/youra_research/20260304_scsl
  %(prog)s --research-folder /absolute/path --timeout 7200
        """,
    )

    parser.add_argument("--research-folder", type=str, required=True,
                        help="Path to research folder containing 045_validated_hypothesis.md")
    parser.add_argument("--timeout", type=int, default=7200,
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
        phase_name="phase6",
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
    clear_phase_complete_lock("phase6")  # Clear any stale PHASE_COMPLETE lock from previous run

    research_folder = str(Path(args.research_folder).resolve())

    validation = validate_inputs(research_folder)

    log("=" * 60)
    log("Phase 6 Launcher starting")
    log(f"  Research folder: {research_folder}")
    log(f"  Folder valid: {validation['valid']}")
    log(f"  Has verification_state: {validation['has_verification_state']}")
    log(f"  Has 045_validated_hypothesis.md: {validation['has_validated_hypothesis']}")
    log(f"  Has 03_refinement.yaml: {validation['has_refinement']}")
    log(f"  Synthesis completed: {validation['synthesis_completed']}")
    log(f"  Hypothesis folders: {validation['hypothesis_count']}")
    log(f"  Timeout: {args.timeout}s")
    log("=" * 60)

    if not validation["valid"]:
        log("ERROR: Research folder does not exist. Aborting.")
        sys.exit(1)

    if not validation["has_verification_state"]:
        log("ERROR: verification_state.yaml not found. Aborting.")
        sys.exit(1)

    if not validation["has_validated_hypothesis"]:
        log("ERROR: 045_validated_hypothesis.md not found — Phase 4.5 must complete first. Aborting.")
        sys.exit(1)

    if not validation["synthesis_completed"]:
        log("WARNING: synthesis_completed is not true in verification_state.yaml.")

    atexit.register(cleanup)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    set_auto_responder_enabled(True)
    create_active_phase(research_folder=research_folder)

    prompt = build_phase6_prompt(research_folder, validation)

    log(f"Launching Claude CLI with prompt ({len(prompt)} chars)")
    output_log = CACHE_DIR / "phase6_output.log"
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
            phase_name="phase6",
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
        log_timeout_marker(log, "phase6", elapsed, attempt="initial")

    if main_timed_out:
        cleanup()
        rc = post_timeout_exit_code(research_folder, "phase6", log)
        sys.exit(rc)

    # Check for MUST_STOP signal from hook
    must_stop_reason = check_must_stop()
    if must_stop_reason:
        log(f"MUST_STOP detected — aborting phase6: {must_stop_reason}")
        cleanup()
        sys.exit(1)

    # Verify outputs; retry with corrective prompt if needed
    verify_and_write_json("phase6", research_folder, exit_code)
    clear_phase_complete_lock("phase6")  # Clear lock so retry session is not immediately approved
    for _attempt in range(MAX_RETRIES):
        if exit_code != 0 or _check_passed("phase6"):
            break
        log(f"Phase 6 verification FAILED — retry {_attempt + 1}/{MAX_RETRIES}")
        _retry_prompt = build_retry_prompt("phase6", research_folder)
        exit_code = _run_claude(_retry_prompt, args.timeout,
                                CACHE_DIR / "phase6_output.log")
        if exit_code == 124:
            cleanup()
            rc = post_timeout_exit_code(research_folder, "phase6", log)
            sys.exit(rc)
        must_stop_reason = check_must_stop()
        if must_stop_reason:
            log(f"MUST_STOP during retry — aborting phase6: {must_stop_reason}")
            exit_code = 1
            break
        verify_and_write_json("phase6", research_folder, exit_code)

    cleanup()

    print(research_folder)

    log("Phase 6 Launcher complete")
    log("=" * 60)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
