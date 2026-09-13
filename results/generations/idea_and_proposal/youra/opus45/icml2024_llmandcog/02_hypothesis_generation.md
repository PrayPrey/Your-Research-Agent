# Phase 2A Extended: Hypothesis Clarification (Summary)

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md (V-PC-RAS)
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** V-PC-RAS-1
**Confidence Level:** 0.82

**Main Hypothesis:**
LLMs that exhibit genuine reasoning (compositional, generalizable) display hierarchical prediction error decay across transformer layers—high residual deltas early (novel structure processing), progressive reduction mid-layers (intermediate representation building), low deltas final (confident inference)—while heuristic-based responses show flat or discontinuous patterns. The complexity-normalized V-PC-RAS score, validated via MLSAE correlation, predicts adversarial Theory of Mind (ToM) benchmark performance.

**Alternative Hypothesis (H0):**
Residual stream delta patterns do not distinguish genuine reasoning from heuristic shortcuts; layer-wise activation changes reflect only task complexity or input length, not cognitive processing mode. V-PC-RAS will show no correlation with adversarial ToM accuracy (r < 0.2).

### 1.2 Variables

| Variable Type | Variable Name | Definition | Measurement |
|---------------|---------------|------------|-------------|
| **Independent** | Task Type | Standard vs adversarial ToM scenarios | Categorical: {ToMBench-standard, HI-TOM-adversarial} |
| **Independent** | Model Scale | Pythia checkpoint | Categorical: {70M, 410M, 1.4B, 2.8B} |
| **Dependent** | Residual Delta (ε_l) | Layer-wise L2 norm of activation change | ε_l = \|\|h_l - h_{l-1}\|\|_2 |
| **Dependent** | PC-RAS Score | Hierarchical decay fit quality | R²_exp - R²_linear (exponential vs linear fit) |
| **Dependent** | CN-PC-RAS | Complexity-normalized PC-RAS | PC-RAS / log(input_tokens) |
| **Dependent** | MLSAE Correlation | Proxy validation metric | Pearson r between ε_l and MLSAE latent variance |
| **Dependent** | Adversarial Accuracy | ToM benchmark performance | Proportion correct on HI-TOM/adversarial splits |
| **Controlled** | Prompt Template | Standardized ToM scenario format | Fixed templates from ToMBench/HI-TOM |
| **Controlled** | Inference Settings | Deterministic generation | temperature=0, top_p=1.0 |

### 1.3 Causal Mechanism

```
[Genuine Reasoning Process]
Input → Early layers: High ε_l (encoding novel structure)
      → Middle layers: Decreasing ε_l (building intermediate representations)
      → Final layers: Low ε_l (confident inference from built model)
      → Output: Correct adversarial ToM response

[Heuristic Shortcut Process]
Input → All layers: Flat/uniform ε_l (pattern matching without progressive abstraction)
      → Output: Correct standard ToM but fails adversarial variants
```

**Evidence for Causal Links:**
1. **PC Theory Evidence:** Predictive coding in neuroscience establishes that hierarchical generative models exhibit prediction error decay from lower to higher levels (Aitchison & Lengyel, 2017; Bottemanne, 2025)
2. **Residual Stream Evidence:** Lawson et al. (2024) MLSAE work shows individual latents activate at specific layers, indicating layer-specific computation
3. **ToM Sparse Parameter Evidence:** Wu et al. (2025) demonstrated ToM capability encoded in 0.001% of parameters linked to positional encoding—suggesting localized, circuit-level cognitive computation
4. **Mechanistic Understanding Evidence:** Beckmann & Queloz (2025) framework identifies three tiers of understanding (conceptual, state-of-world, principled), each tied to distinct computational organization

**Key Tension:**
Transformers are trained via backpropagation, not predictive coding. The analogy between residual deltas and prediction errors is structural, not mechanistic. Phase 0 MLSAE validation addresses this by empirically testing whether residual deltas carry prediction-error-like information.

### 1.4 Key Assumptions

| # | Assumption | Testability | Test Method | Failure Impact |
|---|------------|-------------|-------------|----------------|
| A1 | Residual stream deltas approximate prediction error signals | HIGH | MLSAE correlation in Phase 0 | FATAL: r < 0.3 invalidates core analogy |
| A2 | Hierarchical decay reflects compositional reasoning | MEDIUM | Correlation with adversarial accuracy in Phase 2 | MAJOR: r < 0.2 suggests metric captures something else |
| A3 | ToM tasks require genuine reasoning for adversarial generalization | HIGH | Performance gap standard vs adversarial | LOW: Well-established in literature (Shapira 2023) |
| A4 | Pythia models are representative of transformer LLMs | MEDIUM | Cross-architecture spot-check (optional) | MODERATE: Limits generalization claims |

### 1.5 Scope & Boundaries

**IN SCOPE:**
- Pythia model family (70M, 410M, 1.4B, 2.8B parameters)
- Theory of Mind cognitive task domain (ToMBench, HI-TOM)
- Layer-wise residual stream analysis via TransformerLens
- MLSAE validation methodology (Lawson et al. 2024)
- Behavioral correlation with adversarial benchmark splits

**OUT OF SCOPE:**
- Other cognitive domains (planning, causal reasoning, mathematical reasoning)
- Non-Pythia architectures (GPT, Llama, Mistral) without validation
- Real-time deployment or production systems
- Full causal validation via activation patching (Phase 3 optional extension)
- Multi-token generation dynamics

**BOUNDARY CONDITIONS:**
- Results apply to autoregressive decoder-only transformers
- Requires access to intermediate activations (not API-only models)
- Benchmark must have adversarial/robust split to distinguish reasoning modes

### 1.6 Testable Predictions

**Primary Prediction (P1):**
If residual deltas approximate prediction errors, then the correlation between layer-wise residual delta variance and MLSAE latent activation variance will be r > 0.5 across all Pythia checkpoints.

**Secondary Predictions:**

**P2 (Behavioral Correlation):** If hierarchical decay indicates genuine reasoning, then CN-PC-RAS will positively correlate with adversarial ToM accuracy (r > 0.4) while showing weaker correlation with standard ToM accuracy (r < 0.6).

**P3 (Scale Effect):** Larger Pythia models will exhibit stronger hierarchical decay (higher PC-RAS) on adversarial ToM tasks, reflecting emergence of compositional reasoning circuits with scale.

**P4 (Task Discrimination):** Within the same model, adversarial-correct responses will show significantly higher PC-RAS than adversarial-incorrect responses (Cohen's d > 0.5).

**Falsification Criteria:**
| Criterion | Threshold | Consequence |
|-----------|-----------|-------------|
| MLSAE correlation < 0.3 | Phase 0 | Abandon: core proxy assumption invalid |
| CN-PC-RAS vs adversarial accuracy r < 0.2 | Phase 2 | Major revision: metric doesn't capture reasoning |
| No scale effect in PC-RAS | Phase 2 | Minor revision: reasoning circuits not emergent |
| Task discrimination d < 0.3 | Phase 2 | Major revision: PC-RAS not discriminative |

### 1.7 Statistical Verification Design

**Sample Size Justification:**
- **Models:** 4 Pythia checkpoints (70M, 410M, 1.4B, 2.8B) for scale analysis
- **Benchmark Items:** ToMBench (~2,860 items) + HI-TOM (~1,000 items)
- **Power Analysis:** For r = 0.4 correlation, n = 46 items needed per cell (α = 0.05, power = 0.80). With 1000+ items, adequately powered.

**Statistical Tests:**
1. **Phase 0 (Proxy Validation):** Pearson correlation with 95% CI; test H0: r ≤ 0.3
2. **Phase 2 (Behavioral Correlation):** Partial correlation controlling for input length; Fisher z-transformation for CI
3. **Scale Effect:** Mixed-effects model with model size as fixed effect, benchmark item as random effect
4. **Task Discrimination:** Independent t-test with Welch's correction; Cohen's d effect size

**Multiple Comparison Correction:** Bonferroni correction for 4 primary predictions (α = 0.0125)

---

## 2. Contribution Summary

### Theoretical Contribution
**Novel Framework:** First integration of predictive coding theory from cognitive neuroscience with mechanistic interpretability for LLM cognitive validation. Provides theoretical grounding for why hierarchical error patterns should distinguish genuine reasoning from heuristics—filling the gap identified in Phase 1 (Gap 1: Heuristic Reliance vs Genuine Reasoning Mechanisms).

**Distinction from Prior Work:**
- Unlike ACDC (Conmy et al., 2023): Targets cognitive validation, not circuit discovery
- Unlike ToM benchmarks (ToMBench, HI-TOM): Provides mechanistic validation, not just behavioral testing
- Unlike attention pattern analysis: Uses residual stream (full information flow), not just attention weights

### Methodological Contribution
**V-PC-RAS Metric:** Complexity-normalized hierarchical error decay score with empirical proxy validation. Novel 4-phase methodology:
1. Proxy validation (MLSAE correlation)
2. Metric computation (exponential fit)
3. Behavioral correlation (adversarial accuracy)
4. Causal validation (activation patching, optional)

**Reproducibility:** All components use public tools (TransformerLens, MLSAE code, ToMBench) and standard hardware.

### Practical Contribution
**Pre-Deployment Cognitive Audit:** V-PC-RAS can serve as a mechanistic diagnostic for evaluating whether LLMs exhibit genuine reasoning or "Clever Hans" heuristics before deployment in high-stakes applications (medical diagnosis, legal reasoning, scientific discovery).

---

## 3. Key Related Work

| Source | Year | Relation | How Used |
|--------|------|----------|----------|
| Millidge et al. (Predictive Coding Beyond Backprop) | 2022 | **Foundation** | Theoretical basis for PC-DL connection |
| Bottemanne (Bayesian Brain Theory) | 2025 | **Foundation** | Hierarchical prediction error framework |
| Aitchison & Lengyel (PC and Bayesian Inference) | 2017 | **Foundation** | Mechanistic account of prediction errors |
| Lawson et al. (MLSAE Residual Stream Analysis) | 2024 | **Methodology** | Validation methodology for residual proxy |
| Wu et al. (ToM Sparse Parameters) | 2025 | **Foundation** | Evidence for localized ToM circuits |
| Beckmann & Queloz (Mechanistic Understanding) | 2025 | **Foundation** | Tiered framework for LLM understanding |
| Shapira et al. (Clever Hans ToM) | 2023 | **Motivation** | Problem definition: heuristic reliance |
| Schaeffer et al. (Emergent Abilities Mirage) | 2023 | **Motivation** | Need for mechanistic validation |
| He et al. (HI-TOM) | 2023 | **Evaluation** | Adversarial ToM benchmark |
| ToMBench (ACL 2024) | 2024 | **Evaluation** | Systematic ToM benchmark |
| TransformerLens | 2023 | **Infrastructure** | Activation extraction tool |
| Conmy et al. (ACDC) | 2023 | **Comparison** | Complementary circuit discovery |
| Pinchetti et al. (PC Beyond Gaussian) | 2022 | **Extension** | PC for transformer training |
| Yu & Xu (PC as BP Alternative) | 2025 | **Context** | Recent PC-DL integration review |

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
Residual stream deltas in transformer layers carry information analogous to prediction errors, validated by correlation with MLSAE latent activation patterns (r > 0.5).

**SH2 (Mechanism):**
Hierarchical decay in residual deltas (exponential fit R² > linear R²) reflects compositional reasoning processes that build intermediate representations progressively across layers.

**SH3 (Comparison):**
V-PC-RAS distinguishes genuine reasoning (high hierarchical decay) from heuristic shortcuts (flat patterns), as evidenced by differential correlation with standard vs adversarial ToM accuracy.

### Readiness Checklist

- [x] **Core hypothesis clarified** with main/alternative statements
- [x] **Variables defined** with precise measurements
- [x] **Causal mechanism specified** with evidence links
- [x] **Assumptions enumerated** with testability and failure impact
- [x] **Scope boundaries set** (Pythia, ToM, in-scope tools)
- [x] **Testable predictions** with quantitative thresholds
- [x] **Falsification criteria** with clear abort conditions
- [x] **Statistical design** with power analysis and correction
- [x] **Contributions articulated** (theoretical, methodological, practical)
- [x] **Related work mapped** with relation types
- [x] **Sub-hypothesis decomposition previewed** for Phase 2B

### Open Questions

1. **MLSAE Training:** Should we use pre-trained MLSAE from Lawson et al. or train on Pythia specifically?
   - **Recommendation:** Start with pre-trained; train Pythia-specific if correlation insufficient

2. **Layer Granularity:** Analyze every layer or sample (e.g., early/middle/late)?
   - **Recommendation:** All layers for PC-RAS computation; summarize as early/middle/late for interpretability

3. **Token Position:** Analyze all positions or focus on answer token?
   - **Recommendation:** Final token position (answer prediction) as primary; full sequence as secondary analysis

4. **Complexity Normalization:** log(tokens) or alternative (perplexity, structural complexity)?
   - **Recommendation:** Start with log(tokens); test perplexity-based normalization as robustness check

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-12*
