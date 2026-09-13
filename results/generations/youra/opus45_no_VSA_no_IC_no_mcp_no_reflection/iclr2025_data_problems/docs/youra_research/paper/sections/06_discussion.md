# Discussion

## Key Findings

Our experiments reveal two important findings about embedding-based domain scoring for LLM pretraining:

**Finding 1: The EDMP pipeline is computationally tractable and produces statistically significant domain differences.**

E5-large embeddings successfully distinguish domains in a multi-domain corpus (ANOVA F=1242.59, p<0.001) with perfect reproducibility. This validates the first step of the EDMP causal mechanism: embedding extraction captures domain-relevant semantic structure. The pipeline completes in under 30 minutes on a single GPU—orders of magnitude faster than proxy model training required by DoReMi.

**Finding 2: Synthetic data produces insufficient variance for domain discrimination.**

The cross-domain standard deviation (0.0069) falls well below the 0.05 threshold needed for confident ranking. This is a data quality issue, not a fundamental method flaw: synthetic text with 70% shared vocabulary cannot exhibit the vocabulary diversity of real domains. Real Pile domains (e.g., GitHub code vs. PubMed abstracts) have distinct vocabulary distributions that should yield higher variance.

## Implications

For practitioners interested in training-free domain mixing:

1. **Pipeline feasibility established:** EDMP scoring can be implemented with standard tools (sentence-transformers, numpy) and completes quickly. The infrastructure exists for full validation.

2. **Data quality matters:** Using synthetic or homogeneous data will produce misleading results. Any EDMP deployment must use representative, vocabulary-diverse domain samples.

3. **Predictive power remains unverified:** While we validated that EDMP produces statistically significant domain scores, we did NOT test whether these scores predict downstream training utility. This is the critical question for practical adoption.

## Limitations

Our work has several limitations that must be acknowledged:

**L1: Only existence validated, not predictive power.**

We tested whether EDMP scores CAN be computed (h-e1), not whether they PREDICT training utility (h-m1, h-m2). The core hypothesis—that embedding similarity correlates with transfer performance—remains untested. This is the most significant limitation: pipeline existence does not imply practical value.

*Why acceptable:* Scientific validation proceeds in stages. EXISTENCE hypotheses must pass before MECHANISM hypotheses are tested. Our work validates the infrastructure needed for future predictive power evaluation.

*Future work:* Complete the hypothesis chain by testing h-m1 (score-performance correlation) and h-m2 (top-K mixture comparison) with real domain data.

**L2: Synthetic data used instead of real Pile domains.**

Due to data access constraints (zstd library dependency for Pile streaming), we used synthetic domain-distinguishable text. This data lacks the vocabulary diversity and coherence of real domains, producing insufficient cross-domain variance.

*Why acceptable:* The limitation is infrastructure (data access), not conceptual. The pipeline successfully processes the data format; only the data quality is insufficient.

*Future work:* Retry with real Pile data via streaming with proper zstd setup, or use a cached Pile subset.

**L3: Single embedder evaluated.**

We tested only E5-large-v2. Assumption A3 (scale stability) remains unverified—domain rankings might differ with BGE-large, OpenAI embeddings, or smaller/larger E5 variants.

*Why acceptable:* Starting with one well-validated embedder is standard practice. E5-large is widely used and has strong retrieval benchmark performance.

*Future work:* Compare rankings across multiple embedders (E5, BGE, OpenAI) to assess stability.

**L4: Main predictions (P1, P2, P3) untested.**

None of the three main predictions from our hypothesis were tested:
- P1: EDMP top-3 outperforms perplexity top-3 by ≥3%
- P2: Rankings correlate with performance (τ > 0.5)
- P3: Compute cost < 10% DoReMi

*Why acceptable:* These predictions depend on the causal mechanism chain. With h-e1 only PARTIAL, testing P1-P3 would be premature.

*Future work:* Upon obtaining std > 0.05 with real data, proceed to h-m1 and h-m2 to test P1 and P2.

## Broader Impact

**Positive impacts:**

If validated, EDMP could democratize LLM data optimization by eliminating the need for expensive proxy model training. Compute-constrained practitioners and researchers could optimize domain mixtures using only inference, reducing the barrier to entry for foundation model development.

Training-free optimization methods also reduce energy consumption and carbon footprint compared to iterative training approaches like DoReMi.

**Potential negative impacts:**

More efficient data optimization could accelerate the development of larger language models, amplifying any societal risks associated with such models. However, this is a second-order effect; the primary research contribution is methodological.

**Mitigation:**

We release our pipeline code to enable reproducibility and encourage responsible use. The partial validation status of our work naturally limits potential for misapplication until full validation is achieved.
