#!/usr/bin/env python3
"""
Post-Experiment Pipeline — Phase 4.5 → [Phase 5] → Phase 6 → Phase 6.5 → Phase 6.5.1

Runs the post-experiment phases sequentially after hypothesis validation completes.
Phase 5 (baseline comparison) is optional and skipped by default until implemented.

Pipeline:
  Phase 4.5   — Hypothesis Synthesis   (045_validated_hypothesis.md)
  Phase 5     — Baseline Comparison     (OPTIONAL, --enable-phase5)
  Phase 6     — Paper Writing           (06_paper.md)
  Phase 6.5   — Adversarial Review      (06_paper_final.md)
  Phase 6.5.1 — Overleaf LaTeX + PDF    (paper/overleaf/)
  Refine      — Paper Refinement        (OPTIONAL, --enable-refine)

Precondition:
  - Hypothesis loop must have completed (sub_hypotheses_complete = true)
  - verification_state.yaml and h-*/04_validation.md must exist

Resume support:
  --resume-from phase6    : Skip Phase 4.5/5, start from Phase 6
  --resume-from phase65   : Skip Phase 4.5/5/6, start from Phase 6.5
  --resume-from phase651  : Skip all earlier phases, start from Phase 6.5.1
  --resume-from refine    : Skip all earlier phases, start from Refine

Each phase verifies its prerequisites before starting. If a phase fails,
the pipeline stops and reports which phase failed.

Usage:
  python run_post_experiment.py --research-folder docs/youra_research/20260304_scsl
  python run_post_experiment.py --research-folder <path> --enable-phase5
  python run_post_experiment.py --research-folder <path> --timeout-phase45 7200
  python run_post_experiment.py --research-folder <path> --resume-from phase651
  python run_post_experiment.py --research-folder <path> --enable-refine

Exit codes:
  0 — All phases completed successfully
  1 — Fatal error (phase failure, missing prerequisites)

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

LOG_FILE = CACHE_DIR / "run_post_experiment.log"

# Phase launcher scripts
RUN_PHASE45 = SCRIPT_DIR / "run_phase45.py"
RUN_PHASE5 = SCRIPT_DIR / "run_phase5.py"  # Does not exist yet
RUN_PHASE6 = SCRIPT_DIR / "run_phase6.py"
RUN_PHASE65 = SCRIPT_DIR / "run_phase65.py"
RUN_PHASE651 = SCRIPT_DIR / "run_phase651.py"
RUN_PHASE_REFINE = SCRIPT_DIR / "run_phase_refine.py"

# Default timeouts (seconds)
DEFAULT_TIMEOUTS = {
    "phase45": 5400,
    "phase5": 7200,
    "phase6": 7200,
    "phase65": 7200,
    "phase651": 7200,
    "refine": 1800,
}

# Valid resume points (ordered)
POST_EXP_RESUME_POINTS = ["phase45", "phase5", "phase6", "phase65", "phase651", "refine"]


# ============================================================
# Logging
# ============================================================
def log(message: str):
    """Log to file and stderr."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] [POST-EXP] {message}"
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
# Prerequisite Checks
# ============================================================
def restore_from_archive(research_folder: str) -> bool:
    """Restore all files/folders from the most recent _archive entry back to research_folder.

    Called when reflection limit was reached after archive: the archive contains the last
    valid state before routing, which is exactly what Phase 4.5 needs.
    Moves every item inside the latest archive subfolder directly into research_folder.
    Returns True if restoration succeeded, False otherwise.
    """
    import shutil
    folder = Path(research_folder)
    archive_root = folder / "_archive"
    if not archive_root.exists():
        log("RESTORE: _archive/ not found — cannot restore")
        return False

    # Find most recent archive subfolder (sorted by name = timestamp prefix)
    archive_entries = sorted(
        [d for d in archive_root.iterdir() if d.is_dir()],
        key=lambda d: d.name,
        reverse=True,
    )
    if not archive_entries:
        log("RESTORE: No archive entries found")
        return False

    latest = archive_entries[0]
    log(f"RESTORE: Restoring all items from archive: {latest.name}")

    restored = 0
    for item in latest.iterdir():
        if item.name == "_ARCHIVED.md":
            continue
        dest = folder / item.name
        if dest.exists():
            log(f"RESTORE: {item.name} already exists in research_folder — skipping")
            continue
        shutil.move(str(item), str(dest))
        log(f"RESTORE: moved {item.name} → research_folder/")
        restored += 1

    log(f"RESTORE: {restored} item(s) restored from {latest.name}")
    return restored > 0


def check_phase45_prereqs(research_folder: str) -> bool:
    """Check Phase 4.5 prerequisites: verification_state.yaml + h-*/04_validation.md.

    If verification_state.yaml is missing (e.g. archived after reflection-limit routing),
    attempt to restore it from the most recent _archive entry before failing.
    """
    folder = Path(research_folder)

    vs = folder / "verification_state.yaml"
    if not vs.exists():
        log("WARNING: verification_state.yaml not found — attempting restore from _archive/")
        if restore_from_archive(research_folder):
            if not vs.exists():
                log("ERROR: verification_state.yaml still not found after restore")
                return False
            log("verification_state.yaml successfully restored from archive")
        else:
            log("ERROR: verification_state.yaml not found and restore failed")
            return False

    # At least one h-*/04_validation.md must exist (also check _archive/ in case Claude archived directly)
    validation_files = (
        list(folder.glob("h-*/04_validation.md"))
        or list(folder.glob("_archive/h-*/04_validation.md"))
        or list(folder.glob("_archive/*/h-*/04_validation.md"))
    )
    if not validation_files:
        log("ERROR: No h-*/04_validation.md files found — hypothesis loop must complete first")
        return False

    log(f"Phase 4.5 prerequisites OK: {len(validation_files)} validation file(s) found")
    return True


def check_phase6_prereqs(research_folder: str) -> bool:
    """Check Phase 6 prerequisites: 045_validated_hypothesis.md."""
    folder = Path(research_folder)

    vh = folder / "045_validated_hypothesis.md"
    if not vh.exists():
        log("ERROR: 045_validated_hypothesis.md not found — Phase 4.5 must complete first")
        return False

    log(f"Phase 6 prerequisites OK: 045_validated_hypothesis.md ({vh.stat().st_size} bytes)")
    return True


def check_phase65_prereqs(research_folder: str) -> bool:
    """Check Phase 6.5 prerequisites: paper/06_paper.md."""
    folder = Path(research_folder)

    paper = folder / "paper" / "06_paper.md"
    if not paper.exists():
        log("ERROR: paper/06_paper.md not found — Phase 6 must complete first")
        return False

    log(f"Phase 6.5 prerequisites OK: paper/06_paper.md ({paper.stat().st_size} bytes)")
    return True


def check_phase651_prereqs(research_folder: str) -> bool:
    """Check Phase 6.5.1 prerequisites: paper/06_paper_final.md."""
    folder = Path(research_folder)

    paper_final = folder / "paper" / "06_paper_final.md"
    if not paper_final.exists():
        log("ERROR: paper/06_paper_final.md not found — Phase 6.5 must complete first")
        return False

    log(f"Phase 6.5.1 prerequisites OK: paper/06_paper_final.md ({paper_final.stat().st_size} bytes)")
    return True


# ============================================================
# Subprocess Runner
# ============================================================
def run_script(
    script: Path,
    extra_args: list,
    phase_name: str,
    hard_timeout: int,
    output_log_name: str,
) -> int:
    """Run a phase script as subprocess. Returns exit code."""
    cmd = [sys.executable, str(script)] + extra_args

    log(f"Command: {' '.join(cmd)}")

    output_log = CACHE_DIR / output_log_name
    start_time = time.time()

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
                        sys.stdout.write(line)
                        sys.stdout.flush()
                    else:
                        sys.stderr.write(line)
                        sys.stderr.flush()

                if process.poll() is not None:
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
# Signal Handler
# ============================================================
def signal_handler(signum, _frame):
    sig_name = signal.Signals(signum).name
    log(f"Received {sig_name} — aborting post-experiment pipeline")
    sys.exit(128 + signum)


# ============================================================
# CLI
# ============================================================
def parse_args():
    parser = argparse.ArgumentParser(
        description="Post-Experiment Pipeline — Phase 4.5 → [5] → 6 → 6.5 → 6.5.1",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Phase 5 is skipped by default (not yet implemented).
Use --enable-phase5 to include it when run_phase5.py is available.

Exit codes:
  0 — All phases completed successfully
  1 — Fatal error (phase failure, missing prerequisites)

Examples:
  %(prog)s --research-folder docs/youra_research/20260304_scsl
  %(prog)s --research-folder <path> --enable-phase5
  %(prog)s --research-folder <path> --timeout-phase45 7200 --timeout-phase6 10800
        """,
    )

    parser.add_argument(
        "--research-folder", type=str, required=True,
        help="Research folder containing verification_state.yaml and h-*/04_validation.md",
    )
    parser.add_argument(
        "--resume-from", type=str, default=None,
        choices=POST_EXP_RESUME_POINTS,
        help="Resume from a specific phase. Choices: phase45, phase5, phase6, phase65, phase651",
    )
    parser.add_argument(
        "--enable-phase5", action="store_true", default=False,
        help="Enable Phase 5 (baseline comparison). Requires run_phase5.py to exist. (default: skip)",
    )
    parser.add_argument(
        "--enable-refine", action="store_true", default=False,
        help="Enable paper refinement after Phase 6.5.1. (default: skip)",
    )
    parser.add_argument(
        "--timeout-phase45", type=int, default=DEFAULT_TIMEOUTS["phase45"],
        help=f"Phase 4.5 timeout in seconds (default: {DEFAULT_TIMEOUTS['phase45']})",
    )
    parser.add_argument(
        "--timeout-phase5", type=int, default=DEFAULT_TIMEOUTS["phase5"],
        help=f"Phase 5 timeout in seconds (default: {DEFAULT_TIMEOUTS['phase5']})",
    )
    parser.add_argument(
        "--timeout-phase6", type=int, default=DEFAULT_TIMEOUTS["phase6"],
        help=f"Phase 6 timeout in seconds (default: {DEFAULT_TIMEOUTS['phase6']})",
    )
    parser.add_argument(
        "--timeout-phase65", type=int, default=DEFAULT_TIMEOUTS["phase65"],
        help=f"Phase 6.5 timeout in seconds (default: {DEFAULT_TIMEOUTS['phase65']})",
    )
    parser.add_argument(
        "--timeout-phase651", type=int, default=DEFAULT_TIMEOUTS["phase651"],
        help=f"Phase 6.5.1 timeout in seconds (default: {DEFAULT_TIMEOUTS['phase651']})",
    )
    parser.add_argument(
        "--timeout-refine", type=int, default=DEFAULT_TIMEOUTS["refine"],
        help=f"Refine timeout in seconds (default: {DEFAULT_TIMEOUTS['refine']})",
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

    research_folder = str(Path(args.research_folder).resolve())

    if not Path(research_folder).exists():
        log(f"ERROR: Research folder does not exist: {research_folder}")
        sys.exit(1)

    resume_from = args.resume_from  # None or one of POST_EXP_RESUME_POINTS
    resume_idx = POST_EXP_RESUME_POINTS.index(resume_from) if resume_from else 0
    # 0=phase45, 1=phase5, 2=phase6, 3=phase65

    # Determine pipeline phases
    all_phases = ["Phase 4.5", "Phase 6", "Phase 6.5", "Phase 6.5.1"]
    if args.enable_phase5:
        all_phases.insert(1, "Phase 5")
    if args.enable_refine:
        all_phases.append("Refine")

    resume_label = resume_from or "phase45 (full)"

    print_banner(
        f"Post-Experiment Pipeline\n"
        f"  Research folder: {research_folder}\n"
        f"  Phases: {' → '.join(all_phases)}\n"
        f"  Phase 5: {'ENABLED' if args.enable_phase5 else 'SKIPPED (not yet implemented)'}\n"
        f"  Resume from: {resume_label}"
    )

    # Validate required scripts exist
    required_scripts = [
        ("run_phase45.py", RUN_PHASE45),
        ("run_phase6.py", RUN_PHASE6),
        ("run_phase65.py", RUN_PHASE65),
        ("run_phase651.py", RUN_PHASE651),
    ]
    if args.enable_phase5:
        required_scripts.insert(1, ("run_phase5.py", RUN_PHASE5))
    if args.enable_refine:
        required_scripts.append(("run_phase_refine.py", RUN_PHASE_REFINE))

    for name, path in required_scripts:
        if not path.exists():
            log(f"ERROR: {name} not found at {path}")
            if name == "run_phase5.py":
                log("HINT: Phase 5 is not yet implemented. Remove --enable-phase5 to skip it.")
            sys.exit(1)

    pipeline_start = time.time()

    # Track which phases actually ran
    phases_completed = []

    # ================================================================
    # Phase 4.5 — Hypothesis Synthesis
    # ================================================================
    if resume_idx <= 0:  # phase45 or earlier
        print_banner("Phase 4.5 — Hypothesis Synthesis")

        if not check_phase45_prereqs(research_folder):
            log("Phase 4.5 prerequisites not met — aborting")
            sys.exit(1)

        exit_code = run_script(
            script=RUN_PHASE45,
            extra_args=[
                "--research-folder", research_folder,
                "--timeout", str(args.timeout_phase45),
            ],
            phase_name="Phase 4.5",
            hard_timeout=args.timeout_phase45 + 60,
            output_log_name="post_exp_phase45.log",
        )

        if exit_code != 0:
            log(f"Phase 4.5 FAILED (exit code {exit_code}) — aborting")
            sys.exit(1)

        log("Phase 4.5 COMPLETE")
        phases_completed.append("Phase 4.5")
    else:
        log("Phase 4.5 SKIPPED (resuming from later phase)")

    # ================================================================
    # Phase 5 — Baseline Comparison (OPTIONAL)
    # ================================================================
    if resume_idx <= 1:  # phase5 or earlier
        if args.enable_phase5:
            print_banner("Phase 5 — Baseline Comparison")

            exit_code = run_script(
                script=RUN_PHASE5,
                extra_args=[
                    "--research-folder", research_folder,
                    "--timeout", str(args.timeout_phase5),
                ],
                phase_name="Phase 5",
                hard_timeout=args.timeout_phase5 + 60,
                output_log_name="post_exp_phase5.log",
            )

            if exit_code != 0:
                log(f"Phase 5 FAILED (exit code {exit_code}) — aborting")
                sys.exit(1)

            log("Phase 5 COMPLETE")
            phases_completed.append("Phase 5")
        else:
            log("Phase 5 SKIPPED (not enabled)")
    else:
        log("Phase 5 SKIPPED (resuming from later phase)")

    # ================================================================
    # Phase 6 — Paper Writing
    # ================================================================
    if resume_idx <= 2:  # phase6 or earlier
        print_banner("Phase 6 — Paper Writing")

        if not check_phase6_prereqs(research_folder):
            log("Phase 6 prerequisites not met — aborting")
            sys.exit(1)

        exit_code = run_script(
            script=RUN_PHASE6,
            extra_args=[
                "--research-folder", research_folder,
                "--timeout", str(args.timeout_phase6),
            ],
            phase_name="Phase 6",
            hard_timeout=args.timeout_phase6 + 60,
            output_log_name="post_exp_phase6.log",
        )

        if exit_code != 0:
            log(f"Phase 6 FAILED (exit code {exit_code}) — aborting")
            sys.exit(1)

        log("Phase 6 COMPLETE")
        phases_completed.append("Phase 6")
    else:
        log("Phase 6 SKIPPED (resuming from later phase)")

    # ================================================================
    # Phase 6.5 — Adversarial Review
    # ================================================================
    if resume_idx <= 3:  # phase65 or earlier
        print_banner("Phase 6.5 — Adversarial Review")

        if not check_phase65_prereqs(research_folder):
            log("Phase 6.5 prerequisites not met — aborting")
            sys.exit(1)

        exit_code = run_script(
            script=RUN_PHASE65,
            extra_args=[
                "--research-folder", research_folder,
                "--timeout", str(args.timeout_phase65),
            ],
            phase_name="Phase 6.5",
            hard_timeout=args.timeout_phase65 + 60,
            output_log_name="post_exp_phase65.log",
        )

        if exit_code != 0:
            log(f"Phase 6.5 FAILED (exit code {exit_code}) — aborting")
            sys.exit(1)

        log("Phase 6.5 COMPLETE")
        phases_completed.append("Phase 6.5")
    else:
        log("Phase 6.5 SKIPPED (resuming from later phase)")

    # ================================================================
    # Phase 6.5.1 — Overleaf LaTeX + PDF
    # ================================================================
    # Phase 6.5.1 always runs (it's the last phase)
    print_banner("Phase 6.5.1 — Overleaf LaTeX + PDF")

    if not check_phase651_prereqs(research_folder):
        log("Phase 6.5.1 prerequisites not met — aborting")
        sys.exit(1)

    exit_code = run_script(
        script=RUN_PHASE651,
        extra_args=[
            "--research-folder", research_folder,
            "--timeout", str(args.timeout_phase651),
        ],
        phase_name="Phase 6.5.1",
        hard_timeout=args.timeout_phase651 + 60,
        output_log_name="post_exp_phase651.log",
    )

    if exit_code != 0:
        log(f"Phase 6.5.1 FAILED (exit code {exit_code}) — aborting")
        sys.exit(1)

    log("Phase 6.5.1 COMPLETE")
    phases_completed.append("Phase 6.5.1")

    # ================================================================
    # Refine — Paper Refinement (OPTIONAL)
    # ================================================================
    if resume_idx <= 5:  # refine or earlier
        if args.enable_refine:
            print_banner("Refine — Paper Refinement")

            # Prerequisite: same as Phase 6.5.1 (paper/06_paper_final.md)
            if not check_phase651_prereqs(research_folder):
                log("Refine prerequisites not met — skipping")
            else:
                exit_code = run_script(
                    script=RUN_PHASE_REFINE,
                    extra_args=[
                        "--research-folder", research_folder,
                        "--timeout", str(args.timeout_refine),
                    ],
                    phase_name="Refine",
                    hard_timeout=args.timeout_refine + 60,
                    output_log_name="post_exp_refine.log",
                )

                if exit_code != 0:
                    log(f"Refine FAILED (exit code {exit_code}) — continuing (non-fatal)")
                else:
                    log("Refine COMPLETE")
                    phases_completed.append("Refine")
        else:
            log("Refine SKIPPED (not enabled)")
    else:
        log("Refine SKIPPED (resuming from later phase)")

    # ================================================================
    # Done
    # ================================================================
    total_elapsed = time.time() - pipeline_start
    print_banner("Post-Experiment Pipeline COMPLETE")
    log(f"Total elapsed: {total_elapsed:.0f}s ({total_elapsed / 60:.1f} min)")
    log(f"Research folder: {research_folder}")
    log(f"Phases completed: {' → '.join(phases_completed)}")

    print(json.dumps({
        "status": "COMPLETE",
        "research_folder": research_folder,
        "phases_completed": phases_completed,
        "phase5_enabled": args.enable_phase5,
        "total_elapsed_seconds": round(total_elapsed),
    }, ensure_ascii=False))

    sys.exit(0)


if __name__ == "__main__":
    main()
