# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-ModularShield-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under conditions where multimodal LMMs face diverse jailbreak attacks (visual, textual, cross-modal, adaptive), if a 4-layer hierarchical defense framework (ModularShield) with modular plug-and-play architecture is applied, then Attack Success Rate (ASR) will be significantly lower than single-layer defenses because the layered defense with inter-layer information flow catches attacks that bypass individual layers, and the modular design enables integration of proven defense methods (UniGuard, SafeMLLM, Q-MLLM) at appropriate abstraction levels.

**Alternative Hypothesis (H0):**
The 4-layer hierarchical defense architecture provides no statistically significant improvement in ASR over the best-performing single-layer defense, indicating that defense integration and information flow do not provide additive or synergistic protection benefits.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Defense Architecture | Independent | Configuration: Single-layer (UniGuard-only, SafeMLLM-only, Q-MLLM-only, E²AT) vs ModularShield 4-layer | Categorical: 5 conditions |
| Attack Type | Independent | Attack category from JailBreakV-28K: visual perturbation, textual jailbreak, cross-modal obfuscation, adaptive attacks | Categorical: 4 categories |
| Attack Success Rate (ASR) | Dependent | Percentage of attacks eliciting harmful/policy-violating responses; measured via JailbreakBench judge | 0-100%, lower is better |
| Model Utility | Dependent | VQA accuracy on clean inputs (VQAv2, MMBench test sets) | 60-85%, higher is better |
| Inference Latency | Dependent | Average response time per query in milliseconds | 50-500ms, lower is better |
| Base LMM Model | Controlled | LLaVA-1.5-7B with frozen base weights | Fixed |
| Attack Benchmark | Controlled | JailBreakV-28K test set (standardized split) | Fixed |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Layer 1 (Input Sanitization)
    → Layer 2 (Embedding Anomaly)
    → Layer 3 (Cross-Modal Consistency)
    → Layer 4 (Response Verification)
    → Outcome (Reduced ASR)
```

**Step 1:** Input Sanitization blocks obvious pattern-based jailbreaks → reduces attack volume to Layer 2
**Step 2:** Embedding Anomaly Detection catches perturbation-level attacks → flags semantically suspicious inputs
**Step 3:** Cross-Modal Consistency catches sophisticated attacks with visual-textual divergence → exploits alignment signals
**Step 4:** Response Verification catches harmful outputs that slip through → final safety net

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Layer 1 → Layer 2 | UniGuard (Oh et al., 2024) | Joint unimodal and cross-modal guardrails reduce obvious jailbreaks | Strong |
| Layer 2 → Layer 3 | SafeMLLM (Yin et al., 2025) | Contrastive embedding attack detection catches perturbation-level threats | Strong |
| Layer 3 → Layer 4 | E²AT (Lu et al., 2025) | Joint multimodal optimization improves defense by 34% | Strong |
| Layer 4 → Outcome | JailbreakBench evaluation framework | Standardized ASR measurement validates defense effectiveness | Medium |

**Key Tension:**
- **Tension:** UniGuard focuses on pre-generation guardrails while E²AT uses adversarial training that modifies model behavior (external filtering vs. internal robustness).
- **Resolution:** ModularShield's modular architecture accommodates both paradigms. Verification plan will test whether integration provides additive benefits.

### 1.4 Key Assumptions

1. **Cross-modal gap exploitation:** Cross-modal attacks succeed by exploiting gaps between modality-specific defenses.
   - Consequence if violated: Layered architecture provides no advantage over single comprehensive defense

2. **Defense complementarity:** Different defense mechanisms at different abstraction levels provide complementary coverage.
   - Consequence if violated: Added complexity provides no benefit

3. **Cross-modal measurability:** Cross-modal semantic consistency can be reliably measured using adversarially-robust CLIP.
   - Consequence if violated: Layer 3 becomes unreliable, reducing to 3-layer defense

4. **Early rejection efficiency:** Early rejection at lower layers reduces computational overhead for obvious attacks.
   - Consequence if violated: Framework becomes too slow for practical deployment

### 1.5 Scope & Boundaries

**Applies to:** LMMs with vision-language capabilities (LLaVA, MiniGPT-4, GPT-4V, Gemini Pro); jailbreak attacks (visual, textual, cross-modal, adaptive)

**Does NOT apply to:** Text-only LLMs; single-modality models; audio/video-language models; unintentional errors

**Limitations:** Requires one-time CLIP fine-tuning; threshold tuning per deployment; novel attack categories may bypass

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (ASR Reduction vs Single-Layer Baselines):**
ModularShield will achieve ASR at least 20% lower (absolute) than the best single-layer baseline defense across all attack types.
- Measurement: JailbreakBench standardized judge
- Success: ModularShield ASR ≤ 0.8 × (best single-layer ASR), p < 0.05
- Falsification: ModularShield ASR ≥ (best single-layer ASR)

**Secondary Predictions:**

**P2 (Latency Overhead):** Inference latency < 2× base LMM latency with early rejection

**P3 (Adaptive Attack Resistance):** Randomized thresholds achieve lower ASR than fixed thresholds against adaptive attacks

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:
1. ModularShield ASR ≥ best single-layer ASR (no improvement)
2. Removing any single layer does not increase ASR (layers redundant)
3. Inference latency > 5× baseline (impractical)
4. Model utility drops > 10% vs baseline (excessive false positives)

### 1.8 Statistical Verification Design

**Sample Size:** n ≥ 30 per condition (5 conditions × 4 attack types = 600 minimum experiments)
**Statistical Test:** Mixed-design ANOVA, Tukey HSD post-hoc, α = 0.05
**Effect Size:** Cohen's d ≥ 0.8 target
**Report Format:** Mean ± Std Dev, 95% CI, p-values, effect sizes

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does ModularShield reduce ASR compared to undefended baseline LMM?"
- Maps to: Primary prediction P1
- Critical: MUST PASS

**SH2 (Mechanism):**
"Does each layer contribute independently to defense effectiveness?"
- Maps to: Causal mechanism (4 sub-hypotheses: H-M1 through H-M4)
- Verification: Ablation study

**SH3 (Comparison):**
"Does ModularShield outperform best single-layer baseline across attack types?"
- Maps to: Secondary predictions
- Critical: Determines practical value

**Total Sub-Hypotheses:** 2 + 4 = **6** sub-hypotheses

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-ModularShield-v1
- [x] Confidence level: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] Variables operationalized
- [x] Causal mechanism with evidence (N=4 steps)
- [x] Key tension identified with resolution
- [x] Assumptions with consequences
- [x] Testable predictions (3 total)
- [x] Falsification criteria (4 criteria)
- [x] Baselines identified (4 baselines)
- [x] SH1, SH2, SH3 defined

**Status:** ✅ READY FOR PHASE 2B

### Open Questions

1. **Resource Requirements:** GPU-hours for adversarial CLIP training (Layer 3)?
2. **Data Availability:** JailBreakV-28K public access with standardized splits?
3. **Implementation Feasibility:** Integration complexity for combining UniGuard, SafeMLLM APIs?
4. **Verification Priority:** Recommend SH1 first as gate condition

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
