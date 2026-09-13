# Config: H-M2
# Min vs. Mean Log-Prob Aggregation Sensitivity Across Distribution Types

**Applied**: flat module-level constants (matches H-E1/H-M1 pattern)

---

## Codebase Analysis

**Pattern Used**: flat module-level constants (dict + scalars), same as H-M1
**Inherits from**: H-E1 config (MODELS, SEED, MAX_NEW_TOKENS override to 20)

---

## C-1: Full H-M2 Config Schema

```python
# code/config.py  (complete file)
import os
import sys

# ── Paths ─────────────────────────────────────────────────────────────────────
_THIS_DIR   = os.path.dirname(os.path.abspath(__file__))
_H_M2_ROOT  = os.path.dirname(_THIS_DIR)
_REPO_ROOT  = os.path.dirname(os.path.dirname(os.path.dirname(_H_M2_ROOT)))
# _REPO_ROOT resolves to: /home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_question

H_E1_CODE_DIR    = os.path.join(_REPO_ROOT, "docs", "youra_research", "h-e1", "code")
H_M1_RESULTS_DIR = os.path.join(_REPO_ROOT, "docs", "youra_research", "h-m1", "results")

RESULTS_DIR = os.path.join(_H_M2_ROOT, "results")
FIGURES_DIR = os.path.join(_H_M2_ROOT, "figures")
LOG_FILE    = os.path.join(_H_M2_ROOT, "experiment.log")

# ── Models ────────────────────────────────────────────────────────────────────
MODELS = {
    "llama2":  "meta-llama/Llama-2-7b-hf",
    "mistral": "mistralai/Mistral-7B-v0.1",
}
MODELS_TO_RUN = ["llama2", "mistral"]   # llama2 primary; mistral secondary replication

# ── Datasets ──────────────────────────────────────────────────────────────────
DATASETS = ["trivia_qa", "nq", "truthful_qa"]

N_SAMPLES = {
    "trivia_qa":   400,    # Farquhar 2023 seed-fixed test split
    "nq":          400,    # Farquhar 2023 seed-fixed test split
    "truthful_qa": 817,    # full generation split
}

FEW_SHOT_K = {
    "trivia_qa":   4,      # Farquhar 2023 4-shot format
    "nq":          4,      # Farquhar 2023 4-shot format
    "truthful_qa": 0,      # 0-shot
}

# ── Inference ─────────────────────────────────────────────────────────────────
MAX_NEW_TOKENS = 20        # short-phrase regime (Farquhar 2023: answers are short phrases)
SEED           = 42        # fixed for dataset sampling and reproducibility
TORCH_DTYPE    = "float16" # use torch.float16 in code
DEVICE_MAP     = "auto"    # multi-GPU support

# ── Aggregation ───────────────────────────────────────────────────────────────
AGGREGATION_METHODS = ["min", "mean", "raw_sum"]

# ── Statistical Analysis ──────────────────────────────────────────────────────
N_RESAMPLES_BOOTSTRAP = 1000
CONFIDENCE_LEVEL      = 0.95
BOOTSTRAP_METHOD      = "percentile"   # scipy.stats.bootstrap method parameter
BOOTSTRAP_PAIRED      = True           # paired=True for within-sample CI

# ── Sanity Checks ─────────────────────────────────────────────────────────────
MIN_GENERATED_TOKENS       = 2         # filter 1-token degenerate outputs
DEGENERATE_FRACTION_MAX    = 0.05      # fail-fast if > 5% degenerate samples

# ── Scoring / Labels ──────────────────────────────────────────────────────────
TRIVIAQA_NQ_SCORING        = "exact_match_normalized"  # lowercase, strip punct/articles
TRUTHFULQA_ROUGE_THRESHOLD = 0.3       # ROUGE-L F1 threshold for truthful label
```

---

## C-2: Visualization Config

```python
# Embed in code/figures.py

VIZ_CONFIG = {
    # Colors — consistent across all figures
    "color_min":      "#E74C3C",   # red (min aggregation)
    "color_mean":     "#3498DB",   # blue (mean aggregation)
    "color_raw_sum":  "#95A5A6",   # grey (raw_sum baseline)
    "color_correct":  "#2ECC71",   # green (correct samples)
    "color_hallucinated": "#E74C3C",  # red (hallucinated samples)

    # Figure sizes (width, height) inches
    "figsize_rho_bar":     (10, 6),   # ρ differential bar chart (mandatory)
    "figsize_rho_scatter": (8, 6),    # scatter: ρ(min) vs ρ(mean)
    "figsize_auroc_heatmap": (9, 5),  # AUROC heatmap
    "figsize_dist_overlay": (8, 5),   # distribution overlays

    # Output quality
    "dpi": 150,

    # Annotation
    "p_value_format": "{:.3f}",
    "sig_marker":     "*",
    "ns_marker":      "ns",

    # File names
    "fname_rho_bar":      "rho_differential_bar.png",         # MANDATORY
    "fname_rho_scatter":  "rho_scatter.png",
    "fname_auroc_heatmap": "auroc_heatmap.png",
    "fname_dist_overlay": "dist_overlay_{dataset}.png",       # .format(dataset=...)
}
```

---

## C-3: Results Summary Schema

The `results_summary.json` written to `h-m2/results/` has this structure:

```python
{
    "llama2": {
        "trivia_qa": {
            "rho_min":      float,   # Spearman ρ(min scores, labels)
            "rho_mean":     float,   # Spearman ρ(mean scores, labels)
            "rho_raw_sum":  float,
            "pval_min":     float,
            "pval_mean":    float,
            "pval_raw_sum": float,
            "ci_min":       [float, float],   # 95% bootstrap CI
            "ci_mean":      [float, float],
            "ci_raw_sum":   [float, float],
            "auroc_min":    float,
            "auroc_mean":   float,
            "auroc_raw_sum": float,
            "diff_min_mean": float,           # rho(min) - rho(mean)
            "diff_ci":      [float, float],
            "min_beats_mean": bool,
            "n_samples":    int,
            "n_hallucinated": int,
            "n_correct":    int,
        },
        "nq": { ... },           # same schema
        "truthful_qa": { ... },  # same schema
    },
    "mistral": { ... },          # same schema
    "gate": {
        "gate":   str,           # "PASS" | "PARTIAL_PASS_P1_ONLY" | "PARTIAL_PASS_P2_ONLY" | "FAIL"
        "p1_met": bool,
        "p2_met": bool,
    }
}
```

---

## C-4: Hyperparameter Rationale

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `MAX_NEW_TOKENS` | 20 | Short-phrase QA answers; Farquhar 2023 regime; prevents padding effects |
| `N_SAMPLES["trivia_qa"]` | 400 | Farquhar 2023 exact test split size |
| `N_SAMPLES["nq"]` | 400 | Farquhar 2023 exact test split size |
| `N_SAMPLES["truthful_qa"]` | 817 | Full generation split — no subsampling needed |
| `FEW_SHOT_K` | 4 (TriviaQA/NQ), 0 (TruthfulQA) | Farquhar 2023 format; TruthfulQA is 0-shot by convention |
| `SEED` | 42 | Fixed for dataset sampling; matches H-M1 and H-E1 |
| `N_RESAMPLES_BOOTSTRAP` | 1000 | Standard for 95% CI stability |
| `CONFIDENCE_LEVEL` | 0.95 | Standard two-sided 95% CI |
| `TRUTHFULQA_ROUGE_THRESHOLD` | 0.3 | Matches H-E1 `score_answer` ROUGE-L threshold |
| `MIN_GENERATED_TOKENS` | 2 | Filter 1-token outputs where min == mean |
| `DEGENERATE_FRACTION_MAX` | 0.05 | Fail-fast guard: > 5% degenerate → pipeline error |

---

## C-5: Subtasks

| ID | Subtask | Description |
|----|---------|-------------|
| C-1 | Full H-M2 Config | Paths, dataset/model/inference/analysis constants; complete config.py |
| C-2 | Visualization Config | VIZ_CONFIG dict with colors, sizes, DPI, filenames |
