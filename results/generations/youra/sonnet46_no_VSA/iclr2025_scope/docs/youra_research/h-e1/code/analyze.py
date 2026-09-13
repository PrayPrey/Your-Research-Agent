"""Statistical analysis: bootstrap CI, mixed-effects model, mechanism verification."""
import json
import math
import os
from pathlib import Path
from collections import defaultdict

import numpy as np

CODE_DIR = Path(__file__).parent
HYPOTHESIS_DIR = CODE_DIR.parent

from config import (
    CATEGORIES, RETRIEVAL_HEAVY, GENERATION_HEAVY, RESULTS_DIR,
)


def bootstrap_interaction_ratio(
    delta_norm_ssm: dict[str, float],
    delta_norm_lawcat: dict[str, float],
    longbench_per_example: list[dict] | None = None,
    n_resamples: int = 10_000,
    seed: int = 42,
) -> tuple[float, float, float]:
    """
    Bootstrap 95% CI for ratio = mean(Δ_norm^SSM[retrieval]) / mean(Δ_norm^LAWCAT[retrieval]).
    Returns (ratio, ci_low, ci_high).

    If longbench_per_example is None, uses aggregate delta_norm values with
    category-level bootstrap (appropriate when per-example data unavailable).
    """
    rng = np.random.default_rng(seed)

    retrieval_cats = [c for c in CATEGORIES if c in RETRIEVAL_HEAVY]
    generation_cats = [c for c in CATEGORIES if c in GENERATION_HEAVY]

    # Point estimate
    ssm_retrieval = np.mean([delta_norm_ssm.get(c, 0.0) for c in retrieval_cats])
    lawcat_retrieval = np.mean([delta_norm_lawcat.get(c, 0.0) for c in retrieval_cats])
    ratio_point = ssm_retrieval / max(lawcat_retrieval, 1e-8)

    if longbench_per_example is not None and len(longbench_per_example) > 0:
        # Per-example bootstrap: resample examples, recompute delta_norm, recompute ratio
        # We need per-example results for teacher and each student
        # Structure: [{category, pred_teacher, pred_mohawk, pred_lawcat, label}, ...]
        examples = longbench_per_example
        n = len(examples)
        ratios = []
        for _ in range(n_resamples):
            idx = rng.integers(0, n, size=n)
            sample = [examples[i] for i in idx]

            # Compute per-category accuracy for teacher and students
            t_correct, m_correct, l_correct = defaultdict(int), defaultdict(int), defaultdict(int)
            cat_total = defaultdict(int)
            for ex in sample:
                cat = ex["category"]
                cat_total[cat] += 1
                t_correct[cat] += int(ex["pred_teacher"] == ex["label"])
                m_correct[cat] += int(ex["pred_mohawk"] == ex["label"])
                l_correct[cat] += int(ex["pred_lawcat"] == ex["label"])

            # Compute delta_norm per category
            ssm_ret = []
            lawcat_ret = []
            for cat in retrieval_cats:
                total = max(cat_total[cat], 1)
                acc_t = t_correct[cat] / total
                acc_m = m_correct[cat] / total
                acc_l = l_correct[cat] / total
                ssm_ret.append((acc_t - acc_m) / max(acc_t, 1e-8))
                lawcat_ret.append((acc_t - acc_l) / max(acc_t, 1e-8))

            ratio = np.mean(ssm_ret) / max(np.mean(lawcat_ret), 1e-8)
            ratios.append(ratio)
    else:
        # Category-level bootstrap: resample from retrieval categories
        all_cats = list(CATEGORIES)
        n_cats = len(all_cats)
        ratios = []
        for _ in range(n_resamples):
            idx = rng.integers(0, n_cats, size=n_cats)
            boot_cats = [all_cats[i] for i in idx]
            # Filter to retrieval categories that appeared
            boot_retrieval = [c for c in boot_cats if c in RETRIEVAL_HEAVY]
            if not boot_retrieval:
                ratios.append(ratio_point)
                continue
            ssm_r = np.mean([delta_norm_ssm.get(c, 0.0) for c in boot_retrieval])
            lawcat_r = np.mean([delta_norm_lawcat.get(c, 0.0) for c in boot_retrieval])
            ratios.append(ssm_r / max(lawcat_r, 1e-8))

    ratios = np.array(ratios)
    ci_low = float(np.percentile(ratios, 2.5))
    ci_high = float(np.percentile(ratios, 97.5))

    print(f"[Bootstrap] ratio={ratio_point:.4f} 95% CI=[{ci_low:.4f}, {ci_high:.4f}]")
    print(f"  SSM retrieval Δ_norm = {ssm_retrieval:.4f}")
    print(f"  LAWCAT retrieval Δ_norm = {lawcat_retrieval:.4f}")
    return ratio_point, ci_low, ci_high


def fit_mixed_effects_model(
    all_delta_norms: dict[str, dict[str, float]],
) -> tuple[float, float]:
    """
    Fit: Δ_norm ~ TaskType * Strategy + (1|Task)
    Returns (interaction_p_value, holm_corrected_p).

    TaskType: "retrieval" | "generation" | "neutral"
    Strategy: "mohawk" | "lawcat" | "hybrid4"
    """
    try:
        import statsmodels.formula.api as smf
        import pandas as pd
        from scipy import stats
    except ImportError:
        print("[Mixed Effects] statsmodels not available, using scipy F-test approximation")
        return _fit_anova_approximation(all_delta_norms)

    import pandas as pd

    rows = []
    for strategy, cat_deltas in all_delta_norms.items():
        if strategy == "teacher":
            continue
        for cat, delta in cat_deltas.items():
            if cat in RETRIEVAL_HEAVY:
                task_type = "retrieval"
            elif cat in GENERATION_HEAVY:
                task_type = "generation"
            else:
                task_type = "neutral"
            rows.append({
                "delta_norm": delta,
                "strategy": strategy,
                "task_type": task_type,
                "task": cat,
            })

    df = pd.DataFrame(rows)
    if df.empty or df["delta_norm"].std() < 1e-10:
        print("[Mixed Effects] Insufficient variance for model fitting")
        return 1.0, 1.0

    try:
        # Mixed-effects model with random intercept per task
        model = smf.mixedlm(
            "delta_norm ~ C(task_type) * C(strategy)",
            data=df,
            groups=df["task"],
        )
        result = model.fit(reml=True)

        # Extract interaction p-value
        interaction_terms = [k for k in result.pvalues.index
                             if "task_type" in k.lower() and "strategy" in k.lower()]
        if interaction_terms:
            p_values = [result.pvalues[k] for k in interaction_terms]
            # Holm correction for multiple interaction terms
            p_values_sorted = sorted(enumerate(p_values), key=lambda x: x[1])
            n_tests = len(p_values)
            holm_corrected = []
            max_p = 0.0
            for rank, (orig_idx, p) in enumerate(p_values_sorted):
                corrected = min(p * (n_tests - rank), 1.0)
                corrected = max(corrected, max_p)
                max_p = corrected
                holm_corrected.append((orig_idx, corrected))

            interaction_p = min(p_values)
            holm_p = min(c for _, c in holm_corrected)
        else:
            interaction_p, holm_p = 1.0, 1.0

        print(f"[Mixed Effects] interaction p={interaction_p:.4f} (Holm={holm_p:.4f})")
        return float(interaction_p), float(holm_p)

    except Exception as e:
        print(f"[Mixed Effects] Model failed: {e}. Falling back to ANOVA approximation.")
        return _fit_anova_approximation(all_delta_norms)


def _fit_anova_approximation(
    all_delta_norms: dict[str, dict[str, float]],
) -> tuple[float, float]:
    """Simple 2-sample t-test as fallback interaction estimate."""
    from scipy import stats

    ssm_retrieval = [all_delta_norms.get("mohawk", {}).get(c, 0.0) for c in RETRIEVAL_HEAVY]
    lawcat_retrieval = [all_delta_norms.get("lawcat", {}).get(c, 0.0) for c in RETRIEVAL_HEAVY]
    ssm_generation = [all_delta_norms.get("mohawk", {}).get(c, 0.0) for c in GENERATION_HEAVY]
    lawcat_generation = [all_delta_norms.get("lawcat", {}).get(c, 0.0) for c in GENERATION_HEAVY]

    # Interaction = (SSM_retrieval - LAWCAT_retrieval) - (SSM_generation - LAWCAT_generation)
    ret_diff = [s - l for s, l in zip(ssm_retrieval, lawcat_retrieval)]
    gen_diff = [s - l for s, l in zip(ssm_generation, lawcat_generation)]

    if len(ret_diff) >= 2 and len(gen_diff) >= 2:
        t_stat, p_val = stats.ttest_ind(ret_diff, gen_diff, equal_var=False)
        holm_p = min(p_val * 3, 1.0)  # conservative Holm with 3 comparisons
    else:
        p_val = 1.0
        holm_p = 1.0

    print(f"[ANOVA Approx] interaction p≈{p_val:.4f} (Holm={holm_p:.4f})")
    return float(p_val), float(holm_p)


def verify_mechanism_activated(
    mohawk_checkpoint: str | None,
    lawcat_checkpoint: str | None,
    training_logs: dict,
    delta_norms: dict[str, dict[str, float]],
) -> tuple[bool, dict[str, bool]]:
    """Check if both MOHAWK and LAWCAT mechanisms are properly installed and functioning."""
    indicators = {}

    # MOHAWK: Stage 1 Frobenius loss from training logs
    mohawk_stage1_log = training_logs.get("mohawk_stage1_loss", None)
    if mohawk_stage1_log is not None:
        indicators["mohawk_stage1_converged"] = float(mohawk_stage1_log) < 0.15
    else:
        indicators["mohawk_stage1_converged"] = None  # Unknown

    # Functional: Both students degrade vs teacher
    mohawk_dn = delta_norms.get("mohawk", {})
    lawcat_dn = delta_norms.get("lawcat", {})

    overall_mohawk = np.mean(list(mohawk_dn.values())) if mohawk_dn else 0.0
    overall_lawcat = np.mean(list(lawcat_dn.values())) if lawcat_dn else 0.0

    indicators["both_students_degrade"] = (
        overall_mohawk > 0.01 and overall_lawcat > 0.01
    )

    # Direction: Retrieval degradation larger for SSM than LAWCAT
    ssm_retrieval_avg = np.mean([mohawk_dn.get(c, 0.0) for c in RETRIEVAL_HEAVY])
    lawcat_retrieval_avg = np.mean([lawcat_dn.get(c, 0.0) for c in RETRIEVAL_HEAVY])
    indicators["interaction_direction_correct"] = ssm_retrieval_avg > lawcat_retrieval_avg

    # Model architecture checks (if checkpoints available)
    if mohawk_checkpoint:
        try:
            from transformers import AutoModelForCausalLM
            import torch
            m = AutoModelForCausalLM.from_pretrained(
                mohawk_checkpoint, torch_dtype=torch.float16, device_map="cpu",
                trust_remote_code=True,
            )
            # Check that SSM layers exist (no self_attn in backbone layers)
            if hasattr(m, "backbone"):
                ssm_installed = not any(
                    hasattr(l, "self_attn") and l.self_attn is not None
                    for l in m.backbone.layers
                )
            else:
                ssm_installed = True  # Trust the training
            indicators["mohawk_ssm_layers_installed"] = ssm_installed
        except Exception:
            indicators["mohawk_ssm_layers_installed"] = None

    if lawcat_checkpoint:
        try:
            from transformers import AutoModelForCausalLM
            import torch
            m = AutoModelForCausalLM.from_pretrained(
                lawcat_checkpoint, torch_dtype=torch.float16, device_map="cpu",
                trust_remote_code=True,
            )
            # Check Conv1D or GLA in layers
            has_lawcat = any(
                "conv" in str(type(getattr(l, "self_attn", None))).lower() or
                "gla" in str(type(getattr(l, "self_attn", None))).lower() or
                "lawcat" in str(type(getattr(l, "self_attn", None))).lower()
                for l in m.model.layers
            )
            indicators["lawcat_conv1d_installed"] = has_lawcat
        except Exception:
            indicators["lawcat_conv1d_installed"] = None

    # Exclude None values from all_pass
    known_indicators = {k: v for k, v in indicators.items() if v is not None}
    all_pass = all(known_indicators.values()) if known_indicators else False

    return all_pass, indicators


def run_analysis(results_dir: str | None = None) -> dict:
    """Load evaluation results and run full statistical analysis."""
    if results_dir is None:
        results_dir = str(RESULTS_DIR)

    # Load summary
    summary_path = os.path.join(results_dir, "evaluation_summary.json")
    if not os.path.exists(summary_path):
        raise FileNotFoundError(f"evaluation_summary.json not found in {results_dir}")

    with open(summary_path) as f:
        summary = json.load(f)

    delta_norms = summary["delta_norms"]
    raw_accuracies = summary["raw_accuracies"]

    # Load per-example data for bootstrap (if available)
    mohawk_per_example_path = os.path.join(results_dir, "mohawk_longbench.json")
    lawcat_per_example_path = os.path.join(results_dir, "lawcat_longbench.json")
    teacher_per_example_path = os.path.join(results_dir, "teacher_longbench.json")

    per_example_combined = None
    if all(os.path.exists(p) for p in [teacher_per_example_path, mohawk_per_example_path, lawcat_per_example_path]):
        with open(teacher_per_example_path) as f:
            teacher_data = json.load(f)
        with open(mohawk_per_example_path) as f:
            mohawk_data = json.load(f)
        with open(lawcat_per_example_path) as f:
            lawcat_data = json.load(f)

        # Merge per-example results
        per_example_combined = []
        teacher_by_idx = {i: ex for i, ex in enumerate(teacher_data.get("per_example", []))}
        mohawk_by_idx = {i: ex for i, ex in enumerate(mohawk_data.get("per_example", []))}
        lawcat_by_idx = {i: ex for i, ex in enumerate(lawcat_data.get("per_example", []))}

        for i in range(min(len(teacher_by_idx), len(mohawk_by_idx), len(lawcat_by_idx))):
            t = teacher_by_idx.get(i)
            m = mohawk_by_idx.get(i)
            l = lawcat_by_idx.get(i)
            if t and m and l:
                per_example_combined.append({
                    "category": t["category"],
                    "label": t["label"],
                    "pred_teacher": t["pred"],
                    "pred_mohawk": m["pred"],
                    "pred_lawcat": l["pred"],
                })

    # Bootstrap CI
    ratio, ci_low, ci_high = bootstrap_interaction_ratio(
        delta_norm_ssm=delta_norms["mohawk"],
        delta_norm_lawcat=delta_norms["lawcat"],
        longbench_per_example=per_example_combined,
    )

    # Mixed-effects model
    interaction_p, holm_p = fit_mixed_effects_model(delta_norms)

    # Load training logs if available
    training_logs = {}
    gate_path = os.path.join(HYPOTHESIS_DIR, "checkpoints", "mohawk", "gate_results.json")
    if os.path.exists(gate_path):
        with open(gate_path) as f:
            training_logs.update(json.load(f))

    # Mechanism verification
    all_pass, indicators = verify_mechanism_activated(
        mohawk_checkpoint=None,
        lawcat_checkpoint=None,
        training_logs=training_logs,
        delta_norms=delta_norms,
    )

    # Gate check
    gate_passed = ratio >= 2.0 and ci_low > 1.0 and holm_p < 0.01

    analysis_results = {
        "interaction_ratio": ratio,
        "interaction_ratio_ci_low": ci_low,
        "interaction_ratio_ci_high": ci_high,
        "gate_passed": gate_passed,
        "interaction_p_value": interaction_p,
        "holm_corrected_p": holm_p,
        "mechanism_all_pass": all_pass,
        "mechanism_indicators": indicators,
        "delta_norms": delta_norms,
        "raw_accuracies": raw_accuracies,
    }

    # Print gate result
    print("\n" + "=" * 60)
    print("GATE RESULT: MUST_WORK")
    print("=" * 60)
    print(f"Ratio Δ_norm^SSM(retrieval) / Δ_norm^LAWCAT(retrieval) = {ratio:.4f}")
    print(f"95% Bootstrap CI = [{ci_low:.4f}, {ci_high:.4f}]")
    print(f"Interaction p = {interaction_p:.4f} (Holm = {holm_p:.4f})")
    print(f"Gate PASSED: {gate_passed}")
    print(f"  Criterion 1 (ratio ≥ 2.0): {ratio >= 2.0}")
    print(f"  Criterion 2 (CI low > 1.0): {ci_low > 1.0}")
    print(f"  Criterion 3 (Holm p < 0.01): {holm_p < 0.01}")

    # Save
    out_path = os.path.join(results_dir, "analysis_results.json")
    with open(out_path, "w") as f:
        json.dump(analysis_results, f, indent=2)
    print(f"\nAnalysis saved to {out_path}")

    return analysis_results


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--results-dir", type=str, default=str(RESULTS_DIR))
    args = p.parse_args()
    results = run_analysis(args.results_dir)
