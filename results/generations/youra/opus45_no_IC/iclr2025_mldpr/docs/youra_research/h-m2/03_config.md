# Config: H-M2 (MECHANISM Validation)

**Applied**: No KB pattern matched (search "experiment config dataclass patterns" returned unrelated torch/inductor config, consistency_models launch script, and a LaTeX knitting-patterns page — none applicable). Using hardcoded-dict pattern, same as H-M1 (statistical validation script, no trainable hyperparameters).

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1) + external (H-E1)
**Status**: Both `h-m1/code/` and `h-e1/code/` / `h-e1/data/` confirmed absent (per h-m2/03_architecture.md Codebase Analysis — glob returned no files). No actual config classes exist to verify field names against. Falling back to specs (h-m1/03_architecture.md, h-e1/04_validation.md) for HHI table field names, and h-m1/03_config.md for pattern consistency only (H-M1 also has no config.py — hardcoded dicts inlined).
**Config Files Found**: None — H-M1 and H-E1 have no `config.py`
**Pattern Used**: Hardcoded dict (single fixed config; architecture.md specifies "no config.py, few constants used once")

---

## Configuration

Matches architecture.md: no `config.py`; constants inlined in `analyze.py` (or a small shared block imported by `data_loader.py`/`labeling.py`).

```python
CONFIG = {
    # Data paths
    "pwc_papers_path": "h-m2/data/papers-with-abstracts.json",
    "pwc_datasets_path": "h-m2/data/datasets.json",
    "hf_fallback_dataset": "paperswithcode/paperswithcode-data",
    "hhi_source_path": "h-e1/04_validation.md",   # derived table; recompute via H-M1 compute_hhi if absent
    "results_out_path": "h-m2/results/results.json",
    "figures_out_dir": "h-m2/figures/",

    # Venue/year scope (FR-1.1)
    "venues": ("NeurIPS", "ICML", "ICLR"),
    "years": range(2018, 2025),   # 2018-2024 inclusive

    # Standard benchmark identification (FR-2.1)
    "top_n": 5,   # top-5 datasets by usage count in venue's prior year

    # Statistical thresholds (Gate Condition, Success Criteria)
    "alpha": 0.05,             # p-value gate on beta_hhi (primary, MUST)
    "odds_ratio_threshold": 1.5,   # effect-meaningful secondary criterion (SHOULD)
    "effect_size_threshold": 0.1,  # |beta| > 0.1 for verify_mechanism_activation

    # Data quality minimums (NFR-2)
    "min_papers": 500,

    # Reproducibility
    "seed": 42,
}
```

**Non-standard**: `effect_size_threshold=0.1` — not stated explicitly in PRD success criteria table, but required by architecture.md's `verify_mechanism_activation` (`effect_meaningful(|beta|>0.1)`); kept consistent with that function signature.

---

## Figure Output Settings

```python
FIGURE_CONFIG = {
    "dpi": 150,
    "format": "png",
    "figsize": (8, 6),
    "filenames": {
        "gate_metrics": "gate_metrics.png",
        "hhi_adoption_scatter": "hhi_vs_adoption_scatter.png",
        "predicted_probability": "predicted_probability_curve.png",
        "model_comparison": "model_comparison_table.png",
    },
}
```

---

## Subtasks

None (0 budget used of 5 — statistical validation script per architecture.md's "no config.py" note; config is 2 inline dicts, same pattern as H-M1).
