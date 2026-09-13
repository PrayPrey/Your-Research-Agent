#!/usr/bin/env python3
"""
Phase 6.5.1 Launcher — Runs /phase651-overleaf Unattended

Launches Claude CLI with the /phase651-overleaf command and configures
the phase-specific auto-responder hook for fully unattended execution.
Requires --research-folder pointing to the folder containing Phase 6.5 output.

Phase 6.5.1 is a 4-step Overleaf LaTeX + PDF generation workflow:
  Step 01: Initialize (validate inputs, create folder structure, check LaTeX toolchain)
  Step 02: Markdown to LaTeX Conversion (split paper, convert sections, escape chars)
  Step 03: Assemble Project (main.tex from template, copy figures/references, README)
  Step 04: Compile and Verify (pdflatex + bibtex, verify PDF, update state)

Usage:
  python run_phase651.py --research-folder docs/youra_research/20260304_scsl
  python run_phase651.py --research-folder <path> --timeout 7200

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
PHASE_CONFIG_FILE = SCRIPT_DIR / "phase651_auto_config.yaml"
AUTO_RESPONDER_CONFIG = SCRIPT_DIR / "auto_responder_config.yaml"
PROJECT_DIR = SCRIPT_DIR.parent.parent
CLAUDE_CLI = Path.home() / ".local" / "bin" / "claude"

LOG_FILE = CACHE_DIR / "run_phase651.log"


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
    """Validate research folder and Phase 6.5 prerequisites."""
    folder = Path(research_folder)
    paper_dir = folder / "paper"
    result = {
        "valid": False,
        "files": [],
        "has_verification_state": False,
        "has_paper_final": False,
        "has_references": False,
        "has_figures": False,
        "figure_count": 0,
        "has_overleaf": False,
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

    # Check Phase 6.5 final paper output
    paper_final = paper_dir / "06_paper_final.md"
    if paper_final.exists():
        result["has_paper_final"] = True
        result["files"].append(f"  - paper/06_paper_final.md ({paper_final.stat().st_size} bytes)")

    # Check references
    refs = paper_dir / "06_references.bib"
    if refs.exists():
        result["has_references"] = True
        result["files"].append(f"  - paper/06_references.bib ({refs.stat().st_size} bytes)")

    # Check figures folder
    figures_dir = paper_dir / "figures"
    if figures_dir.exists() and figures_dir.is_dir():
        fig_files = list(figures_dir.glob("*"))
        result["figure_count"] = len(fig_files)
        if fig_files:
            result["has_figures"] = True
        for ff in sorted(fig_files)[:20]:  # Cap listing at 20
            result["files"].append(f"  - paper/figures/{ff.name} ({ff.stat().st_size} bytes)")

    # Check for existing overleaf folder (for resume)
    overleaf_dir = paper_dir / "overleaf"
    if overleaf_dir.exists():
        result["has_overleaf"] = True
        for of in sorted(overleaf_dir.iterdir()):
            if of.is_file():
                result["files"].append(f"  - paper/overleaf/{of.name} ({of.stat().st_size} bytes)")
        # Check sections subfolder
        sec_dir = overleaf_dir / "sections"
        if sec_dir.exists():
            for sf in sorted(sec_dir.iterdir()):
                if sf.is_file():
                    result["files"].append(f"  - paper/overleaf/sections/{sf.name} ({sf.stat().st_size} bytes)")

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
        "phase": "phase651",
        "enabled": True,
        "config_file": str(PHASE_CONFIG_FILE),
        "pid": os.getpid(),
        "started_at": datetime.now().isoformat(),
        "research_folder": research_folder or "",
    }

    with open(ACTIVE_PHASE_FILE, "w", encoding="utf-8") as f:
        json.dump(phase_info, f, indent=2)

    log(f"Created active_phase.json: phase=phase651, pid={os.getpid()}, research_folder={research_folder or 'NONE'}")


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
def build_phase651_prompt(research_folder: str, validation: dict) -> str:
    """Build the initial prompt for Phase 6.5.1 unattended execution."""
    files_str = "\n".join(validation["files"]) if validation["files"] else "  (no files found)"

    prompt = f"""/phase651-overleaf

#batch-mode

Proceed in Unattended mode. Research folder is located at:

  {research_folder}

Available files:
{files_str}

Execute all Phase 6.5.1 steps automatically (Step 01 through Step 04).
Do NOT ask for user confirmation — proceed through all steps without stopping.

Key instructions:
- Step 01: Initialize — validate 06_paper_final.md exists, create paper/overleaf/ folder
  structure (sections/, figures/), check pdflatex/bibtex availability, download ICML 2025
  style files if needed
- Step 02: Markdown to LaTeX — split 06_paper_final.md into sections, convert each to
  LaTeX format (escape special chars, booktabs tables, figure environments, \\cite{{}} refs),
  write 9 .tex files to overleaf/sections/
- Step 03: Assemble Project — generate main.tex, copy 06_references.bib to
  overleaf/references.bib, copy figures, generate README.md
- Step 04: Compile and Verify — run pdflatex + bibtex (3 passes), verify output.pdf
  exists and is non-empty, update verification_state.yaml
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
        description="Phase 6.5.1 Launcher — Run /phase651-overleaf unattended",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --research-folder docs/youra_research/20260304_scsl
  %(prog)s --research-folder /absolute/path --timeout 7200
        """,
    )

    parser.add_argument("--research-folder", type=str, required=True,
                        help="Path to research folder containing paper/06_paper_final.md")
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
        phase_name="phase651",
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
    clear_phase_complete_lock("phase651")

    research_folder = str(Path(args.research_folder).resolve())

    validation = validate_inputs(research_folder)

    log("=" * 60)
    log("Phase 6.5.1 Launcher starting")
    log(f"  Research folder: {research_folder}")
    log(f"  Folder valid: {validation['valid']}")
    log(f"  Has verification_state: {validation['has_verification_state']}")
    log(f"  Has paper/06_paper_final.md: {validation['has_paper_final']}")
    log(f"  Has paper/06_references.bib: {validation['has_references']}")
    log(f"  Has figures ({validation['figure_count']}): {validation['has_figures']}")
    log(f"  Existing overleaf folder: {validation['has_overleaf']}")
    log(f"  Timeout: {args.timeout}s")
    log("=" * 60)

    if not validation["valid"]:
        log("ERROR: Research folder does not exist. Aborting.")
        sys.exit(1)

    if not validation["has_paper_final"]:
        log("ERROR: paper/06_paper_final.md not found — Phase 6.5 must complete first. Aborting.")
        sys.exit(1)

    if not validation["has_references"]:
        log("WARNING: paper/06_references.bib not found — bibliography may be missing.")

    if not validation["has_figures"]:
        log("WARNING: paper/figures/ not found or empty — figures may be missing.")

    atexit.register(cleanup)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    set_auto_responder_enabled(True)
    create_active_phase(research_folder=research_folder)

    prompt = build_phase651_prompt(research_folder, validation)

    log(f"Launching Claude CLI with prompt ({len(prompt)} chars)")
    output_log = CACHE_DIR / "phase651_output.log"
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
            phase_name="phase651",
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
        log_timeout_marker(log, "phase651", elapsed, attempt="initial")

    if main_timed_out:
        cleanup()
        rc = post_timeout_exit_code(research_folder, "phase651", log)
        sys.exit(rc)

    # Check for MUST_STOP signal from hook
    must_stop_reason = check_must_stop()
    if must_stop_reason:
        log(f"MUST_STOP detected — aborting phase651: {must_stop_reason}")
        cleanup()
        sys.exit(1)

    # Verify outputs; retry with corrective prompt if needed
    verify_and_write_json("phase651", research_folder, exit_code)
    clear_phase_complete_lock("phase651")
    for _attempt in range(MAX_RETRIES):
        if exit_code != 0 or _check_passed("phase651"):
            break
        log(f"Phase 6.5.1 verification FAILED — retry {_attempt + 1}/{MAX_RETRIES}")
        _retry_prompt = build_retry_prompt("phase651", research_folder)
        exit_code = _run_claude(_retry_prompt, args.timeout,
                                CACHE_DIR / "phase651_output.log")
        if exit_code == 124:
            cleanup()
            rc = post_timeout_exit_code(research_folder, "phase651", log)
            sys.exit(rc)
        must_stop_reason = check_must_stop()
        if must_stop_reason:
            log(f"MUST_STOP during retry — aborting phase651: {must_stop_reason}")
            exit_code = 1
            break
        verify_and_write_json("phase651", research_folder, exit_code)

    cleanup()

    print(research_folder)

    log("Phase 6.5.1 Launcher complete")
    log("=" * 60)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
