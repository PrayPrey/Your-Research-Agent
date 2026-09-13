# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-IEGH-HP-v1
**Confidence Level:** 0.88

**Main Hypothesis:**
Under training conditions with balanced excitatory-inhibitory neural populations, **if** inhibitory error neurons compute local prediction errors that gate Hebbian plasticity via neuromodulator scaling, **then** SNNs will achieve credit assignment comparable to backpropagation-based methods (within 10% accuracy) while requiring significantly fewer computational operations, **because** inhibitory error-gating provides local gradient-equivalent signals that enable weight updates proportional to prediction mismatch.

**Alternative Hypothesis (H0):**
Local error-gated Hebbian plasticity does not provide sufficient credit assignment for SNN training. Specifically: (1) inhibitory error neurons cannot reliably compute prediction errors that correlate with gradient signals, OR (2) the neuromodulator broadcast mechanism is too coarse to enable layer-specific learning, resulting in accuracy more than 20% below surrogate gradient baselines.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Inhibitory Error Gating | Independent | Binary error gate computed from inhibitory neuron activity exceeding threshold; measured as spike rate of error neurons | Gate threshold: 0.1-0.5 normalized spike rate |
| Neuromodulator Scale | Independent | Scalar multiplier (0.01-1.0) applied to Hebbian updates based on task-level loss feedback | 0.01-1.0; optimal expected ~0.1-0.3 |
| Homeostatic Rate | Independent | Learning rate for inhibitory synapses that maintains E/I balance | 0.001-0.1; default 0.01 |
| Architecture Config | Independent | Layer count, neurons per layer, connectivity pattern | 2-4 layers; 128-512 neurons/layer |
| Classification Accuracy | Dependent | Test accuracy (%) on benchmark datasets; compared against surrogate gradient SNN baseline | MNIST: 95-99%; CIFAR-10: 70-85%; SHD: 75-90% |
| Energy Efficiency | Dependent | Synaptic operations per inference (SOPs); measured as sum of active synapses × spike events | 50-80% reduction vs. backprop baseline |
| Continual Learning Performance | Dependent | Backward transfer metric: accuracy drop on previous tasks after learning new task | <5% forgetting (vs. >30% for naive baselines) |
| Dataset | Controlled | Fixed benchmarks | MNIST, CIFAR-10, SHD |
| Random Seed | Controlled | Fixed seeds for reproducibility | {0, 42, 123, 456, 789} |
| Training Epochs | Controlled | Fixed epochs per dataset | MNIST=50, CIFAR-10=100, SHD=100 |
| Baseline Architecture | Controlled | Identical network topology for all methods | Same layer sizes, neuron models |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
[Step 1: Prediction Encoding]
Excitatory principal neurons encode predictions via spike patterns
    ↓
[Step 2: Error Computation]
Inhibitory error neurons compute prediction mismatch via subtractive/divisive inhibition
    ↓
[Step 3: Gated Plasticity]
Error signals gate Hebbian weight updates: Δw = η × pre × post × error_gate
    ↓
[Step 4: Global Credit Assignment]
Neuromodulator broadcast scales all gated updates based on task-level feedback
    ↓
[Outcome: Backprop-Free Learning]
SNN achieves supervised learning without explicit gradient computation
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Wilmes 2024 | Layer 2/3 neurons receive predictions and compute UPE via inhibitory interneurons | Strong |
| Step2 → Step3 | Wilmes 2024, Xiao 2024 | Inhibitory activity can gate plasticity; Hebbian lateral connections enable selective updates | Strong |
| Step3 → Step4 | Tian 2025 (DA-SSDP) | Loss-sensitive gating adjusts local update magnitude without altering model structure | Medium |
| Step4 → Outcome | Multiple SNN papers | Local learning rules with global modulation can train SNNs on classification tasks | Medium |

**Key Tension:**
- **Tension:** Wilmes 2024 demonstrates uncertainty-modulated prediction errors in continuous-time cortical models, but SNN implementations use discrete LIF neurons with simplified dynamics.
- **Resolution:** This verification plan will test whether the subtractive/divisive inhibition mechanism translates effectively to discrete spiking dynamics. Ablation study will compare continuous vs. discrete error computation.

### 1.4 Key Assumptions

1. **E/I Balance Achievability**
   - Assumption: Homeostatic inhibitory plasticity can maintain stable E/I balance throughout training
   - Evidence: Asabuki 2024 demonstrates prediction-based plasticity with homeostatic inhibitory regulation
   - Consequence if violated: Training instability, divergence, or oscillations → Mitigation: adaptive homeostatic rate tuning

2. **Local Credit Assignment Sufficiency**
   - Assumption: Error-gated Hebbian learning provides sufficient credit assignment for moderate-complexity tasks (MNIST, CIFAR-10)
   - Evidence: Wilmes 2024 shows local UPE computation can guide learning; Xiao 2024 achieves near-zero forgetting with Hebbian orthogonal projection
   - Consequence if violated: Performance gap >10% vs. backprop baselines → Fallback: hybrid approach with sparse backprop

3. **Neuromodulator Broadcast Effectiveness**
   - Assumption: Task-level feedback can be effectively broadcast to modulate layer-specific plasticity
   - Evidence: Tian 2025 DA-SSDP shows loss-sensitive gating works across network layers
   - Consequence if violated: Coarse credit assignment → poor convergence → Mitigation: layer-specific neuromodulator scaling

4. **LIF Model Compatibility**
   - Assumption: Subtractive and divisive inhibition can be implemented in standard LIF neuron models (snnTorch)
   - Evidence: snnTorch supports custom neuron dynamics and lateral connections
   - Consequence if violated: Need custom neuron implementation → increases implementation difficulty

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Image classification tasks (MNIST, CIFAR-10, Fashion-MNIST)
- Neuromorphic audio classification (SHD, SSC)
- Event-based vision (DVS128 Gesture)
- Networks with 2-4 layers, moderate depth
- Online/continual learning scenarios

**Where Hypothesis Does NOT Apply:**
- Large-scale datasets (ImageNet) without additional scaling work
- Complex reasoning or sequence-to-sequence tasks
- Very deep networks (>6 layers) - credit assignment may degrade
- Real-time neuromorphic deployment (requires Loihi compilation, out of scope)

**Known Limitations:**
- Accuracy gap vs. backpropagation may exist (targeted: <10%)
- Requires custom snnTorch implementation (not standard API)
- Hyperparameter sensitivity (gating threshold, neuromodulator scale, homeostatic rate)
- May not generalize to all SNN architectures (tested on feedforward + lateral connections)

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Accuracy vs. Baseline):**
IEGH-HP will achieve classification accuracy within 10% of surrogate gradient SNN baselines on MNIST, CIFAR-10, and SHD benchmarks.

*Measurement:*
- Test accuracy (%) across 5 random seeds
- Statistical test: Paired t-test (same seeds), p < 0.05
- Baseline: Surrogate gradient SNN with identical architecture

*Expected Values:*
| Dataset | Baseline (Expected) | IEGH-HP Target | Acceptable Gap |
|---------|---------------------|----------------|----------------|
| MNIST | 98.5% ± 0.3% | ≥88.5% | <10% |
| CIFAR-10 | 78% ± 1.5% | ≥68% | <10% |
| SHD | 85% ± 2% | ≥75% | <10% |

*Success Criteria:* Primary prediction PASS if accuracy gap ≤ 10 percentage points on all three datasets.

**Secondary Predictions:**

**P2 (Energy Efficiency):**
IEGH-HP will require 30-50% fewer synaptic operations per inference compared to backpropagation-based training, due to elimination of backward pass.

**P3 (Continual Learning):**
IEGH-HP with homeostatic plasticity will exhibit <5% backward transfer (forgetting) on sequential task learning, compared to >30% for naive fine-tuning baselines.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any of the following occur:

1. **Primary Failure:** IEGH-HP accuracy is more than 20% below surrogate gradient baseline on ANY benchmark dataset

2. **Mechanism Failure:** Ablation study shows that removing inhibitory error-gating does NOT significantly degrade performance (p > 0.1)

3. **Stability Failure:** Training diverges in >50% of random seeds

4. **Efficiency Failure:** IEGH-HP requires MORE synaptic operations than backpropagation baseline

### 1.7 SOTA Baseline (Optional)

*Not applicable - IEGH-HP is a novel architecture, not targeting SOTA improvement on existing benchmarks.*

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (Cohen's d): ~1.0
- Required runs: n ≥ 15 per condition
- Statistical power: 0.8

**Test Specification:**
- Method: Paired t-test (same random seeds)
- Significance level: α = 0.05 (one-tailed)
- Multiple comparison correction: Bonferroni for 3 datasets

**Report Format:**
- Mean ± Standard Deviation, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does inhibitory error-gated Hebbian learning enable successful training of SNNs on classification tasks without backpropagation?"
- Maps to: Primary prediction (P1)
- Verification type: Empirical classification accuracy
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the proposed 4-step mechanism (prediction encoding → error computation → gated plasticity → global modulation) the actual cause of learning success?"
- Maps to: Causal mechanism (4 causal links)
- Will decompose into 4 sub-hypotheses in Phase 2B:
  - H-M1: Prediction encoding in excitatory neurons
  - H-M2: Error computation via inhibitory neurons
  - H-M3: Error-gated Hebbian plasticity
  - H-M4: Neuromodulator broadcast scaling
- Verification type: Ablation studies for each component

**SH3 (Comparison):**
"Does IEGH-HP provide advantages over surrogate gradient baselines in energy efficiency and/or continual learning?"
- Maps to: Secondary predictions (P2, P3)
- Verification type: Comparative empirical

**Total Sub-Hypotheses in Phase 2B:** 2 + 4 = 6

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-IEGH-HP-v1
- [x] Confidence level specified: 0.88
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (4 steps)
- [x] Causal chain length (N=4) determined
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (3 provided)
- [x] Falsification criteria are defined (4 criteria)
- [x] Baselines are identified for comparison
- [x] SH1, SH2, SH3 are clear starting points

**All 13 checklist items: PASS**

### Open Questions

1. **Implementation Complexity:** How difficult is the custom layer implementation in snnTorch? Need to estimate development time for lateral inhibitory connections + gating mechanism.

2. **Hyperparameter Sensitivity:** What is the sensitivity to gating threshold, neuromodulator scale, and homeostatic rate? May need extensive grid search or Bayesian optimization.

3. **Scaling Behavior:** Will the 10% accuracy gap increase or decrease with network depth? Phase 2B should include explicit depth scaling experiments.

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-13*
