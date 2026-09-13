# Configuration: H-M1 — Transfer Inversion Mechanism Analysis

**Applied: hardcoded dict pattern (analysis-only, no training)**

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — analysis script only, reuses H-E2 SFT outputs as inputs
**Config Files Found**: None — new config
**Pattern Used**: hardcoded dict

---

## Full Configuration

```python
# h_m1_analysis.py  —  top-level constants, copy-paste ready

# ── Paths ──────────────────────────────────────────────────────────────────
PATHS = {
    "h_e2_results_dir":     "docs/youra_research/h-e2/results/",
    "h_e2_checkpoints_dir": "docs/youra_research/h-e2/checkpoints/",
    "output_dir":           "docs/youra_research/h-m1/",
    "figures_dir":          "docs/youra_research/h-m1/figures/",
    "result_file":          "docs/youra_research/h-m1/h_m1_result.json",
}

# ── Analysis ───────────────────────────────────────────────────────────────
ANALYSIS = {
    "conditions": ["humaneval_only", "mbpp_only", "leetcode_only", "equal_mix"],
    "benchmarks": ["humaneval_plus", "mbpp_plus"],
    "seeds": {
        "humaneval_only": [42, 123],
        "mbpp_only":      [42, 777],
        "leetcode_only":  [42, 123, 777],
        "equal_mix":      [123],
    },
    "primary_conditions": ["humaneval_only", "mbpp_only"],  # for inversion check
    "success_threshold": 0.667,   # non-standard: ≥2/3 seeds must show inversion
    "min_valid_seeds":   1,       # minimum seeds present to attempt analysis
}

# ── Fallback (if MBPP+ results missing from H-E2) ─────────────────────────
FALLBACK = {
    "fallback_eval_enabled": True,
    "evalplus_dataset":      "mbpp",
    "evalplus_backend":      "hf",
    "evalplus_greedy":       True,
    "evalplus_batch_size":   16,
}

# ── Figures ────────────────────────────────────────────────────────────────
FIGURE = {
    "dpi":             300,
    "format":          "png",
    "heatmap_figsize": [10, 4],
    "strip_figsize":   [12, 4],
    "delta_figsize":   [8, 4],
    "colormap":        "RdYlGn",
}
```

---

## Sample YAML Config (reference equivalent)

```yaml
paths:
  h_e2_results_dir:     "docs/youra_research/h-e2/results/"
  h_e2_checkpoints_dir: "docs/youra_research/h-e2/checkpoints/"
  output_dir:           "docs/youra_research/h-m1/"
  figures_dir:          "docs/youra_research/h-m1/figures/"
  result_file:          "docs/youra_research/h-m1/h_m1_result.json"

analysis:
  conditions: [humaneval_only, mbpp_only, leetcode_only, equal_mix]
  benchmarks: [humaneval_plus, mbpp_plus]
  seeds:
    humaneval_only: [42, 123]
    mbpp_only:      [42, 777]
    leetcode_only:  [42, 123, 777]
    equal_mix:      [123]
  primary_conditions: [humaneval_only, mbpp_only]
  success_threshold: 0.667
  min_valid_seeds: 1

fallback:
  fallback_eval_enabled: true
  evalplus_dataset: mbpp
  evalplus_backend: hf
  evalplus_greedy: true
  evalplus_batch_size: 16

figure:
  dpi: 300
  format: png
  heatmap_figsize: [10, 4]
  strip_figsize:   [12, 4]
  delta_figsize:   [8, 4]
  colormap: RdYlGn
```

---

## Subtasks

| ID | Subtask | Description |
|----|---------|-------------|
| C-M1-1 | Load H-E2 results | Read per-condition/seed eval JSONs from `h_e2_results_dir` |
| C-M1-2 | Inversion check | For each primary condition, check score ordering across benchmarks per seed; apply `success_threshold` |
| C-M1-3 | Fallback eval | If MBPP+ missing, run evalplus with FALLBACK config |
| C-M1-4 | Figures | Heatmap, strip, delta plots using FIGURE config |
| C-M1-5 | Write result | Dump conclusion + raw numbers to `result_file` |
