# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-HUALoRA-v1
**Confidence Level:** 0.78

**Main Hypothesis:**
Under the condition of LLM fine-tuning with training data access, if domain-partitioned LoRA adapters are trained with data isolation and multiplicative weight decay is applied to targeted adapters, then scalable machine unlearning will be achieved (>90% MIA evasion, >95% utility retention) because data influence is localized to specific adapters and neuroscience-inspired decay mechanisms effectively weaken learned representations.

**Alternative Hypothesis (H0):**
Domain-partitioned LoRA adapters do not provide sufficient data influence isolation, and/or multiplicative weight decay does not effectively remove learned representations at LLM scale, resulting in either failed unlearning (MIA success >50%) or unacceptable utility degradation (<80% retention).

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Data partition granularity | Independent | Number of domain-level LoRA adapters | 10-100 domains |
| Decay rate schedule | Independent | Multiplicative factor λ per epoch | λ ∈ [0.1, 0.9], exponential/linear/step |
| Adapter rank | Independent | LoRA rank parameter r | r ∈ {8, 16, 32, 64} |
| Forgetting efficacy | Dependent | MIA success rate on forget set post-unlearning | Target: <10% (vs ~50% baseline) |
| Model utility retention | Dependent | Accuracy/perplexity on retain set relative to original | Target: >95% |
| Unlearning efficiency | Dependent | Time/compute relative to full retraining | Target: <1% (100x speedup) |
| Base LLM architecture | Controlled | Model architecture and size | Fixed (e.g., LLaMA-7B) |
| Training data distribution | Controlled | Dataset with domain labels | Fixed benchmark dataset |
| Evaluation protocol | Controlled | MIA attack methodology | MIAU score, SMIA statistical test |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: Domain-Partitioned Training
    ↓ (Data assigned to specific adapters)
Step 2: Data Influence Localization
    ↓ (Knowledge compartmentalized)
Step 3: Targeted Adapter Identification
    ↓ (Domain labels enable targeting)
Step 4: Multiplicative Decay Application
    ↓ (FNN-style weight decay)
Outcome: Verified Forgetting (MIA evasion + utility preservation)
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Hugging Face PEFT | LoRA adapters successfully isolate task-specific knowledge | Strong |
| Step2 → Step3 | Mixture-of-Experts literature | Expert routing demonstrates knowledge compartmentalization | Medium |
| Step3 → Step4 | FNN paper (Hatua 2024) | Multiplicative decay with per-neuron factors achieves targeted forgetting | Strong |
| Step4 → Outcome | MIAU/SMIA papers (2025-2026) | MIA-based verification can detect incomplete forgetting | Strong |

**Key Tension:**
- **Tension**: FNN (Hatua 2024) validates decay mechanisms on MNIST/Fashion-MNIST (small CNNs), but LLMs have fundamentally different knowledge distribution patterns.
- **Resolution**: This verification plan tests whether FNN decay principles transfer to transformer adapter weights at scale, using rigorous MIA evaluation (MIAU score, SMIA statistical tests).

### 1.4 Key Assumptions

1. **LoRA adapters can localize domain-specific knowledge**
   - Evidence: PEFT library adoption; adapter merging literature
   - Consequence if violated: Cross-adapter interference undermines isolation

2. **Domain partitioning at training time is feasible**
   - Evidence: Data often has natural domain labels
   - Consequence if violated: Retrofit mode required; efficiency reduced

3. **Multiplicative decay transfers from CNNs to transformers**
   - Evidence: FNN on MNIST (Hatua 2024); neuroscience grounding
   - Consequence if violated: Alternative decay mechanisms needed

4. **Cross-adapter interference is bounded**
   - Evidence: Mixture-of-Experts limited cross-expert activation
   - Consequence if violated: Decay must target multiple adapters

### 1.5 Scope & Boundaries

**Applies to:**
- LLM fine-tuning with training data access
- GDPR "right to be forgotten" compliance scenarios
- Domains with natural data partitioning

**Does NOT apply to:**
- Pre-trained base model unlearning
- Real-time unlearning without compute budget
- Scenarios without domain labels

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Forgetting Efficacy)**:
MIA success rate on forget set will drop from ~50% to <10%, with MIAU score > 0.9.

*Success Criteria*: MIA success rate < 10% AND MIAU score > 0.9
*Falsification*: MIA success rate > 30% OR MIAU score < 0.5

**Secondary Predictions:**

**P2 (Utility Preservation)**: Retain set performance >95% of original
**P3 (Efficiency Advantage)**: Unlearning time <1% of retraining

**Falsification Criteria:**

The hypothesis will be **REJECTED** if:
1. MIA success rate > 30% (unlearning ineffective)
2. Cross-adapter interference > 20%
3. Retain set performance < 80%
4. Unlearning time > 10% of retraining

### 1.7 Statistical Verification Design

**Sample Size**: n ≥ 15 per condition
**Test**: Paired t-test, α = 0.05
**Design**: 27 configurations × 5 seeds = 135 runs
**Report**: Mean ± Std Dev, 95% CI, Cohen's d

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Can domain-partitioned LoRA adapters achieve measurable data influence localization during LLM fine-tuning?"

**SH2 (Mechanism):**
"Does the 4-step causal chain operate as proposed?"
- H-M1: Domain partitioning → Localization
- H-M2: Localization → Targeting accuracy
- H-M3: Targeting → Decay application
- H-M4: Decay → Forgetting outcome

**SH3 (Comparison):**
"Does HUA-LoRA outperform LUNE, AdapterSwap, and baselines?"

**Total Sub-Hypotheses:** 6 (SH1, H-M1-M4, SH3)

### Readiness Checklist

- [x] Hypothesis in scientific format
- [x] Hypothesis ID: H-HUALoRA-v1
- [x] Confidence level: 0.78
- [x] H0 defined
- [x] Variables operationalized
- [x] Causal mechanism with evidence (N=4)
- [x] Key tension identified
- [x] Assumptions with consequences
- [x] Testable predictions (P1 primary, P2-P3)
- [x] Falsification criteria defined
- [x] Baselines identified
- [x] SH1, SH2, SH3 ready

### Open Questions

1. **Resources**: 4-8 A100 GPUs for 2-4 weeks estimated
2. **Data**: RedPajama domains, C4 sources, WikiMem as candidates
3. **Calibration**: Decay rate λ requires sensitivity analysis
4. **Priority**: Start with SH1 (existence) as gate

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (YOLO Mode)*
*2026-02-12*
