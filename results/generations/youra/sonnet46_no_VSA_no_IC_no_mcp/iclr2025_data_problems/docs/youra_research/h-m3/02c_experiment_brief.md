# Experiment Design: H-M3

**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr
**Hypothesis Statement:** Under the setting of Pythia dedup-Pile vs Pile benchmark accuracy differentials at token-count-matched checkpoints, if benchmarks vary in their estimated n-gram contamination overlap with the Pile corpus, then the per-benchmark accuracy differential (dedup-Pile minus Pile) will show positive correlation with contamination overlap estimate (Pearson r ≥ 0.5), because higher contamination means greater near-memorization advantage for Pile models and thus greater accuracy drop in dedup-Pile when that advantage is removed.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** — Requires correlation analysis, not just direction check. Statistical tests included.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 (PASS), H-M1 (PASS), H-M2 (FAILED/SHOULD_WORK — limitation noted, continue)
**Gate Status:** SHOULD_WORK (failure → EXPLORE, not STOP)

> ⚠️ **H-M2 Limitation:** Min-k% memorization signal not confirmed at Bonferroni-corrected threshold. H-M3 proceeds using H-M1 contamination estimates (13-gram overlap) as the primary contamination predictor. H-M2 min-k% differential used as secondary estimator only if partially significant.

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Gate:** SHOULD_WORK
- **Prerequisites:** H-E1 (PASS), H-M1 (PASS), H-M2 (FAILED/SHOULD_WORK)

### Gate Condition

SHOULD_WORK — if Pearson r < 0.3: EXPLORE (try additional benchmarks, check whether data-volume effect dominates contamination-correction signal). Failure does not block H-M4.

---

## Continuation Context

H-M3 inherits outputs from three completed hypotheses:

| Source | Output Reused |
|--------|---------------|
| H-E1 (PASS) | Per-benchmark accuracy differentials (dedup-Pile minus Pile) at token-count-matched checkpoints for all 4 model sizes |
| H-M1 (PASS) | Per-benchmark 13-gram overlap estimates for removed vs retained documents |
| H-M2 (FAILED) | Min-k% differential scores — partially significant results used as secondary estimator |

### Previous Hypothesis Results (if applicable)

- **H-E1:** ≥1 benchmark Bonferroni-significant at ≥2 model sizes. Accuracy differential vector confirmed.
- **H-M1:** Removed documents show significantly higher 13-gram overlap vs retained on ≥2 benchmarks (p<0.05). Contamination estimate vector confirmed.
- **H-M2 (FAILED):** Min-k% probability scores did not reach Bonferroni-corrected threshold (p<0.0125). Partial signal (n_significant=2/4 benchmarks before correction) noted as secondary evidence only.

**Implication for H-M3:** The contamination estimate vector from H-M1 (13-gram overlap per benchmark) is the primary independent variable. Min-k% differential from H-M2 used as robustness check only.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

> ⚠️ **MCP UNAVAILABLE (NO_MCP session):** Archon MCP server not connected. Synthesized from Phase 2B protocol + established literature (Lee et al. 2022, Shi et al. 2023, Biderman et al. 2023, GPT-4 Technical Report).

**Literature-derived insights (substituting Archon search):**

**Finding 1: N-gram contamination methodology (Lee et al. 2022 / GPT-4 TR)**
- Standard n-gram overlap: 13-gram overlap rate between training corpus and benchmark test sets
- Tools: google-research/deduplicate-text-datasets suffix array tool
- Typical contamination rates: MMLU ~3-8%, HellaSwag ~15-25%, ARC ~5-12%, WinoGrande ~1-4%
- Key insight: contamination rates vary substantially across benchmarks; this variance is the signal H-M3 exploits

**Finding 2: Correlation analysis for benchmark contamination (Shi et al. 2023)**
- Min-k% probability as per-item memorization proxy
- Pearson/Spearman on 4-point vectors (4 benchmarks) requires large effect sizes (r≥0.5) to be meaningful
- Small n (4 benchmarks) means significance depends on effect magnitude, not sample size
- Key insight: with n=4, p<0.05 requires r≥0.95 (two-tailed Pearson t-test); must aggregate across model sizes to increase effective n

**Finding 3: Aggregation strategy (Biderman et al. 2023)**
- Pythia releases 4 model sizes × 2 corpus variants = 8 model configurations
- Aggregating differential across model sizes gives 4 (benchmarks) × 4 (model sizes) = 16 observations
- Pearson on 16 observations: p<0.05 at r≥0.50 (achievable)
- Key insight: model-size expansion is the correct strategy to achieve statistical power for the correlation test

### Archon Code Examples

> ⚠️ **MCP UNAVAILABLE:** No Archon code examples retrieved. Implementation derived from Shi et al. 2023 reference implementation and standard scipy/numpy patterns.

**Literature-derived code patterns:**

```python
# Standard Pearson/Spearman correlation for contamination-accuracy analysis
from scipy import stats
import numpy as np

# Pattern: aggregate across model sizes for statistical power
# contamination_estimates: shape (n_benchmarks,) from H-M1
# accuracy_differentials: shape (n_model_sizes, n_benchmarks) from H-E1

def compute_contamination_correlation(contamination_vec, acc_diff_matrix):
    """
    contamination_vec: (4,) — 13-gram overlap per benchmark
    acc_diff_matrix: (4, 4) — dedup-Pile minus Pile per (model_size, benchmark)
    Returns: Pearson r, Spearman rho, p-values
    """
    # Flatten: each model size contributes one (contamination, differential) pair per benchmark
    cont_repeated = np.tile(contamination_vec, acc_diff_matrix.shape[0])  # (16,)
    diff_flat = acc_diff_matrix.flatten()  # (16,)
    
    pearson_r, pearson_p = stats.pearsonr(cont_repeated, diff_flat)
    spearman_rho, spearman_p = stats.spearmanr(cont_repeated, diff_flat)
    return pearson_r, pearson_p, spearman_rho, spearman_p
```

### Exa GitHub Implementations

> ⚠️ **MCP UNAVAILABLE (NO_MCP session):** Exa MCP server not connected. Literature-derived reference implementations listed.

**[LIMITED_RESULTS - NO_MCP]** Known relevant repositories:

**Repository 1:** EleutherAI/lm-evaluation-harness
- URL: https://github.com/EleutherAI/lm-evaluation-harness
- Relevance: Standard benchmark evaluation for Pythia models; produces accuracy results that are H-M3's dependent variable
- Architecture: Python CLI + task registry, supports MMLU/HellaSwag/ARC/WinoGrande out of box
- Key insight: Use `--tasks mmlu,hellaswag,arc_challenge,winogrande --num_fewshot 0` for zero-shot; results directly comparable to Biderman et al. 2023

**Repository 2:** google-research/deduplicate-text-datasets
- URL: https://github.com/google-research/deduplicate-text-datasets
- Relevance: Suffix array tool for 13-gram overlap estimation; used in H-M1 to produce contamination estimates reused here
- Key code: `python scripts/find_similar.py --queries benchmark_test.txt --db pile_train.txt --ngram 13`

**Repository 3:** swj0419/detect-pretrain-code (Shi et al. 2023)
- URL: https://github.com/swj0419/detect-pretrain-code
- Relevance: Min-k% implementation for H-M2 outputs reused as secondary predictor in H-M3
- Key code: `mink_plus.py` — compute per-token min-k% probability scores

### 🎯 Implementation Priority Assessment

H-M3 is a **correlation analysis** — it aggregates outputs from H-E1 and H-M1 rather than running new model evaluations.

**Recommended Implementation Path:**
- Primary: Load H-E1 accuracy differentials + H-M1 contamination estimates from previous results files; compute scipy.stats.pearsonr/spearmanr
- Fallback: Re-run lm-evaluation-harness on Pythia checkpoints (already done in H-E1; reuse cached results)
- Justification: H-M3 requires no new model training or fine-tuning; it is a downstream analysis of previously computed vectors

### Code Analysis (Serena MCP)

*Skipped* — H-M3 uses no novel model architecture; no complex codebase to analyze. Correlation analysis uses standard scipy functions.

---

## Experiment Specification

### Dataset

**Primary: Benchmark Accuracy Differentials (from H-E1)**
- **Type:** programmatic-api (computed from existing Pythia checkpoint evaluations)
- **Source:** lm-evaluation-harness outputs from H-E1 experiment
- **Content:** Per-benchmark few-shot accuracy for Pythia-160M/410M/1B/6.9B × Pile/dedup-Pile at token-count-matched checkpoints
- **Benchmarks:** MMLU (full test, ~14,000 items), HellaSwag (full test, ~10,000 items), ARC-Challenge (full test, ~1,172 items), WinoGrande (full test, ~1,267 items)
- **Split used:** Full standard test sets (no subsampling)
- **Processing:** Accuracy differentials = dedup-Pile accuracy minus Pile accuracy per (benchmark, model_size)

**Secondary: Contamination Estimates (from H-M1)**
- **Type:** programmatic-api (computed 13-gram overlap scores from H-M1)
- **Source:** H-M1 experiment outputs (Mann-Whitney significant results)
- **Content:** Per-benchmark mean 13-gram overlap rate for removed documents vs benchmark test sets
- **Vector dimension:** 4 (one value per benchmark)

**Tertiary: Min-k% Differentials (from H-M2, secondary only)**
- **Type:** programmatic-api (computed min-k% scores from H-M2)
- **Status:** PARTIAL — available but not Bonferroni-significant; used as robustness check only

**Synthetic data policy check:** PASS — all data is real (standard benchmark test sets; Pythia model evaluations; n-gram overlap from real corpus comparison).

**Loading Information** (for Phase 4 download):
- Method: File-based (load from H-E1/H-M1 output directories)
- Identifier: `docs/youra_research/h-e1/results/accuracy_differentials.json`, `docs/youra_research/h-m1/results/contamination_estimates.json`
- Code:
```python
import json
with open("../h-e1/results/accuracy_differentials.json") as f:
    acc_diff = json.load(f)  # {model_size: {benchmark: float}}
with open("../h-m1/results/contamination_estimates.json") as f:
    cont_est = json.load(f)  # {benchmark: float}
```

### Models

#### Baseline Model

No model training required. H-M3 is a correlation analysis over pre-computed vectors.

**Pythia checkpoint evaluations (from H-E1, inherited):**
- Architecture: GPT-NeoX (decoder-only)
- Sizes: 160M, 410M, 1B, 6.9B
- Variants: Pile (pythia-{size}) and dedup-Pile (pythia-{size}-deduped)
- Source: EleutherAI/pythia-* on HuggingFace
- Checkpoint matching: token-count-matched (154 checkpoints per model; match by closest token count)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace (pre-evaluated; load results files)
- Identifier: `EleutherAI/pythia-{size}`, `EleutherAI/pythia-{size}-deduped`
- Code: `from transformers import AutoModelForCausalLM; model = AutoModelForCausalLM.from_pretrained("EleutherAI/pythia-1b-deduped")`

#### Proposed Model

Not applicable — H-M3 is an analysis experiment, not a model training experiment. The "proposed mechanism" is the contamination-correlation hypothesis itself.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Contamination-Performance Correlation Analysis
# Based on: Shi et al. 2023, Biderman et al. 2023, standard scipy stats
# H-M3 tests whether per-benchmark contamination predicts accuracy differential

import numpy as np
from scipy import stats

BENCHMARKS = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]
MODEL_SIZES = ["160m", "410m", "1b", "6.9b"]

def build_analysis_vectors(acc_diff_dict, cont_est_dict):
    """
    acc_diff_dict: {model_size: {benchmark: float}} — dedup minus pile
    cont_est_dict: {benchmark: float} — 13-gram overlap rate
    Returns: (cont_repeated, diff_flat) for correlation
    """
    cont_vec = np.array([cont_est_dict[b] for b in BENCHMARKS])
    diff_matrix = np.array([
        [acc_diff_dict[m][b] for b in BENCHMARKS]
        for m in MODEL_SIZES
    ])  # shape: (4 sizes, 4 benchmarks)
    cont_repeated = np.tile(cont_vec, len(MODEL_SIZES))  # (16,)
    diff_flat = diff_matrix.flatten()                    # (16,)
    return cont_repeated, diff_flat

def run_correlation_analysis(cont_vec, diff_vec):
    pearson_r, pearson_p = stats.pearsonr(cont_vec, diff_vec)
    spearman_rho, spearman_p = stats.spearmanr(cont_vec, diff_vec)
    return {
        "pearson_r": pearson_r, "pearson_p": pearson_p,
        "spearman_rho": spearman_rho, "spearman_p": spearman_p,
    }

# Per-benchmark summary (aggregate over model sizes)
def per_benchmark_summary(acc_diff_dict, cont_est_dict):
    rows = []
    for b in BENCHMARKS:
        diffs = [acc_diff_dict[m][b] for m in MODEL_SIZES]
        rows.append({
            "benchmark": b,
            "contamination": cont_est_dict[b],
            "mean_diff": np.mean(diffs),
            "std_diff": np.std(diffs),
        })
    return rows
```

### Training Protocol

H-M3 requires no model training. Protocol covers the analysis pipeline.

**Analysis Protocol:**

| Step | Operation | Tool |
|------|-----------|------|
| 1 | Load H-E1 accuracy differentials | json / pandas |
| 2 | Load H-M1 13-gram contamination estimates | json / numpy |
| 3 | Load H-M2 min-k% differentials (secondary) | json / numpy |
| 4 | Build 16-observation (contamination, differential) pairs | numpy |
| 5 | Pearson + Spearman correlation (primary) | scipy.stats |
| 6 | Bootstrap 95% CI on Pearson r (1000 resamples) | numpy random |
| 7 | Repeat with min-k% as contamination predictor (robustness) | scipy.stats |
| 8 | Directional check: high-contamination benchmarks → negative diff | pandas |
| 9 | Scatter plot: contamination vs accuracy differential per benchmark | matplotlib |
| 10 | Report with CI and both estimators | markdown / JSON |

**Optimizer:** N/A (no gradient descent)
**Batch size:** N/A
**Epochs:** N/A
**Loss:** N/A
**Seeds:** 1 (analysis is deterministic; bootstrap uses fixed seed=42)
**Compute:** CPU-only; analysis completes in <60 seconds

**Software dependencies:**
```
numpy>=1.24
scipy>=1.10
pandas>=2.0
matplotlib>=3.7
transformers>=4.35  # only if re-running H-E1 evaluations
lm-evaluation-harness  # only if re-running H-E1 evaluations
```

### Evaluation

**Primary Metrics:**

| Metric | Definition | Success Threshold |
|--------|-----------|-------------------|
| Pearson r | Correlation between 13-gram contamination and accuracy differential, n=16 | r ≥ 0.5, p < 0.05 |
| Spearman ρ | Rank correlation (same vectors) | ρ ≥ 0.5, p < 0.05 |
| Directionality | High-contamination benchmarks show negative (or smaller positive) differential | ≥3 of 4 benchmarks follow predicted direction |

**Secondary Metrics (robustness):**

| Metric | Definition | Purpose |
|--------|-----------|---------|
| Pearson r (min-k%) | Correlation using H-M2 min-k% as contamination predictor | Robustness check — do both estimators agree? |
| 95% bootstrap CI on r | 1000 bootstrap resamples of 16 observations | Uncertainty quantification |
| Per-model-size breakdown | Correlation computed separately for each model size (n=4) | Scale-interaction check |

**Success Criteria:**
- Primary: Pearson r ≥ 0.5 AND p < 0.05 (with 13-gram contamination estimate)
- Supporting: Spearman ρ ≥ 0.5 AND p < 0.05
- Directional: ≥3/4 benchmarks show contamination-predicted sign for accuracy differential

**Failure threshold:** r < 0.3 → EXPLORE (data-volume effect may dominate; run with additional benchmarks)

**Expected Baseline Performance (from H-E1/H-M1 prior results):**
- H-E1 showed significant accuracy differentials exist (≥1 benchmark)
- H-M1 confirmed contamination estimates are non-uniform across benchmarks
- Prior work (Lee et al. 2022) reports aggregate improvement; H-M3 tests fine-grained per-benchmark prediction

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: correlation analysis
- Library: `scipy.stats` (pearsonr, spearmanr)
- Code: `from scipy.stats import pearsonr, spearmanr`

### Ablation Studies

**Ablation 1: Contamination Estimator Comparison**
- Compare 13-gram overlap (H-M1) vs min-k% differential (H-M2) as contamination predictor
- What it measures: Which estimator better predicts accuracy differential? Are they consistent?
- Expected: Both show similar r; disagreement flags estimator sensitivity

**Ablation 2: Aggregation Strategy**
- Option A: Flatten all (model_size, benchmark) pairs → n=16
- Option B: Average across model sizes first → n=4 per benchmark
- What it measures: Sensitivity to aggregation choice
- Note: With n=4, Pearson significance requires r≥0.95; n=16 is the valid choice

**Ablation 3: Token-count vs Step-count Matching**
- Compare contamination-accuracy correlation under token-count matching (primary) vs step matching
- What it measures: Whether token-count matching changes the correlation (validates H-M4 design)
- Implementation: Run same analysis on step-matched differentials from H-E1 results

**Ablation 4: Per-model-size correlation**
- Run Pearson on each model size separately (n=4)
- What it measures: Consistency of contamination-accuracy relationship across scale
- Expected: Smaller models may show weaker signal; 6.9B should show strongest

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Scatter plot of contamination estimate (x-axis) vs accuracy differential (y-axis) per benchmark, with regression line, r value, and p-value annotated

#### Additional Figures (LLM Autonomous)

1. **Correlation heatmap**: Pearson r values by model size × contamination estimator (2×4 grid)
2. **Per-benchmark accuracy differential bar chart**: 4 benchmarks × 4 model sizes, colored by contamination level
3. **Bootstrap CI plot**: Distribution of Pearson r under bootstrap resampling
4. **Contamination rank vs differential rank**: Spearman rank visualization for 4 benchmarks

All figures saved to `docs/youra_research/h-m3/figures/`

---

## 🔬 Mechanism Verification Protocol

**Pre-conditions (must verify before running):**
- `mechanism_exists`: H-E1 accuracy differential file exists and contains all 8 model variants × 4 benchmarks
- `mechanism_isolatable`: H-M1 contamination estimates exist with per-benchmark values (not just aggregate)
- `baseline_measurable`: scipy.stats.pearsonr callable on 16-observation vectors

**Architecture Compatibility:**
- `architecture_compatibility`: No model architecture involved — pure statistical analysis; no compatibility concerns

**Activation Indicators:**
- `mechanism_log_message`: "Contamination-accuracy correlation computed: Pearson r={r:.3f}, p={p:.4f}"
- `tensor_shape_change`: cont_repeated.shape == (16,), diff_flat.shape == (16,)
- `metric_delta_expected`: Pearson r ≥ 0.5 if contamination-correction hypothesis holds

**Mechanism Verification Code:**
```python
def verify_mechanism(results):
    r = results["pearson_r"]
    p = results["pearson_p"]
    rho = results["spearman_rho"]
    assert len(results["cont_vec"]) == 16, "Expected 16 observations (4 benchmarks × 4 model sizes)"
    mechanism_active = (r >= 0.5) and (p < 0.05)
    partial_support = (0.3 <= r < 0.5) and (p < 0.05)
    print(f"Pearson r={r:.3f} (p={p:.4f}), Spearman ρ={rho:.3f}")
    print(f"Mechanism CONFIRMED: {mechanism_active}")
    print(f"Partial support: {partial_support}")
    return mechanism_active
```

**Failure Detection:**
- If `p > 0.05`: correlation not significant — explore data-volume confound
- If `r < 0`: negative correlation — contamination is anti-predictive; investigate data artifacts
- If input vectors contain NaN: missing H-E1/H-M1 result; abort and re-run upstream hypotheses

**Success Criteria:**
- `hypothesis_support_threshold`: Pearson r ≥ 0.5
- `hypothesis_support_metric`: pearson_r (primary), spearman_rho (secondary)

---

## PoC Success Check (MECHANISM)

**Pass Condition for MECHANISM gate (SHOULD_WORK):**
1. Analysis runs without error
2. Pearson r ≥ 0.5 and p < 0.05 (with 13-gram contamination estimates)
3. Spearman ρ ≥ 0.5 and p < 0.05

**Failure → EXPLORE (not STOP):** r < 0.3 triggers additional benchmark extension and volume-confound investigation.

---

## Appendix: Reference Implementations

### A. Literature Sources (substituting Archon KB — MCP unavailable)

**Source A.1:** Shi et al. 2023 — "Detecting Pretraining Data from Large Language Models"
- arXiv: 2310.16789
- Key insight: Min-k% probability as memorization proxy; per-benchmark analysis methodology
- Used for: H-M2 design (inherited by H-M3 as secondary estimator)
- Code: github.com/swj0419/detect-pretrain-code

**Source A.2:** Lee et al. 2022 — "Deduplicating Training Data Makes Language Models Better"
- arXiv: 2107.06499
- Key insight: 13-gram overlap methodology for contamination estimation; aggregate dedup effects
- Used for: Contamination estimator methodology (H-M1, reused in H-M3)
- Code: github.com/google-research/deduplicate-text-datasets

**Source A.3:** Biderman et al. 2023 — "Pythia: A Suite for Analyzing Large Language Models Across Training and Scaling"
- arXiv: 2304.01373
- Key insight: Pile vs dedup-Pile controlled comparison; 154 checkpoint granularity; tabulated benchmark results
- Used for: Model selection, checkpoint matching, accuracy differential source
- Code: github.com/EleutherAI/pythia

**Source A.4:** GPT-4 Technical Report — OpenAI 2023
- Key insight: 13-gram contamination estimation methodology at scale; per-benchmark contamination reporting
- Used for: Contamination estimation design (H-M1 methodology)

### B. GitHub Implementations (Exa — MCP unavailable; known repos)

**[LIMITED_RESULTS - NO_MCP]**

**Repository B.1:** EleutherAI/lm-evaluation-harness
- URL: https://github.com/EleutherAI/lm-evaluation-harness
- Relevance: Produces accuracy differentials (H-M3 DV); standard evaluation harness for Pythia
- Used for: H-E1 evaluation pipeline (inherited)

**Repository B.2:** google-research/deduplicate-text-datasets
- URL: https://github.com/google-research/deduplicate-text-datasets
- Relevance: 13-gram overlap contamination estimation (H-M1 methodology)
- Used for: Contamination estimate vector (H-M3 IV)

**Repository B.3:** swj0419/detect-pretrain-code (Shi et al. 2023)
- URL: https://github.com/swj0419/detect-pretrain-code
- Relevance: Min-k% implementation for H-M2 outputs (H-M3 secondary estimator)

### C. Code Analysis (Serena MCP)

*Skipped* — No novel architecture. H-M3 uses standard scipy correlation functions; no complex codebase to analyze semantically.

### D. Previous Hypothesis Context

**Source:** H-E1 and H-M1 validation reports

| Component | Source | Status |
|-----------|--------|--------|
| Accuracy differentials | H-E1 04_validation.md | PASS — available |
| 13-gram contamination estimates | H-M1 04_validation.md | PASS — available |
| Min-k% differentials | H-M2 04_validation.md | PARTIAL — significant pre-correction |
| Token-count matching protocol | H-E1 design | Inherited |

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|---------------|-------------|------------------|
| Independent variable (contamination) | Literature + H-M1 results | A.2, A.4, H-M1 |
| Dependent variable (accuracy differential) | Literature + H-E1 results | A.3, H-E1 |
| Correlation analysis method | Literature | A.1, A.2 |
| Aggregation strategy (n=16) | Derived from A.3 | A.3 (4 model sizes) |
| Success threshold (r≥0.5) | Phase 2B verification protocol | 02b_verification_plan.md §2.2 H-M3 |
| Bootstrap CI | Standard practice | scipy.stats docs |
| Ablation: token vs step matching | Phase 2B rationale | 02b_verification_plan.md §2.2 H-M4 rationale |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — no file write)
**Date:** 2026-08-25

### Workflow History for This Hypothesis

| Event | Timestamp | Phase |
|-------|-----------|-------|
| Experiment design started | 2026-08-25T17:30:00+00:00 | Phase 2C |
| MCP unavailable — NO_MCP session | 2026-08-25T17:30:00+00:00 | Phase 2C Step 2 |
| Literature-based synthesis used | 2026-08-25T17:30:00+00:00 | Phase 2C Steps 2-3 |
| Experiment design completed | 2026-08-25T17:45:00+00:00 | Phase 2C Step 8 |

---

*MCP Tools Used: NONE (NO_MCP session — Archon and Exa unavailable; literature-based synthesis applied)*
*All specifications grounded in Phase 2B protocol + established literature (Lee et al. 2022, Shi et al. 2023, Biderman et al. 2023)*
*Next Phase: Phase 3 - Implementation Planning*
