# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-05-04
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0 (Fallback Mode — Claude writes all exchanges)
- **Gap ID**: gap-1
- **Gap Title**: Joint KV Cache Eviction and Fine-Tuning Co-Optimization
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 7

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 7

**Convergence Reason**: All 6 criteria met — SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS

### Key Insights
- The field has developed KV cache eviction (H2O, SnapKV) and PEFT fine-tuning (LoRA, AdaLoRA) entirely independently — no prior work trains adapters with simulated KV budget constraints
- The core mechanism is distribution-mismatch elimination: sequential-baseline adapters are trained on full KV cache but deployed under evicted-cache conditions; eviction-aware training closes this gap
- Per-category LongBench reporting (6 categories, 21 tasks) is essential — aggregate scores can mask task-specific regression that undermines practical value
- Prof. Pax confirmed H2O hard-mask eviction during LoRA forward pass is mathematically valid structured attention masking — no fundamental barriers

### Breakthrough Moments
- Prof. Vera (Exchange 2) separated eviction-robust adapters from rank-budget coupling — preventing confounded experiments and sharpening the core claim to a single testable mechanism
- Prof. Pax (Exchange 4) confirmed mechanistic soundness and identified the critical methodological constraint: eviction policy must be consistent between training simulation and inference evaluation
- Prof. Rex (Exchange 6) surfaced three unstated assumptions — model dependence, task distribution specificity, training data confound — all of which were addressable within the existing experimental design without new data

---

## Final Hypothesis

### Title
Eviction-Aware LoRA: Joint KV Cache Budget Simulation and Adapter Fine-Tuning for Long-Context LLMs

### Hypothesis ID
H-EvictionAwareLoRA-v1

### Core Claim
Under long-context LLM fine-tuning with fixed KV cache budget constraints, if LoRA adapters are trained with hard H2O-style KV eviction masks applied during the forward pass (simulating budget ratio r ∈ {25%, 50%, 75%}), then per-category LongBench accuracy will exceed the sequential baseline (standard LoRA fine-tuning followed by H2O eviction at inference only) by ≥2% at r=50% KV retention across ≥4/6 LongBench task categories on both LLaMA-2-7B and Mistral-7B-v0.1, because adapters trained under token-position scarcity learn more information-efficient attention representations that extract higher utility from surviving KV cache entries (token-scarcity regularization mechanism).

### Null Hypothesis
There is no statistically significant difference in per-category LongBench accuracy between eviction-aware LoRA fine-tuning and sequential baseline (standard LoRA + H2O eviction at inference) at matched KV cache budget ratio r.

### Mechanism
Token-scarcity regularization: H2O hard-mask eviction removes low-cumulative-attention token positions from KV cache during LoRA forward pass. Adapters exposed to systematic token absence learn attention patterns calibrated to surviving-token distributions. At inference under the same H2O eviction policy, eviction-aware adapters face no distribution mismatch, while sequential-baseline adapters — trained on full KV cache — face a novel token-absence distribution that degrades accuracy.

---

## Predictions

| ID | Statement | Success Criterion | Primary |
|----|-----------|-------------------|---------|
| P1 | Eviction-aware LoRA achieves ≥2% higher per-category LongBench accuracy than sequential baseline at r=50% in ≥4/6 categories on both LLaMA-2-7B and Mistral-7B-v0.1 | p<0.05, paired t-test with Bonferroni correction | ✅ Yes |
| P2 | Accuracy advantage increases monotonically as r decreases (tighter budget → larger benefit) | Spearman ρ < -0.8 across r ∈ {25%, 50%, 75%} | No |
| P3 | ≥1.8× inference throughput at r=50% vs. full-cache baseline on A100 GPU | Consistent across batch sizes 1 and 8 | No |

---

## Novelty

**Key Innovation:** First systematic study integrating KV cache eviction simulation into PEFT fine-tuning — training adapters to be eviction-robust rather than applying eviction post-hoc to eviction-unaware adapters.

**Differentiation from prior work:**
- vs. H2O (Zhang et al. 2023): H2O is post-hoc eviction on pre-trained/sequentially fine-tuned models; our method integrates eviction awareness into fine-tuning
- vs. SnapKV (Li et al. 2024): SnapKV optimizes eviction policy selection; our method optimizes the adapter to work with a fixed eviction policy
- vs. AdaLoRA (Zhang et al. 2023): AdaLoRA optimizes rank allocation for accuracy; our method adds eviction simulation as a training constraint
- vs. Dropout: Dropout operates on neurons within tokens; our method operates on entire token positions, changing sequence structure

---

## Experimental Design

**Base Models:** LLaMA-2-7B, Mistral-7B-v0.1 (both open-weight, HuggingFace Hub)

**Fine-tuning Data:** LongAlpaca-12k (Yukang/LongAlpaca) — identical for baseline and eviction-aware variants

**Evaluation:** LongBench (THUDM/LongBench) — 21 tasks, 6 categories, per-category reporting

**KV Budget Ratios:** r ∈ {25%, 50%, 75%}

**Eviction Policy:** H2O (fixed as both training simulation and inference policy)

**Baselines:**
1. Sequential: standard LoRA fine-tuning + H2O eviction at inference
2. Full-cache: standard LoRA fine-tuning + no eviction
3. Pre-trained model + H2O eviction (no fine-tuning)

**LoRA Hyperparameters:** rank=16, alpha=32, dropout=0.05 (identical for both variants)

**Statistics:** Paired t-test within each category; Bonferroni correction across 6 categories

**Optional sanity check:** Repeat with Alpaca-52k (short-context) to rule out training data distribution confound

---

## Limitations

- Results are specific to H2O eviction policy; generalization to SnapKV or StreamingLLM requires separate experiments
- LongAlpaca-12k training data may favor eviction-aware training if its distribution aligns with LongBench tasks — Alpaca-52k sanity check addresses this
- Throughput measurements are A100-specific; reported values may not generalize to other hardware
- Rank-budget coupling (AdaLoRA rank allocation guided by eviction scores) not tested in core hypothesis — follow-up direction
- Models tested in 7B class only; results may not generalize to larger models

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met after 7 exchanges |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Statistical significance reporting required; Alpaca-52k sanity check recommended |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
*Fallback Mode: External LLM (OpenRouter) unavailable — Claude wrote all exchanges*
