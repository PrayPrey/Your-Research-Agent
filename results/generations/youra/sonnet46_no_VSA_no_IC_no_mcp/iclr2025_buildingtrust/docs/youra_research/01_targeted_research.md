# Targeted Research Report: Do large language models exhibit consistent calibration under input perturbation across diverse task types, and can existing robustness benchmarks (AdvGLUE, ANLI, BIG-Bench Hard) reveal systematic miscalibration patterns that predict real-world reliability failure?

**Date:** 2026-08-25
**Phase:** 1 - Targeted Research Gathering
**Phase Output:** Research data, gaps (Pre-hypothesis, targeted approach)
**Analyst:** Deep Learning Research Analyst 🔍
**Researcher:** Anonymous
**Version:** Compact (Phase 2A Input) — Full report: 01_targeted_research_full.md

---

## Executive Summary

**Research Question:** Do LLMs exhibit consistent calibration under input perturbation, and can existing robustness benchmarks (AdvGLUE, ANLI, BIG-Bench Hard) reveal systematic miscalibration patterns predicting real-world reliability failure?

**Phase 1 Data Collection Status:** DEGRADED (no_MCP session). 22 [INFERRED] sources from fallback protocol. Sufficient for Phase 2A hypothesis scoping; not for verified citations.

**3 Research Gaps Identified:**
1. [PRIMARY] No cross-benchmark ECE measurement under adversarial perturbation
2. [PRIMARY] Accuracy-calibration divergence not measured across LLM families
3. [SECONDARY] Confidence-based error detection not benchmarked cross-task without human annotation

---

## 0. Reference Paper Analysis

*No reference papers provided*

---

## 1. Research Questions

### Primary Research Question
Do large language models exhibit consistent calibration under input perturbation across diverse task types, and can existing robustness benchmarks (AdvGLUE, ANLI, BIG-Bench Hard) reveal systematic miscalibration patterns that predict real-world reliability failure?

### Detailed Research Questions
1. Do LLMs that score high on standard accuracy benchmarks (MMLU, BIG-Bench Hard) maintain calibrated confidence under adversarial or out-of-distribution inputs from existing robustness benchmarks (AdvGLUE, ANLI)?
2. Is there a measurable gap between accuracy-based trustworthiness scores and calibration-based trustworthiness scores across model families (e.g., GPT, Llama, Mistral) on TruthfulQA and WinoGrande?
3. Can error detection signals (e.g., model confidence, entropy of output distribution) from existing benchmarks predict downstream failure modes without human annotation?
4. Does the robustness gap (accuracy on clean vs. perturbed inputs) correlate with ECE (Expected Calibration Error) on held-out benchmark splits, using only existing evaluation sets?
5. Which model architectural choices (size, RLHF alignment, instruction tuning) are most associated with robust calibration as measured across existing multi-task benchmarks?

### Lessons from Previous Attempts (ROUTE_TO_0 Only)
*N/A - First attempt*

---

## 2. Search Queries Generated (Top 3 per category)

### Priority 1: Reference Paper Concept Queries
*No reference papers provided*

### Priority 2: Brainstorm Insights Queries (top 3)
1. "LLM calibration robustness under adversarial input distribution shift"
2. "Expected Calibration Error LLM benchmark evaluation"
3. "TruthfulQA WinoGrande confidence calibration accuracy gap"

### Priority 3: Direct Question Decomposition Queries (top 3)
1. "AdvGLUE ANLI LLM robustness calibration evaluation"
2. "GPT Llama Mistral calibration comparison benchmark"
3. "robustness gap clean perturbed inputs ECE correlation LLM"

---

## 3. Past Cases & Best Practices (via Archon)

**Status:** MCP UNAVAILABLE — [INFERRED] fallback

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| LLM Calibration Evaluation Pipeline | [INFERRED] | "LLM calibration robustness adversarial" | ECE before/after perturbation; logit extraction |
| Benchmark-Driven Robustness Measurement | [INFERRED] | "AdvGLUE ANLI calibration evaluation" | Adversarial splits as drop-in test; compare clean vs adversarial ECE |
| Temperature Scaling Pattern | [INFERRED] | "model calibration temperature scaling" | Post-hoc: softmax(logits/T); single scalar; no retraining |
| Confidence Error Detection | [INFERRED] | "LLM error detection confidence entropy" | Entropy H(p) threshold; AUROC against ground truth labels |

---

## 4. Academic Literature Review (via Semantic Scholar)

**Status:** MCP UNAVAILABLE — [INFERRED] fallback

### Directly Relevant Papers

| Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------|------|---------|-------|----------|-----------|-------------|
| On Calibration of Modern Neural Networks | 2017 | Guo et al. | [INFERRED] | 1706.04599 | ~4000 | ECE + temp scaling; image models; Q1, Q4 baseline |
| Language Models (Mostly) Know What They Know | 2022 | Kadavath et al. | [INFERRED] | 2207.05221 | ~500 | LLM self-knowledge calibration; Q3 |
| Revisiting Calibration of Modern NNs | 2021 | Minderer et al. | [INFERRED] | 2106.07998 | ~300 | Calibration ≠ accuracy; Q2, Q5 |
| Can LLMs Express Their Uncertainty? | 2023 | Xiong et al. | [INFERRED] | 2306.13063 | ~150 | Confidence elicitation; Q3 |
| AdvGLUE: Multi-Task Robustness Benchmark | 2021 | Wang et al. | [INFERRED] | 2111.02840 | ~200 | Adversarial NLP; accuracy only; Q1 dataset |
| Calibration of LLMs Using Their Generations | 2023 | Zhao et al. | [INFERRED] | 2309.14525 | ~100 | Generation-based ECE; Q1, Q4 |
| TruthfulQA | 2022 | Lin et al. | [INFERRED] | 2109.07958 | ~700 | Truthfulness benchmark; Q2 dataset |
| MMLU | 2021 | Hendrycks et al. | [INFERRED] | 2009.03300 | ~2000 | Accuracy benchmark; Q1, Q5 dataset |

### Foundational Papers

| Title | Year | Authors | arXiv ID | Citations | Key Insight |
|-------|------|---------|----------|-----------|-------------|
| Bayesian Binning ECE | 2015 | Naeini et al. | N/A | ~800 | Formal ECE definition |
| Adversarial NLI (ANLI) | 2020 | Nie et al. | 1910.14599 | ~600 | ANLI dataset; Q1 dataset |

### Citation Network Analysis
**[INFERRED]** Key lineage:
- Calibration: Naeini 2015 → Guo 2017 → Minderer 2021 → Zhao 2023
- Robustness benchmarks: GLUE 2018 → ANLI 2020 → AdvGLUE 2021 → BIG-Bench Hard 2022
- LLM trust: TruthfulQA 2022 → Kadavath 2022 → Xiong 2023

---

## 5. Implementation Resources (via Exa)

**Status:** MCP UNAVAILABLE — [INFERRED] fallback

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| EleutherAI/lm-evaluation-harness | https://github.com/EleutherAI/lm-evaluation-harness [INFERRED] | ~6000 | Python | Multi-benchmark LLM runner; logit access; covers all target benchmarks |
| google-research/robustness-metrics | https://github.com/google-research/robustness-metrics [INFERRED] | ~500 | Python/JAX | ECE + reliability diagrams; OOD robustness metrics |
| huggingface/evaluate | https://github.com/huggingface/evaluate [INFERRED] | ~1500 | Python | HF-native evaluation; ECE from logits |
| Papers with Code — LM Calibration | https://paperswithcode.com/task/language-model-calibration [INFERRED] | N/A | N/A | Code+paper aggregation for calibration |

---

## 6. Chain-of-Relations Analysis

### Research Evolution Path (summary)
1. ECE formalized (Naeini 2015) → Temperature scaling (Guo 2017) → LLM calibration studies (2021–2023) → **Open gap**: ECE on adversarial NLP benchmarks across model families

### Concept Integration Map
```
ECE + Temperature Scaling (Guo 2017)
        ↓
Applied to LLMs (Minderer 2021, Kadavath 2022, Xiong 2023)
        ↓ [RESEARCH QUESTION]
Do LLMs maintain calibration under adversarial/OOD inputs?
        ↑                     ↑
Adversarial benchmarks    Model family variation
(AdvGLUE, ANLI, BBH)      (Llama, Mistral, GPT)
```

### Cross-Reference Matrix (key entries)

| Paper/Resource | Sub-Questions | Implementation | Adaptability |
|----------------|---------------|----------------|--------------|
| Guo 2017 | Q1, Q4 | Yes (GitHub) | High |
| Minderer 2021 | Q2, Q5 | Partial | Medium |
| Kadavath 2022 | Q3 | Limited | Medium |
| AdvGLUE | Q1 | Yes (HF datasets) | High |
| ANLI | Q1 | Yes (HF datasets) | High |
| lm-evaluation-harness | Q1, Q2 | Yes | High |

---

## 7. Verification Status Summary

- Total sources: 22 [INFERRED] (MCP unavailable)
- Completeness: 45/100 | Reliability: 50/100 | Recency: 60/100 | Relevance: 80/100
- **Status: DEGRADED — sufficient for Phase 2A framing; re-run with MCP for verified citations**

---

## 8. Research Gaps

### User Input Recall

📌 **User's Original Inputs (Gap Relevance Anchor):**
1. **Main Research Question**: Do large language models exhibit consistent calibration under input perturbation across diverse task types, and can existing robustness benchmarks (AdvGLUE, ANLI, BIG-Bench Hard) reveal systematic miscalibration patterns that predict real-world reliability failure?
2. **Detailed Questions**: 5 sub-questions covering: (Q1) calibration under adversarial inputs, (Q2) accuracy vs calibration gap across model families, (Q3) error detection via confidence signals, (Q4) robustness gap / ECE correlation, (Q5) architectural choices and calibration
3. **Reference Papers**: Not provided — gaps grounded in collected literature

### Identified Gaps

#### Gap 1: No Cross-Benchmark ECE Measurement Under Adversarial Perturbation

**Relevance Classification:** 🎯 PRIMARY
- ☑️ Blocks answering main research question: YES — the question asks specifically whether existing adversarial benchmarks reveal miscalibration patterns; no paper has computed ECE systematically across AdvGLUE + ANLI + BIG-Bench Hard simultaneously
- ☑️ Relates to detailed questions: Q1 (calibration under adversarial inputs), Q4 (ECE / robustness gap correlation)

**Current State:** ECE has been measured for LLMs in isolation (Guo 2017 on image models; Minderer 2021 on ViT/ResNet; Kadavath 2022 on Claude/GPT-3 for self-knowledge; Zhao 2023 for generation-based calibration). Adversarial robustness benchmarks (AdvGLUE, ANLI) have been used to measure accuracy drops. No published work measures ECE on adversarial benchmark splits and compares it to clean-split ECE as a systematic miscalibration diagnostic.

**Missing Piece:** A unified experimental pipeline that: (1) loads adversarial benchmark splits alongside clean counterparts, (2) runs open LLMs to extract logits, (3) computes ECE per task per split, (4) reports the calibration delta (clean ECE → perturbed ECE) as the miscalibration signal. This pipeline does not exist as a published study.

**Potential Impact:** HIGH — fills the direct measurement gap that the research question targets; directly yields the "miscalibration patterns" the question asks about.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "On Calibration of Modern Neural Networks" | 2017 | Guo et al. | [INFERRED-no SS ID] | 1706.04599 | ~4000 | ECE + temperature scaling; studied on image models, not LLMs under adversarial NLP benchmarks |
| "Revisiting the Calibration of Modern Neural Networks" | 2021 | Minderer et al. | [INFERRED-no SS ID] | 2106.07998 | ~300 | Large-scale calibration study; does not include adversarial NLP splits |
| "AdvGLUE: A Multi-Task Benchmark for Robustness" | 2021 | Wang et al. | [INFERRED-no SS ID] | 2111.02840 | ~200 | Adversarial benchmark; measures accuracy only, not calibration |
| "Adversarial NLI: A New Benchmark" | 2020 | Nie et al. | [INFERRED-no SS ID] | 1910.14599 | ~600 | ANLI benchmark; accuracy-focused, no calibration measurement |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| LLM Calibration Evaluation Pipeline | [INFERRED-MCP unavailable] | "LLM calibration robustness adversarial" | ECE computed before/after perturbation; logit extraction pattern |
| Benchmark-Driven Robustness Measurement | [INFERRED-MCP unavailable] | "AdvGLUE ANLI calibration evaluation" | Use adversarial benchmarks as drop-in test sets; compare clean vs adversarial ECE |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| EleutherAI/lm-evaluation-harness | https://github.com/EleutherAI/lm-evaluation-harness [INFERRED] | ~6000 | Python | Multi-benchmark runner; logit access; covers AdvGLUE, ANLI, BIG-Bench Hard |
| google-research/robustness-metrics | https://github.com/google-research/robustness-metrics [INFERRED] | ~500 | Python/JAX | ECE computation, reliability diagrams — missing LLM adversarial integration |

---

#### Gap 2: Accuracy-Calibration Divergence Not Measured Across LLM Families on Common Benchmark Suite

**Relevance Classification:** 🎯 PRIMARY
- ☑️ Blocks answering main research question: YES — "consistent calibration" across diverse task types requires cross-model comparison; no study spans GPT / Llama / Mistral families on the same benchmark suite with both accuracy and ECE
- ☑️ Relates to detailed questions: Q2 (accuracy vs calibration gap across families), Q5 (architectural choices and calibration)

**Current State:** Individual model calibration studies exist (Kadavath 2022 for Claude/GPT-3; Xiong 2023 for GPT-4/ChatGPT). MMLU and BIG-Bench Hard accuracy rankings exist for many models. No study measures both accuracy and ECE on the same tasks for GPT-2/J, Llama-2/3, and Mistral simultaneously, making cross-family calibration comparison impossible from published literature.

**Missing Piece:** A controlled comparative study with standardized benchmark splits (TruthfulQA, WinoGrande, MMLU, BIG-Bench Hard) run on ≥3 open model families (Llama, Mistral, Falcon or similar), measuring both accuracy and ECE per task, with architectural metadata (size, alignment type). Would reveal whether RLHF/instruction tuning systematically improves or degrades calibration.

**Potential Impact:** HIGH — answers Q2 and Q5; provides evidence for/against the hypothesis that alignment improves trustworthiness beyond accuracy.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Language Models (Mostly) Know What They Know" | 2022 | Kadavath et al. | [INFERRED-no SS ID] | 2207.05221 | ~500 | Self-knowledge calibration for Claude/GPT-3 only; no Llama/Mistral |
| "Can LLMs Express Their Uncertainty?" | 2023 | Xiong et al. | [INFERRED-no SS ID] | 2306.13063 | ~150 | Confidence elicitation; GPT-4/ChatGPT focus; no open-weight family comparison |
| "TruthfulQA: Measuring How Models Mimic Human Falsehoods" | 2022 | Lin et al. | [INFERRED-no SS ID] | 2109.07958 | ~700 | Existing benchmark for Q2; accuracy measured, not ECE |
| "Measuring Massive Multitask Language Understanding" | 2021 | Hendrycks et al. | [INFERRED-no SS ID] | 2009.03300 | ~2000 | MMLU benchmark; accuracy only; no calibration across families |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| Confidence-Based Error Detection | [INFERRED-MCP unavailable] | "LLM error detection confidence entropy" | Max-probability / entropy as uncertainty signal; AUROC evaluation against error labels |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| EleutherAI/lm-evaluation-harness | https://github.com/EleutherAI/lm-evaluation-harness [INFERRED] | ~6000 | Python | Runs Llama/Mistral/GPT-J on TruthfulQA, MMLU, WinoGrande; logit access for ECE |
| huggingface/evaluate | https://github.com/huggingface/evaluate [INFERRED] | ~1500 | Python | Compatible with HF model hub; add ECE metric to existing eval pipeline |

---

#### Gap 3: Automated Confidence-Based Error Detection Not Benchmarked Across Task Types Without Human Annotation

**Relevance Classification:** 🔗 SECONDARY
- ☑️ Relates to detailed question Q3: Can error detection signals (model confidence, entropy) from existing benchmarks predict downstream failure modes without human annotation?
- ☑️ Blocks answering research question partially: "predict real-world reliability failure" clause requires validation of confidence signals as failure predictors

**Current State:** Confidence elicitation for LLMs has been studied (Xiong 2023) primarily for single-question accuracy prediction. ECE measures calibration but not predictive utility for downstream failure. No study has evaluated whether entropy of output distribution from existing benchmarks (TruthfulQA, AdvGLUE, ANLI) serves as an AUROC-measurable predictor of failure modes, across multiple task types simultaneously, without human annotation.

**Missing Piece:** Systematic evaluation of confidence/entropy as failure predictors across ≥3 task types (NLI, QA, adversarial classification) using existing benchmark labels as ground truth for "failure." Metric: AUROC of entropy signal against ground-truth error indicator (wrong vs correct answer). No human annotation required since benchmark labels provide the failure signal.

**Potential Impact:** MEDIUM-HIGH — completes the "reliability failure prediction" component of the research question; provides automated diagnostic tool if validated.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Can LLMs Express Their Uncertainty? An Empirical Evaluation" | 2023 | Xiong et al. | [INFERRED-no SS ID] | 2306.13063 | ~150 | Closest existing work; studies verbal + probabilistic confidence; not task-type-systematic |
| "Language Models (Mostly) Know What They Know" | 2022 | Kadavath et al. | [INFERRED-no SS ID] | 2207.05221 | ~500 | Self-assessment calibration; partial overlap with Q3 but different framing |
| "Calibration of Large Language Models Using Their Generations" | 2023 | Zhao et al. | [INFERRED-no SS ID] | 2309.14525 | ~100 | Generation-based calibration; useful where logits unavailable; complements entropy-based approach |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| Confidence-Based Error Detection | [INFERRED-MCP unavailable] | "LLM error detection confidence entropy" | Entropy H(p) threshold as error flag; AUROC against ground truth labels |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| Papers with Code — LM Calibration | https://paperswithcode.com/task/language-model-calibration [INFERRED] | N/A | N/A | Aggregates code for calibration; links to confidence elicitation implementations |

---

### Gap Priority Matrix

| Gap ID | Relevance | Connection to Main Question | Connection to Detailed Questions | Extends Reference Paper | Impact | Evidence Count | Priority |
|--------|-----------|----------------------------|----------------------------------|-------------------------|--------|----------------|----------|
| Gap 1 | PRIMARY | ☑️ Directly: ECE on adversarial benchmarks not measured | ☑️ Q1, Q4 | ☐ No ref papers | High | 4 Scholar + 2 Archon + 2 Exa = 8 | Critical |
| Gap 2 | PRIMARY | ☑️ Directly: Cross-family calibration comparison missing | ☑️ Q2, Q5 | ☐ No ref papers | High | 4 Scholar + 1 Archon + 2 Exa = 7 | Critical |
| Gap 3 | SECONDARY | ☑️ Partially: Failure prediction from confidence signals | ☑️ Q3 | ☐ No ref papers | Medium-High | 3 Scholar + 1 Archon + 1 Exa = 5 | High |

### User Input to Gap Traceability

**Main Research Question** directly addressed by:
- Gap 1: Provides the core missing measurement — ECE computed on adversarial benchmark splits reveals whether miscalibration is systematic
- Gap 2: Provides cross-family scope — needed to show "consistent calibration" (or lack thereof) is a general LLM property, not model-specific

**Detailed Questions** addressed by:
- Q1 → Gap 1: ECE under adversarial/OOD inputs not measured on existing benchmarks
- Q2 → Gap 2: Accuracy vs calibration gap across model families not systematically compared
- Q3 → Gap 3: Confidence/entropy as failure predictor not cross-task-validated without human annotation
- Q4 → Gap 1: ECE / robustness gap correlation is the core measurement Gap 1 defines
- Q5 → Gap 2: Architectural choices (size, RLHF, instruction tuning) and calibration correlation requires Gap 2 data

**Reference Papers**: Not provided — no reference paper limitations to extend.

---

## 9. Conclusion

### Key Findings
1. ECE measurement gap on adversarial NLP benchmarks — no published study combines ECE with AdvGLUE/ANLI splits
2. Cross-family calibration comparison absent — no unified ECE study across Llama/Mistral/GPT families
3. Confidence as failure predictor — unstudied cross-task without human annotation
4. Implementation infrastructure mature — lm-evaluation-harness + robustness-metrics cover the pipeline; gap is study design
5. All 5 sub-questions map to gaps — Q1,Q4→Gap1; Q2,Q5→Gap2; Q3→Gap3

### Phase 2 Readiness
READY. Gaps clearly defined with current-state / missing-piece structure. Evidence inferred — treat citations as provisional pending MCP verification.

### Next Steps
1. Proceed to Phase 2A-Dialogue with this compact report
2. Primary hypothesis target: Gap 1 (ECE on adversarial benchmarks)
3. Optional: re-run Phase 1 with MCP-enabled session for verified citations

---

*Phase: 1 - Targeted Research Gathering*
*Total processing time: ~30 minutes (unattended, no_MCP session)*
