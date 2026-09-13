# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-SACT-v1
**Confidence Level:** 0.85

**Main Hypothesis:**
Under the condition of graph-to-LLM encoding tasks across diverse domains (molecular, knowledge graphs, social networks), if adaptive spectral chunking is applied to learn domain-specific decomposition boundaries via eigenvalue threshold learning, then graph-LLM alignment quality will improve by >5% over fixed tokenization methods (HIGHT, GFT) because learned spectral thresholds partition graphs into natural structural units that preserve hierarchical information while achieving O(n) → O(n/k) token reduction.

**Alternative Hypothesis (H0):**
There is no significant difference in graph-LLM alignment quality between adaptive spectral chunking (SACT) and fixed tokenization methods (HIGHT, HQT, GFT); any observed improvements are due to increased model capacity or training data rather than the adaptive chunking mechanism itself.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| **Chunking Method** | Independent | Adaptive spectral (SACT) vs. fixed hierarchy (HIGHT) vs. quantization (HQT) vs. tree vocabulary (GFT) | Categorical: 4 levels |
| **Hierarchy Depth** | Independent | Number of hierarchical levels in tokenization | 2, 3, or 4 levels |
| **Task Conditioning** | Independent | Whether task-specific router is enabled | Binary: enabled/disabled |
| **Graph-LLM Alignment Quality** | Dependent | Graph-text retrieval accuracy (R@1, R@5, R@10) on benchmarks | 0-100% accuracy |
| **Hallucination Rate** | Dependent | Percentage of LLM outputs contradicting ground-truth graph structure | 0-100% (lower is better) |
| **Token Reduction Ratio** | Dependent | Original nodes / chunked tokens | Expected: 3-10x reduction |
| **Downstream Task Accuracy** | Dependent | Node classification, link prediction, graph classification accuracy | 0-100% accuracy |
| **Base LLM Architecture** | Controlled | Fixed to specific model | LLaMA-7B or equivalent |
| **Evaluation Benchmarks** | Controlled | Fixed dataset suite | MoleculeNet, OGB-MAG, Cora, Freebase |

### 1.3 Causal Mechanism

```
[Spectral Analysis] → [Natural Chunk Boundaries] → [Hierarchical Token Encoding] → [Task-Conditioned Selection] → [Improved Graph-LLM Alignment]
```

**Step 1: Spectral Analysis → Natural Chunk Boundaries**
Learned eigenvalue thresholds partition graphs along structural discontinuities via Lanczos approximation.

**Step 2: Natural Chunk Boundaries → Hierarchical Token Encoding**
Chunks at multiple scales (node → subgraph → motif → global) create multi-resolution representation.

**Step 3: Hierarchical Token Encoding → Task-Conditioned Selection**
Lightweight MLP router learns task-dependent mixtures over hierarchy depths.

**Step 4: Task-Conditioned Selection → Improved Graph-LLM Alignment**
Selected token granularity matches task requirements, reducing token count while preserving structure.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | GFT (Wang et al. 2024) | Tree vocabulary achieves cross-domain transfer via structural decomposition | Strong |
| Step2 → Step3 | HQT (Xiang et al. 2025) | Task-conditioned routing improves quantized tokenization | Strong |
| Step3 → Step4 | HCM (Wu et al. 2022) | Hierarchical chunking produces interpretable, transferable representations | Medium |
| Step4 → Outcome | GraphToken taxonomy | Node2token → group2token hierarchy validated across graph-LLM systems | Medium |

**Key Tension:**
GFT proposes fixed tree vocabulary (data-independent) while HCM suggests learned boundaries (data-dependent). SACT tests whether learned spectral boundaries outperform fixed boundaries on multi-domain benchmarks.

### 1.4 Key Assumptions

1. **Spectral Structure Assumption:** Graphs have detectable hierarchical structure via spectral eigenvalue gaps.
   - *Consequence if violated:* DiffPool fallback activated.

2. **Semantic Correspondence Assumption:** Spectral boundaries correspond to semantically meaningful units.
   - *Consequence if violated:* Alignment quality degrades.

3. **Cross-Domain Transfer Assumption:** Chunking learned on one domain transfers to related domains.
   - *Consequence if violated:* Domain-specific training required.

4. **LLM Integration Viability Assumption:** Learned graph tokens align with LLM embedding spaces.
   - *Consequence if violated:* Graph-text alignment fails regardless of tokenization.

### 1.5 Scope & Boundaries

**Applies to:** Graphs with detectable structure (molecules, KGs, social networks, 10+ nodes), graph-language tasks

**Does NOT apply to:** Extremely small graphs (<10 nodes), random graphs, real-time inference scenarios

**Known Limitations:** Approximate spectral methods trade accuracy for speed; DiffPool fallback adds complexity

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Graph-LLM Alignment Improvement)**:
SACT will achieve graph-text retrieval accuracy >5% higher than the best fixed tokenization baseline (HIGHT, GFT, or HQT) on multi-domain benchmarks.

*Measurement*: R@10 > baseline + 5% with p < 0.05 (paired t-test, n ≥ 25 runs)
*Falsification*: R@10 ≤ baseline - 2% triggers rejection

**Secondary Predictions:**

**P2 (Hallucination Reduction)**: >30% reduction vs. flat tokenization
**P3 (Token Efficiency)**: 5-10x reduction with <5% quality degradation
**P4 (Cross-Domain Transfer)**: >80% of supervised performance in zero-shot setting

**Falsification Criteria:**
1. Primary Failure: Alignment ≤ baseline - 2%
2. Mechanism Failure: Ablation shows no spectral benefit
3. Efficiency Failure: Token reduction <2x OR degradation >10%
4. Transfer Failure: Cross-domain <50% of single-domain

### 1.8 Statistical Verification Design

**Sample Size**: n ≥ 25 runs per condition (power = 0.8, α = 0.05)
**Test**: Paired t-test with Bonferroni correction
**Report**: Mean ± Std Dev, 95% CI, Cohen's d, p-values

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does adaptive spectral chunking produce detectable, consistent chunk boundaries across different graph types?"
- Verification type: Empirical observation
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is learned spectral threshold partitioning the actual cause of improved alignment?"
- Maps to: 4 causal steps (will decompose into H-M1 through H-M4)
- Verification type: Ablation studies

**SH3 (Comparison):**
"Does SACT outperform existing tokenization methods (HIGHT, GFT, HQT)?"
- Verification type: Comparative empirical

**Total Sub-Hypotheses:** 2 + 4 = 6

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-SACT-v1
- [x] Confidence level: 0.85
- [x] Alternative hypothesis (H0) defined
- [x] Variables operationalized with evidence
- [x] Causal mechanism with evidence (N=4 steps)
- [x] Key tension identified with resolution
- [x] Assumptions with consequences (4)
- [x] Testable predictions (4, P1 primary)
- [x] Falsification criteria (4 conditions)
- [x] Baselines identified (HIGHT, GFT, HQT, SAMGPT)
- [x] SH1, SH2, SH3 defined

### Open Questions

1. **Resource Requirements:** GPU compute for spectral decomposition on large graphs?
2. **Data Availability:** Graph-text pairs for all target domains?
3. **Implementation Complexity:** Custom CUDA kernels for differentiable spectral chunking?
4. **Priority Order:** SH1 before mechanism ablations or parallel?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
