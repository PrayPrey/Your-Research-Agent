# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-UniGenBench-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under conditions of evaluating generative biomolecule models across proteins, small molecules, and antibodies, **if** a hierarchical three-tier benchmark framework with modality-aware metrics and optional uncertainty quantification is applied, **then** cross-modal evaluation consistency and reproducibility will significantly improve (Kendall's tau > 0.7, CV < 10%), **because** the hierarchical separation of validity, quality, and function evaluation with standardized protocols eliminates the inconsistencies caused by fragmented single-modality evaluation approaches.

**Alternative Hypothesis (H0):**
There is no significant relationship between benchmark architecture (hierarchical vs. flat) and evaluation consistency/reproducibility. Specifically: (a) Hierarchical three-tier evaluation does not improve failure mode diagnosis compared to single-tier evaluation, (b) Modality-aware metrics do not provide better discrimination than generic metrics, (c) Bootstrap uncertainty quantification does not improve cross-lab reproducibility.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Benchmark architecture | Independent | Three-tier hierarchical framework (Tier 1: structural validity, Tier 2: quality metrics, Tier 3: functional verification) vs flat single-tier evaluation | Binary: Hierarchical / Flat |
| Uncertainty quantification | Independent | Bootstrap uncertainty estimation with 100+ resamples (Rigorous mode) vs point estimates only (Quick mode) | Binary: Present / Absent |
| Evaluation mode | Independent | Quick mode (~1x compute) vs Rigorous mode (~10x compute with confidence intervals) | Binary: Quick / Rigorous |
| Cross-modal evaluation consistency | Dependent | Kendall's tau correlation of model rankings across proteins, molecules, antibodies | Target: tau > 0.7 |
| Reproducibility | Dependent | Inter-lab agreement measured by coefficient of variation (CV) of metric scores | Target: CV < 10% |
| Test datasets | Controlled | PDB (proteins, temporal cutoff 2024), ChEMBL (molecules), SAbDab (antibodies) with fixed random seeds | Fixed across experiments |
| Metric implementations | Controlled | RDKit 2024.03, ESMFold 1.0, DeepChem 2.8 with pinned versions | Fixed across experiments |

### 1.3 Causal Mechanism

```
Step 1: Hierarchical Tier Separation (Validity -> Quality -> Function)
    |
    [Enables systematic failure diagnosis]
    |
Step 2: Modality-Aware Metric Selection
    |
    [Provides domain-specific evaluation relevance]
    |
Step 3: Uncertainty Quantification + Standardized Protocols
    |
    [Produces reproducible cross-modal rankings]
    |
OUTCOME: Improved evaluation consistency and reproducibility
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 -> Step 2 | FoldBench (2025) | 9 distinct task categories enable precise identification of model weaknesses; antibody prediction failure >50% | Strong |
| Step 2 -> Step 3 | GEMv2 (Gehrmann et al., 2022) | Modular infrastructure for 40+ datasets shows domain-specific metrics outperform generic metrics | Strong |
| Step 3 -> Outcome | Rainio et al. 2024 (832 citations) | Bootstrap confidence intervals enable statistically valid model comparisons across domains | Strong |
| Foundation | SzCORE (Dan et al., 2024) | Standardization reduced EEG seizure detection variance by establishing unified formats, metrics, protocols | Strong |

**Key Tension:**
- **Tension:** SzCORE demonstrates standardization success in a single domain (EEG), but UniGenBench targets cross-modal evaluation where modality-specific metrics may conflict
- **Resolution:** Phase 2B will test whether modality-aware Tier 1 metrics maintain independence while Tier 2-3 metrics allow fair cross-modal comparison through normalized rankings

### 1.4 Key Assumptions

1. **Existing metrics are valid quality proxies**
   - Assumption: pLDDT, QED, TM-score, etc. meaningfully correlate with experimental biomolecule quality
   - Evidence: CASP validation, widespread adoption in ProteinBench/MolGenBench
   - *If violated:* The benchmark measures computation artifacts, not biological relevance

2. **Modality-specific validity is computationally definable**
   - Assumption: Structural validity rules can be programmatically verified
   - Evidence: RDKit, ESMFold, and antibody numbering tools exist
   - *If violated:* Tier 1 becomes subjective/inconsistent

3. **Community adoption follows friction reduction**
   - Assumption: Researchers will adopt standardized protocols if they simplify workflows
   - Evidence: GEMv2 achieved 40+ dataset adoption
   - *If violated:* UniGenBench becomes an unused academic artifact

4. **Bootstrap uncertainty is appropriate for benchmark metrics**
   - Assumption: Non-parametric bootstrap provides valid confidence intervals
   - Evidence: Rainio et al. 2024 recommends bootstrap for ML model comparison
   - *If violated:* Uncertainty estimates are misleading

### 1.5 Scope & Boundaries

**Applies to:**
- Generative models producing 3D biomolecular structures (proteins, small molecules, peptides, antibodies)
- Research groups seeking reproducible, comparable benchmark results

**Does NOT apply to:**
- Sequence-only generation (no 3D structure)
- Genomics, transcriptomics, or other non-molecular modalities
- Real-time evaluation needs (Rigorous mode requires ~10x compute)

**Known Limitations:**
- Tier 3 functional verification depends on sparse experimental data
- Antibody evaluation metrics are less mature than protein/molecule metrics
- Uncertainty estimation adds ~10x computational overhead

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Evaluation Consistency via Hierarchical Architecture)**:
If models are evaluated with UniGenBench's hierarchical three-tier framework, then model rankings will show higher consistency across independent evaluations compared to flat single-tier evaluation.

*Measurement*:
- Kendall's tau correlation: tau > 0.7 with UniGenBench vs tau < 0.5 with existing methods
- Inter-rater reliability (ICC) > 0.8

*Success Criteria for Phase 2B*:
- Primary: Kendall's tau > 0.7 for model rankings across 3+ independent evaluations
- Falsification: tau <= 0.5 indicates hierarchical structure provides no consistency benefit

**Secondary Predictions:**

**P2 (Failure Mode Diagnosis)**:
If hierarchical evaluation is used, failure modes will be classified with >90% precision/recall.

**P3 (Uncertainty Reveals Instability)**:
If bootstrap uncertainty is applied, at least 20% of models will show ranking reversals vs point estimates.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure**: Kendall's tau <= 0.5 for cross-evaluation consistency
2. **Mechanism Failure**: Hierarchical tiers show >0.8 correlation (collinearity)
3. **Adoption Failure**: Zero external lab adoption within 12 months

### 1.7 SOTA Baseline (Optional)

*Not applicable - benchmark framework creation, not SOTA performance comparison*

### 1.8 Statistical Verification Design

**Sample Size**: n >= 30 models across 3 modalities
**Statistical Test**: Permutation test for Kendall's tau, alpha = 0.05
**Bootstrap**: 1000 resamples for CI estimation
**Multi-site**: 3+ independent sites, CV < 10% threshold

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does UniGenBench's hierarchical evaluation produce measurably different results from flat single-tier evaluation?"
- Verification: Empirical comparison
- Critical: MUST PASS

**SH2 (Mechanism):**
"Is the three-step causal mechanism the actual cause of improved consistency?"
- Decomposes to 3 sub-hypotheses (H-M1, H-M2, H-M3) based on N=3 causal chain
- Verification: Ablation study

**SH3 (Comparison):**
"Does UniGenBench outperform existing benchmarks (ProteinBench, MolGenBench) in cross-modal evaluation?"
- Verification: Comparative empirical

**Total Sub-Hypotheses:** 5 (SH1 + 3 mechanism + SH3)

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-UniGenBench-v1
- [x] Confidence level: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] All variables operationalized with evidence
- [x] Causal mechanism with evidence (N=3 steps)
- [x] Key tension identified with resolution
- [x] Assumptions list consequences if violated
- [x] 3 testable predictions (primary marked)
- [x] Falsification criteria defined (3 criteria)
- [x] Baselines identified (ProteinBench, MolGenBench, FoldBench)
- [x] SH1, SH2, SH3 clear starting points

### Open Questions

1. **Resource Requirements:** Compute for Rigorous mode (100+ resamples x 30+ models x 3 modalities)?

2. **Data Availability:** SAbDab antibody structures sufficient for robust benchmarking?

3. **Priority Order:** Test SH1 first with minimal viable benchmark, or implement all tiers first?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
