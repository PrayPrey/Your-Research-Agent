# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md (Round 1 - RG-STFM, FEASIBLE)
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-RGSTFM-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under conditions of near-critical physical systems exhibiting scale-invariant behavior, if we embed explicit renormalization group (RG) flow structure as interpretable embeddings in a foundation model architecture, then cross-domain scale transition transfer will achieve higher accuracy and interpretability than data-driven physics foundation models (PhysiX, GPhyT), because RG universality provides domain-agnostic mathematical structure that captures the essential physics of scale transitions across different physical systems.

**Alternative Hypothesis (H0):**
There is no relationship between explicit RG flow embeddings and cross-domain transfer performance. Data-driven approaches (PhysiX with 4.5B parameters, GPhyT with 1.8TB training data) achieve equivalent or better results by learning scale transitions implicitly from large-scale data without explicit physics-based inductive bias.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| RG embedding dimension | Independent | Dimensionality of latent space encoding RG flow structure | 64, 128, 256 dimensions |
| Pre-training domain diversity | Independent | Number of distinct physical domains in training set (PDEBench, The Well) | 3-10 domains |
| Architecture depth | Independent | Number of transformer layers in RG Flow Encoder | 6, 12, 24 layers |
| Zero-shot transfer accuracy | Dependent | VRMSE on held-out domain without fine-tuning, measured on The Well benchmark | Lower is better; target ≤ PhysiX baseline |
| Few-shot adaptation efficiency | Dependent | Number of samples required to match PhysiX/GPhyT performance on new domain | 10-100 samples (vs 1000+ for baselines) |
| Interpretability score | Dependent | Accuracy of universality class prediction + critical exponent regression MAE | >80% class accuracy, MAE < 0.1 for exponents |
| Target domain scale separation | Controlled | Fixed ratio of fine-to-coarse scale | 100:1 |
| Evaluation benchmark | Controlled | The Well benchmark (standard physics FM evaluation) | Fixed benchmark |
| Training compute budget | Controlled | GPU-hours comparable to PhysiX training | Fixed budget |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
RG Flow Encoder → Domain-Agnostic RG Embeddings → Universality Class Clustering → Cross-Domain Transfer → Superior Performance
     (Step 1)              (Step 2)                     (Step 3)                    (Step 4)            (Outcome)
```

**Step 1: RG Flow Encoder → Domain-Agnostic RG Embeddings**
- Mechanism: Transformer with RG-aware positional encodings captures scale hierarchy
- Evidence: Layer-wise DNN transformations are analogous to RG transformations (Liaw 2025)
- Falsification: Embedding space shows no scale structure

**Step 2: Domain-Agnostic RG Embeddings → Universality Class Clustering**
- Mechanism: Contrastive learning clusters scale transitions by RG universality class
- Evidence: Systems in same universality class share critical exponents and scaling relations
- Falsification: >100 distinct clusters instead of 3-5 major universality classes

**Step 3: Universality Class Clustering → Efficient Cross-Domain Transfer**
- Mechanism: Shared embeddings for same universality class enable zero-shot transfer
- Evidence: Transfer PINN (Wang 2025) shows transfer within domains works; RG should extend across domains
- Falsification: Transfer accuracy worse than random initialization

**Step 4: Efficient Cross-Domain Transfer → Superior Performance vs Data-Driven FMs**
- Mechanism: RG inductive bias reduces learning space compared to learning from scratch
- Evidence: MLRG (Hou 2023) achieves phase classification without labels; theory-guided outperforms data-only
- Falsification: No accuracy or interpretability advantage over PhysiX/GPhyT

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Liaw (2025) | RG Framework for DNNs - layer-wise RG analogy | Medium |
| Step2 → Step3 | RG Theory | Universality classes share critical exponents | Strong |
| Step3 → Step4 | Wang (2025) | Transfer PINN demonstrates within-domain transfer | Medium |
| Step4 → Outcome | Hou (2023), Luo (2024) | MLRG/OLRG show theory-guided advantages | Medium |

**Key Tension:**
- **Tension:** PhysiX/GPhyT papers suggest data-driven approaches can learn effective physics representations without explicit RG structure, while our hypothesis claims RG-explicit design is necessary for interpretability and transfer.
- **Resolution:** This verification plan tests whether RG-explicit design provides measurable interpretability and transfer efficiency advantages that data-driven approaches cannot match, even with 10x more parameters.

### 1.4 Key Assumptions

1. **Scale transitions share RG structure across domains**
   - Evidence: MLRG (Hou 2023) demonstrates automatic RG learning in Ising models
   - Consequence if violated: Cross-domain transfer will fail; model becomes domain-specific like existing neural operators

2. **Neural networks can approximate RG transformations**
   - Evidence: OLRG (Luo 2024) successfully learns operator maps for RG; Rançon (2025) shows minimal NNs invert RG
   - Consequence if violated: RG Flow Encoder cannot capture scale transitions; architecture fundamentally flawed

3. **Multi-domain pre-training leads to emergent universal representations**
   - Evidence: Transfer PINN (Wang 2025) shows transfer works within domains
   - Consequence if violated: Pre-training provides no benefit; fine-tuning always required

4. **Near-critical systems are representative for practical applications**
   - Evidence: RG universality is rigorous near critical points; many important systems are near-critical
   - Consequence if violated: Scope too narrow; limited practical applicability (fusion, climate may not qualify)

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Physical systems exhibiting scale-invariant behavior (turbulence, phase transitions, critical phenomena)
- Near-critical systems where RG universality is rigorous (Ising, XY, Heisenberg models)
- Multiscale PDEs with clear scale separation (fluid dynamics, materials science)
- Systems belonging to well-characterized universality classes

**Where Hypothesis Does NOT Apply:**
- Far-from-equilibrium systems without scale invariance
- Non-scale-invariant dynamics (some biological systems, financial markets)
- Systems where microscopic details matter at all scales (quantum chemistry)
- Very high-dimensional systems where RG is computationally intractable

**Known Limitations:**
- RG universality is mathematically rigorous only near critical points
- Training requires universality class labels (manual annotation or heuristic assignment)
- Scope narrower than general physics FM (but stronger theoretical guarantees within scope)

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Multi-Metric vs SOTA PhysiX/GPhyT):**
RG-STFM will achieve:
- Zero-shot VRMSE ≤ PhysiX baseline on The Well benchmark (parity or better)
- AND Interpretability score > 80% (universality class prediction accuracy)
- AND Critical exponent regression MAE < 0.1

*Measurement:*
- VRMSE on held-out domains from The Well benchmark
- Universality class prediction accuracy on labeled validation set
- MAE for critical exponent regression vs known physics values
- Statistical test: Paired t-test, n ≥ 25 runs, p < 0.05

*Success Criteria for Phase 2B:*
- Primary: VRMSE ≤ PhysiX (p < 0.05) AND interpretability > 80%
- Falsification: VRMSE > PhysiX × 1.5 OR interpretability < 50%

**Secondary Predictions:**

**P2 (Data Efficiency Advantage):**
RG-STFM will require 10x fewer training samples than PhysiX to achieve comparable performance on new domains.

**P3 (Embedding Structure Validation):**
Embedding space will show clear clustering by universality class, with silhouette score > 0.5.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any of the following occur:

1. **Primary Failure:** VRMSE > PhysiX × 1.5 on The Well benchmark
2. **Interpretability Failure:** Universality class prediction accuracy < 50%
3. **Mechanism Failure:** Critical exponent regression MAE > 0.5
4. **Comparative Failure:** No advantage on any dimension (accuracy, efficiency, interpretability)

### 1.7 SOTA Baseline (SOTA Comparison Mode)

| Method | Dataset | Performance | Year |
|--------|---------|-------------|------|
| PhysiX | The Well | SOTA on 18/21 eval points | 2025 |
| GPhyT | Custom | 5-29x vs FNO | 2025 |
| FNO | PDEBench | Baseline | 2020 |

**Strategy:** Multi-Metric (accuracy + interpretability + efficiency)

### 1.8 Statistical Verification Design

**Sample Size:** n ≥ 25 runs
**Test:** Paired t-test, α = 0.05 (Bonferroni corrected: 0.017)
**Effect Size:** Cohen's d ~0.6 (medium)
**Power:** 0.8

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does the RG Flow Encoder produce domain-agnostic embeddings that capture scale transition structure under near-critical conditions?"
- Maps to: Primary prediction (P1)
- Verification type: Empirical (embedding analysis + transfer test)
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the RG universality structure the actual cause of cross-domain transfer success?"
- Maps to: Causal mechanism (N=4 causal links)
- Will decompose into 4 sub-hypotheses in Phase 2B:
  - H-M1: RG Encoder → RG Embeddings
  - H-M2: RG Embeddings → Universality Clustering
  - H-M3: Universality Clustering → Cross-Domain Transfer
  - H-M4: Cross-Domain Transfer → Superior Performance
- Verification type: Causal analysis (ablation studies)

**SH3 (Comparison):**
"Does RG-STFM outperform PhysiX/GPhyT on interpretability while maintaining accuracy?"
- Maps to: Secondary predictions (P2, P3)
- Verification type: Comparative empirical

**Total sub-hypotheses in Phase 2B:** 2 + 4 = 6

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-RGSTFM-v1
- [x] Confidence level specified: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=4 steps)
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (3 defined)
- [x] Falsification criteria are defined (4 failure modes)
- [x] Baselines identified: PhysiX, GPhyT
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Data availability:** Are universality class labels available for The Well benchmark, or do we need heuristic assignment?

2. **Compute requirements:** Can RG-STFM achieve competitive performance with fewer parameters than PhysiX (4.5B)?

3. **Scope validation:** How many physical systems in standard benchmarks are actually near-critical and within RG-STFM's scope?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
