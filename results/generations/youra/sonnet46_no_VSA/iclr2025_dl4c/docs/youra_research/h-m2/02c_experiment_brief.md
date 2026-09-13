# Experiment Design: H-M2

**Date:** 2026-08-02
**Author:** Anonymous
**Hypothesis Statement:** Spearman rank correlation between code-embedding mean pairwise cosine similarity (training source → test benchmark) and pass@1 rank order across source conditions is statistically significant via permutation test (10,000 shuffles, p < 0.05) for at least one benchmark at at least one model size, confirmed by both CodeBERT and all-MiniLM-L6-v2 encoders.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** — Pure statistical analysis step. No model training. Consumes H-E1 embedding distances and H-E2/H-C1 pass@1 ranks to test whether distributional alignment predicts behavioral outcomes.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 VALIDATED ✅, H-E2 VALIDATED ✅
**Gate Status:** SHOULD_WORK — does not block Phase 5 on failure; mechanistic claim weakened if ρ ≤ 0 or p ≥ 0.05

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM (SHOULD_WORK)
- **Prerequisites:** H-E1 (embedding similarity matrices), H-E2 (pass@1 at 1.3B), H-C1 (pass@1 at 7B, optional)

### Gate Condition
SHOULD_WORK: Observed Spearman ρ > 0 with permutation test p < 0.05 for ≥1 benchmark at ≥1 model size, confirmed by both CodeBERT and all-MiniLM-L6-v2 encoders. Falsified if ρ ≤ 0 or permutation p ≥ 0.05 for both benchmarks at both model sizes, or if pretraining-source similarity predicts pass@1 better than SFT-source similarity.

---

## Continuation Context

This experiment is a pure statistical analysis step — it re-uses all data produced by H-E1 and H-E2 with zero additional compute. The key inputs are:

- **From H-E1 (VALIDATED):** 4×2 mean pairwise cosine similarity matrix per encoder (4 training sources × 2 test benchmarks). MiniLM values span 0.247–0.311; CodeBERT spans 0.909–0.980 for some pairs.
- **From H-E2 (VALIDATED):** pass@1 per source condition × benchmark × seed at 1.3B scale. Source identity produces ≥2.0 pp effect, confirming rank variation exists to correlate against.
- **From H-C1 (pending, optional):** pass@1 at 7B scale — extends the analysis to a second model size if available.

### Previous Hypothesis Results (if applicable)

**H-E1:** 10/16 pairwise similarities below 0.95 threshold. MiniLM encoder: all 8 pairs dramatically below (0.247–0.311). CodeBERT: 2/8 pairs below (LeetCode→HumanEval+ 0.909, LeetCode→MBPP+ 0.946). Mean similarity: 0.611, std: 0.340.

**H-E2:** Source identity effect confirmed at 1.3B. Fixed effect p < 0.05, minimum pairwise contrast ≥2.0 pp for ≥1 source-benchmark pair.

**Risk note from H-E1:** CodeBERT shows very high similarity for HumanEval-only and MBPP-only pairs (~0.978–0.980), meaning rank spread for CodeBERT may be insufficient to drive a significant ρ. MiniLM has much better rank separation. Dual-encoder concordance is required — but even if CodeBERT alone fails, MiniLM success + CodeBERT direction agreement is meaningful.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Archon KB returned no domain-relevant results for this query (KB contains primarily diffusion model and computer vision content, not code LLM statistical analysis). All design grounded in Exa search results and standard statistical methodology.

**Key insight from Archon query attempt:** The mechanism being tested (Spearman ρ between embedding distance and pass@1 rank) is a statistical relationship test, not a learned neural mechanism. Standard scipy implementation is the ground truth.

### Archon Code Examples

No relevant code examples found in Archon KB. Implementation grounded directly in scipy.stats documentation and established patterns from Exa search.

### Exa GitHub Implementations

**Source 1: scipy.stats.permutation_test documentation + examples**
- **URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html
- **Relevance:** Canonical implementation of permutation test for Spearman correlation with small samples
- **Key finding:** `permutation_type='pairings'` is explicitly recommended for Spearman ρ, Kendall's τ, and Pearson's r. For n=4 conditions, exact null distribution computable (4! = 24 distinct pairings).
- **Key code pattern:**
  ```python
  def statistic(x):  # permute only embedding_distances
      return stats.spearmanr(x, pass_at_1_ranks).statistic
  res = stats.permutation_test((embedding_distances,), statistic,
                               permutation_type='pairings',
                               n_resamples=10000,
                               alternative='greater')
  ```
- **Critical note:** scipy docs explicitly warn: asymptotic p-value only accurate for >500 observations. For n=4 (our case), **permutation test is mandatory**, not optional.

**Source 2: scipy.stats.spearmanrho with PermutationMethod (scipy ≥1.17)**
- **URL:** https://scipy.github.io/devdocs/reference/generated/scipy.stats.spearmanrho.html
- **Relevance:** Newer API that handles ties correctly in exact permutation mode
- **Key code:**
  ```python
  res = stats.spearmanrho(embedding_distances, pass_at_1,
                          method=stats.PermutationMethod())
  ```
- **Advantage:** Handles ties correctly (relevant if two sources have identical pass@1)

**Source 3: PILLAR-Benchmarking/calculate_spearman.py (stfbk)**
- **URL:** https://github.com/stfbk/PILLAR-Benchmarking/blob/master/calculate_spearman.py
- **Relevance:** Real-world pattern for computing Spearman ρ between two judge systems — rank multiple conditions, report ρ per subset
- **Pattern extracted:** Compute ρ per condition grouping, report in structured table

**Source 4: "Examining robustness of LLM evaluation to distributional shifts" (arxiv 2404.16966)**
- **URL:** https://arxiv.org/html/2404.16966v2
- **Relevance:** Uses permutation tests to test whether semantic similarity drives performance correlation across benchmarks — directly analogous to H-M2
- **Key methodology:** Permute performance matrix column labels, compute similarity distribution, compare observed vs permuted. Exactly the logic H-M2 uses.
- **Insight:** They use 75th percentile and KS test as additional robustness checks alongside mean permutation test. We should report both ρ and the full null distribution.

**Source 5: "The Magic Correlations" — Fan et al. 2025 (arxiv 2602.11217)**
- **URL:** https://arxiv.org/html/2602.11217v1
- **Relevance:** Directly investigates correlation between pretraining rank order and SFT rank order across benchmarks and model scales — the closest published analogue to H-M2
- **Key finding:** "Transfer reliability varies dramatically across capability categories, benchmarks, and scales." Exactly the heterogeneity H-M2 must handle.
- **Methodology:** Suite of correlation protocols applied to accuracy metrics across diverse data mixtures and model scales — reports ρ per (benchmark × scale) cell.

**Source 6: "The Best Instruction-Tuning Data are Those That Fit" — GRAPE paper (arxiv 2502.04194)**
- **URL:** https://arxiv.org/html/2502.04194v3
- **Relevance:** GRAPE selects SFT data by distributional alignment (normalized probability similarity to target model) — validates the core H-D1 alignment mechanism from a different angle
- **Key finding:** GRAPE's alignment-based selection significantly outperforms distillation-only baselines on HumanEval and MBPP.

### 🎯 Implementation Priority Assessment

**This is a statistical analysis experiment, not a paper method reproduction.** No author implementation to find.

**Recommended Implementation Path:**
- Primary: `scipy.stats.permutation_test` with `permutation_type='pairings'`, `n_resamples=10000`
- Fallback: `scipy.stats.spearmanrho` with `stats.PermutationMethod()` (scipy ≥1.17, handles ties exactly)
- Justification: scipy is the ground-truth implementation for Spearman permutation tests; n=4 makes exact enumeration feasible (24 permutations) but 10K random shuffles produces equivalent p-values and matches H-M2's protocol specification.

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. H-M2 uses scipy.stats directly; no complex architecture requiring semantic analysis. n=4 conditions means the entire analysis fits in ~50 lines of Python.

---

## Experiment Specification

### Dataset

**Type:** programmatic-api (pre-computed results from upstream pipeline steps — not synthetic)
**Source:** H-E1 and H-E2 pipeline outputs

**Input Data Specification:**

| Input | Source | Format | Size |
|-------|--------|--------|------|
| Embedding similarity matrix | H-E1 output | 4×2 float matrix per encoder | 8 values × 2 encoders |
| pass@1 per condition | H-E2 output | 4×2 float matrix (source × benchmark) | 8 values × 3 seeds |
| pass@1 at 7B (optional) | H-C1 output | 4×2 float matrix | 8 values × 3 seeds (if available) |

**Conditions (n=4):**
- HumanEval-only (HE)
- MBPP-only (MB)
- LeetCode-only (LC)
- Equal-mix (EQ)

**Benchmarks (n=2):** HumanEval+ (164 problems), MBPP+ (374 problems)

**Encoders (n=2):** `microsoft/codebert-base`, `sentence-transformers/all-MiniLM-L6-v2`

**Model sizes:** 1.3B (required), 7B (if H-C1 available)

**No new data download required.** All inputs are files written by H-E1 and H-E2 validation scripts.

**Loading Information** (for Phase 4):
- Method: programmatic-api (load numpy/JSON files from prior hypothesis output dirs)
- Identifier: `docs/youra_research/h-e1/results/similarity_matrix_*.npy`, `docs/youra_research/h-e2/results/pass_at_1_*.json`
- Code:
  ```python
  import numpy as np, json
  sim_codebert = np.load("docs/youra_research/h-e1/results/similarity_matrix_codebert.npy")  # shape (4, 2)
  sim_minilm   = np.load("docs/youra_research/h-e1/results/similarity_matrix_minilm.npy")   # shape (4, 2)
  with open("docs/youra_research/h-e2/results/pass_at_1_1b.json") as f:
      pass_at_1_1b = json.load(f)  # dict: source_condition -> {humaneval+: float, mbpp+: float}
  ```

### Models

#### Baseline Model

**No neural model.** H-M2 is a statistical test over pre-computed matrices. The "model" is the statistical procedure.

**Statistical method:** Spearman rank correlation + permutation test (scipy.stats)

**Loading Information** (for Phase 4):
- Method: pip package
- Identifier: `scipy>=1.7.0`, `numpy>=1.21`, `matplotlib>=3.4`, `seaborn>=0.11`
- Code: `from scipy import stats; import numpy as np`

#### Proposed Model

**Architecture:** Statistical correlation analysis — Spearman ρ computed between embedding-distance rank and pass@1 rank across 4 source conditions, for each (benchmark × encoder × model_size) cell.

**Core Mechanism Implementation:**

```python
# Core Mechanism: H-M2 Spearman Permutation Test
# Based on: scipy.stats.permutation_test (permutation_type='pairings')
# Reference: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html

import numpy as np
from scipy import stats

def run_h_m2_analysis(sim_matrix, pass_at_1, encoder_name, benchmark, model_size, n_resamples=10000):
    """
    Args:
        sim_matrix: shape (4,) — mean cosine sim for each source condition to this benchmark
        pass_at_1:  shape (4,) — mean pass@1 across seeds for each source condition
        encoder_name: str — 'codebert' or 'minilm'
        benchmark: str — 'humaneval+' or 'mbpp+'
        model_size: str — '1.3b' or '7b'
    Returns:
        dict with rho, pvalue, significant, null_distribution
    """
    # Higher similarity = closer = higher predicted rank
    # Higher pass@1 = better performance = higher rank
    # Hypothesis: closer embedding distance → higher pass@1 (positive ρ)
    
    def statistic(x):  # permute only embedding distances
        return stats.spearmanr(x, pass_at_1).statistic

    result = stats.permutation_test(
        (sim_matrix,), statistic,
        permutation_type='pairings',
        n_resamples=n_resamples,
        alternative='greater'  # one-sided: ρ > 0
    )
    return {
        'rho': result.statistic,
        'pvalue': result.pvalue,
        'significant': result.pvalue < 0.05,
        'null_distribution': result.null_distribution,
        'encoder': encoder_name,
        'benchmark': benchmark,
        'model_size': model_size
    }

# Run all (benchmark × encoder × model_size) cells
# Significance requires ≥1 cell: pvalue < 0.05 AND rho > 0
# Concordance check: both encoders must agree in direction (rho > 0) for valid support
```

### Training Protocol

**No training.** This is a statistical analysis experiment.

**Compute protocol:**

| Step | Operation | Cost |
|------|-----------|------|
| Load H-E1 matrices | Read numpy files | Negligible |
| Load H-E2/H-C1 pass@1 | Read JSON files | Negligible |
| Permutation test × 8 cells | 10K shuffles each | <1 second total |
| Bootstrap CI for ρ | 1000 resamples | <1 second |
| Visualization | matplotlib/seaborn | <5 seconds |

**Seeds:** Fixed seed for reproducibility (`numpy.random.seed(42)` before permutation tests). Single run sufficient — permutation test is deterministic given seed.

**Total wall-clock time:** ~30 seconds including I/O and plotting.

### Evaluation

**Primary metric:** Spearman ρ between embedding similarity ranks and pass@1 ranks across 4 source conditions.

**Test cells (2 benchmarks × 2 encoders × ≤2 model sizes = up to 8 cells):**

| Cell | Benchmark | Encoder | Model Size |
|------|-----------|---------|------------|
| C1 | HumanEval+ | CodeBERT | 1.3B |
| C2 | MBPP+ | CodeBERT | 1.3B |
| C3 | HumanEval+ | MiniLM | 1.3B |
| C4 | MBPP+ | MiniLM | 1.3B |
| C5* | HumanEval+ | CodeBERT | 7B |
| C6* | MBPP+ | CodeBERT | 7B |
| C7* | HumanEval+ | MiniLM | 7B |
| C8* | MBPP+ | MiniLM | 7B |

*C5–C8 only if H-C1 data available.

**Success criteria:**
- **Gate satisfied:** ρ > 0 AND permutation p < 0.05 in ≥1 cell, with both encoders agreeing in direction (ρ > 0) for that benchmark-model_size pair
- **Strong support:** ≥2 cells significant, both encoders independently significant for ≥1 benchmark
- **Falsified:** ρ ≤ 0 or p ≥ 0.05 in ALL cells across both benchmarks and both model sizes

**Risk specific to n=4:**
With n=4 ranked items, the minimum achievable p-value under permutation test (one-sided, `alternative='greater'`) is 1/24 ≈ 0.042. Perfect rank concordance (ρ=1.0) achieves p=0.042, which IS below 0.05. So the gate is achievable but requires near-perfect rank alignment. This is a known limitation documented in the risk register.

**Expected baseline ρ from H-E1 data:**
MiniLM similarities (0.247–0.311 range) show better separation than CodeBERT (0.909–0.980). MiniLM rank order from H-E1: LeetCode ≈ 0.25 (most distant), HumanEval ≈ 0.31 (closest to HumanEval+). If pass@1 ranks from H-E2 show HumanEval-only > LeetCode-only > MBPP-only > Equal-mix on HumanEval+, ρ approaches 1.0 for MiniLM cells.

**Supplementary analysis:**
- Bootstrap 95% CI for ρ (1000 resamples with replacement)
- Kendall's τ as robustness check (consistent with Spearman for small n)
- Pretraining-vs-SFT comparison: if pretraining corpus similarity (CodeBERT on base model) predicts pass@1 better than SFT-source similarity, this weakens the mechanism claim

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical correlation analysis
- Library: `scipy>=1.7.0`, `numpy`, `matplotlib`, `seaborn`
- Code:
  ```python
  from scipy import stats
  import numpy as np
  # permutation test: stats.permutation_test((x,), statistic, permutation_type='pairings')
  # bootstrap CI: np.percentile(bootstrap_rhos, [2.5, 97.5])
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Summary:** Bar chart of Spearman ρ per cell (benchmark × encoder), with p-value annotations and significance markers (p < 0.05 marked with *)

#### Additional Figures (LLM Autonomous)
- **Scatter plot:** Embedding similarity rank vs pass@1 rank, one panel per (benchmark × encoder), with regression line and ρ/p annotated
- **Null distribution plot:** Histogram of null ρ distribution from permutation test, with observed ρ marked as vertical line, for the most significant cell
- **Rank order table:** Visual heatmap of condition rankings (rows: source conditions, columns: benchmarks × metrics), showing alignment or misalignment between embedding rank and pass@1 rank
- **Dual-encoder concordance plot:** Scatter of CodeBERT ρ vs MiniLM ρ per benchmark, showing whether encoders agree

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m2/figures/`.

---

## 🔬 Mechanism Verification Protocol

**Pre-conditions:**
- `mechanism_exists`: H-E1 and H-E2 result files exist and are loadable as numpy/JSON
- `mechanism_isolatable`: Embedding distance and pass@1 are independently measured — no circularity
- `baseline_measurable`: Null distribution from permutation test provides exact comparison baseline

**Architecture compatibility:**
- No neural architecture — scipy.stats.permutation_test is the mechanism
- Compatibility check: verify scipy version ≥ 1.7.0 (required for `permutation_type='pairings'`)
- Verify H-E1 output has correct shape (4, 2) per encoder
- Verify H-E2 output has all 4 source conditions × 2 benchmarks × 3 seeds

**Activation indicators:**
- `mechanism_log_message`: "Permutation test completed: ρ={rho:.3f}, p={pvalue:.4f} for {benchmark}/{encoder}/{model_size}"
- `tensor_shape_change`: Input rank vectors shape (4,) → Spearman ρ scalar + p-value scalar
- `metric_delta_expected`: ρ > 0.6 expected for MiniLM+HumanEval+ cell (based on H-E1 distance spread); ρ may be near 0 for CodeBERT due to compressed similarity range

**Mechanism verification code:**
```python
# Sanity check before running permutation test
def verify_inputs(sim_matrix, pass_at_1):
    assert sim_matrix.shape == (4,), f"Expected (4,), got {sim_matrix.shape}"
    assert pass_at_1.shape == (4,), f"Expected (4,), got {pass_at_1.shape}"
    assert not np.any(np.isnan(sim_matrix)), "NaN in similarity matrix"
    assert not np.any(np.isnan(pass_at_1)), "NaN in pass@1"
    # Check rank variation exists (required for meaningful Spearman)
    assert len(np.unique(pass_at_1)) > 1, "All pass@1 values identical — no rank variation"
    print(f"✓ Input verified: sim range [{sim_matrix.min():.3f}, {sim_matrix.max():.3f}], "
          f"pass@1 range [{pass_at_1.min():.3f}, {pass_at_1.max():.3f}]")
```

**Failure detection:**
- If all pass@1 values are identical → analysis aborted, gate CANNOT_TEST (not FAIL)
- If H-E1 files missing → raise FileNotFoundError with clear message pointing to H-E1 rerun
- If ρ = NaN → likely tie in ranks; switch to `spearmanrho(..., method=stats.PermutationMethod())` for tie-safe exact test

**Success/failure thresholds:**
- `hypothesis_support_threshold`: p < 0.05 for ≥1 cell (gate), concordant direction for both encoders
- `hypothesis_support_metric`: permutation test p-value + Spearman ρ sign agreement across encoders

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Spearman ρ > 0 AND permutation p < 0.05 for ≥1 (benchmark × encoder × model_size) cell
3. Both encoders agree in sign of ρ for ≥1 benchmark

**Minimal success scenario:** MiniLM cells (C3 or C4) show p ≈ 0.042 (perfect rank concordance) — sufficient for gate satisfaction even if CodeBERT cells are non-significant due to compressed similarity range.

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

Archon KB returned no domain-relevant results (KB indexed primarily diffusion/vision content). Zero Archon sources used in this design. All specifications grounded in Exa search.

### B. GitHub Implementations (Exa)

**Source B.1: scipy.stats.permutation_test — official SciPy documentation**
- **URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html
- **Query Used:** "permutation test Spearman correlation n=4 small sample LLM benchmark ranking Python scipy stats"
- **Relevance:** Canonical, authoritative implementation. Explicitly designed for Spearman ρ with small samples via `permutation_type='pairings'`.
- **Key code (annotated):**
  ```python
  # For n=4: 4! = 24 distinct pairings → exact null distribution feasible
  # n_resamples=10000 for random approximation (matches H-M2 protocol spec)
  def statistic(x):
      return stats.spearmanr(x, y).statistic
  res = stats.permutation_test((x,), statistic,
                               permutation_type='pairings',
                               n_resamples=10000,
                               alternative='greater')
  ```
- **Used for:** Core mechanism pseudo-code, training protocol

**Source B.2: scipy.stats.spearmanrho — exact permutation with ties (scipy ≥1.17)**
- **URL:** https://scipy.github.io/devdocs/reference/generated/scipy.stats.spearmanrho.html
- **Query Used:** "permutation test Spearman correlation n=4 small sample LLM benchmark ranking Python scipy stats"
- **Relevance:** Handles ties correctly via `PermutationMethod()` — critical if two source conditions have identical pass@1 values
- **Used for:** Fallback implementation path

**Source B.3: PILLAR-Benchmarking/calculate_spearman.py**
- **URL:** https://github.com/stfbk/PILLAR-Benchmarking/blob/master/calculate_spearman.py
- **Query Used:** "Spearman rank correlation permutation test code LLM evaluation Python implementation"
- **Relevance:** Real-world pattern for multi-condition Spearman ρ reporting in LLM evaluation context
- **Used for:** Output reporting structure (per-subset ρ table)

**Source B.4: "Examining the robustness of LLM evaluation to distributional shifts" (arxiv 2404.16966)**
- **URL:** https://arxiv.org/html/2404.16966v2
- **Query Used:** "Spearman rank correlation permutation test code LLM evaluation Python implementation"
- **Relevance:** Directly analogous methodology — permutation tests to test whether semantic similarity drives performance correlation in LLM benchmarks
- **Key insight:** They additionally use KS test and 75th percentile statistics as robustness checks. We adopt the KS test as a supplementary validation.
- **Used for:** Evaluation methodology, supplementary analysis design

**Source B.5: "The Magic Correlations: Understanding Knowledge Transfer from Pretraining to SFT" (Fan et al. 2025, arxiv 2602.11217)**
- **URL:** https://arxiv.org/html/2602.11217v1
- **Query Used:** "SFT training distribution alignment pass@1 embedding cosine similarity rank correlation code benchmark"
- **Relevance:** Closest published analogue to H-M2 — correlation protocols applied to accuracy metrics across data mixtures and model scales. Finds transfer reliability varies by benchmark and scale.
- **Key finding applied:** Report ρ per (benchmark × scale) cell, not as single aggregate number. Heterogeneity is expected and informative.
- **Used for:** Evaluation design (per-cell reporting), expected result interpretation

**Source B.6: GRAPE — "The Best Instruction-Tuning Data are Those That Fit" (Zhang et al. 2026, arxiv 2502.04194)**
- **URL:** https://arxiv.org/html/2502.04194v3
- **Query Used:** "SFT training distribution alignment pass@1 embedding cosine similarity rank correlation code benchmark"
- **Relevance:** Independent validation of the H-D1 distributional alignment hypothesis from a different angle (response selection by perplexity alignment). Corroborates that closer-distribution SFT data improves HumanEval/MBPP.
- **Used for:** Prior art context in experiment discussion

### C. Code Analysis (Serena)

Serena analysis not performed — code from search results was sufficiently clear. H-M2 uses scipy.stats directly; the entire analysis is ~50 lines of Python with no complex architecture requiring semantic decomposition.

### D. Previous Hypothesis Context

**Source:** H-E1 validation outputs (VALIDATED) and H-E2 validation outputs (VALIDATED)

**Reused components:**
- Similarity matrices from H-E1: 4×2 arrays per encoder — directly fed as `sim_matrix` input
- pass@1 from H-E2: per-condition per-benchmark per-seed — averaged across seeds before rank computation
- No hyperparameters inherited (statistical analysis, not training)

**Why reused:** H-M2 is explicitly defined in H-D1 verification plan as a secondary analysis over H-E1 + H-E2 data. No new data collection.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Statistical method (Spearman + permutation test) | GitHub/Docs | B.1 (scipy.stats.permutation_test) |
| `permutation_type='pairings'` choice | GitHub/Docs | B.1 (SciPy docs explicit recommendation for Spearman) |
| Tie-safe fallback | GitHub/Docs | B.2 (spearmanrho + PermutationMethod) |
| n_resamples=10000 | Phase 2B spec | 02b_verification_plan.md §H-M2 |
| alternative='greater' (one-sided) | Phase 2B spec | 02b_verification_plan.md §H-M2 "ρ > 0" |
| Per-cell reporting structure | GitHub | B.3 (PILLAR-Benchmarking pattern) |
| Supplementary KS test | Paper | B.4 (arxiv 2404.16966) |
| Per-(benchmark × scale) cell design | Paper | B.5 (arxiv 2602.11217) |
| Input data (sim matrices) | Pipeline | H-E1 outputs |
| Input data (pass@1 ranks) | Pipeline | H-E2 outputs |
| n=4 minimum p-value constraint (1/24 ≈ 0.042) | Statistical theory | Standard combinatorics (documented in risk register) |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-02

### Workflow History for This Hypothesis
- 2026-08-02T00:00:00Z: experiment_design.status set to IN_PROGRESS
- 2026-08-02: Phase 2C experiment brief completed — all steps executed

---

*MCP Tools Used: Archon (no relevant results), Exa (GitHub + web search — 6 sources), Serena (skipped — sufficient clarity)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
