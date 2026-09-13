# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-HCFM-BG-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under the condition of structured folded proteins with >1000 atoms, if hierarchical factorization P(backbone) × P(all-atom|backbone) is applied with SE(3)-equivariant flow matching and importance reweighting, then equilibrium Boltzmann sampling will scale to 10x larger systems than single-scale approaches while maintaining thermodynamic accuracy within 1 kT, because the hierarchical decomposition reduces effective dimensionality and importance reweighting corrects factorization approximation errors.

**Alternative Hypothesis (H0):**
Hierarchical factorization provides no scalability advantage over single-scale Boltzmann generators for large protein systems, OR the importance reweighting required to correct factorization errors results in prohibitively low effective sample sizes (ESS < 1%), negating any computational benefits.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Hierarchical factorization (backbone → all-atom) | Independent | Two-stage flow: Stage 1 samples Cα coordinates from P(backbone\|E), Stage 2 conditionally generates all-atom from P(all-atom\|backbone, E) | Binary: enabled vs single-scale baseline |
| System size (number of atoms) | Independent | Total atom count of protein system | 1,000 - 10,000 atoms |
| Sampling efficiency (ESS/GPU-hour) | Dependent | Effective Sample Size per GPU-hour computed via importance weights variance: ESS = (Σw)² / Σw² | Target: >10% ESS; Baseline: Sequential BG ~5-50% on peptides |
| Thermodynamic accuracy | Dependent | Free energy RMSE vs long MD reference (kT units); KL divergence D_KL(q‖p) to target Boltzmann | Target: <1 kT RMSE; KL < 0.5 |
| Temperature | Controlled | Fixed at physiological temperature | 300K |
| Force field | Controlled | Standardized molecular mechanics force field | AMBER ff14SB or CHARMM36m |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: Hierarchical Factorization
    ↓ (reduces search space)
Step 2: Dimensionality Reduction
    ↓ (enables faster exploration)
Step 3: Conditional Local Structure Preservation
    ↓ (maintains physical validity)
Step 4: Importance Reweighting
    ↓ (corrects approximation errors)
Outcome: Exact Boltzmann Sampling at Scale
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Wavelet CRG (Marchand 2022) | Hierarchical factorization avoids critical slowing down | Strong |
| Step2 → Step3 | Transferable BG (Klein 2024) | Flow matching in reduced space enables zero-shot generalization | Strong |
| Step3 → Step4 | FoldFlow-2 (Huguet 2024) | SE(3)-equivariant architecture preserves geometric validity | Strong |
| Step4 → Outcome | Sequential BG (Tan 2025) | SMC + Langevin achieves state-of-the-art ESS | Strong |

**Key Tension:**
- **Tension:** Single-scale approaches (Sequential BG) achieve high ESS on small peptides without hierarchical factorization, suggesting the benefit may only emerge at larger scales.
- **Resolution:** This verification plan tests scalability explicitly by comparing performance curves as system size increases from 100 to 10,000 atoms.

### 1.4 Key Assumptions

1. **Backbone captures slow modes:** Cα coordinates represent dominant slow degrees of freedom.
   - Consequence if violated: Factorization misses important slow modes; require fallback for IDPs

2. **Conditional simplification:** Side-chain distributions conditioned on backbone are simpler than joint.
   - Consequence if violated: Conditional flow training equally difficult; no computational advantage

3. **Flow learnability:** SE(3)-equivariant flow matching learns accurate conditional distributions.
   - Consequence if violated: Generated conformations physically invalid

4. **Reweighting efficiency:** Importance reweighting corrects errors without prohibitive weight variance.
   - Consequence if violated: ESS → 0 renders method statistically useless

### 1.5 Scope & Boundaries

**Applies to:**
- Folded globular proteins (>1000 atoms) with clear secondary structure
- Equilibrium sampling at 300K with standard force fields (AMBER, CHARMM)

**Does NOT apply to:**
- Intrinsically disordered proteins (IDPs)
- Membrane proteins in lipid bilayers
- Non-equilibrium dynamics
- Systems requiring quantum treatment

**Limitations:**
- ~2x inference cost from reweighting
- Requires MD training data
- Very large systems (>50,000 atoms) may need additional coarse-graining

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Scalability vs SOTA):**
Our hierarchical approach will achieve ESS/GPU-hour > 5% for protein systems with 5,000-10,000 atoms, where Sequential BG (current SOTA) achieves ESS < 1% or fails entirely.

*Measurement:* ESS/GPU-hour via importance weights; paired comparison n ≥ 20 runs
*Success Criteria:* ESS/GPU-hour > 5% for 5,000-atom systems (p < 0.05)
*Falsification:* ESS/GPU-hour < 0.1% triggers rejection

**Secondary Predictions:**

**P2 (Thermodynamic Accuracy):**
Free energy estimates match long MD reference within 1 kT RMSE.

**P3 (Hierarchical Advantage):**
Performance gap (hierarchical/single-scale ESS ratio) increases monotonically with system size.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if:
1. ESS/GPU-hour < 0.1% for systems > 3,000 atoms
2. Importance weight variance explodes (ESS/n < 0.01) despite good training
3. Single-scale baseline achieves comparable ESS at all scales
4. Free energy RMSE > 5 kT even with sufficient samples

### 1.7 SOTA Baseline

| Method | System Size | ESS | Year |
|--------|-------------|-----|------|
| Sequential BG | Hexa-peptide (~100 atoms) | 5-50% | 2025 |
| Transferable BG | Dipeptides (~30 atoms) | Variable | 2024 |

**Target:** Match ~20% ESS at 10x larger scale (1000+ atoms)

### 1.8 Statistical Verification Design

**Sample Size:** n ≥ 20 per condition
**Systems:** 100, 500, 1000, 3000, 5000, 10000 atoms
**Test:** Paired t-test (same seeds), α = 0.05 (one-tailed)
**Report:** Mean difference, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Can hierarchical Boltzmann generators achieve ESS > 1% for proteins exceeding 1000 atoms?"
- Verification: Empirical (direct measurement)
- Critical: MUST PASS

**SH2 (Mechanism):**
"Is hierarchical factorization the causal mechanism enabling scalability?"
- Decomposed into 4 sub-hypotheses (H-M1 to H-M4)
- Verification: Causal analysis (ablation studies)

**SH3 (Comparison):**
"Does hierarchical approach outperform Sequential BG as system size increases?"
- Verification: Comparative benchmark suite

**Total Sub-Hypotheses:** 2 + 4 = 6

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-HCFM-BG-v1
- [x] Confidence level: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] Variables operationalized with evidence
- [x] Causal mechanism (N=4) with evidence table
- [x] Key tension + resolution identified
- [x] Assumptions list consequences
- [x] 3 testable predictions (primary marked)
- [x] Falsification criteria (4 conditions)
- [x] Baselines identified
- [x] SH1/SH2/SH3 defined

### Open Questions

1. **Data Availability:** Sufficient MD trajectories for 1000-10000 atom training?
2. **Compute Resources:** GPU memory requirements for SE(3) flows at scale?
3. **Priority:** Verify SH1 (existence) first before systematic comparison?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
