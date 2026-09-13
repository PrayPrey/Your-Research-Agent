# Phase 2B Summary: Ready for Verification Planning

**Date:** 2026-02-06
**Hypothesis ID:** H-neurips2023-mlncp-DEQ-neuromorphic
**Confidence:** 0.82 (High)
**Source:** Round 1 FEASIBLE hypothesis from Phase 2A

---

## Core Hypothesis (Testable)

**Main Claim:**
Mapping DEQ fixed-point iterations to neuromorphic recurrent dynamics (SpiNNaker2/Intel Loihi) with hybrid-precision training achieves **10-27× energy reduction** with **<2% accuracy degradation**, enabling constant-memory edge deployment.

**Alternative (H0):**
Neuromorphic DEQ either fails to achieve >5× energy reduction OR incurs >5% accuracy degradation, making the approach impractical.

---

## Primary Testable Prediction (P1)

**IF:** DEQ (depth=5, channels=64) trained with hybrid-precision QAT (ε=1e-2) deployed on SpiNNaker2 for CIFAR-10

**THEN:**
- ✅ Energy: ≤10 μJ (vs. 100-300 μJ GPU = 10-30× reduction)
- ✅ Accuracy: ≥88% (vs. 90% GPU = <2.2% degradation)
- ✅ Memory: O(1) constant (~5-10 MB)
- ✅ Latency: ≤50ms (15-20 iterations)

**Falsification:** Accept H0 if energy reduction <5× OR accuracy loss >5%

---

## Causal Mechanism (3-Step Chain)

```
[DEQ Fixed-Point: z_{t+1}=f(z_t)]
    ↓ [Mathematical Mapping]
[SNN Recurrent Dynamics on Neuromorphic Hardware]
    ↓ [Sparse Event-Driven Computation]
[10-27× Energy Reduction + <2% Accuracy Loss]
```

**Key Mechanisms:**
1. **Sparsity:** Only active neurons consume power (14.4 fJ/spike)
2. **Local Memory:** Eliminate GPU↔CPU data transfer overhead
3. **QAT Robustness:** Simulate neuromorphic noise during training

**Critical Tension:** Neuromorphic noise increases iterations vs. sparse computation reduces per-iteration energy → Net 10-27× gain expected

---

## Key Variables

| Type | Variable | Levels/Range |
|------|----------|--------------|
| **Independent** | Neuromorphic Platform | SpiNNaker2, Intel Loihi 2 |
| **Independent** | Convergence Tolerance (ε) | 1e-2, 1e-3, 1e-4 |
| **Independent** | Training Method | Hybrid-Precision QAT, Baseline |
| **Dependent** | Energy per Inference | Joules (J) |
| **Dependent** | Accuracy | Top-1 %, PSNR (MRI) |
| **Dependent** | Convergence Time | Iterations, milliseconds |
| **Controlled** | Dataset | MNIST, CIFAR-10, fastMRI |

---

## Scope & Boundaries

**Applicable:**
- Implicit models with fixed-point iterations (DEQs, Neural ODEs)
- Edge deployment prioritizing energy over speed (medical, mobile, IoT)
- Neuromorphic hardware with recurrence (SpiNNaker2, Loihi)

**NOT Applicable:**
- Explicit feedforward networks (ResNets, Transformers)
- Ultra-high-precision requirements (ε<1e-3 unreliable)
- Training-from-scratch on neuromorphic (deployment-focused)

**Known Limitations:**
- Neuromorphic spike noise prevents tight tolerance (ε<1e-3)
- Custom compiler required (not plug-and-play)
- Limited by chip capacity (~131k neurons for Loihi 2)

---

## Contributions Summary

### 1. Theoretical
**Title:** Computational Equivalence Between Implicit Models and Neuromorphic Recurrent Dynamics

**Innovation:** Formal mapping DEQ fixed-point ↔ SNN recurrence with Lyapunov stability extension to bounded noise

**Novelty:** First to bridge implicit models (continuous optimization) and neuromorphic computing (discrete-event)

### 2. Methodological
**Title:** Quantization-Aware Implicit Differentiation (QA-ID)

**Innovation:** Hybrid-precision training - simulate neuromorphic noise (forward), FP16 gradients (backward), surrogate gradients for implicit differentiation

**Novelty:** First application of QAT+surrogate gradients to implicit models

### 3. Practical
**Title:** Ultra-Low-Power Edge Deployment of Implicit Models

**Innovation:** Enable DEQ on neuromorphic hardware with 10-27× energy reduction

**Applications:** Medical imaging (portable MRI), mobile vision (drones), IoT (sensor networks)

---

## Key Related Work (Foundations)

| Paper | Type | Relation to Us |
|-------|------|---------------|
| Bai et al. (2019) DEQ | Scholar | Foundational architecture → We add neuromorphic acceleration |
| McCallum et al. (2025) Reversible DEQ | Scholar | Gradient efficiency → We adapt to neuromorphic constraints |
| Chu et al. (2023) Lyapunov-stable DEQ | Scholar | Stability framework → We extend to noisy hardware |
| Gonzalez et al. (2024) SpiNNaker2 | Scholar | Hardware platform → We deploy DEQs on it |
| Chandarana et al. (2022) Loihi | Scholar | Energy baseline (27×) → We target similar gains |
| Neftci et al. (2019) Surrogate Gradients | Scholar | SNN training → We apply to DEQ backward pass |
| BitsAndBytes QAT | Archon | QAT principles → We adapt to neuromorphic noise |

**Gap We Fill:** No prior work on implicit models (DEQs) on neuromorphic hardware

---

## Phase 2B Decomposition Preview

**SH1 (Existence - Proof of Concept):**
- **Claim:** DEQ→SNN mapping achieves convergence on simulators
- **Verification:** Compare SNN vs. PyTorch DEQ dynamics (correlation >0.95, convergence >90%)
- **Success:** MNIST convergence ≥90%, MAE <5%

**SH2 (Mechanism - Energy & Accuracy):**
- **Claim:** QAT enables 10-27× energy + <2% accuracy loss
- **Verification:** Train with QA-ID, deploy on simulator, measure energy/accuracy
- **Success:** ≤10 μJ energy, ≥88% accuracy on CIFAR-10

**SH3 (Comparison - SOTA Benchmark):**
- **Claim:** Neuromorphic DEQ dominates Pareto frontier
- **Verification:** Compare 5 approaches (pruning, distillation, explicit neuromorphic, approximate solvers)
- **Success:** Neuromorphic DEQ <50% energy of next-best at ≥88% accuracy

---

## Phase 2B Readiness Checklist

**Research Design:** ✅ Complete
- [✅] Hypothesis testable (falsifiable predictions defined)
- [✅] Variables defined (IV, DV, controlled)
- [✅] Causal mechanism articulated
- [✅] Assumptions stated (5 key assumptions)
- [✅] Scope/boundaries clear
- [✅] Statistical design specified

**Literature:** ✅ Complete
- [✅] Foundations identified (DEQ, neuromorphic papers)
- [✅] Methodological precedents (QAT, surrogate gradients)
- [✅] Application domains (MRI, mobile vision)
- [✅] Gaps documented (no DEQ+neuromorphic)

**Experimental Planning:** ✅ Complete
- [✅] Datasets: MNIST, CIFAR-10, fastMRI
- [✅] Baselines: GPU DEQ, neuromorphic feedforward
- [✅] Metrics: energy, accuracy, convergence
- [✅] Hardware: SpiNNaker2 PyNN, Lava-DL simulators

**Feasibility:** ✅ Complete
- [✅] Toolchain clear (PyTorch, ONNX, compiler)
- [✅] Hardware plan (simulators first)
- [✅] Risk mitigation (hybrid-precision, phased validation)
- [✅] Confidence: 0.82 (acknowledges engineering effort)

**Overall:** ✅ READY FOR PHASE 2B

---

## Open Questions for Phase 2B

**Must Address:**
1. **Q1:** Optimal convergence tolerance ε (ablation: 1e-1, 1e-2, 1e-3)
2. **Q2:** Best spike encoding (rate, temporal, burst coding)
3. **Q4:** Hybrid vs. full neuromorphic backward pass

**Should Address:**
4. **Q3:** Energy scaling with model size (depth, channels)
5. **Q5:** Compiler optimization level (naive vs. optimized)
6. **Q7:** Primary application (mobile vision vs. MRI)

**Nice to Have:**
7. **Q6:** Physical hardware access (vs. simulators)
8. **Q8:** Tighter Lyapunov convergence bounds (theory)

---

## Next Steps (Phase 2B → 2C → 3 → 4)

**Phase 2B (Verification Planning - Next):**
1. Decompose main hypothesis into sub-hypotheses (SH1-SH3)
2. Design experiments for each sub-hypothesis
3. Prioritize verification order (SH1 → SH2 → SH3)
4. Identify dependencies and risks

**Phase 2C (Experiment Design):**
1. Detailed experiment specifications for SH1-SH3
2. Dataset preparation, baseline implementations
3. Metrics instrumentation (energy profiling, convergence tracking)

**Phase 3 (Implementation Planning):**
1. PRD: DEQ-to-SNN compiler requirements
2. Architecture: QA-ID training framework, neuromorphic deployment pipeline
3. Epics/Stories: Break down into implementable tasks

**Phase 4 (Coding & Validation):**
1. Implement DEQ-to-SNN compiler (PyTorch → ONNX → PyNN)
2. QA-ID training framework (hybrid-precision, surrogate gradients)
3. Run experiments, validate predictions
4. Iterate based on results

---

**File Generated:** 2026-02-06
**Workflow:** Phase 2A-Extended (YOLO Mode - Automated)
**Status:** ✅ READY - Proceed to `/hypothesis-loop` or `/hypothesis-next`

---

*For full details, see: 02a_extended_hypothesis_full.md*
