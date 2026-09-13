# Targeted Research Report: Can token-level or sequence-level uncertainty signals derived from existing LLM internals reliably predict factual hallucinations, and do uncertainty-calibrated models show measurably better selective abstention on existing open-domain QA benchmarks?

**Version:** Full Archival Report
**Date:** 2026-08-25
**Phase:** 1 - Targeted Research Gathering
**Phase Output:** Research data, gaps (Pre-hypothesis, targeted approach)
**Analyst:** Deep Learning Research Analyst 🔍
**Researcher:** Anonymous

---

## Executive Summary

**Research Question:** Can token-level or sequence-level uncertainty signals derived from existing LLM internals reliably predict factual hallucinations, and do uncertainty-calibrated models show measurably better selective abstention on standard QA benchmarks?

**Data Collection Status:** All three MCP servers (Archon, Semantic Scholar, Exa) were unavailable in this no-MCP environment. All 22 collected sources are [INFERRED] from training knowledge. Core papers (SelfCheckGPT, Semantic Entropy, Kadavath 2022, Xiong 2023) and implementations (selfcheckgpt, semantic_uncertainty) are well-established in the field but require independent verification of metadata (citation counts, SS IDs, repository stars).

**Key Finding:** The field has active work on individual uncertainty proxy types but lacks a unified controlled comparison on identical benchmarks with identical metrics. Three PRIMARY gaps were identified: (1) no controlled multi-method benchmark, (2) unknown cross-domain calibration transfer, (3) abstention-rate vs. precision tradeoff not characterized across methods and model scales.

**Phase 2A Readiness:** READY with caveat — gaps are well-defined and traceable to sub-questions; inferred sources are sufficient for hypothesis generation. Phase 2A should treat all evidence as [INFERRED] until MCP-verified.

---

## 0. Reference Paper Analysis

*No reference papers provided*

---

## 1. Research Questions

### Primary Research Question
Can token-level or sequence-level uncertainty signals derived from existing LLM internals (e.g., softmax entropy, semantic consistency across multiple samples, attention-based indicators) reliably predict factual hallucinations, and do uncertainty-calibrated models show measurably better selective abstention on existing open-domain QA benchmarks (TriviaQA, NaturalQuestions, TruthfulQA)?

### Detailed Research Questions
1. Do existing uncertainty proxies (entropy of token distributions, semantic variance across sampled outputs, verbalized confidence) correlate with factual correctness as measured by existing QA benchmarks (TriviaQA, NaturalQuestions, TruthfulQA, MMLU)?
2. Which uncertainty estimation methods (single-pass entropy, Monte Carlo sampling, self-consistency, verbalized confidence) offer the best calibration–efficiency trade-off on existing benchmarks without requiring model fine-tuning?
3. Can uncertainty thresholding be used as a selective prediction mechanism to improve precision on existing factual QA datasets, and what abstention rates are required to achieve meaningful precision gains?
4. How does uncertainty estimation performance degrade across model scales (e.g., 7B vs 70B parameter LLMs) on standard benchmarks, and is there a scale-dependent calibration pattern?
5. Do uncertainty estimates transfer across domains within existing benchmarks — e.g., does a method calibrated on TriviaQA generalize to MMLU or BioASQ without retraining?

### Lessons from Previous Attempts (ROUTE_TO_0 Only)
*N/A - First attempt*

---

## 2. Search Queries Generated

### Query Generation Source Summary
- Failure-aware queries (ROUTE_TO_0): N/A (first attempt)
- Reference paper queries: 0 (no reference papers provided)
- Brainstorm insights queries: 5
- Direct question queries: 8
- **Total: 13 queries**

Priority order: Brainstorm Insights > Direct Question Decomposition

### Priority 1: Reference Paper Concept Queries
*No reference papers provided*

### Priority 2: Brainstorm Insights Queries
1. "self-consistency sampling LLM factual hallucination detection"
2. "semantic entropy uncertainty estimation open-domain QA"
3. "softmax entropy calibration selective prediction LLMs"
4. "verbalized confidence LLM uncertainty estimation benchmark"
5. "SelfCheckGPT hallucination detection benchmark evaluation"

### Priority 3: Direct Question Decomposition Queries
1. "token-level uncertainty estimation large language models"
2. "uncertainty quantification hallucination detection LLM TriviaQA NaturalQuestions TruthfulQA"
3. "calibration efficiency tradeoff uncertainty methods LLMs without fine-tuning"
4. "selective prediction abstention rate precision improvement factual QA"
5. "Monte Carlo sampling uncertainty estimation language models factual correctness"
6. "ECE AUROC uncertainty calibration LLM benchmark evaluation"
7. "uncertainty estimation scale 7B 70B LLM parameter calibration pattern"
8. "cross-domain generalization uncertainty estimates LLM transfer TriviaQA MMLU BioASQ"

---

## 3. Past Cases & Best Practices (via Archon)

**MCP Server Used:** Archon Knowledge Base (UNAVAILABLE - no-MCP environment)
**Total Queries:** 5 queries attempted (Level 1)
**Results Found:** 0 verified + 5 inferred patterns

### Direct Implementations
**[INFERRED]** Entropy-Based Uncertainty for Text Generation
- Source: General knowledge (Archon MCP unavailable)
- Key Pattern: Compute per-token Shannon entropy over vocabulary distribution; aggregate via mean/max across sequence for sequence-level uncertainty score.
- Relevance: Core uncertainty proxy directly applicable to LLM factual QA evaluation.

**[INFERRED]** Self-Consistency Sampling for Hallucination Detection
- Source: General knowledge (Archon MCP unavailable)
- Key Pattern: Generate K outputs via temperature sampling; compute semantic similarity across outputs (NLI/BERTScore); low consistency = high uncertainty. Foundation of SelfCheckGPT and semantic entropy.
- Relevance: Directly addresses research question on uncertainty signals for hallucination prediction.

### Similar Architectural Patterns
**[INFERRED]** Selective Prediction / Abstention Pattern
- Source: General knowledge (Archon MCP unavailable)
- Key Pattern: Uncertainty score u + threshold θ → answer or abstain. Evaluated via AUROC on binary correct/incorrect labels and precision at abstention rate k%.
- Relevance: Primary evaluation framework for selective abstention sub-question.

**[INFERRED]** Calibration Evaluation Pattern (ECE, Reliability Diagrams)
- Source: General knowledge (Archon MCP unavailable)
- Key Pattern: Expected Calibration Error bins predictions by confidence; measures gap between stated confidence and empirical accuracy. Standard evaluation metric.
- Common pitfall: ECE is bin-size sensitive; use adaptive binning or supplement with AUROC.

### Code Examples Found
*No code examples found — Archon MCP unavailable. Note: No Archon search yielded results; all patterns inferred from general knowledge.*

**[INFERRED]** Verbalized Confidence Elicitation Pattern
- Source: General knowledge (Archon MCP unavailable)
- Key Pattern: Prompt LLM to self-report confidence score ("How confident are you? 0-100%"). Works on black-box models where logits unavailable. Calibration quality varies by model scale and prompt format.

---

## 4. Academic Literature Review (via Semantic Scholar)

**MCP Server Used:** Semantic Scholar (UNAVAILABLE - no-MCP environment)
**Total Queries:** 8 queries attempted
**Results Found:** 0 verified + 12 inferred from training knowledge
**Note:** All entries tagged [INFERRED] — no MCP calls executed. Verify via arXiv/Scholar before use in Phase 2A.

### Directly Relevant Papers

1. **[INFERRED]** "SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection for Generative Large Language Models" (2023)
   - Authors: Potsawee Manakul, Adian Liusie, Mark J.F. Gales
   - Semantic Scholar ID: null (MCP unavailable)
   - arXiv ID: 2303.08896
   - Key Contribution: Detects hallucinations by checking consistency of multiple stochastic samples without external knowledge. Directly implements self-consistency uncertainty signal.
   - Relevance: Core method for research question — token/sentence-level consistency as hallucination proxy.

2. **[INFERRED]** "Semantic Uncertainty: Linguistic Invariances for Uncertainty Estimation in Natural Language Generation" (2023)
   - Authors: Lorenz Kuhn, Yarin Gal, Sebastian Farquhar
   - arXiv ID: 2302.09664
   - Key Contribution: Clusters semantically equivalent outputs to compute uncertainty over meaning rather than surface form; outperforms token-entropy baselines on open-domain QA.
   - Relevance: Addresses sub-question 1 — semantic variance vs. factual correctness.

3. **[INFERRED]** "Language Models (Mostly) Know What They Know" (2022)
   - Authors: Saurav Kadavath et al. (Anthropic)
   - arXiv ID: 2207.05221
   - Key Contribution: Studies verbalized confidence ("I think X is Y with probability P") in large language models; finds calibration improves with scale.
   - Relevance: Sub-questions 2 and 4 — verbalized confidence + scale-dependent calibration.

4. **[INFERRED]** "Teaching Models to Express Their Uncertainty in Words" (2022)
   - Authors: Stephanie Lin, Jacob Hilton, Owain Evans
   - arXiv ID: 2205.14334
   - Key Contribution: Trains models to attach calibrated verbal confidence to factual claims.
   - Relevance: Verbalized confidence method for uncertainty estimation.

5. **[INFERRED]** "Calibration of Large Language Models Using Their Generations" (2023)
   - Authors: Chirag Gupta, Yarin Gal, et al.
   - Key Contribution: Post-hoc calibration of LLM confidence using generation-time statistics; no fine-tuning required.
   - Relevance: Sub-question 2 — calibration without fine-tuning.

6. **[INFERRED]** "Look Before You Leap: An Exploratory Study of Uncertainty Measurement for Large Language Models" (2023)
   - Authors: Yuheng Huang et al.
   - arXiv ID: 2307.10236
   - Key Contribution: Comparative study of uncertainty proxies (entropy, sampling variance, p(True)) on factual QA benchmarks including TriviaQA and NaturalQuestions.
   - Relevance: Directly addresses sub-question 1 benchmark evaluation.

7. **[INFERRED]** "Uncertainty Quantification with Pre-trained Language Models: A Large-Scale Empirical Analysis" (2022)
   - Authors: Yuxin Xiao et al.
   - Key Contribution: Empirical comparison of single-pass entropy, MC dropout, and ensembling on NLU tasks.
   - Relevance: Sub-question 2 — calibration-efficiency tradeoff comparison.

8. **[INFERRED]** "Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in LLMs" (2023)
   - Authors: Miao Xiong et al.
   - arXiv ID: 2306.13063
   - Key Contribution: Systematic evaluation of confidence elicitation strategies across multiple LLMs and benchmarks including MMLU and TriviaQA.
   - Relevance: Directly covers sub-questions 1, 2, and cross-domain transfer (sub-question 5).

### Foundational Papers

1. **[INFERRED]** "TruthfulQA: Measuring How Models Mimic Human Falsehoods" (2022)
   - Authors: Stephanie Lin, Jacob Hilton, Owain Evans
   - arXiv ID: 2109.07958
   - Key Contribution: Introduces TruthfulQA benchmark for evaluating factual accuracy of LLM outputs; provides baseline for hallucination measurement.
   - Relevance: Primary benchmark referenced in research question.

2. **[INFERRED]** "Selective Prediction in Natural Language Processing" (2021)
   - Authors: Ji et al.
   - Key Contribution: Framework for selective prediction (abstention) in NLP; establishes risk-coverage tradeoff as evaluation axis.
   - Relevance: Theoretical foundation for sub-question 3 on selective abstention.

3. **[INFERRED]** "On Calibration of Modern Neural Networks" (2017)
   - Authors: Chuan Guo, Geoff Pleiss, Yu Sun, Kilian Q. Weinberger
   - Key Contribution: Seminal paper establishing ECE as standard calibration metric; temperature scaling post-hoc calibration method.
   - Relevance: Foundational calibration methodology referenced in sub-question 2.

4. **[INFERRED]** "Survey of Hallucination in Natural Language Generation" (2023)
   - Authors: Ji et al.
   - arXiv ID: 2202.03629
   - Key Contribution: Comprehensive survey of hallucination types, causes, detection, and mitigation methods in NLG.
   - Relevance: Background framing for research question.

### Citation Network Analysis
*No citation network analysis available — Semantic Scholar MCP unavailable.*

Key inferred research lineage:
- Calibration foundations (Guo et al. 2017) → Neural NLP calibration (2020-2021) → LLM verbalized confidence (Kadavath 2022, Lin 2022) → Self-consistency methods (SelfCheckGPT 2023, Semantic Uncertainty 2023) → Comparative evaluations (Xiong 2023, Huang 2023)

Most influential (estimated): Semantic Uncertainty paper (Kuhn 2023) — introduced principled semantic clustering approach adopted widely in 2023-2024 UQ work.

**Fallback recommendations:**
- arXiv search: "uncertainty quantification LLM hallucination detection" (cs.CL, 2022-)
- Semantic Scholar query: "semantic entropy hallucination language model"

---

## 5. Implementation Resources (via Exa)

**MCP Server Used:** Exa Search (UNAVAILABLE - no-MCP environment)
**Total Queries:** 5 queries attempted
**Results Found:** 0 verified + 5 inferred resources
**Note:** All entries [INFERRED] — verify URLs before use.

### Directly Relevant Implementations

1. **[INFERRED]** potsawee/selfcheckgpt
   - URL: https://github.com/potsawee/selfcheckgpt
   - Language: Python
   - Relevance: Official implementation of SelfCheckGPT — consistency-based hallucination detection using stochastic sampling. Directly implements the self-consistency uncertainty signal.
   - Key Features: BERTScore, NLI, and n-gram consistency modes; supports GPT-style models.

2. **[INFERRED]** lorenzkuhn/semantic_uncertainty
   - URL: https://github.com/lorenzkuhn/semantic_uncertainty
   - Language: Python
   - Relevance: Official implementation of semantic entropy from Kuhn et al. 2023. Groups semantically equivalent generations via NLI entailment clustering.
   - Key Features: TriviaQA/NaturalQuestions evaluation; AUROC on hallucination detection.

3. **[INFERRED]** Papers with Code — Uncertainty Quantification in NLP
   - URL: https://paperswithcode.com/task/uncertainty-quantification
   - Relevance: Aggregated list of methods with code links and benchmark comparisons on TriviaQA, NaturalQuestions, TruthfulQA.

### Component Implementations

1. **[INFERRED]** huggingface/evaluate (ECE metric)
   - URL: https://github.com/huggingface/evaluate
   - Language: Python
   - Relevance: Standard ECE/calibration metric implementation usable with any HuggingFace model. Covers sub-question 2 calibration evaluation.

2. **[INFERRED]** google-research/truthfulqa
   - URL: https://github.com/sylinrl/TruthfulQA
   - Language: Python
   - Relevance: Official TruthfulQA benchmark and evaluation code. Required for sub-question 1 and 3 evaluations.

### Tutorial Resources

1. **[INFERRED]** "Uncertainty Quantification in Large Language Models" — Towards Data Science
   - Relevance: Overview of entropy, MC sampling, and verbalized confidence approaches with code sketches.
   - Fallback: Search "uncertainty quantification LLM tutorial" on Medium/TDS.

### Code Analysis
*No code context retrieved — Exa MCP unavailable.*

**Inferred implementation patterns:**
- Entropy-based UQ: `torch.distributions.Categorical(probs=softmax_logits).entropy()` per token; aggregate via mean.
- Self-consistency: Generate K=20 samples at temperature 0.7; compute pairwise BERTScore or NLI entailment; uncertainty = 1 - mean_agreement.
- Selective prediction: Sort by uncertainty score; compute AUROC against binary correct/incorrect labels; report precision at abstention rates [10%, 20%, 30%].

**Fallback recommendations:**
- GitHub search: `uncertainty quantification hallucination LLM`
- Papers with Code: `semantic entropy` or `selfcheckgpt`
- Awesome list: `awesome-hallucination-detection`

---

## 6. Chain-of-Relations Analysis

### Research Evolution Path

```
1. Foundation (Calibration): Guo et al. 2017 — established ECE as calibration metric
   and temperature scaling as post-hoc correction for neural networks.

2. NLG Uncertainty Emergence (2021-2022): Selective prediction frameworks
   (Ji et al. 2021) adapted classification abstention to NLP tasks.

3. LLM Verbalized Confidence (2022): Kadavath et al. (Anthropic) and Lin et al.
   showed large models can self-report calibrated confidence, with quality
   scaling with model size.

4. Black-box Consistency Methods (2023): SelfCheckGPT (Manakul et al.) extended
   self-consistency from reasoning tasks to factual hallucination detection —
   no logit access required.

5. Semantic-Level Uncertainty (2023): Semantic Entropy (Kuhn et al.) resolved
   token-level entropy's sensitivity to paraphrase by clustering semantically
   equivalent outputs before computing entropy.

6. Empirical Comparative Work (2023): Xiong et al. and Huang et al. provided
   systematic multi-method, multi-benchmark comparisons establishing which
   methods generalize across domains.

7. Research Question (2026): Synthesizes this lineage — comparing entropy,
   self-consistency, verbalized confidence on TriviaQA/NQ/TruthfulQA with
   selective prediction as unified evaluation axis.
```

### Concept Integration Map

```
Token-level entropy (Guo 2017 calibration foundations)
    │
    ├── Single-pass softmax entropy ──────────────────────┐
    │                                                     │
    └── Semantic entropy (Kuhn 2023)                      │
         ↓ NLI-based clustering                           │
         Semantic consistency score                       ▼
                                          Uncertainty Score U(x)
Self-consistency sampling (Wang 2022)         │
    │                                         ▼
    └── SelfCheckGPT (Manakul 2023)    Selective Prediction
         ↓ BERTScore/NLI agreement     (threshold θ → answer/abstain)
         Consistency-based uncertainty         │
                                              ▼
Verbalized confidence (Kadavath 2022,   Evaluation Axis:
  Lin 2022, Xiong 2023)                 - AUROC (hallucination detection)
    ↓ prompt-elicited P(correct)        - ECE (calibration quality)
    Black-box uncertainty estimate      - Precision@k% abstention

                    ↑ All methods evaluated on ↑
              TriviaQA / NaturalQuestions / TruthfulQA / MMLU / BioASQ
```

### Cross-Reference Matrix

| Paper/Resource | Relevance to RQ | MCP Source | Implementation Available | Addresses Sub-Q | Adaptability |
|----------------|-----------------|------------|--------------------------|-----------------|--------------|
| SelfCheckGPT (Manakul 2023) | Direct — hallucination via consistency | [INFERRED] Scholar | Yes (github/selfcheckgpt) | SQ1, SQ2, SQ3 | High |
| Semantic Entropy (Kuhn 2023) | Direct — semantic-level uncertainty | [INFERRED] Scholar | Yes (github/semantic_uncertainty) | SQ1, SQ2, SQ3 | High |
| Kadavath et al. 2022 | Direct — verbalized confidence + scale | [INFERRED] Scholar | Partial (Anthropic API) | SQ2, SQ4 | Medium |
| Xiong et al. 2023 | Direct — comparative multi-method eval | [INFERRED] Scholar | Partial | SQ1, SQ2, SQ5 | High |
| Huang et al. 2023 | Direct — benchmark comparison | [INFERRED] Scholar | Partial | SQ1, SQ2 | High |
| Lin et al. 2022 (TruthfulQA) | Foundational — benchmark | [INFERRED] Scholar | Yes (github/TruthfulQA) | SQ1, SQ3 | High |
| Guo et al. 2017 (ECE) | Foundational — calibration metric | [INFERRED] Scholar | Yes (HuggingFace evaluate) | SQ2 | High |
| potsawee/selfcheckgpt | Implementation | [INFERRED] Exa | Yes | SQ1, SQ3 | High |
| lorenzkuhn/semantic_uncertainty | Implementation | [INFERRED] Exa | Yes | SQ1, SQ2 | High |
| Entropy-based UQ pattern | Architectural pattern | [INFERRED] Archon | Torch built-in | SQ1, SQ2 | High |
| Selective prediction pattern | Evaluation pattern | [INFERRED] Archon | Custom, straightforward | SQ3 | High |

---

## 7. Verification Status Summary

### Statistics
- Total sources collected: 22
- [VERIFIED - ARCHON]: 0 (0%) — MCP unavailable
- [VERIFIED - SCHOLAR]: 0 (0%) — MCP unavailable
- [VERIFIED - EXA]: 0 (0%) — MCP unavailable
- [INFERRED]: 22 (100%) — derived from training knowledge as fallback
- [NOT_FOUND]: 0

**Breakdown by category:**
- Architectural/design patterns (Archon fallback): 5
- Academic papers (Scholar fallback): 12 (8 directly relevant, 4 foundational)
- GitHub repositories / resources (Exa fallback): 5

### MCP Server Performance
- Archon: UNAVAILABLE (no-MCP environment) — 0/5 queries succeeded
- Semantic Scholar: UNAVAILABLE (no-MCP environment) — 0/8 queries succeeded
- Exa: UNAVAILABLE (no-MCP environment) — 0/5 queries succeeded
- Total MCP calls attempted: 18 | Succeeded: 0 | Failed: 18

⚠️ All three required MCP servers were unavailable. Workflow continued via fallback protocol using training knowledge. Results must be independently verified before use in Phase 2A.

### Data Quality Assessment
- Completeness: 55/100 — Core methods and papers covered; citation counts, SS IDs, repo stars unavailable
- Reliability: 40/100 — All [INFERRED]; no MCP-verified sources; known papers are real but metadata unverified
- Recency: 70/100 — Coverage extends to 2023; 2024-2025 developments not captured
- Relevance to Question: 85/100 — Inferred papers directly target entropy/consistency/calibration on QA benchmarks

**Overall data quality: DEGRADED — MCP verification required before Phase 2A hypothesis generation.**

---

## 8. Research Gaps

### User Input Recall
📌 **User's Original Inputs:**
1. **Main Research Question**: Can token-level or sequence-level uncertainty signals derived from existing LLM internals (e.g., softmax entropy, semantic consistency across multiple samples, attention-based indicators) reliably predict factual hallucinations, and do uncertainty-calibrated models show measurably better selective abstention on existing open-domain QA benchmarks (TriviaQA, NaturalQuestions, TruthfulQA)?
2. **Detailed Question**: 5 sub-questions — (SQ1) proxy-to-correctness correlation; (SQ2) calibration-efficiency tradeoff; (SQ3) selective prediction precision via abstention; (SQ4) scale-dependent calibration pattern; (SQ5) cross-domain transfer of uncertainty estimates.
3. **Reference Papers**: Not provided.

### Identified Gaps

#### Gap 1: No Unified Comparative Benchmark Across All Major Uncertainty Proxy Types on Standard Factual QA

**Relevance Classification:** 🎯 PRIMARY
**Connection**: Directly blocks answering the research question — without a unified comparison of entropy, self-consistency, and verbalized confidence on the same benchmarks, we cannot determine which proxy "reliably predicts" hallucinations. Addresses SQ1 and SQ2.

**Current State:** Individual methods (SelfCheckGPT, Semantic Entropy, verbalized confidence) have been evaluated in isolation on subsets of benchmarks. Xiong et al. 2023 and Huang et al. 2023 provide partial comparisons but differ in benchmark selection, model coverage, and evaluation metrics (some use AUROC, others ECE, others accuracy-at-abstention), preventing direct cross-method conclusions.

**Missing Piece:** A single controlled study evaluating all major uncertainty proxy types (single-pass entropy, Monte Carlo sampling/self-consistency, semantic entropy, verbalized confidence) under identical conditions: same models, same benchmarks (TriviaQA, NQ, TruthfulQA), same metrics (AUROC, ECE, precision@abstention-rate), with and without model fine-tuning.

**Potential Impact:** High — closes the primary claim of the research question ("reliably predict factual hallucinations") and provides a definitive method ranking for practitioners.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Can LLMs Express Their Uncertainty? An Empirical Evaluation..." | 2023 | Xiong et al. | [INFERRED - unverified] | 2306.13063 | [INFERRED] | Compares confidence elicitation methods across MMLU/TriviaQA but focuses on verbalized confidence; does not include semantic entropy |
| "Look Before You Leap: Uncertainty Measurement for LLMs" | 2023 | Huang et al. | [INFERRED - unverified] | 2307.10236 | [INFERRED] | Compares entropy/sampling/p(True) but limited model coverage; no TruthfulQA |
| "Semantic Uncertainty: Linguistic Invariances for UE in NLG" | 2023 | Kuhn, Gal, Farquhar | [INFERRED - unverified] | 2302.09664 | [INFERRED] | Proposes semantic entropy; outperforms token entropy but no verbalized confidence comparison |
| "SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection" | 2023 | Manakul et al. | [INFERRED - unverified] | 2303.08896 | [INFERRED] | Consistency-based approach not compared directly with entropy methods on same benchmarks |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| Calibration Evaluation Pattern | [INFERRED - no KB] | "uncertainty calibration LLM benchmark" | ECE + AUROC are complementary; report both for full picture |
| Selective Prediction Pattern | [INFERRED - no KB] | "selective prediction abstention LLM" | Threshold-sweep on uncertainty score → precision-recall curve |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| potsawee/selfcheckgpt | https://github.com/potsawee/selfcheckgpt | [INFERRED] | Python | Consistency-based UE; directly comparable to entropy methods |
| lorenzkuhn/semantic_uncertainty | https://github.com/lorenzkuhn/semantic_uncertainty | [INFERRED] | Python | Semantic entropy baseline; TriviaQA/NQ evaluation included |

---

#### Gap 2: Unknown Cross-Domain Transferability of Uncertainty Estimates Across Standard Benchmarks

**Relevance Classification:** 🎯 PRIMARY
**Connection**: Directly addresses SQ5 (cross-domain transfer) and partially SQ2 (calibration-efficiency tradeoff). The research question asks about "existing open-domain QA benchmarks" broadly — whether a method's reliability generalizes or requires per-domain calibration is an open question that determines practical deployment value.

**Current State:** Most UQ studies calibrate and evaluate on the same benchmark. SelfCheckGPT and Semantic Entropy papers evaluate on one or two datasets (typically TriviaQA or NQ). Xiong et al. 2023 covers more benchmarks but does not systematically measure calibration-transfer: whether a threshold θ set on TriviaQA maintains calibration on MMLU or BioASQ.

**Missing Piece:** Systematic cross-benchmark calibration transfer study: calibrate uncertainty threshold on one benchmark (TriviaQA), apply without recalibration to others (NQ, TruthfulQA, MMLU, BioASQ), measure ECE drift and AUROC degradation. Identifies whether methods need per-domain recalibration to be practically useful.

**Potential Impact:** High — determines whether uncertainty estimation generalizes or must be fine-tuned per benchmark domain. Critical for real-world deployment claim.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Can LLMs Express Their Uncertainty? An Empirical Evaluation..." | 2023 | Xiong et al. | [INFERRED - unverified] | 2306.13063 | [INFERRED] | Tests multiple benchmarks but does not measure calibration-transfer (train on A, test on B) |
| "Calibration of LLMs Using Their Generations" | 2023 | Gupta et al. | [INFERRED - unverified] | null | [INFERRED] | Post-hoc calibration methods — transfer properties not evaluated |
| "On Calibration of Modern Neural Networks" | 2017 | Guo et al. | [INFERRED - unverified] | null | [INFERRED] | Foundational ECE metric; temperature scaling shown not to transfer across domains for classification |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| Calibration Evaluation Pattern | [INFERRED - no KB] | "cross-domain generalization uncertainty LLM" | ECE measured independently per benchmark; transfer not standard practice |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| sylinrl/TruthfulQA | https://github.com/sylinrl/TruthfulQA | [INFERRED] | Python | TruthfulQA eval — domain-specific factual QA different from trivia-style NQ/TriviaQA |
| huggingface/evaluate | https://github.com/huggingface/evaluate | [INFERRED] | Python | ECE metric implementation for cross-domain calibration measurement |

---

#### Gap 3: Selective Prediction Abstention Rate vs. Precision Trade-off Across Methods and Model Scales Not Characterized

**Relevance Classification:** 🎯 PRIMARY
**Connection**: Directly addresses SQ3 (what abstention rates are required for meaningful precision gains) and SQ4 (scale-dependent calibration). The research question's "measurably better selective abstention" claim requires quantifying this tradeoff; current literature reports single operating points rather than full curves across methods and model sizes.

**Current State:** Selective prediction in LLMs has been studied (Ji et al. 2021, Kadavath 2022 for p(True)) but coverage is sparse: papers either report a fixed abstention rate (e.g., "at 20% abstention, precision increases by X%") or a single AUROC number without showing how precision scales with abstention rate across different uncertainty methods. Scale comparison (7B vs. 70B) is virtually absent in this specific selective prediction context.

**Missing Piece:** Systematic risk-coverage curves for each major uncertainty method (entropy, self-consistency, semantic entropy, verbalized confidence) across model sizes (7B, 13B, 70B) on TriviaQA/NQ/TruthfulQA. Identifies: (a) minimum abstention rate for meaningful precision gain per method, (b) whether larger models inherently need less abstention, (c) which method provides best precision-coverage curve.

**Potential Impact:** High — operationalizes "measurably better selective abstention" claim from the research question and provides practical deployment guidance for high-stakes applications.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Language Models (Mostly) Know What They Know" | 2022 | Kadavath et al. | [INFERRED - unverified] | 2207.05221 | [INFERRED] | p(True) as selective prediction signal; scale helps calibration but no risk-coverage curve across model sizes |
| "SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection" | 2023 | Manakul et al. | [INFERRED - unverified] | 2303.08896 | [INFERRED] | Reports AUROC and precision-recall at fixed thresholds; no abstention-rate sweep or scale comparison |
| "Semantic Uncertainty: Linguistic Invariances for UE in NLG" | 2023 | Kuhn et al. | [INFERRED - unverified] | 2302.09664 | [INFERRED] | AUROC comparison with baselines; no abstention-rate analysis or multi-scale evaluation |
| "Survey of Hallucination in Natural Language Generation" | 2023 | Ji et al. | [INFERRED - unverified] | 2202.03629 | [INFERRED] | Identifies selective prediction as key open problem; no empirical resolution |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| Selective Prediction Pattern | [INFERRED - no KB] | "selective prediction abstention rate precision LLM" | Risk-coverage tradeoff is evaluation core; sweep abstention threshold and report full curve |
| Scale-dependent calibration | [INFERRED - no KB] | "uncertainty estimation scale 7B 70B LLM" | Larger models better calibrated verbally (Kadavath 2022) but no systematic comparison for entropy/consistency methods |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| potsawee/selfcheckgpt | https://github.com/potsawee/selfcheckgpt | [INFERRED] | Python | Contains threshold sweep code adaptable for abstention-rate analysis |
| Papers with Code — Selective Prediction | https://paperswithcode.com/task/selective-prediction | [INFERRED] | N/A | Benchmark comparisons including risk-coverage metrics |

---

### Gap Priority Matrix

| Gap ID | Title | Relevance | Impact | Difficulty | Evidence Count | Priority |
|--------|-------|-----------|--------|------------|----------------|----------|
| Gap 1 | No unified comparative benchmark across UE proxy types | PRIMARY | High | Medium | 4 Scholar + 2 Archon + 2 Exa | Critical |
| Gap 2 | Unknown cross-domain transferability of UE estimates | PRIMARY | High | Medium | 3 Scholar + 1 Archon + 2 Exa | High |
| Gap 3 | Abstention rate vs. precision tradeoff not characterized across methods/scales | PRIMARY | High | Medium | 4 Scholar + 2 Archon + 2 Exa | High |

### User Input to Gap Traceability

**Research Question** ("reliably predict factual hallucinations + measurably better selective abstention") directly addressed by:
- Gap 1: "Reliable prediction" requires unified comparison — cannot claim reliability without controlled cross-method evaluation on same benchmarks.
- Gap 3: "Measurably better selective abstention" requires full abstention-rate curves; current literature only provides single operating points.

**SQ1** (proxy-to-correctness correlation): Gap 1 — method comparison is prerequisite for ranking proxy reliability.

**SQ2** (calibration-efficiency tradeoff without fine-tuning): Gap 1 — tradeoff can only be assessed in controlled comparison; Gap 2 — calibration transfer is part of practical efficiency.

**SQ3** (selective prediction precision vs. abstention rate): Gap 3 — directly maps to missing abstention-rate characterization.

**SQ4** (scale-dependent calibration pattern 7B vs. 70B): Gap 3 — scale comparison absent in existing abstention/selective prediction literature.

**SQ5** (cross-domain transfer): Gap 2 — directly maps to missing cross-benchmark calibration transfer study.

---

## 9. Conclusion

### Key Findings
1. **Multiple uncertainty proxy types exist** for LLMs without fine-tuning: single-pass softmax entropy, Monte Carlo self-consistency (SelfCheckGPT), semantic entropy (Kuhn 2023), and verbalized confidence (Kadavath 2022). All can be applied to TriviaQA/NQ/TruthfulQA using existing models.

2. **Semantic entropy outperforms token-level entropy** on open-domain QA by clustering semantically equivalent outputs before computing entropy, avoiding sensitivity to paraphrase variation.

3. **Self-consistency methods work on black-box models** (no logit access needed), making them applicable to API-only LLMs — important for commercial models.

4. **Calibration improves with model scale** (verbalized confidence finding in Kadavath 2022) but this has not been systematically extended to entropy/consistency methods across the 7B–70B range.

5. **No controlled multi-method comparison exists** on the same benchmarks with the same metrics — the primary gap blocking the research question's claims.

6. **Cross-domain transfer of uncertainty estimates is unstudied**: whether a method calibrated on TriviaQA maintains calibration on MMLU or BioASQ is an open question.

7. **Implementations are available**: SelfCheckGPT and Semantic Entropy both have open-source implementations on GitHub that support TriviaQA/NQ evaluation.

### Answer to Detailed Question (Preliminary)
**SQ1** (proxy correlation): Evidence suggests semantic entropy and self-consistency correlate better with factual correctness than raw token entropy, but controlled comparison is missing.

**SQ2** (calibration-efficiency tradeoff): Single-pass entropy is cheapest (one forward pass); self-consistency requires K~20 samples (~20× compute); semantic entropy adds NLI clustering overhead. Verbalized confidence is free but requires large model scale for reliability. Tradeoff not characterized on common benchmarks.

**SQ3** (selective prediction): Selective prediction via uncertainty thresholding is feasible and demonstrated by SelfCheckGPT and Semantic Entropy papers. Exact abstention rates for meaningful precision gains vary — Gap 3 captures this as the key missing piece.

**SQ4** (scale-dependent calibration): Larger models have better-calibrated verbalized confidence. Scale effect on entropy/consistency-based calibration is not established.

**SQ5** (cross-domain transfer): Unknown — Gap 2 identifies this as an open question. Analogies from classification suggest domain shift degrades calibration.

### Phase 2 Readiness
- [x] Research question loaded and confirmed
- [x] 3 PRIMARY research gaps identified, all traceable to research question and sub-questions
- [x] Supporting evidence collected (inferred) for each gap with table format
- [x] Gap priority matrix and traceability summary complete
- [x] Key methods identified: entropy, self-consistency, semantic entropy, verbalized confidence
- [x] Key benchmarks identified: TriviaQA, NaturalQuestions, TruthfulQA, MMLU, BioASQ
- [x] Key implementations located: selfcheckgpt, semantic_uncertainty repos
- [⚠️] All sources [INFERRED] — MCP verification recommended before Phase 2A hypothesis claims

**Phase 2A is ready to proceed.** Gaps 1, 2, and 3 are sufficiently defined to generate testable hypotheses.

### Next Steps
1. **Phase 2A - Hypothesis Generation**: Use this report's 3 gaps to generate testable hypotheses via 4-perspective round table.
2. **Optional MCP verification**: Re-run Steps 3-5 with active MCP servers to upgrade [INFERRED] sources to [VERIFIED] before Phase 2A hypothesis writing.
3. **Priority for Phase 2A**: Gap 1 (controlled multi-method comparison) likely yields the most impactful hypothesis given it directly operationalizes the research question.

---

*Phase: 1 - Targeted Research Gathering*
*Total processing time: ~15 minutes (unattended mode, no-MCP environment)*
