# Experiment Mock Detection Guide (Phase 5)

> **Purpose:** LLM-based verification to detect mock/synthetic experiment results in baseline comparison.
> **Context:** Phase 5 runs {total_runs} experiments ({baselines_count} baselines × {methods_per_baseline} methods per baseline). This guide ensures real experiments are executed.
> **Reference:** Adapted from `helpers/mock_detection.md` for baseline comparison context.

---

## Overview

Phase 5 executes baseline comparison experiments. Unlike Phase 4 (single hypothesis validation), Phase 5 injects **OUR algorithm into BASELINE's environment** = **{total_runs} total runs** ({baselines_count} baselines × {methods_per_baseline} methods).

**Mode B Principle:** Each baseline uses THEIR OWN model, dataset, config. The ONLY difference is the algorithm (baseline_original vs ours_injected).

**Detection Points:**
1. **Pre-Experiment (9.0):** Before launching experiments
2. **Post-Experiment (9.6.5):** After collecting comparison_data.csv

---

## 1. Pre-Experiment Verification (Section 9.0)

### verify_pre_experiment_reality()

Called before launching experiments. Verifies adaptation code and runner scripts are set up for real experiments.

```python
def verify_pre_experiment_reality(
    baseline_folder: str,
    checkpoint_file: str,
    experiment_brief_file: str
) -> dict:
    """
    Verify experiment setup is configured for real execution.

    Args:
        baseline_folder: Path to baseline_comparison folder
        checkpoint_file: Path to 05_baseline_checkpoint.yaml
        experiment_brief_file: Path to 02c_experiment_brief.md (expected values)

    Returns:
        - detected: bool - Mock setup detected
        - violations: list - Detected issues
        - severity: str - CRITICAL/HIGH/MEDIUM/LOW/NONE
        - summary: str - Human-readable summary
    """
    # Read checkpoint and experiment brief
    checkpoint = Read(checkpoint_file) if file_exists(checkpoint_file) else None
    experiment_brief = Read(experiment_brief_file) if file_exists(experiment_brief_file) else None

    if not checkpoint:
        return {"detected": False, "violations": [], "severity": "NONE",
                "summary": "Checkpoint not found", "confidence": 0.0}

    # Build LLM prompt for pre-experiment verification
    prompt = build_pre_experiment_prompt(checkpoint, experiment_brief, baseline_folder)
    llm_response = llm_analyze(prompt)

    return parse_llm_response(llm_response)
```

### Pre-Experiment LLM Prompt

```python
def build_pre_experiment_prompt(checkpoint: str, experiment_brief: str, baseline_folder: str) -> str:
    """Build LLM prompt for pre-experiment mock detection."""

    return f"""## Phase 5 Pre-Experiment Reality Verification

You are verifying whether baseline comparison experiments are set up for REAL execution.

**Context:** This is Phase 5 (Baseline Comparison), NOT Phase 4.
- 6 experiments total: 3 Baselines × 2 Methods (baseline_original vs ours_injected)
- Mode B: Each baseline uses THEIR OWN model, dataset, config (baseline's environment)
- Only the ALGORITHM differs between runs (baseline's original vs our injected algorithm)
- Experiments should take significant time (hours to days for full training)

### 05_baseline_checkpoint.yaml (Experiment Setup)
```yaml
{checkpoint[:3000]}
```

### 02c_experiment_brief.md (Expected Values)
```markdown
{experiment_brief[:2000] if experiment_brief else "NOT PROVIDED"}
```

### Verification Questions:

1. **Runner Scripts Reality:**
   - Do runner scripts reference REAL dataset paths (not placeholder/mock)?
   - Are epochs/iterations realistic for full training?
   - Is batch size appropriate for real GPU training?

2. **Baseline Adaptation Reality:**
   - Are baseline repositories actually cloned and modified?
   - Do adaptation files reference real data loaders?
   - Is there evidence of real model loading?

3. **Fallback/Mock Indicators (CRITICAL):**
   - ⚠️ ANY mention of "mock", "fallback", "synthetic", "placeholder" in:
     - Runner scripts
     - Experiment plan
     - Checkpoint configuration
   - ⚠️ Suspiciously short expected duration (< 1 hour for full training)
   - ⚠️ Pre-defined result values in scripts

### Judgment Format:
**Verdict:** REAL_SETUP or MOCK_DETECTED
**Confidence:** (0.0 - 1.0)
**Issues Found:** (list of specific issues or "None")
**Severity:** CRITICAL/HIGH/MEDIUM/LOW/NONE
**Reasoning:** (detailed explanation)
"""
```

---

## 2. Post-Experiment Verification (Section 9.6.5)

### verify_experiment_results_reality()

Called after collecting comparison_data.csv. Compares actual results with expected values.

```python
def verify_experiment_results_reality(
    comparison_data_file: str,
    experiment_log_file: str,
    checkpoint_file: str,
    experiment_brief_file: str
) -> dict:
    """
    Verify experiment results are from real execution.

    Compares:
    - Expected values from 02c_experiment_brief.md
    - Actual results from comparison_data.csv
    - Execution evidence from experiment.log

    Args:
        comparison_data_file: Path to comparison_data.csv ({total_runs} rows)
        experiment_log_file: Path to experiment.log
        checkpoint_file: Path to 05_baseline_checkpoint.yaml
        experiment_brief_file: Path to 02c_experiment_brief.md

    Returns:
        - detected: bool - Mock results detected
        - violations: list - Detected issues
        - severity: str - CRITICAL/HIGH/MEDIUM/LOW/NONE
        - summary: str - Human-readable summary
    """
    # Read all files
    comparison_data = Read(comparison_data_file) if file_exists(comparison_data_file) else None
    experiment_log = Read(experiment_log_file, last_500_lines=True) if file_exists(experiment_log_file) else None
    checkpoint = Read(checkpoint_file) if file_exists(checkpoint_file) else None
    experiment_brief = Read(experiment_brief_file) if file_exists(experiment_brief_file) else None

    if not comparison_data:
        return {"detected": True, "violations": [{"description": "comparison_data.csv not found"}],
                "severity": "CRITICAL", "summary": "Results file missing"}

    # Build LLM prompt for post-experiment verification
    prompt = build_post_experiment_prompt(
        comparison_data, experiment_log, checkpoint, experiment_brief
    )
    llm_response = llm_analyze(prompt)

    return parse_llm_response(llm_response)
```

### Post-Experiment LLM Prompt

```python
def build_post_experiment_prompt(
    comparison_data: str,
    experiment_log: str,
    checkpoint: str,
    experiment_brief: str
) -> str:
    """Build LLM prompt for post-experiment mock detection."""

    return f"""## Phase 5 Post-Experiment Reality Verification

You are verifying whether baseline comparison results are from REAL experiments.

**Mode B Context:** {baselines_count} Baselines × {methods_per_baseline} Methods (baseline_original vs ours_injected) = {total_runs} runs
Each baseline uses THEIR OWN model, dataset, config. Only the algorithm differs.

**Critical Comparison:** Expected values (02c) vs Actual results (comparison_data.csv)

### comparison_data.csv (ACTUAL Results - {total_runs} rows expected)
```csv
{comparison_data[:2000]}
```

### experiment.log (Execution Evidence - last 500 lines)
```
{experiment_log[:3000] if experiment_log else "LOG NOT FOUND"}
```

### 02c_experiment_brief.md (EXPECTED Values)
```markdown
{experiment_brief[:2000] if experiment_brief else "NOT PROVIDED"}
```

### 05_baseline_checkpoint.yaml (Experiment Configuration)
```yaml
{checkpoint[:1500] if checkpoint else "NOT PROVIDED"}
```

### Verification Questions:

1. **Result Plausibility:**
   - Are metrics within expected ranges for the task?
   - Do different methods show meaningful variance?
   - Are "ours" results consistent with Phase 4 results?

2. **Training Evidence (from experiment.log):**
   - Is there evidence of actual training iterations?
   - Do logs show realistic epoch progression?
   - Is GPU memory usage visible in logs?
   - Are there realistic batch processing times?

3. **Suspicious Patterns (CRITICAL - Flag as MOCK_DETECTED):**
   - ⚠️ All methods have identical metrics (no variance between baseline vs ours)
   - ⚠️ Results too perfect (e.g., 99.9% accuracy)
   - ⚠️ Training completed impossibly fast (6 experiments in < 10 minutes)
   - ⚠️ No gradual loss decrease in logs
   - ⚠️ Pre-defined constant values (same number repeated)
   - ⚠️ Metrics don't match expected order of magnitude
   - ⚠️ Missing epochs/iterations in log progression

4. **Cross-Validation:**
   - Does "ours" performance match Phase 4 results (should be similar)?
   - Do baseline performances match known literature ranges?

### Judgment Format:
**Verdict:** REAL_EXPERIMENT or MOCK_DETECTED
**Confidence:** (0.0 - 1.0)
**Expected vs Actual Comparison:**
- Metric Range: [Expected] vs [Actual]
- Training Duration: [Expected] vs [Actual]
- Result Variance: [Expected variation] vs [Actual variation]
**Issues Found:** (list of specific issues or "None")
**Severity:** CRITICAL/HIGH/MEDIUM/LOW/NONE
**Reasoning:** (detailed explanation of why you reached this verdict)
"""
```

---

## 3. Response Parser

```python
def parse_llm_response(response: str) -> dict:
    """Parse LLM response into structured result."""
    import re

    # Extract verdict
    is_mock = "mock_detected" in response.lower()

    # Extract confidence
    conf_match = re.search(r"confidence[:\s]*(\d+\.?\d*)", response.lower())
    confidence = float(conf_match.group(1)) if conf_match else 0.5
    if confidence > 1: confidence /= 100

    # Extract severity
    severity = "NONE"
    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        if sev.lower() in response.lower():
            severity = sev
            break

    # Extract reasoning
    reasoning_match = re.search(r"reasoning[:\s]*(.+?)(?=\n\*\*|$)", response, re.I | re.DOTALL)
    reasoning = reasoning_match.group(1).strip()[:500] if reasoning_match else ""

    # Extract issues
    violations = []
    issues_match = re.search(r"issues found[:\s]*(.+?)(?=\n\*\*|$)", response, re.I | re.DOTALL)
    if issues_match and is_mock:
        for line in issues_match.group(1).split('\n'):
            if line.strip().startswith('-'):
                violations.append({
                    "description": line.strip()[1:].strip(),
                    "severity": severity
                })

    return {
        "detected": is_mock,
        "violations": violations,
        "violation_count": len(violations),
        "severity": severity if is_mock else "NONE",
        "summary": f"{'Mock detected' if is_mock else 'Real experiment'} ({confidence:.0%} confidence)",
        "llm_reasoning": reasoning,
        "confidence": confidence,
        "detection_context": "phase5_baseline_comparison",
        "method": "llm_verification"
    }
```

---

## 4. Return-to-Step-07 Logic

When mock is detected, return to adaptation coding (step-07) for fix.

```python
def handle_mock_detected(checkpoint_file: str, detection_result: dict, detection_phase: str):
    """
    Handle mock detection by returning to step-07 (Adaptation Coding).

    Args:
        checkpoint_file: Path to 05_baseline_checkpoint.yaml
        detection_result: Result from verify_*_reality() function
        detection_phase: "pre_experiment" or "post_experiment"
    """
    checkpoint = load_yaml(checkpoint_file)

    # Check retry limit
    retry_key = f"mock_{detection_phase}_retries"
    current_retries = checkpoint.get(retry_key, 0)
    max_retries = 3

    if current_retries >= max_retries:
        print(f"🚨 Max mock retries ({max_retries}) exceeded - marking as BLOCKED")
        checkpoint["mock_detection_blocked"] = True
        checkpoint["mock_detection_status"] = "BLOCKED_MAX_RETRIES"
        save_yaml(checkpoint, checkpoint_file)
        return {"action": "PROCEED_BLOCKED", "retries": current_retries}

    # Increment retry counter
    checkpoint[retry_key] = current_retries + 1
    checkpoint["return_reason"] = f"MOCK_DETECTED_{detection_phase.upper()}"
    checkpoint["current_step"] = 7 # Return to step-07

    # Log detection details
    checkpoint["mock_detection_history"] = checkpoint.get("mock_detection_history", [])
    checkpoint["mock_detection_history"].append({
        "phase": detection_phase,
        "result": detection_result,
        "timestamp": now(),
        "retry_number": current_retries + 1
    })

    save_yaml(checkpoint, checkpoint_file)

    print(f"""
🚨 MOCK DETECTED in {detection_phase}!

Summary: {detection_result['summary']}
Severity: {detection_result['severity']}
Confidence: {detection_result['confidence']:.0%}

Issues:
{chr(10).join(f" - {v['description']}" for v in detection_result.get('violations', []))}

🔄 Returning to Step 7 (Adaptation Coding) for fix...
   Attempt: {current_retries + 1}/{max_retries}
""")

    return {"action": "RETURN_TO_STEP_7", "retries": current_retries + 1}
```

---

## 5. Quick Reference for step-09-experiment.md

### Section 9.0 Usage (Pre-Experiment)

```python
# READ this reference file for complete verification logic
from experiment_mock_detection import verify_pre_experiment_reality, handle_mock_detected

result = verify_pre_experiment_reality(
    baseline_folder=baseline_folder,
    checkpoint_file=f"{baseline_folder}/05_baseline_checkpoint.yaml",
    experiment_brief_file=f"{hypothesis_folder}/02c_experiment_brief.md"
)

IF result["detected"]:
    handle_mock_detected(checkpoint_file, result, "pre_experiment")
    Load, read entire file, then execute: step-07-adaptation-coding.md
    EXIT
```

### Section 9.6.5 Usage (Post-Experiment)

```python
# READ this reference file for complete verification logic
from experiment_mock_detection import verify_experiment_results_reality, handle_mock_detected

result = verify_experiment_results_reality(
    comparison_data_file=f"{baseline_folder}/experiments/comparison_data.csv",
    experiment_log_file=f"{baseline_folder}/experiments/experiment.log",
    checkpoint_file=f"{baseline_folder}/05_baseline_checkpoint.yaml",
    experiment_brief_file=f"{hypothesis_folder}/02c_experiment_brief.md"
)

IF result["detected"]:
    handle_mock_detected(checkpoint_file, result, "post_experiment")
    Load, read entire file, then execute: step-07-adaptation-coding.md
    EXIT
```

---

## 6. Mock Detection Patterns (LLM Guidance)

### Flag as MOCK_DETECTED when:

| Pattern | Example | Severity |
|---------|---------|----------|
| Identical results for baseline vs ours | Both methods: accuracy = 0.95 (no difference) | CRITICAL |
| Suspiciously perfect metrics | accuracy = 0.9999 | HIGH |
| Impossibly fast training | 6 experiments in 5 minutes | CRITICAL |
| No training dynamics in logs | Loss constant, no epoch progression | HIGH |
| Pre-defined constant values | Same metric value repeated 6 times | CRITICAL |
| Missing experiment evidence | No GPU logs, no batch times | MEDIUM |
| Results don't match expected range | Expected: 80-90%, Actual: 15% | HIGH |

### Accept as REAL_EXPERIMENT when:

| Pattern | Example |
|---------|---------|
| Meaningful baseline vs ours variance | Baseline1: baseline=0.82, ours=0.87 (different) |
| Realistic training duration | 6 experiments over 6+ hours |
| Gradual loss decrease in logs | Epoch 1: 2.3, Epoch 50: 0.8, Epoch 100: 0.4 |
| GPU utilization evidence | "CUDA memory allocated: 4.2GB" |
| Consistent with Phase 4 | "Ours" matches Phase 4 results (±5%) |

---

## Related Files

| File | Purpose |
|------|---------|
| `step-09-experiment.md` | Main experiment step (references this) |
| `step-07-adaptation-coding.md` | Return target on mock detection |
| `helpers/mock_detection.md` | Phase 4 mock detection (reference) |
| `result-collection-guide.md` | How comparison_data.csv is built |
