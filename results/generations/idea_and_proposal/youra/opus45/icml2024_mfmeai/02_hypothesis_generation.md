# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-CIPAM-v1
**Confidence Level:** 0.85

**Main Hypothesis:**
Under contact-rich manipulation conditions, if a lightweight predictive network (CIPAM) is trained on VLA input-output pairs and deployed in parallel with VLA, then control frequency will increase from 5 Hz to 50+ Hz while maintaining ≥90% task success rate, because CIPAM learns to predict VLA outputs with sufficient accuracy that only periodic semantic anchoring is needed.

**Alternative Hypothesis (H0):**
A lightweight predictive network trained on VLA outputs cannot achieve sufficient prediction accuracy to enable high-frequency control without significant degradation in task success rate; the VLA's full inference is required at each timestep for reliable manipulation.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| CIPAM Architecture | Independent | 4-layer Transformer encoder (256 dim, 4 heads) | Fixed architecture; ablations on layers (2-6), dims (128-512) |
| Anchoring Frequency | Independent | VLA inference rate | Default 5 Hz, adaptive 5-10 Hz |
| Confidence Threshold | Independent | Softmax confidence cutoff for adaptive anchoring | 0.5-0.9 (default 0.7) |
| Training Data Ratio | Independent | Simulation vs real-world VLA rollouts | 80/20 to 100/0 sim/real |
| Control Frequency | Dependent | Hz measurement of action output rate | Target: 50+ Hz |
| Task Success Rate | Dependent | Percentage of successful task completions | Target: ≥90% of VLA-only baseline |
| Semantic Consistency | Dependent | Cosine similarity between CIPAM and VLA outputs | Target: >95% |
| Safety Violation Rate | Dependent | Percentage of runs with force/torque anomalies | Target: <1% |
| VLA Model | Controlled | OpenVLA 7B parameters | Fixed |
| Robot Embodiment | Controlled | Franka Panda arm | Fixed |
| Task Environment | Controlled | ManiSkill3 manipulation benchmarks | Fixed set of tasks |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: Sensory Input Encoding
├── Image embedding + proprioceptive state + last VLA action
├── CIPAM learns the mapping via supervised learning on VLA rollouts
└── Output: Predicted next action with confidence score

Step 2: High-Frequency Inference
├── Lightweight Transformer (256d, 4 heads, 4 layers)
├── Runs at 50+ Hz on standard robot compute (~15ms/inference)
└── Output: Continuous action stream at 50 Hz

Step 3: Semantic Anchoring
├── VLA runs in parallel at 5 Hz (200ms intervals)
├── Provides ground-truth corrections that prevent prediction drift
└── Output: CIPAM predictions calibrated to VLA semantic understanding

Step 4: Adaptive Safety Control
├── Confidence-based triggering: VLA called when confidence < 0.7
├── Anomaly-based triggering: VLA called on force/torque spike
└── Output: Safe real-time manipulation control
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Nguyen & Person (2025) | "Cerebellum implements model-free implicit mappings of high-dimensional sensorimotor contexts to motor output" | Strong |
| Step 2 → Step 3 | Corki (Huang 2024) | Trajectory prediction achieves 5.9× speedup by exploiting temporal smoothness | Strong |
| Step 3 → Step 4 | OpenVLA (Kim 2024) | VLA maintains semantic grounding through language-conditioned policies | Strong |
| Step 4 → Outcome | ReAct Agent Pattern | Deliberative-reactive separation enables fast responses with slow oversight | Medium |

**Key Tension:**
- **Tension:** Cerebellar models in neuroscience use spike-timing-dependent plasticity for learning, while CIPAM uses standard gradient descent. Additionally, the 200ms anchoring interval may be too long for rapidly changing manipulation scenarios.
- **Resolution:** This verification plan tests whether gradient-based learning is sufficient (acceptable simplification) and includes ablations on anchoring frequency (100ms, 200ms, 500ms) to determine the optimal interval for different task dynamics.

### 1.4 Key Assumptions

1. **Policy Continuity Assumption:** VLA policy outputs vary smoothly over short time horizons (~200ms) for manipulation tasks.
   - *Evidence:* Corki achieves 5.9× speedup via trajectory prediction, implying temporal smoothness
   - *Consequence if violated:* CIPAM predictions will have high error, requiring near-continuous VLA inference (defeating latency gains)

2. **Prediction Learnability:** CIPAM can learn to predict VLA outputs with >90% cosine similarity given sufficient training data.
   - *Evidence:* Cerebellar models learn accurate forward models; neural networks approximate complex functions
   - *Consequence if violated:* Semantic consistency target cannot be met; hypothesis falsified

3. **Acceptable Anchoring Delay:** 200ms maximum delay between VLA inferences is acceptable for most manipulation tasks.
   - *Evidence:* Human reaction time is ~200-300ms; many manipulation tasks have slower dynamics
   - *Consequence if violated:* Error accumulation causes task failures or safety violations

4. **Anomaly Detection Sufficiency:** Proprioceptive feedback (force/torque) provides sufficient signal for detecting dangerous situations.
   - *Evidence:* Contact-rich manipulation generates measurable force signatures
   - *Consequence if violated:* Safety violations increase beyond 1% threshold; adaptive anchoring fails

### 1.5 Scope & Boundaries

**Applies to:**
- Contact-rich manipulation tasks with proprioceptive feedback
- Tasks with relatively smooth dynamics (object manipulation, assembly, pick-and-place)
- VLA models with continuous action outputs (OpenVLA, π0)
- Robot embodiments with force/torque sensing capability

**Does NOT apply to:**
- High-speed dynamic tasks requiring <10ms latency (catching, batting)
- Tasks with discontinuous state changes (contact making/breaking at high frequency)
- VLA models with discrete action outputs
- Embodiments without proprioceptive feedback

**Known Limitations:**
- Variable VLA frequency (5-10 Hz) instead of fixed 5 Hz under uncertainty
- Requires simulation environment for bootstrap training
- Anomaly detection thresholds may need task-specific tuning
- CIPAM must be retrained when switching VLA models

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Control Frequency vs Task Success Trade-off):**
If CIPAM is trained on ≥10,000 VLA rollout trajectories and deployed with adaptive safety anchoring, then:
- Control frequency will increase from 5 Hz to 50+ Hz (10× improvement)
- Task success rate will remain ≥90% of VLA-only baseline
- With p < 0.05 (paired t-test, n ≥ 20 runs per condition)

*Measurement:*
- Control frequency: Average action output rate (Hz) measured over task duration
- Task success: Binary success/failure on ManiSkill3 benchmark tasks

**Secondary Predictions:**

**P2 (Semantic Consistency):**
CIPAM predictions will achieve >95% cosine similarity with VLA outputs during normal operation (confidence ≥ 0.7).

**P3 (Safety via Adaptive Anchoring):**
With adaptive safety anchoring enabled, safety violation rate will be <1%, comparable to VLA-only baseline.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any of the following occur:

1. **Primary Failure:** Task success rate drops below 80% of VLA-only baseline (≥10% degradation) despite CIPAM achieving 50+ Hz control

2. **Mechanism Failure:** CIPAM cannot achieve >85% cosine similarity with VLA outputs, indicating the prediction learning mechanism is insufficient

3. **Safety Failure:** Safety violation rate exceeds 5% even with adaptive anchoring enabled

4. **Efficiency Failure:** CIPAM inference time exceeds 20ms, preventing 50 Hz operation

### 1.7 SOTA Baseline (Optional)

*Not applicable* - Absolute performance validation mode (latency improvement target).

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (Cohen's d): ~2.0 (large effect for 10× latency improvement)
- Required runs: n ≥ 20 per condition
- Statistical power: 0.95

**Test Specification:**
- Primary comparison: Paired t-test (same random seeds, same tasks)
- Significance level: α = 0.05
- Report format: Mean ± Std Dev, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does CIPAM achieve 50+ Hz control frequency while maintaining task performance on ManiSkill3 manipulation benchmarks?"
- Maps to: Primary prediction (P1)
- Verification type: Empirical measurement
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the cerebellum-inspired predictive coding mechanism the actual cause of the latency-performance trade-off improvement?"
- Maps to: Causal mechanism (N=4 steps)
- Phase 2B will decompose into 4 sub-hypotheses:
  - H-M1: Prediction learning from sensorimotor context
  - H-M2: Efficient high-frequency inference
  - H-M3: Semantic anchoring via periodic VLA
  - H-M4: Safety through adaptive triggering
- Verification type: Ablation studies and mechanism probing

**SH3 (Comparison):**
"Does CIPAM outperform existing latency reduction approaches (Corki, Consistency Policy) on the latency-accuracy trade-off?"
- Maps to: Secondary predictions (P2, P3)
- Verification type: Comparative empirical

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-CIPAM-v1
- [x] Confidence level specified: 0.85
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (4 steps, evidence table provided)
- [x] Causal chain length (N=4) determined and stored
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (3 provided, primary marked)
- [x] Falsification criteria are defined (4 criteria)
- [x] Baselines are identified for comparison (OpenVLA, Corki, Consistency Policy)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Resource Requirements:** What compute resources are needed for CIPAM training? Estimated: 8× A100 GPUs for 2 days on 10k rollout trajectories.

2. **Data Availability:** Can sufficient VLA rollout data be collected from ManiSkill3 simulation? Estimated: 10k trajectories require ~100 GPU-hours of OpenVLA inference.

3. **Technical Feasibility:** Can CIPAM achieve <20ms inference on robot edge compute (e.g., NVIDIA Jetson)? Requires inference optimization and potential quantization.

4. **Priority Verification Order:** Recommended order: SH1 → SH2-M1,M2 → SH3 → SH2-M3,M4

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
