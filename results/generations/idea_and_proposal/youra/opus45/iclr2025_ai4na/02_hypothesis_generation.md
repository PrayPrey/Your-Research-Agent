# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md (Round 1 - HiMamba-CL)
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-HiMamba-CL-v1
**Confidence Level:** 0.87

**Main Hypothesis:**
Under conditions of sufficient paired RNA sequence-structure data (RNAcentral + Rfam with >1M sequence-structure pairs), if hierarchical bidirectional Mamba layers (4 layers with 2x receptive field expansion) are combined with contrastive cross-modal alignment using biological augmentations (orthologs, splice isoforms, synonymous mutations), then unified RNA representations will achieve superior downstream task performance (≥10% improvement on structure prediction accuracy, ≥15% improvement on cross-task transfer efficiency) because hierarchical processing captures multi-scale RNA patterns (local motifs → secondary domains → full transcript context) while contrastive alignment learns modality-invariant features that generalize across RNA types and species.

**Alternative Hypothesis (H0):**
There is no significant difference in downstream RNA task performance between hierarchical multimodal contrastive models and flat single-modality RNA foundation models; alternatively, sequence information alone is sufficient for RNA representation learning, and structure integration provides no measurable benefit.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Architecture depth | Independent | Number of hierarchical Mamba layers (2, 4, 6) with 2x receptive field expansion per layer | 2-6 layers; default=4 |
| Modality inclusion | Independent | Training modalities: seq-only, seq+2D, seq+2D+3D | 3 configurations |
| Alignment method | Independent | Loss function: contrastive (InfoNCE τ=0.07), reconstruction (MSE), hybrid | 3 methods |
| Structure prediction accuracy | Dependent | RMSD (Å) and TM-score on RNA 3D structure benchmarks | RMSD: 2.0-5.0Å; TM: 0.5-0.9 |
| Function classification | Dependent | AUC-ROC on ncRNA family classification (13 BEACON tasks) | AUC: 0.75-0.95 |
| Embedding quality | Dependent | Normalized Mutual Information (NMI) of RNA family clusters | NMI: 0.6-0.9 |
| Cross-task transfer | Dependent | Fine-tuning data efficiency (samples needed for 90% max performance) | 10-100% of baseline |
| Model size | Controlled | Total parameters fixed across configurations | ~100M parameters |
| Training data | Controlled | RNAcentral subset + Rfam families | 5M sequences, 4K families |
| Hyperparameters | Controlled | Batch=256, LR=1e-4 cosine decay, 100 epochs | Fixed across experiments |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: Hierarchical Mamba Layers
    ↓ (captures progressively larger receptive fields)
Step 2: Multi-Scale RNA Pattern Representations
    ↓ (local motifs + secondary domains + global context)
Step 3: Contrastive Cross-Modal Alignment
    ↓ (InfoNCE with biological augmentations creates modality-invariant embeddings)
Step 4: Modality-Invariant Unified Embeddings
    ↓ (generalize across RNA types, species, and tasks)
Outcome: Superior Downstream Task Performance
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | HiSS (Bhirangi et al., 2024) | Hierarchical SSM stacking achieves 23% improvement on MSE over flat Mamba, S4, Transformers | Strong |
| Step 2 → Step 3 | RNA biology fundamentals | RNA motifs operate at 3-10nt (local), 50-200nt (domains), full-length scales | Strong |
| Step 3 → Step 4 | Orthrus (Fradkin et al., 2024) | Contrastive learning with orthologs/isoforms creates functional RNA clusters; outperforms genomic FMs | Strong |
| Step 4 → Outcome | Protein Contrastive (2025) | Cross-modal sequence-structure alignment improves diverse downstream tasks | Medium |

**Key Tension:**
- **Tension:** HiSS was validated on continuous sensor signals (tactile, accelerometer data), not discrete biological sequences. The effectiveness of hierarchical stacking for RNA sequences specifically is not yet empirically validated.
- **Resolution:** This verification plan includes ablation studies (Step 1 mechanism test) comparing hierarchical vs. flat Mamba architectures on RNA-specific benchmarks to directly test transferability.

### 1.4 Key Assumptions

| # | Assumption | Evidence | Consequence if Violated |
|---|------------|----------|------------------------|
| A1 | Paired sequence-structure data exists at sufficient scale (>1M pairs) in RNAcentral/Rfam | RNAcentral contains 20M+ sequences; Rfam has 4K+ families with secondary structure annotations | If insufficient: staged training approach fails; revert to sequence-only pre-training |
| A2 | Predicted tertiary structures are accurate enough for pre-training | AlphaFold-RNA and similar tools show moderate accuracy on known families | If inaccurate: tertiary tower provides noise; fall back to sequence+secondary only |
| A3 | Hierarchical pattern extraction from HiSS transfers to biological sequences | HiSS demonstrated on continuous sensor data; DGRNA shows Mamba works for RNA | If no transfer: hierarchical provides no benefit; use flat Mamba baseline |
| A4 | Contrastive benefits extend from single-modality (Orthrus) to multimodal setting | Orthrus sequence-only + protein multimodal precedent | If no extension: multimodal contrastive may not outperform single-modality contrastive |

### 1.5 Scope & Boundaries

**Applies To:**
- Coding and non-coding RNAs (mRNA, lncRNA, miRNA, rRNA, tRNA, etc.)
- RNA lengths from 50nt to 10,000nt (chunking for longer)
- Species-agnostic (trained on multi-species data)
- Tasks: structure prediction, function classification, interaction prediction, embedding generation

**Does NOT Apply To:**
- Real-time applications (training is offline; inference ~100ms/sequence)
- Single-nucleotide resolution predictions (e.g., exact modification sites)
- RNA design/generation tasks (this is a discriminative model)
- Very short RNAs (<50nt) - insufficient context for hierarchical processing

**Known Limitations:**
- Tertiary structure data limited to ~5K experimental + predicted structures
- Very long RNAs (>10K nt) require chunking with potential context loss
- Computational requirements: 4-8 GPUs, ~100 GPU-hours for pre-training

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Hierarchical Advantage):**
If hierarchical Mamba architecture is used (4 layers, 2x expansion), then long-range RNA structure prediction accuracy will improve by ≥10% (relative) compared to flat Mamba baseline.

*Measurement:*
- Metric: TM-score on RNA 3D structure prediction benchmark
- Baseline: DGRNA flat Mamba (~0.65 TM-score on CASP-RNA subset)
- Target: ≥0.72 TM-score (10% relative improvement)
- Statistical test: Paired t-test, n ≥ 25 runs, p < 0.05

*Success Criteria:*
- Primary: TM-score > 0.72 with p < 0.05
- Falsification: TM-score ≤ 0.65 (no improvement over flat baseline)

**Secondary Predictions:**

**P2 (Multimodal Advantage):**
If multimodal training (sequence + secondary structure) is used, then cross-task transfer efficiency will improve by ≥15% (measured as reduction in fine-tuning samples needed for 90% max performance).

**P3 (Contrastive Embedding Quality):**
If contrastive alignment with biological augmentations is used, then RNA embeddings will show higher functional clustering quality (NMI ≥ 0.8) compared to non-contrastive baselines (NMI ~0.6).

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any of the following occur:

1. **Primary Failure:** Hierarchical Mamba shows ≤5% improvement over flat Mamba on structure prediction (TM-score ≤ 0.68)

2. **Mechanism Failure:** Ablation studies show contrastive alignment provides no benefit over reconstruction loss (NMI difference < 0.1)

3. **Multimodal Failure:** Adding structure modalities provides no improvement over sequence-only (cross-task transfer unchanged within error margins)

4. **Baseline Failure:** HiMamba-CL performs worse than existing baselines (DGRNA, HydraRNA, Orthrus) on majority of BEACON tasks

### 1.7 SOTA Baseline

| Method | Dataset/Task | Performance | Year |
|--------|--------------|-------------|------|
| DGRNA | ncRNA classification | ~85% accuracy | 2024 |
| HydraRNA | RNA secondary structure F1 | 0.76 | 2025 |
| PlantRNA-FM | Genic annotation | 0.974 F1 | 2024 |
| Orthrus | mRNA property prediction | SOTA | 2024 |

**Target:** >84.5% on ncRNA tasks (2.5% improvement over mean)
**Falsification:** <80% (below SOTA mean)

### 1.8 Statistical Verification Design

**Sample Size:** n ≥ 25 runs per configuration
**Effect Size:** Cohen's d ≥ 0.6 (medium-large)
**Test:** Paired t-test with Bonferroni correction
**Significance:** α = 0.05 (one-tailed)
**Report:** Mean difference, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**Total Sub-Hypotheses:** 6 (2 + N where N=4)

**SH1 (Existence):**
"Does HiMamba-CL successfully learn unified RNA representations that capture both sequence and structure information?"
- Maps to: Primary prediction P1
- Verification: Empirical benchmark evaluation
- Critical: MUST PASS to proceed

**SH2 (Mechanism):**
"Is the proposed 4-step causal mechanism the actual explanation for performance gains?"
- Phase 2B decomposes into 4 sub-hypotheses:
  - H-M1: Hierarchical stacking → multi-scale patterns
  - H-M2: Multi-scale patterns → richer representations
  - H-M3: Contrastive alignment → modality-invariant embeddings
  - H-M4: Modality-invariance → better transfer
- Verification: Ablation studies for each link

**SH3 (Comparison):**
"Does HiMamba-CL outperform existing RNA FMs on BEACON benchmark?"
- Maps to: SOTA comparison, P2/P3
- Verification: Comparative empirical
- Critical: Determines publication readiness

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-HiMamba-CL-v1
- [x] Confidence: 0.87
- [x] H0 defined
- [x] Variables operationalized (10 variables)
- [x] Causal mechanism with evidence (N=4 steps)
- [x] Key tension identified + resolution
- [x] Assumptions with consequences (4 assumptions)
- [x] Testable predictions (P1 primary, P2/P3 secondary)
- [x] Falsification criteria (4 conditions)
- [x] Baselines: DGRNA, HydraRNA, Orthrus, PlantRNA-FM
- [x] SH1/SH2/SH3 ready

### Open Questions

1. **Resource Budget:** Exact GPU-hours for 100M param pre-training? (Est. 80-120h A100)
2. **Data Pipeline:** Zoonomia ortholog pair construction complexity?
3. **Tertiary Strategy:** Include from start or staged training?
4. **Verification Order:** SH1 gate first, or parallel ablations?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work (8 sources with full citations)

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
