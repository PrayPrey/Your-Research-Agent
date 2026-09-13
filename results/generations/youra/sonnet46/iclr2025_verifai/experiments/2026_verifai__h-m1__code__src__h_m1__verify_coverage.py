"""H-M1: Coverage verification module.

Loads pass@1 from h-e1 results, computes coverage and distribution stats,
evaluates MUST_WORK gate (coverage >= 95%, non-trivial distribution).
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np

# ─── Constants ────────────────────────────────────────────────────────────────

# Coverage gate threshold
COVERAGE_GATE: float = 0.95

# Benchmark problem totals
HE_TOTAL: int = 164
MBPP_TOTAL: int = 378
COMBINED_TOTAL: int = 542

BENCHMARK_TOTALS: dict[str, int] = {
    "humaneval": HE_TOTAL,
    "mbpp": MBPP_TOTAL,
    "combined": COMBINED_TOTAL,
}

# Benchmark prefix → key mapping
BENCHMARK_PREFIXES: dict[str, str] = {
    "HumanEval/": "humaneval",
    "Mbpp/": "mbpp",
}

# Model IDs (verified from h-e1 actual code)
MODEL_IDS: list[str] = [
    "NousResearch/Meta-Llama-3-8B",
    "codellama/CodeLlama-7b-hf",
    "deepseek-ai/deepseek-coder-6.7b-base",
]

# HF model ID → short name (verified from h-e1 actual code)
MODEL_SHORT_NAMES: dict[str, str] = {
    "NousResearch/Meta-Llama-3-8B": "llama3_8b",
    "codellama/CodeLlama-7b-hf": "codellama_7b",
    "deepseek-ai/deepseek-coder-6.7b-base": "deepseek_6.7b",
}

# Reverse mapping: short name → HF ID
SHORT_NAME_TO_MODEL_ID: dict[str, str] = {v: k for k, v in MODEL_SHORT_NAMES.items()}

# Pass@1 histogram bins
HIST_BINS: list[float] = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]

# Threshold line styling (for plot_coverage_rates)
GATE_LINE_COLOR: str = "red"
GATE_LINE_STYLE: str = "--"
GATE_LINE_LABEL: str = f"Gate ({COVERAGE_GATE:.0%})"

# Smoke test size
N_SMOKE: int = 10

# Default h-e1 results path
DEFAULT_H_E1_RESULTS: str = "../../h-e1/results"

logger = logging.getLogger(__name__)


# ─── File integrity check ─────────────────────────────────────────────────────

def _check_file_integrity(
    h_e1_results_dir: Path,
    model_short: str,
) -> dict[str, bool]:
    """Check which result files exist for a model.

    Returns: {"pass_at_1": bool, "correctness": bool, "solutions": bool}
    """
    return {
        "pass_at_1": (h_e1_results_dir / f"pass_at_1_{model_short}.json").exists(),
        "correctness": (h_e1_results_dir / f"correctness_{model_short}.json").exists(),
        "solutions": (h_e1_results_dir / f"solutions_{model_short}.jsonl").exists(),
    }


# ─── Load or recompute pass@1 ─────────────────────────────────────────────────

def load_or_recompute_pass_at_1(
    h_e1_results_dir: Path,
    model_short: str,
    force_regenerate: bool = False,
) -> dict[str, float]:
    """Load pass_at_1 from file or recompute from correctness/solutions.

    Returns: {task_id: float}
    Raises:
        FileNotFoundError: if force_regenerate=False and all files missing
        NotImplementedError: if force_regenerate=True (out of scope)
    """
    h_e1_results_dir = Path(h_e1_results_dir)
    integrity = _check_file_integrity(h_e1_results_dir, model_short)

    # PATH 5: force_regenerate=True → out of scope
    if force_regenerate:
        raise NotImplementedError(
            f"Solution regeneration (k=5 generation) not in h-m1 scope. "
            f"Re-run h-e1 to regenerate solutions for {model_short}."
        )

    # PATH 1: primary pass_at_1 JSON
    p1_path = h_e1_results_dir / f"pass_at_1_{model_short}.json"
    if integrity["pass_at_1"] and p1_path.exists():
        with open(p1_path) as f:
            data = json.load(f)
        if len(data) > 0:
            logger.info(f"PATH 1: Loaded pass_at_1 for {model_short} ({len(data)} entries)")
            return data

    # PATH 2: recompute from correctness JSON (CPU only, no GPU needed)
    corr_path = h_e1_results_dir / f"correctness_{model_short}.json"
    if integrity["correctness"] and corr_path.exists():
        logger.info(f"PATH 2: Recomputing pass_at_1 from correctness for {model_short}")
        with open(corr_path) as f:
            correctness = json.load(f)
        # Recompute: pass@1 = mean of k correctness booleans
        pass_at_1 = {
            tid: float(sum(v)) / len(v) if v else 0.0
            for tid, v in correctness.items()
        }
        return pass_at_1

    # PATH 3: solutions JSONL fallback → re-evaluate (no generation needed)
    sol_path = h_e1_results_dir / f"solutions_{model_short}.jsonl"
    if integrity["solutions"] and sol_path.exists():
        logger.warning(f"PATH 3: Re-evaluating solutions for {model_short} from JSONL")
        try:
            import sys as _sys
            # Add h-e1 code to path
            h_e1_src = str(h_e1_results_dir.parent / "code" / "src")
            if h_e1_src not in _sys.path:
                _sys.path.insert(0, h_e1_src)
            from h_e1.evaluate_solutions import evaluate_all_solutions, load_solutions_jsonl
            from h_e1.analyze_tiers import compute_pass_at_1
            from evalplus.data import get_human_eval_plus, get_mbpp_plus

            solutions = load_solutions_jsonl(str(sol_path))
            problems_he = get_human_eval_plus()
            problems_mbpp = get_mbpp_plus()
            correctness = evaluate_all_solutions(
                solutions, problems_he, problems_mbpp,
                str(h_e1_results_dir), model_short
            )
            pass_at_1 = compute_pass_at_1(correctness)
            logger.info(f"PATH 3: Re-evaluated {len(pass_at_1)} tasks for {model_short}")
            return pass_at_1
        except Exception as e:
            logger.error(f"PATH 3 failed for {model_short}: {e}")
            raise

    # PATH 4: all files missing, force_regenerate=False
    raise FileNotFoundError(
        f"No result files found for model '{model_short}' in {h_e1_results_dir}.\n"
        f"  Checked: pass_at_1_{model_short}.json, correctness_{model_short}.json, "
        f"solutions_{model_short}.jsonl\n"
        f"  Run h-e1 Phase 4 to generate these files, or use --force_regenerate "
        f"(not in h-m1 scope)."
    )


# ─── Split by benchmark ───────────────────────────────────────────────────────

def split_by_benchmark(
    pass_at_1: dict[str, float],
) -> tuple[dict[str, float], dict[str, float]]:
    """Split pass_at_1 dict by benchmark prefix.

    Returns: (he_dict, mbpp_dict)
    """
    he_dict = {k: v for k, v in pass_at_1.items() if k.startswith("HumanEval/")}
    mbpp_dict = {k: v for k, v in pass_at_1.items() if k.startswith("Mbpp/")}
    return he_dict, mbpp_dict


# ─── Compute coverage ─────────────────────────────────────────────────────────

def compute_coverage(
    pass_at_1_splits: dict[str, tuple[dict, dict]],
) -> dict[str, dict[str, float]]:
    """Compute coverage fractions per model and benchmark.

    Args:
        pass_at_1_splits: {model_short: (he_dict, mbpp_dict)}

    Returns:
        {model_short: {"humaneval": float, "mbpp": float, "combined": float}}
    """
    coverage_data = {}
    for model_short, (he_dict, mbpp_dict) in pass_at_1_splits.items():
        he_cov = len(he_dict) / HE_TOTAL if HE_TOTAL > 0 else 0.0
        mbpp_cov = len(mbpp_dict) / MBPP_TOTAL if MBPP_TOTAL > 0 else 0.0
        combined_total_tasks = len(he_dict) + len(mbpp_dict)
        combined_cov = combined_total_tasks / COMBINED_TOTAL if COMBINED_TOTAL > 0 else 0.0
        coverage_data[model_short] = {
            "humaneval": he_cov,
            "mbpp": mbpp_cov,
            "combined": combined_cov,
        }
        logger.info(
            f"Coverage {model_short}: HE={he_cov:.4f}, MBPP={mbpp_cov:.4f}, "
            f"Combined={combined_cov:.4f}"
        )
    return coverage_data


# ─── Compute distribution stats ───────────────────────────────────────────────

def compute_distribution_stats(
    pass_at_1: dict[str, float],
) -> dict:
    """Compute distribution statistics over pass@1 values.

    Returns:
        {mean, std, min, max, histogram_6pt: {bin: count}, non_trivial: bool}
    Edge cases:
        empty dict → all zeros, non_trivial=False
        all same → std=0, non_trivial=False
    """
    if not pass_at_1:
        return {
            "mean": 0.0,
            "std": 0.0,
            "min": 0.0,
            "max": 0.0,
            "histogram_6pt": {str(b): 0 for b in HIST_BINS},
            "non_trivial": False,
        }

    arr = np.array(list(pass_at_1.values()), dtype=float)
    mean = float(np.mean(arr))
    std = float(np.std(arr))
    min_val = float(np.min(arr))
    max_val = float(np.max(arr))

    # 6-bin histogram: use np.isclose for exact matching
    histogram_6pt = {}
    for b in HIST_BINS:
        histogram_6pt[str(b)] = int(np.sum(np.isclose(arr, b)))

    # non_trivial: std > 0 AND at least 3 non-zero histogram buckets
    non_zero_buckets = sum(1 for v in histogram_6pt.values() if v > 0)
    non_trivial = (std > 0) and (non_zero_buckets >= 3)

    return {
        "mean": mean,
        "std": std,
        "min": min_val,
        "max": max_val,
        "histogram_6pt": histogram_6pt,
        "non_trivial": non_trivial,
    }


# ─── Verify gate ──────────────────────────────────────────────────────────────

def verify_gate(
    coverage_data: dict[str, dict[str, float]],
    stats_by_model: dict[str, dict],
) -> tuple[bool, dict[str, dict]]:
    """Check MUST_WORK gate per model, aggregate to overall.

    Gate criteria per model:
        - coverage_combined >= COVERAGE_GATE (0.95)
        - std > 0 (non-trivial distribution)

    Returns:
        (overall_gate_pass: bool, per_model_results: dict)
    """
    per_model_results = {}
    for model_short in MODEL_SHORT_NAMES.values():
        cov = coverage_data.get(model_short, {}).get("combined", 0.0)
        std = stats_by_model.get(model_short, {}).get("std", 0.0)

        cov_ok = cov >= COVERAGE_GATE
        std_ok = std > 0

        gate_pass = cov_ok and std_ok
        checks = [
            f"coverage={cov:.4f} >= {COVERAGE_GATE}: {'PASS' if cov_ok else 'FAIL'}",
            f"non_trivial (std={std:.4f} > 0): {'PASS' if std_ok else 'FAIL'}",
        ]
        partial = cov_ok != std_ok  # exactly one condition failed

        per_model_results[model_short] = {
            "gate_pass": gate_pass,
            "checks": checks,
            "partial": partial,
            "coverage_combined": cov,
            "std": std,
        }

    n_pass = sum(1 for r in per_model_results.values() if r["gate_pass"])
    n_partial = sum(1 for r in per_model_results.values() if r["partial"])

    if n_pass == 3:
        overall = True
    elif n_pass >= 2:
        overall = False
        logger.warning(f"PARTIAL: {n_pass}/3 models pass MUST_WORK gate")
    else:
        overall = False

    return overall, per_model_results


# ─── Verify mechanism activated ───────────────────────────────────────────────

def verify_mechanism_activated(
    pass_at_1_dicts: dict[str, dict],
    results: dict,
) -> tuple[bool, dict]:
    """Verify that the h-m1 mechanism (coverage + non-trivial distribution) is activated.

    Returns: (activated: bool, indicators: dict)
    """
    indicators = {}
    all_activated = True

    for model_short, p1 in pass_at_1_dicts.items():
        stats = results.get("stats_by_model", {}).get(model_short, {})
        cov_data = results.get("coverage_data", {}).get(model_short, {})

        coverage_ok = cov_data.get("combined", 0.0) >= COVERAGE_GATE
        non_trivial = stats.get("non_trivial", False)
        n_problems = len(p1)

        activated = coverage_ok and non_trivial
        indicators[model_short] = {
            "activated": activated,
            "n_problems": n_problems,
            "coverage_combined": cov_data.get("combined", 0.0),
            "non_trivial": non_trivial,
        }
        if not activated:
            all_activated = False

    return all_activated, indicators


# ─── Main orchestrator ────────────────────────────────────────────────────────

def run_verification(
    h_e1_results_dir: Path,
    output_dir: Path,
    smoke_test: bool = False,
    force_regenerate: bool = False,
) -> dict:
    """Orchestrate full h-m1 verification pipeline.

    Steps: load → (smoke truncate) → split → coverage → stats → gate → mechanism

    Returns:
        {
            "pass_at_1_by_model": {model_short: {task_id: float}},
            "coverage_data": {model_short: {humaneval, mbpp, combined}},
            "stats_by_model": {model_short: {mean, std, min, max, histogram_6pt, non_trivial}},
            "gate_results": {model_short: {gate_pass, checks, partial, ...}},
            "overall_gate_pass": bool,
            "mechanism_activated": bool,
            "mechanism_indicators": dict,
            "all_ok": bool,
        }
    """
    h_e1_results_dir = Path(h_e1_results_dir)
    output_dir = Path(output_dir)

    # Step 1: Load pass_at_1 for each model
    pass_at_1_by_model = {}
    for model_id, model_short in MODEL_SHORT_NAMES.items():
        try:
            p1 = load_or_recompute_pass_at_1(
                h_e1_results_dir, model_short, force_regenerate=force_regenerate
            )
            pass_at_1_by_model[model_short] = p1
            logger.info(f"Loaded {len(p1)} entries for {model_short}")
        except Exception as e:
            logger.error(f"Failed to load pass_at_1 for {model_short}: {e}")
            raise

    # Step 2: Smoke test truncation (no file writes)
    if smoke_test:
        logger.info(f"SMOKE TEST: truncating to {N_SMOKE} HE + {N_SMOKE} MBPP per model")
        for model_short in list(pass_at_1_by_model.keys()):
            p1 = pass_at_1_by_model[model_short]
            he_keys = sorted(k for k in p1 if k.startswith("HumanEval/"))[:N_SMOKE]
            mbpp_keys = sorted(k for k in p1 if k.startswith("Mbpp/"))[:N_SMOKE]
            pass_at_1_by_model[model_short] = {k: p1[k] for k in he_keys + mbpp_keys}

    # Step 3: Split by benchmark
    splits = {
        model_short: split_by_benchmark(p1)
        for model_short, p1 in pass_at_1_by_model.items()
    }

    # Step 4: Compute coverage
    coverage_data = compute_coverage(splits)

    # Step 5: Compute distribution stats (combined pass@1 per model)
    stats_by_model = {}
    for model_short, p1 in pass_at_1_by_model.items():
        stats_by_model[model_short] = compute_distribution_stats(p1)

    # Step 6: Verify gate
    overall_gate_pass, gate_results = verify_gate(coverage_data, stats_by_model)

    # Build intermediate results for mechanism check
    intermediate = {
        "coverage_data": coverage_data,
        "stats_by_model": stats_by_model,
    }

    # Step 7: Verify mechanism activated
    mechanism_activated, mechanism_indicators = verify_mechanism_activated(
        pass_at_1_by_model, intermediate
    )

    results = {
        "pass_at_1_by_model": pass_at_1_by_model,
        "coverage_data": coverage_data,
        "stats_by_model": stats_by_model,
        "gate_results": gate_results,
        "overall_gate_pass": overall_gate_pass,
        "mechanism_activated": mechanism_activated,
        "mechanism_indicators": mechanism_indicators,
        "all_ok": overall_gate_pass and mechanism_activated,
        "smoke_test": smoke_test,
    }

    logger.info(f"Verification complete. Gate: {'PASS' if overall_gate_pass else 'FAIL'}")
    return results
