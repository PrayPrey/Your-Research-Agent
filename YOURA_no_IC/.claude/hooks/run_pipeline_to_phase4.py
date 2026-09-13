#!/usr/bin/env python3
"""
Pipeline Runner — Phase 0 → 1 → 2A → 2B → Hypothesis Loop (Phase 2C → 3 → 4)

Orchestrates the full research pipeline from brainstorming to hypothesis validation.
Handles Reflection routing: when a MUST_WORK hypothesis fails (ROUTED), the pipeline
automatically restarts from the routed phase (Phase 0 or Phase 2A).

SELF_MODIFY is handled internally by run_hypothesis_loop.py and does NOT require
external intervention.

Reflection Flow:
  ┌──────────────────────────────────────────────────┐
  │  run_early_pipeline.py (Phase 0 → 1 → 2A → 2B)  │
  └───────────────────┬──────────────────────────────┘
                      ▼
  ┌──────────────────────────────────────────────────┐
  │  run_hypothesis_loop.py (Phase 2C → 3 → 4 × N)  │
  └───────────────────┬──────────────────────────────┘
                      ▼
  Exit code 0 (COMPLETE)  → Success, pipeline done
  Exit code 1 (ERROR)     → Fatal error, abort
  Exit code 2 (ROUTED)    → Parse route_to from stdout JSON
    → "Phase 0"            : Restart from run_early_pipeline.py
    → "Phase 2A-Dialogue"  : Restart from Phase 2A → 2B → hypothesis_loop
  Exit code 3 (INCOMPLETE) → No more READY hypotheses, abort

User-controlled reflection limit:
  --max-reflections 0   : No reflection (ROUTED → immediate exit)
  --max-reflections 3   : Up to 3 re-routes (default)
  --max-reflections -1  : Unlimited (until ERROR or COMPLETE)

Resume support:
  --resume-from phase2b   : Skip Phase 0/1/2A, start from Phase 2B
  --resume-from hypothesis-loop : Skip early pipeline, go directly to hypothesis loop
  Requires --research-folder when resuming from anything other than phase0.

Usage:
  python run_pipeline_to_phase4.py docs/research_idea.md
  python run_pipeline_to_phase4.py docs/research_idea.md --max-reflections 5
  python run_pipeline_to_phase4.py docs/research_idea.md \\
      --research-folder docs/youra_research/20260304_scsl \\
      --max-reflections 3 --timeout-hypothesis-loop 21600
  python run_pipeline_to_phase4.py docs/research_idea.md \\
      --resume-from phase2b --research-folder docs/youra_research/20260304_scsl

Exit codes:
  0 — All hypotheses validated (COMPLETE)
  1 — Fatal error
  2 — Reflection limit reached (still ROUTED)
  3 — Incomplete (BLOCKED/FAILED, no more READY)

Author: Anonymous
"""

import argparse
import json
import os
import select
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ============================================================
# Path Configuration
# ============================================================
SCRIPT_DIR = Path(__file__).parent
CACHE_DIR = SCRIPT_DIR / ".cache"
PROJECT_DIR = SCRIPT_DIR.parent.parent
AUTO_RESPONDER_CONFIG = SCRIPT_DIR / "auto_responder_config.yaml"

LOG_FILE = CACHE_DIR / "run_pipeline_to_phase4.log"

# Sub-scripts
RUN_EARLY_PIPELINE = SCRIPT_DIR / "run_early_pipeline.py"
RUN_HYPOTHESIS_LOOP = SCRIPT_DIR / "run_hypothesis_loop.py"


def _load_max_reflections_from_config() -> int:
    """Load max_reflections from auto_responder_config.yaml.

    Returns the configured value, or 3 as default.
    """
    try:
        import yaml
        if AUTO_RESPONDER_CONFIG.exists():
            with open(AUTO_RESPONDER_CONFIG, encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
            return int(cfg.get("pipeline_reflection", {}).get("max_reflections", 3))
    except Exception:
        pass
    return 3

# Individual phase launchers (for partial restart / resume)
RUN_PHASE0 = SCRIPT_DIR / "run_phase0.py"
RUN_PHASE1 = SCRIPT_DIR / "run_phase1.py"
RUN_PHASE2A = SCRIPT_DIR / "run_phase2a.py"
RUN_PHASE2B = SCRIPT_DIR / "run_phase2b.py"

# Valid resume points (ordered)
RESUME_POINTS = ["phase0", "phase1", "phase2a", "phase2b", "hypothesis-loop"]

REFLECTION_STATE_FILE = CACHE_DIR / "reflection_state.json"


def save_reflection_state(
    reflection_count: int,
    research_folder: str,
    last_routed_hypothesis: str = None,
    last_route_to: str = None,
    last_gate_result: str = None,
):
    """Persist reflection state so resume can continue where it left off."""
    state = {
        "reflection_count": reflection_count,
        "research_folder": research_folder,
        "last_routed_hypothesis": last_routed_hypothesis,
        "last_route_to": last_route_to,
        "last_gate_result": last_gate_result,
        "saved_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(REFLECTION_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        log(f"Reflection state saved: count={reflection_count}, folder={research_folder}")
    except Exception as e:
        log(f"WARNING: Failed to save reflection state: {e}")


def load_reflection_state(research_folder: str) -> int:
    """Load reflection_count from persisted state if it matches the research folder.

    Returns the saved reflection_count, or 0 if no matching state exists.
    """
    try:
        if REFLECTION_STATE_FILE.exists():
            with open(REFLECTION_STATE_FILE, encoding="utf-8") as f:
                state = json.load(f)
            saved_folder = state.get("research_folder", "")
            # Match by research folder to avoid cross-pipeline contamination
            if saved_folder and os.path.abspath(saved_folder) == os.path.abspath(research_folder):
                count = int(state.get("reflection_count", 0))
                log(f"Reflection state restored: count={count} (from {state.get('saved_at', '?')})")
                return count
            else:
                log(f"Reflection state exists but for different folder — starting from 0")
    except Exception as e:
        log(f"WARNING: Failed to load reflection state: {e}")
    return 0


# Default timeouts (seconds)
DEFAULT_TIMEOUTS = {
    "early_pipeline_phase0": 3600,
    "early_pipeline_phase1": 3600,
    "early_pipeline_phase2a": 5400,
    "early_pipeline_phase2b": 7200,
    "hypothesis_loop": 345600,  # 4 days; per-phase cap in run_hypothesis_loop.py still applies
    "phase2a": 5400,
    "phase2b": 7200,
}


# ============================================================
# Logging
# ============================================================
def log(message: str):
    """Log to file and stderr."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] [PIPELINE-TO-P4] {message}"
    print(entry, file=sys.stderr)
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except Exception:
        pass


def print_banner(text: str):
    """Print a visible section banner."""
    border = "=" * 70
    log(border)
    log(text)
    log(border)


# ============================================================
# Subprocess Runner (with stdout capture)
# ============================================================
def run_script(
    script: Path,
    extra_args: list,
    phase_name: str,
    hard_timeout: int,
    output_log_name: str,
) -> tuple:
    """
    Run a script as a subprocess.
    Streams output in real-time and captures stdout lines for JSON parsing.

    Returns: (exit_code: int, stdout_lines: list[str])
    """
    cmd = [sys.executable, str(script)] + extra_args

    log(f"Command: {' '.join(cmd)}")

    output_log = CACHE_DIR / output_log_name
    start_time = time.time()
    stdout_lines = []

    env = os.environ.copy()
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
                    if stream is process.stdout:
                        stdout_lines.append(line)
                        sys.stdout.write(line)
                        sys.stdout.flush()
                    else:
                        sys.stderr.write(line)
                        sys.stderr.flush()

                if process.poll() is not None:
                    for line in process.stdout:
                        stdout_lines.append(line)
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
        return exit_code, stdout_lines

    except FileNotFoundError:
        log(f"ERROR: Script not found: {script}")
        return 127, []
    except Exception as e:
        log(f"ERROR running {phase_name}: {e}")
        return 1, []


# ============================================================
# JSON Parsing from stdout
# ============================================================
def parse_last_json(stdout_lines: list) -> dict:
    """Parse the last JSON object from stdout lines.

    run_hypothesis_loop.py and run_early_pipeline.py both output
    a JSON object as the last line of stdout.
    """
    for line in reversed(stdout_lines):
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    return {}


# ============================================================
# Research Folder Detection
# ============================================================
RESEARCH_BASE = PROJECT_DIR / "docs" / "youra_research"


def find_research_folder() -> str:
    """Find the most recently modified research folder."""
    candidates = []

    if RESEARCH_BASE.exists():
        if (RESEARCH_BASE / "00_brainstorm_session.md").exists():
            candidates.append(str(RESEARCH_BASE))
        for d in RESEARCH_BASE.iterdir():
            if d.is_dir() and (d / "00_brainstorm_session.md").exists():
                candidates.append(str(d))

    for d in PROJECT_DIR.iterdir():
        if d.is_dir() and not d.name.startswith(".") and (d / "00_brainstorm_session.md").exists():
            candidates.append(str(d))
        if d.is_dir() and not d.name.startswith("."):
            for sub in d.iterdir():
                if sub.is_dir() and (sub / "00_brainstorm_session.md").exists():
                    candidates.append(str(sub))

    if not candidates:
        return None

    candidates = list(dict.fromkeys(candidates))
    return max(candidates, key=os.path.getmtime)


# ============================================================
# Phase Runners
# ============================================================
def run_early_pipeline(
    input_arg: str,
    research_folder: str,
    timeouts: dict,
) -> tuple:
    """Run Phase 0 → 1 → 2A → 2B via run_early_pipeline.py.

    Returns: (exit_code, research_folder_resolved)
    """
    print_banner("Early Pipeline — Phase 0 → 1 → 2A → 2B")

    args = [input_arg]
    if research_folder:
        args += ["--research-folder", research_folder]
    args += [
        "--timeout-phase0", str(timeouts.get("early_pipeline_phase0", DEFAULT_TIMEOUTS["early_pipeline_phase0"])),
        "--timeout-phase1", str(timeouts.get("early_pipeline_phase1", DEFAULT_TIMEOUTS["early_pipeline_phase1"])),
        "--timeout-phase2a", str(timeouts.get("early_pipeline_phase2a", DEFAULT_TIMEOUTS["early_pipeline_phase2a"])),
        "--timeout-phase2b", str(timeouts.get("early_pipeline_phase2b", DEFAULT_TIMEOUTS["early_pipeline_phase2b"])),
    ]

    # Total hard timeout = sum of all phase timeouts + buffer
    total_timeout = sum(
        timeouts.get(k, DEFAULT_TIMEOUTS[k])
        for k in ["early_pipeline_phase0", "early_pipeline_phase1",
                   "early_pipeline_phase2a", "early_pipeline_phase2b"]
    ) + 300  # 5 min buffer

    exit_code, stdout_lines = run_script(
        script=RUN_EARLY_PIPELINE,
        extra_args=args,
        phase_name="Early Pipeline",
        hard_timeout=total_timeout,
        output_log_name="pipeline_to_p4_early.log",
    )

    # run_early_pipeline.py prints research folder path as last stdout line
    resolved_folder = research_folder
    if exit_code == 0:
        for line in reversed(stdout_lines):
            line = line.strip()
            if line and not line.startswith("{") and not line.startswith("["):
                if os.path.isdir(line):
                    resolved_folder = line
                    break
        if not resolved_folder:
            resolved_folder = find_research_folder()

    return exit_code, resolved_folder


def run_partial_pipeline_from_phase2a(
    research_folder: str,
    timeouts: dict,
) -> int:
    """Run Phase 2A → 2B only (for ROUTED → Phase 2A restart).

    Returns: exit_code (0 = success)
    """
    print_banner("Partial Restart — Phase 2A → 2B")

    # Phase 2A
    log("Running Phase 2A...")
    phase2a_timeout = timeouts.get("phase2a", DEFAULT_TIMEOUTS["phase2a"])
    phase2a_args = [
        "--research-folder", research_folder,
        "--timeout", str(phase2a_timeout),
    ]
    exit_code, _ = run_script(
        script=RUN_PHASE2A,
        extra_args=phase2a_args,
        phase_name="Phase 2A (re-route)",
        hard_timeout=phase2a_timeout + 60,
        output_log_name="pipeline_to_p4_phase2a_reroute.log",
    )
    if exit_code != 0:
        log(f"Phase 2A (re-route) FAILED with exit code {exit_code}")
        return exit_code

    log("Phase 2A (re-route) COMPLETE")

    # Phase 2B
    log("Running Phase 2B...")
    phase2b_timeout = timeouts.get("phase2b", DEFAULT_TIMEOUTS["phase2b"])
    phase2b_args = [
        "--research-folder", research_folder,
        "--timeout", str(phase2b_timeout),
    ]
    exit_code, _ = run_script(
        script=RUN_PHASE2B,
        extra_args=phase2b_args,
        phase_name="Phase 2B (re-route)",
        hard_timeout=phase2b_timeout + 60,
        output_log_name="pipeline_to_p4_phase2b_reroute.log",
    )
    if exit_code != 0:
        log(f"Phase 2B (re-route) FAILED with exit code {exit_code}")
        return exit_code

    log("Phase 2B (re-route) COMPLETE")
    return 0


def run_hypothesis_loop(
    research_folder: str,
    timeout: int,
) -> tuple:
    """Run hypothesis loop (Phase 2C → 3 → 4 for each hypothesis).

    Returns: (exit_code, parsed_json_result)
    """
    print_banner("Hypothesis Loop — Phase 2C → 3 → 4")

    args = [
        "--research-folder", research_folder,
        "--timeout", str(timeout),
    ]

    exit_code, stdout_lines = run_script(
        script=RUN_HYPOTHESIS_LOOP,
        extra_args=args,
        phase_name="Hypothesis Loop",
        hard_timeout=timeout + 300,  # 5 min buffer
        output_log_name="pipeline_to_p4_hypothesis_loop.log",
    )

    result_json = parse_last_json(stdout_lines)
    return exit_code, result_json


# ============================================================
# Signal Handler
# ============================================================
def signal_handler(signum, _frame):
    sig_name = signal.Signals(signum).name
    log(f"Received {sig_name} — aborting pipeline")
    sys.exit(128 + signum)


# ============================================================
# CLI
# ============================================================
def parse_args():
    parser = argparse.ArgumentParser(
        description="Pipeline Runner — Phase 0 → 1 → 2A → 2B → Hypothesis Loop (2C → 3 → 4)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Reflection control:
  --max-reflections 0   No reflection (ROUTED → immediate exit)
  --max-reflections 3   Up to 3 re-routes (default)
  --max-reflections -1  Unlimited (until ERROR or COMPLETE)

Exit codes:
  0 — All hypotheses validated (COMPLETE)
  1 — Fatal error
  2 — Reflection limit reached (still ROUTED)
  3 — Incomplete (BLOCKED/FAILED)

Resume (--resume-from):
  phase0            Start from beginning (default)
  phase1            Skip Phase 0, start from Phase 1
  phase2a           Skip Phase 0/1, start from Phase 2A
  phase2b           Skip Phase 0/1/2A, start from Phase 2B
  hypothesis-loop   Skip early pipeline, go directly to hypothesis loop

Examples:
  %(prog)s docs/research_idea.md
  %(prog)s docs/research_idea.md --max-reflections 5
  %(prog)s docs/research_idea.md --research-folder docs/youra_research/20260304_scsl
  %(prog)s "Weak supervision for image classification" --max-reflections -1
  %(prog)s dummy --resume-from phase2b --research-folder docs/youra_research/20260304_scsl
  %(prog)s dummy --resume-from hypothesis-loop --research-folder docs/youra_research/20260304_scsl
        """,
    )

    parser.add_argument(
        "input", type=str,
        help="Phase 0 input: .md file path OR plain text topic string",
    )
    parser.add_argument(
        "--research-folder", type=str, default=None,
        help="Research folder path (default: Phase 0 auto-creates)",
    )
    parser.add_argument(
        "--resume-from", type=str, default=None,
        choices=RESUME_POINTS,
        help="Resume from a specific phase instead of starting from Phase 0. "
             "Requires --research-folder for anything other than phase0. "
             "Choices: phase0, phase1, phase2a, phase2b, hypothesis-loop",
    )
    config_max_reflections = _load_max_reflections_from_config()
    parser.add_argument(
        "--max-reflections", type=int, default=config_max_reflections,
        help=f"Max number of ROUTED re-routes allowed. 0=none, -1=unlimited "
             f"(default from config: {config_max_reflections})",
    )
    parser.add_argument(
        "--timeout-phase0", type=int, default=DEFAULT_TIMEOUTS["early_pipeline_phase0"],
        help=f"Phase 0 timeout in seconds (default: {DEFAULT_TIMEOUTS['early_pipeline_phase0']})",
    )
    parser.add_argument(
        "--timeout-phase1", type=int, default=DEFAULT_TIMEOUTS["early_pipeline_phase1"],
        help=f"Phase 1 timeout in seconds (default: {DEFAULT_TIMEOUTS['early_pipeline_phase1']})",
    )
    parser.add_argument(
        "--timeout-phase2a", type=int, default=DEFAULT_TIMEOUTS["early_pipeline_phase2a"],
        help=f"Phase 2A timeout in seconds (default: {DEFAULT_TIMEOUTS['early_pipeline_phase2a']})",
    )
    parser.add_argument(
        "--timeout-phase2b", type=int, default=DEFAULT_TIMEOUTS["early_pipeline_phase2b"],
        help=f"Phase 2B timeout in seconds (default: {DEFAULT_TIMEOUTS['early_pipeline_phase2b']})",
    )
    parser.add_argument(
        "--timeout-hypothesis-loop", type=int, default=DEFAULT_TIMEOUTS["hypothesis_loop"],
        help=f"Hypothesis loop timeout per phase in seconds (default: {DEFAULT_TIMEOUTS['hypothesis_loop']})",
    )

    return parser.parse_args()


# ============================================================
# Main
# ============================================================
def run_individual_phase(
    script: Path,
    research_folder: str,
    timeout: int,
    phase_name: str,
    log_name: str,
) -> int:
    """Run an individual phase script (Phase 1, 2A, or 2B).

    Returns: exit_code (0 = success)
    """
    print_banner(f"{phase_name} (individual)")

    phase_args = [
        "--research-folder", research_folder,
        "--timeout", str(timeout),
    ]

    exit_code, _ = run_script(
        script=script,
        extra_args=phase_args,
        phase_name=phase_name,
        hard_timeout=timeout + 60,
        output_log_name=log_name,
    )

    if exit_code != 0:
        log(f"{phase_name} FAILED with exit code {exit_code}")
    else:
        log(f"{phase_name} COMPLETE")

    return exit_code


def main():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    args = parse_args()

    resume_from = args.resume_from  # None or one of RESUME_POINTS

    research_folder = None
    if args.research_folder:
        research_folder = str(Path(args.research_folder).resolve())
        os.makedirs(research_folder, exist_ok=True)

    # --resume-from requires --research-folder (except phase0)
    if resume_from and resume_from != "phase0" and not research_folder:
        log("ERROR: --resume-from requires --research-folder (except phase0)")
        sys.exit(1)

    timeouts = {
        "early_pipeline_phase0": args.timeout_phase0,
        "early_pipeline_phase1": args.timeout_phase1,
        "early_pipeline_phase2a": args.timeout_phase2a,
        "early_pipeline_phase2b": args.timeout_phase2b,
        "hypothesis_loop": args.timeout_hypothesis_loop,
        "phase2a": args.timeout_phase2a,
        "phase2b": args.timeout_phase2b,
    }

    max_reflections = args.max_reflections
    pipeline_start = time.time()

    # Restore reflection_count from persisted state whenever a research
    # folder is known. We deliberately do NOT require --resume-from: any
    # invocation that targets the same research folder is, by definition,
    # continuing that folder's reflection flow. If reflection_state.json
    # exists but belongs to a different folder, load_reflection_state
    # returns 0 (no contamination).
    if research_folder:
        reflection_count = load_reflection_state(research_folder)
    else:
        reflection_count = 0

    resume_label = resume_from or "phase0 (full)"

    print_banner(
        f"Pipeline to Phase 4\n"
        f"  Input: {args.input}\n"
        f"  Research folder: {research_folder or 'AUTO'}\n"
        f"  Max reflections: {max_reflections if max_reflections >= 0 else 'unlimited'}\n"
        f"  Reflection count (restored): {reflection_count}\n"
        f"  Resume from: {resume_label}"
    )

    # Validate sub-scripts exist
    for name, path in [
        ("run_early_pipeline.py", RUN_EARLY_PIPELINE),
        ("run_hypothesis_loop.py", RUN_HYPOTHESIS_LOOP),
        ("run_phase0.py", RUN_PHASE0),
        ("run_phase1.py", RUN_PHASE1),
        ("run_phase2a.py", RUN_PHASE2A),
        ("run_phase2b.py", RUN_PHASE2B),
    ]:
        if not path.exists():
            log(f"ERROR: {name} not found at {path}")
            sys.exit(1)

    # ================================================================
    # Determine starting point
    # ================================================================
    resume_idx = RESUME_POINTS.index(resume_from) if resume_from else 0
    # 0=phase0, 1=phase1, 2=phase2a, 3=phase2b, 4=hypothesis-loop

    if resume_idx == 0:
        # Full early pipeline: Phase 0 → 1 → 2A → 2B
        exit_code, research_folder = run_early_pipeline(
            input_arg=args.input,
            research_folder=research_folder,
            timeouts=timeouts,
        )

        if exit_code != 0:
            log(f"Early pipeline FAILED (exit code {exit_code}) — aborting")
            sys.exit(exit_code)

    else:
        # Partial resume: run individual phases from resume_idx onward
        # Phases: 1=phase1, 2=phase2a, 3=phase2b, 4=hypothesis-loop
        individual_phases = [
            # (resume_idx, script, timeout_key, phase_name, log_name)
            (1, RUN_PHASE1, "early_pipeline_phase1", "Phase 1", "pipeline_to_p4_resume_phase1.log"),
            (2, RUN_PHASE2A, "early_pipeline_phase2a", "Phase 2A", "pipeline_to_p4_resume_phase2a.log"),
            (3, RUN_PHASE2B, "early_pipeline_phase2b", "Phase 2B", "pipeline_to_p4_resume_phase2b.log"),
        ]

        for idx, script, timeout_key, phase_name, log_name in individual_phases:
            if idx < resume_idx:
                log(f"SKIP: {phase_name} (resuming from {resume_from})")
                continue
            if idx >= 4:
                break  # hypothesis-loop handled separately below

            exit_code = run_individual_phase(
                script=script,
                research_folder=research_folder,
                timeout=timeouts[timeout_key],
                phase_name=phase_name,
                log_name=log_name,
            )

            if exit_code != 0:
                log(f"{phase_name} FAILED (exit code {exit_code}) — aborting")
                sys.exit(exit_code)

    if not research_folder:
        log("ERROR: Cannot determine research folder after early pipeline — aborting")
        sys.exit(1)

    log(f"Research folder resolved: {research_folder}")

    # ================================================================
    # Main reflection loop
    # ================================================================
    while True:
        # ---- Hypothesis Loop ----
        exit_code, result_json = run_hypothesis_loop(
            research_folder=research_folder,
            timeout=timeouts["hypothesis_loop"],
        )

        status = result_json.get("status", "UNKNOWN")
        log(f"Hypothesis loop result: status={status}, exit_code={exit_code}")

        # ---- Exit code 0: COMPLETE ----
        if exit_code == 0:
            total_elapsed = time.time() - pipeline_start
            print_banner("Pipeline to Phase 4 COMPLETE")
            log(f"Total elapsed: {total_elapsed:.0f}s ({total_elapsed / 60:.1f} min)")
            log(f"Total reflections used: {reflection_count}")
            log(f"Research folder: {research_folder}")

            # Clean up reflection state on success
            if REFLECTION_STATE_FILE.exists():
                try:
                    REFLECTION_STATE_FILE.unlink()
                    log("Reflection state file cleaned up")
                except Exception:
                    pass

            hypotheses = result_json.get("hypotheses", {})
            for h_id, h_info in hypotheses.items():
                log(f"  {h_id}: status={h_info.get('status')}, "
                    f"gate={h_info.get('gate_type')}, "
                    f"satisfied={h_info.get('gate_satisfied')}")

            print(json.dumps({
                "status": "COMPLETE",
                "research_folder": research_folder,
                "reflections_used": reflection_count,
                "total_elapsed_seconds": round(total_elapsed),
                "hypotheses": hypotheses,
            }, ensure_ascii=False))
            sys.exit(0)

        # ---- Exit code 1: ERROR ----
        if exit_code == 1:
            log(f"Hypothesis loop ERROR — aborting pipeline")
            print(json.dumps({
                "status": "ERROR",
                "reason": result_json.get("reason", "Hypothesis loop returned exit code 1"),
                "research_folder": research_folder,
                "reflections_used": reflection_count,
            }, ensure_ascii=False))
            sys.exit(1)

        # ---- Exit code 3: INCOMPLETE / BLOCKED ----
        if exit_code == 3:
            log(f"Hypothesis loop INCOMPLETE/BLOCKED — aborting pipeline")
            print(json.dumps({
                "status": status,
                "reason": result_json.get("reason", "No more READY hypotheses"),
                "research_folder": research_folder,
                "reflections_used": reflection_count,
                "hypotheses": result_json.get("hypotheses", {}),
            }, ensure_ascii=False))
            sys.exit(3)

        # ---- Exit code 2: ROUTED ----
        if exit_code == 2:
            route_to = result_json.get("route_to", "Phase 0")
            routed_hypothesis = result_json.get("hypothesis", "unknown")
            gate_result = result_json.get("gate_result", "unknown")

            log(f"ROUTED: {routed_hypothesis} → {route_to} (gate_result={gate_result})")

            # Check reflection limit
            if max_reflections >= 0 and reflection_count >= max_reflections:
                log(f"Reflection limit reached ({max_reflections}) — stopping pipeline")
                print(json.dumps({
                    "status": "REFLECTION_LIMIT_REACHED",
                    "route_to": route_to,
                    "hypothesis": routed_hypothesis,
                    "gate_result": gate_result,
                    "reflections_used": reflection_count,
                    "max_reflections": max_reflections,
                    "research_folder": research_folder,
                    "hypotheses": result_json.get("hypotheses", {}),
                }, ensure_ascii=False))
                sys.exit(2)

            reflection_count += 1
            log(f"Reflection {reflection_count}"
                f"{'/' + str(max_reflections) if max_reflections >= 0 else ' (unlimited)'}"
                f" — restarting from {route_to}")

            # Persist reflection state for resume
            save_reflection_state(
                reflection_count=reflection_count,
                research_folder=research_folder,
                last_routed_hypothesis=routed_hypothesis,
                last_route_to=route_to,
                last_gate_result=gate_result,
            )

            # ---- Route to Phase 0: full early pipeline restart ----
            if route_to == "Phase 0":
                print_banner(
                    f"Reflection {reflection_count} — Restarting from Phase 0\n"
                    f"  Triggered by: {routed_hypothesis} ({gate_result})"
                )

                exit_code, research_folder = run_early_pipeline(
                    input_arg=args.input,
                    research_folder=research_folder,
                    timeouts=timeouts,
                )

                if exit_code != 0:
                    log(f"Early pipeline (reflection) FAILED — aborting")
                    log(f"  Resume with: --resume-from phase0 --research-folder {research_folder}")
                    sys.exit(exit_code)

                if not research_folder:
                    log("ERROR: Cannot determine research folder after reflection — aborting")
                    sys.exit(1)

                # Loop continues → next iteration runs hypothesis_loop again

            # ---- Route to Phase 2A: partial restart ----
            elif route_to in ("Phase 2A-Dialogue", "Phase 2A"):
                print_banner(
                    f"Reflection {reflection_count} — Restarting from Phase 2A\n"
                    f"  Triggered by: {routed_hypothesis} ({gate_result})"
                )

                exit_code = run_partial_pipeline_from_phase2a(
                    research_folder=research_folder,
                    timeouts=timeouts,
                )

                if exit_code != 0:
                    log(f"Phase 2A/2B (reflection) FAILED — aborting")
                    log(f"  Resume with: --resume-from phase2a --research-folder {research_folder}")
                    sys.exit(exit_code)

                # Loop continues → next iteration runs hypothesis_loop again

            else:
                log(f"WARNING: Unknown route_to value: {route_to} — treating as Phase 0")
                print_banner(
                    f"Reflection {reflection_count} — Unknown route '{route_to}', "
                    f"falling back to Phase 0 restart"
                )

                exit_code, research_folder = run_early_pipeline(
                    input_arg=args.input,
                    research_folder=research_folder,
                    timeouts=timeouts,
                )

                if exit_code != 0:
                    log(f"Early pipeline (reflection fallback) FAILED — aborting")
                    log(f"  Resume with: --resume-from phase0 --research-folder {research_folder}")
                    sys.exit(exit_code)

                if not research_folder:
                    log("ERROR: Cannot determine research folder — aborting")
                    sys.exit(1)

            continue  # Next iteration of reflection loop

        # ---- Unexpected exit code ----
        log(f"Unexpected exit code {exit_code} from hypothesis loop — aborting")
        print(json.dumps({
            "status": "ERROR",
            "reason": f"Unexpected exit code: {exit_code}",
            "research_folder": research_folder,
            "reflections_used": reflection_count,
        }, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
