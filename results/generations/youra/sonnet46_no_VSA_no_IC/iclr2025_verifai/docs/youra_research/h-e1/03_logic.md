# Logic Design: H-E1

**Hypothesis:** H-E1 — EvalPlus Failure Set Data Integrity Verification
**Type:** EXISTENCE (PoC)
**Date:** 2026-08-22
**Applied:** assertion-guard pattern, early-exit verification pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; no prior codebase in scope for H-E1.

---

## Subtask Breakdown

Budget: 4 subtasks covering A-2 (Data Loader, complexity 9) and A-4 (Figure Generator, complexity 10).

---

## L-A2-1: `data_loader.load_failures`

**Parent Epic:** A-2 (Data Loader, complexity 9)

### Signature

```python
def load_failures(archive: str = ARCHIVE) -> tuple[dict[str, dict], dict[str, dict]]:
    """Load h-e1 Run 2 eval results and extract failure records.

    Args:
        archive: Path to directory containing JSON eval result files.

    Returns:
        (he_failures, mbpp_failures): dicts mapping task_id -> first solution record
        for all tasks where plus_status == "fail".

    Raises:
        FileNotFoundError: if JSON files not found at archive path.
        KeyError: if JSON schema missing "eval" top-level key.
    """
```

### Pseudo-code

```python
def load_failures(archive=ARCHIVE):
    he_path = Path(archive) / HE_FILE
    mbpp_path = Path(archive) / MBPP_FILE

    if not he_path.exists():
        raise FileNotFoundError(f"HE+ results not found: {he_path}")
    if not mbpp_path.exists():
        raise FileNotFoundError(f"MBPP+ results not found: {mbpp_path}")

    with open(he_path) as f:
        he_raw = json.load(f)["eval"]      # {task_id: [record, ...]}
    with open(mbpp_path) as f:
        mbpp_raw = json.load(f)["eval"]

    he_failures = {tid: recs[0] for tid, recs in he_raw.items()
                   if recs and recs[0]["plus_status"] == "fail"}
    mbpp_failures = {tid: recs[0] for tid, recs in mbpp_raw.items()
                     if recs and recs[0]["plus_status"] == "fail"}

    return he_failures, mbpp_failures
```

### Edge Cases
- Empty `recs` list: guarded by `recs and` check
- Missing `"eval"` key: raises `KeyError` (caller logs and marks gate FAIL)
- Non-existent archive dir: raises `FileNotFoundError` (caller catches)

---

## L-A2-2: `data_loader.verify_fields`

**Parent Epic:** A-2 (Data Loader, complexity 9)

### Signature

```python
def verify_fields(failures: dict[str, dict]) -> None:
    """Assert solution and plus_fail_tests present and non-empty for every record.

    Args:
        failures: dict mapping task_id -> solution record (from load_failures).

    Raises:
        AssertionError: with task_id if any field is missing or empty.
    """
```

### Pseudo-code

```python
def verify_fields(failures):
    for tid, rec in failures.items():
        assert rec.get("solution"), \
            f"Empty/missing solution for {tid}"
        assert rec.get("plus_fail_tests"), \
            f"Empty/missing plus_fail_tests for {tid}"
```

### Edge Cases
- `solution` present but empty string: `assert rec.get("solution")` catches it (empty string is falsy)
- `plus_fail_tests` is `[]`: `assert rec.get("plus_fail_tests")` catches it (empty list is falsy)
- `plus_fail_tests` is `None`: same guard

---

## L-A4-1: `figure_generator.plot_gate_metrics`

**Parent Epic:** A-4 (Figure Generator, complexity 10)

### Signature

```python
def plot_gate_metrics(
    he_count: int,
    mbpp_count: int,
    output_dir: str = FIGURES_DIR,
) -> Path:
    """Bar chart comparing actual vs expected failure counts.

    Args:
        he_count: Actual HumanEval+ failure count (expected 34).
        mbpp_count: Actual MBPP+ failure count (expected 100).
        output_dir: Directory to save PNG.

    Returns:
        Path to saved figure.
    """
```

### Pseudo-code

```python
def plot_gate_metrics(he_count, mbpp_count, output_dir=FIGURES_DIR):
    labels = ["HE+ Failures", "MBPP+ Failures", "Total"]
    actual  = [he_count, mbpp_count, he_count + mbpp_count]
    expected = [34, 100, 134]

    x = np.arange(len(labels))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - width/2, actual,   width, label="Actual",   color="#2196F3")
    ax.bar(x + width/2, expected, width, label="Expected", color="#4CAF50", alpha=0.7)

    ax.set_ylabel("Count")
    ax.set_title("H-E1 Gate Metrics: Actual vs Expected Failure Counts")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    for i, (a, e) in enumerate(zip(actual, expected)):
        match = "✓" if a == e else "✗"
        ax.annotate(f"{a} {match}", xy=(x[i] - width/2, a), ha="center", va="bottom")

    out = Path(output_dir) / "gate_metrics.png"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out
```

---

## L-A4-2: `figure_generator.plot_completeness_matrix`

**Parent Epic:** A-4 (Figure Generator, complexity 10)

### Signature

```python
def plot_completeness_matrix(
    he_failures: dict[str, dict],
    mbpp_failures: dict[str, dict],
    he_problems: dict[str, dict],
    mbpp_problems: dict[str, dict],
    output_dir: str = FIGURES_DIR,
) -> Path:
    """Heatmap: 134 tasks × {solution_present, plus_fail_tests_present, task_in_api}.

    Args:
        he_failures: HE+ failure records from data_loader.
        mbpp_failures: MBPP+ failure records from data_loader.
        he_problems: EvalPlus HE+ dataset from api_verifier.
        mbpp_problems: EvalPlus MBPP+ dataset from api_verifier.
        output_dir: Directory to save PNG.

    Returns:
        Path to saved figure.
    """
```

### Pseudo-code

```python
def plot_completeness_matrix(he_failures, mbpp_failures,
                              he_problems, mbpp_problems,
                              output_dir=FIGURES_DIR):
    all_failures = {**he_failures, **mbpp_failures}
    all_problems = {**he_problems, **mbpp_problems}

    task_ids = sorted(all_failures.keys())
    checks = ["solution_present", "plus_fail_tests_present", "task_in_api"]

    # Build binary matrix (134 × 3)
    matrix = np.zeros((len(task_ids), 3), dtype=int)
    for i, tid in enumerate(task_ids):
        rec = all_failures[tid]
        matrix[i, 0] = 1 if rec.get("solution") else 0
        matrix[i, 1] = 1 if rec.get("plus_fail_tests") else 0
        matrix[i, 2] = 1 if tid in all_problems else 0

    fig, ax = plt.subplots(figsize=(6, 16))
    ax.imshow(matrix, aspect="auto", cmap="RdYlGn", vmin=0, vmax=1)
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(checks, rotation=20, ha="right")
    ax.set_yticks([])
    ax.set_title(f"Data Completeness Matrix (134 tasks × 3 checks)\nAll green = PASS")

    out = Path(output_dir) / "completeness_matrix.png"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out
```

---

## Supporting Functions (no dedicated subtask — low complexity)

### `api_verifier.verify_api_accessible`

```python
def verify_api_accessible() -> tuple[dict, dict]:
    from evalplus.data import get_human_eval_plus, get_mbpp_plus
    he_problems = get_human_eval_plus()
    mbpp_problems = get_mbpp_plus()
    assert he_problems, "get_human_eval_plus() returned empty"
    assert mbpp_problems, "get_mbpp_plus() returned empty"
    return he_problems, mbpp_problems
```

### `api_verifier.verify_task_ids`

```python
def verify_task_ids(he_failures, mbpp_failures, he_problems, mbpp_problems):
    for tid in he_failures:
        assert tid in he_problems, f"{tid} not in EvalPlus HE+ dataset"
    for tid in mbpp_failures:
        assert tid in mbpp_problems, f"{tid} not in EvalPlus MBPP+ dataset"
```

### `data_loader.verify_counts`

```python
def verify_counts(he_failures, mbpp_failures):
    assert len(he_failures) == 34, \
        f"Expected 34 HE+ failures, got {len(he_failures)}"
    assert len(mbpp_failures) == 100, \
        f"Expected 100 MBPP+ failures, got {len(mbpp_failures)}"
    assert len(he_failures) + len(mbpp_failures) == 134
```

---

## Error Handling Summary

| Exception | Trigger | Gate Result |
|-----------|---------|-------------|
| `FileNotFoundError` | Archive JSON missing | FAIL |
| `KeyError` | JSON schema changed (no "eval" key) | FAIL |
| `AssertionError` | Count/field/API mismatch | FAIL |
| `ImportError` | `evalplus` not installed | FAIL |

All exceptions caught in `verify_h_e1.run_verification()` → sets gate="FAIL", writes report, exits 1.
