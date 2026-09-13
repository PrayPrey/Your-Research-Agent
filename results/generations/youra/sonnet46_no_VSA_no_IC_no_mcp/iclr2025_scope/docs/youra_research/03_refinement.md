# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-27T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Independent-Controller Self-Play (Claude plays all personas; no external orchestrator)
- **Gap ID**: gap-1
- **Gap Title**: No Systematic Benchmark Comparison of Query-Aware Token Importance Metrics
- **Execution Mode**: UNATTENDED (#batch-mode)
- **Discussion Exchanges**: 8
- **Previous Hypothesis**: h-m2 (SUPERSEDED — ROUTED_TO_PHASE_2A)

---

## Research Dialogue Context

**Participants**: Dr. Nova (Novelty), Prof. Vera (Falsifiability), Dr. Sage (Significance), Prof. Pax (Feasibility), Dr. Ally (Synthesis), Prof. Rex (Critique)

**Total Exchanges**: 8

**Convergence Reason**: All 6 convergence criteria met at Exchange 8 — SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS all satisfied

### Key Insights
1. The critical confound in all prior KV eviction comparisons is that metric type and eviction timing are always co-varied. H2O uses base models + decode-timed eviction; SnapKV uses instruct models + prefill-timed eviction. No paper separates these two factors.
2. The H2O-at-prefill ablation condition (cumulative attention computed and applied at prefill, not decode-time) is the missing experimental point that enables causal attribution of metric vs. timing effects.
3. The task-conditional prediction (prefill-observation advantage is larger on QA than on summarization) provides a mechanistic falsification path beyond overall benchmark ranking.
4. h-m2's failure (base model + 80% eviction causing SnapKV collapse) is entirely avoided by using LLaMA-2-7B-chat at 50% KV retention.

### Breakthrough Moments
- **Exchange 6 (Prof. Rex)**: Identified the timing confound — the most important methodological insight of the discussion. Transformed the design from a benchmark paper to a mechanistic study.
- **Exchange 7 (Dr. Nova)**: Proposed the 2x2 design (metric × timing) with H2O-at-prefill as the decoupling condition — the key novel experimental point.
- **Exchange 3 (Dr. Sage)**: Scoped the minimum sufficient experiment to ~6 GPU-hours without losing scientific value.

---

## Final Hypothesis

### Title
Query-Conditioned Prefill Observation Outperforms Cumulative Attention on Extractive QA under KV Compression (H-PrefixObs-v1)

### Core Claim (Under-If-Then-Because)
Under long-context QA inference using LLaMA-2-7B-chat at 50% KV retention on LongBench (NarrativeQA, HotpotQA, 2WikiMQA, MuSiQue as QA tasks; GovReport and QMSum as summarization contrast), **if** we apply prefill-observation importance scoring (SnapKV-style query-conditioned window, last W=16 query tokens) versus cumulative-attention scoring (H2O-style), both implemented with matched prefill-timing eviction and matched KV retention budgets (50%), **then** prefill-observation achieves ≥2.0 F1 points higher macro-average than cumulative-attention on the 4-task QA subset, with a larger advantage gap on QA than on summarization (delta_F1(QA) > delta_F1(Summ)), **because** query-conditioned observation windows selectively retain KV entries that are semantically aligned with the specific tokens of the question being answered — whereas cumulative attention retains globally-attended structural tokens (initial positions, sentence boundaries) that are less discriminative for specific query answering.

### Mechanism
Three-step causal chain:
1. **Query-alignment (prefill)**: Query-conditioned observation windows identify answer-relevant KV positions during prefill by attending to the final W=16 query tokens. Prefill attention patterns are predictive of decode-time relevance (supported by ScissorHands persistence property).
2. **Selective retention improves QA**: Retaining query-aligned tokens increases the probability that answer-relevant context survives KV compression. Extractive QA tasks require retrieving specific spans — query-aligned retention is more useful than globally-salient structural retention.
3. **Task-conditional advantage**: Summarization tasks have diffuse query signals (the entire input is the query). Cumulative attention is equally informative on summarization because globally high-attention tokens (topic sentences, discourse markers) are systematically important. This creates the task-conditional prediction: delta_F1(QA) > delta_F1(Summ).

**2x2 Ablation Design (metric × timing):**
| | Prefill-Observation metric | Cumulative-Attention metric |
|---|---|---|
| **Prefill eviction** | M1: SnapKV (proposed) | M2: H2O-at-prefill (novel ablation) |
| **Decode eviction** | N/A | M3: H2O original |

M2 is the key decoupling condition: if M1 > M2, the **metric** (query-conditioning) drives the advantage. If M2 > M3, the **timing** (prefill vs. decode) independently contributes.

---

## Predictions

### P1 (Primary) — Metric Effect on QA
- **Statement**: Prefixobs macro-F1(QA) − Cumulative-at-prefill macro-F1(QA) ≥ 2.0 at 50% KV retention, LLaMA-2-7B-chat
- **Success criterion**: ≥2.0 F1 gap AND 95% bootstrap CI lower bound > 0
- **Falsification**: If gap < 2.0 OR CIs overlap → query-conditioning mechanism not supported

### P2 (Secondary) — Task-Conditional Advantage
- **Statement**: delta_F1(QA) > delta_F1(Summ) by at least 1.0 percentage point
- **Success criterion**: delta_F1(QA) − delta_F1(Summ) ≥ 1.0pp
- **Falsification**: If delta_F1(QA) ≤ delta_F1(Summ) → metric advantage is general, not query-specific

### P3 (Tertiary) — Timing Effect
- **Statement**: H2O-at-prefill F1(QA) > H2O-at-decode F1(QA) by ≥0.5 points
- **Success criterion**: 0.5 F1 gap (timing independently contributes)
- **Falsification**: If H2O-at-prefill ≈ H2O-at-decode → timing is not a confound

---

## Novelty

**What's new**: First controlled ablation of KV eviction importance metric families (cumulative attention, prefill observation, warm-up attention, attention entropy, static window) under identical experimental conditions (same model, same benchmark, same eviction ratio, same codebase). First 2x2 metric×timing ablation design. First task-conditional metric advantage prediction.

**How it differs from prior work**:
- H2O: proposes cumulative attention but does not compare to other metric families; uses base models + decode timing
- SnapKV: claims superiority over H2O but conflates metric, timing, and model type
- ScissorHands: proposes warm-up attention but evaluates on small/old models, not LongBench QA
- StreamingLLM: static eviction only — no metric comparison

---

## Experimental Design

**Model**: LLaMA-2-7B-chat-hf (meta-llama/Llama-2-7b-chat-hf)

**Dataset**: LongBench v1 (THUDM/LongBench)
- QA tasks: NarrativeQA, HotpotQA, 2WikiMQA, MuSiQue (100 examples each)
- Summarization tasks: GovReport, QMSum (100 examples each)

**Metric conditions**:
- M1: Prefill-Observation (SnapKV-style, W=16)
- M2: Cumulative-Attention-at-Prefill (H2O metric, prefill timing — novel ablation)
- M3: Cumulative-Attention-at-Decode (H2O original)
- M4: Warm-Up Attention (ScissorHands-style, 32-step warmup)
- M5: Attention Entropy (H(i) = -Σ_h Σ_t α_{h,t,i} log(α_{h,t,i} + 1e-9), avg over heads)
- M6: StreamingLLM (static baseline)
- Full KV (upper bound)

**KV budgets**: 40%, 50%, 60% retention

**Statistics**: Bootstrap CI (1000 resamples), 95% CI non-overlapping as significance criterion

**Compute**: ~6 GPU-hours on A100 40GB

---

## Limitations

- Results are on 5-task LongBench subset — generalization to all 21 LongBench tasks is an assumption
- LLaMA-2-7B-chat at 4096-token truncation (model context limit) — longer contexts not evaluated
- H2O-at-prefill (M2) modifies the original H2O design — acknowledged as a design variant, not the original method
- Cross-architecture generalization not tested (Gap 3 / Phase 5 domain)
- Attention entropy metric definition (averaged across heads) may not be optimal formulation

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Hypothesis ID** | H-PrefixObs-v1 |
| **Discussion Convergence** | All 6 criteria met at Exchange 8 |
| **Clarity Verified** | Yes |
| **h-m2 Failure Avoided** | Yes — instruct model, 50% retention, no LoRA interaction |
| **Feasibility** | HIGH — ~6 GPU-hours, standard stack |
| **Remaining Objections** | None blocking Phase 2B |
| **Phase 2B Ready** | Yes |

---

*Generated by Phase 2A — Independent-Controller Self-Play Architecture*
*Research folder: docs/youra_research/*
*Next: Phase 2B — Hypothesis Verification Planning*
