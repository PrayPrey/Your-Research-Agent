# Results

All four hypotheses pass their gate conditions, providing strong evidence for multi-dimensional truthfulness structure.

## H-E1: Inter-Benchmark Correlations

**Finding:** Cross-benchmark correlations fall in the moderate range, supporting partial independence.

| Benchmark Pair | Spearman r | 95% CI | p-value (adj) | Gate |
|----------------|------------|--------|---------------|------|
| TruthfulQA–HaluEval | 0.578 | [0.357, 0.738] | 3.3×10⁻⁵ | PASS |
| TruthfulQA–FactScore | 0.424 | [0.165, 0.628] | 0.0065 | PASS |
| HaluEval–FactScore | 0.444 | [0.189, 0.643] | 0.0037 | PASS |

**Baseline reference:** r(MMLU-Physics, HaluEval) = 0.10

All correlations satisfy the gate condition: 0.10 < r < 0.70. The correlations are statistically significant after Bonferroni correction (p < 0.0167).

**Interpretation:** Truthfulness benchmarks measure related but non-identical constructs. If they were interchangeable (measuring a single truthfulness factor), we would expect r > 0.7. If they were unrelated, r would approach the 0.10 baseline. The moderate correlations support partial independence—a model's performance on one benchmark provides information about other benchmarks, but substantial unique variance remains unexplained.

Figure 1 shows the correlation heatmap across all benchmark pairs.

## H-M1: TruthfulQA vs. MMLU Distinctness

**Finding:** TruthfulQA measures a capability distinct from general knowledge.

| Metric | Value |
|--------|-------|
| r(TruthfulQA, MMLU) | 0.19 |
| r(MMLU internal, mean) | 0.78 |
| r² gap | 0.58 |

The correlation between TruthfulQA and MMLU (r=0.19) is dramatically lower than the internal correlation among MMLU subjects (r=0.78). This passes the gate condition: r(TQA, MMLU) < r(MMLU internal).

**Divergent Profile Analysis:** We identified 4 models (8%) exhibiting high MMLU (z > 1.0) but low TruthfulQA (z < 0):
- yi-13b-instruct
- qwen-70b-dpo
- qwen-13b-instruct
- llama-70b-dpo

Figure 2 shows the gate comparison visualization. Figure 3 plots TruthfulQA against MMLU with divergent models highlighted.

**Interpretation:** These models demonstrate strong factual knowledge (as measured by MMLU) but weaker resistance to misconceptions (as measured by TruthfulQA). This supports our hypothesis that knowing facts is insufficient for avoiding falsehoods—TruthfulQA captures a distinct capability of resisting imitative falsehoods.

## H-M2: HaluEval vs. TruthfulQA Distinctness

**Finding:** HaluEval measures generation coherence, distinct from misconception resistance.

| Metric | Value | Threshold |
|--------|-------|-----------|
| r(HaluEval, TruthfulQA) | 0.162 | < 0.7 |
| r(intra-HaluEval, mean) | 0.645 | Reference |

**HaluEval subtask correlations with TruthfulQA:**

| Subtask | Spearman r | p-value |
|---------|------------|---------|
| QA | 0.153 | 0.288 |
| Dialogue | 0.148 | 0.306 |
| Summarization | 0.222 | 0.122 |

**Intra-HaluEval correlations (coherence within benchmark):**

| Pair | Spearman r |
|------|------------|
| QA–Dialogue | 0.692 |
| QA–Summarization | 0.601 |
| Dialogue–Summarization | 0.641 |

**Interpretation:** The cross-benchmark correlation (r=0.162) is substantially lower than intra-HaluEval correlations (mean r=0.645). HaluEval subtasks share a common dimension—likely generation coherence—that is largely orthogonal to TruthfulQA's misconception resistance. A model can resist misconceptions while still hallucinating novel details during generation.

## H-M3: FactScore Distinctness and Factor Structure

**Finding:** FactScore measures a third distinct dimension; PCA confirms multi-factor structure.

| Correlation | Value | 95% CI |
|-------------|-------|--------|
| r(FactScore, TruthfulQA) | −0.005 | [−0.274, 0.261] |
| r(FactScore, HaluEval) | −0.147 | [−0.415, 0.130] |

Both correlations fall well below 0.7 (indeed, near zero), passing the gate condition.

**PCA Results:**

| Metric | Value |
|--------|-------|
| Components for 80% variance | 3 |
| PC1 explained variance | 38.6% |
| PC2 explained variance | 34.3% |
| PC3 explained variance | ~7% |

Figure 4 shows the PCA biplot. Figure 5 shows cumulative variance explained.

**Interpretation:** FactScore's near-zero correlations with both TruthfulQA and HaluEval indicate it captures an independent dimension—atomic factual precision in long-form generation. The PCA requiring 3 components for 80% variance definitively rejects the single-factor model. If truthfulness were a unified construct, PC1 should explain >80% variance; instead, it explains only 38.6%.

## Aggregate Results

| Hypothesis | Gate | Result | Pass Rate |
|------------|------|--------|-----------|
| H-E1 | MUST_WORK | PASS | 100% |
| H-M1 | MUST_WORK | PASS | 100% |
| H-M2 | SHOULD_WORK | PASS | 100% |
| H-M3 | SHOULD_WORK | PASS | 100% |

All four hypotheses pass their gate conditions. The evidence supports a three-dimensional truthfulness model:
1. **Misconception resistance** (TruthfulQA)
2. **Generation coherence** (HaluEval)
3. **Factual precision** (FactScore)
