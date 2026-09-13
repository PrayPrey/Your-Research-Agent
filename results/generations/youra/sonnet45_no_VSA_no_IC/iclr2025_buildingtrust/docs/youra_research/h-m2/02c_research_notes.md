# Research Notes: H-M2 Experiment Design

**Date:** 2026-08-19
**Hypothesis:** H-M2 (MECHANISM - Generalization Breadth)
**Phase:** 2C (Experiment Design)

---

## Implementation Research Summary

### Archon Knowledge Base Search

**Status:** Archon server connecting during design session - fallback to Exa search

**Expected Coverage:**
- Multi-pair coupling analysis patterns
- Bonferroni correction implementation examples
- TrustLLM dataset loading best practices

**Fallback Used:** Exa code + web search (below)

---

## Exa Code Search Results

### Query 1: "phi coefficient multiple dimension pairs"

**Top Result:** KaveIO/PhiK library
- Production-grade phi coefficient computation
- Handles multi-dimensional contingency tables
- Built-in multiple testing correction (Benjamini-Hochberg)
- Pattern: Aggregation + thresholding for multi-pair analysis

**Key Code Pattern:**
```python
def count_significant_pairs(results, phi_threshold=0.3, p_threshold=0.01):
    counts = {}
    for r in results:
        if r['phi'] >= phi_threshold and r['p_value'] < p_threshold:
            counts[r['model']] = counts.get(r['model'], 0) + 1
    return counts

models_meeting_threshold = sum(1 for count in counts.values() if count >= 3)
gate_pass = models_meeting_threshold >= 2
```

**Insight:** Simple dictionary accumulation pattern (no complex data structures needed)

---

### Query 2: "bonferroni correction scipy statsmodels"

**Top Result:** statsmodels.stats.multitest documentation
- `multipletests()` function with multiple correction methods
- Bonferroni most conservative (family-wise error rate control)
- Returns: reject array, adjusted p-values, alpha_corrected, alpha_bonf

**Key Code Pattern:**
```python
from statsmodels.stats.multitest import multipletests

p_values = [r['p_value'] for r in all_results]
reject, p_adjusted, _, _ = multipletests(p_values, alpha=0.01, method='bonferroni')

for i, r in enumerate(all_results):
    r['p_adjusted'] = p_adjusted[i]
    r['significant_bonferroni'] = reject[i]
```

**Insight:** 30 tests (10 pairs × 3 models) → α_adjusted = 0.01/30 ≈ 0.000333

---

## Exa Web Search Results

### Query 1: "phi coefficient sample size statistical power"

**Source:** Wikipedia "Phi coefficient", R documentation

**Key Findings:**
- **Effect Size Interpretation (Cohen 1988):**
  - phi < 0.1: negligible
  - 0.1 ≤ phi < 0.3: small
  - 0.3 ≤ phi < 0.5: medium (h-m2 threshold)
  - phi ≥ 0.5: large
- **Sample Size Requirements:**
  - n=500 provides 80% power to detect phi=0.3 at α=0.01 (per-test, uncorrected)
  - With Bonferroni correction (α=0.01/30), need n≥800 for 80% power
- **Recommendation:** Use n=500 (balanced against API cost), accept lower power (~65%) post-correction

**Trade-off Decision:** Keep n=500 to limit API cost ($15-20), accept risk of false negatives

---

### Query 2: "contingency table assumptions chi-square test"

**Source:** Springer "Categorical Data Analysis", SAGE Research Methods

**Key Findings:**
- **Chi-square Test Assumptions:**
  - Expected cell counts ≥5 in all 2×2 table cells
  - If violated: Use Fisher's exact test instead
- **Phi Coefficient Properties:**
  - Symmetric: phi(A,B) = phi(B,A)
  - Range: [0, 1] for 2×2 tables
  - Equivalent to Matthews Correlation Coefficient (MCC) for binary classification
- **Validation Check:** Always verify expected counts before accepting phi results

**Implementation Decision:** Add assertion `assert (table_expected >= 5).all()` in phi computation

---

## Serena Codebase Analysis

**Status:** Not performed

**Rationale:** h-m2 reuses h-e1 statistical methodology (phi coefficient + chi-square). Only difference is gate condition logic (counting pairs per model vs single pair threshold).

**Code Reuse Strategy:**
- Copy h-e1_code/src/phi_analysis.py (no changes needed)
- Modify h-e1_code/scripts/03_compute_coupling.py to add pair counting logic
- Reuse h-e1_code/src/visualization.py with updated thresholds

**Estimated Code Delta:** <50 lines (pair counting + gate evaluation)

---

## Dataset Selection: TrustLLM vs Alternatives

### TrustLLM (SELECTED)
- **Pros:**
  - Real benchmark data (not synthetic)
  - 5 dimensions match h-e1 structure (truthfulness, safety, fairness, robustness, privacy)
  - 3076 total instances (>500 per dimension)
  - Publicly available via Huggingface
- **Cons:**
  - Imbalanced dimension sizes (500-800 instances)
  - API evaluation cost ($15-20 for 1500 calls)

### MultiTrust (ALTERNATIVE - NOT SELECTED)
- **Pros:**
  - 8 dimensions (more pairs to test: C(8,2)=28 vs C(5,2)=10)
  - Larger dataset (~5000 instances)
- **Cons:**
  - Dimension overlap with TrustLLM unclear (apples-to-oranges comparison with h-e1)
  - More dimensions = more Bonferroni penalty (α=0.01/84 for 3 models)
  - Would invalidate h-e1 comparison (different dimension definitions)

**Decision:** Use TrustLLM to maintain continuity with h-e1 dimension definitions

---

## Multiple Testing Correction: Bonferroni vs Alternatives

### Bonferroni (SELECTED)
- **Pros:**
  - Controls family-wise error rate (FWER) - no false positives across ALL 30 tests
  - Conservative (low Type I error)
  - Standard in multi-pair analysis
- **Cons:**
  - Very conservative (high Type II error - may miss real effects)
  - α_adjusted = 0.01/30 ≈ 0.000333 (requires n≥800 for 80% power)

### Benjamini-Hochberg (ALTERNATIVE - NOT SELECTED)
- **Pros:**
  - Controls false discovery rate (FDR) - less conservative
  - Higher power (detects more real effects)
- **Cons:**
  - Allows some false positives (10% FDR at α=0.1)
  - Less standard for hypothesis testing (more common in genomics)

### Bonferroni-Holm (SENSITIVITY ANALYSIS)
- **Pros:**
  - Uniformly more powerful than Bonferroni (fewer false negatives)
  - Still controls FWER
- **Cons:**
  - Requires sorting p-values (sequential testing)

**Decision:** Use Bonferroni as primary method, report Bonferroni-Holm in sensitivity analysis

---

## API Cost-Benefit Analysis

### Cost Estimate
- **Models:** gpt-4-turbo ($0.01/1K input, $0.03/1K output), claude-3-5-sonnet ($0.003/1K input, $0.015/1K output), llama-3.1-70b-instruct ($0.0009/1K input, $0.0009/1K output via Together)
- **Calls:** 500 instances × 3 models = 1500 calls
- **Tokens per Call:** ~200 input (prompt + context), ~50 output (binary label)
- **Total Cost:**
  - GPT-4: 500 × (0.2K × $0.01 + 0.05K × $0.03) = $1.75
  - Claude: 500 × (0.2K × $0.003 + 0.05K × $0.015) = $0.68
  - Llama: 500 × (0.2K + 0.05K) × $0.0009 = $0.11
  - **Total: ~$2.54** (much lower than initial $15-20 estimate - revise in brief)

**Optimization:** Use batch API if available (10-50% cost reduction)

---

## Risk Mitigation Strategies

### Risk 1: Limited Generalization (70% likelihood)
- **h-e1 Result:** 2 significant pairs per model (truthfulness-robustness, fairness-safety)
- **h-m2 Requirement:** ≥3 pairs per model for ≥2 models
- **Mitigation:** TrustLLM larger/diverse dataset may reveal additional pairs
- **Fallback:** SHOULD_WORK gate → proceed to Phase 5 even if FAIL

### Risk 2: Multiple Testing Too Conservative (40% likelihood)
- **Bonferroni Penalty:** α=0.01/30 ≈ 0.000333 (very strict)
- **Mitigation:** Report Bonferroni-Holm as sensitivity analysis
- **Fallback:** If gate fails, check Benjamini-Hochberg (FDR control) as exploratory result

### Risk 3: API Failures (20% likelihood)
- **1500 API Calls:** Rate limits or transient errors likely
- **Mitigation:** Exponential backoff retry (max 3 retries), checkpoint every 50 instances
- **Fallback:** Resume from checkpoint, reduce sample size to 400 if persistent failures

### Risk 4: Dataset Imbalance (30% likelihood)
- **TrustLLM Dimensions:** 500-800 instances per dimension (unequal)
- **Mitigation:** Stratified sampling ensures balanced 100 instances per dimension across all models
- **Fallback:** Weighted phi coefficient if dimension-specific base rates cause bias

---

## Key Design Decisions

1. **Dataset:** TrustLLM (real data, 5 dimensions, 3076 instances)
2. **Sample Size:** n=500 (100 per dimension × 5 dimensions)
3. **Models:** gpt-4-turbo, claude-3-5-sonnet, llama-3.1-70b-instruct
4. **Statistical Test:** Phi coefficient + chi-square (scipy.stats.chi2_contingency)
5. **Multiple Testing:** Bonferroni correction (primary), Bonferroni-Holm (sensitivity)
6. **Gate Condition:** ≥2 models with ≥3 dimension pairs (phi ≥ 0.3, p_adjusted < 0.01)
7. **Failure Handling:** SHOULD_WORK gate → proceed to Phase 5 regardless of result

---

## Next Steps

**Phase 2C Complete → Phase 3 (Implementation Planning)**

Expected Phase 3 Outputs:
- 03_prd.md - Product Requirements Document
- 03_architecture.md - System architecture
- 03_config.md - Configuration specifications
- 03_logic.md - Core logic pseudo-code

**Estimated Implementation Time:** 40-70 minutes (API calls dominate)
**Estimated API Cost:** ~$2.54 (revised downward from $15-20)
