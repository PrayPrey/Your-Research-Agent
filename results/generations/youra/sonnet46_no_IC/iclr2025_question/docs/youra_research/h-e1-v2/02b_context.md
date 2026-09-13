# Hypothesis Context: h-e1-v2

**Generated from:** Phase 2B Verification Plan + h-e1 Phase 4 reflection (A2-v2 refinement)
**Date:** 2026-08-05
**Main Hypothesis:** Depth-Resolved Logit-Lens Uncertainty Signals for Architecture-Robust Hallucination Detection (H-LayerLensUQ-v2)
**Phase 2B Source:** 02b_verification_plan.md
**Version:** 2 (SELF_MODIFY refinement of h-e1, modification attempt 1)

---

## Hypothesis Information

### Statement
At least one screened intermediate layer (1-31) per model exhibits class-separable logit-lens statistics on the selection split: corrected AUROC >= 0.55 for at least one (layer, signal) pair among {entropy, max_token_probability, adjacent_layer_KL}, on both TriviaQA and TruthfulQA. LLaMA-2-7B is the binding existence case.

Includes mandatory **A2-v2 protocol-internal validity anchor** (replaces the unreproducible v1 cross-protocol numeric anchor):
- **(a)** donor-cache protocol identity verified by >= 10-example fresh-regeneration label agreement BEFORE reuse;
- **(b)** per-cell within-sweep final-layer entropy AUROC serves as the baseline the best screened intermediate layer must exceed (depth_beats_final direction check);
- **(c)** direction consistency with the v1 record (llama2 final-layer signal weak/inverted, llama3 strongest) reported descriptively, NOT gated.

All datasets, models, signals, thresholds, split protocol, and code unchanged from h-e1.

### Type
EXISTENCE

### Rationale
The signal must EXIST in token space at depth before any selection, rescue, transfer, or fusion claim is testable. h-e1 Phase 4 already demonstrated the mechanism on the binding cell (llama2/triviaqa: L31 adj_kl corrected AUROC 0.6522 >= 0.55, depth beats final 0.5928, 20/32 layers retained), but the v1 A2 anchor was unsatisfiable by construction (reference numbers came from a 6-way different protocol). v2 re-specifies the anchor as protocol-internal validity so the remaining 5/6 cells can be measured.

### What Changed vs h-e1 (v1)
| Aspect | h-e1 (v1) | h-e1-v2 |
|--------|-----------|---------|
| A2 anchor | Reproduce v1-record final-layer AUROCs ±0.03 (cross-protocol numeric) | Protocol-internal: donor label agreement (a) + depth_beats_final (b) + descriptive direction consistency (c) |
| `check_anchor_and_halt` | Halts on numeric mismatch vs H_E1_REFERENCES | Re-specified per A2-v2; no cross-protocol constants |
| Everything else | — | UNCHANGED (datasets, models, signals, thresholds, splits, code) |

---

## Verification Protocol

### Conceptual Test
1. Load datasets with v1-verbatim prompts/labels; stratified 50/50 selection/test split per dataset (seed 42); write and lock test split (llama2/triviaqa split already locked — reuse).
2. A2-v2(a): verify donor/finalized cache protocol identity via >= 10-example fresh regeneration with label agreement BEFORE reuse; reuse finalized `h-e1/results/cache_llama2_triviaqa.csv` (1000 rows, zero GPU).
3. Smoke run (10 examples/model, shape + memory assert), then full sweep: 1,817 examples x 3 models, single greedy pass with teacher-forced re-forward, streaming 3 signals x 32 layers per example to resumable scalar CSV.
4. Apply degeneracy screen on selection split (drop layers with entropy within 1% of ln|V| OR top-1 agreement with final layer < 5%).
5. A2-v2(b): compute per-cell within-sweep final-layer entropy AUROC; best screened intermediate layer must exceed it (depth_beats_final).
6. Evaluate existence criterion per model on selection split (corrected AUROC >= 0.55, both datasets).
7. A2-v2(c): report v1-record direction-consistency pattern descriptively (NOT gated).

### Success Criteria
- **Primary:** >= 1 screened (layer, signal) pair per model with selection-split corrected AUROC >= 0.55 on both datasets (6/6 cells)
- **Secondary (A2-v2):** (a) donor label agreement >= 10/10 examples before any cache reuse; (b) depth_beats_final holds per cell; degeneracy screen retains >= 5 layers per model
- **Descriptive (ungated):** (c) direction-consistency report vs v1 record

### Variables
- **Independent Variable:** readout_layer (1-31 screened), signal_type (3 levels: entropy, max_token_probability, adjacent_layer_KL), model_family (3 levels)
- **Dependent Variable:** AUROC_corrected on selection split
- **Controlled Variables:** greedy decoding (do_sample=False), v1-verbatim prompts/labels ("Q: {q}\nA:" template, normalized-alias exact match), fp16 weights / float32 statistics, stratified 50/50 split seed 42, log(p+1e-12) guard, KL NaN at layer 1 excluded, max_new_tokens 32

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection. Unchanged from h-e1.

### Selected Dataset
- **Name:** TriviaQA (rc.nocontext) + TruthfulQA (generation)
- **Type:** standard
- **Source:** HuggingFace: mandarjoshi/trivia_qa (validation[:1000]), truthfulqa/truthful_qa (validation, 817)
- **Path:** HF cache (verified present by v1 + h-e1 Phase 4 runs); labels/prompts reused verbatim
- **Hypothesis Fit:** Existing real benchmarks; full standard splits, no subsampling, no synthetic data; llama2/triviaqa cell already finalized with locked splits

### Selected Model
- **Name:** meta-llama/Llama-2-7b-hf + mistralai/Mistral-7B-v0.1 + meta-llama/Meta-Llama-3-8B-Instruct
- **Type:** frozen decoder-only LLMs, 32 layers each, fp16, single GPU
- **Source:** HuggingFace (HF cache verified by h-e1 Phase 4 task-001)
- **Hypothesis Fit:** Identical model set preserves comparability; LLaMA-2-7B is the binding existence case; uniform lens path `model.lm_head(model.model.norm(h_l))` across all three

---

## Baseline & Comparison Targets

### Baseline Methods
| Method | Performance | Dataset |
|--------|-------------|---------|
| Within-sweep final-layer mean token entropy (A2-v2(b) baseline) | llama2/triviaqa: 0.5928 selection-split corrected (measured, h-e1 Phase 4) | per-cell, within-protocol |
| Final-layer max-token probability | Single-pass confidence foil at output layer (within-sweep) | TriviaQA/TruthfulQA |
| FEPoID + hidden-state probing | AUROC avg 0.7253 (LLaMA-3.1-8B-It), 0.8531 (Mistral-7B-It) — supervised skyline, deferred to Phase 5 | QA benchmarks |
| Semantic Entropy [Farquhar et al., 2024] | AUROC 0.5311/0.6560 avg; 10x inference cost — excluded direction | QA benchmarks |
| SAPLMA [Azaria & Mitchell, 2023] | 71-83% accuracy; supervised probe | True-False statements |

### Baseline Performance
**A2-v2 baselines are within-sweep quantities, not v1-record constants.** Measured so far (h-e1 Phase 4): llama2/triviaqa final-layer entropy corrected AUROC 0.5928 (selection) / 0.5739 (full). The other 5 cells' final-layer baselines are computed within the v2 sweep itself. v1-record numbers (0.5186 etc.) are used ONLY for the descriptive direction-consistency report (c) — NEVER as numeric gates.

### Gap Analysis
No training-free, single-pass evaluation of raw logit-lens uncertainty statistics (entropy / max-prob / adjacent-layer KL) as per-layer hallucination-detection AUROC scores exists in the literature (GAP-001). h-e1 existence target (0.55 selection-split) is deliberately below the H-M1 rescue target (0.60 test-split).

---

## Dependencies and Gate Conditions

### Prerequisites
None (Level 0 root hypothesis; v2 of the root)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow

**Consequence if Fails:** Separation absent in token space at depth — entire hypothesis tree dies. If failure is screen-driven (A1 lens degeneracy), tuned-lens fallback is a documented pivot with relabeled claims. This is modification attempt 1 (max 1 for MUST_WORK PARTIAL routing before Phase 2A-Dialogue).

**Phase Assignment:** Phase A — Foundation (Gate 1)

**Estimated Duration:** GPU sweep ~2.5 h for 5 remaining cells (llama2/triviaqa is zero-GPU via finalized cache)

---

## Dependency Context

### Relationship to Other Hypotheses
h-e1-v2 is the root of the DAG. h-m1 (rescue, MUST_WORK), h-m3 (fusion, SHOULD_WORK), and h-c1 (transfer, SHOULD_WORK) are BLOCKED awaiting h-e1-v2; h-m2 depends on h-m1. Dependent interfaces (cache schema 5+96 cols, locked test splits) are UNCHANGED by the v2 refinement — no dependent redesign needed.

Key risks: RISK-1 lens degeneracy (High), RISK-3 aggregation noise, RISK-4 selection overfit, RISK-6 sweep interruption (streaming resumable CSV + resume logic already implemented and tested in h-e1 code).

---

## Previous Version Context (h-e1 Phase 4, gate PARTIAL)

### Proven Components (all validated: 35/35 tests, validator PASS, REAL_MODEL reality check)
| Component | File | Reusable |
|-----------|------|----------|
| `per_layer_lens_signals` | code/model.py | ✅ verbatim |
| `resume_from_cache` / append-mode resume | code/run_h_e1.py | ✅ verbatim |
| `verify_cache_reuse` + donor short-circuit | code/run_h_e1.py | ✅ verbatim (this IS A2-v2(a)) |
| `check_anchor_and_halt` | code/run_h_e1.py | ⚠️ MUST be re-specified per A2-v2 (only change) |
| `degeneracy_screen` → `build_auroc_grid` → `evaluate_gate` | code/analysis.py | ✅ verbatim |
| Finalized llama2/triviaqa cache | results/cache_llama2_triviaqa.csv | ✅ zero-GPU, splits assigned, protocol-verified |

### Measured Evidence (binding cell llama2/triviaqa, selection split n=500)
- Best intermediate: L31 adj_kl corrected AUROC **0.6522** (>= 0.55 ✅)
- Top-5: L31 adj_kl 0.6522, L17 adj_kl 0.6145, L30 adj_kl 0.6062, L16 maxprob 0.5909, L20 adj_kl 0.5903
- Within-sweep final-layer entropy: 0.5928 (depth_beats_final ✅)
- Degeneracy screen: 20/32 layers retained
- adj_kl dominates, concentrated in late layers (L28-31, ~L17)

### Lessons Learned
- Cross-protocol numeric anchors are unsatisfiable by construction — gate on within-protocol quantities only
- Fail-fast anchor ordering (cache-reuse cell first) saved ~2.5 h GPU
- torch 2.8.0+cu128 required (transformers 4.57.6 incompatible with torch 2.4.x — env drifted once; pin it)
- Do NOT cite v1-record AUROCs (0.5186 etc.) as same-protocol baselines anywhere downstream

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS (Phase 2C)
**Workflow Status:** ACTIVE

---

## Phase 2C Usage Notes

**This context file provides:**
1. Complete v2 hypothesis specification with A2-v2 anchor re-specification
2. Gate conditions (MUST_WORK, modification attempt 1)
3. Proven-component inventory from h-e1 Phase 4 for delta-only design
4. Within-protocol baseline quantities (0.5928-class numbers)
5. Measured existence evidence on the binding cell

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap
2. Search for implementation patterns (Archon, Exa MCP)
3. Design delta-only experiment specification (Level 1.5): re-spec `check_anchor_and_halt` per A2-v2, reuse everything else
4. Output: h-e1-v2/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: within-sweep final-layer AUROC is the per-cell floor the depth signal must exceed (A2-v2(b)); v1-record numbers are direction-only descriptive references (c)

---

*Optimized for single-hypothesis experiment design — v2 delta refinement*
