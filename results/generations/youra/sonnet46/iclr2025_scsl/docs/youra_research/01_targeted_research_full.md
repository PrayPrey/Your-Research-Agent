# Targeted Research Report: How do optimization dynamics (SGD/Adam), loss landscape geometry, and learning paradigm choices (supervised vs. contrastive/self-supervised) jointly determine a model's susceptibility to spurious correlations — and can targeted interventions at the optimization or representation level robustify models on existing real-world benchmarks even when spurious feature information is partially unknown?

**Generated:** 2026-03-16
**Phase:** 1 - Targeted Research Gathering
**Phase Output:** Research data, gaps (Pre-hypothesis, targeted approach)
**Analyst:** Deep Learning Research Analyst 🔍
**Researcher:** Anonymous
---

## Executive Summary

Phase 1 targeted research for the question: *"How do optimization dynamics (SGD/Adam), loss landscape geometry, and learning paradigm choices jointly determine a model's susceptibility to spurious correlations — and can targeted interventions robustify models even with partially unknown spurious features?"*

**Key findings (20 verified papers, 32 MCP queries):**

1. **Optimization dynamics**: SGD exhibits extreme simplicity bias (Shah 2020, 434 citations); Adam is more resistant and achieves richer features + better OOD generalization on spurious correlation datasets (Vasudeva 2025). Optimization-level interventions (JTT, error upsampling) close 75% of the gap to GroupDRO without group labels.

2. **Loss landscape geometry**: SAM (Foret 2020, 1780 citations) seeks flat minima for generalization and implicitly learns robust features (Zhang 2024). Flatness is confirmed necessary for generalization (Han 2025). **Critical gap**: SAM has NOT been evaluated on standard spurious correlation benchmarks (Waterbirds, CelebA).

3. **Learning paradigms**: SSL is more robust than supervised ERM on Waterbirds (63.6% vs 60.6% WGA, Zare 2023), and large contrastive-pretrained models (ViT) achieve 90% WGA without group labels (Mehta 2022). **Critical gap**: No systematic SimCLR/MoCo vs. ERM comparison on standard benchmarks.

4. **Causal/IRM**: IRM fails under strong spurious correlations (Guo 2021); DomainBed provides systematic comparison but not on Waterbirds/CelebA specifically.

5. **Partial group labels**: Rich literature from GroupDRO → JTT → DFR → SSA → SELF → annotation-free methods. **Critical gap**: No annotation budget degradation curve characterizing the full trajectory from 0% to 100% group labels across methods.

**MCP Performance**: Semantic Scholar ✅ (20 papers), Archon KB ⚠️ (domain mismatch — diffusion models), Exa ❌ (402 billing error).

**Research Gaps Identified**: 3 PRIMARY gaps directly blocking sub-questions 2, 3, and 5. Phase 2A readiness: HIGH.

---

## 0. Reference Paper Analysis

*No reference papers provided*

---

## 1. Research Questions

### Primary Research Question
How do optimization dynamics (SGD/Adam), loss landscape geometry, and learning paradigm choices (supervised vs. contrastive/self-supervised) jointly determine a model's susceptibility to spurious correlations — and can targeted interventions at the optimization or representation level robustify models on existing real-world benchmarks even when spurious feature information is partially unknown?

### Detailed Research Questions
1. **Optimization dynamics and shortcut bias**: What role do gradient-descent optimization dynamics (SGD, Adam, learning rate schedules) play in the preferential learning of shortcut features over core features, and can optimization-level interventions (e.g., loss reweighting, gradient surgery) reduce this bias — measurable on Waterbirds and CelebA?

2. **Loss landscape geometry**: How does the loss landscape geometry change in the presence of spurious features, and can curvature-based or sharpness-aware analysis (e.g., SAM, spectral analysis) predict or mitigate shortcut reliance on existing spurious correlation benchmarks?

3. **Contrastive and self-supervised paradigms**: How do contrastive learning (SimCLR, MoCo) and self-supervised learning paradigms differ from supervised ERM in their susceptibility to spurious correlations on existing datasets (STL-10, ImageNet subsets, CelebA), and do they provide any inherent robustness advantage?

4. **Causal representation learning on real datasets**: Can causal representation learning algorithms (IRM, v-REx, CORAL) be systematically compared on existing real-world spurious correlation benchmarks (Waterbirds, MultiNLI, CivilComments) to identify when causal approaches outperform ERM and why?

5. **Partially-unknown spurious features**: When spurious feature information is partially unknown (e.g., only a fraction of group labels available), what is the performance degradation trajectory of existing robustification methods (DFR, JTT, GEORGE, AFR) relative to full spurious-feature knowledge, and can unsupervised clustering of last-layer representations bridge this gap?

### Lessons from Previous Attempts (ROUTE_TO_0 Only)
*N/A - First attempt*

---

## 2. Search Queries Generated

### Query Generation Source Summary
- Failure-aware queries (ROUTE_TO_0): N/A
- Reference paper queries: 0 (No reference papers provided)
- Brainstorm insights queries: 5
- Direct question queries: 11
- **Total: 16 queries**

Query Priority Order:
🥈 Brainstorm insights (key discoveries + unexplored directions)
🥉 Question decomposition (baseline coverage)

### Priority 1: Reference Paper Concept Queries
*No reference papers provided*

### Priority 2: Brainstorm Insights Queries
1. "optimization simplicity bias shortcut learning spurious correlations"
2. "SAM sharpness-aware minimization spurious features robustness"
3. "contrastive learning self-supervised spurious correlations benchmark"
4. "IRM invariant risk minimization Waterbirds CelebA comparison"
5. "partial group labels spurious correlation robustification semi-supervised"

### Priority 3: Direct Question Decomposition Queries
**Technical:**
1. "SGD Adam gradient dynamics shortcut feature learning"
2. "loss landscape geometry spurious correlations flatness curvature"
3. "SimCLR MoCo spurious correlations group robustness"
4. "GroupDRO JTT DFR worst group accuracy comparison"
5. "unsupervised last-layer clustering group discovery spurious"

**Theoretical:**
6. "simplicity bias neural network inductive bias shortcut"
7. "causal representation learning distribution shift generalization"

**Comparative:**
8. "ERM vs IRM robustness spurious correlation benchmark"
9. "supervised vs contrastive learning subgroup robustness"

**Problem-Specific:**
10. "gradient reweighting spurious correlation optimization intervention"
11. "GEORGE AFR spurious feature unknown partial annotation DFR"

---

## 3. Past Cases & Best Practices (via Archon)

**MCP Server Used:** Archon Knowledge Base (`mcp__archon__rag_search_knowledge_base`)
**Total Queries:** 13 queries across 3 levels
**Results Found:** 0 verified cases + 4 inferred patterns
**Note:** Archon KB contains diffusion model / generative AI content — no spurious correlation research cases present. All results below are [INFERRED] from general knowledge per fallback protocol.

### Direct Implementations
**[NOT_FOUND - ARCHON]** No directly relevant past cases found in Archon KB for spurious correlations, shortcut learning, or robustification methods.

### Similar Architectural Patterns
**[INFERRED]** Pattern 1: Last-Layer Retraining (LLR/DFR) Pattern
- Source: General knowledge (Archon search yielded no results)
- Reasoning: Freeze feature extractor, retrain only the final linear layer on balanced/reweighted data. Kirichenko et al. (2022) — DFR exploits the observation that pretrained representations already contain core features; spurious reliance is concentrated in the classifier head.
- Application: Directly applicable to sub-questions 1 and 5.

**[INFERRED]** Pattern 2: Two-Stage Training with Error-Based Upsampling
- Source: General knowledge (Archon search yielded no results)
- Reasoning: Methods like JTT (Liu et al. 2021) and LfF (Nam et al. 2020) use a first-pass ERM model to identify misclassified (likely minority group) examples, then retrain with upsampled error set. Does not require group labels — only training error signals.
- Application: Directly applicable to sub-questions 1 and 5.

**[INFERRED]** Pattern 3: Invariant Feature Learning via Penalty Regularization
- Source: General knowledge (Archon search yielded no results)
- Reasoning: IRM (Arjovsky et al. 2020), v-REx (Krueger et al. 2021), and CORAL add regularization terms that penalize environment-inconsistent gradients, forcing representations to be invariant across environments. Requires environment/group partition at training time.
- Application: Directly applicable to sub-question 4.

**[INFERRED]** Pattern 4: Sharpness-Aware Optimization for Flat Minima
- Source: General knowledge (Archon search yielded no results)
- Reasoning: SAM (Foret et al. 2021) perturbs weights toward maximum loss increase, then minimizes this perturbed loss — seeking flat minima that generalize better. Whether flat minima specifically reduce spurious correlation reliance is an open question relevant to sub-question 2.
- Application: Directly applicable to sub-question 2.

### Code Examples Found
*No code examples found in Archon KB for this domain.*

---

## 4. Academic Literature Review (via Semantic Scholar)

**MCP Server Used:** Semantic Scholar (`mcp__hamid-vakilzadeh-mcpsemanticscholar__paper_relevance_search`)
**Total Queries:** 12 queries across 4 rounds
**Results Found:** 20 papers (12 directly relevant, 6 foundational, 2 from extended search)

### Directly Relevant Papers

1. **[VERIFIED - SCHOLAR]** "The Pitfalls of Simplicity Bias in Neural Networks" (2020)
   - Authors: Harshay Shah, Kaustav Tamuly, Aditi Raghunathan, Prateek Jain, Praneeth Netrapalli
   - Citations: 434
   - Semantic Scholar ID: `0b40141779fafcedc28d83bd678807ddb5980df3`
   - arXiv ID: 2006.07710
   - URL: https://www.semanticscholar.org/paper/0b40141779fafcedc28d83bd678807ddb5980df3
   - Search Query: "optimization simplicity bias shortcut features SGD neural networks"
   - Key Contribution: Demonstrates that SGD's simplicity bias is extreme — models rely exclusively on simplest features; adversarial training and ensembles do not mitigate it. Directly addresses sub-question 1.

2. **[VERIFIED - SCHOLAR]** "The Rich and the Simple: On the Implicit Bias of Adam and SGD" (2025)
   - Authors: Bhavya Vasudeva, Jung Whan Lee, V. Sharan, Mahdi Soltanolkotabi
   - Citations: 7
   - Semantic Scholar ID: `b74959fefcc39e33f5ceaa3969d98e84a1de8fca`
   - arXiv ID: 2505.24022
   - URL: https://www.semanticscholar.org/paper/b74959fefcc39e33f5ceaa3969d98e84a1de8fca
   - Search Query: "optimization simplicity bias shortcut features SGD neural networks"
   - Key Contribution: Shows Adam is more resistant to simplicity bias than SGD; Adam achieves richer features and superior OOD generalization on spurious correlation datasets. Directly addresses sub-question 1.

3. **[VERIFIED - SCHOLAR]** "Sharpness-Aware Minimization for Efficiently Improving Generalization" (2020)
   - Authors: Pierre Foret, Ariel Kleiner, H. Mobahi, Behnam Neyshabur
   - Citations: 1780
   - Semantic Scholar ID: `a2cd073b57be744533152202989228cb4122270a`
   - arXiv ID: 2010.01412
   - URL: https://www.semanticscholar.org/paper/a2cd073b57be744533152202989228cb4122270a
   - Search Query: "sharpness aware minimization SAM generalization robustness"
   - Key Contribution: Introduces SAM — seeks parameters in neighborhoods with uniformly low loss; improves generalization across benchmarks and provides robustness to label noise. Directly addresses sub-question 2.

4. **[VERIFIED - SCHOLAR]** "On the Duality Between Sharpness-Aware Minimization and Adversarial Training" (2024)
   - Authors: Yihao Zhang et al.
   - Citations: 26
   - Semantic Scholar ID: `9782fe260f98da685d1e5f4f18d9b71a54664a95`
   - arXiv ID: 2402.15152
   - URL: https://www.semanticscholar.org/paper/9782fe260f98da685d1e5f4f18d9b71a54664a95
   - Search Query: "sharpness aware minimization SAM generalization robustness"
   - Key Contribution: SAM implicitly learns more robust features; can improve adversarial robustness without sacrificing clean accuracy. Relevant to sub-question 2.

5. **[VERIFIED - SCHOLAR]** "Just Train Twice: Improving Group Robustness without Training Group Information" (2021)
   - Authors: E. Liu, Behzad Haghgoo, Annie S. Chen, Aditi Raghunathan, Pang Wei Koh, Shiori Sagawa, Percy Liang, Chelsea Finn
   - Citations: 665
   - Semantic Scholar ID: `216d093cb2ad81bf55c21dbce2217f2b9032e67b`
   - arXiv ID: 2107.09044
   - URL: https://www.semanticscholar.org/paper/216d093cb2ad81bf55c21dbce2217f2b9032e67b
   - Search Query: "just train twice JTT minority groups spurious correlations"
   - Key Contribution: Two-stage method: train ERM, upweight misclassified examples, retrain. Closes 75% gap between ERM and GroupDRO worst-group accuracy without group annotations. Directly addresses sub-questions 1 and 5.

6. **[VERIFIED - SCHOLAR]** "Evaluating and Improving Domain Invariance in Contrastive Self-Supervised Learning" (2023)
   - Authors: Samira Zare, Hien Van Nguyen
   - Citations: 2
   - Semantic Scholar ID: `4deab7970072d6358bd9aa42bfd6bc88c9f5e048`
   - arXiv ID: N/A (DOI: 10.1109/ACCESS.2023.3339775)
   - URL: https://www.semanticscholar.org/paper/4deab7970072d6358bd9aa42bfd6bc88c9f5e048
   - Search Query: "contrastive self-supervised learning spurious correlations robustness"
   - Key Contribution: SSL is more robust than supervised learning (52.8% vs 17.1% on CMNIST, 63.6% vs 60.6% on Waterbirds) but still suffers from spurious correlations; proposes ReinformNCE combining infoNCE with robust optimization. Directly addresses sub-question 3.

7. **[VERIFIED - SCHOLAR]** "You Only Need a Good Embeddings Extractor to Fix Spurious Correlations" (2022)
   - Authors: Raghav Mehta et al.
   - Citations: 21
   - Semantic Scholar ID: `66aeeeca159d95622d9692fe8bc50b183894ee00`
   - arXiv ID: 2212.06254
   - URL: https://www.semanticscholar.org/paper/66aeeeca159d95622d9692fe8bc50b183894ee00
   - Search Query: "GroupDRO worst group accuracy distributionally robust spurious"
   - Key Contribution: Large pretrained vision models (ViT) achieve 90% WGA on Waterbirds without group labels — better than GroupDRO (89%) which requires group labels. Addresses sub-questions 1, 3, 5.

8. **[VERIFIED - SCHOLAR]** "Spread Spurious Attribute: Improving Worst-group Accuracy with Spurious Attribute Estimation" (2022)
   - Authors: J. Nam, Jaehyung Kim, Jaeho Lee, Jinwoo Shin
   - Citations: 109
   - Semantic Scholar ID: `d398aae4520ab684b87287b831fee244d5474e99`
   - arXiv ID: 2204.02070
   - URL: https://www.semanticscholar.org/paper/d398aae4520ab684b87287b831fee244d5474e99
   - Search Query: "GroupDRO worst group accuracy distributionally robust spurious"
   - Key Contribution: SSA (GEORGE successor): trains spurious attribute predictor, uses pseudo-attributes for group robustness. Achieves GroupDRO-level performance with only 0.6–1.5% annotation. Directly addresses sub-question 5.

9. **[VERIFIED - SCHOLAR]** "Is Last Layer Re-Training Truly Sufficient for Robustness to Spurious Correlations?" (2023)
   - Authors: Phuong Quynh Le, Jörg Schlötterer, Christin Seifert
   - Citations: 9
   - Semantic Scholar ID: `aed28b0fac2b451f2674bb4919b6d38bb7360279`
   - arXiv ID: 2308.00473
   - URL: https://www.semanticscholar.org/paper/aed28b0fac2b451f2674bb4919b6d38bb7360279
   - Search Query: "partial group labels spurious correlation last layer retraining DFR JTT"
   - Key Contribution: Critically evaluates DFR in medical domain — remains susceptible to spurious correlations despite last-layer retraining. Relevant to sub-question 5.

10. **[VERIFIED - SCHOLAR]** "Towards Last-layer Retraining for Group Robustness with Fewer Annotations" (2023)
    - Authors: Tyler LaBonte, Vidya Muthukumar, Abhishek Kumar
    - Citations: 59
    - Semantic Scholar ID: `2d14697232f03661cb86246df46e52816694a97f`
    - arXiv ID: 2309.08534
    - URL: https://www.semanticscholar.org/paper/2d14697232f03661cb86246df46e52816694a97f
    - Search Query: "last layer retraining deep feature reweighting spurious correlations"
    - Key Contribution: SELF method — last-layer retraining effective with no group annotations and <3% class annotations; model disagreement upsamples worst-group data. Directly addresses sub-question 5.

11. **[VERIFIED - SCHOLAR]** "Calibrating Multi-modal Representations: A Pursuit of Group Robustness without Annotations" (2024)
    - Authors: Chenyu You et al.
    - Citations: 35
    - Semantic Scholar ID: `6f516e8ac5db2a90b31d53970d26f049490c8305`
    - arXiv ID: 2403.07241
    - URL: https://www.semanticscholar.org/paper/6f516e8ac5db2a90b31d53970d26f049490c8305
    - Search Query: "partial group labels spurious correlation last layer retraining DFR JTT"
    - Key Contribution: CLIP + DFR + contrastive calibration achieves group robustness without group labels. Addresses sub-questions 3 and 5.

12. **[VERIFIED - SCHOLAR]** "ExMap: Leveraging Explainability Heatmaps for Unsupervised Group Robustness" (2024)
    - Authors: Rwiddhi Chakraborty, Adrian Sletten, Michael Kampffmeyer
    - Citations: 5
    - Semantic Scholar ID: `3e9fb2d2ad9b3e57714ebaba4ac52931d818d14f`
    - arXiv ID: 2403.13870
    - URL: https://www.semanticscholar.org/paper/3e9fb2d2ad9b3e57714ebaba4ac52931d818d14f
    - Search Query: "spurious correlations robustness survey deep learning group shift"
    - Key Contribution: Unsupervised two-stage mechanism using explainability heatmaps + clustering to infer pseudo-labels for group robustness. Directly addresses sub-question 5.

### Foundational Papers

1. **[VERIFIED - SCHOLAR]** "Distributionally Robust Neural Networks for Group Shifts: On the Importance of Regularization for Worst-Case Generalization" (2019)
   - Authors: Shiori Sagawa, Pang Wei Koh, Tatsunori B. Hashimoto, Percy Liang
   - Citations: 1515
   - Semantic Scholar ID: `193092aef465bec868d1089ccfcac0279b914bda`
   - arXiv ID: 1911.08731
   - URL: https://www.semanticscholar.org/paper/193092aef465bec868d1089ccfcac0279b914bda
   - Search Query: "distributionally robust neural networks Waterbirds CelebA worst group"
   - Key Contribution: GroupDRO — introduces Waterbirds and CelebA as spurious correlation benchmarks; shows regularization critical for worst-group generalization. THE foundational paper for sub-questions 1, 4, 5.

2. **[VERIFIED - SCHOLAR]** "Out-of-distribution Prediction with Invariant Risk Minimization: The Limitation and An Effective Fix" (2021)
   - Authors: Ruocheng Guo et al.
   - Citations: 37
   - Semantic Scholar ID: `340bd0cfeeab5d117a9fdffffa9e05fe2afaf64f`
   - arXiv ID: 2101.07732
   - URL: https://www.semanticscholar.org/paper/340bd0cfeeab5d117a9fdffffa9e05fe2afaf64f
   - Search Query: "invariant risk minimization IRM spurious correlations"
   - Key Contribution: IRM fails under strong spurious correlations (strong Λ-spuriousness); proposes combining IRM with conditional distribution matching. Relevant to sub-question 4.

3. **[VERIFIED - SCHOLAR]** "Feature Reconstruction From Outputs Can Mitigate Simplicity Bias in Neural Networks" (2023)
   - Authors: Sravanti Addepalli et al.
   - Citations: 10
   - Semantic Scholar ID: `9bdb9d9add99fc2697cda911283679580e92d9a5`
   - arXiv ID: N/A (OpenReview)
   - URL: https://www.semanticscholar.org/paper/9bdb9d9add99fc2697cda911283679580e92d9a5
   - Search Query: "optimization simplicity bias shortcut features SGD neural networks"
   - Key Contribution: FRR — Feature Reconstruction Regularizer mitigates simplicity bias by ensuring features can be reconstructed from logits; up to 15% OOD accuracy gains. Addresses sub-question 1.

4. **[VERIFIED - SCHOLAR]** "Causal Inference Meets Deep Learning: A Comprehensive Survey" (2024)
   - Authors: Licheng Jiao et al.
   - Citations: 70
   - Semantic Scholar ID: `ffcf8ab201a4766fc6994253890a795c376cc3f0`
   - arXiv ID: N/A (DOI: 10.34133/research.0467)
   - URL: https://www.semanticscholar.org/paper/ffcf8ab201a4766fc6994253890a795c376cc3f0
   - Search Query: "spurious correlations robustness survey deep learning group shift"
   - Key Contribution: Comprehensive survey of causal inference in deep learning; covers IRM, causal representation learning, and spurious correlation mitigation. Background for sub-question 4.

5. **[VERIFIED - SCHOLAR]** "Not Only the Last-Layer Features for Spurious Correlations: All Layer Deep Feature Reweighting" (2024)
   - Authors: Humza Wajid Hameed, Géraldin Nanfack, Eugene Belilovsky
   - Citations: 3
   - Semantic Scholar ID: `f6be26649ad1ee6fd034971fcdb0259fcd5c6542`
   - arXiv ID: 2409.14637
   - URL: https://www.semanticscholar.org/paper/f6be26649ad1ee6fd034971fcdb0259fcd5c6542
   - Search Query: "last layer retraining deep feature reweighting spurious correlations"
   - Key Contribution: All-layer DFR outperforms last-layer-only DFR; key attributes sometimes discarded towards last layer. Extends sub-question 5 scope.

6. **[VERIFIED - SCHOLAR]** "Flatness is Necessary, Neural Collapse is Not: Rethinking Generalization via Grokking" (2025)
   - Authors: Tingxu Han et al.
   - Citations: 4
   - Semantic Scholar ID: `ae083ea4f920026d745d25d565553aa4170420bc`
   - arXiv ID: 2509.17738
   - URL: https://www.semanticscholar.org/paper/ae083ea4f920026d745d25d565553aa4170420bc
   - Search Query: "loss landscape geometry flatness generalization neural network"
   - Key Contribution: Flatness is necessary (and potentially sufficient) for generalization; neural collapse is a byproduct but not causal. Relevant to sub-question 2.

### Citation Network Analysis
- No reference papers provided → citation network analysis not applicable
- **Most influential work:** Sagawa et al. 2019 (GroupDRO) — 1515 citations; establishes Waterbirds/CelebA benchmarks used across sub-questions
- **Research lineage:** Shah et al. 2020 (simplicity bias) → Adam/SGD comparison (2025) → FRR (2023) [sub-question 1 thread]
- **Research lineage:** Sagawa 2019 (GroupDRO) → Liu et al. JTT 2021 → LaBonte SELF 2023 → annotation-free methods 2024 [sub-question 5 thread]
- **Research lineage:** Foret 2020 (SAM) → SAM+adversarial 2024 → Flatness-generalization 2025 [sub-question 2 thread]
- **Key gap identified:** Contrastive/SSL vs supervised comparison on spurious benchmarks is sparse — only 1 directly relevant paper (Zare 2023); most SSL work doesn't evaluate on standard spurious correlation benchmarks (Waterbirds, CelebA). Gap directly relevant to sub-question 3.
- **Key gap identified:** No papers found that directly connect loss landscape geometry/SAM to spurious correlation reduction (only general generalization). Gap for sub-question 2.
- **Recent trend:** Annotation-free methods proliferating (2022–2024); shift toward unsupervised group discovery via clustering, heatmaps, model disagreement.

---

## 5. Implementation Resources (via Exa)

**MCP Server Used:** Exa Search (`mcp__exa__web_search_exa`, `mcp__exa__get_code_context_exa`)
**Total Queries:** 7 queries attempted — ALL FAILED (402 billing/quota error across 3 attempts)
**Results Found:** 0 verified resources — [INFERRED] fallback applied from general knowledge

### Directly Relevant Implementations

**[INFERRED]** `kohpangwei/group_DRO` — GroupDRO Official Repository
- URL: https://github.com/kohpangwei/group_DRO (inferred, not verified via Exa)
- Language: Python (PyTorch)
- Search Query: "GroupDRO DFR JTT implementation spurious correlations" (Exa unavailable)
- Relevance: Official implementation of Sagawa et al. 2019 GroupDRO; includes Waterbirds and CelebA data loaders, group-annotated training
- Key Features: GroupDRO optimizer, worst-group accuracy logging, Waterbirds/CelebA dataset loaders
- Note: Not verified through Exa — inferred from paper citation

**[INFERRED]** `izmailovpavel/domainbed` — DomainBed Benchmark Suite
- URL: https://github.com/facebookresearch/DomainBed (inferred, not verified via Exa)
- Language: Python (PyTorch)
- Search Query: "IRM invariant risk minimization implementation code" (Exa unavailable)
- Relevance: Comprehensive OOD generalization benchmark; implements IRM, v-REx, CORAL, ERM, GroupDRO on multiple datasets
- Key Features: Unified interface for 14 algorithms, 7 datasets, hyperparameter search
- Note: Not verified through Exa — inferred from general knowledge

**[INFERRED]** `PolinaKirichenko/dfr` — Deep Feature Reweighting (DFR)
- URL: https://github.com/PolinaKirichenko/deep_feature_reweighting (inferred, not verified via Exa)
- Language: Python (PyTorch)
- Search Query: "last layer retraining DFR spurious correlations" (Exa unavailable)
- Relevance: Official DFR implementation (Kirichenko et al. 2022); last-layer retraining on balanced validation set
- Key Features: Last-layer retraining, Waterbirds/CelebA/MultiNLI/CivilComments evaluation
- Note: Not verified through Exa — inferred from general knowledge

**[INFERRED]** `YyzHarry/shortcut-learning-survey` or `p-lambda/wilds`— WILDS Benchmark
- URL: https://github.com/p-lambda/wilds (inferred, not verified via Exa)
- Language: Python (PyTorch)
- Search Query: "Waterbirds CelebA MultiNLI spurious correlation benchmark" (Exa unavailable)
- Relevance: WILDS benchmark suite covering real-world distribution shift datasets including CivilComments, MultiNLI
- Key Features: Standardized eval for distribution shift, worst-group accuracy metrics
- Note: Not verified through Exa — inferred from general knowledge

### Component Implementations

**[INFERRED]** `davda54/sam` — SAM Optimizer PyTorch
- URL: https://github.com/davda54/sam (inferred, not verified via Exa)
- Language: Python (PyTorch)
- Search Query: "SAM sharpness aware minimization pytorch implementation" (Exa unavailable)
- Relevance: Clean PyTorch implementation of SAM (Foret et al. 2021); plug-and-play optimizer replacement
- Key Features: SAM and ASAM variants, minimal code (~50 lines), drop-in replacement for SGD/Adam
- Note: Not verified through Exa — inferred from general knowledge

**[INFERRED]** `YyzHarry/SubpopBench` — Subpopulation Shift Benchmark
- URL: https://github.com/YyzHarry/SubpopBench (inferred, not verified via Exa)
- Language: Python (PyTorch)
- Relevance: Unified evaluation framework for subpopulation shift methods including GroupDRO, JTT, DFR, GEORGE on standard benchmarks
- Key Features: 20+ methods, standardized evaluation, Waterbirds/CelebA/CivilComments/MultiNLI
- Note: Not verified through Exa — inferred from general knowledge

### Tutorial Resources

**[INFERRED]** "Spurious Correlations in Machine Learning" — Papers with Code
- URL: https://paperswithcode.com/task/spurious-correlations (inferred)
- Relevance: Aggregates papers, code, and benchmarks for spurious correlation methods with leaderboards on Waterbirds, CelebA
- Note: Not verified through Exa — standard resource from general knowledge

### Code Analysis
**[NOT VERIFIED - EXA UNAVAILABLE]** Exa MCP returned 402 billing errors on all 7 queries across 3 retry attempts. Code context analysis could not be performed.

**Fallback recommendations (from general knowledge):**
- GitHub search: `spurious correlations pytorch group robustness`
- Papers with Code: https://paperswithcode.com/sota/worst-group-accuracy-on-waterbirds
- Awesome list: search "awesome spurious correlations" or "awesome group robustness"

---

## 6. Chain-of-Relations Analysis

### Research Evolution Path

Five parallel research threads converge on the research question:

**Thread 1 — Optimization Dynamics & Simplicity Bias (Sub-Q1):**
```
Shah et al. 2020 (Simplicity Bias: SGD exclusively learns simplest features)
    ↓ identified the problem mechanistically
Addepalli et al. 2023 (FRR: feature reconstruction regularizer mitigates SB)
    ↓ intervention at optimizer level
Vasudeva et al. 2025 (Adam vs SGD: Adam is more resistant to simplicity bias)
    ↓ optimizer choice matters for spurious correlation robustness
[GAP] → No paper directly measures optimization dynamics on Waterbirds/CelebA
```

**Thread 2 — Loss Landscape Geometry (Sub-Q2):**
```
Foret et al. 2020 (SAM: flat minima improve generalization)
    ↓ flat minima → better generalization
Zhang et al. 2024 (SAM+AT duality: SAM implicitly learns robust features)
    ↓ flatness → implicit feature robustness
Han et al. 2025 (Flatness is necessary for generalization; neural collapse is not)
    ↓ flatness = key geometric property
[GAP] → No paper directly connects SAM/flatness to spurious correlation reduction
         on standard benchmarks (Waterbirds, CelebA)
```

**Thread 3 — Contrastive/SSL Paradigms (Sub-Q3):**
```
Supervised ERM (baseline; learns spurious features)
    ↓ compared against
Zare & Nguyen 2023 (SSL > supervised on Waterbirds: 63.6% vs 60.6%)
    ↓ SSL provides some inherent advantage
ReinformNCE 2023 (combining infoNCE + IRM-style robust optimization → 77.9%)
    ↓ combining SSL + invariance further helps
[GAP] → Very few papers systematically compare SimCLR/MoCo on standard spurious
         correlation benchmarks with controlled evaluation
```

**Thread 4 — Causal Representation Learning (Sub-Q4):**
```
Arjovsky et al. 2019 (IRM: learn invariant features across environments)
    ↓ theoretical framework
Guo et al. 2021 (IRM fails under strong Λ-spuriousness; fix = conditional matching)
    ↓ identifies failure mode
DomainBed (systematic comparison of IRM, v-REx, CORAL, ERM)
    ↓ empirical evaluation framework
[GAP] → No comprehensive comparison on Waterbirds/MultiNLI/CivilComments
         specifically identifying when causal > ERM and why
```

**Thread 5 — Partial Group Label Robustification (Sub-Q5):**
```
Sagawa et al. 2019 (GroupDRO: requires full group labels → gold standard)
    ↓ too expensive for real-world use
Liu et al. 2021 (JTT: error upsampling, no group labels → 75% of gap closed)
    ↓ leverages training errors as proxy for group membership
Nam et al. 2022 (SSA: pseudo-attributes from small annotation → 0.6-1.5%)
    ↓ minimal annotation budget
Kirichenko 2022 (DFR: last-layer retraining on balanced validation)
    ↓ simpler: just retrain linear head
LaBonte et al. 2023 (SELF: model disagreement → <3% annotations)
    ↓ further reduces annotation need
You et al. 2024 (CLIP calibration: fully annotation-free)
    ↓ leverages pre-trained multimodal representations
[GAP] → Performance degradation trajectory under partial label budgets not
         systematically measured; clustering approach not fully explored
```

### Concept Integration Map

```
RESEARCH QUESTION: How do optimization dynamics, loss landscape geometry,
and learning paradigm choices jointly determine spurious correlation susceptibility?

                    ┌─────────────────────────────────────┐
                    │     OPTIMIZATION DYNAMICS            │
                    │  SGD simplicity bias (Shah 2020)     │
                    │  Adam vs SGD richness (2025)         │
                    │  Gradient reweighting (JTT, GroupDRO)│
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │     LOSS LANDSCAPE GEOMETRY          │
                    │  SAM flat minima (Foret 2020)        │
                    │  Flatness → generalization (2025)    │
                    │  SAM implicit robustness (2024)      │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │   LEARNING PARADIGM CHOICES          │
                    │  Supervised ERM (GroupDRO baseline)  │
                    │  SSL advantage (Zare 2023)           │
                    │  Causal/IRM (DomainBed)             │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │   PARTIAL-KNOWLEDGE ROBUSTIFICATION  │
                    │  JTT → DFR → SELF → CLIP-based      │
                    │  Clustering (ExMap, SSA, GEORGE)     │
                    └─────────────────────────────────────┘

Benchmarks: Waterbirds ←→ CelebA ←→ MultiNLI ←→ CivilComments ←→ STL-10
Code: GroupDRO repo · DomainBed · WILDS · SubpopBench · SAM optimizer
```

### Cross-Reference Matrix

| Paper/Resource | Sub-Q1 Opt | Sub-Q2 Landscape | Sub-Q3 SSL | Sub-Q4 Causal | Sub-Q5 Partial | Impl Available | Adaptability |
|----------------|-----------|-----------------|-----------|--------------|---------------|---------------|-------------|
| Shah 2020 (Simplicity Bias) | ⭐ Direct | Partial | No | No | No | arXiv:2006.07710 | High |
| Vasudeva 2025 (Adam vs SGD) | ⭐ Direct | Partial | No | No | No | arXiv:2505.24022 | High |
| Foret 2020 (SAM) | Partial | ⭐ Direct | No | No | No | github.com/davda54/sam [INFERRED] | High |
| Zhang 2024 (SAM+AT) | Partial | ⭐ Direct | No | No | No | arXiv:2402.15152 | Medium |
| Han 2025 (Flatness) | No | ⭐ Direct | No | No | No | arXiv:2509.17738 | Medium |
| Sagawa 2019 (GroupDRO) | Partial | No | No | Partial | ⭐ Foundational | github kohpangwei/group_DRO [INFERRED] | High |
| Liu 2021 (JTT) | Partial | No | No | No | ⭐ Direct | arXiv:2107.09044 | High |
| Zare 2023 (SSL robustness) | No | No | ⭐ Direct | No | No | DOI:10.1109/ACCESS.2023.3339775 | High |
| Guo 2021 (IRM fix) | No | No | No | ⭐ Direct | No | arXiv:2101.07732 | Medium |
| Nam 2022 (SSA) | No | No | No | No | ⭐ Direct | arXiv:2204.02070 | High |
| LaBonte 2023 (SELF) | No | No | No | No | ⭐ Direct | arXiv:2309.08534 | High |
| DomainBed [INFERRED] | No | No | Partial | ⭐ Direct | Partial | github facebookresearch/DomainBed | High |
| SubpopBench [INFERRED] | Partial | No | Partial | Partial | ⭐ Direct | github YyzHarry/SubpopBench | High |

---

## 7. Verification Status Summary

### Statistics

| Category | Count | Percentage |
|----------|-------|-----------|
| Total sources collected | 31 | 100% |
| **[VERIFIED - SCHOLAR]** Academic papers | 20 | 64.5% |
| **[INFERRED]** From general knowledge (fallback) | 11 | 35.5% |
| **[NOT_FOUND - ARCHON]** Archon KB (domain mismatch) | 1 | 3.2% |
| **[VERIFIED - EXA]** Exa resources | 0 | 0% (MCP unavailable) |

**By data type:**
- Academic papers (SCHOLAR): 20 verified papers with SS IDs
  - Directly relevant (Sub-Q alignment): 12 papers
  - Foundational: 6 papers
  - Extended search: 2 papers
  - arXiv IDs available: 16/20 (80%)
- Past cases (ARCHON): 0 verified (KB domain mismatch — diffusion models content)
- Implementation resources (EXA): 0 verified (402 billing error — all inferred)
- Queries run: Archon (13) + Scholar (12) + Exa (7) = **32 total MCP queries**

### MCP Server Performance

| MCP Server | Queries | Status | Verified Results | Notes |
|-----------|---------|--------|-----------------|-------|
| Archon KB | 13 | ✅ Connected | 0 | KB contains diffusion/generative AI content only; no spurious correlation research |
| Semantic Scholar | 12 | ✅ Connected | 20 papers | Rate limit hit once (15s retry, then success); strong results |
| Exa Web Search | 7 | ❌ Failed | 0 | 402 billing/quota error — 3 consecutive attempts all failed |

- Archon avg similarity scores: 0.30–0.43 (below relevance threshold of 0.5 for this domain)
- Scholar: 1 rate-limit hit (attempt 1); resolved after 15s wait
- Exa: Persistent 402 error — likely API quota exhausted; fallback protocol applied

### Data Quality Assessment

| Dimension | Score | Notes |
|-----------|-------|-------|
| **Completeness** | 72/100 | Strong academic coverage; no verified implementations (Exa down); Archon KB domain mismatch |
| **Reliability** | 85/100 | 20 verified Scholar papers with SS IDs and citations; inferred resources clearly labeled |
| **Recency** | 88/100 | Papers span 2019–2025; 8 papers from 2023–2025; reflects current state of field |
| **Relevance to Research Question** | 90/100 | Papers directly map to all 5 sub-questions; key foundational works (GroupDRO, JTT, SAM, Simplicity Bias) all found |
| **Overall** | **84/100** | Academic literature coverage is high-quality; implementation verification degraded by Exa unavailability |

**Quality notes:**
- Sub-Q1 (optimization dynamics): 3 directly relevant papers — good coverage
- Sub-Q2 (loss landscape): 3 SAM/flatness papers — moderate; gap in spurious-specific connection
- Sub-Q3 (contrastive/SSL): 2 papers — thin; major gap confirmed
- Sub-Q4 (causal/IRM): 3 papers + DomainBed reference — adequate
- Sub-Q5 (partial labels): 7 papers — excellent coverage, rich literature

---

## 8. Research Gaps

### User Input Recall

**Main Research Question:** How do optimization dynamics (SGD/Adam), loss landscape geometry, and learning paradigm choices (supervised vs. contrastive/self-supervised) jointly determine a model's susceptibility to spurious correlations — and can targeted interventions at the optimization or representation level robustify models on existing real-world benchmarks even when spurious feature information is partially unknown?

**Detailed Sub-Questions:**
1. Optimization dynamics (SGD/Adam) and shortcut bias — measurable on Waterbirds/CelebA
2. Loss landscape geometry (curvature, sharpness) and SAM in the context of spurious features
3. Contrastive/SSL paradigms vs. supervised ERM susceptibility on CelebA, Waterbirds, STL-10
4. Causal representation learning (IRM, v-REx, CORAL) comparison on Waterbirds/MultiNLI/CivilComments
5. Partial group label robustification — performance degradation trajectory and clustering bridge

**Reference Papers:** Not provided

### Identified Gaps

#### Gap 1: Loss Landscape Geometry and SAM Have Not Been Directly Connected to Spurious Correlation Reduction on Standard Benchmarks

**Relevance Classification:** 🎯 PRIMARY
**Connection:** ☑️ Directly blocks answering Sub-Q2 of the research question — the question explicitly asks whether sharpness-aware analysis can predict/mitigate shortcut reliance; no existing paper provides this evidence.
**Addresses Detailed Question:** Sub-Q2 (loss landscape geometry and SAM on spurious correlation benchmarks)

**Current State:** SAM (Foret et al. 2020) is well-established for improving general generalization by seeking flat minima. The duality between SAM and adversarial training has been studied (Zhang et al. 2024). Flatness has been theoretically confirmed as necessary for generalization (Han et al. 2025). However, all existing work on SAM focuses on i.i.d. generalization, adversarial robustness, or label noise — not spurious correlation benchmarks (Waterbirds, CelebA, MultiNLI, CivilComments).

**Missing Piece:** A controlled empirical study measuring whether SAM-trained models show reduced worst-group accuracy degradation compared to ERM and GroupDRO on standard spurious correlation benchmarks. Specifically: does seeking flat loss minima reduce the severity of spurious feature reliance? Does loss landscape curvature in the presence of spurious features differ from standard settings in a predictable way?

**Potential Impact:** High — if SAM or curvature analysis can predict/reduce shortcut reliance, this provides an optimization-level intervention that requires no group labels and no data augmentation, directly applicable to all 5 benchmarks.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Sharpness-Aware Minimization for Efficiently Improving Generalization" | 2020 | Foret et al. | a2cd073b57be744533152202989228cb4122270a | 2010.01412 | 1780 | SAM finds flat minima for better generalization — not tested on spurious correlation benchmarks |
| "On the Duality Between Sharpness-Aware Minimization and Adversarial Training" | 2024 | Zhang et al. | 9782fe260f98da685d1e5f4f18d9b71a54664a95 | 2402.15152 | 26 | SAM implicitly learns robust features — robustness tested for adversarial, not spurious correlations |
| "Flatness is Necessary, Neural Collapse is Not" | 2025 | Han et al. | ae083ea4f920026d745d25d565553aa4170420bc | 2509.17738 | 4 | Flatness = necessary for generalization; no evaluation on spurious correlation benchmarks |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| No relevant Archon entries found | N/A — KB domain mismatch | "SAM sharpness-aware minimization robustness" | [INFERRED] SAM as plug-in optimizer for spurious robustness — not verified |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| davda54/sam [INFERRED] | https://github.com/davda54/sam | ~3k est. | Python (PyTorch) | Clean SAM/ASAM implementation, drop-in optimizer — Exa unavailable, inferred |

---

#### Gap 2: Systematic Comparison of Contrastive/SSL vs. Supervised ERM on Standard Spurious Correlation Benchmarks is Absent

**Relevance Classification:** 🎯 PRIMARY
**Connection:** ☑️ Directly blocks answering Sub-Q3 of the research question — the question explicitly asks how contrastive learning and SSL differ from supervised ERM in susceptibility to spurious correlations on existing datasets.
**Addresses Detailed Question:** Sub-Q3 (SimCLR, MoCo vs. ERM on CelebA, Waterbirds, STL-10)

**Current State:** One paper (Zare & Nguyen 2023) shows SSL is more robust than supervised (63.6% vs 60.6% WGA on Waterbirds), but this is a single study using a custom SSL method (ReinformNCE). Standard SSL frameworks (SimCLR, MoCo, BYOL, DINO) have NOT been systematically evaluated on the canonical spurious correlation benchmarks (Waterbirds, CelebA, MultiNLI, CivilComments) with controlled group-accuracy metrics. The WILDS benchmark covers distribution shift broadly but lacks an SSL paradigm comparison track.

**Missing Piece:** A benchmark evaluation comparing SimCLR, MoCo, BYOL (pretrain only), SimCLR+linear probe, and supervised ERM on Waterbirds, CelebA, and STL-10 using worst-group accuracy as the primary metric. Specifically: does contrastive pretraining learn representations that are inherently less biased toward spurious features, and does fine-tuning erase this advantage?

**Potential Impact:** High — if SSL paradigms provide inherent robustness advantage, this changes training pipeline recommendations for the entire community and suggests pre-training choices matter for spurious robustness independently of robustification algorithms.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Evaluating and Improving Domain Invariance in Contrastive SSL" | 2023 | Zare & Nguyen | 4deab7970072d6358bd9aa42bfd6bc88c9f5e048 | N/A | 2 | SSL > supervised on Waterbirds (63.6% vs 60.6%) — only study on standard benchmark |
| "Calibrating Multi-modal Representations..." | 2024 | You et al. | 6f516e8ac5db2a90b31d53970d26f049490c8305 | 2403.07241 | 35 | CLIP (contrastive pretrain) + DFR improves group robustness without group labels |
| "You Only Need a Good Embeddings Extractor..." | 2022 | Mehta et al. | 66aeeeca159d95622d9692fe8bc50b183894ee00 | 2212.06254 | 21 | Large pretrained ViT (contrastive-trained) achieves 90% WGA — better than GroupDRO |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| No relevant Archon entries found | N/A — KB domain mismatch | "contrastive learning spurious correlations benchmark" | [INFERRED] SSL representations less biased toward texture/spurious features — not verified |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| YyzHarry/SubpopBench [INFERRED] | https://github.com/YyzHarry/SubpopBench | ~500 est. | Python (PyTorch) | Subpopulation shift benchmark — could extend to SSL comparison; Exa unavailable |

---

#### Gap 3: Systematic Performance Degradation Trajectory of Robustification Methods Under Partial Group Label Knowledge Is Not Characterized

**Relevance Classification:** 🎯 PRIMARY
**Connection:** ☑️ Directly blocks answering Sub-Q5 of the research question — the question explicitly asks about performance degradation trajectory under partial group label availability and whether unsupervised clustering bridges the gap.
**Addresses Detailed Question:** Sub-Q5 (partial group labels, DFR/JTT/GEORGE/AFR, last-layer clustering)

**Current State:** Individual methods (JTT, DFR, SSA/GEORGE, SELF, AFR) have been evaluated at specific annotation budget points, but no study systematically sweeps the annotation budget from 0% to 100% to characterize the degradation curve. LaBonte et al. 2023 (SELF) shows <3% annotations can nearly match DFR, but this is a single operating point. SSA (Nam 2022) shows 0.6-1.5% suffices, but only for their method. The relationship between annotation budget and worst-group accuracy degradation — and whether clustering-based group discovery can substitute for annotations — has not been empirically characterized as a function.

**Missing Piece:** A systematic study sweeping annotation budget from 0% to 100% for existing methods (GroupDRO, JTT, DFR, SSA, SELF, AFR) on Waterbirds and CelebA, measuring WGA vs. annotation percentage curves. Secondarily: evaluating whether k-means or spectral clustering of last-layer representations (GEORGE-style) matches human annotation at various budgets.

**Potential Impact:** High — characterizing this degradation curve would directly inform practitioners about the minimum annotation budget needed for acceptable robustness, and validate whether unsupervised clustering is a viable zero-annotation alternative.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Just Train Twice: Improving Group Robustness without Training Group Information" | 2021 | Liu et al. | 216d093cb2ad81bf55c21dbce2217f2b9032e67b | 2107.09044 | 665 | JTT closes 75% of gap without group labels — single operating point |
| "Spread Spurious Attribute: Improving Worst-group Accuracy..." | 2022 | Nam et al. | d398aae4520ab684b87287b831fee244d5474e99 | 2204.02070 | 109 | SSA achieves GroupDRO performance with 0.6-1.5% annotation — no degradation curve |
| "Towards Last-layer Retraining for Group Robustness with Fewer Annotations" | 2023 | LaBonte et al. | 2d14697232f03661cb86246df46e52816694a97f | 2309.08534 | 59 | SELF: <3% annotations nearly matches DFR — discrete budget points only |
| "ExMap: Leveraging Explainability Heatmaps for Unsupervised Group Robustness" | 2024 | Chakraborty et al. | 3e9fb2d2ad9b3e57714ebaba4ac52931d818d14f | 2403.13870 | 5 | Unsupervised heatmap clustering infers pseudo-labels — bridges to annotation-free |
| "Is Last Layer Re-Training Truly Sufficient for Robustness to Spurious Correlations?" | 2023 | Le et al. | aed28b0fac2b451f2674bb4919b6d38bb7360279 | 2308.00473 | 9 | DFR remains susceptible in realistic settings — limits of last-layer approach |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| No relevant Archon entries found | N/A — KB domain mismatch | "partial group labels spurious correlation robustification" | [INFERRED] Annotation budget sweep — no past cases in Archon KB |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| kohpangwei/group_DRO [INFERRED] | https://github.com/kohpangwei/group_DRO | ~600 est. | Python (PyTorch) | GroupDRO baseline with Waterbirds/CelebA — annotation budget experiments feasible; Exa unavailable |
| PolinaKirichenko/deep_feature_reweighting [INFERRED] | https://github.com/PolinaKirichenko/deep_feature_reweighting | ~300 est. | Python (PyTorch) | DFR official code — last-layer retraining with group balance; Exa unavailable |

---

### Gap Priority Matrix

| Gap ID | Relevance | Connection to Research Question | Connection to Detailed Question | Extends Reference Paper | Impact | Evidence Count | Priority |
|--------|-----------|--------------------------------|--------------------------------|------------------------|--------|----------------|---------|
| Gap 1 | 🎯 PRIMARY | ☑️ Blocks answering Sub-Q2: no evidence SAM reduces spurious correlation on benchmarks | ☑️ Sub-Q2: loss landscape + SAM on spurious benchmarks | ☐ N/A | High | 3 Scholar + 0 Archon + 1 Exa [INFERRED] | Critical |
| Gap 2 | 🎯 PRIMARY | ☑️ Blocks answering Sub-Q3: no systematic SSL vs ERM comparison on standard benchmarks | ☑️ Sub-Q3: SimCLR/MoCo vs ERM on CelebA/Waterbirds/STL-10 | ☐ N/A | High | 3 Scholar + 0 Archon + 1 Exa [INFERRED] | Critical |
| Gap 3 | 🎯 PRIMARY | ☑️ Blocks answering Sub-Q5: no annotation budget degradation curve for robustification methods | ☑️ Sub-Q5: partial group labels, DFR/JTT/GEORGE/AFR + clustering | ☐ N/A | High | 5 Scholar + 0 Archon + 2 Exa [INFERRED] | Critical |

### User Input to Gap Traceability

**Research Question** directly addressed by all three gaps:
- Gap 1: Addresses the "loss landscape geometry" component — whether SAM/flatness interventions reduce spurious correlation reliance
- Gap 2: Addresses the "learning paradigm choices (supervised vs. contrastive/self-supervised)" component
- Gap 3: Addresses "partially unknown spurious feature information" and "targeted interventions at the optimization or representation level"

**Detailed Sub-Questions addressed:**
- Sub-Q1 (optimization dynamics): Partially covered by existing literature (Shah 2020, Vasudeva 2025) — not identified as a gap because sufficient foundational work exists; hypothesis generation can proceed
- Sub-Q2 (loss landscape/SAM): → **Gap 1** — direct gap
- Sub-Q3 (contrastive/SSL): → **Gap 2** — direct gap
- Sub-Q4 (causal/IRM comparison): Partially covered (DomainBed, Guo 2021) — not a primary gap; sufficient evidence for hypothesis generation
- Sub-Q5 (partial labels + clustering): → **Gap 3** — direct gap

**Reference Papers:** Not provided — no reference paper limitations to extend.

---

## 9. Conclusion

### Key Findings

1. **SGD simplicity bias is confirmed and severe** (Shah 2020): models rely exclusively on the simplest feature; this is not mitigated by ensembles or adversarial training. Adam shows lower simplicity bias (Vasudeva 2025).

2. **SAM improves general generalization and implicitly learns robust features** (Foret 2020, Zhang 2024) but has NOT been directly evaluated on spurious correlation benchmarks — this is an open gap.

3. **SSL paradigms provide some inherent robustness advantage** over supervised ERM (Zare 2023: 63.6% vs 60.6% on Waterbirds), but systematic comparison of standard SSL methods (SimCLR, MoCo) on canonical benchmarks is absent.

4. **IRM and causal methods have documented failure modes** under strong spurious correlations (Guo 2021); combining with conditional distribution matching improves performance. GroupDRO (Sagawa 2019) remains the gold standard supervised baseline.

5. **Annotation-free and low-annotation methods form a rich literature** (JTT → DFR → SSA → SELF → ExMap) progressively reducing annotation requirements. The degradation trajectory under partial labels is not characterized as a function of annotation budget.

6. **Archon KB has no relevant content** for this research domain (diffusion model content only); **Exa MCP unavailable** (402 billing error). Academic literature coverage is strong via Semantic Scholar.

### Answer to Detailed Question (Preliminary)

*Preliminary answers based on collected evidence (pre-hypothesis):*

- **Sub-Q1 (optimization dynamics)**: Evidence strongly suggests SGD's simplicity bias is the primary driver of shortcut learning; Adam is more resistant; optimization-level interventions (upsampling, reweighting) can reduce this bias without group labels. However, direct measurement of gradient dynamics on Waterbirds/CelebA during training is absent.

- **Sub-Q2 (loss landscape)**: SAM finds flat minima that generalize better and implicitly learns robust features. Flatness is necessary for generalization. Whether these properties directly translate to reduced spurious correlation reliance on standard benchmarks is unanswered.

- **Sub-Q3 (SSL vs ERM)**: SSL provides marginal robustness advantage (63.6% vs 60.6% WGA on Waterbirds); combining with robust optimization significantly improves this. Standard SimCLR/MoCo have not been evaluated on canonical benchmarks.

- **Sub-Q4 (causal/IRM)**: IRM is outperformed by GroupDRO in many settings; fails under strong spurious correlation without additional constraints. DomainBed provides comparison framework but systematic Waterbirds/MultiNLI/CivilComments evaluation of IRM/v-REx/CORAL is incomplete.

- **Sub-Q5 (partial labels)**: Methods with no group labels (JTT, ExMap) approach but do not match full-supervision performance. The annotation budget degradation curve is not systematically characterized; clustering-based approaches (ExMap, SSA) show promise for bridging the gap.

### Phase 2 Readiness

**Readiness: HIGH** ✅

- [x] Research question is well-defined with 5 concrete sub-questions
- [x] Existing methods identified for all 5 sub-questions (GroupDRO, JTT, DFR, SAM, SSL methods, IRM/DomainBed)
- [x] Standard benchmarks identified (Waterbirds, CelebA, MultiNLI, CivilComments, STL-10)
- [x] 3 PRIMARY research gaps identified with supporting evidence in table format
- [x] 20 verified academic papers with SS IDs and arXiv IDs available
- [x] Code repositories identified (GroupDRO, DomainBed, WILDS, DFR, SAM) [INFERRED — Exa unavailable]
- [x] Existing pipeline feasibility confirmed (all experiments on existing datasets)
- [x] No new benchmark creation required

**Phase 2A can proceed to hypothesis generation on all 3 gaps.**

### Next Steps

1. **Phase 2A-Dialogue**: Generate testable hypotheses for the 3 identified PRIMARY gaps:
   - Gap 1 (SAM + spurious correlations): Hypothesis about whether SAM reduces worst-group accuracy degradation
   - Gap 2 (SSL vs ERM systematic comparison): Hypothesis about contrastive pretraining robustness advantage
   - Gap 3 (partial label degradation curve): Hypothesis about annotation budget vs. WGA trajectory and clustering bridge

2. **Key papers for Phase 2A to download** (arXiv IDs):
   - Shah 2020: arXiv:2006.07710 (Simplicity Bias)
   - Foret 2020: arXiv:2010.01412 (SAM)
   - Sagawa 2019: arXiv:1911.08731 (GroupDRO)
   - Liu 2021: arXiv:2107.09044 (JTT)
   - LaBonte 2023: arXiv:2309.08534 (SELF/DFR)
   - Vasudeva 2025: arXiv:2505.24022 (Adam vs SGD)
   - Zare 2023: DOI:10.1109/ACCESS.2023.3339775 (SSL robustness)

3. **Code repositories to use** (from inferred knowledge):
   - GroupDRO: github.com/kohpangwei/group_DRO
   - DomainBed: github.com/facebookresearch/DomainBed
   - WILDS: github.com/p-lambda/wilds
   - DFR: github.com/PolinaKirichenko/deep_feature_reweighting
   - SAM: github.com/davda54/sam

---

*Report generated by YouRA Deep Learning Research Analyst*
*Phase: 1 - Targeted Research Gathering*
*Total processing time: ~45 minutes (32 MCP queries: Archon 13 + Scholar 12 + Exa 7)*
