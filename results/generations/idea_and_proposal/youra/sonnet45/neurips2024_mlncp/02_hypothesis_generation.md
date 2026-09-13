# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-06
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-AnalogDEQ-v1
**Confidence Level:** 0.88

**Main Hypothesis:**
Under DEQ fixed-point iteration conditions with analog IMC hardware (FeFET-based, 5-bit precision), if matrix-vector operations are offloaded to analog in-memory computing with digital convergence control, then DEQ training achieves 10-100× energy efficiency improvement while maintaining convergence within 5% of digital baseline, because analog noise acts as beneficial stochastic perturbation (bounded by Hashemi threshold δ = σ_min(J)/√n) and adaptive momentum via voltage control accelerates convergence.

**Alternative Hypothesis (H0):**
There is no energy efficiency advantage from hybrid analog-digital DEQ architecture compared to purely digital DEQ implementation, OR analog noise causes convergence degradation beyond 5% accuracy loss, making the approach impractical.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Analog bit precision | Independent | FeFET device precision configuration | 3-bit, 5-bit, 8-bit |
| Momentum parameter (α) | Independent | Analog reference voltage V_ref | 0.1-0.9 (voltage-encoded) |
| Hybrid partitioning ratio | Independent | Ratio of analog vs digital operations | 0-100% (100% = full analog) |
| Crossbar size | Independent | Analog crossbar dimensions | 128×128, 256×256 |
| Tiling strategy | Independent | Accumulation method for large layers | Sequential, Parallel |
| Convergence speed | Dependent | Iterations to fixed-point (\|x_{k+1} - x_k\| < 10⁻⁴) | 10-100 iterations |
| Energy consumption | Dependent | Joules per inference (hardware-measured) | 0.01-1 J (target: 100× reduction) |
| Final model accuracy | Dependent | ImageNet top-1 accuracy | 70-85% (within 5% of digital) |
| Training throughput | Dependent | Samples processed per second | 100-10000 samples/s |
| DEQ model architecture | Controlled | Fixed DEQ architecture type | MDEQ, DEQ-Transformer |
| Dataset | Controlled | Standard benchmark dataset | ImageNet, CIFAR-10 |
| Baseline comparison | Controlled | Comparison method | Digital DEQ + Anderson acceleration |

### 1.3 Causal Mechanism

The hypothesis proposes a **3-step causal chain** from analog computation to energy-efficient DEQ training:

**Step 1: Parallel Analog Execution**
- Analog IMC performs matrix-vector multiplication in O(1) time using physical in-memory computation
- Crossbar architecture enables parallel analog operations across all matrix elements simultaneously
- Eliminates data movement bottleneck (von Neumann architecture limitation)

**Step 2: Noise-Tolerant Convergence**
- Analog device mismatch (FeFET variability) introduces stochastic noise to fixed-point iteration
- Noise bounded by Hashemi threshold: Var(noise) < δ² where δ = σ_min(J)/√n
- Digital controller maintains global convergence guarantee via outer loop validation

**Step 3: Momentum-Accelerated Iteration**
- Adaptive momentum parameter α encoded as analog voltage V_ref
- Digital controller adjusts V_ref every K=10 iterations based on spectral radius estimate
- Wadayama's Chebyshev step optimization reduces iteration count by controlling eigenvalue spectrum

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Analog IMC hardware (cross-sim) | 100× energy efficiency for analog matrix operations | Strong |
| Step 2 → Step 3 | Hashemi (2025) "Stochastic FPI" | Theorem 3.1: Convergence guaranteed for noise variance < δ² | Strong |
| Step 3 → Outcome | Wadayama (2020) "Deep Unfolding" | Spectral radius control via learnable parameters accelerates convergence | Medium |

**Key Tension:**
Hashemi (2025) assumes i.i.d. noise, but FeFET device mismatch exhibits spatial correlation within crossbars. However, strategic device placement and crossbar tiling can decorrelate noise sources (reducing correlation from ~0.6 to <0.2 based on FeFET characterization studies).

**Resolution:** Phase 2B will test whether decorrelation techniques (device randomization, tiling) reduce correlation sufficiently to satisfy Hashemi's i.i.d. assumption within acceptable approximation (correlation < 0.3).

### 1.4 Key Assumptions

1. **FeFET Device Characteristics Match Literature**
   - Assumption: Analog IMC device characteristics (resistance range, mismatch variance) match FeFET specifications from Pereira-Rial (2025)
   - Evidence: 5-bit precision with feedback compensation demonstrated
   - **Consequence if violated:** If actual device variance > literature, noise threshold exceeded → divergence

2. **Jacobian Stability Under Perturbation**
   - Assumption: DEQ Jacobian eigenvalues remain stable under analog perturbations (Lipschitz constant preserved below noise threshold)
   - Evidence: DEQ theory shows contractive mappings (eigenvalues < 1) are robust to small perturbations
   - **Consequence if violated:** If eigenvalues destabilize, convergence guarantee breaks → unreliable fixed-point solving

3. **On-Chip Communication Latency**
   - Assumption: Hybrid communication latency on-chip < 1ns/element, off-chip PCIe ~ 50-100ms overhead
   - Evidence: Standard on-chip interconnect specifications
   - **Consequence if violated:** If latency > 10ns/element, communication overhead negates analog speedup

4. **Spectral Radius Estimation Efficiency**
   - Assumption: Digital controller can estimate spectral radius every K=10 iterations with < 1% computational overhead
   - Evidence: Power iteration method for dominant eigenvalue is O(n) complexity
   - **Consequence if violated:** If overhead > 5%, momentum adaptation cost exceeds benefit

5. **Noise Decorrelation Feasibility**
   - Assumption: Noise distribution is approximately i.i.d. or can be decorrelated via strategic device placement in crossbar
   - Evidence: Device randomization techniques reduce correlation in analog arrays
   - **Consequence if violated:** If correlation > 0.5, Hashemi's convergence bound invalid → potential divergence

### 1.5 Scope & Boundaries

**Applies to:**
- DEQ models with Lipschitz-continuous fixed-point functions (contractive mappings, eigenvalues < 1)
- Moderate-scale networks (< 1B parameters, layers ≤ 512×512 for practical tiling)
- Standard supervised learning datasets (ImageNet, CIFAR-10, medical imaging)
- Training and inference scenarios requiring energy efficiency (edge deployment, sustainability-focused AI)

**Does NOT apply to:**
- Non-contractive fixed-point iterations (divergent or marginally stable systems)
- Extremely low-bit analog hardware (< 3-bit insufficient for DEQ convergence precision)
- Models requiring exact numerical precision (scientific computing, numerical solvers)
- Off-chip analog IMC for small models (< 128×128 layers) due to communication overhead dominance
- Very large DEQ layers (> 1024×1024) where tiling overhead > 20% negates efficiency gains

**Known Limitations:**
1. On-chip analog IMC required for full speedup (off-chip PCIe adds 50-100ms latency per iteration)
2. Tiling overhead grows quadratically with layer size (5% for 256×256, 15% for 512×512, 25% for 1024×1024)
3. Noise bound depends on DEQ Jacobian conditioning (ill-conditioned models may require 8-bit precision instead of 5-bit)
4. Calibration complexity increases with crossbar count (per-device feedback compensation needed)

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Energy Efficiency vs Digital DEQ Baseline):**
Our hybrid analog-digital DEQ approach will achieve energy consumption < 0.01 J/inference (100× reduction from typical 1 J/inference for digital DEQ) while maintaining ImageNet top-1 accuracy ≥ 75% (within 5% of digital baseline 78-80%).

*Measurement:*
- Energy: Hardware power measurement (oscilloscope + current sensor) integrated over inference time
- Accuracy: Standard ImageNet validation set (50k images)
- Statistical test: Paired t-test comparing hybrid vs digital energy, n ≥ 25 runs, p < 0.05

*Basis:*
Analog IMC literature (cross-sim simulator) demonstrates 100× energy efficiency for matrix operations. DEQ's tolerance for approximate solutions (5% accuracy degradation acceptable per Lin 2025) aligns with 5-bit analog precision capabilities.

*Success Criteria for Phase 2B:*
- Primary: Energy < 0.01 J/inference AND Accuracy ≥ 75% (p < 0.05)
- Falsification: Energy > 0.1 J/inference (< 10× improvement) OR Accuracy < 72% (> 7% degradation) triggers hypothesis rejection

**Secondary Predictions:**

**P2 (Convergence Speed with Momentum Adaptation):**
Adaptive momentum via voltage control (Wadayama spectral radius optimization) will reduce convergence iterations by 10× compared to vanilla fixed-point iteration (baseline: Anderson acceleration).

*Measurement:* Iteration count to reach |x_{k+1} - x_k| < 10⁻⁴
*Basis:* Deep unfolding studies show learnable momentum parameters can achieve 5-15× acceleration

**P3 (Noise Tolerance Validation):**
Analog noise variance will remain below Hashemi threshold (Var(noise) < δ² where δ = σ_min(J)/√n) for 5-bit FeFET precision with device decorrelation, validated by convergence success rate > 95%.

*Measurement:* Empirical noise variance from FeFET characterization, Jacobian singular value analysis
*Basis:* FeFET literature reports mismatch σ ~ 0.05-0.1, Hashemi bound δ ~ 0.2-0.3 for typical DEQ Jacobians

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure**: Energy consumption > 0.1 J/inference (< 10× improvement over digital baseline)
   - Indicates analog efficiency advantage insufficient to justify hybrid complexity

2. **Convergence Failure**: Accuracy degradation > 7% compared to digital DEQ (< 72% on ImageNet if digital achieves 78%)
   - Indicates analog noise exceeds tolerable threshold

3. **Mechanism Failure**: Noise variance exceeds Hashemi threshold (Var(noise) > δ²) leading to divergence in > 10% of trials
   - Invalidates core theoretical foundation

4. **Scalability Failure**: Hybrid approach slower than digital for layers < 256×256 due to communication overhead
   - Indicates practical applicability too narrow

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

N/A - This hypothesis targets absolute energy efficiency improvement, not SOTA accuracy comparison. The goal is 100× energy reduction while maintaining acceptable accuracy (within 5% of digital baseline), not beating current SOTA DEQ accuracy.

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (energy reduction): Cohen's d ~ 5.0 (100× reduction is very large effect)
- Required runs: n ≥ 25 (conservative for high-variance hardware measurements)
- Statistical power: 0.8

**Test Specification:**
- Method: Paired t-test (same DEQ model, dataset, random seeds for hybrid vs digital)
- Significance level: α = 0.05 (two-tailed for energy, one-tailed for accuracy degradation)
- Report format: Mean energy ± Std Dev, Mean accuracy ± Std Dev, 95% CI, Cohen's d, p-value

**Hardware Validation Protocol:**
- Energy measurement: Oscilloscope + shunt resistor for analog power, GPU power monitoring for digital
- Calibration: 10 warm-up runs to stabilize FeFET devices
- Replication: 3 independent hardware setups to verify reproducibility

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence - Foundation):**
"Does hybrid analog-digital fixed-point iteration achieve 10-100× energy efficiency improvement while maintaining DEQ convergence within 5% accuracy of digital baseline?"

- Maps to: Primary prediction (P1)
- Verification type: Empirical (hardware measurement + simulation)
- Critical: MUST PASS for Phase 2B to proceed - validates core value proposition

**SH2 (Mechanism - Core):**
"Is the proposed 3-step causal mechanism (analog parallel execution → noise-tolerant convergence → momentum-accelerated iteration) the actual cause of energy efficiency gains and maintained accuracy?"

This will decompose into **3 sub-hypotheses** in Phase 2B (based on causal chain length N=3):
- **H-M1:** Analog IMC parallel execution reduces computation time by 100× (Step 1)
- **H-M2:** Bounded analog noise (Var < δ²) maintains convergence (Step 2)
- **H-M3:** Adaptive momentum via voltage control accelerates convergence by 10× (Step 3)

- Verification type: Causal analysis (ablation studies, mechanism isolation)
- Critical: Determines explanatory power and identifies failure modes

**SH3 (Comparison - Validation):**
"Does hybrid analog-digital DEQ outperform purely digital DEQ and purely analog inference systems across energy, accuracy, and flexibility dimensions?"

- Maps to: Secondary predictions (P2, P3) and baseline comparisons
- Verification type: Comparative empirical (head-to-head benchmarking)
- Critical: Determines practical value and competitive positioning

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned (H-AnalogDEQ-v1)
- [x] Confidence level specified (0.88)
- [x] Alternative hypothesis (H0) defined (no efficiency advantage OR accuracy degradation)
- [x] All variables have operationalization from evidence (12 variables operationalized)
- [x] Causal mechanism has evidence at each step (3 steps, evidence_for_links table complete)
- [x] Causal chain length (N) determined and stored (N=3: moderate complexity)
- [x] Key tension identified and resolution proposed (i.i.d. noise assumption vs spatial correlation → decorrelation techniques)
- [x] Key assumptions list consequences if violated (5 assumptions with specific failure modes)
- [x] At least 2 testable predictions exist (P1, P2, P3 with primary P1 marked)
- [x] Falsification criteria are defined (4 criteria with quantitative thresholds)
- [x] Baselines are identified for comparison (Digital DEQ + Anderson, Purely Analog)
- [x] SH1, SH2, SH3 are clear starting points (total: 2+3=5 sub-hypotheses for Phase 2B)

**All Phase 2B requirements met ✓**

### Open Questions

1. **Hardware Access & Resources:**
   - Can we obtain FeFET testbed access for hardware validation? (University partnerships, industry collaborations?)
   - Alternative: Simulation-first approach using AnalogAI + cross-sim sufficient for initial validation?
   - Timeline: 6 months simulation track vs 12-18 months hardware track

2. **Data & Model Scope:**
   - Should Phase 2B start with smaller datasets (CIFAR-10) before scaling to ImageNet?
   - Which DEQ architecture priority: MDEQ (vision) vs DEQ-Transformer (NLP)? Impact on hardware requirements.
   - Crossbar size availability: 128×128 realistic near-term, 256×256 requires custom fabrication?

3. **Verification Priority & Dependencies:**
   - Should SH2 mechanism validation (3 sub-hypotheses) precede SH1 existence validation?
   - Rationale: If mechanism fails (e.g., noise exceeds threshold), existence validation becomes irrelevant
   - Proposed order: H-M2 (noise tolerance) → H-M1 (parallel speedup) → H-M3 (momentum) → SH1 (integrated system) → SH3 (comparison)

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-06*
