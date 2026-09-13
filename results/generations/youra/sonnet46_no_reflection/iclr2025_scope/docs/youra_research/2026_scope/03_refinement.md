# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-05-20
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0 (Free-Parse)
- **Gap ID**: gap_1
- **Gap Title**: Joint LoRA Adapter Training and KV Cache Eviction Policy Co-Optimization
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15
- **Convergence**: Exchange 15 — all 6 criteria met

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All 6 convergence criteria satisfied at Exchange 15: SPECIFIC (core claim with Under-If-Then-Because structure), MECHANISM (soft-to-hard differentiable training + representation compression effect), PREDICTIONS (4 quantitative predictions P1-P4), NOVELTY (4-dimensional differentiation from arXiv 2604.21335), FEASIBILITY (all components public, established soft-to-hard pattern, no fundamental barriers), OBJECTIONS (short-context GLUE concern, mechanism evidence, B3 strength — all addressed with concrete experiments).

### Key Insights

1. **Two-regime evaluation design**: Prof. Rex's challenge about GLUE being short-context forced the key experimental refinement — separate predictions for short-context GLUE (regularizer effect, ≥1%) and long-context LongBench-QA (eviction effect, ≥3%). Both are existing benchmarks.

2. **Representation compression effect**: Prof. Rex's question about why joint training beats the sequential baseline B3 surfaced the deepest mechanism claim — joint training allows LoRA adapter weights themselves to adapt to the KV budget constraint, concentrating discriminative information into eviction-surviving entries. This is not achievable by sequential training where LoRA is frozen during Locret training.

3. **Soft-to-hard training resolves gradient problem**: The established pattern in Locret and PruLong (soft scoring during training → hard eviction at inference) makes differentiable joint training technically feasible without novel infrastructure.

4. **QLoRA analogy provides strong prior**: Joint quantization+LoRA (QLoRA) consistently beats sequential approaches — the same principle is now being tested for KV eviction.

### Breakthrough Moments

- **Exchange 6** (Prof. Rex): Short-context GLUE concern → two-regime evaluation design with different predictions per regime
- **Exchange 7** (Dr. Nova): Two-regime structure recognized as itself novel
- **Exchange 12** (Prof. Rex): Representation compression identified as the mechanism distinguishing joint from sequential B3
- **Exchange 13** (Dr. Nova): Representation compression reframed as paradigm-level contribution — efficiency-awareness during adaptation changes what model learns

---

## Final Hypothesis

### Hypothesis ID
`H-JointLoRAKV-v1`

### Title
JointLoRA-KV: Task-Aware Joint Training of LoRA Adapters and KV Eviction Heads

### Core Claim (Under-If-Then-Because)

**Under** standard PEFT fine-tuning conditions on transformer-based LLMs with KV cache (LLaMA-3.1-8B), with a fixed 50% KV retention budget,

**if** LoRA adapter weights and KV eviction head weights (Locret retaining heads) are jointly trained end-to-end via a task classification loss using soft scoring during training and hard eviction at inference (JointLoRA-KV),

**then** JointLoRA-KV will achieve ≥3% higher accuracy than the sequential baseline (B3: LoRA → Locret sequential fine-tune) on LongBench-QA tasks and ≥1% higher on GLUE (MNLI, SST-2, QNLI) at the same 50% KV budget,

**because** task-specific gradient signals direct eviction toward discriminatively relevant tokens rather than merely high-attention-score tokens, and joint training allows LoRA adapters to learn representations that concentrate task-discriminative information into eviction-surviving KV entries ("representation compression effect").

### Null Hypothesis

There is no statistically significant difference in GLUE or LongBench-QA accuracy between JointLoRA-KV and B3 (sequential LoRA→Locret fine-tune) at matched 50% KV budget across 3 seeds on LLaMA-3.1-8B.

### Causal Mechanism (4-step chain)

1. **Attention-eviction misalignment**: LoRA-modified Q/K projections alter which KV tokens receive high attention scores, creating misalignment with heuristic/LM-trained eviction policies *(tested by P3 attribution analysis)*
2. **Task-gradient eviction alignment**: Task classification loss rewards retaining discriminatively relevant tokens (hypothesis markers in MNLI, sentiment anchors in SST-2) — different from next-token-predictive targets rewarded by LM loss
3. **Joint gradient flow**: LoRA A/B matrices and Locret retaining head weights participate in the same backward pass, sharing the task objective while using independent gradient paths (no interference)
4. **Representation compression**: Joint training causes LoRA adapters to concentrate discriminative information into eviction-surviving KV entries — impossible in sequential training where LoRA is frozen during Locret training *(tested by P4 probing)*

---

## Predictions

| ID | Type | Claim | Success Criterion | Falsification |
|----|------|-------|-------------------|---------------|
| **P1** | Primary benchmark | JointLoRA-KV ≥ B3 + 3% on LongBench-QA (NarrativeQA, Qasper, MultiFieldQA) at 50% KV budget | ≥3.0 pp difference, p<0.05, non-overlapping 95% CIs across 3 seeds | B3 matches or exceeds within CI |
| **P2** | Short-context + boundary | JointLoRA-KV ≥ B3 + 1% on GLUE at 50% budget; matches vanilla LoRA ±0.3% at 100% budget | ≥1.0 pp GLUE improvement AND ≤0.3 pp gap at full budget | Degradation at 100% budget OR no GLUE improvement |
| **P3** | Mechanism diagnostic | Spearman ρ < 0.7 between LoRA attention weights and Locret retaining scores on 100 MNLI examples | Mean ρ < 0.7 (systematic misalignment confirmed) | ρ ≥ 0.7 (no meaningful mismatch — revisit mechanism) |
| **P4** | Mechanism (representation compression) | Probing accuracy on TOP-50% retained KV entries ≥5% higher for JointLoRA-KV vs. B3 | ≥5.0 pp probing accuracy difference | <5 pp difference (no differential info concentration) |

---

## Novelty

### What is New
- First systematic NLP benchmark evaluation (GLUE + LongBench) of joint LoRA + KV eviction co-training
- First identification and empirical test of the "representation compression" effect
- Paradigm shift: efficiency-awareness during PEFT adaptation (not post-hoc) changes learned representations

### Differentiation from Prior Work

| Prior Work | Key Difference |
|------------|----------------|
| arXiv 2604.21335 (closest) | We use task loss (not LM loss); GLUE/LongBench (not perplexity/RULER); token-level Locret (not value-group routing); separate but jointly-optimized parameters |
| Locret [Huang et al., 2024] | Co-training vs. post-hoc application; task loss vs. distillation loss |
| LESS [Dong et al., 2024] | LESS uses low-rank recurrence, not LoRA adapters; no GLUE/LongBench evaluation |
| Amazon ICR [EACL 2026] | ICR tests robustness of fixed eviction to fine-tuning; does not jointly optimize eviction during training |
| QLoRA [Dettmers et al., 2023] | QLoRA is the analogical inspiration (joint compression+adaptation > sequential); we test the same principle for KV eviction |

---

## Experimental Design

### Base Setup
- **Model**: LLaMA-3.1-8B (meta-llama/Meta-Llama-3.1-8B, HuggingFace)
- **PEFT**: HuggingFace PEFT library, LoRA r=16, target Q/K/V
- **Eviction**: Locret retaining heads (github.com/huangyuxiang03/Locret), budget_ratio=0.5
- **Seeds**: 3 fixed seeds (42, 123, 456)

### Datasets (all existing, real)
- **Short-context**: GLUE — MNLI, SST-2, QNLI (HuggingFace datasets)
- **Long-context**: LongBench — NarrativeQA, Qasper, MultiFieldQA (public GitHub)
- **Diagnostic**: MNLI validation (100 examples, for P3)

### Baselines
- **B1**: LoRA + frozen Locret (no eviction training)
- **B2**: LoRA + kvpress (heuristic, no training)
- **B3**: LoRA → sequential Locret fine-tune (LoRA frozen — **hardest baseline**)
- **Vanilla LoRA**: no eviction module (100% KV budget boundary check)

### Execution Order
1. Run P3 attribution diagnostic first (cheap, pre-registration check)
2. If P3 passes (ρ < 0.7): proceed with full JointLoRA-KV + all baselines training
3. Evaluate P1 + P2 on GLUE + LongBench
4. Evaluate P4 probing on retained KV representations
5. Statistical testing: 95% CIs, t-tests, effect sizes

---

## Limitations

- **Short-context GLUE**: At ≤512 tokens, 50% KV budget retains 256 tokens — eviction events may be sparse, limiting P2 observable effect
- **Model scale**: Results are for LLaMA-3.1-8B; generalization to larger models (70B+) not tested
- **3% LongBench threshold**: Based on estimated performance gaps, not pre-computed power analysis; may need adjustment
- **Scope boundary**: Applies only to transformer LLMs with KV cache; excludes SSMs (Mamba, RWKV), linear attention models
- **B3 baseline strength**: Locret heads train in <1 GPU hour — sequential adaptation may be faster than expected, narrowing the joint training advantage

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Hypothesis ID** | H-JointLoRAKV-v1 |
| **Discussion Convergence** | All 6 criteria met at Exchange 15 |
| **Clarity Verified** | Yes |
| **Phase 2B Ready** | Yes |
| **Remaining Objections** | B3 strength, GLUE short-context effect size, P4 probing design — all mitigated |
| **Recommended First Step** | Run P3 attribution diagnostic before committing to full training |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
*Executed: 2026-05-20 | UNATTENDED mode | Gap: gap_1 (HIGH+PRIMARY)*
