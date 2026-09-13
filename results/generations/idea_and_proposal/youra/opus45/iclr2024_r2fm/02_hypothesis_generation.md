# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-MetaCog-v1
**Confidence Level:** 0.83

**Main Hypothesis:**
Under autoregressive generation conditions, if a lightweight metacognitive controller monitors transformer hidden states every N tokens (N=5-10) and triggers confidence-weighted soft interventions, then hallucination rates will decrease by 30-50% with less than 20% latency overhead, because internal states encode detectable hallucination risk signals that can inform adaptive mitigation strategies before erroneous tokens are committed.

**Alternative Hypothesis (H0):**
Hidden state monitoring and adaptive interventions during generation do not significantly reduce hallucination rates compared to baseline LLM generation, OR any reduction achieved comes at the cost of unacceptable latency overhead (>20%) or fluency degradation.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Sparse triggering interval (N) | Independent | Controller inference frequency during autoregressive generation | N ∈ {5, 7, 10} tokens |
| Intervention mode | Independent | Selected from four modes: RAG injection, temperature adjustment, abstention flagging, self-correction prompting | Categorical (4 modes) |
| Confidence threshold | Independent | Probing classifier output threshold for triggering intervention | θ ∈ [0.5, 0.9] |
| Hallucination rate | Dependent | Percentage of responses containing factual errors (TruthfulQA, HaluEval) | Target: 30-50% reduction |
| Generation fluency | Dependent | Perplexity score and human coherence evaluation | Δperplexity < 5% |
| Latency overhead | Dependent | Percentage increase in generation time vs baseline | Target: <20% |
| Base LLM architecture | Controlled | Fixed model family across experiments | LLaMA-7B, Mistral-7B |
| Evaluation datasets | Controlled | Same benchmarks for all conditions | TruthfulQA, HaluEval, HELM |
| Temperature baseline | Controlled | Default sampling temperature | T = 0.7 |

### 1.3 Causal Mechanism

```
Step 1: Hidden State Monitoring
    ↓ (every N tokens)
Step 2: Risk Signal Detection (Probing Classifier)
    ↓ (if confidence > threshold)
Step 3: Intervention Selection & Execution
    ↓ (confidence-weighted)
Step 4: Generation Trajectory Modification
    ↓
Outcome: Reduced Hallucination Rate
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Ji et al. (2024) | Probing estimator achieves 84.32% hallucination detection accuracy from hidden states | Strong |
| Step2 → Step3 | MIND (Su et al., 2024) | Real-time detection using internal states is feasible without manual annotations | Strong |
| Step3 → Step4 | RLHF-V (Yu et al., 2023) | Fine-grained segment-level corrections reduce hallucination by 34.8% | Strong |
| Step4 → Outcome | Fleming (2023) | Metacognitive interventions can modify behavior when monitoring indicates risk | Medium |

**Key Tension:**
- **Tension:** Ji et al. (2024) demonstrates detection accuracy on static outputs, but real-time intervention during generation may face timing challenges where the "window of opportunity" for intervention is limited.
- **Resolution:** This verification plan tests sparse triggering intervals (N=5, 7, 10) to identify optimal balance between detection responsiveness and intervention timing.

### 1.4 Key Assumptions

| # | Assumption | Supporting Evidence | Consequence if Violated |
|---|------------|---------------------|------------------------|
| A1 | Hidden states encode hallucination risk signals detectable before token completion | Ji et al. (2024): 84.32% accuracy | Core detection mechanism fails; hypothesis rejected |
| A2 | Lightweight probing classifier can be trained without full model retraining | LoRA/adapter literature | Implementation becomes infeasible |
| A3 | Intervention latency is acceptable when sparse triggering bounds overhead to <20% | MIND real-time feasibility | Latency constraint violated |
| A4 | Four intervention modes cover majority of hallucination scenarios | RLHF-V, SelfCheckGPT analysis | Accept partial coverage |

### 1.5 Scope & Boundaries

**Applies To:**
- Autoregressive transformer-based LLMs (GPT-family, LLaMA, Mistral)
- Generation tasks requiring factual accuracy (QA, summarization)
- Deployment scenarios where moderate latency overhead is acceptable

**Does NOT Apply To:**
- Non-autoregressive models, diffusion-based text generation
- Real-time streaming with strict latency (<10ms)
- Creative tasks where hallucination is desired

**Known Limitations:**
- Sparse triggering may miss very short hallucinations (<N tokens)
- Domain-specific threshold calibration required
- RAG effectiveness depends on retrieval corpus quality

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Hallucination Reduction)**:
Hallucination rate reduction of 30-50% compared to baseline LLM generation.
- *Measurement*: TruthfulQA, HaluEval benchmarks, paired t-test, n ≥ 25 runs, p < 0.05
- *Falsification*: Reduction < 10% OR latency overhead > 25%

**Secondary Predictions:**
**P2 (Latency Efficiency)**: Sparse triggering (N=5-10) maintains latency overhead <20%
**P3 (Fluency Preservation)**: Confidence-weighted interventions maintain perplexity increase <5%

**Falsification Criteria:**
1. **Primary Failure**: Hallucination rate reduction < 10%
2. **Latency Failure**: Latency overhead > 25%
3. **Fluency Failure**: Perplexity increase > 15% OR coherence < 3/5
4. **Mechanism Failure**: Detection accuracy < 60%

### 1.8 Statistical Verification Design

**Sample Size**: n ≥ 25 runs per condition (Cohen's d = 0.6, power = 0.8)
**Test**: Paired t-test with Bonferroni correction, α = 0.05
**Report**: Mean ± SD, 95% CI, effect size

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does the metacognitive controller detect hallucination risk signals from hidden states with accuracy ≥70% under real-time generation conditions?"
- Verification type: Empirical
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the proposed 4-step causal mechanism the actual cause of hallucination reduction?"
- Decomposes into H-M1 to H-M4 (4 sub-hypotheses)
- Verification type: Causal analysis (ablation studies)

**SH3 (Comparison):**
"Does the metacognitive controller outperform baselines on hallucination reduction while maintaining constraints?"
- Verification type: Comparative empirical

**Total sub-hypotheses in Phase 2B:** 2 + 4 = **6 sub-hypotheses**

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-MetaCog-v1
- [x] Confidence level: 0.83
- [x] Alternative hypothesis (H0) defined
- [x] All variables operationalized
- [x] Causal mechanism with evidence (4 steps)
- [x] Key tension identified with resolution
- [x] Assumptions with consequences
- [x] 3 testable predictions (P1 primary)
- [x] 4 falsification criteria defined
- [x] Baselines identified: MIND, SelfCheckGPT, Vanilla LLM
- [x] SH1, SH2, SH3 ready

### Open Questions

1. **Data Availability:** What datasets for probing classifier training? (TruthfulQA, HaluEval preprocessing)
2. **Compute Requirements:** GPU resources for 7B model controller training? (~1x A100)
3. **Priority Order:** Verify SH1 before SH2, or parallel? (Recommend: SH1 first as gate)

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
