# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-NNPC-v1
**Confidence Level:** 0.80

**Main Hypothesis:**
Under conditions where analog or optical hardware exhibits calibratable stochastic noise, if device noise is characterized and mapped to a unified probabilistic abstraction layer, then Bayesian neural networks can achieve cross-paradigm deployment with <5% accuracy degradation and well-calibrated uncertainty estimates (ECE < 5%), because the statistical properties of hardware noise (mean, variance, temporal correlation) can serve as computational resources for probabilistic sampling instead of requiring digital random number generation.

**Alternative Hypothesis (H0):**
Hardware noise across different paradigms (analog vs. optical) cannot be meaningfully abstracted to a unified probabilistic interface; paradigm-specific noise characteristics (thermal noise in analog, shot noise in optical) require fundamentally different algorithmic treatments, making cross-paradigm deployment infeasible without paradigm-specific model retraining.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Source hardware paradigm | Independent | Analog (memristor crossbar via MemTorch simulation) or optical (photonic NN via pytorch-onn simulation) | {Analog, Optical} |
| Noise calibration quality | Independent | Statistical distance between simulated and actual noise distributions measured via KL divergence | KL < 0.1 (good), 0.1-0.3 (acceptable), >0.3 (poor) |
| Cross-paradigm accuracy retention | Dependent | Absolute difference between simulation accuracy and hardware-deployed accuracy on MNIST/CIFAR-10 | Target: <5% drop |
| Uncertainty calibration | Dependent | Expected Calibration Error (ECE) computed over confidence bins | Target: ECE < 5% |
| Energy efficiency | Dependent | Energy per inference relative to digital Bayesian NN baseline (MC Dropout on GPU) | Target: >2x improvement |
| Task benchmark | Controlled | Standard vision classification datasets | Fixed: MNIST, CIFAR-10 |
| Model architecture | Controlled | Bayesian neural network architecture | Fixed: Bayesian LeNet (MNIST), Bayesian ResNet-18 (CIFAR-10) |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: Noise Characterization
    ↓ (Neural-SDE profiling)
Step 2: Unified Abstraction Layer
    ↓ (Gaussian parameter mapping)
Step 3: Noise-Consuming Deployment
    ↓ (Hardware inference)
Outcome: Cross-Paradigm Probabilistic Inference
```

**Step 1 → Step 2: Noise Characterization → Unified Abstraction**
- **Mechanism:** Device noise is measured via Neural-SDE approach to extract statistical parameters: distribution shape, variance σ², temporal correlation τ
- **Evidence:** Manneschi 2024 demonstrates Neural-SDEs for noise modeling; Wang 2025 shows noise properties can be learned

**Step 2 → Step 3: Unified Abstraction → Noise-Consuming Layers**
- **Mechanism:** Paradigm-specific noise statistics are mapped to common Gaussian interface N(μ_calibrated, σ²_calibrated)
- **Evidence:** Choi 2024 shows photonic probabilistic ML using quantum vacuum noise; biological precedent from Rungratsameetaweemana 2025

**Step 3 → Outcome: Noise-Consuming Layers → Cross-Paradigm Deployment**
- **Mechanism:** BNN layers consume calibrated noise for weight sampling; same trained model runs on both paradigms
- **Evidence:** Safa 2024 achieves 27% accuracy improvement using hardware noise for MCMC; Rasch 2023 shows iso-accuracy on analog

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Manneschi 2024 | Neural-SDEs successfully model noise in physical neuromorphic systems | Strong |
| Step1 → Step2 | Wang 2025 | Variance-aware training improves robustness from 79.3% to 97.6% | Strong |
| Step2 → Step3 | Choi 2024 | Quantum vacuum noise enables probabilistic photonic computing | Strong |
| Step2 → Step3 | Lipka-Bartosik 2023 | Thermodynamic neurons exploit thermal fluctuations as computation | Strong |
| Step3 → Outcome | Safa 2024 | Hardware noise for MCMC sampling outperforms backprop by 27% | Strong |
| Step3 → Outcome | Rasch 2023 | Hardware-aware retraining achieves iso-accuracy on analog IMC | Very Strong |

**Key Tension:**
- **Tension:** Wang 2025 and Rasch 2023 treat noise as obstacle to mitigate, while Safa 2024 and Choi 2024 treat noise as computational resource.
- **Resolution:** NNPC bridges both by using noise characterization (mitigation approach) to enable noise exploitation (resource approach) through calibrated probabilistic semantics.

### 1.4 Key Assumptions

1. **Temporal Stability Assumption:**
   - Device noise is sufficiently stationary for calibration over inference timescale
   - **Consequence if violated:** Calibration becomes invalid; requires continuous re-calibration (Wang 2025 approach)

2. **Bandwidth Sufficiency Assumption:**
   - Noise bandwidth exceeds required sampling rate for probabilistic operations
   - **Consequence if violated:** Insufficient randomness for Bayesian sampling; needs noise amplification

3. **Abstraction Validity Assumption:**
   - Statistical abstraction (Gaussian mapping) captures sufficient noise characteristics
   - **Consequence if violated:** Cross-paradigm transfer fails; fallback to paradigm-specific models

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Analog in-memory computing (memristor crossbars, PCM arrays)
- Optical/photonic neural networks (Mach-Zehnder meshes, diffractive networks)
- Bayesian neural network architectures requiring stochastic sampling
- Standard vision benchmarks (MNIST, CIFAR-10)

**Where Hypothesis Does NOT Apply:**
- Fully digital systems (no hardware noise to exploit)
- Quantum computing (different noise model)
- Neuromorphic/spiking systems (temporal dynamics differ)
- Tasks requiring deterministic outputs

**Known Limitations:**
- May not achieve paradigm-specific optimal performance
- Requires per-device calibration step
- Initial validation limited to 2 paradigms

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Cross-Paradigm Accuracy Retention)**:
A BNN trained on GPU simulation with calibrated noise models will achieve accuracy within 5% of simulation accuracy when deployed on both analog AND optical hardware.

*Measurement*: Accuracy_hardware ≥ Accuracy_simulation - 5% with p < 0.05
*Statistical test*: Paired t-test across n ≥ 20 random seeds
*Success Criteria*: Accuracy drop < 5% on BOTH paradigms
*Falsification*: Accuracy drop > 10% on EITHER paradigm triggers rejection

**Secondary Predictions:**

**P2 (Uncertainty Calibration)**: ECE < 5% on deployed models
**P3 (Energy Efficiency)**: Energy/inference < 50% of MC Dropout baseline

**Falsification Criteria:**

1. **Primary Failure**: Accuracy drop > 10% on either paradigm
2. **Mechanism Failure**: Noise Abstraction Layer cannot achieve KL divergence < 0.3
3. **Comparative Failure**: No advantage over paradigm-specific approaches (Zhuge 2025)

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

**Mode: Absolute Performance with Paradigm-Specific Comparison**

| Method | Paradigm | Benchmark | Performance | Reference |
|--------|----------|-----------|-------------|-----------|
| Digital BNN (MC Dropout) | Digital GPU | CIFAR-10 | ~92% | Baseline |
| Hardware-aware CNN | Analog IMC | CIFAR-10 | ~91% | Rasch 2023 |
| Photonic BNN | Optical only | MNIST | 98% | Zhuge 2025 |
| NNPC (proposed) | Analog + Optical | CIFAR-10 | Target: >87% | This work |

### 1.8 Statistical Verification Design

**Sample Size**: n ≥ 25 per paradigm per benchmark (Cohen's d = 0.5, power = 0.8)
**Test**: Paired t-test with Bonferroni correction (4 tests)
**Report**: Mean ± Std Dev, 95% CI, Cohen's d, p-value

**Ablation Studies Required:**
1. Calibration quality impact: KL = {0.05, 0.1, 0.2, 0.3}
2. Noise level impact: σ = {0.5x, 1x, 2x}
3. Per-paradigm vs. unified training comparison

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Can hardware noise across analog and optical paradigms be characterized with sufficient accuracy (KL divergence < 0.1) to enable unified abstraction?"
- Verification type: Empirical measurement
- Critical: MUST PASS for hypothesis to proceed

**SH2 (Mechanism):**
"Does the Noise Abstraction Layer successfully map paradigm-specific noise to common probabilistic interface?"
- Sub-hypotheses (N=3):
  - H-M1: Noise characterization via Neural-SDE is accurate
  - H-M2: Gaussian mapping preserves computational utility
  - H-M3: Noise-consuming layers achieve comparable performance
- Verification type: Causal analysis with ablation

**SH3 (Comparison):**
"Does NNPC achieve competitive performance vs. paradigm-specific approaches while providing cross-paradigm flexibility?"
- Verification type: Comparative empirical
- Critical: Determines practical value proposition

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-NNPC-v1
- [x] Confidence level specified: 0.80
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=3 steps)
- [x] Causal chain length determined: N=3
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist with primary marked
- [x] Falsification criteria defined
- [x] Baselines identified for comparison
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Hardware Access:** Which platform to prioritize - analog (more accessible) or optical?
2. **Calibration Methodology:** Optimal Neural-SDE architecture for noise characterization?
3. **Uncertainty Metrics:** ECE primary, or include Brier score/NLL?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
