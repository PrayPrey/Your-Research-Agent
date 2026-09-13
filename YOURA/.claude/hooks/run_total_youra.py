#!/usr/bin/env python3
"""
YouRA Total Pipeline — Phase 0 → 1 → 2A → 2B → (2C → 3 → 4) × N → 4.5 → [5] → 6 → 6.5 → 6.5.1

End-to-end research pipeline from brainstorming to final reviewed paper + PDF.
Sequentially runs:

  1. run_pipeline_to_phase4.py  — Phase 0~2B + Hypothesis Loop (with Reflection)
  2. run_post_experiment.py     — Phase 4.5 → [5] → 6 → 6.5 → 6.5.1

The research folder resolved by run_pipeline_to_phase4.py is automatically
passed to run_post_experiment.py.

Resume support:
  --resume-from <phase>  : Resume from a specific phase instead of starting from Phase 0.
  Valid phases: phase0, phase1, phase2a, phase2b, hypothesis-loop,
                phase45, phase5, phase6, phase65, phase651
  Requires --research-folder for anything other than phase0.

Usage:
  python run_total_youra.py docs/research_idea.md
  python run_total_youra.py docs/research_idea.md --max-reflections 5
  python run_total_youra.py docs/research_idea.md --research-folder docs/youra_research/20260304_scsl
  python run_total_youra.py docs/research_idea.md --enable-phase5
  python run_total_youra.py docs/research_idea.md \\
      --max-reflections 3 --timeout-phase0 1800 --timeout-phase6 10800
  python run_total_youra.py dummy \\
      --resume-from phase2b --research-folder docs/youra_research/20260304_scsl
  python run_total_youra.py dummy \\
      --resume-from phase651 --research-folder docs/youra_research/20260304_scsl

Exit codes:
  0 — Full pipeline completed successfully
  1 — Fatal error
  2 — Reflection limit reached during hypothesis loop
  3 — Incomplete (hypothesis loop BLOCKED/FAILED)

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
REFLECTION_STATE_FILE = CACHE_DIR / "reflection_state.json"


def _cleanup_stale_reflection_state(research_folder: str | None, reason: str) -> None:
    """Remove reflection_state.json when we know its flow is no longer alive.

    Called when Part 1 is skipped (--resume-from points to a Part 2 phase):
    by definition the Part 1 reflection round is over, so the persisted state
    is stale. Without this, a stale count would silently bleed into the next
    fresh execution that happens to reuse the same research folder.
    """
    if not REFLECTION_STATE_FILE.exists():
        return
    try:
        with open(REFLECTION_STATE_FILE, encoding="utf-8") as f:
            saved = json.load(f)
        saved_folder = saved.get("research_folder", "")
        saved_count = saved.get("reflection_count", 0)
        REFLECTION_STATE_FILE.unlink()
        msg = (
            f"Cleaned stale reflection_state.json (count={saved_count}, "
            f"folder={saved_folder or '?'}) — reason: {reason}"
        )
        # Use stderr log helper if available; this runs before logger setup
        # in some edge paths, so fall back to print.
        try:
            log(msg)
        except NameError:
            print(f"[TOTAL] {msg}", file=sys.stderr)
    except Exception as e:
        try:
            log(f"WARNING: stale reflection_state cleanup failed: {e}")
        except NameError:
            pass
PROJECT_DIR = SCRIPT_DIR.parent.parent
AUTO_RESPONDER_CONFIG = SCRIPT_DIR / "auto_responder_config.yaml"


def _load_max_reflections_from_config() -> int:
    """Load max_reflections from auto_responder_config.yaml.

    Returns the configured value, or 10 as default.
    """
    try:
        import yaml
        if AUTO_RESPONDER_CONFIG.exists():
            with open(AUTO_RESPONDER_CONFIG, encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
            return int(cfg.get("pipeline_reflection", {}).get("max_reflections", 10))
    except Exception:
        pass
    return 10

LOG_FILE = CACHE_DIR / "run_total_youra.log"

RUN_PIPELINE_TO_PHASE4 = SCRIPT_DIR / "run_pipeline_to_phase4.py"
RUN_POST_EXPERIMENT = SCRIPT_DIR / "run_post_experiment.py"

# Valid resume points for run_total_youra.py (ordered)
# Part 1 phases are forwarded to run_pipeline_to_phase4.py via --resume-from
# Part 2 phases skip Part 1 entirely and start run_post_experiment.py at the right phase
PART1_RESUME_POINTS = ["phase0", "phase1", "phase2a", "phase2b", "hypothesis-loop"]
PART2_RESUME_POINTS = ["phase45", "phase5", "phase6", "phase65", "phase651", "refine"]
ALL_RESUME_POINTS = PART1_RESUME_POINTS + PART2_RESUME_POINTS

# Default timeouts (seconds)
DEFAULT_TIMEOUTS = {
    "phase0": 3600,
    "phase1": 3600,
    "phase2a": 5400,
    "phase2b": 7200,
    "hypothesis_loop": 345600,  # 4 days total budget for Phase 2C + 3 + 4 inside hypothesis loop (per-phase cap still enforced by PHASE_TIMEOUTS in run_hypothesis_loop.py)
    "phase45": 5400,
    "phase5": 7200,
    "phase6": 7200,
    "phase65": 14400,   # 4h, matches run_phase65.py standalone default
    "phase651": 7200,
    "refine": 1800,
}


# ============================================================
# Logging
# ============================================================
def log(message: str):
    """Log to file and stderr."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] [TOTAL] {message}"
    print(entry, file=sys.stderr)
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except Exception:
        pass


def print_banner(text: str):
    border = "#" * 70
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
    """Run a script as subprocess. Returns (exit_code, stdout_lines)."""
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


def parse_last_json(stdout_lines: list) -> dict:
    """Parse the last JSON object from stdout lines."""
    for line in reversed(stdout_lines):
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    return {}


# ============================================================
# Signal Handler
# ============================================================
def signal_handler(signum, _frame):
    sig_name = signal.Signals(signum).name
    log(f"Received {sig_name} — aborting total pipeline")
    sys.exit(128 + signum)


# ============================================================
# CLI
# ============================================================
def parse_args():
    parser = argparse.ArgumentParser(
        description="YouRA Total Pipeline — Phase 0 → ... → Phase 6.5.1 (end-to-end)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Runs the full YouRA pipeline:
  Part 1: run_pipeline_to_phase4.py (Phase 0 → 1 → 2A → 2B → Hypothesis Loop)
  Part 2: run_post_experiment.py    (Phase 4.5 → [5] → 6 → 6.5 → 6.5.1)

Exit codes:
  0 — Full pipeline completed
  1 — Fatal error
  2 — Reflection limit reached (Part 1)
  3 — Incomplete hypotheses (Part 1)

Resume (--resume-from):
  Part 1: phase0, phase1, phase2a, phase2b, hypothesis-loop
  Part 2: phase45, phase5, phase6, phase65, phase651

Examples:
  %(prog)s docs/research_idea.md
  %(prog)s docs/research_idea.md --max-reflections 5
  %(prog)s docs/research_idea.md --research-folder docs/youra_research/20260304_scsl
  %(prog)s docs/research_idea.md --enable-phase5 --timeout-phase6 10800
  %(prog)s dummy --resume-from phase2b --research-folder docs/youra_research/20260304_scsl
  %(prog)s dummy --resume-from phase45 --research-folder docs/youra_research/20260304_scsl
        """,
    )

    # Input
    parser.add_argument(
        "input", type=str,
        help="Phase 0 input: .md file path OR plain text topic string",
    )
    parser.add_argument(
        "--research-folder", type=str, default=None,
        help="Research folder path (default: Phase 0 auto-creates)",
    )

    # Resume control
    parser.add_argument(
        "--resume-from", type=str, default=None,
        choices=ALL_RESUME_POINTS,
        help="Resume from a specific phase. Requires --research-folder for anything "
             "other than phase0. Part 1 phases: phase0, phase1, phase2a, phase2b, "
             "hypothesis-loop. Part 2 phases: phase45, phase5, phase6, phase65, phase651.",
    )

    # Reflection control (Part 1)
    # Default is loaded from auto_responder_config.yaml → pipeline_reflection.max_reflections
    config_max_reflections = _load_max_reflections_from_config()
    parser.add_argument(
        "--max-reflections", type=int, default=config_max_reflections,
        help=f"Max ROUTED re-routes in hypothesis loop. 0=none, -1=unlimited "
             f"(default from config: {config_max_reflections})",
    )

    # Phase 5 control (Part 2)
    parser.add_argument(
        "--enable-phase5", action="store_true", default=False,
        help="Enable Phase 5 baseline comparison (default: skip)",
    )

    # Refine control (Part 2)
    parser.add_argument(
        "--enable-refine", action="store_true", default=False,
        help="Enable paper refinement after Phase 6.5.1 (default: skip)",
    )

    # Timeouts — Part 1
    parser.add_argument("--timeout-phase0", type=int, default=DEFAULT_TIMEOUTS["phase0"],
                        help=f"Phase 0 timeout (default: {DEFAULT_TIMEOUTS['phase0']}s)")
    parser.add_argument("--timeout-phase1", type=int, default=DEFAULT_TIMEOUTS["phase1"],
                        help=f"Phase 1 timeout (default: {DEFAULT_TIMEOUTS['phase1']}s)")
    parser.add_argument("--timeout-phase2a", type=int, default=DEFAULT_TIMEOUTS["phase2a"],
                        help=f"Phase 2A timeout (default: {DEFAULT_TIMEOUTS['phase2a']}s)")
    parser.add_argument("--timeout-phase2b", type=int, default=DEFAULT_TIMEOUTS["phase2b"],
                        help=f"Phase 2B timeout (default: {DEFAULT_TIMEOUTS['phase2b']}s)")
    parser.add_argument("--timeout-hypothesis-loop", type=int, default=DEFAULT_TIMEOUTS["hypothesis_loop"],
                        help=f"Hypothesis loop timeout per phase (default: {DEFAULT_TIMEOUTS['hypothesis_loop']}s)")

    # Timeouts — Part 2
    parser.add_argument("--timeout-phase45", type=int, default=DEFAULT_TIMEOUTS["phase45"],
                        help=f"Phase 4.5 timeout (default: {DEFAULT_TIMEOUTS['phase45']}s)")
    parser.add_argument("--timeout-phase5", type=int, default=DEFAULT_TIMEOUTS["phase5"],
                        help=f"Phase 5 timeout (default: {DEFAULT_TIMEOUTS['phase5']}s)")
    parser.add_argument("--timeout-phase6", type=int, default=DEFAULT_TIMEOUTS["phase6"],
                        help=f"Phase 6 timeout (default: {DEFAULT_TIMEOUTS['phase6']}s)")
    parser.add_argument("--timeout-phase65", type=int, default=DEFAULT_TIMEOUTS["phase65"],
                        help=f"Phase 6.5 timeout (default: {DEFAULT_TIMEOUTS['phase65']}s)")
    parser.add_argument("--timeout-phase651", type=int, default=DEFAULT_TIMEOUTS["phase651"],
                        help=f"Phase 6.5.1 timeout (default: {DEFAULT_TIMEOUTS['phase651']}s)")
    parser.add_argument("--timeout-refine", type=int, default=DEFAULT_TIMEOUTS["refine"],
                        help=f"Refine timeout (default: {DEFAULT_TIMEOUTS['refine']}s)")

    return parser.parse_args()


# ============================================================
# Main
# ============================================================
def main():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    args = parse_args()

    resume_from = args.resume_from  # None or one of ALL_RESUME_POINTS

    research_folder = None
    if args.research_folder:
        research_folder = str(Path(args.research_folder).resolve())
        os.makedirs(research_folder, exist_ok=True)

    # --resume-from requires --research-folder (except phase0)
    if resume_from and resume_from != "phase0" and not research_folder:
        log("ERROR: --resume-from requires --research-folder (except phase0)")
        sys.exit(1)

    # Validate scripts exist
    for name, path in [
        ("run_pipeline_to_phase4.py", RUN_PIPELINE_TO_PHASE4),
        ("run_post_experiment.py", RUN_POST_EXPERIMENT),
    ]:
        if not path.exists():
            log(f"ERROR: {name} not found at {path}")
            sys.exit(1)

    # Determine which parts to run
    skip_part1 = resume_from in PART2_RESUME_POINTS
    resume_part2_phase = resume_from if skip_part1 else None

    pipeline_start = time.time()
    resume_label = resume_from or "phase0 (full)"

    print_banner(
        f"YouRA Total Pipeline\n"
        f"  Input: {args.input}\n"
        f"  Research folder: {research_folder or 'AUTO'}\n"
        f"  Max reflections: {args.max_reflections if args.max_reflections >= 0 else 'unlimited'}\n"
        f"  Phase 5: {'ENABLED' if args.enable_phase5 else 'SKIPPED'}\n"
        f"  Refine: {'ENABLED' if args.enable_refine else 'SKIPPED'}\n"
        f"  Resume from: {resume_label}"
    )

    part1_result = {}

    # ================================================================
    # Part 1: run_pipeline_to_phase4.py
    #   Phase 0 → 1 → 2A → 2B → Hypothesis Loop (2C → 3 → 4) + Reflection
    # ================================================================
    if not skip_part1:
        print_banner("Part 1 — Phase 0 through Hypothesis Loop")

        part1_args = [
            args.input,
            "--max-reflections", str(args.max_reflections),
            "--timeout-phase0", str(args.timeout_phase0),
            "--timeout-phase1", str(args.timeout_phase1),
            "--timeout-phase2a", str(args.timeout_phase2a),
            "--timeout-phase2b", str(args.timeout_phase2b),
            "--timeout-hypothesis-loop", str(args.timeout_hypothesis_loop),
        ]
        if research_folder:
            part1_args += ["--research-folder", research_folder]

        # Forward --resume-from to Part 1 if it's a Part 1 phase.
        # Note: phase0 must also be forwarded so the child can restore
        # reflection_count from reflection_state.json. Previously this was
        # guarded by `resume_from != "phase0"`, which silently zeroed the
        # counter on README's own example flow.
        if resume_from and resume_from in PART1_RESUME_POINTS:
            part1_args += ["--resume-from", resume_from]

        # Hard timeout = sum of all Part 1 timeouts × (1 + max_reflections) + buffer
        base_part1_time = (
            args.timeout_phase0 + args.timeout_phase1 +
            args.timeout_phase2a + args.timeout_phase2b +
            args.timeout_hypothesis_loop
        )
        reflection_multiplier = max(1, args.max_reflections + 1) if args.max_reflections >= 0 else 10
        part1_hard_timeout = base_part1_time * reflection_multiplier + 600

        exit_code, stdout_lines = run_script(
            script=RUN_PIPELINE_TO_PHASE4,
            extra_args=part1_args,
            phase_name="Pipeline to Phase 4",
            hard_timeout=part1_hard_timeout,
            output_log_name="total_part1.log",
        )

        part1_result = parse_last_json(stdout_lines)
        part1_status = part1_result.get("status", "UNKNOWN")

        # Resolve research folder from Part 1 output
        if not research_folder:
            research_folder = part1_result.get("research_folder")

        if exit_code != 0:
            total_elapsed = time.time() - pipeline_start
            log(f"Part 1 FAILED — status={part1_status}, exit_code={exit_code}")

            # Exit code 2 = reflection limit reached, exit code 3 = incomplete (BLOCKED)
            # In both cases, proceed to Part 2 with whatever results are available
            if exit_code in (2, 3) and research_folder:
                log(f"Part 1 exit code {exit_code} — proceeding to Part 2 with partial results")
                log(f"  Status: {part1_status}")
                log(f"  Reflections used: {part1_result.get('reflections_used', 0)}")
                log(f"  Research folder: {research_folder}")
                # Fall through to Part 2 instead of exiting
            else:
                # Fatal error (exit code 1) or no research folder — abort
                print(json.dumps({
                    "status": part1_status,
                    "part": "pipeline_to_phase4",
                    "exit_code": exit_code,
                    "research_folder": research_folder,
                    "reflections_used": part1_result.get("reflections_used", 0),
                    "total_elapsed_seconds": round(total_elapsed),
                    "hypotheses": part1_result.get("hypotheses", {}),
                }, ensure_ascii=False))
                sys.exit(exit_code)
        else:
            part1_elapsed = time.time() - pipeline_start
            log(f"Part 1 COMPLETE — {part1_elapsed:.0f}s ({part1_elapsed / 60:.1f} min)")
            log(f"  Research folder: {research_folder}")
            log(f"  Reflections used: {part1_result.get('reflections_used', 0)}")

        if not research_folder:
            log("ERROR: Cannot determine research folder after Part 1 — aborting")
            sys.exit(1)
    else:
        log(f"Part 1 SKIPPED (resuming from {resume_from})")
        _cleanup_stale_reflection_state(
            research_folder,
            reason=f"Part 1 skipped via --resume-from {resume_from}",
        )

    # ================================================================
    # Part 2: run_post_experiment.py
    #   Phase 4.5 → [5] → 6 → 6.5 → 6.5.1
    # ================================================================
    print_banner("Part 2 — Phase 4.5 through Phase 6.5.1")

    part2_args = [
        "--research-folder", research_folder,
        "--timeout-phase45", str(args.timeout_phase45),
        "--timeout-phase5", str(args.timeout_phase5),
        "--timeout-phase6", str(args.timeout_phase6),
        "--timeout-phase65", str(args.timeout_phase65),
        "--timeout-phase651", str(args.timeout_phase651),
        "--timeout-refine", str(args.timeout_refine),
    ]
    if args.enable_phase5:
        part2_args.append("--enable-phase5")
    if args.enable_refine:
        part2_args.append("--enable-refine")

    # Forward --resume-from to Part 2 if it's a Part 2 phase
    if resume_part2_phase:
        part2_args += ["--resume-from", resume_part2_phase]

    part2_hard_timeout = (
        args.timeout_phase45 + args.timeout_phase6 + args.timeout_phase65
        + args.timeout_phase651 + 600
    )
    if args.enable_phase5:
        part2_hard_timeout += args.timeout_phase5
    if args.enable_refine:
        part2_hard_timeout += args.timeout_refine

    exit_code, stdout_lines = run_script(
        script=RUN_POST_EXPERIMENT,
        extra_args=part2_args,
        phase_name="Post-Experiment Pipeline",
        hard_timeout=part2_hard_timeout,
        output_log_name="total_part2.log",
    )

    part2_result = parse_last_json(stdout_lines)

    if exit_code != 0:
        total_elapsed = time.time() - pipeline_start
        log(f"Part 2 FAILED — exit_code={exit_code}")

        print(json.dumps({
            "status": "ERROR",
            "part": "post_experiment",
            "exit_code": exit_code,
            "research_folder": research_folder,
            "total_elapsed_seconds": round(total_elapsed),
        }, ensure_ascii=False))
        sys.exit(1)

    # ================================================================
    # Done
    # ================================================================
    total_elapsed = time.time() - pipeline_start

    print_banner(
        f"YouRA Total Pipeline COMPLETE\n"
        f"  Total time: {total_elapsed:.0f}s ({total_elapsed / 60:.1f} min)\n"
        f"  Research folder: {research_folder}\n"
        f"  Reflections used: {part1_result.get('reflections_used', 0)}\n"
        f"  Phase 5: {'included' if args.enable_phase5 else 'skipped'}\n"
        f"  Refine: {'included' if args.enable_refine else 'skipped'}"
    )

    print(json.dumps({
        "status": "COMPLETE",
        "research_folder": research_folder,
        "reflections_used": part1_result.get("reflections_used", 0),
        "phase5_enabled": args.enable_phase5,
        "total_elapsed_seconds": round(total_elapsed),
        "part1_hypotheses": part1_result.get("hypotheses", {}),
        "part2_phases": part2_result.get("phases_completed", []),
    }, ensure_ascii=False))

    sys.exit(0)


if __name__ == "__main__":
    main()
