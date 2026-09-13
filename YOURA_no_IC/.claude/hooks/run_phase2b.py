#!/usr/bin/env python3
"""
Phase 2B Launcher — Runs /phase2b-planning Unattended

Launches Claude CLI with the /phase2b-planning command and configures
the phase-specific auto-responder hook for fully unattended execution.
Requires --research-folder pointing to the folder containing Phase 2A output.

Phase 2B is an 11-step workflow (Step 00 ~ Step 10):
  Step 00: Init Environment (MCP service verification)
  Step 01: Init Parsing (Phase 2A file loading)
  Step 02: Input Hypothesis (confirmation menu)
  Step 03: Hypothesis Generation (MCP-powered sub-hypothesis generation)
  Step 04: Hypothesis Inventory (inventory creation)
  Step 05: Risk Analysis (risk mapping)
  Step 06: Dependency Graph (DAG generation)
  Step 07: Timeline Planning (Gantt generation)
  Step 08: Dialectical Analysis (thesis-antithesis-synthesis)
  Step 09: Summary (summary generation)
  Step 10: Finalize (verification_state.yaml generation)

The hook system (GPT-5.2 via OpenRouter) handles step transitions where Claude
may stop between steps.

Usage:
  python run_phase2b.py --research-folder /path/to/youra_research/20260304_...
  python run_phase2b.py --research-folder /path/to/youra_research/20260304_... --timeout 7200

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
from phase_output_verifier import verify_and_write_json, build_retry_prompt, MAX_RETRIES, clear_must_stop, check_must_stop, build_claude_cmd, clear_phase_complete_lock
from timeout_policy import log_timeout_marker, post_timeout_exit_code, core_artifacts_exist
from pathlib import Path

# ============================================================
# Path Configuration
# ============================================================
SCRIPT_DIR = Path(__file__).parent
CACHE_DIR = SCRIPT_DIR / ".cache"
ACTIVE_PHASE_FILE = CACHE_DIR / "active_phase.json"
PHASE_CONFIG_FILE = SCRIPT_DIR / "phase2b_auto_config.yaml"
AUTO_RESPONDER_CONFIG = SCRIPT_DIR / "auto_responder_config.yaml"
PROJECT_DIR = SCRIPT_DIR.parent.parent  # /home/anonymous/YouRA_result_new_2/scsl
CLAUDE_CLI = Path.home() / ".local" / "bin" / "claude"

LOG_FILE = CACHE_DIR / "run_phase2b.log"


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
def validate_research_folder(research_folder: str) -> dict:
    """
    Validate that the research folder exists and contains Phase 2A output.

    Required files:
      - 03_refinement.yaml (Phase 2A primary output)
      - 02_synthesis.yaml (synthesis details)
      - 01_round_table/final_opinions.yaml (per-agent assessments)

    Returns:
        dict with keys: valid (bool), files (list of file info strings),
        has_refinement (bool), has_synthesis (bool), has_opinions (bool)
    """
    folder = Path(research_folder)
    result = {
        "valid": False,
        "files": [],
        "has_refinement": False,
        "has_synthesis": False,
        "has_opinions": False,
    }

    if not folder.exists() or not folder.is_dir():
        log(f"ERROR: Research folder does not exist: {research_folder}")
        return result

    result["valid"] = True

    # Check Phase 2A primary output: 03_refinement.yaml
    refinement = folder / "03_refinement.yaml"
    if refinement.exists():
        result["has_refinement"] = True
        size = refinement.stat().st_size
        result["files"].append(f"  - 03_refinement.yaml ({size} bytes)")

    # Check synthesis: 02_synthesis.yaml
    synthesis = folder / "02_synthesis.yaml"
    if synthesis.exists():
        result["has_synthesis"] = True
        size = synthesis.stat().st_size
        result["files"].append(f"  - 02_synthesis.yaml ({size} bytes)")

    # Check round table opinions: 01_round_table/final_opinions.yaml
    opinions = folder / "01_round_table" / "final_opinions.yaml"
    if opinions.exists():
        result["has_opinions"] = True
        size = opinions.stat().st_size
        result["files"].append(f"  - 01_round_table/final_opinions.yaml ({size} bytes)")

    # Also list other relevant files for context
    for fname in ["03_refinement.md", "01_targeted_research.md", "00_brainstorm_session.md"]:
        fpath = folder / fname
        if fpath.exists():
            size = fpath.stat().st_size
            result["files"].append(f"  - {fname} ({size} bytes)")

    # Check papers folder
    papers_dir = folder / "papers"
    if papers_dir.exists() and papers_dir.is_dir():
        paper_count = len(list(papers_dir.glob("*.md")))
        if paper_count > 0:
            result["files"].append(f"  - papers/ ({paper_count} .md files)")

    return result


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
        "phase": "phase2b",
        "enabled": True,
        "config_file": str(PHASE_CONFIG_FILE),
        "pid": os.getpid(),
        "started_at": datetime.now().isoformat(),
        "research_folder": research_folder or "",
    }

    with open(ACTIVE_PHASE_FILE, "w", encoding="utf-8") as f:
        json.dump(phase_info, f, indent=2)

    log(f"Created active_phase.json: phase=phase2b, pid={os.getpid()}, research_folder={research_folder or 'NONE'}")


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
def build_phase2b_prompt(research_folder: str, validation: dict) -> str:
    """
    Build the initial prompt for Phase 2B unattended execution.

    Includes the research folder path so Claude knows where Phase 2A outputs are.
    """
    files_str = "\n".join(validation["files"]) if validation["files"] else "  (no files found)"

    prompt = f"""/phase2b-planning

#batch-mode

Proceed in Unattended mode. Research folder with Phase 2A output is located at:

  {research_folder}

Available files:
{files_str}

Read the Phase 2A output files at the path above and execute all Phase 2B steps automatically.
Do NOT ask for user confirmation — proceed through all steps (Step 00 through Step 10) without stopping.

Key instructions:
- When presented with any menu, automatically select [C] Continue
- Do NOT ask for user confirmation at any point — proceed autonomously
- Step 00: Verify MCP services and environment
- Step 01: Parse Phase 2A outputs (03_refinement.yaml, 02_synthesis.yaml, final_opinions.yaml)
- Step 02: Input and validate main hypothesis from refinement data
- Step 03: Generate sub-hypotheses using MCP-powered analysis
- Step 04: Create hypothesis inventory
- Step 05: Perform risk analysis and risk mapping
- Step 06: Build dependency graph (DAG)
- Step 07: Generate timeline/Gantt planning
- Step 08: Run dialectical analysis (thesis-antithesis-synthesis)
- Step 09: Write summary
- Step 10: Finalize and generate verification_state.yaml

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
        description="Phase 2B Launcher — Run /phase2b-planning unattended",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --research-folder docs/youra_research/20260304_143000_scsl
  %(prog)s --research-folder /absolute/path/to/research_folder --timeout 7200
        """,
    )

    parser.add_argument("--research-folder", type=str, required=True,
                        help="Path to research folder containing Phase 2A output")
    parser.add_argument("--retry-prompt", type=str, default=None,
                        help="Override prompt for retry run (injected by run_early_pipeline.py)")
    parser.add_argument("--timeout", type=int, default=7200,
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
        phase_name="phase2b",
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
    clear_phase_complete_lock("phase2b")  # Clear any stale PHASE_COMPLETE lock from previous run

    # Resolve research folder path (support relative paths)
    research_folder = str(Path(args.research_folder).resolve())

    # Validate research folder
    validation = validate_research_folder(research_folder)

    log("=" * 60)
    log("Phase 2B Launcher starting")
    log(f"  Research folder: {research_folder}")
    log(f"  Folder valid: {validation['valid']}")
    log(f"  Has 03_refinement.yaml: {validation['has_refinement']}")
    log(f"  Has 02_synthesis.yaml: {validation['has_synthesis']}")
    log(f"  Has final_opinions.yaml: {validation['has_opinions']}")
    log(f"  Timeout: {args.timeout}s")

    if not validation["valid"]:
        log("ERROR: Research folder does not exist. Aborting.")
        sys.exit(1)

    if not validation["has_refinement"]:
        log("ERROR: 03_refinement.yaml not found — this is the primary Phase 2A output.")
        log("  Phase 2B cannot proceed without it. Aborting.")
        sys.exit(1)

    if not validation["has_synthesis"]:
        log("WARNING: 02_synthesis.yaml not found in research folder.")
        log("  Phase 2B will attempt to proceed with available data.")

    if not validation["has_opinions"]:
        log("WARNING: 01_round_table/final_opinions.yaml not found in research folder.")
        log("  Phase 2B will attempt to proceed with available data.")

    # Register cleanup
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Step 1: Enable auto_responder_config
    set_auto_responder_enabled(True)

    # Step 2: Create active_phase.json (include research_folder for snapshot-based diff)
    create_active_phase(research_folder=research_folder)

    # Step 3: Build prompt and launch Claude CLI
    prompt = args.retry_prompt if args.retry_prompt else build_phase2b_prompt(research_folder, validation)

    log(f"Launching Claude CLI with prompt ({len(prompt)} chars)")
    output_log = CACHE_DIR / "phase2b_claude_output.log"
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
            phase_name="phase2b",
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
        log_timeout_marker(log, "phase2b", elapsed, attempt="initial")

    if main_timed_out:
        cleanup()
        rc = post_timeout_exit_code(research_folder, "phase2b", log)
        sys.exit(rc)

    # Check for MUST_STOP signal from hook (fatal error — skip verify/retry)
    must_stop_reason = check_must_stop()
    if must_stop_reason:
        log(f"MUST_STOP detected — aborting phase2b: {must_stop_reason}")
        cleanup()
        sys.exit(1)

    # Verify outputs; retry with corrective prompt if needed
    verify_and_write_json("phase2b", research_folder, exit_code)
    clear_phase_complete_lock("phase2b")  # Clear lock so retry session is not immediately approved
    for _attempt in range(MAX_RETRIES):
        if exit_code != 0 or _check_passed("phase2b"):
            break
        log(f"Phase 2B verification FAILED — retry {_attempt + 1}/{MAX_RETRIES}")
        _retry_prompt = build_retry_prompt("phase2b", research_folder)
        exit_code = _run_claude(_retry_prompt, args.timeout,
                               CACHE_DIR / "phase2b_claude_output.log")
        if exit_code == 124:
            cleanup()
            rc = post_timeout_exit_code(research_folder, "phase2b", log)
            sys.exit(rc)
        verify_and_write_json("phase2b", research_folder, exit_code)

    # Step 4: Cleanup
    cleanup()

    # Print research folder path to stdout for downstream chaining
    print(research_folder)

    log("Phase 2B Launcher complete")
    log("=" * 60)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
