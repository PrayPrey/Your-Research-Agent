# Phase 2B Summary: Clarified Hypothesis

**Hypothesis ID:** H-GAP2-R1-HCMF
**Confidence:** 0.89 (HIGH)
**Date:** 2026-02-06
**Status:** ✅ READY FOR PHASE 2B

---

## Core Hypothesis

A **hierarchical causal mediation framework** using genomic variants (SNPs, indels) as instrumental variables, combined with pathway-constrained graph neural networks and counterfactual reasoning, can trace mechanistically interpretable causal pathways from genetic polymorphisms through multi-omics molecular states (genotype → transcriptome → proteome → pathway activity) to patient-specific drug response predictions while quantifying causal uncertainty at each biological scale.

**Alternative Hypothesis (H0):** Standard approaches (direct GWAS, SHAP interpretability, single-scale MR) provide equivalent or superior performance.

---

## Variables

| Type | Name | Measurement | Scale |
|------|------|-------------|-------|
| **Independent** | Genomic Variants | Genotyping arrays, WGS | {0,1,2} dosage |
| **Mediators** | Transcriptome → Proteome → Pathway Activity | RNA-seq, MS, Computed | Continuous |
| **Dependent** | Drug Response (Efficacy, Toxicity) | In vitro/clinical assays | Continuous/Binary |
| **Confounders** | Age, Disease Stage, Comorbidities | Medical records | Various |

**Control:** Mendelian randomization leverages random allele assignment at conception, controlling confounding via IV analysis + sensitivity analyses (MR-Egger, weighted median, MR-PRESSO).

---

## Testable Predictions

**P1 (Mediation):** Proportion mediated ≥30% for ≥70% of drugs, pathway enrichment FDR <0.05, PharmGKB overlap ≥60%

**P2 (Prediction):** Drug response AUC ≥0.75 or R² ≥0.3, calibration error <0.1

**P3 (Causal Validity):** IV tests pass (F>10 for ≥80% variants, Sargan p>0.05 for ≥70% models, MR sensitivity concordance ≥80%)

**P4 (Interpretability):** Expert ratings ≥4/5 for ≥60% cases, significantly higher than SHAP (p<0.05)

**P5 (Counterfactuals):** Intervention predictions agree with experimental perturbations ≥70%

**Falsification:** Hypothesis REJECTED if ≥2 of the following occur:
- F1: Proportion mediated <30% for >50% drugs
- F2: Pathway enrichment FDR >0.05 or PharmGKB overlap <40%
- F3: Prediction AUC <0.65 or R² <0.15
- F4: IV validity tests fail (F<10 for >30% variants OR Sargan p<0.05 for >40% models)
- F5: Counterfactual predictions agree <50% with perturbation data

---

## Key Contributions

**Theoretical:**
1. Hierarchical causal mediation theory for multi-scale biological systems
2. IV validity conditions for multi-omics causal inference
3. Pathway-constrained causal discovery formalization

**Methodological:**
1. Graph Attention Networks with biological pathway topology constraints (KEGG + Reactome + STRING + GO)
2. Multi-scale Mendelian randomization pipeline (automated workflow)
3. Causal counterfactual explanation algorithm (interventional calculus + natural language generation)
4. Comprehensive robustness framework (MR sensitivity + Bayesian UQ + cross-cohort validation)

**Practical:**
1. Pharmacogenomics decision support (patient-specific pathway identification)
2. Regulatory evidence generation (mechanistic causal evidence for FDA)
3. Combination therapy design (causal network synergy identification)
4. Benchmark datasets (GDSC, UK Biobank, PharmGKB with standardized protocols)

---

## SOTA Baselines

1. **Direct GWAS:** Standard genome-wide association (expected AUC 0.60-0.70, no interpretability)
2. **SHAP-XGBoost:** Correlational interpretability (expected AUC 0.70-0.80, no causal guarantees)
3. **Standard MR:** Single-scale causal inference (valid causality, no pathway interpretability)
4. **GSEA + Linear Models:** Pathway enrichment (FDR 0.01-0.10, moderate prediction R² 0.2-0.3)

**Success:** Outperform ≥3/4 baselines on ≥1 primary metric while competitive (within 10%) on others.

---

## Implementation Specifications

**Data Sources:**
- GDSC: ~1000 cancer cell lines (genomics + RNA-seq + proteomics subset + drug response)
- UK Biobank: ~500,000 participants (genotype + proteomics subset + clinical records)
- PharmGKB: Curated pharmacogenomic variants and drug-gene relationships

**Architecture:**
- **Layer 1:** Mendelian randomization (genomic variants as IVs, sensitivity analyses)
- **Layer 2:** Graph Attention Networks (pathway-constrained, ensemble databases)
- **Layer 3:** Hierarchical mediation analysis (genotype → transcriptome → proteome → pathway → drug response)
- **Layer 4:** Counterfactual reasoning (interventional calculus on learned DAG)
- **Uncertainty:** Bayesian neural networks or conformal prediction

**Compute:**
- Hardware: GPU cluster (4×V100), distributed training (PyTorch DDP)
- Estimated budget: 200 GPU-hours (~$500 cloud cost)
- Scalability: Embarrassingly parallel across drugs (100 drugs × 2 GPU-hours)

**Evaluation:**
- Internal: 5-fold cross-validation on GDSC
- External: Train GDSC, test UK Biobank
- Temporal: Train PharmGKB <2020, test ≥2020
- Sensitivity: 4 analyses (pathway databases, GNN architecture, IV selection, unmeasured confounding)

**Fallback Strategy:**
- If pathway-constrained GNN fails (pathway recall <0.4): Revert to standard GSEA + linear mediation analysis
- Estimated performance drop: 10-15% on pathway enrichment metrics

---

## Phase 2B Decomposition Preview

**SH1 (Existence):** Do genomic variants causally affect drug response?
- Verify: IV validity tests (F>10, Sargan p>0.05) + significant total effects (p<0.05 Bonferroni-corrected) for ≥70% drugs
- Data: GDSC (1000 cell lines × 100 drugs × ~10k SNPs)

**SH2 (Mechanism):** Do biological pathways mediate the genomic effect?
- Verify: Proportion mediated ≥30% for ≥70% drugs, pathway enrichment FDR <0.05, PharmGKB overlap ≥60%
- Data: GDSC multi-omics (genomics + RNA-seq + proteomics subset)

**SH3 (Comparison):** Does the framework outperform baselines?
- Verify: Outperform ≥3/4 baselines on ≥1 criterion (causal validity, interpretability, prediction) while competitive on others
- Data: 20% held-out GDSC + UK Biobank external validation

---

## Open Questions for Phase 2B

1. **Multi-Omics Data Completeness:** How to handle missing modalities? (Current plan: modality dropout + transfer learning)
2. **Pathway Database Bias:** Do curated databases miss novel mechanisms? (Plan: ensemble + data-driven edge learning)
3. **Causal Graph Misspecification:** Robustness to DAG errors? (Plan: multi-algorithm ensemble + perturbation validation)
4. **Cross-Cohort Generalization:** Cell lines → population cohorts? (Plan: transfer learning + outcome harmonization)
5. **Compute Scalability:** 1000+ drugs feasible? (Plan: distributed training + dimensionality reduction)
6. **Clinical Actionability:** Are pathway explanations useful? (Plan: user studies with oncologists)

---

## Related Work & Novelty

**Key Building Blocks:**
1. de la Fuente et al. (2025): Pathway-space causal learning (0 citations) - *we extend to drug response + hierarchical multi-scale*
2. Yazdani et al. (2022): MR → causal networks review (26 citations) - *we implement hierarchical IV analysis + pharmacogenomics application*
3. Noviandy et al. (2024): SHAP interpretability for QSAR (18 citations) - *we provide causal (not correlational) interpretability*
4. Zhu et al. (2024): Graph-based DTI (13 citations) - *we extend to genomic variants → drug response pathways*

**Novelty:** First framework combining genomic IVs + pathway-constrained GNNs + counterfactual reasoning for end-to-end causal inference from genetic variants to clinical drug response.

**Gap Addressed:** Gap 2 from Phase 1 - "No end-to-end framework traces causal pathways from genomic variants through molecular mechanisms to drug response predictions with both statistical rigor and biological interpretability."

---

## Timeline & Resources

**Estimated Timeline:**
- Phase 2B (Planning): 2-3 weeks
- Phase 2C (Experiment Design): 3-4 weeks
- Phase 3 (Implementation Planning): 4-6 weeks
- Phase 4 (Coding & Validation): 11-15 weeks
- **Total:** 20-24 weeks

**Key Risks & Mitigations:**
1. IV assumptions violated → MR sensitivity analyses
2. Pathway databases incomplete → Ensemble + data-driven edges
3. Error propagation across stages → Bayesian UQ + per-stage validation
4. de la Fuente methodology unproven → Fallback to GSEA + linear mediation

---

**Judge's Assessment (Phase 2A):**

| Criterion | Score | Rationale |
|-----------|-------|-----------|
| Theoretical Validity | 9/10 | Strong MR + causal DAG foundation, minor IV assumption uncertainty |
| Technical Feasibility | 9/10 | All components implementable, 200 GPU-hours reasonable |
| Gap Resolution | 9/10 | Directly addresses end-to-end causality + interpretability gap |
| Novelty & Differentiation | 8/10 | Integration novelty (HIGH-MODERATE), components known |
| Refinement Quality | 10/10 | All Skeptic concerns addressed, complete specifications |
| **AVERAGE** | **8.9/10** | **STRONG FEASIBILITY** |

**Confidence:** 0.89
**Recommendation:** ✅ **PROCEED TO PHASE 2B** (Hypothesis Verification Planning)

---

*Generated: 2026-02-06*
*Source: Phase 2A Round 1 FEASIBLE hypothesis*
*Full Document: 02a_extended_hypothesis_full.md*
*Next Phase: Phase 2B - Hypothesis Verification Planning (/phase2b-planning)*
