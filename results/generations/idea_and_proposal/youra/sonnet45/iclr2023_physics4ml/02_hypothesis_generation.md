# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-06
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-PH-TRANS-01
**Confidence Level:** 0.85 (HIGH)

**Main Hypothesis:**

Port-Hamiltonian attention mechanisms in Transformer architectures enable stable, length-extrapolating sequence modeling by conserving an information-theoretic energy functional across layers, providing theoretical stability guarantees via passivity that standard self-attention lacks.

**Alternative Hypothesis (H0):**

Standard scaled dot-product attention provides equivalent or superior long-sequence modeling performance compared to Port-Hamiltonian attention, and the energy-conservation constraint reduces expressivity without compensatory stability benefits.

### 1.2 Variables

| Variable Type | Name | Definition | Measurement |
|---------------|------|------------|-------------|
| **Independent** | Attention Mechanism Type | PHT attention vs. Standard attention | Binary (PHT / Standard) |
| **Independent** | Sequence Length (train) | Context window during training | Integer (tokens) |
| **Independent** | Sequence Length (test) | Context window during inference | Integer (tokens) |
| **Dependent** | Perplexity | Model uncertainty on held-out data | Float (lower = better) |
| **Dependent** | Extrapolation Degradation | Perplexity increase ratio (test_len / train_len) | Float (closer to 1.0 = better) |
| **Dependent** | Gradient Stability | Max gradient norm during training | Float (lower = more stable) |
| **Control** | Model Size | d_model, n_layers, n_heads | Fixed across conditions |
| **Control** | Dataset | Training corpus | Long-Range Arena benchmark |
| **Control** | Optimizer | Adam with warmup schedule | Fixed hyperparameters |
| **Mediator** | Energy Conservation Error | ΔH = \|H_t - H_0\| across layers | Float (measures PH structure preservation) |
| **Mediator** | Dissipation Rate | Controlled energy decay via R matrix | Float (tunable hyperparameter) |

### 1.3 Causal Mechanism

**Causal Chain:**

1. **Port-Hamiltonian Structure** (architectural constraint)
   ↓
2. **Energy Functional H(Q,K) = ½(Q^T M K)** (defines system energy)
   ↓
3. **Passivity Property** (energy dissipation ≤ 0)
   ↓
4. **Bounded Gradient Flow** (∇H remains bounded)
   ↓
5. **Gradient Stability** (no explosion/vanishing)
   ↓
6. **Long-Sequence Extrapolation** (energy conservation maintains coherence beyond training length)

**Evidence for Causal Links:**

- **Link 1→2:** Port-Hamiltonian theory defines energy functionals for interconnected systems (Van Der Schaft 2000)
- **Link 2→3:** Passivity is proven property of PH systems with dissipation matrix R ≥ 0 (Khalil 2002)
- **Link 3→4:** Passivity theorem: ∇H · (J-R)∇H ≤ 0 → bounded dynamics
- **Link 4→5:** Bounded gradients prevent explosion (empirical validation needed)
- **Link 5→6:** Stable energy structure enables extrapolation (hypothesis to test)

**Key Tension:**

Energy conservation is a **constraint** that may reduce expressivity. Trade-off:
- **Benefit:** Stability + extrapolation
- **Cost:** Potential performance gap on tasks where unconstrained attention is optimal

**Resolution Strategy:** Tunable dissipation matrix R allows controlled energy decay, balancing conservation (R→0) vs. expressivity (R>0).

### 1.4 Key Assumptions

1. **Information-Theoretic Energy:** Attention scores represent information flow, interpretable as energy exchange (conceptual, not derived from first principles)
2. **Symplectic Discretization Fidelity:** Discrete-time symplectic Euler integrator preserves continuous-time Hamiltonian properties with acceptable error (<5% energy drift)
3. **Computational Feasibility:** ~15% FLOPs overhead is acceptable for production systems
4. **Task Structure:** Long-sequence tasks benefit from energy-conserving structure (not arbitrary constraint)
5. **Metric Tensor Learnability:** M can be learned via gradient descent without pathological local minima

### 1.5 Scope & Boundaries

**Included:**
- Long-sequence tasks (>512 tokens)
- Autoregressive language modeling
- Bidirectional encoding tasks
- Time-series prediction

**Excluded:**
- Very short sequences (<128 tokens) where stability is not bottleneck
- Tasks requiring highly non-conservative dynamics (e.g., adversarial robustness)
- Multi-modal architectures (vision-language) in initial validation

**Validity Range:**
- Sequence length: 512-4096 tokens (training: 512, testing: up to 4096)
- Model scale: 50M-500M parameters (standard research scale)
- Domains: NLP (Long-Range Arena), time-series forecasting

### 1.6 Testable Predictions

**Primary Prediction (P1):**

*PHT attention will exhibit ≤10% perplexity degradation when sequence length doubles from training (512→1024 tokens), compared to ≥25% degradation for standard Transformer attention on Long-Range Arena tasks.*

**Measurement:** Perplexity ratio = PPL(1024) / PPL(512)
- **PHT:** ≤1.10
- **Standard:** ≥1.25

**Secondary Predictions:**

**P2 - Gradient Stability:**
*PHT training will maintain max gradient norm <1.0 throughout training, while standard Transformer will exhibit gradient spikes >5.0 on long sequences (2048+ tokens).*

**P3 - Energy Conservation:**
*Energy error ΔH = |H_final - H_initial| across L layers will satisfy ΔH/H_initial <0.05 for PHT with low dissipation (R→0), demonstrating structure-preserving implementation.*

**Falsification Criteria:**

The hypothesis is **FALSIFIED** if:
1. **F1:** PHT perplexity on 1024-token sequences is >15% worse than standard Transformer (expressivity cost too high)
2. **F2:** PHT shows no gradient stability improvement (max gradient norm within 10% of standard)
3. **F3:** Energy conservation error ΔH/H_initial >0.20 (implementation fails to preserve structure)
4. **F4:** Computational overhead exceeds 30% FLOPs (impractical for deployment)

**Partial Success Conditions:**
- Stability improved (P2 holds) but extrapolation fails (P1 fails) → Refine energy functional design
- Extrapolation works but energy is not conserved (P3 fails) → Symplectic integrator issue

### 1.7 SOTA Baseline (SOTA Comparison Mode)

**Baseline 1: Standard Transformer (Vaswani et al. 2017)**
- **Metric:** Perplexity on Long-Range Arena
- **Expected Performance:** Strong on short sequences, degrades >25% on length extrapolation
- **Differentiation:** PHT adds energy-conservation constraint

**Baseline 2: ALiBi (Press et al. 2022)**
- **Metric:** Extrapolation ratio PPL(2048)/PPL(512)
- **Expected Performance:** ~15% degradation (positional encoding heuristic)
- **Differentiation:** PHT provides theoretical guarantees via passivity

**Baseline 3: Transformer-XL (Dai et al. 2019)**
- **Metric:** Long-context perplexity
- **Expected Performance:** Improved via recurrence mechanism
- **Differentiation:** PHT uses energy conservation (not recurrence)

### 1.8 Statistical Verification Design

**Experimental Design:** Controlled comparison with ablation study

**Conditions:**
1. **PHT (R=0):** Pure Port-Hamiltonian, no dissipation
2. **PHT (R=σI):** Tunable dissipation (σ ∈ {0.01, 0.05, 0.1})
3. **Standard Transformer:** Baseline (Vaswani et al. 2017)
4. **ALiBi Transformer:** Length extrapolation baseline (Press et al. 2022)

**Datasets:**
- **Primary:** Long-Range Arena (ListOps, Text, Retrieval, PathFinder, PathX)
- **Secondary:** WikiText-103 (long-context language modeling)
- **Tertiary:** M4 Competition time-series (temporal dynamics)

**Sample Size:**
- 5 random seeds per condition
- Train on 512-token sequences
- Test on {512, 1024, 2048, 4096} tokens

**Metrics:**
1. **Perplexity** (primary outcome)
2. **Extrapolation ratio** = PPL(2048) / PPL(512)
3. **Max gradient norm** (stability)
4. **Energy conservation error** ΔH/H_initial
5. **Training time** (FLOPs overhead)

**Statistical Tests:**
- **Hypothesis P1:** Paired t-test on perplexity ratios (PHT vs. Standard), α=0.05
- **Hypothesis P2:** Mann-Whitney U test on max gradient norms (non-parametric, outlier-robust)
- **Hypothesis P3:** Descriptive statistics on energy error (theoretical property, not comparison)

**Power Analysis:**
- Effect size: Cohen's d ≥0.8 (large effect) for perplexity improvement
- Power: 0.80 at α=0.05
- Required n: 5 seeds × 5 tasks = 25 measurements per condition (sufficient for paired tests)

---

## 2. Contribution Summary

**Theoretical Contributions:**
1. **First formalization of Transformer attention as Port-Hamiltonian dynamical system** with interconnection/dissipation structure
2. **Passivity-based stability theorem:** Proof that PH structure ensures bounded gradients during training (∇H remains in compact set)
3. **Energy conservation theorem for multi-head attention:** Parallel port structure preserves total energy H_total = Σ_h H_h

**Methodological Contributions:**
1. **Symplectic attention layer:** PyTorch implementation using structure-preserving discrete-time integrator
2. **Energy regularization training:** Loss function L = L_task + λ·ΔH encouraging energy conservation
3. **Principled initialization strategy:** M = I + ε·W_M (small perturbation from identity for backward compatibility)

**Practical Contributions:**
1. **Long-sequence extrapolation:** Enables training on 512 tokens, inference on 2048+ tokens with <10% degradation
2. **Gradient stability:** Addresses Transformer training instability on long sequences
3. **Energy-based interpretability:** Attention visualized as information flow with conserved quantities

---

## 3. Key Related Work

| Work | Relation | Differentiation |
|------|----------|-----------------|
| Greydanus et al. (2019) - Hamiltonian Neural Networks | **Foundation** | PHT applies PH to Transformers (not ODEs); discrete-time (not continuous) |
| Roth et al. (2025) - Stable Port-Hamiltonian NNs | **Build upon** | PHT adds attention mechanism + multi-head port structure; focuses on sequences (not SO(3) equivariance) |
| An et al. (2023) - Quantum Hamiltonian Transformers | **Compare against** | PHT targets classical ML (not quantum systems); PH structure (not basic Hamiltonian) |
| Press et al. (2022) - ALiBi | **Baseline** | PHT provides theoretical guarantees via energy conservation; ALiBi is positional encoding heuristic |
| Vaswani et al. (2017) - Standard Transformer | **Baseline** | PHT adds energy-conservation constraint with stability benefits |
| Moradi et al. (2025) - PH-NNs with Noise Models | **Related** | PHT applies PH to attention (not output-error models); sequence tasks (not control systems) |
| Aboussalah & Ed-dib (2025) - GeoHNNs | **Related** | PHT focuses on Transformers (not geometric deformable objects); information flow (not Riemannian geometry) |

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
*Port-Hamiltonian attention structure can be implemented in Transformers via symplectic discretization of energy functional H(Q,K) = ½(Q^T M K) with energy conservation error <5%.*

**Verification:** Implement PHT layer in PyTorch, measure ΔH/H_initial on forward passes across 12-layer network.

**SH2 (Mechanism):**
*Passivity property (∇H · (J-R)∇H ≤ 0) ensures bounded gradients during training, preventing gradient explosion on sequences >512 tokens.*

**Verification:** Compare max gradient norms between PHT and standard Transformer during training on 2048-token sequences.

**SH3 (Comparison):**
*PHT attention achieves perplexity ≤1.10× baseline when extrapolating from 512→1024 tokens, outperforming standard Transformer (≥1.25×) and matching ALiBi (~1.15×).*

**Verification:** Benchmark on Long-Range Arena with statistical significance testing (paired t-test, α=0.05).

### Readiness Checklist

- [x] **Hypothesis is testable:** Clear predictions (P1, P2, P3) with falsification criteria
- [x] **Variables are operationalized:** All variables have concrete measurements
- [x] **Causal mechanism is explicit:** 6-step chain from PH structure to extrapolation
- [x] **Baselines are identified:** Standard Transformer, ALiBi, Transformer-XL
- [x] **Datasets are specified:** Long-Range Arena (primary), WikiText-103, M4 time-series
- [x] **Statistical plan is complete:** Sample size (n=5 seeds), tests (t-test, Mann-Whitney U), power analysis
- [x] **Implementation is feasible:** PyTorch, symplectic integrator, ~15% FLOPs overhead
- [x] **Scope is narrow:** Long-sequence tasks (512-4096 tokens), NLP + time-series
- [x] **Success/failure criteria are clear:** 4 falsification conditions (F1-F4)

### Open Questions

1. **Metric Tensor Design:** Low-rank (rank-64) vs. Full-rank vs. Diagonal M?
   - **Resolution Path:** Phase 2C ablation study comparing all three variants

2. **Dissipation Tuning:** How to choose σ for R = σ·I?
   - **Resolution Path:** Grid search σ ∈ {0.01, 0.05, 0.1} in Phase 4 experiments

3. **Information-Theoretic Interpretation:** Can attention energy be rigorously connected to mutual information?
   - **Resolution Path:** Theoretical analysis in Phase 5 (paper writing), not blocking for Phase 2B-4

4. **Universality:** Can PHT approximate any attention function?
   - **Resolution Path:** Theoretical investigation (future work), not blocking for empirical validation

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-06*
