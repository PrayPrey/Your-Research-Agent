---
name: 'multi_comparison_gate'
description: 'Mode B: Reusable functions for per-baseline gate evaluation in Phase 5 (ours vs baseline on their turf)'
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'

# Exported Functions
exports:
  - compute_win_matrix # Mode B: per-baseline win/lose
  - compute_per_baseline_wins # Mode B: win count + threshold check
  - compute_overall_gate # Mode B: overall gate result
  - generate_gate_summary_table # Mode B: markdown summary
  - evaluate_mode_b_gate # Mode B: main orchestrator
  - classify_failure # Mode B: failure classification

# Called By
called_by:
  - 'phase5-baseline-repo-comparison/steps/step-10-report.md'
  - 'phase5-baseline-repo-comparison/steps/step-10a-gate-evaluation.md'
---

# Multi-Comparison Gate Helper Functions (Mode B)

> Mode B gate evaluation: Compare ours_injected vs baseline_original on each baseline's own environment.
> Implements the DETERMINES_SUCCESS gate: Win ≥threshold baselines (ours > baseline on their turf).
> Threshold comes from workflow.yaml → checkpoint → step-10a parameter.

---

## Constants

### Gate Thresholds

```python
# Gate configuration (Mode B)
# These are NOT hardcoded — they MUST be loaded from checkpoint at runtime.
# SSoT path: workflow.yaml → step-01-init → checkpoint → step-10a parameter
#
# checkpoint keys used:
# checkpoint["workflow_config"]["gate"]["baseline_win_threshold"] → e.g., "1/4"
# checkpoint["workflow_config"]["gate"]["min_baselines_to_beat"] → e.g., 1
# checkpoint["baselines_count"] → e.g., 1
#
# These functions require explicit parameters — no implicit fallback defaults.
# If caller omits baseline_threshold, raise an error instead of using stale defaults.
```

---

## Functions

### 1. compute_win_matrix

```python
def compute_win_matrix(
    comparison_data_path: str,
    baselines: list
) -> dict:
    """
    Compute win/lose for each baseline (ours_injected vs baseline_original on their turf).

    Args:
        comparison_data_path: Path to comparison_data.csv
        baselines: List of baseline repo names (e.g., ["repo1", "repo2", "repo3"])

    Returns:
        Dictionary containing:
            - win_matrix: dict[baseline_repo] = True/False
            - details: list of per-baseline comparison details

    Usage:
        result = compute_win_matrix(
            "experiments/comparison_data.csv",
            ["repo1", "repo2", "repo3"]
        )
        print(f"Win matrix: {result['win_matrix']}")
    """
    import pandas as pd

    df = pd.read_csv(comparison_data_path)

    win_matrix = {} # dict[baseline_repo] = True/False
    details = []

    for baseline in baselines:
        baseline_df = df[df["baseline_repo"] == baseline]
        baseline_result = baseline_df[baseline_df["method"] == "baseline"]["primary_metric"].values[0]
        ours_result = baseline_df[baseline_df["method"] == "ours"]["primary_metric"].values[0]

        win = ours_result > baseline_result
        win_matrix[baseline] = win

        details.append({
            "baseline_repo": baseline,
            "baseline_model": baseline_df["baseline_model"].values[0],
            "baseline_dataset": baseline_df["baseline_dataset"].values[0],
            "baseline_result": baseline_result,
            "ours_result": ours_result,
            "winner": "ours" if win else baseline,
            "improvement": f"{((ours_result - baseline_result) / baseline_result * 100):+.1f}%",
            "delta": ours_result - baseline_result
        })

    return {
        "win_matrix": win_matrix, # dict[baseline] = True/False
        "details": details # per-baseline comparison details
    }
```

### 2. compute_per_baseline_wins

```python
def compute_per_baseline_wins(
    win_matrix: dict,
    threshold: int = None
) -> dict:
    """
    Count baselines beaten and check if threshold is met.

    Args:
        win_matrix: Result from compute_win_matrix()["win_matrix"]
                    dict[baseline_repo] = True/False
        threshold: Minimum baselines to beat (REQUIRED — from checkpoint)

    Returns:
        Dictionary containing:
            - win_count: Number of baselines beaten
            - total_baselines: Total number of baselines
            - threshold_met: True if win_count >= threshold
            - baselines_beaten: List of beaten baseline names
            - baselines_lost_to: List of baseline names we lost to
            - threshold: Threshold used

    Usage:
        result = compute_per_baseline_wins(win_matrix, threshold=2)
        print(f"Beat {result['win_count']}/{result['total_baselines']} baselines")
    """
    if threshold is None:
        raise ValueError(
            "threshold is required — load from checkpoint.workflow_config.gate.min_baselines_to_beat"
        )

    win_count = sum(win_matrix.values())
    threshold_met = win_count >= threshold

    baselines_beaten = [b for b, won in win_matrix.items() if won]
    baselines_lost_to = [b for b, won in win_matrix.items() if not won]

    return {
        "win_count": win_count,
        "total_baselines": len(win_matrix),
        "threshold_met": threshold_met,
        "baselines_beaten": baselines_beaten,
        "baselines_lost_to": baselines_lost_to,
        "threshold": threshold
    }
```

### 3. compute_overall_gate

```python
def compute_overall_gate(
    per_baseline: dict
) -> dict:
    """
    Determine overall gate result from per-baseline wins.

    Args:
        per_baseline: Result from compute_per_baseline_wins()

    Returns:
        Dictionary containing:
            - overall_passed: True if gate passes
            - gate_result: "PASS" or "PARTIAL"
            - win_count: Number of baselines beaten
            - total_baselines: Total baselines
            - baselines_beaten: List of beaten baselines
            - baselines_lost_to: List of baselines we lost to
            - summary: Human-readable summary

    Usage:
        result = compute_overall_gate(per_baseline)
        if result["overall_passed"]:
            print("DETERMINES_SUCCESS: PASS")
    """
    overall_passed = per_baseline["threshold_met"]
    gate_result = "PASS" if overall_passed else "PARTIAL"
    win_count = per_baseline["win_count"]
    total = per_baseline["total_baselines"]

    if overall_passed:
        summary = f"PASS: Beat {win_count}/{total} baselines on their own turf"
    else:
        summary = f"PARTIAL: Only beat {win_count}/{total} baselines (need ≥{per_baseline['threshold']})"

    return {
        "overall_passed": overall_passed,
        "gate_result": gate_result,
        "win_count": win_count,
        "total_baselines": total,
        "baselines_beaten": per_baseline["baselines_beaten"],
        "baselines_lost_to": per_baseline["baselines_lost_to"],
        "summary": summary
    }
```

### 4. generate_gate_summary_table

```python
def generate_gate_summary_table(
    win_result: dict,
    per_baseline: dict,
    overall: dict
) -> str:
    """
    Generate markdown table summarizing Mode B gate evaluation.

    Args:
        win_result: Result from compute_win_matrix() (contains win_matrix and details)
        per_baseline: Result from compute_per_baseline_wins()
        overall: Result from compute_overall_gate()

    Returns:
        Markdown table string

    Usage:
        table = generate_gate_summary_table(win_result, per_baseline, overall)
        print(table)
    """
    lines = []

    # Header
    lines.append("### Gate Result Summary")
    lines.append("")
    lines.append("| Baseline | Model | Dataset | Winner | Improvement |")
    lines.append("|----------|-------|---------|--------|-------------|")

    # Per-baseline rows
    for detail in win_result["details"]:
        winner_str = "✅ Ours" if detail["winner"] == "ours" else f"❌ {detail['baseline_repo']}"
        lines.append(
            f"| {detail['baseline_repo']} "
            f"| {detail['baseline_model']} "
            f"| {detail['baseline_dataset']} "
            f"| {winner_str} "
            f"| {detail['improvement']} |"
        )

    lines.append("")
    passed_str = "✅ PASS" if overall["overall_passed"] else "❌ PARTIAL"
    lines.append(
        f"**Win Count:** {overall['win_count']}/{overall['total_baselines']} "
        f"| **Threshold:** ≥{per_baseline['threshold']} "
        f"| **Result:** {passed_str}"
    )

    return "\n".join(lines)
```

### 5. evaluate_mode_b_gate (Main Orchestrator)

```python
def evaluate_mode_b_gate(
    comparison_data_path: str,
    baselines: list,
    baseline_threshold: int = None
) -> dict:
    """
    Main function: Complete Mode B gate evaluation.

    This orchestrates the full gate evaluation:
    1. Compute win/lose per baseline (ours vs baseline on their turf)
    2. Count wins and check threshold
    3. Determine overall gate result
    4. Generate summary table
    5. Prepare verification_state updates

    Args:
        comparison_data_path: Path to comparison_data.csv
        baselines: List of baseline repo names
        baseline_threshold: Min baselines to beat (REQUIRED — from checkpoint)

    Returns:
        Dictionary containing:
            - gate_result: "PASS" or "PARTIAL"
            - overall_passed: bool
            - win_matrix: {win_matrix, details} from compute_win_matrix()
            - per_baseline: {win_count, threshold_met, ...} from compute_per_baseline_wins()
            - overall: {gate_result, summary, ...} from compute_overall_gate()
            - summary_table: markdown string
            - verification_state_updates: dict for verification_state.yaml
            - details: per-baseline detail list

    Usage:
        result = evaluate_mode_b_gate(
            "experiments/comparison_data.csv",
            ["repo1", "repo2", "repo3"],
            baseline_threshold=2
        )
        if result["gate_result"] == "PASS":
            print("Hypothesis validated!")
    """
    if baseline_threshold is None:
        raise ValueError(
            "baseline_threshold is required — load from checkpoint.workflow_config.gate.min_baselines_to_beat"
        )

    # Step 1: Compute win/lose per baseline
    win_result = compute_win_matrix(comparison_data_path, baselines)

    # Step 2: Count wins and check threshold
    per_baseline = compute_per_baseline_wins(win_result["win_matrix"], baseline_threshold)

    # Step 3: Determine gate result
    overall = compute_overall_gate(per_baseline)

    # Step 4: Generate summary table
    summary_table = generate_gate_summary_table(win_result, per_baseline, overall)

    # Step 5: Build verification_state updates (Mode B structure)
    verification_updates = {
        "main_hypothesis.baseline_comparison.gate": {
            "type": "DETERMINES_SUCCESS",
            "criteria": f"win ≥{baseline_threshold}/{len(baselines)} baselines (ours > baseline on their turf)",
            "satisfied": overall["overall_passed"],
            "result": overall["gate_result"]
        },
        "main_hypothesis.baseline_comparison.per_baseline_results": win_result["details"],
        "main_hypothesis.baseline_comparison.aggregate_results": {
            "baselines_won": f"{overall['win_count']}/{overall['total_baselines']}",
            "threshold_met": overall["overall_passed"]
        }
    }

    return {
        "gate_result": overall["gate_result"], # "PASS" or "PARTIAL"
        "overall_passed": overall["overall_passed"], # bool
        "win_matrix": win_result, # {win_matrix, details}
        "per_baseline": per_baseline, # {win_count, threshold_met, ...}
        "overall": overall, # {gate_result, summary, ...}
        "summary_table": summary_table, # markdown string
        "verification_state_updates": verification_updates,
        "details": win_result["details"] # per-baseline detail list
    }
```

### 6. classify_failure

```python
def classify_failure(
    gate_result: dict,
    ours_best: float,
    baseline_best: float
) -> dict:
    """
    Classify the failure type when gate is PARTIAL (Mode B).

    Args:
        gate_result: Result from evaluate_mode_b_gate()
        ours_best: Our best metric value
        baseline_best: Best baseline metric value

    Returns:
        Dictionary containing:
            - failure_type: Classification string
            - severity: "HIGH", "MEDIUM", "LOW"
            - gap: Numeric gap (ours - baseline)
            - percentage_gap: Gap as percentage
            - root_causes: List of probable causes
            - recommendations: List of recommendations
            - baselines_lost_to: List of baselines we lost to

    Usage:
        if gate_result["gate_result"] == "PARTIAL":
            failure = classify_failure(gate_result, ours_best, baseline_best)
            print(f"Failure type: {failure['failure_type']}")
    """
    gap = ours_best - baseline_best
    percentage_gap = (gap / baseline_best) * 100 if baseline_best != 0 else 0

    baselines_lost_to = gate_result["overall"]["baselines_lost_to"]

    # Determine failure type based on number of baselines lost to
    if len(baselines_lost_to) == gate_result["overall"]["total_baselines"]:
        # Lost to ALL baselines
        failure_type = "COMPLETE_FAILURE"
        severity = "HIGH"
    elif len(baselines_lost_to) >= 2:
        # Lost to 2+ baselines
        failure_type = "CONSISTENT_UNDERPERFORMANCE"
        severity = "HIGH"
    else:
        # Lost to 1 baseline
        if abs(percentage_gap) > 10:
            failure_type = "WORSE_THAN_BASELINES"
            severity = "MEDIUM"
        else:
            failure_type = "MARGINAL_LOSS"
            severity = "LOW"

    # Generate root causes based on failure pattern
    root_causes = []
    recommendations = []

    if failure_type == "COMPLETE_FAILURE":
        root_causes.append("Hypothesis mechanism may be fundamentally flawed")
        root_causes.append("Our approach may not generalize across baseline environments")
        recommendations.append("Return to Phase 0 for completely new research direction")

    elif failure_type == "CONSISTENT_UNDERPERFORMANCE":
        root_causes.append("Our method loses to most baselines on their own turf")
        root_causes.append("May be missing key optimization techniques from baselines")
        recommendations.append("Analyze what makes winning baselines better")
        recommendations.append("Consider hybrid approach combining best of both")

    elif failure_type == "WORSE_THAN_BASELINES":
        root_causes.append(f"Significant performance gap ({percentage_gap:.1f}%)")
        root_causes.append("Baseline-specific weaknesses detected")
        recommendations.append("Investigate baseline characteristics causing failure")

    elif failure_type == "MARGINAL_LOSS":
        root_causes.append(f"Small performance gap ({percentage_gap:.1f}%)")
        root_causes.append("May be within variance - needs statistical significance test")
        recommendations.append("Consider running more seeds for statistical power")

    return {
        "failure_type": failure_type,
        "severity": severity,
        "gap": gap,
        "percentage_gap": percentage_gap,
        "root_causes": root_causes,
        "recommendations": recommendations,
        "baselines_lost_to": baselines_lost_to
    }
```

---

## Gate Logic Summary

> **Threshold source:** `workflow.yaml` → `gate.criteria.mode_b_comparison.baseline_win_threshold`
> Propagation: workflow.yaml → step-01-init → checkpoint.workflow_config.gate.min_baselines_to_beat → step-10a → evaluate_mode_b_gate(baseline_threshold=N)

| Step | Calculation | Threshold |
|------|-------------|-----------|
| 1. Win Matrix | Compare ours vs baseline per baseline_repo | - |
| 2. Per-Baseline | Count baselines beaten | ≥ `baseline_threshold` (from workflow.yaml) |

| Result | Condition | Action |
|--------|-----------|--------|
| PASS | win_count ≥ baseline_threshold | → Phase 6 |
| PARTIAL | win_count < baseline_threshold | → Phase 0 |
