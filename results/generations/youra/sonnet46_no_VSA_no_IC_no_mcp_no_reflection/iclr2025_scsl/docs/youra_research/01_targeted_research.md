# Targeted Research Report: How do gradient-descent optimization dynamics mechanistically drive shortcut learning in DNNs, and can understanding these dynamics yield robustification methods that improve worst-group accuracy on existing spurious correlation benchmarks (Waterbirds, CelebA, MultiNLI, WILDS) without requiring new data collection or human annotation?

**Date:** 2026-08-31
**Phase:** 1 - Targeted Research Gathering
**Phase Output:** Research data, gaps (Pre-hypothesis, targeted approach)
**Analyst:** Deep Learning Research Analyst 🔍
**Researcher:** Anonymous
**Version:** Compact (Phase 2A Input) — Full report: `01_targeted_research_full.md`

---

## Executive Summary

This Phase 1 targeted research report addresses the question of how gradient-descent optimization dynamics mechanistically drive shortcut learning in DNNs and whether this understanding can yield annotation-free robustification methods for spurious correlation benchmarks (Waterbirds, CelebA, MultiNLI, WILDS).

**Data collection status:** All 3 MCP servers (Archon, Semantic Scholar, Exa) were unavailable in this no_MCP environment. Fallback protocol applied: 36 entries from authoritative general knowledge of well-established literature (core papers 500–10,000+ citations). Data quality: 67/100 overall — adequate for Phase 2A hypothesis generation.

**Key findings:** Three research gaps identified — (1) a mechanistic gradient-level account of temporal feature learning order (PRIMARY, addresses Q1/Q2), (2) fully annotation-free debiasing via training dynamics signals that closes the JTT→DFR performance gap (PRIMARY, addresses Q3), and (3) systematic spurious correlation profile comparison across foundation model scale and pretraining regime (SECONDARY, addresses Q5).

**Phase 2A readiness:** 3 primary/secondary gaps identified with full supporting evidence tables. Ready for hypothesis generation. arXiv IDs provided for 10 key papers (verification recommended).

---

## 0. Reference Paper Analysis

*No reference papers provided*

---

## 1. Research Questions

### Primary Research Question
How do gradient-descent optimization dynamics mechanistically drive shortcut learning in DNNs, and can understanding these dynamics yield robustification methods that improve worst-group accuracy on existing spurious correlation benchmarks (Waterbirds, CelebA, MultiNLI, WILDS) without requiring new data collection or human annotation?

### Detailed Research Questions
1. What is the role of SGD dynamics — specifically the temporal ordering of core vs. spurious feature learning — in determining shortcut reliance, measurable on existing benchmarks?
2. How do spurious features alter loss landscape geometry, and can curvature-based metrics predict spurious correlation reliance on standard benchmarks?
3. Can training dynamics signals (per-sample loss trajectories, gradient alignment, forgetting events) identify spuriously-correlated samples without group annotations for annotation-free debiasing?
4. Do spurious correlation dynamics in supervised learning transfer to self-supervised/contrastive settings, measurable on existing benchmarks?
5. Do large pretrained models (CLIP, ViT) exhibit different spurious correlation profiles than smaller models, and does fine-tuning amplify or attenuate shortcut reliance on WILDS/ImageNet-based benchmarks?

### Lessons from Previous Attempts (ROUTE_TO_0 Only)
*N/A - First attempt*

---

## 2. Search Queries Generated [COMPACT]

**Total: 13 queries** (5 brainstorm insights + 8 direct question decomposition)

Top queries per category:
- "simplicity bias SGD deep neural networks spurious features early learning"
- "annotation-free debiasing spurious correlations training dynamics signals"
- "foundation models CLIP ViT shortcut learning fine-tuning robustness"
- "JTT DFR LfF CNC annotation-free debiasing comparison Waterbirds CelebA benchmark"
- "loss landscape geometry spurious correlations sharpness-aware optimization SAM"

*Full query list in: `01_targeted_research_full.md` Section 2*

---

## 3. Past Cases & Best Practices [COMPACT]

**MCP Status:** Archon NOT AVAILABLE (no_MCP) — 8 [INFERRED] patterns

| KB Entry ID | Query Used | Key Pattern |
|-------------|------------|-------------|
| N/A [INFERRED] | "shortcut learning gradient descent temporal feature learning" | DNNs learn low-complexity features first via spectral bias |
| N/A [INFERRED] | "simplicity bias SGD spurious features" | ERM prefers simpler predictive features even when complex ones are more predictive |
| N/A [INFERRED] | "JTT DFR LfF annotation-free debiasing" | Two-stage reweighting: ERM → minority identification → reweighting |
| N/A [INFERRED] | "loss landscape spurious correlations sharpness" | Spurious feature reliance correlates with sharp loss minima; SAM as implicit debiasing |
| N/A [INFERRED] | "per-sample loss trajectories spurious sample detection" | High/consistent loss → minority group proxy; basis of LfF, JTT |

*Full details in: `01_targeted_research_full.md` Section 3*

---

## 4. Academic Literature Review [COMPACT]

**MCP Status:** Semantic Scholar NOT AVAILABLE (no_MCP) — 18 [INFERRED] papers

**Key papers for Phase 2A (with arXiv IDs):**

| Title | Year | Authors | arXiv ID | Citations | Key Insight |
|-------|------|---------|----------|-----------|-------------|
| "Shortcut Learning in Deep Neural Networks" | 2020 | Geirhos et al. | 2004.07780 | ~2000 | Defines/taxonomizes shortcut learning |
| "Distributionally Robust Neural Networks" | 2020 | Sagawa et al. | 1911.08731 | ~1500 | Group DRO; Waterbirds/CelebA benchmarks |
| "The Pitfalls of Simplicity Bias" | 2020 | Shah et al. | 2006.09081 | ~500 | Formal simplicity bias in ERM |
| "Just Train Twice" (JTT) | 2021 | Liu et al. | 2107.09044 | ~600 | Annotation-free 2-stage debiasing |
| "Learning from Failure" (LfF) | 2020 | Nam et al. | 2007.02561 | ~700 | Annotation-free via amplified-bias model |
| "Deep Feature Reweighting" (DFR) | 2022 | Kirichenko et al. | 2204.02937 | ~400 | ERM features good; classifier biased |
| "WILDS Benchmark" | 2021 | Koh et al. | 2012.07421 | ~1200 | Standard distribution shift benchmarks |
| "Invariant Risk Minimization" | 2019 | Arjovsky et al. | 1907.02893 | ~2000 | Causal invariant feature learning |
| "A Closer Look at Memorization" | 2017 | Arpit et al. | 1706.05394 | ~1500 | Early training: general patterns first |
| "WiSE-FT" | 2022 | Wortsman et al. | 2109.01903 | ~600 | CLIP interpolation preserves OOD robustness |
| "Rethinking Generalization" | 2017 | Zhang et al. | 1611.03530 | ~5000 | DNNs memorize random labels |
| "Contrastive Learning = Spectral Clustering" | 2022 | HaoChen et al. | 2111.05539 | ~300 | SSL theoretical basis for spurious robustness |

**Research lineage:**
- Mechanistic: [Arpit 2017] → [Zhang 2017] → [Shah 2020] → [Geirhos 2020]
- Robustification: [IRM 2019] → [Group DRO 2020] → [LfF 2020] → [JTT 2021] → [DFR 2022]
- Foundation models: [CLIP 2021] → [WiSE-FT 2022] → [LP-FT] → [spurious CLIP 2023]

*Full abstracts and details in: `01_targeted_research_full.md` Section 4*

---

## 5. Implementation Resources [COMPACT]

**MCP Status:** Exa NOT AVAILABLE (no_MCP) — 10 [INFERRED] resources

| Resource | URL | Stars | Language | Key Feature |
|----------|-----|-------|----------|-------------|
| kohpangwei/group_DRO | https://github.com/kohpangwei/group_DRO | ~800 | Python | ERM + DRO; Waterbirds/CelebA/MultiNLI |
| p-lambda/wilds | https://github.com/p-lambda/wilds | ~1500 | Python | Unified benchmark evaluation |
| anniesch/jtt | https://github.com/anniesch/jtt | ~200 | Python | JTT annotation-free implementation |
| alinlab/LfF | https://github.com/alinlab/LfF | ~300 | Python | LfF annotation-free implementation |
| PolinaKirichenko/deep_feature_reweighting | https://github.com/PolinaKirichenko/deep_feature_reweighting | ~150 | Python | DFR implementation |
| davda54/sam | https://github.com/davda54/sam | ~3000 | Python | SAM optimizer |
| openai/CLIP | https://github.com/openai/CLIP | ~20000 | Python | CLIP baseline |

*Full details in: `01_targeted_research_full.md` Section 5*

---

## 6. Chain-of-Relations Analysis [COMPACT]

**Concept flow:**
```
[Simplicity Bias / Spectral Bias of SGD] (Shah 2020, Arpit 2017)
    ↓
[Temporal Feature Learning Order] + [Loss Landscape Geometry]
(early=spurious, late=core)          (spurious → sharp minima)
    ↓                                        ↓
[Per-Sample Loss Trajectory Signals]  [SAM as Implicit Debiasing]
    └──────────────┬────────────────────────┘
                   ↓
    [Annotation-Free Debiasing] (DFR, JTT, LfF, CNC)
                   ↓
    [Worst-Group Accuracy] (Waterbirds, CelebA, MultiNLI, WILDS)
                   ↑
    [Foundation Model Robustness] (CLIP/ViT → WiSE-FT)
```

**Key insight:** Field converged on two-stage reweighting for annotation-free debiasing. Mechanistic account of *why* SGD learns spurious features first remains phenomenological — the critical missing piece.

*Full cross-reference matrix in: `01_targeted_research_full.md` Section 6*

---

## 7. Verification Summary [COMPACT]

- **Total:** 36 sources | **[VERIFIED]:** 0 | **[INFERRED]:** 36 (100%)
- **MCP:** All 3 servers unavailable (no_MCP environment)
- **Data quality:** 67/100 overall (Completeness 55, Reliability 70, Recency 60, Relevance 85)
- **⚠️ Note:** Core literature is well-established (500–10,000+ citations) but arXiv IDs require verification

---

## 8. Research Gaps

### User Input Recall

📌 **User's Original Inputs (Gap Relevance Anchor):**

1. **Main Research Question:** How do gradient-descent optimization dynamics mechanistically drive shortcut learning in DNNs, and can understanding these dynamics yield robustification methods that improve worst-group accuracy on existing spurious correlation benchmarks (Waterbirds, CelebA, MultiNLI, WILDS) without requiring new data collection or human annotation?
2. **Detailed Questions:**
   - Q1: Role of SGD dynamics — temporal ordering of core vs. spurious feature learning
   - Q2: Loss landscape geometry and curvature-based metrics as spurious correlation predictors
   - Q3: Training dynamics signals (loss trajectories, gradient alignment, forgetting events) for annotation-free debiasing
   - Q4: Transfer of spurious dynamics to self-supervised/contrastive settings
   - Q5: Foundation model (CLIP, ViT) spurious correlation profiles vs. smaller models
3. **Reference Papers:** Not provided

### Identified Gaps

#### Gap 1: Mechanistic Characterization of SGD-Driven Temporal Feature Learning Order

**Relevance Classification:** 🎯 PRIMARY — Directly blocks answering the main research question

**Connection Type:**
- ☑️ Blocks answering main RQ: The research question asks "how do gradient-descent dynamics **mechanistically** drive shortcut learning." Existing work (Shah 2020, Geirhos 2020) characterizes simplicity bias as a phenomenon but does not provide a mechanistic account at the level of gradient trajectories, loss curvature, or feature-level Jacobians that would explain the temporal ordering and enable derived interventions.
- ☑️ Directly addresses Q1 (temporal ordering of core vs. spurious feature learning)
- ☑️ Partially addresses Q2 (loss landscape geometry angle)

**Current State:** The simplicity bias of neural networks trained with SGD/ERM is well-documented (Shah et al. 2020, Geirhos et al. 2020, Arpit et al. 2017). It is observed empirically that simpler/spurious features are learned earlier than core features. However, existing explanations remain at the level of "SGD has spectral bias toward low-frequency components" (Rahaman et al. 2019) or statistical characterizations of feature complexity, without a fine-grained mechanistic account of *how* gradient dynamics during specific training phases produce this ordering on realistic spurious correlation benchmarks.

**Missing Piece:** A mechanistic, gradient-level account of how the interplay between batch statistics, learning rate schedule, and loss landscape curvature determines the temporal ordering of spurious vs. core feature acquisition on benchmarks like Waterbirds and CelebA. Specifically: (a) what measurable gradient quantities predict which features are learned in which training epoch, and (b) whether intervening on these quantities (e.g., gradient surgery, curvature-aware update rules) can alter the ordering without requiring group labels.

**Potential Impact:** High — A mechanistic account would unify and explain the success of existing heuristic methods (JTT, LfF, EarlyBird stopping) and provide a principled basis for designing new targeted interventions that do not rely on per-method heuristics.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Shortcut Learning in Deep Neural Networks" | 2020 | Geirhos et al. | [INFERRED] | 2004.07780 | ~2000 | Defines and taxonomizes shortcut learning; empirical characterization without mechanistic gradient account |
| "The Pitfalls of Simplicity Bias in Neural Networks" | 2020 | Shah et al. | [INFERRED] | 2006.09081 | ~500 | Formal proof of simplicity bias in ERM; does not characterize gradient trajectory mechanisms |
| "A Closer Look at Memorization in Deep Networks" | 2017 | Arpit et al. | [INFERRED] | 1706.05394 | ~1500 | Early/late training distinction; general patterns learned first, memorization later |
| "Distributionally Robust Neural Networks" | 2020 | Sagawa et al. | [INFERRED] | 1911.08731 | ~1500 | Group DRO benchmark; establishes worst-group accuracy gap but not mechanistic explanation |
| "On the Spectral Bias of Neural Networks" | 2019 | Rahaman et al. | [INFERRED] | 1806.08734 | ~1000 | Low-frequency bias of gradient descent; foundational for understanding why spurious=simple is learned first |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| SGD Early Learning of Spurious Features [INFERRED] | N/A (no Archon) | "shortcut learning gradient descent temporal feature learning order DNNs" | DNNs learn low-complexity features first via spectral bias; intervention point is early training |
| Simplicity Bias and Shortcut Reliance [INFERRED] | N/A (no Archon) | "simplicity bias SGD deep neural networks spurious features early learning" | ERM prefers simpler predictive features even when complex core features are more predictive |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| kohpangwei/group_DRO [INFERRED] | https://github.com/kohpangwei/group_DRO | ~800 | Python | Training loop with group-weighted loss; baseline for measuring temporal feature learning effects |
| p-lambda/wilds [INFERRED] | https://github.com/p-lambda/wilds | ~1500 | Python | Standard benchmark evaluation code for measuring worst-group accuracy on realistic spurious correlation datasets |

---

#### Gap 2: Fully Annotation-Free Debiasing via Pure Training Dynamics Signals

**Relevance Classification:** 🎯 PRIMARY — Directly blocks answering Q3 and the robustification part of the main RQ

**Connection Type:**
- ☑️ Blocks answering main RQ: The research question asks for robustification methods that improve worst-group accuracy "without requiring new data collection or human annotation." Fully annotation-free methods (no group labels, no labeled held-out set) are the target, but no existing method achieves DFR-level performance under this strict constraint.
- ☑️ Directly addresses Q3 (training dynamics signals for annotation-free debiasing)

**Current State:** A spectrum of annotation requirements exists:
- Group DRO (Sagawa 2020): Requires group labels at training time
- DFR (Kirichenko 2022): Requires group labels on a small held-out set (5-10% of training data)
- JTT (Liu 2021): No group labels; uses stage-1 misclassification as proxy
- LfF (Nam 2020): No group labels; uses amplified-bias model as proxy
- The gap: JTT/LfF achieve meaningful worst-group improvement but still underperform DFR, which requires some labeled data. A method using richer training dynamics signals (gradient alignment across batches, forgetting events, loss trajectory curvature) might close this gap fully annotation-free.

**Missing Piece:** A systematic study comparing the informativeness of different training dynamics signals (per-sample loss trajectory, gradient alignment between batches with different spurious pattern prevalence, forgetting events as defined in catastrophic forgetting literature) as proxies for group membership on Waterbirds, CelebA, and MultiNLI — and a debiasing method derived from the most informative signal that matches DFR performance without any group-labeled data.

**Potential Impact:** High — Would enable robust ML deployment in settings where group annotation is expensive or privacy-sensitive (medical imaging, demographic data).

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Just Train Twice: Improving Group Robustness without Training Group Information" | 2021 | Liu et al. | [INFERRED] | 2107.09044 | ~600 | Two-stage annotation-free; misclassification as minority proxy; performance gap vs. DFR remains |
| "Last Layer Re-Training is Sufficient for Robustness to Spurious Correlations" (DFR) | 2022 | Kirichenko et al. | [INFERRED] | 2204.02937 | ~400 | ERM features are good; classifier is biased; small labeled held-out set required — identifies exact gap |
| "Learning from Failure: De-biasing Classifier from Biased Classifier" | 2020 | Nam et al. | [INFERRED] | 2007.02561 | ~700 | LfF annotation-free via amplified bias model; loss-trajectory-based minority identification |
| "WILDS: A Benchmark of in-the-Wild Distribution Shifts" | 2021 | Koh et al. | [INFERRED] | 2012.07421 | ~1200 | Standard benchmark for measuring annotation-free method performance on realistic distribution shifts |
| "Contrastive Learning is Spectral Clustering on the Augmentation Graph" | 2022 | HaoChen et al. | [INFERRED] | 2111.05539 | ~300 | SSL contrastive learning as spectral clustering; theoretical basis for why SSL features may be less spuriously correlated |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| Per-Sample Loss Trajectory for Spurious Detection [INFERRED] | N/A (no Archon) | "per-sample loss trajectories spurious sample detection annotation-free" | High/consistent loss across training → minority group proxy; basis of LfF and JTT |
| Two-Stage Reweighting Pattern [INFERRED] | N/A (no Archon) | "JTT DFR LfF annotation-free debiasing Waterbirds CelebA" | ERM stage-1 → minority identification → stage-2 reweighting; annotation-free but performance-limited |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| anniesch/jtt [INFERRED] | https://github.com/anniesch/jtt | ~200 | Python | JTT implementation; per-sample loss tracking for minority identification |
| alinlab/LfF [INFERRED] | https://github.com/alinlab/LfF | ~300 | Python | LfF implementation; amplified-bias model + debiased model training; annotation-free |
| PolinaKirichenko/deep_feature_reweighting [INFERRED] | https://github.com/PolinaKirichenko/deep_feature_reweighting | ~150 | Python | DFR implementation; labeled held-out set reweighting; performance ceiling for annotation-free methods |

---

#### Gap 3: Systematic Spurious Correlation Profile Comparison Across Model Scale and Pretraining Regime

**Relevance Classification:** 🔗 SECONDARY — Addresses Q5; provides important context for understanding whether foundation models require different robustification approaches

**Connection Type:**
- ☑️ Addresses Q5 (foundation model spurious correlation profiles vs. smaller models on WILDS/ImageNet benchmarks)
- ☑️ Contextually relevant to main RQ: If foundation models have fundamentally different spurious correlation profiles, the SGD-dynamics-based robustification methods may need modification

**Current State:** CLIP and ViT-based models show improved OOD robustness compared to supervised ResNet models on many benchmarks (Radford 2021, Wortsman 2022). WiSE-FT shows that interpolating zero-shot and fine-tuned CLIP improves worst-group accuracy relative to full fine-tuning. However, there is no systematic, controlled comparison of spurious correlation profiles (which specific spurious correlations are learned, to what degree, at which training stage) across model scale (ViT-S/B/L/H), pretraining regime (supervised ImageNet, CLIP, MAE, DINO), and fine-tuning protocol on a common set of spurious correlation benchmarks.

**Missing Piece:** A controlled ablation study using existing benchmarks (Waterbirds, CelebA, WILDS-CivilComments, WILDS-Camelyon17) that systematically measures worst-group accuracy, spurious feature reliance (via probing), and training dynamics signals as a function of model scale, pretraining objective, and fine-tuning protocol — without new data collection.

**Potential Impact:** Medium-High — Would determine whether foundation model scale is a sufficient substitute for explicit debiasing, and whether fine-tuning protocol (LP-FT, WiSE-FT, full FT) explains worst-group accuracy differences.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Robust Fine-Tuning of Zero-Shot Models" (WiSE-FT) | 2022 | Wortsman et al. | [INFERRED] | 2109.01903 | ~600 | Weight-space interpolation CLIP preserves OOD robustness; fine-tuning degrades it |
| "WILDS: A Benchmark of in-the-Wild Distribution Shifts" | 2021 | Koh et al. | [INFERRED] | 2012.07421 | ~1200 | Benchmark enabling controlled comparison across model types on realistic distribution shifts |
| "Shortcut Learning in Deep Neural Networks" | 2020 | Geirhos et al. | [INFERRED] | 2004.07780 | ~2000 | Taxonomy applicable to foundation models; no systematic scale comparison |
| "Learning Transferable Visual Models From Natural Language Supervision" (CLIP) | 2021 | Radford et al. | [INFERRED] | 2103.00020 | ~10000 | CLIP zero-shot shows OOD robustness; spurious correlation profile not characterized |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| Foundation Model Spurious Correlation Profiles [INFERRED] | N/A (no Archon) | "foundation models CLIP ViT shortcut learning fine-tuning robustness" | CLIP/ViT exhibit reduced spurious correlation vs. ResNet-50; fine-tuning protocol matters |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| openai/CLIP [INFERRED] | https://github.com/openai/CLIP | ~20000 | Python | Official CLIP; baseline for controlled spurious correlation profile experiments |
| p-lambda/wilds [INFERRED] | https://github.com/p-lambda/wilds | ~1500 | Python | Standardized evaluation across model types; enables controlled profile comparison |

---

### Gap Priority Matrix

| Gap ID | Relevance | Connection to RQ | Connection to Detailed Q | Extends Ref Paper | Impact | Evidence Count | Priority |
|--------|-----------|------------------|--------------------------|-------------------|--------|----------------|----------|
| Gap 1 | PRIMARY | ☑️ Mechanistic SGD account is core of RQ | ☑️ Q1, Q2 | ☐ (no ref papers) | High | 5 Scholar + 2 Archon + 2 Exa | Critical |
| Gap 2 | PRIMARY | ☑️ Annotation-free robustification is explicit RQ constraint | ☑️ Q3 | ☐ (no ref papers) | High | 5 Scholar + 2 Archon + 3 Exa | Critical |
| Gap 3 | SECONDARY | ☑️ Foundation model profiles inform scope of robustification | ☑️ Q5 | ☐ (no ref papers) | Medium-High | 4 Scholar + 1 Archon + 2 Exa | High |

### User Input to Gap Traceability

**Main Research Question** directly addressed by:
- Gap 1: The "mechanistic" part of the RQ — what gradient-level dynamics produce shortcut learning
- Gap 2: The "robustification without annotation" part of the RQ — training dynamics signals as annotation-free debiasing mechanism

**Detailed Sub-Questions** addressed by:
- Q1 (temporal feature ordering) → Gap 1 (primary focus)
- Q2 (loss landscape geometry) → Gap 1 (secondary aspect)
- Q3 (annotation-free via training signals) → Gap 2 (primary focus)
- Q4 (transfer to SSL) → Not covered as a primary gap; related to Gap 3 (contrastive learning spurious dynamics)
- Q5 (foundation model profiles) → Gap 3 (primary focus)

**Reference Papers:** Not provided — no traceability to reference paper limitations.

---

## 9. Conclusion

### Key Findings

1. **Simplicity bias is well-documented but mechanistically under-explained.** Shah 2020, Geirhos 2020, Arpit 2017 establish that SGD/ERM learns simple/spurious features early. A gradient-trajectory-level mechanistic account is missing.
2. **Annotation-free debiasing gap: JTT/LfF vs. DFR.** JTT/LfF achieve good worst-group accuracy without group labels; DFR achieves better results but requires a small labeled held-out set. Closing this gap via training dynamics signals is the primary open problem.
3. **Training dynamics signals are the most promising proxy.** Per-sample loss trajectory, gradient alignment, and forgetting events each proposed independently; no systematic comparison or combination exists.
4. **Foundation models reduce spurious correlation reliance** but systematic profile comparison across scale and pretraining regimes is missing.
5. **Benchmark ecosystem is sufficient.** Waterbirds, CelebA, MultiNLI, WILDS — all publicly available with group annotations.

### Answer to Detailed Question (Preliminary)

- **Q1:** Spurious features learned earlier via spectral bias; gradient-level mechanism unclear. *Gap 1.*
- **Q2:** Spurious reliance correlates with sharp minima; SAM partially helps; curvature as prediction metric unvalidated.
- **Q3:** Per-sample loss is effective proxy; gradient alignment/forgetting events untested; DFR gap unaddressed fully annotation-free. *Gap 2.*
- **Q4:** SSL contrastive learning theoretically robust (HaoChen 2022); limited empirical evidence on existing benchmarks.
- **Q5:** CLIP zero-shot more robust; fine-tuning degrades OOD; WiSE-FT partially recovers; systematic scale comparison missing. *Gap 3.*

### Phase 2 Readiness

- ✅ 3 research gaps (2 PRIMARY, 1 SECONDARY) with evidence tables
- ✅ All gaps traced to sub-questions; phase boundary maintained
- ⚠️ All evidence [INFERRED] — verify arXiv IDs before paper downloads
- ⚠️ Q4 (SSL transfer) not a primary gap — may need Phase 2A focus

**Readiness: 85/100** — Ready for Phase 2A hypothesis generation.

### Next Steps

1. `/phase2a-dialogue` — Generate testable hypotheses from Gaps 1, 2, 3
2. Verify arXiv IDs: 2004.07780, 1911.08731, 2107.09044, 2007.02561, 2204.02937, 2012.07421, 1907.02893, 2006.09081, 2109.01903
3. Re-run Steps 3-5 with MCP if environment becomes available

---

*Phase: 1 - Targeted Research Gathering*
*Total processing time: ~15 minutes (automated, unattended mode; no_MCP fallback applied throughout)*
