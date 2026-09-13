# Targeted Research Report: Population-Level Confidence Frequency Calibration in Instruction-Tuned LLMs

**Generated:** 2026-03-24
**Phase:** 1 - Targeted Research Gathering (COMPACT VERSION for Phase 2A)
**Analyst:** Deep Learning Research Analyst 🔍
**Researcher:** Anonymous
---

## Executive Summary

This Phase 1 targeted research investigates **population-level confidence frequency calibration in instruction-tuned LLMs**, examining whether post-hoc temperature scaling can significantly reduce Expected Calibration Error (ECE). This is the 8th attempt (ROUTE_TO_0) pivoting to aggregate population-level statistics to avoid confound saturation from per-instance approaches.

**Key Findings:** Guo et al. 2017 (7,452 citations) establishes temperature scaling foundation; RLHF causes LLM overconfidence; DACA/CCPS/ActCab show 15-55% ECE improvements; gpleiss/temperature_scaling provides canonical implementation.

**Gaps:** (1) Qwen-family uncharacterized, (2) Domain-wise MMLU breakdown missing, (3) Effect size variance unclear.

**Phase 2A Readiness:** HIGH

---

## 0. Reference Paper Analysis

*No reference papers provided. 8th attempt (ROUTE_TO_0) - searches focus on calibration literature.*

---

## 1. Research Questions

### Primary Research Question
Can population-level confidence frequency analysis reveal systematic miscalibration patterns in instruction-tuned LLMs, and does post-hoc temperature scaling significantly reduce ECE on standard QA benchmarks?

### Detailed Research Questions
1. Baseline ECE of Qwen2.5-7B-Instruct on MMLU/TruthfulQA?
2. Systematic over/under-confidence patterns in reliability diagrams?
3. Temperature scaling ECE reduction magnitude?
4. Domain variation (STEM vs. humanities)?
5. Model size robustness?

### ROUTE_TO_0 Context
7 previous failures (entropy confounds, H_rest wrong direction, attention weak, verbalized cascade, p_max task mismatch). **Paradigm shift:** Population-level aggregate statistics via ECE/reliability diagrams.

---

## 2. Search Queries (Top 3 per Category)

**Failure-Aware (HIGHEST):** `"calibration LLM without per-instance uncertainty"`, `"population level confidence calibration"`, `"temperature scaling post-hoc calibration"`

**Brainstorm:** `"reliability diagrams neural networks"`, `"ECE Expected Calibration Error LLM"`, `"post-hoc calibration methods"`

**Direct:** `"Guo temperature scaling calibration"`, `"MMLU TruthfulQA calibration evaluation"`, `"overconfidence underconfidence LLM"`

---

## 3. Past Cases (Archon) - COMPACT

| Case/Pattern | KB Entry ID | Query | Key Insight |
|--------------|-------------|-------|-------------|
| [NOT_FOUND] | N/A | "ECE calibration LLM" | KB focused on diffusion models |
| [INFERRED] Model Evaluation | N/A | general | Bin-wise confidence-accuracy comparison |
| [INFERRED] Post-Hoc Modification | N/A | general | Temperature scaling like quantization post-hoc |
| [VERIFIED] InstructGPT | 60f7c35d-c378-4f3d-847a-d68e377220a3 | "TruthfulQA" | Evaluation methods (not calibration) |

---

## 4. Academic Papers (Scholar) - COMPACT

| Paper | Year | SS ID | arXiv | Cite | Key Insight |
|-------|------|-------|-------|------|-------------|
| On Calibration of Modern NNs (Guo) | 2017 | d65ce2b8300541414bfe51d03906fca72e93523c | 1706.04599 | 7,452 | Temperature scaling + ECE foundation |
| Just Ask for Calibration (Tian) | 2023 | ab4ce5dda7ad4d9032995c9c049a89d65723c6aa | 2305.14975 | 598 | Verbalized > token probs for RLHF |
| DACA (Luo) | 2025 | c95e088f14e7de85161483043f05518504a74f07 | 2505.16690 | 6 | PLM-PoLM disagreement; 15% ECE improvement |
| CCPS (Khanmohammadi) | 2025 | ab24ae5b6e6827ad5e0050d451e3770f966762f8 | 2505.21772 | 9 | 55% ECE reduction on MMLU |
| Revisiting UE (Tao) | 2025 | 2fc250ddefbcf9ce5d70c6a8a37b932f4320f782 | 2505.23854 | 8 | 80 LLM study on MMLU-Pro |
| Flex-ECE (de Oliveira) | 2025 | 65dcf07cef2e0c715c5c8013b43b52725982a2a9 | N/A | 6 | Post-hoc reduces ECE 24-47% → 0.1-4% |
| ActCab (Liu) | 2024 | 332c86a4621500c3b8a7e70d132c38ce003c20f8 | 2406.13230 | 14 | 39% ECE reduction on TruthfulQA |
| Calibration Across Layers (Joshi) | 2025 | 1acca0c4b5f9963f7d262f793bf6a7cfda188a96 | 2511.00280 | 4 | Mechanistic calibration in LLMs |
| Deep Ensembles (Lakshminarayanan) | 2016 | 802168a81571dde28f5ddb94d84677bc007afa7b | N/A | 7,131 | Ensemble-based calibration |

---

## 5. Implementation Resources (Exa) - COMPACT

| Resource | URL | Stars | Language | Key Feature |
|----------|-----|-------|----------|-------------|
| gpleiss/temperature_scaling | https://github.com/gpleiss/temperature_scaling | 1,167 | Python | Canonical Guo et al. implementation |
| dholzmueller/probmetrics | https://github.com/dholzmueller/probmetrics | 55 | Python | Modern streaming ECE |
| Jonathan-Pearce/calibration-toolbox | https://github.com/Jonathan-Pearce/calibration-toolbox | 74 | Python | ECE/MCE/Brier/reliability diagrams |
| ml-stat-Sustech/DACA | https://github.com/ml-stat-Sustech/Disagreement-Aware-Calibration | N/A | Python | LLM-specific DACA method |
| TorchMetrics | https://lightning.ai/docs/torchmetrics/stable/classification/calibration_error.html | Official | Python | PyTorch ecosystem ECE |
| netcal | https://github.com/fabiankueppers/calibration-framework | N/A | Python | Comprehensive calibration toolkit |

---

## 6. Chain-of-Relations - COMPACT

**Evolution Path:**
```
Platt Scaling (1999) → Guo et al. T-Scaling (2017, 7,452 cites) → LLM Calibration (2023-25)
                                                                    ├── Tian (verbalized)
                                                                    ├── DACA (disagreement)
                                                                    └── CCPS (perturbation)
```

**Cross-Reference Matrix:**

| Source | Relevance | Implementation | Adaptability |
|--------|-----------|----------------|--------------|
| Guo 2017 | FOUNDATIONAL | gpleiss/temp_scaling | HIGH |
| Tian 2023 | HIGH | N/A | MEDIUM |
| DACA 2025 | HIGH | GitHub repo | HIGH |
| probmetrics | HIGH | Yes | HIGH |

---

## 7. Verification Summary - COMPACT

- **Total Sources:** 24 | **Verified:** 83% | **Quality:** 90.5/100
- **Scholar:** 14 papers, 100% success, HIGH relevance
- **Exa:** 11 resources, 100% success, HIGH relevance
- **Archon:** 1 verified, 2 not found, 2 inferred (KB focused on diffusion)

---

## 8. Research Gaps (FULL - CRITICAL FOR PHASE 2A)

### User Input Recall

📌 **User's Original Inputs:**

1. **Main Research Question**: Can population-level confidence frequency analysis reveal systematic miscalibration patterns in instruction-tuned LLMs, and does post-hoc temperature scaling significantly reduce Expected Calibration Error (ECE) on standard QA benchmarks without requiring task-specific modifications?

2. **Detailed Questions**:
   - Q1: What is the baseline ECE of instruction-tuned LLMs (e.g., Qwen2.5-7B-Instruct) on MMLU and TruthfulQA?
   - Q2: Do reliability diagrams show systematic over-confidence or under-confidence patterns?
   - Q3: Does temperature scaling (learned T) significantly reduce ECE compared to no calibration?
   - Q4: How does calibration vary across domains (STEM vs. humanities vs. social science)?
   - Q5: Is calibration improvement robust across different model sizes?

3. **Reference Papers**: Not provided (8th attempt - ROUTE_TO_0 recovery from 7 failed approaches)

4. **Context from ROUTE_TO_0**: Previous approaches failed due to per-instance confounds; this attempt uses population-level aggregate statistics to avoid those issues.

### Identified Gaps

#### Gap 1: Limited Qwen-Family Calibration Studies

**Relevance Classification:** 🎯 PRIMARY

**Connection Type:**
- ☑️ Blocks answering research_question: Most calibration studies use GPT/Llama families; Qwen2.5-7B-Instruct calibration characteristics unknown
- ☑️ Relates to detailed_question Q1: Baseline ECE for Qwen specifically not established in literature
- ☐ Extends reference_papers limitation: N/A (no reference papers)

**Current State:** Existing LLM calibration studies (Tian 2023, DACA 2025, Revisiting UE 2025) primarily evaluate GPT-3.5/4, Llama-2/3, and Claude families. Qwen models have limited calibration characterization.

**Missing Piece:** Baseline ECE measurements and reliability diagram patterns specifically for Qwen2.5-7B-Instruct on MMLU and TruthfulQA benchmarks. Without this, we cannot establish whether our findings generalize to Qwen architecture.

**Potential Impact:** HIGH - Directly blocks answering the research question for the target model family.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Revisiting Uncertainty Estimation and Calibration of Large Language Models" | 2025 | Tao et al. | 2fc250ddefbcf9ce5d70c6a8a37b932f4320f782 | 2505.23854 | 8 | Studies 80 LLMs but Qwen coverage unclear; focuses on MMLU-Pro |
| "Just Ask for Calibration" | 2023 | Tian et al. | ab4ce5dda7ad4d9032995c9c049a89d65723c6aa | 2305.14975 | 598 | Evaluated GPT-3.5, Claude; no Qwen |
| "Your Pre-trained LLM is Secretly an Unsupervised Confidence Calibrator" | 2025 | Luo et al. | c95e088f14e7de85161483043f05518504a74f07 | 2505.16690 | 6 | DACA method on Llama-3; Qwen not tested |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| *No Qwen calibration cases found* | N/A | "Qwen instruction tuning" | QLoRA/quantization results only |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| gpleiss/temperature_scaling | https://github.com/gpleiss/temperature_scaling | 1,167 | Python | Reference implementation; model-agnostic |
| probmetrics | https://github.com/dholzmueller/probmetrics | 55 | Python | ECE calculation; framework-agnostic |

---

#### Gap 2: Domain-Wise Calibration Breakdown on MMLU Not Systematically Reported

**Relevance Classification:** 🎯 PRIMARY

**Connection Type:**
- ☑️ Blocks answering research_question: "standard QA benchmarks" implies understanding domain variation
- ☑️ Relates to detailed_question Q4: Directly asks about STEM vs. humanities vs. social science calibration variation
- ☐ Extends reference_papers limitation: N/A

**Current State:** MMLU contains 57 subjects across 4 categories (STEM, humanities, social science, other). Most calibration papers report aggregate ECE across all subjects. Few provide subject-level or category-level calibration breakdowns.

**Missing Piece:** Systematic analysis of whether LLMs are better calibrated on some domain types (e.g., factual STEM) vs. others (e.g., interpretive humanities). This is critical for understanding where post-hoc calibration helps most.

**Potential Impact:** HIGH - Domain-specific calibration insights would reveal practical deployment considerations.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Calibration Across Layers" | 2025 | Joshi et al. | 1acca0c4b5f9963f7d262f793bf6a7cfda188a96 | 2511.00280 | 4 | Studies MMLU but aggregate ECE only |
| "Calibrating LLM Confidence by Probing Perturbed Representation Stability" | 2025 | Khanmohammadi et al. | ab24ae5b6e6827ad5e0050d451e3770f966762f8 | 2505.21772 | 9 | MMLU/MMLU-Pro evaluation; no domain breakdown |
| "Revisiting Uncertainty Estimation" | 2025 | Tao et al. | 2fc250ddefbcf9ce5d70c6a8a37b932f4320f782 | 2505.23854 | 8 | MMLU-Pro aggregate; no category analysis |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| *No domain-wise calibration cases found* | N/A | "MMLU benchmark evaluation" | Only FID metrics found |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| calibration-toolbox | https://github.com/Jonathan-Pearce/calibration-toolbox | 74 | Python | ECE by category could be added |

---

#### Gap 3: Temperature Scaling Effect Size on Instruction-Tuned vs. Base Models

**Relevance Classification:** 🎯 PRIMARY

**Connection Type:**
- ☑️ Blocks answering research_question: "does post-hoc temperature scaling significantly reduce ECE" requires knowing effect size baseline
- ☑️ Relates to detailed_question Q3: Directly asks about ECE reduction magnitude
- ☐ Extends reference_papers limitation: N/A

**Current State:** Guo et al. 2017 established temperature scaling for CNNs (40% ECE reduction typical). Recent LLM papers show varied results: Flex-ECE (2025) shows 24-47% → 0.1-4% reduction; DACA shows up to 15% improvement; CCPS shows 55% reduction. But these use different models, benchmarks, and baseline methods.

**Missing Piece:** Controlled comparison of temperature scaling effectiveness on instruction-tuned models vs. base models, specifically whether RLHF-induced overconfidence makes temperature scaling more or less effective. Effect size variance across model families not systematically characterized.

**Potential Impact:** HIGH - Determines whether temperature scaling is sufficient or if LLM-specific methods (DACA, CCPS) are necessary.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "On Calibration of Modern Neural Networks" | 2017 | Guo et al. | d65ce2b8300541414bfe51d03906fca72e93523c | 1706.04599 | 7,452 | Foundational; T-scaling ~40% ECE reduction on vision models |
| "A study of calibration as a measurement of trustworthiness" | 2025 | de Oliveira et al. | 65dcf07cef2e0c715c5c8013b43b52725982a2a9 | N/A | 6 | Post-hoc methods reduce ECE from 24-47% to 0.1-4% on biomedical LLMs |
| "Your Pre-trained LLM is Secretly an Unsupervised Confidence Calibrator" | 2025 | Luo et al. | c95e088f14e7de85161483043f05518504a74f07 | 2505.16690 | 6 | DACA improves ECE up to 15.08% |
| "Just Ask for Calibration" | 2023 | Tian et al. | ab4ce5dda7ad4d9032995c9c049a89d65723c6aa | 2305.14975 | 598 | RLHF makes LLMs overconfident; verbalized confidence outperforms token probs |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| *No temperature scaling effect size cases found* | N/A | "temperature scaling neural network" | SDXL configs only |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| gpleiss/temperature_scaling | https://github.com/gpleiss/temperature_scaling | 1,167 | Python | Canonical implementation; NLL optimization |
| ml-stat-Sustech/Disagreement-Aware-Calibration | https://github.com/ml-stat-Sustech/Disagreement-Aware-Calibration | N/A | Python | LLM-specific; DACA method |

---

### Gap Priority Matrix

| Gap ID | Title | Relevance | Connection to RQ | Connection to DQ | Impact | Evidence Count | Priority |
|--------|-------|-----------|------------------|------------------|--------|----------------|----------|
| Gap 1 | Limited Qwen-Family Calibration Studies | PRIMARY | ☑️ Target model uncharacterized | ☑️ Q1 (baseline ECE) | HIGH | 6 sources | **CRITICAL** |
| Gap 2 | Domain-Wise MMLU Calibration Breakdown | PRIMARY | ☑️ Benchmark understanding | ☑️ Q4 (domain variation) | HIGH | 4 sources | **HIGH** |
| Gap 3 | Temperature Scaling Effect Size Variance | PRIMARY | ☑️ Method effectiveness | ☑️ Q3 (ECE reduction) | HIGH | 7 sources | **HIGH** |

### User Input to Gap Traceability

**Main Research Question** directly addressed by:
- **Gap 1**: Establishes whether Qwen2.5-7B-Instruct specifically exhibits miscalibration (population-level baseline)
- **Gap 2**: Clarifies "standard QA benchmarks" calibration at domain level
- **Gap 3**: Quantifies "significantly reduce ECE" effect size expectations for temperature scaling

**Detailed Questions** addressed by:
- **Q1 (Baseline ECE)** → Gap 1: Qwen-specific ECE measurements needed
- **Q2 (Reliability patterns)** → All gaps: Overconfidence/underconfidence patterns vary by model family
- **Q3 (Temperature scaling ECE reduction)** → Gap 3: Effect size characterization
- **Q4 (Domain variation)** → Gap 2: STEM vs. humanities breakdown needed
- **Q5 (Model size robustness)** → Gap 1: Qwen family size comparisons not studied

**ROUTE_TO_0 Context** (why population-level approach):
- All gaps focus on AGGREGATE/POPULATION-LEVEL metrics (ECE, reliability diagrams)
- NO per-instance uncertainty signals proposed (avoiding Attempts 1-7 failures)
- Temperature scaling is post-hoc aggregate calibration, not per-instance prediction

---

## 9. Conclusion - COMPACT

**Key Findings:** (1) Temperature scaling (Guo 2017) is foundational; (2) LLM calibration active with 9 papers 2024-25; (3) Population-level avoids prior failures; (4) Implementation ready; (5) Three critical gaps identified.

**Phase 2A Readiness:** HIGH - All checks pass.

**Next:** Phase 2A-Dialogue generates testable hypotheses from gaps.

---

*Phase 1 Complete - Compact version for Phase 2A*
*Full version: 01_targeted_research_full.md*
