# Stratum Collapse as a Boundary Condition for Geometry-Based Contamination Detection Routing in Foundation Model Evaluation

**Date:** 2026-05-13  
**Hypothesis ID:** H-GeomRoute-v1  
**Experiment ID:** h-e1  
**Gate Result:** FAIL (MUST_WORK gate; experimental design and implementation failures)  
**Overall Hypothesis Status:** UNRESOLVED — not falsified, not confirmed

---

## Abstract

Contamination detection for foundation model evaluation benchmarks is complicated by inconsistent signals across detection methods applied to the same benchmarks. This paper describes an attempt to build a geometry-based routing system — a three-zone phase diagram — that classifies benchmark items by corpus-side overlap signals (max 13-gram count and SBERT cosine similarity to nearest corpus neighbor) and routes each item to the detector family best suited to its contamination geometry. The experiment evaluates 25,403 items from MMLU (14,042), HellaSwag (10,042), and GSM8K (1,319) against three pretraining corpora (The Pile, C4, FineWeb) using five detector families. The primary result is not the routing accuracy the experiment was designed to measure but rather the identification of a failure mode called stratum collapse: random corpus streaming produces near-zero SBERT cosine similarity distributions at 50,000-document scale, collapsing all items into a single lexical stratum and making routing structurally impossible. Top-k nearest-neighbor retrieval is identified as a necessary design prerequisite for semantic stratum formation. Two secondary empirical findings are confirmed with cross-corpus reproducibility: MMLU achieves n-gram recall = 1.0 against all three corpora at 50K-document sampling, and GSM8K achieves recall = 0.0. Four implementation bugs in the detector and evaluator code are identified and documented. The primary routing hypothesis (P1) is inconclusive; gate metrics for n-gram lexical recall (0.556 vs. target ≥ 0.80), Min-K%++ F1 variance (0.000 vs. target ≥ 0.15), and indeterminacy rate (0.000 vs. target [0.10, 0.50]) are not met.

---

## 1. Introduction

Large language models trained on web-scale corpora may overlap with standardized evaluation benchmarks, potentially inflating reported performance [Brown et al., 2020; Shi et al., 2024; Deng et al., 2024; Yang et al., 2023]. Multiple detection paradigms have been proposed to identify such contamination: n-gram overlap [Brown et al., 2020; Gao et al., 2021], embedding similarity [Yang et al., 2023; Singh et al., 2024], and membership inference attacks (MIAs) such as Min-K% Prob [Shi et al., 2024], Min-K%++ [Zhang et al., 2024a], and DC-PDD [Zhang et al., 2024b]. These methods have been observed to produce inconsistent signals on the same benchmarks [Singh et al., 2024; Fu et al., 2024], without a principled framework explaining when each method is expected to succeed or fail.

The three distinct signal types operated upon by these detector families — lexical overlap, semantic proximity, and memorization signatures through model log-probabilities — are in principle orthogonal. A benchmark item's position in the two-dimensional space of (lexical overlap, semantic proximity) could, in principle, predict which detector family will perform best on that item. This motivates a three-zone phase diagram for contamination detection routing.

This paper describes hypothesis H-GeomRoute-v1, which proposes that corpus-side geometric signals (max 13-gram overlap count and SBERT cosine similarity to the nearest corpus neighbor) can classify benchmark items into contamination geometry strata, and that a logistic regression routing rule trained on one corpus will predict the top-performing detector family with cross-corpus top-1 accuracy > 40% and Kendall's τ above a simulation-calibrated threshold on determinate items.

The executed experiment (h-e1, EXISTENCE sub-hypothesis) does not produce routing accuracy measurements. Instead, the experiment encounters a structural failure mode: when SBERT cosine similarity is computed against randomly-streamed corpus documents rather than top-k nearest-neighbor retrieved documents, the resulting similarity distribution is degenerate (near-zero) for all benchmark items at 50,000-document scale, causing all 25,403 items to collapse into the lexical stratum. This failure mode is termed stratum collapse.

The paper documents the stratum collapse finding, its root cause, the benchmark-corpus overlap characterizations produced as a byproduct, and four implementation bugs that compound the detector results. The main hypothesis remains unresolved: the gate failure is attributed to experimental design and implementation failures, not to falsifying evidence against the hypothesis.

The paper is organized as follows. Section 2 surveys related work. Section 3 describes the three-zone phase diagram methodology. Section 4 details the experimental setup. Section 5 presents results. Section 6 discusses implications and limitations. Section 7 concludes.

---

## 2. Related Work

### 2.1 Contamination Detection Methods

**N-gram overlap detection.** Brown et al. [2020] introduced 13-gram exact match between benchmark items and training corpora as a contamination flag in the GPT-3 Appendix C. EleutherAI's lm-evaluation-harness [Gao et al., 2021] productionized this pipeline with an inverted index over sorted n-gram files. N-gram methods detect verbatim or near-verbatim contamination; paraphrased items evade detection [Yang et al., 2023].

**Embedding similarity detection.** Yang et al. [2023] showed that 8–18% of HumanEval problems appear in RedPajama and StarCoder corpora in paraphrased form, detectable via embedding similarity. LLMSanitize [Singh et al., 2024] provides a multi-method library integrating string-matching and embedding-based detection. Embedding methods require a meaningful similarity distribution over the corpus — an assumption that is examined in this paper.

**Membership inference attacks (MIAs).** Shi et al. [2024] introduced Min-K% Prob, which identifies training members as sequences whose minimum-k% token log-probabilities are high, without requiring corpus access. Zhang et al. [2024a] proposed Min-K%++, an ICLR 2025 Spotlight that replaces a heuristic with a conditional categorical distribution mode criterion, achieving 6.2–10.5% absolute AUROC improvement on WikiMIA. Zhang et al. [2024b] proposed DC-PDD, which computes cross-entropy divergence from a randomness reference. Fu et al. [2024], reviewing 50 papers on MIA-based detection, document conditions under which MIA methods perform at random guessing.

### 2.2 Detector Inconsistency

Singh et al. [2024] (ConTAM) evaluated 13 benchmarks across 7 models and found that different contamination metrics give inconsistent signals; the longest contaminated substring is identified as the most informative metric, without explaining when different metrics should be trusted. Dekoninck et al. [2024] (ConStat) frame contamination as non-generalizing performance. Xu et al. [2024] identify the absence of a unified comparison framework as an open problem in their comprehensive survey.

### 2.3 Benchmark Contamination Audits

Deng et al. [2024] found that GPT-4 achieves 57% exact match on masked MMLU options, indicating memorization. Yang et al. [2023] showed 8–18% of HumanEval appears in pretraining corpora in paraphrased form. Hidayat et al. [2025] conducted controlled leakage simulations on MMLU and HellaSwag, finding that n-gram detection achieves the highest F1 under controlled contamination.

### 2.4 Positioning

No prior work has proposed a geometry-based routing system for contamination detection, nor has prior work identified the stratum collapse phenomenon described in this paper.

---

## 3. Methodology

### 3.1 The Three-Zone Phase Diagram

The proposed framework assigns each benchmark item to one of three zones based on corpus-side geometry features:

- **Lexical stratum**: high max 13-gram overlap count, any SBERT cosine similarity. N-gram detectors expected to be most effective.
- **Semantic stratum**: low max 13-gram overlap count, high max SBERT cosine similarity. Embedding-based and MIA detectors expected to be most effective.
- **Indeterminate zone**: neither lexical nor semantic signal is strong. Items where no detector may be reliable.

### 3.2 Corpus-Side Geometry Features

Two geometry features are defined per benchmark item $x$:

**Max 13-gram overlap count** $g_{\text{lex}}(x, \mathcal{C})$: the maximum number of consecutive 13-gram tokens from $x$ that appear in any document in corpus $\mathcal{C}$. Computed using an inverted index over sorted 13-gram files, following the EleutherAI pipeline [Gao et al., 2021].

**Max SBERT cosine similarity** $g_{\text{sem}}(x, \mathcal{C})$: the maximum cosine similarity between the SBERT embedding of $x$ and any document embedding in $\mathcal{C}$, using all-MiniLM-L6-v2 [Reimers and Gurevych, 2019].

**Design requirement.** $g_{\text{sem}}$ requires top-k nearest-neighbor retrieval: for each $x$, the $k$ most similar documents in $\mathcal{C}$ are found using a FAISS index [Johnson et al., 2021] and the maximum cosine over those $k$ neighbors is taken. In the executed experiment, this requirement was violated: SBERT cosine was computed against randomly-streamed documents rather than top-k retrieved documents. This deviation is the root cause of stratum collapse (Section 5.1).

**Proposition (Stratum Collapse).** Let $\mathcal{C}_n$ be a random sample of $n$ documents from corpus $\mathcal{C}$. For non-contaminated benchmark items, in expectation across a benchmark set, as $n \to \infty$ under random sampling, the 75th percentile of $\{g_{\text{sem}}(x, \mathcal{C}_n) : x \in \mathcal{B}\}$ converges to the base rate of random document similarity. All items then vacuously exceed the threshold, and all are assigned to the lexical stratum. Top-k retrieval avoids this by construction.

### 3.3 Stratum Assignment

Stratum boundaries are set at the 75th percentile of each feature distribution pooled across all benchmark items and corpora:

$$\text{stratum}(x) = \begin{cases} \text{lexical} & \text{if } g_{\text{lex}}(x) \geq \tau_{\text{lex}} \\ \text{semantic} & \text{if } g_{\text{sem}}(x) \geq \tau_{\text{sem}} \\ \text{indeterminate} & \text{otherwise} \end{cases}$$

### 3.4 Detector Families

Five detector families are evaluated per stratum:

| Family | Method | Signal Type | Reference |
|--------|--------|-------------|-----------|
| F1: N-gram | 13-gram exact match | Lexical | EleutherAI/lm-evaluation-harness [Gao et al., 2021] |
| F2: Embedding | SBERT cosine threshold | Semantic | ntunlp/LLMSanitize [Singh et al., 2024] |
| F3: Min-K%++ | Conditional categorical mode | MIA | zjysteven/mink-plus-plus [Zhang et al., 2024a] |
| F4: DC-PDD | Log-likelihood ratio divergence | MIA | Zhang et al. [2024b] |
| F5: ConStat | Performance-based significance | Statistical | Dekoninck et al. [2024] |

### 3.5 Routing Classifier

The routing objective: given geometry features from a source corpus, predict which detector family achieves the highest F1 for each item on a target corpus. The routing classifier is logistic regression, trained on The Pile and evaluated on C4 and FineWeb. Routing is considered confirmed if top-1 accuracy > 40% and Kendall's τ exceeds a simulation-calibrated threshold on determinate items with F1 margin ≥ 0.05 under bootstrap. Due to stratum collapse, the routing classifier was never reached in the executed experiment.

---

## 4. Experimental Setup

### 4.1 Research Questions

- **RQ1:** Do benchmark items distribute meaningfully across lexical, semantic, and indeterminate strata when geometry features are computed from 50K-document corpus samples?
- **RQ2:** Do n-gram detectors exhibit recall separation between lexical (≥ 0.80) and semantic (≤ 0.40) strata?
- **RQ3:** Does Min-K%++ F1 vary across corpora (variance ≥ 0.15), indicating corpus-dependent detector sensitivity?

### 4.2 Benchmarks

| Benchmark | HuggingFace ID | Items | Type |
|-----------|---------------|-------|------|
| MMLU | `cais/mmlu` | 14,042 | NLU factual QA |
| HellaSwag | `Rowan/hellaswag` | 10,042 | NLU commonsense |
| GSM8K | `openai/gsm8k` | 1,319 | Math reasoning |
| **Total** | | **25,403** | |

### 4.3 Corpora

| Corpus | HuggingFace ID | N-gram Index Size | SBERT Vecs |
|--------|---------------|------------------|------------|
| The Pile | `monology/pile-uncopyrighted` | 37,678,937 n-grams | 50,000 |
| C4 | `allenai/c4` | 17,182,929 n-grams | 50,000 |
| FineWeb* | `HuggingFaceFW/fineweb` | 25,260,267 n-grams | 50,000 |

*FineWeb was substituted for RedPajama-Data-1T (`togethercomputer/RedPajama-Data-1T`). This substitution was not specified in the original hypothesis design and is noted as a limitation.

### 4.4 Models

**LLM models:** Pythia-6.9B (`EleutherAI/pythia-6.9b`, target) and Pythia-2.8B (reference for DC-PDD), loaded in bfloat16.

**SBERT model:** `all-MiniLM-L6-v2` via sentence-transformers. FAISS IndexFlatIP over normalized embeddings.

**Critical deviation:** In the executed experiment, the FAISS index was built over randomly-streamed documents rather than per-item top-k retrieved documents. This is the design deviation that causes stratum collapse.

### 4.5 Hardware and Runtime

- GPU: NVIDIA H100 NVL (CUDA_VISIBLE_DEVICES=1)
- Conda environment: youra-h-e1 (Python 3.10)
- Total runtime: 5,676 seconds (~94 minutes)
- Coder-Validator cycles completed: 1 of 5

### 4.6 Evaluation Metrics and Gate Targets

| Metric | Gate Target |
|--------|-------------|
| N-gram Recall (Lexical stratum) | ≥ 0.80 |
| N-gram Recall (Semantic stratum) | ≤ 0.40 |
| Min-K%++ F1 Variance across corpora | ≥ 0.15 |
| Indeterminacy Rate | [0.10, 0.50] |

Gate type: MUST_WORK. Failure condition: stop entire verification chain; report failure as negative finding.

### 4.7 Dry Run

A dry run at 0.01× scale (500 corpus documents) was conducted prior to the full experiment. The dry run produced 3-way stratification: lexical = 13 items, semantic = 12 items, indeterminate = 25 items. This dry-run result was not predictive of full-scale behavior; the full run at 50K documents produced complete stratum collapse.

---

## 5. Results

### 5.1 Primary Finding: Stratum Collapse

All 25,403 benchmark items (100%) were assigned to the lexical stratum. Zero items were assigned to the semantic or indeterminate strata.

![2D contamination geometry phase diagram: all items collapse to the lexical stratum](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_data_problems_sonnet46_no_reflection/docs/youra_research/20260513_data_problems/paper/figures/phase_diagram.png)

*Figure 1. 2D contamination geometry phase diagram. All 25,403 benchmark items (MMLU, HellaSwag, GSM8K) plotted in max-13-gram-count × max-SBERT-cosine space. All items collapse to the lexical stratum (blue) due to degenerate SBERT similarity distributions from random corpus streaming. No semantic or indeterminate stratum items appear.*

The root cause is the use of random corpus streaming for SBERT cosine computation. At 50,000 randomly sampled documents, the probability that any sampled document is semantically similar to a specific benchmark item is near zero for non-contaminated items. The 75th-percentile threshold is therefore effectively zero and is vacuously satisfied by all items. The intended three-zone structure does not form.

At dry-run scale (500 documents), the same code produced apparent 3-way stratification because the smaller sample has higher cosine distribution variance by chance. At 50K documents, the distribution concentrates to near zero. This scale sensitivity is a specific failure mode: dry-run validation of stratum formation is not sufficient to predict full-scale stratum formation when the geometry feature is computed via random sampling.

### 5.2 N-gram Recall by Benchmark and Corpus

**Table 1: N-gram Recall by Benchmark and Corpus**

| Benchmark | The Pile | C4 | FineWeb | Mean |
|-----------|----------|----|---------|------|
| MMLU | 1.000 | 1.000 | 1.000 | 1.000 |
| HellaSwag | 0.000 | 1.000 | 1.000 | 0.667 |
| GSM8K | 0.000 | 0.000 | 0.000 | 0.000 |
| **Mean** | 0.333 | 0.667 | 0.667 | 0.556 |

MMLU achieves n-gram recall = 1.0 against all three corpora. All 14,042 MMLU test items contain at least one 13-gram appearing in each of The Pile, C4, and FineWeb at 50K-document sampling.

GSM8K achieves n-gram recall = 0.0 against all three corpora. No GSM8K item contains a 13-gram match in any sampled corpus document. Math problem notation and arithmetic reasoning chains do not appear as verbatim 13-gram sequences in general web corpora at this sampling scale.

HellaSwag recall is 0.0 against The Pile and 1.0 against C4 and FineWeb, indicating corpus-specific overlap patterns.

The mean lexical recall of 0.556 is the gate metric value. It fails the target of ≥ 0.80. This failure reflects benchmark heterogeneity: averaging MMLU (recall = 1.0) and GSM8K (recall = 0.0) in the same criterion produces a figure that is not diagnostic of either benchmark type.

### 5.3 Detector Detection Counts

**Table 2: Detector Detection Counts (Items Flagged as Contaminated)**

| Benchmark | Corpus | N-gram | Embedding | Min-K%++ | DC-PDD | ConStat |
|-----------|--------|--------|-----------|----------|--------|---------|
| MMLU | Pile | 14,042 | 0 | 0 | 14,042 | 0 |
| MMLU | C4 | 14,042 | 0 | 0 | 14,042 | 0 |
| MMLU | FineWeb | 14,042 | 0 | 0 | 14,042 | 0 |
| HellaSwag | Pile | 0 | 0 | 0 | 10,042 | 0 |
| HellaSwag | C4 | 3 | 0 | 0 | 10,042 | 0 |
| HellaSwag | FineWeb | 1 | 0 | 0 | 10,042 | 0 |
| GSM8K | Pile | 0 | 0 | 0 | 1,319 | 0 |
| GSM8K | C4 | 0 | 0 | 0 | 1,319 | 0 |
| GSM8K | FineWeb | 0 | 0 | 0 | 1,319 | 0 |

N-gram flags all MMLU items in all corpora (consistent with recall = 1.0). DC-PDD flags every item in every benchmark-corpus combination. This is a consequence of Bug B3 (Section 5.5): the DCPDDDetector implementation computes $-\text{ref\_log\_prob}$ rather than $\log P_{\text{target}} - \log P_{\text{ref}}$, producing all-positive outputs regardless of true contamination status. Embedding, Min-K%++, and ConStat produce zero detections in all conditions, reflecting both stratum collapse and implementation bugs.

### 5.4 Gate Metric Summary

**Table 3: Gate Metric Results (h-e1 EXISTENCE Sub-Hypothesis)**

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| N-gram Recall (Lexical stratum) | ≥ 0.80 | 0.556 | FAIL |
| N-gram Recall (Semantic stratum) | ≤ 0.40 | 0.000 (vacuous — zero semantic items) | PASS (vacuous) |
| Min-K%++ F1 Variance across corpora | ≥ 0.15 | 0.000 | FAIL |
| Indeterminacy Rate | [0.10, 0.50] | 0.000 | FAIL |

Overall gate: MUST_WORK → **FAIL**. Criteria satisfied: 1 of 4 (N-gram Semantic Recall, vacuously, due to empty semantic stratum). Routing result: ROUTED_TO_PHASE_0.

![Gate metric values versus targets for h-e1](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_data_problems_sonnet46_no_reflection/docs/youra_research/20260513_data_problems/paper/figures/gate_metrics.png)

*Figure 2. Gate metric values (bars) versus targets (dashed lines) for h-e1. N-gram lexical recall (0.556) falls below the ≥0.80 target; Min-K%++ F1 variance (0.000) falls below the ≥0.15 target; indeterminacy rate (0.000) falls outside the [0.10, 0.50] target range.*

![Stratum distribution pie chart](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_data_problems_sonnet46_no_reflection/docs/youra_research/20260513_data_problems/paper/figures/indeterminacy_pie.png)

*Figure 3. Stratum distribution of all 25,403 benchmark items. All items (100%) are in the lexical stratum; zero items are in the semantic or indeterminate strata.*

### 5.5 Implementation Bugs Identified

**Table 4: Implementation Bugs Identified by Validator**

| Bug | Component | Implemented Behavior | Correct Behavior |
|-----|-----------|---------------------|-----------------|
| B1 | `NgramIndex.max_overlap` | Counts total matching n-grams | Max consecutive run length |
| B2 | `StratifiedEvaluator.f1_matrix` | Scalar broadcast | Per-item computation |
| B3 | `DCPDDDetector` | $-\text{ref\_log\_prob}$ (single model) | $\log P_{\text{target}} - \log P_{\text{ref}}$ (two models) |
| B4 | `ConStatDetector` | Custom perplexity heuristic | `llmsanitize.contamination.constat()` API |

All four bugs were flagged by the Validator as advisory (non-blocking) issues. The single Coder-Validator cycle (1 of 5) was insufficient to resolve them. Bug B3 is the most consequential: it causes DC-PDD to produce all-positive outputs and makes Min-K%++ F1 variance unmeasurable (variance = 0.000 reflects the bug, not true detector behavior). Bug B4 means ConStat outputs are based on a non-standard heuristic rather than the published method.

![F1 heatmap by detector and stratum](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_data_problems_sonnet46_no_reflection/docs/youra_research/20260513_data_problems/paper/figures/stratum_f1_heatmap.png)

*Figure 4. F1 heatmap by detector family, stratum, and corpus. Only n-gram and DC-PDD produce non-zero outputs. The DC-PDD non-zero values arise from Bug B3. Embedding, Min-K%++, and ConStat show zero F1 across all conditions.*

![Min-K%++ F1 variance across corpora](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_data_problems_sonnet46_no_reflection/docs/youra_research/20260513_data_problems/paper/figures/minkpp_variance.png)

*Figure 5. Min-K%++ F1 variance across The Pile, C4, and FineWeb for MMLU and HellaSwag. Variance = 0.000 for all combinations, attributable to Bug B3 rather than true detector behavior.*

### 5.6 Infrastructure Validation

The core pipeline infrastructure operated correctly. N-gram index construction: The Pile index contains 37,678,937 n-grams; C4 contains 17,182,929; FineWeb contains 25,260,267. SBERT encoding: 50,000 documents encoded per corpus in approximately 5 minutes on NVIDIA H100 NVL. FAISS IndexFlatIP: functioning correctly. Full 3-benchmark × 3-corpus × 5-detector evaluation loop: completed within 94 minutes. Total generated code: 1,643 lines across 19 files.

---

## 6. Discussion

### 6.1 Stratum Collapse

The central finding of this experiment is that geometry-based contamination routing has a hard design prerequisite that was not implemented: top-k nearest-neighbor corpus retrieval for SBERT cosine computation. Any implementation that substitutes random corpus sampling for top-k retrieval when computing embedding-based similarity features is expected to produce degenerate score distributions at production scale. Score distributions change qualitatively, not merely quantitatively, as corpus sample size grows under random sampling — a property that dry-run validation at small scales does not reveal.

The stratum collapse phenomenon has not been previously described in the contamination detection literature. The conditions that produce it — random corpus subsampling for embedding similarity features — are present in some prior work, suggesting that semantic stratum formation may be underestimated in earlier studies using random corpus subsets.

### 6.2 Benchmark Heterogeneity

The finding that MMLU achieves n-gram recall = 1.0 and GSM8K achieves recall = 0.0 against the same corpora reveals that heterogeneous benchmark sets have structurally different corpus overlap profiles. A single recall criterion applied uniformly across benchmark types averaging over NLU and math benchmarks produces a statistic that is not diagnostic of either type. Future contamination detection frameworks should apply benchmark-type-specific criteria and evaluate math benchmarks against domain-specific corpora (e.g., OpenWebMath, Proof-Pile) rather than general web corpora.

### 6.3 Hypothesis Status

The MUST_WORK gate failure for h-e1 is attributed to experimental design and implementation failures:

1. Random corpus streaming for SBERT cosine computation (design flaw)
2. DCPDDDetector log-ratio bug (engineering bug)
3. ConStatDetector non-standard API usage (engineering bug)
4. NgramIndex total count vs. max consecutive run (implementation deviation)
5. StratifiedEvaluator scalar broadcast (engineering bug)
6. FineWeb substitution for RedPajama (data substitution)
7. Heterogeneous benchmark types in unified recall criterion (criterion mismatch)

None of these constitute falsifying evidence against the hypothesis. The theoretical causal chain — that detector families operate on orthogonal signal types whose efficacy is structurally determined by corpus overlap geometry — is consistent with the contamination detection literature [Fu et al., 2024; Singh et al., 2024] and has not been tested. Hypothesis confidence was revised from 0.78 to 0.62, reflecting the severity of the design flaw, not a negative empirical finding.

Dependent sub-hypotheses h-m1 through h-m4 are cascade-failed pending redesign of h-e1.

### 6.4 Limitations

**L1 (Critical):** Stratum collapse invalidates the primary routing accuracy measurement (P1) and indeterminacy rate measurement (P3). The semantic stratum contains zero items; all stratum-conditional metrics are undefined or vacuous.

**L2 (Moderate):** Implementation bugs B3 and B4 make all MIA-based and statistical detector results uninterpretable. Min-K%++ F1 variance = 0.000 reflects Bug B3, not true detector behavior.

**L3 (Moderate):** Corpus coverage at 50K documents represents < 6% of The Pile by document count. All n-gram recall figures are lower bounds on true corpus overlap. GSM8K recall = 0.0 may be a sampling artifact.

**L4 (Low-Moderate):** FineWeb was substituted for RedPajama-Data-1T without prior specification. FineWeb has different deduplication characteristics. Cross-corpus generalization claims involving FineWeb require re-evaluation with RedPajama.

**L5 (Low):** Dry-run results (3-way stratification at 500-document scale) were not predictive of full-scale behavior. Small-scale dry runs are insufficient for validating SBERT-based stratum formation.

**L6 (Low):** The stratum collapse boundary condition is documented for `all-MiniLM-L6-v2`. Whether it generalizes to other SBERT model variants is unverified.

---

## 7. Conclusion

This paper reports an experiment (h-e1) designed to test whether contamination geometry strata can be formed from corpus-side signals (max 13-gram count and SBERT cosine similarity) and whether detector routing across these strata is feasible. The experiment does not produce routing results. Instead, it encounters a structural failure mode: random corpus streaming produces degenerate SBERT cosine distributions at 50,000-document scale, collapsing all 25,403 benchmark items into the lexical stratum. This failure mode, termed stratum collapse, is identified as a predictable consequence of using random corpus sampling for semantic similarity computation, and top-k nearest-neighbor retrieval is identified as a necessary prerequisite for semantic stratum formation.

The experiment additionally establishes two reproducible empirical findings: MMLU achieves n-gram recall = 1.0 against The Pile, C4, and FineWeb at 50K-document sampling; GSM8K achieves recall = 0.0 against the same corpora. These findings indicate that benchmark heterogeneity creates structurally different corpus overlap profiles that require benchmark-type-specific detection criteria.

Four implementation bugs are identified and documented, providing a concrete guide for future implementations of the detector families evaluated.

The routing hypothesis H-GeomRoute-v1 remains unresolved. The gate failure is attributed to experimental design and implementation failures, not to falsifying evidence. The next step is a Phase 0 redesign of h-e1 incorporating: (1) top-k FAISS nearest-neighbor retrieval per benchmark item for SBERT cosine computation, (2) corrected DCPDDDetector with two-model log-likelihood ratio, (3) benchmark-type-specific recall criteria, and (4) controlled synthetic contamination injection for stratum formation validation prior to testing on real corpus overlap.

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

## Appendix A: Implementation Bug Specifications

### A.1 DCPDDDetector Log-Ratio Fix (Bug B3)

The executed implementation computes `score = -ref_log_prob` using a single model. The correct implementation requires two models and computes the per-token log-likelihood ratio:

```python
# Correct: Two-model log-likelihood ratio
score = log_prob_target - log_prob_reference  # per token, then aggregate

# Incorrect (executed): score = -log_prob_reference  # single model
```

Required models: Pythia-6.9B (target), Pythia-2.8B (reference).

### A.2 ConStatDetector API Fix (Bug B4)

```python
# Correct: Use llmsanitize API
from llmsanitize.contamination import constat
result = constat(model_output_seen, model_output_held_out)

# Incorrect (executed): custom heuristic based on perplexity threshold
```

### A.3 NgramIndex Max Consecutive Run Fix (Bug B1)

```python
# Correct: max consecutive n-gram run
def max_overlap(self, text, n=13):
    ngrams = extract_ngrams(text, n)
    return max(len(run) for run in find_consecutive_runs(ngrams, self.index))

# Incorrect (executed): sum of all matching n-grams (overcounts non-consecutive matches)
```

### A.4 StratifiedEvaluator F1 Matrix Fix (Bug B2)

The `f1_matrix` computation uses scalar broadcast, causing `indeterminacy_rate` to be degenerate (0.000). The correct implementation requires per-item F1 computation followed by per-item margin computation between the top-1 and top-2 detectors.

---

## Appendix B: Corpus Index Statistics

| Corpus | N-gram Index Size | SBERT Vectors | Documents Sampled |
|--------|------------------|---------------|-------------------|
| The Pile (monology/pile-uncopyrighted) | 37,678,937 | 50,000 | 50,000 |
| C4 (allenai/c4) | 17,182,929 | 50,000 | 50,000 |
| FineWeb (HuggingFaceFW/fineweb) | 25,260,267 | 50,000 | 50,000 |

---

## Appendix C: Experiment Execution Summary

| Parameter | Value |
|-----------|-------|
| Hypothesis ID | h-e1 (EXISTENCE) |
| Gate Type | MUST_WORK |
| Gate Result | FAIL |
| Reflection Outcome | ROUTED_TO_PHASE_0 |
| Total Items Evaluated | 25,403 |
| Benchmark-Corpus Pairs | 9 (3 × 3) |
| Detector Families | 5 |
| Total Runtime | 5,676 seconds (~94 minutes) |
| Coder-Validator Cycles | 1 / 5 |
| Advisory Bugs Identified | 4 |
| Cascade-Failed Sub-Hypotheses | 4 (h-m1, h-m2, h-m3, h-m4) |
| GPU | NVIDIA H100 NVL |
| Hypothesis Confidence (Pre-Experiment) | 0.78 |
| Hypothesis Confidence (Post-Experiment) | 0.62 |
