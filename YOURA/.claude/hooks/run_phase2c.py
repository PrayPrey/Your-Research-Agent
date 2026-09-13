#!/usr/bin/env python3
"""
Phase 2C Launcher — Runs /phase2c-experiment-design Unattended

Launches Claude CLI with the /phase2c-experiment-design command for a specific
hypothesis. Configures the phase-specific auto-responder hook for fully
unattended execution.

Requires --research-folder and --hypothesis.

Phase 2C is an 8-step workflow (Step 01 ~ Step 08):
  Step 01: Init (hypothesis load, verification_state.yaml check)
  Step 02: Archon KB Search (past experiment cases)
  Step 03: Exa GitHub Search (implementation code)
  Step 04: Serena Codebase Analysis (optional)
  Step 05: Dataset & Baseline Design
  Step 06: Synthesis (experiment spec integration)
  Step 07: References (reference list compilation)
  Step 08: Validation (verification_state.yaml update)

Usage:
  python run_phase2c.py --research-folder docs/youra_research/20260304_scsl --hypothesis h-e1
  python run_phase2c.py --research-folder <path> --hypothesis h-e1 --timeout 3600

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
from timeout_policy import (
    log_timeout_marker, post_timeout_exit_code, core_artifacts_exist,
)

# ============================================================
# Path Configuration
# ============================================================
SCRIPT_DIR = Path(__file__).parent
CACHE_DIR = SCRIPT_DIR / ".cache"
ACTIVE_PHASE_FILE = CACHE_DIR / "active_phase.json"
PHASE_CONFIG_FILE = SCRIPT_DIR / "phase2c_auto_config.yaml"
AUTO_RESPONDER_CONFIG = SCRIPT_DIR / "auto_responder_config.yaml"
PROJECT_DIR = SCRIPT_DIR.parent.parent
CLAUDE_CLI = Path.home() / ".local" / "bin" / "claude"

LOG_FILE = CACHE_DIR / "run_phase2c.log"

MAX_BRIEF_VERIFY_RETRIES = 5


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
def validate_inputs(research_folder: str, hypothesis: str) -> dict:
    """Validate research folder and hypothesis prerequisites."""
    folder = Path(research_folder)
    result = {
        "valid": False,
        "files": [],
        "has_verification_state": False,
        "has_verification_plan": False,
    }

    if not folder.exists() or not folder.is_dir():
        log(f"ERROR: Research folder does not exist: {research_folder}")
        return result

    result["valid"] = True

    # Check verification_state.yaml (required)
    vs = folder / "verification_state.yaml"
    if vs.exists():
        result["has_verification_state"] = True
        result["files"].append(f"  - verification_state.yaml ({vs.stat().st_size} bytes)")

    # Check verification plan (from Phase 2B)
    vp = folder / "02b_verification_plan.md"
    if vp.exists():
        result["has_verification_plan"] = True
        result["files"].append(f"  - 02b_verification_plan.md ({vp.stat().st_size} bytes)")

    # Check hypothesis folder if exists
    h_folder = folder / hypothesis
    if h_folder.exists():
        for fname in h_folder.iterdir():
            if fname.is_file():
                result["files"].append(f"  - {hypothesis}/{fname.name} ({fname.stat().st_size} bytes)")

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


def create_active_phase(research_folder: str = None, hypothesis: str = None):
    """Create .cache/active_phase.json for hook routing."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    phase_info = {
        "phase": "phase2c",
        "enabled": True,
        "config_file": str(PHASE_CONFIG_FILE),
        "pid": os.getpid(),
        "started_at": datetime.now().isoformat(),
        "research_folder": research_folder or "",
        "hypothesis": hypothesis or "",
    }

    with open(ACTIVE_PHASE_FILE, "w", encoding="utf-8") as f:
        json.dump(phase_info, f, indent=2)

    log(f"Created active_phase.json: phase=phase2c, pid={os.getpid()}, research_folder={research_folder or 'NONE'}")


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
def build_phase2c_prompt(research_folder: str, hypothesis: str, validation: dict) -> str:
    """Build the initial prompt for Phase 2C unattended execution."""
    files_str = "\n".join(validation["files"]) if validation["files"] else "  (no files found)"

    prompt = f"""/phase2c-experiment-design

#batch-mode

Proceed in Unattended mode. Research folder is located at:

  {research_folder}

Target hypothesis: {hypothesis}

Available files:
{files_str}

Execute all Phase 2C steps automatically for hypothesis {hypothesis}.
Do NOT ask for user confirmation — proceed through all steps (Step 01 through Step 08) without stopping.
IMPORTANT: When you have completed all tasks, STOP IMMEDIATELY. Do NOT wait for further instructions.
Do NOT say "Awaiting further instructions" — just stop. The pipeline will continue automatically.

Key instructions:
- Load hypothesis {hypothesis} from verification_state.yaml
- Search Archon KB for past experiment cases
- Search Exa for implementation code examples
- Analyze codebase with Serena (if applicable)
- Design dataset preparation and baseline experiments
- Synthesize experiment specification into 02c_experiment_brief.md
- Update verification_state.yaml with experiment_design.status = "COMPLETED"
- When presented with any menu, automatically select [C] Continue

Experiment scale guidance:
- Do NOT design experiments with trivially small sample sizes (e.g., 10-50 samples)
- Use statistically meaningful sample counts: full standard test sets or at minimum 500+ evaluation samples
- Prefer standard dataset splits (full train/val/test) over arbitrary small subsets

Synthetic data policy (CRITICAL):
- Do NOT use synthetic/simulated datasets (Type: synthetic) for experiment design
- Always use real, established datasets (standard, custom, or programmatic-api)
- If the hypothesis seems to require synthetic data, find a real dataset that can test the same hypothesis
- Acceptable types: standard (CIFAR, MNIST, etc.), custom (real user-provided data), programmatic-api (real data via API)
- If no real dataset exists for this hypothesis, document the limitation and FAIL the experiment design
- Experiments with synthetic data produce meaningless results (e.g., completing in <1 second with simulated metrics)"""

    return prompt


# ============================================================
# Experiment Brief Verification (External Claude Session)
# ============================================================

def build_experiment_brief_verification_prompt(research_folder: str, hypothesis: str) -> str:
    """Build prompt for a separate Claude session to verify experiment brief for
    synthetic data plans and tautological experiment design.

    Unlike Phase 4's mock verification (which checks code), this checks the
    DESIGN DOCUMENT (02c_experiment_brief.md) before any code is written.
    """
    brief_path = Path(research_folder) / hypothesis / "02c_experiment_brief.md"

    return f"""#batch-mode

You are an Experiment Design Verification agent. Your ONLY job is to determine whether
the experiment brief plans to use REAL data or falls back to synthetic/simulated data,
and whether the experiment design is tautological (guaranteed to succeed by construction).

## File to Check

Read: {brief_path}

## What Counts as Synthetic Data Violation

- Dataset Type listed as: synthetic, simulated, generated, artificial, mock
- Dataset Name containing "simulated", "synthetic", "generated", "mock"
- Loading method that generates data via np.random, torch.randn, or similar instead of downloading/loading real data
- "PoC only" or "placeholder" dataset descriptions where data is constructed programmatically
- Custom dataset classes that generate trajectories/samples from parametric distributions
- ANY dataset where all samples are produced by code rather than collected from real-world sources

## What Counts as Tautological Design Violation

- Expected results are embedded in the dataset generation parameters (e.g., hard-coded bonus values that guarantee effect sizes)
- Experiment cannot fail because data is constructed to match the hypothesis
- Metrics are computed from the same synthetic process that generates data
- Control and experimental conditions are designed with different hard-coded parameters that guarantee specific outcomes
- The hypothesis is "tested" by generating data that already encodes the answer
- Evaluation metrics will trivially pass because the data generation process ensures they must

## What is NOT a Violation

- Using a real, established benchmark dataset (CIFAR, MNIST, WikiText, TruthfulQA, etc.)
- Using a smaller subset of a real dataset (subsampling is fine)
- Using a proxy real dataset when the ideal one is unavailable
- Data augmentation applied to real data
- Real datasets obtained via API (HuggingFace, Kaggle, etc.)
- Standard train/val/test splits of real data

## Output

After reading the experiment brief, output EXACTLY one JSON block (no other text before or after):

```json
{{
  "synthetic_detected": true or false,
  "tautological_detected": true or false,
  "confidence": "HIGH" or "MEDIUM" or "LOW",
  "dataset_name": "name of dataset from brief",
  "dataset_type": "type from brief (standard/custom/synthetic/etc.)",
  "reasoning": "1-2 sentence explanation",
  "violations": ["description of each issue found"]
}}
```

If neither synthetic nor tautological issues are found, both should be false and violations should be an empty list.
Do NOT output anything other than the JSON block."""


def run_experiment_brief_verification(
    research_folder: str, hypothesis: str, timeout: int = 300,
) -> dict:
    """Run a separate Claude session to verify experiment brief for synthetic data.

    Returns dict with synthetic_detected, tautological_detected, confidence, etc.
    Returns {"synthetic_detected": False, "skipped": True} if brief doesn't exist.
    """
    brief_path = Path(research_folder) / hypothesis / "02c_experiment_brief.md"
    if not brief_path.exists():
        log(f"Brief verification: no 02c_experiment_brief.md for {hypothesis} — skipping")
        return {"synthetic_detected": False, "tautological_detected": False, "skipped": True}

    prompt = build_experiment_brief_verification_prompt(research_folder, hypothesis)
    log_file = CACHE_DIR / f"phase2c_{hypothesis}_brief_verify.log"

    log(f"Running experiment brief verification for {hypothesis} (timeout={timeout}s)")
    exit_code = _run_claude(prompt, timeout, log_file)
    log(f"Brief verification exited with code {exit_code}")

    # Parse JSON from output log
    result = {"synthetic_detected": False, "tautological_detected": False, "parse_error": True}
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Find LAST JSON block (between ```json and ```)
        import re as _re
        all_matches = _re.findall(r'```json\s*\n(.*?)\n\s*```', content, _re.DOTALL)
        if all_matches:
            result = json.loads(all_matches[-1])
        else:
            # Try raw JSON
            all_matches = _re.findall(
                r'\{[^{}]*"synthetic_detected"[^{}]*\}', content, _re.DOTALL
            )
            if all_matches:
                result = json.loads(all_matches[-1])
            else:
                log("WARNING: Could not parse brief verification JSON output")
                return {"synthetic_detected": False, "tautological_detected": False, "parse_error": True}

        result.pop("parse_error", None)
    except Exception as e:
        log(f"WARNING: Brief verification parse error: {e}")
        return {"synthetic_detected": False, "tautological_detected": False, "parse_error": True}

    log(f"Brief verification result: synthetic={result.get('synthetic_detected')}, "
        f"tautological={result.get('tautological_detected')}, "
        f"confidence={result.get('confidence')}, "
        f"violations={len(result.get('violations', []))}")
    return result


def build_experiment_brief_fix_prompt(
    research_folder: str,
    hypothesis: str,
    validation: dict,
    verify_result: dict,
    attempt: int,
) -> str:
    """Build a corrective prompt to fix synthetic data in experiment brief.

    Tells Claude to re-run phase2c and replace the synthetic dataset with a real one.
    """
    files_str = "\n".join(validation["files"]) if validation["files"] else "  (no files found)"
    violations = verify_result.get("violations", [])
    violations_str = "\n".join(f"  - {v}" for v in violations) if violations else "  (no specific violations listed)"
    dataset_name = verify_result.get("dataset_name", "unknown")
    dataset_type = verify_result.get("dataset_type", "unknown")
    reasoning = verify_result.get("reasoning", "")
    synthetic = verify_result.get("synthetic_detected", False)
    tautological = verify_result.get("tautological_detected", False)

    issue_type = []
    if synthetic:
        issue_type.append("SYNTHETIC DATA")
    if tautological:
        issue_type.append("TAUTOLOGICAL DESIGN")
    issue_label = " + ".join(issue_type) or "DESIGN ISSUE"

    return f"""/phase2c-experiment-design

#batch-mode

## {issue_label} FIX — Attempt {attempt}/{MAX_BRIEF_VERIFY_RETRIES}

CRITICAL: External verification detected issues in the experiment brief.
You MUST fix the 02c_experiment_brief.md file.

### Verification Result
- Synthetic data detected: {synthetic}
- Tautological design detected: {tautological}
- Current dataset: {dataset_name} (type: {dataset_type})
- Reasoning: {reasoning}

### Violations Found
{violations_str}

### What You Must Do
1. Read the current 02c_experiment_brief.md at: {research_folder}/{hypothesis}/02c_experiment_brief.md
2. Search Archon KB for real benchmark datasets that can test this hypothesis
3. Search Exa for real datasets used in similar published experiments
4. REPLACE the synthetic/simulated dataset with a REAL, established dataset:
   - Acceptable types: standard (benchmark), custom (real collected), programmatic-api (real data via API)
   - NOT acceptable: synthetic, simulated, generated, mock, artificial
5. Ensure the experiment design is NOT tautological:
   - Results must NOT be guaranteed by the data generation process
   - Control vs experimental comparison must use the SAME real dataset
   - Metrics must be measurable from real experimental outcomes
6. Update the Dataset section of 02c_experiment_brief.md with:
   - Real dataset name, source, and loading code
   - dataset_type: standard, custom, or programmatic-api (NOT synthetic)
7. If absolutely no real dataset exists, set dataset_type to FAILED_NO_REAL_DATA
8. Do NOT regenerate the entire brief — only fix the Dataset section and related parts

Research folder: {research_folder}
Hypothesis: {hypothesis}

Available files:
{files_str}

Do NOT ask for user confirmation — proceed through all steps without stopping.
When presented with any menu, automatically select [C] Continue.
IMPORTANT: When you have completed all tasks, STOP IMMEDIATELY. Do NOT wait for further instructions.
Do NOT say "Awaiting further instructions" — just stop. The pipeline will continue automatically."""


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
        description="Phase 2C Launcher — Run /phase2c-experiment-design unattended",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --research-folder docs/youra_research/20260304_scsl --hypothesis h-e1
  %(prog)s --research-folder /absolute/path --hypothesis h-e1 --timeout 3600
        """,
    )

    parser.add_argument("--research-folder", type=str, required=True,
                        help="Path to research folder containing verification_state.yaml")
    parser.add_argument("--hypothesis", type=str, required=True,
                        help="Hypothesis ID to process (e.g., h-e1)")
    parser.add_argument("--timeout", type=int, default=3600,
                        help="Max runtime in seconds (default: 3600 = 1 hour)")

    return parser.parse_args()


def _set_proc(p):
    global _claude_process
    _claude_process = p


def _run_claude(prompt: str, timeout: int, output_log) -> int:
    """Launch Claude CLI with retry on transient API overload (5xx/Overloaded).

    Delegates to claude_runner.run_claude_with_retry. Monitors phase2c
    PHASE_COMPLETE lock to force-terminate stragglers.
    """
    from claude_runner import run_claude_with_retry
    return run_claude_with_retry(
        claude_cli=CLAUDE_CLI,
        project_dir=PROJECT_DIR,
        cache_dir=CACHE_DIR,
        prompt=prompt,
        timeout=timeout,
        output_log=output_log,
        phase_name="phase2c",
        log_fn=log,
        process_setter=_set_proc,
        echo_to_stdout=True,
        monitor_complete_lock=True,
        lock_grace_period=60,
    )


def _check_passed(phase: str, h_id: str) -> bool:
    import json as _json
    p = CACHE_DIR / f"{phase}_{h_id}_output_verify.json"
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
    clear_must_stop()  # Clear any stale MUST_STOP flag from previous run
    clear_phase_complete_lock("phase2c")  # Clear any stale PHASE_COMPLETE lock from previous run

    research_folder = str(Path(args.research_folder).resolve())

    validation = validate_inputs(research_folder, args.hypothesis)

    log("=" * 60)
    log("Phase 2C Launcher starting")
    log(f"  Research folder: {research_folder}")
    log(f"  Hypothesis: {args.hypothesis}")
    log(f"  Folder valid: {validation['valid']}")
    log(f"  Has verification_state.yaml: {validation['has_verification_state']}")
    log(f"  Timeout: {args.timeout}s")
    log("=" * 60)

    if not validation["valid"]:
        log("ERROR: Research folder does not exist. Aborting.")
        sys.exit(1)

    if not validation["has_verification_state"]:
        log("ERROR: verification_state.yaml not found. Aborting.")
        sys.exit(1)

    # Register cleanup
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Step 1: Enable auto_responder_config
    set_auto_responder_enabled(True)

    # Step 2: Create active_phase.json (include research_folder for snapshot-based diff)
    create_active_phase(research_folder=research_folder, hypothesis=args.hypothesis)

    # Step 3: Build prompt and launch Claude CLI
    prompt = build_phase2c_prompt(research_folder, args.hypothesis, validation)

    log(f"Launching Claude CLI with prompt ({len(prompt)} chars)")

    output_log = CACHE_DIR / f"phase2c_{args.hypothesis}_output.log"
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
            phase_name="phase2c",
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
        log_timeout_marker(log, "phase2c", elapsed,
                           attempt="initial",
                           hypothesis_id=args.hypothesis)

    # Option C: if the initial Claude session hit args.timeout, skip retry +
    # brief-fix and let the orchestrator decide based on core artifacts.
    if main_timed_out:
        cleanup()
        rc = post_timeout_exit_code(research_folder, "phase2c", log,
                                    hypothesis_id=args.hypothesis)
        print(research_folder)
        sys.exit(rc)

    # Check for MUST_STOP signal from hook (fatal error — abort immediately)
    must_stop_reason = check_must_stop()
    if must_stop_reason:
        log(f"MUST_STOP detected — aborting phase2c: {must_stop_reason}")
        cleanup()
        sys.exit(1)

    # Verify outputs; retry with corrective prompt if needed
    verify_and_write_json("phase2c", research_folder, exit_code, hypothesis_id=args.hypothesis)
    clear_phase_complete_lock("phase2c")  # Clear lock so retry session is not immediately approved
    for _attempt in range(MAX_RETRIES):
        if exit_code != 0 or _check_passed("phase2c", args.hypothesis):
            break
        log(f"Phase 2C verification FAILED — retry {_attempt + 1}/{MAX_RETRIES}")
        _retry_prompt = build_retry_prompt("phase2c", research_folder, hypothesis_id=args.hypothesis)
        exit_code = _run_claude(_retry_prompt, args.timeout,
                                CACHE_DIR / f"phase2c_{args.hypothesis}_output.log")
        if exit_code == 124:
            log("phase2c: retry timed out — skipping brief verification")
            cleanup()
            rc = post_timeout_exit_code(research_folder, "phase2c", log,
                                        hypothesis_id=args.hypothesis)
            print(research_folder)
            sys.exit(rc)
        must_stop_reason = check_must_stop()
        if must_stop_reason:
            log(f"MUST_STOP during retry — aborting phase2c: {must_stop_reason}")
            exit_code = 1
            break
        verify_and_write_json("phase2c", research_folder, exit_code, hypothesis_id=args.hypothesis)

    # ---- EXPERIMENT BRIEF VERIFICATION (separate Claude session) ----
    log("=" * 60)
    log("Experiment Brief Verification — starting external LLM check")
    log("=" * 60)

    verify_result = run_experiment_brief_verification(
        research_folder, args.hypothesis, timeout=300
    )

    detected = (
        verify_result.get("synthetic_detected") or verify_result.get("tautological_detected")
    )

    if detected and verify_result.get("confidence") in ("HIGH", "MEDIUM"):
        log(f"SYNTHETIC/TAUTOLOGICAL DETECTED (confidence={verify_result.get('confidence')}): "
            f"{verify_result.get('violations', [])}")

        for brief_attempt in range(1, MAX_BRIEF_VERIFY_RETRIES + 1):
            log(f"Brief fix attempt {brief_attempt}/{MAX_BRIEF_VERIFY_RETRIES}")

            set_auto_responder_enabled(True)
            clear_phase_complete_lock("phase2c")
            create_active_phase(research_folder=research_folder, hypothesis=args.hypothesis)

            fix_prompt = build_experiment_brief_fix_prompt(
                research_folder, args.hypothesis, validation,
                verify_result, brief_attempt
            )
            exit_code = _run_claude(
                fix_prompt, args.timeout,
                CACHE_DIR / f"phase2c_{args.hypothesis}_brief_fix_{brief_attempt}.log",
            )
            cleanup()
            if exit_code == 124:
                log(f"phase2c: brief-fix attempt {brief_attempt} timed out — exiting")
                rc = post_timeout_exit_code(research_folder, "phase2c", log,
                                            hypothesis_id=args.hypothesis)
                print(research_folder)
                sys.exit(rc)
            log(f"Brief fix re-run exited with code {exit_code}")

            # Verify outputs again
            verify_and_write_json("phase2c", research_folder, exit_code,
                                  hypothesis_id=args.hypothesis)

            # Re-verify brief
            verify_result = run_experiment_brief_verification(
                research_folder, args.hypothesis, timeout=300
            )

            detected = (
                verify_result.get("synthetic_detected")
                or verify_result.get("tautological_detected")
            )

            if not detected:
                log(f"Synthetic/tautological issue resolved after attempt {brief_attempt}")
                break

            if verify_result.get("confidence") == "LOW":
                log(f"Detection confidence LOW after attempt {brief_attempt} — accepting")
                break

            log(f"Issue still detected after attempt {brief_attempt} "
                f"(confidence={verify_result.get('confidence')})")

        if detected and verify_result.get("confidence") in ("HIGH", "MEDIUM"):
            log(f"WARNING: Synthetic/tautological issue persists after {MAX_BRIEF_VERIFY_RETRIES} attempts")

    elif detected and verify_result.get("confidence") == "LOW":
        log("Detection confidence LOW — accepting without retry")
    elif verify_result.get("skipped"):
        log("Brief verification skipped (no experiment brief)")
    elif verify_result.get("parse_error"):
        log("WARNING: Brief verification output could not be parsed — continuing")
    else:
        log("Brief verification PASSED — no synthetic/tautological issues detected")

    log("=" * 60)

    cleanup()

    print(research_folder)

    log("Phase 2C Launcher complete")
    log("=" * 60)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
