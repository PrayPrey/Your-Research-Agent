# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-DT-CaPEFT-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under conditions of variable-length input sequences in continual learning scenarios, if context complexity (measured by attention entropy) is used to dynamically route between low-rank (r=4) and high-rank (r=32) adapters with EMA-based consolidation, then continual learning performance will be maintained while reducing parameter usage by 40-60% on simple contexts, because dual-timescale memory consolidation (analogous to hippocampus-neocortex systems) enables efficient knowledge encoding proportional to input complexity.

**Alternative Hypothesis (H0):**
There is no significant relationship between context complexity and optimal adapter rank; fixed-rank adapters perform equivalently to complexity-aware dynamic routing in continual learning settings, and EMA consolidation provides no benefit over independent adapter training.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Context complexity (α) | Independent | Attention entropy from cached attention weights: `entropy = -Σ p_i log(p_i)` averaged across heads | Low: 0-2.0, Medium: 2.0-4.0, High: >4.0 |
| Adapter ranks (r_fast, r_slow) | Independent | Fast adapter r=4, Slow adapter r=32, soft-gated mixing | r ∈ {4, 8, 16, 32} |
| EMA decay rate (β) | Independent | Consolidation rate: `Fast ← β*Fast + (1-β)*project(Slow)` | β ∈ {0.99, 0.999, 0.9999} |
| Gate temperature (τ) | Independent | Softness of routing: `α = sigmoid(W_gate · complexity / τ)` | τ ∈ {0.1, 0.5, 1.0} |
| Task accuracy | Dependent | Accuracy on downstream tasks (SCROLLS, LongBench, Split-CIFAR) | 0-100% |
| Forgetting rate | Dependent | Backward transfer: accuracy drop on previous tasks after learning new tasks | Lower is better |
| Parameter efficiency | Dependent | Active parameters per inference / total adapter parameters | 40-100% |
| Inference latency | Dependent | Time per forward pass including routing overhead | ms/token |
| Base model | Controlled | Llama-3.1-8B with frozen backbone parameters | Fixed |
| Training data | Controlled | Standard continual learning benchmarks | Fixed per experiment |
| Optimizer | Controlled | AdamW with lr=1e-4, weight_decay=0.01 | Fixed |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: Complexity Estimation
   Input → Attention Entropy Computation → Complexity Score (α)

Step 2: Soft-Gated Routing
   Complexity Score → Gate Activation → Adapter Weight Mixing
   α_gate = sigmoid(W_gate · complexity)
   h_out = h_base + α_gate * Slow(h) + (1-α_gate) * Fast(h)

Step 3: EMA Consolidation
   Slow Adapter → Projection → Fast Adapter Update
   Fast_params ← 0.999 * Fast_params + 0.001 * project(Slow_params)

Outcome: Maintained accuracy + 40-60% parameter reduction on simple contexts
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Entropy-Lens (Ali et al., 2025) | Attention entropy reveals decision strategies and computational requirements | Strong |
| Step1 → Step2 | ACL 2025 Attention Entropy paper | High attention entropy indicates complex parallel encoding needs | Strong |
| Step2 → Step3 | FSC-Net (El Gorrim, 2025) | Dual-timescale consolidation achieves +4.27pp retention gain | Strong |
| Step2 → Step3 | PEARL (Bhat et al., 2025) | Dynamic rank allocation based on task proximity improves CL | Medium |
| Step3 → Outcome | Brain-inspired replay (van de Ven, 2020) | Consolidation mechanism validated in continual learning | Strong |
| Step3 → Outcome | C-LoRA (Zhang et al., 2025) | Orthogonality constraints prevent interference | Medium |

**Key Tension:**
- **Tension:** FSC-Net shows pure replay outperforms distillation (+1.2pp), suggesting knowledge transfer from fast→slow may introduce recency bias. However, our hypothesis proposes slow→fast consolidation (opposite direction).
- **Resolution:** DT-CaPEFT consolidates FROM high-capacity (slow) TO efficient (fast), which aligns with neocortical consolidation of hippocampal memories. Phase 2B will test if direction matters by including bidirectional ablation.

### 1.4 Key Assumptions

| # | Assumption | Supporting Evidence | Consequence if Violated |
|---|------------|---------------------|------------------------|
| A1 | Attention entropy correlates with input complexity and required adapter capacity | ChunkKV semantic density correlation; Entropy-Lens computational strategy detection | Routing decisions will be arbitrary, negating efficiency gains |
| A2 | Soft gating provides smooth gradient flow for end-to-end learning | MoE literature (PEER, SliceMoE); differentiable routing | Training instability; need discrete routing with straight-through estimator |
| A3 | EMA consolidation transfers useful knowledge without causing interference | FSC-Net +4.27pp retention; brain-inspired replay mechanisms | Consolidation becomes harmful; need alternative transfer method |
| A4 | Orthogonality constraint encourages complementary rather than redundant learning | C-LoRA empirical results | Adapters learn redundant features; capacity wasted |
| A5 | ~5% computational overhead is acceptable for 40-60% parameter savings | TailorKV hybrid optimization acceptance | Need more aggressive optimization or different complexity estimator |

### 1.5 Scope & Boundaries

**Applies to:**
- Transformer-based language models (decoder-only, encoder-decoder)
- Vision transformers with attention mechanisms
- Multimodal models with cross-attention
- Continual learning scenarios with sequential task arrival
- Variable-length input sequences (short to long context)

**Does NOT apply to:**
- Non-attention architectures (pure CNNs, RNNs without attention)
- State-space models (Mamba, RWKV) without attention entropy
- Single-task fine-tuning (no continual learning benefit)
- Extremely resource-constrained devices where 5% overhead is prohibitive

**Known Limitations:**
- Requires attention mechanism for complexity estimation
- EMA consolidation adds memory for dual adapters during training
- Optimal hyperparameters (β, τ, r_fast, r_slow) may be task-dependent
- Does not address cross-task interference beyond orthogonality constraint

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Parameter Efficiency on Low-Complexity Inputs):**
When context complexity is below threshold (entropy < 2.0), the fast adapter alone achieves ≥95% of full performance while using only 12.5% of adapter parameters (r=4 vs r=32).

*Measurement:*
- Compare accuracy: Fast-only vs Full DT-CaPEFT on low-complexity subset
- Parameter ratio: 4/32 = 12.5% (8x reduction)
- Statistical test: Paired t-test, n ≥ 20 runs, p < 0.05

*Basis:*
- ChunkKV shows semantic density varies significantly across inputs
- Simple patterns require less representational capacity

*Success Criteria for Phase 2B:*
- Primary: Accuracy drop ≤ 5% with 8x parameter reduction
- Falsification: Accuracy drop > 15% indicates complexity-capacity assumption violated

**Secondary Predictions:**

**P2 (Slow Adapter Necessity for High-Complexity):**
When context complexity is above threshold (entropy > 4.0), engaging the slow adapter (r=32) improves accuracy by ≥5% compared to fast-only (r=4).

**P3 (Consolidation Benefit for Generalization):**
Enabling EMA consolidation improves generalization on held-out tasks by ≥3% compared to independent adapter training (no consolidation).

**P4 (Soft Gating Stability):**
Soft gating reduces training variance by ≥20% compared to hard switching between adapters.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any of the following occur:

1. **Primary Failure:** Fast adapter on low-complexity inputs achieves < 80% of full performance (> 20% accuracy drop)
2. **Mechanism Failure:** Attention entropy does NOT correlate with task difficulty (Spearman ρ < 0.3)
3. **Consolidation Failure:** EMA consolidation decreases performance compared to no consolidation
4. **Efficiency Failure:** Computational overhead exceeds 15% (negating efficiency gains)

### 1.7 SOTA Baseline (Not Applicable)

*This hypothesis targets a novel mechanism (context-complexity-aware PEFT) rather than direct SOTA comparison. Baselines are methodological (PEARL, C-LoRA, CL-LoRA) rather than performance benchmarks.*

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (Cohen's d): 0.8 (large, based on FSC-Net +4.27pp / ~1.27% std)
- Required runs: n ≥ 20 per condition
- Statistical power: 0.8
- Significance level: α = 0.05

**Test Specifications:**
| Prediction | Test Type | Conditions | Metric |
|------------|-----------|------------|--------|
| P1 | Paired t-test | Low-complexity subset | Accuracy, Parameters |
| P2 | Independent t-test | High-complexity subset | Accuracy |
| P3 | Paired t-test | With/without consolidation | Held-out accuracy |
| P4 | F-test | Soft vs hard gating | Variance |

**Report Format:**
- Mean ± Std Dev
- 95% Confidence Interval
- Cohen's d effect size
- p-value (two-tailed unless specified)

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does context-complexity-aware adapter routing provide parameter efficiency benefits in continual learning?"
- Maps to: P1 (Primary prediction)
- Verification type: Empirical
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the proposed dual-timescale mechanism (complexity estimation → soft-gated routing → EMA consolidation) the actual cause of improved efficiency-performance tradeoff?"
- Maps to: Causal mechanism (N=3 steps)
- Will decompose into 3 sub-hypotheses:
  - H-M1: Attention entropy correlates with required adapter capacity
  - H-M2: Soft-gated routing improves over static allocation
  - H-M3: EMA consolidation improves over independent training
- Verification type: Ablation studies
- Critical: Determines explanatory power

**SH3 (Comparison):**
"Does DT-CaPEFT outperform existing PEFT methods (PEARL, C-LoRA, CL-LoRA) on continual learning benchmarks?"
- Maps to: Secondary predictions (P2, P3)
- Verification type: Comparative empirical
- Critical: Determines practical value

**Total Sub-Hypotheses in Phase 2B:** 2 + 3 = 5
(SH1: 1, SH2: 3 mechanism sub-hypotheses, SH3: 1)

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-DT-CaPEFT-v1
- [x] Confidence level specified: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=3 steps, evidence table complete)
- [x] Causal chain length (N=3) determined and documented
- [x] Key tension identified (consolidation direction) and resolution proposed
- [x] Key assumptions list consequences if violated (5 assumptions)
- [x] At least 2 testable predictions exist with primary marked (4 predictions)
- [x] Falsification criteria are defined (4 criteria)
- [x] Baselines are identified for comparison (PEARL, C-LoRA, CL-LoRA)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Resource Requirements:**
   - Compute: How many GPU hours needed for full ablation study?
   - Memory: Can dual adapters fit on single GPU with 8B model?
   - Estimated: 2-4 A100 GPUs, 1-2 weeks for full evaluation

2. **Data Availability:**
   - SCROLLS, LongBench: Publicly available
   - Split-CIFAR: Standard benchmark
   - Custom complexity-stratified splits: Need to create based on attention entropy

3. **Priority Verification Order:**
   - SH1 first (existence) → If fails, hypothesis rejected
   - SH2.H-M1 second (entropy-capacity correlation) → Core mechanism
   - SH2.H-M2 third (routing benefit) → Design validation
   - SH2.H-M3 fourth (consolidation benefit) → Full mechanism
   - SH3 last (comparison) → Practical value

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
