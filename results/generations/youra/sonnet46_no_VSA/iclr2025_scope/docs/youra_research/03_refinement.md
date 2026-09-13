# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-03T14:30:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap-1
- **Gap Title**: No cross-strategy accuracy comparison on LongBench v2 task-category splits for converted models
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15
- **Recursive Entry**: v4 (prior hypotheses: h-e1 SUPERSEDED, h-m2 PARTIAL)

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All 6 criteria met — SPECIFIC, MECHANISM, PREDICTIONS (P1-P3 quantitative), NOVELTY, FEASIBILITY (confirmed 14 GPU-days), OBJECTIONS (5 pre-registered disconfirmation pathways)

### Key Insights
1. Holding the base model (LLaMA-3-8B) constant across conversion strategies eliminates H-E1's capability-tier confound — the critical design lesson from prior failures
2. LAWCAT's causal Conv1D layer provides mechanistic basis for predicting *differential* depth-degradation slope vs. MOHAWK-SSM, not just a general "linear attention vs SSM" comparison
3. Overflow Prevention paper [2505.07793] evaluates scratch-trained SSMs on LongBench v2 directly — these results are reusable as a baseline without additional training
4. Scope-bounding was essential: layer-localization (early/middle/late hybrid) is deferred to Phase 4 to preserve publishability of the primary experiment

### Breakthrough Moments
- **Exchange 1**: Dr. Nova identified the task-type × strategy *interaction* as the novel contribution, not just strategy ranking
- **Exchange 7**: Dr. Ally named H-Conv1D-v1 and defended scope-bounded primary claim against Prof. Rex's layer-localization extension
- **Exchange 11**: Dr. Sage recognized Overflow Prevention as a directly reusable LongBench v2 scratch-trained baseline
- **Exchange 14**: Prof. Vera formalized the ≥2× ratio criterion with bootstrap CI as the primary statistical test

---

## Final Hypothesis

### Title
Task-Type × Conversion-Strategy Interaction in Sub-Quadratic Transformer Conversion (H-Conv1D-v1)

### Core Claim
Under fixed-budget (≤1B tokens) short-context distillation of LLaMA-3-8B:
- **If** we compare MOHAWK-SSM vs. LAWCAT-linear-attention conversion on LongBench v2
- **Then** MOHAWK-SSM shows ≥2× larger normalized degradation on retrieval-heavy categories (multi-doc QA, synthetic) compared to generation-heavy categories (summarization, few-shot), while LAWCAT shows a significantly more uniform profile
- **Because** MOHAWK-SSM compresses context into bounded state vectors losing exact needle-token positions, while LAWCAT's causal Conv1D preserves local token-to-token attention enabling shallower retrieval degradation

### Mechanism
1. MOHAWK replaces attention with SSD mixer — matrix approximation fidelity established at N=512 (Frobenius ≈0.097); gate check required at N=8k before committing to distillation
2. SSM bounded state (h_t = A·h_{t-1} + B·x_t) causes exponential forgetting of early token positions — retrieval tasks probe this directly; generation tasks tolerate lossy compression
3. LAWCAT's causal Conv1D provides local attention in a sliding window, preserving short-range token identity — produces shallower depth-degradation slope than pure SSM

---

## Predictions

| ID | Type | Statement | Success Criterion |
|----|------|-----------|-------------------|
| P1 | Primary | MOHAWK-SSM shows ≥2× larger Δ_norm on retrieval vs. generation categories; significant task-type × strategy interaction | Δ_norm^SSM/Δ_norm^LAWCAT ≥ 2.0, 95% CI excluding 1.0; interaction p<0.01 (Holm) |
| P2 | Secondary | LAWCAT β_depth slope shallower than MOHAWK-SSM in needle-depth logistic regression | \|β^SSM\| ≥ 2× \|β^LAWCAT\|, non-overlapping 95% CIs |
| P3 | Secondary | Hybrid-4 (middle 4 attention layers) shows ≤5% Δ_norm vs. full MOHAWK ≥10% on retrieval | Falsifies "full replacement is adequate for retrieval" if confirmed |

---

## Novelty

- **Key innovation**: First controlled within-subject comparison (fixed LLaMA-3-8B) of MOHAWK-SSM vs. LAWCAT on LongBench v2 task-category splits
- **Prior work gaps**: MOHAWK (Phi-1.5, no LongBench v2), LAWCAT (Mistral-7B, synthetic retrieval only), Overflow Prevention (scratch-trained only)
- **Prior failure avoidance**: Fixed base model eliminates H-E1's 20pp capability gap confound; no KV eviction (H-M2 lesson)

---

## Experimental Design

### Models & Conditions
| Condition | Description | Compute |
|-----------|-------------|---------|
| Teacher | LLaMA-3-8B unconverted | baseline |
| MOHAWK-SSM | Stage 1+2 (SSD mixer, ≤1B tokens, 2048-token curriculum) | ~4 days × 4×A100 |
| LAWCAT | Conv1D + gated linear attention (≤1B tokens) | ~3 days × 2×A100 |
| Hybrid-4 | MOHAWK Stage 3 only, 4 middle attention layers retained | ~2 days × 2×A100 |
| Scratch-SSM | Falcon3-Mamba-7B (reuse Overflow Prevention results) | 0 GPU-days |

### Evaluation
- **Benchmark**: LongBench v2 (THUDM/LongBench, 503 questions, 6 categories, 8k–2M)
- **Framework**: EleutherAI/lm-evaluation-harness (LongBench v2 PR #3256)

### Gate Protocol (Day 0, ~2 days)
1. Frobenius error scaling: N ∈ {512, 1k, 2k, 4k, 8k} — abort if log-log slope > 0.5 or 90th pct > 0.3 at N=8k
2. CUDA compatibility check (Flash Linear Attention vs. FSDP on cluster)
3. Spectral norm of SSD mixing matrix vs. token distance

### Training Gates
- Alignment ratio gate: median L2 ratio ≤ 0.15 after Stage 2 (200M tokens)
- Perplexity gate: gap vs. teacher ≤ 5% relative — **STRICTLY ENFORCED before LongBench evaluation**

### Statistical Analysis
- Normalized degradation: Δ_norm = (Acc_teacher − Acc_student) / Acc_teacher per category
- Mixed-effects model: Δ_norm ~ TaskType * Strategy + (1|Task), Holm correction
- Bootstrap CI on Δ_norm ratio (10,000 samples)
- Depth-slope logistic regression: P(correct) ~ DepthPercentile + (1|Task) per model
- Mediation regression: Acc_retrieval ~ Strategy + AlignmentRatio + PPL_gap + MatrixError_2k

---

## Limitations

- Architecture-vs-curriculum confound: retrieval degradation may reflect short-only distillation, not inherent SSM bounds (Phase 4 ablation deferred)
- Layer attribution: "some attention layers necessary" established by Hybrid-4, but which (early/middle/late) requires Phase 4
- Single base model: generalization to Mistral-7B, Phi-3 not tested in primary experiment
- Statistical power: LongBench v2 (503 questions) may require bootstrap CIs rather than asymptotic tests for per-category analysis

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met at exchange 15 |
| **Clarity Verified** | Yes |
| **Remaining Objections** | 3 — all deferred to Phase 4 (curriculum ablation, layer-localization, perplexity gate enforcement) |
| **Phase 2B Ready** | Yes |

---

*Generated by Phase 2A Tikitaka Discussion — 15 exchanges, UNATTENDED mode*
*Recursive entry v4: prior failures h-e1 (SUPERSEDED) and h-m2 (PARTIAL) informed hypothesis design*
*Gap addressed: Gap 1 (Critical/Primary) — no cross-strategy LongBench v2 comparison*
