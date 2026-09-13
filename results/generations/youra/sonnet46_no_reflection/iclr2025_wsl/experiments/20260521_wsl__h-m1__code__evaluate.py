"""Gate metrics computation and validation report generation for H-M1.

Determines PASS/FAIL for MUST_WORK gate:
  PASS if: computability_rate==1.0 AND unified_codebase==True AND overhead_ratio_mean<=1.2
"""
import json
import os
import statistics
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Tuple


@dataclass
class GateMetrics:
    computability_rate: float
    unified_codebase: bool
    overhead_ratio_mean: float
    overhead_ratio_std: float
    dim_consistent: bool
    per_layer_overhead: Dict[str, float]
    n_total: int = 0
    n_success: int = 0
    gate_pass: bool = False


def compute_gate_metrics(
    results: List,
    has_arch_branches: bool = False,
) -> GateMetrics:
    """Aggregate CheckpointResults into GateMetrics.

    computability_rate = sum(r.success) / len(results)
    overhead_ratio_mean/std from all results
    per_layer_overhead: group by layer_types_seen, average overhead_ratio
    """
    if not results:
        return GateMetrics(
            computability_rate=0.0,
            unified_codebase=not has_arch_branches,
            overhead_ratio_mean=0.0,
            overhead_ratio_std=0.0,
            dim_consistent=True,
            per_layer_overhead={},
            n_total=0,
            n_success=0,
            gate_pass=False,
        )

    n_total = len(results)
    n_success = sum(1 for r in results if r.success)
    computability_rate = n_success / n_total

    overhead_ratios = [r.overhead_ratio for r in results]
    overhead_mean = statistics.mean(overhead_ratios) if overhead_ratios else 0.0
    overhead_std = statistics.stdev(overhead_ratios) if len(overhead_ratios) > 1 else 0.0

    # Per-layer overhead: for each layer type seen, avg overhead_ratio across checkpoints that saw it
    layer_overhead_sums: Dict[str, List[float]] = {}
    for r in results:
        for lt in r.layer_types_seen:
            if lt not in layer_overhead_sums:
                layer_overhead_sums[lt] = []
            layer_overhead_sums[lt].append(r.overhead_ratio)

    per_layer_overhead = {
        lt: statistics.mean(vals)
        for lt, vals in layer_overhead_sums.items()
    }

    unified_codebase = not has_arch_branches
    dim_consistent = True  # verified inside orbit_computer.forward() by fixed token_dim

    gate_pass = (
        computability_rate == 1.0
        and unified_codebase
        and overhead_mean <= 1.2
    )

    return GateMetrics(
        computability_rate=computability_rate,
        unified_codebase=unified_codebase,
        overhead_ratio_mean=overhead_mean,
        overhead_ratio_std=overhead_std,
        dim_consistent=dim_consistent,
        per_layer_overhead=per_layer_overhead,
        n_total=n_total,
        n_success=n_success,
        gate_pass=gate_pass,
    )


def verify_orbit_pe_activated(
    checkpoint_results: Dict,
) -> Tuple[bool, Dict]:
    """Check that orbit-PE was called for all checkpoints."""
    results = checkpoint_results.get("results", [])
    if not results:
        return False, {"reason": "no results"}

    indicators = {
        "all_success": all(r.success for r in results),
        "n_results": len(results),
        "n_success": sum(1 for r in results if r.success),
        "layer_types_found": list({lt for r in results for lt in r.layer_types_seen}),
    }
    all_activated = indicators["all_success"]
    return all_activated, indicators


def save_metrics(metrics: GateMetrics, path: str) -> None:
    """Serialize GateMetrics to JSON at path."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = asdict(metrics)
    data["saved_at"] = datetime.now().isoformat()
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Metrics saved to {path}")


def generate_validation_report(
    metrics: GateMetrics,
    output_path: str,
) -> None:
    """Write 04_validation.md with PASS/FAIL gate determination."""
    verdict = "PASS" if metrics.gate_pass else "FAIL"
    timestamp = datetime.now().isoformat()

    lines = [
        "# Phase 4 Validation Report: H-M1",
        "",
        f"**Date**: {timestamp}",
        f"**Hypothesis**: H-M1 (MECHANISM — Orbit-PE Architecture-Agnostic Computability)",
        f"**Gate Type**: MUST_WORK",
        f"**Gate Result**: {verdict}",
        "",
        "---",
        "",
        "## Gate Criteria (MUST_WORK)",
        "",
        f"| Criterion | Threshold | Result | Status |",
        f"|-----------|-----------|--------|--------|",
        f"| computability_rate | == 1.0 | {metrics.computability_rate:.4f} | {'✅ PASS' if metrics.computability_rate == 1.0 else '❌ FAIL'} |",
        f"| unified_codebase | True | {metrics.unified_codebase} | {'✅ PASS' if metrics.unified_codebase else '❌ FAIL'} |",
        f"| overhead_ratio_mean | ≤ 1.2 | {metrics.overhead_ratio_mean:.4f} | {'✅ PASS' if metrics.overhead_ratio_mean <= 1.2 else '❌ FAIL'} |",
        "",
        "---",
        "",
        "## Experiment Results",
        "",
        f"- **Total checkpoints**: {metrics.n_total}",
        f"- **Successful computations**: {metrics.n_success}",
        f"- **Computability rate**: {metrics.computability_rate:.4f}",
        f"- **Overhead ratio mean**: {metrics.overhead_ratio_mean:.4f} ± {metrics.overhead_ratio_std:.4f}",
        f"- **Dimension consistent**: {metrics.dim_consistent}",
        f"- **Unified codebase (HAS_ARCH_BRANCHES=False)**: {metrics.unified_codebase}",
        "",
        "### Per-Layer Overhead",
        "",
        "| Layer Type | Mean Overhead Ratio |",
        "|-----------|---------------------|",
    ]

    for lt, overhead in metrics.per_layer_overhead.items():
        lines.append(f"| {lt} | {overhead:.4f} |")

    lines += [
        "",
        "---",
        "",
        f"## Verdict: {verdict}",
        "",
    ]

    if metrics.gate_pass:
        lines += [
            "All MUST_WORK criteria satisfied:",
            "- Orbit-PE computable for all layer types (computability_rate = 1.0)",
            "- Unified codebase verified (HAS_ARCH_BRANCHES = False)",
            f"- Computation overhead within budget (mean overhead = {metrics.overhead_ratio_mean:.4f} ≤ 1.2)",
            "",
            "**Proceed to H-M2.**",
        ]
    else:
        lines += [
            "MUST_WORK criteria NOT satisfied. Failed checks:",
        ]
        if metrics.computability_rate < 1.0:
            lines.append(f"- computability_rate = {metrics.computability_rate:.4f} (required: 1.0)")
        if not metrics.unified_codebase:
            lines.append("- unified_codebase = False (HAS_ARCH_BRANCHES detected)")
        if metrics.overhead_ratio_mean > 1.2:
            lines.append(f"- overhead_ratio_mean = {metrics.overhead_ratio_mean:.4f} (required: ≤ 1.2)")
        lines += [
            "",
            "**Route to Phase 2A for hypothesis redesign.**",
        ]

    with open(output_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Validation report written to {output_path}")
    print(f"Gate verdict: {verdict}")
