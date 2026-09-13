# 6. Discussion

## 6.1 Key Findings and Their Implications

**The stratum collapse boundary condition.** Our central finding is that geometry-based contamination routing requires top-k nearest-neighbor corpus retrieval as a hard prerequisite. This is not an optimization — it is a binary condition. Under random streaming, SBERT cosine similarity distributions are degenerate at scale, and the stratum formation mechanism fails entirely. The theoretical mechanism (Proposition 1, Section 3.2) is straightforward: random corpus documents are semantically unrelated to specific benchmark items by definition, so their cosine similarities converge to the base rate of random document pairs.

The implication for the contamination detection community is concrete: any system that computes embedding-based similarity features against randomly-sampled corpus subsets is likely producing degenerate scores at production scale. Prior work using random subsampling for embedding similarity (e.g., LLMSanitize at small scale, manual audits using document samples) may not generalize to full-corpus evaluation because the score distributions change qualitatively, not just quantitatively, as corpus size grows.

**MMLU and GSM8K are at opposite extremes.** The finding that MMLU achieves n-gram recall = 1.0 and GSM8K achieves 0.0 against the same corpora at the same scale is more than a curiosity. It reveals that benchmark heterogeneity — specifically, the difference between factual NLU content and symbolic math reasoning — creates structurally different corpus overlap profiles. A contamination detection framework that treats all benchmarks uniformly will systematically misclassify one type or the other. The three-zone phase diagram, if correctly implemented, would naturally handle this heterogeneity: MMLU items would land in the lexical stratum (routing to n-gram detection), GSM8K items would need domain-specific corpora for any detection to work at all.

**The null hypothesis has not been confirmed.** The h-e1 MUST_WORK gate failed due to experimental design and implementation failures — not because the routing hypothesis was tested and found false. The theoretical causal chain (detector families operate on orthogonal signal types whose efficacy is structurally determined by corpus overlap geometry) is consistent with the literature [Fu et al., 2024; Singh et al., 2024a] and has not been contradicted. Confidence in the main hypothesis (H-GeomRoute-v1) was revised from 0.78 to 0.62, reflecting the severity of the design flaws and the number of implementation bugs, not falsifying evidence.

## 6.2 Limitations

**L1: Stratum collapse invalidates primary and tertiary predictions.** The routing accuracy (P1: top-1 accuracy > 40%) and indeterminacy rate (P3: [10%, 50%]) were never measured because the semantic and indeterminate strata were empty. These are the most important predictions of the hypothesis, and our results provide no evidence for or against them.

**L2: Implementation bugs compromise MIA detector results.** The DCPDDDetector bug (−ref_log_prob instead of log P_target − log P_ref) produces all-positive outputs, making Min-K%++ F1 variance unmeasurable (variance = 0.000 reflects the bug, not true detector behavior). The ConStatDetector bug similarly makes ConStat outputs non-standard. Four of five detector families produce unreliable outputs in the current implementation.

**L3: Corpus coverage is a lower bound.** We index 50K documents per corpus — less than 6% of The Pile by document count (~800M total docs). All recall figures should be interpreted as lower bounds on true corpus overlap. GSM8K's zero recall may reflect sampling artifact rather than true absence of math content in the corpora; testing with domain-specific corpora (OpenWebMath, Proof-Pile) is needed.

**L4: FineWeb substituted for RedPajama.** FineWeb (Common Crawl with deduplication) was used in place of RedPajama-Data-1T. Both are general web-crawl corpora, but they have different deduplication strategies and content distributions. Cross-corpus generalization claims in downstream experiments should be re-evaluated with the originally-designed RedPajama corpus.

**L5: Single Coder-Validator cycle.** The pipeline allows up to 5 Coder-Validator cycles for iterative bug fixing. With only 1 cycle completed, the 4 advisory bugs flagged by the validator were not resolved. A full 5-cycle run would likely have fixed B3 (DC-PDD log-ratio) and B4 (ConStat API), substantially changing the detector output quality.

## 6.3 Broader Impact

This work has implications beyond the specific routing hypothesis. By documenting the stratum collapse failure mode and its root cause, we provide a concrete checklist for future implementations of geometry-based contamination detection:

1. Always compute semantic geometry features using top-k nearest-neighbor retrieval, not random sampling.
2. Validate that cosine similarity distributions are non-degenerate before applying threshold-based stratification.
3. Test at multiple corpus scales: dry-run results may show spurious stratification that collapses at full scale.
4. Use benchmark-type-specific contamination criteria: NLU and math benchmarks require different approaches.
5. When using DC-PDD, implement the full two-model log-likelihood ratio — single-model proxies are not equivalent.

These guidelines apply to any future system that uses corpus-side embedding similarity for contamination characterization, not just the three-zone phase diagram framework.

The broader societal impact of accurate contamination detection is positive: it makes FM evaluation more reliable, reduces inflation of apparent capabilities, and helps practitioners make better-informed decisions about model deployment. No negative societal impacts are anticipated from this work's methodology or findings.
