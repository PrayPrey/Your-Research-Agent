# Verification Plan: Budget-Matched UQ Comparison

**Date:** 2026-08-28
**Hypothesis ID:** H-BudgetMatchedUQ-v1
**Confidence:** 0.75
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under matched generation budgets (N samples), if semantic entropy and self-consistency methods are applied to the same hallucination detection task, then they will show different precision-recall tradeoffs with the pattern varying by benchmark, because semantic entropy captures semantic clustering of errors while self-consistency captures surface-level output inconsistency.

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in hallucination detection AUROC between semantic entropy and self-consistency methods under matched generation budgets, and no method × benchmark interaction exists.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | TruthfulQA + HaluEval (standard) | Both benchmarks have ground truth labels for hallucination detection; represent different hallucination distributions |
| **Model** | Llama-3-8B-Instruct, Mistral-7B-Instruct | Open-weight models with sampling API; known to hallucinate; represent different training approaches |

**Dataset Details:**
- Source: HuggingFace datasets
- Path: truthfulqa/truthful_qa, halueval/halueval

**Model Details:**
- Type: decoder-only LLM
- Source: HuggingFace

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Semantic Entropy | AUROC ~0.75-0.85 | TruthfulQA (Kuhn et al.) |
| SelfCheckGPT | AUROC ~0.70-0.80 | WikiBio (Manakul et al.) |
| Contextual Calibration | ECE reduction | Classification tasks |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | NLI models accurately capture semantic equivalence | Kuhn et al. report high agreement; NLI >90% on MNLI | Semantic entropy clusters become noise |
| A2 | Surface metrics correlate but don't perfectly predict semantic equivalence | Known paraphrase vs factual divergence | Methods become identical |
| A3 | TruthfulQA and HaluEval have sufficient label quality | Both published with validated labels | Label noise inflates variance |
| A4 | Llama-3-8B and Mistral-7B produce varied hallucinations | Both known to hallucinate on factual questions | No hallucinations to detect |

### 1.6 Research Gap & Novelty

**Gap:** No existing head-to-head comparison of semantic entropy vs self-consistency under matched computational budgets.

**Novelty:** First controlled comparison using benchmark characteristics as proxies for hallucination type distribution, avoiding need for annotation.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| h-e1 | EXISTENCE | MUST_WORK | None | READY |
| h-m1 | MECHANISM | MUST_WORK | h-e1 | READY |
| h-m2 | MECHANISM | MUST_WORK | h-m1 | READY |
| h-m3 | MECHANISM | SHOULD_WORK | h-m2 | READY |

---

### 2.2 Hypothesis Specifications

#### h-e1: Methods Detect Hallucinations Above Random

**Type:** EXISTENCE
**Statement:** Under standard sampling conditions (N=10, temperature=0.7), if semantic entropy and self-consistency methods are applied to hallucination detection, then both will achieve AUROC > 0.55 on TruthfulQA, because both methods capture meaningful uncertainty signals.

**Variables:**
- IV: detection_method (semantic_entropy, self_consistency)
- DV: AUROC
- CV: sample_count=10, temperature=0.7, model=Llama-3-8B-Instruct

**Success Criteria:**
- AUROC > 0.55 for both methods (above chance + margin)
- p < 0.05 vs random baseline

**Gate:**
- Type: MUST_WORK
- If Fail: Fundamental flaw in methods or implementation

**Prerequisites:** None

**Verification Protocol:**
1. Load TruthfulQA (generation subset, 817 questions)
2. Generate N=10 samples per question with Llama-3-8B
3. Compute semantic entropy using Deberta-v3-large NLI
4. Compute self-consistency using BERTScore
5. Calculate AUROC against ground truth labels
6. Bootstrap 95% CI; verify lower bound > 0.55

---

#### h-m1: Sampling Generates Diverse Outputs

**Type:** MECHANISM
**Statement:** Under sampling temperature=0.7, if the model generates N=10 responses per query, then the responses will show meaningful diversity (avg pairwise BERTScore < 0.95), because temperature > 0 introduces stochastic variation.

**Variables:**
- IV: temperature (0.7 fixed for this experiment)
- DV: avg pairwise BERTScore
- CV: model=Llama-3-8B-Instruct, max_tokens=256

**Success Criteria:**
- Average pairwise BERTScore < 0.95
- At least 10% of queries show BERTScore variance > 0.01

**Gate:**
- Type: MUST_WORK
- If Fail: Mechanism step 1 falsified; methods cannot differentiate

**Prerequisites:** None (but logically h-e1 depends on this)

**Verification Protocol:**
1. Sample 100 queries from TruthfulQA
2. Generate N=10 responses per query
3. Compute pairwise BERTScore for each query
4. Report mean, std, % with variance > threshold

---

#### h-m2: NLI Clustering Differs from Surface Similarity

**Type:** MECHANISM
**Statement:** If semantic entropy uses NLI-based clustering and self-consistency uses BERTScore, then the resulting uncertainty scores will correlate imperfectly (Pearson r < 0.9), because semantic equivalence and surface similarity capture different properties.

**Variables:**
- IV: clustering_method (NLI vs BERTScore)
- DV: uncertainty_score
- CV: same generation set per query

**Success Criteria:**
- Pearson correlation between SE and SC scores < 0.90
- At least 5% of queries show rank disagreement in top-20% uncertainty

**Gate:**
- Type: MUST_WORK
- If Fail: Methods are redundant; no expected performance difference

**Prerequisites:** h-m1

**Verification Protocol:**
1. Use generations from h-m1
2. Compute semantic entropy per query
3. Compute self-consistency (1 - mean BERTScore) per query
4. Correlate scores; report Pearson r and scatter plot
5. Identify queries where methods disagree on uncertainty ranking

---

#### h-m3: Method Differences Vary by Benchmark

**Type:** MECHANISM
**Statement:** If semantic entropy and self-consistency detect different error types, then their relative AUROC advantage will differ across TruthfulQA, HaluEval-QA, and HaluEval-Summarization, because benchmark hallucination distributions differ.

**Variables:**
- IV: detection_method, benchmark
- DV: AUROC difference (SE - SC)
- CV: sample_count=10, model fixed

**Success Criteria:**
- Significant method × benchmark interaction (p < 0.05, two-way ANOVA)
- OR: Rank ordering of methods differs across at least 2 benchmarks

**Gate:**
- Type: SHOULD_WORK
- If Fail: Methods differ but uniformly across benchmarks

**Prerequisites:** h-m2

**Verification Protocol:**
1. Run full evaluation on all 3 benchmarks
2. Compute AUROC for SE and SC per benchmark
3. Two-way ANOVA with method and benchmark factors
4. Report interaction term p-value and effect size

---

## 3. Execution

### 3.1 Dependency Chain
```
h-m1 → h-e1 → h-m2 → h-m3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| h-e1 | MUST_WORK | AUROC > 0.55 both methods | Abort; check implementation |
| h-m1 | MUST_WORK | BERTScore diversity < 0.95 | Increase temperature or sample count |
| h-m2 | MUST_WORK | Correlation < 0.90 | Methods redundant; revise hypothesis |
| h-m3 | SHOULD_WORK | Interaction p < 0.05 | Accept uniform difference finding |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Setup | Infrastructure | 1 day |
| Phase 2: Existence | h-e1, h-m1 | 2 days |
| Phase 3: Mechanism | h-m2 | 1 day |
| Phase 4: Interaction | h-m3 | 2 days |

**Total Duration:** 6 days

---

## 4. Risk Analysis

### 4.1 Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R1: NLI model fails on LLM-generated text | Medium | High | Use Deberta-v3-large; validate on sample |
| R2: Benchmark labels too noisy | Low | High | Use TruthfulQA (human-verified) as primary |
| R3: Compute constraints limit sample count | Medium | Medium | Prioritize N=10; N=20 as stretch |
| R4: Methods highly correlated (r > 0.9) | Medium | High | Still report; pivot to ensemble analysis |

### 4.2 Assumption-Risk Mapping

| Assumption | Risk | Hypothesis Affected |
|------------|------|---------------------|
| A1: NLI accuracy | R1 | h-m2 |
| A2: Surface ≠ Semantic | R4 | h-m2, h-m3 |
| A3: Label quality | R2 | h-e1, h-m3 |
| A4: Model hallucination rate | None | h-e1 |

---

## 5. Dependency Graph

### 5.1 DAG Visualization
```
                    ┌─────────┐
                    │  START  │
                    └────┬────┘
                         │
                         ▼
                    ┌─────────┐
                    │  h-m1   │ ← MUST_WORK: Sampling diversity
                    └────┬────┘
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
         ┌─────────┐          ┌─────────┐
         │  h-e1   │          │  h-m2   │
         │MUST_WORK│          │MUST_WORK│
         └────┬────┘          └────┬────┘
              │                     │
              └──────────┬──────────┘
                         │
                         ▼
                    ┌─────────┐
                    │  h-m3   │ ← SHOULD_WORK: Benchmark interaction
                    └────┬────┘
                         │
                         ▼
                    ┌─────────┐
                    │   END   │
                    └─────────┘
```

### 5.2 Verification Phases

| Phase | Hypotheses | Gate | Duration |
|-------|------------|------|----------|
| 1 | h-m1 | MUST_WORK | 1 day |
| 2 | h-e1, h-m2 (parallel) | MUST_WORK | 2 days |
| 3 | h-m3 | SHOULD_WORK | 2 days |

---

## 6. Dialectical Analysis

### 6.1 Thesis
Semantic entropy and self-consistency methods, despite both using sampling, capture fundamentally different uncertainty signals (semantic clustering vs surface consistency), leading to different detection patterns across hallucination types.

### 6.2 Antithesis (H0 Position)
Both methods ultimately detect the same underlying phenomenon: uncertainty manifests similarly at semantic and surface levels. Any observed differences are artifacts of implementation choices (NLI model, similarity metric) rather than fundamental methodological differences. Under matched budgets, performance converges.

### 6.3 Synthesis
The truth likely lies between extremes: methods capture partially overlapping but non-identical signals. The key empirical question is the *magnitude* of difference. If r < 0.9 between scores, methods provide complementary information. If interaction effects exist, domain-specific method selection becomes valuable.

### 6.4 Robustness Assessment
- **Strongest for:** Method comparison under matched budgets (clear gap in literature)
- **Weakest for:** Generalizing interaction effects beyond tested benchmarks
- **Contingency:** If methods are redundant (r > 0.95), pivot to computational efficiency comparison

---

## 7. Executive Summary

### Key Points
1. **4 sub-hypotheses** decomposed from main claim (2 MUST_WORK, 1 SHOULD_WORK, 1 EXISTENCE)
2. **Critical path:** h-m1 → h-e1/h-m2 → h-m3
3. **Timeline:** 6 days total
4. **Top risk:** Methods may be more correlated than expected (mitigate with ensemble analysis pivot)
5. **Novel contribution:** First matched-budget comparison of SE vs SC

### Success Criteria Summary
- h-e1: Both methods AUROC > 0.55 ✓ → methods work
- h-m2: Correlation < 0.90 ✓ → methods differ meaningfully
- h-m3: Interaction significant ✓ → domain-specific selection valuable

### Next Steps
1. → Phase 2C: Design detailed experiment protocol for each hypothesis
2. → Phase 3: Implementation planning
3. → Phase 4: Execute verification loop

---

## Appendix A: Phase 2A Traceability

| Phase 2A Section | Phase 2B Usage |
|------------------|----------------|
| established_facts | Scope reduction (66% BUILD_ON) |
| causal_mechanism.steps | h-m1, h-m2, h-m3 derivation |
| predictions | Success criteria for h-e1, h-m3 |
| key_assumptions | Risk analysis mapping |

## Appendix B: Established Facts (BUILD_ON)

These claims are accepted without re-verification:
1. Semantic entropy uses NLI-based clustering (Kuhn et al. 2023)
2. SelfCheckGPT measures surface-level consistency (Manakul et al. 2023)
3. Both methods require multiple forward passes (N=5-20)
4. Contextual calibration improves confidence calibration (Zhao et al. 2021)

---

*Generated by Phase 2B Planning Workflow*
*Schema Version: 10.0.0*
