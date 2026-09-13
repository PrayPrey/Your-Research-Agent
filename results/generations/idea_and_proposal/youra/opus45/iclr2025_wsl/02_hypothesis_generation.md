# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-CMN-v1
**Confidence Level:** 0.85

**Main Hypothesis:**
Under the condition of diverse neural network architectures (CNNs, Transformers, MLPs, hybrids), if we decompose weights into computational motifs (primitives) via graph pattern mining and encode them with shared equivariant encoders composed hierarchically using graph attention networks, then cross-architecture transfer will achieve <10% performance drop compared to same-architecture baselines, because compositional primitives abstract away architecture-specific details while preserving functional semantics that are shared across architecture families.

**Alternative Hypothesis (H0):**
Computational motifs do not provide architecture-agnostic representations; the functional semantics of weight patterns are inherently architecture-specific, and cross-architecture transfer using motif-based decomposition will show >20% performance degradation compared to same-architecture methods, no better than architecture-agnostic flattening approaches.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Motif vocabulary size | Independent | Number of distinct computational patterns (attention, convolution, gating, normalization, feedforward) in the vocabulary | 10-50 seed motifs |
| Hierarchy composition depth | Independent | Number of GNN message passing layers for motif composition | 2-6 layers |
| Attention heads in composition | Independent | Number of attention heads in graph attention composition | 4-16 heads |
| Cross-architecture transfer performance | Dependent | Accuracy difference when transferring model embeddings across architecture families (CNN→Transformer, Transformer→MLP) | <10% drop (target) |
| Zero-shot generalization accuracy | Dependent | Property prediction accuracy on unseen architecture families without fine-tuning | >80% (target) |
| Property prediction MAE | Dependent | Mean absolute error for accuracy/loss prediction | <5% MAE |
| Training model zoo size | Controlled | Fixed number of pre-trained models per architecture family | 1000 per family |
| Downstream task complexity | Controlled | Fixed property prediction tasks | Accuracy prediction, hyperparameter inference |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Motif Detection → Motif Embeddings → Hierarchical Representation → Cross-Architecture Transfer
     [Step 1]         [Step 2]              [Step 3]                    [Step 4]
```

**Step 1: Motif Detection → Motif Instances**
- Graph pattern mining identifies recurring computational patterns in neural network computational graphs
- Uses subgraph isomorphism with learned similarity metrics
- Produces discrete motif instances (attention blocks, conv blocks, normalization units, etc.)

**Step 2: Motif Instances → Motif Embeddings**
- Shared NFN-style equivariant encoders process each motif instance
- Respects within-motif permutation symmetry
- Produces fixed-dimensional embeddings for each motif

**Step 3: Motif Embeddings → Hierarchical Representation**
- Graph attention network composes motif embeddings following computational topology
- Output: Model-level embedding capturing compositional structure

**Step 4: Hierarchical Representation → Cross-Architecture Transfer**
- Architecture-agnostic model embeddings used for downstream tasks
- Property prediction, model retrieval across architecture families

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Neural Graphs (Kofinas 2024) | GNN-based weight representation successfully processes computational graphs | Strong |
| Step2 → Step3 | Universal Neural Functionals (Zhou 2024) | Shared equivariant encoders work for any architecture | Strong |
| Step3 → Step4 | Ito et al. (2022) Compositional Generalization | Primitives pretraining enables zero-shot generalization | Strong |
| Step4 → Outcome | SANE (Schürholt 2024) | Weight space learning enables property prediction | Medium |

**Key Tension:**
- **Tension:** Ito et al. (2022) demonstrates compositional transfer in task-space (behavioral primitives), but weight-space motifs may have different characteristics than task primitives.
- **Resolution:** This verification plan tests whether motif-level abstraction provides the optimal granularity for cross-architecture transfer through ablation studies.

### 1.4 Key Assumptions

1. **Computational motifs have functionally similar representations across architectures**
   - Evidence: Ito et al. (2022) shows primitives enable compositional generalization (46 citations)
   - Consequence if violated: Motif embeddings will be architecture-specific; fallback to architecture-conditional encoding

2. **Hierarchical composition of motifs captures model-level properties**
   - Evidence: Theves et al. (2021) demonstrates hierarchical concept representation in brain
   - Consequence if violated: Need additional global context injection

3. **Motif boundaries can be identified from computational graph structure**
   - Evidence: Neural Graphs successfully converts NNs to computational graphs
   - Consequence if violated: Need supervised motif labeling or end-to-end learning

4. **Seed motif vocabulary covers common computational patterns**
   - Evidence: Known architectures share patterns (attention, convolution, normalization)
   - Consequence if violated: Need vocabulary expansion mechanism

5. **Equivariant encoding preserves functional semantics across motif instances**
   - Evidence: NFN (Zhou 2023) demonstrates permutation equivariance preserves weight semantics
   - Consequence if violated: Need richer encoding scheme

### 1.5 Scope & Boundaries

**Applies to:**
- Feed-forward neural networks: CNNs, Transformers, MLPs, MLP-Mixers, hybrids
- Model sizes: Small to medium (up to ~100M parameters initially)
- Tasks: Property prediction, model retrieval

**Does NOT apply to:**
- Recurrent networks (LSTM, GRU) without modification
- Extreme architectures: Neural ODEs, implicit networks
- Very large models (>1B parameters) without scaling strategies
- Weight generation tasks (requires decoder)

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Cross-Architecture Transfer Performance)**:
CMN-based model embeddings will achieve cross-architecture property prediction with <10% accuracy drop compared to same-architecture baselines.

*Measurement*: Train on CNN zoo, evaluate on Transformer zoo; R² or MAE metric
*Threshold*: Performance drop < 10% relative to same-architecture training
*Statistical test*: Paired t-test, n ≥ 20 runs, p < 0.05

*Success Criteria*: Transfer drop < 10% (p < 0.05)
*Falsification*: Transfer drop ≥ 25% triggers rejection

**Secondary Predictions:**

**P2 (Zero-Shot Generalization)**:
Pre-trained CMN will achieve >80% of same-architecture accuracy on unseen architecture families with zero-shot inference.

**P3 (Motif Vocabulary Scalability)**:
Adding new motifs will improve performance on corresponding architectures without degrading existing architectures.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:
1. **Primary Failure**: Cross-architecture transfer drop ≥ 25%
2. **Mechanism Failure**: Motif detection fails on >50% of architectures
3. **Baseline Failure**: CMN worse than simple flattening baseline

### 1.8 Statistical Verification Design

**Sample Size**: n ≥ 20 runs per condition
**Effect Size**: Cohen's d = 0.8 (large effect expected)
**Statistical Test**: Paired t-test, α = 0.05
**Report Format**: Mean ± Std Dev, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Do computational motifs identified by graph pattern mining exist as consistent, identifiable patterns across different neural network architectures?"
- Maps to: Primary prediction (motif detection validity)
- Verification type: Empirical (motif consistency analysis)
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the 4-step causal chain (Motif Detection → Motif Encoding → Hierarchical Composition → Cross-Architecture Transfer) the actual mechanism producing architecture-agnostic representations?"
- Maps to: Causal mechanism (N=4 steps)
- Phase 2B will decompose into 4 sub-hypotheses: H-M1 through H-M4
- Verification type: Ablation studies, component analysis
- Critical: Determines explanatory power

**SH3 (Comparison):**
"Does CMN outperform existing same-architecture methods (NFN, SANE) on cross-architecture transfer tasks?"
- Maps to: Secondary predictions (comparative performance)
- Verification type: Comparative empirical
- Critical: Determines practical value

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-CMN-v1
- [x] Confidence level specified: 0.85
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=4 steps)
- [x] Causal chain length (N=4) determined and stored
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (P1 primary, P2-P3 secondary)
- [x] Falsification criteria are defined
- [x] Baselines identified: NFN, SANE, Neural Graphs
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Resource Requirements:** Estimated 1 GPU for preprocessing, standard training for encoding
2. **Data Availability:** HuggingFace models available; need architecture labels and performance metadata
3. **Technical Feasibility:** Graph pattern mining scalability for large computational graphs (may need sampling)

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
