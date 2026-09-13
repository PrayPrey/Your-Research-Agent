#!/usr/bin/env python3
"""
Early Pipeline Runner — Phase 0 → Phase 1 → Phase 2A → Phase 2B

Sequentially runs the first four phases of the YouRA pipeline unattended.
Each phase is launched as a subprocess via its own run_phase*.py launcher,
which manages its own active_phase.json and hook orchestration system
(phase_auto_responder.py + phase*_auto_config.yaml + phase*_responder.md).

Behavior:
  - Phase 0: Input required (file or text topic). Creates research folder.
  - Phase 1: Auto-detects research folder from Phase 0 output.
  - Phase 2A: Passes research folder from Phase 0/1.
  - Phase 2B: Passes same research folder, aborts if 03_refinement.yaml missing.
  - On any phase failure (exit code != 0): immediately abort, print error.
  - No resume support — start fresh each run.

Usage:
  python run_early_pipeline.py <input> [options]

  python run_early_pipeline.py docs/research_idea.md
  python run_early_pipeline.py "Weak supervision for image classification"
  python run_early_pipeline.py docs/research_idea.md \\
      --research-folder docs/youra_research/20260304_scsl \\
      --timeout-phase0 3600 --timeout-phase1 3600 \\
      --timeout-phase2a 5400 --timeout-phase2b 7200

Author: Anonymous
"""

import argparse
import json
import glob
import os
import select
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# ============================================================
# Path Configuration
# ============================================================
SCRIPT_DIR = Path(__file__).parent
CACHE_DIR = SCRIPT_DIR / ".cache"
PROJECT_DIR = SCRIPT_DIR.parent.parent
RESEARCH_BASE = PROJECT_DIR / "docs" / "youra_research"

LOG_FILE = CACHE_DIR / "run_early_pipeline.log"

# Phase launcher scripts
RUN_PHASE0 = SCRIPT_DIR / "run_phase0.py"
RUN_PHASE1 = SCRIPT_DIR / "run_phase1.py"
RUN_PHASE2A = SCRIPT_DIR / "run_phase2a.py"
RUN_PHASE2B = SCRIPT_DIR / "run_phase2b.py"

# Default timeouts (seconds)
DEFAULT_TIMEOUTS = {
    "phase0": 3600,
    "phase1": 3600,
    "phase2a": 5400,
    "phase2b": 7200,
}

# Maximum retry attempts after verification failure (not counting the first run)
MAX_RETRIES = 2


# ============================================================
# Logging
# ============================================================
def log(message: str):
    """Log to file and stderr."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] [PIPELINE] {message}"
    print(entry, file=sys.stderr)
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except Exception:
        pass


def print_banner(text: str):
    """Print a visible section banner to stderr."""
    border = "=" * 60
    log(border)
    log(text)
    log(border)


# ============================================================
# Phase Output Verification
# ============================================================
def _check_file(research_folder: str, rel_path: str, phase_name: str,
                check_unfilled: bool = False, check_nonempty: bool = False,
                check_contains: str = None) -> bool:
    """Check a single output file. Returns True if all checks pass."""
    fpath = Path(research_folder) / rel_path
    if not fpath.exists():
        log(f"ERROR: [{phase_name}] Missing output: {rel_path}")
        return False
    size = fpath.stat().st_size
    if size == 0:
        log(f"ERROR: [{phase_name}] Empty file: {rel_path}")
        return False
    if check_unfilled or check_contains:
        text = fpath.read_text(encoding="utf-8", errors="ignore")
        if check_unfilled and "{{UNFILLED:" in text:
            log(f"ERROR: [{phase_name}] Unfilled placeholders in: {rel_path}")
            return False
        if check_contains and check_contains not in text:
            log(f"ERROR: [{phase_name}] Missing required content '{check_contains}' in: {rel_path}")
            return False
    log(f"  OK: {rel_path} ({size} bytes)")
    return True


def verify_phase0_output(research_folder: str) -> bool:
    """
    Phase 0 primary output: 00_brainstorm_session.md
    - Must exist and be non-empty
    - Must have no {{UNFILLED:}} placeholders
    - Must contain <phase1-input> section (Phase 1 reads this)
    """
    log("Verifying Phase 0 outputs...")
    return _check_file(research_folder, "00_brainstorm_session.md", "Phase 0",
                       check_unfilled=True, check_contains="<phase1-input>")


def verify_phase1_output(research_folder: str) -> bool:
    """
    Phase 1 primary outputs:
    - 01_targeted_research.md (compact output, required)
    - 01_targeted_research_full.md (full output, required)
    Both must be non-empty with no {{UNFILLED:}} placeholders.
    """
    log("Verifying Phase 1 outputs...")
    ok = True
    ok &= _check_file(research_folder, "01_targeted_research.md", "Phase 1",
                      check_unfilled=True)
    ok &= _check_file(research_folder, "01_targeted_research_full.md", "Phase 1",
                      check_unfilled=True)
    return ok


def verify_phase2a_output(research_folder: str) -> bool:
    """
    Phase 2A primary outputs (all required):
    - 03_refinement.yaml  (primary, used by Phase 2B)
    - 02_synthesis.yaml
    - 01_round_table/final_opinions.yaml
    - 03_refinement.md
    - discussion_log.md   (contains Final Assessments section)
    YAMLs must be non-empty. discussion_log must contain "Final Assessments".
    """
    log("Verifying Phase 2A outputs...")
    ok = True
    ok &= _check_file(research_folder, "03_refinement.yaml", "Phase 2A")
    ok &= _check_file(research_folder, "02_synthesis.yaml", "Phase 2A")
    ok &= _check_file(research_folder, "01_round_table/final_opinions.yaml", "Phase 2A")
    ok &= _check_file(research_folder, "03_refinement.md", "Phase 2A")
    ok &= _check_file(research_folder, "discussion_log.md", "Phase 2A",
                      check_contains="Final Assessments")
    return ok


def verify_phase2b_output(research_folder: str) -> bool:
    """
    Phase 2B primary outputs:
    - verification_state.yaml (critical — drives Phase 2C+ loop)
    - 02b_verification_plan.md (no {{UNFILLED:}} placeholders)
    """
    log("Verifying Phase 2B outputs...")
    ok = True
    ok &= _check_file(research_folder, "verification_state.yaml", "Phase 2B")
    ok &= _check_file(research_folder, "02b_verification_plan.md", "Phase 2B",
                      check_unfilled=True)
    return ok



# ============================================================
# Research Folder Detection
# ============================================================
def find_research_folder_after_phase0() -> str:
    """
    Find the research folder created by Phase 0.

    Search strategy (in order):
    1. docs/youra_research/ directly
    2. All subdirs of docs/youra_research/
    3. Project root — any immediate subdirectory containing 00_brainstorm_session.md
       (catches cases where Phase 0 creates a non-standard folder name)

    Returns the most recently modified folder containing 00_brainstorm_session.md,
    or None if not found.
    """
    candidates = []

    # Strategy 1 & 2: check docs/youra_research/ tree
    if RESEARCH_BASE.exists():
        if (RESEARCH_BASE / "00_brainstorm_session.md").exists():
            candidates.append(str(RESEARCH_BASE))
        for d in RESEARCH_BASE.iterdir():
            if d.is_dir() and (d / "00_brainstorm_session.md").exists():
                candidates.append(str(d))

    # Strategy 3: scan project root subdirs (one level deep)
    for d in PROJECT_DIR.iterdir():
        if d.is_dir() and not d.name.startswith(".") and (d / "00_brainstorm_session.md").exists():
            candidates.append(str(d))
        # Also check one level deeper
        if d.is_dir() and not d.name.startswith("."):
            for sub in d.iterdir():
                if sub.is_dir() and (sub / "00_brainstorm_session.md").exists():
                    candidates.append(str(sub))

    if not candidates:
        return None

    # Deduplicate and return most recently modified
    candidates = list(dict.fromkeys(candidates))
    return max(candidates, key=os.path.getmtime)




# ============================================================
# Retry Prompt Builders
# ============================================================
def _read_verify_json(phase: str) -> dict:
    """Read the verification JSON written by run_phase*.py."""
    json_path = CACHE_DIR / f"{phase}_output_verify.json"
    if not json_path.exists():
        return {}
    try:
        with open(json_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _format_verify_summary(data: dict) -> str:
    """Format verification JSON into a human-readable summary for the retry prompt."""
    if not data:
        return "  (no verification data available)"
    lines = []
    for c in data.get("checks", []):
        icon = "✓" if c.get("ok") else "✗"
        detail = []
        if not c.get("exists", True):
            detail.append("FILE MISSING")
        elif c.get("empty"):
            detail.append("EMPTY FILE")
        elif not c.get("no_unfilled", True):
            detail.append("has {{UNFILLED:}} placeholders")
        else:
            # find any False boolean field (contains_*)
            for k, v in c.items():
                if k not in ("file", "ok", "exists", "size", "no_unfilled") and v is False:
                    detail.append(f"{k}=False")
        suffix = f" — {', '.join(detail)}" if detail else f" ({c.get('size', 0)} bytes)"
        lines.append(f"  {icon} {c['file']}{suffix}")
    for e in data.get("errors", []):
        lines.append(f"  ! ERROR: {e}")
    return "\n".join(lines)


def build_retry_prompt_phase0(research_folder: str, verify_data: dict) -> str:
    summary = _format_verify_summary(verify_data)
    return f"""/phase0-brainstorm

#batch-mode

RETRY after incomplete execution. Research folder: {research_folder}

The previous run did not produce all required outputs.
Verification result:
{summary}

Please re-execute /phase0-brainstorm in Unattended mode.
- Output directory: {research_folder}
- Focus on completing the missing/incomplete files listed above
- Ensure 00_brainstorm_session.md is fully written with no {{{{UNFILLED:}}}} placeholders
- Ensure <phase1-input> section is present in the output
- Do NOT ask for user confirmation"""


def build_retry_prompt_phase1(research_folder: str, verify_data: dict) -> str:
    summary = _format_verify_summary(verify_data)
    return f"""/phase1-targeted

#batch-mode

RETRY after incomplete execution. Research folder: {research_folder}

The previous run did not produce all required outputs.
Verification result:
{summary}

Please re-execute /phase1-targeted in Unattended mode.
- Research folder: {research_folder}
- Focus on completing the missing/incomplete files listed above
- Ensure 01_targeted_research.md AND 01_targeted_research_full.md are fully written
- Ensure no {{{{UNFILLED:}}}} placeholders remain in either file
- At Step 9, auto-select [E] Exit to complete
- Do NOT ask for user confirmation"""


def build_retry_prompt_phase2a(research_folder: str, verify_data: dict) -> str:
    summary = _format_verify_summary(verify_data)
    return f"""/phase2a-dialogue

#batch-mode

RETRY after incomplete execution. Research folder: {research_folder}

The previous run did not produce all required outputs.
Verification result:
{summary}

Please re-execute /phase2a-dialogue in Unattended mode.
- Research folder: {research_folder}
- Focus on completing the missing/incomplete files listed above
- Required outputs: 03_refinement.yaml, 02_synthesis.yaml, 01_round_table/final_opinions.yaml, 03_refinement.md, discussion_log.md
- discussion_log.md must contain the "Final Assessments" section
- Do NOT ask for user confirmation — proceed through all steps without stopping"""


def build_retry_prompt_phase2b(research_folder: str, verify_data: dict) -> str:
    summary = _format_verify_summary(verify_data)
    return f"""/phase2b-planning

#batch-mode

RETRY after incomplete execution. Research folder: {research_folder}

The previous run did not produce all required outputs.
Verification result:
{summary}

Please re-execute /phase2b-planning in Unattended mode.
- Research folder: {research_folder}
- Focus on completing the missing/incomplete files listed above
- Required outputs: verification_state.yaml, 02b_verification_plan.md
- 02b_verification_plan.md must have no {{{{UNFILLED:}}}} placeholders
- When presented with any menu, automatically select [C] Continue
- Do NOT ask for user confirmation — proceed through all steps (Step 00–10)"""

# ============================================================
# Phase Runner
# ============================================================
def run_phase(
    script: Path,
    extra_args: list,
    phase_name: str,
    hard_timeout: int,
    output_log_name: str,
) -> int:
    """
    Run a phase launcher script as a subprocess.

    Each run_phase*.py manages its own:
      - active_phase.json  (tells hook_router which phase is active)
      - auto_responder_config.yaml enabled flag
      - phase*_auto_config.yaml  (LLM model, rate limits, completion signals)
      - phase*_responder.md  (GPT-5.2 system prompt with step-by-step instructions)

    This function only streams stdout/stderr and enforces a hard timeout
    (phase timeout + 60s buffer to allow clean shutdown).

    Returns: exit code (0 = success, non-zero = failure)
    """
    cmd = [sys.executable, str(script)] + extra_args

    log(f"Command: {' '.join(cmd)}")

    output_log = CACHE_DIR / output_log_name
    start_time = time.time()

    env = os.environ.copy()
    # Remove CLAUDECODE to allow nested Claude CLI invocations
    env.pop("CLAUDECODE", None)

    try:
        process = subprocess.Popen(
            cmd,
            cwd=str(PROJECT_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            env=env,
        )

        with open(output_log, "w", encoding="utf-8") as out_f:
            while True:
                # Hard timeout (phase timeout + buffer)
                elapsed = time.time() - start_time
                if elapsed > hard_timeout:
                    log(f"HARD TIMEOUT after {elapsed:.0f}s — killing {phase_name}")
                    process.terminate()
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        process.kill()
                    break

                ready, _, _ = select.select(
                    [process.stdout, process.stderr], [], [], 1.0
                )
                for stream in ready:
                    line = stream.readline()
                    if not line:
                        continue
                    out_f.write(line)
                    out_f.flush()
                    # Route stdout/stderr to same streams
                    if stream is process.stdout:
                        sys.stdout.write(line)
                        sys.stdout.flush()
                    else:
                        sys.stderr.write(line)
                        sys.stderr.flush()

                if process.poll() is not None:
                    # Drain remaining output after process exits
                    for line in process.stdout:
                        out_f.write(line)
                        out_f.flush()
                        sys.stdout.write(line)
                        sys.stdout.flush()
                    for line in process.stderr:
                        out_f.write(line)
                        out_f.flush()
                        sys.stderr.write(line)
                        sys.stderr.flush()
                    break

        exit_code = process.wait()
        elapsed = time.time() - start_time
        log(f"{phase_name} finished — exit code: {exit_code}, elapsed: {elapsed:.0f}s")
        return exit_code

    except FileNotFoundError:
        log(f"ERROR: Script not found: {script}")
        return 127
    except Exception as e:
        log(f"ERROR running {phase_name}: {e}")
        return 1




# ============================================================
# Phase Runner with Retry
# ============================================================
def run_phase_with_retry(
    script: Path,
    extra_args: list,
    phase_name: str,
    phase_key: str,
    hard_timeout: int,
    output_log_name: str,
    research_folder: str,
    verify_fn,
    retry_prompt_fn,
    retry_extra_args_fn,
) -> int:
    """
    Run a phase launcher, then verify outputs.
    On verification failure, retry up to MAX_RETRIES times with a corrective prompt.

    retry_extra_args_fn(retry_prompt) → list of extra args for the retry run
    """
    for attempt in range(1 + MAX_RETRIES):
        if attempt == 0:
            log(f"{phase_name} attempt 1/{1 + MAX_RETRIES}")
            args = extra_args
        else:
            # Read previous verify JSON and build retry prompt
            verify_data = _read_verify_json(phase_key)
            retry_prompt = retry_prompt_fn(research_folder, verify_data)
            log(f"{phase_name} RETRY {attempt}/{MAX_RETRIES} — injecting corrective prompt")
            args = retry_extra_args_fn(retry_prompt)

        exit_code = run_phase(
            script=script,
            extra_args=args,
            phase_name=f"{phase_name} (attempt {attempt + 1})",
            hard_timeout=hard_timeout,
            output_log_name=output_log_name,
        )

        if exit_code != 0:
            log(f"{phase_name} attempt {attempt + 1} exited with code {exit_code}")
            if attempt < MAX_RETRIES:
                log("Will retry...")
                continue
            return exit_code

        # Verify outputs
        if verify_fn(research_folder):
            log(f"{phase_name} verification PASSED on attempt {attempt + 1}")
            return 0
        else:
            log(f"{phase_name} verification FAILED on attempt {attempt + 1}")
            if attempt < MAX_RETRIES:
                log("Will retry with corrective prompt...")
            else:
                log(f"{phase_name} verification still FAILED after {1 + MAX_RETRIES} attempts")
                return 1

    return 1

# ============================================================
# Signal Handling
# ============================================================
def signal_handler(signum, frame):
    sig_name = signal.Signals(signum).name
    log(f"Received {sig_name} — aborting early pipeline")
    sys.exit(128 + signum)


# ============================================================
# Argument Parsing
# ============================================================
def parse_args():
    parser = argparse.ArgumentParser(
        description="Early Pipeline Runner — Phase 0 → 1 → 2A → 2B (unattended)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s docs/research_idea.md
  %(prog)s "Weak supervision for image classification"
  %(prog)s docs/research_idea.md --research-folder docs/youra_research/20260304_scsl
  %(prog)s docs/research_idea.md --timeout-phase0 1800 --timeout-phase2b 10800

After completion, run:
  python run_hypothesis_loop.py --research-folder <printed research folder>
        """,
    )

    parser.add_argument(
        "input",
        type=str,
        help="Phase 0 input: .md file path OR plain text topic string",
    )
    parser.add_argument(
        "--research-folder",
        type=str,
        default=None,
        help=(
            "Research folder path. Phase 0 writes output here; "
            "Phases 1/2A/2B read from here. "
            "(default: Phase 0 auto-creates a new timestamped folder)"
        ),
    )
    parser.add_argument(
        "--timeout-phase0",
        type=int,
        default=DEFAULT_TIMEOUTS["phase0"],
        help=f"Phase 0 timeout in seconds (default: {DEFAULT_TIMEOUTS['phase0']})",
    )
    parser.add_argument(
        "--timeout-phase1",
        type=int,
        default=DEFAULT_TIMEOUTS["phase1"],
        help=f"Phase 1 timeout in seconds (default: {DEFAULT_TIMEOUTS['phase1']})",
    )
    parser.add_argument(
        "--timeout-phase2a",
        type=int,
        default=DEFAULT_TIMEOUTS["phase2a"],
        help=f"Phase 2A timeout in seconds (default: {DEFAULT_TIMEOUTS['phase2a']})",
    )
    parser.add_argument(
        "--timeout-phase2b",
        type=int,
        default=DEFAULT_TIMEOUTS["phase2b"],
        help=f"Phase 2B timeout in seconds (default: {DEFAULT_TIMEOUTS['phase2b']})",
    )

    return parser.parse_args()


# ============================================================
# Main
# ============================================================
def main():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    args = parse_args()

    # Resolve explicitly provided research folder
    research_folder = None
    if args.research_folder:
        research_folder = str(Path(args.research_folder).resolve())
        os.makedirs(research_folder, exist_ok=True)

    print_banner("YouRA Early Pipeline Runner")
    log(f"Input: {args.input}")
    log(f"Research folder: {research_folder or 'AUTO (Phase 0 creates)'}")
    log(
        f"Timeouts — "
        f"Phase0: {args.timeout_phase0}s | "
        f"Phase1: {args.timeout_phase1}s | "
        f"Phase2A: {args.timeout_phase2a}s | "
        f"Phase2B: {args.timeout_phase2b}s"
    )

    # Validate launcher scripts exist before starting
    for name, path in [
        ("run_phase0.py", RUN_PHASE0),
        ("run_phase1.py", RUN_PHASE1),
        ("run_phase2a.py", RUN_PHASE2A),
        ("run_phase2b.py", RUN_PHASE2B),
    ]:
        if not path.exists():
            log(f"ERROR: {name} not found at {path}")
            sys.exit(1)

    pipeline_start = time.time()

    # ============================================================
    # Phase 0 — Brainstorm
    # ============================================================
    print_banner("Starting Phase 0 — Brainstorm")

    phase0_args = [args.input]
    if research_folder:
        phase0_args += ["--research-folder", research_folder]
    phase0_args += ["--timeout", str(args.timeout_phase0)]

    # Phase 0 runs first without retry (research_folder may not exist yet for retry prompt).
    # Retry is handled separately after folder detection.
    exit_code = run_phase(
        script=RUN_PHASE0,
        extra_args=phase0_args,
        phase_name="Phase 0 (attempt 1)",
        # +60s buffer: allows run_phase0.py cleanup() to finish after its own timeout fires
        hard_timeout=args.timeout_phase0 + 60,
        output_log_name="early_pipeline_phase0.log",
    )

    if exit_code != 0:
        log(f"Phase 0 FAILED with exit code {exit_code} — aborting pipeline")
        sys.exit(exit_code)

    log("Phase 0 COMPLETE")

    # Determine research folder for all subsequent phases.
    # run_phase0.py does NOT print it to stdout, so we auto-detect from filesystem.
    if not research_folder:
        research_folder = find_research_folder_after_phase0()
        if not research_folder:
            log("ERROR: Cannot locate research folder after Phase 0 — aborting")
            sys.exit(1)
        log(f"Auto-detected research folder: {research_folder}")
    else:
        log(f"Using provided research folder: {research_folder}")

    # Verify Phase 0; retry with corrective prompt if needed
    for _attempt in range(1 + MAX_RETRIES):
        if verify_phase0_output(research_folder):
            log(f"Phase 0 verification PASSED (attempt {_attempt + 1})")
            break
        if _attempt < MAX_RETRIES:
            log(f"Phase 0 verification FAILED — retrying ({_attempt + 1}/{MAX_RETRIES})")
            _verify_data = _read_verify_json("phase0")
            _retry_prompt = build_retry_prompt_phase0(research_folder, _verify_data)
            _retry_args = [args.input, "--research-folder", research_folder,
                           "--retry-prompt", _retry_prompt, "--timeout", str(args.timeout_phase0)]
            _rc = run_phase(RUN_PHASE0, _retry_args, f"Phase 0 (retry {_attempt + 1})",
                            args.timeout_phase0 + 60, "early_pipeline_phase0.log")
            if _rc != 0:
                log(f"Phase 0 retry {_attempt + 1} FAILED — aborting")
                sys.exit(_rc)
        else:
            log("Phase 0 verification FAILED after all retries — aborting pipeline")
            sys.exit(1)

    # ============================================================
    # Phase 1 — Targeted Research
    # ============================================================
    print_banner("Starting Phase 1 — Targeted Research")

    phase1_args = [
        "--research-folder", research_folder,
        "--timeout", str(args.timeout_phase1),
    ]

    exit_code = run_phase_with_retry(
        script=RUN_PHASE1,
        extra_args=phase1_args,
        phase_name="Phase 1",
        phase_key="phase1",
        hard_timeout=args.timeout_phase1 + 60,
        output_log_name="early_pipeline_phase1.log",
        research_folder=research_folder,
        verify_fn=verify_phase1_output,
        retry_prompt_fn=build_retry_prompt_phase1,
        retry_extra_args_fn=lambda p: [
            "--research-folder", research_folder,
            "--retry-prompt", p,
            "--timeout", str(args.timeout_phase1),
        ],
    )

    if exit_code != 0:
        log(f"Phase 1 FAILED — aborting pipeline")
        sys.exit(exit_code)

    log("Phase 1 COMPLETE")

    # ============================================================
    # Phase 2A — Hypothesis Dialogue
    # ============================================================
    print_banner("Starting Phase 2A — Hypothesis Dialogue")

    phase2a_args = [
        "--research-folder", research_folder,
        "--timeout", str(args.timeout_phase2a),
    ]

    exit_code = run_phase_with_retry(
        script=RUN_PHASE2A,
        extra_args=phase2a_args,
        phase_name="Phase 2A",
        phase_key="phase2a",
        hard_timeout=args.timeout_phase2a + 60,
        output_log_name="early_pipeline_phase2a.log",
        research_folder=research_folder,
        verify_fn=verify_phase2a_output,
        retry_prompt_fn=build_retry_prompt_phase2a,
        retry_extra_args_fn=lambda p: [
            "--research-folder", research_folder,
            "--retry-prompt", p,
            "--timeout", str(args.timeout_phase2a),
        ],
    )

    if exit_code != 0:
        log(f"Phase 2A FAILED — aborting pipeline")
        sys.exit(exit_code)

    log("Phase 2A COMPLETE")

    # ============================================================
    # Phase 2B — Verification Planning
    # ============================================================
    print_banner("Starting Phase 2B — Verification Planning")

    # Phase 2B hard-requires 03_refinement.yaml (Phase 2A primary output).
    # run_phase2b.py also checks this, but we check early for a clearer error message.
    refinement_yaml = Path(research_folder) / "03_refinement.yaml"
    if not refinement_yaml.exists():
        log(
            f"ERROR: 03_refinement.yaml not found in {research_folder}\n"
            f"  This is Phase 2A's primary output and is required by Phase 2B.\n"
            f"  Phase 2A may have completed with an error. Aborting."
        )
        sys.exit(1)

    phase2b_args = [
        "--research-folder", research_folder,
        "--timeout", str(args.timeout_phase2b),
    ]

    exit_code = run_phase_with_retry(
        script=RUN_PHASE2B,
        extra_args=phase2b_args,
        phase_name="Phase 2B",
        phase_key="phase2b",
        hard_timeout=args.timeout_phase2b + 60,
        output_log_name="early_pipeline_phase2b.log",
        research_folder=research_folder,
        verify_fn=verify_phase2b_output,
        retry_prompt_fn=build_retry_prompt_phase2b,
        retry_extra_args_fn=lambda p: [
            "--research-folder", research_folder,
            "--retry-prompt", p,
            "--timeout", str(args.timeout_phase2b),
        ],
    )

    if exit_code != 0:
        log(f"Phase 2B FAILED — aborting pipeline")
        sys.exit(exit_code)

    log("Phase 2B COMPLETE")

    # ============================================================
    # Done
    # ============================================================
    total_elapsed = time.time() - pipeline_start
    print_banner("Early Pipeline COMPLETE — Phase 0 → 1 → 2A → 2B")
    log(f"Total elapsed: {total_elapsed:.0f}s ({total_elapsed/60:.1f} min)")
    log(f"Research folder: {research_folder}")
    log(f"Next step: python run_hypothesis_loop.py --research-folder {research_folder}")

    # Print research folder to stdout for downstream scripting
    print(research_folder)
    sys.exit(0)


if __name__ == "__main__":
    main()
