# Experiment Design: h-e1-v2

**Date:** 2026-08-05
**Author:** Anonymous
**Hypothesis Statement:** At least one screened intermediate layer (1-31) per model exhibits class-separable logit-lens statistics on the selection split: corrected AUROC >= 0.55 for at least one (layer, signal) pair among {entropy, max_token_probability, adjacent_layer_KL}, on both TriviaQA and TruthfulQA. LLaMA-2-7B is the binding existence case. Includes mandatory A2-v2 protocol-internal validity anchor: (a) donor-cache protocol identity via >= 10-example fresh-regeneration label agreement BEFORE reuse; (b) per-cell within-sweep final-layer entropy AUROC as the baseline the best screened intermediate layer must exceed (depth_beats_final); (c) v1-record direction consistency reported descriptively, NOT gated. All datasets, models, signals, thresholds, split protocol, and code unchanged from h-e1.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE — Phase 2C, UNATTENDED mode; h-e1-v2 IN_PROGRESS (version 2, SELF_MODIFY refinement of h-e1, modification attempt 1)
**Prerequisites Satisfied:** Yes — none required (Level 0 root hypothesis)
**Gate Status:** MUST_WORK, not yet evaluated; prior version h-e1 gate = PARTIAL (4/6, A2 anchor provenance flaw), reflection outcome MODIFIED → h-e1-v2

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1-v2
- **Type:** EXISTENCE
- **Prerequisites:** None (Level 0 root; dependents h-m1/h-m2/h-m3/h-c1 BLOCKED awaiting this hypothesis)

### Gate Condition
**MUST_WORK** — Primary: >= 1 screened (layer, signal) pair per model with selection-split corrected AUROC >= 0.55 on both datasets (6/6 model×dataset cells). Secondary (A2-v2): (a) donor label agreement >= 10/10 before cache reuse; (b) depth_beats_final per cell; degeneracy screen retains >= 5 layers per model. Descriptive ungated: (c) direction consistency vs v1 record. Failure stops entire workflow (screen-driven failure → tuned-lens pivot with relabeled claims). This is modification attempt 1 — a second MUST_WORK PARTIAL routes to Phase 2A-Dialogue.

---

## Continuation Context

h-e1-v2 is a delta-only refinement of h-e1 after a Phase 4 MUST_WORK PARTIAL. The v1 A2 anchor demanded reproduction of v1-record final-layer AUROCs (±0.03) that a provenance audit proved came from a 6-way different protocol (random 1000-of-7993 sample, bare prompt, substring labels, generation-time entropy, bfloat16, full-set eval) — unsatisfiable by construction. The halt gate fired correctly on the first cell (47 s instead of ~2.5 h GPU), leaving 5/6 cells intentionally unmeasured. The mechanism itself is proven: existence PASSES on the binding cell (llama2/triviaqa L31 adj_kl corrected AUROC 0.6522 >= 0.55; depth beats final 0.5928; 20/32 layers retained; 35/35 tests; validator PASS; REAL_MODEL reality check).

**The ONLY design change:** `check_anchor_and_halt` re-specified per A2-v2 (protocol-internal validity). Everything else — datasets, models, signals, thresholds, split protocol, code — reused verbatim from `h-e1/code/`.

### Previous Hypothesis Results (if applicable)
From h-e1 Phase 4 (gate PARTIAL, reflection MODIFIED):
- **Measured (binding cell llama2/triviaqa, selection n=500):** L31 adj_kl 0.6522, L17 adj_kl 0.6145, L30 adj_kl 0.6062, L16 maxprob 0.5909, L20 adj_kl 0.5903; within-sweep final-layer entropy 0.5928 (selection) / 0.5739 (full); screen retained 20/32 layers
- **Proven components (all reusable):** `per_layer_lens_signals`, `resume_from_cache`, `verify_cache_reuse` + donor short-circuit, `degeneracy_screen`→`build_auroc_grid`→`evaluate_gate`, `plot_entropy_heatmap`; finalized `results/cache_llama2_triviaqa.csv` (1000 rows, splits assigned) = zero-GPU binding cell
- **Lessons:** gate on within-protocol quantities only; fail-fast cache-first ordering; pin torch 2.8.0+cu128; never cite v1-record AUROCs (0.5186 etc.) as same-protocol baselines
- **Signal priors:** adj_kl dominates, late layers (L28-31, ~L17)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Key terms extracted:** mechanism = per-layer logit-lens uncertainty statistics (entropy / max-prob / adjacent-layer KL) for hallucination detection; domain = LLM hallucination detection / uncertainty quantification; dataset type = short-form QA benchmarks (TriviaQA, TruthfulQA), AUROC evaluation.

**Query 1** — `"logit lens hallucination detection"` (match_count=5): 0 relevant results. Top hits: Wikipedia binocular disparity, HuggingFace diffusers docs, diffusers community examples (aggregate similarity ≤ 0.37).

**Query 2** — `"layer-wise uncertainty AUROC evaluation"` (match_count=5): 0 relevant results. Top hits: diffusers llms.txt, UniPC sampler, PyTorch issue #84039, PEFT LoRA docs (similarity ≤ 0.42).

**Query 3** — `"experiment anchor validity reproducibility gate"` (match_count=5): 0 relevant results. Top hits: unrelated arXiv diffusion/vision papers (similarity ≤ 0.38).

**Conclusion: Archon KB OUT-OF-DOMAIN for this hypothesis (null result, documented).** The indexed corpus (source 8b1c7f40739544a6) is diffusion/generative-vision material with no LLM-interpretability or hallucination-detection content. This replicates the identical null finding recorded in h-e1's Phase 2C brief. The governing internal knowledge source is instead the h-e1 Phase 4 artifact set (04_validation.md Phase 2C Handoff, reflection_report.md, Serena memory `pivot_h-e1_h-e1-v2`), which supplies proven components, measured baselines, and the A2-v2 anchor rationale — used throughout this brief.

### Archon Code Examples

**Query 1** — `"logit lens intermediate layer PyTorch"` (match_count=5): 0 relevant (DALLE2-pytorch, diffusers pipelines; rerank scores ≤ −7.7).

**Query 2** — `"AUROC bootstrap evaluation sklearn"` (match_count=5): 0 relevant (mmgeneration FID eval scripts, Allegro/PixArt training launchers; rerank ≤ −10.5).

**Conclusion:** No reusable code patterns in Archon KB. Authoritative code reference = `h-e1/code/` (7 modules, 35/35 tests, validator PASS) — the primary implementation path for v2 (see Serena Code Analysis section).

### Exa GitHub Implementations

**Query 1: logit-lens / tuned-lens official implementation**

**Repository 1**: AlignmentResearch/tuned-lens (paper-author implementation, Belrose et al. 2023, arXiv:2303.08112)
- **URL**: https://github.com/AlignmentResearch/tuned-lens
- **Relevance**: Canonical lens codebase. `tuned_lens.nn.lenses.LogitLens` implements exactly our lens: identity `transform_hidden` + unembed — formula `LogitLens(h_l) = LayerNorm[h_l] W_U`, confirming the h-e1 lens path `model.lm_head(model.model.norm(h_l))` is the standard raw-logit-lens operationalization.
- **Key API**: `LogitLens.from_model(model)`, `forward(h, idx)`; `TunedLens_l(h_l) = LogitLens(A_l h_l + b_l)` is the documented RISK-1 fallback (trained translators, claims relabeled).
- **Role in v2**: reference/validation only — h-e1/code/model.py already implements the identical computation and is test-covered; no new dependency added.

**Query 2: hallucination detection AUROC on TriviaQA/TruthfulQA**

**Repository 2**: deeplearning-wisc/haloscope (NeurIPS'24 spotlight, paper-author code)
- **URL**: https://github.com/deeplearning-wisc/haloscope
- **Relevance**: Same eval skeleton — greedy "most likely" generation (`most_likely=1, num_gene=1`), TruthfulQA/TriviaQA, llama2-7B family, per-layer feature extraction (`feat_loc_svd` block/mlp/attention), AUROC readout. Confirms single-greedy-pass + per-layer features + AUROC is a published, accepted protocol shape.
- **Repository 3**: oneal2000/UniFact — AUROC evaluation harness for hallucination detection on TriviaQA with llama-3.1-8B; JSON `evaluation_summary` reporting per-method AUROC (e.g. lnpp 0.7476 on 500 items) — matches our per-cell AUROC reporting granularity.
- **Repository 4**: dasrupdip04/hallushift (HalluShift, arXiv:2504.09482 — RISK-7 novelty check subject). Uses internal distribution-shift features + BLEURT-derived labels + a trained detector on llama2-7B/TruthfulQA/TriviaQA. **Differentiation confirmed at code level:** HalluShift trains a classifier over distribution-shift features; ours is training-free per-layer statistic selection with no detector network — novelty claim (per-layer selection, transfer matrix, rescue test) stands.
- Also seen: koppula/TruthfulQA (benchmark reference, generation task + 817 questions — confirms dataset size), EMNLP 2025 "Re-evaluating Hallucination Detection" (AUROC + PR-AUC as primary metrics; ROUGE-vs-judge label caveat — our normalized-alias exact-match labels are v1-verbatim by design, held as controlled variable).

**Query 3: paired bootstrap AUROC CI**
- `scipy.stats.bootstrap(..., paired=True, method='percentile')` — stdlib-grade implementation of our exact CI procedure (example-level resampling, same indices both scores). h-e1/code/analysis.py already implements this hand-rolled (n=1000 percentile); scipy path documented as cross-check only.
- StackOverflow/Codemia canonical pattern (resample indices, `roc_auc_score` per resample, reject single-class resamples, percentile CI) matches analysis.py behavior including the single-class-resample guard tested in h-e1.

**Serena Analysis Needed**: true — target is NOT external repos but `h-e1/code/` (441-line run_h_e1.py; `check_anchor_and_halt` re-spec is the single delta for v2).

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is NOT a paper reproduction — it is a delta refinement of our own validated implementation. Priority hierarchy applied: (1) own validated code > (2) paper-author reference (AlignmentResearch/tuned-lens, used for lens-formula validation only) > (3) community repos (protocol-shape confirmation only). No external code is imported.

**Recommended Implementation Path:**
- Primary: `h-e1/code/` verbatim reuse (7 modules + 6 test files, 35/35 tests, validator PASS, REAL_MODEL reality check) with ONE re-specified function (`check_anchor_and_halt` per A2-v2), one small descriptive-report addition (clause c), and `tests/test_anchor_gate.py` updates
- Fallback: if raw lens degenerates on any model (RISK-1, screen < 5 layers), tuned-lens translators via `AlignmentResearch/tuned-lens` (`TunedLens.from_model_and_pretrained`) — documented pivot with relabeled claims (trained components)
- Justification: v1 code is already protocol-exact, test-covered, and production-fired; reuse minimizes delta risk and preserves cache/split compatibility with dependents (h-m1/h-m2/h-m3/h-c1 consume the 5+96 cache schema and locked splits unchanged)

### Code Analysis (Serena MCP)

**Target:** `h-e1/code/` (validated implementation, 35/35 tests) — analyzed to scope the v2 delta precisely.

**Code Structure (Serena `get_symbols_overview`):**
- `run_h_e1.py` (441 lines): `_cache_header_ok`, `resume_from_cache`, `verify_cache_reuse`, `generate_and_extract`, `write_cache_row`, `run_sweep`, `smoke_test`, `check_anchor_and_halt`, `run_model`, `analyze_all`, `build_parser`, `main`; constants `CACHE_FIELDS`, `LOADERS`, `DONOR_CACHE_LLAMA2_TRIVIAQA`
- `analysis.py`: `degeneracy_screen`, `corrected_auroc`, `build_auroc_grid`, `check_baseline_anchor`, `verify_mechanism_activated`, `evaluate_gate`, `write_cell_report`; constant `SIGNALS`
- Support: `model.py` (lens path), `data.py` (loaders/labels), `visualize.py`, `constants.py`, `generate_figures.py`, `tests/` (6 files)

**Key symbol bodies inspected (`find_symbol`, include_body):**

1. `check_anchor_and_halt(model_key, dataset_name, cache_df)` (run_h_e1.py:260-294) — **THE v2 DELTA.** Currently: selection-split final-layer (L32) entropy AUROC compared to `H_E1_REFERENCES[(model_key, dataset)]` with `BASELINE_TOLERANCE` ±0.03; `SystemExit` on breach (this fired in Phase 4), `ValueError` on contract violations (pending split, single-class labels). The `H_E1_REFERENCES` comparison and `SystemExit` numeric branch must be REMOVED; contract-violation `ValueError` guards are protocol-internal and must be KEPT.

2. `verify_cache_reuse(model, tokenizer, cache_path, dataset, dataset_name, n_check=10)` (run_h_e1.py:77-106) — **already implements A2-v2(a) verbatim**: regenerates first 10 examples fresh, compares `label_response` output to donor rows, handles empty-answer symmetry; any drift → False → fresh generation fallback (never silently drops the cell). Passed 10/10 live in Phase 4. Zero changes needed.

3. `run_model(model_key)` (run_h_e1.py:297-312) — orchestration: smoke → per-dataset `run_sweep` (with donor reuse short-circuit for llama2/triviaqa) → `check_anchor_and_halt` after each cell. Structure retained; only the called anchor semantics change.

4. `evaluate_gate(auroc_grid, retained_layers)` (analysis.py:76-97) — **already implements A2-v2(b) verbatim**: computes `final_layer_entropy_auroc` from the same sweep grid, `best_auroc` over INTERMEDIATE retained layers only (excludes idx 31 = L32), and returns `depth_beats_final = best_auroc > final_auroc` plus `gate_pass = best_auroc >= AUROC_GATE (0.55)`. Zero changes needed.

**Integration conclusion (delta-only design):**

| A2-v2 clause | Implementing symbol | Status |
|---|---|---|
| (a) donor protocol identity, >= 10 examples | `verify_cache_reuse` | ✅ exists, tested, passed live |
| (b) depth_beats_final vs within-sweep final layer | `evaluate_gate` | ✅ exists, tested, ran on real cell |
| (c) descriptive direction-consistency report | new ~15-line reporting function | ➕ add (ungated, report-only) |
| retire cross-protocol numeric halt | `check_anchor_and_halt` | ✏️ re-spec (see pseudo-code) |

The v2 implementation is a 1-function re-spec + 1 small reporting addition + test updates (`tests/test_anchor_gate.py`); everything else (~1,300 lines + 5 test files) reused verbatim.

---

## Experiment Specification

### Dataset

**Confirmed from Phase 2A via Phase 2B (02b_context.md) — NOT re-selected. Identical to h-e1.**

| Field | Dataset 1 | Dataset 2 |
|-------|-----------|-----------|
| Name | TriviaQA (rc.nocontext) | TruthfulQA (generation) |
| Type | **standard** (synthetic policy: PASS) | **standard** (synthetic policy: PASS) |
| HF identifier | `mandarjoshi/trivia_qa`, config `rc.nocontext` | `truthfulqa/truthful_qa`, config `generation` |
| Split used | `validation[:1000]` (first slice, NOT random — v1-verbatim) | `validation` (all 817) |
| Full split size | validation 17,944 (rc.nocontext) | 817 |
| Labels | normalized-alias exact match vs `answer.normalized_aliases`/`normalized_value` | correct/incorrect vs reference answers, v1-verbatim `label_response` in data.py |
| Eval N | 1,000 (500 selection / 500 test) | 817 (408/409 stratified) |

**Total evaluation samples: 1,817 per model × 3 models = 5,451 scored generations** — full standard eval protocol, no subsampling below plan, no synthetic data. HF cache verified present (h-e1 Phase 4 task-001).

**Preprocessing (v1-verbatim, controlled variables — DO NOT CHANGE):**
- Prompt template: `"Q: {question}\nA:"` (not bare question)
- Greedy decoding, `do_sample=False`, `max_new_tokens=32`
- Answer-token span: teacher-forced re-forward over generated answer tokens; per-token statistics streamed
- Split: stratified 50/50 selection/test per dataset, seed 42; llama2/triviaqa split ALREADY LOCKED in `h-e1/results/test_split_locked_llama2_triviaqa.json` — reuse, never recompute
- Augmentation: none (training-free evaluation)

**Cache reuse (A2-v2(a)):** `h-e1/results/cache_llama2_triviaqa.csv` (1000 rows, 5+96 cols, splits finalized, protocol-verified 10/10) → zero-GPU binding cell. Reuse REQUIRES fresh `verify_cache_reuse` pass in the v2 run.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `datasets.load_dataset` (already cached; reuse `data.py` loaders verbatim)
- Identifier: `mandarjoshi/trivia_qa` (config `rc.nocontext`) + `truthfulqa/truthful_qa` (config `generation`)
- Code:
```python
from datasets import load_dataset
trivia = load_dataset("mandarjoshi/trivia_qa", "rc.nocontext", split="validation[:1000]")
tqa    = load_dataset("truthfulqa/truthful_qa", "generation", split="validation")  # 817
```

### Models

#### Baseline Model

**Confirmed from Phase 2A via Phase 2B — NOT re-selected. Identical model set to h-e1 (continuation: controlled comparison, only anchor semantics change).**

| Model | HF identifier | Layers | Dtype | Role |
|-------|---------------|--------|-------|------|
| LLaMA-2-7B | `meta-llama/Llama-2-7b-hf` | 32 | fp16 | binding existence case |
| Mistral-7B | `mistralai/Mistral-7B-v0.1` | 32 | fp16 | base-model robustness |
| LLaMA-3-8B-Instruct | `meta-llama/Meta-Llama-3-8B-Instruct` | 32 | fp16 | instruct-model case (R3 scope note) |

All frozen (no training, no gradients). Single GPU (H100 verified; peak 13.59 GB at batch 1 in h-e1 smoke). Uniform lens path across all three: `model.lm_head(model.model.norm(h_l))` — LSP-verified in `model.py:per_layer_lens_signals` with layout assert (`validate_layout`).

**Baseline score (within-sweep, A2-v2(b)):** per-cell final-layer (L32) mean-answer-token entropy AUROC computed from the SAME sweep — the floor the best screened intermediate layer must exceed. Measured value for binding cell: 0.5928 (selection split). No external/cross-protocol baseline constants.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `transformers` (already in HF cache; reuse `model.py:load_model` verbatim)
- Identifier: `meta-llama/Llama-2-7b-hf`, `mistralai/Mistral-7B-v0.1`, `meta-llama/Meta-Llama-3-8B-Instruct`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16,
                                             device_map="cuda", output_hidden_states=True)
tokenizer = AutoTokenizer.from_pretrained(model_id)
model.eval()
```
- Env pin: conda `youra-h-e1` — python 3.10.20, torch 2.8.0+cu128, transformers 4.57.6 (torch 2.4.x incompatible; env drifted once in v1 — pin it)

#### Proposed Model

**Architecture:** Frozen decoder-only LLM + per-layer logit-lens readout (training-free; no weights modified). "Proposed" = best screened INTERMEDIATE (layer, signal) score; "baseline" = same sweep's final-layer (L32) entropy score. Both computed from one teacher-forced re-forward per example — the comparison is within-model, within-protocol by construction (A2-v2(b)).

**Integration point:** `output_hidden_states=True` on the single greedy pass + teacher-forced re-forward; lens applied to every hidden state h_l via `model.lm_head(model.model.norm(h_l))` (uniform across all 3 models, layout-asserted). Implemented and validated in `h-e1/code/model.py:per_layer_lens_signals` — reused verbatim.

**Signals per layer l ∈ {1..32}, mean over answer tokens (float32, log(p+1e-12) guard):**
1. `entropy_l` = Shannon entropy of softmax(lens logits)
2. `maxprob_l` = max-token probability
3. `adj_kl_l` = KL(p_l ‖ p_{l-1}) (NaN at l=1, excluded)

**Core Mechanism Implementation (v2 DELTA — re-specified `check_anchor_and_halt` per A2-v2; grounded in Serena-analyzed run_h_e1.py:260-294):**

```python
# A2-v2 protocol-internal anchor (replaces v1 cross-protocol numeric gate)
# Clause (a) donor identity: verify_cache_reuse(...) — UNCHANGED, runs BEFORE reuse
# Clause (b) depth_beats_final: evaluate_gate(...) — UNCHANGED, per-cell readout
# This function now checks only WITHIN-PROTOCOL validity contracts:

def check_anchor_and_halt(model_key, dataset_name, cache_df):
    """A2-v2: protocol-internal validity. Halts only on contract violations
    (invalid split / undefined AUROC), NEVER on cross-protocol numeric deltas.
    v1-record numbers are logged descriptively per clause (c), not gated."""
    sel = cache_df[cache_df["split"] == "selection"]
    if sel.empty:
        raise ValueError("no 'selection' rows -- finalize split before anchor")   # kept from v1
    labels, scores = sel["label"].to_numpy(), sel["entropy_L32"].to_numpy()
    if len(np.unique(labels)) < 2:
        raise ValueError("single-class selection split -- AUROC undefined")       # kept from v1
    final_auroc, direction = corrected_auroc(labels, scores)   # within-sweep baseline, clause (b) input
    # clause (c): descriptive direction-consistency report vs v1 record (NO gate, NO SystemExit)
    v1 = V1_DIRECTION_RECORD.get((model_key, dataset_name))    # {"direction": "inverted", ...}
    log.info(f"A2-v2 anchor: {model_key}/{dataset_name} within-sweep final L32 "
             f"entropy AUROC={final_auroc:.4f} direction={direction} "
             f"v1_record_direction={v1} consistent={direction == v1}")
    return final_auroc   # consumed by evaluate_gate's depth_beats_final check

# REMOVED vs v1: H_E1_REFERENCES lookup, BASELINE_TOLERANCE +/-0.03 check,
#                SystemExit numeric-breach branch (unsatisfiable by construction)
```

All other symbols (`per_layer_lens_signals`, `run_sweep`, `resume_from_cache`, `verify_cache_reuse`, `degeneracy_screen`, `build_auroc_grid`, `evaluate_gate`) reused verbatim from `h-e1/code/`.

### Training Protocol

**Training-free method — no optimizer, no learning rate, no loss, no epochs.** All "protocol" is inference-sweep configuration, inherited verbatim from h-e1 (validated 35/35 tests, REAL_MODEL check):

**From Previous Hypothesis (h-e1):**
- **Decoding**: greedy (`do_sample=False`), `max_new_tokens=32`, batch 1
- **Numerics**: fp16 weights / float32 statistics, `log(p+1e-12)` guard, KL NaN at layer 1 excluded
- **Split**: stratified 50/50 selection/test per dataset, **seed 42** (1 seed — EXISTENCE PoC); llama2/triviaqa test split already locked (reuse `test_split_locked_llama2_triviaqa.json`)
- **Sweep**: per-example streaming to resumable CSV (5+96 cols schema: 3 signals × 32 layers), append-mode resume keyed by example_id, corrupt-tail truncation
- **Execution order (fail-fast, per run_model)**: smoke (10 ex, shape+memory assert) → per-cell sweep → A2-v2 anchor report after each cell; llama2/triviaqa first via donor reuse (zero GPU after `verify_cache_reuse` 10/10)
- **Degeneracy screen (selection split only)**: drop layers with entropy within 1% of ln|V| OR top-1 agreement with final layer < 5%; health = retain >= 5 layers/model
- **Compute**: 1× H100, ~2.5 h GPU for the 5 fresh cells (llama2/truthfulqa, mistral×2, llama3×2); binding cell zero-GPU

**Rationale:** Optimal and validated in h-e1; unchanged by design (controlled comparison — only anchor semantics differ).

### Evaluation

**Primary Metric:**
- **AUROC_corrected** on selection split, per (layer, signal, model, dataset) cell: `max(auroc, 1-auroc)` of the raw score vs binary correct/incorrect label (direction-corrected; direction recorded). Implemented in `analysis.py:corrected_auroc` (v1-verbatim).

**Success Criteria (EXISTENCE — direction only, no statistical tests):**
1. **Primary (gate):** >= 1 screened (layer, signal) pair per model with selection-split corrected AUROC >= 0.55 on BOTH datasets — all 6 model×dataset cells measured (v1 measured 1/6 before halt)
2. **A2-v2(a):** `verify_cache_reuse` label agreement 10/10 before any donor/finalized-cache reuse
3. **A2-v2(b):** `depth_beats_final` = best intermediate corrected AUROC > within-sweep final-layer (L32) entropy corrected AUROC, per cell
4. **Screen health:** degeneracy screen retains >= 5 layers per model
5. **A2-v2(c) (descriptive, ungated):** direction-consistency report vs v1 record (llama2 final-layer weak/inverted, llama3 strongest)

**Expected Baseline Performance (within-sweep, measured):**
- llama2/triviaqa final-layer entropy: 0.5928 (selection split, h-e1 Phase 4) — best intermediate already measured at 0.6522 (L31, adj_kl), so the binding cell is expected to PASS again from cache
- Remaining 5 cells: final-layer AUROC computed within the v2 sweep; priors from research (FEPoID-class signals 0.52-0.66 final-layer range per v1 record direction data)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: binary score-ranking (hallucination detection), training-free
- Library: `sklearn.metrics` (+ numpy percentile bootstrap already in analysis.py — not gated for EXISTENCE)
- Code: `from sklearn.metrics import roc_auc_score; auc = roc_auc_score(labels, scores); corrected = max(auc, 1 - auc)`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

Recommended (proven renderers exist in `visualize.py` + `generate_figures.py` — reuse):
1. **AUROC vs depth curve** per cell: 3 signal curves across layers 1-32, with 0.55 gate line and final-layer baseline line (v1 `auroc_vs_depth_*.png` renderer) — now for ALL 6 cells
2. **A2-v2 anchor report figure**: per-cell within-sweep final-layer AUROC + direction-consistency markers vs v1 record (replaces v1's breach-band `anchor_check_*.png`)
3. **Degeneracy screen retention** per model (`degeneracy_screen_*.png` renderer)
4. **Entropy heatmap** examples × layers, correct vs incorrect groups, per model (`plot_entropy_heatmap`, FR-5.6)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1-v2/figures/`. No figures for unmeasured cells (v1 rule retained).

---

## 🔬 Mechanism Verification Protocol (CRITICAL)

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | All 3 models are pre-LN decoder-only with exposed `model.model.norm` + `model.lm_head`; hidden states available via `output_hidden_states=True` (33 states = embeddings + 32 layers, smoke-asserted in v1) | TRUE |
| Mechanism Isolatable | Intermediate-layer score vs final-layer (L32) score from the same sweep — toggle is the layer index; no code branch needed | TRUE |
| Baseline Measurable | Final-layer entropy AUROC computed per cell within the sweep (measured 0.5928 on binding cell) | TRUE |

### Architecture Compatibility Check

All three models (Llama-2-7b-hf, Mistral-7B-v0.1, Meta-Llama-3-8B-Instruct) are 32-layer pre-LN decoder-only transformers with tied unembedding path `lm_head(norm(h))`. `validate_layout(model)` (model.py, v1-tested) asserts: 32 decoder layers, final RMSNorm present, lm_head shape matches vocab. LLaMA/Mistral lineage is the documented best-behaved raw-lens family [Belrose et al. 2023].

**Required Features:** `output_hidden_states=True` support; accessible `model.model.norm` and `model.lm_head`.
**Incompatible Architectures:** post-LN models, encoder-decoder, models with untied/absent lens path (none in our set).

> ⚠️ If `validate_layout` fails, Phase 4 MUST fail early (existing behavior).

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"A2-v2 anchor: {cell} within-sweep final L32 entropy AUROC=... direction=... consistent=..."` per cell + `"verify_cache_reuse: 10 examples consistent -> reuse OK"` before any reuse | run_h_e1.py (`check_anchor_and_halt`, `verify_cache_reuse`) |
| Tensor Shape | Per example: 33 hidden states; cache row = 5 meta + 96 signal cols (3 signals × 32 layers); adj_kl NaN at L1 only | model.py `per_layer_lens_signals`; smoke assert |
| Metric Delta | Per cell: best intermediate corrected AUROC ≠ final-layer AUROC (non-degenerate grid); `depth_beats_final` computed | analysis.py `evaluate_gate` |

**Activation Verification Code (Phase 4 must implement — `verify_mechanism_activated` exists in analysis.py, extend for v2):**

```python
def verify_mechanism_activated(experiment_log, results):
    indicators = {
        "reuse_verified": "verify_cache_reuse: 10 examples consistent" in experiment_log
                          or "fresh generation" in experiment_log,          # (a)
        "anchor_reported": all(f"A2-v2 anchor: {c}" in experiment_log
                               for c in results["completed_cells"]),        # (b)+(c) logged
        "grid_nondegenerate": all(r["best_auroc"] != r["final_layer_entropy_auroc"]
                                  for r in results["cells"].values()),
        "screen_healthy": all(r["retained_layers"] >= 5 for r in results["cells"].values()),
        "all_cells_measured": len(results["completed_cells"]) == 6,          # v1 stopped at 1
    }
    return all(indicators.values()), indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Cache reuse without identity check | reuse log line absent before donor short-circuit | FAIL: A2-v2(a) violated |
| Lens degenerate (RISK-1) | screen retains < 5 layers on any model | FAIL: document; tuned-lens pivot per plan |
| Anchor not reported | missing per-cell A2-v2 log line | FAIL: anchor protocol not executed |
| Sweep incomplete (RISK-6) | completed_cells < 6 with no contract violation raised | FAIL: resume from streamed CSV, re-run |
| Cross-protocol constant reintroduced | `H_E1_REFERENCES` numeric gate present in code | FAIL: v2 spec violation (regression to v1 flaw) |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE | all activation indicators above |
| Effect Measurable | grid non-degenerate, 6/6 cells | `evaluate_gate` outputs per cell |
| Hypothesis Supported | >= 1 screened (layer, signal) pair per model with corrected AUROC >= 0.55 on both datasets AND depth_beats_final per cell | selection-split corrected AUROC (analysis.py) |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Null result (documented):** 5 queries executed (3 KB: "logit lens hallucination detection", "layer-wise uncertainty AUROC evaluation", "experiment anchor validity reproducibility gate"; 2 code: "logit lens intermediate layer PyTorch", "AUROC bootstrap evaluation sklearn"; + 2 loading queries in Step 5). Indexed corpus (source `8b1c7f40739544a6`) is diffusion/generative-vision — 0 relevant results, similarity ≤ 0.47. Replicates h-e1 Phase 2C null finding. **Used For:** confirming no prior in-KB case supersedes the h-e1 internal artifact set.

### B. GitHub Implementations (Exa)

**Repository 1**: AlignmentResearch/tuned-lens (paper-author: Belrose et al., arXiv:2303.08112)
- **URL**: https://github.com/AlignmentResearch/tuned-lens
- **Query Used**: "logit lens tuned-lens Belrose official implementation intermediate layer decoding transformer"
- **Key Code**: `LogitLens(h_l) = LayerNorm[h_l] W_U` (`tuned_lens.nn.lenses.LogitLens`, identity `transform_hidden`); `TunedLens_l(h_l) = LogitLens(A_l h_l + b_l)`
- **Used For**: validation of our lens path as the standard raw-lens formula; RISK-1 tuned-lens fallback path (`TunedLens.from_model_and_pretrained`)

**Repository 2**: deeplearning-wisc/haloscope (NeurIPS'24 spotlight)
- **URL**: https://github.com/deeplearning-wisc/haloscope
- **Query Used**: "hallucination detection AUROC evaluation TriviaQA TruthfulQA LLM code"
- **Config Extracted**: `most_likely=1, num_gene=1` greedy protocol; per-layer feature location flags; llama2-7B + tqa/triviaqa
- **Used For**: protocol-shape confirmation (single greedy pass + per-layer features + AUROC is published practice)

**Repository 3**: oneal2000/UniFact — https://github.com/oneal2000/UniFact — AUROC harness granularity reference (per-method per-dataset JSON summaries; lnpp 0.7476/500 items). **Used For:** evaluation reporting format.

**Repository 4**: dasrupdip04/hallushift (arXiv:2504.09482) — https://github.com/dasrupdip04/hallushift — **Used For:** RISK-7 novelty check at code level: trained classifier over distribution-shift features ≠ our training-free per-layer statistic selection; novelty claim stands.

**Repository 5**: koppula/TruthfulQA — https://github.com/koppula/TruthfulQA — benchmark reference (817 questions, generation task). **Used For:** dataset statistics confirmation.

**Statistics references**: `scipy.stats.bootstrap(paired=True, method='percentile')` (docs.scipy.org); jacobgil/confidenceinterval (bootstrap_bca AUROC CI); canonical index-resampling pattern (StackOverflow 52373318/19124239). **Used For:** cross-check documentation of analysis.py's hand-rolled paired percentile bootstrap (not gated in this EXISTENCE PoC).

**HF loading references**: huggingface.co/datasets/mandarjoshi/trivia_qa (rc.nocontext, validation 17,944); huggingface.co/docs/transformers models guide (`AutoModelForCausalLM.from_pretrained(..., torch_dtype=torch.float16)`). **Used For:** dataset/model loading blocks.

### C. Code Analysis (Serena)

**Analyzed Code**: `h-e1/code/` (own validated implementation)
- **Analysis Method**: Serena MCP semantic analysis
- **Tools Used**:
  - `get_symbols_overview` on run_h_e1.py + analysis.py: full symbol inventory (12 + 8 functions)
  - `find_symbol` (include_body): `check_anchor_and_halt` (260-294), `verify_cache_reuse` (77-106), `run_model` (297-312), `evaluate_gate` (analysis.py 76-97)
- **Key Findings**: A2-v2(a) already implemented (`verify_cache_reuse`, 10-example regeneration check); A2-v2(b) already implemented (`evaluate_gate.depth_beats_final` vs within-grid final layer); only `check_anchor_and_halt`'s `H_E1_REFERENCES`/±0.03/`SystemExit` branch must be removed (contract-violation `ValueError` guards kept); clause (c) needs a ~15-line descriptive report
- **Used For**: v2 delta pseudo-code (Experiment Specification) and Mechanism Verification Protocol

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Report — h-e1
- **Files**: `h-e1/04_validation.md` (incl. Phase 2C Handoff), `h-e1/reflection_report.md`, `h-e1/experiment_results.json`, Serena memory `pivot_h-e1_h-e1-v2`
- **Reused Components**: entire `code/` tree (1 function re-spec); finalized `results/cache_llama2_triviaqa.csv` (zero-GPU binding cell); locked test split; conda env `youra-h-e1` (torch 2.8.0+cu128)
- **Measured priors**: L31 adj_kl 0.6522 (binding cell), final-layer 0.5928, screen 20/32, adj_kl dominant in late layers
- **Why Reused**: controlled comparison — only the anchor operationalization changes; dependent interfaces (cache schema, splits) preserved

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection + splits | Phase 2A via 02b_context.md + HF docs | Fixed selection; B (HF loading refs) |
| Preprocessing / prompts / labels | Previous hypothesis (v1-verbatim) | D |
| Baseline (within-sweep final layer) | Previous hypothesis + Serena | D, C (`evaluate_gate`) |
| Lens mechanism + pseudo-code | Serena + paper-author repo | C, B.1 |
| A2-v2 anchor re-spec | Reflection report + Serena | D, C (`check_anchor_and_halt`) |
| Sweep/training protocol | Previous hypothesis | D |
| Evaluation metrics | Phase 2B success criteria + sklearn | 02b_verification_plan.md, B (stats refs) |
| Protocol-shape validation | Community repos | B.2, B.3 |
| Novelty check (RISK-7) | Community repo | B.4 |
| RISK-1 fallback | Paper-author repo | B.1 |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-05

### Workflow History for This Hypothesis
- 2026-08-05T07:49:42Z — h-e1-v2 created by Phase 4 reflection (SELF_MODIFY, modification attempt 1): A2 anchor provenance flaw → A2-v2 protocol-internal anchor; existence evidence preserved (llama2/triviaqa L31 adj_kl 0.6522)
- 2026-08-05T07:58:22Z — set IN_PROGRESS by hypothesis loop (Phase 2C → 3 → 4)
- 2026-08-05T08:00:00Z — Phase 2C started (UNATTENDED); 02b_context.md JIT-generated with v1 evidence + A2-v2 delta
- 2026-08-05 — Phase 2C completed: Level 1.5 delta-only brief (1-function re-spec + clause-c report; everything else verbatim reuse); Archon KB out-of-domain (null documented); 7+ Exa sources; Serena analysis of h-e1/code/

### Quality Validation (Step 8)

| Check | Result |
|-------|--------|
| All hyperparameters justified | ✅ all inherited from h-e1 validated run (source: 04_validation.md) or Phase 2B plan |
| Dataset choice justified | ✅ Phase 2A selection, standard real datasets, full splits (1,817 eval samples × 3 models), synthetic policy PASS |
| Mechanism grounded in code | ✅ pseudo-code derived from Serena-read `run_h_e1.py:260-294` bodies, not invented |
| No unsupported assumptions | ✅ every claim traced (Traceability Matrix E) |
| Full traceability | ✅ Appendix A-E complete |
| EXISTENCE PoC compliance | ✅ no statistical-test section, no ablation section, 1 seed, direction-based success |
| MCP sources cited | ✅ 7 Exa sources + Serena analysis + 7 Archon queries (KB null result documented) |

**Limitation noted (UNATTENDED):** Archon KB is out-of-domain for LLM-interpretability content (diffusion/vision corpus) — internal h-e1 artifact set substitutes as the governing knowledge source; identical to the precedent recorded in h-e1's Phase 2C.

**Overall: PASSED**

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
