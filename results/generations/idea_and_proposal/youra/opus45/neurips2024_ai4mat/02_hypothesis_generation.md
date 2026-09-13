# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-HCMB-v1
**Confidence Level:** 0.85

**Main Hypothesis:**
Under the condition of multimodal materials characterization data with arbitrary modality dropout (10-50%), if hierarchical cross-modal binding with local (within modality groups) and global (across groups) attention is applied, then property prediction error will decrease and robustness to missing modalities will increase, because the hierarchical binding mechanism creates unified representations that leverage complementary information across available modalities without requiring all modalities to be present.

**Alternative Hypothesis (H0):**
There is no significant relationship between hierarchical cross-modal binding and prediction accuracy/robustness in multimodal materials property prediction. Standard late fusion or simple concatenation achieves equivalent performance.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| number_of_modalities | Independent | Count of available characterization modalities (composition, structure, XRD) | 2-5 modalities |
| missing_modality_rate | Independent | Percentage of samples with at least one missing modality, controlled via random dropout | 0-50% |
| prediction_error | Dependent | MAE and RMSE on held-out test set for formation energy (eV/atom) and band gap (eV) | MAE: 0.02-0.10 eV/atom |
| robustness_score | Dependent | Performance degradation ratio = (MAE_missing - MAE_full) / MAE_full | 0-30% degradation |
| dataset_size | Controlled | Alexandria dataset with 5M samples, fixed 80/10/10 train/val/test splits | Fixed |
| architecture_hyperparameters | Controlled | Embedding dim=256, attention heads=8, encoder depths fixed per modality | Fixed |

### 1.3 Causal Mechanism

**Step 1: Modality-Specific Encoding**
Each characterization modality is encoded by a domain-appropriate encoder:
- Composition → Elemental embedding (Magpie-style features + learned embeddings)
- Crystal structure → E(3)-equivariant GNN (e3nn-based)
- XRD patterns → Transformer encoder (1D sequence)

**Step 2: Contrastive Cross-Modal Alignment**
CLIP-style contrastive learning projects modality-specific embeddings into shared semantic space:
- InfoNCE loss between paired modality embeddings
- Temperature-scaled similarity matching
- Result: Semantically aligned latent representations

**Step 3: Hierarchical Binding → Unified Prediction**
Two-level attention binding fuses aligned representations:
- Local binding: Attention within modality groups (e.g., spectroscopy group)
- Global binding: Cross-group attention to create unified representation
- Attention masking handles missing modalities gracefully

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | COSNet (2023) | Bimodal composition+structure encoding works | Strong |
| Step1 → Step2 | GNoME (2023) | GNN for structure achieves SOTA at scale | Strong |
| Step2 → Step3 | UniDiffuser (Archon) | Joint modality learning via unified transformer | Medium |
| Step2 → Step3 | EEG-fNIRS fusion (2025) | Dual attention for multimodal brain signals | Medium |
| Step3 → Outcome | FuseMoE (NeurIPS 2024) | MoE gating for incomplete modalities | Strong |

**Key Tension:**
COSNet demonstrates bimodal learning with missing data augmentation is effective but limited to 2 modalities. FuseMoE shows MoE-based fusion scales to N modalities but lacks domain-specific inductive biases. HCMB-Net bridges this gap by combining hierarchical attention (scalable) with domain-specific equivariant encoders (materials-aware).

### 1.4 Key Assumptions

1. **Materials properties are predictable from multimodal characterization**
   - Evidence: GNoME, COSNet, JARVIS demonstrate this for single/bimodal cases
   - Consequence if violated: Hypothesis fundamentally invalid

2. **Modalities provide complementary rather than redundant information**
   - Evidence: Multimodal spectroscopy fusion (2025) showed defects detectable only via fusion
   - Consequence if violated: Multimodal fusion provides no benefit over best single modality

3. **Contrastive alignment creates meaningful shared representations**
   - Evidence: CLIP success in vision-language; UniDiffuser in image-text
   - Consequence if violated: Direct fusion might work better; alignment step removable

4. **Hierarchical binding outperforms flat attention for N>3 modalities**
   - Evidence: Neuroscience multisensory integration; reduced O(N²) complexity
   - Consequence if violated: Simpler flat attention sufficient

### 1.5 Scope & Boundaries

**Applies to:**
- Inorganic crystalline materials with periodic structure
- Characterization modalities: composition, crystal structure, XRD patterns
- Property prediction tasks: formation energy, band gap, bulk modulus
- Dataset: Alexandria (5M samples), Materials Project, JARVIS

**Does NOT apply to:**
- Amorphous materials (no periodic structure for GNN)
- Organic molecules (different bonding patterns)
- Modalities requiring different physics: magnetic properties, defect concentrations

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Multimodal vs Bimodal Performance)**:
HCMB-Net with 3 modalities will achieve statistically significant improvement over COSNet (2 modalities).

*Measurement*: MAE improvement > 5% relative to COSNet baseline; p < 0.05, n ≥ 25 runs
*Success Criteria*: MAE < 0.045 eV/atom (10% improvement over COSNet ~0.05)
*Falsification*: MAE ≥ 0.055 eV/atom triggers rejection

**Secondary Predictions:**

**P2 (Robustness)**: Under 30% modality dropout, <10% performance degradation
**P3 (Hierarchical vs Flat)**: Hierarchical outperforms flat attention when N ≥ 3

**Falsification Criteria:**
1. Primary Failure: MAE ≥ 0.055 eV/atom (worse than COSNet)
2. Robustness Failure: Degradation > 25% under 30% dropout
3. Mechanism Failure: Hierarchical ≤ flat attention performance
4. Baseline Failure: Single modality matches multimodal

### 1.7 Statistical Verification Design

**Sample Size**: n ≥ 25 independent training runs
**Effect Size Target**: Cohen's d = 0.5 (medium)
**Statistical Test**: Paired t-test, α = 0.05 (one-tailed)
**Report Format**: Mean ± Std Dev, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does hierarchical cross-modal binding improve materials property prediction accuracy compared to single-modality and bimodal baselines?"

**SH2 (Mechanism):**
"Is the hierarchical binding mechanism the actual cause of improved performance?"
- H-M1: Modality-specific encoders preserve domain-relevant features
- H-M2: Contrastive alignment creates meaningful shared representations
- H-M3: Hierarchical binding outperforms flat attention

**SH3 (Comparison):**
"Does HCMB-Net provide practical advantages (robustness, efficiency) over existing methods?"

**Total sub-hypotheses:** 5 (SH1, H-M1, H-M2, H-M3, SH3)

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-HCMB-v1
- [x] Confidence level: 0.85
- [x] Alternative hypothesis (H0) defined
- [x] All variables operationalized
- [x] Causal mechanism with evidence (N=3 steps)
- [x] Key tension identified with resolution
- [x] Assumptions list consequences if violated
- [x] Testable predictions with primary marked
- [x] Falsification criteria defined
- [x] Baselines identified: COSNet, single-modality, flat attention
- [x] SH1, SH2, SH3 ready

### Open Questions

1. **Data Access:** Alexandria dataset directly vs Materials Project + JARVIS proxy?
2. **Compute Requirements:** E(3)-equivariant GNN on 5M samples - GPU hours estimate?
3. **Modality Priority:** If reduced scope, which 2 modalities are most complementary?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-13*
