# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-HLEE-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under the condition of training on crystalline materials data (Materials Project, ~150K structures), if hierarchical local environment encoding with adversarial domain alignment (HLEE architecture) is applied, then materials foundation models will achieve cross-domain generalization to amorphous and surface materials with <15% accuracy degradation (vs >50% for baseline GNNs), because local atomic coordination features are physics-invariant across material types while adversarial training with gradient reversal extracts domain-invariant representations that transfer across material type boundaries.

**Alternative Hypothesis (H0):**
Local atomic environment features are NOT sufficiently transferable across material types; domain-specific structural characteristics (periodicity, long-range order) dominate property prediction, making adversarial domain alignment ineffective for cross-material-type generalization. Standard fine-tuning on target domain data will match or exceed HLEE performance.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Architecture Type | Independent | HLEE (hierarchical local-global with GRL) vs baseline GNN (MatGL/NequIP without adaptation) vs ablated variants | Categorical: {HLEE-full, HLEE-lite, MatGL-baseline, NequIP-baseline} |
| Training Strategy | Independent | Adversarial domain alignment vs standard fine-tuning vs multi-task learning | Categorical: {adversarial, fine-tune, multi-task} |
| Property Prediction Accuracy | Dependent | MAE on formation energy (eV/atom) and forces (eV/Å) for target domain materials | Formation energy: 0.02-0.15 eV/atom; Forces: 0.02-0.10 eV/Å |
| Transfer Efficiency | Dependent | Performance gain per fine-tuning sample = (baseline_MAE - adapted_MAE) / N_samples | 0.0001-0.001 eV/atom per sample |
| Cross-Domain Degradation | Dependent | (Target_MAE - Source_MAE) / Source_MAE × 100% | HLEE: <15%; Baseline: >50% |
| Model Size | Controlled | Fixed architecture capacity | ~1M parameters |
| Training Configuration | Controlled | Optimizer, learning rate schedule, epochs | Adam, cosine annealing, 500 epochs |
| Source Domain | Controlled | Pre-training dataset | Materials Project crystalline (~150K structures) |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: Hierarchical Decomposition
    ↓ (separates local from global)
Step 2: Adversarial Domain Alignment
    ↓ (extracts domain-invariant features)
Step 3: Physics-Informed Constraints
    ↓ (preserves chemical validity)
Step 4: Few-Shot Adaptation
    ↓ (completes transfer)
Outcome: Accurate Property Prediction on Target Domain
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | ALIGNN (Choudhary 2021) | Local+angular decomposition → 85% accuracy improvement | Strong |
| Step2 → Step3 | TL-PINN (Mustajab 2024) | Adversarial transfer → 74% improvement with 5% data | Strong |
| Step3 → Step4 | PaiNN (Schütt 2021) | Equivariant message passing preserves symmetries | Strong |
| Step4 → Outcome | Multi-fidelity PINN (Ramezankhani 2022) | Adaptive transfer bridges domain gaps | Medium |

**Key Tension:**
- **Tension:** Universal MLIPs paper (Focassio 2024) shows current models fail significantly on out-of-domain surfaces, BUT no prior work has applied adversarial local environment alignment specifically to this problem
- **Resolution:** This hypothesis proposes that adversarial alignment at the LOCAL ENVIRONMENT level (not material level) is the missing ingredient. Verification will test whether this novel approach resolves the documented failure mode.

### 1.4 Key Assumptions

1. **Local Environment Transferability (CRITICAL)**
   - Assumption: Local atomic environments are governed by the same physical principles regardless of material type
   - *Consequence if violated:* Entire hypothesis fails; adversarial alignment would have no valid target features

2. **Adversarial Training Convergence**
   - Assumption: Adversarial training can converge on graph-structured atomic data with gradient penalty stabilization
   - *Consequence if violated:* Training instability; need fallback to HLEE-lite

3. **Target Domain Data Availability**
   - Assumption: JARVIS contains sufficient amorphous/surface structures (>1000)
   - *Consequence if violated:* Insufficient validation data; need alternative targets

4. **Local Property Dominance**
   - Assumption: Formation energy is dominated by local coordination chemistry
   - *Consequence if violated:* Scope limitation to local properties only

### 1.5 Scope & Boundaries

**Applies to:** Formation energy, atomic forces, local electronic density; crystalline → amorphous/surface transfer

**Does NOT apply to:** Band gap, conductivity, magnetic properties (require long-range features)

**Limitations:** Adversarial hyperparameter sensitivity; limited amorphous data; extreme OOD not guaranteed

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Cross-Domain Accuracy Retention):**
HLEE cross-domain degradation < 15% (baseline degrades >50%)

*Measurement:* Cross-domain degradation = (Target_MAE - Source_MAE) / Source_MAE × 100%

**Secondary Predictions:**

**P2:** HLEE with 100 samples matches baseline with 1000+ samples

**P3:** HLEE-full outperforms HLEE-lite by >10% on cross-domain metrics

**Falsification Criteria:**

1. Cross-domain degradation ≥ 25%
2. HLEE-lite matches HLEE-full (adversarial has no effect)
3. Standard fine-tuning matches HLEE efficiency
4. Adversarial training fails to converge

### 1.7 SOTA Baseline

*Not applicable - targets new capability rather than SOTA comparison*

### 1.8 Statistical Verification Design

- **Sample Size:** n ≥ 20 runs per condition (Cohen's d = 0.8)
- **Test:** Two-sample t-test, α = 0.05 (one-tailed)
- **Report:** Mean ± Std, 95% CI, Cohen's d, p-values

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does hierarchical decomposition successfully separate transferable local features from domain-specific global features?"

**SH2 (Mechanism):**
"Is adversarial local environment alignment the actual cause of improved transfer?"
- Phase 2B decomposes into: H-M1, H-M2, H-M3, H-M4 (4 mechanism sub-hypotheses)

**SH3 (Comparison):**
"Does HLEE outperform baselines in cross-domain prediction?"

**Total sub-hypotheses:** 6 (SH1 + 4 mechanism + SH3)

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-HLEE-v1
- [x] Confidence: 0.82
- [x] H0 defined
- [x] Variables operationalized (7 variables)
- [x] Causal mechanism with evidence (N=4 steps)
- [x] Key tension + resolution
- [x] Assumptions with consequences (4)
- [x] Testable predictions (3: P1 primary)
- [x] Falsification criteria (4)
- [x] Baselines identified
- [x] SH1/SH2/SH3 defined

### Open Questions

1. **Data:** Verify JARVIS amorphous/surface count (target: >1000)
2. **Hyperparameters:** Gradient penalty weight λ range [0.1, 1.0]
3. **Priority:** SH1 → H-M1 → H-M2 → H-M3 → H-M4 → SH3

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
