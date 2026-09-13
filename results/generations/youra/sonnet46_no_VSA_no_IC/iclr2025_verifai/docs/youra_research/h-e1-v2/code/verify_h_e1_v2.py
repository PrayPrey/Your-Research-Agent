"""H-E1-v2: EvalPlus Failure Set Recovery Verification."""
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


def _check_c1_failure_ids(
    archive: pathlib.Path,
) -> tuple:
    """
    Load HE+ and MBPP+ eval result files.
    Extract task IDs where ALL solutions have plus_status != "pass".

    Returns:
        result: {"he_count": int, "mbpp_count": int, "total": int, "pass": bool}
        he_failures: list of HE+ failure task IDs (expected len=34)
        mbpp_failures: list of MBPP+ failure task IDs (expected len=100)
    """
    with open(archive / "humaneval_samples_eval_results.json") as f:
        he_eval = json.load(f)["eval"]

    he_failures = [
        tid for tid, entries in he_eval.items()
        if isinstance(entries, list)
        and len(entries) > 0
        and all(e.get("plus_status") != "pass" for e in entries)
    ]

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
        "pass": total == 134,
    }
    return result, he_failures, mbpp_failures


def _check_c2_stored_solutions(
    archive: pathlib.Path,
    he_failures: list,
    mbpp_failures: list,
) -> dict:
    """
    Load solutions_cache.jsonl line by line.
    Verify all 134 failure task IDs have at least one stored solution.

    Returns:
        {"he_covered": int, "mbpp_covered": int, "pass": bool}
    """
    cache: set = set()
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
        "pass": covered_he == len(he_failures) and covered_mbpp == len(mbpp_failures),
    }


def _check_c3_evalplus_api(
    he_failures: list,
    mbpp_failures: list,
) -> tuple:
    """
    Call get_human_eval_plus() and get_mbpp_plus().
    Verify all failure task IDs are present in the returned dicts.

    Returns:
        result: {"he_tasks_in_api": int, "mbpp_tasks_in_api": int, "pass": bool}
        he_data: full HumanEval+ dataset dict
        mbpp_data: full MBPP+ dataset dict
    """
    he_data = get_human_eval_plus()
    mbpp_data = get_mbpp_plus()

    he_found = sum(1 for tid in he_failures if tid in he_data)
    mbpp_found = sum(1 for tid in mbpp_failures if tid in mbpp_data)

    result = {
        "he_tasks_in_api": he_found,
        "mbpp_tasks_in_api": mbpp_found,
        "pass": he_found == len(he_failures) and mbpp_found == len(mbpp_failures),
    }
    return result, he_data, mbpp_data


def _check_c4_deterministic_test(
    he_failures: list,
    he_data: dict,
) -> dict:
    """
    Access plus_input field for the first HE+ failure task.
    Confirm it is a non-empty list.

    Returns:
        {"sample_task": str, "plus_input_count": int, "pass": bool}
    """
    sample_task = he_failures[0]
    plus_input = he_data[sample_task].get("plus_input", [])

    return {
        "sample_task": sample_task,
        "plus_input_count": len(plus_input),
        "pass": len(plus_input) > 0,
    }


def _generate_figure(results: dict, figures_dir: pathlib.Path) -> None:
    """
    4-bar chart: one bar per condition (C1-C4), green=pass, red=fail.
    Saves to figures_dir/gate_conditions.png.
    """
    conditions = [
        (
            "C1: Failure IDs",
            results["c1_failure_ids"]["pass"],
            f"HE+={results['c1_failure_ids']['he_count']}\nMBPP+={results['c1_failure_ids']['mbpp_count']}",
        ),
        (
            "C2: Stored Solutions",
            results["c2_stored_solutions"]["pass"],
            f"covered={results['c2_stored_solutions']['he_covered'] + results['c2_stored_solutions']['mbpp_covered']}/134",
        ),
        (
            "C3: EvalPlus API",
            results["c3_evalplus_api"]["pass"],
            f"HE+={results['c3_evalplus_api']['he_tasks_in_api']}/34\nMBPP+={results['c3_evalplus_api']['mbpp_tasks_in_api']}/100",
        ),
        (
            "C4: Deterministic Test",
            results["c4_deterministic_test"]["pass"],
            f"plus_input_count={results['c4_deterministic_test']['plus_input_count']}",
        ),
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
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.05,
            ann,
            ha="center",
            va="bottom",
            fontsize=9,
        )

    gate_color = "#2ecc71" if results["gate_passed"] else "#e74c3c"
    gate_label = "GATE: PASSED" if results["gate_passed"] else "GATE: FAILED"
    ax.text(
        0.98,
        0.95,
        gate_label,
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=12,
        fontweight="bold",
        color=gate_color,
    )

    fig.tight_layout()
    fig.savefig(figures_dir / "gate_conditions.png", dpi=150)
    plt.close(fig)


def verify_h_e1_v2(archive_path: str) -> dict:
    """
    Run all 4 sub-condition checks against the h-e1 archive.

    Returns structured results dict with per-condition pass/fail and gate_passed bool.
    """
    archive = pathlib.Path(archive_path)

    c1, he_failures, mbpp_failures = _check_c1_failure_ids(archive)
    print(
        f"[H-E1-v2] C1: failure_ids — HE+={c1['he_count']}, MBPP+={c1['mbpp_count']}, "
        f"total={c1['total']} — {'PASS' if c1['pass'] else 'FAIL'}"
    )

    c2 = _check_c2_stored_solutions(archive, he_failures, mbpp_failures)
    print(
        f"[H-E1-v2] C2: stored_solutions — covered={c2['he_covered'] + c2['mbpp_covered']}/134 — "
        f"{'PASS' if c2['pass'] else 'FAIL'}"
    )

    c3, he_data, mbpp_data = _check_c3_evalplus_api(he_failures, mbpp_failures)
    print(
        f"[H-E1-v2] C3: evalplus_api — HE+={c3['he_tasks_in_api']}/34, "
        f"MBPP+={c3['mbpp_tasks_in_api']}/100 — {'PASS' if c3['pass'] else 'FAIL'}"
    )

    c4 = _check_c4_deterministic_test(he_failures, he_data)
    print(
        f"[H-E1-v2] C4: deterministic_test — plus_input_count={c4['plus_input_count']} — "
        f"{'PASS' if c4['pass'] else 'FAIL'}"
    )

    gate = c1["pass"] and c2["pass"] and c3["pass"] and c4["pass"]
    print(
        f"[H-E1-v2] GATE: {'PASSED' if gate else 'FAILED'} — "
        f"downstream hypotheses {'unblocked' if gate else 'blocked'}"
    )

    return {
        "c1_failure_ids": c1,
        "c2_stored_solutions": c2,
        "c3_evalplus_api": c3,
        "c4_deterministic_test": c4,
        "gate_passed": gate,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="H-E1-v2 verification script")
    parser.add_argument(
        "--archive",
        default="docs/youra_research/_archive/20260822T150921_routing_recovery/h-e1/results",
    )
    parser.add_argument(
        "--output",
        default="docs/youra_research/h-e1-v2/results.json",
    )
    parser.add_argument(
        "--figures",
        default="docs/youra_research/h-e1-v2/figures",
    )
    parser.add_argument("--no-figure", action="store_true")
    args = parser.parse_args()

    # Verify archive
    archive = pathlib.Path(args.archive)
    assert archive.exists(), f"Archive not found: {archive}"
    for fname in [
        "humaneval_samples_eval_results.json",
        "mbpp_samples_eval_results.json",
        "solutions_cache.jsonl",
    ]:
        assert (archive / fname).exists(), f"Missing: {fname}"

    results = verify_h_e1_v2(archive_path=args.archive)

    out_path = pathlib.Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[H-E1-v2] Results written to: {out_path}")

    if not args.no_figure and HAS_MATPLOTLIB:
        figures_dir = pathlib.Path(args.figures)
        figures_dir.mkdir(parents=True, exist_ok=True)
        _generate_figure(results, figures_dir)
        print(f"[H-E1-v2] Figure saved to: {figures_dir / 'gate_conditions.png'}")

    assert results["gate_passed"], f"H-E1-v2 gate FAILED: {results}"
    print("H-E1-v2 GATE PASSED — all 4 conditions satisfied")
    sys.exit(0)
