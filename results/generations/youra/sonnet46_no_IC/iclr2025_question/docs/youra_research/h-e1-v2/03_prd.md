---
title: "PRD: h-e1-v2 — Layer-Wise Logit-Lens Existence Sweep (A2-v2 protocol-internal anchor)"
hypothesis_id: h-e1-v2
hypothesis_type: EXISTENCE
gate: MUST_WORK
tier: LIGHT
date: 2026-08-05
author: Anonymous
source: 02c_experiment_brief.md
modified_from: h-e1
modification_attempt: 1
stepsCompleted: [executive-summary, problem-statement, functional-requirements, nfrs, success-criteria, dependencies]
note: "BMAD bmm PRD workflow not installed in this environment; PRD generated directly from Phase 2C brief following BMAD v6 PRD section structure (deviation logged in Phase 3 summary). Consistent with h-e1 precedent."
---

# PRD: h-e1-v2 — Per-Layer Logit-Lens Existence Sweep with Protocol-Internal Anchor

## Executive Summary

Delta refinement of h-e1 after a Phase 4 MUST_WORK PARTIAL (4/6). The mechanism is proven — existence PASSES on the binding cell (llama2/triviaqa L31 adj_kl corrected AUROC 0.6522 ≥ 0.55, depth beats final 0.5928, 20/32 layers retained, 35/35 tests, validator PASS) — but the v1 A2 anchor demanded reproduction of v1-record final-layer AUROCs (±0.03) whose provenance audit proved a 6-way different protocol: unsatisfiable by construction. The halt gate fired correctly on the first cell, leaving 5/6 cells intentionally unmeasured.

**The ONLY design change:** `check_anchor_and_halt` re-specified per A2-v2 (protocol-internal validity): (a) donor-cache protocol identity via ≥ 10-example fresh-regeneration label agreement BEFORE reuse (already implemented: `verify_cache_reuse`); (b) per-cell within-sweep final-layer entropy AUROC as the depth_beats_final baseline (already implemented: `evaluate_gate`); (c) direction-consistency vs v1 record reported descriptively, NOT gated (new ~15-line report). Everything else — datasets (TriviaQA rc.nocontext validation[:1000] + TruthfulQA generation validation 817), models (LLaMA-2-7B, Mistral-7B-v0.1, LLaMA-3-8B-Instruct, frozen fp16), signals, thresholds, split protocol, and ~1,300 lines of code + 5 test files — reused verbatim from `h-e1/code/`. Full-scale evaluation: 1,817 examples × 3 models = 5,451 scored generations (binding cell zero-GPU via finalized cache; ~4,451 fresh).

## Problem Statement

h-e1's MUST_WORK gate returned PARTIAL solely because the A2 anchor gated on cross-protocol numbers: `H_E1_REFERENCES` (e.g. llama2/triviaqa 0.5186) came from a run with random 1000-of-7993 sampling, bare prompts, substring labels, generation-time entropy, bfloat16, and full-set eval — six documented differences from the current logit-lens protocol. Observed within-protocol final-layer AUROC was 0.5928 (selection), a 0.074 delta that no correct implementation could close. The fail-fast halt (47 s instead of ~2.5 h GPU) left 5/6 model×dataset cells unmeasured, so the existence claim across all three models remains unestablished.

h-e1-v2 must (1) retire the unreproducible cross-protocol numeric gate, (2) anchor validity on protocol-internal quantities only, and (3) complete the full 6-cell sweep so the existence criterion is measured everywhere. Dependents h-m1 (rescue), h-m2 (robustness), h-m3 (fusion), h-c1 (transfer) remain BLOCKED until this gate passes; they consume the 5+96 cache schema and locked splits unchanged, so cache/split compatibility is a hard contract. This is modification attempt 1 — a second MUST_WORK PARTIAL routes to Phase 2A-Dialogue.

## Functional Requirements

### FR-1: Dataset Loading & Partitioning (v1-verbatim, controlled variables)
- FR-1.1: TriviaQA `mandarjoshi/trivia_qa` config `rc.nocontext`, split `validation[:1000]` (deterministic first-1000 slice — NOT random). Reuse `data.py` loaders verbatim.
- FR-1.2: TruthfulQA `truthfulqa/truthful_qa` config `generation`, split `validation`, all 817 rows.
- FR-1.3: v1-verbatim prompt template `"Q: {question}\nA:"` and `label_response` protocols (TriviaQA normalized-alias exact match; TruthfulQA correct/incorrect reference comparison).
- FR-1.4: Stratified 50/50 selection/test split per dataset, seed 42. **llama2/triviaqa split ALREADY LOCKED** in `h-e1/results/test_split_locked_llama2_triviaqa.json` — reuse, never recompute. Other cells: compute + lock per v1 protocol. Test split written but NEVER read by v2 analysis (reserved for h-m1).

### FR-2: Model Loading (all three — none omitted)
- FR-2.1: `meta-llama/Llama-2-7b-hf` — binding existence case.
- FR-2.2: `mistralai/Mistral-7B-v0.1` — base-model robustness case.
- FR-2.3: `meta-llama/Meta-Llama-3-8B-Instruct` — instruct-model case (R3 scope note).
- FR-2.4: fp16 weights, single GPU (H100 verified, peak 13.59 GB batch 1), `model.eval()`, `output_hidden_states=True`; `validate_layout` asserts 32 layers + `model.model.norm` + `model.lm_head` + 33 hidden states — fail early on violation (existing behavior). Env pin: conda `youra-h-e1`, python 3.10.20, torch 2.8.0+cu128, transformers 4.57.6 (torch 2.4.x incompatible — env drifted once in v1).

### FR-3: Generation, Extraction & Cache (v1-verbatim)
- FR-3.1: Greedy decoding (`do_sample=False`, `max_new_tokens=32`, batch 1); teacher-forced re-forward; lens path `model.lm_head(model.model.norm(h_l))`, float32 statistics, `log(p+1e-12)` guard.
- FR-3.2: Three signals per layer l ∈ {1..32}, mean over answer tokens: Shannon entropy, max-token probability, adjacent-layer KL (NaN at l=1, excluded). Reuse `model.py:per_layer_lens_signals` verbatim.
- FR-3.3: Streaming resumable per-cell CSV cache, 5+96 column schema, append-mode resume keyed by example_id, corrupt-tail truncation (`resume_from_cache`, `write_cache_row` — verbatim).
- FR-3.4: **A2-v2(a) — donor cache reuse gate:** `h-e1/results/cache_llama2_triviaqa.csv` (1000 rows, splits finalized) reused for the binding cell ONLY after a fresh `verify_cache_reuse` pass in the v2 run: regenerate ≥ 10 examples, compare `label_response` output to donor rows; any drift → False → fresh generation fallback (never silently drop the cell). Function exists, tested, passed 10/10 live — zero changes.
- FR-3.5: Smoke test first per model (10 examples: shape + memory assert), then per-cell sweep in fail-fast order — llama2/triviaqa first (zero-GPU via donor reuse).

### FR-4: Analysis & A2-v2 Anchor (THE delta)
- FR-4.1: **Re-specified `check_anchor_and_halt` (run_h_e1.py:260-294):** REMOVE `H_E1_REFERENCES` lookup, `BASELINE_TOLERANCE` ±0.03 check, and the `SystemExit` numeric-breach branch. KEEP protocol-internal contract guards (`ValueError` on empty selection split; `ValueError` on single-class labels/undefined AUROC). Compute within-sweep final-layer (L32) entropy corrected AUROC per cell and return it for the depth_beats_final check. Log per cell: `"A2-v2 anchor: {model}/{dataset} within-sweep final L32 entropy AUROC={x:.4f} direction={d} v1_record_direction={v1} consistent={bool}"`.
- FR-4.2: **A2-v2(c) — descriptive direction-consistency report (new, ~15 lines, ungated):** compare per-cell final-layer signal direction vs `V1_DIRECTION_RECORD` (llama2 final-layer weak/inverted, llama3 strongest); report only — NO gate, NO SystemExit. Reintroducing any cross-protocol numeric gate is a v2 spec violation.
- FR-4.3: Degeneracy screen on selection split (verbatim): drop layers with entropy within 1% of ln|V| OR top-1 agreement with final layer < 5%; health = retain ≥ 5 layers per model.
- FR-4.4: Corrected AUROC grid `max(auc, 1−auc)` per screened (layer, signal), selection split only (`corrected_auroc`, `build_auroc_grid` — verbatim).
- FR-4.5: **A2-v2(b) — depth_beats_final (existing, verbatim):** `evaluate_gate` computes best intermediate corrected AUROC over retained layers (excludes L32) vs the same sweep's final-layer entropy AUROC; `gate_pass = best_auroc >= 0.55`; `depth_beats_final = best_auroc > final_auroc`. Zero changes.
- FR-4.6: Existence criterion per model: ≥ 1 screened (layer, signal) pair with selection-split corrected AUROC ≥ 0.55 on BOTH datasets — **all 6 model×dataset cells measured** (v1 measured 1/6 before halt).
- FR-4.7: `verify_mechanism_activated` extended for v2: reuse_verified (a), anchor_reported per completed cell (b/c), grid non-degenerate, screen healthy, `all_cells_measured == 6`.

### FR-5: Reporting & Figures
- FR-5.1: Per-cell reports via `write_cell_report` (verbatim): AUROC grid, screened layers, within-sweep final-layer baseline, positive/negative counts.
- FR-5.2: Mandatory figure — gate metrics comparison bar chart (target vs actual).
- FR-5.3: AUROC-vs-depth curves per cell (3 signal lines + 0.55 gate line + final-layer baseline line) — now for ALL 6 cells (v1 renderer reused).
- FR-5.4: A2-v2 anchor report figure — per-cell within-sweep final-layer AUROC + direction-consistency markers vs v1 record (replaces v1 breach-band chart).
- FR-5.5: Degeneracy screen retention map per model; per-layer entropy heatmap (correct vs incorrect groups) per model (`plot_entropy_heatmap`).
- FR-5.6: All figures to `h-e1-v2/figures/`; no figures for unmeasured cells; figure generation logic included in experiment code (Phase 4 mandate).

### FR-6: Test Updates
- FR-6.1: Update `tests/test_anchor_gate.py`: remove tests asserting the `H_E1_REFERENCES`/±0.03/`SystemExit` numeric branch; add tests asserting (i) contract-violation `ValueError` guards retained, (ii) NO SystemExit on any numeric AUROC value, (iii) clause-(c) descriptive log emitted, (iv) returned final_auroc consumed by `evaluate_gate`.
- FR-6.2: All other 5 test files pass unmodified (35/35 baseline; regression guard on the verbatim-reuse claim).

### Ablations
None — EXISTENCE PoC. The layer × signal sweep IS the search space; Phase 2C defines no ablation variants.

## Non-Functional Requirements

- NFR-1: Single GPU (H100); fp16 ≈ 14–16 GB; batch 1 streaming. ~2.5 h GPU for the 5 fresh cells; binding cell zero-GPU.
- NFR-2: Deterministic: seed 42 (partition), greedy decoding; 1 seed total (EXISTENCE PoC).
- NFR-3: Numerics: fp16 weights / float32 statistics; `log(p+1e-12)` guard; adj_kl NaN at layer 1 excluded from grids.
- NFR-4: LIGHT infrastructure tier — constants module + argparse (v1 pattern), print + CSV logging; existing test suite maintained (inherited from v1, not expanded beyond FR-6).
- NFR-5: Scale: 1,817 evaluation examples × 3 models = 5,451 example-model pairs, full standard splits, no subsampling.
- NFR-6: Resumability: interruption loses at most the in-flight example (streamed CSV, RISK-6).
- NFR-7: **Delta discipline:** any change outside `check_anchor_and_halt` + clause-(c) report + `tests/test_anchor_gate.py` must be justified in the validation report; cache schema (5+96) and locked splits are frozen contracts for h-m1/h-m2/h-m3/h-c1.

## Success Criteria

1. **Primary (MUST_WORK):** ≥ 1 screened (layer, signal) pair per model with selection-split corrected AUROC ≥ 0.55 on BOTH datasets — all 6 cells measured.
2. **A2-v2(a):** `verify_cache_reuse` label agreement ≥ 10/10 before any donor/finalized-cache reuse (else fresh generation fallback, logged).
3. **A2-v2(b):** depth_beats_final per cell — best intermediate corrected AUROC > within-sweep final-layer (L32) entropy corrected AUROC.
4. **Screen health:** degeneracy screen retains ≥ 5 layers per model (RISK-1 early warning → tuned-lens pivot decision, documented).
5. **A2-v2(c) (descriptive, ungated):** direction-consistency report vs v1 record present for every measured cell.
6. Code runs end-to-end without error; caches, per-cell reports, figures produced; no `H_E1_REFERENCES` numeric gate anywhere in the run path.

**PoC pass condition:** code runs without error AND best screened intermediate AUROC > within-sweep final-layer baseline (binding cell expected: 0.6522 > 0.5928 from cache).

**Failure semantics (MUST_WORK):** existence miss on any model → STOP workflow, A1 autopsy (lens degeneracy vs signal absence), dependents stay BLOCKED; screen-driven failure → documented tuned-lens pivot with relabeled claims. Second PARTIAL routes to Phase 2A-Dialogue.

## Dependencies

- Python (conda `youra-h-e1`, pinned): python 3.10.20, torch 2.8.0+cu128, transformers 4.57.6, `datasets`, `scikit-learn`, `numpy`, `matplotlib` (+ `tuned-lens` ONLY if RISK-1 pivot triggered — not installed by default).
- HF access: `HF_TOKEN` for meta-llama gated repos; all weights + datasets already in local HF cache (verified h-e1 Phase 4).
- **Primary code path:** `h-e1/code/` copied to `h-e1-v2/code/` — 7 modules + 6 test files (35/35, validator PASS, REAL_MODEL check); single-function re-spec + clause-(c) addition + test updates.
- **Reused artifacts:** `h-e1/results/cache_llama2_triviaqa.csv` (1000 rows, splits finalized — zero-GPU binding cell, gated by FR-3.4); `h-e1/results/test_split_locked_llama2_triviaqa.json`.
- Reference-only: AlignmentResearch/tuned-lens (lens-formula validation + RISK-1 fallback); haloscope/UniFact (protocol-shape confirmation). No external code imported.
- Downstream consumers: h-m1/h-m2/h-m3/h-c1 consume the 5+96 cache schema + locked splits unchanged — frozen contracts (NFR-7).
