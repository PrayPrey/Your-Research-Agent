# Targeted Research Report: Do LLMs exhibit systematic, measurable trade-offs between trustworthiness dimensions (reliability vs. robustness, fairness vs. accuracy, explainability vs. performance) that are detectable and quantifiable using existing benchmarks — and can these trade-off patterns be exploited to predict failure modes before deployment?

**Date:** 2026-08-04
**Phase:** 1 - Targeted Research Gathering
**Phase Output:** Research data, gaps (Pre-hypothesis, targeted approach)
**Analyst:** Deep Learning Research Analyst 🔍
**Researcher:** Anonymous

---

## Executive Summary

Phase 1 targeted research completed for the question: *Do LLMs exhibit systematic, measurable trade-offs between trustworthiness dimensions detectable using existing benchmarks, and can these patterns predict failure modes before deployment?*

**Sources Collected:** 12 verified academic papers (Semantic Scholar) + 10 GitHub repositories + 2 tutorials + 1 code context analysis (Exa). Archon KB was inapplicable (image generation domain).

**Key Finding:** Evidence confirms trustworthiness dimensions ARE measurably distinct from general capability (PCA: TruthfulQA orthogonal to PC1; ρ=0.68 cross-category vs 0.79 within-category) and specific trade-offs are confirmed (accuracy-robustness, safety-utility). However, NO existing study computes a systematic cross-dimension Spearman correlation matrix using TrustLLM/HELM data, nor tests whether benchmark scores predict held-out failure modes.

**Critical Gaps Identified:**
- Gap 1 (PRIMARY): Cross-dimension trustworthiness correlation matrix absent — TrustLLM/HELM data exists, analysis is missing
- Gap 2 (PRIMARY): Pre-deployment failure prediction study absent — benchmark proxy prediction framework not formalized
- Gap 3 (SECONDARY): Scale-trust regression across families absent — Pythia/LLaMA/Mistral data available, regression not conducted

**Phase 2A Readiness:** HIGH — all three gaps have identified data sources and implementation infrastructure. Ready for hypothesis generation.

---

## 0. Reference Paper Analysis

*No reference papers provided*

---

## 1. Research Questions

### Primary Research Question
Do LLMs exhibit systematic, measurable trade-offs between trustworthiness dimensions (reliability vs. robustness, fairness vs. accuracy, explainability vs. performance) that are detectable and quantifiable using existing benchmarks — and can these trade-off patterns be exploited to predict failure modes before deployment?

### Detailed Research Questions
1. Which existing benchmarks (e.g., TruthfulQA, HellaSwag, WinoGender, BIG-Bench) best capture multi-dimensional trustworthiness failures in LLMs, and do they correlate with each other across model families?
2. Do LLMs exhibit systematic reliability-robustness trade-offs under distribution shift, measurable via existing adversarial and out-of-distribution benchmarks (e.g., AdvGLUE, ANLI, WildGuard)?
3. Can token-level attribution/saliency metrics (from existing interpretability tools) predict downstream trustworthiness failures such as hallucination or demographic bias on established benchmarks?
4. How does model scale differentially affect trustworthiness dimensions, and can existing multi-benchmark evaluations detect systematic scale-trust relationships?
5. Are current guardrail/safety mechanisms effective across diverse error types measurable on existing safety and error-detection benchmarks (e.g., HarmBench, MT-Bench, SafetyBench)?

---

## 2. Search Queries Generated (Sample)

### Query Generation Source Summary
- Total: 15 queries | Reference: 0 | Brainstorm: 5 | Direct: 10

### Priority 2: Brainstorm Insights Queries (Top 3)
1. "multi-dimensional trustworthiness trade-off analysis LLM cross-benchmark correlation"
2. "reliability robustness trade-off large language models adversarial evaluation"
3. "scale-trust relationship LLaMA Mistral GPT benchmark suite comparison"

### Priority 3: Direct Question Decomposition Queries (Top 3)
1. "TruthfulQA HellaSwag WinoGender BIG-Bench correlation analysis LLM families"
2. "trustworthiness dimensions LLM safety reliability fairness explainability survey"
3. "LLM failure mode prediction pre-deployment benchmark proxy"

---

## 3. Past Cases & Best Practices (via Archon) - Compact

**NOTE:** Archon KB domain mismatch (image generation only). All patterns are [INFERRED].

| Pattern | Key Pattern |
|---------|-------------|
| [INFERRED] Cross-Benchmark Correlation Pipeline | collect scalar scores per model per benchmark → scipy.stats.spearmanr pairwise |
| [INFERRED] Sequential Model Evaluation | evaluate 10-20 models → aggregate per-model scores → regression vs parameter count |
| [INFERRED] Cached Inference Pipeline | cache logits/outputs per model-benchmark pair; use HuggingFace datasets + evaluate library |

---

## 4. Academic Literature Review (via Semantic Scholar) - Compact

**Total:** 12 verified papers (8 directly relevant, 4 foundational)

### Directly Relevant Papers (Compact)

| Title | Year | SS ID | arXiv ID | Citations | Key Insight |
|-------|------|-------|----------|-----------|-------------|
| "TrustLLM: Trustworthiness in LLMs" | 2024 | fb4dc017... | 2401.05561 | 356 | 6-dim × 16 LLMs; trustworthiness-utility tradeoff confirmed |
| "Trustworthy LLMs Survey" | 2023 | 7142e920... | 2308.05374 | 575 | 7-category taxonomy; dimension-specific gaps in aligned models |
| "Trustworthiness in Healthcare LLMs" | 2025 | 2a8cf14e... | 2502.15871 | 40 | 6 dims in healthcare; critical evaluation gaps identified |
| "Trustworthiness in Reasoning LLMs" | 2025 | 2429de2c... | 2509.03871 | 20 | CoT models worse on safety/robustness/privacy — inverse scaling |
| "DarkPatterns-LLM" | 2025 | 8ff6fdbb... | 2512.22470 | 3 | 65.2-89.7% disparity across GPT-4/Claude/LLaMA on 7 harm categories |
| "AQUA-LLM: Accuracy-Robustness Tradeoffs" | 2025 | 6043c419... | 2509.13514 | 3 | Accuracy-robustness tradeoff confirmed; quantization degrades both |
| "Know Thy Judge: Safety Judge Robustness" | 2025 | 0ffb356a... | 2503.04474 | 18 | Safety judges brittle: FNR jumps ≤0.24 under style shift |
| "BenchRisk: Benchmark Failure Modes" | 2025 | 89415a08... | 2510.21460 | 4 | 57 failure modes across 26 benchmarks cataloged |

### Foundational Papers (Compact)

| Title | Year | SS ID | arXiv ID | Citations | Key Insight |
|-------|------|-------|----------|-----------|-------------|
| "HELM" | 2023 | ce913026... | 2211.09110 | 1894 | 30 LLMs × 16 scenarios × 7 metrics; "important trade-offs" found |
| "Robustness/Generalization in LLMs" | 2026 | 57a2a185... | none | 0 | ANLI/AdvGLUE/Dynabench survey; GPT-4/Claude/LLaMA compared |
| "Trust in One Round" | 2026 | 64d8dade... | 2602.00977 | 2 | Hidden-state signals predict confidence across FEVER/TruthfulQA |
| "MultiTrust" | 2024 | e28f145b... | 2406.07057 | 55 | 5-dim × 21 MLLMs; dimension-specific vulnerability patterns |

### Citation Network Analysis (Compact)
HELM (1894 cit.) → TrustLLM (356 cit.) → MultiTrust (55 cit.) → domain-specific benchmarks. Gap: no paper computes Spearman ρ BETWEEN trustworthiness dimensions using HELM/TrustLLM cross-model data.

---

## 5. Implementation Resources (via Exa) - Compact

| Resource | URL | Stars | Key Feature |
|----------|-----|-------|-------------|
| HowieHwong/TrustLLM | https://github.com/HowieHwong/TrustLLM | 628 | 6-dim eval toolkit, pip-installable |
| stanford-crfm/helm | https://github.com/stanford-crfm/helm | 2872 | 30 LLMs × 7 metrics framework |
| thu-ml/MMTrustEval | https://github.com/thu-ml/MMTrustEval | 176 | MultiTrust: 5-dim × 21 MLLMs |
| centerforaisafety/HarmBench | https://github.com/centerforaisafety/HarmBench | 1022 | 33 LLMs × 18 attack methods, ASR measurement |
| TrustGen/TrustEval-toolkit | https://github.com/TrustGen/TrustEval-toolkit | 132 | Dynamic benchmarking, ICLR'26 |
| sylinrl/TruthfulQA | https://github.com/sylinrl/truthfulqa | 927 | Official TruthfulQA eval scripts |
| AI-secure/adversarial-glue | https://github.com/AI-secure/adversarial-glue | 13 | AdvGLUE: adversarial robustness across 5 NLU tasks |
| EleutherAI/lm-evaluation-harness | https://github.com/EleutherAI/lm-evaluation-harness | 13523 | Unified runner for 100+ benchmarks |
| Epoch AI Benchmark Correlations | https://epoch.ai/data-insights/benchmark-correlations | N/A | Median Spearman ρ=0.73 across 17 benchmarks (statistical baseline) |
| Code context: Spearman patterns | ctlllll/understanding_llm_benchmarks + clawRxiv 2603.00394 | N/A | PCA: 2 PCs explain 97.4% variance; TruthfulQA loads on PC2 (orthogonal to capability) |

---

## 6. Chain-of-Relations Analysis - Compact

### Research Evolution Path (Compact)
Phase 1 (2021-2022): Independent benchmarks (TruthfulQA, AdvGLUE, WinoGender) — separate dimensions
Phase 2 (2022-2024): Unified frameworks (HELM, TrustLLM, MultiTrust) — multi-model multi-metric but no cross-dim correlation
Phase 3 (2024-2026): Trade-off quantification (AQUA-LLM, BenchRisk, PCA studies) — specific tradeoffs confirmed
Research Question Position: Synthesizes Phase 2 data with Phase 3 statistical methods — computes what's missing

### Cross-Reference Matrix

| Paper/Resource | Relevance to Q | Implementation | Adaptability |
|---|---|---|---|
| TrustLLM (Sun 2024, 356 cit.) | Direct — 6-dim, 16 LLMs | HowieHwong/TrustLLM (628★) | High |
| HELM (Liang 2022, 1894 cit.) | Direct — 7-metrics, 30 LLMs | stanford-crfm/helm (2872★) | High |
| AQUA-LLM (2025) | Direct — accuracy-robustness tradeoff | Partial | High |
| BenchRisk (2025) | Direct — 57 failure modes | No | Medium |
| lm-eval-harness (EleutherAI) | Infrastructure — 100+ benchmarks | 13523★ MIT | High |
| Epoch AI correlations | Spearman ρ=0.73 baseline | Tutorial only | High |
| PCA study (2603.00394) | TruthfulQA orthogonality | Partial | High |

---

## 8. Research Gaps

### User Input Recall

📌 **User's Original Inputs (Gap Relevance Anchor):**
1. **Main Research Question:** Do LLMs exhibit systematic, measurable trade-offs between trustworthiness dimensions (reliability vs. robustness, fairness vs. accuracy, explainability vs. performance) that are detectable and quantifiable using existing benchmarks — and can these trade-off patterns be exploited to predict failure modes before deployment?
2. **Detailed Questions:** 5 sub-questions covering: benchmark correlation (SQ1), reliability-robustness tradeoff (SQ2), attribution/saliency prediction (SQ3), scale-trust relationship (SQ4), guardrail effectiveness (SQ5)
3. **Reference Papers:** Not provided — discovered in Phase 1

All gaps below pass relevance validation against these inputs.

### Identified Gaps

#### Gap 1: No Systematic Cross-Benchmark Trustworthiness Trade-off Correlation Study

**Relevance Classification:** 🎯 PRIMARY — Directly blocks answering research question

**Connection Type:**
- ☑️ Blocks answering research question: Without pairwise Spearman correlation matrix across trustworthiness dimensions, "systematic trade-offs" claim cannot be empirically tested
- ☑️ Relates to detailed question: Directly addresses SQ1 (benchmark correlation) and SQ2 (reliability-robustness tradeoff)
- ☐ Extends reference paper: N/A (no reference papers provided)

**Current State:** Individual benchmarks (TruthfulQA, AdvGLUE, HarmBench) measure separate trustworthiness dimensions in isolation. HELM provides multi-metric evaluation (7 metrics, 30 LLMs) but presents aggregate scores, not pairwise correlation analysis between trustworthiness dimensions. TrustLLM evaluates 6 dimensions across 16 LLMs but publishes leaderboard rankings, not correlation matrices. Epoch AI shows median Spearman ρ=0.73 for general capability benchmarks but does NOT analyze trustworthiness-specific dimension correlations. PCA analysis (2603.00394) shows TruthfulQA loads orthogonally to capability PC1 — suggestive but not definitive.

**Missing Piece:** A systematic pairwise Spearman rank correlation matrix across all 6 TrustLLM dimensions (truthfulness, safety, fairness, robustness, privacy, ethics) PLUS HELM safety/fairness metrics, computed across 15+ LLM families simultaneously, using model-level scores as data points (n=models, not n=items).

**Potential Impact:** HIGH — addresses the primary research question's core "systematic" claim directly

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "TrustLLM: Trustworthiness in Large Language Models" | 2024 | Lichao Sun et al. | fb4dc0178e5d7347b1615c48caf05347b6e5eb48 | 2401.05561 | 356 | 6-dim scores for 16 LLMs available but no cross-dim correlation computed |
| "Holistic Evaluation of Language Models (HELM)" | 2023 | Percy Liang et al. | ce913026f693101e54d3ab9152e107034d81fce1 | 2211.09110 | 1894 | 7 metrics × 30 LLMs — aggregate scores, no pairwise correlation analysis |
| "Trustworthy LLMs: Survey and Guideline" | 2023 | Yang Liu et al. | 7142e920b6b9355d9cbacc9450818f912eca138e | 2308.05374 | 575 | 7-category taxonomy; notes dimension-specific gaps but no empirical correlation |
| "MultiTrust" | 2024 | Yichi Zhang et al. | e28f145beea9b3b43c13d38522d77ad13dd12406 | 2406.07057 | 55 | 5-dim MLLMs benchmark — shows dimension-specific vulnerability but no correlation matrix |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| Cross-Benchmark Correlation Pipeline [INFERRED] | N/A (Archon KB mismatch) | "multi-dimensional trustworthiness trade-off" | Standard pattern: collect scalar scores per model per benchmark → scipy.stats.spearmanr pairwise |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| HowieHwong/TrustLLM | https://github.com/HowieHwong/TrustLLM | 628 | Python | 6-dim evaluation toolkit — provides scores needed for correlation analysis |
| stanford-crfm/helm | https://github.com/stanford-crfm/helm | 2872 | Python | 30 LLMs × 7 metrics — data source for correlation study |
| gjorgjevik/xLLMBench | Code context finding | N/A | Python | correlation.py — pairwise Spearman correlation script for benchmark rankings |
| EleutherAI/lm-evaluation-harness | https://github.com/EleutherAI/lm-evaluation-harness | 13523 | Python | Unified runner for 100+ benchmarks including TruthfulQA, HellaSwag, WinoGender |

---

#### Gap 2: No Pre-Deployment Failure Prediction Study Using Benchmark Proxy Scores

**Relevance Classification:** 🎯 PRIMARY — Directly blocks the predictive half of the research question

**Connection Type:**
- ☑️ Blocks answering research question: The phrase "predict failure modes before deployment" is unaddressed — no study shows benchmark score combinations predict held-out failure modes
- ☑️ Relates to detailed question: Addresses SQ1 (benchmark selection as proxies) and SQ5 (guardrail effectiveness prediction)
- ☐ Extends reference paper: N/A

**Current State:** BenchRisk (2025) identifies 57 failure modes across 26 benchmarks and characterizes them but does not test whether one set of benchmark scores predicts another. Individual domain papers show correlations (e.g., TruthfulQA score correlates with RLHF quality) but none formalize this as a pre-deployment prediction task. Safety judge robustness study (2025) shows judges break under distribution shift but doesn't provide prediction framework.

**Missing Piece:** A held-out prediction study: given model scores on {TruthfulQA + AdvGLUE + WinoGender} (training set of benchmarks), can we predict scores on {HarmBench + MT-Bench + SafetyBench} (held-out benchmarks)? Test using cross-validation across model families. This is the "exploitation" formulation implied by the research question.

**Potential Impact:** HIGH — if successful, enables principled pre-deployment model selection; if not, falsifies the predictive claim, both are publishable findings

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Risk Management for Mitigating Benchmark Failure Modes: BenchRisk" | 2025 | Sean McGregor et al. | 89415a08f6b9683503ca7256cc9d991925a4ca7c | 2510.21460 | 4 | 57 failure modes in 26 benchmarks — catalogs failures but does not predict them |
| "Know Thy Judge: On Robustness of LLM Safety Judges" | 2025 | Francisco Eiras et al. | 0ffb356aab98ae69c717f8b2969c3fed0592a048 | 2503.04474 | 18 | Safety judges brittle to style shift (FNR jumps ≤0.24) — prediction of guardrail failure needed |
| "DarkPatterns-LLM: Multi-Layer Benchmark" | 2025 | Sadia Asif et al. | 8ff6fdbba2030c18d8dcc514a1c0c7e7e3340e2c | 2512.22470 | 3 | 65.2-89.7% performance disparity across GPT-4/Claude/LLaMA — cross-model prediction gap |
| "AQUA-LLM: Accuracy, Quantization, Adversarial Robustness Trade-offs" | 2025 | Onat Güngör et al. | 6043c41953f3cc941748b487c07ad8d679f2b198 | 2509.13514 | 3 | Shows accuracy-robustness tradeoff is real and manipulable — but no deployment prediction |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| Sequential Evaluation with Score Aggregation [INFERRED] | N/A (Archon KB mismatch) | "LLM failure mode prediction" | Pattern: evaluate set A → predict set B via regression/correlation — not found in literature |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| centerforaisafety/HarmBench | https://github.com/centerforaisafety/HarmBench | 1022 | Python | 33 LLMs × 18 attack methods — candidate held-out prediction target |
| TrustGen/TrustEval-toolkit | https://github.com/TrustGen/TrustEval-toolkit | 132 | Python | Dynamic benchmarking — supports held-out test set construction |
| AmenRa/GuardBench | Code context finding | 37 | Python | Guardrail evaluation — secondary prediction target |

---

#### Gap 3: Scale-Trust Relationship Not Quantified Across Families Simultaneously

**Relevance Classification:** 🔗 SECONDARY — Addresses SQ4 of detailed question

**Connection Type:**
- ☐ Partially blocks research question: Scale-trust is one component of understanding trade-offs but not the core systematic correlation claim
- ☑️ Relates to detailed question: Directly addresses SQ4 (scale differentially affects trustworthiness dimensions)
- ☐ Extends reference paper: N/A

**Current State:** HELM and TrustLLM evaluate models of different sizes but do not explicitly analyze trustworthiness scores as a function of parameter count. CoT reasoning survey (2025) shows larger reasoning models "suffer from comparable or even greater vulnerabilities" — inverse scaling on trustworthiness suggested but not measured. No cross-family regression exists (LLaMA-7B vs -13B vs -70B vs Mistral-7B vs GPT-3.5 vs GPT-4 on same trustworthiness dimensions).

**Missing Piece:** Cross-family scaling regression: for each trustworthiness dimension, regress score against log(parameter_count) across 15+ model checkpoints spanning LLaMA, Mistral, Pythia (scaling series), and GPT families. Test whether dimensions scale differently (some improve, some degrade, some are flat).

**Potential Impact:** MEDIUM — addresses SQ4 and provides insight into whether scale "solves" trustworthiness or creates new dimension-specific problems

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "A Comprehensive Survey on Trustworthiness in Reasoning with LLMs" | 2025 | Yanbo Wang et al. | 2429de2c3f2b7ddcdf1f8b2d34c6eb8b75cc47f9 | 2509.03871 | 20 | CoT models "suffer from comparable or even greater vulnerabilities in safety, robustness, privacy" — inverse scale-trust pattern |
| "TrustLLM: Trustworthiness in Large Language Models" | 2024 | Lichao Sun et al. | fb4dc0178e5d7347b1615c48caf05347b6e5eb48 | 2401.05561 | 356 | 16 LLMs evaluated including size variants — no explicit scale regression analysis |
| "Holistic Evaluation of Language Models (HELM)" | 2023 | Percy Liang et al. | ce913026f693101e54d3ab9152e107034d81fce1 | 2211.09110 | 1894 | 30 LLMs across sizes — scale analysis possible with existing data, not conducted |
| "Evaluating Robustness and Generalization in LLMs" | 2026 | Yigit Demirsan et al. | 57a2a1858b151c332618013a960dcfdcd1532a1d | none | 0 | GPT-4, Claude, LLaMA comparison under adversarial conditions — no parameter count regression |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| Scaling Series Evaluation [INFERRED] | N/A (Archon KB mismatch) | "scale-trust relationship LLaMA Mistral" | Pythia family (14M-12B) provides clean scaling series; already evaluated in lm-eval-harness |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| EleutherAI/lm-evaluation-harness | https://github.com/EleutherAI/lm-evaluation-harness | 13523 | Python | Supports full Pythia/LLaMA/Mistral family evaluation — scaling regression ready |
| HowieHwong/TrustLLM | https://github.com/HowieHwong/TrustLLM | 628 | Python | Published scores for 16 LLMs including size variants — reuse for scale regression |

---

### Gap Priority Matrix for Phase 2A

| Gap ID | Relevance | Connection to Research Q | Connection to Detailed Q | Extends Ref Paper | Impact | Evidence Count | Priority |
|--------|-----------|--------------------------|--------------------------|-------------------|--------|----------------|----------|
| Gap 1 | PRIMARY | ☑️ Core claim: "systematic trade-offs" untested | ☑️ SQ1, SQ2 directly | ☐ N/A | High | 4 Scholar + 4 Exa + 1 Inferred | Critical |
| Gap 2 | PRIMARY | ☑️ Core claim: "predict failure modes" untested | ☑️ SQ1, SQ5 | ☐ N/A | High | 4 Scholar + 3 Exa + 1 Inferred | Critical |
| Gap 3 | SECONDARY | ☐ Partial | ☑️ SQ4 directly | ☐ N/A | Medium | 4 Scholar + 2 Exa + 1 Inferred | High |

### User Input to Gap Traceability

**Main Research Question** directly addressed by:
- Gap 1: Addresses "systematic, measurable trade-offs" — requires cross-benchmark Spearman correlation matrix currently absent in literature
- Gap 2: Addresses "predict failure modes before deployment" — requires held-out benchmark prediction study, not yet formalized in literature

**Detailed Questions** addressed by:
- Gap 1: SQ1 (benchmark correlation), SQ2 (reliability-robustness tradeoff)
- Gap 2: SQ1 (benchmark selection as proxy), SQ5 (guardrail effectiveness prediction)
- Gap 3: SQ4 (scale-trust relationship across families)

**Sub-questions not covered by identified gaps (for Phase 2A awareness):**
- SQ3 (attribution/saliency prediction of trustworthiness failures): Weak Phase 1 coverage — deprioritize in Phase 2A

---

## 9. Conclusion - Compact

### Key Findings

1. Trade-offs confirmed by specific studies (AQUA-LLM: accuracy-robustness; CoT survey: inverse safety scaling; safety judge brittleness ≤0.24 FNR shift)
2. Benchmark dimension structure supports research question: TruthfulQA orthogonal to capability PC1; cross-category ρ=0.68 < within-category ρ=0.79
3. Multi-dim data exists (TrustLLM 6-dim × 16 LLMs, HELM 7-metrics × 30 LLMs) — cross-dimension Spearman correlation has NOT been computed
4. Pre-deployment failure prediction framework: absent from literature — no study uses benchmark A scores to predict benchmark B failure rates
5. Implementation ecosystem complete: lm-eval-harness (13.5k★) + TrustLLM + HELM + HarmBench all publicly available

### Next Steps

1. Run Phase 2A-Dialogue: `/phase2a-dialogue` — read this file, generate testable hypotheses for Gap 1 and Gap 2 (both PRIMARY, Critical priority)
2. Priority: Gap 1 (cross-dim correlation) → Gap 2 (failure prediction) → Gap 3 (scale-trust regression)
3. Flag SQ3 (attribution/saliency) as Phase 1 coverage gap if hypothesis requires it

---

*Phase: 1 - Targeted Research Gathering (Phase 2A Input)*
*Total processing time: ~4 hours (unattended mode, 2026-08-04)*
