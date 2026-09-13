# Product Requirements Document: H-M2
# Difficulty-Stratified Curriculum GRPO — Reward Entropy & Predictive Correlation

**Hypothesis ID:** H-M2
**Type:** MECHANISM (SHOULD_WORK)
**Gate:** SHOULD_WORK — Pearson r > 0.5, reward entropy direction correct
**Generated:** 2026-05-03
**Phase:** 3 — Implementation Planning
**Tier:** FULL (max 30 tasks)

---

## 1. Executive Summary

Implement a log-analysis experiment that verifies two mechanistic claims about how reward density mediates learning quality in GRPO training. **No new model training is required** — all data already exists from H-E1 full training runs. The experiment:
1. Computes reward entropy H(p) from checkpoint reward density logs (extending H-M1 infrastructure)
2. Computes pass@1 gain per 500-step interval from EvalPlus checkpoint evaluations
3. Runs Pearson correlation between reward density at step T and pass@1 gain from T to T+500 (36 pooled observations)
4. Generates required scatter plot and time-series visualizations

**Success criteria (SHOULD_WORK gate):**
- Pearson r > 0.5 AND p < 0.05 (one-tailed) for pooled 36 observations
- Mean reward entropy in curriculum condition (steps 0–2500) > mean reward entropy in uniform condition (steps 0–2500)

---

## 2. Problem Statement

H-M1 confirmed that reward density is measurably higher in the curriculum condition during early training (variance ratio 76×, p=5.34e-44). H-M2 asks whether this elevated reward density is accompanied by higher reward entropy (more informative gradient signal), and whether reward density at step T predicts subsequent pass@1 improvement from T to T+500. This closes the causal chain: curriculum ordering → higher reward density → more informative GRPO updates → faster pass@1 gains.

---

## 3. Functional Requirements

### FR-1: Data Loading Infrastructure

- **FR-1.1**: Load reward density CSV logs from H-E1: `h-e1/logs/reward_density_{condition}.csv` for all 4 conditions (curriculum, uniform, easy_only, hard_only)
- **FR-1.2**: Verify each CSV has ≥10 rows (one per 500-step checkpoint); assert on `step` and `reward_density` columns
- **FR-1.3**: Load pass@1 checkpoint CSV logs: `h-e1/logs/pass1_checkpoint_{condition}.csv` for all 4 conditions
- **FR-1.4**: Verify each pass@1 CSV has ≥10 rows with `step` and `pass1` columns
- **FR-1.5**: Fallback: if `pass1_checkpoint_{condition}.csv` not found, search for EvalPlus JSON outputs in `h-e1/results/eval_results_{condition}_step{step}.json` and build the CSV programmatically
- **FR-1.6**: Sort all loaded data by `step` column before analysis

### FR-2: Reward Entropy Computation

- **FR-2.1**: Implement `compute_entropy_from_density(density: float) -> float` using binary entropy formula:
  - H(p) = −p·log₂(p) − (1−p)·log₂(1−p)
  - where p = reward density (fraction of non-degenerate batches)
  - Edge cases: if p≤0 or p≥1, return 0.0
- **FR-2.2**: Apply to all 10 checkpoint rows per condition → produces entropy time series
- **FR-2.3**: Compute `mean_entropy_curriculum_early` = mean of entropy values for checkpoints at steps 500–2500 (5 values)
- **FR-2.4**: Compute `mean_entropy_uniform_early` = mean of entropy values for checkpoints at steps 500–2500 (5 values)
- **FR-2.5**: Compute entropy direction: `delta_entropy = mean_entropy_curriculum_early - mean_entropy_uniform_early`

### FR-3: Pass@1 Gain Computation

- **FR-3.1**: For each condition, compute pass@1 gain per 500-step interval: `gain[i] = pass1[i+1] - pass1[i]` for i in 0..8 (9 values from 10 checkpoints)
- **FR-3.2**: Pool across all 4 conditions: `all_densities` = reward_density values at steps 500–4500 (first 9 rows per condition), `all_gains` = corresponding pass@1 gains
- **FR-3.3**: Result: 36 pooled (density, gain) observation pairs (9 × 4 conditions)
- **FR-3.4**: Validate: `len(all_densities) == 36` and `len(all_gains) == 36`

### FR-4: Pearson Correlation Analysis

- **FR-4.1**: Compute `scipy.stats.pearsonr(all_densities, all_gains)` → `(r, p_value)`
- **FR-4.2**: Store: `pearson_r`, `p_value_twotailed`, `p_value_onetailed = p_value_twotailed / 2`
- **FR-4.3**: Gate check: `gate_passed = (pearson_r > 0.5) and (p_value_onetailed < 0.05)`
- **FR-4.4**: Compute per-condition correlations separately (4 individual r values) for supplementary analysis
- **FR-4.5**: Compute 95% CI for Pearson r using Fisher z-transformation

### FR-5: Statistical Tests (Secondary)

- **FR-5.1**: One-tailed Wilcoxon signed-rank test: curriculum entropy vs uniform entropy (steps 0–2500, 5 paired values)
- **FR-5.2**: Report: Wilcoxon statistic, p-value, effect direction

### FR-6: Results Output

- **FR-6.1**: Save results to `h-m2/results/results_summary.json` with full metrics:
  ```json
  {
    "pearson_r": float,
    "p_value_onetailed": float,
    "n_observations": 36,
    "gate_passed": bool,
    "mean_entropy_curriculum_early": float,
    "mean_entropy_uniform_early": float,
    "delta_entropy": float,
    "per_condition_r": {"curriculum": float, "uniform": float, "easy_only": float, "hard_only": float}
  }
  ```
- **FR-6.2**: Print gate result to stdout: `"GATE: PASSED/FAILED — Pearson r={r:.4f}, p={p:.4f}"`
- **FR-6.3**: Save entropy time-series to `h-m2/results/entropy_timeseries.csv`
- **FR-6.4**: Save pooled correlation data to `h-m2/results/correlation_data.csv`

### FR-7: Visualization (Mandatory)

- **FR-7.1**: **Scatter plot** (gate metric figure): reward density at step T vs pass@1 gain T→T+500, color-coded by condition, with regression line and Pearson r annotation. Save to `h-m2/figures/scatter_density_vs_gain.png`
- **FR-7.2**: **Reward entropy time-series**: line plot for all 4 conditions over steps 0–5000 with vertical line at step 2500. Save to `h-m2/figures/entropy_timeseries.png`
- **FR-7.3**: **Entropy vs density comparison**: side-by-side bar chart (early phase 0–2500) for all 4 conditions. Save to `h-m2/figures/entropy_density_comparison.png`
- **FR-7.4**: **Per-condition scatter plots**: 2×2 subplot grid, one per condition, with regression line. Save to `h-m2/figures/per_condition_scatter.png`
- **FR-7.5**: **Pass@1 gain time-series**: line plot of pass@1 gain per interval for all 4 conditions. Save to `h-m2/figures/pass1_gain_timeseries.png`
- **FR-7.6**: All figures use consistent color scheme: curriculum=blue, uniform=orange, easy_only=green, hard_only=red

### FR-8: Checkpoint Recovery / Fallback

- **FR-8.1**: If `pass1_checkpoint_{condition}.csv` missing, scan for saved checkpoint directories in `h-e1/checkpoints/{condition}/` and report which are available
- **FR-8.2**: If fewer than 10 checkpoints available per condition, proceed with available data and log warning: `"WARNING: Only {n} checkpoints available for {condition}"`
- **FR-8.3**: Minimum viable: ≥5 checkpoints per condition to compute meaningful correlation

---

## 4. Data Specification

### 4.1 Input Data (Existing — No Download Required)

| Dataset | Path | Format | Rows |
|---------|------|--------|------|
| Reward density logs (curriculum) | `h-e1/logs/reward_density_curriculum.csv` | CSV: step, reward_density | 10 |
| Reward density logs (uniform) | `h-e1/logs/reward_density_uniform.csv` | CSV: step, reward_density | 10 |
| Reward density logs (easy_only) | `h-e1/logs/reward_density_easy_only.csv` | CSV: step, reward_density | 10 |
| Reward density logs (hard_only) | `h-e1/logs/reward_density_hard_only.csv` | CSV: step, reward_density | 10 |
| Pass@1 checkpoints (curriculum) | `h-e1/logs/pass1_checkpoint_curriculum.csv` | CSV: step, pass1 | 10 |
| Pass@1 checkpoints (uniform) | `h-e1/logs/pass1_checkpoint_uniform.csv` | CSV: step, pass1 | 10 |
| Pass@1 checkpoints (easy_only) | `h-e1/logs/pass1_checkpoint_easy_only.csv` | CSV: step, pass1 | 10 |
| Pass@1 checkpoints (hard_only) | `h-e1/logs/pass1_checkpoint_hard_only.csv` | CSV: step, pass1 | 10 |

**Total input: 8 CSV files, 10 rows each = 80 data points**

**Fallback path:** EvalPlus JSON results at `h-e1/results/eval_results_{condition}_step{step}.json`

### 4.2 Evaluation Protocol

| Metric | Method | n |
|--------|--------|---|
| Pearson r (primary gate) | scipy.stats.pearsonr, pooled 36 obs | 36 |
| Entropy comparison (secondary) | Binary entropy + Wilcoxon signed-rank | 5 pairs |
| Per-condition correlation | scipy.stats.pearsonr per condition | 9 obs each |

### 4.3 Conditions

| Condition | Steps 0–2500 | Steps 2501–5000 | Role |
|-----------|-------------|-----------------|------|
| curriculum | Easy pool | Hard pool | Proposed |
| uniform | Full pool random | Full pool random | Baseline |
| easy_only | Easy pool | Easy pool | Ablation |
| hard_only | Hard pool | Hard pool | Ablation |

---

## 5. Non-Functional Requirements

- **NFR-1**: Log-analysis only — no GPU required; runs on CPU in < 5 minutes
- **NFR-2**: All input data already exists from H-E1 full 5000-step training
- **NFR-3**: Reproducible: all operations are deterministic (no random seeds needed for analysis)
- **NFR-4**: Output figures saved at 200 DPI minimum for paper quality
- **NFR-5**: Infrastructure tier: FULL (analysis pipeline with structured output and multiple visualizations)

---

## 6. Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Data loaded | All 8 CSV files readable with ≥10 rows | Assertion check |
| Entropy direction | delta_entropy > 0 (curriculum > uniform, early phase) | numpy comparison |
| Gate (SHOULD_WORK primary) | Pearson r > 0.5 AND p_onetailed < 0.05 | scipy.stats.pearsonr |
| Gate (secondary) | Wilcoxon p < 0.05 for entropy comparison | scipy.stats.wilcoxon |
| Figures generated | 5 figures saved to h-m2/figures/ | File existence check |
| Results saved | results_summary.json with all required fields | JSON validation |

---

## 7. Dependencies

### 7.1 Python Packages

```
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

**Note:** All packages already confirmed working from H-E1/H-M1 environment. No new packages required.

### 7.2 Input Dependencies (from H-E1)

| Dependency | Source | Status |
|-----------|--------|--------|
| Reward density CSVs | H-E1 RewardDensityCallback | Confirmed by H-M1 PASSED gate |
| Pass@1 checkpoint CSVs | H-E1 EvalPlus evaluations | Required — verify existence in Phase 4 |
| Full 5000-step training | H-E1 training runs | Confirmed by H-M1 PASSED gate |

### 7.3 External Repositories (Reference Only)

| Repo | Purpose |
|------|---------|
| scipy/scipy | Pearson correlation, Wilcoxon test |
| numpy/numpy | Array operations, binary entropy |
| matplotlib/matplotlib | Visualization |

---

## 8. Ablation Analysis

| Analysis | Description | Output |
|----------|-------------|--------|
| A1: Pooled correlation | Primary gate: 36 obs across all conditions | pearson_r, p_value |
| A2: Per-condition correlation | Within-condition predictiveness | 4 individual r values |
| A3: Entropy direction (early) | Curriculum > uniform entropy, steps 0–2500 | delta_entropy, Wilcoxon |
| A4: Entropy full time-series | All conditions over 5000 steps | entropy_timeseries.csv |
| A5: Between vs within effect | Compare pooled r to within-condition r | Interpretation |

---

## 9. File Structure

```
h-m2/
├── code/
│   ├── analysis/
│   │   ├── compute_entropy.py          # FR-2: Binary entropy from density
│   │   ├── compute_gains.py            # FR-3: Pass@1 gain computation
│   │   ├── pearson_correlation.py      # FR-4: Pearson r analysis
│   │   └── load_data.py                # FR-1: CSV data loading with fallback
│   ├── visualization/
│   │   └── generate_figures.py         # FR-7: All 5 figures
│   └── run_analysis.py                 # Main entry point
├── figures/
│   ├── scatter_density_vs_gain.png     # FR-7.1 (gate metric)
│   ├── entropy_timeseries.png          # FR-7.2
│   ├── entropy_density_comparison.png  # FR-7.3
│   ├── per_condition_scatter.png       # FR-7.4
│   └── pass1_gain_timeseries.png       # FR-7.5
├── results/
│   ├── results_summary.json            # FR-6.1
│   ├── entropy_timeseries.csv          # FR-6.3
│   └── correlation_data.csv            # FR-6.4
├── 02c_experiment_brief.md
├── 03_prd.md
├── 03_architecture.md
├── 03_logic.md
├── 03_config.md
└── 03_tasks.yaml
```

---

## 10. Traceability

| Requirement | Source |
|-------------|--------|
| FR-1 (data loading) | H-M1 experiment brief §Dataset; H-E1 validation report |
| FR-2 (entropy) | 02c_experiment_brief.md §Reward Entropy Mechanism; Phase 2B §2.2 |
| FR-3 (pass@1 gains) | 02c_experiment_brief.md §Pearson Correlation Design |
| FR-4 (Pearson r) | 02b_verification_plan.md H-M2 gate condition |
| FR-5 (Wilcoxon) | 02c_experiment_brief.md §Statistical Tests |
| FR-6 (results) | Pipeline convention from H-M1 |
| FR-7 (figures) | 02c_experiment_brief.md §Visualization Requirements |
| Success threshold r>0.5 | 02b_verification_plan.md SHOULD_WORK gate |
| 36 pooled observations | 02c_experiment_brief.md §Pearson Correlation Design |
