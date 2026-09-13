#!/usr/bin/env python3
"""
Phase 4 Launcher — Runs /phase4-coding Unattended

Launches Claude CLI with the /phase4-coding command for a specific hypothesis.
Configures the phase-specific auto-responder hook for fully unattended execution.

After completion, outputs a JSON result to stdout (last line) with gate result
information for the calling script to parse.

Requires --research-folder and --hypothesis.

Phase 4 has 13 steps (with sub-steps):
  Step 01:  Initialize (Phase 3 completion check, 03_tasks.yaml load)
  Step 01a: Data Setup (dataset/model download)
  Step 01b: Continue (checkpoint-based resume)
  Step 02:  Coder Loop (code generation, iterative)
  Step 03:  Validator Agent (Task tool sub-agent)
  Step 04:  Experiment Confirm
  Step 05a: Pre-validation
  Step 05b: Execution (experiment run — longest step, GPU usage)
  Step 05c: Post-validation
  Step 06:  Gate Processing (MUST_WORK gate verdict)
  Step 06b: Reflection (failure reflection + routing decision)
  Step 07:  Report Generation (04_validation.md)
  Step 08:  Completion (verification_state.yaml update)

Usage:
  python run_phase4.py --research-folder docs/youra_research/20260304_scsl --hypothesis h-e1
  python run_phase4.py --research-folder <path> --hypothesis h-e1 --timeout 14400

Author: Anonymous
Version: 1.0
"""

import argparse
import atexit
import json
import os
import re
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from phase_output_verifier import (
    clear_must_stop, check_must_stop,
    verify_and_write_json, build_retry_prompt, MAX_RETRIES,
    clear_phase_complete_lock, proc_tree_cputime,
)

# Hang detection thresholds (heredoc/eval deadlocks freeze CPU time entirely;
# real training keeps CPU time moving via data loader / Python interpreter).
HANG_IDLE_SECS = 1800       # 30 min of zero CPU growth = hung
HANG_STARTUP_GRACE = 600    # ignore first 10 min (env setup, MCP boot)

try:
    import yaml
except ImportError:
    yaml = None

# ============================================================
# Path Configuration
# ============================================================
SCRIPT_DIR = Path(__file__).parent
CACHE_DIR = SCRIPT_DIR / ".cache"
ACTIVE_PHASE_FILE = CACHE_DIR / "active_phase.json"
PHASE_CONFIG_FILE = SCRIPT_DIR / "phase4_auto_config.yaml"
AUTO_RESPONDER_CONFIG = SCRIPT_DIR / "auto_responder_config.yaml"
PROJECT_DIR = SCRIPT_DIR.parent.parent
CLAUDE_CLI = Path.home() / ".local" / "bin" / "claude"

LOG_FILE = CACHE_DIR / "run_phase4.log"


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
    """Validate research folder and Phase 3 prerequisites."""
    folder = Path(research_folder)
    result = {
        "valid": False,
        "files": [],
        "has_verification_state": False,
        "has_tasks_yaml": False,
        "has_phase3_docs": False,
    }

    if not folder.exists() or not folder.is_dir():
        log(f"ERROR: Research folder does not exist: {research_folder}")
        return result

    result["valid"] = True

    vs = folder / "verification_state.yaml"
    if vs.exists():
        result["has_verification_state"] = True
        result["files"].append(f"  - verification_state.yaml ({vs.stat().st_size} bytes)")

    # Check Phase 3 outputs
    h_folder = folder / hypothesis
    tasks = h_folder / "03_tasks.yaml"
    if tasks.exists():
        result["has_tasks_yaml"] = True
        result["files"].append(f"  - {hypothesis}/03_tasks.yaml ({tasks.stat().st_size} bytes)")

    phase3_docs = ["03_prd.md", "03_architecture.md", "03_logic.md", "03_config.md"]
    found = sum(1 for f in phase3_docs if (h_folder / f).exists())
    if found >= 4:
        result["has_phase3_docs"] = True

    # List hypothesis folder files
    if h_folder.exists():
        for fname in sorted(h_folder.iterdir()):
            if fname.is_file() and fname.name != "03_tasks.yaml":
                result["files"].append(f"  - {hypothesis}/{fname.name} ({fname.stat().st_size} bytes)")

    return result


# ============================================================
# Gate Result Reading
# ============================================================
def read_gate_result(research_folder: str, hypothesis: str) -> dict:
    """Read Phase 4 gate result from verification_state.yaml and 04_checkpoint.yaml.

    Returns a dict with gate information for the calling script.
    """
    result = {
        "hypothesis": hypothesis,
        "gate_result": "UNKNOWN",
        "gate_type": "UNKNOWN",
        "route_to": None,
        "hypothesis_status": "UNKNOWN",
    }

    if not yaml:
        log("WARNING: PyYAML not available, cannot read gate result")
        return result

    # Read verification_state.yaml
    vs_path = Path(research_folder) / "verification_state.yaml"
    if vs_path.exists():
        try:
            with open(vs_path, "r", encoding="utf-8") as f:
                content = f.read()
            try:
                state = yaml.safe_load(content) or {}
            except yaml.YAMLError:
                # Recovery: truncate at serena_memory section
                idx = content.rfind("# SERENA MEMORY REFERENCES")
                if idx > 0:
                    state = yaml.safe_load(content[:idx]) or {}
                else:
                    state = {}
        except Exception as e:
            log(f"WARNING: Failed to read verification_state.yaml: {e}")
            state = {}

        h_data = state.get("sub_hypotheses", {}).get(hypothesis, {})
        result["hypothesis_status"] = h_data.get("status", "UNKNOWN")
        result["gate_type"] = h_data.get("gate", {}).get("type", "UNKNOWN")

        gate = h_data.get("gate", {})
        gate_satisfied = gate.get("satisfied")
        _val_raw = h_data.get("validation", {}).get("result") or ""
        if isinstance(_val_raw, dict):
            # LLM sometimes writes a metrics dict here — extract a verdict field
            _val_raw = (_val_raw.get("verdict") or _val_raw.get("result")
                        or _val_raw.get("status")
                        or ("PASS" if _val_raw.get("primary_pass") is True
                            or _val_raw.get("passed") is True else ""))
        validation_result = str(_val_raw or "").upper()
        _gate_result_raw = gate.get("result") or ""
        gate_result_field = (_gate_result_raw.get("verdict", "") if isinstance(_gate_result_raw, dict) else _gate_result_raw).upper()
        h_status = h_data.get("status", "UNKNOWN")

        # Priority: gate.satisfied > validation.result/gate.result > status
        # gate.satisfied=False means gate not met, even if status=COMPLETED
        if gate_satisfied is False:
            # Check reflection_outcome from checkpoint to determine routing
            effective_result = validation_result or gate_result_field
            result["gate_result"] = "FAILED"  # Default

            # Read checkpoint for reflection outcome (Phase 4 step-06b sets this)
            # Fallback to _archive/h-*/ in case Claude archived the folder directly
            checkpoint_path = Path(research_folder) / hypothesis / "04_checkpoint.yaml"
            if not checkpoint_path.exists():
                archive_root = Path(research_folder) / "_archive"
                # Check _archive/<hypothesis>/ directly (Claude-archived)
                candidate = archive_root / hypothesis / "04_checkpoint.yaml"
                if candidate.exists():
                    checkpoint_path = candidate
                    log(f"WARNING: checkpoint found in _archive/{hypothesis}/ — using archived copy")
                else:
                    # Check _archive/<timestamp>/<hypothesis>/
                    for ts_dir in sorted(archive_root.iterdir(), key=lambda d: d.name, reverse=True):
                        candidate = ts_dir / hypothesis / "04_checkpoint.yaml"
                        if candidate.exists():
                            checkpoint_path = candidate
                            log(f"WARNING: checkpoint found in _archive/{ts_dir.name}/{hypothesis}/ — using archived copy")
                            break
            reflection_outcome = None
            if checkpoint_path.exists():
                try:
                    with open(checkpoint_path, "r", encoding="utf-8") as cf:
                        checkpoint = yaml.safe_load(cf) or {}
                    reflection_outcome = checkpoint.get("reflection_outcome")
                    route_field = checkpoint.get("route_to", "")
                except Exception:
                    pass

            if reflection_outcome:
                # Step-06b ran and determined outcome
                ro = str(reflection_outcome).upper()
                if ro in ("ROUTED_TO_PHASE_0", "FAILED"):
                    result["gate_result"] = "ROUTED_TO_PHASE_0"
                    result["route_to"] = "Phase 0"
                elif ro in ("ROUTED_TO_PHASE_2A", "SUPERSEDED"):
                    result["gate_result"] = "ROUTED_TO_PHASE_2A"
                    result["route_to"] = "Phase 2A-Dialogue"
                elif ro in ("MODIFIED", "SELF_MODIFY"):
                    result["gate_result"] = "SELF_MODIFY"
                    result["route_to"] = "Phase 2C"
                elif ro == "LIMITATION_RECORDED":
                    result["gate_result"] = "LIMITATION_RECORDED"
            else:
                # reflection_outcome is null — step-06b was NOT executed
                # PARTIAL/FAIL with no reflection is an anomaly; flag for re-run
                if effective_result in ("PARTIAL", "FAIL"):
                    result["gate_result"] = "NEEDS_REFLECTION"
                    result["needs_reflection"] = True
                    result["effective_result"] = effective_result
                    log(f"WARNING: {hypothesis} has {effective_result} gate but "
                        f"reflection_outcome is null — step-06b was skipped")

        elif gate_satisfied is True and h_status in ("VALIDATED", "COMPLETED"):
            result["gate_result"] = "PASS"
        elif h_status == "FAILED":
            result["gate_result"] = "FAILED"
        elif h_status == "LIMITATION_RECORDED":
            result["gate_result"] = "LIMITATION_RECORDED"

    # (checkpoint reading is now integrated into gate_satisfied=False branch above)

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
        "phase": "phase4",
        "enabled": True,
        "config_file": str(PHASE_CONFIG_FILE),
        "pid": os.getpid(),
        "started_at": datetime.now().isoformat(),
        "research_folder": research_folder or "",
        "hypothesis": hypothesis or "",
    }

    with open(ACTIVE_PHASE_FILE, "w", encoding="utf-8") as f:
        json.dump(phase_info, f, indent=2)

    log(f"Created active_phase.json: phase=phase4, pid={os.getpid()}, research_folder={research_folder or 'NONE'}")


def cleanup():
    """Cleanup on exit."""
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
def build_phase4_prompt(research_folder: str, hypothesis: str, validation: dict) -> str:
    """Build the initial prompt for Phase 4 unattended execution."""
    files_str = "\n".join(validation["files"]) if validation["files"] else "  (no files found)"

    prompt = f"""/phase4-coding

#batch-mode

Proceed in Unattended mode. Research folder is located at:

  {research_folder}

Target hypothesis: {hypothesis}

Available files:
{files_str}

Execute all Phase 4 steps automatically for hypothesis {hypothesis}.
Do NOT ask for user confirmation — proceed through all steps without stopping.
IMPORTANT: When you have completed all tasks, STOP IMMEDIATELY. Do NOT wait for further instructions.
Do NOT say "Awaiting further instructions" — just stop. The pipeline will continue automatically.

Key instructions:
- Load 03_tasks.yaml for {hypothesis}
- Set up dataset and model files
- Execute Coder-Validator loop
- Run experiment and collect results
- Determine gate verdict (MUST_WORK gate)
- Generate 04_validation.md report
- Update verification_state.yaml with validation results and gate_result
- When presented with any menu, automatically select [C] Continue

Experiment scale guidance:
- Do NOT use trivially small sample sizes (e.g., 10-50 samples) for experiments
- Use statistically meaningful sample counts: full standard test sets or at minimum 500+ evaluation samples
- Prefer standard dataset splits (full train/val/test) over arbitrary small subsets
- If a dataset is too large for single-GPU execution, subsample to a reasonable size (e.g., 10-20% of full set) rather than using a toy-sized subset

Experiment launcher rules (MANDATORY — prevents unrecoverable hangs):
- Every shell wrapper that runs an experiment MUST install a completion-marker finalizer
  as the FIRST line after setting LOG. Use this exact pattern:
      LOG=experiment.log
      trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT
      python main.py --config cfg.yaml > "$LOG" 2>&1
  The marker string MUST be "EXPERIMENT COMPLETE" exactly. `trap ... EXIT` fires on
  success, Python exception, OOM kill, SIGTERM, and Ctrl-C, so the marker is always
  written. This is non-negotiable — write the trap before the python invocation.

Experiment waiting rules (MANDATORY — do NOT use unbounded polling):
- NEVER use unbounded polling such as:
      until [ -f log ] && grep -q "EXPERIMENT COMPLETE" log; do sleep N; done
  If the python process dies before writing the marker, this loop runs forever and
  the Bash tool_result never returns, hanging the whole pipeline.
- Use one of these termination-guaranteed patterns instead, in order of preference:
  1. Foreground with timeout:
         timeout <seconds> python main.py --config cfg.yaml 2>&1 | tee experiment.log
  2. Background + wait on PID:
         python main.py --config cfg.yaml > experiment.log 2>&1 &
         PID=$!; wait "$PID"; echo "done exit=$?"
  3. Background + tail --pid (auto-terminates when PID exits):
         python main.py --config cfg.yaml > experiment.log 2>&1 &
         PID=$!; tail --pid="$PID" -f experiment.log
- If you absolutely must poll, cap it with a hard wall-clock limit and always break on timeout:
      START=$(date +%s); LIMIT=14400
      until [ -f log ] && grep -q "EXPERIMENT COMPLETE" log; do
        [ $(($(date +%s)-START)) -gt $LIMIT ] && {{ echo "TIMEOUT"; break; }}
        sleep 30
      done
- Watcher hygiene: if a previous turn launched a background polling/tail shell,
  you MUST call KillBash on that shell_id BEFORE starting a new experiment. Never
  leave stale watchers behind — they can pin a Claude turn indefinitely."""

    return prompt


def build_mock_fix_prompt(research_folder: str, hypothesis: str,
                          validation: dict, mock_result: dict,
                          attempt: int) -> str:
    """Build a prompt specifically for fixing mock data violations.

    Unlike build_phase4_prompt, this includes the exact violations found
    by the mock verification agent so Claude knows exactly what to fix.
    """
    files_str = "\n".join(validation["files"]) if validation["files"] else "  (no files found)"
    violations = mock_result.get("violations", [])
    violations_str = "\n".join(f"  - {v}" for v in violations) if violations else "  (no specific violations listed)"
    expected_dataset = mock_result.get("expected_dataset", "see 02c_experiment_brief.md")
    actual_source = mock_result.get("actual_data_source", "mock/synthetic")
    confidence = mock_result.get("confidence", "UNKNOWN")
    reasoning = mock_result.get("reasoning", "")

    workflow_dir = (
        "bmad-custom-src/custom/modules/youra-research/workflows/phase4-coding"
    )
    prompt = f"""#batch-mode

## MOCK DATA FIX — Attempt {attempt}/{MAX_MOCK_RETRIES}

CRITICAL: External mock verification detected that the experiment code uses
mock/synthetic data instead of the REAL dataset. You MUST fix this.

### Phase 4 Workflow Reference
You may read the Phase 4 workflow for guidance on coding patterns and step structure:
  {workflow_dir}/workflow.md
  {workflow_dir}/workflow.yaml
  {workflow_dir}/steps/  (step-01a through step-08)

### Mock Verification Result
- Confidence: {confidence}
- Expected dataset: {expected_dataset}
- Actual data source: {actual_source}
- Reasoning: {reasoning}

### Violations Found
{violations_str}

### What You Must Do
1. Read 04_checkpoint.yaml — it has return_reason=mock_data_detected and a [MOCK FIX] task
2. Read 02c_experiment_brief.md to understand the REAL dataset specification
3. Find and REMOVE all mock/synthetic data generation in the main experiment code
4. Replace with REAL dataset loading as specified in 02c_experiment_brief.md
5. Mock data in tests/*.py and conftest.py is OK — do NOT touch those
6. After fixing, re-run the experiment with the real dataset
7. Generate updated 04_validation.md report

---

Research folder: {research_folder}
Target hypothesis: {hypothesis}

Available files:
{files_str}

Do NOT ask for user confirmation — proceed through all steps without stopping.
When presented with any menu, automatically select [C] Continue.

IMPORTANT: When you have completed all tasks, STOP IMMEDIATELY. Do NOT wait for further instructions.
Do NOT say "Awaiting further instructions" — just stop. The pipeline will continue automatically.

Experiment scale guidance:
- Do NOT use trivially small sample sizes (e.g., 10-50 samples) for experiments
- Use statistically meaningful sample counts: full standard test sets or at minimum 500+ evaluation samples
- Prefer standard dataset splits (full train/val/test) over arbitrary small subsets
- If a dataset is too large for single-GPU execution, subsample to a reasonable size (e.g., 10-20% of full set) rather than using a toy-sized subset

Experiment launcher rules (MANDATORY — prevents unrecoverable hangs):
- Every shell wrapper that runs an experiment MUST install a completion-marker finalizer
  as the FIRST line after setting LOG. Use this exact pattern:
      LOG=experiment.log
      trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT
      python main.py --config cfg.yaml > "$LOG" 2>&1
  The marker string MUST be "EXPERIMENT COMPLETE" exactly. `trap ... EXIT` fires on
  success, Python exception, OOM kill, SIGTERM, and Ctrl-C, so the marker is always
  written. This is non-negotiable — write the trap before the python invocation.

Experiment waiting rules (MANDATORY — do NOT use unbounded polling):
- NEVER use unbounded polling such as:
      until [ -f log ] && grep -q "EXPERIMENT COMPLETE" log; do sleep N; done
  If the python process dies before writing the marker, this loop runs forever and
  the Bash tool_result never returns, hanging the whole pipeline.
- Use one of these termination-guaranteed patterns instead, in order of preference:
  1. Foreground with timeout:
         timeout <seconds> python main.py --config cfg.yaml 2>&1 | tee experiment.log
  2. Background + wait on PID:
         python main.py --config cfg.yaml > experiment.log 2>&1 &
         PID=$!; wait "$PID"; echo "done exit=$?"
  3. Background + tail --pid (auto-terminates when PID exits):
         python main.py --config cfg.yaml > experiment.log 2>&1 &
         PID=$!; tail --pid="$PID" -f experiment.log
- If you absolutely must poll, cap it with a hard wall-clock limit and always break on timeout:
      START=$(date +%s); LIMIT=14400
      until [ -f log ] && grep -q "EXPERIMENT COMPLETE" log; do
        [ $(($(date +%s)-START)) -gt $LIMIT ] && {{ echo "TIMEOUT"; break; }}
        sleep 30
      done
- Watcher hygiene: if a previous turn launched a background polling/tail shell,
  you MUST call KillBash on that shell_id BEFORE starting a new experiment. Never
  leave stale watchers behind — they can pin a Claude turn indefinitely."""

    return prompt


def build_reflection_retry_prompt(research_folder: str, hypothesis: str, effective_result: str) -> str:
    """Build a prompt to re-run step-06b reflection after it was skipped.

    This is triggered when Phase 4 completed with PARTIAL/FAIL gate result
    but checkpoint.reflection_outcome is null (step-06b was not executed).
    """
    step_06b_path = (
        "bmad-custom-src/custom/modules/youra-research/workflows/"
        "phase4-coding/steps/step-06b-reflection.md"
    )

    prompt = f"""#batch-mode

CRITICAL: Phase 4 for hypothesis {hypothesis} completed with gate result {effective_result},
but step-06b-reflection was NOT executed. The checkpoint shows reflection_outcome=null.

You MUST now execute step-06b-reflection to determine the correct routing decision.

Research folder: {research_folder}
Hypothesis: {hypothesis}
Gate result: {effective_result}

Instructions:
1. Read the checkpoint: {research_folder}/{hypothesis}/04_checkpoint.yaml
2. Read verification_state.yaml: {research_folder}/verification_state.yaml
3. Read and execute the FULL step-06b file: {step_06b_path}
4. The step-06b file will determine reflection_outcome (SELF_MODIFY, SUPERSEDED, FAILED, LIMITATION_RECORDED, etc.)
5. After step-06b completes, execute step-07 (report generation) and step-08 (completion) as specified in step-06b Section 9
6. Ensure checkpoint.reflection_outcome is set to a non-null value before finishing

Do NOT skip step-06b. Do NOT decide the routing yourself.
Read the entire step-06b file and follow its EXECUTION SEQUENCE exactly.
When presented with any menu, automatically select [C] Continue.
IMPORTANT: When you have completed all tasks, STOP IMMEDIATELY. Do NOT wait for further instructions.
Do NOT say "Awaiting further instructions" — just stop. The pipeline will continue automatically."""

    return prompt


def build_post_mock_fix_retry_prompt(
    research_folder: str,
    hypothesis: str,
    mock_attempt: int,
    verify_data: dict = None,
) -> str:
    """Build a retry prompt specifically for after mock data fix.

    After mock fix, the code has been updated to use real data and the experiment
    has re-run, but the tracking files (verification_state.yaml, 04_checkpoint.yaml,
    04_validation.md) may still contain stale data from the previous (mock) run.

    This prompt tells Claude to update ONLY the tracking files based on the
    NEW experiment results — NOT to re-run the experiment or modify code.
    """
    # Load verify summary if available
    summary = ""
    if verify_data:
        from phase_output_verifier import _format_verify_summary
        summary = _format_verify_summary(verify_data)

    return f"""#batch-mode

## POST-MOCK-FIX UPDATE — After mock fix attempt {mock_attempt}

The experiment code was fixed to use real data and the experiment has been re-run.
However, the tracking files still contain stale data from the previous (mock) run.

You MUST update the following files to reflect the NEW experiment results.
Do NOT re-run the experiment or modify code — only update tracking files.

### Research folder: {research_folder}
### Hypothesis: {hypothesis}

### Verification failures:
{summary}

### What You Must Do

1. Read the NEW experiment results:
   - {research_folder}/{hypothesis}/code/experiment_results.json (or similar results file)
   - {research_folder}/{hypothesis}/code/experiment.log (if exists)
   - Check {research_folder}/{hypothesis}/code/ for any results/*.json or output files

2. Update 04_validation.md:
   - Replace old (mock) metrics with new (real) experiment results
   - Update gate evaluation based on actual results
   - Ensure no {{{{UNFILLED:}}}} placeholders remain

3. Update 04_checkpoint.yaml:
   - partial_results.gate_result: set based on actual experiment outcome
   - partial_results.experiment_status: set to completed/failed
   - partial_results.validation_passed: true/false based on actual gate check
   - If gate failed: set reflection_outcome appropriately (see step-06b)
   - If serena memory needed: write it and set serena_memory.memory_written: true

4. Update verification_state.yaml for sub_hypotheses.{hypothesis}:
   - validation.status: COMPLETED (or FAIL/PARTIAL based on results)
   - validation.result: actual result summary (NOT null)
   - gate.satisfied: true/false based on actual gate evaluation (NOT null)
   - gate.result: PASS/FAIL/PARTIAL based on actual results

5. Execute step-06 (gate processing) through step-08 (completion) from the Phase 4 workflow:
   bmad-custom-src/custom/modules/youra-research/workflows/phase4-coding/steps/

Do NOT ask for user confirmation — proceed through all steps without stopping.
When presented with any menu, automatically select [C] Continue.
IMPORTANT: When you have completed all tasks, STOP IMMEDIATELY. Do NOT wait for further instructions.
Do NOT say "Awaiting further instructions" — just stop. The pipeline will continue automatically."""


# ============================================================
# Mock Data Verification (External LLM Session)
# ============================================================
MAX_MOCK_RETRIES = 5
MOCK_VERIFICATION_TIMEOUT = 2400  # 40 minutes


def build_mock_verification_prompt(research_folder: str, hypothesis: str) -> str:
    """Build prompt for a separate Claude session to verify mock data usage.

    Compares 02c_experiment_brief.md (expected dataset) against actual code
    to detect mock/synthetic data in the main experiment path.
    """
    h_folder = Path(research_folder) / hypothesis
    brief_path = h_folder / "02c_experiment_brief.md"
    code_folder = h_folder / "code"

    prompt = f"""#batch-mode

You are a Mock Data Verification agent. Your ONLY job is to determine whether
the experiment code uses REAL data as specified in the experiment brief, or
whether it falls back to mock/synthetic/random data.

## Files to Compare

1. **Expected dataset specification:**
   Read: {brief_path}
   This defines what dataset the experiment SHOULD use (name, source, loading method).

2. **Actual experiment code:**
   Folder: {code_folder}
   Read ALL .py files EXCEPT those under tests/ and conftest.py.
   Focus on: data loading, dataset initialization, main experiment entry points.

## What Counts as Mock Data Violation

- Generating random/synthetic tensors as training data (torch.randn, np.random, etc.)
- Importing or calling a mock data generator in the main experiment path
- "if data not found, generate mock" fallback patterns in non-test code
- Using placeholder/dummy rewards, states, or labels instead of real data
- Hard-coded toy data instead of loading from the specified dataset
- Dataset classes that WRAP np.random/torch.randn in a class but still generate all data programmatically
  (e.g., SimulatedDataset, SyntheticDataset classes that produce data from parametric distributions)

## What Counts as Tautological Experiment Violation

- Hard-coded bonus/reward values that guarantee specific metric outcomes
  (e.g., deep_learning_bonus = 0.18 added to one condition but not another)
- Constant metric values assigned directly (e.g., cca_score = 0.08) instead of computed from data
- Results computed from the same synthetic process that generates the data
- Experiment that CANNOT FAIL because expected results are embedded in the code
- Control vs experimental conditions differentiated only by hard-coded parameters
  that guarantee the hypothesis is confirmed
- Random penalties/rewards (np.random.uniform) used as placeholders for real computations

## What is NOT a Violation

- Mock data in test files (tests/*.py, conftest.py)
- Mock data generator file existing but NOT imported by main experiment code
- Using a smaller subset of real data (subsampling is fine)
- Data augmentation on real data

## Output

After reading both the experiment brief and all relevant code files,
output EXACTLY one JSON block (no other text before or after):

```json
{{
  "mock_detected": true or false,
  "tautological_detected": true or false,
  "confidence": "HIGH" or "MEDIUM" or "LOW",
  "expected_dataset": "name of dataset from 02c brief",
  "actual_data_source": "what the code actually uses",
  "reasoning": "1-2 sentence explanation",
  "violations": ["filename:line_number — description", ...]
}}
```

If neither mock nor tautological issues are found, both should be false and violations should be an empty list.
Do NOT output anything other than the JSON block."""

    return prompt


def run_mock_verification(research_folder: str, hypothesis: str,
                          timeout: int = MOCK_VERIFICATION_TIMEOUT) -> dict:
    """Run a separate Claude session to verify mock data usage.

    Returns dict with mock_detected, confidence, violations, etc.
    Returns {"mock_detected": False, "skipped": True} if code folder doesn't exist.
    """
    code_dir = Path(research_folder) / hypothesis / "code"
    if not code_dir.exists():
        log(f"Mock verification: no code directory for {hypothesis} — skipping")
        return {"mock_detected": False, "skipped": True}

    brief_path = Path(research_folder) / hypothesis / "02c_experiment_brief.md"
    if not brief_path.exists():
        log(f"Mock verification: no 02c_experiment_brief.md for {hypothesis} — skipping")
        return {"mock_detected": False, "skipped": True}

    prompt = build_mock_verification_prompt(research_folder, hypothesis)
    log_file = CACHE_DIR / f"phase4_{hypothesis}_mock_verify.log"

    log(f"Running mock verification for {hypothesis} (timeout={timeout}s)")
    exit_code = _run_claude(prompt, timeout, log_file)
    log(f"Mock verification exited with code {exit_code}")

    # Parse JSON from output log
    result = {"mock_detected": False, "parse_error": True}
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Find LAST JSON block in output (between ```json and ```)
        # Use findall to get all matches and take the last one,
        # since the log file accumulates across retry attempts.
        all_matches = re.findall(r'```json\s*\n(.*?)\n\s*```', content, re.DOTALL)
        if all_matches:
            result = json.loads(all_matches[-1])
        else:
            # Try to find last raw JSON object
            all_matches = re.findall(r'\{[^{}]*"mock_detected"[^{}]*\}', content, re.DOTALL)
            if all_matches:
                result = json.loads(all_matches[-1])
            else:
                log("WARNING: Could not parse mock verification JSON output")
                return {"mock_detected": False, "parse_error": True}

        result.pop("parse_error", None)
    except Exception as e:
        log(f"WARNING: Mock verification parse error: {e}")
        return {"mock_detected": False, "parse_error": True}

    log(f"Mock verification result: mock_detected={result.get('mock_detected')}, "
        f"confidence={result.get('confidence')}, "
        f"violations={len(result.get('violations', []))}")
    return result


def prepare_checkpoint_for_mock_fix(research_folder: str, hypothesis: str,
                                    mock_result: dict) -> bool:
    """Modify checkpoint to trigger Phase 4 re-entry at step-02 for mock fix.

    Sets current_step=2, adds mock fix task, records mock_data_check=FAILED.
    Returns True if checkpoint was modified, False on error.
    """
    if not yaml:
        log("ERROR: PyYAML not available — cannot modify checkpoint")
        return False

    checkpoint_path = Path(research_folder) / hypothesis / "04_checkpoint.yaml"
    if not checkpoint_path.exists():
        log(f"ERROR: Checkpoint not found: {checkpoint_path}")
        return False

    try:
        with open(checkpoint_path, "r", encoding="utf-8") as f:
            checkpoint = yaml.safe_load(f) or {}

        # Set resume point to step-02 (coder loop)
        checkpoint["current_step"] = 2
        checkpoint["return_reason"] = "mock_data_detected"

        # Record mock check failure
        violations = mock_result.get("violations", [])
        checkpoint["mock_data_check"] = {
            "status": "FAILED",
            "method": "external_llm_verification",
            "violations": violations,
            "expected_dataset": mock_result.get("expected_dataset", "unknown"),
            "actual_data_source": mock_result.get("actual_data_source", "unknown"),
            "confidence": mock_result.get("confidence", "unknown"),
            "reasoning": mock_result.get("reasoning", ""),
            "checked_at": datetime.now().isoformat(),
        }

        # Add mock fix task with highest priority
        import uuid
        fix_task = {
            "id": f"fix-mock-{str(uuid.uuid4())[:8]}",
            "title": "[MOCK FIX] Replace mock/synthetic data with real dataset from 02c",
            "status": "todo",
            "output_file": None,
            "test_file": None,
            "started_at": None,
            "completed_at": None,
            "sdd_phases": {"TEST": None, "IMPL": None, "VERIFY": None},
            "retry_count": 0,
            "priority": 99,
            "complexity": None,
            "epic": "Mock Data Fix",
            "description": (
                f"CRITICAL: External mock verification detected mock/synthetic data.\n"
                f"Expected dataset: {mock_result.get('expected_dataset', 'see 02c')}\n"
                f"Actual source: {mock_result.get('actual_data_source', 'mock')}\n"
                f"Violations:\n" +
                "\n".join(f"  - {v}" for v in violations) +
                f"\n\nFix: Remove mock data fallback from main experiment code. "
                f"Use REAL dataset as specified in 02c_experiment_brief.md. "
                f"Mock data generators may remain for tests/ only."
            ),
            "feature_tag": "mock-fix",
            "reference_files": {
                "experiment_brief": "02c_experiment_brief.md",
            },
        }

        tasks = checkpoint.get("tasks", {})
        items = tasks.get("items", [])
        items.append(fix_task)
        tasks["items"] = items

        summary = tasks.get("summary", {})
        summary["remaining"] = summary.get("remaining", 0) + 1
        summary["total"] = summary.get("total", 0) + 1
        tasks["summary"] = summary
        checkpoint["tasks"] = tasks

        # Reset experiment status so it re-runs after code fix
        partial = checkpoint.get("partial_results", {})
        partial["experiment_status"] = "pending"
        partial["validation_passed"] = False
        checkpoint["partial_results"] = partial

        # Save
        with open(checkpoint_path, "w", encoding="utf-8") as f:
            yaml.dump(checkpoint, f, default_flow_style=False, allow_unicode=True)

        log(f"Checkpoint modified: current_step=2, mock fix task added, "
            f"return_reason=mock_data_detected")
        return True

    except Exception as e:
        log(f"ERROR: Failed to modify checkpoint: {e}")
        return False


# ============================================================
# Signal Handlers
# ============================================================
_claude_process = None


def _set_proc(p):
    global _claude_process
    _claude_process = p


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
        description="Phase 4 Launcher — Run /phase4-coding unattended",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Stdout output (last line, JSON):
  {"hypothesis": "h-e1", "gate_result": "PASS", "gate_type": "MUST_WORK", ...}
  {"hypothesis": "h-e1", "gate_result": "ROUTED_TO_PHASE_0", "route_to": "Phase 0", ...}
  {"hypothesis": "h-e1", "gate_result": "FAILED", "gate_type": "SHOULD_WORK", ...}

Examples:
  %(prog)s --research-folder docs/youra_research/20260304_scsl --hypothesis h-e1
  %(prog)s --research-folder /absolute/path --hypothesis h-e1 --timeout 14400
        """,
    )

    parser.add_argument("--research-folder", type=str, required=True,
                        help="Path to research folder containing verification_state.yaml")
    parser.add_argument("--hypothesis", type=str, required=True,
                        help="Hypothesis ID to process (e.g., h-e1)")
    parser.add_argument("--timeout", type=int, default=1128800,
                        help="Max runtime in seconds (default: 1128800)")

    return parser.parse_args()


def _run_claude(prompt: str, timeout: int, output_log,
                echo_to_stdout: bool = False, truncate_log: bool = False) -> int:
    """Launch Claude CLI with Phase 4 controls and transient API retry."""
    if truncate_log:
        Path(output_log).write_text("", encoding="utf-8")

    from claude_runner import run_claude_with_retry

    return run_claude_with_retry(
        claude_cli=CLAUDE_CLI,
        project_dir=PROJECT_DIR,
        cache_dir=CACHE_DIR,
        prompt=prompt,
        timeout=timeout,
        output_log=Path(output_log),
        phase_name="phase4",
        log_fn=log,
        process_setter=_set_proc,
        echo_to_stdout=echo_to_stdout,
        monitor_complete_lock=True,
        lock_grace_period=60,
        hang_startup_grace=HANG_STARTUP_GRACE,
        hang_idle_secs=HANG_IDLE_SECS,
        proc_tree_cputime_fn=proc_tree_cputime,
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
    clear_phase_complete_lock("phase4")  # Clear any stale PHASE_COMPLETE lock from previous run

    research_folder = str(Path(args.research_folder).resolve())

    validation = validate_inputs(research_folder, args.hypothesis)

    log("=" * 60)
    log("Phase 4 Launcher starting")
    log(f"  Research folder: {research_folder}")
    log(f"  Hypothesis: {args.hypothesis}")
    log(f"  Folder valid: {validation['valid']}")
    log(f"  Has 03_tasks.yaml: {validation['has_tasks_yaml']}")
    log(f"  Has Phase 3 docs: {validation['has_phase3_docs']}")
    log(f"  Timeout: {args.timeout}s")
    log("=" * 60)

    if not validation["valid"]:
        log("ERROR: Research folder does not exist. Aborting.")
        sys.exit(1)

    if not validation["has_verification_state"]:
        log("ERROR: verification_state.yaml not found. Aborting.")
        sys.exit(1)

    if not validation["has_tasks_yaml"]:
        log("WARNING: 03_tasks.yaml not found — Phase 4 may fail.")

    atexit.register(cleanup)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    set_auto_responder_enabled(True)
    create_active_phase(research_folder=research_folder, hypothesis=args.hypothesis)

    prompt = build_phase4_prompt(research_folder, args.hypothesis, validation)
    log(f"Launching Claude CLI with prompt ({len(prompt)} chars)")
    output_log = CACHE_DIR / f"phase4_{args.hypothesis}_output.log"

    try:
        start_time = time.time()
        exit_code = _run_claude(
            prompt,
            args.timeout,
            output_log,
            echo_to_stdout=True,
            truncate_log=True,
        )
        elapsed = time.time() - start_time
        log(f"Claude CLI exited with code {exit_code} after {elapsed:.0f}s")

    except FileNotFoundError:
        log(f"ERROR: Claude CLI not found at {CLAUDE_CLI}")
        cleanup()
        sys.exit(1)
    except Exception as e:
        log(f"ERROR: {e}")
        cleanup()
        sys.exit(1)

    cleanup()

    # Read and output gate result as JSON (last line of stdout)
    # Check for MUST_STOP signal from hook (fatal error — abort immediately)
    must_stop_reason = check_must_stop()
    if must_stop_reason:
        log(f"MUST_STOP detected — aborting phase4: {must_stop_reason}")
        cleanup()
        sys.exit(1)

    # Verify outputs; retry with corrective prompt if needed
    verify_and_write_json("phase4", research_folder, exit_code, hypothesis_id=args.hypothesis)
    clear_phase_complete_lock("phase4")  # Clear lock so retry session is not immediately approved
    for _attempt in range(MAX_RETRIES):
        if exit_code != 0 or _check_passed("phase4", args.hypothesis):
            break
        log(f"Phase 4 verification FAILED — retry {_attempt + 1}/{MAX_RETRIES}")
        _retry_prompt = build_retry_prompt("phase4", research_folder, hypothesis_id=args.hypothesis)
        exit_code = _run_claude(_retry_prompt, args.timeout,
                                CACHE_DIR / f"phase4_{args.hypothesis}_output.log")
        must_stop_reason = check_must_stop()
        if must_stop_reason:
            log(f"MUST_STOP during retry — aborting phase4: {must_stop_reason}")
            exit_code = 1
            break
        verify_and_write_json("phase4", research_folder, exit_code, hypothesis_id=args.hypothesis)

    # ---- MOCK DATA VERIFICATION (separate Claude session) ----
    log("=" * 60)
    log("Mock Data Verification — starting external LLM check")
    log("=" * 60)

    mock_result = run_mock_verification(
        research_folder, args.hypothesis, timeout=MOCK_VERIFICATION_TIMEOUT
    )

    mock_or_tautological = (
        mock_result.get("mock_detected") or mock_result.get("tautological_detected")
    )

    if mock_or_tautological and mock_result.get("confidence") in ("HIGH", "MEDIUM"):
        log(f"MOCK/TAUTOLOGICAL DETECTED (confidence={mock_result.get('confidence')}): "
            f"{mock_result.get('violations', [])}")

        for mock_attempt in range(1, MAX_MOCK_RETRIES + 1):
            log(f"Mock fix attempt {mock_attempt}/{MAX_MOCK_RETRIES}")

            # Modify checkpoint: current_step=2, add mock fix task
            if not prepare_checkpoint_for_mock_fix(
                research_folder, args.hypothesis, mock_result
            ):
                log("ERROR: Could not modify checkpoint — skipping mock fix")
                break

            # Re-run Phase 4 (step-01b will resume from step-02 via checkpoint)
            set_auto_responder_enabled(True)
            clear_phase_complete_lock("phase4")  # Clear lock so mock-fix session is not immediately approved
            create_active_phase(research_folder=research_folder, hypothesis=args.hypothesis)

            fix_prompt = build_mock_fix_prompt(research_folder, args.hypothesis, validation, mock_result, mock_attempt)
            exit_code = _run_claude(
                fix_prompt, args.timeout,
                CACHE_DIR / f"phase4_{args.hypothesis}_mock_fix_{mock_attempt}.log",
            )
            cleanup()
            log(f"Mock fix Phase 4 re-run exited with code {exit_code}")

            # Verify outputs after fix; retry if YAML fields not updated
            verify_and_write_json("phase4", research_folder, exit_code,
                                  hypothesis_id=args.hypothesis)
            clear_phase_complete_lock("phase4")
            for _verify_attempt in range(MAX_RETRIES):
                if exit_code != 0 or _check_passed("phase4", args.hypothesis):
                    break
                log(f"Post-mock-fix verification FAILED — retry {_verify_attempt + 1}/{MAX_RETRIES}")

                # Load verify data for the prompt
                _verify_json_path = CACHE_DIR / f"phase4_{args.hypothesis}_output_verify.json"
                _verify_data = {}
                if _verify_json_path.exists():
                    try:
                        with open(_verify_json_path) as _vf:
                            _verify_data = json.load(_vf)
                    except Exception:
                        pass

                set_auto_responder_enabled(True)
                create_active_phase(research_folder=research_folder, hypothesis=args.hypothesis)
                _retry_prompt = build_post_mock_fix_retry_prompt(
                    research_folder, args.hypothesis, mock_attempt, _verify_data
                )
                exit_code = _run_claude(_retry_prompt, args.timeout,
                                        CACHE_DIR / f"phase4_{args.hypothesis}_post_mock_fix_{mock_attempt}.log")
                cleanup()
                must_stop_reason = check_must_stop()
                if must_stop_reason:
                    log(f"MUST_STOP during post-mock-fix retry — aborting: {must_stop_reason}")
                    exit_code = 1
                    break
                verify_and_write_json("phase4", research_folder, exit_code,
                                      hypothesis_id=args.hypothesis)

            # Re-verify mock data
            mock_result = run_mock_verification(
                research_folder, args.hypothesis, timeout=MOCK_VERIFICATION_TIMEOUT
            )

            mock_or_tautological = (
                mock_result.get("mock_detected") or mock_result.get("tautological_detected")
            )

            if not mock_or_tautological:
                log(f"Mock/tautological issue resolved after attempt {mock_attempt}")
                break

            if mock_result.get("confidence") == "LOW":
                log(f"Detection confidence LOW after attempt {mock_attempt} — accepting")
                break

            log(f"Issue still detected after attempt {mock_attempt} "
                f"(confidence={mock_result.get('confidence')})")

        if mock_or_tautological and mock_result.get("confidence") in ("HIGH", "MEDIUM"):
            log(f"WARNING: Mock/tautological issue persists after {MAX_MOCK_RETRIES} attempts — "
                f"recording warning in gate result")

    elif mock_or_tautological and mock_result.get("confidence") == "LOW":
        log("Detection confidence LOW — accepting without retry")
    elif mock_result.get("skipped"):
        log("Mock verification skipped (no code dir or 02c brief)")
    elif mock_result.get("parse_error"):
        log("WARNING: Mock verification output could not be parsed — continuing")
    else:
        log("Mock verification PASSED — no mock data detected")

    log("=" * 60)

    gate_result = read_gate_result(research_folder, args.hypothesis)

    # Inject mock/tautological warning into gate result if issue persists
    mock_or_taut = mock_result.get("mock_detected") or mock_result.get("tautological_detected")
    if mock_or_taut and mock_result.get("confidence") in ("HIGH", "MEDIUM"):
        gate_result["mock_data_warning"] = True
        gate_result["tautological_warning"] = mock_result.get("tautological_detected", False)
        gate_result["mock_violations"] = mock_result.get("violations", [])
        gate_result["mock_confidence"] = mock_result.get("confidence")

    # ---- REFLECTION RETRY: step-06b was skipped ----
    MAX_REFLECTION_RETRIES = 2
    if gate_result.get("needs_reflection"):
        effective = gate_result.get("effective_result", "UNKNOWN")
        log(f"NEEDS_REFLECTION detected: {args.hypothesis} has {effective} "
            f"but reflection_outcome=null — launching step-06b retry")

        for refl_attempt in range(1, MAX_REFLECTION_RETRIES + 1):
            log(f"Reflection retry {refl_attempt}/{MAX_REFLECTION_RETRIES}")

            set_auto_responder_enabled(True)
            clear_phase_complete_lock("phase4")  # Clear lock so reflection-retry session is not immediately approved
            create_active_phase(research_folder=research_folder, hypothesis=args.hypothesis)

            refl_prompt = build_reflection_retry_prompt(
                research_folder, args.hypothesis, effective
            )
            refl_exit = _run_claude(
                refl_prompt, args.timeout,
                CACHE_DIR / f"phase4_{args.hypothesis}_reflection_retry.log",
            )

            cleanup()

            log(f"Reflection retry exited with code {refl_exit}")

            # Re-read gate result after reflection retry
            gate_result = read_gate_result(research_folder, args.hypothesis)

            if not gate_result.get("needs_reflection"):
                log(f"Reflection retry SUCCESS: reflection_outcome is now set "
                    f"→ gate_result={gate_result['gate_result']}")
                break

            log(f"Reflection retry {refl_attempt} did not set reflection_outcome")

        # If still needs_reflection after all retries, use safe fallback
        if gate_result.get("needs_reflection"):
            log(f"WARNING: reflection_outcome still null after "
                f"{MAX_REFLECTION_RETRIES} retries — applying safe fallback")
            if effective == "PARTIAL":
                gate_result["gate_result"] = "ROUTED_TO_PHASE_2A"
                gate_result["route_to"] = "Phase 2A-Dialogue"
                gate_result["fallback"] = "reflection_retry_exhausted"
            else:  # FAIL
                gate_result["gate_result"] = "ROUTED_TO_PHASE_0"
                gate_result["route_to"] = "Phase 0"
                gate_result["fallback"] = "reflection_retry_exhausted"

    gate_result["research_folder"] = research_folder
    gate_result["exit_code"] = exit_code
    print(json.dumps(gate_result, ensure_ascii=False))

    log(f"Gate result: {gate_result['gate_result']} (type={gate_result['gate_type']})")
    log("Phase 4 Launcher complete")
    log("=" * 60)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
