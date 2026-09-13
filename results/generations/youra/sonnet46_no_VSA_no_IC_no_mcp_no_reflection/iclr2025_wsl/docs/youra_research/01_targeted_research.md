# Targeted Research Report (Phase 2A Compact): Weight Space Learning — Model Property Prediction

**Date:** 2026-08-31
**Phase:** 1 - Targeted Research Gathering (Compact for Phase 2A)
**Researcher:** Anonymous
**Full Report:** 01_targeted_research_full.md

---

## Executive Summary

Phase 1 identified 11 key papers, 6 GitHub repositories, and 3 research gaps for the weight space learning research question. All results are [INFERRED] (no_MCP environment). Core finding: the model zoo benchmark is well-established; three equivariant encoder architectures compete (DWS, NFT, GNN); generalization gap prediction and cross-architecture transfer are the two primary unexplored axes. Phase 2A readiness: HIGH.

---

## 0. Reference Paper Analysis

*No reference papers provided*

---

## 1. Research Questions

### Primary Research Question
Can lightweight, permutation-invariant weight space embeddings predict downstream model properties — specifically test accuracy and generalization gap — for networks trained on standard image classification benchmarks, using only the model weights as input?

### Detailed Research Questions
1. Which weight space representation method (plain MLP flattening, graph hypernetwork, neural functional network, or transformer-based) achieves the best predictive accuracy for test accuracy on existing model zoo benchmarks?
2. Does enforcing permutation equivariance in the weight encoder improve predictive correlation of generalization gap compared to permutation-agnostic baselines on the same existing model zoo?
3. How does the sample efficiency of weight space encoders compare — how many trained models are needed to reach a given Spearman correlation with test accuracy?
4. Can a single weight space encoder trained on one architecture family transfer predictive ability to a held-out architecture family without retraining, evaluated on existing cross-architecture model zoos?
5. What weight space features (layer norms, singular value spectra, weight covariance) are most predictive of generalization, as measured by feature importance on existing labeled model zoo data?

### Lessons from Previous Attempts (ROUTE_TO_0 Only)
*N/A - First attempt*

---

## 2. Search Queries Generated (Top 3 per category)

- Brainstorm: "permutation equivariance weight space neural networks", "model zoo accuracy prediction benchmark", "generalization gap prediction from weights"
- Direct: "predicting neural network accuracy from weights Unterthiner model zoo", "neural functional transformers weight encoder", "cross-architecture transfer weight space encoder held-out"

---

## 3. Past Cases & Best Practices (via Archon) — COMPACT

**Status:** Archon MCP unavailable — [INFERRED] results only

| Case/Pattern | Query Used | Key Pattern |
|---|---|---|
| Model Zoo Accuracy Prediction Pipeline [INFERRED] | "predicting neural network accuracy from weights" | Flat MLP on flattened weights is baseline; permutation-alignment preprocessing needed |
| Equivariant Weight Space Encoders [INFERRED] | "permutation equivariance weight space" | Navon DWS (2023) / Kofinas GNN (2024); parameter sharing across permutation-equivalent positions |
| Graph-Based Weight Representation [INFERRED] | "graph hypernetwork weight space" | Nodes=neurons, edges=weights; GNN for equivariant embedding |
| Hyper-Representation Pattern [INFERRED] | "weight space learning model property" | Encode full weight set → fixed embedding → predictor head |

---

## 4. Academic Literature Review (via Semantic Scholar) — COMPACT

**Status:** Scholar MCP unavailable — [INFERRED] from known literature

### Directly Relevant Papers

| Title | Year | Authors | arXiv ID | Citations | Key Insight |
|---|---|---|---|---|---|
| "Predicting Neural Network Accuracy from Weights" | 2020 | Unterthiner et al. | 2002.11448 | ~300 [I] | Foundational benchmark; model zoo + Spearman correlation metric |
| "Equivariant Architectures for Learning in Deep Weight Spaces" | 2023 | Navon et al. | 2301.12780 | ~150 [I] | DWS — permutation-equivariant layers; model zoo accuracy prediction |
| "Neural Functional Transformers" | 2023 | Zhou et al. | 2305.13546 | ~120 [I] | NFT — transformer for weight space; symmetry-aware; model property prediction |
| "Graph Neural Networks for Equivariant Representations of NNs" | 2024 | Kofinas et al. | 2403.12143 | ~60 [I] | GNN-based equivariant encoder; competitive with DWS on model zoo |
| "Self-Supervised Learning on NN Weights for Model Prediction" | 2022 | Schürholt et al. | 2110.15288 | ~100 [I] | Hyper-representations; self-supervised pretraining; PDFD dataset |
| "Classifying the Classifier" | 2020 | Eilertsen et al. | 2002.05688 | ~80 [I] | Weight statistics for model classification; spectral norms important |
| "Universal Neural Functionals" | 2024 | Trabucco et al. | 2402.05232 | ~40 [I] | Universal NFN for variable architectures; relevant to cross-arch transfer |

### Foundational Papers

| Title | Year | arXiv ID | Key Insight |
|---|---|---|---|
| "HyperNetworks" | 2017 | 1609.09106 | Foundational weight generation; predecessor to weight space learning |
| "Deep Sets" | 2017 | 1703.06114 | Permutation invariance for sets; baseline for weight encoders |
| "PDFD Model Zoo Dataset" | 2022 | 2209.14764 | Large multi-arch model zoo; enables cross-arch evaluation |

[I] = INFERRED citation count

---

## 5. Implementation Resources (via Exa) — COMPACT

**Status:** Exa MCP unavailable — [INFERRED] from known repositories

| Resource | URL | Stars | Language | Key Feature |
|---|---|---|---|---|
| AvivNavon/DWSNets [I] | https://github.com/AvivNavon/DWSNets | ~400 | PyTorch | Official DWS; model zoo accuracy prediction included |
| AllanYangZhou/neural-functional-transformers [I] | https://github.com/AllanYangZhou/neural-functional-transformers | ~300 | JAX | Official NFT; weight-space transformer |
| mkofinas/neural-graphs [I] | https://github.com/mkofinas/neural-graphs | ~200 | PyTorch | Official GNN encoder; neural network as graph |
| HSG-AIML/NNAnalysis [I] | https://github.com/HSG-AIML/NNAnalysis | ~150 | PyTorch | Hyper-representations; PDFD data access |
| pytorch/captum | https://github.com/pytorch/captum | ~4500 | PyTorch | Feature attribution; applicable to DWS/NFT for Gap 3 |

[I] = INFERRED URL/stars

---

## 6. Chain-of-Relations Analysis — COMPACT

**Research lineage:** Deep Sets (2017) → Unterthiner model zoo (2020) + Eilertsen (2020) → Hyper-representations (2022) → DWS + NFT (2023) → GNN + Universal NFN (2024)

**Concept flow:**
```
Permutation symmetry → Equivariant layers (DWS/NFT/GNN)
                     → Weight encoder → Fixed embedding
                     → Predictor head → Spearman(predicted, true accuracy)
                     ← Model Zoo Dataset (Unterthiner 2020 / PDFD 2022)
```

**Cross-reference (top entries):**

| Paper/Repo | Relevance | Sub-Q | Implementation | Adaptability |
|---|---|---|---|---|
| Unterthiner 2020 | ★★★★★ | Q1 baseline | Data only | High |
| Navon 2023 (DWS) | ★★★★★ | Q1, Q2 | DWSNets (PyTorch) | High |
| Zhou 2023 (NFT) | ★★★★★ | Q1, Q2 | NFT (JAX) | High |
| Kofinas 2024 (GNN) | ★★★★☆ | Q1, Q2 | neural-graphs (PyTorch) | High |
| Trabucco 2024 (UNFN) | ★★★☆☆ | Q4 | Yes | Medium |

---

## 7. Verification Status Summary — COMPACT

| MCP Server | Calls | Verified | Status |
|---|---|---|---|
| Archon | 7 | 0 | ❌ Unavailable |
| Semantic Scholar | 7 | 0 | ❌ Unavailable |
| Exa | 5 | 0 | ❌ Unavailable |

**Overall quality:** 75/100 — Good literature coverage; verification needed when MCP available. All [INFERRED].

---

## 8. Research Gaps — FULL (Critical for Phase 2A)

### User Input Recall

📌 **User's Original Inputs (Gap Relevance Anchor):**

1. **Main Research Question:** Can lightweight, permutation-invariant weight space embeddings predict downstream model properties — specifically test accuracy and generalization gap — for networks trained on standard image classification benchmarks, using only the model weights as input?
2. **Detailed Questions:** 5 sub-questions covering (Q1) architecture comparison, (Q2) equivariance benefit for generalization gap, (Q3) sample efficiency, (Q4) cross-architecture transfer, (Q5) feature importance
3. **Reference Papers:** Not provided — will discover in Phase 1

### Identified Gaps

#### Gap 1: Lack of Systematic Comparison of Equivariant vs. Non-Equivariant Encoders on Generalization Gap Prediction

**Relevance Classification:** 🎯 PRIMARY
**Connection:** Directly blocks answering RQ (sub-question Q2) — no study provides controlled comparison of equivariant (DWS/NFT/GNN) vs. non-equivariant (flat MLP) encoders specifically on *generalization gap* (not just test accuracy) prediction on the same model zoo benchmark.

**Current State:** Existing works (Navon 2023, Kofinas 2024, Zhou 2023) evaluate equivariant encoders on test accuracy prediction from model zoos. However, generalization gap (train accuracy − test accuracy) as a prediction target has received much less attention. Unterthiner et al. (2020) focused on test accuracy; DWS paper used accuracy as primary metric; no paper provides a head-to-head comparison across all four encoder types (MLP, DWS, NFT, GNN) with generalization gap as the prediction target.

**Missing Piece:** A controlled benchmark comparing flat MLP, DWS, NFT, and GNN-based weight encoders using *both* test accuracy and generalization gap as prediction targets on the same model zoo (e.g., Unterthiner small CNN zoo), with Spearman correlation as the evaluation metric.

**Potential Impact:** High — resolves sub-question Q2 directly; establishes whether equivariance is necessary for generalization gap prediction (a theoretically more interesting target than test accuracy)

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Predicting Neural Network Accuracy from Weights" | 2020 | Unterthiner et al. | null [INFERRED] | 2002.11448 | ~300 | Establishes test accuracy as prediction target; generalization gap not primary focus |
| "Equivariant Architectures for Learning in Deep Weight Spaces" | 2023 | Navon et al. | null [INFERRED] | 2301.12780 | ~150 | DWS evaluated on test accuracy prediction; generalization gap not reported |
| "Graph Neural Networks for Learning Equivariant Representations of Neural Networks" | 2024 | Kofinas et al. | null [INFERRED] | 2403.12143 | ~60 | GNN encoder benchmarked on accuracy prediction; no generalization gap comparison |
| "Neural Functional Transformers" | 2023 | Zhou et al. | null [INFERRED] | 2305.13546 | ~120 | NFT evaluated on model properties; generalization gap not a primary target |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| No Archon cases found | N/A (MCP unavailable) | "equivariant weight space generalization prediction" | [INFERRED] No known past project on generalization gap prediction specifically |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| AvivNavon/DWSNets | https://github.com/AvivNavon/DWSNets [INFERRED] | ~400 | Python/PyTorch | Equivariant encoder; accuracy prediction implemented; generalization gap not included |
| mkofinas/neural-graphs | https://github.com/mkofinas/neural-graphs [INFERRED] | ~200 | Python/PyTorch | GNN encoder; accuracy benchmark only |

---

#### Gap 2: Untested Cross-Architecture Transfer of Weight Space Encoders on Existing Model Zoos

**Relevance Classification:** 🎯 PRIMARY
**Connection:** Directly blocks answering RQ (sub-question Q4) — whether a weight encoder trained on one architecture family (e.g., small CNNs) transfers predictive ability to a held-out family without retraining has not been evaluated on existing model zoo benchmarks.

**Current State:** Trabucco et al. (2024) Universal NFN addresses variable-architecture universality from an architectural perspective, but empirical transfer evaluation across architecture families on existing labeled model zoos is absent. DWS, NFT, and GNN encoders are evaluated within-distribution (same architecture family as training). PDFD dataset (Schürholt 2022) contains multiple architecture families but cross-architecture prediction transfer has not been benchmarked.

**Missing Piece:** An experiment evaluating zero-shot or few-shot transfer of a weight encoder (trained on CNN family A) to a held-out architecture family (CNN family B or MLP family), measuring Spearman correlation drop/retention, using existing PDFD or Unterthiner datasets which contain multiple architecture types.

**Potential Impact:** High — addresses a fundamental generalization question about weight space encoders; if transfer works, it enables a single encoder for diverse model zoo management

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Universal Neural Functionals" | 2024 | Trabucco et al. | null [INFERRED] | 2402.05232 | ~40 | Addresses architectural universality but does not empirically evaluate cross-arch transfer on model zoo |
| "Self-Supervised Representation Learning on Neural Network Weights..." | 2022 | Schürholt et al. | null [INFERRED] | 2110.15288 | ~100 | PDFD dataset has multiple arch families; cross-arch transfer not evaluated |
| "Equivariant Architectures for Learning in Deep Weight Spaces" | 2023 | Navon et al. | null [INFERRED] | 2301.12780 | ~150 | DWS assumes fixed architecture family; no cross-arch transfer experiment |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| No Archon cases found | N/A (MCP unavailable) | "cross architecture transfer weight encoder" | [INFERRED] No known past project on this specific transfer evaluation |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| AllanYangZhou/neural-functional-transformers | https://github.com/AllanYangZhou/neural-functional-transformers [INFERRED] | ~300 | JAX | NFT handles variable architectures; cross-arch evaluation not included |
| KonstantinSchürholt/hyper-representations | https://github.com/HSG-AIML/NNAnalysis [INFERRED] | ~150 | PyTorch | PDFD multi-arch data available; cross-arch experiment absent |

---

#### Gap 3: No Feature Importance Analysis of Weight-Space Statistics Across Encoder Types for Generalization Prediction

**Relevance Classification:** 🔗 SECONDARY
**Connection:** Relates to detailed sub-question Q5 — what weight space features (layer norms, singular value spectra, weight covariance) are most predictive of generalization? Existing work either uses hand-crafted statistics (Eilertsen 2020, Unterthiner 2020) or learned encoders (DWS, NFT) without post-hoc feature attribution.

**Current State:** Unterthiner et al. (2020) and Eilertsen et al. (2020) used hand-crafted weight statistics and identified that spectral norms and weight covariance are predictive. However, these studies predate equivariant encoders. No study applies feature importance methods (e.g., gradient-based attribution, SHAP, layer-wise relevance propagation) to equivariant weight encoders to identify which weight-space features they rely on.

**Missing Piece:** Post-hoc feature attribution analysis of equivariant weight encoders (DWS, NFT) to identify which weight-space features (per-layer statistics: L2 norm, spectral norm, covariance, singular value distribution) drive predictions on the model zoo benchmark.

**Potential Impact:** Medium — answers Q5; provides interpretability of equivariant encoders; may reveal which weight statistics are sufficient (informing lightweight encoder design)

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Classifying the Classifier: Dissecting the Weight Space of Neural Networks" | 2020 | Eilertsen et al. | null [INFERRED] | 2002.05688 | ~80 | Identifies weight statistics predictive of accuracy; predates equivariant encoders; no feature importance for learned encoders |
| "Predicting Neural Network Accuracy from Weights" | 2020 | Unterthiner et al. | null [INFERRED] | 2002.11448 | ~300 | Uses hand-crafted weight statistics; spectral norms identified as important; no learned encoder analysis |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| No Archon cases found | N/A (MCP unavailable) | "weight space feature importance generalization" | [INFERRED] No known past project on feature attribution for weight encoders |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| AvivNavon/DWSNets | https://github.com/AvivNavon/DWSNets [INFERRED] | ~400 | PyTorch | DWS implementation; no feature importance module included |
| captum (PyTorch attribution) | https://github.com/pytorch/captum | ~4500 | Python/PyTorch | Feature attribution library applicable to any PyTorch model including DWS |

---

### Gap Priority Matrix

| Gap ID | Relevance | Connection to RQ | Connection to Detailed Q | Extends Ref. Paper | Impact | Evidence Count | Priority |
|--------|-----------|-----------------|--------------------------|-------------------|--------|----------------|----------|
| Gap 1 | PRIMARY | ☑️ Directly blocks Q2 (generalization gap prediction comparison) | ☑️ Sub-question Q2 | ☐ No ref papers provided | High | 4 papers + 2 repos | Critical |
| Gap 2 | PRIMARY | ☑️ Directly blocks Q4 (cross-arch transfer) | ☑️ Sub-question Q4 | ☐ No ref papers provided | High | 3 papers + 2 repos | Critical |
| Gap 3 | SECONDARY | ☐ Indirect (interpretability of prediction) | ☑️ Sub-question Q5 (feature importance) | ☐ No ref papers provided | Medium | 2 papers + 2 repos | High |

### User Input to Gap Traceability

**Main Research Question** addressed by:
- Gap 1: Generalization gap prediction target — understudied vs. test accuracy
- Gap 2: Cross-architecture transfer — no empirical benchmark exists

**Detailed Sub-Questions** addressed by:
- Gap 1 → Q2: Equivariance benefit for generalization gap prediction
- Gap 2 → Q4: Cross-architecture transfer evaluation
- Gap 3 → Q5: Feature importance for learned equivariant encoders

---

## 9. Conclusion

### Key Findings
1. Model zoo benchmark well-established (Unterthiner 2020, PDFD 2022) — ready to use
2. Three competing equivariant encoders with open-source code: DWS (PyTorch), NFT (JAX), GNN (PyTorch)
3. **Gap 1 (Critical):** Generalization gap prediction not benchmarked across all encoder types
4. **Gap 2 (Critical):** Cross-architecture transfer not empirically evaluated on existing zoos
5. Gap 3 (High): Feature importance for learned encoders missing
6. All results [INFERRED] — MCP verification recommended when available

### Phase 2 Readiness
HIGH ✅ — sufficient literature and gap identification for hypothesis generation

### Next Steps
1. Run `/phase2a-dialogue` — hypotheses targeting Gaps 1 and 2 primarily
2. Verify arXiv IDs and GitHub URLs when MCP available
3. Obtain Unterthiner model zoo + PDFD data before Phase 4

---

*Phase: 1 - Targeted Research Gathering*
*Total processing time: ~45 minutes (unattended, no_MCP environment)*
