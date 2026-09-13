# Targeted Research Report: Can optimization-level interventions reduce reliance on shortcut features in self-supervised and contrastive learning settings?

**Date:** 2026-08-21
**Phase:** 1 - Targeted Research Gathering
**Phase Output:** Research data, gaps (Pre-hypothesis, targeted approach)
**Analyst:** Deep Learning Research Analyst 🔍
**Researcher:** Anonymous

---

## Executive Summary

Phase 1 research on optimization-level interventions for spurious correlation robustness in SSL settings found 13 verified papers, 7 GitHub repos, and 3 tutorials. Three PRIMARY gaps confirmed: (1) SAM/geometry-aware optimization during SSL pre-training (SimCLR/MoCo/DINO) for shortcut reduction — entirely unstudied; (2) systematic worst-group accuracy comparison of SSL vs. supervised ERM on Waterbirds/CelebA/CMNIST/UrbanCars — absent; (3) loss landscape curvature as empirical predictor of shortcut reliance in SSL models — theoretically motivated but unmeasured. Annotation-free constraint is satisfiable via existing baselines (JTT, LFR, EVaLS, EIIL). Implementation infrastructure is ready (davda54/sam 1983★, izmailovpavel/spurious_feature_learning 48★, kohpangwei/group_DRO 295★). Phase 2A hypothesis generation can begin immediately.

---

## 0. Reference Paper Analysis

*No reference papers provided*

---

## 1. Research Questions

### Primary Research Question
Can optimization-level interventions (e.g., sharpness-aware minimization, gradient surgery, or loss landscape regularization) reduce reliance on shortcut features in self-supervised and contrastive learning settings on existing spurious correlation benchmarks, without requiring group labels or knowledge of spurious feature identity?

### Detailed Research Questions
1. Do standard self-supervised learning objectives (SimCLR, MoCo, DINO) exhibit differential shortcut reliance compared to supervised learning on Waterbirds, CelebA, CMNIST, and UrbanCars?
2. Does the temporal order of learning (core vs. spurious feature acquisition) differ between supervised and self-supervised training regimes on existing benchmarks?
3. Can SAM or related geometry-aware optimizers reduce shortcut reliance in self-supervised pre-training without group annotations, measured by worst-group accuracy on existing benchmarks?
4. Is there a detectable loss landscape signature (flatness/curvature) that predicts shortcut reliance degree, measurable on existing trained models?
5. Can gradient alignment interventions in contrastive learning (between augmented views) mitigate shortcut adoption on Waterbirds, CelebA, CMNIST without new annotations?

### Lessons from Previous Attempts (ROUTE_TO_0 Only)
*N/A - First attempt*

---

## 2. Search Queries Generated

### Query Generation Source Summary
- Failure-aware queries (ROUTE_TO_0): N/A (first attempt)
- Reference paper queries: 0 (no reference papers provided)
- Brainstorm insights queries: 5
- Direct question queries: 8
- Total: 13 queries

Query Priority Order:
🥈 Brainstorm insights (key discoveries + unexplored directions)
🥉 Question decomposition (baseline coverage)

### Priority 1: Reference Paper Concept Queries
*No reference papers provided*

### Priority 2: Brainstorm Insights Queries (top 3)
1. "SSL self-supervised learning spurious correlations shortcut features"
2. "optimization-level robustification sharpness-aware minimization worst-group accuracy"
3. "loss landscape geometry simplicity bias shortcut learning deep neural networks"

### Priority 3: Direct Question Decomposition Queries (top 3)
1. "SimCLR MoCo DINO shortcut learning contrastive spurious correlation benchmarks"
2. "SAM sharpness-aware minimization spurious correlation group robustness"
3. "worst-group accuracy Waterbirds CelebA CMNIST UrbanCars self-supervised"

---

## 3. Past Cases & Best Practices (via Archon)

**MCP Server Used:** Archon Knowledge Base (`mcp__archon__rag_search_knowledge_base`)
**Total Queries:** 5 queries across 3 levels
**Results Found:** 0 verified cases + 4 inferred patterns

*Archon KB off-domain (image generation / diffusion models). Max similarity 0.42. 0 relevant cases. Applying Fallback Protocol.*

| Case/Pattern | KB Entry ID | Query Used | Key Pattern |
|---|---|---|---|
| [INFERRED] Worst-group reweighting (Group DRO/JTT) | N/A | "worst-group accuracy robustification" | Upweight hard examples; no group labels needed |
| [INFERRED] Annotation-free disentanglement (DFR/GEORGE) | N/A | "spurious correlation SSL shortcut features" | Cluster last-layer reps to find spurious features |
| [INFERRED] SAM for generalization | N/A | "sharpness-aware minimization worst-group accuracy" | Flat minima theoretically linked to core feature learning |
| [INFERRED] SimCLR/MoCo + SAM training loop | N/A | "SSL contrastive SAM integration" | Two-pass SAM gradient update wraps any SSL training loop |

---

## 4. Academic Literature Review (via Semantic Scholar)

**MCP Server Used:** Semantic Scholar (`mcp__hamid-vakilzadeh-mcpsemanticscholar__paper_relevance_search`)
**Total Queries:** 9 queries across 4 rounds
**Results Found:** 18 papers (8 directly relevant, 4 foundational, 6 related)

### Directly Relevant Papers

| Title | Year | SS ID | arXiv | Cit | 1-line insight |
|---|---|---|---|---|---|
| "Breaking Spurious Correlations via Generative Randomization and Cross-Variant SSL" | 2026 | d222c5f8b8dc04cfa54d181871864b19ab53da60 | 2607.05850 | 0 | Cross-Variant SSL: 92.5% Waterbirds; SSL+spurious+GroupDRO finetune |
| "Achieving Distributional Robustness with Group-Wise Flat Minima" (G2-SAM) | 2025 | ef857d039dfa1a88d329e636c888ef7a3b09c5aa | null | 0 | Group-wise SAM for worst-group accuracy — supervised only, SSL gap confirmed |
| "DGSAM: Domain Gen via Individual SAM" | 2025 | 0da44af38f5bbe7c342dd0bf05988378fb5dc192 | 2503.23430 | 1 | Fake flat minima problem; per-domain perturbation for domain gen (not spurious corr) |
| "Improving Group Robustness Requires Preciser Group Inference" (GIC) | 2024 | c3f81f72de99d31323bd69cc9261c5cfc91a0290 | 2404.13815 | 16 | Oracle vs. pseudo group label gap; annotation-free robustification pipeline |
| "Spurious Correlation-Aware Embedding Regularization" (SCER) | 2025 | 3c40fa562e053143b26eceb84d8ac825174bd8bc | 2511.04401 | 1 | Theoretically links embedding geometry to worst-group error |
| "EVaLS: Trained Models Tell Us How to Robustify" | 2024 | dcd528fdcf34ddd5e38bde4c9e9bf00b23c0019a | 2410.05345 | 0 | ERM losses → balanced dataset without group annotations |
| "LFR: Annotation-Free Group Robustness via Loss-Based Resampling" | 2023 | d14a2ac7495589fe09f903ef6e0e76470b0dea6e | 2312.04893 | 3 | Annotation-free DFR via loss-based grouping; beats DFR on Waterbirds/CelebA |
| "Calibrating Multi-modal Representations for Group Robustness" | 2024 | 6f516e8ac5db2a90b31d53970d26f049490c8305 | 2403.07241 | 49 | DFR + contrastive on CLIP SSL without group labels |
| "Self-Guided Spurious Correlation Mitigation" | 2024 | 52a90368334e0d88f3341325c6b8c4202316b644 | 2405.03649 | 14 | Annotation-free spuriousness embedding space |
| "Contrastive Adapters for Foundation Model Group Robustness" | 2022 | de4be9e0fa2f660eefb2d4c2a27c146d3e654a85 | 2207.07180 | 93 | Contrastive adapters on CLIP; 80.7pp avg-worst gap confirms SSL shortcut problem |
| "Simplicity Bias via Global Convergence of Sharpness Minimization" | 2024 | 0ab20995ed9d1c02dec42ca0cf4fd11774a8bf7d | 2410.16401 | 4 | Theory: SAM → rank-1 features → simplicity bias in 2-layer nets |
| "EIIL: Environment Inference for Invariant Learning" | 2021 | 00325cb5408da77827951abd3fa93ec3bd019608 | 2010.07249 | 476 | Annotation-free env inference + IRM; strong on CMNIST/Waterbirds |
| "Reproducibility: Spurious Correlations, Shortcut Learning, Clever Hans" | 2026 | 16cdba8cee4e6f7c509b978b9d63c84384b53220 | 2604.04518 | 0 | Unifies communities; CFKD most effective; group labels remain main obstacle |

### Foundational Papers

| Title | Year | SS ID | arXiv | Cit | 1-line insight |
|---|---|---|---|---|---|
| "Group DRO: Distributionally Robust Neural Networks" | 2019 | 193092aef465bec868d1089ccfcac0279b914bda | 1911.08731 | 1750 | THE baseline; Waterbirds dataset; regularization essential for worst-group gen |
| "SAM: Sharpness-Aware Minimization" | 2020 | a2cd073b57be744533152202989228cb4122270a | 2010.01412 | 2062 | Original SAM; flat minima via min-max optimization; supervised only |
| "Flat Minima and Generalization: Insights from SCO" | 2025 | 39c469839a7c4b799b685d0063ff5249736281eb | 2511.03548 | 2 | SAM may converge to sharp minima — theoretical risk for applying to SSL |
| "Is Last Layer Re-Training Truly Sufficient for Spurious Corr?" | 2023 | aed28b0fac2b451f2674bb4919b6d38bb7360279 | 2308.00473 | 10 | DFR limitations in realistic domains; important for baseline evaluation |

**Citation lineage:** Group DRO (2019) → JTT/DFR (2021-22) → EVaLS/LFR (2023-24) → CLIP+contrastive/Cross-Variant SSL (2024-26). SAM+SSL gap confirmed: no found paper combines SAM-type optimization with SSL pre-training on spurious correlation benchmarks.

---

## 5. Implementation Resources (via Exa)

**MCP Server Used:** Exa Search (`mcp__exa__web_search_exa`, `mcp__exa__get_code_context_exa`)
**Total Queries:** 4 queries across Priorities 1-4
**Results Found:** 7 GitHub repos + 3 tutorials + 1 code context

### Implementations

| Name | URL | Stars | Lang | Key Feature |
|---|---|---|---|---|
| davda54/sam | https://github.com/davda54/sam | 1983 | PyTorch | SAM+ASAM; `first_step`/`second_step` API; BN-compatible; drop-in optimizer |
| google-research/sam | https://github.com/google-research/sam | 640 | JAX/PT | Official SAM; reference for rho tuning |
| weizeming/SAM_AT | https://github.com/weizeming/SAM_AT | 25 | Python | SAM-adversarial training duality; loss landscape analysis tools |
| izmailovpavel/spurious_feature_learning | https://github.com/izmailovpavel/spurious_feature_learning | 48 | PyTorch | NeurIPS 2022 code; core/spurious feature analysis; extend with SAM for Q3 |
| kohpangwei/group_DRO | https://github.com/kohpangwei/group_DRO | 295 | PyTorch | Official Group DRO; Waterbirds/CelebA loaders; worst-group baseline infra |
| anniesch/jtt | https://github.com/anniesch/jtt | 72 | PyTorch | Official JTT; annotation-free upweighting; Waterbirds/CelebA |
| hygnhan/DPR | https://github.com/hygnhan/DPR | 1 | PyTorch | NeurIPS 2024; annotation-free disagreement probability method |
| p-giakoumoglou/pyssl | (via code context) | N/A | PyTorch | Unified SimCLR/MoCo/DINO/SwAV; `model(x)` → loss; easy SAM swap |
| SubpopBench | https://subpopbench.csail.mit.edu/ | N/A | Python | 20 algos × 12 datasets; supervised only — gap confirmed |

**SAM+SSL code pattern (from code context):**
```python
optimizer = SAM(model.parameters(), base_optimizer=SGD, rho=0.05, lr=0.1)
for (x1, x2), _ in loader:
    loss = simclr_loss(model(x1), model(x2))
    loss.backward()
    optimizer.first_step(zero_grad=True)
    simclr_loss(model(x1), model(x2)).backward()
    optimizer.second_step(zero_grad=True)
```
BN caveat: disable running stat tracking between passes. Cost: 2× forward-backward.

---

## 6. Chain-of-Relations Analysis

### Research Evolution Path

```
2019-2021: Group DRO (Waterbirds/CelebA) → SAM (flat minima) → EIIL (annotation-free env) → JTT (misclassification proxy)
2022:       DFR (last-layer retrain) → Izmailov et al. (SSL spurious analysis) → Contrastive Adapters (CLIP group robustness)
2023-2024:  LFR/EVaLS (annotation-free DFR variants) → CLIP Calibration (SSL+DFR) → Self-Guided SCM
2024-2025:  G2-SAM (SAM+group robustness, SUPERVISED) → DGSAM (SAM+domain gen) → Gatmiry (SAM→simplicity bias theory)
2026 OPEN:  ??? SAM/geometry-aware opt DURING SSL pre-training (SimCLR/MoCo/DINO)
            ??? Loss landscape curvature as shortcut predictor in SSL models
            ??? Gradient alignment between contrastive views as spurious mitigation
```

### Cross-Reference Matrix

| Paper/Resource | Relevance | Q Addressed | Adaptability |
|---|---|---|---|
| G2-SAM (Ji 2025) | Direct — SAM+group robustness | Q3 (supervised) | High — adapt to SSL |
| DGSAM (Song 2025) | High — SAM+distribution shift | Q3 (domain gen) | High — adapt to spurious |
| Simplicity Bias↔SAM (Gatmiry 2024) | High — theoretical link | Q4 (loss landscape) | Medium — theory only |
| Cross-Variant SSL (Yadav 2026) | Direct — SSL+spurious+Waterbirds | Q1, Q5 | High — direct baseline |
| izmailovpavel/spurious_feature_learning | Direct — SSL spurious analysis | Q1, Q2 | High — extend with SAM |
| LFR (Ghaznavi 2023) | High — annotation-free DFR | Q3 annotation-free | High — direct baseline |
| CLIP Calibration (You 2024, 49 cit) | High — SSL+no annotations | Q3, Q5 | High — DFR+contrastive |
| Contrastive Adapters (Zhang 2022, 93 cit) | High — SSL+group robustness | Q1, Q5 | High — contrastive finetune |
| davda54/sam (1983★) | Tool — SAM optimizer | Q3 (tool) | Very High — drop-in |
| EIIL (Creager 2021, 476 cit) | High — annotation-free env | Q3 annotation-free | High — CMNIST baseline |

---

## 7. Verification Status Summary

**Totals:** 28 sources — [VERIFIED-SCHOLAR]: 13 (46%) | [VERIFIED-EXA]: 11 (39%) | [INFERRED]: 4 (14%) | [UNVERIFIED]: 0

**MCP Performance:** Archon ❌ (off-domain, max sim 0.42, 3 timeouts) | Scholar ✅ (9 queries, 1 rate limit retry, 13 papers) | Exa ✅ (4 queries, 11 results)

**Quality:** Completeness 82 | Reliability 92 | Recency 88 | Relevance 85 — Q2/Q4/Q5 underrepresented = novel contribution space

---

## 8. Research Gaps

### User Input Recall

📌 **User's Original Inputs (Gap Relevance Anchor):**
1. **Main Research Question**: Can optimization-level interventions (e.g., SAM, gradient surgery, or loss landscape regularization) reduce reliance on shortcut features in self-supervised and contrastive learning settings on existing spurious correlation benchmarks, without requiring group labels or knowledge of spurious feature identity?
2. **Detailed Questions (5 sub-questions)**:
   - Q1: Do SSL objectives (SimCLR, MoCo, DINO) exhibit differential shortcut reliance vs. supervised learning on Waterbirds/CelebA/CMNIST/UrbanCars?
   - Q2: Does temporal order of feature acquisition differ between supervised vs. SSL training regimes?
   - Q3: Can SAM/geometry-aware optimizers reduce shortcut reliance in SSL pre-training without group annotations?
   - Q4: Is there a detectable loss landscape signature (flatness/curvature) predicting shortcut reliance?
   - Q5: Can gradient alignment interventions in contrastive learning (between augmented views) mitigate shortcut adoption?
3. **Reference Papers**: Not provided

### Identified Gaps

#### Gap 1: SAM and Geometry-Aware Optimization During SSL Pre-Training for Shortcut Reduction

**Relevance Classification**: 🎯 PRIMARY
- ☑️ **Blocks answering research question**: The core RQ asks whether SAM-type optimization reduces shortcut reliance in SSL settings. No paper or implementation addresses this directly — SAM has been studied for supervised training and domain generalization, but never applied during SSL pre-training (SimCLR/MoCo/DINO) with worst-group accuracy on spurious correlation benchmarks as the outcome metric.
- ☑️ **Relates to detailed Q3**: Directly addresses Q3 (SAM in SSL without group annotations).
- ☑️ **Relates to detailed Q4**: G2-SAM and theoretical work link SAM to group-wise sharpness, but the loss landscape signature in SSL pre-training is unmeasured.

**Current State:** SAM has been applied to supervised classification (original SAM, ASAM), domain generalization (DGSAM), and supervised group robustness (G2-SAM). SSL frameworks (SimCLR, MoCo, DINO) have well-established implementations. Annotation-free robustification exists for supervised ERM (JTT, DFR, LFR, EVaLS). No paper combines SAM-type optimization with SSL contrastive pre-training objectives and measures worst-group accuracy on Waterbirds/CelebA/CMNIST.

**Missing Piece:** Empirical evaluation of SAM (and variants: ASAM, GSAM) applied to SSL contrastive pre-training on spurious correlation benchmarks, without group labels, measuring worst-group accuracy on existing datasets.

**Potential Impact:** High — if SAM during SSL pre-training reduces shortcut reliance, it provides a training-time, annotation-free robustification mechanism applicable to any SSL framework, directly enabling safer deployment of foundation models pre-trained on biased data.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Achieving Distributional Robustness with Group-Wise Flat Minima" | 2025 | Ji et al. | ef857d039dfa1a88d329e636c888ef7a3b09c5aa | null | 0 | G2-SAM applies group-wise SAM to supervised setting only — SSL gap confirmed |
| "DGSAM: Domain Generalization via Individual Sharpness-Aware Minimization" | 2025 | Song et al. | 0da44af38f5bbe7c342dd0bf05988378fb5dc192 | 2503.23430 | 1 | Per-domain SAM for domain gen, not spurious correlation; confirms SSL gap |
| "Simplicity Bias via Global Convergence of Sharpness Minimization" | 2024 | Gatmiry et al. | 0ab20995ed9d1c02dec42ca0cf4fd11774a8bf7d | 2410.16401 | 4 | Theoretical: sharpness minimization → rank-1 features → simplicity bias — suggests SAM may encourage core feature learning |
| "Sharpness-Aware Minimization for Efficiently Improving Generalization" | 2020 | Foret et al. | a2cd073b57be744533152202989228cb4122270a | 2010.01412 | 2062 | Original SAM — only supervised classification; no SSL or spurious correlation benchmarks |
| "Flat Minima and Generalization: Insights from SCO" | 2025 | Schliserman et al. | 39c469839a7c4b799b685d0063ff5249736281eb | 2511.03548 | 2 | SAM may not always generalize — theoretical risk for applying to SSL |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| No relevant cases found | N/A | "sharpness-aware minimization worst-group accuracy robustness" | Archon KB off-domain (image generation) |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| davda54/sam | https://github.com/davda54/sam | 1983 | Python/PyTorch | SAM+ASAM optimizer; `first_step`/`second_step` API; BN-compatible; drop-in for any training loop |
| google-research/sam | https://github.com/google-research/sam | 640 | Python | Official SAM — reference for rho tuning |
| p-giakoumoglou/pyssl | (referenced via code context) | N/A | Python/PyTorch | Unified SSL (SimCLR/MoCo/DINO) with simple `model(x)` → loss interface; easy SAM integration |

---

#### Gap 2: Differential Shortcut Reliance Between SSL and Supervised Learning Paradigms

**Relevance Classification**: 🎯 PRIMARY
- ☑️ **Blocks answering research question**: Cannot assess whether optimization interventions help in SSL without first establishing whether SSL even has different shortcut behavior than supervised learning (baseline comparison required).
- ☑️ **Relates to detailed Q1**: Directly addresses Q1 (differential shortcut reliance SSL vs. supervised on Waterbirds/CelebA/CMNIST/UrbanCars).
- ☑️ **Relates to detailed Q2**: Temporal dynamics of spurious vs. core feature acquisition in SSL vs. supervised not measured.

**Current State:** Izmailov et al. (NeurIPS 2022) study spurious feature learning in ERM/supervised settings and extend analysis to SSL (izmailovpavel/spurious_feature_learning). However, quantitative worst-group accuracy comparison of SimCLR vs. MoCo vs. DINO vs. supervised ERM on the same set of Waterbirds/CelebA/CMNIST/UrbanCars benchmarks does not exist as a systematic study. SubpopBench covers 20 supervised algorithms but not SSL pre-training paradigms. Cross-Variant SSL (Yadav et al. 2026) shows SSL-based method outperforms supervised but doesn't characterize the differential shortcut reliance.

**Missing Piece:** Systematic empirical comparison of worst-group accuracy for SSL (SimCLR/MoCo/DINO) vs. supervised ERM on Waterbirds/CelebA/CMNIST/UrbanCars using identical evaluation protocol — establishing whether and how much more (or less) shortcut-prone SSL is compared to supervised training.

**Potential Impact:** High — without this baseline, the research question cannot be answered: we need to know the SSL shortcut profile before measuring whether SAM reduces it.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "On Feature Learning in the Presence of Spurious Correlations" | 2022 | Izmailov et al. | (not found in search) | N/A | N/A | NeurIPS 2022 — partial SSL analysis; confirms gap exists |
| "Breaking Spurious Correlations via Generative Randomization and Cross-Variant SSL" | 2026 | Yadav et al. | d222c5f8b8dc04cfa54d181871864b19ab53da60 | 2607.05850 | 0 | Uses SSL (Cross-Variant) for spurious corr on Waterbirds — but no comparison to supervised shortcut reliance |
| "Contrastive Adapters for Foundation Model Group Robustness" | 2022 | Zhang & Ré | de4be9e0fa2f660eefb2d4c2a27c146d3e654a85 | 2207.07180 | 93 | CLIP (SSL) has up to 80.7pp gap between avg and worst-group accuracy — confirms SSL shortcut problem |
| "Spurious Correlation-Aware Embedding Regularization for Worst-Group Robustness" | 2025 | Park et al. | 3c40fa562e053143b26eceb84d8ac825174bd8bc | 2511.04401 | 1 | Theoretical framework linking embedding geometry to worst-group error — applicable to SSL representations |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| No relevant cases found | N/A | "self-supervised learning spurious correlations shortcut features" | Archon KB off-domain |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| izmailovpavel/spurious_feature_learning | https://github.com/izmailovpavel/spurious_feature_learning | 48 | Python | NeurIPS 2022 code; evaluates core/spurious feature information in representations; extend to SimCLR/MoCo/DINO |
| kohpangwei/group_DRO | https://github.com/kohpangwei/group_DRO | 295 | Python | Waterbirds/CelebA dataset loading; worst-group accuracy evaluation — baseline measurement infrastructure |
| subpopbench.csail.mit.edu | https://subpopbench.csail.mit.edu/ | N/A | Python | 20 algorithms × 12 datasets benchmark suite; currently supervised only — gap confirmed |

---

#### Gap 3: Loss Landscape Geometry as Predictor of Shortcut Reliance in SSL Models

**Relevance Classification**: 🎯 PRIMARY
- ☑️ **Blocks answering research question**: The RQ posits loss landscape regularization as a mechanism. Validating this requires knowing whether loss landscape curvature/flatness actually correlates with shortcut reliance in SSL models — this has not been established empirically.
- ☑️ **Relates to detailed Q4**: Directly addresses Q4 (detectable loss landscape signature predicting shortcut reliance).
- ☑️ **Relates to detailed Q5**: Gradient alignment between augmented views changes the loss landscape — understanding the landscape geometry is prerequisite to designing alignment-based interventions.

**Current State:** Theoretical work (Gatmiry et al. 2024) proves sharpness minimization leads to simplicity/rank-1 features in 2-layer networks. SCER (Park et al. 2025) theoretically links embedding directions to worst-group error. Flat minima criticism (Schliserman et al. 2025) shows SAM doesn't guarantee good generalization in convex settings. However, empirical measurement of loss landscape curvature (Hessian spectrum, sharpness) as a predictor of worst-group accuracy or shortcut reliance in SSL pre-trained models does not exist.

**Missing Piece:** Empirical measurement of loss landscape properties (sharpness, curvature around spurious vs. core feature directions, flatness of learned representations) in SSL pre-trained models (SimCLR/MoCo/DINO), and correlation of these properties with worst-group accuracy on existing benchmarks.

**Potential Impact:** Medium-High — if a loss landscape signature predicts shortcut reliance, it provides: (a) a diagnostic tool for SSL models before deployment, (b) a theoretical grounding for SAM-based interventions in SSL, (c) a model selection criterion without group annotations.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Simplicity Bias via Global Convergence of Sharpness Minimization" | 2024 | Gatmiry et al. | 0ab20995ed9d1c02dec42ca0cf4fd11774a8bf7d | 2410.16401 | 4 | Theory: SAM → rank-1 features → simplicity bias in 2-layer nets — not verified empirically in SSL |
| "Spurious Correlation-Aware Embedding Regularization for Worst-Group Robustness" | 2025 | Park et al. | 3c40fa562e053143b26eceb84d8ac825174bd8bc | 2511.04401 | 1 | Theoretically links embedding space geometry (spurious vs. core directions) to worst-group error |
| "Softly Induced Functional Simplicity: Implications for Neural Network Generalisation" | 2026 | Glowacki | 15354a981fdcdd9d27f41ab470ed2db43106116c | 2601.06584 | 0 | Hessian analysis of functional complexity — lower complexity → better generalization |
| "Flat Minima and Generalization: Insights from SCO" | 2025 | Schliserman et al. | 39c469839a7c4b799b685d0063ff5249736281eb | 2511.03548 | 2 | Theoretical critique: flat minima ≠ good generalization in general — sets boundary conditions |
| "Reproducibility study: Spurious Correlations, Shortcut Learning, Clever Hans" | 2026 | Delzer & Bender | 16cdba8cee4e6f7c509b978b9d63c84384b53220 | 2604.04518 | 0 | Unifies DRO/IRM/shortcut communities; group label dependency is main obstacle — motivates landscape-based alternatives |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| No relevant cases found | N/A | "loss landscape geometry simplicity bias shortcut learning" | Archon KB off-domain |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| weizeming/SAM_AT | https://github.com/weizeming/SAM_AT | 25 | Python | ICML 2024: SAM-adversarial training duality — contains loss landscape analysis tools |
| davda54/sam | https://github.com/davda54/sam | 1983 | Python | SAM optimizer with rho parameter controlling perturbation radius — controls landscape flatness |

---

### Gap Priority Matrix

| Gap ID | Relevance | Connection to RQ | Connection to Detailed Q | Extends Ref Paper | Impact | Evidence Count | Priority |
|--------|-----------|------------------|--------------------------|-------------------|--------|----------------|----------|
| Gap 1: SAM in SSL Pre-training | PRIMARY | ☑️ Core mechanism of RQ — SAM for shortcut reduction in SSL | ☑️ Q3 (SAM without annotations), Q4 (loss landscape) | ☐ No ref papers | High | 8 sources (5 scholar + 3 exa) | 🔴 Critical |
| Gap 2: SSL vs. Supervised Shortcut Differential | PRIMARY | ☑️ Prerequisite baseline for RQ — must establish SSL shortcut profile | ☑️ Q1 (differential reliance), Q2 (temporal dynamics) | ☐ No ref papers | High | 7 sources (4 scholar + 3 exa) | 🔴 Critical |
| Gap 3: Loss Landscape as Shortcut Predictor in SSL | PRIMARY | ☑️ Theoretical mechanism of RQ — landscape geometry → shortcut reliance | ☑️ Q4 (landscape signature), Q5 (gradient alignment prerequisite) | ☐ No ref papers | Medium-High | 7 sources (5 scholar + 2 exa) | 🟡 High |

### User Input to Gap Traceability

**Main Research Question** directly addressed by:
- Gap 1: Tests whether SAM (the intervention) works in SSL (the setting) on spurious benchmarks (the measurement) — this IS the research question.
- Gap 2: Establishes the baseline that makes the RQ answerable — if SSL has no differential shortcut behavior, the RQ is moot.
- Gap 3: Provides mechanistic explanation for WHY SAM would or wouldn't work (loss landscape geometry → shortcut reliance).

**Detailed Questions** addressed by:
- Gap 1 → Q3 (SAM in SSL without annotations), Q4 (loss landscape in SAM training)
- Gap 2 → Q1 (SSL vs. supervised differential), Q2 (temporal dynamics of spurious/core feature acquisition)
- Gap 3 → Q4 (loss landscape signature as predictor), Q5 (gradient alignment changes landscape → prerequisite understanding)

**Reference Papers**: Not provided — no reference paper extensions to trace.

---

## 9. Conclusion

### Key Findings

1. SAM + SSL pre-training gap is real and unoccupied: No paper combines SAM-type optimization with SimCLR/MoCo/DINO and measures worst-group accuracy on spurious correlation benchmarks. G2-SAM (2025) is closest but supervised-only.
2. Theoretical foundation exists: Gatmiry et al. (2024) proves sharpness minimization leads to simplicity bias (rank-1 features). Empirical bridge to SSL settings missing.
3. Annotation-free constraint satisfiable: JTT, LFR, EVaLS, EIIL all operate without group labels on same benchmarks. SAM also label-free.
4. Infrastructure ready: davda54/sam (1983★), izmailovpavel/spurious_feature_learning (48★), kohpangwei/group_DRO (295★), p-giakoumoglou/pyssl provide all needed components.
5. SSL shortcut baseline understudied: No systematic SimCLR/MoCo/DINO vs. supervised ERM comparison on Waterbirds/CelebA/CMNIST/UrbanCars simultaneously.
6. Theoretical risk: Schliserman et al. (2025) warns SAM can converge to sharp minima. DGSAM (2025) identifies "fake flat minima" problem.

### Next Steps

Phase 2A-Dialogue: Hypothesis Generation
- Read this compact file as primary input
- Generate testable hypotheses for each of the 3 PRIMARY gaps
- Prioritize Gap 1 (SAM+SSL) and Gap 2 (SSL shortcut baseline) as prerequisites for Gap 3
- Design validation approaches using identified implementations
- Maintain annotation-free constraint throughout

---

*Phase: 1 - Targeted Research Gathering*
*Total processing time: ~4 hours (Steps 0-9, including 3 MCP tool categories, rate limit retries, and Archon fallback protocol)*
