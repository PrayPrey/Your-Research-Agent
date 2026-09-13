---
hypothesis_id: H-E1
phase: Phase 3
generated: 2026-08-25
author: yoon303@ust.ac.kr
---

# Configuration: H-E1 — SE vs TE AUROC Comparison

Applied: EXISTENCE PoC single-config pattern (fixed values, 1 seed, no grid)
Applied: Argparse CLI pattern (LIGHT tier — no YAML needed)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design, no existing code to analyze
**Config Files Found**: None - new config
**Pattern Used**: hardcoded dict + argparse CLI

---

## Configuration Dict (copy-paste into run.py)

```python
CONFIG = {
    # LLM
    "model_id": "meta-llama/Llama-2-7b-hf",
    "torch_dtype": "float16",
    "device_map": "auto",

    # NLI
    "nli_model_id": "cross-encoder/nli-deberta-v3-large",
    "nli_device": 0,

    # Stochastic sampling (for SE / h-e2-v2 fallback regeneration)
    "temperature": 0.7,
    "max_new_tokens": 50,
    "top_p": 1.0,
    "K": 10,

    # TE: greedy decode (temperature=0 means greedy in HF generate)
    "te_temperature": 0,
    "te_nonzero_threshold": 0.0,

    # Experiment
    "n_pilot": 98,
    "n_extension": 500,
    "seed": 42,

    # Evaluation
    "bootstrap_iterations": 1000,

    # Decision gates
    "gap_threshold": 0.05,        # MUST_WORK gate: SE - TE >= 0.05
    "gap_extend_low": 0.03,       # Extension trigger: gap in [0.03, 0.05]
    "avg_clusters_min": 1.5,      # Mechanism verification: avg_clusters > 1.5

    # Paths (overridable via CLI)
    "out_dir": "docs/youra_research/h-e1/results/",
    "figures_dir": "docs/youra_research/h-e1/figures/",
}
```

---

## Argparse CLI Specification

All flags for `code/run.py`:

```python
import argparse

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="H-E1: SE vs TE AUROC on TriviaQA/Llama-2-7B")

    p.add_argument(
        "--samples-path",
        type=str,
        required=True,
        help="Path to h-e2-v2 K=10 samples file (JSON or dir). Required.",
    )
    p.add_argument(
        "--n",
        type=int,
        default=98,
        choices=range(1, 10001),
        metavar="N",
        help="Number of questions to evaluate. Default: 98 (pilot). Use 500 for extension.",
    )
    p.add_argument(
        "--out-dir",
        type=str,
        default="docs/youra_research/h-e1/results/",
        help="Output directory for results.json and *.npy files.",
    )
    p.add_argument(
        "--figures-dir",
        type=str,
        default="docs/youra_research/h-e1/figures/",
        help="Output directory for figures.",
    )
    p.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for bootstrap and sampling. Default: 42.",
    )
    p.add_argument(
        "--smoke-test",
        action="store_true",
        help="Run on N=5 questions only; verify no crash. Skips result saving.",
    )
    p.add_argument(
        "--skip-te",
        action="store_true",
        help="Skip TE computation (reuse cached te_scores.npy if present).",
    )
    p.add_argument(
        "--extension",
        action="store_true",
        help="Run extension protocol: N=500, non-overlapping with pilot N=98.",
    )

    return p.parse_args()
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `HF_TOKEN` | Yes | HuggingFace token for gated `meta-llama/Llama-2-7b-hf` access |

Usage in code:
```python
import os
from huggingface_hub import login
login(token=os.environ["HF_TOKEN"])
```

---

## Hyperparameters Reference

| Parameter | Type | Default | Valid Range | Notes |
|-----------|------|---------|-------------|-------|
| `model_id` | str | `meta-llama/Llama-2-7b-hf` | — | Gated; needs HF_TOKEN |
| `torch_dtype` | str | `float16` | float16, bfloat16 | — |
| `nli_model_id` | str | `cross-encoder/nli-deberta-v3-large` | — | — |
| `temperature` | float | 0.7 | (0.0, 2.0] | SE sampling only |
| `te_temperature` | int | 0 | 0 | Greedy decode for TE |
| `max_new_tokens` | int | 50 | [10, 200] | — |
| `top_p` | float | 1.0 | (0.0, 1.0] | Nucleus sampling |
| `K` | int | 10 | [5, 50] | Samples per question for SE |
| `n_pilot` | int | 98 | [10, 500] | Pilot questions |
| `n_extension` | int | 500 | [100, 2000] | Extension questions |
| `seed` | int | 42 | any int | All random ops |
| `bootstrap_iterations` | int | 1000 | [100, 10000] | — |
| `gap_threshold` | float | 0.05 | (0.0, 1.0) | MUST_WORK gate |
| `gap_extend_low` | float | 0.03 | (0.0, gap_threshold) | Extension trigger lower bound |
| `avg_clusters_min` | float | 1.5 | (1.0, K) | Mechanism verification |
| `te_nonzero_threshold` | float | 0.0 | [0.0, 1.0) | TE sanity check floor |

---

## File / Directory Conventions

```
docs/youra_research/h-e1/
    code/
        run.py
        data.py
        compute_te.py
        compute_se.py
        evaluate.py
    results/                        # auto-created by save_results()
        results.json                # {n_questions, auroc_te, auroc_se, gap, te_ci, se_ci, avg_clusters, correctness_rate}
        te_scores.npy
        se_scores.npy
        correctness.npy
    figures/                        # auto-created by plot_figures()
        fig1_auroc_bar.png          # Bar chart: SE vs TE AUROC with 95% CI
        fig2_roc_curves.png         # ROC curves overlaid
        fig3_violin_distributions.png  # Uncertainty score distributions
        fig4_bootstrap_hist.png     # Bootstrap AUROC histogram
```

Directory creation pattern:
```python
import os
os.makedirs(CONFIG["out_dir"], exist_ok=True)
os.makedirs(CONFIG["figures_dir"], exist_ok=True)
```

---

## Decision Logic (Gate Constants)

```python
# In run.py main(), after computing gap = auroc_se - auroc_te:
if gap >= CONFIG["gap_threshold"]:
    print(f"PASS: gap={gap:.4f} >= {CONFIG['gap_threshold']} — H-E1 CONFIRMED")
elif gap >= CONFIG["gap_extend_low"]:
    print(f"EXTEND: gap={gap:.4f} in [{CONFIG['gap_extend_low']}, {CONFIG['gap_threshold']}] — running N=500")
    # re-invoke with --n 500 --extension or inline extension protocol
else:
    print(f"FAIL: gap={gap:.4f} < {CONFIG['gap_extend_low']} — H-E1 NOT CONFIRMED")
```
