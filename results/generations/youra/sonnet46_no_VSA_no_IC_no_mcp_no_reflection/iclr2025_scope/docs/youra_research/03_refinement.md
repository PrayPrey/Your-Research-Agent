# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-31
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap-2
- **Gap Title**: No PEFT Method Exploiting SSM State Structure (State-Aware PEFT)
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 7

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 7

**Convergence Reason**: All 6 convergence criteria met at Exchange 7: SPECIFIC (core claim stated), MECHANISM (decay adaptation explained), PREDICTIONS (3 quantitative predictions), NOVELTY (memory-horizon adaptation as new PEFT axis), FEASIBILITY (mechanistically sound), OBJECTIONS (all 3 concerns addressed)

### Key Insights
1. The SSM A matrix is a task-specific memory horizon parameter — its HiPPO initialization is general, not task-optimal. Task-specific fine-tuning should relax this prior.
2. A_log bias adaptation is stability-preserving by construction: A = -exp(A_log) is always negative regardless of bias magnitude.
3. dt_proj LoRA (indirect decay via Δ) and A_log bias (direct decay) are mathematically non-redundant: one adapts input-dependent timescale modulation, the other adapts the base forgetting rate.
4. The 4-condition ablation (A→B→C→D) is the minimal design to fully characterize state-aware PEFT.
5. LongBench (long-range tasks) is necessary alongside GLUE to validate the memory-horizon claim — short-sequence GLUE alone may not show the effect.

### Breakthrough Moments
- **Exchange 1**: Dr. Nova reframed from "can LoRA work on SSMs?" to "what does SSM-specific memory require?" — introduced the memory-horizon framing.
- **Exchange 4**: Prof. Pax confirmed non-redundancy of α and B/C via mathematical analysis of the SSM update equation.
- **Exchange 6**: Prof. Rex identified that GLUE alone is insufficient — LongBench required to validate the core mechanism claim.
- **Exchange 7**: All concerns resolved; 4-condition design finalized.

---

## Final Hypothesis

### Title
**State-Aware LoRA (SA-LoRA): Memory-Horizon Adaptation for Mamba SSMs**

**Hypothesis ID:** H-SA-LoRA-v1

### Core Claim
Under fine-tuning of Mamba SSMs (130m, 370m) on NLP tasks (GLUE + LongBench), if we adapt the recurrent state decay parameters (A_log bias for Mamba-1; scalar A multiplier for Mamba-2) in addition to standard LoRA on projection layers, then downstream task accuracy improves beyond projection-only LoRA (GLUE ≥1pp, LongBench ≥2pp), because A-adaptation modifies task-specific memory horizons that projection layers cannot replicate.

### Mechanism
1. **Projection LoRA** (in_proj, out_proj, x_proj): adapts what information enters and exits SSM state — modifies the effective B (input→state) and C (state→output) mappings.
2. **A_log bias** (δ ∈ ℝ^{d_model}): shifts the base decay rate per channel, allowing task-appropriate information retention timescales — longer for multi-hop QA, shorter for sentiment.
3. **Complementarity**: B/C adaptation (projection) and α adaptation (A_log) are non-redundant — y_t = C_t·h_t; h_t = α·h_{t-1} + B_t·x_t. Only A-adaptation changes α.

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| **P1** (primary) | SA-LoRA (condition D) improves GLUE average ≥1pp over projection-only LoRA (A) on Mamba-130m | Mean GLUE(D) > GLUE(A) by ≥1.0pp, p<0.05 | GLUE delta ≤0.5pp → H₀ supported |
| **P2** | Accuracy gain from A-adaptation larger on LongBench than SST-2 | LongBench delta(C vs. A) > SST-2 delta(C vs. A) by ≥1pp | Equal gain across sequence lengths → memory-horizon mechanism not task-length-sensitive |
| **P3** (diagnostic) | Learned A_log biases larger for MNLI than SST-2 | Mean |δ_MNLI| > mean |δ_SST-2| | All |δ| < 0.01 → null hypothesis holds; A prior already task-optimal |

---

## Novelty

**What's new:** First PEFT method to explicitly adapt SSM state decay parameters (A_log) as a distinct adaptation category. Prior work treats Mamba as "an architecture with linear layers" — SA-LoRA exploits the recurrent structure unique to SSMs.

**Key differentiation:**
- vs. projection-only LoRA: SA-LoRA additionally adapts the temporal dimension of memory (decay rate), not just spatial channel mappings
- vs. IA³: SA-LoRA targets state transition parameter (across time steps), not single-step activation scaling
- vs. AdaLoRA: AdaLoRA optimizes rank budget; SA-LoRA introduces an entirely new target category (state parameters)

**Extension principle:** Memory-aware PEFT generalizes to any model with learnable state decay — RWKV (WKV decay), RetNet (retention γ), future SSM variants.

---

## Experimental Design

**Models:** Mamba-130m, Mamba-370m (HuggingFace: state-spaces/mamba-{130m,370m}-hf)

**Datasets:**
- GLUE: SST-2, MNLI, QNLI, QQP (short-range classification, ~20-100 tokens)
- LongBench: 2WikiMultihopQA (long-range QA, ~5K tokens)

**4-Condition Ablation:**
| Condition | Parameters Adapted | Purpose |
|-----------|-------------------|---------|
| A | in_proj, out_proj, x_proj (LoRA r=8) | Naive projection-only baseline |
| B | + dt_proj (LoRA r=8) | Indirect decay adaptation via Δ |
| C | + A_log bias δ (no rank constraint) | Direct base decay adaptation |
| D | A + B + C combined | Full state-aware SA-LoRA |

**LoRA rank:** r ∈ {4, 8, 16}; primary comparison at r=8

**Training:** lr=3e-4, bs=32, epochs=3, warmup_ratio=0.1, seeds={42,43,44}

**Evaluation:** lm-evaluation-harness for GLUE; THUDM/LongBench scripts for 2WikiMultihopQA

---

## Limitations

- Results at 130m/370m may not fully generalize to >1B parameters
- A_log bias is simpler than LoRA (additive bias only, not rank decomposition) — stronger adaptation possible if A were nn.Linear
- Only Mamba-1 in primary scope; Mamba-2 scalar-A extension depends on checkpoint availability
- LongBench generation evaluation validity for Mamba needs verification before Phase 4

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met at Exchange 7 |
| **Clarity Verified** | Yes |
| **Hypothesis ID** | H-SA-LoRA-v1 |
| **Remaining Objections** | LongBench-Mamba compatibility (verify pre-Phase 4); dt_proj vs. A_log separation (resolved empirically in Phase 4) |

---

*Phase 2A complete. Outputs ready for Phase 2B.*
