# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-EVTCFM-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under standard climate simulation conditions, if Physics-Constrained Flow Matching (PCFM) is applied to pretrained climate flow models with EVT-parameterized tail guidance, then generated extreme climate events will satisfy hard conservation laws (energy, mass, moisture) to numerical precision (< 10⁻⁶) AND accurately represent GPD tail distributions (QQ-plot R² > 0.95), because PCFM enforces continuous physics-based corrections during the flow ODE integration while EVT parameters guide sampling toward statistically correct extreme tails.

**Alternative Hypothesis (H0):**
There is no significant improvement in either conservation law satisfaction or tail distribution accuracy when applying PCFM + EVT guidance compared to unconstrained flow-matching generation. The additional computational overhead of constraint projection provides no measurable benefit for extreme climate event generation.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| PCFM constraint projection | Independent | Binary: enabled/disabled during flow sampling; measured by number of Newton iterations per ODE step | 2-3 iterations/step |
| EVT tail guidance (ξ, σ, μ) | Independent | GPD parameters fit from historical extreme events; threshold selection via mean residual life plot | ξ ∈ [-0.5, 0.5], σ > 0, μ = 95th percentile |
| Constraint tolerance | Independent | Acceptance threshold for conservation law violations | 10⁻⁴ to 10⁻⁸ |
| Conservation law violation | Dependent | L2 norm of constraint residual at final timestep | Target: < 10⁻⁶ |
| Tail distribution accuracy | Dependent | QQ-plot linearity R², KS-statistic vs fitted GPD | Target: R² > 0.95, KS < 0.1 |
| Spatial coherence | Dependent | Variogram correlation with observed extreme events; Moran's I | Target: r > 0.8, I > 0.6 |
| Base flow model | Controlled | Pretrained climate flow-matching model (ClimateDiffuse or ArchesWeatherGen) | Fixed weights, same architecture |
| Training data | Controlled | ERA5/CMIP6 reanalysis at fixed resolution | 0.25° or 1°, 1979-2020 |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: PCFM Constraint Projection → Conservation Law Satisfaction
        (Newton iterations project flow onto constraint manifold)
             ↓
Step 2: Conservation Law Satisfaction → Physically Plausible Intermediate States
        (Energy/mass/moisture conservation ensures valid physics)
             ↓
Step 3: EVT Tail Parameters → Tail Distribution Guidance
        (GPD parameters condition generation toward extreme tails)
             ↓
Step 4: Tail Guidance + Physical States → Physically Consistent Extreme Events
        (Combined mechanism: physically valid AND statistically correct)
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | PCFM (Utkarsh et al. 2025) | Zero-shot constraint enforcement achieves exact satisfaction for PDEs | Strong |
| Step2 → Step3 | Energy-consistent interpolants (Mücke & Sanderse 2025) | Physics embedding maintains stability for 10x longer rollouts | Strong |
| Step3 → Step4 | Peard & Hall 2023 | EVT+GAN captures spatial coherence in compound hazards | Medium |
| Step4 → Outcome | Lin et al. 2024 | Climate-invariant features improve OOD robustness | Medium |

**Key Tension:**
- **Tension:** PCFM tested on small-scale PDEs (100s DOFs), but climate grids have 10⁵-10⁶ DOFs
- **Resolution:** Patch-based constraint projection with progressive validation from low to high resolution

### 1.4 Key Assumptions

1. **Conservation laws are differentiable** - Evidence: NeuralGCM, PCFM for PDEs
   - *If violated:* Must switch to soft penalty methods

2. **EVT applicability to climate extremes** - Evidence: Peard & Hall 2023, extensive EVT literature
   - *If violated:* Must explore alternative tail models

3. **Zero-shot inference capability** - Evidence: PCFM core contribution
   - *If violated:* Requires full model retraining; loses practical advantage

4. **Acceptable computational overhead** - Evidence: PCFM reports 1.5-3x overhead
   - *If violated:* Method impractical for operational use; optimize projection

### 1.5 Scope & Boundaries

**Applies to:**
- Climate variables with conservation laws: temperature, precipitation, pressure, humidity
- Resolution: 0.25° to 2°; Extreme events: precipitation extremes, heat waves, cold snaps
- Flow models: ClimateDiffuse, ArchesWeatherGen, any flow-matching climate model

**Does NOT apply to:**
- Discrete phenomena without continuous physics (e.g., tropical cyclone tracks)
- Variables without conservation laws (e.g., vegetation indices)

**Limitations:**
- Patch boundary artifacts; EVT requires >30 threshold exceedances; hierarchical constraint conflicts

### 1.6 Testable Predictions

**Primary Prediction (P1 - Conservation):**
Conservation law violations < 10⁻⁶ when PCFM enabled
- *Falsification:* Violation > 10⁻³

**Secondary Predictions:**
- **P2 (Tail Accuracy):** QQ-plot R² > 0.95, KS < 0.1 with EVT guidance
- **P3 (Combined):** Joint satisfaction of P1 AND P2 without degradation

**Falsification Criteria:**
1. Conservation violation > 10⁻³
2. Newton iterations fail to converge for >10% of samples
3. QQ-plot R² < 0.8 OR KS > 0.2
4. Combined PCFM+EVT performs worse than either alone

### 1.7 SOTA Baseline (Optional)

**Mode:** Absolute Performance (Novel Capability Validation)

| Baseline | Lacks | EVT-CFM Advantage |
|----------|-------|-------------------|
| Unconstrained diffusion | Physics | Conservation 10⁻⁶ vs 10⁻² |
| Soft-physics diffusion | Hard guarantees | Conservation 10⁻⁶ vs 10⁻⁴ |
| EVT+GAN | Physics | Adds conservation guarantees |

### 1.8 Statistical Verification Design

**Sample Size:** n ≥ 30 runs per configuration
**Tests:** Paired t-test (conservation), KS test (distributions), Bonferroni correction
**Report:** Mean ± SD, 95% CI, Cohen's d

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does PCFM constraint projection reduce conservation law violations in climate flow models?"
- Maps to: P1; Verification: Empirical ablation; Critical: MUST PASS

**SH2 (Mechanism - N=4 sub-hypotheses):**
"Is the 4-step causal mechanism the actual cause of improvement?"
- H-M1: PCFM → Conservation (Newton effectiveness)
- H-M2: Conservation → Physical states (propagation)
- H-M3: EVT → Tail guidance (GPD effectiveness)
- H-M4: Combined → Final output (no conflict)
- Verification: Causal analysis with ablations

**SH3 (Comparison):**
"Does EVT-CFM outperform baselines on joint metrics?"
- Maps to: P2, P3; Verification: Comparative empirical

**Total sub-hypotheses:** 2 + 4 = 6

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-EVTCFM-v1
- [x] Confidence level: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] All variables operationalized (7 variables)
- [x] Causal mechanism with evidence (N=4 steps)
- [x] Key tension identified with resolution
- [x] Assumptions list consequences (4 assumptions)
- [x] 3 testable predictions (P1 primary)
- [x] Falsification criteria defined (4 criteria)
- [x] Baselines identified (3)
- [x] SH1, SH2, SH3 generated

### Open Questions

1. **Data Availability:** Access to pretrained climate flow model (ClimateDiffuse/ArchesWeatherGen)?
2. **EVT Parameters:** Sufficient extreme events in ERA5 for robust GPD fitting?
3. **Priority Order:** Validate SH1 first or parallel with SH2?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
