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

# VSA-IC ablation (ws4 spec): set in main() when --state-mode=shadow.
# None → transparent passthrough (full-YouRA arm unchanged).
_MANAGER = None


def _mp(path):
    """Resolve a VSA target-file path through the ablation manager."""
    if _MANAGER is not None:
        return _MANAGER.state_path(path)
    return Path(path)


def _shadow_wrap(prompt: str, hypothesis: str,
                 include_checkpoint: bool = True,
                 include_tasks: bool = False) -> str:
    """Shadow mode: prepend override block + FRESH truncated state text
    (rebuilt from the shadow copy at call time — CR-3) and neutralize
    file-access instructions inside the launcher prompt."""
    if _MANAGER is None or not _MANAGER.is_shadow_mode():
        return prompt
    blocks = _MANAGER.build_prompt_blocks(
        hypothesis, phase="phase4",
        include_checkpoint=include_checkpoint, include_tasks=include_tasks)
    return blocks + _MANAGER.apply_prompt_replacements(prompt)


def _shadow_merge(log_path, hypothesis: str) -> bool:
    """Shadow mode: parse the session transcript's last ```state block and
    merge it into the shadow copies. Returns True if merged."""
    if _MANAGER is None or not _MANAGER.is_shadow_mode():
        return True
    merged = _MANAGER.merge_from_transcript(log_path, hypothesis_id=hypothesis)
    if merged:
        log(f"[ablation] shadow merge OK from {Path(log_path).name}")
    else:
        log(f"[ablation] WARNING: no restate block found in {Path(log_path).name}")
    return merged


def _ensure_shadow_merged_before_gate(research_folder: str, hypothesis: str) -> bool:
    """R3 hard gate (ablation): before read_gate_result(), make sure the shadow
    copy actually carries this session's final gate verdict. A stale shadow
    (gate.satisfied=null with no reflection_outcome) surfaces as UNKNOWN and
    triggers a destructive ROUTED_TO_PHASE_0 archive in run_hypothesis_loop.

    Order of attempts: (1) shadow already has a verdict → OK; (2) re-scan all
    candidate transcripts newest-first for a restate block; (3) launch a short
    restate-only recovery session (no experiment re-run)."""
    if _MANAGER is None or not _MANAGER.is_shadow_mode():
        return True

    def _gate_known() -> bool:
        st = _MANAGER.load_shadow_state()
        h = (st.get("sub_hypotheses") or {}).get(hypothesis) or {}
        gate = h.get("gate") or {}
        satisfied = gate.get("satisfied") if isinstance(gate, dict) else None
        outcome = _MANAGER.load_shadow_checkpoint(hypothesis).get("reflection_outcome")
        return satisfied is not None or outcome is not None

    if _gate_known():
        return True

    patterns = [
        f"phase4_{hypothesis}_reflection_retry.log",
        f"phase4_{hypothesis}_post_mock_fix_*.log",
        f"phase4_{hypothesis}_mock_fix_*.log",
        f"phase4_{hypothesis}_output.log",
    ]
    candidates = []
    for pat in patterns:
        candidates.extend(CACHE_DIR.glob(pat))
    for lf in sorted(set(candidates), key=lambda p: p.stat().st_mtime, reverse=True):
        _MANAGER.merge_from_transcript(lf, hypothesis_id=hypothesis)
        if _gate_known():
            log(f"[ablation] R3 gate: shadow recovered from {lf.name}")
            return True

    log("[ablation] R3 gate: no usable restate found — launching recovery session")
    # A stale PHASE_COMPLETE lock from the main session would force-kill the
    # recovery session after the 60s grace period — clear it first.
    clear_phase_complete_lock("phase4")
    recovery_prompt = _shadow_wrap(
        f"""#batch-mode

You just completed (or partially completed) Phase 4 for hypothesis {hypothesis}
in research folder {research_folder}, but your final state restate was not
captured. Do NOT re-run any experiment and do NOT modify any code.

Restate the final pipeline state NOW in a single ```state fenced block:
- sub_hypotheses.{hypothesis}: gate (satisfied/result), validation
  (status/result/key_findings), reflection_outcome and route_to if the gate
  failed, completed/completed_at.
- checkpoint: the full current 04_checkpoint.yaml content.

Base it on the experiment artifacts on disk ({research_folder}/{hypothesis}/code/,
experiment_results.json, 04_validation.md). Output ONLY the state block, then stop.""",
        hypothesis)
    recovery_log = CACHE_DIR / f"phase4_{hypothesis}_state_recovery.log"
    _run_claude(recovery_prompt, 600, recovery_log, truncate_log=True)
    _MANAGER.merge_from_transcript(recovery_log, hypothesis_id=hypothesis)
    if _gate_known():
        log("[ablation] R3 recovery session succeeded")
        return True
    log("[ablation] CRITICAL: R3 recovery failed — gate may read UNKNOWN")
    return False


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

    vs = _mp(folder / "verification_state.yaml")
    if vs.exists():
        result["has_verification_state"] = True
        result["files"].append(f"  - verification_state.yaml ({vs.stat().st_size} bytes)")

    # Check Phase 3 outputs
    h_folder = folder / hypothesis
    tasks = _mp(h_folder / "03_tasks.yaml")
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

    # Read verification_state.yaml (shadow copy in ablation mode)
    vs_path = _mp(Path(research_folder) / "verification_state.yaml")
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
        gate = h_data.get("gate") or {}
        result["gate_type"] = gate.get("type", "UNKNOWN")

        gate_satisfied = gate.get("satisfied")
        _val_status = str((h_data.get("validation") or {}).get("status") or "").upper()
        _val_raw = (h_data.get("validation") or {}).get("result") or ""
        if isinstance(_val_raw, dict):
            # LLM sometimes writes a metrics dict here — extract a verdict field.
            # gate_verdict first (shadow restate schema), then mainline fallbacks.
            _val_raw = (_val_raw.get("gate_verdict") or _val_raw.get("verdict")
                        or _val_raw.get("result") or _val_raw.get("status")
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
            checkpoint_path = _mp(Path(research_folder) / hypothesis / "04_checkpoint.yaml")
            if not checkpoint_path.exists():
                archive_root = Path(research_folder) / "_archive"
                # Check _archive/<hypothesis>/ directly (Claude-archived)
                candidate = archive_root / hypothesis / "04_checkpoint.yaml"
                if candidate.exists():
                    checkpoint_path = candidate
                    log(f"WARNING: checkpoint found in _archive/{hypothesis}/ — using archived copy")
                else:
                    # Check _archive/<timestamp>/<hypothesis>/
                    for ts_dir in (sorted(archive_root.iterdir(), key=lambda d: d.name, reverse=True)
                                   if archive_root.exists() else []):
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

        elif gate_satisfied is True and (
                h_status in ("VALIDATED", "COMPLETED")
                or _val_status == "COMPLETED"):
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


def create_active_phase(research_folder: str = None, hypothesis: str = None,
                        state_mode: str = "normal"):
    """Create .cache/active_phase.json for hook routing."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    phase_info = {
        "phase": "phase4",
        "enabled": True,
        "config_file": str(PHASE_CONFIG_FILE),
        "pid": os.getpid(),
        "started_at": datetime.now().isoformat(),
        "research_folder": research_folder or "",
        "state_mode": state_mode or "normal",
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

    # Shadow mode: wrap the QA session too (zero-exemption R8 audit — the
    # override prevents any accidental read of the 3 VSA files here).
    prompt = _shadow_wrap(
        build_mock_verification_prompt(research_folder, hypothesis),
        hypothesis, include_checkpoint=False,
    )
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

    checkpoint_path = _mp(Path(research_folder) / hypothesis / "04_checkpoint.yaml")
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
    parser.add_argument("--state-mode", type=str, choices=("normal", "shadow"),
                        default="normal",
                        help="VSA-IC ablation: 'shadow' relays state via prompt "
                             "context + .ablation_shadow/ (default: normal)")

    return parser.parse_args()


def _run_claude(prompt: str, timeout: int, output_log,
                echo_to_stdout: bool = False, truncate_log: bool = False) -> int:
    """Launch Claude CLI with Phase 4 controls and transient API retry.

    Shadow mode logs the FULL session as stream-json: `claude -p` text mode
    only emits the final message, which loses intermediate ```state restates
    AND leaves the R8 audit blind to tool calls (both required by ws4 R8).
    """
    if truncate_log:
        Path(output_log).write_text("", encoding="utf-8")

    from claude_runner import run_claude_with_retry

    _shadow = _MANAGER is not None and _MANAGER.is_shadow_mode()
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
        extra_cli_args=(["--output-format", "stream-json", "--verbose"]
                        if _shadow else None),
        stream_json=_shadow,
        separate_stderr=_shadow,
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

    # VSA-IC ablation mode: install the shadow-state manager into this module
    # and the shared verifier/timeout helpers.
    global _MANAGER
    if args.state_mode == "shadow":
        from ablation_state_manager import AblationStateManager
        import phase_output_verifier as _pov
        import timeout_policy as _tp
        _MANAGER = AblationStateManager(research_folder, mode="shadow", log_fn=log)
        _pov.set_state_manager(_MANAGER)
        _tp.set_state_manager(_MANAGER)
        log(f"VSA-IC ABLATION MODE: state relayed via {_MANAGER.shadow_dir}")

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
    create_active_phase(research_folder=research_folder, hypothesis=args.hypothesis, state_mode=args.state_mode)

    prompt = _shadow_wrap(
        build_phase4_prompt(research_folder, args.hypothesis, validation),
        args.hypothesis, include_checkpoint=True, include_tasks=True,
    )
    log(f"Launching Claude CLI with prompt ({len(prompt)} chars)")
    output_log = CACHE_DIR / f"phase4_{args.hypothesis}_output.log"

    # R7 (ablation): crash/timeout of the main session restarts it from step 1
    # with fresh shadow state re-injected. Normal mode: single attempt, as before.
    MAX_RESTARTS = 2
    ablation_restart_count = 0

    try:
        while True:
            start_time = time.time()
            exit_code = _run_claude(
                prompt,
                args.timeout,
                output_log,
                echo_to_stdout=True,
                truncate_log=(ablation_restart_count == 0),
            )
            elapsed = time.time() - start_time
            log(f"Claude CLI exited with code {exit_code} after {elapsed:.0f}s")

            # Shadow mode: salvage whatever state the session restated.
            _shadow_merge(output_log, args.hypothesis)

            if _MANAGER is None or not _MANAGER.is_shadow_mode():
                break
            if exit_code == 0 or ablation_restart_count >= MAX_RESTARTS:
                break
            # PHASE_COMPLETE lock present → the non-zero exit is the benign
            # lock-grace straggler kill (SIGTERM from claude_runner), NOT a
            # crash. Treat as completed.
            if (CACHE_DIR / "phase4_complete.lock").exists():
                log("[ablation] R7: PHASE_COMPLETE lock present — session "
                    "completed (straggler kill), not restarting")
                break
            if exit_code not in (124, 137, -9, -15):
                # Non-timeout failure — not an R7 restart case.
                break
            ablation_restart_count += 1
            log(f"[ablation] R7 RESTART {ablation_restart_count}/{MAX_RESTARTS}: "
                f"session timed out/crashed — re-injecting fresh shadow state")
            # Re-arm the session environment (a stale lock would kill the
            # restarted session after 60s; active_phase must be fresh).
            clear_phase_complete_lock("phase4")
            set_auto_responder_enabled(True)
            create_active_phase(research_folder=research_folder,
                                hypothesis=args.hypothesis, state_mode=args.state_mode)
            prompt = _shadow_wrap(
                build_phase4_prompt(research_folder, args.hypothesis, validation),
                args.hypothesis, include_checkpoint=True, include_tasks=True,
            )

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
        clear_phase_complete_lock("phase4")  # a lock written by the hook mid-retry must not leak into this retry
        _retry_prompt = _shadow_wrap(
            build_retry_prompt("phase4", research_folder, hypothesis_id=args.hypothesis),
            args.hypothesis,
        )
        exit_code = _run_claude(_retry_prompt, args.timeout,
                                CACHE_DIR / f"phase4_{args.hypothesis}_output.log")
        _shadow_merge(CACHE_DIR / f"phase4_{args.hypothesis}_output.log", args.hypothesis)
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
            create_active_phase(research_folder=research_folder, hypothesis=args.hypothesis, state_mode=args.state_mode)

            # CR-3 (ablation): prepare_checkpoint_for_mock_fix() just wrote the
            # [MOCK FIX] task to the SHADOW checkpoint — _shadow_wrap rebuilds
            # the injected state from shadow at this moment, so the sub-session
            # sees the fresh task, not the previous session's stale restate.
            fix_prompt = _shadow_wrap(
                build_mock_fix_prompt(research_folder, args.hypothesis, validation, mock_result, mock_attempt),
                args.hypothesis, include_checkpoint=True,
            )
            exit_code = _run_claude(
                fix_prompt, args.timeout,
                CACHE_DIR / f"phase4_{args.hypothesis}_mock_fix_{mock_attempt}.log",
            )
            _shadow_merge(CACHE_DIR / f"phase4_{args.hypothesis}_mock_fix_{mock_attempt}.log",
                          args.hypothesis)
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
                create_active_phase(research_folder=research_folder, hypothesis=args.hypothesis, state_mode=args.state_mode)
                _retry_prompt = _shadow_wrap(
                    build_post_mock_fix_retry_prompt(
                        research_folder, args.hypothesis, mock_attempt, _verify_data
                    ),
                    args.hypothesis, include_checkpoint=True,
                )
                exit_code = _run_claude(_retry_prompt, args.timeout,
                                        CACHE_DIR / f"phase4_{args.hypothesis}_post_mock_fix_{mock_attempt}.log")
                _shadow_merge(CACHE_DIR / f"phase4_{args.hypothesis}_post_mock_fix_{mock_attempt}.log",
                              args.hypothesis)
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

    # R3 hard gate (ablation): shadow must carry the final verdict before the
    # harness reads it — a stale shadow here means UNKNOWN → destructive archive.
    _ensure_shadow_merged_before_gate(research_folder, args.hypothesis)

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
            create_active_phase(research_folder=research_folder, hypothesis=args.hypothesis, state_mode=args.state_mode)

            # CR-3 (ablation): reflection-retry gets FRESH shadow state injected
            # (the "Read the checkpoint" instructions are neutralized by the wrap).
            refl_prompt = _shadow_wrap(
                build_reflection_retry_prompt(
                    research_folder, args.hypothesis, effective
                ),
                args.hypothesis, include_checkpoint=True,
            )
            refl_exit = _run_claude(
                refl_prompt, args.timeout,
                CACHE_DIR / f"phase4_{args.hypothesis}_reflection_retry.log",
            )
            _shadow_merge(CACHE_DIR / f"phase4_{args.hypothesis}_reflection_retry.log",
                          args.hypothesis)

            cleanup()

            log(f"Reflection retry exited with code {refl_exit}")

            # R3 hard gate before re-reading (second read_gate_result call site)
            _ensure_shadow_merged_before_gate(research_folder, args.hypothesis)

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
    if _MANAGER is not None and _MANAGER.is_shadow_mode():
        gate_result["ablation_restart_count"] = ablation_restart_count
        gate_result["ablation_truncation"] = _MANAGER.last_truncation_meta
    print(json.dumps(gate_result, ensure_ascii=False))

    log(f"Gate result: {gate_result['gate_result']} (type={gate_result['gate_type']})")
    log("Phase 4 Launcher complete")
    log("=" * 60)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
