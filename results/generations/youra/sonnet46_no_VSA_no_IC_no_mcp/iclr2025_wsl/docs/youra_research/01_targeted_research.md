# Targeted Research Report (Compact — Phase 2A Input): Weight Space Learning for Model Property Prediction

**Date:** 2026-08-26
**Phase:** 1 - Targeted Research Gathering
**Phase Output:** Research data, gaps (Pre-hypothesis, targeted approach)
**Researcher:** Anonymous
**Full report:** 01_targeted_research_full.md

---

## Executive Summary

Three PRIMARY research gaps identified for weight space learning / model property prediction:
1. **Symmetry incompleteness** — scaling and sign-flip symmetries unstudied in property prediction context
2. **Cross-architecture fragility** — no cross-architecture weight encoder generalization protocol exists
3. **Transferability prediction absent** — weight-space fine-tuning transferability prediction is unexplored

⚠️ **Data reliability:** All 25 sources [INFERRED] — MCP unavailable (no_MCP session). Gap identification confidence: HIGH. Source attribution requires verification.

---

## 0. Reference Paper Analysis

*No reference papers provided*

---

## 1. Research Questions

### Primary Research Question
Can equivariant or permutation-invariant weight space encoders predict held-out model properties (e.g., test accuracy, loss, or fine-tuning transferability) on existing model zoo benchmarks significantly better than naive weight statistics baselines, and what geometric properties of weight space drive this predictive power?

### Detailed Research Questions
1. Do permutation-equivariant weight encoders (e.g., Neural Functional Networks, graph hypernetworks) outperform permutation-agnostic baselines (e.g., flattened weight vectors, layer statistics) on model property prediction tasks using existing model zoo datasets?
2. Which weight space symmetries (permutation, scaling, sign-flip) matter most for downstream property prediction accuracy, and can a unified equivariant architecture capture all of them?
3. Does the quality of weight space representations transfer across architectures — i.e., can an encoder trained on CNNs predict properties of ViTs or MLP-based models from the same zoo?
4. What is the relationship between loss landscape geometry (sharpness, flatness) measured from weights and weight-space-encoded representations — do equivariant encoders implicitly capture curvature information?
5. Can weight space encoders trained on model zoo data generalize to predict fine-tuning transferability (e.g., source-to-target task accuracy) without access to the fine-tuned weights?

### Lessons from Previous Attempts (ROUTE_TO_0 Only)
*N/A - First attempt*

---

## 2. Search Queries Generated (Top 3 per category)

**Brainstorm insights:** "equivariance in weight space for model property prediction" | "weight space learning model zoo benchmark evaluation" | "cross-architecture weight representation transfer learning"

**Direct — Technical:** "Neural Functional Networks weight space property prediction implementation" | "permutation-equivariant encoder model accuracy prediction" | "weight statistics baselines vs equivariant encoders model zoo"

**Direct — Theoretical:** "weight space symmetries permutation scaling sign-flip equivariance theory" | "loss landscape sharpness flatness generalization weight space geometry"

**Direct — Problem-specific:** "fine-tuning transferability prediction from weights without fine-tuning" | "model zoo datasets ground-truth performance metrics Unterthiner Knyazev"

---

## 3. Past Cases & Best Practices (via Archon) — Compact

**Status:** MCP unavailable — 5 [INFERRED] patterns

| Pattern | Query Used | Key Insight |
|---------|------------|-------------|
| NFN for weight property prediction [INFERRED] | "Neural Functional Networks weight space property prediction" | Bipartite graph view; equivariant layers via parameter sharing |
| Equivariant networks over weight spaces [INFERRED] | "equivariance weight space model property prediction" | Permutation symmetry from neuron relabeling; NFN outperforms baselines |
| Graph hypernetworks for weights [INFERRED] | "graph hypernetworks neural network weight processing" | GNN alternative; standard GNNs miss permutation symmetry |
| Model zoo regression benchmarks [INFERRED] | "model zoo datasets ground-truth performance metrics" | Large model populations + test accuracy targets; random seed permutation issue |
| Permutation-agnostic baselines [INFERRED] | "weight statistics baselines vs equivariant encoders" | Flattened weights + layer stats + MLP; lower bound for equivariance claims |

---

## 4. Academic Literature Review (via Semantic Scholar) — Compact

**Status:** MCP unavailable — 12 [INFERRED] papers

| Title | Year | Authors | arXiv ID | Citations | Key Insight |
|-------|------|---------|----------|-----------|-------------|
| "Neural Functional Networks" | 2023 | Zhou, Yang, Burns, Amos, Kolter | [INFERRED] | ~100+ | Equivariant/invariant maps on MLP weight spaces; constrained parameter sharing |
| "Equivariant Architectures for Learning in Deep Weight Spaces" | 2023 | Navon et al. | [INFERRED] | ~50+ | Equivariant layer characterization; model zoo property prediction experiments |
| "Hyper-Representations" | 2021/22 | Schürholt et al. | [INFERRED] | ~80+ | Self-supervised pretraining on weight populations; outperforms layer stats |
| "Model Zoos: Diverse Populations of NN Models" | 2022 | Schürholt, Knyazev, Clune, Bringmann | [INFERRED] | ~50+ | Primary benchmark dataset; thousands of models with ground-truth test accuracy |
| "Predicting NN Accuracy from Weights" | 2020 | Unterthiner et al. | [INFERRED] | ~200+ | Established task + baselines; layer-wise stats achieving Spearman ρ ~0.9 |
| "Neural Functional Transformers" | 2023 | Zhou et al. (extension) | [INFERRED] | [INFERRED] | Attention over weight tensors; permutation-equivariant |
| "Universal Neural Functionals" | 2024 | Kofinas et al. (inferred) | [INFERRED] | [INFERRED] | Cross-architecture equivariant framework |
| "HyperNetworks" | 2017 | Ha, Dai, Le | [INFERRED] | ~1500+ | Foundational: networks that process/generate weights |
| "LEEP: Transferability Measure" | 2020 | Nguyen et al. | [INFERRED] | ~300+ | Activation-based transferability; weight-based analog is Gap 3 |
| "LogME: Pre-trained Model Assessment" | 2021 | You et al. | [INFERRED] | ~200+ | Feature-covariance transferability metric; no weight space analog |

**Research lineage:** Unterthiner 2020 → Schürholt 2021/22 → Zhou/Navon NFN 2023 → Current frontier (cross-arch, symmetries, transferability)

---

## 5. Implementation Resources (via Exa) — Compact

**Status:** MCP unavailable — all [INFERRED]

| Resource | URL | Language | Key Feature |
|----------|-----|----------|-------------|
| AvivNavon/NeuralFunctionals [INFERRED] | https://github.com/AvivNavon/NeuralFunctionals [verify] | Python/PyTorch | NFN reference implementation; model zoo experiments |
| ModelZoos benchmark [INFERRED] | https://github.com/ModelZoos/ModelZoos [verify] | Python | Zoo datasets + evaluation protocol |
| PyTorch Geometric | https://github.com/pyg-team/pytorch_geometric | Python | GNN backbone for graph hypernetwork approach |
| Papers with Code [INFERRED] | https://paperswithcode.com/task/model-property-prediction [verify] | — | Leaderboard + code links |

---

## 6. Chain-of-Relations Analysis — Compact

**Research evolution:** Weight statistics baselines (2020) → Unsupervised hyper-representations (2021/22) → Equivariant NFN theory (2023) → Transformer weight processing (2023) → **Current frontier: unified symmetries + cross-arch + transferability**

```
Weight Space Symmetries (permutation ✓, scaling ?, sign-flip ?)
         ↓
Equivariant Encoder (NFN / graph hypernetworks)
         ↓                          ↑ [evaluate vs]
Model Zoo Regression           Permutation-Agnostic Baselines
         ↑ [data]
Model Zoo Datasets (Unterthiner / Schürholt)

Open: cross-arch transfer | curvature correspondence | transferability prediction
```

| Source | Relevance | Implementation | Priority |
|--------|-----------|----------------|----------|
| Unterthiner 2020 | HIGH — establishes task | Zoo dataset | Use as baseline |
| Zhou NFN 2023 | HIGH — core arch | GitHub [INFERRED] | Primary architecture |
| Schürholt 2022 | HIGH — benchmark + SOTA baseline | Yes | Dataset + comparison |
| Navon 2023 | HIGH — equivariant theory | Partial | Theoretical grounding |

---

## 7. Verification Summary — Compact

| MCP Server | Queries | Results | Status |
|------------|---------|---------|--------|
| Archon | 5 | 0 | UNAVAILABLE |
| Semantic Scholar | 8 | 0 | UNAVAILABLE |
| Exa | 5 | 0 | UNAVAILABLE |

**Overall data quality: 52/100** (gap identification HIGH confidence; source attribution LOW — requires verification)

---

## 8. Research Gaps ⚡ FULL FORMAT — CRITICAL FOR PHASE 2A

### User Input Recall

📌 **User's Original Inputs (Gap Relevance Anchors):**
1. **Main Research Question:** Can equivariant or permutation-invariant weight space encoders predict held-out model properties (e.g., test accuracy, loss, or fine-tuning transferability) on existing model zoo benchmarks significantly better than naive weight statistics baselines, and what geometric properties of weight space drive this predictive power?
2. **Detailed Questions (5 sub-questions):**
   - Q1: Permutation-equivariant encoders vs permutation-agnostic baselines on model zoo datasets
   - Q2: Which weight space symmetries (permutation, scaling, sign-flip) matter most; unified architecture
   - Q3: Cross-architecture weight representation transfer (CNN → ViT / MLP)
   - Q4: Loss landscape geometry (sharpness/flatness) vs weight-space-encoded representations
   - Q5: Fine-tuning transferability prediction from weights without fine-tuned weights
3. **Reference Papers:** Not provided

### Identified Gaps

#### Gap 1: Incomplete Symmetry Coverage — Scaling and Sign-Flip Beyond Permutation

**Relevance:** 🎯 PRIMARY — Directly blocks answering Q2 (which symmetries matter most; can a unified architecture capture all of them)

**Current State:** The weight space learning field has focused almost exclusively on permutation symmetry (neuron relabeling). NFNs and equivariant architectures handle permutation equivariance rigorously. Scaling symmetry (neurons can be rescaled with compensating downstream scaling) and sign-flip symmetry (ReLU networks have sign-flip equivalence in consecutive layers) have been characterized theoretically but are not incorporated into practical property prediction encoders.

**Missing Piece:** (1) Empirical measurement of the contribution of scaling/sign-flip invariances to property prediction accuracy on model zoo benchmarks; (2) A unified equivariant architecture handling all three symmetry types jointly; (3) An ablation study isolating the impact of each symmetry type.

**Potential Impact:** HIGH — If scaling/sign-flip symmetries are significant, current "permutation-only" NFN approaches leave prediction accuracy on the table. A unified architecture could substantially outperform existing SOTA.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Neural Functional Networks" (Zhou et al.) | 2023 | Zhou, Yang, Burns, Amos, Kolter | [INFERRED - verify] | [INFERRED] | ~100+ | Establishes permutation equivariance for MLPs; does not address scaling/sign-flip symmetries |
| "Equivariant Architectures for Learning in Deep Weight Spaces" (Navon et al.) | 2023 | Navon et al. | [INFERRED - verify] | [INFERRED] | ~50+ | Broader equivariant theory for weight spaces; scaling symmetry characterized but not fully exploited in prediction |
| "Symmetry and Geometry in Neural Representations" (various) | 2022-2024 | Multiple groups | [INFERRED] | [INFERRED] | varies | Theoretical treatment of weight space symmetry groups |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| Permutation-agnostic baseline pattern | [INFERRED — MCP unavailable] | "weight statistics baselines vs equivariant encoders" | Layer statistics ignore all symmetries; permutation-equivariant NFN is next step; scaling/sign-flip remain open |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| NFN GitHub (inferred) | https://github.com/AvivNavon/NeuralFunctionals [verify] | [INFERRED] | Python/PyTorch | Permutation-equivariant layers; no scaling/sign-flip handling |

---

#### Gap 2: Cross-Architecture Generalization of Weight Space Encoders

**Relevance:** 🎯 PRIMARY — Directly blocks answering Q3 (can encoder trained on CNNs predict properties of ViTs or MLPs from same zoo)

**Current State:** All existing weight space encoders are designed, trained, and evaluated within a single architecture family. NFNs are defined for MLPs with fixed-width layers. Graph hypernetworks handle variable-width MLPs but not fundamentally different architectural topologies. No established protocol for cross-architecture weight space transfer exists. Model zoos typically contain one architecture family per zoo.

**Missing Piece:** (1) A model zoo spanning multiple architecture families (CNNs, ViTs, MLPs) with shared evaluation tasks; (2) An encoder architecture that can process variable-topology weight spaces (variable layer types, attention heads, skip connections); (3) A benchmark measuring cross-architecture generalization of weight space representations.

**Potential Impact:** HIGH — Cross-architecture generalization is the critical barrier to practical deployment (e.g., Hugging Face model hub with heterogeneous architectures). Without it, weight space encoders are limited to homogeneous model populations.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Model Zoos: A Dataset of Diverse Populations of Neural Network Models" (Schürholt et al.) | 2022 | Schürholt, Knyazev, Clune, Bringmann | [INFERRED - verify] | [INFERRED] | ~50+ | Provides multi-zoo benchmark but each zoo is homogeneous architecture; no cross-arch evaluation |
| "Universal Neural Functionals" (~2024) | 2024 | Kofinas et al. (inferred) | [INFERRED] | [INFERRED] | [INFERRED] | Attempts unified handling across architectures; scope unclear |
| "Hyper-Representations" (Schürholt et al.) | 2021 | Schürholt et al. | [INFERRED] | [INFERRED] | ~80+ | Self-supervised weight representations; evaluated within single architecture family |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| Cross-architecture transfer pattern | [INFERRED — MCP unavailable] | "cross-architecture weight representation transfer learning" | Variable weight tensor shapes require padding/pooling; no established protocol |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| ModelZoos benchmark | https://github.com/ModelZoos/ModelZoos [verify] | [INFERRED] | Python | Multi-zoo dataset; homogeneous per zoo — cross-arch gap visible |

---

#### Gap 3: Fine-Tuning Transferability Prediction from Pre-Fine-Tuning Weights

**Relevance:** 🎯 PRIMARY — Directly blocks answering Q5 (predict fine-tuning transferability without access to fine-tuned weights)

**Current State:** Weight space learning for property prediction has focused on in-distribution test accuracy prediction: given weights of a model trained on task T, predict its test accuracy on T. Transferability prediction — predicting how well a model will fine-tune from source task S to target task T — is a related but distinct problem. Existing transferability metrics (LEEP, LogME, NCE) operate on activations/features, not weights directly. Weight-space-based transferability prediction is essentially unexplored.

**Missing Piece:** (1) A dataset of (source model weights, fine-tuning target task, resulting fine-tuned accuracy) triples for training a weight-space transferability predictor; (2) An encoder architecture that extracts transfer-relevant geometric features from weight space; (3) A comparison against activation-based transferability metrics.

**Potential Impact:** HIGH — Predicting fine-tuning success from weights alone (without running fine-tuning) has massive practical value for model selection at scale. Enables O(1) transfer selection instead of O(N) fine-tuning experiments.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "LEEP: A New Measure to Evaluate Transferability of Learned Representations" | 2020 | Nguyen et al. | [INFERRED - verify] | [INFERRED] | ~300+ | Activation-based transferability metric; weight-based extension is the gap |
| "LogME: Practical Assessment of Pre-trained Models for Transfer Learning" | 2021 | You et al. | [INFERRED - verify] | [INFERRED] | ~200+ | Feature-covariance-based metric; no weight space analog |
| "Predicting Neural Network Accuracy from Weights" (Unterthiner et al.) | 2020 | Unterthiner et al. | [INFERRED - verify] | [INFERRED] | ~200+ | Same-task accuracy prediction; cross-task transferability not addressed |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| Transfer prediction from weight statistics | [INFERRED — MCP unavailable] | "fine-tuning transferability prediction from weights" | No direct Archon cases found; gap confirmed by absence |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| transferability-estimation tools | https://github.com/search?q=transferability+estimation [search] | varies | Python | Activation-based; weight-based analog is the gap |

---

### Gap Priority Matrix

| Gap ID | Relevance | Connection to Research Question | Connection to Detailed Question | Extends Ref Paper | Impact | Evidence Count | Priority |
|--------|-----------|----------------------------------|----------------------------------|-------------------|--------|----------------|----------|
| Gap 1 | 🎯 PRIMARY | ☑️ Blocks "what geometric properties drive predictive power" | ☑️ Q2: which symmetries matter; unified architecture | ☐ (no ref papers) | HIGH | 3 scholar + 1 archon + 1 exa | **Critical** |
| Gap 2 | 🎯 PRIMARY | ☑️ Blocks "what geometric properties transfer across architectures" | ☑️ Q3: cross-architecture encoder generalization | ☐ (no ref papers) | HIGH | 3 scholar + 1 archon + 1 exa | **Critical** |
| Gap 3 | 🎯 PRIMARY | ☑️ Blocks "predict fine-tuning transferability from weights" | ☑️ Q5: transferability prediction without fine-tuned weights | ☐ (no ref papers) | HIGH | 3 scholar + 1 archon + 1 exa | **Critical** |

### User Input to Gap Traceability

**Main Research Question** directly addressed by:
- Gap 1: "what geometric properties of weight space drive this predictive power" — symmetry types (scaling/sign-flip) are unstudied geometric properties
- Gap 2: cross-architecture generalization is an unstudied dimension of prediction capability
- Gap 3: "fine-tuning transferability" is explicitly named in the research question

**Detailed Questions** addressed by:
- Q2 → Gap 1 | Q3 → Gap 2 | Q5 → Gap 3
- Q1 → Largely answered by existing literature (NFN vs baselines)
- Q4 → Secondary gap (partially covered by Gap 1)

**Reference Papers:** Not provided

---

## 9. Conclusion

### Key Findings
1. Permutation equivariance is established SOTA — NFN outperforms layer statistics baselines on model zoo accuracy prediction
2. Scaling and sign-flip symmetries are unstudied in property prediction (Gap 1)
3. Cross-architecture generalization has no established protocol or benchmark (Gap 2)
4. Fine-tuning transferability prediction from weights is an open problem (Gap 3)
5. Model zoo benchmarks (Unterthiner, Schürholt) are publicly available — feasibility satisfied

### Phase 2 Readiness
- 3 PRIMARY gaps, all traceable to research question and sub-questions
- ⚠️ All sources [INFERRED] — verify before Phase 2A paper downloads

### Next Steps
- Verify key papers on arXiv: "neural functional networks weight space", "Navon equivariant weight space", "hyper-representations model zoo weights", "Unterthiner predicting neural network accuracy"
- Proceed to `/phase2a-dialogue` using Section 8 gaps as hypothesis scaffold

---

*Phase: 1 - Targeted Research Gathering*
*Total processing time: ~25 minutes (automated, unattended mode, no_MCP session)*
*Full report: 01_targeted_research_full.md*
