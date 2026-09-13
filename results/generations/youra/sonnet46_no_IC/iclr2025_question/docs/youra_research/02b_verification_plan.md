---
stepsCompleted: ["step-00-init-environment", "step-01-init-parsing",
                 "step-02-input-hypothesis", "step-03-hypothesis-generation",
                 "step-04-hypothesis-inventory", "step-05-risk-analysis",
                 "step-06-dependency-graph", "step-07-timeline-planning",
                 "step-08-dialectical-analysis", "step-09-summary",
                 "step-10-finalize"]
status: complete
completedAt: 2026-08-05T06:44:30Z
workflow: phase2b-planning
mode: incremental
hypothesis_id: H-LayerLensUQ-v2
pipeline_project_id: b2a6df7d-2750-409c-8f12-871a1f069d03
---

# Verification Plan: Depth-Resolved Logit-Lens Uncertainty Signals for Architecture-Robust Hallucination Detection

**Date:** 2026-08-05
**Hypothesis ID:** H-LayerLensUQ-v2
**Confidence:** 0.72
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under white-box, single-greedy-pass inference on TriviaQA and TruthfulQA with LLaMA-2-7B, Mistral-7B-v0.1, and LLaMA-3-8B-Instruct, if hallucination scores are computed as per-layer logit-lens uncertainty statistics (Shannon entropy, max-token probability, adjacent-layer KL divergence of decoded distributions, averaged over answer tokens) with (layer, signal, direction) selected per model on a held-out selection split, then the selected intermediate-layer score achieves test-split AUROC >= 0.60 on both datasets for all three models AND on LLaMA-2-7B exceeds the final-layer entropy baseline (0.5186) with a 95% paired-bootstrap CI on the AUROC difference excluding zero, because intermediate layers preserve the separation between resolved (factual) and unresolved (hallucinated) candidate competition that final-layer output calibration — tokenizer- and tuning-dependent — suppresses.

### 1.2 Alternative Hypothesis (H0)
Per-layer logit-lens statistics carry no separation the final layer lacks: for every screened intermediate layer of LLaMA-2-7B, the 95% paired-bootstrap CI of ΔAUROC(intermediate − final-layer entropy) contains zero, and no model achieves test-split AUROC >= 0.60 on both datasets beyond what final-layer signals provide; cross-dataset layer transfer performs no better than chance layer choice.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | TriviaQA (rc.nocontext) + TruthfulQA (generation) (standard) | Existing real benchmarks with the documented final-layer failure baseline (llama2/TriviaQA 0.5186) — the rescue test is only meaningful on the exact protocol where the failure was recorded; no new benchmarks, no synthetic data, no human evaluation |
| **Model** | LLaMA-2-7B (base) + Mistral-7B-v0.1 (base) + LLaMA-3-8B-Instruct | Identical model set to h-e1 preserves baseline comparability; LLaMA-2-7B is the designated rescue stress test; uniform lens path model.lm_head(model.model.norm(h_l)) across all three; base/instruct asymmetry documented as scope limitation R3 |

**Dataset Details:**
- Source: HuggingFace: mandarjoshi/trivia_qa (validation[:1000]), truthfulqa/truthful_qa (validation, 817)
- Path: HF cache (verified present by h-e1/v1 runs); labels/prompts reused verbatim from h-e1

**Model Details:**
- Type: frozen decoder-only LLMs, 32 layers each, fp16, single GPU
- Source: HuggingFace: meta-llama/Llama-2-7b-hf, mistralai/Mistral-7B-v0.1, meta-llama/Meta-Llama-3-8B-Instruct (HF cache verified by v1)

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Final-layer mean token entropy (h-e1) | AUROC 0.5186/0.5153 (llama2, FAIL), 0.5268/0.5886 (mistral), 0.6583/0.6161 (llama3) | TriviaQA/TruthfulQA |
| Final-layer max-token probability | Single-pass confidence foil at output layer (within-sweep) | TriviaQA/TruthfulQA |
| FEPoID + hidden-state probing | AUROC avg 0.7253 (LLaMA-3.1-8B-It), 0.8531 (Mistral-7B-It) — supervised skyline, deferred to Phase 5 | CoQA/SQuAD/HotpotQA/TriviaQA/PsiLoQA |
| Semantic Entropy [Farquhar et al., 2024] | AUROC 0.5311/0.6560 avg in FEPoID comparison; 10x inference cost — excluded direction | QA benchmarks |
| SAPLMA [Azaria & Mitchell, 2023] | 71-83% accuracy (topic-held-out); supervised probe | True-False + generated statements |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Raw logit lens yields valid (non-degenerate) decoded distributions on enough intermediate layers of all three models to permit selection | LLaMA/Mistral lineage best-behaved lens case [Belrose et al., 2023]; v1 archive ran extraction healthily | Degeneracy screen rejects most layers; fallback to tuned-lens translators (trained components — claim vocabulary relabeled for that variant) |
| A2 | h-e1 labels, prompts, answer-span extraction reusable verbatim, reproducing final-layer reference AUROCs within ±0.03 | Labels/templates preserved in v1 archive; identical protocol re-run mid-flight in v1 | Baseline anchor fails — ALL downstream comparisons uninterpretable; pipeline must halt and reconcile (mandatory protocol-validity gate) |
| A3 | Mean-over-answer-tokens aggregation not dominated by end-of-sequence noise for short-form QA | TriviaQA/TruthfulQA greedy answers short-form; FST degradation concerns 30-token instruct rambles; per-token statistics cached for truncated-aggregation ablation | Aggregation noise depresses all AUROCs; run cached FST-style truncated ablation offline; adopt with documented deviation if it rescues |
| A4 | Selection split (500/408 examples) suffices to select (layer, signal, direction) from ~192 candidates without destructive overfitting | Single discrete argmax over smooth AUROC(layer) curves is low-complexity; h-e1 CI machinery (n=1000 bootstrap) quantifies uncertainty | Test AUROC systematically below selection AUROC beyond CI width; report both splits, widen to top-k layer ensembling as documented deviation |
| A5 | AUROC under standard correct/incorrect labels measures hallucination separation, not merely question familiarity | Standard protocol across the field (FEPoID, SAPLMA, h-e1); Chi et al. 2025 challenge scoped out causally | Claims remain valid as stated (separation under standard labels); direction-pattern diagnostic flags familiarity-like behavior; causal disentanglement out of scope (R1) |

### 1.6 Research Gap & Novelty

**Gap (GAP-001):** No training-free, single-pass evaluation of raw logit-lens uncertainty statistics (entropy / max-prob) as per-layer hallucination-detection AUROC scores exists in the literature.

**Preserved Novelty:** First AUROC evaluation of raw logit-lens uncertainty statistics (per-layer entropy, max-prob, adjacent-layer KL) as training-free, single-pass hallucination-detection scores with per-model held-out layer selection; first cross-dataset layer-transfer measurement for hallucination detection; first controlled rescue test on an architecture with a documented final-layer failure baseline.

**Key Innovation:** Reading uncertainty BEFORE final-layer calibration via per-model depth selection — turning the interpretability community's per-layer entropy instrument (Entropy-Lens) into a detection score, with the h-e1 failure record providing a unique falsification anchor no external work possesses.

**Differentiation:** Entropy-Lens computes the identical feature as a computation signature, never for detection. FEPoID solves the task with supervised MLP probes and intrinsic-dimension selection. Kim et al. 2025's negative result concerns final-prediction-token trajectories (tuned lens, MCQ) — a strictly narrower measurement, answered by scope. SAPLMA requires a trained probe. END/DoLa/SLED use cross-layer shifts only at decoding time. h-e1 (own prior failure) read one scalar at the final layer. HalluShift overlap: formal novelty check scheduled this phase.

**Scope Reduction:** 62% — 5 of 8 core claims are BUILD_ON (cited, not re-verified); only 3 PROVE_NEW claims decomposed here: (1) per-layer signal existence + LLaMA-2 rescue (P1), (2) cross-dataset layer transfer (P2, separable), (3) KL-entropy fusion complementarity (P3, quarantined trained component).

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism (rescue, P1) | MUST_WORK | H-E1 | BLOCKED |
| H-M2 | Mechanism (robustness, P4) | SHOULD_WORK | H-M1 | BLOCKED |
| H-M3 | Mechanism (fusion, P3) | SHOULD_WORK | H-E1 | BLOCKED |
| H-C1 | Condition (transfer, P2) | SHOULD_WORK | H-E1 | BLOCKED |

---

### 2.2 Hypothesis Specifications

#### H-E1: Intermediate-Layer Signal Existence

**Type:** EXISTENCE
**Statement:** Under white-box single-greedy-pass inference on TriviaQA and TruthfulQA, if per-layer logit-lens statistics (entropy, max-prob, adjacent-layer KL; mean over answer tokens) are computed at every intermediate layer, then at least one screened (layer, signal) pair per model exhibits class-separable statistics on the selection split (corrected AUROC >= 0.55, both datasets), because unresolved candidate competition for hallucinated answers leaves separation in token space at depth.

**Rationale:** The signal must EXIST in token space at depth before any selection, rescue, transfer, or fusion claim is testable. LLaMA-2-7B is the binding existence case — its documented final-layer failure (0.5186) is exactly what depth reading must escape.

**Variables:**
- IV: readout_layer (1-31 screened), signal_type (3 levels), model_family (3 levels)
- DV: AUROC_corrected on selection split
- CV: greedy decoding, h-e1-verbatim prompts/labels, fp16/float32 numerics

**Verification Protocol:**
1. Load datasets with h-e1-verbatim prompts/labels; stratified 50/50 selection/test split per dataset (seed 42); write and lock test split.
2. Smoke run (10 examples/model, shape + memory assert), then full sweep: 1,817 examples x 3 models, single greedy pass with teacher-forced re-forward, streaming 3 signals x 32 layers per example to scalar CSV (reuse v1 code + 871/1000 llama2/TriviaQA cache where protocol-identical).
3. Reproduce h-e1 final-layer references within ±0.03 (A2 halt gate).
4. Apply degeneracy screen on selection split (drop layers with entropy within 1% of ln|V| OR top-1 agreement with final layer < 5%).
5. Evaluate existence criterion per model on selection split.

**Success Criteria:**
- Primary: >= 1 screened (layer, signal) pair per model with selection-split corrected AUROC >= 0.55 on both datasets
- Secondary: A2 anchor reproduced ±0.03; screen retains >= 5 layers per model

**Gate:**
- Type: MUST_WORK
- If Fail: separation absent in token space at depth — entire tree dies; if failure is screen-driven (A1), tuned-lens fallback is a documented pivot with relabeled claims

**Prerequisites:** None

**Source:** Phase 2A SH1, causal step 1, P1

---

#### H-M1: LLaMA-2-7B Rescue (Calibration Suppression)

**Type:** MECHANISM
**Statement:** Under the locked test split, if the (layer, signal, direction) tuple selected per model on the selection split is evaluated frozen, then LLaMA-2-7B achieves test AUROC >= 0.60 on both datasets AND its paired ΔAUROC vs the final-layer mean-entropy baseline on TriviaQA has a 95% bootstrap CI excluding zero, because final-layer output calibration suppresses a separation that intermediate layers preserve.

**Rationale:** This is the primary falsification gate (P1) — inherited from the gate that killed h-e1, so the hypothesis cannot be talked past its own death condition. The within-model comparison cancels tokenizer/tuning confounds by construction.

**Variables:**
- IV: readout_layer (selected intermediate vs final layer 32, within model)
- DV: AUROC_corrected (test), delta_AUROC_rescue (paired bootstrap n=1000, 95% percentile CI)
- CV: direction sign frozen from selection split; test split read once

**Verification Protocol:**
1. Select (layer, signal, direction) per model on selection split only; freeze all choices.
2. Evaluate frozen tuples on locked test split; compute corrected AUROC per cell.
3. Paired percentile bootstrap (n=1000, example-level resampling, both scores per resample) for ΔAUROC vs final-layer entropy on TriviaQA.
4. Run diagnostics: raw-direction pattern report (familiarity flag, R1), length-stratified AUROC on selected layers (A3/label-noise check).

**Success Criteria:**
- Primary: LLaMA-2-7B test AUROC >= 0.60 on both datasets AND ΔAUROC CI(2.5%, 97.5%) > 0 on TriviaQA
- Secondary: selection-split → test-split AUROC drop within CI width (A4 overfit check)

**Gate:**
- Type: MUST_WORK
- If Fail: Tier 1 fails — depth-resolved hypothesis dies at the same gate that killed h-e1; trigger reflection/SUPERSEDED routing

**Prerequisites:** H-E1

**Source:** Phase 2A causal step 2, P1, SH2

---

#### H-M2: Architecture Robustness + No-Regression

**Type:** MECHANISM
**Statement:** Under the same frozen evaluation, if suppression severity is architecture/tuning-dependent, then all six model x dataset cells achieve test AUROC >= 0.60 AND on Mistral-7B and LLaMA-3-8B (the h-e1-passing architectures) the selected intermediate layer's AUROC is >= final-layer AUROC − 0.02 per dataset, because reading before calibration must not sacrifice architectures where final-layer readout already worked.

**Rationale:** Tier 2 robustness: the depth-resolved pivot is only "architecture-robust" if it rescues LLaMA-2 without regressing the passing models (P4, Exchange 10). Improvement patterns vs tuning status stay descriptive (R3: llama3 is the only instruct model).

**Variables:**
- IV: model_family (3 levels), readout_layer (selected vs final, within model)
- DV: AUROC_corrected per cell; within-model AUROC difference on passing models
- CV: same sweep, same frozen tuples, locked test split

**Verification Protocol:**
1. From the same frozen test-split evaluation, tabulate corrected AUROC for all six cells.
2. Check >= 0.60 in every cell (Tier 2 robustness clause).
3. Check intermediate >= final − 0.02 on all four passing-model cells (no-regression clause).
4. Report depth-of-selected-layer pattern across families as descriptive observation only (R3).

**Success Criteria:**
- Primary: all six cells >= 0.60
- Secondary: no-regression clause holds on all four mistral/llama3 cells

**Gate:**
- Type: SHOULD_WORK
- If Fail: PIVOT — claims narrow to the rescued architecture(s); "architecture-robust" headline dropped, per-model applicability documented

**Prerequisites:** H-M1

**Source:** Phase 2A causal step 3, P4

---

#### H-M3: KL-Entropy Fusion Complementarity

**Type:** MECHANISM
**Statement:** Under the frozen selection-split fits, if adjacent-layer KL (belief-revision "turbulence") carries signal complementary to entropy (distribution "width"), then a 2-parameter logistic fusion of best entropy-family + best KL signal exceeds the best single signal's test AUROC by >= 0.02 with paired bootstrap CI excluding zero in a majority of the six cells, because the mechanism's two facets — elevated width and persistent revision — are distinct symptoms of unresolved competition.

**Rationale:** Tests the two-facet reading of the mechanism (P3). Explicitly a trained component, quarantined from the training-free headline claim; a null result is informative (turbulence redundant with width) rather than fatal.

**Variables:**
- IV: signal combination (fusion vs best single)
- DV: fusion_gain (paired bootstrap CI, per cell)
- CV: 2-coefficient logistic fit on selection split only; test locked

**Verification Protocol:**
1. Fit 2-parameter logistic fusion (best entropy-family + best KL signal) on selection split per model-dataset cell.
2. Evaluate frozen fusion on locked test split.
3. Paired bootstrap (n=1000) on fusion_gain per cell; count cells with gain >= 0.02 and CI excluding zero.

**Success Criteria:**
- Primary: fusion gain >= 0.02 with CI excluding zero in >= 4 of 6 cells
- Secondary: KL-alone AUROC reported per cell (signal-family characterization)

**Gate:**
- Type: SHOULD_WORK
- If Fail: EXPLORE — informative null; mechanism's two-facet reading weakened but rescue claim unaffected; report as negative finding

**Prerequisites:** H-E1

**Source:** Phase 2A P3, PROVE_NEW claim 3

---

#### H-C1: Cross-Dataset Layer Transfer (Boundary Condition)

**Type:** CONDITION
**Statement:** Under frozen per-model selection, if the (layer, signal, direction) tuple selected on dataset A is evaluated on dataset B's locked test split, then its AUROC is within 0.05 of the natively selected tuple's AUROC and >= 0.60, in both directions (TriviaQA↔TruthfulQA) per model, because the selected layer reflects a model property (calibration depth) rather than a dataset artifact.

**Rationale:** Decides deployable-constant vs per-domain-calibration — an unmeasured, deployment-decisive quantity (no published numbers exist). Genuinely uncertain (R2: FEPoID variability, SAPLMA layer shift are counter-evidence); a failure stands alone and must NOT contaminate the H-M1 verdict.

**Variables:**
- IV: selection_dataset vs evaluation_dataset (transfer matrix, both directions)
- DV: transfer_AUROC_gap (tolerance on AUROC scale; layer-index matching rejected as criterion)
- CV: within-model transfer only; locked test splits

**Verification Protocol:**
1. Cross-evaluate each model's selected tuple from dataset A on dataset B's locked test split, both directions.
2. Compute transfer_AUROC_gap vs natively selected tuple per model per direction.
3. Check gap <= 0.05 AND transferred AUROC >= 0.60 for all cells; report per-model verdicts separably from H-M1.

**Success Criteria:**
- Primary: transfer gap <= 0.05 AND transferred AUROC >= 0.60, both directions, per model
- Secondary: pre-interpreted failure reading — per-domain selection required (publishable either way)

**Gate:**
- Type: SHOULD_WORK
- If Fail: EXPLORE — transfer fails for that model; finding stands alone (per-domain selection required); does not contaminate H-M1/P1 verdict

**Prerequisites:** H-E1

**Source:** Phase 2A P2, PROVE_NEW claim 2, scope R2

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2
  ├──→ H-M3   (parallel-eligible after H-E1; executed sequentially)
  └──→ H-C1   (parallel-eligible after H-E1; executed sequentially)
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | ≥1 screened (layer, signal) pair per model, selection-split AUROC ≥ 0.55 both datasets; A2 anchor ±0.03 | STOP — tree dies; A1 screen-driven failure → tuned-lens pivot (relabeled claims) |
| H-M1 | MUST_WORK | LLaMA-2-7B test AUROC ≥ 0.60 both datasets AND ΔAUROC CI > 0 on TriviaQA | Tier 1 fail — hypothesis dies; reflection/SUPERSEDED routing |
| H-M2 | SHOULD_WORK | All 6 cells ≥ 0.60 AND no-regression on mistral/llama3 (≥ final − 0.02) | PIVOT — narrow claims to rescued architecture(s) |
| H-M3 | SHOULD_WORK | Fusion gain ≥ 0.02 with CI excluding zero in ≥ 4/6 cells | EXPLORE — informative null, report negative finding |
| H-C1 | SHOULD_WORK | Transfer gap ≤ 0.05 AND transferred AUROC ≥ 0.60, both directions, per model | EXPLORE — per-domain selection finding, separable from H-M1 |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| A — Foundation | H-E1 (sweep + anchor + screen + selection) | 2 weeks (W1-2) |
| B — Core Mechanism | H-M1 (rescue) | 1 week (W3) |
| C — Extensions | H-M2 (W4), H-M3 (W5) | 2 weeks (W4-5) |
| C — Conditions | H-C1 (transfer matrix) | 1 week (W6) |

**Total Duration:** 6 weeks (2 + 3 H-M + 1 H-C); note: wall-clock is compute-dominated by the Phase A sweep — H-M1 through H-C1 are analysis-only passes over the streamed scalars and can compress substantially in practice.

---

## 4. Risk Analysis

Seven-risk register validated by expert panel (ClearThought collaborative reasoning: methodologist, systems engineer, interpretability researcher): five assumption-derived risks (A1-A5) plus two new risks surfaced in review — infrastructure interruption recurrence (the v1 run died at 871/1000 samples from a routing restart, not science) and HalluShift novelty overlap (formal check scheduled). Panel consensus: the A2 anchor check must run FIRST, before the full sweep; A4 selection overfit is the top statistical risk; empirical signal absence on LLaMA-2 is priced by the MUST_WORK gates rather than listed as a mitigable risk. Archon KB search returned no additional relevant failure cases; the governing failure record is `failure_h-e1_run1` (Serena memory), already integrated as the baseline anchor. Note: risk IDs here (RISK-n) are distinct from Phase 2A permanent caveats R1-R4.

### 4.1 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| RISK-1 Lens degeneracy | A1 | H-E1 (+ all downstream) | High |
| RISK-2 Anchor reproduction failure | A2 | ALL (halt gate) | Medium |
| RISK-3 Aggregation noise | A3 | H-E1, H-M1, H-M2 | Medium |
| RISK-4 Selection overfit | A4 | H-M1, H-M2, H-M3, H-C1 | High |
| RISK-5 Recall shadow | A5 | ALL (interpretation only) | Medium |
| RISK-6 Interruption recurrence | New (v1 history) | H-E1 (sweep stage) | Medium |
| RISK-7 HalluShift novelty overlap | New (Phase 2A open question) | Novelty claim (no gate) | Low |

### 4.2 Mitigation Strategies

**RISK-1: Lens degeneracy (A1)** — Severity: High (Low-Medium likelihood x High impact)
- Prevention: LLaMA/Mistral lineage chosen as best-behaved lens case [Belrose et al., 2023]; uniform lens path across families.
- Detection: degeneracy screen on selection split (entropy within 1% of ln|V| OR top-1 agreement with final layer < 5%); early warning = screen retains < 5 layers on any model.
- Response: PIVOT to tuned-lens translators with claim vocabulary relabeled (trained components); SCOPE to models passing the screen; ABORT only if all models fail the screen.

**RISK-2: Anchor reproduction failure (A2)** — Severity: Medium (Low likelihood x High impact; mandatory halt gate)
- Prevention: reuse h-e1 prompts/labels/answer-span extraction verbatim; verify protocol-identity of v1 cache via prompt + label hashes before reuse.
- Detection: final-layer reference AUROCs outside ±0.03 of h-e1 records (llama2 .5186/.5153, mistral .5268/.5886, llama3 .6583/.6161); run this check FIRST, before the full sweep.
- Response: HALT and reconcile labels/prompts — no downstream result is interpretable until the anchor reproduces.

**RISK-3: Aggregation noise (A3)** — Severity: Medium
- Prevention: short-form QA answers bound end-of-sequence noise; per-token statistics cached during sweep at no extra cost.
- Detection: length-stratified AUROC on selected layers diverges across strata.
- Response: run cached FST-style truncated-aggregation ablation offline; if it rescues, adopt with documented deviation.

**RISK-4: Selection overfit (A4)** — Severity: High (Medium likelihood x High impact)
- Prevention: all selection-sensitive operations (screen, selection, direction freezing, fusion fitting) confined to selection split; test split locked, read once; paired bootstrap on differences.
- Detection: early warning = test-split AUROC systematically below selection-split AUROC beyond CI width (reported explicitly).
- Response: SCOPE — report both splits honestly; widen to top-k layer ensembling only as a documented deviation.

**RISK-5: Recall shadow (A5)** — Severity: Medium (High likelihood x Low claim-impact)
- Prevention: claims scoped to "separation under standard labels", never "truthfulness detection" (R1 caveat).
- Detection: direction-pattern diagnostic flags familiarity-like behavior across models/datasets.
- Response: report the diagnostic; causal disentanglement remains explicitly out of scope — claims stand as stated.

**RISK-6: Interruption recurrence (new)** — Severity: Medium
- Prevention: streaming per-example scalar CSV (no hidden-state stacks); resumable sweep keyed by example ID; reuse 871/1000 llama2/TriviaQA cache after protocol-identity verification.
- Detection: sweep progress monitoring; phased error checks as in v1.
- Response: resume from streamed scalars — no recomputation of completed examples.

**RISK-7: HalluShift novelty overlap (new)** — Severity: Low
- Prevention: differentiation already argued from abstract (internal distribution-shift features ≠ per-layer logit-lens KL from single greedy pass).
- Detection: formal novelty check against HalluShift (arXiv 2504.09482) feature list before Phase 2C.
- Response: SCOPE — narrow the novelty claim to the untested cells (per-layer selection, transfer matrix, rescue test); detection claims unaffected.

### 4.3 Risk Summary

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| RISK-1 | Lens degeneracy rejects layers | A1 | High | H-E1+ | Screen + tuned-lens fallback (relabeled claims) |
| RISK-2 | h-e1 anchor fails ±0.03 | A2 | Medium | ALL | Anchor check first; halt and reconcile |
| RISK-3 | EOS noise depresses AUROCs | A3 | Medium | H-E1, H-M1-2 | Cached truncated-aggregation ablation |
| RISK-4 | 192-candidate selection overfit | A4 | High | H-M1-3, H-C1 | Split discipline; selection-vs-test drop reporting |
| RISK-5 | Familiarity, not truthfulness | A5 | Medium | ALL (interp.) | Scoped vocabulary + direction diagnostic |
| RISK-6 | Sweep interrupted again | v1 history | Medium | H-E1 | Streaming resumable scalars + cache reuse |
| RISK-7 | HalluShift overlap | Open question | Low | Novelty | Formal check before Phase 2C |

Critical: 0 | High: 2 | Medium: 4 | Low: 1

---

## 5. Dependency Graph & Timeline

### 5.1 DAG

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence: signal at depth + A2 anchor)  [MUST_WORK]
         │
         ├────────────────┬────────────────┐
         ▼                ▼                ▼
[Level 1]
    H-M1 (Rescue)    H-M3 (Fusion)    H-C1 (Transfer)
    [MUST_WORK]      [SHOULD_WORK]    [SHOULD_WORK]
         │
         ▼
[Level 2]
    H-M2 (Robustness + No-Regression)  [SHOULD_WORK]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2
Execution: sequential (incremental mode); H-M3/H-C1 are
logically independent of H-M1's verdict (separability by
design: a P2/P3 failure must not contaminate P1)
═══════════════════════════════════════════════════════════
```

**Verification Phases & Gates:**

- **Phase A — Foundation:** H-E1. Gate 1 (MUST_WORK): existence + anchor. Fail → STOP, reassess entire hypothesis (or A1 tuned-lens pivot).
- **Phase B — Core Mechanism:** H-M1. Gate 2 (MUST_WORK): the P1 rescue — the same gate that killed h-e1. Fail → SUPERSEDED routing.
- **Phase C — Extensions:** H-M2, H-M3, H-C1. Gate 3 (SHOULD_WORK): failures narrow scope or produce informative nulls; none invalidates the Tier 1 verdict.

No circular dependencies detected.

### 5.2 Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 1 | H-M3 | H-E1 | SHOULD_WORK |
| 1 | H-C1 | H-E1 | SHOULD_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1  │ W2  │ W3  │ W4  │ W5  │ W6  │
─────────────────┼─────┼─────┼─────┼─────┼─────┼─────┤
PHASE A: Foundation
  H-E1           │ ████│ ████│     │     │     │     │
  [Gate 1]       │     │  ◆  │     │     │     │     │
─────────────────┼─────┼─────┼─────┼─────┼─────┼─────┤
PHASE B: Core Mechanism
  H-M1           │     │     │ ████│     │     │     │
  [Gate 2]       │     │     │  ◆  │     │     │     │
─────────────────┼─────┼─────┼─────┼─────┼─────┼─────┤
PHASE C: Extensions & Conditions
  H-M2           │     │     │     │ ████│     │     │
  H-M3           │     │     │     │     │ ████│     │
  H-C1           │     │     │     │     │     │ ████│
  [Gate 3]       │     │     │     │     │     │  ◆  │
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path

```
Critical Path: H-E1 → H-M1 → H-M2  (gate-relevant path: 4 weeks)
Sequential schedule: H-E1 → H-M1 → H-M2 → H-M3 → H-C1 (6 weeks)

Total Duration: 6 weeks = 2 (H-E1) + 3 (H-M1-3) + 1 (H-C1)
Slack: H-M3 and H-C1 have 0 slack in the sequential schedule but
are parallel-eligible after Phase A artifacts (frozen selections,
streamed scalars) exist — they gate nothing on the critical path.
```

The schedule is front-loaded by design: Phase A contains all GPU compute (1,817 examples x 3 models sweep) and both MUST_WORK preconditions (A2 anchor, existence). Everything after W2 is CPU-side analysis of streamed scalars, so a Gate 1 failure kills the plan at 1/3 of the timeline cost.

### 5.5 Resources

```
Total Hypotheses: 5
- Existence: 1 (H-E1)
- Mechanism: 3 (H-M1, H-M2, H-M3)
- Condition: 1 (H-C1)

Verification Phases: 3 (A Foundation, B Core Mechanism, C Extensions/Conditions)
Compute: single GPU (fp16, 7-8B models); full sweep 1,817 examples x 3 models,
  single greedy pass + teacher-forced re-forward; ~871/1000 llama2/TriviaQA
  reusable from v1 cache after protocol-identity verification
Data: TriviaQA rc.nocontext validation[:1000] + TruthfulQA generation
  validation (817) — full standard splits, no subsampling
Storage: streaming per-example scalar CSV (3 signals x 32 layers per example);
  per-token statistics cached for A3 ablation
Total Duration: 6 weeks | Execution Mode: Sequential chain
```

### 5.6 Execution Order

1. **Execute H-E1** (W1-2): lock splits → A2 anchor check FIRST (halt on failure) → smoke run → full sweep with streaming/resumable writes → degeneracy screen → per-model selection → existence readout.
2. **Evaluate Gate 1** (MUST_WORK): existence + anchor pass → proceed; fail → STOP (or A1 tuned-lens pivot).
3. **Execute H-M1** (W3): frozen test-split evaluation, paired bootstrap ΔAUROC rescue on LLaMA-2-7B + diagnostics.
4. **Evaluate Gate 2** (MUST_WORK): Tier 1 rescue pass → proceed; fail → reflection/SUPERSEDED routing.
5. **Execute H-M2** (W4): six-cell robustness + no-regression clauses.
6. **Execute H-M3** (W5): fusion fits (selection split) + frozen test evaluation.
7. **Execute H-C1** (W6): transfer matrix, both directions, per model.
8. **Evaluate Gate 3** (SHOULD_WORK): record scope narrowings/informative nulls → verification complete → Phase 4.5 synthesis.

---

## 6. Dialectical Analysis

Thesis-Antithesis-Synthesis evaluation of H-LayerLensUQ-v2 against its null hypothesis, run via ClearThought structured argumentation (3 chained arguments: thesis 0.72, antithesis 0.40, synthesis 0.80). The antithesis is built from H0 plus the strongest external attackers (Kim et al. 2025 trajectory alignment, Belrose lens bias, FEPoID geometry alternative, Chi familiarity challenge, A4 selection overfit).

### 6.1 Thesis

**Core Claim:** Per-layer logit-lens uncertainty statistics with per-model held-out (layer, signal, direction) selection achieve detection AUROC >= 0.60 on both datasets for all three models, including a CI-separated rescue of LLaMA-2-7B where final-layer entropy failed at 0.5186 — because intermediate layers preserve the resolved/unresolved candidate-competition separation that final-layer calibration suppresses.

**Supporting Evidence:**
1. Intermediate>final signal consensus (FEPoID, LLMs-Know-More, Layer-by-Layer — BUILD_ON) and Entropy-Lens's validated mechanistic reading of per-layer entropy (Spearman 0.74-0.88).
2. The mechanism retrodicts BOTH h-e1 anomalies: the llama2 miss (0.5186) and the TriviaQA direction inversion; the same statistic works on llama3-instruct (0.6583) — calibration varies by model.
3. SAPLMA proves information exists at intermediate depth; the only open question is whether it survives unembedding into token space.

**Strengths:** anchored at both ends (published consensus + own failure record as falsification anchor); numeric criteria and explicit falsifiers on all predictions; within-model rescue cancels confounds by construction.

**Expected Outcomes:** P1 pass (moderate-high), P3 pass (moderate), P2 genuinely uncertain, P4 pass (guard).

### 6.2 Antithesis

**Null Hypothesis (H0):** Per-layer logit-lens statistics carry no separation the final layer lacks: every screened intermediate layer's ΔAUROC CI on LLaMA-2-7B contains zero; no model clears 0.60 on both datasets beyond final-layer performance; transfer is no better than chance layer choice.

**Counter-Arguments:**
1. Kim et al. 2025: certain/uncertain layer-wise trajectories largely ALIGNED (5 models x 11 datasets) — the nearest measurement found nothing at depth.
2. The raw logit lens is a biased, family-dependent instrument (Belrose 2023) — intermediate readouts may be instrument artifacts.
3. The intermediate-layer signal may live in hidden-state geometry (FEPoID) and die at unembedding — supervision, not depth, may be what works.
4. 192-candidate selection over 500/408 examples can manufacture apparent rescue via overfit (A4/RISK-4).
5. AUROC may track familiarity/recall, not hallucination (Chi et al. 2025 — A5/RISK-5); the h-e1 direction inversion is consistent with a recall artifact.

**Potential Failure Points:** RISK-1 (screen guts LLaMA-2's layer pool), RISK-4 (test-split collapse of selected tuples), RISK-3 (aggregation noise floor).

**H0 Supported If:** all LLaMA-2 ΔAUROC CIs straddle zero (P1 falsifier — the gate that killed h-e1); no screened layer separates on any model (H-E1 falsifier); transfer gaps exceed tolerance everywhere (P2 falsifier).

### 6.3 Synthesis

**Balanced Assessment:** Thesis and antithesis disagree only about the open middle of the causal chain — whether separation survives unembedding into token space at depth — and that is precisely what H-E1/H-M1 adjudicate empirically. Every antithesis attack is already internalized by the plan as a gate, diagnostic, or scope boundary: token-space-vs-geometry → measured by H-E1/H-M1; selection overfit → split discipline + frozen directions + reported selection-vs-test drop; familiarity → direction-pattern diagnostic + claim scoped to "separation under standard labels"; transfer skepticism → P2 demoted to separable SHOULD_WORK condition; Kim's alignment → answered by measurement-scope boundary (single-token trajectories ≠ full-distribution statistics), with his own 97%-positive PD correlations conceding residual signal.

**Resolution Path:** (1) Foundation verification H-E1 establishes existence before mechanism; (2) sequential gated testing H-M1 → H-M2/M3/C1 separates the death condition from scope-narrowing failures; (3) the ±0.03 anchor makes both spurious passes and spurious fails detectable.

**Conditions for Thesis Support:** Gates 1-2 pass (existence + CI-separated rescue) with frozen protocol.
**Conditions for Antithesis Support:** H-E1 or H-M1 fail — single-pass token-space statistics exhausted; geometry/recall explanations promoted (informative negative, publishable).
**Nuanced Outcomes:** Tier 1 pass + Tier 2/P2/P3 failures → refined thesis with narrowed scope (per-domain selection, single-architecture rescue, redundant KL) — all pre-interpreted by the two-tier frozen gates.

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Separation survives into token space at depth | Kim alignment; lens artifacts | H-E1 (screened, selection split) |
| Mechanism | Calibration suppression, retrodicts h-e1 | Geometry-only signal; overfit rescue | H-M1 with frozen protocol + drop reporting |
| Robustness | Architecture-robust via per-model selection | Regression on passing models | H-M2 no-regression clause |
| Scope | Layer is a model property (transfers) | FEPoID/SAPLMA variability | H-C1 separable transfer matrix |
| Interpretation | Hallucination separation | Familiarity/recall shadow | Direction diagnostic + R1 scoping |
| Performance | Beats within-sweep baselines | Marginal vs supervised skyline | Phase 5 (deferred) |

**Overall Robustness Score:** High — the plan cannot be talked past its own death condition; all outcome classes pre-interpreted.

**Confidence in Verification Plan:** 0.72 (P1 moderate-high, P2 genuinely uncertain, P3 moderate — stratification inherited from Phase 2A Exchange 13)

---

## 7. Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** Per-layer logit-lens uncertainty statistics (entropy, max-prob, adjacent-layer KL) with per-model held-out selection achieve hallucination-detection AUROC >= 0.60 on TriviaQA + TruthfulQA for 3 models, including a CI-separated rescue of LLaMA-2-7B (final-layer failure: 0.5186).
- ID: H-LayerLensUQ-v2, Confidence: 0.72

**Verification Structure:**
- Mode: Incremental (62% scope reduction — 5 of 8 claims BUILD_ON)
- Sub-Hypotheses: 5 total — H-E: 1, H-M: 3, H-C: 1
- Phases: 3 phases over 6 weeks (compute front-loaded in Phase A)
- Critical Gates: 3 decision points (2 MUST_WORK, 1 SHOULD_WORK)

**Risk Assessment:** Medium
- Primary concerns: RISK-4 selection overfit (192 candidates), RISK-1 lens degeneracy (tuned-lens fallback ready)

**Immediate Action:** Begin Phase A with H-E1 — A2 anchor check FIRST, before the full sweep.

### 7.2 Final Summary

**Key Achievements:**
- 5 hypotheses across 3 gated phases decompose exactly the 3 PROVE_NEW claims (P1 rescue → H-E1/H-M1/H-M2, P3 fusion → H-M3, P2 transfer → H-C1); BUILD_ON claims cited, not re-tested
- H0 addressed: every antithesis attack (Kim alignment, lens bias, geometry alternative, overfit, familiarity) mapped to a gate, diagnostic, or scope boundary
- P1/P2 separability preserved by design: a transfer failure cannot contaminate the rescue verdict

**Verification Execution Order:**
- **Phase A — Foundation** (2 wks): H-E1 (splits → anchor → sweep → screen → selection). Gate 1: MUST PASS.
- **Phase B — Core Mechanism** (1 wk): H-M1 rescue on locked test split. Gate 2: MUST PASS.
- **Phase C — Extensions/Conditions** (3 wks): H-M2 robustness, H-M3 fusion, H-C1 transfer. Gate 3: failures narrow scope, don't invalidate.

### 7.3 Conclusions

**Critical Decision Points:**
1. **Gate 1 (H-E1):** FAIL → STOP and reassess (screen-driven → tuned-lens pivot with relabeled claims); PASS → Phase B.
2. **Gate 2 (H-M1):** FAIL → Tier 1 dead, reflection/SUPERSEDED routing to Phase 2A; PASS → Phase C.
3. **Gate 3 (H-M2/M3/C1):** failures produce narrowed claims or informative nulls — all pre-interpreted.

**Open Questions (from Phase 2A):**
- Does the TriviaQA-selected layer transfer to TruthfulQA within ±0.05 AUROC (P2 — genuinely uncertain)?
- Is adjacent-layer KL complementary or redundant with entropy (P3)?
- Do informative layers cluster at 40-80% relative depth (exploratory, ungated, descriptive per R3)?
- Does the degeneracy screen retain enough LLaMA-2 layers (A1)?
- HalluShift feature overlap — formal novelty check before Phase 2C (RISK-7).

**Recommendations:**
1. **Immediate:** run A2 anchor reproduction before any sweep; verify v1 cache protocol-identity (prompt/label hashes) before reuse.
2. **Resources:** 6 weeks nominal; GPU needed only in Phase A — reserve buffer for one full re-sweep in case of RISK-6 interruption.
3. **Failure management:** report selection-vs-test AUROC drop always (RISK-4 early warning); document deviations (A3 truncated aggregation, A4 top-k ensembling) explicitly.

### 7.4 Appendices

**A. Phase 2A Reference**
- Source: docs/youra_research/03_refinement.yaml (H-LayerLensUQ-v2, schema 10.0.0, GAP-001)
- Supplementary: 02_synthesis.yaml, 01_round_table/final_opinions.yaml (6-persona convergence, exchange 15)

**B. MCP Tool Usage Summary**
- Total MCP calls: 9 ClearThought + 4 Archon
- Tools: scientificmethod (5: H-E1 3-stage, H-M-integrated, H-C-conditions), collaborativereasoning (1: risk panel), structuredargumentation (3: thesis/antithesis/synthesis); Archon (health, project, tasks, KB search)

---
