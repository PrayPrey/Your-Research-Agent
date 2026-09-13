# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-SBT-01
**Confidence Level:** 0.85

**Main Hypothesis:**
Under the condition of multimodal input processing in Vision-Language Models (VLMs), if cross-modal attention creates binding interference at integration layers, then compositional safety will degrade (measured by increased attack success rates at integration layers vs. unimodal layers), because individually safe modality-specific representations interfere when combined through non-commutative composition operators in the Safety Binding Algebra: S_compose(v,t) = S(v) ⊗ S(t) + ε_bind.

**Alternative Hypothesis (H0):**
Cross-modal attention integration does NOT create measurable safety binding interference; safety degradation in multimodal models is fully explained by individual modality vulnerabilities without emergent compositional effects.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Cross-modal attention patterns | Independent | Attention entropy at integration layers (higher entropy = more diffuse binding) | 0.0-1.0 normalized entropy |
| Integration layer depth | Independent | Layer index where vision-language features merge | Layers 12-24 in standard VLMs |
| Modality combination type | Independent | Vision-first, text-first, or simultaneous input order | Categorical: V→T, T→V, V+T |
| Safety property preservation | Dependent | Refusal rate on toxic content via MMDT safety metrics | 0-100% refusal rate |
| Attack success rate (ASR) | Dependent | Percentage of adversarial inputs eliciting unsafe outputs | 0-100% ASR |
| Binding interference measure (BIM) | Dependent | Cross-modal attention entropy + hidden state semantic shift | BIM = H(attn) + ||Δh_safety|| |
| Base model architecture | Controlled | Fixed VLM architecture (e.g., LLaVA-1.5, InstructBLIP) | Fixed per experiment |
| Training data | Controlled | Standard pretraining datasets | Fixed (LLaVA-Instruct, etc.) |
| Evaluation benchmark | Controlled | MMDT benchmark suite | Fixed benchmark version |

### 1.3 Causal Mechanism

**3-Step Causal Chain:**

```
[Multimodal Input] → [Cross-Modal Attention Integration] → [Safety Binding Interference] → [Compositional Safety Degradation]
```

**Step 1: Multimodal Input → Cross-Modal Attention Integration**
Vision-language alignment projects visual features through attention layers that integrate with text embeddings. The projector module transforms visual tokens into the LLM embedding space, where cross-modal attention computes relevance weights.

**Step 2: Cross-Modal Attention Integration → Safety Binding Interference**
Hidden states undergo semantic shift when visual tokens are projected. Current vision-language alignment methods are insufficient at the hidden states level, causing safety-trained text representations to receive out-of-distribution inputs. This manifests as elevated attention entropy at integration layers.

**Step 3: Safety Binding Interference → Compositional Safety Degradation**
The interference disrupts activation of safety mechanisms trained on text-only patterns. Attacks targeting high-attention integration regions achieve higher success rates than attacks on unimodal components, demonstrating emergent compositional vulnerability.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Zhou et al. (2024) MMCoA | Cross-modal attention is the integration mechanism | Strong |
| Step2 → Step3 | Xu et al. (2025) TGA (ICLR) | Hidden states at specific layers activate safety; alignment fails to preserve this | Strong |
| Step3 → Outcome | Wang et al. (2025) "Multimodal Safety Is Asymmetric" | Safety degrades asymmetrically across modalities | Strong |
| Mechanism support | SAGA (2026) | Attention scores correlate with adversarial loss sensitivity | Strong |
| Theoretical basis | Campbell et al. (2024) | Binding problem explains VLM multi-object failures | Strong |

**Key Tension:**
**Tension:** Campbell et al. (2024) explains VLM binding failures through perceptual interference (representation quality), while TGA (2025) locates safety failures in hidden state semantic shift (safety-specific patterns). These may be the same phenomenon or distinct failure modes.

**Resolution:** This verification plan tests whether binding interference metrics (attention entropy) predict SAFETY degradation specifically, not just general task failure. If correlation exists only for safety metrics, the SBT explanation is distinct from general binding failures.

### 1.4 Key Assumptions

**A1: Layer-wise Safety Measurement Validity**
Safety properties can be meaningfully measured at individual transformer layers.
- *Evidence:* TGA (ICLR 2025) demonstrates that hidden states at specific layers play a crucial role in safety mechanism activation
- *If violated:* Cannot identify WHERE binding interference occurs; must treat safety as emergent property of full model only

**A2: Attention-Safety Information Encoding**
Cross-modal attention patterns encode safety-relevant information beyond task performance.
- *Evidence:* SAGA (2026) shows attention scores correlate with adversarial loss sensitivity; CAGUL (2025) uses cross-modal attention to identify safety-relevant visual tokens
- *If violated:* Cannot use attention analysis to predict or prevent safety failures; need alternative safety proxy

**A3: Measurable Binding Interference**
Binding interference is quantifiable via attention entropy and hidden state analysis.
- *Evidence:* Campbell et al. (2024) successfully applied binding framework to explain VLM failures using attention patterns
- *If violated:* SBT remains theoretical without empirical validation pathway; would need alternative operationalization

### 1.5 Scope & Boundaries

**Applies to:**
- Multimodal foundation models with attention-based cross-modal integration (VLMs, MLLMs)
- Architectures: LLaVA, InstructBLIP, Qwen-VL, GPT-4V-style models
- Safety domains: Toxic content refusal, harmful instruction resistance, jailbreak defense

**Does NOT apply to:**
- Early fusion architectures without explicit cross-modal attention
- Single-modality models (no binding to interfere)
- Non-attention integration methods (e.g., purely concatenative fusion)

**Known limitations:**
- Requires attention-level access for analysis (not available for closed-source models like GPT-4V)
- Binding interference metric needs empirical calibration per architecture
- Does not address agent-level compositional safety (future extension)

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Attack Success Rate at Integration Layers vs. Unimodal Layers)**:
If cross-modal attention creates binding interference, then adversarial attack success rates will be statistically higher (≥15% absolute increase) at integration layers compared to attacks targeting only unimodal components.

*Measurement*:
- ASR_integration vs. ASR_unimodal with p < 0.05
- Statistical test: Paired t-test across attack types, n ≥ 20 runs

*Basis*:
Domain standard for AI safety research. SAGA (2026) demonstrates attention-region correlation with adversarial sensitivity.

*Success Criteria*:
- Primary: ASR_integration - ASR_unimodal ≥ 15% (p < 0.05)
- Falsification: ASR_integration ≤ ASR_unimodal (no integration layer vulnerability)

**Secondary Predictions:**
**P2 (Attention Entropy Correlation with Safety Degradation)**:
Cross-modal attention entropy at integration layers will show significant positive correlation (Pearson r ≥ 0.5) with safety property degradation.

*Measurement*: Pearson correlation between H(attn_cross_modal) and (1 - refusal_rate)

**P3 (Binding-Aware Training Improvement)**:
Extending MMCoA with binding-aware objectives will improve compositional safety by ≥10% on MMDT without sacrificing unimodal safety (≤2% degradation).

*Measurement*: MMDT safety score comparison with/without binding-aware training

**Falsification Criteria:**
The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure**: ASR at integration layers ≤ ASR at unimodal layers
   (No evidence of emergent compositional vulnerability)

2. **Mechanism Failure**: Attention entropy shows no correlation (|r| < 0.3) with safety degradation
   (Binding interference not measurable via attention)

3. **Intervention Failure**: Binding-aware training provides no improvement OR degrades unimodal safety significantly (>5%)
   (Proposed defense mechanism does not work)

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

*Not applicable - This hypothesis establishes a new theoretical framework rather than competing on existing benchmarks. Evaluation uses absolute metrics (attack success rates, correlation coefficients) against domain standards.*

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Minimum n ≥ 20 runs per condition (attack type × layer type)
- Statistical power: 0.8 for detecting 15% ASR difference
- Effect size target: Cohen's d ≥ 0.5 (medium effect)

**Test Specifications:**

| Prediction | Test | Significance |
|------------|------|--------------|
| P1 (ASR comparison) | Paired t-test | α = 0.05, one-tailed |
| P2 (Entropy correlation) | Pearson correlation | r ≥ 0.5, p < 0.05 |
| P3 (Training improvement) | Independent t-test | α = 0.05, two-tailed |

**Report Format:**
- Mean ± Std Dev for all metrics
- 95% Confidence Intervals
- Effect sizes (Cohen's d for comparisons, r for correlations)
- p-values for all statistical tests

---

## 2. Contribution Summary

**Primary Contribution:**
- **Type:** Theoretical
- **Statement:** Safety Binding Theory (SBT) provides the first formal framework for understanding WHY and WHERE compositional safety fails in multimodal foundation models. By introducing the Safety Binding Algebra (S_compose(v,t) = S(v) ⊗ S(t) + ε_bind), SBT models safety degradation as emergent binding interference at cross-modal integration layers.
- **Novelty:** Unlike modality gap research (representation quality) or standard adversarial robustness studies, SBT specifically addresses how SAFETY PROPERTIES fail to compose across modalities—a fundamental gap identified in multimodal AI safety.

**Secondary Contributions:**
- **Methodological:** Binding-aware adversarial training protocol extending MMCoA to optimize for cross-modal safety coherence at integration layers
- **Practical:** Predictive diagnostic tool using attention entropy to identify high-risk modal combinations before deployment
- **Empirical:** Quantitative binding interference metric (BIM) enabling measurement of compositional safety degradation

---

## 3. Key Related Work

**Foundation Sources (MUST CITE):**

1. **"Understanding the Limits of VLMs Through the Lens of the Binding Problem"** (2024)
   - Authors: Campbell, Webb, Griffiths, Cohen et al.
   - URL: https://arxiv.org/abs/2411.00238
   - Key Finding: VLM failures mirror human perceptual binding limitations; provides theoretical foundation for applying binding framework to VLMs (55 citations)

2. **"Cross-Modal Safety Mechanism Transfer in Large Vision-Language Models"** (ICLR 2025)
   - Authors: Xu, Pang, Zhu, Shen, Cheng
   - URL: https://proceedings.iclr.cc/paper_files/paper/2025/
   - Key Finding: Hidden states at specific transformer layers activate safety mechanisms; vision-language alignment fails to transfer safety patterns

3. **"Revisiting Adversarial Robustness of VLMs: A Multimodal Perspective"** (2024)
   - Authors: Zhou, Bai, Zhao, Chen
   - URL: https://arxiv.org/abs/2404.19287
   - Key Finding: MMCoA framework for multimodal contrastive adversarial training; provides methodology basis for binding-aware training (25 citations)

4. **"MMDT: Decoding Trustworthiness and Safety of Multimodal Foundation Models"** (2025)
   - Authors: Xu, Zhang, Chen, Li, Song et al.
   - URL: https://mmdecodingtrust.github.io/
   - Key Finding: First unified safety evaluation platform for MMFMs; provides benchmark infrastructure (11 citations)

**Comparison Baselines:**

5. **"Stage-wise Attention-Guided Adversarial Attack on LVLMs" (SAGA)** (2026)
   - Authors: Kwak, Cao, Cho, Lee, Ahn, Yun
   - URL: https://arxiv.org/abs/2602.04356
   - Key Finding: Attention scores positively correlate with adversarial loss sensitivity; validates attention-based vulnerability measurement

6. **"Cross-Modal Attention Guided Unlearning in Vision-Language Models" (CAGUL)** (2025)
   - Authors: Bhaila, Komanduri, Van, Wu
   - URL: https://arxiv.org/abs/2510.07567
   - Key Finding: Cross-modal attention identifies safety-relevant visual tokens; demonstrates attention as safety proxy

**Gap Evidence:**

7. **"Multimodal Safety Is Asymmetric"** (2025)
   - Authors: Wang et al.
   - Key Finding: Visual alignment creates uneven safety constraints across modalities—empirically validates SBT's core claim of compositional safety failure

8. **MMCoA GitHub Repository**
   - URL: https://github.com/ElleZWQ/MMCoA
   - Purpose: Codebase to extend for binding-aware training implementation

**Total: 8 key sources selected**

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does safety binding interference exist at cross-modal integration layers in VLMs, measurable as elevated attack success rates at integration layers vs. unimodal layers?"
- Maps to: Primary prediction (P1)
- Verification type: Empirical analysis via layer-wise adversarial attacks
- Critical: MUST PASS for Phase 2B to proceed—if no integration layer vulnerability exists, SBT is falsified

**SH2 (Mechanism):**
"Is cross-modal attention integration the mechanism causing safety binding interference and subsequent compositional safety degradation?"
- Maps to: 3-step causal chain (N=3)
- Phase 2B will decompose into 3 sub-hypotheses:
  - **H-M1:** Multimodal Input → Cross-Modal Attention Integration (projector/attention mechanism)
  - **H-M2:** Cross-Modal Attention Integration → Safety Binding Interference (hidden state semantic shift)
  - **H-M3:** Safety Binding Interference → Compositional Safety Degradation (safety mechanism misactivation)
- Verification type: Causal analysis via attention entropy correlation and intervention studies
- Critical: Determines explanatory power of SBT

**SH3 (Comparison):**
"Does binding-aware training (extending MMCoA) improve compositional safety compared to standard adversarial training without sacrificing unimodal safety?"
- Maps to: Secondary prediction (P3)
- Verification type: Comparative empirical evaluation on MMDT benchmark
- Critical: Determines practical value of SBT-derived interventions

**Total Sub-Hypotheses for Phase 2B:** 5 (1 + 3 + 1)

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format ✓
- [x] Hypothesis ID assigned: H-SBT-01 ✓
- [x] Confidence level specified: 0.85 ✓
- [x] Alternative hypothesis (H0) defined ✓
- [x] All 9 variables have operationalization from evidence ✓
- [x] Causal mechanism has evidence at each step (N=3 steps, evidence_for_links table) ✓
- [x] Causal chain length (N=3) determined and stored ✓
- [x] Key tension identified (binding vs. hidden state failure modes) and resolution proposed ✓
- [x] Key assumptions (3) list consequences if violated ✓
- [x] 3 testable predictions exist with primary (P1) marked ✓
- [x] Falsification criteria defined (3 failure conditions) ✓
- [x] Baselines identified: MMCoA, MAT, standard adversarial training ✓
- [x] SH1, SH2 (3 sub), SH3 are clear starting points ✓

**Status: ALL REQUIREMENTS MET** ✅

### Open Questions

1. **Compute Requirements:** Layer-wise adversarial attack analysis and attention entropy computation across multiple VLM architectures (LLaVA, InstructBLIP) requires significant GPU resources. Estimate: 4× A100 for 2-3 weeks.

2. **Data Availability:** MMDT benchmark provides safety evaluation infrastructure, but need access to adversarial attack toolkits (SAGA codebase, MMCoA implementation). Verify GitHub repository availability and compatibility.

3. **Priority Verification Order:** Recommend verifying SH1 (Existence) first—if integration layer vulnerability does not exist, SBT is falsified early. Then SH2-M1 through SH2-M3 sequentially to establish causal chain, finally SH3 for practical validation.

---

**Note:** Full output with Contribution Summary and Key Related Work available in: `02a_extended_hypothesis_full.md`

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
