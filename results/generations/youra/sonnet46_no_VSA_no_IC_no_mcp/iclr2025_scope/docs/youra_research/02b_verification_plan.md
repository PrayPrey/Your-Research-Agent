# Verification Plan: Prefill-Observation vs. Cumulative-Attention KV Eviction Metric Comparison

**Date:** 2026-08-27
**Hypothesis ID:** H-PrefixObs-v1
**Confidence:** 0.75
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under long-context QA inference using LLaMA-2-7B-chat at 50% KV retention on LongBench (NarrativeQA, HotpotQA, 2WikiMQA, MuSiQue as QA tasks; GovReport and QMSum as summarization contrast), if we apply prefill-observation importance scoring (SnapKV-style query-conditioned window over the last W=16 query tokens) versus cumulative-attention scoring (H2O-style, both implemented with matched prefill-timing eviction) at matched KV retention budgets (50%), then prefill-observation achieves ≥2.0 F1 points higher macro-average than cumulative-attention on the 4-task QA subset, with a larger performance gap on QA than on summarization (delta_F1(QA) > delta_F1(Summ)), because query-conditioned observation windows selectively retain KV entries that are semantically aligned with the specific tokens of the question being answered, whereas cumulative attention retains globally-attended structural tokens (initial positions, sentence boundaries) that are less discriminative for specific query answering.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in LongBench macro-average F1 between prefill-observation scoring and cumulative-attention scoring at 50% KV retention on LLaMA-2-7B-chat (i.e., the 95% bootstrap confidence intervals overlap on the 4-task QA subset).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | LongBench v1 (standard) | LongBench contains diverse long-context tasks including extractive QA (NarrativeQA, HotpotQA, 2WikiMQA, MuSiQue) and summarization (GovReport, QMSum), enabling the task-conditional comparison central to this hypothesis. Standard automated metrics (F1, ROUGE-L) — no human evaluation required. |
| **Model** | LLaMA-2-7B-chat-hf | Instruction-tuned variant avoids h-m2 base-model collapse. 7B size fits on single A100 40GB at FP16. SnapKV's results suggest stable performance at 40-60% KV retention on this model. |

**Dataset Details:**
- Source: THUDM/LongBench on HuggingFace Hub
- Path: HuggingFace: THUDM/LongBench

**Model Details:**
- Type: decoder-only, instruction-tuned
- Source: meta-llama/Llama-2-7b-chat-hf on HuggingFace Hub

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| H2O (cumulative attention, decode-timed) | ~1 PPL degradation at 20% KV budget on WikiText-2 | WikiText-2, MT-Bench (base models) |
| SnapKV (prefill observation) | ~1-2% F1 degradation at 40% KV retention | LongBench, RULER (instruct models) |
| StreamingLLM (static) | Stable PPL over long sequences; poor on extractive QA | WikiText-2, PassKey (base models) |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | LLaMA-2-7B-chat attention patterns during prefill are predictive of decode-time token relevance for QA tasks | ScissorHands persistence hypothesis (Spearman r>0.85 at OPT-6.7B); SnapKV's prefill-observation design relies on this property | Prefill-observation metric would not outperform decode-timed metrics; H2O-at-prefill would equal H2O-at-decode |
| A2 | LLaMA-2-7B-chat does not catastrophically degrade at 50% KV retention (unlike h-m2's 80% eviction failure) | SnapKV paper reports ~1-2% F1 degradation at 40-60% retention on LLaMA-2-chat; StreamingLLM stable at 50% retention | All methods produce near-zero F1 at 50% retention — making metric comparison invalid (same failure mode as h-m2) |
| A3 | LongBench QA tasks have sufficient answer-relevant context within the 4096-token window for metric differences to manifest | LongBench tasks are designed for long-context evaluation; average lengths are 8-32K tokens but LLaMA-2 is tested at 4K truncation | If answers are uniformly distributed throughout the context, positional eviction may be as good as query-aware eviction |
| A4 | Unified codebase implementation of all metrics is equivalent to original paper implementations | Each metric reduces to a score_fn over attention weights — no architectural changes; HuggingFace past_key_values API is the common interface | Metric differences reflect implementation quality, not metric quality — results would not generalize |
| A5 | 100 examples per task provides sufficient statistical power to detect 2.0 F1 point differences at 95% confidence | LongBench NarrativeQA has ~2613 test examples; F1 variance is typically ~5-10 F1 points — 100 examples gives SE ~0.5-1.0 F1, sufficient for 2.0 F1 effect size | Confidence intervals overlap even when true effect is 2.0 F1 — requires more examples (200+) |

### 1.6 Research Gap & Novelty

**Gap:** No controlled ablation exists comparing cumulative attention vs. prefill observation vs. warm-up attention vs. entropy under identical conditions (same model, same benchmark, same eviction ratio). All prior papers conflate metric type with eviction timing and model type (instruct vs. base).

**Innovation:** 2×2 design (metric type × eviction timing) that disentangles WHAT to score vs. WHEN to evict — a confound present in all prior KV eviction comparisons. The task-conditional prediction (delta_F1(QA) > delta_F1(Summ)) provides a mechanistic test of query-awareness that has not been tested by prior work.

**Scope Reduction:** 50% of claims are BUILD_ON (established facts) — Phase 2B-4 focuses only on PROVE_NEW claims: (1) no controlled cross-method ablation exists, and (2) prefill-observation achieves higher F1 than cumulative-attention on QA tasks.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-C1 | CONDITION | SHOULD_WORK | H-M1, H-M2 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

#### H-E1: Existence — Prefill-Observation Outperforms Cumulative-Attention on QA

**Type:** EXISTENCE
**Statement:** Under long-context QA inference using LLaMA-2-7B-chat at 50% KV retention on LongBench 4-task QA subset (NarrativeQA, HotpotQA, 2WikiMQA, MuSiQue), if we apply prefill-observation importance scoring (SnapKV-style, W=16 query tokens) versus cumulative-attention-at-prefill scoring (H2O-style, both applied at prefill timing to eliminate timing confound), then prefill-observation achieves ≥2.0 macro-average F1 higher than cumulative-attention-at-prefill, because query-conditioned observation windows selectively retain answer-relevant KV entries.

**Variables:**
- IV: Importance metric type (prefill-observation M1 vs. cumulative-attention-at-prefill M2)
- DV: LongBench macro-average F1 on 4-task QA subset (100 examples per task)
- CV: Model (LLaMA-2-7B-chat-hf), KV retention (50%), hardware (A100 40GB FP16), seed (42), unified codebase

**Success Criteria:**
- prefixobs_F1_QA − cumulative_at_prefill_F1_QA ≥ 2.0 F1 points
- 95% bootstrap CI lower bound > 0 (non-overlapping with zero)

**Gate:**
- Type: MUST_WORK
- If Fail: Hypothesis invalidated — query-conditioning mechanism not supported at this scale; trigger reflection and route to Phase 2A-Dialogue for redesign

**Prerequisites:** None

**Verification Protocol:** Implement both score_fn variants in unified HuggingFace codebase using past_key_values API. Run LLaMA-2-7B-chat-hf on 100 examples each from NarrativeQA, HotpotQA, 2WikiMQA, MuSiQue at 50% KV retention. Apply M1 (mean attention from last 16 query tokens at prefill end) and M2 (cumulative sum of attention weights at prefill end) as eviction criterion. Compute per-task F1 and macro-average. Bootstrap 95% CI (1000 resamples). Compare macro-average F1 difference. Pass if ≥2.0 F1 and CI non-overlapping zero.

---

#### H-M1: Mechanism — Timing Effect (Prefill vs. Decode Eviction)

**Type:** MECHANISM
**Statement:** Under long-context QA inference using LLaMA-2-7B-chat at 50% KV retention, if we apply cumulative-attention scoring at prefill timing (H2O-at-prefill, single eviction before generation) versus at decode timing (H2O-at-decode, original H2O with per-step eviction), then H2O-at-prefill achieves ≥0.5 macro-average F1 higher on the 4-task QA subset, because prefill-phase attention patterns capture the full prompt context before generation begins, whereas decode-phase cumulative attention accumulates generation artifacts that dilute the importance scores.

**Variables:**
- IV: Eviction timing (prefill-phase M2 vs. decode-phase M3)
- DV: LongBench macro-average F1 on 4-task QA subset
- CV: Same metric type (cumulative-attention), model, KV retention (50%), unified codebase

**Success Criteria:**
- H2O_at_prefill_F1 − H2O_at_decode_F1 ≥ 0.5 F1 points

**Gate:**
- Type: MUST_WORK
- If Fail: Timing effect not confirmed — H-E1 result cannot be attributed to prefill timing; may still support H-E1 as a metric-type effect

**Prerequisites:** H-E1 (unified codebase verified operational)

**Verification Protocol:** Using the same unified codebase from H-E1, run M2 (cumulative-at-prefill) versus M3 (cumulative-at-decode, H2O original) on 4 QA tasks at 50% KV retention. M2 applies cumulative attention once at prefill end; M3 updates scores and evicts per decode step. Compute macro-average F1 for each. Compare: if H2O-at-prefill > H2O-at-decode by ≥0.5 F1, timing is an independent causal factor. This isolates eviction timing from metric type.

---

#### H-M2: Mechanism — Task-Conditional Advantage (QA vs. Summarization)

**Type:** MECHANISM
**Statement:** Under long-context inference using LLaMA-2-7B-chat at 50% KV retention comparing prefill-observation (M1) vs. cumulative-attention-at-prefill (M2), if we compute the metric advantage separately on QA tasks (NarrativeQA, HotpotQA, 2WikiMQA, MuSiQue) and summarization tasks (GovReport, QMSum), then delta_F1(QA) > delta_F1(Summ) by at least 1.0 percentage point, because summarization tasks have diffuse query signals (the entire input is the query) so cumulative globally-salient attention is equally informative, whereas QA tasks benefit from query-conditioned token selection.

**Variables:**
- IV: Task type (QA subset vs. summarization subset) × metric type (M1 vs. M2)
- DV: delta_F1(QA) = F1_M1(QA) − F1_M2(QA); delta_ROUGE(Summ) = ROUGE-L_M1(Summ) − ROUGE-L_M2(Summ)
- CV: Model, KV retention (50%), same metric pair (M1 vs. M2), unified codebase

**Success Criteria:**
- delta_F1(QA) − delta_ROUGE(Summ) ≥ 1.0 percentage point

**Gate:**
- Type: MUST_WORK
- If Fail: Task-conditional mechanism not supported — metric advantage is general, not query-specific; revise mechanistic claim

**Prerequisites:** H-E1 (M1 and M2 results already available from H-E1 run)

**Verification Protocol:** Reuse M1 and M2 runs from H-E1 plus additional runs on summarization tasks (GovReport, QMSum, 100 examples each). Compute delta_F1(QA) and delta_ROUGE-L(Summ). Compare: if delta_F1(QA) > delta_ROUGE(Summ) by ≥1.0, the query-specificity mechanism is confirmed. Note: GovReport and QMSum use ROUGE-L as the primary metric (standard LongBench practice) while QA tasks use F1.

---

#### H-C1: Condition — Metric Advantage Bounds (KV Retention Sensitivity)

**Type:** CONDITION
**Statement:** Under long-context QA inference using LLaMA-2-7B-chat comparing prefill-observation (M1) vs. cumulative-attention-at-prefill (M2), if we vary KV retention budget from 40% to 60%, then the prefill-observation advantage (delta_F1_QA) is positive and ≥1.0 F1 at all tested retention levels, because the query-conditioning mechanism's benefit is not confined to a narrow compression regime but holds across moderate retention budgets.

**Variables:**
- IV: KV retention budget (40%, 50%, 60%)
- DV: delta_F1(QA) at each retention level
- CV: Metric pair (M1 vs. M2), model, tasks (4 QA tasks), unified codebase

**Success Criteria:**
- delta_F1_QA ≥ 1.0 F1 at 40%, 50%, and 60% KV retention

**Gate:**
- Type: SHOULD_WORK
- If Fail: Result is valid — boundary condition identified; report retention regime where advantage holds

**Prerequisites:** H-M1, H-M2 (core mechanism confirmed before boundary testing)

**Verification Protocol:** Run M1 and M2 on 4 QA tasks at KV retention budgets of 40%, 50%, and 60%. Compute delta_F1(QA) for each budget level. Report whether the advantage is monotonically increasing, decreasing, or flat across retention levels. This maps the operational boundary of the query-conditioning advantage and is informative even if not all levels pass the threshold.

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 (MUST_WORK) → H-M1 (MUST_WORK) → H-C1 (SHOULD_WORK)
H-E1 (MUST_WORK) → H-M2 (MUST_WORK) → H-C1 (SHOULD_WORK)
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | prefixobs_F1 − cumul_F1 ≥ 2.0 AND 95% CI lower > 0 | Stop pipeline; trigger reflection; route to Phase 2A-Dialogue |
| H-M1 | MUST_WORK | H2O_at_prefill − H2O_at_decode ≥ 0.5 F1 | Timing effect not confirmed; document as null result; H-E1 remains as metric-type effect |
| H-M2 | MUST_WORK | delta_F1(QA) − delta_ROUGE(Summ) ≥ 1.0 | Task-conditional mechanism not supported; revise mechanistic claim |
| H-C1 | SHOULD_WORK | delta_F1_QA ≥ 1.0 at 40%, 50%, 60% KV | Report boundary regime where advantage holds; paper scope adjustment |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Core Setup | H-E1 (codebase + M1 vs M2) | 3-4 days |
| Phase 2: Mechanism Tests | H-M1 (timing), H-M2 (task-conditional) | 2-3 days |
| Phase 3: Boundary Testing | H-C1 (retention sensitivity) | 1-2 days |

**Total Duration:** 6-9 days

---

## 4. Risk Analysis

### 4.1 Identified Risks

| Risk ID | Source Assumption | Risk Description | Likelihood | Impact | Hypothesis Affected |
|---------|-------------------|------------------|------------|--------|---------------------|
| R1 | A1 | Prefill attention patterns do not persist to decode-time relevance — prefill-observation advantage fails to materialize | Medium | Critical | H-E1, H-M1 |
| R2 | A2 | LLaMA-2-7B-chat catastrophically degrades at 50% KV retention — all methods near-zero F1 (h-m2 repeat) | Low | Critical | All |
| R3 | A3 | Answer spans uniformly distributed in context — positional eviction as good as query-aware eviction | Medium | High | H-E1, H-M2 |
| R4 | A4 | Implementation quality differences between M1-M6 codebase variants inflate or deflate true metric differences | Low-Medium | High | All |
| R5 | A5 | 100 examples per task insufficient statistical power — 95% CI overlaps even with true 2.0 F1 effect | Low | High | H-E1 |
| R6 | Design | H2O-at-prefill (M2) is a non-standard variant — the "fairness" of comparing to original H2O is questionable | Medium | Medium | H-M1 |

### 4.2 Risk-Hypothesis Mapping

| Hypothesis | Primary Risks | Mitigation |
|------------|---------------|------------|
| H-E1 | R1, R2, R3, R4, R5 | Run full KV cache (M0) as sanity check first; verify F1 non-degenerate |
| H-M1 | R1, R6 | Document M2 as "H2O metric applied at prefill timing" — a valid ablation even if not canonical |
| H-M2 | R3 | Include task-type interaction analysis; use matched metric families across tasks |
| H-C1 | R2 (at 40%) | If 40% retention degrades all methods, report 50-60% only as valid regime |

### 4.3 Mitigation Strategies

1. **R1 (prefill persistence):** Run M2 vs. M3 (H-M1) as an explicit timing ablation before final H-E1 interpretation. If timing effect is null, prefill-observation advantage is entirely attributable to metric type, which is still a valid result.
2. **R2 (model degradation):** Pre-validate model health: run full KV cache baseline and StreamingLLM at 50% retention before any metric comparison. If both degrade catastrophically, stop and document.
3. **R3 (uniform context):** If delta_F1(QA) is near zero for all metrics, examine attention heatmaps for 5 examples to diagnose whether answer spans are retrievable at 4096-token truncation.
4. **R4 (implementation quality):** Validate each score_fn against expected behavior: M1 should produce attention-weighted token importances concentrated on last-query-token positions; M2 should show monotonically increasing cumulative sums. Unit-test each.
5. **R5 (statistical power):** Pre-register the analysis plan: bootstrap 95% CI as primary criterion, not just point estimate. If CI barely overlaps zero, consider running 50 additional examples.
6. **R6 (M2 fairness):** Clearly label M2 as "cumulative-attention-at-prefill" — an ablation condition, not a claim about H2O's original design. The original H2O (M3) is also tested in H-M1.

### 4.4 Risk Summary

| Severity | Count | Risks |
|----------|-------|-------|
| Critical | 2 | R1, R2 |
| High | 3 | R3, R4, R5 |
| Medium | 1 | R6 |

**Overall Risk Level:** Medium-High. R2 (model degradation) is the most dangerous because it blocked h-m2; the redesign to 50% retention and instruct model specifically addresses this. R1 (prefill persistence) is the key mechanistic assumption and is directly tested by H-M1.

---

## 5. Dependency Graph (DAG) & Timeline

### 5.1 Dependency Graph

```
                    [START]
                       │
                       ▼
              ┌─────────────────┐
              │      H-E1       │  MUST_WORK
              │  Existence Test │
              │ (M1 vs M2, QA)  │
              └────────┬────────┘
                       │ PASS
              ┌────────┴────────┐
              │                 │
              ▼                 ▼
   ┌────────────────┐  ┌─────────────────┐
   │     H-M1       │  │      H-M2       │  Both MUST_WORK
   │ Timing Effect  │  │ Task-Conditional│
   │(M2 vs M3 QA)   │  │(QA vs Summ)     │
   └────────┬───────┘  └────────┬────────┘
            │ PASS              │ PASS
            └────────┬──────────┘
                     ▼
          ┌─────────────────────┐
          │        H-C1         │  SHOULD_WORK
          │  Retention Boundary │
          │  (40%, 50%, 60%)    │
          └──────────┬──────────┘
                     │
                     ▼
                  [DONE]
                  → Phase 4.5 Synthesis
```

### 5.2 Dependency Hierarchy

| Level | Hypotheses | Condition to Advance |
|-------|------------|----------------------|
| 0 (Root) | H-E1 | Must PASS (MUST_WORK gate) |
| 1 (Parallel) | H-M1, H-M2 | Both must PASS (MUST_WORK gates) |
| 2 (Final) | H-C1 | SHOULD_WORK (boundary, informative even if partial) |

### 5.3 Gantt Timeline

```
Week 1                     Week 2
Mon  Tue  Wed  Thu  Fri │ Mon  Tue  Wed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
H-E1  ████████████████  │
H-M1                    │ ████████
H-M2                    │ ████████
H-C1                    │          ████
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Days:  1  2  3  4  5    │  6  7  8  9
```

**Note:** H-M1 and H-M2 run in parallel after H-E1 passes (M1 and M2 results are already computed in H-E1; H-M1 adds M3 run only; H-M2 adds summarization task runs only).

### 5.4 Critical Path

H-E1 → H-M1 (or H-M2) → H-C1

**Critical path duration:** 7-9 days
**Bottleneck:** H-E1 (requires codebase implementation of all metric variants)

### 5.5 Resource Summary

| Resource | Requirement |
|----------|-------------|
| GPU | 1× A100 40GB (FP16) |
| Model | LLaMA-2-7B-chat-hf (~14GB VRAM) |
| Compute per run | ~2-4 hours per metric × task subset at 100 examples |
| Total GPU hours | ~30-50 GPU hours (6 metrics × 6 tasks × 100 examples) |
| Storage | ~50GB (model weights + activation cache) |
| Code | Unified HuggingFace codebase (~500 lines) |

### 5.6 Execution Order

1. Implement and unit-test all 6 score_fn variants in unified codebase
2. Run sanity checks: full KV cache + StreamingLLM baseline at 50% retention
3. **H-E1:** Run M1 vs. M2 on 4 QA tasks → compute F1 + bootstrap CI
4. **H-M1 (parallel):** Run M3 (H2O-at-decode) → compare to M2 (already done in H-E1)
5. **H-M2 (parallel):** Run M1 and M2 on summarization tasks → compute ROUGE-L
6. **H-C1:** Run M1 vs. M2 at 40% and 60% retention (50% already done)

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Statement:** Prefill-observation importance scoring (SnapKV-style, query-conditioned) achieves meaningfully higher F1 on extractive QA tasks than cumulative-attention scoring at matched 50% KV retention, and this advantage is larger on QA than on summarization tasks — demonstrating that query-conditioned KV retention is a superior mechanism for task-specific long-context compression.

**Supporting Arguments:**
- A1 (prefill persistence) is supported by two independent papers (SnapKV, ScissorHands) with Spearman r>0.85 at OPT-6.7B
- The 2×2 design (metric × timing) controls for the confounds present in all prior comparisons
- The task-conditional prediction (P2: delta_F1(QA) > delta_F1(Summ)) is a mechanistically grounded and independently testable claim

### 6.2 Antithesis

**Challenges:**
1. **Prefill persistence may not hold for instruct models:** The ScissorHands result is on OPT-6.7B (base), not instruction-tuned models. Instruction tuning changes attention patterns; the persistence property may be weaker.
2. **The 2.0 F1 threshold may be too ambitious:** At 50% KV retention, LongBench QA task baselines have high variance (~5-10 F1 points). The 2.0 F1 effect may be detectable in macro-average but not at individual task level.
3. **H2O-at-prefill (M2) is a modified method, not the original H2O:** Comparing M1 to M2 is comparing two non-standard methods. The "fair comparison" framing may be critiqued.
4. **The summarization contrast (P2) uses ROUGE-L, not F1:** Cross-metric comparison of QA-F1 advantage vs. summarization-ROUGE-L advantage is methodologically awkward.

### 6.3 Synthesis

**Resolution:**
1. **Instruct model persistence:** The assumption is explicitly tested by H-M1 (timing ablation). If H2O-at-prefill = H2O-at-decode for instruct models, the timing effect is null — and the prefill-observation advantage (H-E1) must be attributed to metric type alone. This is still a valid and publishable result.
2. **Threshold conservatism:** The 2.0 F1 gate is on macro-average (4 tasks), which reduces variance by averaging. Bootstrap CI is the primary criterion. If the CI is non-overlapping zero but point estimate is <2.0, the result is directionally confirmed — gate can be softened at Phase 4.5 synthesis.
3. **M2 framing:** M2 is explicitly labeled as an ablation condition ("cumulative-at-prefill timing"), not a claim about H2O's design. The original H2O (M3) is also tested. The comparison is transparent.
4. **Cross-metric (P2):** P2 is directional evidence, not a statistical test. We compare the size of the advantage on QA vs. summarization — the metric difference (F1 vs. ROUGE-L) is noted as a limitation, and results are reported separately.

### 6.4 Robustness Assessment

| Dimension | Assessment |
|-----------|------------|
| Internal validity | High — unified codebase eliminates implementation confounds; 2×2 design controls timing |
| External validity | Medium — single model (LLaMA-2-7B-chat), 5-task LongBench subset; generalization limited |
| Statistical power | Medium — 100 examples/task sufficient for 2.0 F1 effect at macro-average; borderline for individual tasks |
| Mechanistic clarity | High — three predictions (P1, P2, P3) each test a distinct causal link |
| Prior work alignment | High — builds on established foundations (SnapKV, ScissorHands, H2O); extends rather than contradicts |

**Overall Robustness:** Medium-High. The primary risk is external validity (single model, single benchmark subset). Phase 5 Baseline Comparison will extend to additional conditions.

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

This verification plan operationalizes hypothesis H-PrefixObs-v1 (confidence: 0.75) into 4 sub-hypotheses testing whether prefill-observation KV importance scoring outperforms cumulative-attention scoring on long-context QA tasks. The plan addresses the core mechanistic gap: no prior paper has controlled for metric type × eviction timing confounds simultaneously.

**Sub-hypotheses:**
- **H-E1 (MUST_WORK):** Prefill-observation ≥2.0 F1 above cumulative-at-prefill on 4-task LongBench QA macro-average
- **H-M1 (MUST_WORK):** Prefill-timed eviction ≥0.5 F1 above decode-timed eviction (timing ablation)
- **H-M2 (MUST_WORK):** Task-conditional advantage: delta_F1(QA) > delta_ROUGE(Summ) by ≥1.0 pp
- **H-C1 (SHOULD_WORK):** Advantage holds across 40-60% KV retention budgets

**Scope reduction:** 50% of Phase 2A claims are BUILD_ON (established) — verification effort focused on 2 PROVE_NEW claims.

**Timeline:** 7-9 days, single A100 40GB GPU, ~30-50 GPU hours total.

### 7.2 Conclusions

1. **Execution order:** H-E1 first (critical gate) → H-M1 and H-M2 in parallel → H-C1 last
2. **Decision point:** H-E1 is the binary gate — if prefill-observation does not outperform at 50% retention, the hypothesis is invalidated and routes back to Phase 2A-Dialogue
3. **Efficiency:** H-M1 and H-M2 reuse H-E1 compute (M1 and M2 runs already complete); only incremental compute needed
4. **Risk:** R2 (model degradation) is the highest-priority pre-check; must validate 50% retention is non-degenerate before metric comparison

### 7.3 Open Questions (Deferred to Phase 5 or Later)

- Optimal observation window size W (W=16 is SnapKV default — sensitivity analysis deferred)
- Generalization to other model sizes (13B, 70B) — Phase 5
- Attention entropy (M5) behavior — included as condition in H-C1 optional extension
- Cross-architecture generalization — Phase 5 Baseline Comparison

### 7.4 Appendices

**A: Metric Conditions Summary**

| ID | Name | Timing | Score Function |
|----|------|--------|----------------|
| M1 | Prefill-Observation (SnapKV-style) | prefill | mean attention from last W=16 query tokens at prefill end |
| M2 | Cumulative-Attention-at-Prefill (H2O-at-prefill) | prefill | cumulative sum of attention weights at prefill end |
| M3 | Cumulative-Attention-at-Decode (H2O original) | decode | cumulative sum, updated per decode step |
| M4 | Warm-Up Attention (ScissorHands-style) | decode | attention during first 32 decode steps |
| M5 | Attention Entropy | prefill | H(i) = −Σ_h Σ_t α_{h,t,i} × log(α_{h,t,i} + ε), averaged across heads |
| M6 | StreamingLLM (static baseline) | N/A | attention sinks (first 4 tokens) + sliding window |

**B: LongBench Tasks Used**

| Task | Type | Metric | Examples |
|------|------|--------|----------|
| NarrativeQA | Extractive QA | F1 | 100 |
| HotpotQA | Multi-hop QA | F1 | 100 |
| 2WikiMQA | Multi-hop QA | F1 | 100 |
| MuSiQue | Multi-hop QA | F1 | 100 |
| GovReport | Summarization | ROUGE-L | 100 |
| QMSum | Summarization | ROUGE-L | 100 |

**C: Established Facts (BUILD_ON — Do Not Re-Verify)**

1. Cumulative attention score (H2O) outperforms static sliding window (StreamingLLM) on WikiText-2 perplexity at 20% KV retention
2. SnapKV prefill-observation scoring outperforms H2O on LongBench at 40% KV retention (instruct models) — note: conflates metric and timing
3. Attention patterns exhibit persistence — importance at step K correlates with importance at step K+20 (Spearman r>0.85 at OPT-6.7B)
