# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-EPOEA-v1
**Confidence Level:** 0.78

**Main Hypothesis:**
Under conditions of sparse experimental biomolecular data with heterogeneous protein families, if evidential deep learning with Normal-Inverse-Gamma (NIG) output layers is applied to molecular property prediction using ESM-2 structural embeddings, then the model will produce calibrated uncertainty estimates (ECE > 0.85) that enable efficient experimental prioritization (40% reduction in validation candidates) because evidential neural networks decompose aleatoric and epistemic uncertainty while hierarchical protein family priors share information across related proteins.

**Alternative Hypothesis (H0):**
Evidential deep learning with NIG output layers does not produce better-calibrated uncertainty estimates than standard regression approaches (deep ensembles, MC dropout) for biomolecular property prediction, and uncertainty-guided prioritization does not improve experimental efficiency compared to random selection or prediction-score ranking.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Oracle architecture | Independent | Evidential (NIG output) vs Standard (point estimate + ensemble/dropout) | Binary: EPOEA vs Baseline |
| Hierarchical prior structure | Independent | Pfam-based protein family groupings with shared uncertainty parameters | None / Flat / Hierarchical |
| Calibration score (ECE) | Dependent | Expected Calibration Error on held-out experimental binding data using 10 equal-width bins | 0.0 (perfect) to 1.0 (worst); Target: < 0.15 |
| Experimental efficiency | Dependent | % reduction in candidates needed to identify top-K binders via uncertainty ranking | 0-100%; Target: ≥ 40% |
| Cross-family transfer retention | Dependent | Performance retention when applied to unseen protein family | 0-100%; Target: ≥ 80% |
| Model backbone | Controlled | ESM-2 650M protein language model | Fixed |
| Training data | Controlled | PDBbind v2020 refined set (~5,000 complexes) + BindingDB curated subset | Fixed |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: ESM-2 Embeddings → Rich Structural Representations
   ↓
Step 2: NIG Evidential Layer → Calibrated Uncertainty Decomposition
   ↓
Step 3: Calibrated Uncertainty → Efficient Experimental Prioritization
   ↓
Outcome: Reduced experimental validation costs with maintained hit rate
```

**Step 1: Structural Representation**
- ESM-2 protein language model captures evolutionary and structural information from protein sequences
- Provides informative input features for property prediction
- Evidence: ESM-2 (Meta AI) demonstrated state-of-the-art performance on structure prediction

**Step 2: Uncertainty Quantification**
- Normal-Inverse-Gamma output parameterization enables direct estimation of both prediction mean and uncertainty
- Natural decomposition into aleatoric (measurement noise) and epistemic (model ignorance) components
- Evidence: EviDTI (Zhao 2025) achieves calibrated uncertainty in DTI; Busk et al. show calibrated molecular property prediction

**Step 3: Experimental Prioritization**
- High-confidence predictions prioritized for experimental validation
- Low epistemic uncertainty indicates model has sufficient knowledge
- Evidence: EviDTI case study identified novel tyrosine kinase modulators via uncertainty-guided selection

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Busk et al. (Molecular MPNNs) | Graph embeddings + ensemble calibration achieves calibrated molecular predictions | Strong |
| Step2 → Step3 | EviDTI (Zhao 2025) | Evidential DL prioritizes high-confidence DTI predictions for validation | Strong |
| Step3 → Outcome | EviDTI Case Study | Uncertainty-guided selection identified FAK/FLT3 modulators | Medium |

**Key Tension:**
- **Tension:** EviDTI (Zhao 2025) demonstrates evidential DL for classification (DTI binary prediction), but EPOEA requires continuous regression (binding affinity values). Busk et al. use ensembles rather than evidential DL for molecular property regression.
- **Resolution:** This verification plan tests whether evidential NIG layers maintain calibration properties when adapted from classification to continuous regression tasks. SH2-M2 specifically addresses this mechanism validation.

### 1.4 Key Assumptions

1. **Uncertainty Decomposition Assumption**
   - Experimental uncertainty in biomolecular measurements decomposes into aleatoric (measurement noise, ~0.5-1.0 kcal/mol for binding affinity) and epistemic (model knowledge gaps) components
   - Evidence: Hertäg 2025 shows neural prediction-error circuits naturally separate these uncertainty types
   - **If violated:** Model uncertainty estimates conflate noise and ignorance, reducing prioritization effectiveness

2. **Methodology Transfer Assumption**
   - Evidential deep learning methodology transfers from classification (EviDTI) to continuous property regression without fundamental loss of calibration properties
   - Evidence: NIG distribution is the conjugate prior for Gaussian likelihood, theoretically sound for regression
   - **If violated:** Calibration degrades significantly in regression setting, requiring alternative uncertainty methods

3. **Hierarchical Prior Usefulness Assumption**
   - Hierarchical protein family structure (Pfam taxonomy) provides useful inductive bias for uncertainty sharing
   - Evidence: Protein families share evolutionary and functional properties that influence binding behavior
   - **If violated:** Hierarchical priors add complexity without improving calibration or transfer

4. **Data Quality Assumption**
   - PDBbind and BindingDB experimental data quality is sufficient for training calibrated models
   - Evidence: PDBbind refined set is curated for high-quality crystal structures and binding measurements
   - **If violated:** Noisy training labels prevent proper calibration; may require data filtering or noise modeling

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Binding affinity prediction (Kd, Ki, IC50) for protein-ligand interactions
- Protein stability prediction (ΔΔG) for mutation effects
- Property prediction tasks with experimental ground truth data
- Protein families with sufficient representation in training data (≥50 examples)

**Where Hypothesis Does NOT Apply:**
- Completely novel protein folds without family assignment (orphan proteins)
- Properties with no experimental data available (purely computational targets)
- Kinetic properties (kon, koff) that require time-resolved measurements
- Multi-target selectivity optimization (requires joint uncertainty modeling)

**Known Limitations:**
- Calibration quality depends on training data diversity across protein families
- Hierarchical prior specification requires domain expertise (Pfam mapping)
- Initial validation limited to single protein family before generalization
- Computational overhead of evidential head (~10-20% additional inference time)

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Calibration Target)**:
EPOEA will achieve Expected Calibration Error (ECE) < 0.15 on held-out experimental binding affinity data.

*Measurement*:
- ECE calculated using 10 equal-width confidence bins
- Evaluated on held-out test set (20% of PDBbind refined set)
- Statistical test: ECE < 0.15 with 95% confidence interval

*Basis*:
Domain standard for well-calibrated models. EviDTI achieves calibrated predictions for DTI classification.

*Success Criteria for Phase 2B*:
- Primary: ECE < 0.15
- Falsification: ECE > 0.30 triggers rejection

**Secondary Predictions:**

**P2 (Experimental Efficiency)**:
Uncertainty-guided candidate selection will achieve ≥40% reduction in candidates needed to identify top-10% binders compared to random selection.

*Measurement*:
- Calculate area under the oracle curve (AUOC) for uncertainty-ranked vs random selection
- Efficiency = (Random candidates - Uncertainty candidates) / Random candidates × 100%

**P3 (Cross-Family Transfer)**:
When applied to an unseen protein family with hierarchical priors, EPOEA will retain ≥80% of calibration performance compared to in-family evaluation.

*Measurement*:
- Train on N-1 protein families, evaluate on held-out family
- Retention = ECE(in-family) / ECE(transfer) × 100%

**Falsification Criteria:**
The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure**: ECE > 0.30 on held-out test set (severely miscalibrated)

2. **Mechanism Failure**: Evidential NIG layer produces uncertainty estimates uncorrelated with prediction error (Spearman ρ < 0.3)

3. **Efficiency Failure**: Uncertainty-guided selection performs worse than random (negative efficiency gain)

4. **Transfer Failure**: Cross-family transfer retention < 50% (hierarchical priors ineffective)

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

*Not applicable - Absolute performance validation mode*

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (Cohen's d): ~0.7 (medium-large) for calibration improvement
- Required test samples: n ≥ 500 protein-ligand complexes
- Statistical power: 0.8

**Test Specification:**
- Method: Bootstrap confidence intervals for ECE (1000 resamples)
- Significance level: α = 0.05
- Report format: ECE mean, 95% CI, comparison to baseline methods

**Baseline Comparisons:**
- Deep Ensemble (5 models): Standard uncertainty baseline
- MC Dropout (50 samples): Approximate Bayesian baseline
- Single Model + Temperature Scaling: Post-hoc calibration baseline

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does EPOEA produce calibrated uncertainty estimates (ECE < 0.15) on held-out experimental binding affinity data?"
- Maps to: Primary prediction P1
- Verification type: Empirical measurement
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the evidential NIG layer the actual cause of calibrated uncertainty decomposition?"
- Maps to: Causal mechanism (3 sub-hypotheses)
  - H-M1: ESM-2 embeddings capture property-relevant structural information
  - H-M2: NIG layer produces calibrated uncertainty in regression setting
  - H-M3: Uncertainty ranking correlates with experimental success
- Verification type: Causal analysis with ablation studies
- Critical: Determines explanatory power

**SH3 (Comparison):**
"Does EPOEA outperform baseline uncertainty methods (deep ensembles, MC dropout, temperature scaling) on calibration and efficiency metrics?"
- Maps to: Secondary predictions P2, P3
- Verification type: Comparative empirical
- Critical: Determines practical value

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-EPOEA-v1
- [x] Confidence level specified: 0.78
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (3 steps, evidence table complete)
- [x] Causal chain length (N=3) determined and stored
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (3 total, primary marked)
- [x] Falsification criteria are defined (4 criteria)
- [x] Baselines are identified for comparison (3 baselines)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Data Availability:** Is PDBbind v2020 refined set sufficient (~5,000 complexes) or should BindingDB be included for diversity? What is the Pfam coverage?

2. **Technical Feasibility:** What is the computational overhead of evidential NIG layer compared to standard regression? Does it fit within GPU memory constraints for ESM-2 650M backbone?

3. **Priority Verification Order:** Should SH1 (existence) be verified first to establish basic feasibility, or should SH2-M2 (NIG calibration in regression) be prioritized as the highest-risk assumption?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-12*
