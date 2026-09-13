# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-CSR-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under the condition of few-shot in-context learning tasks with state space models, if Contextual State Reinstatement (CSR) mechanism is added to Mamba's selective scan (implementing temporal context encoding, similarity-based retrieval, and gated state reinstatement), then ICL performance will improve by >10% AND CMR-like behavioral signatures (recency effects, temporal contiguity) will emerge, because the CMR framework that explains Transformer ICL through induction heads can be computationally implemented in SSM state dynamics through selective gating.

**Alternative Hypothesis (H0):**
Adding CSR mechanism to Mamba's selective scan will NOT improve ICL performance beyond baseline Mamba, AND no CMR-like behavioral signatures will emerge, indicating that CMR mechanisms cannot be meaningfully translated to SSM architectures or that SSM state dynamics are fundamentally incompatible with episodic-like memory retrieval.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| CSR mechanism components | Independent | Three components: (1) temporal context vectors as dedicated state channels (d_context = 64-256), (2) cosine similarity-based retrieval gates (threshold τ = 0.5-0.8), (3) threshold-activated state reinstatement (context window W = 256-1024 tokens) | Binary: present/absent; Components can be ablated individually |
| ICL accuracy | Dependent | Performance on GINC, MetaICL benchmarks measured as accuracy percentage | Baseline ~60-75%; Target >70-85% |
| Behavioral signatures | Dependent | Recency effect (probability of recall vs lag), temporal contiguity (conditional response probability CRP), measured via probing experiments following Ji-An et al. (2024) protocol | CRP asymmetry > 0.1; Recency slope significant at p < 0.05 |
| Perplexity | Dependent | Language modeling perplexity on PG19 benchmark | Baseline ~15-20; Target ≤ baseline (no degradation) |
| Model size | Controlled | Fixed at Mamba-370M and Mamba-1.4B for comparability | 370M, 1.4B parameters |
| Training data | Controlled | Standard pretraining corpus (Pile or equivalent) | Fixed dataset |
| Baseline architecture | Controlled | Unmodified Mamba with identical parameters | Mamba-370M, Mamba-1.4B |

### 1.3 Causal Mechanism

**Causal Chain (N=3):**

```
Step 1: Temporal Context Encoding
    ↓
Step 2: Similarity-Based Retrieval Activation
    ↓
Step 3: State Reinstatement
    ↓
Outcome: Enhanced ICL Performance + CMR Behavioral Signatures
```

**Step 1 → Step 2: Temporal Context Encoding → Stored Context Patterns**
When input tokens arrive, dedicated context channels in extended SSM state accumulate task-relevant information through selective filtering. The temporal context vector c_t evolves as: c_t = α·c_{t-1} + (1-α)·f(x_t), where f is a learned projection and α controls temporal smoothing.

**Step 2 → Step 3: Stored Context Patterns → Retrieval Activation**
When current input embeddings match stored context patterns above threshold τ, retrieval gates activate. Similarity s_t = cos(c_t, h_t) is computed between context and current hidden state. Gate g_t = σ(s_t - τ) activates retrieval when similarity exceeds threshold.

**Step 3 → Outcome: Retrieval Activation → State Reinstatement → Enhanced ICL**
Activated gates restore relevant prior context to current state: h'_t = h_t + g_t · c_t. This enables the model to leverage past task patterns for current predictions, implementing CMR's "jump back in time" mechanism within SSM dynamics.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Gu & Dao (2023) Mamba | Selective scan implements input-dependent state updates | Strong |
| Step1 → Step2 | Oh et al. (2025) | "Nonlinear gating mechanism crucial for feature extraction" | Strong |
| Step2 → Step3 | Ji-An et al. (2024) | CMR cosine similarity matching explains Transformer ICL | Strong |
| Step2 → Step3 | Howard & Kahana (2002) | Original CMR model uses similarity-based context retrieval | Strong |
| Step3 → Outcome | Ji-An et al. (2024) | Context reinstatement is key CMR component for ICL | Strong |
| Step3 → Outcome | Grazzi et al. (2024) | Mamba "incrementally optimizes internal representations" for ICL | Medium |

**Key Tension:**
- **Tension:** Ji-An et al. (2024) showed CMR explains Transformer ICL through attention-based induction heads, but Wang et al. (2025) found "Mamba2 uses a different mechanism from FVs [function vectors] to perform ICL" - suggesting SSM ICL may fundamentally differ from Transformer ICL.
- **Resolution:** This verification plan tests whether CMR-INSPIRED (not CMR-identical) mechanisms can enhance SSM ICL. If CSR improves performance WITHOUT producing CMR behavioral signatures, this indicates SSMs may achieve ICL through alternative computational pathways, which would be an equally valuable finding.

### 1.4 Key Assumptions

1. **CMR mechanisms are computationally implementable in neural architectures**
   - Evidence: Ji-An et al. (2024) demonstrated CMR-like behavior emerges in Transformer induction heads
   - Consequence if violated: Core theoretical motivation fails; would need alternative framework

2. **SSM state dynamics can support episodic-like retrieval**
   - Evidence: Oh et al. (2025) showed nonlinear gating enables feature extraction
   - Consequence if violated: CSR may cause training instability or performance degradation

3. **Linear O(n) complexity can be preserved with bounded context window**
   - Evidence: Gating operations are O(1) per token; context window W is fixed
   - Consequence if violated: Loses efficiency advantage over Transformer attention

4. **Behavioral signatures from cognitive science transfer to neural network analysis**
   - Evidence: Ji-An et al. (2024) successfully applied CMR behavioral measures to Transformers
   - Consequence if violated: Cannot validate mechanism through behavioral signatures

### 1.5 Scope & Boundaries

**Where hypothesis applies:**
- SSM architectures with selective state mechanisms (Mamba, S6, Mamba2)
- In-context learning tasks with discrete tokens (language, symbolic reasoning)
- Model scales from 370M to 3B parameters (academic compute range)

**Where hypothesis does NOT apply:**
- Transformer-only architectures (already have attention-based ICL)
- Non-selective SSMs (vanilla S4, LRU without input-dependent parameters)
- Models below 100M parameters (may lack capacity for ICL)

**Known limitations:**
- Requires modification of core SSM CUDA kernels (implementation complexity: MEDIUM)
- Behavioral signature analysis requires interpretability infrastructure

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (ICL Accuracy Improvement):**
CSR-enhanced Mamba will achieve ICL accuracy > 10% improvement over baseline Mamba on GINC and MetaICL benchmarks.

*Measurement*: Accuracy improvement with p < 0.05 (paired t-test), Cohen's d > 0.5
*Falsification*: Accuracy improvement < 3% OR accuracy degradation

**Secondary Predictions:**

**P2 (Behavioral Signature Emergence):**
CSR-enhanced Mamba will exhibit CMR-like behavioral signatures:
- Recency effect: Higher recall probability for recent tokens
- Temporal contiguity: Asymmetric CRP curve with forward bias > 0.1

**P3 (Ablation Sensitivity):**
Ablating individual CSR components will cause proportional performance degradation (>30-50% per component).

**Falsification Criteria:**
The hypothesis will be **REJECTED** if any occur:
1. **Primary Failure**: ICL accuracy improvement < 3% (statistically indistinguishable from baseline)
2. **Mechanism Failure**: Ablations show <10% performance change per component
3. **Behavioral Failure**: No CMR-like signatures AND no performance improvement
4. **Efficiency Failure**: >2x throughput degradation vs baseline Mamba

### 1.7 SOTA Baseline (Optional)

*Not applicable - mechanism validation focus rather than SOTA comparison.*

### 1.8 Statistical Verification Design

**Sample Size**: n ≥ 25 runs per condition (Cohen's d = 0.5, power = 0.8)
**Statistical Test**: Paired t-test, α = 0.05, Bonferroni correction for multiple comparisons
**Ablation Design**: Full factorial (2³ = 8 conditions), ≥10 runs per condition
**Report Format**: Mean ± Std Dev, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does CSR-enhanced Mamba demonstrate statistically significant ICL performance improvement over baseline Mamba?"
- Maps to: Primary Prediction P1
- Verification type: Empirical comparative study
- Critical: MUST PASS for further verification

**SH2 (Mechanism):**
"Is the CSR three-component mechanism the actual cause of ICL improvement?"
- Maps to: Causal mechanism (N=3 steps)
- Verification type: Ablation studies + causal analysis
- Decomposes into 3 sub-hypotheses: H-M1, H-M2, H-M3

**SH3 (Comparison):**
"Does CSR provide advantages compared to alternative approaches (MambaFormer, attention hybrids)?"
- Maps to: Secondary predictions + comparison baselines
- Verification type: Comparative empirical + behavioral signature analysis

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-CSR-v1
- [x] Confidence level specified: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=3 steps)
- [x] Causal chain length (N=3) determined
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (3 provided)
- [x] Falsification criteria defined (4 criteria)
- [x] Baselines identified (Mamba, MambaFormer)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Resource Requirements:** GPU memory and training time for CSR-modified Mamba? (Estimate: 1.5-2x baseline)

2. **Data Availability:** Are GINC and MetaICL benchmarks publicly available with standard protocols?

3. **Implementation Feasibility:** CUDA kernel modification complexity? Consider PyTorch-native proof-of-concept first.

4. **Priority Verification Order:** SH1 (existence) first as gate; then SH2 + SH3 in parallel.

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
