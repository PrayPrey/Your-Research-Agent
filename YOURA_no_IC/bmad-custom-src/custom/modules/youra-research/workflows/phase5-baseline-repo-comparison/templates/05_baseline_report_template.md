# Multi-Baseline Comparison Report (Mode B)

## Hypothesis: {{hypothesis_id}}
## Baselines: {{baseline_1}}, {{baseline_2}}, {{baseline_3}}
## Generated: {{timestamp}}
## Total Runs: {{total_runs}}
## Mode: B (Inject OUR algorithm into BASELINE's environment)

---

## Executive Summary

{{executive_summary}}

**Mode B Fair Comparison Note:** Each baseline uses THEIR OWN model, dataset, and config. The ONLY difference is the ALGORITHM (baseline_original vs ours_injected). This is "baseline's home turf" - winning here provides strong evidence that our algorithm is genuinely better.

**Key Findings:**
- **Baselines Won:** {{baselines_won}}/{{total_baselines}} (threshold: ≥{{baseline_win_threshold}})
- **Gate Result:** {{gate_result}}
- {{additional_observation}}

---

## 1. Experimental Setup

### 1.1 Mode B Fair Comparison Context (CRITICAL!)

> **IMPORTANT:** This comparison follows the Mode B Fair Comparison Principle.
> Each baseline uses THEIR OWN environment. We inject OUR algorithm and compare.

| Baseline | Model | Dataset | Config | Algorithm Comparison |
|----------|-------|---------|--------|---------------------|
| **{{baseline_1}}** | {{baseline_1_model}} (THEIRS) | {{baseline_1_dataset}} (THEIRS) | LR={{baseline_1_lr}} (THEIRS) | baseline_original vs ours_injected |
| **{{baseline_2}}** | {{baseline_2_model}} (THEIRS) | {{baseline_2_dataset}} (THEIRS) | LR={{baseline_2_lr}} (THEIRS) | baseline_original vs ours_injected |
| **{{baseline_3}}** | {{baseline_3_model}} (THEIRS) | {{baseline_3_dataset}} (THEIRS) | LR={{baseline_3_lr}} (THEIRS) | baseline_original vs ours_injected |

**The ONLY difference between runs is the ALGORITHM/METHODOLOGY.**
Each baseline's original model, dataset, and config were PRESERVED UNCHANGED.

### 1.2 Experiment Configuration

| Parameter | Value |
|-----------|-------|
| Mode | B (Inject our algorithm into baseline's environment) |
| Baselines | {{total_baselines}} |
| Methods per Baseline | {{methods_per_baseline}} (baseline_original, ours_injected) |
| Seeds per Run | {{seeds}} (baseline's default) |
| Total Runs | {{total_runs}} ({{total_baselines}} × {{methods_per_baseline}} × {{seeds}}) |
| Primary Metric | {{primary_metric}} |

### 1.3 Per-Baseline Environment Details

#### Baseline 1: {{baseline_1}}

| Component | Value |
|-----------|-------|
| Repository | {{baseline_1_url}} |
| Model | {{baseline_1_model}} |
| Dataset | {{baseline_1_dataset}} |
| Learning Rate | {{baseline_1_lr}} |
| Epochs | {{baseline_1_epochs}} |
| Seed | {{baseline_1_seed}} |

#### Baseline 2: {{baseline_2}}

| Component | Value |
|-----------|-------|
| Repository | {{baseline_2_url}} |
| Model | {{baseline_2_model}} |
| Dataset | {{baseline_2_dataset}} |
| Learning Rate | {{baseline_2_lr}} |
| Epochs | {{baseline_2_epochs}} |
| Seed | {{baseline_2_seed}} |

#### Baseline 3: {{baseline_3}}

| Component | Value |
|-----------|-------|
| Repository | {{baseline_3_url}} |
| Model | {{baseline_3_model}} |
| Dataset | {{baseline_3_dataset}} |
| Learning Rate | {{baseline_3_lr}} |
| Epochs | {{baseline_3_epochs}} |
| Seed | {{baseline_3_seed}} |

---

## 2. Results: Per-Baseline Comparison

### 2.1 Baseline 1: {{baseline_1}}

| Method | {{primary_metric}} | {{secondary_metric}} | Epochs |
|--------|-------------------|---------------------|--------|
| baseline_original | {{baseline_1_baseline_primary}} | {{baseline_1_baseline_secondary}} | {{baseline_1_epochs}} |
| ours_injected | {{baseline_1_ours_primary}} | {{baseline_1_ours_secondary}} | {{baseline_1_epochs}} |

**Winner:** {{baseline_1_winner}}
**Improvement:** {{baseline_1_improvement}}

### 2.2 Baseline 2: {{baseline_2}}

| Method | {{primary_metric}} | {{secondary_metric}} | Epochs |
|--------|-------------------|---------------------|--------|
| baseline_original | {{baseline_2_baseline_primary}} | {{baseline_2_baseline_secondary}} | {{baseline_2_epochs}} |
| ours_injected | {{baseline_2_ours_primary}} | {{baseline_2_ours_secondary}} | {{baseline_2_epochs}} |

**Winner:** {{baseline_2_winner}}
**Improvement:** {{baseline_2_improvement}}

### 2.3 Baseline 3: {{baseline_3}}

| Method | {{primary_metric}} | {{secondary_metric}} | Epochs |
|--------|-------------------|---------------------|--------|
| baseline_original | {{baseline_3_baseline_primary}} | {{baseline_3_baseline_secondary}} | {{baseline_3_epochs}} |
| ours_injected | {{baseline_3_ours_primary}} | {{baseline_3_ours_secondary}} | {{baseline_3_epochs}} |

**Winner:** {{baseline_3_winner}}
**Improvement:** {{baseline_3_improvement}}

---

## 3. Aggregate Results

### 3.1 Win Summary

| Baseline | Model | Dataset | Baseline Result | Ours Result | Winner | Improvement |
|----------|-------|---------|-----------------|-------------|--------|-------------|
| {{baseline_1}} | {{baseline_1_model}} | {{baseline_1_dataset}} | {{baseline_1_baseline_primary}} | {{baseline_1_ours_primary}} | {{baseline_1_winner}} | {{baseline_1_improvement}} |
| {{baseline_2}} | {{baseline_2_model}} | {{baseline_2_dataset}} | {{baseline_2_baseline_primary}} | {{baseline_2_ours_primary}} | {{baseline_2_winner}} | {{baseline_2_improvement}} |
| {{baseline_3}} | {{baseline_3_model}} | {{baseline_3_dataset}} | {{baseline_3_baseline_primary}} | {{baseline_3_ours_primary}} | {{baseline_3_winner}} | {{baseline_3_improvement}} |

**Total Baselines Won:** {{baselines_won}}/{{total_baselines}}

### 3.2 Gate Evaluation

| Criterion | Value | Threshold | Status |
|-----------|-------|-----------|--------|
| Baselines where Ours wins (ours > baseline on their turf) | {{baselines_won}}/{{total_baselines}} | ≥{{baseline_win_threshold}} | **{{gate_status}}** |

**Gate Result:** {{gate_result}} ({{gate_details}})

### 3.3 Mode B Interpretation

{{#if gate_passed}}
Our algorithm demonstrates superiority even when tested on baseline's own environments.
This provides **strong evidence** that our algorithm is genuinely better, not just tuned for our setup.
{{else}}
Our algorithm did not consistently outperform baselines on their home turf.
This suggests the advantage may be environment-specific rather than algorithmic.
{{/if}}

---

## 4. Hypothesis Journey Context

### 4.1 Version History

| Version | Changes | Result |
|---------|---------|--------|
{{version_history_table}}

### 4.2 Key Learnings

{{lessons_learned}}

### 4.3 Final Hypothesis Status

| Field | Value |
|-------|-------|
| Gate Type | DETERMINES_SUCCESS |
| Gate Result | {{gate_result}} |
| Baselines Won | {{baselines_won}}/{{total_baselines}} |
| Key Insight | {{key_insight}} |

---

## 5. Comparison Figures

### 5.1 Per-Baseline Comparison Chart

![Per-Baseline Comparison](figures/per_baseline_comparison.png)

*Bar chart comparing baseline_original vs ours_injected for each baseline's environment.*

### 5.2 Win/Lose Summary

![Win Summary](figures/win_summary.png)

*Visual summary of wins across all baselines.*

### 5.3 Additional Figures

{{additional_figures}}

---

## 6. Conclusion

{{conclusion}}

### Paper-Ready Summary

> {{paper_ready_summary}}

### Gate Decision Rationale

| Aspect | Detail |
|--------|--------|
| Mode | B (Inject our algorithm into baseline's environment) |
| Criteria | Win ≥{{baseline_win_threshold}} baselines (ours > baseline on their turf) |
| Baselines Won | {{baselines_won}}/{{total_baselines}} (threshold: ≥{{baseline_win_threshold}}) |
| **Final Decision** | **{{gate_result}}** |

---

## 7. Data Files

| File | Description | Location |
|------|-------------|----------|
| comparison_data.csv | Full experiment data ({{total_runs}} rows) | experiments/ |
| results_summary.md | Summary statistics | / |
| experiment.log | Experiment execution log | experiments/ |
| per_baseline_comparison.png | Per-baseline chart | figures/ |
| win_summary.png | Win/lose summary | figures/ |

---

## Appendix

### A. Baseline Repositories

| Baseline | URL | Stars | Original Commit | Branch |
|----------|-----|-------|-----------------|--------|
| {{baseline_1}} | {{baseline_1_url}} | {{baseline_1_stars}} | {{baseline_1_sha}} | youra-baseline |
| {{baseline_2}} | {{baseline_2_url}} | {{baseline_2_stars}} | {{baseline_2_sha}} | youra-baseline |
| {{baseline_3}} | {{baseline_3_url}} | {{baseline_3_stars}} | {{baseline_3_sha}} | youra-baseline |

### B. Baseline Environment Details

| Baseline | Model | Dataset | LR | Epochs | Seed |
|----------|-------|---------|-----|--------|------|
| {{baseline_1}} | {{baseline_1_model}} | {{baseline_1_dataset}} | {{baseline_1_lr}} | {{baseline_1_epochs}} | {{baseline_1_seed}} |
| {{baseline_2}} | {{baseline_2_model}} | {{baseline_2_dataset}} | {{baseline_2_lr}} | {{baseline_2_epochs}} | {{baseline_2_seed}} |
| {{baseline_3}} | {{baseline_3_model}} | {{baseline_3_dataset}} | {{baseline_3_lr}} | {{baseline_3_epochs}} | {{baseline_3_seed}} |

### C. Experiment Artifacts

```
{{baseline_folder}}/
├── comparison_plan.md
├── repo_candidates.md
├── evaluation_matrix.md
├── selected_baselines.md
├── injection_analysis.md
├── setup_log.md
├── code_analysis.md
├── results_summary.md
├── 05_baseline_checkpoint.yaml
├── 05_baseline_comparison.md <- This Report
├── baselines/
│ ├── {{baseline_1}}/
│ ├── {{baseline_2}}/
│ └── {{baseline_3}}/
├── adaptations/
│ ├── {{baseline_1}}/
│ │   ├── algorithm_injection.py
│ │   ├── metric_injection.py
│ │   ├── results_saver.py
│ │   └── training_script.py
│ ├── {{baseline_2}}/
│ └── {{baseline_3}}/
├── experiments/
│ ├── comparison_data.csv ({{total_runs}} rows)
│ ├── {{baseline_1}}/
│ │   ├── run_baseline_{seed}.log
│ │   └── run_ours_{seed}.log
│ ├── {{baseline_2}}/
│ │   ├── run_baseline_{seed}.log
│ │   └── run_ours_{seed}.log
│ └── {{baseline_3}}/
│ ├── run_baseline_{seed}.log
│ └── run_ours_{seed}.log
└── figures/
    ├── per_baseline_comparison.png
    └── win_summary.png
```

---
