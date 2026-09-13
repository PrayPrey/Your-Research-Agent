# Experimental Setup

Our experiments test two hypotheses: (1) **h-e1 (EXISTENCE):** Do data quality components Q(D) correlate with information density? and (2) **h-m1 (MECHANISM):** Does curation causally increase information density? The first is our primary contribution; the second encountered scale limitations we discuss honestly in Section 5.

## Hypothesis h-e1: Quality Metrics Correlation

**Research Question:** Do deduplication ratio, domain diversity, perplexity score, and token efficiency correlate (r > 0.5, p < 0.01) with information density?

### Datasets

We created 12 controlled C4 subsets (10GB each, 120GB total) using fractional factorial sampling to isolate quality dimensions:

| Subset ID | Dedup Level | Diversity | Perplexity | Efficiency | Total Tokens |
|-----------|-------------|-----------|------------|------------|--------------|
| C4-L1 | None (40% dups) | Low (1 domain) | Low (clean) | Low (<50th) | 2.1B |
| C4-L2 | Medium (20% dups) | Medium (4 domains) | Medium | Medium (50-75th) | 2.3B |
| C4-L3 | High (<5% dups) | High (8 domains) | High (noisy) | High (>75th) | 2.5B |
| ... | | | | | |
| C4-L12 | High | Low | Low | High | 2.4B |

Each subset isolates specific quality variations while holding other factors approximately constant via stratified sampling from C4 (allenai/c4, en split). Document selection uses MinHash LSH for deduplication detection (128 hash functions, Jaccard threshold 0.9), GPT-2 small perplexity scoring, automated domain classification, and efficiency filtering via regex-based heuristics.

### Metrics

For each subset, we compute:

**Q(D) components:**
- Deduplication ratio: 1 - (duplicate_tokens / total_tokens)
- Domain diversity: Shannon entropy over 8 C4 source categories
- Perplexity score: 1 - normalized log(GPT-2_perplexity)
- Token efficiency: content_tokens / total_tokens (excludes whitespace/boilerplate)

**Information density:**
- Token entropy: H(unigram distribution) normalized by log₂|V|
- N-gram redundancy: 1 - (repeated 3-grams / total 3-grams)
- Semantic diversity: 1 - average cosine similarity of SentenceTransformer embeddings

Combined info_density = average of three normalized components ∈ [0,1].

### Evaluation Protocol

1. **Correlation analysis:** Compute Pearson r and Spearman ρ between each Q(D) component and info_density across 12 subsets
2. **Statistical significance:** Two-tailed t-test for H₀: r = 0 at α = 0.01 with Bonferroni correction (8 tests → α = 0.00125)
3. **Effect size:** Report R² (variance explained) for composite Q(D) fitted via linear regression
4. **Success criterion:** ALL four components must achieve r > 0.5, p < 0.01 (h-e1 MUST_WORK gate)

### Reproducibility Test

We independently resampled three additional C4 subsets at "Medium" quality level (middle of all dimensions) and computed coefficient of variation (CV = σ/μ) for each Q(D) component across the four instances.

**Success criterion:** CV < 10% for all components (stable enough for production use)

### Baseline Comparisons

- **Random baseline:** Correlate Q(D) with shuffled info_density (expect r ≈ 0, validates null hypothesis)
- **Single-metric baseline:** Best individual component (dedup_ratio alone)
- **Composite advantage:** Does weighted Q(D) outperform best single metric?

## Hypothesis h-m1: Curation Mechanism (Proof-of-Concept)

**Research Question:** Does data curation (deduplication + filtering + domain mixing) causally increase information density (>20% entropy reduction, >15% Fisher information increase)?

### Experimental Design (Planned vs Actual)

**Planned (from 02c_experiment_brief.md):**
- 9 curation conditions (factorial: {dedup, filter, mix} × {none, medium, aggressive})
- 50GB per condition (~10B tokens)
- 50,000 training steps per condition
- GPT-2 small (125M params) trained from scratch
- Measure entropy and Fisher information trace at convergence

**Actual (PoC in batch mode):**
- 3 curation conditions (baseline, medium, full) due to resource constraints
- 1,000 C4 samples per condition (~500k tokens, **0.005% of planned scale**)
- 500 training steps (1% of planned)
- Simplified curation: length-based filtering only (no MinHash LSH, no perplexity filter)

**Scale mismatch:** The PoC is 20,000× below specification in token count. We executed it to validate code correctness and measure PoC-scale effects, but we do NOT claim it tests the full hypothesis.

### Metrics

**Entropy reduction:** 
$$
\Delta H = \frac{H_{\text{baseline}} - H_{\text{curated}}}{H_{\text{baseline}}} \times 100\%
$$

Expected >20% if curation removes redundancy (Shannon theory prediction).

**Fisher information increase:**
$$
\Delta F = \frac{F_{\text{curated}} - F_{\text{baseline}}}{F_{\text{baseline}}} \times 100\%
$$

where F = trace(Fisher information matrix) computed via diagonal approximation of second derivatives of loss. Expected >15% if curation increases gradient informativeness.

### Success Criterion (h-m1 MUST_WORK gate)

Both thresholds must be met:
- Entropy reduction ≥ 20%
- Fisher increase ≥ 15%

Failure triggers either (a) one modification attempt, or (b) route to Phase 2A for hypothesis reformulation.

## Compute Resources

- **h-e1:** V100 GPUs (32GB), 9.2 GPU-hours total for all subset creation and analysis
- **h-m1 PoC:** H100 NVL GPUs (95GB), 2.5 GPU-hours for 3-condition training
- **Environment:** PyTorch 2.6.0, Transformers 4.46.0, datasketch 1.6.0
- **Code:** Open-sourced at [URL]

## Limitations (By Design)

**Web text only:** C4 represents web-crawled English text. Generalization to code (The Stack), scientific text (arXiv), or multilingual corpora (mC4) is untested. This is a principled boundary condition (Section 5), not an oversight—web text is the most common pretraining domain (GPT-3, T5, LLaMA).

**Single model scale:** GPT-2 small (125M params) for perplexity scoring and h-m1 training. Scale-invariance (whether Q(D) weights hold at 1B-100B params) is future work (hypothesis h-c1, blocked by h-m1).

**Correlation, not causation:** h-e1 tests correlation only. Causality requires h-m1 validation at full scale (900 GPU-hours budgeted for future work).
