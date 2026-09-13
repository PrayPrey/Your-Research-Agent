# Phase 2A Extended: Hypothesis Clarification Summary

**Date:** 2026-02-06
**Author:** Pray
**Hypothesis ID:** H-NEURIPS2024-UNIREPS-R1
**Status:** ✅ Ready for Phase 2B Verification Planning

---

## Executive Summary

**Research Question:** Can we bridge biological and artificial neural representation convergence through a unified theoretical framework?

**Hypothesis:** Enforcing biological neural constraints (sparse coding, energy efficiency, local learning) as auxiliary training objectives in standard artificial neural networks promotes convergence to representations similar to both biological neural systems and other artificial models, because these bio-constraints define identifiability-promoting conditions that guide training toward a solution space overlapping with biological systems.

**Confidence Level:** 0.75 (High feasibility, moderate theoretical validation confidence)

**Source:** Round 1 FEASIBLE hypothesis from Phase 2A (Bio-Constrained Identifiability Framework)

---

## 1. Core Hypothesis Statement

**Main Hypothesis (If-Then-Because):**

**IF** we enforce biological constraints (L_sparse + L_energy + L_local) as auxiliary losses in CNNs/ViTs trained on ImageNet,

**THEN** representations will show enhanced similarity to both (1) biological neural recordings (debiased CKA > baseline + 3-5%) and (2) other bio-constrained models (CKA > baseline + 2-4%),

**BECAUSE** bio-constraints define an identifiability-promoting solution space that overlaps with the space biological systems occupy through evolutionary pressure under similar resource constraints.

**Alternative Hypothesis (H0):** Bio-constraint enforcement does NOT enhance convergence beyond standard training; any similarity is due to task optimization alone.

**Variables:**
- **IV:** Constraint enforcement (sparse/energy/local, individual vs. combined), constraint strength (λ ∈ [0, 1])
- **DV Primary:** Bio-similarity (debiased CKA, target >0.50), cross-model similarity (CKA, target >0.60)
- **DV Secondary:** Task performance (ImageNet Top-1, >74%), sparsity (L0 norm), FLOPs (target 10-20% reduction)
- **Controlled:** Architecture (ResNet-50, ViT-B/16), data (ImageNet), neural data (THINGS fMRI, Allen Brain)

**Causal Mechanism:** Bio-constraints → Constrained solution space S_bio → Overlapping with biological space → Representational similarity

**Key Assumptions:**
1. Biological systems evolved optimal representations under resource constraints
2. Identifiability-promoting conditions enhance convergence (EXPLORATORY - to be tested)
3. Sparse/energy/local are PRIMARY constraints (acknowledged as hypothesis)
4. Debiased CKA measures similarity accurately (validated by Murphy 2024)
5. Public datasets sufficient for validation (THINGS n=3 subjects)

**Scope:** Vision domain (ImageNet, visual cortex), feedforward CNNs/Transformers, supervised learning
**Excluded:** Language, audio, RL, recurrent architectures

---

## 2. Testable Predictions

**P1 (Dual Convergence):** Bio-constrained models achieve bio-similarity > baseline + 3-5% AND cross-model similarity > baseline + 2-4%

**P2 (Constraint Necessity):** Full combination (sparse + energy + local) > any single constraint by >2%

**P3 (Dose-Response):** Bio-similarity increases monotonically with λ, task performance decreases (trade-off)

**P4 (Layer-Specific):** Early layers → higher V1/V2 similarity, late layers → higher IT similarity

**P5 (Representational Properties):** Bio-constrained models show higher sparsity (L0: 0.4-0.6), lower FLOPs (10-20% reduction)

**Falsification Criteria:**
- ❌ Bio-similarity ≤ baseline + 1% (no effect)
- ❌ Task accuracy < baseline - 5% (performance collapse)
- ❌ Individual constraints perform as well as combined (constraint independence)
- ❌ SNNs outperform by >2% (spiking architecture necessary)
- ❌ Randomized controls match principled constraints (measurement artifact)

---

## 3. Contributions

**Theoretical:**
- First unified framework explaining bio-artificial convergence via identifiability lens
- Formalizes bio-constraints as identifiability-promoting conditions (novel connection)
- Resolves Gap 2: mechanistic link between biological and artificial representation convergence

**Methodological:**
- Bio-constrained training framework (L_sparse, L_energy, L_local auxiliary losses)
- Dual-benchmark validation (bio-similarity + cross-model similarity simultaneously)
- Comprehensive ablation methodology (7 conditions: 3 individual + 3 pairs + 1 full)

**Practical:**
- Neuroscience validation tool (test biological theories using artificial models)
- Bio-inspired design principles (achieve bio-alignment while maintaining performance)
- Energy-efficient architectures (10-20% FLOPs reduction via biological constraints)

---

## 4. Key Related Work

**Foundational:**
- Platonic Representation Hypothesis (Huh 2024, 249 cites) - convergence framework
- Universality of representation (Hosseini 2024) - empirical evidence, lacks mechanism
- Deep SNNs (Huang 2023) - **CRITICAL BASELINE:** 6.6% higher bio-similarity

**Bio-Plausible Baselines:**
- Oja et al. 2024 - Hebbian learning for stability (not convergence)
- Stricker et al. 2024 - Sparse networks (architecture, not training)
- Ororbia et al. 2024 - Review of bio-plausible learning algorithms

**Identifiability Theory:**
- Bona-Pellissier 2022 - Local identifiability (static analysis)
- Chen 2023 - Task-structure identifiability
- Reizinger 2025 - Singular Identifiability Theory for PRH

**Measurement:**
- Murphy et al. 2024 - Debiased CKA for neural data (adopted methodology)

**Differentiation:** Prior work uses bio-constraints for training methods OR identifiability separately; we unite both for convergence guarantees.

---

## 5. Phase 2B Readiness

### Sub-Hypothesis Preview

**SH1 (Existence):** Bio-constraint enforcement enhances similarity to both biological and artificial systems
- Validation: Paired t-test (bio-constrained vs. baseline), n=5 seeds, p<0.05, d>0.5

**SH2 (Mechanism):** Bio-constraints define identifiability-promoting solution space
- Validation: Ablation study (individual vs. combined), representational analysis (sparsity, FLOPs, local similarity)

**SH3 (Comparison):** Bio-constrained framework outperforms existing bio-plausible methods
- Validation: Baseline comparison (SNNs, Oja, Stricker, ResNet, ViT), multi-metric evaluation

### Readiness Checklist

✅ **READY (95% complete):**
- Clear main hypothesis with If-Then-Because structure
- Operationalized variables with measurement methods
- Quantitative predictions (5 predictions + 5 falsification criteria)
- Statistical design (3×2×5 factorial, power analysis)
- SOTA baselines identified (SNNs, Oja, Stricker, ResNet, ViT)
- Public datasets accessible (THINGS, Allen Brain, ImageNet)
- Implementation tools specified (PyTorch, torch.profiler, debiased CKA)
- Scope clearly bounded (vision domain, supervised learning)

⚠️ **NEEDS CLARIFICATION (for Phase 2C):**
- Identifiability formalization: Mathematical proof or explicit exploratory framing
- Hyperparameter selection: Principled initialization before grid search
- Energy metric calibration: Justify FLOPs as ATP proxy
- Layer-to-cortex mapping: Define specific layer groupings
- SNN baseline access: Identify public implementation or contact authors

❌ **BLOCKED:** None identified

### Open Questions

**Theoretical (Phase 2B):**
- Q1: Can we formally prove sparse + energy + local satisfy identifiability conditions?
- Q2: Are three constraints sufficient or are additional ones needed?
- Q3: Why does static identifiability theory apply to dynamic SGD training?

**Empirical (Phase 2C/3):**
- Q4: What is optimal accuracy-biosimilarity trade-off (Pareto frontier)?
- Q5: Do representations transfer to other vision tasks?
- Q6: How sensitive are results to hyperparameter choices?

**Measurement (Phase 2C):**
- Q7: Is debiased CKA best metric or should we use RSA/MI/regression?
- Q8: How to handle layer mismatch between CNNs and cortical areas?
- Q9: What CKA threshold counts as "sufficient" bio-similarity?

**Implementation (Phase 3):**
- Q10: How to implement Hebbian local loss in PyTorch?
- Q11: Can we use standard GPUs or need neuromorphic hardware?
- Q12: How to ensure reproducibility (random seeds, augmentation)?

---

## 6. Statistical Design Summary

**Experimental Design:** 3×2×5 Mixed Factorial
- Factor 1: Constraint condition (unconstrained, single-constraint, full bio-constrained)
- Factor 2: Architecture (ResNet-50, ViT-B/16)
- Factor 3: Random seed (5 replications)
- Total models: 30

**Primary Tests:**
- H1: Bio-similarity enhancement (paired t-test, one-tailed, α=0.05, d>0.5)
- H2: Cross-model similarity enhancement (paired t-test, one-tailed)
- H3: Constraint necessity (one-way ANOVA + Tukey post-hoc, Bonferroni correction)

**Success Criteria:**
- Bio-similarity > baseline + 3%
- Cross-model similarity > baseline + 2%
- Task accuracy within baseline - 2%
- All statistical tests p < 0.05 with d > 0.5

---

## 7. SOTA Baseline Benchmarks

| Baseline | Bio-Similarity | Task Accuracy | FLOPs | Notes |
|----------|----------------|---------------|-------|-------|
| **SNNs (Huang 2023)** | **HIGH (+6.6%)** | ~70-74% | ~5 GFLOPs | **CRITICAL: Must match or exceed** |
| Oja Networks (2024) | Medium | ~72-75% | ~4 GFLOPs | Local learning only |
| Sparse Nets (Stricker 2024) | Medium | ~73-76% | ~3.5 GFLOPs | Sparsity only |
| ResNet-50 (Standard) | **~0.45** | **76.2%** | 4.1 GFLOPs | **PRIMARY baseline** |
| ViT-B/16 (Standard) | ~0.40 | 81.1% | 17.6 GFLOPs | Transformer baseline |
| **Our Target** | **>0.50** | **>74%** | **3.3-3.7 GFLOPs** | **All 3 constraints** |

**Minimum Requirements:**
- Bio-similarity ≥ SNN - 2% (within striking distance of spiking architecture)
- Task accuracy > 74.2% (ResNet-50 - 2%)
- FLOPs < 3.7 GFLOPs (10% reduction)

---

## Next Steps: Phase 2B

**Immediate Actions:**
1. ✅ Proceed to Phase 2B: Sub-hypothesis decomposition (SH1-SH3)
2. ✅ Develop verification roadmap for each sub-hypothesis
3. ⚠️ Address theoretical questions (Q1-Q3) - formalize identifiability connection
4. ⚠️ Specify layer-to-cortex mapping for layer-specific analysis
5. ⚠️ Identify SNN implementation (snnTorch, Norse) or contact Huang et al. for code

**Phase 2C Preparation:**
- Define detailed experiment protocols (training procedures, hyperparameter grids)
- Specify data splits and evaluation procedures
- Implement L_sparse, L_energy, L_local losses
- Set up debiased CKA measurement pipeline
- Prepare baseline model training scripts

**Timeline Estimate:**
- Phase 2B (Verification Planning): 1 week
- Phase 2C (Experiment Design): 2 weeks
- Phase 3 (Implementation Planning): 2-3 weeks
- Phase 4 (Coding + Validation): 8-12 weeks

**Budget Estimate:**
- Training: ~$1.3K (8-GPU days for 30 models + 30% overhead)
- Baselines: ~$500 (reproduce Oja, Stricker, SNNs if needed)
- Total: ~$1.8K (well within $5K research budget)

---

**Status:** ✅ APPROVED for Phase 2B
**Confidence:** 0.75 (High feasibility, ready to proceed)
**Next Workflow:** `/phase2b-planning` with input from this clarified hypothesis

*Generated: 2026-02-06 (YOLO Mode - Fully Automated)*
*Workflow: Phase 2A Extended (v2.0)*
*Input: Round 1 FEASIBLE hypothesis (Bio-Constrained Identifiability Framework)*
