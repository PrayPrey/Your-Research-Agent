---
stepsCompleted: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
status: complete
completedAt: "2026-08-31"
hypothesis_id: H-SA-LoRA-v1
research_scope_mode: incremental
last_updated: "2026-08-31"
---

# Verification Plan: State-Aware LoRA (SA-LoRA) for Mamba SSMs

**Date:** 2026-08-31
**Hypothesis ID:** H-SA-LoRA-v1
**Confidence:** 0.72
**Total Hypotheses:** 4 (H-E1, H-M1, H-M2, H-M3)

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under fine-tuning of Mamba SSMs (Mamba-1 130m/370m; Mamba-2 if checkpoint available) on NLP classification and long-context tasks (GLUE + LongBench subset), if we adapt the recurrent state decay parameters (A_log bias for Mamba-1; scalar A multiplier for Mamba-2) in addition to standard LoRA on projection layers (in_proj, out_proj, x_proj, dt_proj), then downstream task accuracy improves beyond projection-only LoRA (GLUE average ≥1%, LongBench ≥2%), because A-adaptation modifies task-specific memory horizons (base forgetting rate) in a way that projection-layer LoRA cannot replicate, with gain magnitude positively correlated with task sequence length requirements.

### 1.2 Alternative Hypothesis (H0)

There is no statistically significant difference in downstream NLP accuracy (GLUE average, LongBench) between State-Aware LoRA (projection LoRA + A-adaptation) and projection-only LoRA at matched or lower trainable parameter count on Mamba-130m and Mamba-370m.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | GLUE + LongBench (2WikiMultihopQA subset) (standard) | GLUE provides short-range classification tasks (SST-2: ~20 tokens, MNLI: ~100 tokens) to test baseline PEFT transfer; LongBench 2WikiMultihopQA provides long-range QA (~5K tokens) to test memory-horizon effect. Together they span the sequence length range needed to validate P2. |
| **Model** | Mamba-130m, Mamba-370m | Primary target architecture; 130m provides fast iteration; 370m validates scale generalization per Prof. Rex's Concern 2 |

**Dataset Details:**
- Source: HuggingFace datasets (glue), THUDM/LongBench
- Path: hf://datasets/glue; hf://datasets/THUDM/LongBench

**Model Details:**
- Type: State Space Model (SSM), causal language model
- Source: state-spaces/mamba-130m-hf, state-spaces/mamba-370m-hf (HuggingFace Hub)

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| LoRA on transformer (GPT-2, LLaMA-7B) | GLUE average: ~85-90% for GPT-2-large equivalent; competitive with full fine-tuning at r=8 | GLUE |
| Full fine-tuning of Mamba | Unknown — no systematic GLUE evaluation in Phase 1 literature | GLUE |
| Projection-only LoRA on Mamba (Condition A) | Unknown — this is the primary comparison baseline being established | GLUE, LongBench |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Pretrained Mamba A_log initialization (HiPPO-based) is suboptimal for specific downstream tasks | HiPPO optimizes for memorizing continuous functions — a general prior; task-specific tasks have different temporal structure | A_log bias trains to zero; state-aware PEFT provides no benefit |
| A2 | GLUE and LongBench tasks are sufficiently diverse in temporal depth to reveal memory-horizon effects | SST-2 avg ~20 tokens; MNLI ~100 tokens; 2WikiMultihopQA ~5000 tokens — three orders of magnitude difference | Memory-horizon adaptation provides uniform negligible benefit |
| A3 | Mamba-130m and 370m pretrained checkpoints available and loadable via HuggingFace | state-spaces/mamba-130m-hf and state-spaces/mamba-370m-hf listed on HuggingFace Hub | Experiment requires alternative checkpoint source or Mamba-2 variants |
| A4 | EleutherAI lm-evaluation-harness supports Mamba for both GLUE and LongBench evaluation | lm-eval-harness has Mamba integration per Phase 1 research; LongBench generation needs verification | LongBench evaluation requires custom code; fallback to SCROLLS or GLUE+MMLU |
| A5 | HuggingFace PEFT can be extended or A_log bias added manually before get_peft_model() | A_log bias is simpler than LoRA — register trainable nn.Parameter δ and add to A_log in forward() | Custom training loop needed; adds engineering complexity but does not block experiment |

### 1.6 Research Gap & Novelty

**Gap:** No prior PEFT work targets SSM state decay parameters as a distinct adaptation category. All prior methods (LoRA, AdaLoRA, IA³, DoRA) treat Mamba as an architecture with linear projection layers, ignoring recurrent state dynamics.

**Novelty:** SA-LoRA introduces memory-horizon adaptation — treating the SSM decay parameter as a task-specific prior over information persistence. This is the first PEFT method to explicitly adapt the temporal structure of SSM memory (A_log), opening a new design axis for parameter-efficient adaptation of recurrent models. The gain is predicted to be larger on longer-range tasks, providing an empirically testable mechanistic signature.

**Established Facts (BUILD_ON — do not re-verify):**
1. LoRA on nn.Linear layers applies to Mamba projection layers without modification (Hu et al., 2022)
2. Mamba-1 A_log bias adaptation preserves recurrent stability (mathematical: A = -exp(A_log) always negative)
3. Mamba-2 scalar A per SSM head enables IA³-style adaptation with O(num_heads) parameter overhead

**Scope Reduction:** 60% (3 BUILD_ON claims skipped; only 2 PROVE_NEW claims require empirical validation)

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | MUST_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | MUST_WORK | H-M2 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Projection-Layer LoRA Transfers to Mamba (Existence)**

**Statement**: Under fine-tuning of Mamba-130m on GLUE (SST-2, MNLI, QNLI, QQP) with LoRA on projection layers (in_proj, out_proj, x_proj, r=8), if we apply projection-only LoRA (Condition A), then GLUE average accuracy exceeds 70% on SST-2 and is non-trivially above zero-shot baseline, because standard LoRA applies to any nn.Linear layer including Mamba projection layers without architectural modification.

**Rationale**: This hypothesis validates that parameter-efficient fine-tuning transfers to Mamba SSMs at all — establishing the existence of a signal before testing state-aware improvement. It subsumes Gap 1 (baseline benchmarking) as a byproduct and provides the Condition A reference point for all subsequent H-M comparisons. Without passing H-E1, state-aware PEFT gains cannot be meaningfully attributed to A-adaptation.

**Variables** (from Phase 2A):
- Independent: PEFT configuration (Condition A: in_proj, out_proj, x_proj LoRA, r=8)
- Dependent (primary): GLUE average accuracy (SST-2, MNLI, QNLI, QQP)
- Controlled: lr=3e-4, batch_size=32, epochs=3, seeds {42,43,44}

**Verification Protocol**:
1. Fine-tune Mamba-130m with Condition A LoRA config on each GLUE task for 3 epochs × 3 seeds.
2. Evaluate with lm-evaluation-harness on SST-2, MNLI, QNLI, QQP; record per-task accuracy and average.
3. Verify SST-2 accuracy > 70% (non-trivial transfer) and average above zero-shot Mamba-130m baseline.

**Success Criteria** (PoC):
- Primary: SST-2 accuracy > 70% (proposed > uninstructed baseline)
- Secondary: GLUE average improvement over zero-shot Mamba-130m baseline (directional)

**Failure Response**:
- IF fails: PIVOT — investigate lm-eval-harness Mamba compatibility (A4 assumption violated); fallback to MMLU or custom eval

**Dependencies**: None (foundation)
**Source**: Phase 2A SH1, Prediction P1, Section 2 Experimental Setup

---
**H-M1: Projection LoRA Adapts Input/Output State Mappings (Mechanism Step 1)**

**Statement**: Under fine-tuning of Mamba-130m with projection LoRA (Condition A, r=8), if we examine the effective B and C matrices (state read/write mappings) before and after fine-tuning, then the fine-tuned model shows changed effective B/C behavior measurable as improved accuracy relative to untrained Mamba, because LoRA on in_proj, out_proj, x_proj directly modifies what information enters (B) and exits (C) the recurrent state without changing the state evolution rate (α = exp(Δ·A)).

**Rationale**: This hypothesis validates the first causal step: projection LoRA works mechanistically as claimed. It establishes that the baseline improvement from H-E1 is attributable to B/C adaptation and not to other factors. The key empirical test is whether projection LoRA alone saturates at a performance level below full fine-tuning, leaving room for A-adaptation to add value.

**Variables**:
- Independent: PEFT configuration (Condition A vs. zero-shot baseline)
- Dependent: GLUE average accuracy; learned LoRA weight magnitudes (diagnostic)
- Controlled: Fixed A_log (no A adaptation); all training hyperparameters

**Verification Protocol**:
1. Compare Condition A (projection LoRA) vs. zero-shot Mamba-130m on GLUE average.
2. Compute performance gap between Condition A and full fine-tuning ceiling to assess saturation.
3. Verify that projection-LoRA accuracy delta vs. zero-shot is positive and consistent across 3 seeds.

**Success Criteria** (PoC):
- Primary: Condition A > zero-shot baseline by measurable margin (>2pp on GLUE average)
- Secondary: Condition A < full fine-tuning ceiling (headroom exists for further improvement)

**Failure Response**:
- IF fails: EXPLORE — if Condition A already matches full fine-tuning, projection LoRA is sufficient and A-adaptation is unnecessary; revise H-M2/H-M3

**Dependencies**: H-E1 (must confirm LoRA transfers before attributing mechanism)
**Source**: Phase 2A Causal Step 1, Section 1.3

---
**H-M2: A_log Bias Adaptation Shifts State Decay Rate Measurably (Mechanism Step 2)**

**Statement**: Under fine-tuning of Mamba-130m with state-aware LoRA (Condition C: projection LoRA + A_log bias δ ∈ ℝ^{d_model}), if we train and extract the learned δ values after fine-tuning on tasks with different sequence length requirements (SST-2 ~20 tokens, MNLI ~100 tokens, 2WikiMultihopQA ~5K tokens), then the mean |δ| is larger for longer-range tasks (MNLI > SST-2), because A-adaptation shifts the base state decay rate per channel in a task-appropriate direction — shorter retention for local-context tasks, longer retention for multi-step reasoning.

**Rationale**: This hypothesis validates the core mechanism claim: A_log bias is not merely a regularization add-on but a task-specific adaptation of temporal memory structure. The diagnostic P3 (|δ_MNLI| > |δ_SST-2|) provides mechanistic evidence of the memory-horizon effect independent of accuracy gain. If δ collapses to near-zero across all tasks, the HiPPO initialization is already task-optimal and the entire SA-LoRA contribution is invalidated.

**Variables**:
- Independent: PEFT configuration (Condition C: projection LoRA + A_log bias); task type (short vs. long range)
- Dependent: Mean |δ_A_log| per task after fine-tuning; GLUE and LongBench accuracy
- Controlled: Projection LoRA fixed at r=8; training hyperparameters; model checkpoint

**Verification Protocol**:
1. Fine-tune Mamba-130m with Condition C on each GLUE task + 2WikiMultihopQA for 3 epochs × 3 seeds.
2. After each run, extract δ = learned A_log bias from model state_dict; compute mean |δ| per channel.
3. Compare mean |δ| across SST-2, MNLI, 2WikiMultihopQA — verify monotonic increase with task range.
4. Report as diagnostic (directional, no significance threshold); |δ| < 0.01 across all tasks = P3 falsified.

**Success Criteria** (PoC):
- Primary: Mean |δ_MNLI| > mean |δ_SST-2| after task-specific fine-tuning (directional diagnostic)
- Secondary: Mean |δ| > 0.01 in at least one task (non-trivial A-adaptation occurring)

**Failure Response**:
- IF |δ| < 0.01 for all tasks: ABANDON H-M2 and H-M3; A1 assumption violated; HiPPO is task-optimal; publish null finding

**Dependencies**: H-M1 (projection LoRA mechanism confirmed before adding A-adaptation layer)
**Source**: Phase 2A Causal Step 2, Prediction P3, Section 1.4 Assumption A1

---
**H-M3: State-Aware LoRA (A-Adaptation + Projection) Is Non-Redundant with Projection-Only LoRA (Mechanism Step 3)**

**Statement**: Under fine-tuning of Mamba-130m on GLUE + LongBench 2WikiMultihopQA, if we compare Condition D (full state-aware: projection LoRA + dt_proj LoRA + A_log bias) vs. Condition A (projection-only LoRA) at matched or lower trainable parameter count, then Condition D achieves ≥1pp higher GLUE average and ≥2pp higher LongBench F1, because A-adaptation controls temporal memory structure (α = exp(Δ·A)) in a way that B/C projection adaptation cannot replicate — modifying what is stored/read leaves the decay rate unchanged, so memory horizon mismatch persists under projection-only LoRA.

**Rationale**: This is the central empirical claim — non-redundancy of A-adaptation and projection LoRA. The 4-condition ablation (A, B, C, D) is designed to isolate this: if D > A but B ≈ C ≈ A, then direct A-adaptation (not indirect dt_proj modulation) is responsible. The key tension is whether dt_proj LoRA (Condition B, indirect decay via Δ) already captures the memory-horizon effect, making direct A_log bias (Condition C) redundant. H-M3 passes only if state-aware adaptation provides demonstrable gain beyond projection-only, regardless of which state-aware variant is strongest.

**Variables**:
- Independent: PEFT configuration (4 conditions: A, B, C, D); model scale (130m, 370m)
- Dependent (primary): GLUE average accuracy; LongBench 2WikiMultihopQA F1
- Controlled: LoRA rank r=8 (ablate r=4,16 as secondary); training hyperparameters; seeds {42,43,44}

**Verification Protocol**:
1. Run full 4-condition × 2-scale × 3-seed ablation on GLUE (SST-2, MNLI, QNLI, QQP) and LongBench 2WikiMultihopQA.
2. Compare GLUE average(D) vs. GLUE average(A); run paired t-test across 3 seeds (p < 0.05).
3. Compare LongBench F1(C or D) vs. LongBench F1(A); verify LongBench delta > SST-2 delta (P2 check).
4. Replicate primary comparison at Mamba-370m to verify scale generalization.

**Success Criteria** (PoC):
- Primary: GLUE average(D) > GLUE average(A) by ≥1.0pp, p < 0.05 (paired t-test, 3 seeds)
- Secondary (P2): LongBench gain (state-aware vs. projection-only) ≥ SST-2 gain by ≥1pp

**Failure Response**:
- IF GLUE delta < 0.5pp: PIVOT — state-aware PEFT does not generalize to classification tasks; test generation-only tasks or accept null result
- IF LongBench delta not larger than SST-2 delta: EXPLORE — memory-horizon mechanism may be weaker than predicted; revise scope

**Dependencies**: H-M2 (A-adaptation shown to produce non-zero δ before testing accuracy gain)
**Source**: Phase 2A Causal Step 3, Predictions P1+P2, PROVE_NEW claim 2, Section 1.4 Assumption A2

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | SST-2 accuracy > 70%; GLUE average above zero-shot | STOP all downstream; reassess entire hypothesis |
| H-M1 | MUST_WORK | Condition A > zero-shot by >2pp; headroom vs. full fine-tuning exists | EXPLORE — if A ≈ ceiling, projection LoRA sufficient |
| H-M2 | MUST_WORK | Mean |δ_A_log| > 0.01 in ≥1 task; MNLI |δ| > SST-2 |δ| | ABANDON H-M2/H-M3; publish null finding |
| H-M3 | MUST_WORK | GLUE avg(D) > avg(A) ≥1pp, p<0.05; LongBench gain > SST-2 gain | PIVOT to generation tasks or accept null |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1 — Foundation | H-E1 | ~2 days (setup + GLUE eval × 3 seeds) |
| Phase 2 — Mechanism Step 1 | H-M1 | ~1 day (analysis of Condition A results already run) |
| Phase 2 — Mechanism Step 2 | H-M2 | ~3 days (Condition C training + δ extraction × tasks × seeds) |
| Phase 2 — Mechanism Step 3 | H-M3 | ~4 days (4-condition × 2-scale × 3-seed full ablation) |

**Total Duration:** ~10 days (sequential; Phase 1 and partial Phase 2 can be batched)

---

## 4. Risk Analysis

Risks derived from Phase 2A key assumptions A1-A5. Each assumption violation maps to one risk. No H-C hypotheses; all risks affect H-E1 or H-M chain.

### Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: HiPPO already task-optimal | A1 | H-M2, H-M3 | High |
| R2: Tasks not diverse enough in temporal depth | A2 | H-M3 | Medium |
| R3: Mamba checkpoints unavailable | A3 | All (H-E1, H-M1, H-M2, H-M3) | High |
| R4: lm-eval-harness incompatible with Mamba LongBench | A4 | H-M3 (LongBench) | Medium |
| R5: PEFT/A_log integration engineering barrier | A5 | H-M2, H-M3 | Low |

### Mitigation Strategies

**Risk R1: HiPPO Already Task-Optimal (Severity: High)**
- Source Assumption: A1 — HiPPO initialization is suboptimal for specific downstream tasks
- Affected Hypotheses: H-M2, H-M3
- Severity: High (invalidates core novelty claim if violated)
- Prevention: Monitor learned |δ| magnitudes as training progresses — early signal of violation
- Detection: If mean |δ_A_log| < 0.01 across all tasks after 1 epoch, stop and assess
- Response:
  - PIVOT: Test on more diverse tasks (code generation, math) where memory horizon matters more
  - SCOPE: Publish as "null finding with diagnostic" — near-zero δ is itself a contribution to PEFT understanding
  - ABORT: If P3 falsified (δ ≈ 0 universally), abandon H-M2/H-M3 and revise to conditional hypothesis

**Risk R2: Tasks Not Sufficiently Diverse in Temporal Depth (Severity: Medium)**
- Source Assumption: A2 — GLUE and LongBench span sufficient temporal range to reveal memory-horizon effects
- Affected Hypotheses: H-M3 (P2 prediction)
- Prevention: The 3-order-of-magnitude span (20 tokens to 5K tokens) is extreme — task diversity is strong
- Detection: If accuracy gain from A-adaptation is uniform across SST-2, MNLI, and LongBench (no length correlation)
- Response:
  - EXPLORE: Add SCROLLS or RULER benchmark (extreme long-context) to amplify memory-horizon signal
  - SCOPE: Report as "memory-horizon mechanism exists but gain is task-length-insensitive within tested range"

**Risk R3: Mamba Pretrained Checkpoints Unavailable (Severity: High)**
- Source Assumption: A3 — state-spaces/mamba-130m-hf and state-spaces/mamba-370m-hf loadable from HuggingFace
- Affected Hypotheses: All (H-E1, H-M1, H-M2, H-M3)
- Prevention: Verify checkpoint availability in Phase 2C pre-experiment setup before writing any Phase 4 code
- Detection: HuggingFace Hub 404 or model loading error at Phase 4 start
- Response:
  - PIVOT: Use Mamba-2 checkpoints (Tri Dao's repo) or download and cache locally before experiment
  - PIVOT: Fall back to MambaFormer or other publicly available Mamba-family models
  - Early Warning: Run `from transformers import MambaForCausalLM` import test as Phase 2C check

**Risk R4: lm-eval-harness Incompatible with Mamba LongBench Generation (Severity: Medium)**
- Source Assumption: A4 — lm-eval-harness supports Mamba for both classification (GLUE) and generation (LongBench)
- Affected Hypotheses: H-M3 (LongBench component of P2)
- Prevention: Pre-experiment LongBench compatibility check in Phase 2C design
- Detection: lm-eval-harness raises NotImplementedError or produces degenerate outputs for Mamba generation tasks
- Response:
  - PIVOT: Use 2WikiMultihopQA as extractive QA (substring match), bypassing generation — Prof. Rex's suggested mitigation
  - PIVOT: Implement custom LongBench evaluation loop outside lm-eval-harness
  - SCOPE: If generation fails entirely, restrict to GLUE + MMLU (multiple choice) for primary evaluation; report LongBench as future work

**Risk R5: PEFT/A_log Integration Engineering Barrier (Severity: Low)**
- Source Assumption: A5 — A_log bias can be added as trainable nn.Parameter before get_peft_model()
- Affected Hypotheses: H-M2, H-M3
- Prevention: A_log bias implementation is simple (register nn.Parameter δ; add to A_log in forward()); no PEFT library extension needed
- Detection: Unexpected gradient flow issues or PEFT wrapping errors
- Response:
  - PIVOT: Use custom training loop with manual optimizer (bypasses PEFT library)
  - SCOPE: Engineering complexity adds ~1 day; does not block experiment
  - Early Warning: Test A_log bias addition in isolation (1-layer Mamba test) before full fine-tuning

### Risk Summary

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | HiPPO already task-optimal; δ → 0 | A1 | High | H-M2, H-M3 | Monitor |δ| during training; pivot to harder tasks or publish null |
| R2 | Task temporal range insufficient | A2 | Medium | H-M3 | Add SCROLLS if needed; report length-insensitive gain |
| R3 | Mamba checkpoints unavailable | A3 | High | All | Verify pre-Phase 4; fallback to Mamba-2 or local cache |
| R4 | lm-eval LongBench incompatibility | A4 | Medium | H-M3 | Extractive QA fallback; custom eval loop |
| R5 | A_log PEFT engineering barrier | A5 | Low | H-M2, H-M3 | Custom training loop; 1-day workaround |

Critical Risks: 0
High Risks: 2 (R1, R3)
Medium Risks: 2 (R2, R4)
Low Risks: 1 (R5)

---

## 5. Visualization

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root: Foundation]
    H-E1: Projection LoRA Existence
    (Gate: MUST_WORK — no deps)
         │
         ▼ [Gate 1: SST-2 > 70%]
[Level 1 - Mechanism Step 1]
    H-M1: Projection LoRA Mechanism
    (Dep: H-E1)
         │
         ▼ [Gate 2: Condition A > zero-shot]
[Level 2 - Mechanism Step 2]
    H-M2: A_log Bias Non-Zero Adaptation
    (Dep: H-M1)
         │
         ▼ [Gate 3: |δ| > 0.01, MNLI > SST-2]
[Level 3 - Mechanism Step 3]
    H-M3: State-Aware Non-Redundancy
    (Dep: H-M2)
         │
         ▼ [Gate 4: GLUE D > A by ≥1pp]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Levels: 4 | Phases: 2 | Circular deps: None
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|------------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | MUST_WORK |
| 3 | H-M3 | H-M2 | MUST_WORK |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses (H-SA-LoRA-v1)
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2    │ W3-4    │ W5      │ W6-7
─────────────────┼─────────┼─────────┼─────────┼──────────
PHASE 1: Foundation
  H-E1 (Exist.) │ ████████│         │         │
  [Gate 1]       │       ◆ │         │         │
─────────────────┼─────────┼─────────┼─────────┼──────────
PHASE 2: Mechanisms
  H-M1 (Mech.1) │         │ ████████│         │
  H-M2 (Mech.2) │         │         │ ████    │
  H-M3 (Mech.3) │         │         │         │ ████████
  [Gate 2]       │         │         │         │       ◆
─────────────────┼─────────┼─────────┼─────────┼──────────
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 5-6 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

Critical Path: H-E1 → H-M1 → H-M2 → H-M3

Total Duration: 5-6 weeks
- Formula: 2 (H-E1) + 3 (H-M1 + H-M2 + H-M3) = 5 weeks minimum
- H-M3 runs 4-condition × 2-scale × 3-seed: may require 2 weeks → 6 weeks total

Slack: 0 weeks (fully sequential; no parallelization — each gate requires prior result)

Bottleneck: H-M3 (largest experiment: 4 conditions × 2 scales × 3 seeds × 5 tasks)

### 5.5 Resource Summary

Total Hypotheses: 4
- Existence: 1 (H-E1)
- Mechanism: 3 (H-M1, H-M2, H-M3)
- Condition: 0

Verification Phases: 2 (Foundation, Mechanisms)
Total Duration: 5-6 weeks
Critical Path Length: 5-6 weeks
Execution Mode: Sequential chain (all MUST_WORK gates)

Compute Requirements (estimate):
- H-E1: ~12 runs (4 GLUE tasks × 3 seeds) on 1 GPU
- H-M2: ~20 runs (5 tasks × 3 seeds × Condition C) on 1 GPU
- H-M3: ~120 runs (4 conditions × 2 scales × 3 seeds × 5 tasks) on 1-2 GPUs

### 5.6 Execution Order

Step 1: Execute H-E1 (Condition A, projection-only LoRA) — Weeks 1-2
Step 2: Evaluate Gate 1 → SST-2 > 70%; if fail: STOP and reassess
Step 3: Execute H-M1 (analyze Condition A results mechanistically) — Week 3-4
Step 4: Evaluate Gate 2 (H-M1) → Condition A > zero-shot; headroom exists
Step 5: Execute H-M2 (Condition C, A_log bias) + extract δ magnitudes — Week 5
Step 6: Evaluate Gate 3 (H-M2) → |δ| > 0.01 in ≥1 task; if fail: ABANDON H-M3
Step 7: Execute H-M3 (full 4-condition × 2-scale ablation + LongBench) — Weeks 6-7
Step 8: Evaluate Gate 4 (H-M3) → GLUE avg(D) > avg(A) ≥1pp, p<0.05
Final: Verification complete → Phase 4.5 synthesis

---

## 6. Dialectical Analysis

Structured evaluation of H-SA-LoRA-v1 using Thesis-Antithesis-Synthesis framework. Antithesis grounded in H0 from Phase 2A. Incremental mode: 1 dialectical evaluation (main hypothesis vs. H0).

**Thesis:**

Core Claim: SA-LoRA (State-Aware LoRA) improves NLP fine-tuning accuracy on Mamba SSMs beyond projection-only LoRA by adapting the recurrent state decay parameter (A_log bias), which controls task-specific memory horizons that projection-layer LoRA cannot replicate.

Supporting Evidence:
1. Mathematical: y_t = C_t·h_t, h_t = α·h_{t-1} + B_t·x_t — adapting B/C (projections) leaves α (decay, controlled by A) unchanged; A_log bias is the only parameter that shifts α
2. Mechanistic: HiPPO initialization is general-purpose; task-specific tasks have different temporal structure (SST-2 ~20 tokens vs. 2WikiMultihopQA ~5K tokens) — task-specific decay adaptation is theoretically motivated
3. Predictive: Three independently testable predictions (P1: accuracy gain, P2: gain correlates with task length, P3: |δ| correlates with task range) allow partial validation even if not all predictions hold

Strengths:
- Stability-preserving by construction: A = -exp(A_log) is always negative, so any bias δ on A_log is safe
- Non-redundancy is mathematically derivable (not just asserted) — the 4-condition ablation cleanly tests this
- Parameter overhead is tiny (~0.3% of LoRA budget for Mamba-130m), making the method practically attractive

Expected Outcomes:
- Primary (P1): Condition D GLUE avg > Condition A by ≥1pp, p < 0.05
- Secondary (P2): LongBench gain (state-aware) > SST-2 gain by ≥1pp
- Diagnostic (P3): |δ_MNLI| > |δ_SST-2| after fine-tuning

**Antithesis:**

Null Hypothesis (H0): There is no statistically significant difference in downstream NLP accuracy (GLUE average, LongBench) between State-Aware LoRA (projection LoRA + A-adaptation) and projection-only LoRA at matched or lower trainable parameter count on Mamba-130m and Mamba-370m.

Counter-Arguments:
1. dt_proj LoRA (Condition B) may already provide sufficient indirect decay adaptation via Δ modulation — if Condition B ≈ Condition C in accuracy, direct A_log bias adds nothing beyond what indirect timescale adaptation achieves (key tension identified in Phase 2A)
2. HiPPO initialization may already be sufficiently task-adaptive across the tested task range — the tasks differ in surface length but may require similar effective memory depths after tokenization/embedding
3. Mamba SSMs may adapt to tasks primarily through projection layers (what to encode/decode from state) rather than through how long to retain state, making memory-horizon adaptation a second-order effect below the noise floor at 130m/370m scale

Potential Failure Points:
- R1: |δ| collapses to near-zero (HiPPO is task-optimal) → P3 falsified, core mechanism absent
- R2: GLUE tasks show uniform gain regardless of task length → P2 falsified, memory-horizon effect not observable
- R3: Mamba checkpoints unavailable → experiment cannot run at all

Conditions Under Which H0 Would Be Supported:
- GLUE avg(D) ≤ GLUE avg(A) + 0.5pp (within noise, p ≥ 0.05)
- Mean |δ_A_log| < 0.01 across all tasks after fine-tuning (near-zero bias = P3 falsified)
- Condition B (indirect dt_proj) shows same accuracy as Condition C (direct A_log) — indirect adaptation sufficient

**Synthesis:**

H-SA-LoRA-v1 presents a mechanistically grounded and testable claim with a clear causal chain. The antithesis raises three legitimate challenges (dt_proj redundancy, HiPPO task-adequacy, scale sensitivity) that the verification plan directly addresses through the 4-condition ablation design.

Resolution Path: The verification plan addresses this dialectic through:
1. Foundation verification (H-E1): Establishes that PEFT on Mamba works at all before testing state-aware improvement
2. Diagnostic mechanism test (H-M2): P3 (|δ| analysis) provides mechanistic evidence independent of accuracy gain — if δ ≈ 0, H0 is supported without wasting H-M3 compute
3. Gate conditions: H-M2 gate (|δ| > 0.01) prevents expensive H-M3 ablation when mechanism is absent
4. 4-condition ablation design isolates dt_proj vs. A_log vs. combined — directly tests the redundancy antithesis

Conditions for Thesis Support: All MUST_WORK gates pass; P1 confirmed (GLUE gain ≥1pp); P3 non-trivial (|δ| > 0.01)
Conditions for Antithesis Support: H-M2 gate fails (|δ| ≈ 0) OR H-M3 gate fails (Condition D ≈ Condition A)

Nuanced Outcomes:
1. Full Support: H-E1 ✓, H-M1 ✓, H-M2 ✓, H-M3 ✓ → SA-LoRA validated; P2 confirms memory-horizon mechanism
2. Partial Support (Mechanism Real but Weak): H-M2 ✓ (|δ| > 0, non-zero), H-M3 marginal (0.5pp < gain < 1pp) → SA-LoRA has theoretical validity but practical gain is small; publish with appropriate scoping
3. Indirect Sufficient: H-M3 shows Condition B ≈ Condition C >> Condition A → dt_proj LoRA captures most of state-aware benefit; direct A_log bias adds marginal value; publish Condition B as recommended practice
4. Null Finding: H-M2 fails (|δ| ≈ 0) → H0 supported; HiPPO is task-optimal; publish as important negative result for PEFT community

**Robustness Assessment:**

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | PEFT transfers to Mamba SSMs | SSMs may not benefit from standard LoRA | H-E1 test (direct empirical) |
| Mechanism (projection) | B/C adaptation modifies state content | Projections may be sufficient alone | H-M1 (saturation analysis) |
| Mechanism (A-decay) | A_log bias shifts memory horizon non-trivially | HiPPO may already be task-optimal | H-M2 (δ diagnostic, early exit) |
| Non-redundancy | A-adaptation non-redundant with projection LoRA | dt_proj LoRA may capture same effect indirectly | H-M3 (4-condition ablation) |
| Scope | Effect larger on longer-range tasks | Effect uniform/absent | P2 check in H-M3 |

Overall Robustness Score: **High** — 3-step causal chain is mathematically grounded; 4 independent falsification points; early-exit gate (H-M2) prevents wasted compute if mechanism absent

Confidence in Verification Plan: 0.72 (matches Phase 2A confidence; main uncertainty is dt_proj vs. A_log redundancy, resolved empirically in H-M3)

---

## 7. Executive Summary & Conclusions

**Main Hypothesis:** SA-LoRA adapts Mamba A_log decay bias alongside projection LoRA → GLUE avg ≥1pp gain, LongBench ≥2pp gain
- ID: H-SA-LoRA-v1 | Confidence: 0.72

**Verification Structure:**
- Mode: Incremental (Phase 2A pre-validated 60% of claims)
- Sub-Hypotheses: 4 (H-E1, H-M1, H-M2, H-M3) — no H-C
- Phases: 2 (Foundation + Mechanisms) over 5-6 weeks
- Critical Gates: 4 MUST_WORK decision points

**Risk Assessment:** Medium
- Primary concerns: R1 (HiPPO task-optimal, δ→0), R3 (checkpoint availability)

**Immediate Action:** Verify Mamba checkpoint availability (A3 pre-check) → then begin H-E1

### Final Summary

Key Achievements:
- 4 sub-hypotheses spanning 3 causal steps
- H0 (null) explicitly tested via 4-condition ablation (Conditions A/B/C/D)
- Early-exit gate at H-M2 (|δ| diagnostic) saves compute if mechanism absent

Verification Execution Order:
- Phase 1 Foundation (Weeks 1-2): H-E1 → Gate 1 (SST-2 > 70%)
- Phase 2 Mechanism Step 1 (Weeks 3-4): H-M1 → Gate 2 (Condition A > zero-shot)
- Phase 2 Mechanism Step 2 (Week 5): H-M2 → Gate 3 (|δ| > 0.01)
- Phase 2 Mechanism Step 3 (Weeks 6-7): H-M3 → Gate 4 (GLUE avg D > A ≥1pp)

### Conclusions

Critical Decision Points:
1. Gate 1 (H-E1): MUST_WORK — if fails, stop; lm-eval-harness Mamba compat broken or projections don't transfer
2. Gate 2 (H-M1): MUST_WORK — if Condition A ≈ ceiling, projection LoRA is sufficient; explore whether state-aware helps generation (not classification)
3. Gate 3 (H-M2): MUST_WORK (early exit) — if |δ| < 0.01, HiPPO task-optimal; abandon H-M3; publish null
4. Gate 4 (H-M3): MUST_WORK — primary success gate; GLUE avg(D) > avg(A) ≥1pp, p < 0.05

Open Questions (from Phase 2A):
- Does lm-eval-harness support Mamba for LongBench generation? (verify pre-Phase 4)
- Is dt_proj LoRA (Condition B) empirically redundant with A_log bias (Condition C)? (Phase 4 answers)
- Is Mamba-2 checkpoint available at 130m/370m scale? (check before Phase 4)
- What is optimal LoRA rank for Mamba projection layers? (ablate r=4,8,16 in H-M3)

Recommendations:
1. Immediate: Run Mamba-130m import test + lm-eval-harness smoke test before Phase 2C design
2. Resource: Allocate 6 weeks for full critical path; reserve 1 week buffer for H-M3 compute
3. Failure management: Log δ magnitudes each epoch (H-M2 early warning); if δ stagnates at <0.01 after epoch 1, stop H-M2 training early

### Appendices

A. Phase 2A Reference
- Source: docs/youra_research/03_refinement.yaml (H-SA-LoRA-v1)
- Discussion: 7 exchanges, 6 agents, all convergence criteria met at Exchange 7

B. Scope Reduction Summary
- BUILD_ON (3 claims, skipped): LoRA architecture-agnosticism, A_log stability, Mamba-2 IA³ overhead
- PROVE_NEW (2 claims, verified here): non-redundancy, state-aware > projection-only

C. MCP Usage
- MCP calls made: 0 (ablation mode — no MCP services available)
- Scientific method reasoning performed inline

---

## 10. Finalization Status

- verification_state.yaml: Restated in ```state block (ABLATION MODE — no file write)
- Pipeline tasks: Skipped (Archon MCP unavailable in ablation session)
- Hypothesis tasks: Skipped (Archon MCP unavailable in ablation session)
- Output file: COMPLETE (all placeholders filled)
- Phase 2B: COMPLETE — ready for Phase 2C
