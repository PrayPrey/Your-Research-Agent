# Phase 2B Input: BioRenorm Hypothesis Summary

**Date:** 2026-02-08
**Hypothesis ID:** H-BioRenorm-Gap3-RG
**Confidence:** 0.85 (High)
**Implementation Difficulty:** MEDIUM (acceptable)
**Status:** ✅ Ready for Phase 2B Verification Planning

---

## Executive Summary

**Main Hypothesis:**

A multimodal foundation model incorporating learnable renormalization (RG) operators inspired by statistical physics can bridge molecular, cellular, and tissue biological scales by discovering data-driven coarse-graining rules. Enhanced with skip connections and multi-stage training, BioRenorm achieves ≥0.7 correlation for molecular→tissue drug response prediction, outperforming standard hierarchical approaches by ≥10%.

**Core Innovation:**

First application of physics RG theory to biological scale transitions (molecular→cellular→tissue), using learnable operators with biological priors (pathway-aware pooling from KEGG/Reactome, conservation constraints for information/mass balance). Distinct from existing concatenation/attention approaches.

**Target Gap:** Gap 3 - Multimodal Foundation Models Bridging Molecular and Cellular Scales (P0 CRITICAL)

---

## Key Components

### Testable Predictions

1. **P1 (Primary)**: Molecular→tissue correlation **r ≥ 0.7**, **≥10% improvement** over hierarchical baseline
2. **P2**: Skip connections prevent error amplification, degradation **<10%** vs oracle
3. **P3**: Biological priors enable interpretability, **≥30% pathway alignment** (KEGG/Reactome)
4. **P4**: Multi-stage training achieves strong performance with **<10K fully-paired samples**
5. **P5**: RG operators outperform hierarchical transformer AND late fusion by **≥10%**

**Falsification**: Reject if baseline equivalence (≤5% difference), oracle gap >25%, pathway alignment <10%, skip dominance >90%, or data efficiency <70% of single-stage.

### Sub-Hypothesis Decomposition (Phase 2B Preview)

**SH1 - Existence**: RG operators discover conserved patterns (pathway alignment ≥30%, >baseline)
- **Timeline**: 2 months (Stage 1+2 training + analysis)

**SH2 - Mechanism**: Skip connections prevent error amplification (degradation <10% vs oracle)
- **Timeline**: 1 month (ablation studies)

**SH3 - Comparison**: RG outperforms hierarchical approaches (≥10% improvement vs both baselines)
- **Timeline**: 3 months (parallel training of 3 architectures)

**Dependencies**: SH1 ← FOUNDATION → SH2 ← ROBUSTNESS → SH3 ← ADVANTAGE

---

## Contributions

### Theoretical

**RG Formalization of Biological Scale Transitions**: First framework connecting physics RG concepts (coarse-graining, universality classes, scale invariance) to biological hierarchies (molecular→cellular→tissue). Defines learnable RG operators $\mathcal{R}_{\theta}$ with conservation constraints (information preservation, mass balance).

**Novel**: Biological universality classes (conserved modules across scales), scale-invariant features, emergent complexity formalization.

### Methodological

**Learnable RG Operators with Biological Priors**:
- Pathway-aware aggregation (respects gene ontology: KEGG, Reactome structure)
- Conservation constraints (information + mass balance regularization)
- Skip connections with learnable gating (prevents error amplification)
- Multi-stage training (Stage 1: separate pretraining, Stage 2: pairwise RG, Stage 3: end-to-end)

**Novel**: First integration of (1) RG framework, (2) biological pathway priors, (3) conservation constraints, (4) robustness via skip connections.

### Practical

**Drug Discovery Applications**:
- **In Silico Screening**: 90% cost reduction ($5M → $500K), 5x time reduction (6 months → 1 month)
- **CRISPR Prioritization**: 85% cost reduction ($1.5M → $200K), 2.3x time reduction (9 → 4 months)
- **RNA Therapeutic Design**: 60% cost reduction ($350K → $150K), 2x time reduction (6 → 3 months), 10x candidate exploration (100 → 1,000)

**Mechanistic Insights**: RG operators identify conserved biological modules (e.g., NF-κB motif → inflammatory genes → tissue inflammation).

---

## Key Related Work

| Work | Year | Cites | Relation | How We Differ |
|------|------|-------|----------|---------------|
| **Aevermann et al.** | 2025 | 0 | Foundation - Data standardization bottleneck | Multi-stage training addresses heterogeneity |
| **Yao et al. (Organoids)** | 2024 | 56 | Methodology - Validation platform | Use organoid data as ground truth |
| **Nguyen & Hy (Protein)** | 2023 | 22 | Methodology - Multimodal pretraining | Extend to cross-scale (mol+cell+tissue) |
| **Steurer et al.** | 2024 | 8 | Comparison - Multimodal transformers | RG coarse-graining vs cross-attention |
| **Liaw et al. (RG-DL)** | 2025 | N/A | Inspiration - RG for scale invariance | Apply to BIOLOGICAL scales with domain priors |
| **PAST** | 2025 | N/A | Comparison - Single-cell foundation model | Add molecular scale, RG operators vs late fusion |
| **FN-MVP** | 2025 | N/A | Comparison - Graph multi-scale | RG + pathway priors vs graph pooling |

**Gaps Addressed**: (1) No principled cross-scale mechanism, (2) No biological priors in scale transitions, (3) No cross-scale interpretability, (4) No molecular→tissue prediction for drug discovery.

---

## Experimental Design

**Dataset**: PRISM Repurposing organoid drug screening (~2.25M data points: 4,500 compounds × 500 organoid models)

**Arms**:
1. **BioRenorm** (RG + skip + priors)
2. **Hierarchical Transformer** (Swin-style, no RG)
3. **Late Fusion** (concatenation+MLP)
4. **Ablations**: RG only, skip only, no priors, no conservation

**Evaluation**:
- **Primary Metric**: Pearson r (molecular→tissue response)
- **Secondary**: Spearman ρ, MAE, Top-K precision, pathway alignment %, computational cost
- **Protocol**: 5-fold CV, paired t-test with Bonferroni correction (α=0.01), Cohen's d≥0.5

**Success Criteria**:
- r_BioRenorm ≥ 0.7
- (r_BioRenorm - r_baseline) / r_baseline ≥ 0.10 for BOTH baselines
- Pathway alignment ≥ 30%
- Degradation vs oracle < 10%

**Computational Budget**: ~15,000 GPU-hours (~$50K), 64 A100 GPUs, 40 days

---

## Phase 2B Readiness

### Checklist

- [x] **Hypothesis Clarity**: Core statement, variables, mechanism, assumptions, scope, predictions, falsification
- [x] **Contribution Specification**: Theoretical (RG formalization), methodological (pathway-aware operators), practical (drug discovery cost/time reduction)
- [x] **Related Work Mapped**: Foundation models, multimodal representations, multi-scale integration, physics-inspired ML, architectural patterns
- [x] **Experimental Design**: Dataset (PRISM), baselines (hierarchical transformer, late fusion), evaluation protocol (5-fold CV, statistical tests), success criteria
- [x] **Data Availability**: Stage 1 (PubChem, scRNA-seq atlases, TCGA), Stage 2 (CellPainting, spatial transcriptomics), Stage 3 (PRISM/DepMap organoids)
- [x] **Implementation Feasibility**: MEDIUM difficulty, ~3B params, 32-64 GPUs, ~$50K, anti-patterns ALL CLEAR

**Status**: ✅ **FULLY READY FOR PHASE 2B**

### Open Questions for Phase 2B

1. **P1-CRITICAL**: Optimal conservation constraint strength ($\lambda_{\text{info}}$, $\lambda_{\text{mass}}$)?
2. **P1-CRITICAL**: Optimal skip connection gating mechanism (learnable sigmoid, hard threshold, attention-based)?
3. **P2-HIGH**: Optimal RG operator depth (2, 3, 4, 5 layers)?
4. **P2-HIGH**: Pathway database choice (KEGG vs Reactome vs GO vs ensemble)?
5. **P3-MEDIUM**: Generalization to novel modalities (peptides, microbiome therapies)?
6. **P3-MEDIUM**: Failure mode characterization (low data, high noise, novel cell types, adversarial perturbations)?
7. **P4-LOW**: Comparison with diffusion-based alternatives (hierarchical diffusion)?

---

## Next Steps

### Immediate: Proceed to Phase 2B - Verification Planning

**Phase 2B Objectives**:
1. Decompose BioRenorm hypothesis into detailed sub-hypotheses (SH1-Existence, SH2-Mechanism, SH3-Comparison)
2. Establish verification plans for each sub-hypothesis with specific experiments, datasets, success criteria
3. Prioritize experiments based on dependencies (SH1 must pass before SH2, SH2 before SH3)
4. Define success criteria and failure modes (when to revise architecture vs reject hypothesis)
5. Create verification roadmap with timelines (SH1: 2 months, SH2: 1 month, SH3: 3 months)

**Expected Phase 2B Output**: `02b_verification_plan.md` with:
- Detailed experimental protocols for each sub-hypothesis
- Resource allocation (GPU budgets, timeline, personnel)
- Success/failure decision trees
- Risk mitigation strategies for each failure mode
- Integration plan for sub-hypothesis results → main hypothesis validation

### Subsequent Phases

**Phase 2C - Experiment Design**:
- Generate Level 1.5 experiment brief for BioRenorm implementation
- Specify architectures (RG operator equations, skip connection details), datasets (exact train/val/test splits), baselines (hyperparameters), evaluation metrics (statistical test code)

**Phase 3 - Implementation Planning**:
- Generate PRD, Architecture document, PRP (Project Requirements Plan), Archon tasks
- Detailed technical specifications for BioRenorm development (PyTorch code structure, data pipelines, training loops)

**Phase 4 - Coding & Validation**:
- Implement BioRenorm with Coder-Validator loop
- Execute experiments, validate sub-hypotheses (SH1→SH2→SH3)
- Produce `04_validation.md` report with results

**Phase 5 - Paper Writing**:
- Transform research artifacts (Phase 0-4) into academic paper
- Target venues: NeurIPS 2024 AIDrugX Workshop (ML Track + Application Track), ICLR 2025, Nature Machine Intelligence

---

**File Generated**: 2026-02-08 (YOLO Mode - Fully Automated)
**Research Topic**: AI for Emerging Drug Modalities (RNA therapeutics, cell/gene therapies, protein engineering)
**Gap Addressed**: Gap 3 - Multimodal Foundation Models Bridging Molecular and Cellular Scales (P0 CRITICAL)
**Outcome**: ✅ FEASIBLE Hypothesis (Confidence 0.85, Implementation Difficulty MEDIUM)

**Phase 2A-Extended Duration**: ~30 minutes (automated execution)
**Auto-Detected FEASIBLE Round**: Round 1 (from `02a_validated_hypotheses.md`)
**Input Source**: `02a_round_1_discussion.md` (Extended Workflow Input section)
**Reference Documents**: Phase 0 (`00_brainstorm_session.md`), Phase 1 (`01_targeted_research.md`), Phase 2A (`02a_validated_hypotheses.md`, `02a_round_1_discussion.md`)

---

*Ready for Phase 2B: Hypothesis Verification Planning*
*Researcher: Pray*
*YouRA Pipeline: Phase 2A-Extended → Phase 2B*
