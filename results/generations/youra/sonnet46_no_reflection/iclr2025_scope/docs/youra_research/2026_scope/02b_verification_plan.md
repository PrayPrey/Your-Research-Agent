---
stepsCompleted: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
status: complete
completedAt: "2026-05-20"
hypothesis_id: "H-JointLoRAKV-v1"
research_scope_mode: "incremental"
pipeline_project_id: "febb001c-d193-48b2-a83e-f95c7e40af2f"
phase2b_task_id: "32ef89f5-6e69-4766-aa9a-1e2c6c10dd8f"
phase2c_task_id: "a60aa522-e7c5-458a-ae68-e228d7f8a963"
---

# Verification Plan: JointLoRA-KV — Task-Aware Joint Training of LoRA Adapters and KV Eviction Heads

**Date:** 2026-05-20
**Hypothesis ID:** H-JointLoRAKV-v1
**Confidence:** 0.75
**Total Hypotheses:** 5 (H-E1, H-M1, H-M2, H-M3, H-M4)

---

## 0. Established Facts & Scope Reduction

### 0.1 Established Facts Registry (BUILD_ON — Do NOT Re-Verify)

| # | Claim | Evidence |
|---|-------|----------|
| EF1 | LoRA effectively fine-tunes LLMs with <1% parameter overhead via A·B matrix injection into Q/K/V projections | Hu et al. 2021; HuggingFace PEFT; QLoRA (Dettmers et al. 2023) |
| EF2 | KV cache compression (eviction/quantization) can reduce memory footprint by 50–80% with manageable accuracy loss | Locret [Huang et al. 2024] 20x compression; kvpress (NVIDIA ★1025); ZSMerge 20:1 |
| EF3 | Soft-to-hard training (differentiable scoring during training, hard selection at inference) is an established pattern for learned sparse methods | Locret soft scoring; PruLong [Princeton 2024] 0/1 attention masks |
| EF4 | arXiv 2604.21335 demonstrates architectural feasibility of joint routed LoRA + KV value-group routing | arXiv 2604.21335 (2025): sub-token routing combining LoRA paths and KV value groups |

### 0.2 PROVE_NEW Claims (Phase 2B Hypothesis Targets)

| # | Claim | Verification |
|---|-------|-------------|
| PN1 | Task-specific gradient signals differ from LM loss in eviction priorities | P3 attribution analysis (Spearman ρ) |
| PN2 | Joint end-to-end training outperforms sequential training on GLUE + LongBench-QA | P1 + P2 benchmark experiments |
| PN3 | Joint training induces "representation compression" in eviction-surviving KV entries | P4 linear probing experiment |

**Scope Reduction:** 43% (4 BUILD_ON claims excluded from Phase 2B hypothesis generation)

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under standard PEFT fine-tuning conditions on transformer-based LLMs with KV cache (specifically LLaMA-3.1-8B), with a fixed 50% KV retention budget, if LoRA adapter weights and KV eviction head weights (Locret retaining heads) are jointly trained end-to-end via a task classification loss using soft scoring during training and hard eviction at inference (JointLoRA-KV), then JointLoRA-KV will achieve ≥3% higher accuracy than the sequential baseline (B3: LoRA → Locret sequential fine-tune) on LongBench-QA tasks and ≥1% higher on GLUE (MNLI, SST-2, QNLI) at the same 50% KV budget, because task-specific gradient signals direct eviction toward discriminatively relevant tokens rather than merely high-attention-score tokens, and joint training allows the LoRA adapter itself to learn representations that concentrate task-discriminative information into eviction-surviving KV entries ("representation compression").

### 1.2 Alternative Hypothesis (H0)

There is no statistically significant difference in GLUE or LongBench-QA accuracy between JointLoRA-KV and the sequential fine-tuning baseline (B3: LoRA → Locret sequential fine-tune) at matched 50% KV budget, when tested across 3 seeds on LLaMA-3.1-8B. Formally: H0: μ(JointLoRA-KV) − μ(B3) = 0 on both GLUE and LongBench-QA accuracy metrics.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | GLUE Benchmark + LongBench (standard) | GLUE (MNLI, SST-2, QNLI) for short-context classification with well-defined discriminative tokens; LongBench-QA (NarrativeQA, Qasper, MultiFieldQA) for long-context QA where KV compression is meaningfully activated — P1 primary test |
| **Model** | LLaMA-3.1-8B | Most widely benchmarked open-weight model for PEFT research; Locret and kvpress tested on LLaMA family; LoRA injection via HuggingFace PEFT fully supported; tractable for single-GPU fine-tuning |

**Dataset Details:**
- Source: HuggingFace datasets (GLUE); LongBench public GitHub repository
- Path: `glue` (HuggingFace), https://github.com/THUDM/LongBench

**Model Details:**
- Type: Decoder-only transformer LLM with KV cache
- Source: meta-llama/Meta-Llama-3.1-8B on HuggingFace Model Hub

### 1.4 Baseline Methods

| Method | Expected Performance | Dataset |
|--------|---------------------|---------|
| B1: LoRA + frozen Locret (no eviction training) | Below vanilla LoRA; heuristic eviction misaligned with task-adapted attention | GLUE + LongBench |
| B2: LoRA + kvpress (heuristic eviction) | Below B3; no learned eviction | GLUE + LongBench |
| B3: LoRA → sequential Locret fine-tune (hardest baseline) | ~1–2% below vanilla LoRA on GLUE; ~3–5% below on LongBench at 50% KV budget | GLUE + LongBench |
| Vanilla LoRA (100% KV budget) | Reference ceiling; no eviction overhead | GLUE boundary condition |

**Best Baseline Performance:** B3 (sequential LoRA→Locret fine-tune): estimated ~1–2% below vanilla LoRA on GLUE, ~3–5% below on LongBench at 50% KV budget.

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Task-discriminative tokens are NOT consistently among highest-attention-score tokens in LoRA-fine-tuned LLMs | arXiv 2604.21335 shows routing signal differs from raw attention; task-relevant tokens are semantically dense but not always high-frequency | Existing eviction heuristics already handle task alignment — joint training provides no signal. P3 directly tests this. |
| A2 | Locret's soft scoring mechanism can accept task classification loss without architectural changes | Locret retaining heads are simple linear networks over KV representations; distillation loss is a training choice, not architectural requirement | Locret heads require architectural redesign; implementation more complex than assumed |
| A3 | Gradient paths for LoRA and Locret retaining head parameters are sufficiently independent (no harmful interference) | Prof. Pax verified: LoRA A/B matrices (Q/K/V projections) and Locret head parameters (linear over KV) are disjoint; both update via frozen base model through separate hooks | Training instability or worse-than-independent performance; detectable and addressable via gradient scaling or separate LRs |
| A4 | Representation compression effect is strong enough to produce ≥3% LongBench-QA improvement over B3 | Knowledge distillation literature: budget-aware training produces qualitatively different representations; QLoRA analogy (joint compression+LoRA beats sequential) | Effect size <3% on LongBench-QA: P1 falsified but still partially supported; 3% threshold may need revision |
| A5 | LLaMA-3.1-8B on GLUE/LongBench is representative — results generalize to Mistral, Qwen etc. | LLaMA-3.1-8B is most widely benchmarked open-weight model in PEFT literature; Locret and kvpress tested on it; GLUE and LongBench are community standards | Results may be model-specific; multi-model validation needed — addressable in follow-up work |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First systematic evaluation of joint LoRA + KV eviction co-training on standard NLP benchmarks (GLUE + LongBench). First identification and empirical test of the "representation compression" effect: joint training causing LoRA to concentrate discriminative information in eviction-surviving KV entries.

**Key Innovation:** The core paradigm shift — efficiency-awareness during PEFT adaptation (joint training with KV budget constraint) changes WHAT the model learns, not just HOW it compresses. This moves the field from "efficiency as post-processing" to "efficiency as a training objective." The representation compression mechanism is the novel theoretical contribution; the GLUE/LongBench evaluation fills the benchmark gap left open by arXiv 2604.21335.

**Differentiation:**
- vs. arXiv 2604.21335: Task loss vs. LM loss; GLUE/LongBench vs. perplexity/RULER; token-level Locret heads vs. value-group routing; four-dimensional differentiation
- vs. Locret: Co-training vs. post-hoc application; task loss vs. distillation loss
- vs. Amazon ICR (EACL 2026): Jointly optimizes eviction policy during fine-tuning vs. tests robustness of fixed eviction
- vs. QLoRA: Analogical inspiration — joint compression+LoRA > sequential; we test for KV eviction (QLoRA does not address KV cache compression)

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | todo |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | todo |
| H-M2 | MECHANISM | MUST_WORK | H-E1 | todo |
| H-M3 | MECHANISM | MUST_WORK | H-M1, H-M2 | todo |
| H-M4 | MECHANISM | MUST_WORK | H-M3 | todo |

---

### 2.2 Hypothesis Specifications

---

**H-E1: Task-Attention / Eviction-Score Misalignment Exists**

**Statement**: Under LLaMA-3.1-8B fine-tuned with LoRA (r=16) on MNLI, if we compute Spearman ρ between LoRA-modified attention weights and Locret retaining head scores (LM-trained) across 100 MNLI validation examples, then mean ρ < 0.7, because task-adapted attention prioritizes discriminatively relevant tokens (hypothesis markers, contrast words) while LM-trained eviction heads prioritize high-frequency/local tokens.

**Rationale**: This is the existence precondition for the entire hypothesis chain. If misalignment is absent (ρ ≥ 0.7), existing eviction heuristics already align with task-relevant tokens and joint training provides no additional signal. P3 tests this cheaply using existing fine-tuned models with no new training required.

**Variables**:
- Independent: LoRA attention weights vs. Locret retaining head scores (both from existing models)
- Dependent: Spearman ρ (mean across 100 MNLI examples, all attention heads)
- Controlled: LLaMA-3.1-8B checkpoint, LoRA r=16, seed=42, 100 fixed validation examples

**Verification Protocol**:
1. Load existing LoRA-fine-tuned LLaMA-3.1-8B on MNLI from HuggingFace Model Hub.
2. Load Locret retaining heads (LM-distillation-trained) for same base model.
3. Extract per-token attention weights and retaining scores on 100 MNLI validation examples.
4. Compute Spearman ρ per example; report mean ± std; flag misaligned token types.
5. If borderline (0.65–0.75), extend to 500 examples and check SST-2, QNLI.

**Success Criteria**:
- Primary: Mean Spearman ρ < 0.7 across 100 MNLI examples
- Secondary: Misaligned tokens concentrated at hypothesis/contrast positions (qualitative)

**Failure Response**:
- IF ρ ≥ 0.7: PIVOT — re-examine A1; test whether task-loss gradient still differs from LM-loss gradient in a gradient attribution experiment before abandoning

**Dependencies**: None (pre-experiment diagnostic — run first before full training)

**Source**: Phase 2A Section 5 (SH1 Existence), Prediction P3, Causal Step 1

---

**H-M1: Task-Gradient Eviction Alignment — Classification Loss Rewrites Eviction Priorities**

**Statement**: Under LLaMA-3.1-8B PEFT fine-tuning on MNLI/SST-2/QNLI at 50% KV budget, if Locret retaining heads are trained via task classification cross-entropy loss (rather than LM distillation loss), then the resulting eviction policy retains tokens with higher MNLI/SST-2/QNLI label-relevant attribution scores than LM-trained eviction, because classification gradients reward token positions whose values discriminate between output classes rather than positions that predict the next token.

**Rationale**: This mechanism step establishes that task-loss training of Locret heads produces qualitatively different eviction policies than LM-loss training. It directly underpins why joint training should improve over B1 (frozen Locret) and B2 (heuristic eviction) baselines. Empirical evidence comes from the P1/P2 accuracy comparison and P3 attribution diagnostic.

**Variables**:
- Independent: Locret retaining head training loss (task classification CE vs. LM distillation)
- Dependent: GLUE accuracy at 50% KV budget (MNLI, SST-2, QNLI; mean across 3 seeds)
- Controlled: LLaMA-3.1-8B, LoRA r=16, budget_ratio=0.5, seeds 42/123/456

**Verification Protocol**:
1. Train B1 condition (LoRA + frozen Locret, no eviction training) as lower bound.
2. Train JointLoRA-KV with task CE loss directing Locret retaining heads.
3. Evaluate both on GLUE at budget_ratio=0.5; compute mean accuracy ± std across 3 seeds.
4. Compare JointLoRA-KV vs. B1: expect JointLoRA-KV > B1 on GLUE by ≥2%.
5. Also compare vs. B2 (kvpress heuristic) to confirm learned > heuristic eviction.

**Success Criteria**:
- Primary: JointLoRA-KV GLUE accuracy ≥ B1 + 2% at 50% KV budget
- Secondary: JointLoRA-KV ≥ B2 on GLUE (learned eviction beats heuristic)

**Failure Response**:
- IF JointLoRA-KV ≤ B1: EXPLORE — check if GLUE short-context (≤512 tokens) produces minimal KV eviction events at 50% budget; supplement with LongBench-QA results

**Dependencies**: H-E1 (existence precondition confirmed)

**Source**: Phase 2A Causal Step 2, Key Assumption A1, Prediction P2

---

**H-M2: Joint Gradient Flow Feasibility — Single-Backward-Pass Co-Optimization**

**Statement**: Under LLaMA-3.1-8B PEFT fine-tuning with LoRA (r=16) and Locret retaining heads in a shared AdamW optimizer, if both parameter sets receive gradients from the same task classification loss in a single backward pass (JointLoRA-KV), then training converges stably (no loss divergence or NaN) and achieves ≥ B3 accuracy on LongBench-QA at 50% KV budget, because LoRA A/B matrices and Locret retaining head weights are disjoint parameter sets whose independent gradient paths do not interfere.

**Rationale**: This hypothesis validates the technical feasibility of joint optimization — the prerequisite for H-M3 and H-M4. Gradient interference between LoRA and Locret heads would manifest as training instability detectable before full evaluation. Prof. Pax confirmed parameter disjointness at design time; empirical validation is still required.

**Variables**:
- Independent: Joint vs. sequential parameter optimization (shared optimizer vs. staged training)
- Dependent: Training stability (loss convergence, no divergence), LongBench-QA accuracy vs. B3
- Controlled: LLaMA-3.1-8B, LoRA r=16, seeds 42/123/456, budget_ratio=0.5, same GLUE training data

**Verification Protocol**:
1. Implement JointLoRA-KV with shared AdamW optimizer over LoRA and Locret parameters.
2. Monitor training loss curves for both parameter groups across all 3 seeds.
3. Flag divergence (loss spike >2x baseline) or NaN as gradient interference signal.
4. Evaluate final model on LongBench-QA at 50% budget; compare to B3.
5. If unstable: apply separate learning rates (LoRA LR vs. Locret head LR) as mitigation.

**Success Criteria**:
- Primary: Training converges for all 3 seeds (no loss divergence or NaN)
- Secondary: JointLoRA-KV LongBench-QA accuracy ≥ B3 (at minimum matches sequential)

**Failure Response**:
- IF training unstable: EXPLORE — try gradient clipping, separate LRs (1e-4 LoRA / 1e-3 Locret), or GradNorm balancing before abandoning

**Dependencies**: H-E1

**Source**: Phase 2A Causal Step 3, Key Assumption A3, Prediction P1

---

**H-M3: Joint Training Outperforms Sequential Baseline — LongBench-QA Primary Benchmark**

**Statement**: Under LLaMA-3.1-8B with LoRA (r=16) and Locret retaining heads at 50% KV budget, if joint end-to-end training (JointLoRA-KV) is compared to the strongest sequential baseline (B3: LoRA → Locret sequential fine-tune with frozen LoRA), then JointLoRA-KV achieves ≥3% higher accuracy on LongBench-QA (NarrativeQA, Qasper, MultiFieldQA) and ≥1% higher on GLUE at the same budget, because synchronized optimization of both components toward the task objective produces better task-eviction alignment than B3's decoupled training where LoRA representations are fixed before Locret adaptation.

**Rationale**: This is the primary benchmark hypothesis (P1) — the main empirical claim of the paper. B3 is the hardest baseline because Locret can adapt rapidly to LoRA-modified representations in <1 GPU hour; the 3% LongBench-QA threshold reflects the expected advantage from joint gradient flow that B3 cannot replicate. Both P1 and P2 success are required for the main hypothesis to be SUPPORTED.

**Variables**:
- Independent: JointLoRA-KV vs. B3 (sequential) training strategy
- Dependent: LongBench-QA accuracy (primary, F1/accuracy on NarrativeQA/Qasper/MultiFieldQA); GLUE accuracy (secondary)
- Controlled: LLaMA-3.1-8B, LoRA r=16, budget_ratio=0.5, seeds 42/123/456, same GLUE training splits

**Verification Protocol**:
1. Train JointLoRA-KV and B3 on full GLUE training splits with LLaMA-3.1-8B (3 seeds each).
2. Evaluate both on LongBench-QA test sets at budget_ratio=0.5; report mean F1/accuracy ± std.
3. Evaluate both on GLUE test sets at budget_ratio=0.5; report mean accuracy ± std.
4. Compute 95% CIs via bootstrap; run two-tailed t-test for JointLoRA-KV vs. B3.
5. Report effect size (Cohen's d) and whether CIs overlap as primary statistical evidence.

**Success Criteria**:
- Primary: JointLoRA-KV LongBench-QA mean accuracy ≥ B3 + 3.0 pp (p < 0.05, non-overlapping 95% CIs)
- Secondary: JointLoRA-KV GLUE mean accuracy ≥ B3 + 1.0 pp at 50% budget

**Failure Response**:
- IF 1% ≤ gap < 3% on LongBench-QA: EXPLORE — report partial support; analyze per-task breakdown (NarrativeQA vs. Qasper vs. MultiFieldQA); revise threshold if B3 rapid adaptation stronger than expected
- IF gap < 1%: PIVOT — re-examine mechanism via H-M4 probing; consider whether representation compression is too weak

**Dependencies**: H-M1, H-M2

**Source**: Phase 2A Causal Step 4, Key Assumption A4, Predictions P1+P2

---

**H-M4: Representation Compression — Joint Training Changes What LoRA Learns**

**Statement**: Under LLaMA-3.1-8B trained with JointLoRA-KV vs. B3 (sequential), if we extract KV representations at the median transformer layer and split by Locret retention scores into top-50% (retained) and bottom-50% (evicted), then a linear classifier trained on the retained-KV representations achieves ≥5% higher MNLI probing accuracy for JointLoRA-KV vs. B3, because joint training with KV budget awareness causes LoRA adapters to concentrate task-discriminative information into eviction-surviving entries — an effect not achievable when LoRA is frozen during Locret training (B3).

**Rationale**: This mechanistic hypothesis distinguishes JointLoRA-KV from B3 at the representation level, not just the accuracy level. It provides the theoretical contribution: joint training changes WHAT LoRA learns, not just how compression is applied. Confirmation of H-M4 supports the "representation compression" paradigm shift claim. This is the lowest-confidence hypothesis (0.65) because the effect may be too subtle for linear probing to detect.

**Variables**:
- Independent: JointLoRA-KV vs. B3 training paradigm
- Dependent: Linear probing accuracy on top-50% retained KV representations (MNLI label prediction at layer 16)
- Controlled: Layer 16 (median, 32-layer model), budget_ratio=0.5, same 200 MNLI examples, logistic regression C=1.0, L2-normalized KV representations

**Verification Protocol**:
1. Freeze JointLoRA-KV and B3 models post-training; forward-pass 200 MNLI validation examples.
2. Extract KV representations at layer 16; apply Locret scores to split retained vs. evicted.
3. Train logistic regression on retained-KV features for MNLI label prediction (80/20 train/val split).
4. Compare probing accuracy JointLoRA-KV vs. B3; compute delta with 95% bootstrap CI.
5. Control check: probe evicted-KV entries — expect JointLoRA-KV evicted accuracy < B3 evicted (complementary).

**Success Criteria**:
- Primary: JointLoRA-KV retained-KV probing accuracy ≥ B3 + 5 pp (bootstrap 95% CI excludes 0)
- Secondary: JointLoRA-KV evicted-KV probing accuracy < B3 evicted-KV (complementary information redistribution)

**Failure Response**:
- IF delta < 5 pp: EXPLORE — run sensitivity analysis across layers 8, 16, 24; extend to SST-2 probing; report as suggestive if trend consistent even if below threshold

**Dependencies**: H-M3

**Source**: Phase 2A Causal Step 4, Key Assumption A4, Prediction P4, Section 3 (Novelty)

---

## 3. Risk Analysis

### 3.1 Risk Register

| ID | Risk Title | Source Assumption | Severity | Likelihood | Impact |
|----|-----------|------------------|----------|------------|--------|
| R1 | Task-attention / eviction alignment absent | A1 | CRITICAL | Medium | All hypotheses fail |
| R2 | Locret code incompatible with task CE loss | A2 | HIGH | Low-Medium | H-M1, H-M2, H-M3 |
| R3 | Gradient interference — joint training instability | A3 | HIGH | Low-Medium | H-M2, H-M3 |
| R4 | 3% LongBench-QA threshold too optimistic | A4 | HIGH | Medium-High | H-M3 |
| R5 | GLUE short-context minimal KV eviction events | A5 | MEDIUM | Medium | H-M1, H-M3 (P2) |
| R6 | Linear probing insensitive to compression effect | (additional) | MEDIUM | Medium | H-M4 |

### 3.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: Alignment absent (ρ ≥ 0.7) | A1 | H-E1, H-M1, H-M2, H-M3, H-M4 (all) | CRITICAL |
| R2: Locret code incompatibility | A2 | H-M1, H-M2, H-M3 | HIGH |
| R3: Gradient interference | A3 | H-M2, H-M3 | HIGH |
| R4: Effect size below 3% threshold | A4 | H-M3 (P1 primary) | HIGH |
| R5: GLUE eviction minimal | A5 | H-M1, H-M3 (P2 secondary) | MEDIUM |
| R6: Linear probe insensitivity | (additional) | H-M4 | MEDIUM |

### 3.3 Mitigation Strategies

**Risk R1: Task-Attention / Eviction Alignment Absent**

**Source Assumption:** A1 — Task-discriminative tokens are NOT consistently among highest-attention-score tokens in LoRA-fine-tuned LLMs

**Description:** If MNLI hypothesis markers and SST-2 sentiment anchors coincidentally have high attention scores after LoRA fine-tuning, Spearman ρ ≥ 0.7 and the mechanism precondition (H-E1) fails — collapsing the entire hypothesis chain.

**Affected Hypotheses:** H-E1, H-M1, H-M2, H-M3, H-M4

**Severity:** CRITICAL

**Mitigation Strategy:**
1. **Prevention:** Execute P3 attribution diagnostic (H-E1) as the first experiment — before any GPU-intensive training. This is a cheap (<1 hour) pre-registration check.
2. **Detection:** Monitor Spearman ρ distribution across 100 examples; flag if mean ρ > 0.65 as early warning.
3. **Response:**
   - If borderline (0.65–0.75): Extend to 500 examples; add SST-2 and QNLI attribution checks; if ρ < 0.7 confirmed on full set, proceed.
   - PIVOT: If ρ ≥ 0.7 on MNLI but < 0.7 on long-context sequences (NarrativeQA), reframe H-E1 as long-context-specific phenomenon and shift primary evaluation to LongBench-QA only.
   - ABORT: If ρ ≥ 0.7 across all tasks and context lengths — mechanism precondition absent; revisit main hypothesis before committing to full training.

**Early Warning Indicators:**
- Mean ρ > 0.65 on first 50 MNLI examples
- Task-relevant token types (hypothesis markers, contrast words) consistently ranking in top-30% by attention score

---

**Risk R2: Locret Code Incompatible with Task CE Loss**

**Source Assumption:** A2 — Locret's soft scoring mechanism can accept task classification loss without architectural changes

**Description:** Locret retaining heads may be architecturally coupled to the distillation loss (e.g., the scoring network expects full-context KV distributions as targets), making it non-trivial to substitute task CE loss without code-level redesign.

**Affected Hypotheses:** H-M1, H-M2, H-M3

**Severity:** HIGH

**Mitigation Strategy:**
1. **Prevention:** Inspect Locret public codebase (github.com/huangyuxiang03/Locret) during Phase 3 planning to identify coupling points before implementation.
2. **Detection:** Implementation fails or requires >3 days of refactoring to substitute CE loss.
3. **Response:**
   - PIVOT: Replace Locret retaining heads with lightweight 2-layer MLP scorer trained from scratch using task CE loss — same soft-to-hard training pattern, simpler architecture.
   - SCOPE: If MLP scorer cannot match Locret's efficiency, narrow evaluation to MNLI only (single task) to reduce implementation complexity.

**Early Warning Indicators:**
- Locret training loop directly computes distillation targets from teacher attention (hard to replace)
- Retaining head scoring function requires KV distributions not available during CE loss computation

---

**Risk R3: Gradient Interference — Joint Training Instability**

**Source Assumption:** A3 — Gradient paths for LoRA and Locret retaining head parameters are sufficiently independent

**Description:** Even though LoRA A/B matrices and Locret head weights are disjoint parameter sets, shared optimizer dynamics (momentum, adaptive LR) with mismatched gradient scales may cause training instability: loss spikes, NaN gradients, or oscillation between the two parameter groups.

**Affected Hypotheses:** H-M2, H-M3

**Severity:** HIGH

**Mitigation Strategy:**
1. **Prevention:** Use separate parameter groups in AdamW with different learning rates: LoRA LR = 1e-4, Locret head LR = 5e-4; apply gradient clipping (max_norm=1.0) from epoch 1.
2. **Detection:** Monitor per-group gradient norm ratio each step; flag if ratio > 10x as interference signal.
3. **Response:**
   - PIVOT: Apply GradNorm balancing to equalize gradient magnitudes across parameter groups.
   - SCOPE: If interference persists, use alternating mini-batch training (LoRA step → Locret step) rather than simultaneous backward pass.
   - ABORT: If loss diverges after 3 hyperparameter configurations — report instability as a negative finding; document conditions under which joint training fails.

**Early Warning Indicators:**
- Training loss spike > 2× baseline within first 100 steps
- Per-group gradient norm ratio (Locret / LoRA) > 10 sustained for > 50 steps
- NaN in any parameter group gradient

---

**Risk R4: 3% LongBench-QA Threshold Too Optimistic**

**Source Assumption:** A4 — Representation compression effect is strong enough to produce ≥3% LongBench-QA improvement over B3

**Description:** B3 (sequential LoRA→Locret fine-tune) is a strong baseline because Locret heads can rapidly adapt to LoRA-modified representations in <1 GPU hour. The actual effect size may be 1–2% — real and publishable but technically failing P1's pre-registered 3% threshold.

**Affected Hypotheses:** H-M3

**Severity:** HIGH

**Mitigation Strategy:**
1. **Prevention:** Pre-register the partial support interpretation (1–3% range = partial support, <1% = falsification) in the experiment protocol before running training.
2. **Detection:** Monitor validation accuracy gap (JointLoRA-KV vs. B3) after each epoch; project final gap at epoch 3.
3. **Response:**
   - EXPLORE: Report per-task breakdown (NarrativeQA, Qasper, MultiFieldQA separately) — expect strongest effects on longer-context subtasks (MultiFieldQA, Qasper) where KV compression matters most.
   - PIVOT: If overall gap is 1–2%, reframe as "consistent improvement across long-context tasks" rather than relying on absolute threshold; use confidence intervals as primary evidence.
   - SCOPE: Reduce LongBench evaluation to the two longest-context subtasks (Qasper + MultiFieldQA) where 50% KV eviction is most impactful.

**Early Warning Indicators:**
- After epoch 1: JointLoRA-KV validation gap vs. B3 < 0.5% on LongBench (insufficient trajectory)
- B3 converges faster than expected (< 30 min for Locret head adaptation)

---

**Risk R5: GLUE Short-Context Minimal KV Eviction Events**

**Source Assumption:** A5 — Results on LLaMA-3.1-8B GLUE/LongBench are representative

**Description:** GLUE sequences are ≤512 tokens; at 50% KV budget, the eviction mechanism may rarely activate because the KV cache never fills to the budget threshold on such short inputs. This would make P2 (GLUE ≥1% over B3) undetectable even if the mechanism is valid.

**Affected Hypotheses:** H-M1, H-M3 (P2 secondary claim)

**Severity:** MEDIUM

**Mitigation Strategy:**
1. **Prevention:** Before training, verify KV eviction activation rate on 100 GLUE validation examples at budget_ratio=0.5; compute fraction of tokens actually evicted.
2. **Detection:** If >80% of GLUE examples have all KV entries retained (eviction inactive), P2 will be null.
3. **Response:**
   - PIVOT: If GLUE eviction rarely activates, remove P2 as a primary claim; demote to "boundary condition check" only.
   - SCOPE: Focus all primary evaluation on LongBench-QA (P1) where KV compression is meaningfully activated; report GLUE results as supplementary.

**Early Warning Indicators:**
- GLUE sequence length distribution mostly < 256 tokens
- budget_ratio=0.5 results in < 10% tokens actually evicted on GLUE inputs

---

**Risk R6: Linear Probing Insensitive to Representation Compression**

**Source Assumption:** (Additional — not in A1-A5) Linear probing adequately measures information concentration in KV representations

**Description:** The P4 probing experiment uses logistic regression on KV representations. If the representation compression effect exists but is expressed through complex non-linear feature combinations, logistic regression will miss it and H-M4 will appear to fail even if the underlying effect is real.

**Affected Hypotheses:** H-M4

**Severity:** MEDIUM

**Mitigation Strategy:**
1. **Prevention:** Include a 2-layer MLP probe as a parallel baseline alongside logistic regression from the start.
2. **Detection:** Large gap between MLP probe accuracy and logistic regression accuracy on the same KV representations indicates non-linear structure.
3. **Response:**
   - EXPLORE: Run probing across layers 8, 16, 24 to check if compression is layer-specific; report mutual information (MI) between retained-KV and MNLI labels as theory-grounded supplementary measure.
   - SCOPE: If neither probe detects >5% delta, report H-M4 as non-confirmed and frame representation compression as a theoretical prediction requiring future probing methodology development.

**Early Warning Indicators:**
- MLP probe accuracy on retained KV >> logistic regression accuracy (>5% gap) — indicates non-linear structure
- Both probes show near-random accuracy on retained KV entries for both JointLoRA-KV and B3

### 3.4 Risk Summary

| ID | Risk | Source | Severity | Affected Hypotheses | Mitigation |
|----|------|--------|----------|---------------------|------------|
| R1 | Task-attention/eviction alignment absent (ρ ≥ 0.7) | A1 | **CRITICAL** | All (H-E1, H-M1–4) | Run P3 diagnostic first; extend to 500 examples if borderline |
| R2 | Locret code incompatible with task CE loss | A2 | **HIGH** | H-M1, H-M2, H-M3 | Inspect code Week 1; fallback: 2-layer MLP scorer |
| R3 | Gradient interference / training instability | A3 | **HIGH** | H-M2, H-M3 | Separate LRs; GradNorm; early abort conditions |
| R4 | 3% LongBench-QA threshold too optimistic | A4 | **HIGH** | H-M3 | Pre-register partial support (1–3%); subtask breakdown |
| R5 | GLUE eviction inactive at short context | A5 | **MEDIUM** | H-M1, H-M3 (P2) | Verify activation rate; demote GLUE to supplementary if inactive |
| R6 | Linear probe insensitive to compression | (additional) | **MEDIUM** | H-M4 | Add MLP probe; cross-layer analysis; MI supplementary |

**Critical Risks:** 1 (R1)
**High Risks:** 3 (R2, R3, R4)
**Medium Risks:** 2 (R5, R6)
**Low Risks:** 0

---

## 4. Execution

### 4.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) — 5 Hypotheses, Sequential Chain
═══════════════════════════════════════════════════════════════════════

[Phase 1 — Foundation: Existence Precondition]

    ┌─────────────────────────────────────────────┐
    │  H-E1: Task-Attention/Eviction Misalignment │  ← GATE 1 (MUST_WORK)
    │  Spearman ρ < 0.7 on MNLI (P3 diagnostic)  │  Run FIRST, no training needed
    └─────────────────────┬───────────────────────┘
                          │  PASS → proceed
                          │  FAIL → STOP, reassess entire hypothesis
                          ▼

[Phase 2 — Core Mechanisms: Causal Chain Steps 2–4]

    ┌─────────────────────────────────────────────┐
    │  H-M1: Task Gradient Rewrites Eviction      │  ← GATE 2a (MUST_WORK)
    │  JointLoRA-KV > B1/B2 on GLUE+LongBench    │  Prerequisites: H-E1
    └─────────────────────┬───────────────────────┘
                          │  PASS → proceed
                          │  FAIL → EXPLORE (check GLUE eviction activation)
                          ▼
    ┌─────────────────────────────────────────────┐
    │  H-M2: Joint Gradient Flow Feasible         │  ← GATE 2b (MUST_WORK)
    │  Training converges stably, ≥ B3 accuracy   │  Prerequisites: H-E1
    └─────────────────────┬───────────────────────┘
                          │  PASS → proceed
                          │  FAIL → PIVOT (separate LRs / GradNorm)
                          ▼
    ┌─────────────────────────────────────────────┐
    │  H-M3: Joint > Sequential (Primary Bench.)  │  ← GATE 2c (MUST_WORK)
    │  LongBench-QA ≥ B3 + 3% (P1), GLUE ≥ B3+1%│  Prerequisites: H-M1, H-M2
    └─────────────────────┬───────────────────────┘
                          │  PASS → confirmed core hypothesis
                          │  PARTIAL (1–3%) → report partial support
                          │  FAIL → revisit A4, check H-M4 for mechanism insight
                          ▼
    ┌─────────────────────────────────────────────┐
    │  H-M4: Representation Compression Effect    │  ← GATE 2d (SHOULD_WORK)
    │  Probing accuracy retained-KV ≥ B3 + 5 pp  │  Prerequisites: H-M3
    └─────────────────────┬───────────────────────┘
                          │  PASS → mechanistic contribution confirmed
                          │  FAIL → EXPLORE (cross-layer, MLP probe, MI)
                          ▼

[Terminal: Phase 5 Baseline Comparison — DEFERRED]
    (skip_baseline_comparison=true in module.yaml)
    → Proceed directly to Phase 2C Experiment Design

═══════════════════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
No parallelization opportunities (pure sequential chain)
═══════════════════════════════════════════════════════════════════════
```

### 4.2 Dependency Hierarchy

**Dependency Analysis:**
- H-E1 → [] (root, no prerequisites — run first as cheap diagnostic)
- H-M1 → [H-E1] (task gradient mechanism requires existence confirmed)
- H-M2 → [H-E1] (feasibility test requires existence confirmed; runs in parallel with H-M1 logically, but same training run)
- H-M3 → [H-M1, H-M2] (primary benchmark requires mechanism feasibility)
- H-M4 → [H-M3] (probing requires trained JointLoRA-KV and B3 models)

**No circular dependencies detected. ✓**

**Dependency Hierarchy Table:**

| Level | Hypothesis | Type | Prerequisites | Gate Type | Fail Action |
|-------|-----------|------|---------------|-----------|-------------|
| 0 | H-E1 | EXISTENCE | None | MUST_WORK | STOP — reassess mechanism |
| 1 | H-M1 | MECHANISM | H-E1 | MUST_WORK | EXPLORE — GLUE eviction check |
| 1 | H-M2 | MECHANISM | H-E1 | MUST_WORK | PIVOT — separate LRs / GradNorm |
| 2 | H-M3 | MECHANISM | H-M1, H-M2 | MUST_WORK | PARTIAL OK if 1–3%; PIVOT if <1% |
| 3 | H-M4 | MECHANISM | H-M3 | SHOULD_WORK | EXPLORE — MLP probe, cross-layer |

**Verification Phases:**

**Phase 1 — Foundation (H-E1):** Pre-training attribution diagnostic. No GPU-intensive compute. Gate 1: if ρ ≥ 0.7 across all tasks, stop and reassess. ~2 hours.

**Phase 2 — Mechanism Validation (H-M1, H-M2, H-M3):** Full training and benchmark evaluation. H-M1 and H-M2 are validated within the same training run as JointLoRA-KV. H-M3 is the primary benchmark comparison (P1+P2). Gate 2: H-M3 must show ≥1% LongBench-QA improvement (partial support threshold). ~3–5 GPU days.

**Phase 3 — Mechanistic Confirmation (H-M4):** Probing experiment on frozen trained models. Gate 3: H-M4 should show ≥5 pp probing delta; failure narrows but does not invalidate the overall contribution. ~4–8 hours.

### 4.3 Timeline (Gantt)

```
═══════════════════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE — 5 Hypotheses | Total: 6 Weeks
═══════════════════════════════════════════════════════════════════════════════════
Phase / Hypothesis    │ W1-2         │ W3-4         │ W5           │ W6
──────────────────────┼──────────────┼──────────────┼──────────────┼──────────────
PHASE 1: Foundation
  H-E1 (P3 diagnostic)│ ████████████ │              │              │
  [Gate 1: ρ < 0.7?]  │         ◆   │              │              │
──────────────────────┼──────────────┼──────────────┼──────────────┼──────────────
PHASE 2: Mechanisms
  H-M1 (Task gradient)│              │ ████████████ │              │
  H-M2 (Joint feasib.)│              │ ████████████ │              │
  [Gate 2a: converges?]│             │          ◆  │              │
  H-M3 (Benchmark)    │              │              │ ████████████ │
  [Gate 2b: ≥1% LB?]  │              │              │         ◆   │
──────────────────────┼──────────────┼──────────────┼──────────────┼──────────────
PHASE 3: Mechanistic
  H-M4 (Repr. compr.) │              │              │              │ ████████████
  [Gate 3: ≥5pp probe?]│             │              │              │         ◆
──────────────────────┼──────────────┼──────────────┼──────────────┼──────────────
═══════════════════════════════════════════════════════════════════════════════════
Legend: ████ = Active work  |  ◆ = Gate decision point
Note: H-M1 and H-M2 verified within same training run (W3-4); H-M3 = evaluation phase
Total Duration: 6 weeks  |  Critical Path: H-E1 → H-M1/M2 → H-M3 → H-M4
═══════════════════════════════════════════════════════════════════════════════════
```

### 4.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1/H-M2 → H-M3 → H-M4

Duration Breakdown:
  H-E1  (W1–W2): 2 weeks — attribution diagnostic, no training
  H-M1+H-M2 (W3–W4): 2 weeks — joint training run, stability + mechanism validation
  H-M3  (W5):   1 week  — benchmark evaluation (GLUE + LongBench inference)
  H-M4  (W6):   1 week  — probing experiment on frozen models

Total Duration: 6 weeks
  Formula: 2 (H-E1) + 4 (H-M1–4) + 0 (H-C) = 6 weeks
  H-M1 and H-M2 share the same training run → no extra week for H-M2

Slack Available: 0 weeks (pure sequential chain, no parallelization)

Gate Decision Points:
  ◆ Gate 1 (end W2): H-E1 ρ < 0.7? → PASS: proceed to H-M1/M2; FAIL: STOP/PIVOT
  ◆ Gate 2a (end W4): Training converges? → PASS: evaluate; FAIL: PIVOT (LR tuning)
  ◆ Gate 2b (end W5): LongBench-QA gap ≥ 1%? → PASS: H-M3 supported; PARTIAL: document
  ◆ Gate 3  (end W6): Probing delta ≥ 5pp? → PASS: H-M4 confirmed; FAIL: EXPLORE

Risk Buffer Recommendation: Add 1-week buffer after W4 if gradient interference detected
Adjusted Total with Buffer: 7 weeks (worst case)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4.5 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 5
  Existence: 1 (H-E1)
  Mechanism: 4 (H-M1, H-M2, H-M3, H-M4)
  Condition: 0 (none)

Verification Phases: 3
  Phase 1: Foundation (H-E1)         — 2 weeks
  Phase 2: Mechanism (H-M1–H-M3)     — 3 weeks
  Phase 3: Confirmation (H-M4)       — 1 week

Compute Resources:
  Phase 1 (H-E1):       CPU/small GPU, ~2h  — attribution diagnostic only
  Phase 2 (H-M1–M3):    Single A100/H100 GPU
    - Training (JointLoRA-KV + B1/B2/B3/vanilla): ~3 seeds × 5 conditions × ~4h = ~60 GPU hours
    - Evaluation (GLUE + LongBench): ~5 conditions × ~2h = ~10 GPU hours
  Phase 3 (H-M4):       CPU or small GPU, ~4–8h — probing on frozen models

Dataset Requirements:
  - GLUE (MNLI, SST-2, QNLI): HuggingFace datasets (existing)
  - LongBench (NarrativeQA, Qasper, MultiFieldQA): public GitHub (existing)
  - MNLI validation (100–200 examples): subset of GLUE (existing)

Model Requirements:
  - LLaMA-3.1-8B: meta-llama/Meta-Llama-3.1-8B (HuggingFace Hub)
  - Locret retaining heads: github.com/huangyuxiang03/Locret (public)

Total Duration: 6 weeks  |  Critical Path: 6 weeks  |  Execution: Sequential
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4.6 Execution Order

**Step 1 (W1–W2):** Execute H-E1 — Load existing LoRA-fine-tuned LLaMA-3.1-8B; compute Spearman ρ between LoRA attention weights and Locret retaining scores on 100 MNLI validation examples.

**Step 2 (end W2):** Evaluate Gate 1 — If ρ < 0.7: proceed to Step 3. If ρ ≥ 0.7: STOP, reassess mechanism assumption before committing to training.

**Step 3 (W3–W4):** Execute H-M1 + H-M2 — Implement JointLoRA-KV; train all 5 conditions (JointLoRA-KV, B1, B2, B3, vanilla LoRA) on GLUE with 3 seeds; monitor training stability (Gate 2a) and per-group gradient norms.

**Step 4 (end W4):** Evaluate Gate 2a — If training converges for all 3 seeds: proceed to Step 5. If instability: PIVOT (separate LRs / GradNorm) and add 1-week buffer.

**Step 5 (W5):** Execute H-M3 — Run inference at budget_ratio=0.5 on GLUE test sets and LongBench-QA test sets; compute accuracy/F1; report mean ± std; compute 95% CIs.

**Step 6 (end W5):** Evaluate Gate 2b — If LongBench-QA gap ≥ 3%: H-M3 SUPPORTED. If 1–3%: PARTIAL support, document subtask breakdown. If < 1%: revisit mechanism via H-M4 probing.

**Step 7 (W6):** Execute H-M4 — Freeze JointLoRA-KV and B3 models; extract KV representations at layer 16; split retained/evicted by Locret scores; train logistic regression probes; compare delta probing accuracy.

**Step 8 (end W6):** Evaluate Gate 3 — If delta ≥ 5pp: H-M4 CONFIRMED (representation compression mechanistic evidence). If < 5pp: EXPLORE (cross-layer, MLP probe). Compile all results for Phase 2C experiment design.

---

## 5. Dialectical Analysis

### 5.1 Thesis

**Core Claim:** Joint end-to-end training of LoRA adapter weights and KV eviction head weights (Locret retaining heads) via task classification loss (JointLoRA-KV) outperforms sequential decoupled training (B3) on both GLUE (≥1%) and LongBench-QA (≥3%) at fixed 50% KV retention budget on LLaMA-3.1-8B, because task-specific gradients align eviction with discriminatively relevant tokens and joint training induces representation compression in eviction-surviving KV entries.

**Supporting Evidence:**
1. LoRA-modified attention patterns are systematically misaligned with LM-loss-trained eviction heuristics for task-discriminative tokens (A1, to be verified by P3 diagnostic)
2. Task classification CE loss rewards retaining discriminatively relevant tokens that differ from tokens rewarded by next-token-prediction LM loss (Causal Step 2; functional distinction between classification and language modeling objectives)
3. LoRA A/B matrices and Locret retaining head weights are disjoint parameter sets enabling interference-free joint optimization (A3, Prof. Pax verified; established soft-to-hard training pattern in Locret + PruLong)
4. Budget-aware joint training causes LoRA to learn representation compression — concentrating task-discriminative info into eviction-surviving entries — not achievable when LoRA is frozen (B3) (Causal Step 4; knowledge distillation analogy)
5. QLoRA analogy: joint compression+adaptation consistently beats sequential decoupling in analogous settings

**Expected Outcomes:**
- Primary (P1): JointLoRA-KV ≥ B3 + 3% on LongBench-QA at 50% KV budget
- Secondary (P2): JointLoRA-KV ≥ B3 + 1% on GLUE; ±0.3% of vanilla LoRA at 100% budget
- Mechanistic (P3): Spearman ρ < 0.7 on MNLI attribution diagnostic
- Confirmatory (P4): Probing delta ≥ 5pp on retained-KV representations

**Confidence:** 0.72

### 5.2 Antithesis

**Null Hypothesis (H0):** There is no statistically significant difference in GLUE or LongBench-QA accuracy between JointLoRA-KV and B3 (sequential LoRA→Locret fine-tune) at matched 50% KV budget across 3 seeds on LLaMA-3.1-8B. H0: μ(JointLoRA-KV) − μ(B3) = 0.

**Counter-Arguments:**
1. **B3 rapid adaptation**: Locret retaining heads adapt rapidly to LoRA-modified representations in <1 GPU hour of sequential fine-tuning, potentially capturing most of the task-eviction alignment benefit without joint training (R4)
2. **Attention alignment pre-existing**: Task-discriminative tokens (MNLI hypothesis markers, SST-2 sentiment anchors) may coincidentally have high attention scores in LoRA-fine-tuned models, making heuristic eviction already task-aligned (R1/A1 violation)
3. **GLUE eviction inactive**: Short-context GLUE sequences (≤512 tokens) produce minimal KV eviction events at 50% budget, making any P2 advantage statistically undetectable (R5)
4. **Limited statistical power**: 3-seed evaluation with expected 1–3% effect sizes produces wide confidence intervals; apparent improvements may be within noise

**Conditions Under Which H0 Would Be Supported:**
- If Spearman ρ ≥ 0.7 on MNLI P3 diagnostic (mechanism precondition absent)
- If JointLoRA-KV LongBench-QA accuracy < B3 + 1% (effect too small to claim improvement)
- If training instability prevents JointLoRA-KV from converging stably (gradient interference)

**Antithesis Confidence:** 0.28 (lower confidence — antithesis has structural weaknesses: cannot explain why classification and LM gradients would produce identical eviction priorities, nor why QLoRA analogy fails in this setting)

### 5.3 Synthesis

**Resolution:** The dialectic between JointLoRA-KV and H0 is resolved by the P3 attribution diagnostic (H-E1): if ρ < 0.7 (mechanism precondition confirmed), the thesis holds; if ρ ≥ 0.7, the antithesis gains support and the mechanism should be reconsidered before committing to training.

**Resolution Path:**
1. **Foundation verification (H-E1/P3):** Cheap pre-registration test that gates the entire training pipeline — settles the thesis/antithesis disagreement about mechanism precondition existence before expensive GPU compute
2. **Sequential mechanism testing (H-M1–H-M4):** Tests the causal chain step-by-step; failures at each gate are informative rather than requiring complete experiment restart
3. **Pre-registered partial support:** 1–3% LongBench-QA gap = partial support (documented before experiment execution); <1% = falsification. Prevents post-hoc threshold revision.
4. **Two-regime evaluation:** GLUE + LongBench separation ensures short-context eviction concerns (antithesis R5) do not invalidate the primary long-context LongBench-QA contribution

**Conditions for Thesis Support:**
- H-E1: ρ < 0.7 (mechanism precondition)
- H-M2: Training converges stably
- H-M3: LongBench-QA gap ≥ 1% (partial) or ≥ 3% (full)

**Conditions for Antithesis Support:**
- H-E1: ρ ≥ 0.7 across all tasks/context lengths
- H-M3: Gap < 1% even on LongBench-QA
- Training instability despite separate LR mitigation

**Nuanced Outcome Possibilities:**
1. **Full Support** (gap ≥ 3% + H-M4 confirmed): Thesis fully validated — paradigm shift claim supported
2. **Partial Support** (gap 1–3%): Real but modest effect; representation compression mechanism may explain the ceiling; publishable with revised framing
3. **Mechanism-Only** (gap < 1% but H-M4 confirmed): Representation compression exists but does not translate to accuracy; theoretical contribution without empirical benchmark claim
4. **No Support** (H-E1 fails or gap < 1%): Antithesis supported; document conditions; null result is still a publishable benchmark contribution filling the gap left by arXiv 2604.21335

**Synthesis Confidence:** 0.78

### 5.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence (H-E1) | LoRA attention ≠ Locret eviction for task tokens | ρ ≥ 0.7: alignment already sufficient | P3 diagnostic (cheap, decisive pre-registration) |
| Mechanism (H-M1–M2) | Task CE loss rewrites eviction; joint flow feasible | B3 rapid adaptation captures same benefit | P1/P2 benchmark comparison + training stability monitoring |
| Primary Benchmark (H-M3) | ≥3% LongBench-QA over B3 | Effect ≤ 1% within noise | Pre-registered partial support (1–3%); subtask breakdown |
| Repr. Compression (H-M4) | LoRA learns qualitatively different representations | Compression too subtle for linear probing | MLP probe + cross-layer analysis as fallback |
| Generalizability | LLaMA-3.1-8B representative for PEFT research | Single model limits claims | Phase 6 discussion; future work scope |

**Overall Robustness Score:** **MEDIUM-HIGH**
- Strong: pre-registration design, multiple publishable outcomes, mechanistic depth via H-M4
- Moderate: 3% threshold uncertainty (R4), single-model scope (A5)

**Confidence in Verification Plan:** 0.75 (higher than hypothesis confidence 0.72 — the plan design is robust even if the hypothesis outcome is uncertain)

---

## 6. Executive Summary & Conclusions

### 6.1 Executive Summary

**Main Hypothesis:** JointLoRA-KV — jointly training LoRA adapters and KV eviction heads via task classification loss outperforms sequential fine-tuning (B3) on GLUE (≥1%) and LongBench-QA (≥3%) at 50% KV budget on LLaMA-3.1-8B.
- **ID:** H-JointLoRAKV-v1 | **Confidence:** 0.75 | **Mode:** Incremental (43% scope reduction from Phase 2A)

**Verification Structure:**
- **5 hypotheses:** H-E1 (existence) + H-M1–H-M4 (mechanism chain, 4 causal steps)
- **3 phases** over **6 weeks** | **4 gate decision points**
- **Critical first step:** H-E1 P3 attribution diagnostic (cheap, ~2h, pre-registers mechanism assumption)

**Risk Assessment:** MEDIUM-HIGH concern
- **Critical:** R1 — mechanism precondition absent (ρ ≥ 0.7); gates entire pipeline
- **High:** R4 — 3% threshold optimistic vs. B3 rapid adaptation; partial support (1–3%) pre-registered

**Immediate Action:** Run H-E1 (P3 diagnostic) before any GPU-intensive training

### 6.2 Final Summary

**Phase 2B Verification Plan for H-JointLoRAKV-v1 is complete.**

The plan decomposes the main hypothesis into 5 sub-hypotheses (H-E1, H-M1–H-M4) along the 4-step causal chain from Phase 2A. The verification follows a 6-week sequential pipeline gated at 4 decision points. The P3 attribution diagnostic (H-E1) is the mandatory first experiment — a cheap pre-registration check that validates the mechanism precondition before committing to ~70 GPU hours of training. Pre-registered partial support interpretation (1–3% LongBench-QA = partial, ≥3% = full) ensures multiple publishable outcomes. The representation compression mechanism (H-M4) provides mechanistic depth independent of benchmark accuracy thresholds.

### 6.3 Conclusions

**Key Achievements:**
- 5 hypothesis specifications with explicit verification protocols and success criteria
- 6 risks identified and mapped (1 critical, 3 high, 2 medium) with mitigation strategies
- DAG with 4 gate conditions and 6-week Gantt timeline
- Dialectical analysis: synthesis confidence 0.78, multiple publishable outcome paths

**Verification Execution Order:**
- **Phase 1 (W1–W2):** H-E1 — P3 attribution diagnostic (ρ threshold test) → Gate 1
- **Phase 2 (W3–W5):** H-M1 + H-M2 (joint training, stability) → H-M3 (benchmark P1/P2) → Gate 2
- **Phase 3 (W6):** H-M4 — probing for representation compression → Gate 3

**Critical Decision Points:**
1. **Gate 1 (end W2):** H-E1 ρ < 0.7? FAIL → STOP/PIVOT before any training
2. **Gate 2a (end W4):** Training stable? FAIL → PIVOT (separate LRs, GradNorm)
3. **Gate 2b (end W5):** LongBench-QA gap ≥ 1%? FAIL → revisit mechanism via H-M4
4. **Gate 3 (end W6):** Probing delta ≥ 5pp? FAIL → EXPLORE (cross-layer, MLP probe)

**Open Questions (from Phase 2A):**
- Is the 3% LongBench-QA threshold achievable given B3 rapid adaptation? → Pre-run H-E1 first
- Do GLUE short sequences (≤512 tokens) produce sufficient KV eviction at 50% budget?
- What LoRA/Locret LR ratio produces stable joint training?
- Does representation compression (P4) generalize across GLUE task types?

**Recommendations:**
1. **Immediate:** Execute H-E1 (P3 diagnostic) this week — no GPU required, just inference
2. **Before training:** Inspect Locret public code for CE loss compatibility (R2 mitigation)
3. **During training:** Monitor per-group gradient norms from epoch 1; abort condition: loss spike >2×
4. **Pre-registration:** Document 1–3% partial support interpretation before running P1 experiment

### 6.4 Appendices

**A. Phase 2A Reference**
- Source: `docs/youra_research/20260520_scope/03_refinement.yaml` (H-JointLoRAKV-v1)
- Phase 2A convergence: 15 exchanges, all 6 criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

**B. MCP Tool Usage Summary**
- `mcp__clearThought__scientificmethod`: 3 calls (H-E1, H-M1/M2, H-M3/M4)
- `mcp__clearThought__collaborativereasoning`: 1 call (risk analysis, 3-expert panel)
- `mcp__clearThought__structuredargumentation`: 3 calls (thesis, antithesis, synthesis)
- Total MCP calls: 7

**C. Scope Reduction Summary**
- Total claims: 7 | BUILD_ON (excluded): 4 | PROVE_NEW (targets): 3 | Reduction: 43%
- No cross-domain transfer validation required (requires_transfer_validation = false)

---

## 7. Pipeline State

**Verification State Status:** WRITTEN — `docs/youra_research/20260520_scope/verification_state.yaml` created with 5 sub-hypotheses (h-e1 READY; h-m1, h-m2, h-m3, h-m4 NOT_STARTED with correct prerequisites), pipeline IDs, baseline SKIPPED, hypothesis_task_mapping populated, schema v3.5.
**Pipeline Tasks Updated:** Phase 2B (`32ef89f5-6e69-4766-aa9a-1e2c6c10dd8f`) → `done`; Phase 2C (`a60aa522-e7c5-458a-ae68-e228d7f8a963`) → `doing` (Archon project `febb001c-d193-48b2-a83e-f95c7e40af2f`)
**Hypothesis Tasks Created:** 5 tasks in Archon Pipeline Project `febb001c-d193-48b2-a83e-f95c7e40af2f`, feature "Hypothesis Verification":
- H-E1: `02034080-df73-40b0-9ff5-0146dbe218af` (task_order=90, todo)
- H-M1: `c08c300f-1871-4cdb-a00a-eca48f5793ed` (task_order=85, todo)
- H-M2: `359d69ec-7d37-4627-be34-3f02f79f8cf8` (task_order=84, todo)
- H-M3: `442b0763-f97d-4d8a-b2e7-f68e7a64792f` (task_order=75, todo)
- H-M4: `3a9b43dd-b253-42ab-a72d-503ec62062af` (task_order=60, todo)

---

*Generated by YouRA Phase 2B | 2026-05-20*
