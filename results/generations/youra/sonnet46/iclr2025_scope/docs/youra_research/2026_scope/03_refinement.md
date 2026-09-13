# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-05-08T06:10:00Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0 (Free-Parse)
- **Gap ID**: gap_1
- **Gap Title**: No Static Pre-Fine-Tuning Signal for Per-Layer LoRA Rank Allocation
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova (Creative Novelty Explorer), Prof. Vera (Rigorous Validation Architect), Dr. Sage (Research Impact Evaluator), Prof. Pax (Feasibility & Reality Checker), Dr. Ally (Hypothesis Strengthening Champion), Prof. Rex (Hypothesis Stress-Test Master)

**Total Exchanges**: 15

**Convergence Reason**: All 6 convergence criteria met — SPECIFIC core claim, MECHANISM causal chain, PREDICTIONS with measurable thresholds, NOVELTY vs. prior work, FEASIBILITY, OBJECTIONS addressed

### Key Insights
1. **Ranking-based framing (Kendall's tau >= 0.4) is more robust than exact correlation** — Dr. Nova's pivot in Exchange 9 significantly strengthened the hypothesis by reframing from "exact correlation" to "ordinal ranking proxy"
2. **"Sparsity as free AdaLoRA approximation" is the core novelty claim** — if Kendall's tau >= 0.4 between sparsity ranking and AdaLoRA's learned allocation, the hypothesis is directly validated against the state-of-the-art method
3. **Mechanistic validation via ΔW spectral decay** — post-training SVD of learned ΔW matrices provides a tractable mechanistic check that addresses the gradient norm confound
4. **Joint budget allocation is essential** — marginal rank sensitivity (one layer perturbed at a time) is insufficient; joint protocol (fixed total budget, redistribution when perturbing) is required

### Breakthrough Moments
- **Exchange 9**: Dr. Nova reframes from Pearson r to Kendall's tau — more robust and practically useful
- **Exchange 14-15**: Dr. Ally synthesizes "sparsity as free AdaLoRA approximation" framing — cleanest falsifiable novelty statement
- **Exchange 11**: Prof. Pax identifies ΔW spectral decay (torch.linalg.svd post-training) as cheap mechanistic validation

---

## Final Hypothesis

### Title
**SparsityLoRA: Activation Sparsity as a Pre-Training Structural Prior for LoRA Rank Allocation**

**Hypothesis ID**: H-SparsityLoRA-v1

### Core Claim
Under LLaMA-3-8B, if layer-wise MLP activation sparsity (fraction |a| < 0.01, measured via forward hooks on 512 Alpaca calibration samples BEFORE fine-tuning) is used to inversely allocate per-layer LoRA ranks under a fixed total parameter budget equal to 60% of uniform-r=16, then the sparsity-guided rank allocation achieves ≥95% of oracle joint allocation performance on both SST-2 and MNLI, **because** pre-training drives MLP layers toward low-dimensional activation attractors whose dimensionality is proxied by activation sparsity and determines the rank needed for quality fine-tuning.

### Mechanism
1. **Pre-training creates sparse activation attractors**: LLaMA-3-8B MLP layers develop highly sparse activation patterns during pre-training (Lazy Neuron Phenomenon). Layers vary significantly in sparsity (CV > 0.3 expected).
2. **Sparsity proxies effective intrinsic dimension**: Layers with high sparsity operate in compressed representational subspaces — low intrinsic dimension [Aghajanyan et al. 2021] → low LoRA rank needed to redirect effectively.
3. **Inverse-sparsity rank allocation approximates AdaLoRA**: Sparsity ranking (high sparsity = low rank) Kendall's tau ≥ 0.4 with AdaLoRA's training-time learned per-layer allocation — free approximation of expensive adaptive method.
4. **ΔW spectral validation**: High-sparsity layers learn naturally low-rank updates (top-4 SVs explain ≥80% Frobenius norm) — confirms the rank constraint is architecturally motivated, not artificially imposed.

---

## Predictions

### P1 — EXISTENCE (prerequisite)
**Statement**: Layer-wise sparsity CV > 0.3 across 32 MLP layers on Alpaca calibration set; stable across Alpaca vs. WikiText (Kendall's τ_calibration ≥ 0.6) and 128 vs. 512 token inputs.

**Test**: Forward hooks on MLP gate layers; measure |a| < 0.01 per layer across 512 samples; compute CV and Kendall's τ between datasets.

**Success**: CV > 0.3 AND τ_calibration ≥ 0.6 | **Failure**: CV ≤ 0.3 OR τ < 0.6

### P2 — MECHANISM (primary)
**Statement**: Pearson r ≤ -0.4 between sparsity and joint rank sensitivity on sensitive layers (≥0.5% accuracy drop); Kendall's τ ≥ 0.4 between sparsity ranking and AdaLoRA's learned allocation; sparsity explains ≥20% unique variance in ΔW spectral decay beyond gradient norm.

**Test**: Joint rank sensitivity protocol (fixed 60% budget, redistribute when perturbing one layer); AdaLoRA at matched budget; torch.linalg.svd on ΔW; multiple regression with gradient norm control.

**Success**: r ≤ -0.4 on SST-2 AND MNLI; τ ≥ 0.4 vs. AdaLoRA; ≥20% unique variance | **Failure**: r > -0.2 on either task, or τ < 0.2, or sparsity loses significance in regression

### P3 — EFFICIENCY (end-to-end)
**Statement**: SparsityLoRA achieves ≥95% of oracle performance at 60% parameter budget on SST-2 and MNLI; outperforms uniform and random baselines (p < 0.05 over 5 seeds).

**Test**: 5 allocation strategies under identical 60% budget (SparsityLoRA, uniform r=~10, random 10-seed average, AdaLoRA, full r=16 reference); oracle = best of 20 random allocations.

**Success**: ≥95% oracle on BOTH tasks; p < 0.05 vs. uniform and random | **Failure**: <95% oracle on either task, or fails to beat baselines

---

## Novelty

### What's New
All prior adaptive rank allocation methods (AdaLoRA, ARD-LoRA, DyLoRA, Sensitivity-LoRA, La-LoRA) require training-time signals. Act-LoRA uses forward-pass activations for binary layer selection only. **SparsityLoRA is the first to use static pre-training activation sparsity for continuous rank magnitude allocation before fine-tuning begins.**

### Key Differentiation
| Method | Signal Type | Requires Training? | What It Allocates |
|--------|-------------|-------------------|-------------------|
| AdaLoRA | SVD importance (gradients) | YES (full run) | Rank magnitude |
| DyLoRA | Rank range training | YES (full run) | Rank range |
| Act-LoRA | Activation L2-norm | NO | Binary: which layers |
| **SparsityLoRA** | **Activation sparsity** | **NO** | **Rank magnitude** |

### Research Direction Opened
"Structural priors for PEFT" — properties of pre-trained models that configure fine-tuning without gradient computation. Future work: cross-architecture (Mistral, Gemma), quantization-sparsity interaction, continual learning rank re-estimation.

---

## Experimental Design

### Model & Datasets
- **Model**: LLaMA-3-8B (meta-llama/Meta-Llama-3-8B)
- **Fine-tuning**: GLUE SST-2 (sentiment) and MNLI (NLI)
- **Calibration**: Alpaca 512 samples (primary) + WikiText 512 (stability)
- **Infrastructure**: HuggingFace PEFT `rank_pattern`, PyTorch `register_forward_hook`, `torch.linalg.svd`

### Baselines (all at 60% parameter budget)
1. Uniform LoRA r=16 (full budget — reference quality ceiling)
2. Uniform LoRA r=~10 (budget-matched — primary comparison)
3. Random allocation (10-seed average)
4. AdaLoRA (training-time adaptive — state-of-the-art comparison)
5. SparsityLoRA (our method)

### Key Protocol Details
- **Epsilon sensitivity sweep**: ε ∈ {0.001, 0.01, 0.05, 0.1} for SiLU soft-sparsity threshold
- **Joint rank sensitivity**: Fix total budget at 60%, redistribute when perturbing one layer's rank (not marginal)
- **Repetitions**: 5 seeds for all fine-tuning experiments
- **ΔW spectral analysis**: torch.linalg.svd on B×A per layer post-training with r=16

---

## Limitations

- **SiLU is soft-sparse**: Unlike ReLU, SiLU produces non-binary activations — threshold ε selection affects sparsity estimates (mitigated by sensitivity sweep)
- **Task-conditioned rank sensitivity**: Rank requirements may differ between SST-2 and MNLI — if results diverge, scope narrows to task-compatible with calibration distribution
- **LLaMA-3-8B only**: Cross-architecture generalization not tested (deferred to follow-up)
- **Marginal approximation**: Joint sensitivity protocol approximates true joint sensitivity under combinatorial rank optimization

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | Exchange 15 — all 6 criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Epsilon sensitivity (mitigated), task-conditioned rank variation (mitigated by 2-task test), 20% unique variance threshold (implementation risk only) |
| **Phase 2B Readiness** | READY |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
*Participants: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex*
*Gap: No Static Pre-Fine-Tuning Signal for Per-Layer LoRA Rank Allocation*
