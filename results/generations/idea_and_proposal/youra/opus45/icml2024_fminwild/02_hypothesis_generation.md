# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-CAL-LoRA-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under domain adaptation conditions, if first-order meta-learning (Reptile-style) is used to learn LoRA initialization across diverse domains with calibration-aware loss, then domain-adapted foundation models will maintain significantly lower Expected Calibration Error (20-25% reduction) compared to standard LoRA, because the meta-learned initialization encodes calibration-preserving properties that transfer across domains.

**Alternative Hypothesis (H0):**
There is no significant difference in Expected Calibration Error between CAL-LoRA (meta-learned initialization) and standard LoRA initialization when adapting foundation models to new domains. Any observed calibration differences are attributable to random variation or confounding factors rather than the meta-learning mechanism.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Meta-learning method | Independent | Reptile-style first-order meta-learning with calibration loss vs standard LoRA initialization | Binary: CAL-LoRA vs Standard LoRA |
| LoRA rank | Independent | Low-rank dimension r | r ∈ {4, 8, 16, 32} |
| Number of meta-training domains | Independent | Diverse domains for meta-training | N ∈ {3, 5, 7} (medical, legal, scientific) |
| Post-adaptation ECE | Dependent | Expected Calibration Error on held-out domain-specific test sets using 15 bins | 0.0-0.3 (lower is better) |
| Post-adaptation accuracy | Dependent | Task accuracy on domain-specific evaluation benchmarks | 70-95% depending on task |
| Base model | Controlled | LLaMA2-7B frozen base parameters | Fixed |
| Fine-tuning epochs | Controlled | Training epochs per domain adaptation | Fixed at 3 epochs |
| Calibration loss weight | Controlled | Weight for focal calibration loss | λ_cal = 0.1 |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Meta-training with calibration loss
           ↓ (Link 1)
Calibration-aware LoRA initialization
           ↓ (Link 2)
Constrained adaptation trajectory
           ↓ (Link 3)
Maintained post-adaptation calibration
```

**Step 1: Meta-training → Calibration-aware Initialization**
The Reptile-style outer loop optimization across diverse domains with focal calibration loss shapes LoRA parameters to encode calibration-preserving structure.

**Step 2: Calibration-aware Initialization → Constrained Trajectory**
When fine-tuning starts from meta-learned initialization, updates remain in a subspace that preserves calibration properties.

**Step 3: Constrained Trajectory → Maintained Calibration**
Because the adaptation trajectory is constrained to the calibration-preserving manifold, the final domain-adapted model retains low ECE while achieving competitive task accuracy.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Domain generalization meta-learning survey (Khoee 2024) | Meta-learning enables fast adaptation while preserving desired properties | Strong |
| Step2 → Step3 | C-LoRA (NeurIPS 2025) | Contextualized LoRA achieves calibrated uncertainties in constrained space | Strong |
| Step3 → Outcome | Calibration-aware fine-tuning (Xiao 2025) | ECE regularization maintains low calibration error | Strong |

**Key Tension:**
- **Tension:** C-LoRA achieves calibration through architectural modification (contextualized modules), while CAL-LoRA proposes achieving it through initialization learning.
- **Resolution:** This verification plan tests whether initialization-based calibration (CAL-LoRA) can match or exceed architecture-based calibration (C-LoRA) with lower computational overhead at inference time.

### 1.4 Key Assumptions

1. **Calibration properties can be encoded in LoRA parameter space**
   - Evidence: C-LoRA (NeurIPS 2025) demonstrated contextualized LoRA achieves well-calibrated uncertainties
   - Consequence if violated: Meta-learning outer loop cannot optimize for calibration

2. **Meta-learning can learn property-preserving initializations for calibration**
   - Evidence: Domain generalization survey (Khoee 2024) shows property preservation
   - Consequence if violated: Initialization may optimize for accuracy but not calibration

3. **First-order approximation (Reptile) is sufficient for calibration preservation**
   - Evidence: Reptile achieves similar quality to MAML at 10x lower cost
   - Consequence if violated: Would require full MAML, 10x cost increase

4. **Diverse meta-training domains enable generalization to unseen domains**
   - Evidence: Cross-domain meta-learning confirms diversity aids generalization
   - Consequence if violated: Calibration preservation would be domain-specific

### 1.5 Scope & Boundaries

**Where hypothesis applies:**
- LLM domain adaptation tasks with discrete outputs (classification, QA, multiple choice)
- Foundation models with attention layers suitable for LoRA injection
- Settings where calibrated uncertainty is valuable (medical, legal, scientific)

**Where it does NOT apply:**
- Open-ended generation tasks where calibration is difficult to measure
- Models without attention layers
- Extremely low-resource domains with insufficient meta-training data

**Known limitations:**
- Computational overhead: ~5-10x training cost vs standard LoRA for meta-training
- Data requirements: Requires diverse domain adaptation datasets
- Scale constraints: Primary validation on 7B models; scalability to 70B+ uncertain

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (ECE Reduction Target)**:
CAL-LoRA will achieve Expected Calibration Error reduction ≥ 20% compared to standard LoRA on held-out domain adaptation tasks.

*Measurement*:
- ECE reduction ≥ 20% with p < 0.05
- Paired t-test across 5+ domain adaptation tasks, n ≥ 20 runs per condition
- ECE computed with 15 bins on held-out test sets

*Success Criteria*:
- Primary: ECE reduction ≥ 20% (p < 0.05)
- Falsification: ECE reduction < 10% triggers rejection

**Secondary Predictions:**

**P2 (Accuracy Preservation)**:
CAL-LoRA will maintain task accuracy within 2% of standard LoRA.

**P3 (Calibration Transfer)**:
On unseen domains, CAL-LoRA will achieve ECE reduction ≥ 15%.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if:
1. ECE reduction < 10% on meta-trained domains
2. Calibration improvement does not correlate with meta-training diversity
3. Zero calibration improvement on unseen domains
4. Accuracy drops > 5% compared to standard LoRA

### 1.7 Statistical Verification Design

**Sample Size:** n ≥ 20 runs per condition (80% power at α = 0.05)
**Test:** Paired t-test with Bonferroni correction
**Report:** Mean difference, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does calibration-preserving LoRA initialization exist such that domain-adapted models maintain significantly lower ECE than standard LoRA?"
- Maps to: Primary prediction (P1)
- Verification type: Empirical comparison
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is first-order meta-learning with calibration loss the actual mechanism that produces calibration-preserving initialization?"

Phase 2B will decompose into 3 sub-hypotheses:
- **H-M1:** Meta-training produces initialization encoding calibration information
- **H-M2:** Calibration-aware initialization constrains adaptation trajectory
- **H-M3:** Constrained trajectory maintains post-adaptation calibration

**SH3 (Comparison):**
"Does CAL-LoRA achieve better calibration-accuracy trade-off than alternatives?"
- Maps to: Secondary predictions (P2, P3)
- Verification type: Comparative empirical

**Total sub-hypotheses in Phase 2B:** 5 (1 + 3 + 1)

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-CAL-LoRA-v1
- [x] Confidence level: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] All variables operationalized
- [x] Causal mechanism with N=3 steps and evidence
- [x] Key tension identified with resolution
- [x] Assumptions with consequences if violated
- [x] 3 testable predictions (primary marked)
- [x] 4 falsification criteria
- [x] Baselines identified
- [x] SH1, SH2, SH3 clear for Phase 2B

### Open Questions

1. **Resource Requirements:** Minimum meta-training domains for effective calibration transfer?
2. **Data Availability:** Domain adaptation datasets with calibration-suitable evaluation?
3. **Technical Feasibility:** Sensitivity to Reptile hyperparameters?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
