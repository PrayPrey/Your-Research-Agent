# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-CMGCRL-v1
**Confidence Level:** 0.85

**Main Hypothesis:**
Under the condition of molecular property prediction with uncertainty estimates, if we train GNN molecular encoders φ(mol) and property encoders ψ(prop) via graph-aware contrastive learning with confidence-weighted HER-style property relabeling, then sample efficiency will improve by >30% while maintaining molecular validity >85%, because the contrastive-GCRL equivalence (φ(s)ᵀψ(g) ≈ V(s,g)) extends to discrete graph-structured molecular spaces and HER relabeling leverages failed generations as implicit curriculum.

**Alternative Hypothesis (H0):**
There is no meaningful relationship between contrastive molecular representations and goal-conditioned value functions; the inner product φ(mol)ᵀψ(prop) does not correlate with molecular goal achievement, and HER-style relabeling provides no sample efficiency benefit over standard RL in molecular property optimization.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Contrastive loss weight λ | Independent | Weight coefficient for InfoNCE loss in total training objective | [0.1, 1.0] |
| HER relabeling ratio k | Independent | Fraction of transitions relabeled with achieved properties | {0.25, 0.5, 0.8} |
| Confidence threshold τ | Independent | Minimum property predictor confidence for relabeling | [0.7, 0.95] |
| GNN architecture | Controlled | Fixed to SchNet or DimeNet for equivariant representation | SchNet/DimeNet |
| Training data | Controlled | QM9 dataset (134k molecules) | Fixed |
| Evaluation protocol | Controlled | GuacaMol metrics | Fixed |
| Sample efficiency | Dependent | Number of molecules needed to achieve goal with 80% success | Lower is better |
| Goal achievement rate | Dependent | Fraction achieving target property within tolerance ε | [0, 1.0] |
| Molecular diversity | Dependent | Tanimoto diversity of successful molecules | [0, 1.0] |
| Multi-property success | Dependent | Fraction satisfying all property constraints | [0, 1.0] |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: GNN Encoder + InfoNCE Loss
    ↓
Step 2: Property-Aligned Representations → Value Function
    ↓
Step 3: Value Function + HER Relabeling → Sample-Efficient Policy
    ↓
Step 4: Confidence Weighting → Robust Learning
    ↓
[OUTCOME: Sample-efficient multi-property molecular design]
```

**Step 1: GNN → Representations**
- Input: Molecular graphs (atoms, bonds, 3D coordinates)
- Process: Graph neural network with graph-level pooling
- Output: Molecular embeddings φ(mol) capturing property-relevant features
- Evidence: UniCorn (2024) achieves SOTA on quantum/physicochemical/biological tasks

**Step 2: Representations → Value Function**
- Input: Molecular embeddings φ(mol), property embeddings ψ(prop)
- Process: Inner product computation
- Output: Goal-conditioned value function V(mol, prop) = φ(mol)ᵀψ(prop)
- Evidence: Eysenbach (2022) proves this equivalence for continuous spaces

**Step 3: Value Function + HER → Policy**
- Input: Value function, failed molecular generations
- Process: Relabel failed molecules with achieved properties as new goals
- Output: Sample-efficient policy learning from implicit curriculum
- Evidence: HER improves sample efficiency 10-100x in robotics (Andrychowicz 2017)

**Step 4: Confidence → Robustness**
- Input: Property predictions with uncertainty estimates
- Process: Only relabel when predictor confidence > τ
- Output: Robust learning despite property predictor noise
- Evidence: Uncertainty quantification prevents label corruption in neural networks

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | UniCorn (2024) | Multi-view contrastive achieves SOTA molecular representations | Strong |
| Step2 → Step3 | Eysenbach (2022) | φ(s)ᵀψ(g) = V(s,g) proven mathematically | Strong |
| Step3 → Step4 | Andrychowicz (2017) | HER enables learning from sparse binary rewards | Strong |
| Step4 → Outcome | Neural network uncertainty literature | Confidence thresholding filters unreliable predictions | Medium |

**Key Tension:**
- Tension: Eysenbach (2022) proves contrastive-GCRL equivalence for continuous state spaces, but molecular graphs are discrete structures
- Resolution: This verification plan tests whether graph-level pooling enables the discrete→continuous mapping required for the equivalence to hold. UniCorn's success with molecular graphs provides preliminary support.

### 1.4 Key Assumptions

1. **Property predictor accuracy (>85%)**
   - Supporting evidence: QM9 benchmarks show neural network predictors achieve >90% on many properties
   - Consequence if violated: HER relabeling with incorrect achieved properties corrupts training signal, leading to policy divergence

2. **Contrastive-GCRL equivalence extends to graphs**
   - Supporting evidence: UniCorn demonstrates contrastive learning works on molecular graphs; Eysenbach proves equivalence for continuous spaces
   - Consequence if violated: Inner product φ(mol)ᵀψ(prop) does not encode goal-conditioned value, requiring alternative value function architectures

3. **Molecular space has sufficient local structure**
   - Supporting evidence: Drug discovery manifold hypothesis; similar molecules often have similar properties
   - Consequence if violated: Representation learning fails to generalize; random embeddings perform similarly to learned ones

### 1.5 Scope & Boundaries

**Where hypothesis applies:**
- Small to medium drug-like molecules (<100 heavy atoms)
- Properties with available neural network predictors (binding affinity, solubility, LogP, toxicity)
- Goal-directed generation tasks (single and multi-property optimization)
- Offline and online RL settings

**Where it does NOT apply:**
- Macromolecules and proteins (require specialized architectures)
- Properties without reliable predictors (novel biological assays)
- Combinatorial library enumeration (not goal-directed)
- Synthesis planning (different problem formulation)

**Known limitations:**
- Relies on property predictor quality and calibration
- Confidence threshold τ reduces effective relabeling rate
- Computational cost of GNN + contrastive + property prediction pipeline
- Limited to chemical space covered by training data distribution

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Sample Efficiency vs Baseline):**
CM-GCRL with HER relabeling will achieve 80% goal success rate using ≥30% fewer molecular generations compared to standard RL without HER relabeling.

*Measurement*:
- Sample efficiency: molecules_needed(CM-GCRL) < 0.7 × molecules_needed(baseline)
- Statistical test: Paired t-test, n ≥ 20 runs, p < 0.05

*Basis*:
HER provides 10-100x improvement in robotics; molecular domain expected to show at least 30% improvement due to property space continuity.

*Success Criteria for Phase 2B*:
- Primary: ≥30% reduction in samples needed (p < 0.05)
- Falsification: <15% reduction triggers hypothesis revision

**Secondary Predictions:**

**P2 (Confidence Threshold Effect):**
Applying confidence threshold τ will reduce label noise corruption while maintaining ≥80% of sample efficiency gains from unrestricted HER.

*Measurement*: Compare τ=0 vs τ=0.8 conditions; efficiency(τ=0.8) ≥ 0.8 × efficiency(τ=0)

**P3 (Multi-Property Generalization):**
CM-GCRL will achieve higher Pareto front coverage than single-property baselines when optimizing multiple properties simultaneously.

*Measurement*: Hypervolume indicator for multi-objective optimization

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure**: Sample efficiency improvement <15%
   - Indicates HER relabeling provides no meaningful benefit for molecules

2. **Mechanism Failure**: φ(mol)ᵀψ(prop) does not correlate with goal achievement (r < 0.3)
   - Indicates contrastive-GCRL equivalence fails for molecular graphs

3. **Comparative Failure**: CM-GCRL performs worse than Mol-AIR or GFlowNets on all metrics
   - Indicates the approach has no practical advantage

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

**Note:** Molecular GCRL is a new domain without established SOTA benchmarks.

**Available Comparison Methods:**
| Method | Domain | Key Metric | Performance |
|--------|--------|------------|-------------|
| Mol-AIR (2024) | Molecular RL | Goal achievement | Reported on specific tasks |
| GFlowNets (2023) | Multi-objective | Pareto coverage | Uniform exploration |
| Standard RL | Molecular generation | Sample efficiency | Baseline reference |

**Benchmarks:** GuacaMol, MOSES, QM9

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (Cohen's d): 0.8 (large, based on HER robotics results)
- Required runs: n ≥ 20
- Statistical power: 0.8

**Test Specification:**
- Method: Paired t-test (same random seeds across conditions)
- Significance level: α = 0.05 (one-tailed for improvement hypothesis)
- Report format: Mean difference, 95% CI, Cohen's d, p-value

**Multiple Comparison Correction:**
- Bonferroni correction for 3 primary comparisons
- Adjusted α = 0.05/3 = 0.017

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does graph-aware contrastive learning on molecular-property pairs create meaningful goal-conditioned value representations where φ(mol)ᵀψ(prop) correlates with molecular goal achievement?"
- Verification type: Empirical correlation analysis
- Critical: MUST PASS for hypothesis to proceed

**SH2 (Mechanism):**
"Is the proposed 4-step causal mechanism (GNN→Representations→Value Function→Policy with HER→Robust Learning) the actual cause of sample efficiency improvement?"
- Will decompose into 4 sub-hypotheses (H-M1 through H-M4) in Phase 2B:
  - H-M1: GNN encoder creates property-relevant representations
  - H-M2: Contrastive equivalence holds for molecular graphs
  - H-M3: HER relabeling improves sample efficiency
  - H-M4: Confidence thresholding reduces noise corruption
- Verification type: Ablation studies and causal analysis

**SH3 (Comparison):**
"Does CM-GCRL outperform Mol-AIR and Goal-conditioned GFlowNets baselines on sample efficiency and multi-property success rate?"
- Verification type: Comparative empirical evaluation
- Critical: Determines practical value of approach

**Total Sub-Hypotheses:** 2 + 4 = 6

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-CMGCRL-v1
- [x] Confidence level specified: 0.85
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=4 steps)
- [x] Causal chain length determined: N=4
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (3 defined)
- [x] Falsification criteria are defined (3 conditions)
- [x] Baselines are identified for comparison (Mol-AIR, GFlowNets, Standard RL)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Resource Requirements:**
   - Compute: Single GPU sufficient for GNN training?
   - Data: QM9 (134k molecules) + GuacaMol benchmarks accessible
   - Time: Estimated 10K-100K molecule generations per experiment

2. **Property Predictor Access:**
   - Need uncertainty-calibrated predictors for binding affinity, solubility, toxicity
   - Options: Ensemble methods, MC dropout, or conformal prediction

3. **Priority Verification Order:**
   - Recommended: SH1 (Existence) → SH2-H-M2 (Contrastive equivalence) → SH2-H-M3 (HER effect) → SH3 (Comparison)
   - Rationale: Early validation of core theoretical claim before comparative evaluation

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-12*
