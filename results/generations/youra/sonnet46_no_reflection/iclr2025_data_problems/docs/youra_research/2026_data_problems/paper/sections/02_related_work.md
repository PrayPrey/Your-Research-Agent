# 2. Related Work

## 2.1 Contamination Detection Methods

Contamination detection for FM evaluation benchmarks has evolved through three distinct paradigms, each operating on a different signal type.

**N-gram overlap detection.** The earliest systematic approach, introduced by Brown et al. [2020] in GPT-3's Appendix C, uses 13-gram exact match between benchmark items and training corpora to flag contaminated examples. EleutherAI's lm-evaluation-harness [Gao et al., 2021] productionized this pipeline with an inverted index over sorted n-gram files. N-gram methods are highly interpretable and fast, but detect only verbatim or near-verbatim contamination — paraphrased or semantically similar items evade detection entirely [Yang et al., 2023].

**Embedding similarity detection.** Yang et al. [2023] demonstrated that LLMs memorize rephrased benchmark content not captured by n-gram methods: 8–18% of HumanEval problems appear in RedPajama and StarCoder corpora in paraphrased form. Their LLM-decontaminator uses embedding similarity to identify such cases. LLMSanitize [Singh et al., 2024b] provides a multi-method library integrating string-matching and embedding-based detection. However, embedding methods require a meaningful similarity distribution over the corpus — an assumption we show is violated under random corpus sampling.

**Membership inference attacks (MIAs).** Shi et al. [2023] introduced Min-K% Prob, which identifies training members as sequences whose minimum-k% token log-probabilities are high, without requiring corpus access. Zhang et al. [2024a] improved this with Min-K%++, an ICLR 2025 Spotlight that replaces the heuristic with a theoretically motivated conditional categorical distribution mode criterion, achieving 6.2–10.5% AUROC improvement on WikiMIA. Zhang et al. [2024b] proposed DC-PDD, a divergence-calibrated method that outperforms Min-K% Prob by computing cross-entropy divergence from a randomness reference. Fu et al. [2024], reviewing 50 papers on MIA-based detection, show that MIA methods can perform at random guessing when their modeling assumptions are violated — a finding our implementation audit confirms concretely.

## 2.2 Meta-Studies Showing Detector Inconsistency

Several studies have documented that contamination detectors give inconsistent signals, motivating a routing framework.

Singh et al. [2024a] (ConTAM) evaluated 13 benchmarks across 7 models and found that different contamination metrics give inconsistent signals. Importantly, they identify the longest contaminated substring as the most informative metric, but do not explain why different metrics disagree or when each should be trusted. Dekoninck et al. [2024] (ConStat) reframe contamination as non-generalizing performance: a model is contaminated if it performs significantly better on seen examples than held-out versions of the same task. This performance-based approach avoids the inconsistency problem but requires access to held-out partitions not available for all benchmarks. Fu et al. [2024] survey 50 papers and identify 8 MIA assumption categories that, when violated, cause near-random detection performance. Xu et al. [2024], in a comprehensive survey of benchmark data contamination, identify the lack of a unified comparison framework as an open problem.

The key limitation across all these works is that they document inconsistency without providing a principled framework for when each detector should be used. Our work addresses this by proposing geometry-based routing — and by identifying the methodological prerequisite that previous work missed.

## 2.3 Benchmark Contamination Audits

Several papers have measured contamination in specific benchmarks. Deng et al. [2023] found that GPT-4 achieves 57% exact match on masked MMLU options, indicating memorization. Yang et al. [2023] showed 8–18% of HumanEval appears in RedPajama and StarCoder in paraphrased form. Hidayat et al. [2025] conducted controlled leakage simulations on MMLU and HellaSwag, finding that n-gram detection achieves the highest F1 under controlled contamination. Our finding that MMLU achieves n-gram recall = 1.0 across The Pile, C4, and FineWeb at 50K-doc sampling extends these results and provides the first cross-corpus confirmation using three independent corpora simultaneously.

## 2.4 Geometry-Based and Routing Approaches

No prior work has proposed a geometry-based routing system for contamination detection. The closest precursor is the ConTAM observation that detector disagreement is informative [Singh et al., 2024a], but ConTAM does not use corpus-side geometric signals to explain or predict that disagreement. The three-zone phase diagram we propose is, to our knowledge, the first attempt to use (13-gram count, SBERT cosine) as a routing signal for contamination detector selection.

**Positioning.** Our work does not replace any existing detector — it proposes a meta-level routing layer that selects among them. Our main contribution is not the routing result (which we do not reach, due to stratum collapse) but the identification of the boundary condition that must be satisfied before routing is possible.
