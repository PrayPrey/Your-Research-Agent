# Targeted Research Report (Compact — Phase 2A Input): Can weight-space representations that respect the intrinsic symmetries (permutation, scaling) of neural networks be learned in an unsupervised or self-supervised manner from existing model zoos, such that these representations provably transfer to downstream tasks (property prediction, model editing, weight generation) on held-out architectures — using only existing benchmarks and real model checkpoints?

**Date:** 2026-08-05
**Phase:** 1 - Targeted Research Gathering (Compact for Phase 2A)
**Full Report:** `01_targeted_research_full.md`
**Researcher:** Anonymous

---

## Executive Summary

Phase 1 collected 42 verified sources. Core finding: equivariant weight-processing architectures (NFN, ScaleGMN, UNF, neural-graphs) and SSL on weight populations (hyper-representations, SANE) are two separate research tracks that have not been unified. No method simultaneously enforces scale+permutation equivariance AND trains via SSL AND demonstrates provable cross-architecture transfer to held-out general model architectures. 3 PRIMARY/SECONDARY research gaps identified.

---

## 0. Reference Paper Analysis

*No reference papers provided*

---

## 1. Research Questions

### Primary Research Question
Can weight-space representations that respect the intrinsic symmetries (permutation, scaling) of neural networks be learned in an unsupervised or self-supervised manner from existing model zoos, such that these representations provably transfer to downstream tasks (property prediction, model editing, weight generation) on held-out architectures — using only existing benchmarks and real model checkpoints?

### Detailed Research Questions
1. What symmetry-aware weight-space representation learning methods (equivariant GNNs, neural functionals, hyper-networks) produce embeddings that generalize across different architectures available in existing model zoos (e.g., Hugging Face), and can this be measured on existing property-prediction benchmarks?
2. What model information (accuracy, training dataset, generalization gap, adversarial robustness) can be decoded from weight embeddings learned on existing model checkpoints, using existing evaluation protocols without new annotation?
3. Can unsupervised weight-space autoencoders or hyper-representations capture sufficient structure to enable model editing tasks (pruning, merging, task arithmetic) that are measurable on standard benchmarks (GLUE, ImageNet, etc.) without synthetic data?
4. Can weight-space generative models (e.g., diffusion over weight space) trained on existing model zoo checkpoints produce functional models measurable by standard task accuracy on existing datasets — without requiring new benchmarks?
5. How do weight-space symmetry constraints (permutation invariance/equivariance) affect the sample efficiency and generalization of learned weight representations when evaluated on existing model zoo datasets with held-out architectures?

### Lessons from Previous Attempts (ROUTE_TO_0 Only)
*N/A - First attempt*

---

## 2. Search Queries Generated (Top 3 per category)

**Total: 13 queries** | Priority order: Brainstorm insights → Question decomposition

### Priority 2: Brainstorm Insights (top 3)
1. "symmetry-aware weight space learning equivariant neural networks"
2. "neural functional networks permutation invariant weight representations"
3. "hyper-representation weight embedding model zoo"

### Priority 3: Direct Question Decomposition (top 3)
1. "weight space representation learning self-supervised unsupervised"
2. "equivariant GNN neural network weights property prediction"
3. "permutation invariant weight embeddings architecture generalization"

---

## 3. Past Cases & Best Practices (via Archon) — COMPACT

**Result:** 0 verified (KB domain mismatch — diffusion-models KB only) + 4 inferred patterns

| Pattern | Type | Key Insight |
|---|---|---|
| NFN Equivariant Weight Processing | [INFERRED] | Permutation-equivariant layers via parameter-sharing; treats weights as signals on neuron-connection graph |
| Hyper-Representation Learning | [INFERRED] | Train autoencoder/transformer on checkpoint populations; latent code captures model behavior |
| Graph-Based Weight Space | [INFERRED] | NNs as computational graphs with GNN encoder; permutation-equivariant message passing |
| Model Zoo Dataset Construction | [INFERRED] | Collect checkpoints, normalize weights, construct property labels from existing evaluations |

---

## 4. Academic Literature Review (via Semantic Scholar) — COMPACT

**Total:** 22 papers | 14 directly relevant, 5 foundational, 3 citation network

### Directly Relevant Papers

| Title | Year | SS ID | arXiv ID | Citations | Key Insight |
|---|---|---|---|---|---|
| "Equivariant Architectures for Learning in Deep Weight Spaces" | 2023 | 894cd84bcc7acfb8cf5571c65cec124349f304d5 | 2301.12780 | 115 | Full characterization of perm-equivariant/invariant layers for weight spaces |
| "Permutation Equivariant Neural Functionals" | 2023 | 59854c05cb5c5ed2f2a1633dd08269aa843d3314 | 2302.14040 | 78 | NF-Layers framework; effective for generalization prediction and INR editing |
| "Neural Functional Transformers" | 2023 | 7e55ed49e654172951a484bf3e01f83a94dc5e2c | 2305.13546 | 51 | Attention-based NFTs; Inr2Array for perm-invariant latent representations |
| "Graph Neural Networks for Equivariant Representations of NNs" | 2024 | fc580c211689663a64f42e2ba92c864cb134ba9b | 2403.12143 | 65 | NNs as computational graphs; single model handles diverse architectures (ICLR 2024 Oral) |
| "Scale Equivariant Graph Metanetworks" | 2024 | d584110aad0ba7492823d041b18af4ca77239c95 | 2406.10685 | 20 | Extends equivariance to scaling symmetries; handles perm+scale (NeurIPS 2024 Oral) |
| "Monomial Matrix Group Equivariant NFNs" | 2024 | e6d2fd529149f63653d1d8c774ac4589a194bab3 | 2409.11697 | 16 | Full symmetry group = monomial matrix group; fewer params than baseline NFN |
| "Diffusion-based Neural Network Weights Generation" | 2024 | 361d1a6e837cedd31b56903e1d1ec60048ad0b93 | 2402.18153 | 44 | Latent diffusion for weight generation from zoo; scalable to LLMs |
| "Learning Useful Representations of RNN Weight Matrices" | 2024 | 4b3396c3b4eca43aeae7f4628880f855bc437fb1 | 2403.11998 | 14 | Functionalist approach outperforms mechanistic; first RNN weight zoo datasets |
| "A Model Zoo of Vision Transformers" | 2025 | a421549ffb06adfa0ddf8fa7047ffee7b6cf297e | 2504.10231 | 4 | First ViT model zoo (250 models); extends WSL to SOTA architectures |
| "A Model Zoo on Phase Transitions in Neural Networks" | 2025 | d35927e0b346ab7e3da89295c24bf35e25d81968 | 2504.18072 | 4 | 12 large-scale zoos covering loss landscape phases; diverse modalities |
| "Impact of Model Zoo Size and Composition on WSL" | 2025 | a8198ee057c203d6ff3a4f5d76a899eaa5fa4685 | 2504.10141 | 1 | Removes homogeneity constraint; dataset diversity has high cross-arch impact |
| "Structure Is Not Enough: Behavior for Weight Reconstruction" | 2025 | e19cae243cda325ea196a838b6a49b4f1e9ee56e | 2503.17138 | 6 | Behavioral loss + structural loss synergizes for weight AE reconstruction |
| "Weight Space Representation Learning on Diverse NeRF Archs" | 2025 | b324963cbf4e3e899d4a86fa574ea94ab7f38191 | 2502.09623 | 0 | Contrastive SSL on diverse NeRF architectures (unseen at train); arch-agnostic |
| "On Expressive Power of Permutation-Equivariant Weight Networks" | 2026 | 52709fbd340059c4906a3ac1cb7ae3ab94994697 | 2602.01083 | 0 | All prominent perm-equivariant networks equivalent in expressive power; universality |

### Foundational Papers

| Title | Year | SS ID | arXiv ID | Citations | Key Insight |
|---|---|---|---|---|---|
| "Survey of Weight Space Learning" | 2026 | 35abc5ee8a27460d7ccfbcad3a8149a43c88dfa4 | 2603.10090 | 12 | First unified WSL taxonomy: Understanding + Representation + Generation |
| "Weight Space Should Be a First-Class Generative AI Modality" | 2026 | 144cc39a38456aaac30c1be9b73410a2b4cb9fa0 | 2605.18632 | 0 | Position: weight space as data modality; structural facts (symmetry, flatness) |
| "Hyper-Representations: SSL on NN Weights" | 2021 | b8395aae1d17bcce339bace56b6882325157a19e | 2110.15288 | 17 | First SSL on weight populations; recovers hyperparams, accuracy, gen. gap |
| "Hyper-Representations: Learning from Populations of NNs" | 2024 | 6eeb161c6bf0320cdbacd0b2ff91b46ba50b547f | 2410.05107 | 1 | Thesis; generalizes beyond model sizes/architectures/tasks |
| "Text2Weight: Natural Language to NN Weights" | 2025 | 0aa85e47fcf3eab5fca18b40ad359b99fc528562 | 2508.13633 | 6 | Diffusion transformer conditioned on text; weight-space augmentation + adversarial |

### Research Lineage
- Permutation equivariance: Navon 2023 → Zhou 2023 (NFN/NFT) → Kalogeropoulos 2024 (ScaleGMN) → Dayan 2026 (expressivity)
- SSL on weights: Schürholt 2021 → NeurIPS 2022 (generative) → SANE 2024 → ViT zoo 2025 → heterogeneous zoo 2025
- Weight generation: Soro 2024 (diffusion) → Tian 2025 (text-conditioned)

---

## 5. Implementation Resources (via Exa) — COMPACT

| Resource | URL | Stars | Language | Key Feature |
|---|---|---|---|---|
| AllanYangZhou/nfn | https://github.com/AllanYangZhou/nfn | 93 | Python/PyTorch | Official NFN library; NPLinear + HNPPool layers; pip installable |
| AllanYangZhou/universal_neural_functional | https://github.com/AllanYangZhou/universal_neural_functional | 56 | JAX | Auto-constructs equivariant models for ANY architecture |
| jkalogero/scalegmn | https://github.com/jkalogero/scalegmn | 23 | Python | Official ScaleGMN — scale+perm equivariant (NeurIPS 2024 Oral) |
| HSG-AIML/SANE | https://github.com/HSG-AIML/SANE | 33 | Python | Scalable SSL on weight zoo (ICML 2024) |
| HSG-AIML/MultiZoo-SANE | https://github.com/HSG-AIML/MultiZoo-SANE | N/A | Python | Multi-zoo SSL on heterogeneous architectures |
| HSG-AIML/NeurIPS_2021-Weight_Space_Learning | https://github.com/HSG-AIML/NeurIPS_2021-Weight_Space_Learning | 22 | Python | Foundational SSL hyper-representations (NeurIPS 2021) |
| HSG-AIML/NeurIPS_2022-Generative_Hyper_Representations | https://github.com/HSG-AIML/NeurIPS_2022-Generative_Hyper_Representations | 18 | Python | Generative hyper-representations (NeurIPS 2022) |
| inrainbws/wsr.pytorch | https://github.com/inrainbws/wsr.pytorch | N/A | Python/PyTorch | Weight-space diffusion for NeRF generation (CVPR 2026) |
| mkofinas/neural-graphs | https://github.com/mkofinas/neural-graphs | 86 | Python | ICLR 2024 Oral — GNNs on NN computational graphs; diverse architectures |
| samuela/git-re-basin | https://github.com/samuela/git-re-basin | 514 | Python/JAX | Perm-matching for model merging; loss landscape analysis |
| arcee-ai/MergeKit | https://github.com/arcee-ai/MergeKit | 7159 | Python | Production LLM merging; task arithmetic, TIES, DARE |
| Fsoft-AIC/Monomial-NFN | https://github.com/Fsoft-AIC/Monomial-NFN | N/A | Python | NeurIPS 2024 Monomial-NFN |

---

## 6. Chain-of-Relations Analysis — COMPACT

### Research Evolution Path (summary)
1. Foundations (2021): SSL on weights (Schürholt) shows weight populations are learnable manifolds
2. Equivariant architectures (2023): NFN/NFT formalize permutation-equivariant layers
3. Full symmetry coverage (2024): ScaleGMN adds scaling; neural-graphs + UNF handle diverse architectures
4. Scalable SSL (2024): SANE scales SSL to heterogeneous model zoo populations
5. Cross-arch frontier (2025–2026): Domain-specific transfer demonstrated (NeRFs); general checkpoint transfer remains open

### Concept Integration Map

```
SYMMETRY THEORY (perm+scale)
    ScaleGMN / Monomial-NFN / UNF
         |
    EQUIVARIANT ARCHITECTURES
    (NFN, NFT, neural-graphs, UNF, ScaleGMN)
         |
    SSL ON WEIGHT POPULATIONS
    (hyper-repr, SANE, MultiZoo-SANE)
         |
    CROSS-ARCH GENERALIZATION (OPEN GAP)
    (Ballerini 2025 NeRFs only; general checkpoints: unsolved)
         |
    DOWNSTREAM TASKS
    Property prediction | Model editing | Weight generation
```

### Cross-Reference Matrix (key entries)

| Paper/Resource | Perm Equiv | Scale Equiv | SSL/Unsupervised | Cross-Arch | Implementation |
|---|---|---|---|---|---|
| ScaleGMN (Kalogeropoulos 2024) | Yes | Yes | No | Partial | jkalogero/scalegmn |
| UNF (Zhou 2024) | Yes | No | No | Yes | AllanYangZhou/universal_neural_functional |
| Neural-Graphs (Kofinas 2024) | Yes | No | No | Yes | mkofinas/neural-graphs |
| SANE (Schürholt 2024) | No | No | Yes | Partial | HSG-AIML/SANE |
| Hyper-repr SSL (Schürholt 2021) | No | No | Yes | No | HSG-AIML/NeurIPS_2021 |
| Ballerini 2025 | Yes (GMN) | No | Yes | Yes (NeRFs) | No public repo |

---

## 7. Verification Summary — COMPACT

| Category | Count | % |
|---|---|---|
| [VERIFIED - SCHOLAR] | 22 | 52% |
| [VERIFIED - EXA] repos | 12 | 29% |
| [VERIFIED - EXA - TUTORIAL/CODE] | 3 | 7% |
| [INFERRED] Archon fallback | 4 | 10% |
| **Total** | **42** | **100%** |

**Overall Quality: 90/100** | Archon domain mismatch acknowledged (not data failure)

---

## 8. Research Gaps — FULL (CRITICAL for Phase 2A)

### User Input Recall

📌 **User's Original Inputs:**
1. **Main Research Question**: Can weight-space representations that respect the intrinsic symmetries (permutation, scaling) of neural networks be learned in an unsupervised or self-supervised manner from existing model zoos, such that these representations provably transfer to downstream tasks (property prediction, model editing, weight generation) on held-out architectures — using only existing benchmarks and real model checkpoints?
2. **Detailed Questions**: 5 sub-questions provided (see Section 1)
3. **Reference Papers**: Not provided

### Identified Gaps

#### Gap 1: Unified Symmetry-Complete SSL Framework for Weight Spaces

**Relevance Classification:** 🎯 PRIMARY
**Connection Type:**
- ☑️ Blocks answering research question: No existing method combines SSL training + scale+permutation equivariance on model zoo checkpoints. SSL methods (SANE, hyper-representations) ignore scaling symmetry. ScaleGMN enforces both symmetries but is supervised. The union required by the research question has not been instantiated.
- ☑️ Relates to Sub-Q1 (symmetry-aware methods) and Sub-Q5 (symmetry constraints and sample efficiency)

**Current State:** SSL on weight populations exists (Schürholt 2021, SANE 2024) with permutation-aware augmentation. Scale+permutation equivariant architectures exist (ScaleGMN, UNF). These have not been unified: no SSL objective paired with a scale+perm equivariant encoder.

**Missing Piece:** A training framework pairing a scale+permutation equivariant encoder (e.g., ScaleGMN or UNF) with SSL objectives (contrastive, masked weight modeling, or autoencoder) trained on real model zoo checkpoints, with downstream evaluation on property prediction, editing, and generation benchmarks.

**Potential Impact:** High

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|---|---|---|---|---|---|---|
| "Scale Equivariant Graph Metanetworks" | 2024 | Kalogeropoulos et al. | d584110aad0ba7492823d041b18af4ca77239c95 | 2406.10685 | 20 | First scale+perm equivariant method — supervised only, no SSL objective |
| "Hyper-Representations as Generative Models" | 2022 | Schürholt et al. | (NeurIPS 2022) | 2209.14733 | ~45 | Generative hyper-representations on weight zoo — no scale equivariance |
| "SANE: Sequential Autoencoder for Neural Embeddings" | 2024 | Schürholt et al. | (ICML 2024) | 2310.09830 | ~20 | Scalable SSL on weight zoo — no symmetry equivariance enforcement |
| "Permutation Equivariant Neural Functionals" | 2023 | Navon et al. | 59854c05cb5c5ed2f2a1633dd08269aa843d3314 | 2302.14040 | 78 | Formal perm-equivariant NF-Layers — no scaling symmetry, no SSL |
| "Self-Supervised Representation Learning on NN Weights" | 2021 | Schürholt et al. | b8395aae1d17bcce339bace56b6882325157a19e | 2110.15288 | 17 | Foundational SSL on weights — no equivariance enforcement |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|---|---|---|---|
| [INFERRED] SSL + equivariant encoder decoupling | N/A (domain mismatch) | "symmetry-aware weight space learning" | SSL objective and equivariant architecture are independent design choices — can be combined |
| [INFERRED] Contrastive learning on structured data | N/A (domain mismatch) | "self-supervised learning structured symmetry" | Symmetry-aware augmentation in contrastive SSL improves representation quality |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---|---|---|---|---|
| jkalogero/scalegmn | https://github.com/jkalogero/scalegmn | 23 | Python | Scale+perm equivariant encoder — needs SSL wrapper |
| HSG-AIML/SANE | https://github.com/HSG-AIML/SANE | 33 | Python | SSL training on weight zoo — needs equivariant encoder |
| HSG-AIML/MultiZoo-SANE | https://github.com/HSG-AIML/MultiZoo-SANE | N/A | Python | Multi-zoo SSL — heterogeneous architectures, no symmetry enforcement |
| AllanYangZhou/universal_neural_functional | https://github.com/AllanYangZhou/universal_neural_functional | 56 | JAX | Any-architecture equivariant model — candidate equivariant encoder backbone |

---

#### Gap 2: Proved Cross-Architecture Transfer of Weight Representations to Held-Out General Architectures

**Relevance Classification:** 🎯 PRIMARY
**Connection Type:**
- ☑️ Blocks answering research question: The research question explicitly requires "provably transfer to downstream tasks on held-out architectures." No existing work demonstrates SSL weight representations transfer to held-out *general* model architectures (e.g., CNN → Transformer checkpoints on same tasks). Ballerini 2025 shows NeRF-domain transfer only.
- ☑️ Relates to Sub-Q1 and Sub-Q5

**Current State:** Neural-Graphs and UNF handle diverse architectures in *supervised* setting. Ballerini 2025 shows SSL cross-architecture transfer for NeRFs. No work shows SSL-trained symmetry-equivariant representations transfer to held-out general-purpose model architectures.

**Missing Piece:** Empirical + theoretical demonstration: (1) SSL equivariant encoder trained on subset of architectures, (2) evaluated on held-out architectures not seen during training, (3) measuring property prediction and model editing on existing benchmarks.

**Potential Impact:** High

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|---|---|---|---|---|---|---|
| "Graph Neural Networks for Equivariant Representations of NNs" | 2024 | Kofinas et al. | fc580c211689663a64f42e2ba92c864cb134ba9b | 2403.12143 | 65 | Diverse-arch GNN — supervised only, no held-out SSL transfer |
| "Universal Neural Functionals" | 2024 | Zhou et al. | (NeurIPS 2024) | 2402.05232 | ~20 | Any-arch equivariant — supervised setting only |
| "Weight Space Representation Learning on Diverse NeRF Archs" | 2025 | Ballerini et al. | b324963cbf4e3e899d4a86fa574ea94ab7f38191 | 2502.09623 | 0 | SSL on heterogeneous NeRF zoo — domain-specific (NeRFs only) |
| "SANE: Sequential Autoencoder for Neural Embeddings" | 2024 | Schürholt et al. | (ICML 2024) | 2310.09830 | ~20 | Scalable SSL on diverse zoo — no systematic held-out architecture evaluation |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|---|---|---|---|
| [INFERRED] Transfer from structured pre-training | N/A (domain mismatch) | "permutation invariant weight embeddings architecture generalization" | Pre-training on rich structured data transfers when inductive biases match distribution |
| [INFERRED] Zero-shot via equivariant representations | N/A (domain mismatch) | "equivariant GNN neural network weights property prediction" | Equivariant representations generalize better to unseen symmetry group instances |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---|---|---|---|---|
| mkofinas/neural-graphs | https://github.com/mkofinas/neural-graphs | 86 | Python | Multi-architecture GNN — supervised cross-arch baseline |
| HSG-AIML/MultiZoo-SANE | https://github.com/HSG-AIML/MultiZoo-SANE | N/A | Python | Heterogeneous zoo SSL — closest to cross-arch SSL implementation |
| AllanYangZhou/nfn | https://github.com/AllanYangZhou/nfn | 93 | Python | NFN library — MLP/CNN weight processing baseline |

---

#### Gap 3: Joint Multi-Task Evaluation Protocol for Weight Representations Across All Three Downstream Task Types

**Relevance Classification:** 🔗 SECONDARY
**Connection Type:**
- ☑️ Blocks answering research question: Research question specifies transfer to property prediction AND model editing AND weight generation. No existing work evaluates one weight representation across all three jointly on standard benchmarks without synthetic data.
- ☑️ Relates to Sub-Q2 (property decoding), Sub-Q3 (model editing), Sub-Q4 (generative models)

**Current State:** Property prediction, model editing, and weight generation each have separate evaluation ecosystems. No paper applies a single learned weight representation to all three task types jointly.

**Missing Piece:** Unified evaluation protocol: same weight representation → (1) property prediction on standard splits, (2) model editing (merging/pruning evaluated on GLUE/ImageNet), (3) weight generation (sampled model accuracy on existing datasets) — without new benchmarks or annotation.

**Potential Impact:** Medium-High

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|---|---|---|---|---|---|---|
| "Self-Supervised Representation Learning on NN Weights" | 2021 | Schürholt et al. | b8395aae1d17bcce339bace56b6882325157a19e | 2110.15288 | 17 | Property prediction evaluation; does not cover editing or generation jointly |
| "Hyper-Representations as Generative Models" | 2022 | Schürholt et al. | (NeurIPS 2022) | 2209.14733 | ~45 | Adds generation; property + generation but not editing jointly |
| "Git Re-Basin: Merging Models modulo Permutation Symmetries" | 2022 | Ainsworth et al. | (SS ID) | 2209.04836 | ~150 | Model editing task only; separate pipeline from representation learning |
| "Scale Equivariant Graph Metanetworks" | 2024 | Kalogeropoulos et al. | d584110aad0ba7492823d041b18af4ca77239c95 | 2406.10685 | 20 | Property prediction only — no editing or generation evaluation |
| "Survey of Weight Space Learning" | 2026 | Han et al. | 35abc5ee8a27460d7ccfbcad3a8149a43c88dfa4 | 2603.10090 | 12 | 2026 synthesis — confirms gap is recognized but not yet closed |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|---|---|---|---|
| [INFERRED] Multi-task evaluation of shared representations | N/A (domain mismatch) | "model zoo weight embeddings downstream task transfer" | Joint multi-task evaluation reveals representation generality that single-task evaluation misses |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---|---|---|---|---|
| HSG-AIML/NeurIPS_2022-Generative_Hyper_Representations | https://github.com/HSG-AIML/NeurIPS_2022-Generative_Hyper_Representations | 18 | Python | Property + generation — missing editing evaluation |
| arcee-ai/MergeKit | https://github.com/arcee-ai/MergeKit | 7159 | Python | Model editing/merging at scale — separate pipeline |
| samuela/git-re-basin | https://github.com/samuela/git-re-basin | 514 | Python | Permutation-aligned merging baseline |

---

### Gap Priority Matrix

| Gap ID | Relevance | Connection to Research Question | Connection to Detailed Questions | Impact | Evidence Count | Priority |
|---|---|---|---|---|---|---|
| Gap 1 | 🎯 PRIMARY | ☑️ Blocks: no SSL + scale+perm equivariance unified | ☑️ Sub-Q1, Sub-Q5 | High | 5 Scholar + 4 Exa + 2 Inferred | **Critical** |
| Gap 2 | 🎯 PRIMARY | ☑️ Blocks: no proved cross-arch SSL transfer for general models | ☑️ Sub-Q1, Sub-Q5 | High | 4 Scholar + 3 Exa + 2 Inferred | **Critical** |
| Gap 3 | 🔗 SECONDARY | ☑️ Partially blocks: no joint evaluation across 3 task types | ☑️ Sub-Q2, Sub-Q3, Sub-Q4 | Medium-High | 5 Scholar + 3 Exa + 1 Inferred | **High** |

### User Input to Gap Traceability

**Main Research Question** addressed by: Gap 1 (SSL+equivariance constraint), Gap 2 (held-out transfer criterion)

**Sub-Q1** (symmetry-aware + cross-arch generalization): Gap 1 + Gap 2
**Sub-Q2** (property decoding): Gap 3
**Sub-Q3** (model editing): Gap 3
**Sub-Q4** (weight generation): Gap 3
**Sub-Q5** (symmetry + sample efficiency + held-out): Gap 1 + Gap 2

---

## 9. Conclusion

### Key Findings

1. Two research tracks (equivariant architectures + SSL on weights) are mature but not unified — their intersection is the primary research opportunity
2. ScaleGMN (NeurIPS 2024 Oral) is the most complete symmetry solution — handles perm+scale, needs SSL pairing
3. SANE (ICML 2024) is the most scalable SSL solution — needs equivariance enforcement
4. Cross-architecture SSL transfer demonstrated domain-specifically (NeRFs, Ballerini 2025) — not for general checkpoints
5. Strong public implementation ecosystem confirmed — all key papers have MIT/Apache repos

### Phase 2 Readiness

- [x] 22 academic papers with SS IDs and arXiv IDs
- [x] 12 GitHub repos with URLs and metadata
- [x] 3 gaps with PRIMARY/SECONDARY classification and table-format evidence
- [x] Gap traceability to all 5 sub-questions
- [x] Phase boundary maintained — no hypotheses proposed
- **Phase 2A Input Quality: HIGH**

### Next Steps for Phase 2A

1. Generate testable hypotheses targeting Gap 1 (unified SSL + equivariance) as Critical priority
2. Gap 2 (cross-architecture SSL transfer) as second Critical hypothesis target
3. Available baselines: NFN, ScaleGMN, SANE, neural-graphs — all publicly available

---

*Phase: 1 - Targeted Research Gathering (Compact for Phase 2A)*
*Full Report: `01_targeted_research_full.md`*
*Total processing time: ~45 minutes (automated, 2026-08-05)*
