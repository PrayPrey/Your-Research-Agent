from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


def _default_serializer(obj):
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, float) and np.isnan(obj):
        return None
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def write_results_json(
    score_matrix: pd.DataFrame,
    corr_results: pd.DataFrame,
    factor_results: dict,
    gate_eval: dict,
    out_path: Path,
) -> None:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "generated_at": datetime.utcnow().isoformat(),
        "hypothesis": "h-e1",
        "gate_evaluation": {
            "PASS": gate_eval.get("PASS", False),
            "results": [
                {
                    "pair": list(r["pair"]),
                    "rho": r["rho"],
                    "ci_low": r["ci"][0],
                    "ci_high": r["ci"][1],
                    "passes": r["passes"],
                }
                for r in gate_eval.get("results", [])
            ],
        },
        "score_matrix": json.loads(score_matrix.to_json(orient="records")),
        "partial_corr_matrix": json.loads(corr_results.to_json(orient="records")),
        "factor_analysis": {
            "loadings": factor_results.get("loadings", []),
            "variance_explained": factor_results.get("variance_explained"),
            "kmo": factor_results.get("kmo"),
            "congruence": factor_results.get("congruence"),
        },
    }

    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2, default=_default_serializer)


def write_validation_md(
    gate_eval: dict,
    corr_results: pd.DataFrame,
    factor_results: dict,
    loo_results: dict,
    out_path: Path,
) -> None:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    gate_pass = gate_eval.get("PASS", False)
    gate_str = "**PASS**" if gate_pass else "**FAIL**"
    congruence = factor_results.get("congruence", float("nan"))
    kmo = factor_results.get("kmo", float("nan"))
    var_exp = factor_results.get("variance_explained", float("nan"))
    auc = loo_results.get("auc", float("nan"))
    auc_mmlu = loo_results.get("auc_mmlu_only", float("nan"))

    lines = [
        "# Phase 4 Validation Report — H-E1",
        "",
        f"**Generated:** {datetime.utcnow().isoformat()}",
        f"**Gate Type:** MUST_WORK",
        f"**Gate Result:** {gate_str}",
        "",
        "## Gate Evaluation",
        "",
        "| Pair | Partial ρ | BCa CI 95% | Passes |",
        "|------|-----------|------------|--------|",
    ]
    for r in gate_eval.get("results", []):
        pair_str = f"{r['pair'][0]} vs {r['pair'][1]}"
        ci = r["ci"]
        lines.append(
            f"| {pair_str} | {r['rho']:.3f} | [{ci[0]:.3f}, {ci[1]:.3f}] | {'✓' if r['passes'] else '✗'} |"
        )

    lines += [
        "",
        "## Partial Spearman Correlation Matrix (Top 5 by |ρ|)",
        "",
        "| x | y | ρ | CI low | CI high | p-value |",
        "|---|---|---|--------|---------|---------|",
    ]
    top5 = corr_results.reindex(corr_results["rho"].abs().sort_values(ascending=False).index).head(5)
    for _, row in top5.iterrows():
        lines.append(
            f"| {row['x']} | {row['y']} | {row['rho']:.3f} | {row['ci_low']:.3f} | {row['ci_high']:.3f} | {row['p_value']:.4f} |"
        )

    lines += [
        "",
        "## Factor Analysis",
        "",
        f"- KMO adequacy: {kmo:.3f}" if not (isinstance(kmo, float) and kmo != kmo) else "- KMO adequacy: N/A",
        f"- Variance explained (Factor 1): {var_exp:.1%}" if not (isinstance(var_exp, float) and var_exp != var_exp) else "- Variance explained: N/A",
        f"- Tucker's congruence (greedy vs T=0.7): {congruence:.3f}" if not (isinstance(congruence, float) and congruence != congruence) else "- Tucker congruence: N/A",
        f"  - Threshold: ≥ 0.85 → {'✓ PASS' if isinstance(congruence, float) and not (congruence != congruence) and congruence >= 0.85 else '✗ FAIL'}",
        "",
        "## LOO Logistic Regression (AUC)",
        "",
        f"- Composite (ECE + TruthfulQA + Brier) AUC: {auc:.3f}" if not (isinstance(auc, float) and auc != auc) else "- Composite AUC: N/A",
        f"- MMLU-only baseline AUC: {auc_mmlu:.3f}" if not (isinstance(auc_mmlu, float) and auc_mmlu != auc_mmlu) else "- MMLU-only AUC: N/A",
        "",
        "## Summary",
        "",
        f"The MUST_WORK gate for H-E1 has {'**PASSED**' if gate_pass else '**FAILED**'}.",
        "",
        "The experiment verified whether partial Spearman correlations between epistemic",
        "reliability metrics (ECE, TruthfulQA%, AdvGLUE drop) exceed the |ρ| ≥ 0.40 threshold",
        "with BCa 95% CIs excluding zero.",
    ]

    out_path.write_text("\n".join(lines))
