# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-AIWD-E-v1
**Confidence Level:** 0.835

**Main Hypothesis:**
Under the condition of generative adversarial attacks on image watermarks (using WAVES benchmark attack suite), if an immune-inspired detector population with clonal expansion and affinity maturation is applied during offline training followed by knowledge distillation for online deployment, then watermark detection rates (TPR) will improve by >15% compared to static detectors, because evolutionary adaptation enables detectors to recognize attack-transformed watermark patterns that static detectors cannot recognize—analogous to how immune systems adapt to mutating pathogens.

**Alternative Hypothesis (H0):**
There is no significant difference in watermark detection rates (TPR) between immune-inspired adaptive detectors and static detectors under generative adversarial attacks, OR immune-inspired adaptation provides ≤5% improvement (within noise margin), suggesting that attack transformations are either too random to learn or that static detectors already capture the essential detection patterns.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Detector population size | Independent | Number of detector variants initialized via weight perturbation | 20 variants (per RAILS methodology) |
| Adaptation generations | Independent | Number of evolutionary optimization iterations (clonal expansion + affinity maturation cycles) | 5-10 generations |
| Distillation approach | Independent | Knowledge transfer method from adapted ensemble to single detector | Soft labels vs. logit matching |
| True Positive Rate (TPR) | Dependent | Watermark detection rate under WAVES generative attacks | Target: >15% improvement over static baseline |
| False Positive Rate (FPR) | Dependent | Rate of non-watermarked images incorrectly classified as watermarked | Target: ≤ static detector FPR |
| Inference latency | Dependent | Time to classify single image (ms) | Target: <2x single detector baseline |
| Attack types | Controlled | WAVES benchmark generative attack suite | Diffusive attacks + adversarial attacks (fixed) |
| Base watermark scheme | Controlled | Underlying watermarking algorithm | DiffuseTrace (fixed) |
| Dataset | Controlled | Evaluation image dataset | WAVES benchmark dataset (fixed) |

### 1.3 Causal Mechanism

**4-Step Causal Chain (N=4):**

```
[Population Initialization] → [Diverse Detection Boundaries] → [Clonal Expansion] → [Affinity Maturation] → [Improved TPR]
```

**Step 1: Population Initialization → Diverse Detection Boundaries**
- *Mechanism:* Initializing 20 detector variants with different weight perturbations creates diverse decision boundaries that collectively cover more attack variations than a single detector
- *Evidence:* RAILS methodology demonstrates effective population diversity through weight perturbation
- *Falsification:* Fails if variants produce degenerate (identical) decision boundaries despite perturbation

**Step 2: Diverse Detection Boundaries → Clonal Expansion of Successful Detectors**
- *Mechanism:* Detectors that successfully detect attacked watermarks are amplified in the population, similar to B-cell proliferation in immune response
- *Evidence:* RAILS AISE architecture validates clonal expansion principle for adversarial robustness
- *Falsification:* Fails if successful detection does not correlate with detector parameters (random success)

**Step 3: Clonal Expansion → Affinity Maturation via Gradient Refinement**
- *Mechanism:* Successful detector clones undergo gradient-based fine-tuning to sharpen detection boundaries for specific attack patterns (analogous to somatic hypermutation)
- *Evidence:* RAILS achieves 5-12% robustness improvement through affinity maturation process
- *Falsification:* Fails if gradient refinement causes catastrophic forgetting of previously learned patterns

**Step 4: Affinity Maturation → Improved TPR Under Attacks**
- *Mechanism:* Evolutionary process produces detectors specialized for attack-transformed watermark patterns, enabling recognition that static detectors cannot achieve
- *Evidence:* Target >15% TPR improvement based on RAILS transfer success + WAVES attack diversity
- *Falsification:* Fails if attack diversity exceeds evolutionary capacity (distribution shift)

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | RAILS (Wang et al., 2020) | Weight perturbation creates meaningful population diversity on CIFAR-10/MNIST | Strong |
| Step2 → Step3 | RAILS AISE Architecture | Clonal expansion amplifies successful detection patterns | Strong |
| Step3 → Step4 | RAILS + WEvade (2023) | Gradient refinement improves robustness; attack patterns are learnable | Medium |
| Step4 → Outcome | WAVES (2024) + RAILS | Combined evidence: Adaptive methods improve robustness 5-12%; WAVES confirms attack systematicity | Medium |

**Key Tension:**
- **Tension:** RAILS (2020) demonstrates immune-inspired adaptation improves adversarial robustness by 5-12% on classification tasks, but WEvade (2023) shows watermark attacks use human-imperceptible perturbations that may differ from classification adversarial examples in their systematicity.
- **Resolution:** This verification plan tests whether the immune→classification transfer (validated by RAILS) extends to immune→watermark detection. The WAVES benchmark provides attack diversity to assess transferability across attack types.

### 1.4 Key Assumptions

**A1: Systematic Attack Patterns**
- *Assumption:* Generative attacks create systematic (not purely random) perturbation patterns that can be characterized and learned
- *Evidence:* WEvade (2023, 100 citations) demonstrates adversarial perturbations follow learnable patterns to evade watermark detection
- *Consequence if violated:* If attacks are purely random, evolutionary adaptation cannot converge to useful patterns; hypothesis fails at Step 2

**A2: Meaningful Population Diversity**
- *Assumption:* Detector variants generated through parameter perturbation maintain meaningful diversity in detection boundaries
- *Evidence:* RAILS (2020, 9 citations) demonstrates effective population diversity through weight perturbation on CIFAR-10/MNIST/SVHN
- *Consequence if violated:* Degenerate population provides no benefit over single detector; falls back to static baseline

**A3: Convergence Within Budget**
- *Assumption:* Evolutionary optimization (clonal expansion + affinity maturation) converges within 10 generations
- *Evidence:* RAILS achieves 5-12% robustness improvement within standard training budgets
- *Consequence if violated:* Computational cost exceeds practical deployment; may need simplified adaptation strategy

**A4: Benchmark Representativeness**
- *Assumption:* WAVES benchmark attacks are representative of real-world generative attack distribution
- *Evidence:* WAVES (2024, 72 citations) covers traditional distortions, diffusive attacks, and adversarial attacks; adopted as industry standard
- *Consequence if violated:* Results may not generalize to production attacks; requires additional evaluation on deployment data

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Image watermarking with diffusion-based schemes (DiffuseTrace, Stable Signature, etc.)
- Generative adversarial attacks (diffusive regeneration, adversarial perturbations)
- Offline adaptation with periodic retraining (not real-time continuous adaptation)
- Production environments with labeled attack samples for adaptation

**Where Hypothesis Does NOT Apply:**
- LLM text watermarking (requires different architecture; token-level vs. pixel-level)
- Real-time continuous adaptation (current design uses periodic offline adaptation)
- Zero-shot attack scenarios (requires at least some labeled attack data for adaptation)
- Audio/video watermarking (different signal characteristics; not validated)

**Known Limitations:**
- **Adaptation lag:** Periodic offline adaptation means new attacks may succeed until next retraining cycle
- **Labeled data requirement:** Needs ground truth labels for attacked samples during adaptation phase
- **Distillation trade-off:** Knowledge distillation for efficient deployment may lose some population benefits
- **Computational overhead:** Offline training requires GPU resources for evolutionary optimization

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (TPR Improvement vs Static Baseline)**:
AIWD-E will achieve True Positive Rate (TPR) improvement of >15% over static detector baseline under WAVES generative attacks.

*Measurement:*
- TPR_AIWD-E - TPR_static > 15 percentage points with p < 0.05
- Statistical test: Paired t-test across attack types, n ≥ 25 runs per configuration
- Evaluation: WAVES benchmark attack suite (diffusive + adversarial attacks)

*Basis:*
- RAILS achieves 5-12% robustness improvement on classification tasks
- Cross-domain transfer to watermarking expected to achieve similar or greater gains due to attack systematicity (WEvade evidence)
- Target 15% represents meaningful improvement above RAILS baseline with safety margin

*Success Criteria for Phase 2B:*
- Primary: TPR improvement > 15% (p < 0.05)
- Partial Success: TPR improvement 5-15% (mechanism validated, magnitude lower than expected)
- Falsification: TPR improvement ≤ 5% triggers hypothesis rejection

**Secondary Predictions:**

**P2 (Mechanism Validation - Population Diversity Contribution)**:
Ablation removing population diversity (single detector with affinity maturation only) will achieve <50% of the full AIWD-E TPR improvement, demonstrating that population diversity is essential to the mechanism.

*Measurement:* Compare AIWD-E vs. AIWD-E (no diversity ablation)

**P3 (Deployment Efficiency - Distillation Effectiveness)**:
Knowledge-distilled single detector will retain ≥80% of the adapted ensemble's TPR improvement while achieving inference latency <2x single static detector.

*Measurement:* TPR retention ratio and latency benchmarking

**Falsification Criteria:**

The hypothesis will be **REJECTED** if ANY of the following occur:

1. **Primary Failure**: TPR improvement ≤ 5% over static baseline
   - Interpretation: Immune-inspired adaptation does not transfer to watermark detection domain

2. **Mechanism Failure**: Population diversity ablation achieves ≥90% of full AIWD-E improvement
   - Interpretation: Population diversity is not the operative mechanism; simpler approaches suffice

3. **Practical Failure**: Distilled detector achieves <50% TPR retention OR latency >5x baseline
   - Interpretation: Efficiency-robustness trade-off is unacceptable for deployment

4. **Baseline Failure**: AIWD-E performs worse than fixed ensemble (no evolution) baseline
   - Interpretation: Evolutionary adaptation provides no benefit over simple ensembling

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

**SOTA Comparison: Adaptive Defense Methods**

| Method | Domain | Robustness Improvement | Dataset | Year |
|--------|--------|----------------------|---------|------|
| RAILS | Classification | 5.62-12.5% | CIFAR-10/MNIST/SVHN | 2020 |
| Static Watermark Detectors | Watermarking | Baseline (vulnerable to WAVES attacks) | WAVES | 2024 |
| Fixed Ensemble | Watermarking | Expected ~5-8% (no evolution) | WAVES | Baseline |

**Target Positioning:**
- AIWD-E targets >15% TPR improvement (above RAILS transfer baseline)
- Comparison baselines: Static detector, Fixed ensemble (no evolution), AIWD-E

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (Cohen's d): ~0.6-0.8 (medium-large, based on 15% improvement target with ~10% std)
- Required runs: n ≥ 25 per configuration (for 80% power at α = 0.05)

**Test Specification:**
- Primary comparison: Paired t-test (AIWD-E vs. static detector, same random seeds)
- Multiple comparisons: Bonferroni correction for 3 pairwise comparisons
- Significance level: α = 0.05 (one-tailed for improvement hypothesis)

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does immune-inspired adaptive watermark detection (AIWD-E) achieve measurable TPR improvement (>5%) over static detectors under WAVES generative attacks?"
- Maps to: Primary prediction P1
- Verification type: Empirical (TPR measurement)
- Critical: MUST PASS for Phase 2B to proceed
- Success threshold: TPR improvement > 5% (existence); > 15% (full hypothesis)

**SH2 (Mechanism):**
"Is the 4-step evolutionary mechanism (population diversity → clonal expansion → affinity maturation → improved detection) the actual cause of TPR improvement?"
- Maps to: 4-step causal mechanism (N=4)
- Phase 2B will decompose into 4 sub-hypotheses:
  - **H-M1:** Population initialization creates meaningful detection boundary diversity
  - **H-M2:** Clonal expansion amplifies successful detection patterns
  - **H-M3:** Affinity maturation refines detectors without catastrophic forgetting
  - **H-M4:** Evolved detectors recognize attack patterns static detectors cannot
- Verification type: Causal analysis via ablation studies
- Critical: Determines explanatory power

**SH3 (Comparison):**
"Does AIWD-E outperform both static detectors AND fixed ensembles (no evolution) on WAVES benchmark?"
- Maps to: Secondary predictions P2 and P3
- Verification type: Comparative empirical
- Critical: Determines practical value and isolates evolutionary contribution
- Success criteria: AIWD-E > Fixed Ensemble > Static Detector

### Readiness Checklist

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Hypothesis in "Under [C], if [X], then [Y] because [Z]" format | ✅ | Section 1.1 Core Statement |
| Hypothesis ID assigned | ✅ | H-AIWD-E-v1 |
| Confidence level specified (0.0-1.0) | ✅ | 0.835 |
| Alternative hypothesis (H0) defined | ✅ | Section 1.1 |
| All variables have operationalization from evidence | ✅ | Section 1.2 Variables Table (9 variables) |
| Causal mechanism has evidence at each step | ✅ | Section 1.3 (4 steps, evidence_for_links table) |
| Causal chain length (N) determined | ✅ | N = 4 |
| Key tension identified and resolution proposed | ✅ | Section 1.3 Key Tension |
| Key assumptions list consequences if violated | ✅ | Section 1.4 (4 assumptions with consequences) |
| At least 2 testable predictions exist | ✅ | P1 (primary), P2, P3 in Section 1.6 |
| Falsification criteria defined | ✅ | 4 falsification conditions in Section 1.6 |
| Baselines identified for comparison | ✅ | Static detector, Fixed ensemble |
| SH1, SH2, SH3 clear starting points | ✅ | Decomposition Preview above |

**Status: ALL 13 REQUIREMENTS MET ✓**

### Open Questions

**Q1: Resource Requirements**
- Compute: What GPU resources are needed for 20-detector population training with 5-10 evolutionary generations?
- Estimate: 1-2 GPU-days for offline adaptation (based on RAILS training time)
- Phase 2B verification: Confirm resource availability before SH2 experiments

**Q2: Data Availability**
- WAVES benchmark: Publicly available ✓
- DiffuseTrace implementation: Check if official code is released
- Attack samples with ground truth labels: Need to generate or obtain labeled attacked images
- Phase 2B verification: Secure data access before SH1 experiments

**Q3: Priority Verification Order**
- Recommended order: SH1 → SH2 (H-M1 → H-M2 → H-M3 → H-M4) → SH3
- Rationale: Establish existence first, then validate mechanism, finally confirm practical advantage
- Early exit: If SH1 fails (TPR ≤ 5%), hypothesis rejected without further mechanism investigation

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work (9 sources)

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
