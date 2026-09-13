---
hypothesis_id: H-M1
phase: Phase 3
generated: 2026-08-25
author: yoon303@ust.ac.kr
base_hypothesis: H-E1
---

# Configuration: H-M1 — Paraphrase Token Entropy Variance Analysis

Applied: analysis-only-hardcoded-dict pattern (no training params, no grid)
Applied: inherited-base-config pattern (reuse H-E1 NLI model, seed, n defaults)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (incremental on H-E1)
**Status**: config classes verified from base code (h-e1/code/run.py direct read)
**Config Files Found**: `docs/youra_research/h-e1/code/run.py` (CONFIG dict)
**Pattern Used**: hardcoded dict (analysis-only — no training hyperparameters)

---

## Inherited Configuration (Base Hypothesis)

### CONFIG Dict (From Actual H-E1 Code — run.py)

```python
# Verified from: docs/youra_research/h-e1/code/run.py
CONFIG = {
    "model_id": "meta-llama/Llama-2-7b-hf",       # ← actual code value
    "nli_model_id": "cross-encoder/nli-deberta-v3-large",  # ← actual code value
    "nli_device": 0,
    "K": 10,
    "n_pilot": 98,
    "seed": 42,
    "bootstrap_iterations": 1000,
    "gap_threshold": 0.05,
    "gap_extend_low": 0.03,
    "avg_clusters_min": 1.5,
    "out_dir": "docs/youra_research/h-e1/results/",
    "figures_dir": "docs/youra_research/h-e1/figures/",
}
```

**Verified from**: `docs/youra_research/h-e1/code/run.py` (actual implementation).
Note: H-E1 spec listed `deberta-large-mnli` but actual code uses `cross-encoder/nli-deberta-v3-large`. H-M1 inherits the actual code value.

---

## H-M1 Configuration

### CONFIG Dict (copy-paste into h-m1/code/run.py)

```python
CONFIG = {
    # --- Inherited from H-E1 (verified from actual run.py) ---
    "nli_model_id": "cross-encoder/nli-deberta-v3-large",
    "nli_device": 0,
    "K": 10,
    "n": 98,
    "seed": 42,

    # --- H-E1 source paths ---
    "he1_results_dir": "docs/youra_research/h-e1/results/",
    "he1_code_dir": "docs/youra_research/h-e1/code/",
    "samples_path": None,  # auto-detect h-e2-v2 JSONL if None

    # --- H-M1 output paths ---
    "out_dir": "docs/youra_research/h-m1/results/",
    "figures_dir": "docs/youra_research/h-m1/figures/",

    # --- Gate thresholds (A-5) ---
    "intra_var_threshold": 0.1,         # primary gate: mean intra-cluster var > 0.1 nats
    "min_passing_questions": 15,        # must pass on ≥15 of eligible
    "min_eligible_questions": 20,       # assert: ≥20 questions have paraphrase pairs
    "variance_thresholds": [0.05, 0.1, 0.2, 0.5],  # sensitivity table thresholds

    # --- Figure settings (A-6) ---
    "fig_dpi": 150,
    "fig_size_bar": (6, 4),             # fig1_gate_bar, fig5_threshold_sensitivity
    "fig_size_violin": (8, 5),          # fig2_violin_intra_var
    "fig_size_scatter": (6, 5),         # fig3_scatter_size_var
    "fig_size_heatmap": (10, 4),        # fig4_nli_heatmap (3 panels)
    "n_heatmap_questions": 3,           # representative questions for NLI heatmap
    "color_palette": "Set2",            # seaborn palette for all plots
    "threshold_color": "#d62728",       # red line for 0.1 nats gate marker
}
```

---

## A-5: Gate Verification Config [Complexity: 10, Budget: 2 subtasks]

Applied: threshold-sensitivity-table pattern

```python
# Gate constants (also in CONFIG above — copy for evaluate.py clarity)
GATE = {
    "intra_var_threshold": 0.1,
    "min_passing_questions": 15,
    "min_eligible_questions": 20,
    "variance_thresholds": [0.05, 0.1, 0.2, 0.5],
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Gate thresholds config | `intra_var_threshold`, `min_passing_questions`, `min_eligible_questions` used by `verify_mechanism_activated()` |
| C-5-2 | Sensitivity metrics config | `variance_thresholds` list for threshold sensitivity table in `compute_secondary_metrics()` |

---

## A-6: Visualization Config [Complexity: 9, Budget: 2 subtasks]

Applied: per-figure-size pattern (different aspect ratios per plot type)

```python
# Figure constants (also in CONFIG above — copy for visualize.py clarity)
FIG = {
    "dpi": 150,
    "size_bar": (6, 4),
    "size_violin": (8, 5),
    "size_scatter": (6, 5),
    "size_heatmap": (10, 4),
    "n_heatmap_questions": 3,
    "palette": "Set2",
    "threshold_color": "#d62728",
}

# Figure filename map
FIGURE_FILES = {
    "gate_bar": "fig1_gate_bar.png",
    "violin": "fig2_violin_intra_var.png",
    "scatter": "fig3_scatter_size_var.png",
    "heatmap": "fig4_nli_heatmap.png",
    "sensitivity": "fig5_threshold_sensitivity.png",
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Figure size + DPI config | Per-figure sizes (`fig_size_*`), `fig_dpi=150`, `n_heatmap_questions=3` |
| C-6-2 | Color + palette config | `color_palette="Set2"`, `threshold_color="#d62728"` for gate marker line across all plots |

---

## Argparse CLI Specification

```python
def parse_args():
    p = argparse.ArgumentParser(description="H-M1: Paraphrase TE variance analysis")
    p.add_argument("--he1-results-dir", type=str, default=CONFIG["he1_results_dir"])
    p.add_argument("--he1-code-dir", type=str, default=CONFIG["he1_code_dir"])
    p.add_argument("--samples-path", type=str, default=None)
    p.add_argument("--out-dir", type=str, default=CONFIG["out_dir"])
    p.add_argument("--figures-dir", type=str, default=CONFIG["figures_dir"])
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--smoke-test", action="store_true", help="N=5 only; verify no crash.")
    p.add_argument("--skip-recompute", action="store_true",
                   help="Load cached per-sample TE + cluster data; skip recomputation.")
    return p.parse_args()
```
