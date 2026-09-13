# Validated Hypothesis Synthesis

**Generated:** 2026-08-05
**Workflow:** Phase 4.5 Hypothesis Synthesis
**Pipeline Position:** Phase 4 (Hypothesis Loop) → [Phase 4.5] → Phase 6 (Phase 5 skipped by config)

---

## 1. Executive Summary

The original hypothesis H-LayerLensUQ-v2 claimed that per-layer logit-lens uncertainty statistics, with per-model (layer, signal, direction) selection, achieve test-split AUROC ≥ 0.60 on TriviaQA and TruthfulQA for LLaMA-2-7B, Mistral-7B-v0.1, and LLaMA-3-8B-Instruct, and on LLaMA-2-7B beat the final-layer entropy baseline (0.5186) with bootstrap-CI separation — because intermediate layers preserve candidate-competition separation that final-layer output calibration suppresses. The completed experiments (h-e1 PARTIAL, h-e1-v2 PASS) validated the **existence premise** of this claim decisively but did **not** reach the test-split, CI, transfer, or fusion claims: the four dependent hypotheses assigned to predictions P1–P4 (h-m1, h-c1, h-m3, h-m2) ended the episode BLOCKED and never executed.

What the evidence establishes: in **all six model × dataset cells**, at least one screened intermediate layer is class-separable (selection-split corrected AUROC 0.6092–0.7011, gate ≥ 0.55), and in **all six cells** the best screened intermediate layer beats the within-sweep final-layer entropy baseline (margins +0.0035 to +0.130, largest on TriviaQA). The run was full-scale and real (5,451 scored generations, 3 models, H100, REAL_MODEL reality check, 37/37 tests). A second, methodological finding emerged from the h-e1 PARTIAL: the v1-record baseline anchor (0.5186) proved unreproducible **by construction** — its provenance protocol differed in six documented ways — establishing that cross-protocol numeric anchors are invalid and forcing a protocol-internal anchor redesign (A2-v2) that then passed cleanly.

The refined hypothesis therefore keeps only the existence and depth-advantage claims (fully supported), replaces the invalid 0.5186 cross-protocol baseline with within-sweep baselines, demotes the calibration-suppression mechanism from established cause to directionally-supported hypothesis, and explicitly marks the ≥ 0.60 test-split rescue, cross-dataset transfer, and KL-entropy fusion claims as unmeasured. Key limitations: selection-split-only evidence, single seed, no confidence intervals, and the four dependent hypotheses unexecuted — nearly all of which are addressable with zero GPU from the finalized per-example caches.

| Metric | Value |
|--------|-------|
| **Original Core Statement** | Per-model-selected intermediate logit-lens signals achieve test AUROC ≥ 0.60 (all 3 models, both datasets) and rescue LLaMA-2-7B vs the 0.5186 final-layer baseline with CI separation |
| **Refined Core Statement** | Intermediate-layer logit-lens signals are class-separable (selection-split AUROC 0.61–0.70) and beat the within-sweep final layer in 6/6 cells at PoC scale; test-split rescue, transfer, and fusion remain unmeasured |
| **Predictions Supported** | 0 / 4 directly tested (all four INCONCLUSIVE — dependents blocked); existence premise SUPPORTED 6/6 cells |
| **Overall Pass Rate** | h-e1: 66.7% (PARTIAL) · h-e1-v2: 100% (PASS) |
| **Hypotheses Validated** | 1 PASS + 1 PARTIAL→MODIFIED / 6 total (4 BLOCKED, never run) |

---

## 2. Prediction-Result Matrix

Predictions P1–P4 were decomposed by Phase 2B onto dependent hypotheses h-m1 (P1), h-c1 (P2), h-m3 (P3), h-m2 (P4). All four dependents ended the episode BLOCKED (h-e1 gate PARTIAL consumed the loop; h-e1-v2 PASS unblocked them, but the loop terminated before any executed). Per the status assignment rules, a prediction with no direct test is INCONCLUSIVE regardless of favorable precursor evidence.

| Prediction | Original Statement | Tested By | Key Metric | Result | Status | Confidence | Evidence Summary |
|------------|-------------------|-----------|------------|--------|--------|------------|------------------|
| **P1** | LLaMA-2-7B rescue: selected intermediate signal reaches test-split AUROC ≥ 0.60 on both datasets, ΔAUROC vs final-layer entropy CI excluding zero on TriviaQA | h-m1 (BLOCKED, never ran) | test-split AUROC + paired bootstrap CI | Not measured | INCONCLUSIVE | — (precursor evidence favorable) | Selection-split precursors from h-e1-v2: llama2/triviaqa L31 adj_kl 0.6522, llama2/truthfulqa L29 entropy 0.7011 (both ≥ 0.60 on *selection* split); depth margin +0.059/+0.034 as point estimates. Frozen-tuple test-split evaluation and CI never executed. |
| **P2** | Cross-dataset layer transfer: tuple selected on dataset A performs within 0.05 and ≥ 0.60 on dataset B, both directions, per model | h-c1 (BLOCKED, never ran) | transfer AUROC gap | Not measured | INCONCLUSIVE | — (genuinely uncertain, as pre-registered) | No transfer matrix computed. Descriptive precursor: best layers cluster at L28–L31 across datasets within each model (favors transfer), but the winning *signal* differs across datasets in 4/6 cells (transfer must move the full tuple). |
| **P3** | KL-entropy fusion: 2-parameter logistic fusion beats best single signal by ≥ 0.02 with CI excluding zero in majority of cells | h-m3 (BLOCKED, never ran) | fusion gain + CI | Not measured | INCONCLUSIVE | — (complementarity plausible) | No fusion fit. Precursor: entropy-family and adj_kl winners differ across cells (adj_kl wins 3/6, entropy 2/6, maxprob 2/6 as best signal families), consistent with — but not evidence of — complementary information. |
| **P4** | No-regression guard: on Mistral and LLaMA-3, selected intermediate AUROC ≥ final-layer − 0.02 on each dataset | h-m2 (BLOCKED, never ran) | test-split within-model comparison | Not measured | INCONCLUSIVE | — (precursor evidence strongly favorable) | On the selection split, the intermediate layer *strictly beats* the final layer in all four Mistral/LLaMA-3 cells (depth_beats_final), trivially clearing the −0.02 tolerance there; test-split evaluation never performed. The separate ≥ 0.60 level clause is at risk on mistral/triviaqa (selection 0.6092, boundary). |

**Status Legend:** SUPPORTED | PARTIALLY_SUPPORTED | REFUTED | INCONCLUSIVE

**What WAS directly tested — the existence premise (Phase 2B sh1, gate for all of P1–P4):**

| Premise | Tested By | Result | Status | Confidence |
|---------|-----------|--------|--------|------------|
| ≥ 1 screened intermediate (layer, signal) pair per model with selection-split corrected AUROC ≥ 0.55, both datasets | h-e1 (1/6 cells before designed halt), h-e1-v2 (6/6 cells) | 6/6 cells pass, range 0.6092–0.7011 | **SUPPORTED** | HIGH (full-scale real run; single seed, no CI) |
| depth_beats_final: best intermediate > within-sweep final-layer entropy AUROC, per cell | h-e1-v2 | 6/6 cells, margins +0.0035 to +0.130 | **SUPPORTED** (point estimates) | MEDIUM (no CI; one margin is 0.0035) |

### Causal Mechanism Verification

| Mechanism Step | Description | Falsifier | Evidence | Verification Status |
|----------------|-------------|-----------|----------|---------------------|
| 1 | Candidate competition resolves at intermediate depth for factual answers; stays unresolved for hallucinated ones — separable statistics exist in token space at depth | No screened intermediate layer on any model shows class-separable statistics (AUROC ≈ 0.5) | h-e1-v2: 6/6 cells with best intermediate corrected AUROC 0.6092–0.7011 ≥ 0.55; screen retained 20/15/15 layers; falsifier NOT triggered | **VERIFIED** (at PoC/selection-split level) |
| 2 | Final-layer output calibration suppresses this separation at L32 | Intermediate ≤ final on LLaMA-2-7B (CI containing zero) | depth_beats_final in 6/6 cells as point estimates (llama2/triviaqa +0.059; largest llama3/triviaqa +0.130); the specified CI test was never run (h-m1 blocked). Complication: llama2 final layer is NOT at chance under the current protocol (0.5928/0.6669), so suppression is relative, not absolute | **PARTIALLY_VERIFIED** (direction consistent 6/6; statistical separation untested) |
| 3 | Suppression severity is architecture/tuning-dependent — worst in base LLaMA-2, mildest in RLHF-tuned LLaMA-3-Instruct | Improvements appear uniformly with no relation to tuning status, or per-model intermediates still fail on llama2 | Observed depth margins on TriviaQA: llama3-instruct +0.130 > mistral +0.064 > llama2 +0.059 — the **largest** gain is on the model predicted to need it least, contradicting the predicted severity ordering. Descriptive only (R3 scope), one seed | **UNVERIFIED** (descriptive evidence runs contrary to predicted ordering) |

### Planned-vs-Actual Comparison (summary — full table in §5.5)

- **h-e1:** planned 6/6-cell existence sweep + A2 anchor reproduction (±0.03). Actual: anchor breached on cell 1 (Δ +0.0742), designed halt fired after 47 s, 1/6 cells measured. Deviation type: **DESIGN_ISSUE** — the anchor spec adopted cross-protocol reference numbers as a same-protocol gate (Phase 2B/2C spec flaw; implementation verified faithful: donor labels 10/10, 35/35 tests). The existence prediction was *not* refuted — the experiment design prevented it from being fully tested in v1.
- **h-e1-v2:** planned 6/6-cell sweep under A2-v2 protocol-internal anchor. Actual: executed as planned, 6/6 pass, pass_rate 1.0. Deviation type: **NONE** substantive (logged env deviations: conda env swap after v1 env broke, transformers 4.57.1 vs pinned 4.57.6, one test assertion inverted per the mandated Gap C path patch).

### Experiment Design Integrity Assessment

Controlled variables held in both runs: identical prompts/labels (v1-verbatim `data.py`), greedy decoding, seed 42, fp16 weights / float32 statistics, stratified 50/50 splits with test locked, degeneracy screen constants byte-identical. h-e1-v2's donor-cache reuse was identity-verified (10/10 fresh-regeneration label agreement) before use; resume across three session interruptions preserved example_id uniqueness. The h-e1 anchor breach was a spec-provenance flaw, not a control failure — the single measured cell remains valid and was reproduced in v2. Confidence in the 6-cell grid: results are trustworthy *as selection-split point estimates*; the design's known soft spots are single-seed, no CI, and selection-split-only gating (by EXISTENCE-PoC design).

---

## 3. Hypothesis Refinement

### 3.1 Original Core Statement (Phase 2A)

> Under white-box, single-greedy-pass inference on TriviaQA and TruthfulQA with LLaMA-2-7B, Mistral-7B-v0.1, and LLaMA-3-8B-Instruct, if hallucination scores are computed as per-layer logit-lens uncertainty statistics (Shannon entropy, max-token probability, adjacent-layer KL divergence of decoded distributions, averaged over answer tokens) with (layer, signal, direction) selected per model on a held-out selection split, then the selected intermediate-layer score achieves test-split AUROC >= 0.60 on both datasets for all three models AND on LLaMA-2-7B exceeds the final-layer entropy baseline (0.5186) with a 95% paired-bootstrap CI on the AUROC difference excluding zero, because intermediate layers preserve the separation between resolved (factual) and unresolved (hallucinated) candidate competition that final-layer output calibration — tokenizer- and tuning-dependent — suppresses.

### 3.2 Refined Core Statement (Phase 4.5)

> Under white-box, single-greedy-pass inference on TriviaQA and TruthfulQA with LLaMA-2-7B, Mistral-7B-v0.1, and LLaMA-3-8B-Instruct, per-layer logit-lens uncertainty statistics (Shannon entropy, max-token probability, adjacent-layer KL divergence, averaged over answer tokens) are class-separable for hallucination detection at intermediate depth: in all six model × dataset cells, at least one screened intermediate layer — concentrated at L28–L31 — achieves selection-split corrected AUROC ≥ 0.55 (observed 0.6092–0.7011), and in all six cells the best screened intermediate layer exceeds the same sweep's final-layer entropy AUROC (point-estimate margins +0.0035 to +0.130, largest on TriviaQA), under a protocol-internal validity anchor, one seed, and per-model per-dataset selection. This is consistent with — but does not yet establish — the calibration-suppression mechanism. Whether these selection-split signals survive frozen evaluation on locked test splits with CI separation (the original ≥ 0.60 rescue claim), transfer across datasets, or fuse complementarily remains unmeasured: the dependent hypotheses testing P1–P4 were never executed.

**Key Changes:**
1. Test-split AUROC ≥ 0.60 clause (all models, both datasets) — **removed as claim**, demoted to explicit unmeasured prediction (h-m1/h-m2 never ran).
2. "Exceeds the final-layer entropy baseline (0.5186) with 95% CI excluding zero" — **removed**: the 0.5186 reference is cross-protocol-invalid by provenance audit; no CI was computed. Replaced by within-sweep final-layer comparison (0.5928 on the binding cell), point-estimate only.
3. Existence of class-separable intermediate-layer signals — **kept and strengthened** with measured ranges and layer localization (L28–L31).
4. Calibration-suppression mechanism ("because…suppresses") — **weakened** from established cause to "consistent with": direction supported 6/6, CI separation untested, severity-ordering sub-claim contradicted descriptively.
5. Scope qualifier **added**: selection-split evidence, single seed, PoC scale.

### 3.3 Causal Mechanism — Verified Chain

```
Original Chain: Step 1 (separation exists at depth)
             → Step 2 (final-layer calibration suppresses it)
             → Step 3 (suppression severity tracks tuning status)

Verified Chain: Step 1 [VERIFIED — 6/6 cells ≥ 0.55, screen healthy]
             → Step 2 [PARTIALLY_VERIFIED — depth_beats_final 6/6 point
                       estimates; CI separation untested (h-m1 blocked)]
             → Step 3 [UNVERIFIED — observed margin ordering (llama3-instruct
                       largest) contradicts the predicted severity ordering;
                       descriptive only per R3]
```

**Removed/Modified Steps:**
- **Step 3** (tuning-dependent suppression severity): retained as open hypothesis but excluded from the supported chain — the TriviaQA depth-margin ordering (llama3 +0.130 > mistral +0.064 > llama2 +0.059) is the reverse of the prediction that base LLaMA-2 suffers the worst suppression and would gain most from depth readout.

### 3.4 Claims Removed or Weakened

| Original Claim | Action | Reason | Evidence |
|----------------|--------|--------|----------|
| Test-split AUROC ≥ 0.60, all 3 models, both datasets | REMOVE (demote to prediction) | Never measured — test splits locked, untouched; h-m1/h-m2 blocked | verification_state: h-m1/h-m2 validation NOT_STARTED |
| LLaMA-2 rescue vs 0.5186 baseline with CI excluding zero | REMOVE | 0.5186 is cross-protocol (6 documented protocol differences); anchor unsatisfiable by construction; no CI computed | h-e1 anchor forensics (Δ +0.0742/+0.0553); pivot record |
| "Final-layer entropy FAILS on LLaMA-2-7B (chance level)" (premise) | MODIFY | Under the current protocol, llama2 final-layer entropy is 0.5928/0.6669 — weak, direction-inconsistent, but not chance. The "rescue from failure" framing becomes "consistent depth advantage over a weaker final-layer readout" | h-e1 unexpected finding; h-e1-v2 gate grid |
| Intermediate layers preserve separation that final-layer calibration suppresses (mechanism, causal) | WEAKEN | Direction supported in 6/6 cells (point estimates); causal/statistical confirmation and severity ordering untested or contradicted | Gate grid + mechanism table §2 |
| Cross-dataset layer transfer within 0.05 (P2) | REMOVE (demote to prediction) | h-c1 never ran | verification_state |
| KL-entropy fusion gain ≥ 0.02 (P3) | REMOVE (demote to prediction) | h-m3 never ran | verification_state |
| Existence: class-separable intermediate-layer statistics on both datasets, all models | KEEP | Fully supported, 6/6 cells, full-scale real run | h-e1-v2 gate PASS 5/5 criteria |
| Depth advantage claim | KEEP (as point estimate) | depth_beats_final 6/6 | h-e1-v2 gate grid |

### 3.5 Assumptions Status

| Assumption | Original Status | Verification Status | Evidence | Impact if Violated |
|------------|----------------|---------------------|----------|-------------------|
| A1: Raw logit lens non-degenerate on enough intermediate layers | Assumed (Belrose et al. lineage argument) | **VERIFIED** | Degeneracy screen retained 20 (llama2), 15 (mistral), 15 (llama3) layers — all ≥ 5; no tuned-lens fallback needed | Would have forced trained-translator pivot, relabeling claims |
| A2: h-e1 labels/prompts reusable AND v1 reference AUROCs reproducible ±0.03 | Assumed | **VIOLATED (as operationalized)** → re-specified | Labels/prompts reuse verified (10/10 donor agreement) — that half held. Numeric reproduction impossible: reference protocol differed 6 ways; observed Δ +0.0742. Replaced by A2-v2 protocol-internal anchor, which passed all clauses | All cross-protocol baseline comparisons uninterpretable — this materialized; downstream writing must never cite 0.5186-class numbers as same-protocol baselines |
| A3: Mean-over-answer-tokens aggregation not dominated by end-of-sequence noise | Assumed | **UNVERIFIED** | Truncated-aggregation ablation never run. Indirect support only: aggregated signals reached 0.61–0.70 AUROC | Aggregation noise would depress all AUROCs; observed levels suggest tolerable, but untested |
| A4: Selection-split discipline (500/408) selects (layer, signal, direction) without destructive overfitting | Assumed | **UNVERIFIED** | Test-split evaluation never performed (h-m1 blocked); selection-only results cannot assess generalization | Test AUROC could fall systematically below selection AUROC — the central threat to the unmeasured ≥ 0.60 claims |
| A5: AUROC under correct/incorrect labels measures hallucination separation, not question familiarity | Assumed (scoped out causally, R1) | **UNVERIFIED** | Direction-pattern diagnostic logged (final-layer direction inconsistent with v1 record in 2/6 cells); no familiarity-stratified analysis run | Signal could reflect recall/popularity; claims remain valid as stated (separation under standard labels) but interpretation narrows |

---

## 4. Theoretical Interpretation

### 4.1 Mechanistic Explanation (Experiment-Verified)

Our experiments demonstrate that hallucination-relevant uncertainty information **exists in token space at intermediate depth** in all three model families: after degeneracy screening, at least one intermediate layer per model yields a class-separable uncertainty statistic on both datasets (corrected AUROC 0.6092–0.7011), with informative layers concentrated late in the stack (L28–L31 in every cell, plus a secondary L17 site on llama2/triviaqa). This directly supports the first step of the proposed mechanism: for factual versus hallucinated answers, the decoded next-token distributions at depth differ measurably in width (entropy, max-prob) and inter-layer belief revision (adjacent-layer KL).

Our experiments further show that in every cell the best intermediate layer beats the same sweep's final-layer entropy readout (depth_beats_final 6/6, margins +0.0035 to +0.130). This is *consistent with* the calibration-suppression reading — information present at depth is partially attenuated at the output layer — but we have not established it causally: the paired-bootstrap separation test was never run, and one margin (llama3/truthfulqa, +0.0035) is small enough to be noise at this sample size.

Contrary to our initial expectation, the depth advantage does **not** track tuning status as predicted. The severity ordering hypothesized (base llama2 worst-suppressed, instruct llama3 mildest) is descriptively reversed on TriviaQA: llama3-instruct shows the largest depth margin (+0.130). We hypothesize (unverified) that instruct tuning *sharpens* final-layer calibration — strengthening suppression rather than weakening it — which would still be a calibration story, but with the opposite tuning polarity from Phase 2A's version. We also note the depth advantage is dataset-dependent: TruthfulQA final-layer entropy is comparatively strong (0.60–0.67), leaving thin depth margins there.

Signal-family structure: adjacent-layer KL dominates on TriviaQA-style cells (best signal in 3/6 cells, top-3 llama2/triviaqa intermediates all adj_kl), a signal never previously evaluated as a detection score — the "turbulence vs width" distinction motivating P3 remains plausible and untested.

### 4.2 Unexpected Findings Analysis

#### Finding 1: The v1 "final-layer failure at 0.5186" was protocol-specific — the same cell measures 0.5928 under the current protocol

- **Observation:** h-e1's anchor check found llama2/triviaqa final-layer entropy AUROC 0.5928 (selection) / 0.5739 (full set) vs the v1-recorded 0.5186 — a +0.055–0.074 shift for the same model and nominal dataset.
- **Why Unexpected:** The 02c brief treated the v1 record as a reproducible same-protocol anchor with ±0.03 tolerance; it was the motivating "documented failure" for the whole rescue framing.
- **Deviation-type check:** DESIGN_ISSUE (anchor spec), not implementation — provenance audit found six protocol differences (random-sample vs first-slice, bare vs templated prompt, substring vs normalized-alias labels, generation-time vs teacher-forced lens entropy, bfloat16 vs fp16, full-set vs selection-split eval); donor identity separately verified 10/10.
- **Competing Explanations:**
  1. **Protocol sensitivity (measurement change):** prompt template, label rule, and signal definition each plausibly shift AUROC by points; jointly they explain the gap. (Plausibility: HIGH)
  2. **Sampling variance:** different 1000-question samples from a 7,993-question pool. (Plausibility: MEDIUM as contributor — cannot explain the direction stability alone)
  3. **Implementation error in v2 code:** (Plausibility: LOW — 35/35 tests, donor labels 10/10, validator REAL_MODEL)
- **Most Likely Interpretation:** joint protocol sensitivity — AUROC magnitudes for weak signals are not portable across prompt/label/signal/dtype variants; only the *direction* of the effect transferred.
- **Additional Evidence Needed:** factorial re-run toggling each protocol difference on the same cell to attribute the shift.

#### Finding 2: Adjacent-layer KL dominates late-stack on TriviaQA

- **Observation:** top-3 llama2/triviaqa intermediate signals are all adj_kl (L31 0.6522, L17 0.6145, L30 0.6062); adj_kl is the best-signal winner in 3/6 cells overall.
- **Why Unexpected:** the motivating instrument (Entropy-Lens) and the Phase 2A framing centered entropy; adj_kl was the speculative third signal (P3's fusion candidate), and cross-layer KL had only ever been validated at decoding time (DoLa/END), never as a detection score.
- **Deviation-type check:** genuine HYPOTHESIS-level finding (no implementation or design deviation involved).
- **Competing Explanations:**
  1. **Belief-revision ("turbulence") is a distinct, stronger correlate of unresolved competition than distribution width** near the output layers. (Plausibility: MEDIUM-HIGH)
  2. **adj_kl at L31 proxies the final calibration step itself** — measuring how much the last layers rewrite the distribution, i.e., a direct readout of the suppression event. (Plausibility: MEDIUM)
  3. **Single-seed/selection-split artifact.** (Plausibility: LOW-MEDIUM — pattern repeats across three cells and two models)
- **Most Likely Interpretation:** (1) or (2) — both are calibration-adjacent readings; current data cannot separate them.
- **Additional Evidence Needed:** h-m3 fusion (if adj_kl and entropy fuse with gain ≥ 0.02, they carry complementary information → supports 1); correlation of adj_kl(L31→32) with final-layer entropy shift (supports 2). Both computable from existing caches, zero GPU.

#### Finding 3: TruthfulQA final layers are relatively strong — depth margins thin

- **Observation:** within-sweep final-layer entropy AUROC on TruthfulQA is 0.6048–0.6669 across models; the llama3/truthfulqa depth margin is only +0.0035.
- **Why Unexpected:** the mechanism narrative implied a broadly suppressed final layer; the 02c expectation was final-layer signals in the 0.52–0.66 range with clear depth advantage.
- **Deviation-type check:** genuine finding (design executed as planned).
- **Competing Explanations:**
  1. **Dataset-dependent suppression:** TruthfulQA's adversarial false-belief questions may produce uncertainty that survives output calibration. (Plausibility: MEDIUM)
  2. **Label-protocol artifact:** TruthfulQA labels derive from similarity to reference answers — different noise structure could favor coarse final-layer signals. (Plausibility: MEDIUM)
  3. **Small-sample variance** (n=408 selection rows). (Plausibility: MEDIUM)
- **Most Likely Interpretation:** undetermined — all three remain live; the practical consequence (depth advantage is dataset-dependent) holds under any of them.
- **Additional Evidence Needed:** CIs on the existing grid (zero GPU); a third dataset with exact-match labels.

### 4.3 Connection to Existing Literature

| Our Finding | Related Work | Relationship | Citation |
|-------------|-------------|--------------|----------|
| Class-separable uncertainty at intermediate depth, 6/6 cells, training-free token-space statistics | FEPoID — intermediate > final consensus (supervised probing) | EXTENDS (to training-free, token-space, selection-based readout) | [Wang et al., 2026, arXiv 2605.26366] |
| Same | "LLMs Know More Than They Show"; "Layer by Layer" | CONSISTENT_WITH | [Orgad et al., 2024; 2025] |
| Per-layer logit-lens entropy as detection score | Entropy-Lens — same statistic as computation signature, never as detection AUROC | BUILDS_ON | [Ali et al., 2025, arXiv 2502.16570] |
| Screen retained 15–20 layers on LLaMA/Mistral lineage; raw lens usable | Tuned Lens — raw lens biased but LLaMA/Mistral best-behaved | SUPPORTS (their characterization predicted our screen health) | [Belrose et al., 2023, arXiv 2303.08112] |
| Full-distribution statistics separate where single-token trajectories aligned | Kim et al. 2025 — final-prediction-token trajectories largely aligned (adversarial bound) | CONSISTENT_WITH (scope boundary confirmed: different measurement, different outcome) | [arXiv 2507.06722] |
| Best layer/signal varies per model and dataset (L28–L31; signal identity varies 4/6) | SAPLMA — optimal probe layer shifts across models and distributions | CONSISTENT_WITH | [Azaria & Mitchell, 2023, arXiv 2304.13734] |
| Hidden states of a single pass carry uncertainty signal cheaply | Semantic Entropy Probes — hidden states approximate semantic entropy, layer-dependent | CONSISTENT_WITH (independent, probe-based route to the same premise) | [Kossen et al., 2024, arXiv 2406.15927] |
| Per-layer lens entropy trajectories detect hallucination (trained probes, 3 pathways) | TriLens — nearest neighbor; trained L2-logistic/MLP on 3L-dim entropy trajectories, Qwen/Gemma | CONSISTENT_WITH + differentiated (ours: training-free single-tuple selection, LLaMA/Mistral families, transfer/rescue design) | [arXiv 2606.01033] |
| adj_kl as detection-time score | DoLa / END / SLED — cross-layer distribution shift exploited at decoding time only | EXTENDS (first use as detection score; PoC-level) | [Chuang et al., 2023 and successors] |
| Cross-layer hidden-state dynamics carry detection signal | ICR Probe — quantifies module contributions to residual-stream updates for hallucination detection (trained probe) | CONSISTENT_WITH (dynamics route, supervised) | [Zhang et al., ACL 2025, arXiv 2507.16488] |
| Same premise via semantic-trajectory geometry | Layer-wise Semantic Dynamics — factual vs hallucinated responses diverge across depth (contrastive-trained, single pass) | CONSISTENT_WITH | [Mir, 2025, arXiv 2510.04933] |
| Logit-lens entropy signal concentrated mid-network, degrades at final layer | "What Intermediate Layers Know" — jailbreak detection from per-layer entropy dynamics; signal strongest at intermediate depth, weakest at output head | CONSISTENT_WITH (independent task, same depth pattern for lens entropy) | [arXiv 2606.25182, 2026] |
| Distribution-shift features for detection require trained detector | HalluShift | differentiated (ours training-free) | [arXiv 2504.09482] |
| Cross-protocol AUROC non-portability (0.5186 vs 0.5928) | Reproducibility literature on measurement sensitivity in LLM evaluation | CONSISTENT_WITH (concrete quantified instance) | — |

### 4.4 Theoretical Contributions

1. **EMPIRICAL — Existence of training-free depth-resolved detection signal:** First AUROC evaluation of raw logit-lens per-layer uncertainty statistics (entropy, max-prob, adjacent-layer KL) as single-pass, training-free hallucination-detection scores; class-separability confirmed in 6/6 model × dataset cells at PoC scale. This matters because it removes the trained probe from the intermediate-layer detection recipe (delta to SAPLMA/FEPoID/TriLens is supervision).
2. **EMPIRICAL — Universal point-estimate depth advantage:** best screened intermediate layer beats the within-sweep final-layer entropy readout in every cell tested — training-free, token-space corroboration of the intermediate>final consensus, with the new observation that the advantage concentrates on TriviaQA and at L28–L31.
3. **EMPIRICAL — Adjacent-layer KL is a viable detection signal:** first detection-time use of cross-layer belief revision, dominant in half the cells; upgrades DoLa-style decoding heuristics into a measurable detection statistic.
4. **METHODOLOGICAL — Protocol-internal validity anchoring:** demonstrated that a cross-protocol numeric anchor is unsatisfiable by construction (six-way protocol drift shifted a "failing" 0.5186 baseline to 0.5928), and that anchor *direction* transfers while *magnitude* does not. The A2-v2 pattern (identity-verified cache reuse + within-sweep baselines + descriptive-only cross-run comparison) is a reusable validity-gate design for iterated LLM evaluation pipelines.

---

## 5. Experiment Results (Phase 6 Evidence)

### 5.1 Per-Hypothesis Results

| Hypothesis | Title | Gate | Result | Pass Rate | Key Insight |
|------------|-------|------|--------|-----------|-------------|
| **h-e1** | Per-layer logit-lens existence sweep (v1 anchor spec) | MUST_WORK | PARTIAL → MODIFIED (h-e1-v2) | 66.7% (4/6) | A numeric anchor is only as valid as its provenance: same model+dataset under a 6-way different protocol produced AUROCs 0.055–0.074 apart; direction transferred, magnitude did not. Existence passed on the binding cell (L31 adj_kl 0.6522). |
| **h-e1-v2** | Existence sweep under A2-v2 protocol-internal anchor | MUST_WORK | **PASS** | 100% (5/5) | Intermediate-layer logit-lens signals are class-separable in every model × dataset cell, and the best intermediate beats the within-sweep final layer in all 6 — existence premise confirmed at PoC scale with a fully protocol-internal validity anchor. |
| h-m1 | LLaMA-2 rescue on test split (P1) | MUST_WORK | not run (BLOCKED) | — | — |
| h-m2 | Architecture robustness + no-regression (P4) | SHOULD_WORK | not run (BLOCKED) | — | — |
| h-m3 | KL-entropy fusion (P3) | SHOULD_WORK | not run (BLOCKED) | — | — |
| h-c1 | Cross-dataset transfer (P2) | SHOULD_WORK | not run (BLOCKED) | — | — |

### 5.2 Aggregate Metrics

| Metric | Value |
|--------|-------|
| **Total Hypotheses** | 6 (h-e1, h-e1-v2, h-m1, h-m2, h-m3, h-c1) |
| **Fully Validated** | 1 (h-e1-v2, MUST_WORK PASS) |
| **Partially Validated** | 1 (h-e1, PARTIAL → self-modified) |
| **Failed** | 0 |
| **Blocked / Never Run** | 4 (h-m1, h-m2, h-m3, h-c1) |
| **Total Tasks Completed** | 30 / 30 (15 + 15; 1 Coder–Validator cycle each) |
| **SDD Compliance Rate** | 100% (30/30 tasks SDD-compliant) |
| **Scale** | 5,451 scored generations (1,817/model × 3), 6 cells; binding cell zero-GPU via verified donor cache |
| **Tests** | h-e1: 35/35 · h-e1-v2: 37/37; both REAL_MODEL reality checks |

### 5.3 Optimal Hyperparameters

```yaml
# Training-free (EXISTENCE PoC) — protocol constants, must stay fixed for dependents
seed: 42
decoding: greedy (do_sample=False)
max_new_tokens: 32
weights_dtype: fp16
statistics_dtype: float32
numerics_guard: log(p + 1e-12); adj_kl NaN at layer 1 (excluded)
split: stratified 50/50 selection/test per dataset, test locked
AUROC_GATE: 0.55
DEGENERACY_ENTROPY_PCT: 0.01      # drop layers with entropy within 1% of ln|V|
DEGENERACY_AGREEMENT_MIN: 0.05    # drop layers with <5% top-1 agreement w/ final layer
anchor: A2-v2 protocol-internal (verify_cache_reuse 10/10; within-sweep final-layer
        baseline; direction-consistency descriptive, never gated)
# Selection-split winners (freeze for any test-split evaluation):
selected_tuples:
  llama2/triviaqa:    {layer: 31, signal: adj_kl,  auroc: 0.6522}
  llama2/truthfulqa:  {layer: 29, signal: entropy, auroc: 0.7011}
  mistral/triviaqa:   {layer: 31, signal: maxprob, auroc: 0.6092}
  mistral/truthfulqa: {layer: 31, signal: adj_kl,  auroc: 0.6570}
  llama3/triviaqa:    {layer: 28, signal: entropy, auroc: 0.6868}
  llama3/truthfulqa:  {layer: 31, signal: maxprob, auroc: 0.6213}
```

### 5.4 Proven Components

| Component | Source Hypothesis | File | Reusable |
|-----------|-------------------|------|----------|
| Per-layer logit-lens sweep (33 hidden states, 3 signals, answer-token averaging) | h-e1-v2 | code/model.py, code/run_h_e1.py | Yes |
| Streaming per-example cache + resume by example_id (survived 3 interruptions) | h-e1-v2 | code/run_h_e1.py | Yes |
| Donor-cache reuse with 10-example identity verification | h-e1-v2 | code/run_h_e1.py (`verify_cache_reuse`) | Yes |
| Degeneracy screen → corrected AUROC grid → gate evaluation | h-e1-v2 | code/analysis.py | Yes |
| A2-v2 protocol-internal anchor (`check_anchor_and_halt` v2) | h-e1-v2 | code/run_h_e1.py | Yes |
| `verify_v2_run_complete` 5-indicator run verifier | h-e1-v2 | code/analysis.py | Yes |
| Stratified 50/50 split, seed 42, test locked | h-e1 | code/data.py | Yes — test splits must be reused untouched |
| 6 finalized per-example caches (5+96 cols, both splits, all per-layer signals) | h-e1-v2 | results/cache_{model}_{dataset}.csv | Yes — enables zero-GPU h-m1/h-m3/h-c1/h-m2 |
| 6-cell figure loop + anchor v2 report | h-e1-v2 | code/generate_figures.py | Yes |

### 5.5 Planned-vs-Actual Comparison

| Hypothesis | Planned Metric (03_tasks) | Planned Target | Actual Result (04_validation) | Deviation Type | Notes |
|------------|--------------------------|----------------|-------------------------------|----------------|-------|
| **h-e1** | Existence: ≥ 1 screened pair per model, selection AUROC ≥ 0.55, both datasets, 6/6 cells | 6/6 cells | 1/6 measured (binding cell PASS: L31 adj_kl 0.6522) | DESIGN_ISSUE | A2 anchor spec adopted cross-protocol reference numbers; designed halt stopped campaign at 47 s |
| **h-e1** | A2 anchor: all 6 final-layer entropy AUROCs within ±0.03 of v1 references | Δ ≤ 0.03 | Δ +0.0742 (selection) / +0.0553 (full) on cell 1 — breach | DESIGN_ISSUE | Unsatisfiable by construction (6 protocol differences); implementation verified faithful |
| **h-e1** | Screen health ≥ 5 layers | ≥ 5 | 20/32 retained | NONE | |
| **h-e1-v2** | Existence 6/6 cells, selection AUROC ≥ 0.55 | 6/6 | 6/6, range 0.6092–0.7011 | NONE | |
| **h-e1-v2** | A2-v2(a) donor identity 10/10 before reuse | 10/10 | 10/10 | NONE | Zero-GPU binding cell |
| **h-e1-v2** | A2-v2(b) depth_beats_final per cell | 6/6 | 6/6 | NONE | Margins +0.0035 to +0.130 |
| **h-e1-v2** | Screen ≥ 5 layers per model | ≥ 5 | 20 / 15 / 15 | NONE | |
| **h-e1-v2** | Env: conda youra-h-e1, transformers 4.57.6 | pinned env | youra-h-e1-v2, transformers 4.57.1 (pinned env broke) | SCOPE_CHANGE (logged, non-substantive) | Lesson: pin by spec, not by env name |

**Deviation Types:** IMPLEMENTATION_GAP | DESIGN_ISSUE | HYPOTHESIS_ISSUE | SCOPE_CHANGE | NONE

Interpretation: no IMPLEMENTATION_GAP or HYPOTHESIS_ISSUE deviations occurred. The single substantive failure (h-e1 anchor) was a DESIGN_ISSUE, which means the v1 PARTIAL does **not** count as evidence against the hypothesis — the v2 re-run under a corrected design confirmed this by passing everything the flawed design had blocked.

### 5.6 Key Figures Reference

| Figure | Source | Description | Suggested Paper Section |
|--------|--------|-------------|------------------------|
| gate_metrics_bar.png | h-e1-v2/figures/ | Target vs actual gate metrics, all 6 cells | Results (headline) |
| auroc_heatmap.png | h-e1-v2/figures/ | Corrected AUROC across layers × signals per cell | Results |
| auroc_vs_depth_llama2_triviaqa.png (+5 sibling cells) | h-e1-v2/figures/ | AUROC vs depth, 3 signals, gate + final-layer lines | Results / Analysis |
| entropy_heatmap_llama2.png | h-e1-v2/figures/ | Examples × layers entropy, correct vs incorrect groups | Method intuition / Analysis |
| degeneracy_screen.png | h-e1-v2/figures/ | Retained/dropped layers per model | Method / Appendix |
| anchor_v2_report.png | h-e1-v2/figures/ | Per-cell within-sweep final-layer AUROC + direction-consistency markers | Method (validity) / Appendix |
| anchor_check_llama2_triviaqa.png | h-e1/figures/ | v1 anchor breach visual (observed vs reference ±0.03 band) | Discussion (protocol-sensitivity finding) |

---

## 6. Limitations & Scope Boundaries

### 6.1 Principled Limitations

#### Selection-split-only evidence — the deployable-detector claims are unmeasured

- **What:** All six existence AUROCs were computed on the selection split, which also chose the (layer, signal, direction) tuples. The locked test splits were never evaluated; h-m1/h-m2 (test-split gates) never ran.
- **Why This Matters:** The original headline claim (test AUROC ≥ 0.60, CI-separated rescue) is exactly the part that remains unproven; selection-split numbers overestimate generalization by construction.
- **Root Cause:** The hypothesis loop budget was consumed by the h-e1 DESIGN_ISSUE and its v2 re-run; the loop terminated after h-e1-v2 PASS with dependents still queued (not a scientific failure — a scheduling outcome).
- **Impact on Claims:** Refined statement is explicitly restricted to selection-split separability; A4 (selection discipline) marked UNVERIFIED.
- **Why Acceptable:** The EXISTENCE gate was designed as the precondition tier — its purpose was to establish that the signal exists before spending test-split confirmations, and it did. All caches needed for test-split evaluation exist; the follow-up is zero-GPU.

#### No statistical uncertainty quantification on the existence grid

- **What:** One seed (42), no bootstrap CIs on any of the six cell AUROCs or the six depth margins.
- **Why This Matters:** The thinnest depth margin (llama3/truthfulqa, +0.0035) is almost certainly within noise; "6/6 depth_beats_final" is a point-estimate statement, not a statistical one.
- **Root Cause:** Deliberate EXISTENCE-PoC design (direction-based success, no statistical tests) inherited from Phase 2B; CIs were assigned to the blocked mechanism tier.
- **Impact on Claims:** Depth-advantage claim stated as point estimates; mechanism step 2 capped at PARTIALLY_VERIFIED.
- **Why Acceptable:** The binding gate quantity (AUROC ≥ 0.55) clears by 0.059–0.151 in every cell — margins large relative to plausible CI widths for n=408–500 — and the bootstrap machinery exists in `analysis.py`, runnable on cached data.

#### The original baseline anchor is invalid — the "rescue from documented failure" narrative must be reframed

- **What:** A2 as specified was violated: the 0.5186 v1 baseline came from a materially different protocol and cannot anchor same-protocol comparisons. Under the current protocol, llama2's final layer is weak (0.5928, direction-unstable) but not at chance.
- **Why This Matters:** The Phase 2A story ("final layer FAILS on llama2; depth rescues it") overstates what the current protocol shows; the honest framing is a consistent relative depth advantage, not rescue from chance.
- **Root Cause:** Anchor numbers adopted across a protocol boundary without provenance audit (Phase 2B/2C spec flaw); the donor episode crashed before its own anchor check would have caught it.
- **Impact on Claims:** All cross-protocol baseline citations removed; A2 marked VIOLATED→re-specified; the mechanism's "suppression to chance" reading weakened to relative attenuation.
- **Why Acceptable:** The flaw was caught by a designed halt gate in 47 seconds, forensically attributed, and converted into a methodological contribution (A2-v2); no contaminated numbers survive in the v2 results.

#### Scope: three 7–8B families, two short-form QA datasets, greedy decoding, one instruct model

- **What:** "Architecture-robust" means across LLaMA-2-7B, Mistral-7B-v0.1, LLaMA-3-8B-Instruct only; R3 instruct asymmetry (one instruct model) confounds any tuning-status interpretation; familiarity shadow (R1/A5) unaddressed.
- **Why This Matters:** The step-3 mechanism claim (tuning-dependent suppression) is untestable within this model set — the contrary descriptive ordering we observed cannot be attributed cleanly.
- **Root Cause:** Model set inherited from the v1 episode for baseline comparability (a deliberate controlled-variable choice with a known cost).
- **Impact on Claims:** Depth-pattern and tuning observations stay descriptive; refined statement names the three checkpoints explicitly.
- **Why Acceptable:** Standard PoC scoping; the controlled-comparison benefit (v1 lineage, donor cache) outweighed breadth at this tier.

### 6.2 Scope Conditions

| Condition | Results Hold | Results May Not Hold | Evidence |
|-----------|-------------|---------------------|----------|
| Evaluation split | Selection split (tuples selected and gated there) | Locked test splits (never evaluated) | h-m1/h-m2 not run; A4 UNVERIFIED |
| Dataset | TriviaQA rc.nocontext, TruthfulQA generation (short-form QA, these label protocols) | Long-form generation, summarization, other label rules (protocol shift moved AUROC by +0.055–0.074) | Finding 1 (§4.2) |
| Depth-advantage size | TriviaQA (margins +0.059 to +0.130) | TruthfulQA (margins +0.0035 to +0.052; final layer already 0.60–0.67) | h-e1-v2 gate grid |
| Model family | LLaMA-2-7B, Mistral-7B-v0.1, LLaMA-3-8B-Instruct (32-layer, pre-LN, clean lens path) | Other sizes/families; post-LN or lens-degenerate architectures (screen would catch) | A1 VERIFIED for these three only; Belrose et al. lineage argument |
| Decoding | Greedy, max_new_tokens=32, single pass | Sampling, long generations | Controlled variable, untested elsewhere |
| Signal interpretation | Separation under standard correct/incorrect labels | Causal truthfulness vs familiarity/recall (A5 UNVERIFIED, R1) | Direction inconsistencies 2/6 vs v1 record; no stratified diagnostic |
| Anchor comparisons | Within-protocol (same prompt/label/signal/dtype/split) | Cross-protocol numeric comparisons (invalid by demonstration) | h-e1 anchor forensics |

### 6.3 Assumption Violation Impact

- **A2 (v1 references reproducible ±0.03):** VIOLATED — provenance mismatch, Δ +0.0742. → Impact: HIGH on narrative (rescue framing reframed; all 0.5186-class citations banned downstream), NONE on v2 results (protocol-internal anchor substituted and satisfied). Mitigation: A2-v2 design; ban recorded in h-e1 recommendations ("never cite v1-record AUROCs as same-protocol baselines — Phase 4.5/6 writing included").

---

## 7. Future Work

### 7.1 From Untested Alternative Explanations

- **Alternative:** adj_kl and entropy carry complementary information (turbulence ≠ width) — vs adj_kl being an entropy-redundant proxy.
  - **Why Not Yet Tested:** h-m3 (fusion) blocked; only single-signal AUROCs measured.
  - **Proposed Experiment:** 2-parameter logistic fusion of best entropy-family + best adj_kl signal, fit on selection split, evaluated on locked test split — runnable **entirely from the existing 6 caches, zero GPU**.
  - **Expected Outcome:** gain ≥ 0.02 with CI excluding zero in a majority of cells → complementarity (supports the two-facet mechanism reading); null → informative negative (turbulence redundant with width).
- **Alternative:** adj_kl@L31 proxies the final calibration step (a direct suppression readout) rather than independent belief-revision signal.
  - **Why Not Yet Tested:** requires signal-correlation analysis not in the gate design.
  - **Proposed Experiment:** per-example correlation of adj_kl(L31→32) with the L32-vs-L31 entropy drop, and with final-layer AUROC deficits across cells; cached data, zero GPU.
  - **Expected Outcome:** strong correlation → adj_kl is a calibration-step meter (mechanism step 2 evidence); weak → independent signal.
- **Alternative:** the +0.055–0.074 baseline shift (Finding 1) is dominated by one specific protocol factor (label rule vs prompt template vs signal definition).
  - **Why Not Yet Tested:** v1 protocol was never re-run factor-by-factor.
  - **Proposed Experiment:** factorial toggle of the six protocol differences on llama2/triviaqa (one GPU pass per factor).
  - **Expected Outcome:** attribution of AUROC protocol-sensitivity — a standalone reproducibility contribution.

### 7.2 From Unverified Assumptions

- **Assumption:** A4 — selection-split tuple selection generalizes to the locked test split.
  - **Current Status:** UNVERIFIED
  - **Proposed Test:** freeze the six selected tuples (§5.3), evaluate on locked test splits with paired bootstrap (n=1000) vs within-sweep final-layer entropy — this IS h-m1/h-m2, zero GPU from caches. **The single highest-value next experiment**: it converts the refined existence claim back into the original headline claim (or refutes it).
  - **If Violated:** test AUROC systematically below selection AUROC beyond CI width → selection overfit; adaptation: top-k layer ensembling (documented deviation path from A4).
- **Assumption:** A3 — answer-token mean aggregation robust to end-of-sequence noise.
  - **Current Status:** UNVERIFIED
  - **Proposed Test:** truncated-aggregation ablation (first-k answer tokens). Note: the streaming caches store per-example layer means, not per-token values, so this needs a partial re-sweep (moderate GPU).
  - **If Violated:** adopt truncated aggregation with documented deviation; existence conclusions likely strengthen, not weaken.
- **Assumption:** A5 — AUROC reflects hallucination separation, not question familiarity.
  - **Current Status:** UNVERIFIED
  - **Proposed Test:** popularity/frequency-stratified AUROC on TriviaQA (entity frequency as stratifier) + direction-pattern analysis across strata; cached scores, zero GPU given a frequency table.
  - **If Violated:** claims remain valid as stated (separation under standard labels) but the interpretation narrows to recall-correlated uncertainty; motivates causal follow-up outside current scope (R1).

### 7.3 From Scope Extension Opportunities

- **Extension:** Cross-dataset transfer of selected tuples (P2 / h-c1), both directions, per model.
  - **Current Evidence Suggesting Feasibility:** best layers cluster at L28–L31 across datasets within every model; caution: winning signal differs across datasets in 4/6 cells, so transfer the full (layer, signal, direction) tuple.
  - **Required Resources:** zero GPU — cross-evaluation on existing caches with locked test splits.
- **Extension:** Statistical hardening of the existence grid (bootstrap CIs on all 6 AUROCs and 6 depth margins).
  - **Current Evidence Suggesting Feasibility:** CI machinery already implemented and tested in `analysis.py`.
  - **Required Resources:** zero GPU, minutes of CPU. Quick win that upgrades "6/6 point estimates" to CI-qualified claims (llama3/truthfulqa margin expected to lose significance — honest reporting either way).
- **Extension:** Base-vs-instruct pairs of the same family (e.g., LLaMA-3-8B base vs Instruct) to unconfound R3 and directly test the revised tuning-polarity hypothesis (instruct tuning sharpens final-layer calibration → larger depth margins).
  - **Current Evidence Suggesting Feasibility:** the contrary margin ordering (llama3-instruct largest) is exactly the pattern this design would explain or refute.
  - **Required Resources:** ~1 GPU-day per additional model (1,817 examples, measured ~0.7 s/example on H100).

---

## 8. Implications for Phase 6 (Paper Writing)

### 8.1 Recommended Narrative Hook

**Hook Strategy:** Counterintuitive finding + measurement-validity subplot.

**Suggested hook:** "In every model and dataset we tested, the model's intermediate layers scored its own hallucinations better than its output layer did — and the reference baseline we set out to beat turned out to be an artifact of someone else's protocol." Lead with the 6/6 depth_beats_final result (concrete, universal within scope, easy to visualize with the AUROC-vs-depth curves), then use the anchor-provenance forensics as the methods-credibility subplot: a validity gate killed a doomed 2.5-hour campaign in 47 seconds and exposed that AUROC magnitudes do not survive protocol changes (0.5186 → 0.5928 on the same cell).

**Why This Hook:** It is fully experiment-backed (no reliance on the unmeasured test-split claims), differentiates from probe-based prior work (training-free), and the validity subplot converts the pipeline's one failure into a reproducibility contribution reviewers can verify from forensics tables.

### 8.2 Key Insight (Experiment-Verified)

> Hallucination-predictive uncertainty is present and class-separable in the token-space readout of intermediate layers (L28–L31) of every model × dataset cell tested, and always exceeds the final layer's own entropy readout — without training any probe.

**Verification Evidence:** h-e1-v2 gate grid — 6/6 cells corrected AUROC 0.6092–0.7011 (gate 0.55); depth_beats_final 6/6; 5,451 real scored generations; MUST_WORK PASS 5/5 criteria; 37/37 tests, REAL_MODEL verdict.

### 8.3 Strongest Claims (Paper-Ready)

1. **Training-free per-layer logit-lens statistics are class-separable hallucination scores in all six model × dataset cells (AUROC 0.61–0.70, selection split).**
   - Evidence: h-e1-v2 gate grid (§5.3 tuples); Confidence: HIGH
   - Suggested Section: Results (primary)
2. **The best screened intermediate layer beats the within-sweep final-layer entropy baseline in every cell (point-estimate margins +0.0035 to +0.130, largest on TriviaQA).**
   - Evidence: depth_beats_final 6/6, h-e1-v2; Confidence: MEDIUM-HIGH (no CI yet; 5/6 margins > 0.03)
   - Suggested Section: Results + Discussion (calibration-suppression framed as supported direction, not established cause)
3. **Adjacent-layer KL divergence — previously used only to steer decoding (DoLa-style) — works as a detection score, and is the dominant signal in half the cells.**
   - Evidence: adj_kl best signal in 3/6 cells; top-3 llama2/triviaqa intermediates all adj_kl; Confidence: MEDIUM-HIGH
   - Suggested Section: Results / Analysis
4. **AUROC baselines for weak uncertainty signals are not portable across evaluation protocols: six documented protocol differences moved the same cell's final-layer entropy AUROC from 0.5186 to 0.5928; direction transferred, magnitude did not.**
   - Evidence: h-e1 anchor forensics (provenance audit, Δ +0.0742/+0.0553); Confidence: HIGH
   - Suggested Section: Discussion / a "measurement validity" subsection (reproducibility contribution)
5. **Protocol-internal validity anchoring (identity-verified cache reuse + within-sweep baselines + ungated cross-run direction reports) is a workable replacement for cross-run numeric anchors.**
   - Evidence: A2-v2 satisfied 5/5 with zero spurious halts vs v1's constructive unsatisfiability; Confidence: HIGH
   - Suggested Section: Method (validity protocol)

### 8.4 Honest Limitations (Must Include in Paper)

1. **All detection AUROCs are selection-split values; the locked test splits were never evaluated.**
   - Why Acceptable: EXISTENCE-tier design — the gate's purpose was to establish signal existence before test-split confirmation, and every artifact for the test-split follow-up exists (zero-GPU).
   - Suggested Framing: present as staged verification with the test-split stage explicitly future work; never phrase results as held-out performance.
2. **Single seed, no confidence intervals; the smallest depth margin (+0.0035, llama3/truthfulqa) is within plausible noise.**
   - Why Acceptable: gate margins on the binding quantity (≥ 0.55) are large (+0.059 to +0.151); CI machinery exists and the claim degrades gracefully (5/6 cells have margins > 0.03).
   - Suggested Framing: report depth_beats_final as point estimates and flag the thin cell explicitly.
3. **The original "rescue from documented final-layer failure (0.5186)" premise is protocol-specific; under the current protocol llama2's final layer is 0.59, not chance.**
   - Why Acceptable: converted into the paper's measurement-validity contribution; the relative depth advantage stands on within-protocol comparisons.
   - Suggested Framing: report the v1 record as motivating context with explicit cross-protocol caveat; never as a same-protocol baseline.
4. **Scope: three 7–8B checkpoints, two short-form QA datasets, greedy decoding, one instruct model; familiarity-vs-truthfulness confound unaddressed (A5).**
   - Why Acceptable: standard PoC scope; controlled-variable lineage to the v1 record was a deliberate design choice.
   - Suggested Framing: "architecture-robust across the three tested families"; tuning-status observations descriptive only.

### 8.5 Evidence Highlights (Most Persuasive)

1. **The 6/6 existence grid**
   - Data: llama2/triviaqa L31 adj_kl 0.6522 · llama2/truthfulqa L29 entropy 0.7011 · mistral/triviaqa L31 maxprob 0.6092 · mistral/truthfulqa L31 adj_kl 0.6570 · llama3/triviaqa L28 entropy 0.6868 · llama3/truthfulqa L31 maxprob 0.6213 — all ≥ 0.55, all beating their final layer.
   - "So What": the signal exists everywhere tested, not in cherry-picked cells — the field's intermediate>final consensus holds for training-free token-space statistics.
   - Suggested Visual: 6-panel auroc_vs_depth grid or auroc_heatmap.png (Results centerpiece).
2. **Depth margins by dataset**
   - Data: TriviaQA margins +0.059/+0.064/+0.130 vs TruthfulQA +0.034/+0.052/+0.0035; TruthfulQA final layers already 0.60–0.67.
   - "So What": the depth advantage is real but dataset-dependent — a nuance that preempts reviewer over-generalization and motivates the transfer experiment.
   - Suggested Visual: paired bar chart (best-intermediate vs final per cell), derived from gate_metrics_bar.png.
3. **The anchor forensics table**
   - Data: same cell, 0.5186 (v1 protocol) vs 0.5928/0.5739 (current protocol); six enumerated protocol differences; halt at 47 s vs ~2.5 h GPU.
   - "So What": quantified, attributable demonstration that AUROC magnitudes are protocol-bound — and that cheap validity gates pay for themselves.
   - Suggested Visual: anchor_check_llama2_triviaqa.png (v1 breach band) + protocol-difference table.
4. **adj_kl dominance late in the stack**
   - Data: top-3 llama2/triviaqa intermediate signals all adj_kl (L31/L17/L30: 0.6522/0.6145/0.6062); adj_kl best-signal in 3/6 cells, always at L31.
   - "So What": inter-layer belief revision is a first-class detection signal, not just a decoding heuristic — the paper's most novel single observation.
   - Suggested Visual: auroc_vs_depth_llama2_triviaqa.png (signal-colored curves).
5. **Zero-GPU verified reuse**
   - Data: donor-cache identity 10/10 fresh-regeneration agreement; binding cell reproduced without GPU; sweep survived 3 interruptions via example_id resume.
   - "So What": the protocol is cheap, resumable, and auditable — supports the practicality claim of training-free detection.
   - Suggested Visual: none needed (method text + appendix log excerpts).

---

## Source Files Reference

| File | Hypothesis | Purpose |
|------|------------|---------|
| `h-e1/04_validation.md` | h-e1 | Experiment results, anchor forensics, lessons learned, Phase 2C handoff |
| `h-e1/04_checkpoint.yaml` | h-e1 | pass_rate 0.667, failed_checks, anchor_failure_analysis, SDD metrics |
| `h-e1/03_tasks.yaml` | h-e1 | 15 planned tasks (A-1…A-7), planned anchor targets — planned-vs-actual basis |
| `h-e1/02c_experiment_brief.md` | h-e1 | v1 experiment design: variables, datasets, A2 anchor spec, evaluation protocol |
| `h-e1-v2/04_validation.md` | h-e1-v2 | 6-cell gate grid, A2-v2 results, unexpected findings, dependent recommendations |
| `h-e1-v2/04_checkpoint.yaml` | h-e1-v2 | pass_rate 1.0, experiment_results, deviations, validator result |
| `h-e1-v2/03_tasks.yaml` | h-e1-v2 | 15 planned tasks (D-1…D-7), A2-v2 re-spec targets |
| `h-e1-v2/02c_experiment_brief.md` | h-e1-v2 | Delta-only design under A2-v2; Serena-verified reuse map |
| `03_refinement.yaml` | — | Original hypothesis: core statement, P1–P4, mechanism, A1–A5, scope |
| `verification_state.yaml` | — | Pipeline state: gates, blocked dependents, modification history |
| Serena `pivot_h-e1_h-e1-v2`, `failure_h-e1_run1` | — | Pivot rationale; v1-record full 6-cell final-layer AUROC table with CIs |

**Input files per hypothesis:**
- `h-{id}/04_validation.md` — Experiment results, gate outcomes, lessons learned
- `h-{id}/04_checkpoint.yaml` — Pass rate, failed checks, SDD metrics
- `h-{id}/03_tasks.yaml` — Planned tasks, expected metrics, success criteria
- `h-{id}/02c_experiment_brief.md` — Experiment design, variables, evaluation protocol

---

*Anonymous Research Pipeline — Evidence-refined hypothesis with theoretical interpretation*
