#!/usr/bin/env python3
"""
Phase 2A Launcher — Runs /phase2a-dialogue Unattended

Launches Claude CLI with the /phase2a-dialogue command and configures
the phase-specific auto-responder hook for fully unattended execution.
Requires --research-folder pointing to the folder containing Phase 1 output.

Phase 2A is a 3-step workflow:
  Step 0: Initialize (gap selection + paper preparation)
  Step 1: Tikitaka Discussion (self-contained inline loop with orchestrate_exchange.py)
  Step 2: Result Structuring (produces Phase 2B-compatible YAML outputs)

The hook system (GPT-5.2 via OpenRouter) handles step transitions where Claude
may stop between steps. The discussion loop itself runs inline without hooks.

Usage:
  python run_phase2a.py --research-folder /path/to/youra_research/20260304_...
  python run_phase2a.py --research-folder /path/to/youra_research/20260304_... --timeout 5400

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
PHASE_CONFIG_FILE = SCRIPT_DIR / "phase2a_auto_config.yaml"
AUTO_RESPONDER_CONFIG = SCRIPT_DIR / "auto_responder_config.yaml"
PROJECT_DIR = SCRIPT_DIR.parent.parent  # /home/anonymous/YouRA_result_new_2/scsl
CLAUDE_CLI = Path.home() / ".local" / "bin" / "claude"

LOG_FILE = CACHE_DIR / "run_phase2a.log"


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
    Validate that the research folder exists and contains Phase 1 output.

    Returns:
        dict with keys: valid (bool), files (list of file info strings),
        has_phase1 (bool), has_papers (bool)
    """
    folder = Path(research_folder)
    result = {
        "valid": False,
        "files": [],
        "has_phase1": False,
        "has_papers": False,
    }

    if not folder.exists() or not folder.is_dir():
        log(f"ERROR: Research folder does not exist: {research_folder}")
        return result

    result["valid"] = True

    # Check Phase 1 output
    phase1_file = folder / "01_targeted_research.md"
    if phase1_file.exists():
        result["has_phase1"] = True
        size = phase1_file.stat().st_size
        result["files"].append(f"  - 01_targeted_research.md ({size} bytes)")

    # Check papers folder
    papers_dir = folder / "papers"
    if papers_dir.exists() and papers_dir.is_dir():
        paper_count = len(list(papers_dir.glob("*.md")))
        if paper_count > 0:
            result["has_papers"] = True
            result["files"].append(f"  - papers/ ({paper_count} .md files)")

    # Check Phase 0 output (should be preserved)
    brainstorm = folder / "00_brainstorm_session.md"
    if brainstorm.exists():
        size = brainstorm.stat().st_size
        result["files"].append(f"  - 00_brainstorm_session.md ({size} bytes)")

    return result


def collect_serena_memory_context() -> dict:
    """
    Read every Markdown memory file under .serena/memories for direct prompt injection.

    Phase 2A reroutes depend on these memories as hard cross-phase input. The launcher
    injects their contents into the initial prompt instead of asking Claude to discover
    them opportunistically.
    """
    memories_dir = PROJECT_DIR / ".serena" / "memories"
    result = {
        "count": 0,
        "files": [],
        "content": "",
        "dir": str(memories_dir),
    }

    if not memories_dir.exists() or not memories_dir.is_dir():
        log(f"Serena memories directory not found: {memories_dir}")
        return result

    chunks = []
    for memory_file in sorted(memories_dir.glob("*.md")):
        try:
            content = memory_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = memory_file.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            log(f"WARNING: Failed to read Serena memory {memory_file}: {e}")
            continue

        rel_path = memory_file.relative_to(PROJECT_DIR)
        result["files"].append(f"  - {rel_path} ({len(content)} chars)")
        chunks.append(f"### {rel_path}\n\n{content.rstrip()}")

    result["count"] = len(chunks)
    result["content"] = "\n\n---\n\n".join(chunks)
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
        "phase": "phase2a",
        "enabled": True,
        "config_file": str(PHASE_CONFIG_FILE),
        "pid": os.getpid(),
        "started_at": datetime.now().isoformat(),
        "research_folder": research_folder or "",
    }

    with open(ACTIVE_PHASE_FILE, "w", encoding="utf-8") as f:
        json.dump(phase_info, f, indent=2)

    log(f"Created active_phase.json: phase=phase2a, pid={os.getpid()}, research_folder={research_folder or 'NONE'}")


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
FEASIBILITY_CONSTRAINTS = """\

## MANDATORY FEASIBILITY CONSTRAINTS (Pipeline-Enforced)

Reject ideas that require **new benchmarks, rubrics, or scoring frameworks**.
Reject ideas that require **synthetic/generated data or future follow-up data that does not yet exist**.
Reject ideas that require **human evaluation, annotation, or subjective scoring by human raters**.
Accept only hypotheses that can be **tested immediately using existing real datasets and existing benchmarks**."""


def build_serena_memory_prompt_block(serena_memory_context: dict) -> str:
    """Build the mandatory cross-phase memory block injected into Phase 2A."""
    if not serena_memory_context or serena_memory_context.get("count", 0) == 0:
        return f"""\

## MANDATORY SERENA MEMORY CONTEXT (Hard Input)

The Phase 2A launcher checked `{PROJECT_DIR / ".serena" / "memories"}` and found no `.md` memory files.
Proceed as a first Phase 2A attempt only if the research folder also has no routing archive.
"""

    files_str = "\n".join(serena_memory_context["files"])
    content = serena_memory_context["content"]

    return f"""\

## MANDATORY SERENA MEMORY CONTEXT (Hard Input)

The Phase 2A launcher has already read every `.md` file under:

  {serena_memory_context["dir"]}

Treat the content below as a mandatory Phase 2A input, not optional background.
Before Step 0 gap selection and before Step 1 discussion:

- Use these memories to identify prior failed/superseded hypotheses, pivots, partial results, and prohibited redesign directions.
- Do not proceed as a first attempt if any memory contains `ROUTED_TO_PHASE_2A`, `SUPERSEDED`, `PARTIAL`, `FAIL`, or pivot records.
- Initialize `discussion_log.md` with a `Previous Failure / Routing Context` section summarizing these memories.
- Ensure the generated hypothesis explicitly avoids the failed approach families described in these memories.

Loaded memory files:
{files_str}

<serena_memory_context>
{content}
</serena_memory_context>
"""


def build_phase2a_prompt(research_folder: str, validation: dict, serena_memory_context: dict = None) -> str:
    """
    Build the initial prompt for Phase 2A unattended execution.

    Includes the research folder path so Claude knows where Phase 1 outputs are.
    """
    files_str = "\n".join(validation["files"]) if validation["files"] else "  (no files found)"
    serena_memory_block = build_serena_memory_prompt_block(serena_memory_context or {})

    prompt = f"""/phase2a-dialogue

#batch-mode

Proceed in Unattended mode. Research folder with Phase 1 output is located at:

  {research_folder}

Available files:
{files_str}

Read the Phase 1 output files at the path above and execute all Phase 2A steps automatically.
Read and apply the mandatory Serena memory context embedded below as hard input.
Do NOT ask for user confirmation — proceed through all steps (Step 0, Step 1, Step 2) without stopping.

Key instructions:
- Step 0: Select highest priority gap from 01_targeted_research.md, prepare papers, initialize discussion_log.md
- Step 1: Run the Tikitaka discussion loop (orchestrate_exchange.py) inline until convergence
- Step 2: Structure discussion results into Phase 2B-compatible YAML outputs (03_refinement.yaml, 02_synthesis.yaml, final_opinions.yaml)
{serena_memory_block}
{FEASIBILITY_CONSTRAINTS}"""

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
        description="Phase 2A Launcher — Run /phase2a-dialogue unattended",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --research-folder docs/youra_research/20260304_143000_scsl
  %(prog)s --research-folder /absolute/path/to/research_folder --timeout 5400
        """,
    )

    parser.add_argument("--research-folder", type=str, required=True,
                        help="Path to research folder containing Phase 1 output")
    parser.add_argument("--retry-prompt", type=str, default=None,
                        help="Override prompt for retry run (injected by run_early_pipeline.py)")
    parser.add_argument("--timeout", type=int, default=5400,
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
        phase_name="phase2a",
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
    clear_phase_complete_lock("phase2a")  # Clear any stale PHASE_COMPLETE lock from previous run

    # Resolve research folder path (support relative paths)
    research_folder = str(Path(args.research_folder).resolve())

    # Validate research folder
    validation = validate_research_folder(research_folder)

    log("=" * 60)
    log("Phase 2A Launcher starting")
    log(f"  Research folder: {research_folder}")
    log(f"  Folder valid: {validation['valid']}")
    log(f"  Has Phase 1 output: {validation['has_phase1']}")
    log(f"  Has papers: {validation['has_papers']}")
    log(f"  Timeout: {args.timeout}s")

    serena_memory_context = collect_serena_memory_context()
    log(f"  Serena memory .md files: {serena_memory_context['count']}")

    if not validation["valid"]:
        log("ERROR: Research folder does not exist. Aborting.")
        sys.exit(1)

    if not validation["has_phase1"]:
        log("WARNING: 01_targeted_research.md not found in research folder.")
        log("  Phase 2A workflow will attempt to find it on its own.")

    # Register cleanup
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Step 1: Enable auto_responder_config
    set_auto_responder_enabled(True)

    # Step 2: Create active_phase.json (include research_folder for snapshot-based diff)
    create_active_phase(research_folder=research_folder)

    # Step 3: Build prompt and launch Claude CLI
    prompt = args.retry_prompt if args.retry_prompt else build_phase2a_prompt(
        research_folder,
        validation,
        serena_memory_context,
    )

    log(f"Launching Claude CLI with prompt ({len(prompt)} chars)")
    log(f"CWD: {PROJECT_DIR}")

    output_log = CACHE_DIR / "phase2a_claude_output.log"
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
            phase_name="phase2a",
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
        log_timeout_marker(log, "phase2a", elapsed, attempt="initial")

    if main_timed_out:
        cleanup()
        rc = post_timeout_exit_code(research_folder, "phase2a", log)
        sys.exit(rc)

    # Check for MUST_STOP signal from hook (fatal error — skip verify/retry)
    must_stop_reason = check_must_stop()
    if must_stop_reason:
        log(f"MUST_STOP detected — aborting phase2a: {must_stop_reason}")
        cleanup()
        sys.exit(1)

    # Verify outputs; retry with corrective prompt if needed
    verify_and_write_json("phase2a", research_folder, exit_code)
    clear_phase_complete_lock("phase2a")  # Clear lock so retry session is not immediately approved
    for _attempt in range(MAX_RETRIES):
        if exit_code != 0 or _check_passed("phase2a"):
            break
        log(f"Phase 2A verification FAILED — retry {_attempt + 1}/{MAX_RETRIES}")
        _retry_prompt = build_retry_prompt("phase2a", research_folder)
        exit_code = _run_claude(_retry_prompt, args.timeout,
                               CACHE_DIR / "phase2a_claude_output.log")
        if exit_code == 124:
            cleanup()
            rc = post_timeout_exit_code(research_folder, "phase2a", log)
            sys.exit(rc)
        verify_and_write_json("phase2a", research_folder, exit_code)

    # Step 4: Cleanup
    cleanup()

    # Print research folder path to stdout for downstream chaining
    print(research_folder)

    log("Phase 2A Launcher complete")
    log("=" * 60)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
