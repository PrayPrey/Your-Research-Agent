# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-ARID-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under multi-vector attack conditions against LLMs, if representation-level monitoring with contrastive adversarial-intent projection is applied at selective transformer layers (1, L/2, L), then multi-vector attacks will be detected at significantly higher rates than surface-level pattern matching (>20% improvement in TPR@FPR=0.1%) because attacks share detectable trajectory shifts in the representation space toward adversarial objectives, which can be captured by immune-inspired adaptive defense mechanisms.

**Alternative Hypothesis (H0):**
Multi-vector attacks do NOT share detectable representation-level signatures, and therefore representation-level monitoring with contrastive projection will NOT achieve significantly better detection rates than surface-level pattern matching defenses. Detection accuracy difference < 5% and/or computational overhead > 10%.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Defense Architecture | Independent | ARID (representation-level with contrastive projection) vs Baseline (pattern matching, e.g., perplexity detection) vs Single-vector (SPIN, guardrails) | 3 conditions |
| Attack Type | Independent | Direct injection, Indirect injection (RAG), Context manipulation, Cognitive overload, Combined multi-vector | 5 attack categories |
| Detection Accuracy | Dependent | True Positive Rate at False Positive Rate = 0.1% (TPR@FPR=0.1%) | 0-100%, target >80% |
| Attack Success Rate | Dependent | Percentage of attacks that successfully manipulate model output despite defense | 0-100%, target <20% |
| Inference Overhead | Dependent | Additional latency percentage compared to undefended baseline | Target <5% |
| Model Architecture | Controlled | Fixed to Llama-3 family (8B, 70B variants) | 2 model sizes |
| Attack Sophistication | Controlled | Fixed optimization budget for attack generation | Standard AdvBench/JailbreakBench |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Attack Input → Representation Shift → Adversarial-Intent Subspace → Trajectory Detection → Defense Response
```

**Step 1: Attack Input → Representation Shift**
When a multi-vector attack is processed by an LLM, it induces measurable changes in hidden state representations at transformer layers because attacks must manipulate internal processing to achieve adversarial objectives.

**Step 2: Representation Shift → Adversarial-Intent Subspace**
Contrastive learning projects diverse attack representations into a shared adversarial-intent subspace, enabling detection across attack vectors because all attacks share the goal of directing model behavior toward adversarial outcomes.

**Step 3: Adversarial-Intent Subspace → Trajectory Detection**
ARID monitors the direction of representation shift (trajectory) rather than absolute threshold values. This trajectory-based approach detects the optimization direction of attacks, making evasion fundamentally harder.

**Step 4: Trajectory Detection → Defense Response**
Lightweight probe classifiers at selective layers (1, L/2, L) generate confidence-weighted alerts, enabling graduated response while maintaining <5% inference overhead.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | JudgeDeceiver (Shi et al., 2024) | Optimization-based attacks target representation-level behavior; existing defenses insufficient | Strong |
| Step 2 → Step 3 | RAILS (Wang et al., 2022) | Immune-inspired contrastive learning enables cross-threat detection | Medium |
| Step 3 → Step 4 | Kushnerov et al. (2026) | Character-level representation analysis achieves 95.99% accuracy; ρ=1.0 robustness | Strong |
| Step 4 → Outcome | Defense-in-Depth (Onyagu et al., 2024) | Multi-layer architecture reduces overhead while maintaining coverage | Medium |

**Key Tension:**
- **Tension:** JudgeDeceiver demonstrates optimization-based attacks defeat threshold-based detection, but trajectory-based detection (monitoring direction) has not been validated against such attacks in LLM context.
- **Resolution:** Prediction P2 specifically tests trajectory-based detection against JudgeDeceiver-style attacks.

### 1.4 Key Assumptions

| # | Assumption | Consequence if Violated |
|---|------------|------------------------|
| A1 | Multi-vector attacks produce detectable signatures in LLM hidden states | **CRITICAL:** Entire approach fails; pivot to input/output-level defense |
| A2 | Attack signatures share sufficient commonality for contrastive projection | **MAJOR:** Per-vector defenses remain necessary; reduce to ensemble |
| A3 | Selective layer monitoring (1, L/2, L) captures sufficient signal | **MODERATE:** May need more layers; fallback: add L/4, 3L/4 |
| A4 | Adversaries cannot fully obfuscate attack intent while maintaining effectiveness | **MAJOR:** Arms race continues; require continuous adaptation |

### 1.5 Scope & Boundaries

**Applies to:**
- Transformer-based LLMs (GPT, Llama, Claude families)
- Text-based prompt attacks (injection, jailbreak, manipulation, overload)
- Inference-time defense

**Does NOT apply to:**
- Training-time attacks (data poisoning, backdoor injection)
- Non-transformer architectures (Mamba, RWKV)
- Multimodal attacks (image+text)

**Limitations:** Arms race potential; periodic retraining needed; scale validation required (70B+)

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Cross-Vector Detection Advantage):**
ARID achieves TPR@FPR=0.1% > 80% on combined multi-vector attacks, exceeding single-vector defenses by >20 percentage points.

*Measurement*: TPR@FPR=0.1% on AdvBench + JailbreakBench + multi-vector test set
*Statistical test*: McNemar's test, α = 0.05
*Falsification*: TPR@FPR=0.1% ≤ 60% triggers rejection

**Secondary Predictions:**

**P2 (Trajectory-Based Evasion Resistance):**
ARID detects JudgeDeceiver-style optimization attacks at >80% rate vs <50% for threshold-based defenses.

**P3 (Computational Efficiency):**
Selective layer monitoring maintains inference overhead <5% vs >20% for full-layer monitoring.

**Falsification Criteria:**

1. **Primary Failure**: TPR@FPR=0.1% ≤ 60%
2. **Mechanism Failure**: Silhouette score < 0.3 on projected embeddings
3. **Efficiency Failure**: Inference overhead > 10%
4. **Comparative Failure**: No significant improvement over best baseline (p ≥ 0.05)

### 1.7 SOTA Baseline

Not applicable - defense mechanism validation rather than SOTA comparison.

### 1.8 Statistical Verification Design

**Sample Size:** n ≥ 200 attack samples per category (1000 total)
**Effect size:** Cohen's h = 0.4 (medium-large)
**Power:** 0.8, α = 0.05 (one-tailed)

**Test Specification:**
- McNemar's test for paired comparison
- Bonferroni correction for 4 predictions
- Report: Detection rates, 95% CI, odds ratios, confusion matrices

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Do multi-vector attacks produce detectable and distinguishable signatures in LLM hidden state representations?"
- Maps to: P1 + Assumption A1
- Verification: Empirical (representation analysis)
- **Critical: MUST PASS for Phase 2B to proceed**

**SH2 (Mechanism):**
"Is the ARID causal mechanism the actual cause of improved detection?"

Decomposes into N=4 sub-hypotheses:
- **H-M1:** Attack inputs cause measurable representation shifts at layers 1, L/2, L
- **H-M2:** Contrastive learning projects diverse attacks into shared adversarial-intent subspace
- **H-M3:** Trajectory-based detection identifies adversarial direction even when magnitude is optimized
- **H-M4:** Selective layer monitoring achieves sufficient coverage with <5% overhead

**SH3 (Comparison):**
"Does ARID outperform baselines on multi-vector attacks?"
- Maps to: All testable predictions
- Verification: Comparative empirical

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-ARID-v1
- [x] Confidence level: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] Variables operationalized
- [x] Causal mechanism with evidence (N=4 steps)
- [x] Key tension identified with resolution
- [x] Assumptions with consequences
- [x] 3 testable predictions (primary marked)
- [x] 4 falsification criteria defined
- [x] Baselines identified (SPIN, guardrails, perplexity)
- [x] SH1, SH2, SH3 clear

**Status: 12/12 PASSED ✓**

### Open Questions

1. **Data Availability:** Are AdvBench/JailbreakBench sufficient or need custom multi-vector combinations?
2. **Compute Requirements:** Estimate 4x A100 (training), 1x A100 (inference validation)
3. **Priority Order:** SH1 first → H-M1 → H-M2 → H-M3 → H-M4 → SH3

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
