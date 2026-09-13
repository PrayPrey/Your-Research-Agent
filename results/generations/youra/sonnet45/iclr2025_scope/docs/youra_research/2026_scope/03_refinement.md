# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-03-18T01:22:50Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: Gap 1
- **Gap Title**: Unified Conversion Framework for Quadratic-to-Sub-Quadratic Model Transformation
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All 6 convergence criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights
- Selective SSM input-conditioning (Δ mechanism from Mamba) is critical - non-selective LTI control will fail this test
- Operator entropy decrease with depth is necessary condition for bounded-state conversion feasibility
- Jacobian eigenvalue alignment distinguishes true operator equivalence from mere output emulation
- Hybrid SSM+SWA pattern (from Samba) is architecturally proven, question is post-hoc applicability
- Failure scenarios are scientifically valuable - they characterize fundamental conversion limits

### Breakthrough Moments
- **Exchange 7**: Dr. Ally synthesized complete four-phase experimental protocol with clear go/no-go falsification gates
- **Exchange 10**: Prof. Vera elevated validation from output matching to operator-level equivalence via Wasserstein-2 Jacobian criterion
- **Exchange 12**: Prof. Rex demanded monotonic entropy decrease with depth as falsifiable structural prediction
- **Exchange 14**: Prof. Vera added LTI SSM control to isolate selectivity mechanism necessity (per Mamba ablations)

---

## Final Hypothesis

### Title
Post-Hoc Hybrid SSM-Attention Conversion for Pre-Trained Transformers

### Hypothesis ID
H-SSMConv-v1

### Core Claim
Under LLaMA-7B/13B inference on long-context benchmarks (8K-128K tokens), if deeper Transformer layers (L ≥ 20 in 32-layer models) are converted to hybrid selective SSM–SWA blocks via adapter-based knowledge distillation on ≤5% original pretraining tokens, then the converted model achieves ≥2.5× wall-clock throughput at 128K context with <5% perplexity degradation, because deep layers exhibit operator-level low-rank structure (effective rank r_eff < 256, state size N ≤ 1024) with input-conditioned dynamics compressible into selective SSM recurrence while local dependencies are preserved via SWA windows.

### Mechanism

The conversion operates via four causal steps:

1. **Deep Layer Compression Structure**: Deep Transformer layers (L≥20) exhibit low effective attention rank (r_eff < 256) due to semantic compression in late layers, with monotonically decreasing operator entropy across depth (validated via SVD analysis and statistical testing: β < 0, p < 0.01).

2. **Selective SSM Adapter Distillation**: Adapter matrices W_adapt distill frozen Q/K/V weights into selective SSM parameters A(x), B(x), C(x), Δ(x) = Softplus(W_Δ[Q,K,V]), preserving operator-level equivalence validated by Jacobian eigenvalue alignment (Wasserstein-2 distance < 0.05 between attention and SSM eigenvalue distributions).

3. **Lightweight Calibration**: Calibration on ≤5% original pretraining tokens (160B for LLaMA-7B's 3.2T pretraining) suffices because deep layers encode compressed semantic representations not raw positional patterns. Rapid saturation validated by pre-registered slope criterion: perplexity improvement 1B→10B tokens < 20% of 10M→1B gain.

4. **Hybrid Linear-Time Architecture**: SSM component provides O(L) complexity for global dependencies, SWA component (window=2048) preserves local token-level precision for sharp alignments (induction heads, copying), achieving ≥2.5× end-to-end throughput with adapter overhead <20% FLOPs.

### Causal Chain Diagram
```
Deep Layers (L≥20)                  Selective SSM Adapters
[Low r_eff, Decreasing Entropy] → [W_adapt: Q/K/V → A/B/C/Δ]
                                    [Jacobian Alignment]
         ↓                                   ↓
Lightweight Calibration              Hybrid SSM-SWA Blocks
[≤5% Tokens, Rapid Saturation] →   [O(L) Global + SWA Local]
         ↓                                   ↓
                    ≥2.5× Throughput, <5% Degradation
```

---

## Predictions

### P1 (Primary): Throughput Gain
**Statement**: Converted model achieves ≥2.5× wall-clock throughput at 128K context compared to vanilla LLaMA-7B on A100 GPU

**Test Method**: End-to-end latency measurement across sequence lengths {8K, 16K, 32K, 64K, 128K}, fit linear model T(L), require R²>0.98

**Success Criterion**: Speedup ≥2.5× at L=128K AND linear scaling confirmed (R²>0.98)

**Falsification**: If speedup <2× OR latency shows quadratic curvature (R²<0.98), efficiency claim fails

### P2: Perplexity Preservation
**Statement**: <5% perplexity degradation on The Pile compared to vanilla Transformer

**Test Method**: Evaluate on held-out 10M token subset of The Pile

**Success Criterion**: Relative degradation <5%

**Falsification**: If degradation >10%, conversion harms language modeling quality unacceptably

### P3: Phase 0 Operator Equivalence
**Statement**: Single-layer distillation achieves exponential error decay in SSM state size N with Jacobian alignment and cross-domain stability

**Test Method**: Train SSM on LLaMA-7B L28, sweep N∈{64,128,256,512,1024}, measure (1) MSE decay, (2) Wasserstein-2 Jacobian eigenvalue distance, (3) error delta on The Pile vs LongBench

**Success Criterion**: Exponential MSE decay, W2<0.05 at N=512, cross-domain error increase <3%, selective SSM outperforms LTI control by >2×

**Falsification**: Any metric fails → proceed to Phase 1 with caution; if LTI performs similarly to selective, selectivity assumption fails

### P4: Depth-Dependent Compression
**Statement**: Deep layers (L≥20) exhibit monotonically decreasing operator entropy with depth (statistical significance p<0.01)

**Test Method**: Compute operator entropy (log-det covariance of principal vectors) for each layer, fit linear regression entropy vs depth, test H1: β<0

**Success Criterion**: β<0, p<0.01 across 3 random seeds, entropy stable or decreasing across 8K→128K context

**Falsification**: If entropy increases with depth OR grows with context length in deep layers, bounded-N assumption collapses

### P5: Calibration Efficiency
**Statement**: Calibration saturates rapidly - perplexity improvement 1B→10B tokens <20% of 10M→1B gain

**Test Method**: Train adapters on schedule {10M, 100M, 1B, 10B tokens}, measure perplexity at each checkpoint

**Success Criterion**: Improvement slope threshold met

**Falsification**: If improvement continues logarithmically without plateau, effectively retraining (conversion impractical)

---

## Novelty

### What's New
Post-hoc architectural transformation of pre-trained Transformers to hybrid SSM-SWA via adapter-based knowledge distillation - addresses the "trillion-dollar fleet" of existing checkpoints without full retraining.

### Key Innovation
Operator-level equivalence validation via Jacobian eigenvalue alignment (Wasserstein-2 distance) rather than just output matching - provides principled theoretical grounding for conversion.

### Differentiation from Prior Work

**vs. Mamba (Gu & Dao 2023)**
- Mamba: Trains selective SSMs from scratch (3.2T tokens)
- This work: Converts existing pre-trained models, tests knowledge transfer not fresh training

**vs. Samba (Ren et al. 2024)**
- Samba: Native hybrid architecture co-trained end-to-end (100% pretraining)
- This work: Post-hoc hybrid blocks via lightweight calibration (≤5% tokens), enables rapid deployment upgrades

**vs. Quantization/Pruning**
- Quantization: Parameter-level compression (precision reduction)
- This work: Architectural paradigm shift (attention→SSM), fundamentally different compression approach

---

## Experimental Design

### Four-Phase Protocol with Falsification Gates

**Phase 0: Single-Layer Distillation Pilot** (Falsification Gate)
- Layer: LLaMA-7B L28 (deepest layer)
- Sweep: SSM state size N ∈ {64, 128, 256, 512, 1024}
- Controls: Selective SSM vs LTI SSM (isolates selectivity necessity)
- Metrics:
  - Exponential MSE decay: MSE(N) ∝ exp(-N/r_eff)
  - Jacobian alignment: Wasserstein-2 eigenvalue distance < 0.05
  - Cross-domain: The Pile (in-domain) vs LongBench (out-of-domain), error delta <3%
  - Selectivity: E_sel(N=512) / E_LTI(N=512) < 0.5 (selective >2× better)
- **Go criterion**: All four metrics pass
- **No-go criterion**: Any metric fails → report "operator-level incompatibility," pivot hypothesis

**Phase 1: Full-Model Rank & Stability Diagnostic**
- Effective rank (95% Frobenius norm) per layer at {8K, 32K, 64K}
- Operator entropy vs depth (linear regression β<0, p<0.01 across 3 seeds)
- Grassmannian distance E[d(S_k(x),S_k(x'))] - must decrease with depth
- **Pass criterion**: r_eff(L≥20) < 256, entropy monotonic decrease, Grassmannian decreasing
- **Fail criterion**: Entropy increases in deep layers → reject bounded-N assumption

**Phase 2: Multi-Layer Hybrid Conversion**
- Convert layers 20-32 to hybrid SSM-SWA
- Calibration schedule: 10M → 100M → 1B → 10B tokens on The Pile
- Monitoring:
  - Layerwise KL divergence (attention vs SSM outputs)
  - Spectral radius ρ(A_t) enforced <0.95 via A_t = -exp(Ã_t)
  - State norm growth over 128K (variance ratio ≤1.2× baseline)
  - Calibration slope (P5 prediction)
- **Success**: Calibration plateaus early, state growth bounded

**Phase 3: Stress-Test Suite** (Adversarial Validation)
- Needle-in-haystack at 64K/128K (≥95% baseline accuracy)
- Induction head synthetic task
- Passkey retrieval (Samba protocol)
- SWA window sensitivity: 512→4096, performance variance <10%
- FLOP decomposition: adapter overhead <20% of total
- **Success**: All adversarial tests pass, window robustness confirmed

**Phase 4: End-to-End Throughput Benchmark**
- Wall-clock latency at {8K, 16K, 32K, 64K, 128K} on A100
- Linear scaling validation: T(L) fit R² > 0.98
- Peak memory: O(L) not O(L²)
- Comparison: vanilla LLaMA, converted hybrid, native Samba
- **Success**: ≥2.5× speedup vs vanilla, <1.5× degradation vs native Samba

### Datasets & Baselines

**Datasets**
- The Pile (calibration continuity with LLaMA pretraining)
- LongBench (long-context evaluation, 16 tasks, 3750 samples)
- Synthetic adversarial tasks

**Models**
- Base: LLaMA-7B, LLaMA-13B (32-layer architectures)

**Baselines**
- Vanilla LLaMA-7B (standard quadratic attention)
- Samba-3.8B (reference native hybrid, upper bound)
- LTI SSM (non-selective control, isolates selectivity)

---

## Limitations

### Known Constraints
- Tested only on LLaMA-7B/13B - scaling to 70B+ requires validation
- Single-GPU inference focus - distributed inference may have different bottlenecks
- English language benchmarks - multilingual generalization unknown
- Adapter overhead may scale unfavorably with hidden dimension in larger models

### Scope Boundaries

**Applies To**:
- Pre-trained decoder-only Transformers (LLaMA, Mistral, similar)
- Models with ≥32 layers enabling deep-layer subset selection
- Long-context scenarios (8K-128K) where quadratic cost is prohibitive
- Deployment prioritizing efficiency over absolute performance (<5% degradation acceptable)

**Does Not Apply To**:
- Encoder-only or encoder-decoder (BERT, T5) - different attention patterns
- Small models (<1B parameters) - overhead outweighs gains
- Short-context tasks (<4K) - quadratic attention already efficient
- Safety-critical applications requiring zero degradation

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met after 15 exchanges |
| **Clarity Verified** | Yes |
| **Remaining Objections** | 3 (long-horizon stability, adapter scaling, SWA optimization) |

### Remaining Concerns (Prof. Rex)
1. **Long-Horizon Stability**: Jacobian alignment is local (per layer) - cumulative error over 128K tokens may diverge. **Mitigation**: Track cumulative state divergence (h_t norm difference) over full context.
2. **Adapter Scaling**: Overhead may grow with model size (70B hidden dims). **Mitigation**: Test at 7B/13B/30B, pre-register adapter parameter budget <5% base model.
3. **SWA Window Optimization**: Window=2048 from Samba may not be optimal post-conversion. **Mitigation**: Phase 3 sensitivity test addresses evaluation-time, add training-time adaptation if needed.

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
