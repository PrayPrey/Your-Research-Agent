# Logic Design: H-E1-v2
## EvalPlus Failure Set Recovery Verification

Applied: N/A — Archon KB is CV-domain only; no applicable API design patterns found for EvalPlus data verification.

---

## Codebase Analysis (Serena)

**Status:** green-field — no existing codebase to analyze.
**Serena:** skipped (N/A for data verification scripts with no prior code).

---

## Overview

Single script: `code/verify_h_e1_v2.py`. Five private functions + `verify_h_e1_v2()` orchestrator + `__main__` entry point. No tensors, no model, no training. All data types are Python stdlib (dict, list, str, pathlib.Path).

---

## API Signatures and Pseudo-code

### Epic A-1: Environment Setup (complexity 4)

No dedicated function. Handled at import time and in `__main__`:

```python
# At module top:
import json
import pathlib
import argparse
import sys
from typing import Optional

try:
    from evalplus.data import get_human_eval_plus, get_mbpp_plus
except ImportError:
    print("[H-E1-v2] ERROR: evalplus not installed. Run: pip install evalplus==0.3.1")
    sys.exit(1)

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
```

Pseudo-code for archive path check (in `__main__`):
```
ARCHIVE = pathlib.Path(args.archive)
assert ARCHIVE.exists(), f"Archive not found: {ARCHIVE}"
for fname in ["humaneval_samples_eval_results.json",
              "mbpp_samples_eval_results.json",
              "solutions_cache.jsonl"]:
    assert (ARCHIVE / fname).exists(), f"Missing: {fname}"
```

---

### Epic A-2: C1 + C2 Logic (complexity 7)

#### `_check_c1_failure_ids`

```python
def _check_c1_failure_ids(
    archive: pathlib.Path
) -> tuple[dict, list[str], list[str]]:
    """
    Load HE+ and MBPP+ eval result files.
    Extract task IDs where ALL solutions have plus_status != "pass".

    Returns:
        result: {"he_count": int, "mbpp_count": int, "total": int, "pass": bool}
        he_failures: list of HE+ failure task IDs (expected len=34)
        mbpp_failures: list of MBPP+ failure task IDs (expected len=100)

    Raises:
        FileNotFoundError if eval result files missing
        KeyError if "eval" key absent from JSON
    """
    # Load HE+ eval results
    with open(archive / "humaneval_samples_eval_results.json") as f:
        he_eval = json.load(f)["eval"]

    he_failures = [
        tid for tid, entries in he_eval.items()
        if isinstance(entries, list)
        and len(entries) > 0
        and all(e.get("plus_status") != "pass" for e in entries)
    ]

    # Load MBPP+ eval results
    with open(archive / "mbpp_samples_eval_results.json") as f:
        mbpp_eval = json.load(f)["eval"]

    mbpp_failures = [
        tid for tid, entries in mbpp_eval.items()
        if isinstance(entries, list)
        and len(entries) > 0
        and all(e.get("plus_status") != "pass" for e in entries)
    ]

    total = len(he_failures) + len(mbpp_failures)
    result = {
        "he_count": len(he_failures),
        "mbpp_count": len(mbpp_failures),
        "total": total,
        "pass": total == 134
    }
    return result, he_failures, mbpp_failures
```

#### `_check_c2_stored_solutions`

```python
def _check_c2_stored_solutions(
    archive: pathlib.Path,
    he_failures: list[str],
    mbpp_failures: list[str]
) -> dict:
    """
    Load solutions_cache.jsonl line by line.
    Verify all 134 failure task IDs have at least one stored solution.

    Returns:
        {"he_covered": int, "mbpp_covered": int, "pass": bool}

    Notes:
        solutions_cache.jsonl has 542 entries; multiple solutions per task_id possible.
        We only need presence (>= 1 solution per failure ID).
    """
    cache: set[str] = set()
    with open(archive / "solutions_cache.jsonl") as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                cache.add(item["task_id"])

    covered_he = sum(1 for tid in he_failures if tid in cache)
    covered_mbpp = sum(1 for tid in mbpp_failures if tid in cache)

    return {
        "he_covered": covered_he,
        "mbpp_covered": covered_mbpp,
        "pass": covered_he == 34 and covered_mbpp == 100
    }
```

---

### Epic A-3: C3 + C4 Logic (complexity 7)

#### `_check_c3_evalplus_api`

```python
def _check_c3_evalplus_api(
    he_failures: list[str],
    mbpp_failures: list[str]
) -> tuple[dict, dict, dict]:
    """
    Call get_human_eval_plus() and get_mbpp_plus().
    Verify all failure task IDs are present in the returned dicts.

    Returns:
        result: {"he_tasks_in_api": int, "mbpp_tasks_in_api": int, "pass": bool}
        he_data: full HumanEval+ dataset dict (164 tasks)
        mbpp_data: full MBPP+ dataset dict (378 tasks)

    Notes:
        evalplus auto-downloads and caches data on first call.
        Subsequent calls use local cache — no network required.
    """
    he_data = get_human_eval_plus()    # dict: task_id -> problem dict
    mbpp_data = get_mbpp_plus()        # dict: task_id -> problem dict

    he_found = sum(1 for tid in he_failures if tid in he_data)
    mbpp_found = sum(1 for tid in mbpp_failures if tid in mbpp_data)

    result = {
        "he_tasks_in_api": he_found,
        "mbpp_tasks_in_api": mbpp_found,
        "pass": he_found == 34 and mbpp_found == 100
    }
    return result, he_data, mbpp_data
```

#### `_check_c4_deterministic_test`

```python
def _check_c4_deterministic_test(
    he_failures: list[str],
    he_data: dict
) -> dict:
    """
    Access plus_input field for the first HE+ failure task.
    Confirm it is a non-empty list (deterministic first-test selection is possible).

    Returns:
        {"sample_task": str, "plus_input_count": int, "pass": bool}

    Notes:
        plus_input[0] is deterministically the first augmented test case.
        This confirms downstream code can always select a deterministic failing test.
    """
    sample_task = he_failures[0]
    plus_input = he_data[sample_task].get("plus_input", [])

    return {
        "sample_task": sample_task,
        "plus_input_count": len(plus_input),
        "pass": len(plus_input) > 0
    }
```

---

### Epic A-4: Entry Point + Reporting (complexity 6)

#### `verify_h_e1_v2` (orchestrator)

```python
def verify_h_e1_v2(archive_path: str) -> dict:
    """
    Run all 4 sub-condition checks against the h-e1 archive.

    Args:
        archive_path: path to h-e1 results directory

    Returns:
        {
            "c1_failure_ids": {"he_count": int, "mbpp_count": int, "total": int, "pass": bool},
            "c2_stored_solutions": {"he_covered": int, "mbpp_covered": int, "pass": bool},
            "c3_evalplus_api": {"he_tasks_in_api": int, "mbpp_tasks_in_api": int, "pass": bool},
            "c4_deterministic_test": {"sample_task": str, "plus_input_count": int, "pass": bool},
            "gate_passed": bool
        }
    """
    archive = pathlib.Path(archive_path)

    c1, he_failures, mbpp_failures = _check_c1_failure_ids(archive)
    print(f"[H-E1-v2] C1: failure_ids — HE+={c1['he_count']}, MBPP+={c1['mbpp_count']}, total={c1['total']} — {'PASS' if c1['pass'] else 'FAIL'}")

    c2 = _check_c2_stored_solutions(archive, he_failures, mbpp_failures)
    print(f"[H-E1-v2] C2: stored_solutions — covered={c2['he_covered']+c2['mbpp_covered']}/134 — {'PASS' if c2['pass'] else 'FAIL'}")

    c3, he_data, mbpp_data = _check_c3_evalplus_api(he_failures, mbpp_failures)
    print(f"[H-E1-v2] C3: evalplus_api — HE+={c3['he_tasks_in_api']}/34, MBPP+={c3['mbpp_tasks_in_api']}/100 — {'PASS' if c3['pass'] else 'FAIL'}")

    c4 = _check_c4_deterministic_test(he_failures, he_data)
    print(f"[H-E1-v2] C4: deterministic_test — plus_input_count={c4['plus_input_count']} — {'PASS' if c4['pass'] else 'FAIL'}")

    gate = c1["pass"] and c2["pass"] and c3["pass"] and c4["pass"]
    print(f"[H-E1-v2] GATE: {'PASSED' if gate else 'FAILED'} — downstream hypotheses {'unblocked' if gate else 'blocked'}")

    return {
        "c1_failure_ids": c1,
        "c2_stored_solutions": c2,
        "c3_evalplus_api": c3,
        "c4_deterministic_test": c4,
        "gate_passed": gate
    }
```

#### `__main__` block pseudo-code

```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="H-E1-v2 verification script")
    parser.add_argument("--archive", default="docs/youra_research/_archive/20260822T150921_routing_recovery/h-e1/results")
    parser.add_argument("--output", default="docs/youra_research/h-e1-v2/results.json")
    parser.add_argument("--figures", default="docs/youra_research/h-e1-v2/figures")
    parser.add_argument("--no-figure", action="store_true")
    args = parser.parse_args()

    results = verify_h_e1_v2(archive_path=args.archive)

    # Write results.json
    out_path = pathlib.Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    # Generate figure
    if not args.no_figure and HAS_MATPLOTLIB:
        figures_dir = pathlib.Path(args.figures)
        figures_dir.mkdir(parents=True, exist_ok=True)
        _generate_figure(results, figures_dir)

    # Assert gate
    assert results["gate_passed"], f"H-E1-v2 gate FAILED: {results}"
    print("H-E1-v2 GATE PASSED — all 4 conditions satisfied")
    sys.exit(0)
```

---

### Epic A-5: Figure Generation (complexity 5)

#### `_generate_figure`

```python
def _generate_figure(results: dict, figures_dir: pathlib.Path) -> None:
    """
    4-bar chart: one bar per condition (C1–C4), green=pass, red=fail.
    Saves to figures_dir/gate_conditions.png.

    Args:
        results: output dict from verify_h_e1_v2()
        figures_dir: directory to save figure

    Layout:
        x-axis: ["C1: Failure IDs", "C2: Stored Solutions", "C3: EvalPlus API", "C4: Deterministic Test"]
        y-axis: 0 or 1 (fail/pass)
        color: green (#2ecc71) if pass else red (#e74c3c)
        title: "H-E1-v2 Gate Conditions"
        annotation: counts on each bar (e.g., "34+100=134")
    """
    import matplotlib.pyplot as plt

    conditions = [
        ("C1: Failure IDs", results["c1_failure_ids"]["pass"],
         f"HE+={results['c1_failure_ids']['he_count']}\nMBPP+={results['c1_failure_ids']['mbpp_count']}"),
        ("C2: Stored Solutions", results["c2_stored_solutions"]["pass"],
         f"covered={results['c2_stored_solutions']['he_covered']+results['c2_stored_solutions']['mbpp_covered']}/134"),
        ("C3: EvalPlus API", results["c3_evalplus_api"]["pass"],
         f"HE+={results['c3_evalplus_api']['he_tasks_in_api']}/34\nMBPP+={results['c3_evalplus_api']['mbpp_tasks_in_api']}/100"),
        ("C4: Deterministic Test", results["c4_deterministic_test"]["pass"],
         f"plus_input_count={results['c4_deterministic_test']['plus_input_count']}"),
    ]

    labels = [c[0] for c in conditions]
    values = [1 if c[1] else 0 for c in conditions]
    colors = ["#2ecc71" if c[1] else "#e74c3c" for c in conditions]
    annotations = [c[2] for c in conditions]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(labels, values, color=colors)
    ax.set_ylim(0, 1.4)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["FAIL", "PASS"])
    ax.set_title("H-E1-v2 Gate Conditions", fontsize=14, fontweight="bold")

    for bar, ann in zip(bars, annotations):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.05,
                ann, ha="center", va="bottom", fontsize=9)

    gate_color = "#2ecc71" if results["gate_passed"] else "#e74c3c"
    gate_label = "GATE: PASSED" if results["gate_passed"] else "GATE: FAILED"
    ax.text(0.98, 0.95, gate_label, transform=ax.transAxes,
            ha="right", va="top", fontsize=12, fontweight="bold", color=gate_color)

    fig.tight_layout()
    fig.savefig(figures_dir / "gate_conditions.png", dpi=150)
    plt.close(fig)
```

---

### Epic A-6: End-to-End Integration Test (complexity 5)

```python
# tests/test_verify_h_e1_v2.py
import pathlib
import sys
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "code"))

from verify_h_e1_v2 import verify_h_e1_v2

ARCHIVE = pathlib.Path("docs/youra_research/_archive/20260822T150921_routing_recovery/h-e1/results")

def test_gate_passes():
    """Full integration test: run verify_h_e1_v2 against real archive."""
    results = verify_h_e1_v2(str(ARCHIVE))
    assert results["gate_passed"], f"Gate failed: {results}"

def test_c1_counts():
    results = verify_h_e1_v2(str(ARCHIVE))
    assert results["c1_failure_ids"]["he_count"] == 34
    assert results["c1_failure_ids"]["mbpp_count"] == 100
    assert results["c1_failure_ids"]["total"] == 134

def test_c2_full_coverage():
    results = verify_h_e1_v2(str(ARCHIVE))
    assert results["c2_stored_solutions"]["he_covered"] == 34
    assert results["c2_stored_solutions"]["mbpp_covered"] == 100

def test_c3_api_accessible():
    results = verify_h_e1_v2(str(ARCHIVE))
    assert results["c3_evalplus_api"]["he_tasks_in_api"] == 34
    assert results["c3_evalplus_api"]["mbpp_tasks_in_api"] == 100

def test_c4_deterministic():
    results = verify_h_e1_v2(str(ARCHIVE))
    assert results["c4_deterministic_test"]["plus_input_count"] > 0
```

---

## Budget Summary

- Subtask budget: 0 (all epics Low complexity ≤ 8; no subtask decomposition triggered)
- Total logic tasks: 0 additional subtasks
- All logic fully specified above as part of epic implementations

---

*Source: Phase 2C experiment brief + 03_architecture.md*
*Hypothesis: H-E1-v2 | Tier: LIGHT | No base hypothesis*
