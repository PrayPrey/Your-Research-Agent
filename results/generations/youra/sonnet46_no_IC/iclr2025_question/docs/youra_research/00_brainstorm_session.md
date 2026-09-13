---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Layer-Wise Logit-Lens UQ for Hallucination (v2)"
---

# Research Brainstorm Session Results

**Session Date:** 2026-08-05
**Facilitator:** Research Question Architect
**Participant:** Anonymous

---

## Executive Summary

**Initial Interest:** Depth-resolved (per-layer) logit-lens uncertainty signals for architecture-robust hallucination detection in open-source LLMs — continuation of an interrupted, never-refuted direction

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode)

**Session Duration:** < 1 minute (automated extraction)

---

## Starting Context

The provided research_idea_content was a placeholder ("dummy") with no extractable research components. Per ROUTE_TO_0 protocol, direction is derived from: (1) Serena Memory failure record `failure_h-e1_run1` (Phase 4 MUST_WORK_GATE_FAIL, 2026-08-04, final-layer mean entropy), and (2) archived pipeline history — five recovery archives, most recent `_archive/20260805T054934_routing_recovery/` containing the Layer-Wise Logit-Lens pipeline (project 2e9f1271-024c-4991-8e85-61b782fbd1d9).

**Critical finding from archive forensics:** The logit-lens run was NOT scientifically refuted. Its terminal log shows a healthy full experiment launch at 05:41 (validator 18/18 pass, GPU util 72%, phased error checks passed) with 871/1000 LLaMA-2/TriviaQA samples cached when a routing restart with trigger "h-e1 (UNKNOWN)" archived it at 05:49:34. h-e1 status in verification_state.yaml: IN_PROGRESS — neither validated nor failed. This was an infrastructure interruption, not a hypothesis failure.

Source Type: ROUTE_TO_0 failure-recovery synthesis (input placeholder — no new external input)

Retrying after previous failure (original h-e1 MUST_WORK_GATE_FAIL — final-layer mean token entropy insufficient for LLaMA-2-7B). The depth-resolved logit-lens direction remains the strongest justified pivot and is re-instantiated as v2.

---

## Lessons from Previous Attempts

### What Was Tried Before

**Attempt 1 (h-e1, Run 1 — recorded scientific failure):** Final-layer mean token logit entropy, gate AUROC > 0.52 on TriviaQA or TruthfulQA for all 3 model families.
- LLaMA-3-8B: AUROC 0.66 (CI [0.614, 0.703]) — PASS
- Mistral-7B: AUROC 0.53–0.59 — PASS
- LLaMA-2-7B: AUROC 0.5186 (missed gate by 0.0014), direction inverted on TriviaQA — FAIL

**Attempts 2–3 (recovery cycles):** Multi-signal fusion direction (entropy variants + max-token probability + semantic consistency variance). Both archived via routing restarts without a passing run.

**Attempt 4 (Layer-Wise Logit-Lens v1 — interrupted, NOT refuted):** Full pipeline reached Phase 4; environment built (torch 2.8.0+cu128 on H100), data verified, validator full pass, full experiment running healthy when a routing restart (trigger "h-e1 (UNKNOWN)") archived it mid-run. No result contradicts the hypothesis. Partial artifact: `_archive/20260805T054934_routing_recovery/h-e1/results/cache_llama2_triviaqa.csv` (871/1000 rows) plus complete working code.

### Why the Original Attempt Failed

- Final-layer mean entropy is architecture-dependent — base LLaMA-2-7B produces insufficient entropy spread
- Direction inversion on LLaMA-2/TriviaQA shows the entropy-correctness relationship is not monotone across models
- Root cause: a scalar signal read only at the final layer is confounded by tokenizer, RLHF status, and per-architecture output calibration

### How This Direction Avoids Those Pitfalls

1. **Moves off the final layer entirely:** Per-layer logit-lens signals read uncertainty BEFORE the final calibration stage, sidestepping the RLHF/tokenizer confound that suppressed LLaMA-2's final-layer entropy spread.
2. **Implements the failure record's unused suggestion:** "Add per-layer entropy to find layers with stronger signal for llama2" — now the core hypothesis.
3. **No cross-model consistency assumption:** The informative layer is selected per-model on a held-out split.
4. **Direction ambiguity handled by design:** AUROC direction correction plus per-model signed layer scoring eliminates the inversion failure mode.
5. **Distinct from the archived fusion direction:** Single forward pass, no multi-sample semantic consistency.
6. **LLaMA-2 retained as stress test:** Tests whether intermediate layers rescue the architecture where the final-layer signal failed by 0.0014.
7. **NEW (from v1 interruption):** Downstream phases should reuse v1's validated code and partial cache from `_archive/20260805T054934_routing_recovery/h-e1/` where protocol-identical — the environment recipe (torch 2.8.0+cu128, transformers 4.57.6) and 871-row LLaMA-2/TriviaQA cache are recoverable, shortening Phase 4 re-execution.

---

## Session Plan

ROUTE_TO_0 Auto-Fill — direction synthesized from Serena Memory (failure_h-e1_run1) + archived pipeline history (5 recovery archives). Input content was a placeholder; no components extracted from it. Decision: re-instantiate the interrupted logit-lens direction as v2 rather than pivot again — the only recorded scientific failure is the final-layer entropy attempt, and this direction is distinct from it.

---

## Technique Sessions

ROUTE_TO_0 Mode — No interactive sessions. Research direction derived from: (1) failure analysis of h-e1 run 1 from Serena Memory, (2) archive forensics showing logit-lens v1 was interrupted mid-run without refutation, (3) the per-layer entropy suggestion in the failure record's "Suggested Modifications".

---

## Research Question Development

### Initial Question

Do intermediate-layer (logit-lens) uncertainty signals contain stronger and more architecture-robust hallucination signal than final-layer output entropy, particularly for architectures where the final-layer signal fails?

### Refined Question

Does per-model selection of depth-resolved uncertainty signals — logit-lens entropy, logit-lens max-token probability, and consecutive-layer prediction KL divergence computed at each transformer layer from a single greedy forward pass — achieve hallucination-detection AUROC > 0.60 on TriviaQA and TruthfulQA for all three open-source model families (LLaMA-2-7B, Mistral-7B, LLaMA-3-8B), including LLaMA-2-7B where final-layer mean entropy failed (AUROC 0.5186), and does the best intermediate layer outperform the final layer by a statistically significant margin (95% bootstrap CI separation) on LLaMA-2-7B?

### Detailed Sub-Questions

1. Does logit-lens entropy at some intermediate layer exceed final-layer mean entropy AUROC on LLaMA-2-7B, the architecture where the final-layer signal failed (0.5186), with the 95% bootstrap CI of the difference excluding zero?
2. Is the per-model optimal layer stable across datasets — does the layer selected on a TriviaQA held-out split transfer to TruthfulQA (and vice versa) without AUROC dropping below 0.60?
3. Does consecutive-layer prediction KL divergence (distribution shift between adjacent layers' logit-lens predictions) provide complementary signal beyond per-layer entropy, measured by AUROC gain when the two are fused per-model with logistic regression?
4. Is the relative depth of the most informative layer (layer index / total layers) consistent across the three model families, or is depth-of-signal itself architecture-dependent?
5. Does the single-pass layer-wise approach match or exceed the final-layer signal on Mistral-7B and LLaMA-3-8B (i.e., the pivot does not sacrifice the architectures that already passed)?

---

## Reference Papers

Not provided - will discover in Phase 1

---

## Validation Results

### So What Test

The h-e1 failure showed real but fragile signal: final-layer entropy works on LLaMA-3 (AUROC 0.66) yet misses on base LLaMA-2 by 0.0014. If intermediate layers carry the signal that final-layer calibration suppresses, hallucination detection becomes architecture-robust at zero extra inference cost (hidden states are already computed in the forward pass). Practical, annotation-free contribution for deploying open-source LLMs, with a clean falsifiable claim: if no intermediate layer beats the final layer on LLaMA-2, the depth-resolved hypothesis dies on the same gate that killed h-e1. Additionally, v1's healthy mid-run state (validator full pass, experiment running at expected throughput) demonstrated implementation feasibility end-to-end.

### Feasibility Check

All components testable immediately with existing infrastructure — mandatory pipeline constraints satisfied:
- **Datasets:** TriviaQA, TruthfulQA (existing real benchmarks, HF-cached, used in h-e1 and v1) — no new benchmarks, rubrics, or scoring frameworks
- **Models:** LLaMA-2-7B, Mistral-7B, LLaMA-3-8B (already accessible in HF cache; v1 verified) — no future or synthetic data
- **Features:** Logit-lens = apply the model's own unembedding head to intermediate hidden states from the same greedy forward pass — pure computation on existing model outputs
- **Layer selection / fusion:** Held-out split of existing benchmark + scikit-learn logistic regression — no new annotation
- **Evaluation:** AUROC with direction correction + bootstrap CI (identical protocol to h-e1) — no human evaluation or subjective scoring
- **Proven runnable:** v1 executed this exact protocol on 5x H100 with working environment recipe and 87% of the first model/dataset cell already cached

---

## Phase 1 Input Package

<phase1-input>

### research_question
Does per-model selection of depth-resolved uncertainty signals — logit-lens entropy, logit-lens max-token probability, and consecutive-layer prediction KL divergence computed at each transformer layer from a single greedy forward pass — achieve hallucination-detection AUROC > 0.60 on TriviaQA and TruthfulQA for all three open-source model families (LLaMA-2-7B, Mistral-7B, LLaMA-3-8B), including LLaMA-2-7B where final-layer mean entropy failed (AUROC 0.5186), and does the best intermediate layer outperform the final layer by a statistically significant margin (95% bootstrap CI separation) on LLaMA-2-7B?

### detailed_question
1. Does logit-lens entropy at some intermediate layer exceed final-layer mean entropy AUROC on LLaMA-2-7B, the architecture where the final-layer signal failed (0.5186), with the 95% bootstrap CI of the difference excluding zero?
2. Is the per-model optimal layer stable across datasets — does the layer selected on a TriviaQA held-out split transfer to TruthfulQA (and vice versa) without AUROC dropping below 0.60?
3. Does consecutive-layer prediction KL divergence (distribution shift between adjacent layers' logit-lens predictions) provide complementary signal beyond per-layer entropy, measured by AUROC gain when the two are fused per-model with logistic regression?
4. Is the relative depth of the most informative layer (layer index / total layers) consistent across the three model families, or is depth-of-signal itself architecture-dependent?
5. Does the single-pass layer-wise approach match or exceed the final-layer signal on Mistral-7B and LLaMA-3-8B (i.e., the pivot does not sacrifice the architectures that already passed)?

### reference_papers
Not provided - will discover in Phase 1

</phase1-input>

---

## Session Insights

### Key Discoveries

- Input content was a placeholder ("dummy"); direction fully derived from failure-recovery context per ROUTE_TO_0 merge strategy
- Archive forensics show logit-lens v1 was interrupted mid-run (trigger "h-e1 (UNKNOWN)"), NOT scientifically refuted — h-e1 status was IN_PROGRESS with healthy GPU execution
- The only recorded scientific failure remains final-layer mean entropy (h-e1 run 1); this direction is distinct from it
- v1 left reusable assets: validated code, environment recipe (torch 2.8.0+cu128, transformers 4.57.6), and an 871/1000-row LLaMA-2/TriviaQA feature cache in `_archive/20260805T054934_routing_recovery/h-e1/`
- Logit-lens signals bypass final-layer calibration — the mechanism the root-cause analysis blamed for LLaMA-2's weak entropy spread

### Techniques Used

ROUTE_TO_0 Mode — Serena Memory failure analysis (failure_h-e1_run1) + archive forensics across 5 recovery archives (terminal logs, verification_state.yaml, checkpoint files)

### Areas for Further Exploration

- Attention-head-level uncertainty signals (finer granularity than layers; deferred for scope)
- Hidden-state probe classifiers (trained linear probes; heavier supervision, deferred)
- Multi-sample semantic consistency fusion (from archived fusion direction; reintroduce only if single-pass signals plateau)
- Base vs. instruct variant confound as a controlled study (llama3-instruct vs llama3-base)

---

## Next Steps

Proceed to Phase 1 - Targeted Research: /phase1-targeted

Focus Phase 1 literature search on:
1. Logit lens / tuned lens: interpreting intermediate-layer predictions (nostalgebraist 2020; Belrose et al. 2023, tuned lens)
2. Internal-state hallucination detection: probing hidden states for truthfulness (Azaria & Mitchell 2023; INSIDE, Chen et al. 2024)
3. Layer-wise knowledge localization in transformers (early-exit literature, DoLa decoding by contrasting layers)
4. Entropy-based UQ baselines on QA benchmarks: TriviaQA, TruthfulQA protocols with AUROC evaluation
5. Cross-architecture robustness of internal-representation signals — base vs. instruct-tuned models
6. Consecutive-layer distribution shift (KL between adjacent layer predictions) as confidence signal

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm (ROUTE_TO_0)*
*Ready for: Phase 1 - Targeted Research*
