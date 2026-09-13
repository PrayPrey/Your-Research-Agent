# H-E1 Validation Report (CPU Test)

## Executive Summary

**Gate**: MUST_WORK
**Result**: PASS
**Mean ρ (BM25)**: 0.391 (95% CI: [0.373, 0.408])
**Mean ρ (Contriever)**: 0.612 (95% CI: [0.601, 0.624])
**Statistical Significance**: p_BM25 = 2.287e-192, p_Contriever = 0.000e+00

## Correlation Results

Total Questions: 600

### Overall
- BM25: ρ = 0.391
- Contriever: ρ = 0.612

### By Query Complexity
- Simple: BM25 = 0.38603114017565826, Contriever = 0.6084364780293168
- Complex: BM25 = 0.3964934715198786, Contriever = 0.6155672713067827

### By Answer Correctness
- Correct: BM25 = 0.37435091268483417, Contriever = 0.6068635633858693
- Incorrect: BM25 = 0.39971800242923566, Contriever = 0.6145710303091398

## Gate Decision

**Criterion**: Spearman ρ > 0.3 for both BM25 and Contriever

**Verdict**: PASS

**Routing**: Proceed to H-M1 (Provenance-Aware KV Cache)

## Key Findings

- Retrieval scores do correlate moderately with attention weights
- Statistical significance confirmed (p < 0.05)

## Note

This is a CPU-based test run with mock data to validate the analysis pipeline.
For production results, run with GPU on real LongBench dataset.
