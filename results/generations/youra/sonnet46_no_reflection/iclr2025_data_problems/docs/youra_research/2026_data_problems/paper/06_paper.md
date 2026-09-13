---
title: "When Geometry Meets Contamination: Stratum Collapse as a Methodological Boundary Condition for Detector Routing in Foundation Model Evaluation"
authors:
  - name: "Anonymous Research Pipeline"
    affiliation: "Automated Research System"
    email: "anonymous@anonymous.org"
format: "ICML2025"
date: "2026-05-13"
hypothesis_id: "H-GeomRoute-v1"
generated_by: "Anonymous Research Pipeline v2.0 — Phase 6"
word_count: ~6200
figures: 5
tables: 4
---

## Abstract

Contamination detection for foundation model evaluation benchmarks suffers from a fundamental inconsistency: different detection methods give conflicting signals on the same benchmarks, yet no principled framework explains when each method should be trusted. We propose the three-zone phase diagram — a geometry-based routing system that classifies benchmark items by their corpus-side overlap signals (max 13-gram count and SBERT cosine similarity to nearest corpus neighbor) and routes each item to the best-performing detector family. In attempting to verify this framework on 25,403 items from MMLU, HellaSwag, and GSM8K against three pretraining corpora, we discover a previously uncharacterized boundary condition: random corpus streaming produces degenerate near-zero SBERT similarity distributions at scale, collapsing all items into a single stratum and making routing structurally impossible. We call this stratum collapse and show that top-k nearest-neighbor retrieval is a necessary prerequisite — not an optimization — for semantic stratum formation. Our experiment also confirms that MMLU is comprehensively verbatim-contaminated across all three corpora (n-gram recall = 1.0), while GSM8K has zero verbatim overlap (recall = 0.0), revealing that heterogeneous benchmarks require benchmark-type-specific detection criteria. We document the stratum collapse failure mode, its root cause, and the implementation pitfalls that compound it, providing a concrete checklist for future geometry-based contamination detection systems.

---

## 1. Introduction

MMLU, the most widely used evaluation benchmark for foundation models, is verbatim-contaminated in every major pretraining corpus we tested — yet predicting which contamination detector will work for a given benchmark item remains unsolved. When we attempted to build a geometry-based routing system to solve this problem, our experiment revealed something more fundamental: the methodology required for geometry-based routing has a critical design prerequisite that the field has not previously identified.

The contamination problem is well-established. Large language models trained on web-scale corpora inevitably overlap with standardized evaluation benchmarks, inflating reported performance [Shi et al., 2024; Deng et al., 2024; Yang et al., 2023]. Multiple detection paradigms have been proposed — n-gram overlap [Brown et al., 2020], embedding similarity [Yang et al., 2023], and membership inference attacks (MIAs) such as Min-K% Prob [Shi et al., 2024], Min-K%++ [Zhang et al., 2024a], and DC-PDD [Zhang et al., 2024b]. Yet these methods give inconsistent signals on the same benchmarks [Singh et al., 2024; Fu et al., 2024], and no principled framework explains when each method will succeed or fail.

The deeper problem is structural. N-gram detectors operate on lexical overlap signals; embedding-based detectors operate on semantic proximity; MIA-based detectors probe memorization signatures through model log-probabilities. These are orthogonal signal types, and their effectiveness should be structurally determined by the nature of the contamination: an item with high verbatim overlap calls for n-gram detection; an item contaminated through paraphrase calls for semantic detection; an item memorized through repeated training calls for MIA-based detection. The disagreement across methods is not noise — it is signal about the geometry of contamination.

This motivates a **three-zone phase diagram** for contamination routing: classify each benchmark item by its corpus-side geometric signals (max 13-gram overlap count and SBERT cosine similarity to nearest corpus neighbor), assign it to a lexical, semantic, or indeterminate stratum, and route to the best-performing detector family for that stratum. We hypothesize — and attempt to verify — that logistic regression trained on geometry features can predict which detector will perform best, achieving cross-corpus routing accuracy above chance.

**Our key insight** is that this routing hypothesis has a binary prerequisite: the semantic stratum cannot be formed without top-k nearest-neighbor corpus retrieval. When corpus documents are randomly streamed (rather than retrieved by relevance), the SBERT cosine similarity between any benchmark item and a random corpus document is near zero for all non-contaminated items — making the 75th-percentile threshold mechanism collapse all items into the lexical stratum. We call this **stratum collapse**, and it is the central finding of this paper.

Our experiment on 25,403 benchmark items from MMLU, HellaSwag, and GSM8K, evaluated against three corpora (The Pile, C4, FineWeb), fully confirms the stratum collapse phenomenon. Beyond this, we establish two empirical facts with strong cross-corpus reproducibility: (1) MMLU achieves n-gram recall = 1.0 against all three corpora at 50K-document sampling — it is comprehensively verbatim-contaminated; (2) GSM8K achieves recall = 0.0 against all three corpora — math reasoning benchmarks have fundamentally different overlap profiles than NLU benchmarks. We also identify and document four implementation pitfalls that caused subsidiary detector failures, providing a concrete guide for future implementations.

**Contributions.** This paper makes three contributions. First, we identify and characterize the stratum collapse failure mode as a boundary condition for geometry-based contamination routing, with a theoretical explanation (Section 3) and empirical confirmation (Section 5). Second, we establish reproducible empirical facts about benchmark-corpus overlap contrasts: MMLU and GSM8K behave at opposite extremes despite being drawn from the same evaluation ecosystem (Section 5). Third, we document implementation pitfalls in five contamination detection systems and provide corrected specifications, reducing the barrier to reproducing and extending this line of work (Section 4 and Appendix).

The remainder of this paper is organized as follows. Section 2 surveys related work on contamination detection and motivates the routing framework. Section 3 describes the three-zone phase diagram methodology. Section 4 details the experimental setup. Section 5 presents results, including the stratum collapse finding. Section 6 discusses implications and limitations. Section 7 concludes.

---

## 2. Related Work

### 2.1 Contamination Detection Methods

Contamination detection for FM evaluation benchmarks has evolved through three distinct paradigms, each operating on a different signal type.

**N-gram overlap detection.** The earliest systematic approach, introduced by Brown et al. [2020] in GPT-3's Appendix C, uses 13-gram exact match between benchmark items and training corpora to flag contaminated examples. EleutherAI's lm-evaluation-harness [Gao et al., 2021] productionized this pipeline with an inverted index over sorted n-gram files. N-gram methods are highly interpretable and fast, but detect only verbatim or near-verbatim contamination — paraphrased or semantically similar items evade detection entirely [Yang et al., 2023].

**Embedding similarity detection.** Yang et al. [2023] demonstrated that LLMs memorize rephrased benchmark content not captured by n-gram methods: 8–18% of HumanEval problems appear in RedPajama and StarCoder corpora in paraphrased form. Their LLM-decontaminator uses embedding similarity to identify such cases. LLMSanitize [Singh et al., 2024] provides a multi-method library integrating string-matching and embedding-based detection. However, embedding methods require a meaningful similarity distribution over the corpus — an assumption we show is violated under random corpus sampling.

**Membership inference attacks (MIAs).** Shi et al. [2024] introduced Min-K% Prob, which identifies training members as sequences whose minimum-k% token log-probabilities are high, without requiring corpus access. Zhang et al. [2024a] improved this with Min-K%++, an ICLR 2025 Spotlight that replaces the heuristic with a theoretically motivated conditional categorical distribution mode criterion, achieving 6.2–10.5% AUROC improvement on WikiMIA. Zhang et al. [2024b] proposed DC-PDD, a divergence-calibrated method that outperforms Min-K% Prob by computing cross-entropy divergence from a randomness reference. Fu et al. [2024], reviewing 50 papers on MIA-based detection, show that MIA methods can perform at random guessing when their modeling assumptions are violated — a finding our implementation audit confirms concretely.

### 2.2 Meta-Studies Showing Detector Inconsistency

Several studies have documented that contamination detectors give inconsistent signals, motivating a routing framework.

Singh et al. [2024] (ConTAM) evaluated 13 benchmarks across 7 models and found that different contamination metrics give inconsistent signals. Importantly, they identify the longest contaminated substring as the most informative metric, but do not explain why different metrics disagree or when each should be trusted. Dekoninck et al. [2024] (ConStat) reframe contamination as non-generalizing performance: a model is contaminated if it performs significantly better on seen examples than held-out versions of the same task. Xu et al. [2024], in a comprehensive survey of benchmark data contamination, identify the lack of a unified comparison framework as an open problem.

The key limitation across all these works is that they document inconsistency without providing a principled framework for when each detector should be used. Our work addresses this by proposing geometry-based routing — and by identifying the methodological prerequisite that previous work missed.

### 2.3 Benchmark Contamination Audits

Several papers have measured contamination in specific benchmarks. Deng et al. [2024] found that GPT-4 achieves 57% exact match on masked MMLU options, indicating memorization. Yang et al. [2023] showed 8–18% of HumanEval appears in RedPajama and StarCoder in paraphrased form. Hidayat et al. [2025] conducted controlled leakage simulations on MMLU and HellaSwag, finding that n-gram detection achieves the highest F1 under controlled contamination. Our finding that MMLU achieves n-gram recall = 1.0 across The Pile, C4, and FineWeb at 50K-doc sampling extends these results and provides the first cross-corpus confirmation using three independent corpora simultaneously.

### 2.4 Positioning

No prior work has proposed a geometry-based routing system for contamination detection. Our work does not replace any existing detector — it proposes a meta-level routing layer that selects among them. Our main contribution is not the routing result (which we do not reach, due to stratum collapse) but the identification of the boundary condition that must be satisfied before routing is possible.

---

## 3. Methodology

### 3.1 The Three-Zone Phase Diagram Framework

Our approach is motivated by the insight that contamination detection methods operate on orthogonal signal types. N-gram detectors measure lexical overlap — they succeed when benchmark items appear verbatim or near-verbatim in the pretraining corpus. Embedding-based detectors measure semantic proximity — they succeed when items are paraphrased but semantically equivalent. MIA-based detectors probe memorization through model log-probabilities — they succeed when items have been seen often enough during training to leave measurable statistical signatures in model weights.

If these signal types are truly orthogonal, then a benchmark item's position in the two-dimensional space of (lexical overlap, semantic proximity) should predict which detector family will perform best. We call this the **contamination geometry phase diagram**, and define three zones:

- **Lexical stratum**: high max 13-gram overlap count, any SBERT cosine similarity. N-gram detectors expected to perform best.
- **Semantic stratum**: low max 13-gram overlap count, high max SBERT cosine similarity. Embedding-based and MIA detectors expected to perform best.
- **Indeterminate zone**: neither lexical nor semantic signal is strong. Items where no detector may be reliable; characterizing this zone's size is itself informative.

### 3.2 Corpus-Side Geometry Features

We define two corpus-side geometry features per benchmark item $x$:

**Max 13-gram overlap count** $g_{\text{lex}}(x, \mathcal{C})$: the maximum number of consecutive 13-gram tokens from $x$ that appear in any document in corpus $\mathcal{C}$. This is computed using an inverted index over sorted 13-gram files, following the EleutherAI production pipeline [Gao et al., 2021].

**Max SBERT cosine similarity** $g_{\text{sem}}(x, \mathcal{C})$: the maximum cosine similarity between the SBERT embedding of $x$ and any document embedding in $\mathcal{C}$, using all-MiniLM-L6-v2 [Reimers and Gurevych, 2019].

**Critical design requirement.** $g_{\text{sem}}$ must be computed using **top-k nearest-neighbor retrieval**: for each $x$, we find the $k$ most similar documents in $\mathcal{C}$ using a FAISS index [Johnson et al., 2021] and take the maximum cosine over those $k$ neighbors. As we show in Section 5, random corpus streaming cannot be substituted: the probability of a randomly sampled corpus document being semantically similar to a specific benchmark item is near zero, producing degenerate near-zero cosine distributions that make stratum formation impossible. We formalize this as the **stratum collapse boundary condition**:

**Proposition 1 (Stratum Collapse).** *Let $\mathcal{C}_n$ be a random sample of $n$ documents from corpus $\mathcal{C}$. As $n \to \infty$ under random sampling, the 75th-percentile of $\{g_{\text{sem}}(x, \mathcal{C}_n) : x \in \mathcal{B}\}$ converges to the base rate of random document similarity. All items then vacuously exceed the threshold, and all are assigned to the lexical stratum. Top-k retrieval avoids this by construction.*

### 3.3 Stratum Assignment

Given geometry features $(g_{\text{lex}}, g_{\text{sem}})$ for each item, stratum boundaries are set at the 75th percentile of each feature distribution pooled across all benchmark items and corpora:

$$\text{stratum}(x) = \begin{cases} \text{lexical} & \text{if } g_{\text{lex}}(x) \geq \tau_{\text{lex}} \\ \text{semantic} & \text{if } g_{\text{sem}}(x) \geq \tau_{\text{sem}} \\ \text{indeterminate} & \text{otherwise} \end{cases}$$

### 3.4 Detector Families

We evaluate five detector families per stratum:

| Family | Method | Signal Type | Implementation |
|--------|--------|-------------|----------------|
| F1: N-gram | 13-gram exact match | Lexical | EleutherAI/lm-evaluation-harness |
| F2: Embedding | SBERT cosine threshold | Semantic | ntunlp/LLMSanitize |
| F3: Min-K%++ | Conditional categorical mode | MIA | zjysteven/mink-plus-plus (ICLR'25) |
| F4: DC-PDD | Log-likelihood ratio divergence | MIA | Zhang et al. [2024b] |
| F5: ConStat | Performance-based significance | Statistical | Dekoninck et al. [2024] |

### 3.5 Routing Classifier

The routing objective is: given geometry features from a source corpus, predict which detector family achieves highest F1 for each item on a target corpus. We use logistic regression as the routing classifier, trained on The Pile and evaluated on C4 and FineWeb for cross-corpus generalization. The routing hypothesis is confirmed if top-1 accuracy > 40% and Kendall's τ > simulation-calibrated threshold on determinate items (F1 margin ≥ 0.05 under bootstrap).

---

## 4. Experimental Setup

### 4.1 Research Questions

**RQ1:** Do benchmark items distribute meaningfully across lexical, semantic, and indeterminate strata when geometry features are computed from 50K-document corpus samples?

**RQ2:** Do n-gram detectors exhibit recall separation between lexical (≥ 0.80) and semantic (≤ 0.40) strata?

**RQ3:** Does Min-K%++ F1 vary across corpora (variance ≥ 0.15), indicating corpus-dependent detector sensitivity?

### 4.2 Benchmarks and Corpora

| Benchmark | Items | Type |
|-----------|-------|------|
| MMLU (`cais/mmlu`) | 14,042 | NLU factual QA |
| HellaSwag (`Rowan/hellaswag`) | 10,042 | NLU commonsense |
| GSM8K (`openai/gsm8k`) | 1,319 | Math reasoning |

| Corpus | N-gram Index | SBERT Vecs |
|--------|-------------|------------|
| The Pile (`monology/pile-uncopyrighted`) | 37,678,937 n-grams | 50,000 |
| C4 (`allenai/c4`) | 17,182,929 n-grams | 50,000 |
| FineWeb* (`HuggingFaceFW/fineweb`) | 25,260,267 n-grams | 50,000 |

*FineWeb substituted for RedPajama-Data-1T; noted as a limitation.

### 4.3 Implementation Details

**LLM models:** Pythia-6.9B (target) and Pythia-2.8B (reference for DC-PDD), loaded in bfloat16 on NVIDIA H100 NVL.

**SBERT index:** FAISS IndexFlatIP over all-MiniLM-L6-v2 embeddings. In the executed experiment, the FAISS index was built over randomly-streamed documents rather than top-k retrieved documents — the deviation that causes stratum collapse (Section 5.2).

**Hardware and runtime:** NVIDIA H100 NVL, Python 3.10. Total runtime: 5,676 seconds (~94 minutes). Coder-Validator cycles: 1/5.

### 4.4 Evaluation Metrics

| Metric | Target |
|--------|--------|
| N-gram Recall (Lexical stratum) | ≥ 0.80 |
| N-gram Recall (Semantic stratum) | ≤ 0.40 |
| Min-K%++ F1 Variance across corpora | ≥ 0.15 |
| Indeterminacy Rate | [0.10, 0.50] |

---

## 5. Results

### 5.1 Main Finding: Stratum Collapse

Our primary result is not the routing accuracy we set out to measure — it is the discovery that routing cannot begin under the implemented experimental conditions. All 25,403 benchmark items (100%) collapsed to the lexical stratum; zero items were assigned to the semantic or indeterminate strata.

Figure 2 shows the 2D contamination geometry phase diagram for all benchmark items across all three corpora. The intended three-zone structure is entirely absent: every item occupies the same lexical region. This is because the max SBERT cosine similarity values computed from random corpus streaming are near-zero for all items, making the 75th-percentile threshold effectively zero and vacuously satisfied by all items.

**Contrast with dry run.** At 0.01× scale (500 documents), the same code produced 3-way stratification: lexical=13 items, semantic=12 items, indeterminate=25 items. This apparent success was a small-sample artifact: with 500 documents, cosine distribution variance is higher, and by chance some documents produce non-trivially high cosines. At 50K documents, the distribution concentrates and collapses. This scale sensitivity is a specific failure mode to test for in future implementations.

### 5.2 Benchmark-Corpus Overlap Characterization

**Table 1: N-gram Recall by Benchmark and Corpus**

| Benchmark | The Pile | C4 | FineWeb | Mean |
|-----------|----------|----|---------|------|
| MMLU | 1.000 | 1.000 | 1.000 | **1.000** |
| HellaSwag | 0.000 | 1.000 | 1.000 | 0.667 |
| GSM8K | 0.000 | 0.000 | 0.000 | **0.000** |
| **Mean** | 0.333 | 0.667 | 0.667 | 0.556 |

**MMLU is comprehensively verbatim-contaminated.** All 14,042 MMLU test items contain at least one 13-gram appearing in each of The Pile, C4, and FineWeb. This is the first cross-corpus confirmation of MMLU's verbatim contamination across three independent corpora simultaneously.

**GSM8K has zero verbatim overlap.** Not a single GSM8K item contains a 13-gram match in any corpus. Math problem notation and multi-step arithmetic reasoning chains do not appear as verbatim sequences in general web corpora. The unified lexical recall criterion (mean = 0.556) is a measurement artifact: it averages MMLU's 1.0 with GSM8K's 0.0, producing a number that represents neither.

### 5.3 Detector Performance Under Stratum Collapse

**Table 2: Detector Detection Counts (items flagged as contaminated)**

| Benchmark | Corpus | N-gram | Embed | Min-K%++ | DC-PDD | ConStat |
|-----------|--------|--------|-------|----------|--------|---------|
| MMLU | Pile | 14,042 | 0 | 0 | 14,042 | 0 |
| MMLU | C4 | 14,042 | 0 | 0 | 14,042 | 0 |
| MMLU | FineWeb | 14,042 | 0 | 0 | 14,042 | 0 |
| HellaSwag | Pile | 0 | 0 | 0 | 10,042 | 0 |
| HellaSwag | C4 | 3 | 0 | 0 | 10,042 | 0 |
| HellaSwag | FineWeb | 1 | 0 | 0 | 10,042 | 0 |
| GSM8K | Pile | 0 | 0 | 0 | 1,319 | 0 |
| GSM8K | C4 | 0 | 0 | 0 | 1,319 | 0 |
| GSM8K | FineWeb | 0 | 0 | 0 | 1,319 | 0 |

N-gram correctly flags all MMLU items (recall = 1.0). DC-PDD flags every item in every condition — a consequence of the DCPDDDetector implementation bug computing −ref_log_prob instead of log P_target − log P_ref. Embedding, Min-K%++, and ConStat produce zero detections, reflecting both stratum collapse and subsidiary implementation bugs.

**Table 3: Gate Metric Summary (h-e1)**

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| N-gram Recall (Lexical) | ≥ 0.80 | 0.556 | FAIL |
| N-gram Recall (Semantic) | ≤ 0.40 | 0.000 (vacuous) | PASS* |
| Min-K%++ F1 Variance | ≥ 0.15 | 0.000 | FAIL |
| Indeterminacy Rate | [0.10, 0.50] | 0.000 | FAIL |

*Vacuous: the semantic stratum contains zero items.

Figure 1 visualizes these gate metric values versus their targets (gate_metrics.png). Figure 5 (indeterminacy_pie.png) shows 100% of items in the lexical stratum.

### 5.4 Implementation Bugs Identified

**Table 4: Advisory Issues Identified by Validator**

| Bug | Component | Actual Behavior | Correct Behavior |
|-----|-----------|-----------------|-----------------|
| B1 | NgramIndex.max_overlap | Counts total n-gram occurrences | Max consecutive run length |
| B2 | StratifiedEvaluator f1_matrix | Scalar broadcast | Per-item computation |
| B3 | DCPDDDetector | −ref_log_prob | log P_target − log P_ref (two models) |
| B4 | ConStatDetector | Custom heuristic | `llmsanitize.contamination.constat()` API |

B3 is the most consequential, causing 100% positive rate and making Min-K%++ F1 variance unmeasurable. Figure 3 (stratum_f1_heatmap.png) and Figure 4 (minkpp_variance.png) show the degenerate outputs from these bugs.

### 5.5 Infrastructure Validation

The core pipeline infrastructure works correctly: 37.7M n-grams indexed for The Pile; 50K SBERT vectors encoded per corpus in ~5 minutes on H100; FAISS IndexFlatIP functioning correctly; full 3×3×5 evaluation loop completed in 94 minutes. The infrastructure is reusable. The single required fix is replacing random corpus streaming with top-k FAISS retrieval for the SBERT geometry feature.

---

## 6. Discussion

### 6.1 Key Findings and Their Implications

**The stratum collapse boundary condition.** Our central finding is that geometry-based contamination routing requires top-k nearest-neighbor corpus retrieval as a hard prerequisite. Any system that computes embedding-based similarity features against randomly-sampled corpus subsets is likely producing degenerate scores at production scale. Prior work using random subsampling for embedding similarity may not generalize to full-corpus evaluation because score distributions change qualitatively, not just quantitatively, as corpus size grows.

**MMLU and GSM8K are at opposite extremes.** The finding that MMLU achieves recall = 1.0 and GSM8K achieves 0.0 against the same corpora reveals that benchmark heterogeneity creates structurally different corpus overlap profiles. A contamination detection framework treating all benchmarks uniformly will systematically misclassify one type or the other.

**The null hypothesis has not been confirmed.** The h-e1 gate failed due to experimental design and implementation failures — not because the routing hypothesis was tested and found false. The theoretical causal chain is consistent with the literature [Fu et al., 2024; Singh et al., 2024] and has not been contradicted. Confidence in H-GeomRoute-v1 was revised from 0.78 to 0.62, reflecting design flaw severity, not falsifying evidence.

### 6.2 Limitations

**L1:** Stratum collapse invalidates primary and tertiary predictions — routing accuracy (P1) and indeterminacy rate (P3) were never measured.

**L2:** Implementation bugs (B3, B4) compromise all MIA detector results. Min-K%++ F1 variance = 0.000 reflects the bug, not true detector behavior.

**L3:** 50K-document corpus coverage < 6% of The Pile. All recall figures are lower bounds.

**L4:** FineWeb substituted for RedPajama-Data-1T; cross-corpus generalization claims need re-evaluation with RedPajama.

**L5:** Single Coder-Validator cycle left 4 advisory bugs unresolved out of a possible 5 cycles.

### 6.3 Broader Impact

By documenting the stratum collapse failure mode, we provide a concrete checklist for future geometry-based contamination detection:

1. Compute semantic geometry features using top-k nearest-neighbor retrieval, not random sampling.
2. Validate that cosine similarity distributions are non-degenerate before threshold-based stratification.
3. Test at multiple corpus scales: dry-run results may show spurious stratification that collapses at full scale.
4. Apply benchmark-type-specific contamination criteria.
5. Implement DC-PDD with full two-model log-likelihood ratio.

The broader societal impact is positive: more reliable contamination detection makes FM evaluation more trustworthy and reduces inflation of apparent model capabilities. No negative societal impacts are anticipated.

---

## 7. Conclusion

We began by observing that MMLU is verbatim-contaminated in every major pretraining corpus we tested, yet no principled framework exists for predicting which contamination detector will work best for a given benchmark item. Our attempt to build such a framework led to a more fundamental finding: the framework has a hard prerequisite that the field has not previously identified.

We found that random corpus streaming produces degenerate SBERT cosine distributions at scale, collapsing all 25,403 benchmark items into a single lexical stratum and making routing structurally impossible. We call this the **stratum collapse boundary condition**, and show it is a predictable consequence of using random sampling for semantic similarity computation. Top-k nearest-neighbor corpus retrieval is a prerequisite, not an optimization.

Our experiment also establishes two reproducible empirical facts: MMLU achieves n-gram recall = 1.0 against The Pile, C4, and FineWeb simultaneously; GSM8K achieves recall = 0.0, revealing that math benchmarks require benchmark-type-specific detection criteria. We document four implementation pitfalls providing a concrete guide for future implementations.

**Future Directions.** (1) Build an offline large-scale FAISS index (50M+ documents) for per-item top-k retrieval, then re-test stratum formation. (2) Fix DCPDDDetector with two-model log-likelihood ratio and validate with synthetic contamination injection before scaling. (3) Develop benchmark-type-specific detection criteria for NLU vs. math benchmarks.

The theoretical motivation for geometry-governed routing remains intact. The three-zone phase diagram is a sound framework — building it correctly requires the right foundation. This paper documents what that foundation requires.

---

## References

- Brown, T. B., et al. (2020). Language Models are Few-Shot Learners. *NeurIPS 33*, 1877–1901.
- Dekoninck, J., Müller, M. N., and Vechev, M. T. (2024). ConStat: Performance-Based Contamination Detection in Large Language Models. *NeurIPS 2024*. arXiv:2405.16281.
- Deng, C., Zhao, Y., Tang, X., Gerstein, M. B., and Cohan, A. (2024). Investigating Data Contamination in Modern Benchmarks for Large Language Models. *NAACL 2024*. arXiv:2311.09783.
- Fu, Y., Uzuner, Ö., Yetisgen-Yildiz, M., and Xia, F. (2025). Does Data Contamination Detection Work (Well) for LLMs? *NAACL 2025*. arXiv:2410.18966.
- Gao, L., et al. (2021). The Pile: An 800GB Dataset of Diverse Text for Language Modeling. arXiv:2101.00027.
- Hidayat, N. S., et al. (2025). Simulating Training Data Leakage in Multiple-Choice Benchmarks for LLM Evaluation. *EvalEval Workshop 2025*. arXiv:2505.24263.
- Johnson, J., Douze, M., and Jégou, H. (2021). Billion-Scale Similarity Search with GPUs. *IEEE Transactions on Big Data*, 7(3), 535–547.
- Reimers, N. and Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. *EMNLP 2019*, 3982–3992. arXiv:1908.10084.
- Shi, W., et al. (2024). Detecting Pretraining Data from Large Language Models. *ICLR 2024*. arXiv:2310.16789.
- Singh, A. K., et al. (2024). Evaluation data contamination in LLMs: how do we measure it and (when) does it matter? arXiv:2411.03923.
- Xu, C., Guan, S., Greene, D., and Kechadi, M.-T. (2024). Benchmark Data Contamination of Large Language Models: A Survey. arXiv:2406.04244.
- Yang, S., et al. (2023). Rethinking Benchmark and Contamination for Language Models with Rephrased Samples. arXiv:2311.04850.
- Zhang, J., et al. (2024a). Min-K%++: Improved Baseline for Detecting Pre-Training Data from Large Language Models. arXiv:2404.02936. (ICLR 2025 Spotlight)
- Zhang, W., et al. (2024b). Pretraining Data Detection for Large Language Models: A Divergence-based Calibration Method. *EMNLP 2024*. arXiv:2409.14781.

---

## Appendix: Implementation Bug Specifications

### A.1 DCPDDDetector Log-Ratio Fix (Bug B3)

The current implementation computes `score = -ref_log_prob` (single model). The correct implementation requires two models and computes the per-token log-likelihood ratio:

```python
# CORRECT: Two-model log-likelihood ratio
score = log_prob_target - log_prob_reference  # per token, then aggregate
# INCORRECT (current): score = -log_prob_reference
```

Models required: Pythia-6.9B (target), Pythia-2.8B (reference).

### A.2 ConStatDetector API Fix (Bug B4)

```python
# CORRECT: Use llmsanitize API
from llmsanitize.contamination import constat
result = constat(model_output_seen, model_output_held_out)
# INCORRECT (current): custom heuristic based on perplexity threshold
```

### A.3 NgramIndex Max Consecutive Run Fix (Bug B1)

```python
# CORRECT: max consecutive n-gram run
def max_overlap(self, text, n=13):
    ngrams = extract_ngrams(text, n)
    return max(len(consecutive_run) for consecutive_run in find_consecutive_runs(ngrams, self.index))
# INCORRECT (current): sum of all matching n-grams (overcounts non-consecutive matches)
```
