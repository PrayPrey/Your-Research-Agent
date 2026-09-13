---
name: 'serena_memory_patterns'
description: 'Standardized patterns for saving and reading Serena Memory across phases for cross-phase persistence'
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'

# Exported Functions
exports:
  - save_failure_record
  - save_pivot_record
  - save_superseded_record
  - save_comparison_summary
  - save_limitation_record

# Called By
called_by:
  - 'phase4-coding/steps/step-06-gate-processing.md'
  - 'phase4-coding/steps/step-06b-reflection.md'
  - 'phase4-coding/steps/step-08-completion.md'
  - 'phase5-baseline-repo-comparison/steps/step-09-memory.md'
  - 'phase5-baseline-repo-comparison/steps/step-10-report.md'
---

# Serena Memory Patterns Helper Functions

> Standardized patterns for saving and reading Serena Memory across phases.
> Enables cross-phase persistence for failure analysis, pivot records, and lesson learning.

---

## Constants

### Memory File Naming Conventions

```python
# Memory file naming patterns
# NOTE: {run} suffix prevents overwrite when same hypothesis fails multiple times.
# Use _next_run_number() to determine {run} before writing.
MEMORY_FILE_PATTERNS = {
    # Phase 4 patterns (run-aware to prevent overwrite)
    "failure": "failure_{hypothesis_id}_run{run}.md",
    "pivot": "pivot_{old_id}_{new_id}.md",
    "superseded": "superseded_{hypothesis_id}.md",
    "limitation": "limitation_{hypothesis_id}_run{run}.md",

    # Phase 5 patterns (run-aware to prevent overwrite)
    "phase5_comparison": "phase5_comparison_{hypothesis_id}.md",
    "phase5_failure": "phase5_failure_{hypothesis_id}_run{run}.md",

    # Shared patterns
    "lessons": "lessons_{hypothesis_id}.md",
    "experiment_log": "experiment_log_{hypothesis_id}.md"
}

# Memory types for routing detection
MEMORY_TYPES = {
    "PHASE4_FAIL": ["failure_"],
    "PHASE4_PIVOT": ["pivot_"],
    "PHASE4_SUPERSEDED": ["superseded_"],
    "PHASE4_LIMITATION": ["limitation_"], # SHOULD_WORK gate limitation (optional learning)
    "PHASE5_PARTIAL": ["phase5_failure_"]
}
```

---

## Helper: _next_run_number

```python
def _next_run_number(prefix: str) -> int:
    """
    Determine the next run number for a memory file prefix.

    Calls mcp__serena__list_memories() and counts existing files
    matching the prefix to avoid overwriting previous records.

    Args:
        prefix: The memory file prefix to search for (e.g., "failure_h-e1")

    Returns:
        Next available run number (1-based)

    Example:
        # If "failure_h-e1_run1.md" and "failure_h-e1_run2.md" exist:
        _next_run_number("failure_h-e1") # returns 3

        # If no matching files exist:
        _next_run_number("failure_h-e1") # returns 1
    """
    memories = mcp__serena__list_memories() # returns list of memory names

    # Count existing files matching this prefix
    existing_runs = [m for m in memories if m.startswith(prefix)]
    return len(existing_runs) + 1
```

> **Compatibility Note:** Phase 0 and Phase 2A read ALL memory files via `list_memories()` → read all `.md`.
> They match by prefix (e.g., `"failure_"`), so `failure_h-e1_run1.md` and `failure_h-e1_run2.md`
> are both detected correctly. No changes needed in readers.

---

## Functions

### 1. save_failure_record

```python
def save_failure_record(
    hypothesis_id: str,
    phase: str,
    failure_type: str,
    performance_data: dict,
    root_causes: list,
    lessons_learned: list,
    phase_feedback: dict = None
) -> dict:
    """
    Save failure record to Serena Memory.

    Args:
        hypothesis_id: Hypothesis identifier
        phase: "Phase 4" or "Phase 5"
        failure_type: e.g., "WORSE_THAN_BASELINE", "IMPLEMENTATION_BUG"
        performance_data: Dict with metrics (ours_best, baseline_best, gap)
        root_causes: List of identified root causes
        lessons_learned: List of lessons
        phase_feedback: Optional feedback for next phase

    Returns:
        Dictionary containing:
            - memory_file: str - Created file name
            - success: bool
            - content: str - Content written

    Usage:
        result = save_failure_record(
            "h-e1", "Phase 5", "WORSE_THAN_BASELINE",
            {"ours_best": 0.82, "baseline_best": 0.85, "gap": -0.03},
            ["Mechanism ineffective at high LR"],
            ["Baseline uses better optimization"]
        )
    """
    from datetime import datetime

    if phase == "Phase 5":
        prefix = f"phase5_failure_{hypothesis_id}"
    else:
        prefix = f"failure_{hypothesis_id}"

    run = _next_run_number(prefix)
    memory_file = f"{prefix}_run{run}.md"

    gap = performance_data.get("gap", 0)
    percentage_gap = (gap / performance_data.get("baseline_best", 1)) * 100 if performance_data.get("baseline_best") else 0

    content = f"""# {phase} Failure Record: {hypothesis_id} (Run {run})

**Date:** {datetime.now().isoformat()}
**Hypothesis:** {hypothesis_id}
**Run:** {run}
**Final Status:** PARTIAL/FAIL
**Failure Type:** {failure_type}

## Performance Gap

| Metric | Ours | Baseline | Gap |
|--------|------|----------|-----|
| Best Metric | {performance_data.get('ours_best', 'N/A')} | {performance_data.get('baseline_best', 'N/A')} | {gap:.4f} ({percentage_gap:.1f}%) |

## Root Cause Analysis

{chr(10).join(f'- {cause}' for cause in root_causes)}

## Lessons Learned

{chr(10).join(f'{i+1}. {lesson}' for i, lesson in enumerate(lessons_learned))}

"""

    if phase_feedback:
        content += f"""## Feedback for Next Phase

### Suggested Modifications
{chr(10).join(f'- {s}' for s in phase_feedback.get('suggestions', []))}

### What NOT To Do
{chr(10).join(f'- {a}' for a in phase_feedback.get('avoid', []))}

### What Showed Promise
{chr(10).join(f'- {p}' for p in phase_feedback.get('promise', []))}

"""

    content += f"""---
*For cross-phase reference*
*Written at: {datetime.now().isoformat()}*
"""

    # Write to Serena Memory
    mcp__serena__write_memory(
        memory_file_name=memory_file,
        content=content
    )

    return {
        "memory_file": memory_file,
        "success": True,
        "content": content
    }
```

### 2. save_pivot_record

```python
def save_pivot_record(
    old_hypothesis_id: str,
    new_hypothesis_id: str,
    pivot_reason: str,
    modifications: list,
    preserved_elements: list,
    partial_results: dict = None
) -> dict:
    """
    Save pivot record when PARTIAL leads to hypothesis modification.

    Args:
        old_hypothesis_id: Original hypothesis ID
        new_hypothesis_id: New hypothesis ID after pivot
        pivot_reason: Why the pivot was necessary
        modifications: What changed
        preserved_elements: What was kept
        partial_results: Optional partial results to preserve

    Returns:
        Dictionary containing memory file info

    Usage:
        result = save_pivot_record(
            "h-e1", "h-e1-v2",
            "PARTIAL result - mechanism needs adjustment",
            ["Changed loss function", "Adjusted learning rate range"],
            ["Core model architecture", "Dataset setup"]
        )
    """
    from datetime import datetime

    memory_file = f"pivot_{old_hypothesis_id}_{new_hypothesis_id}.md"

    content = f"""# Hypothesis Pivot Record

**Date:** {datetime.now().isoformat()}
**From:** {old_hypothesis_id}
**To:** {new_hypothesis_id}

## Pivot Reason

{pivot_reason}

## What Changed

{chr(10).join(f'- {m}' for m in modifications)}

## What Was Preserved

{chr(10).join(f'- {p}' for p in preserved_elements)}

"""

    if partial_results:
        content += f"""## Partial Results Preserved

| Metric | Value | Notes |
|--------|-------|-------|
"""
        for metric, value in partial_results.items():
            content += f"| {metric} | {value} | From {old_hypothesis_id} |\n"

    content += f"""
## Lineage

```
{old_hypothesis_id}
    └── (PIVOT: {pivot_reason[:50]}...)
        └── {new_hypothesis_id}
```

---
*Pivot recorded at: {datetime.now().isoformat()}*
"""

    mcp__serena__write_memory(
        memory_file_name=memory_file,
        content=content
    )

    return {
        "memory_file": memory_file,
        "success": True,
        "old_id": old_hypothesis_id,
        "new_id": new_hypothesis_id
    }
```

### 3. save_superseded_record

```python
def save_superseded_record(
    hypothesis_id: str,
    superseded_by: str,
    supersede_reason: str,
    compatibility_assessment: dict,
    cascade_targets: list = None
) -> dict:
    """
    Save superseded record when hypothesis is replaced.

    Args:
        hypothesis_id: Superseded hypothesis ID
        superseded_by: New hypothesis ID that replaces it
        supersede_reason: Why it was superseded
        compatibility_assessment: LLM assessment results
        cascade_targets: Other hypotheses affected

    Returns:
        Dictionary containing memory file info

    Usage:
        result = save_superseded_record(
            "h-e1", "Phase2A-v2",
            "Approach fundamentally incompatible with dependents",
            {"score": 0.3, "recommendation": "SUPERSEDE"},
            ["h-e2", "h-e3"] # Dependents marked CASCADE_SUPERSEDED
        )
    """
    from datetime import datetime

    memory_file = f"superseded_{hypothesis_id}.md"

    content = f"""# Superseded Hypothesis Record

**Date:** {datetime.now().isoformat()}
**Hypothesis:** {hypothesis_id}
**Superseded By:** {superseded_by}
**Status:** SUPERSEDED

## Supersede Reason

{supersede_reason}

## Compatibility Assessment

| Factor | Score/Result |
|--------|--------------|
| Compatibility Score | {compatibility_assessment.get('score', 'N/A')} |
| Recommendation | {compatibility_assessment.get('recommendation', 'N/A')} |
| Reasoning | {compatibility_assessment.get('reasoning', 'N/A')[:200]}... |

"""

    if cascade_targets:
        content += f"""## Cascade Effects

The following hypotheses were marked CASCADE_SUPERSEDED:

{chr(10).join(f'- {t}' for t in cascade_targets)}

These will be re-evaluated when new hypothesis is ready.

"""

    content += f"""## Timeline

1. Original hypothesis: {hypothesis_id}
2. PARTIAL result detected
3. LLM assessment: compatibility_score = {compatibility_assessment.get('score', 'N/A')}
4. Decision: SUPERSEDE (not SELF_MODIFY)
5. New direction: {superseded_by}

---
*Superseded at: {datetime.now().isoformat()}*
"""

    mcp__serena__write_memory(
        memory_file_name=memory_file,
        content=content
    )

    return {
        "memory_file": memory_file,
        "success": True,
        "cascade_count": len(cascade_targets) if cascade_targets else 0
    }
```

### 4. save_comparison_summary

```python
def save_comparison_summary(
    hypothesis_id: str,
    gate_result: str,
    comparison_data: dict,
    hypothesis_journey: dict = None
) -> dict:
    """
    Save comparison summary (always, regardless of gate result).

    Args:
        hypothesis_id: Hypothesis identifier
        gate_result: "PASS" or "PARTIAL"
        comparison_data: Performance comparison data
        hypothesis_journey: Optional hypothesis version history

    Returns:
        Dictionary containing memory file info

    Usage:
        result = save_comparison_summary(
            "h-e1", "PASS",
            {"ours_best": 0.88, "baseline_best": 0.85, "winner": "ours"},
            {"version": 2, "modifications": 3}
        )
    """
    from datetime import datetime

    memory_file = f"phase5_comparison_{hypothesis_id}.md"

    winner = "Ours" if comparison_data.get("ours_best", 0) > comparison_data.get("baseline_best", 0) else "Baseline"

    content = f"""# Phase 5 Comparison Summary: {hypothesis_id}

**Date:** {datetime.now().isoformat()}
**Gate Result:** {gate_result}

## Performance Comparison

| Metric | Ours | Baseline | Winner |
|--------|------|----------|--------|
| Best Metric | {comparison_data.get('ours_best', 'N/A')} | {comparison_data.get('baseline_best', 'N/A')} | {winner} |

## Gate Evaluation

- **Result:** {gate_result}
- **Criteria:** Win ≥2/3 baselines on ≥1/2 datasets
- **Satisfied:** {'Yes' if gate_result == 'PASS' else 'No'}

"""

    if hypothesis_journey:
        content += f"""## Hypothesis Journey

- **Version:** v{hypothesis_journey.get('version', 1)}
- **Total Modifications:** {hypothesis_journey.get('modifications', 0)}
- **Lessons Applied:** {hypothesis_journey.get('lessons_count', 0)}

"""

    if comparison_data.get("win_matrix"):
        content += """## Win Matrix Summary

"""
        for dataset, results in comparison_data["win_matrix"].items():
            wins = sum(results.values())
            content += f"- {dataset.capitalize()}: {wins}/{len(results)} baselines beaten\n"

    content += f"""
---
*Summary generated at: {datetime.now().isoformat()}*
"""

    mcp__serena__write_memory(
        memory_file_name=memory_file,
        content=content
    )

    return {
        "memory_file": memory_file,
        "success": True,
        "gate_result": gate_result
    }
```

### 5. save_limitation_record

```python
def save_limitation_record(
    hypothesis_id: str,
    gate_type: str,
    limitation_reason: str,
    failed_checks: list,
    partial_results: dict = None,
    experiment_summary: str = None
) -> dict:
    """
    Save limitation record when SHOULD_WORK gate fails.

    Unlike failure_record (which indicates fundamental failure requiring Phase 0),
    limitation_record indicates an acceptable limitation that doesn't block
    the pipeline but should inform future research attempts.

    Args:
        hypothesis_id: Hypothesis identifier (e.g., "h-m2")
        gate_type: Gate type (typically "SHOULD_WORK")
        limitation_reason: Why the limitation was recorded
        failed_checks: List of failed validation checks
        partial_results: Optional dict with partial success metrics
        experiment_summary: Optional summary of experiment results

    Returns:
        Dictionary containing:
            - memory_file: str - Created file name
            - success: bool
            - content: str - Content written

    Usage:
        result = save_limitation_record(
            "h-m2",
            "SHOULD_WORK",
            "No specific improvement identified after 3 retries",
            ["auxiliary_loss_convergence", "optional_metric_threshold"],
            {"best_metric": 0.72, "target": 0.80}
        )
    """
    from datetime import datetime

    prefix = f"limitation_{hypothesis_id}"
    run = _next_run_number(prefix)
    memory_file = f"{prefix}_run{run}.md"

    content = f"""# Limitation Record: {hypothesis_id} (Run {run})

**Date:** {datetime.now().isoformat()}
**Hypothesis:** {hypothesis_id}
**Run:** {run}
**Gate Type:** {gate_type}
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

{limitation_reason}

## Failed Checks

{chr(10).join(f'- {check}' for check in failed_checks)}

"""

    if partial_results:
        content += f"""## Partial Results

| Metric | Value |
|--------|-------|
"""
        for metric, value in partial_results.items():
            content += f"| {metric} | {value} |\n"
        content += "\n"

    if experiment_summary:
        content += f"""## Experiment Summary

{experiment_summary}

"""

    content += f"""## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded to Phase 5 with this limitation noted.

Future research attempts should consider:
1. The specific checks that failed
2. Whether the limitation is fundamental or circumstantial
3. Alternative approaches that might avoid this limitation

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0 (from Phase 5 PARTIAL),
  this limitation informs brainstorming to avoid similar issues
- **Phase 6 Discussion:** Limitation is included in paper's Limitations section

---
*Limitation recorded at: {datetime.now().isoformat()}*
*For cross-phase reference*
"""

    # Write to Serena Memory
    mcp__serena__write_memory(
        memory_file_name=memory_file,
        content=content
    )

    return {
        "memory_file": memory_file,
        "success": True,
        "content": content
    }
```

---

## Memory File Types Summary

> **Note:** Both Phase 0 and Phase 2A read ALL memory files via `list_memories()` → read all `.md`.
> The "Primary Reader" column indicates which phase most commonly acts on each type.

| Pattern | Phase | When Created | Primary Reader | Read By |
|---------|-------|--------------|----------------|---------|
| `failure_{id}_run{N}.md` | Phase 4 | FAIL gate | Phase 0 | Phase 0, Phase 2A |
| `pivot_{old}_{new}.md` | Phase 4 | PARTIAL + SELF_MODIFY | Phase 2A | Phase 0, Phase 2A |
| `superseded_{id}.md` | Phase 4 | PARTIAL + SUPERSEDE | Phase 2A | Phase 0, Phase 2A |
| `limitation_{id}_run{N}.md` | Phase 4 | SHOULD_WORK FAIL | Phase 6 | Phase 0, Phase 2A, Phase 6 Discussion |
| `phase5_comparison_{id}.md` | Phase 5 | Always | Any | Phase 0, Phase 2A, Any |
| `phase5_failure_{id}_run{N}.md` | Phase 5 | PARTIAL gate | Phase 0 | Phase 0, Phase 2A |

> **Run-aware naming:** `failure_`, `limitation_`, `phase5_failure_` patterns include `_run{N}` suffix
> to prevent overwriting previous failure records when the same hypothesis fails multiple times.
> Readers match by prefix (`"failure_"`), so all runs are detected automatically.
