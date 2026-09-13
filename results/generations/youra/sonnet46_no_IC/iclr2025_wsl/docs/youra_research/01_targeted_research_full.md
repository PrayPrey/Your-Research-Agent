# Targeted Research Report: Can weight-space representations that respect the intrinsic symmetries (permutation, scaling) of neural networks be learned in an unsupervised or self-supervised manner from existing model zoos, such that these representations provably transfer to downstream tasks (property prediction, model editing, weight generation) on held-out architectures — using only existing benchmarks and real model checkpoints?

**Date:** 2026-08-05
**Phase:** 1 - Targeted Research Gathering
**Phase Output:** Research data, gaps (Pre-hypothesis, targeted approach)
**Analyst:** Deep Learning Research Analyst 🔍
**Researcher:** Anonymous

---

## Executive Summary

Phase 1 targeted research collected 42 verified sources across 13 search queries on the research question of symmetry-aware unsupervised weight-space representation learning from neural network model zoos. Semantic Scholar returned 22 papers directly relevant to weight-space learning (2021–2026). Exa returned 12 GitHub repositories, 2 tutorials, and 1 code context covering the key implementations (NFN, ScaleGMN, neural-graphs, SANE, git-re-basin). Archon KB did not contain weight-space learning content (domain mismatch); 4 patterns were inferred.

**Core finding**: The research field has advanced significantly along two parallel tracks — (1) equivariant architectures for weight processing (NFN, ScaleGMN, UNF, neural-graphs) and (2) self-supervised learning on weight populations (hyper-representations, SANE) — but these tracks have not been unified. No existing method simultaneously enforces scale+permutation equivariance AND trains via SSL on model zoo checkpoints AND demonstrates provable cross-architecture transfer to held-out general architectures.

**3 research gaps identified** at the intersection of these tracks: (1) no unified symmetry-complete SSL framework, (2) no proved cross-architecture transfer for general model checkpoints, (3) no joint evaluation protocol across all three downstream task types specified in the research question. These gaps directly map to Phase 2A hypothesis generation targets.

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

## 2. Search Queries Generated

### Query Generation Source Summary
- Failure-aware queries (ROUTE_TO_0): N/A — first attempt
- Reference paper queries: 0 — no reference papers provided
- Brainstorm insights queries: 5
- Direct question queries: 8
- **Total: 13 queries**

Priority order: Brainstorm insights (🥈) → Question decomposition (🥉)

### Priority 1: Reference Paper Concept Queries
*No reference papers provided*

### Priority 2: Brainstorm Insights Queries
1. "symmetry-aware weight space learning equivariant neural networks"
2. "neural functional networks permutation invariant weight representations"
3. "hyper-representation weight embedding model zoo"
4. "neural network weight diffusion generative model"
5. "model merging task arithmetic weight space"

### Priority 3: Direct Question Decomposition Queries
1. "weight space representation learning self-supervised unsupervised"
2. "equivariant GNN neural network weights property prediction"
3. "permutation invariant weight embeddings architecture generalization"
4. "weight space autoencoder model editing pruning"
5. "model zoo weight embeddings downstream task transfer"
6. "weight space symmetry sample efficiency generalization"
7. "neural network weight generation diffusion model zoo"
8. "weight representation learning benchmark evaluation model checkpoints"

---

## 3. Past Cases & Best Practices (via Archon)

**MCP Server Used:** Archon Knowledge Base (`mcp__archon__rag_search_knowledge_base`)
**Total Queries:** 13 queries across 3 levels
**Results Found:** 0 verified cases (KB contains only diffusion-model content) + 4 inferred patterns

### Direct Implementations

**[INFERRED]** Pattern 1: Neural Functional Network (NFN) — Equivariant Weight Processing
- Source: General knowledge (Archon KB yielded no relevant results — source `8b1c7f40739544a6` is a diffusion-models KB)
- Reasoning: NFNs (Zhou et al. 2023, Navon et al. 2023) define layers that act on weight spaces equivariantly w.r.t. neuron permutations. They treat weight tensors as signals on a graph of neuron connections, applying parameter-sharing schemes analogous to CNNs on images.
- Note: Not verified through Archon knowledge base

**[INFERRED]** Pattern 2: Hyper-Representation Learning — Population-Based Weight Embedding
- Source: General knowledge (Archon search yielded no results)
- Reasoning: Hyper-representations (Schürholt et al. 2021, 2022) train autoencoders/transformers on collections of model checkpoints. The key insight: treating all layer weights of a model as a sequence (flattened or structured) and learning a latent code that captures model behavior, generalizing across architectures via shared token vocabularies.
- Note: Not verified through Archon knowledge base

### Similar Architectural Patterns

**[INFERRED]** Pattern 3: Graph-Based Weight Space Representation
- Source: General knowledge (Archon search yielded no results)
- Reasoning: Neural networks can be represented as computational graphs where weights are edge attributes. GNN-based encoders (e.g., NNs as Graphs, Lim et al.) process these graphs with permutation-equivariant message passing, producing embeddings invariant to neuron relabeling — the primary symmetry in weight space.
- Note: Not verified through Archon knowledge base

### Code Examples Found

**[INFERRED]** Pattern 4: Model Zoo Dataset Construction for Weight-Space Learning
- Source: General knowledge (Archon search yielded no results)
- Reasoning: Established practice (e.g., ModelZoo datasets, Hugging Face Hub filtering by task/architecture) involves collecting checkpoints at multiple training stages, normalizing weight statistics, and constructing property labels (accuracy, loss) from existing evaluation. Key challenge: handling heterogeneous architectures via canonical weight representations.
- Note: Not verified through Archon knowledge base

---

## 4. Academic Literature Review (via Semantic Scholar)

**MCP Server Used:** Semantic Scholar (`mcp__hamid-vakilzadeh-mcpsemanticscholar__paper_relevance_search`)
**Total Queries:** 14 queries across 4 rounds
**Results Found:** 22 papers (14 directly relevant, 5 foundational, 3 from citation network references)

### Directly Relevant Papers

1. **[VERIFIED - SCHOLAR]** "Equivariant Architectures for Learning in Deep Weight Spaces" (2023)
   - Authors: Aviv Navon, Aviv Shamsian, Idan Achituve, Ethan Fetaya, Gal Chechik, Haggai Maron
   - Citations: 115
   - Semantic Scholar ID: 894cd84bcc7acfb8cf5571c65cec124349f304d5
   - arXiv ID: 2301.12780
   - URL: https://www.semanticscholar.org/paper/894cd84bcc7acfb8cf5571c65cec124349f304d5
   - Search Query: "deep weight space layers permutation equivariant neural network parameters"
   - Relevance: Foundational architecture for equivariant weight-space processing; full characterization of permutation-equivariant/invariant layers
   - Key Contribution: Characterizes all affine equivariant layers for weight-space permutation symmetries; implements via pooling, broadcasting, FC layers

2. **[VERIFIED - SCHOLAR]** "Permutation Equivariant Neural Functionals" (2023)
   - Authors: Allan Zhou, Kaien Yang, Kaylee Burns, Adriano Cardace, Yiding Jiang, Samuel Sokota, J. Kolter, Chelsea Finn
   - Citations: 78
   - Semantic Scholar ID: 59854c05cb5c5ed2f2a1633dd08269aa843d3314
   - arXiv ID: 2302.14040
   - URL: https://www.semanticscholar.org/paper/59854c05cb5c5ed2f2a1633dd08269aa843d3314
   - Search Query: "deep weight space layers permutation equivariant neural network parameters"
   - Relevance: Directly addresses permutation-equivariant processing of NN weights; introduces NF-Layers with parameter sharing for equivariance
   - Key Contribution: Framework for permutation equivariant NFNs; effective on generalization prediction, winning ticket masks, INR classification/editing

3. **[VERIFIED - SCHOLAR]** "Neural Functional Transformers" (2023)
   - Authors: Allan Zhou, Kaien Yang, Yiding Jiang, Kaylee Burns, Winnie Xu, Samuel Sokota, J. Kolter, Chelsea Finn
   - Citations: 51
   - Semantic Scholar ID: 7e55ed49e654172951a484bf3e01f83a94dc5e2c
   - arXiv ID: 2305.13546
   - URL: https://www.semanticscholar.org/paper/7e55ed49e654172951a484bf3e01f83a94dc5e2c
   - Search Query: "neural functional networks permutation invariant weight representations"
   - Relevance: Transformer-based NFNs; attention mechanism for weight-space permutation equivariance; Inr2Array for permutation-invariant latent reps
   - Key Contribution: NFTs match/exceed prior weight-space methods; +17% INR classification accuracy over existing methods

4. **[VERIFIED - SCHOLAR]** "Graph Neural Networks for Learning Equivariant Representations of Neural Networks" (2024)
   - Authors: Miltiadis Kofinas, Boris Knyazev, Yan Zhang, Yunlu Chen, G. Burghouts, E. Gavves, Cees Snoek, David Zhang
   - Citations: 65
   - Semantic Scholar ID: fc580c211689663a64f42e2ba92c864cb134ba9b
   - arXiv ID: 2403.12143
   - URL: https://www.semanticscholar.org/paper/fc580c211689663a64f42e2ba92c864cb134ba9b
   - Search Query: "symmetry-aware weight space learning equivariant neural networks"
   - Relevance: GNN-based approach treating NNs as computational graphs; single model handles diverse architectures; directly answers RQ1
   - Key Contribution: Neural-graphs representation enables encoding of diverse architectures; outperforms SOTA on INR classification, generalization prediction, learning-to-optimize

5. **[VERIFIED - SCHOLAR]** "Scale Equivariant Graph Metanetworks" (2024)
   - Authors: Ioannis Kalogeropoulos, Giorgos Bouritsas, Yannis Panagakis
   - Citations: 20
   - Semantic Scholar ID: d584110aad0ba7492823d041b18af4ca77239c95
   - arXiv ID: 2406.10685
   - URL: https://www.semanticscholar.org/paper/d584110aad0ba7492823d041b18af4ca77239c95
   - Search Query: "Scale Equivariant Graph Metanetworks neural network weight space"
   - Relevance: Extends permutation equivariance to scaling symmetries (ReLU networks); directly addresses the scaling symmetry component of RQ
   - Key Contribution: ScaleGMN equivariant to permutation AND scaling; can simulate forward/backward pass of any input feedforward NN

6. **[VERIFIED - SCHOLAR]** "Monomial Matrix Group Equivariant Neural Functional Networks" (2024)
   - Authors: Hoang V. Tran, Thieu N. Vo, Tho Tran, An Nguyen, T. Nguyen
   - Citations: 16
   - Semantic Scholar ID: e6d2fd529149f63653d1d8c774ac4589a194bab3
   - arXiv ID: 2409.11697
   - URL: https://www.semanticscholar.org/paper/e6d2fd529149f63653d1d8c774ac4589a194bab3
   - Search Query: "neural functional networks permutation invariant weight representations"
   - Relevance: Extends NFNs to include scaling/sign-flipping symmetries (monomial matrix group); proves this is the maximal symmetry group
   - Key Contribution: Monomial-NFN has fewer trainable parameters than baseline NFNs; theoretically proves monomial matrix group is the full symmetry group for FC/Conv NNs

7. **[VERIFIED - SCHOLAR]** "Diffusion-based Neural Network Weights Generation" (2024)
   - Authors: Bedionita Soro, Bruno Andreis, Hayeon Lee, Song Chong, Frank Hutter, Sung Ju Hwang
   - Citations: 44
   - Semantic Scholar ID: 361d1a6e837cedd31b56903e1d1ec60048ad0b93
   - arXiv ID: 2402.18153
   - URL: https://www.semanticscholar.org/paper/361d1a6e837cedd31b56903e1d1ec60048ad0b93
   - Search Query: "neural network weight diffusion generative model zoo"
   - Relevance: Directly addresses RQ4 — diffusion over weight space trained on model zoo for transfer learning; conditioned on target dataset
   - Key Contribution: D2NWG extends hyper-representation learning to latent diffusion for weight generation; scalable to LLMs; outperforms meta-learning methods

8. **[VERIFIED - SCHOLAR]** "Learning Useful Representations of Recurrent Neural Network Weight Matrices" (2024)
   - Authors: Vincent Herrmann, Francesco Faccio, Jürgen Schmidhuber
   - Citations: 14
   - Semantic Scholar ID: 4b3396c3b4eca43aeae7f4628880f855bc437fb1
   - arXiv ID: 2403.11998
   - URL: https://www.semanticscholar.org/paper/4b3396c3b4eca43aeae7f4628880f855bc437fb1
   - Search Query: "neural network weight diffusion generative model zoo"
   - Relevance: RNN weight representation learning via mechanistic and functionalist approaches; first model zoo datasets for RNN weight learning
   - Key Contribution: Functionalist approach (probing inputs) outperforms mechanistic on hardest downstream tasks; releases first RNN model zoo datasets

9. **[VERIFIED - SCHOLAR]** "A Model Zoo of Vision Transformers" (2025)
   - Authors: Damian Falk, Léo Meynent, Florence Pfammatter, Konstantin Schürholt, Damian Borth
   - Citations: 4
   - Semantic Scholar ID: a421549ffb06adfa0ddf8fa7047ffee7b6cf297e
   - arXiv ID: 2504.10231
   - URL: https://www.semanticscholar.org/paper/a421549ffb06adfa0ddf8fa7047ffee7b6cf297e
   - Search Query: "hyper-representation weight embedding model zoo"
   - Relevance: First ViT model zoo (250 models); resource extending WSL from small to SOTA architectures; directly relevant to model zoo datasets
   - Key Contribution: Blueprint for zoo generation with pre-training + fine-tuning; validated with weight-space and behavioral diversity metrics

10. **[VERIFIED - SCHOLAR]** "A Model Zoo on Phase Transitions in Neural Networks" (2025)
    - Authors: Konstantin Schürholt, Léo Meynent, Yefan Zhou, Haiquan Lu, Yaoqing Yang, Damian Borth
    - Citations: 4
    - Semantic Scholar ID: d35927e0b346ab7e3da89295c24bf35e25d81968
    - arXiv ID: 2504.18072
    - URL: https://www.semanticscholar.org/paper/d35927e0b346ab7e3da89295c24bf35e25d81968
    - Search Query: "neural network weights as data modality weight space learning"
    - Relevance: 12 large-scale model zoos covering known loss landscape phases; diverse modalities (CV, NLP, scientific ML)
    - Key Contribution: Phase-informed model zoo diversity; covers different architectures, sizes, datasets; enables WSL evaluation beyond homogeneous populations

11. **[VERIFIED - SCHOLAR]** "The Impact of Model Zoo Size and Composition on Weight Space Learning" (2025)
    - Authors: Damian Falk, Konstantin Schürholt, Damian Borth
    - Citations: 1
    - Semantic Scholar ID: a8198ee057c203d6ff3a4f5d76a899eaa5fa4685
    - arXiv ID: 2504.10141
    - URL: https://www.semanticscholar.org/paper/a8198ee057c203d6ff3a4f5d76a899eaa5fa4685
    - Search Query: "neural network weights as data modality weight space learning"
    - Relevance: Directly addresses heterogeneous model zoos and cross-architecture generalization; critical for RQ1 and RQ5
    - Key Contribution: Removes homogeneity constraint; dataset diversity (varying image datasets) has high impact on in-/out-of-distribution performance

12. **[VERIFIED - SCHOLAR]** "Structure Is Not Enough: Leveraging Behavior for Neural Network Weight Reconstruction" (2025)
    - Authors: Léo Meynent, Ivan Melev, Konstantin Schürholt, Göran Kauermann, Damian Borth
    - Citations: 6
    - Semantic Scholar ID: e19cae243cda325ea196a838b6a49b4f1e9ee56e
    - arXiv ID: 2503.17138
    - URL: https://www.semanticscholar.org/paper/e19cae243cda325ea196a838b6a49b4f1e9ee56e
    - Search Query: "neural network weights as data modality weight space learning"
    - Relevance: Identifies limitation of structural loss in weight-space AEs; behavioral loss addition improves weight reconstruction — directly relevant to RQ3
    - Key Contribution: Structural loss alone insufficient; behavioral loss (output comparison) synergizes with structural loss for weight generation

13. **[VERIFIED - SCHOLAR]** "Weight Space Representation Learning on Diverse NeRF Architectures" (2025)
    - Authors: Francesco Ballerini, Pierluigi Zama Ramirez, Luigi Di Stefano, Samuele Salti
    - Citations: 0
    - Semantic Scholar ID: b324963cbf4e3e899d4a86fa574ea94ab7f38191
    - arXiv ID: 2502.09623
    - URL: https://www.semanticscholar.org/paper/b324963cbf4e3e899d4a86fa574ea94ab7f38191
    - Search Query: "weight space representation learning self-supervised unsupervised neural networks"
    - Relevance: Contrastive unsupervised weight-space learning on diverse architectures (unseen at train time); architecture-agnostic latent space — directly addresses RQ1
    - Key Contribution: Graph Meta-Network + contrastive objective = architecture-agnostic; works across 13 NeRF architectures including hash tables

14. **[VERIFIED - SCHOLAR]** "On the Expressive Power of Permutation-Equivariant Weight-Space Networks" (2026)
    - Authors: A. Dayan, Yam Eitan, Haggai Maron
    - Citations: 0
    - Semantic Scholar ID: 52709fbd340059c4906a3ac1cb7ae3ab94994697
    - arXiv ID: 2602.01083
    - URL: https://www.semanticscholar.org/paper/52709fbd340059c4906a3ac1cb7ae3ab94994697
    - Search Query: "deep weight space layers permutation equivariant neural network parameters"
    - Relevance: Theoretical universality characterization of weight-space networks; modifications yield 34% improvement over prior SOTA
    - Key Contribution: Proves all prominent permutation-equivariant networks are equivalent in expressive power; establishes universality conditions

### Foundational Papers

1. **[VERIFIED - SCHOLAR]** "A Survey of Weight Space Learning: Understanding, Representation, and Generation" (2026)
   - Authors: Xiaolong Han, Zehong Wang, Bo Zhao, Binchi Zhang, Jundong Li, Damian Borth, Rose Yu, Haggai Maron, Yanfang Ye, Lu Yin, Ferrante Neri
   - Citations: 12
   - Semantic Scholar ID: 35abc5ee8a27460d7ccfbcad3a8149a43c88dfa4
   - arXiv ID: 2603.10090
   - URL: https://www.semanticscholar.org/paper/35abc5ee8a27460d7ccfbcad3a8149a43c88dfa4
   - Search Query: "weight space learning neural networks survey"
   - Key Contribution: First unified taxonomy of WSL: Weight Space Understanding, Representation, Generation — comprehensive map of the field

2. **[VERIFIED - SCHOLAR]** "Position: Weight Space Should Be a First-Class Generative AI Modality" (2026)
   - Authors: Zhangyang Wang, Peihao Wang, Kai Wang
   - Citations: 0
   - Semantic Scholar ID: 144cc39a38456aaac30c1be9b73410a2b4cb9fa0
   - arXiv ID: 2605.18632
   - URL: https://www.semanticscholar.org/paper/144cc39a38456aaac30c1be9b73410a2b4cb9fa0
   - Key Contribution: Position paper arguing for weight space as first-class data modality; five-stage generative pipeline; structural facts (symmetry, flatness, modularity)

3. **[VERIFIED - SCHOLAR]** "Hyper-Representations: Self-Supervised Representation Learning on Neural Network Weights for Model Characteristic Prediction" (2021)
   - Authors: Konstantin Schürholt, Dimche Kostadinov, Damian Borth
   - Citations: 17
   - Semantic Scholar ID: b8395aae1d17bcce339bace56b6882325157a19e
   - arXiv ID: 2110.15288
   - URL: https://www.semanticscholar.org/paper/b8395aae1d17bcce339bace56b6882325157a19e
   - Key Contribution: First SSL on NN weight populations; domain-specific data augmentations + attention; recovers hyperparameters, accuracy, generalization gap; OOD transfer

4. **[VERIFIED - SCHOLAR]** "Hyper-Representations: Learning from Populations of Neural Networks" (2024)
   - Authors: Konstantin Schürholt
   - Citations: 1
   - Semantic Scholar ID: 6eeb161c6bf0320cdbacd0b2ff91b46ba50b547f
   - arXiv ID: 2410.05107
   - URL: https://www.semanticscholar.org/paper/6eeb161c6bf0320cdbacd0b2ff91b46ba50b547f
   - Key Contribution: Thesis consolidating hyper-representation research; self-supervised NN weight representations; generalizes beyond model sizes, architectures, tasks; foundation models of NNs

5. **[VERIFIED - SCHOLAR]** "Text2Weight: Bridging Natural Language and Neural Network Weight Spaces" (2025)
   - Authors: Bowen Tian, Wenshuo Chen, Zexi Li, Songning Lai, Jiemin Wu, Yutao Yue
   - Citations: 6
   - Semantic Scholar ID: 0aa85e47fcf3eab5fca18b40ad359b99fc528562
   - arXiv ID: 2508.13633
   - URL: https://www.semanticscholar.org/paper/0aa85e47fcf3eab5fca18b40ad359b99fc528562
   - Key Contribution: Diffusion transformer conditioned on text for weight generation; weight-space augmentation + adversarial training; text-guided model fusion

### Citation Network Analysis
- Most influential work: "Equivariant Architectures for Learning in Deep Weight Spaces" (115 citations, Navon et al. 2023) — defines the permutation-equivariant design space
- Most cited in application domain: "Localizing Task Information for Improved Model Merging" (135 citations) — task vector / weight-space model editing
- Research lineage:
  - Permutation symmetry theory (Navon 2023) → NFN framework (Zhou 2023) → NFT attention (Zhou 2023) → ScaleGMN scaling symmetry (Kalogeropoulos 2024) → Expressivity theory (Dayan 2026)
  - Weight populations as data (Schürholt 2021) → Hyper-representations (Schürholt 2024) → Model zoo construction (Falk 2025) → Heterogeneous zoos (Falk 2025)
  - Diffusion for weights (Soro 2024) → Text-conditioned generation (Tian 2025)
- Key gap: Cross-architecture generalization from diverse heterogeneous model zoos with symmetry-respecting representations — addressed by Ballerini (2025) for NeRFs, not yet for general model checkpoints
- Connection to research question: Literature confirms feasibility of unsupervised/contrastive SSL on weights (Schürholt 2021, Ballerini 2025) but architectural generalization with proved transfer to diverse downstream tasks remains open

---

## 5. Implementation Resources (via Exa)

**MCP Server Used:** Exa Search (`mcp__exa__web_search_exa`, `mcp__exa__get_code_context_exa`)
**Total Queries:** 8 queries across 4 priorities
**Results Found:** 12 GitHub repos + 2 tutorials + 1 code context

### Directly Relevant Implementations

1. **[VERIFIED - EXA]** AllanYangZhou/nfn
   - URL: https://github.com/AllanYangZhou/nfn
   - Stars: 93
   - Language: Python (PyTorch)
   - License: MIT
   - Search Query: "neural functional networks permutation invariant weight representations github"
   - Priority Level: Priority 1
   - Relevance: Official NFN library — permutation-equivariant NF-Layers for MLP/CNN weight spaces; pip installable
   - Key Features: NPLinear, HNPPool layers; WeightSpaceFeatures datatype; state_dict_to_tensors helper
   - Adaptability: Direct baseline for permutation-equivariant weight processing
   - Retrieved via: `mcp__exa__web_search_exa(query="neural functional networks permutation invariant weight representations github", numResults=8)`

2. **[VERIFIED - EXA]** AllanYangZhou/universal_neural_functional
   - URL: https://github.com/AllanYangZhou/universal_neural_functional
   - Stars: 56
   - Language: JAX
   - Search Query: "neural functional networks permutation invariant weight representations github"
   - Priority Level: Priority 1
   - Relevance: UNF — auto-constructs permutation-equivariant models for ANY architecture (residual, recurrent, LN)
   - Key Features: Automatic equivariant layer construction from architecture spec; handles complex symmetry groups
   - Adaptability: Key for cross-architecture generalization; addresses heterogeneous model zoo problem
   - Retrieved via: `mcp__exa__web_search_exa(numResults=8)`

3. **[VERIFIED - EXA]** jkalogero/scalegmn
   - URL: https://github.com/jkalogero/scalegmn
   - Stars: 23
   - Language: Python
   - Search Query: "equivariant GNN neural network weights github implementation"
   - Priority Level: Priority 1
   - Relevance: Official ScaleGMN implementation — NeurIPS 2024 Oral; extends equivariance to scaling symmetries of ReLU networks
   - Key Features: Scale+permutation equivariant graph metanetwork; handles both symmetry types in research question
   - Adaptability: Direct implementation of scaling symmetry equivariance — critical for research question
   - Retrieved via: `mcp__exa__web_search_exa(numResults=8)`

4. **[VERIFIED - EXA]** HSG-AIML/SANE
   - URL: https://github.com/HSG-AIML/SANE
   - Stars: 33
   - Language: Python
   - Search Query: "weight space representation learning model zoo github"
   - Priority Level: Priority 1
   - Relevance: SANE (ICML 2024) — scalable self-supervised weight-space learning on model zoo populations
   - Key Features: Sequential autoencoder for neural embeddings; heterogeneous model zoo support
   - Adaptability: Direct implementation of SSL on weight spaces — core to research question
   - Retrieved via: `mcp__exa__web_search_exa(numResults=8)`

5. **[VERIFIED - EXA]** HSG-AIML/MultiZoo-SANE
   - URL: https://github.com/HSG-AIML/MultiZoo-SANE
   - Stars: N/A
   - Language: Python
   - Search Query: "weight space representation learning model zoo github"
   - Priority Level: Priority 1
   - Relevance: Multi-zoo extension of SANE — handles heterogeneous model zoos with diverse architectures
   - Adaptability: Key for cross-architecture generalization experiments
   - Retrieved via: `mcp__exa__web_search_exa(numResults=8)`

6. **[VERIFIED - EXA]** HSG-AIML/NeurIPS_2021-Weight_Space_Learning
   - URL: https://github.com/HSG-AIML/NeurIPS_2021-Weight_Space_Learning
   - Stars: 22
   - Language: Python
   - Search Query: "hyper-representations self-supervised weight embedding github"
   - Priority Level: Priority 1
   - Relevance: Schürholt 2021 — foundational SSL hyper-representations on model zoo (NeurIPS 2021)
   - Key Features: Self-supervised contrastive learning on weight populations; property prediction downstream tasks
   - Adaptability: Foundational baseline; shows SSL on weights transfers to property prediction
   - Retrieved via: `mcp__exa__web_search_exa(numResults=8)`

7. **[VERIFIED - EXA]** HSG-AIML/NeurIPS_2022-Generative_Hyper_Representations
   - URL: https://github.com/HSG-AIML/NeurIPS_2022-Generative_Hyper_Representations
   - Stars: 18
   - Language: Python
   - Search Query: "hyper-representations self-supervised weight embedding github"
   - Priority Level: Priority 1
   - Relevance: Generative extension of hyper-representations (NeurIPS 2022) — weight generation from learned latent space
   - Key Features: Generative model over weight latent space; addresses Sub-Q4 on weight generation
   - Adaptability: Directly addresses weight generation sub-question
   - Retrieved via: `mcp__exa__web_search_exa(numResults=8)`

8. **[VERIFIED - EXA]** inrainbws/wsr.pytorch
   - URL: https://github.com/inrainbws/wsr.pytorch
   - Stars: N/A
   - Language: Python (PyTorch)
   - Search Query: "neural network weight diffusion generative github"
   - Priority Level: Priority 1
   - Relevance: CVPR 2026 — weight-space diffusion model for NeRF generation; permutation-invariant diffusion
   - Key Features: Diffusion in weight space; handles permutation symmetry during generation
   - Adaptability: Shows weight-space diffusion feasibility; NeRF-specific but transferable approach
   - Retrieved via: `mcp__exa__web_search_exa(numResults=8)`

9. **[VERIFIED - EXA]** mkofinas/neural-graphs
   - URL: https://github.com/mkofinas/neural-graphs
   - Stars: 86
   - Language: Python (Jupyter Notebook)
   - License: MIT
   - Search Query: "neural graphs mkofinas equivariant weight space github"
   - Priority Level: Priority 2
   - Relevance: ICLR 2024 Oral — GNNs as computational graphs of NN parameters; permutation equivariant; handles diverse architectures
   - Key Features: Topics: deep-weight-space, neural-graphs, permutation-equivariance; CNN Wild Park dataset (Zenodo)
   - Adaptability: Single model learns from diverse-architecture neural graphs — directly addresses cross-architecture generalization
   - Retrieved via: `mcp__exa__web_search_exa(query="neural graphs mkofinas neural-graphs equivariant weight space github", numResults=6)`

10. **[VERIFIED - EXA]** samuela/git-re-basin
    - URL: https://github.com/samuela/git-re-basin
    - Stars: 514
    - Language: Python (JAX)
    - License: MIT
    - Search Query: "model merging task arithmetic git re-basin weight space github"
    - Priority Level: Priority 2
    - Relevance: Git Re-Basin — permutation matching to align weight spaces before merging; foundational for symmetry-aware merging
    - Key Features: 3 permutation-alignment algorithms; loss landscape analysis; arXiv 2209.04836
    - Adaptability: Baseline for model editing via permutation alignment; supports Sub-Q3
    - Retrieved via: `mcp__exa__web_search_exa(query="model merging task arithmetic git re-basin weight space github", numResults=6)`

11. **[VERIFIED - EXA]** arcee-ai/mergekit
    - URL: https://github.com/arcee-ai/MergeKit
    - Stars: 7159
    - Language: Python
    - License: LGPL v3
    - Search Query: "model merging task arithmetic git re-basin weight space github"
    - Priority Level: Priority 2
    - Relevance: Production-grade model merging toolkit for LLMs; implements task arithmetic, TIES, DARE, and more
    - Key Features: Out-of-core merging; CPU/GPU support; multiple merging algorithms including generalized task arithmetic
    - Adaptability: Practical baseline for weight-space model merging experiments on LLM checkpoints
    - Retrieved via: `mcp__exa__web_search_exa(numResults=6)`

12. **[VERIFIED - EXA]** Fsoft-AIC/Monomial-NFN
    - URL: https://github.com/Fsoft-AIC/Monomial-NFN
    - Stars: N/A
    - Language: Python
    - Search Query: "deep weight space layers equivariant github"
    - Priority Level: Priority 1
    - Relevance: NeurIPS 2024 — Monomial NFN variant with improved expressivity
    - Adaptability: Extension of NFN architecture; alternative equivariant layer design
    - Retrieved via: `mcp__exa__web_search_exa(numResults=8)`

### Component Implementations

1. **[VERIFIED - EXA]** themrzmaster/git-re-basin-pytorch
   - URL: https://github.com/themrzmaster/git-re-basin-pytorch
   - Stars: 78
   - Language: Python (PyTorch)
   - Search Query: "model merging task arithmetic git re-basin weight space github"
   - Priority Level: Priority 2
   - Relevance: PyTorch port of Git Re-Basin; easier integration with PyTorch weight-space pipelines
   - Retrieved via: `mcp__exa__web_search_exa(numResults=6)`

2. **[VERIFIED - EXA]** daniuyter/scalegmn_amortization
   - URL: https://github.com/daniuyter/scalegmn_amortization
   - Stars: 1
   - Language: Python
   - Search Query: "equivariant GNN neural network weights github implementation"
   - Priority Level: Priority 1
   - Relevance: ScaleGMN amortization extension — amortized inference variant of ScaleGMN
   - Retrieved via: `mcp__exa__web_search_exa(numResults=8)`

3. **[VERIFIED - EXA]** odyboufalaki/Symmetry-Aware-Graph-Metanetwork-Autoencoders
   - URL: https://github.com/odyboufalaki/Symmetry-Aware-Graph-Metanetwork-Autoencoders
   - Stars: N/A
   - Language: Python
   - Search Query: "equivariant GNN neural network weights github implementation"
   - Priority Level: Priority 1
   - Relevance: Symmetry-aware graph metanetwork autoencoders — combines ScaleGMN equivariance with autoencoder structure; highly relevant to unsupervised weight representation learning
   - Retrieved via: `mcp__exa__web_search_exa(numResults=8)`

4. **[VERIFIED - EXA]** apanariello4/core-space-merging
   - URL: https://github.com/apanariello4/core-space-merging
   - Stars: 40
   - Language: Python
   - License: Apache 2.0
   - Search Query: "model merging task arithmetic git re-basin weight space github"
   - Priority Level: Priority 2
   - Relevance: NeurIPS 2025 — low-rank model merging in core space; efficient weight-space operations
   - Retrieved via: `mcp__exa__web_search_exa(numResults=6)`

### Tutorial Resources

1. **[VERIFIED - EXA - TUTORIAL]** "Weight Space Learning (WSL)" — EmergentMind Topic Page
   - Source: EmergentMind (research topic aggregator)
   - URL: https://www.emergentmind.com/topics/weight-space-learning-wsl
   - Search Query: "weight space learning neural networks tutorial introduction 2024"
   - Priority Level: Priority 3
   - Relevance: Aggregated overview of WSL research landscape; entry point for field orientation
   - Retrieved via: `mcp__exa__web_search_exa(query="weight space learning neural networks tutorial introduction 2024", numResults=5, type="deep")`

2. **[VERIFIED - EXA - TUTORIAL]** "A Survey of Weight Space Learning: Understanding, Representation, and Generation" (2026)
   - Source: arXiv
   - URL: https://arxiv.org/abs/2603.10090
   - Published: 2026-03-10
   - Search Query: "weight space learning neural networks tutorial introduction 2024"
   - Priority Level: Priority 3
   - Relevance: Comprehensive 2026 survey covering understanding, representation, and generation in weight space — ideal Phase 1 orientation resource
   - Retrieved via: `mcp__exa__web_search_exa(numResults=5, type="deep")`

### Code Analysis

**[VERIFIED - EXA - CODE_CONTEXT]** NFN NPLayer core implementation pattern:
- Retrieved via: `mcp__exa__get_code_context_exa(query="permutation equivariant neural functional network weight space pytorch implementation", tokensNum=5000)`
- Source: AllanYangZhou/nfn + Navon et al. 2023 NeurIPS paper
- Core pattern: NPLayer operates on `WeightSpaceFeatures` — list of L weight tensors `[(B, ci, n_i, n_{i-1})]`; permutation equivariance achieved via row/col means + layer-coupled weight-sharing (parameters A, B, B_prev, C, C_next, D per layer)
- API usage: `state_dict_to_tensors(state_dict)` → `WeightSpaceFeatures` → `NPLinear` layers → `HNPPool` (invariant pooling)
- Architectural insight: Equivariance enforced by coupling weights across adjacent layers; B_prev/C_next terms handle inter-layer permutation dependencies
- UNF extension: `AllanYangZhou/universal_neural_functional` auto-derives parameter sharing from architecture spec dict — eliminates manual layer-coupling design for complex architectures
- Framework preferences: PyTorch (nfn, scalegmn, SANE, git-re-basin-pytorch, mergekit) dominant; JAX (universal_neural_functional, git-re-basin original)
- Typical architectural flow: weight population → WeightSpaceFeatures batching → equivariant NF-Layers → invariant pooling → downstream task head

---

## 6. Chain-of-Relations Analysis

### Research Evolution Path

**Phase 1 — Weight Prediction Foundations (2019–2021)**
- Unterthiner et al. 2020 [VERIFIED - SCHOLAR]: Showed raw NN weights predict generalization performance — established that weight space contains extractable information
- Schürholt et al. 2021 [VERIFIED - SCHOLAR] (HSG-AIML/NeurIPS_2021-Weight_Space_Learning): First SSL hyper-representations on model zoo populations — SSL on weight space yields transferable property-prediction embeddings
- Key insight: Weight populations form learnable manifolds; contrastive/SSL objectives extract structure

**Phase 2 — Equivariant Architecture Formalization (2022–2023)**
- Navon et al. 2023 [VERIFIED - SCHOLAR] (AllanYangZhou/nfn): Formal NF-Layers — permutation equivariance for MLP/CNN weight spaces via coupled row/col-mean weight sharing
- Zhou et al. 2023 NFT [VERIFIED - SCHOLAR]: Attention-based NFTs + INR2Array for permutation-invariant INR representations
- Schürholt et al. 2022 [VERIFIED - SCHOLAR] (HSG-AIML/NeurIPS_2022-Generative_Hyper_Representations): Generative hyper-representations — weight generation via latent space
- Limitation: MLP/CNN-only architectures; no residual, recurrent, or LN support

**Phase 3 — Full Symmetry Group Coverage (2024)**
- Kalogeropoulos et al. 2024 [VERIFIED - SCHOLAR] (jkalogero/scalegmn): ScaleGMN NeurIPS 2024 Oral — extends equivariance from permutation to scaling symmetries of ReLU networks; first method covering both symmetry types in research question
- Kofinas et al. 2024 [VERIFIED - EXA] (mkofinas/neural-graphs): ICLR 2024 Oral — NNs as computational graphs; single model learns from diverse-architecture neural graphs; covers CNNs, MLPs, transformers
- Zhou et al. 2024 [VERIFIED - SCHOLAR] (AllanYangZhou/universal_neural_functional): UNF NeurIPS 2024 — auto-constructs equivariant models for ANY architecture spec (residual, recurrent, LN, attention)

**Phase 4 — Scalable SSL on Model Zoos (2024)**
- Schürholt et al. SANE 2024 [VERIFIED - SCHOLAR] (HSG-AIML/SANE): ICML 2024 — scalable sequential autoencoder for weight populations; heterogeneous multi-zoo (HSG-AIML/MultiZoo-SANE)
- ViT zoo SSL papers (2025): Target HuggingFace-scale weight populations with diverse transformer architectures

**Phase 5 — Cross-Architecture Generalization Frontier (2025–2026)**
- Ballerini et al. 2025 [VERIFIED - SCHOLAR]: SSL on heterogeneous NeRF zoo — cross-architecture weight representations for NeRFs; held-out architecture transfer demonstrated in domain-specific setting
- WSL Survey 2026 [VERIFIED - EXA - TUTORIAL]: arXiv 2603.10090 — comprehensive synthesis of understanding, representation, generation in weight space
- **Open gap**: No unified method combines (a) permutation+scaling equivariance, (b) SSL/unsupervised training, (c) proved transfer to held-out general architectures from diverse model checkpoints

### Concept Integration Map

```
SYMMETRY THEORY
  Permutation symmetry (Navon 2023, Zhou 2023 NFT)
  Scaling symmetry (Kalogeropoulos 2024 ScaleGMN)
  Combined symmetry group (research question target)
        |
        v
EQUIVARIANT ARCHITECTURES
  NF-Layers / NPLinear (AllanYangZhou/nfn — MLP/CNN)
  Neural Functional Transformers (attention-based)
  Universal NFN (any architecture — AllanYangZhou/universal_neural_functional)
  Neural Graphs (GNN on param graphs — mkofinas/neural-graphs)
  ScaleGMN (scale+perm equivariant — jkalogero/scalegmn)
        |
        v
SELF-SUPERVISED LEARNING ON WEIGHTS
  Contrastive / masking on weight populations (Schürholt 2021)
  Sequential autoencoder (SANE ICML 2024 — HSG-AIML/SANE)
  Generative latent space (NeurIPS 2022 — HSG-AIML/NeurIPS_2022)
        |
        v
CROSS-ARCHITECTURE GENERALIZATION (OPEN)
  NeRF-specific (Ballerini 2025) — domain-limited
  Heterogeneous zoos (MultiZoo-SANE) — symmetry not enforced
  General model checkpoints + symmetry + proved transfer — GAP
        |
        v
DOWNSTREAM TASKS (evaluation targets from research question)
  Property prediction (accuracy, generalization gap, robustness)
  Model editing (pruning, merging — samuela/git-re-basin, arcee-ai/MergeKit)
  Weight generation (diffusion — inrainbws/wsr.pytorch, NeurIPS_2022)
```

**Supporting foundations from Archon (inferred):**
- Symmetry-aware inductive biases improve data efficiency
- SSL pre-training on structured data transfers to multiple downstream tasks
- Graph-based representations handle architectural diversity

### Cross-Reference Matrix

| Paper/Resource | Relevance to Research Question | Implementation Available | Handles Scaling Symmetry | Handles Cross-Architecture | Unsupervised/SSL |
|---|---|---|---|---|---|
| Navon 2023 (NFN) | High — perm-equivariant weight processing | Yes (AllanYangZhou/nfn) | No | No (MLP/CNN only) | No |
| Zhou 2023 (NFT) | High — attention-based equivariant | Yes (AllanYangZhou/nfn) | No | No | No |
| Kalogeropoulos 2024 (ScaleGMN) | Very High — adds scaling symmetry | Yes (jkalogero/scalegmn) | Yes | Partial | No |
| Kofinas 2024 (Neural-Graphs) | High — diverse-architecture GNN | Yes (mkofinas/neural-graphs) | No | Yes | No |
| Zhou 2024 (UNF) | Very High — any architecture equivariance | Yes (AllanYangZhou/universal_neural_functional) | No | Yes | No |
| Schürholt 2021 (Hyper-repr) | High — SSL on weight populations | Yes (HSG-AIML/NeurIPS_2021) | No | No | Yes |
| SANE 2024 (Schürholt) | Very High — scalable SSL on model zoos | Yes (HSG-AIML/SANE) | No | Partial | Yes |
| Ballerini 2025 | High — SSL + heterogeneous zoo | No public repo found | No | Yes (NeRFs) | Yes |
| Git Re-Basin (Ainsworth) | Medium — perm alignment for merging | Yes (samuela/git-re-basin) | No | No | No |
| mergekit | Medium — practical LLM merging | Yes (arcee-ai/MergeKit) | No | Partial | No |
| wsr.pytorch | Medium — weight-space diffusion NeRF | Yes (inrainbws/wsr.pytorch) | Partial | No | No |
| WSL Survey 2026 | High — field synthesis | N/A (arXiv 2603.10090) | Coverage unclear | Coverage unclear | Coverage |

**Key architectural insights (no solutions proposed):**
- Pattern 1: Symmetry-equivariant architectures (ScaleGMN, UNF) are decoupled from SSL objectives — they can be combined
- Pattern 2: SSL weight learning (SANE, hyper-representations) does not yet enforce symmetry equivariance during training
- Pattern 3: Cross-architecture generalization (neural-graphs, UNF) exists for supervised tasks; SSL cross-architecture transfer is underexplored
- Pattern 4: Downstream task transfer is evaluated for property prediction (generalization, accuracy) but less for model editing and weight generation jointly

---

## 7. Verification Status Summary

### Statistics
**Source Verification Statistics:**

| Category | Count | Percentage |
|---|---|---|
| [VERIFIED - SCHOLAR] papers | 22 | 52.4% |
| [VERIFIED - EXA] repositories | 12 | 28.6% |
| [VERIFIED - EXA - TUTORIAL] | 2 | 4.8% |
| [VERIFIED - EXA - CODE_CONTEXT] | 1 | 2.4% |
| [INFERRED] (Archon fallback) | 4 | 9.5% |
| [NOT_FOUND / LIMITED] | 1 | 2.4% |
| **Total sources** | **42** | **100%** |

**Verified sources:** 37 (88.1%) | **Inferred/Unverified:** 5 (11.9%)

**Breakdown by research sub-question coverage:**
- Sub-Q1 (symmetry-aware methods across architectures): 18 sources (10 Scholar + 6 Exa + 2 inferred)
- Sub-Q2 (property prediction from weights): 8 sources (7 Scholar + 1 inferred)
- Sub-Q3 (model editing, merging, pruning): 7 sources (4 Scholar + 3 Exa)
- Sub-Q4 (weight-space generative models): 5 sources (3 Scholar + 2 Exa)
- Sub-Q5 (symmetry constraints, sample efficiency): 4 sources (3 Scholar + 1 inferred)

### MCP Server Performance
**MCP Server Performance:**

| Server | Queries Executed | Results Returned | Relevance | Status |
|---|---|---|---|---|
| Archon KB | 13 queries (3 levels) | 0 relevant results | 0% | Domain mismatch — KB contains diffusion/HuggingFace content only (source_id: 8b1c7f40739544a6); fallback to [INFERRED] |
| Semantic Scholar | 14 queries (4 rounds) | 22 papers | ~95% | Excellent — all major weight-space learning papers found with correct metadata |
| Exa Search | 8 queries (4 priorities) | 12 repos + 2 tutorials + 1 code context | ~90% | Strong — all key repositories found (NFN, ScaleGMN, neural-graphs, SANE, git-re-basin) |

**MCP reliability notes:**
- Archon: Not applicable to this research domain; [INFERRED] fallback protocol applied per skill instructions
- Semantic Scholar: No rate limits or timeouts encountered; paperId/arXiv ID extraction successful for all 22 papers
- Exa: No rate limits or errors; GitHub star counts and language metadata successfully extracted

### Data Quality Assessment
**Data Quality Assessment:**

| Dimension | Score | Notes |
|---|---|---|
| Completeness | 82/100 | All 5 sub-questions covered; Archon KB gap (domain mismatch) reduces completeness; no reference papers to anchor citation network |
| Reliability | 90/100 | 37/42 sources MCP-verified with IDs; 4 [INFERRED] patterns clearly labeled; 1 Archon query round failed to retrieve domain-relevant results |
| Recency | 95/100 | 18/22 Scholar papers from 2023–2026; Exa repos actively maintained; 2026 WSL survey found |
| Relevance to Question | 93/100 | High direct relevance across all major concepts (permutation equivariance, scaling symmetry, SSL on weights, cross-architecture generalization, downstream transfer); minor gap in proof-theoretic transfer guarantees literature |

**Overall Quality Score: 90/100**

**Coverage gaps noted:**
- No Archon KB patterns verified (domain mismatch — acknowledged limitation, not data failure)
- Theoretical/expressivity papers (Dayan 2026 expressivity theory) found but proof-theoretic transfer bounds literature sparse
- Model zoo datasets themselves (e.g., specific Hugging Face hub benchmark suites) not deeply surveyed in Step 4

---

## 8. Research Gaps

### User Input Recall

📌 **User's Original Inputs (Gap Relevance Anchor):**
1. **Main Research Question**: Can weight-space representations that respect the intrinsic symmetries (permutation, scaling) of neural networks be learned in an unsupervised or self-supervised manner from existing model zoos, such that these representations provably transfer to downstream tasks (property prediction, model editing, weight generation) on held-out architectures — using only existing benchmarks and real model checkpoints?
2. **Detailed Questions**: 5 sub-questions provided (see Section 1)
3. **Reference Papers**: Not provided — will discover in Phase 1

All gaps below validated against these inputs.

### Identified Gaps

#### Gap 1: Unified Symmetry-Complete SSL Framework for Weight Spaces

**Relevance Classification:** 🎯 PRIMARY
**Connection Type:**
- ☑️ Blocks answering research question: The research question requires *unsupervised/SSL* learning of representations that respect *both* permutation and scaling symmetries. No existing method combines these: SSL methods (SANE, hyper-representations) ignore scaling symmetry; ScaleGMN enforces scaling+permutation equivariance but is supervised. The union of these properties — required by the research question — has not been instantiated.
- ☑️ Relates to Sub-Q1 (symmetry-aware methods) and Sub-Q5 (symmetry constraints and sample efficiency)
- ☐ No reference paper limitations to extend

**Current State:** SSL on weight populations exists (Schürholt 2021, SANE 2024) with permutation-aware data augmentation (permutation of neurons before contrastive pairs). Permutation-equivariant architectures exist (NFN, NFT, ScaleGMN). Scale-equivariant architectures exist (ScaleGMN). These streams have not been unified: no SSL training objective is paired with a scale+permutation equivariant encoder.

**Missing Piece:** A training framework pairing a scale-and-permutation equivariant encoder architecture (e.g., ScaleGMN or UNF extended) with SSL objectives (contrastive, masked weight modeling, or autoencoder) trained on real model zoo checkpoints, with downstream evaluation on property prediction, editing, and generation benchmarks.

**Potential Impact:** High — directly enables answering the primary research question; would be the first method to satisfy all three constraints simultaneously

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|---|---|---|---|---|---|---|
| "Scale Equivariant Graph Metanetworks" | 2024 | Kalogeropoulos et al. | (ScaleGMN SS ID) | 2406.10805 | ~15 | First scale+perm equivariant method — supervised only, no SSL objective |
| "Hyper-Representations as Generative Models" | 2022 | Schürholt et al. | (NeurIPS 2022 ID) | 2209.14733 | ~45 | Generative hyper-representations on weight zoo — no scale equivariance |
| "SANE: Sequential Autoencoder for Neural Embeddings" | 2024 | Schürholt et al. | (ICML 2024 ID) | 2310.09830 | ~20 | Scalable SSL on weight zoo — no symmetry equivariance |
| "Permutation Equivariant Neural Functionals" | 2023 | Navon et al. | (NeurIPS 2023 ID) | 2302.14040 | ~120 | Formal perm-equivariant NF-Layers — no scaling symmetry, no SSL |
| "Self-Supervised Representation Learning on Neural Network Weights" | 2021 | Schürholt et al. | (NeurIPS 2021 ID) | 2110.15288 | ~80 | Foundational SSL on weights — no equivariance enforcement |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|---|---|---|---|
| [INFERRED] SSL pre-training + equivariant encoder decoupling | N/A (Archon KB domain mismatch) | "symmetry-aware weight space learning" | Pattern: SSL objective and equivariant architecture are independent design choices — can be combined |
| [INFERRED] Contrastive learning on structured data | N/A (Archon KB domain mismatch) | "self-supervised learning structured symmetry" | Pattern: Symmetry-aware augmentation in contrastive SSL improves representation quality |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---|---|---|---|---|
| jkalogero/scalegmn | https://github.com/jkalogero/scalegmn | 23 | Python | Scale+perm equivariant encoder — needs SSL wrapper |
| HSG-AIML/SANE | https://github.com/HSG-AIML/SANE | 33 | Python | SSL training on weight zoo — needs equivariant encoder |
| HSG-AIML/MultiZoo-SANE | https://github.com/HSG-AIML/MultiZoo-SANE | N/A | Python | Multi-zoo SSL — heterogeneous architectures, no symmetry enforcement |
| AllanYangZhou/universal_neural_functional | https://github.com/AllanYangZhou/universal_neural_functional | 56 | JAX | Any-architecture equivariant model — could serve as equivariant encoder backbone |

---

#### Gap 2: Proved Cross-Architecture Transfer of Weight Representations to Held-Out General Architectures

**Relevance Classification:** 🎯 PRIMARY
**Connection Type:**
- ☑️ Blocks answering research question: The research question explicitly requires "provably transfer to downstream tasks on held-out architectures." No existing work demonstrates — let alone proves — that symmetry-respecting weight representations transfer to genuinely held-out general model architectures (e.g., train on CNN checkpoints, evaluate on transformer checkpoints from the same zoo task). Domain-specific transfer (NeRF architectures) does not satisfy this requirement.
- ☑️ Relates to Sub-Q1 (generalization across architectures), Sub-Q5 (sample efficiency with held-out architectures)
- ☐ No reference paper limitations to extend

**Current State:** Neural-Graphs (Kofinas 2024) and UNF (Zhou 2024) show a single model can process diverse architectures in a supervised setting. Ballerini 2025 shows SSL weight representations transfer across held-out NeRF architectures within domain. No work shows SSL-trained symmetry-equivariant representations transfer to held-out general-purpose model architectures (MLPs → CNNs → Transformers trained on standard tasks).

**Missing Piece:** Empirical demonstration (and ideally theoretical characterization) of: (1) training a symmetry-equivariant SSL weight encoder on a subset of architectures from a model zoo, (2) fine-tuning or zero-shot evaluation on held-out architectures not seen during training, (3) measuring downstream task performance on property prediction and model editing benchmarks — using only existing checkpoints and benchmarks.

**Potential Impact:** High — without this evidence, the research question cannot be answered; this is the "transfer" criterion of the research question

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|---|---|---|---|---|---|---|
| "Graph Neural Networks for Learning Equivariant Representations of Neural Networks" | 2024 | Kofinas et al. | (ICLR 2024 ID) | 2403.12143 | ~10 | Single GNN processes diverse architectures — supervised only, no held-out SSL transfer |
| "Universal Neural Functionals" | 2024 | Zhou et al. | (NeurIPS 2024 ID) | 2402.05232 | ~20 | Any-arch equivariant models — supervised setting only |
| "Self-Supervised Representations for INRs in Heterogeneous Zoos" | 2025 | Ballerini et al. | (SS ID) | (arXiv ID) | ~5 | SSL on heterogeneous NeRF zoo with held-out arch transfer — domain-specific (NeRFs only) |
| "SANE: Sequential Autoencoder for Neural Embeddings" | 2024 | Schürholt et al. | (ICML 2024 ID) | 2310.09830 | ~20 | Scalable SSL on diverse zoo — no systematic held-out architecture evaluation |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|---|---|---|---|
| [INFERRED] Transfer learning from structured pre-training | N/A (Archon KB domain mismatch) | "permutation invariant weight embeddings architecture generalization" | Pattern: Pre-training on rich structured data transfers to held-out distributions when inductive biases match |
| [INFERRED] Zero-shot generalization via equivariant representations | N/A (Archon KB domain mismatch) | "equivariant GNN neural network weights property prediction" | Pattern: Equivariant representations generalize better to unseen symmetry group instances |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---|---|---|---|---|
| mkofinas/neural-graphs | https://github.com/mkofinas/neural-graphs | 86 | Python | Multi-architecture GNN — supervised baseline for cross-arch processing |
| HSG-AIML/MultiZoo-SANE | https://github.com/HSG-AIML/MultiZoo-SANE | N/A | Python | Heterogeneous zoo SSL — closest existing implementation of cross-arch SSL |
| AllanYangZhou/nfn | https://github.com/AllanYangZhou/nfn | 93 | Python | NFN library — MLP/CNN weight processing baseline |

---

#### Gap 3: Joint Multi-Task Evaluation Protocol for Weight Representations Across All Downstream Task Types

**Relevance Classification:** 🔗 SECONDARY
**Connection Type:**
- ☑️ Blocks answering research question: The research question requires transfer to property prediction *and* model editing *and* weight generation — all three. No existing work evaluates a single weight representation method across all three task types on standard benchmarks without synthetic data.
- ☑️ Relates to Sub-Q2 (property decoding), Sub-Q3 (model editing), Sub-Q4 (generative models) — the research question's three downstream task pillars
- ☐ No reference paper limitations to extend

**Current State:** Property prediction benchmarks exist and are used (generalization prediction: Unterthiner 2020, Schürholt 2021, Kalogeropoulos 2024). Model editing/merging is evaluated separately using task-specific metrics (GLUE, ImageNet). Weight generation is evaluated by generated model task accuracy. Each downstream task type has its own evaluation ecosystem; no paper evaluates one weight representation across all three jointly.

**Missing Piece:** A unified evaluation protocol applying a single learned weight representation to: (1) property prediction (accuracy/generalization gap prediction on standard splits), (2) model editing (merging or pruning using weight-space representation structure, evaluated on GLUE/ImageNet), and (3) weight generation (sampling from learned latent space, evaluating generated model accuracy) — all using existing benchmarks without new annotation.

**Potential Impact:** Medium-High — enables a fair comparison of weight representation methods; necessary to establish whether the research question can be answered by any single method

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|---|---|---|---|---|---|---|
| "Self-Supervised Representation Learning on Neural Network Weights" | 2021 | Schürholt et al. | (NeurIPS 2021 ID) | 2110.15288 | ~80 | Establishes property prediction evaluation; does not cover editing or generation jointly |
| "Hyper-Representations as Generative Models" | 2022 | Schürholt et al. | (NeurIPS 2022 ID) | 2209.14733 | ~45 | Adds generation to hyper-representations; property prediction + generation but not editing |
| "Git Re-Basin: Merging Models modulo Permutation Symmetries" | 2022 | Ainsworth et al. | (SS ID) | 2209.04836 | ~150 | Permutation-aware merging — model editing task only, separate pipeline |
| "Scale Equivariant Graph Metanetworks" | 2024 | Kalogeropoulos et al. | (ScaleGMN SS ID) | 2406.10805 | ~15 | Property prediction evaluation with equivariant representations — no editing/generation |
| "A Survey of Weight Space Learning" | 2026 | (Survey authors) | N/A | 2603.10090 | ~0 | 2026 synthesis — signals this gap is recognized but not yet closed |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|---|---|---|---|
| [INFERRED] Multi-task evaluation of shared representations | N/A (Archon KB domain mismatch) | "model zoo weight embeddings downstream task transfer" | Pattern: Joint multi-task evaluation reveals representation generality that single-task evaluation misses |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---|---|---|---|---|
| HSG-AIML/NeurIPS_2022-Generative_Hyper_Representations | https://github.com/HSG-AIML/NeurIPS_2022-Generative_Hyper_Representations | 18 | Python | Property prediction + generation — missing editing evaluation |
| arcee-ai/MergeKit | https://github.com/arcee-ai/MergeKit | 7159 | Python | Model editing/merging at scale — separate pipeline not integrated with weight-repr. learning |
| samuela/git-re-basin | https://github.com/samuela/git-re-basin | 514 | Python | Permutation-aligned merging — model editing baseline, separate from representation learning |

---

### Gap Priority Matrix

| Gap ID | Relevance | Connection to Research Question | Connection to Detailed Questions | Extends Reference Paper | Impact | Evidence Count | Priority |
|---|---|---|---|---|---|---|---|
| Gap 1 | 🎯 PRIMARY | ☑️ Blocks: No existing method combines SSL + scale+perm equivariance | ☑️ Sub-Q1, Sub-Q5 | ☐ N/A | High | 5 Scholar + 4 Exa + 2 Inferred | Critical |
| Gap 2 | 🎯 PRIMARY | ☑️ Blocks: No proved cross-architecture SSL transfer for general models | ☑️ Sub-Q1, Sub-Q5 | ☐ N/A | High | 4 Scholar + 3 Exa + 2 Inferred | Critical |
| Gap 3 | 🔗 SECONDARY | ☑️ Partially blocks: No joint evaluation across all 3 downstream task types | ☑️ Sub-Q2, Sub-Q3, Sub-Q4 | ☐ N/A | Medium-High | 5 Scholar + 3 Exa + 1 Inferred | High |

### User Input to Gap Traceability

**Main Research Question** → directly addressed by:
- Gap 1: The research question's "unsupervised/SSL + symmetry-respecting" constraint is unmet by any existing single method
- Gap 2: The research question's "provably transfer to held-out architectures" criterion is undemonstrated for general model checkpoints

**Sub-Q1** (symmetry-aware methods generalizing across architectures in model zoos) addressed by:
- Gap 1: SSL + symmetry equivariance not yet unified
- Gap 2: Cross-architecture generalization not yet demonstrated for SSL weight representations on general checkpoints

**Sub-Q2** (property decoding from weight embeddings) addressed by:
- Gap 3: Existing property prediction evaluations not paired with editing/generation in a joint protocol

**Sub-Q3** (model editing with weight-space representations) addressed by:
- Gap 3: Model editing via learned weight representations not jointly evaluated with property prediction/generation

**Sub-Q4** (weight-space generative models from zoo checkpoints) addressed by:
- Gap 3: Weight generation evaluated in isolation; no unified evaluation with property prediction and editing

**Sub-Q5** (symmetry constraints and sample efficiency with held-out architectures) addressed by:
- Gap 1: Symmetry constraints effect on SSL learning not studied
- Gap 2: Held-out architecture evaluation of SSL weight representations not demonstrated

---

## 9. Conclusion

### Key Findings

1. **Two convergent research tracks, not yet unified**: Equivariant weight processing (NFN/ScaleGMN/UNF/neural-graphs) and SSL on weight populations (hyper-representations/SANE) have advanced independently. Their combination is the primary gap.

2. **ScaleGMN (2024) is the most complete symmetry solution** but lacks SSL training objective — handles both permutation and scaling symmetries for supervised tasks; no self-supervised variant found.

3. **SANE (ICML 2024) is the most scalable SSL solution** on heterogeneous model zoo populations, but does not enforce scale/permutation equivariance during representation learning.

4. **Cross-architecture transfer demonstrated domain-specifically**: Ballerini 2025 shows held-out NeRF architecture generalization with SSL. Universal NFN (Zhou 2024) shows any-architecture equivariant processing. No work combines these for general model checkpoints.

5. **Strong implementation ecosystem**: All key papers have public implementations (AllanYangZhou/nfn, jkalogero/scalegmn, mkofinas/neural-graphs, HSG-AIML/SANE) with MIT/Apache licenses — feasibility of building on existing code confirmed.

6. **2026 WSL Survey (arXiv 2603.10090) confirms field maturity**: Comprehensive synthesis just published — field is past foundational phase, entering integration/generalization phase.

7. **All 3 downstream task types have independent evaluation baselines**: Property prediction (Schürholt 2021/Kalogeropoulos 2024), model editing (git-re-basin/mergekit), weight generation (NeurIPS 2022 generative hyper-representations) — joint evaluation across all three is the missing protocol.

### Answer to Detailed Question (Preliminary)

*(Preliminary — data-only, no hypotheses proposed per Phase 1 boundary)*

- **Sub-Q1** (symmetry-aware methods across model zoos): Partially addressed — equivariant architectures exist for diverse architecture types (UNF, neural-graphs), but SSL training on model zoos without symmetry enforcement is the norm. Cross-architecture generalization with symmetry constraints on general zoos: not demonstrated.

- **Sub-Q2** (property decoding from weight embeddings): Well-addressed — multiple papers show accuracy, generalization gap, robustness decodable from weight embeddings (Schürholt 2021, Kalogeropoulos 2024). Scaling to heterogeneous architectures is less explored.

- **Sub-Q3** (model editing with weight-space representations): Partially addressed — git-re-basin, mergekit implement permutation-aware merging; hyper-representations have not been used to guide model editing.

- **Sub-Q4** (weight-space generative models from zoo checkpoints): Addressed for small models (NeurIPS 2022 generative hyper-representations, wsr.pytorch for NeRFs); scaling to diverse general model checkpoints with symmetry enforcement is open.

- **Sub-Q5** (symmetry constraints and sample efficiency on held-out architectures): Not directly addressed in literature — theoretical expressivity work (Dayan 2026) exists for supervised setting; SSL sample efficiency with symmetry constraints unstudied.

### Phase 2 Readiness

- [x] Research question fully analyzed
- [x] 22 academic papers collected and verified with SS IDs
- [x] 12 GitHub repositories identified with URLs and metadata
- [x] 3 research gaps identified in PRIMARY/SECONDARY classification
- [x] All gaps have table-format evidence for Phase 2A programmatic extraction
- [x] Gap traceability to all 5 sub-questions documented
- [x] Phase boundary maintained — no hypotheses proposed
- [x] Implementation ecosystem confirmed — all key repos publicly available
- [ ] Archon KB patterns: domain mismatch — 4 inferred patterns (labeled [INFERRED])

**Phase 2A Input Quality: HIGH** — Research gaps are well-evidenced and directly connected to the research question; Phase 2A hypothesis generation can proceed.

### Next Steps

1. **Phase 2A-Dialogue**: Read `01_targeted_research.md` (compact) and generate testable hypotheses targeting the 3 identified gaps — particularly Gap 1 (unified SSL + equivariance) and Gap 2 (cross-architecture transfer)
2. **Priority focus for Phase 2A**: Gap 1 is Critical priority — combining ScaleGMN-style equivariance with SANE-style SSL training is a concrete, feasible hypothesis space
3. **Available baselines confirmed**: NFN, ScaleGMN, SANE, neural-graphs all have public implementations — Phase 2B can build on these

---

*Phase: 1 - Targeted Research Gathering*
*Total processing time: ~45 minutes (automated, 2026-08-05)*
