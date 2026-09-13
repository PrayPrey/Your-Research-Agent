# Validation Report: h-m1

**Date:** 2026-07-12  
**Hypothesis ID:** h-m1  
**Hypothesis Type:** MECHANISM (Step 1 of 4)  
**Validation Status:** COMPLETED  
**Gate Status:** ❌ FAIL (ratio: 0.973 < 1.15)

---

## Executive Summary

This validation report documents the implementation and execution of hypothesis h-m1, which tests whether stratified training enables a retrieval-quality classifier to learn factual density features independent of educational quality signals.

**Key Finding:** The experiment successfully ran with real BEIR data and measured actual entity density using spaCy NER. The mechanism validation resulted in a **density ratio of 0.973** (retrieval-selected documents had 97.3% of the entity density of perplexity-selected documents), **failing the gate threshold of 1.15** (15% improvement).

**Mock Data Status:** ✅ **FIXED** - All mock data generators removed from main experiment code. The experiment now uses:
- Real BEIR Natural Questions corpus (2.68M documents, 3.45K queries)
- Held-out evaluation set (documents not in training qrels)
- Actual entity density measurement via spaCy NER on real text

---

## Hypothesis Context

### Hypothesis Statement

Under stratified training (oversampling low-educational, high-BEIR examples), the retrieval-quality classifier learns to identify documents with high factual density and entity coverage, as evidenced by classifier-selected documents showing ≥15% higher named entity density than perplexity-matched controls.

### Prerequisites

- **H-E1 (EXISTENCE):** PASSED - Retrieval-quality filtering achieves +5% Recall@10 improvement (baseline: 0.47 → 0.52)

### Gate Condition

**Type:** SHOULD_WORK  
**Condition:** `entity_density_retrieval / entity_density_perplexity ≥ 1.15`  
**Action on Fail:** PIVOT to different training strategy or feature engineering

---

## Implementation Summary

### Dataset

**Training Data:**
- Source: BEIR Natural Questions qrels (4,201 documents with relevance judgments)
- Positive examples: 1,000 documents from successful BEIR retrievals
- Negative examples: 1,000 random documents from corpus
- Stratification: Oversampled 352 divergent examples (low-educational, high-BEIR) 3×
- Final training set: 2,704 examples (after stratification)

**Evaluation Data:**
- Source: Held-out BEIR corpus (2,677,267 documents not in qrels)
- Sample size: 10,000 documents randomly sampled from held-out set
- Selection size: 5,000 documents per method (retrieval classifier vs perplexity baseline)

### Models

**Baseline (Perplexity):**
- Model: GPT-2 (base)
- Selection: Top-5,000 documents with lowest perplexity
- Mean perplexity (eval corpus): 2,562.54

**Proposed (Stratified Retrieval Classifier):**
- Architecture: FastText text classifier
- Embedding dimension: 100
- N-grams: 2 (bigrams)
- Epochs: 25
- Learning rate: 0.1
- Training time: <5 seconds (CPU)

**Entity Density Measurement:**
- Model: spaCy `en_core_web_sm`
- Metric: Named entities per 100 tokens
- Batch size: 100 documents

### Execution Details

**Total Runtime:** 209.5 seconds (~3.5 minutes)

**Breakdown:**
1. BEIR data loading: ~9 seconds
2. Training data extraction: <1 second
3. Perplexity computation (2,000 training docs): ~15 seconds
4. Stratified sampling: <1 second
5. FastText training: <5 seconds
6. Classifier selection (10,000 docs): ~5 seconds
7. Perplexity selection (10,000 docs): ~15 seconds
8. Entity density computation (10,000 docs total): ~150 seconds
9. Visualization generation: <1 second

**Computational Resources:**
- CPU-only execution (no GPU required)
- Peak memory usage: <8 GB
- Environment: Conda (youra-h-m1, Python 3.11)

---

## Results

### Primary Metric: Entity Density Ratio

| Method | Entity Density | Ratio vs Baseline |
|--------|---------------|-------------------|
| Retrieval Classifier | 10.38 entities/100 tokens | 0.973× |
| Perplexity Baseline | 10.66 entities/100 tokens | 1.000× (reference) |

**Gate Threshold:** 1.15× (15% improvement required)  
**Observed Ratio:** 0.973× (2.7% **decrease**)  
**Gate Status:** ❌ FAIL

### Interpretation

The stratified retrieval-quality classifier selected documents with **slightly lower** entity density (10.38) compared to the perplexity baseline (10.66), contrary to the hypothesis prediction. This suggests:

1. **Mechanism not validated:** Stratified training on BEIR examples did not teach the classifier to prioritize factual density
2. **Possible explanations:**
   - BEIR relevance may correlate with different features than entity density (e.g., query-document semantic match, not factual coverage)
   - Stratification strategy may need refinement (different oversampling ratio, different stratification dimensions)
   - Entity density may not be the primary discriminator for retrieval quality
   - Held-out BEIR corpus may have different characteristics than Common Crawl (original experiment design)

---

## Validation Evidence

### Code Validation

✅ **All tasks implemented:**
- D-1: Download BEIR Natural Questions Dataset ✓
- D-2: Sample Common Crawl Documents (replaced with held-out BEIR sampling) ✓
- E-1: Install Dependencies ✓
- M-1: Data Infrastructure ✓
- M-2: Stratification Module ✓
- M-3: Classifier Training ✓
- M-4: Perplexity Baseline ✓
- M-5: NER Evaluation ✓
- M-6: Document Selection ✓
- M-7: Visualization ✓
- M-8: Integration ✓

✅ **Mock Data Fixed:**
- `run_experiment_simple.py`: Renamed to `.mock_backup` (hard-coded constants removed from execution path)
- `run_experiment.py`: Refactored to use held-out evaluation set, removed tautological label usage
- Entity density now measured via spaCy NER on real text, not derived from training labels

### Runtime Validation

✅ **Experiment executed successfully:**
- No crashes or errors
- All modules loaded correctly (BEIR, spaCy, FastText, GPT-2)
- Data pipeline: BEIR load → train/eval split → stratification → training → selection → evaluation
- Results saved to `outputs/results.json`
- Visualization saved to `figures/entity_density_comparison.png`

✅ **Data integrity:**
- Training set: 2,000 examples from qrels (1,000 positive, 1,000 negative)
- Evaluation set: 10,000 held-out documents (not in qrels)
- No data leakage between train and eval

### Output Validation

**Results file (`outputs/results.json`):**
```json
{
  "entity_density_retrieval": 10.377451089537372,
  "entity_density_baseline": 10.662917928120219,
  "density_ratio": 0.9732280750440726,
  "gate_threshold": 1.15,
  "gate_satisfied": false,
  "execution_time_seconds": 209.45902514457703
}
```

**Figure:** `figures/entity_density_comparison.png` (99 KB PNG)

---

## Gate Verdict

**Status:** ❌ FAIL  
**Condition:** `entity_density_retrieval / entity_density_perplexity ≥ 1.15`  
**Observed:** `10.38 / 10.66 = 0.973 < 1.15`

**Action:** PIVOT to different training strategy or feature engineering (per gate definition)

---

## Recommended Next Steps

### Immediate Actions (Addressing Failure)

1. **Investigate mechanism failure:**
   - Analyze which features the classifier actually learned (feature importance, model introspection)
   - Check if BEIR positive examples actually have higher entity density than negative examples
   - Verify stratification logic (confirm divergent examples were correctly identified)

2. **Experiment modifications:**
   - **Alternative 1:** Try different stratification dimensions (e.g., oversample high-BEIR, low-perplexity instead)
   - **Alternative 2:** Use Common Crawl for evaluation instead of held-out BEIR (original design called for this)
   - **Alternative 3:** Increase training data size (current: 2,000 examples) or adjust oversampling ratio

3. **Hypothesis refinement:**
   - **Pivot option:** Test whether BEIR relevance correlates with different features (e.g., semantic density, question-answering cues)
   - **Pivot option:** Replace entity density with alternative factual density metrics (e.g., knowledge graph coverage, citation density)

### Research Implications

**For Paper:**
- Document negative result: Stratified training on BEIR examples does not improve entity density selection
- Insight: BEIR retrieval quality may not be driven by factual density (challenges assumption from H-E1)
- Contribution: First systematic test of stratification strategy for retrieval-quality classification

**For Hypothesis Chain:**
- **Step 2 (Necessity):** May need to reconsider or skip if mechanism is not validated
- **Step 3 (Efficiency):** Depends on mechanism validation success
- **Step 4 (Limits):** Requires validated mechanism

---

## Appendix: Files Generated

### Code Files
- `run_experiment.py` (main experiment script, 298 lines)
- `run_experiment_simple.py.mock_backup` (mock version, not executed)

### Output Files
- `outputs/results.json` (experiment metrics)
- `figures/entity_density_comparison.png` (primary visualization)
- `experiment.log` (execution logs, 209.5s runtime)

### Data Files
- `data/beir_nq/` (symlink to cached BEIR Natural Questions corpus)
- `models/pretrained/gpt2/` (cached GPT-2 model)

---

## Changelog

**2026-07-12 08:00 UTC** - Mock data fix applied:
- Removed hard-coded constants from `run_experiment_simple.py`
- Refactored `run_experiment.py` to use held-out evaluation set
- Fixed tautological label usage in stratification
- Measured real entity density via spaCy NER
- Experiment executed successfully with real BEIR data
- Gate failed (ratio: 0.973 < 1.15)

---

*Validation completed in unattended mode. All steps executed automatically without user intervention.*
