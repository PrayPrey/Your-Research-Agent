"""H-M2 Report Generation: 04_validation.md."""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict

from config import HM2Config


def generate_validation_report(
    cfg: HM2Config,
    results: Dict,
    stat_results: Dict,
    gate_result: Dict,
) -> str:
    """Generate 04_validation.md report.

    Returns path to generated report.
    """
    gate_pass = gate_result.get("gate_pass", False)
    gate_verdict = gate_result.get("verdict", "unknown")
    rho = gate_result.get("rho", 0)
    pvalue = gate_result.get("pvalue", 1)
    reason = gate_result.get("reason", "")

    spearman = stat_results.get("spearman", {})
    ols = stat_results.get("ols", {})
    neg_ctrl = stat_results.get("negative_control", {})
    configs_used = stat_results.get("configs_used", [])

    status_emoji = "PASS" if gate_pass else "FAIL (EXPLORE)"

    # Build probe results table
    probe_results = results.get("probe_results", {})
    probe_table_rows = []
    for cid in ["C0", "C1", "C2", "C3", "C4", "C5", "C6", "C7"]:
        r = probe_results.get(cid, {})
        m = r.get("mean_logit_margin")
        n = r.get("n_samples", 0)
        m_str = f"{m:.4f}" if m is not None else "N/A"
        probe_table_rows.append(f"| {cid} | {m_str} | {n} |")
    probe_table = "\n".join(probe_table_rows)

    neg_ctrl_str = ""
    if neg_ctrl:
        delta = neg_ctrl.get("delta", "N/A")
        passes = neg_ctrl.get("passes", False)
        neg_ctrl_str = f"**|C7-C0| = {delta:.4f}** — {'PASS' if passes else 'FAIL'} (threshold: {cfg.negative_control_delta_threshold})"
    else:
        neg_ctrl_str = "Negative control data unavailable"

    ols_str = ""
    if ols:
        ols_str = (
            f"- Coefficient: {ols.get('coef', 'N/A'):.4f}\n"
            f"- Intercept: {ols.get('intercept', 'N/A'):.4f}\n"
            f"- R²: {ols.get('r_squared', 'N/A'):.4f}\n"
            f"- p-value: {ols.get('pvalue', 'N/A'):.4f}\n"
            f"- Meets R²>0.3 criterion: {ols.get('meets_r2_criterion', 'N/A')}"
        )
    else:
        ols_str = "OLS results unavailable"

    report = f"""# H-M2 Validation Report

**Hypothesis**: Corpus Entropy → Model Logit Margin Internalization
**Gate Type**: SHOULD_WORK
**Gate Result**: {status_emoji}
**Generated**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

---

## Executive Summary

H-M2 tests whether training corpus occupational-demographic entropy (H(occ|demo))
is internalized by Pythia-1B as a logit margin for gender-stereotyped occupations.

**Primary Gate (Spearman ρ > 0, p < 0.01):**
- Spearman ρ = {rho:.4f}
- p-value = {pvalue:.6f}
- 95% CI: [{spearman.get('ci_lower', 'N/A'):.4f}, {spearman.get('ci_upper', 'N/A'):.4f}]
- **Verdict: {gate_verdict}**
- Reason: {reason}

---

## Probe Results

| Config | Mean Logit Margin | N Samples |
|--------|-------------------|-----------|
{probe_table}

Configs used for main analysis: {configs_used}

---

## Statistical Tests

### 1. Spearman Rank Correlation (Primary Gate)

- ρ = {rho:.4f}
- p = {pvalue:.6f}
- 95% CI = [{spearman.get('ci_lower', 'N/A'):.4f}, {spearman.get('ci_upper', 'N/A'):.4f}]
- N bootstrap = {cfg.n_bootstrap}
- Gate threshold: ρ > 0, p < {cfg.alpha_level}
- **Gate: {'PASS' if gate_pass else 'FAIL'}**

### 2. Log-Linear OLS (logit_margin ~ log(H_entropy))

{ols_str}

### 3. Negative Control (C7 vs C0)

{neg_ctrl_str}

---

## Figures Generated

1. `figures/01_entropy_vs_margin.png` — Scatter: H(occ|demo) vs. mean logit margin
2. `figures/02_logit_margin_heatmap.png` — Heatmap: occupation × config
3. `figures/03_training_curves.png` — Training loss curves per config
4. `figures/04_negative_control.png` — C0 vs C7 comparison
5. `figures/05_config_comparison.png` — Logit margins sorted by entropy

---

## Gate Decision

**Gate Type**: SHOULD_WORK
**Result**: {gate_verdict}

{"✓ Gate PASSED: Spearman ρ > 0 and p < 0.01 confirmed. Corpus entropy is internalized as logit margin." if gate_pass else "✗ Gate FAILED: Gate conditions not met. Action: EXPLORE — investigate training depth, probe design, or corpus quality."}

---

## Notes

- Quick run (50B tokens, {cfg.train_iters_quick} steps) used for PoC gating
- Architecture: Pythia-1B (GPT-NeoX), hidden_size=2048, 16 layers
- Probe: WinoBias 20 occupation pairs × 50+ templates
- Corpus configs: C0 (unfiltered) through C6 (filtered) + C7 (negative control)
- H-M2 builds on H-M1 (occupational entropy) and H-E1 (corpus construction)
"""

    report_path = Path(cfg.validation_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    print(f"[report] Validation report written: {report_path}")
    return str(report_path)
