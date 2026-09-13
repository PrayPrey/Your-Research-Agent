# Config: H-M1 (MECHANISM Validation)

**Applied**: Standard scipy.stats hardcoded-dict pattern (PoC/validation script, no training hyperparameters). No KB pattern matched (KB only returned unrelated diffusion/training configs).

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: `h-e1/code/` confirmed absent (per `h-m1/03_architecture.md` Codebase Analysis section — glob returned no files). Serena skipped for code verification since there is no actual implementation to inspect; falling back to spec (`h-e1/03_architecture.md`) for the `compute_hhi` reimplementation, and to `h-e1/03_prd.md` mean-HHI figure (0.0171) for sanity context only.
**Config Files Found**: None — H-E1 has no `config.py`
**Pattern Used**: Hardcoded dict (single fixed config, no dataclass needed — this is a 21-datapoint validation script, not a trainable module)

---

## Configuration

No config.py needed — single small dict inlined in `validate.py`, matching architecture.md's "no config.py needed" note.

```python
CONFIG = {
    # Data paths
    "cache_path": "h-e1/data/pwc_papers_filtered.parquet",
    "hf_fallback_dataset": "pwc-archive/papers-with-abstracts",
    "results_out_path": "h-m1/results/results.json",
    "figures_out_dir": "h-m1/figures/",

    # Statistical thresholds (FR-5, success criteria)
    "alpha": 0.05,              # Mann-Whitney p-value gate (primary, MUST)
    "spearman_rho_threshold": 0.7,   # secondary criterion (SHOULD)
    "spearman_alpha": 0.05,     # secondary p-value criterion (SHOULD)
    "mannwhitney_alternative": "greater",  # one-sided: high-HHI > low-HHI

    # Top-5 share computation
    "top_n": 5,

    # Group split
    "split_method": "median",   # median HHI split into high/low groups

    # Reproducibility
    "seed": 42,                 # unused by scipy.stats (deterministic), kept for convention
}
```

**Non-standard**: none — all values are directly from PRD success criteria (FR-5.1/5.2, Success Criteria table).

---

## Figure Output Settings

```python
FIGURE_CONFIG = {
    "dpi": 150,
    "format": "png",
    "figsize": (8, 6),
    "filenames": {
        "bar": "group_comparison_bar.png",
        "scatter": "hhi_vs_top5_scatter.png",
        "histograms": "distribution_histograms.png",
        "heatmap": "venue_year_heatmap.png",
    },
}
```

---

## Subtasks

None (0 budget — validation script needs no config subtask breakdown; config is 2 inline dicts).
