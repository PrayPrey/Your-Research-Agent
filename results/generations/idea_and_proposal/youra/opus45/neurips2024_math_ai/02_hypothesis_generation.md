# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-MRM-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under the condition of mathematical word problem solving with LLMs, if a Metacognitive Reasoning Monitor (MRM) combining hidden-state pattern detection, step-level PRM uncertainty quantification, and selective arithmetic verification is applied, then the accuracy drop on variation benchmarks will be reduced by >50% relative to baseline, because the MRM detects pattern-matching behavior in real-time and triggers corrective verification before outputting memorized but incorrect solutions.

**Alternative Hypothesis (H0):**
There is no significant difference in accuracy drop rates between LLMs with MRM and baseline LLMs on variation benchmarks. Hidden-state patterns do not reliably distinguish pattern-matching from novel reasoning, and selective verification provides no meaningful improvement over standard inference.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Metacognitive Classifier Output | Independent | Binary classification (0=novel reasoning, 1=pattern matching) from attention patterns + final layer activations | 0 or 1 per inference |
| Step-Level Uncertainty Score | Independent | Process Reward Model confidence score per reasoning step | 0.0-1.0 continuous |
| Verification Trigger Threshold | Controlled | Fixed threshold for triggering arithmetic verification | 0.7 (fixed) |
| Base Model Architecture | Controlled | LLM architecture (e.g., LLaMA-3-8B, Mistral-7B) | Fixed per experiment |
| Benchmark Dataset | Controlled | GSM8K variations, GSM-DC, or Putnam-AXIOM variations | Fixed per experiment |
| Accuracy Drop Rate | Dependent | (Original accuracy - Variation accuracy) / Original accuracy × 100% | 0-100% (target: <25% vs baseline ~50%) |
| Pattern Detection AUC | Dependent | Area under ROC curve for hidden-state classifier | 0.5-1.0 (target: >0.75) |
| Latency Overhead | Dependent | Time ratio: MRM-enhanced inference / baseline inference | 1.0-5.0x (target: <3.0x) |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: Hidden-State Pattern Detection
    ↓ (detects memorization signatures in attention + activations)
Step 2: Uncertainty Quantification via PRM
    ↓ (combines detection with step-level confidence scores)
Step 3: Selective Arithmetic Verification
    ↓ (triggers lightweight verification when pattern-matching detected)
Outcome: Reduced Accuracy Drop on Variation Benchmarks
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Zhou et al. 2025 (Hidden State Forensics) | >95% detection accuracy for abnormal LLM behaviors via layer-specific activation patterns | Strong |
| Step 1 → Step 2 | Makhija et al. 2025 (Neural Breadcrumbs) | 0.85 AUC for membership inference via hidden states and attention patterns | Strong |
| Step 2 → Step 3 | Goedel-Prover-V2 (Lin et al. 2025) | 88.1% MiniF2F using PRM-guided beam search for step-level confidence | Strong |
| Step 3 → Outcome | APOLLO (Ospanov et al. 2025) | 84.9% accuracy with error-fixing agents and selective verification | Medium |

**Key Tension:**
- **Tension:** Zhou et al. 2025 demonstrates hidden-state forensics for security threats, but pattern-matching in mathematical reasoning may have different activation signatures.
- **Resolution:** This verification plan includes SH2-M1 to specifically test hidden state separability in mathematical contexts using labeled GSM8K/variation pairs.

### 1.4 Key Assumptions

1. **Hidden State Separability:** Hidden states differentiate memorization from novel reasoning.
   - Evidence: Zhou et al. 2025 (>95% detection); Makhija et al. 2025 (0.85 AUC)
   - **If violated:** Classifier AUC < 0.6 → entire MRM mechanism fails

2. **PRM-Correctness Correlation:** Step-level confidence correlates with reasoning quality.
   - Evidence: Goedel-Prover-V2 uses PRM successfully
   - **If violated:** False triggers → latency increases without accuracy benefit

3. **Arithmetic Verification Effectiveness:** Lightweight verification catches pattern-matching errors.
   - Evidence: APOLLO demonstrates error-fixing agents work
   - **If violated:** No improvement in accuracy drop

4. **Selective Triggering Efficiency:** High-confidence triggering maintains acceptable latency.
   - Evidence: APOLLO achieves sub-100 sampling budget
   - **If violated:** Latency > 5x baseline → impractical

### 1.5 Scope & Boundaries

**Applies to:**
- Mathematical word problems (GSM8K, MATH level)
- Open-source LLMs with accessible hidden states
- Variation benchmarks (GSM-DC, Putnam-AXIOM, RV-BENCH)

**Does NOT apply to:**
- Formal theorem proving (use LeanDojo directly)
- Closed-source models without hidden state access
- Real-time applications requiring <100ms latency

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Accuracy Drop Reduction):**
MRM-enhanced LLM achieves accuracy drop rate < 25% on variation benchmarks vs. baseline ~50%.

*Measurement:* Drop rate = (Original - Variation) / Original × 100%
*Statistical test:* Paired t-test, n ≥ 25, p < 0.05
*Falsification:* Drop rate ≥ 45% triggers rejection

**Secondary Predictions:**
**P2 (Pattern Detection Validity):**
Hidden-state classifier achieves AUC > 0.75 on labeled pattern-matching examples.

**P3 (Efficiency Constraint):**
Average latency overhead < 3x baseline inference time.

**Falsification Criteria:**
1. **Primary Failure:** Accuracy drop ≥ 45%
2. **Mechanism Failure:** Classifier AUC < 0.60
3. **Efficiency Failure:** Latency > 5x baseline

### 1.7 SOTA Baseline

| Model | Original | Variation | Drop Rate | Source |
|-------|----------|-----------|-----------|--------|
| O1-preview | 41.9% | 22.3% | 46.8% | Putnam-AXIOM 2025 |
| O3 | 49% | ~39% | ~20% | Hao et al. 2025 |
| Open-source | Variable | Variable | 50-70% | RV-BENCH 2025 |

**Target:** Reduce drop rate from ~50% to <25% (>50% relative improvement)

### 1.8 Statistical Verification Design

- **Effect size:** Cohen's d ~0.8 (large)
- **Required runs:** n ≥ 25 problem-variation pairs
- **Test:** Paired t-test, α = 0.05 (one-tailed)
- **Report:** Mean difference, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does hidden-state separability for pattern-matching vs. novel reasoning exist in LLMs during mathematical problem solving?"
- Maps to: P2 (AUC > 0.75)
- Verification: Empirical classifier evaluation
- **Critical:** MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the three-component MRM mechanism the cause of reduced accuracy drop?"
- Decomposes into 3 sub-hypotheses (H-M1, H-M2, H-M3) for each causal link
- Verification: Ablation studies
- **Total:** 3 mechanism hypotheses

**SH3 (Comparison):**
"Does MRM outperform baseline on accuracy drop reduction?"
- Maps to: P1 (Drop < 25%)
- Baselines: Standard CoT, Didolkar skill-labeling
- Verification: Comparative evaluation

**Total sub-hypotheses:** 5 (SH1 + 3×SH2 + SH3)

### Readiness Checklist

- [x] Hypothesis in scientific format with H0
- [x] Hypothesis ID: H-MRM-v1, Confidence: 0.82
- [x] Variables operationalized with evidence
- [x] Causal mechanism: N=3 steps with evidence table
- [x] Key tension identified with resolution
- [x] Assumptions with violation consequences
- [x] Testable predictions with thresholds
- [x] Falsification criteria defined
- [x] Baselines identified
- [x] SH1, SH2, SH3 ready for Phase 2B

### Open Questions

1. **Data:** Labeled examples for classifier training - use GSM8K/variation pairs or manual annotation?
2. **Compute:** Single A100 estimated for classifier; verify resource availability
3. **Priority:** Verify SH1 (hidden-state separability) first as gate-keeper

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-13*
