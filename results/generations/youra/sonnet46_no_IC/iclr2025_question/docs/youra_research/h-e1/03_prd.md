---
title: "PRD: h-e1 — Layer-Wise Logit-Lens Existence Sweep (v2)"
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
gate: MUST_WORK
tier: LIGHT
date: 2026-08-05
author: Anonymous
source: 02c_experiment_brief.md
stepsCompleted: [executive-summary, problem-statement, functional-requirements, nfrs, success-criteria, dependencies]
note: "BMAD bmm PRD workflow not installed in this environment; PRD generated directly from Phase 2C brief following BMAD v6 PRD section structure (deviation logged in Phase 3 summary). Consistent with prior-episode precedent (_archive/20260805T054934)."
---

# PRD: h-e1 — Per-Layer Logit-Lens Hallucination Signal Existence Sweep

## Executive Summary

Inference-only, training-free PoC establishing whether class-separable hallucination signals exist at intermediate transformer layers (1–31). For each of three frozen 32-layer LLMs (LLaMA-2-7B, Mistral-7B-v0.1, LLaMA-3-8B-Instruct), run greedy single-pass generation on TriviaQA rc.nocontext validation[:1000] and TruthfulQA generation validation (817), teacher-force a re-forward with `output_hidden_states=True`, extract per-layer logit-lens scalars (Shannon entropy, max-token probability, adjacent-layer KL) via the uniform lens path `model.lm_head(model.model.norm(h_l))` in float32, stream rows to resumable per-cell CSV caches, apply the degeneracy screen, and compute corrected AUROC = max(AUROC, 1−AUROC) per (layer, signal) on the SELECTION split only. Pass (Gate 1, MUST_WORK): ≥ 1 screened (layer, signal) pair per model with selection-split corrected AUROC ≥ 0.55 on BOTH datasets, AND the A2 protocol-validity anchor (all 6 v1 final-layer entropy AUROCs reproduced within ±0.03) checked BEFORE the full sweep. Primary implementation path: near-verbatim reuse of the Serena-verified v1 archive codebase plus the 1000-row `cache_llama2_triviaqa.csv` after protocol-identity hash verification.

## Problem Statement

Final-layer uncertainty signals collapse on some architectures: the v1 record shows final-layer entropy AUROC 0.5186 (TriviaQA) / 0.5153 (TruthfulQA) on LLaMA-2-7B — chance level — while LLaMA-3-8B reaches 0.6583/0.6161. If intermediate layers preserve the separation between resolved and unresolved candidate competition that final-layer output calibration suppresses, a depth-resolved logit-lens readout should recover a usable signal. h-e1 must establish that the signal EXISTS before h-m1 (rescue), h-m2 (robustness), h-m3 (fusion), and h-c1 (transfer) can exploit it. MUST_WORK gate: failure kills the entire hypothesis tree; screen-driven failure (A1 lens degeneracy) triggers a documented pivot decision to tuned-lens translators. The v1 episode died at 871/1000 llama2/TriviaQA examples from an infrastructure interruption (RISK-6), so streaming resumable scalar writes are a hard requirement, not an optimization.

## Functional Requirements

### FR-1: Dataset Loading & Partitioning
- FR-1.1: Load TriviaQA `mandarjoshi/trivia_qa` config `rc.nocontext`, split `validation[:1000]` (deterministic first-1000 slice, v1-identical). Fields: `question`, `answer.aliases`/`normalized_aliases`.
- FR-1.2: Load TruthfulQA `truthfulqa/truthful_qa` config `generation`, split `validation`, all 817 rows. Fields: `question`, `correct_answers`, `incorrect_answers`.
- FR-1.3: Reuse v1-verbatim `format_prompt` (few-shot QA template) and `label_response` protocols (TriviaQA: normalized-alias match; TruthfulQA: similarity to correct vs incorrect references per sylinrl/TruthfulQA provenance).
- FR-1.4: Stratified 50/50 selection/test partition per dataset, stratified on correctness label, `SEED=42`, via v1 `stratified_split` + `write_test_split_locked` → `data_splits.json`. Test split written to disk but NEVER read by h-e1 analysis (locked for h-m1). Selection split sizes: TriviaQA 500, TruthfulQA 408.

### FR-2: Model Loading (all three baselines — none omitted)
- FR-2.1: `meta-llama/Llama-2-7b-hf` — binding existence case (final-layer FAIL 0.5186 to escape).
- FR-2.2: `mistralai/Mistral-7B-v0.1` — v1-passing architecture, no-regression reference.
- FR-2.3: `meta-llama/Meta-Llama-3-8B-Instruct` — v1-passing, only instruct model (R3 scope note).
- FR-2.4: fp16 weights, `device_map="auto"`, `model.eval()`, single GPU; gated repos require `HF_TOKEN` env var (v1 `constants.py` guard). `validate_layout` asserts 32 layers, `model.model.norm` + `model.lm_head` present, `len(hidden_states) == 33`; raise `LayoutError` early otherwise (never silently mis-lens).

### FR-3: Generation & Extraction
- FR-3.1: Greedy decoding (`do_sample=False`, `MAX_NEW_TOKENS=32`, v1-identical); answer-span extraction via v1 `_first_line`/`_normalize`.
- FR-3.2: Teacher-forced re-forward of prompt+answer with `output_hidden_states=True`; per-layer lens readout `logits_l = lm_head(norm(h_l)).float()`, skipping embedding state index 0, float32 statistics.
- FR-3.3: Three signals per layer, mean over answer tokens (v1 `per_layer_lens_signals`, model.py:27-59): Shannon entropy, max-token probability, adjacent-layer KL(l‖l−1) with `adj_kl[0]=NaN`; plus `top1_match` vs final-layer argmax for the degeneracy screen. Single `prev_logp` buffer — no 32-layer logit stack (memory-safe).
- FR-3.4: Streaming resumable cache (RISK-6): `write_cache_row` appends one row per example to `cache_{model}_{dataset}.csv` immediately; schema `example_id, dataset, model, split, label, entropy_L1..L32, maxprob_L1..L32, adj_kl_L1..L32` (5 + 96 columns). Resume by example_id on interruption — no recomputation.
- FR-3.5: Cache reuse: `_archive/20260805T054934_routing_recovery/h-e1/results/cache_llama2_triviaqa.csv` (1000 rows) reused for the llama2/TriviaQA cell AFTER protocol-identity verification — prompt + label hash check against freshly generated rows on ≥ 10 examples.
- FR-3.6: Smoke test FIRST: `SMOKE_N=10` examples per model — assert 33 hidden states, finite signals, memory ceiling (v1 `smoke_test`).

### FR-4: Analysis (selection split only)
- FR-4.1: A2 anchor check BEFORE full sweep (halt gate): final-layer entropy AUROC per cell must be within `BASELINE_TOLERANCE=0.03` of `H_E1_REFERENCES` (llama2 0.5186/0.5153, mistral 0.5268/0.5886, llama3 0.6583/0.6161 TriviaQA/TruthfulQA). Outside tolerance → HALT, reconcile labels/prompts (RISK-2); llama2/TriviaQA cell computable from reused cache after hash verification.
- FR-4.2: Degeneracy screen on selection split: drop layers with entropy within 1% of ln|V| (`DEGENERACY_ENTROPY_PCT=0.01`) OR top-1 agreement with final layer < 5% (`DEGENERACY_AGREEMENT_MIN=0.05`).
- FR-4.3: Corrected AUROC grid: `max(auc, 1−auc)` per screened (layer, signal) per model per dataset via `sklearn.metrics.roc_auc_score`; raw direction logged (`"raw_auc={x:.4f} flipped={bool}"`, R8 diagnostic); NaN cells (adj_kl layer 1) pre-filtered.
- FR-4.4: Existence criterion per model: ≥ 1 screened (layer, signal) pair with corrected selection-split AUROC ≥ `AUROC_GATE=0.55` on BOTH datasets (`evaluate_gate`).
- FR-4.5: Mechanism-activation verification (`verify_mechanism_activated`): signals finite, layer variation (nanstd of entropy AUROC grid > 0.005), anchor reproduced ±0.03, screen retains ≥ 5 layers.

### FR-5: Reporting & Figures
- FR-5.1: Per-cell reports (model × dataset) via `write_cell_report`: AUROC grid, screened layers, anchor delta, positive/negative counts.
- FR-5.2: Mandatory figure — gate metrics comparison bar chart (target vs actual).
- FR-5.3: AUROC-vs-layer curves per model per dataset (3 signal lines + final-layer entropy baseline horizontal + 0.55 gate line); llama2/TriviaQA panel is the headline.
- FR-5.4: Anchor reproduction chart — reproduced vs reference final-layer AUROCs with ±0.03 band.
- FR-5.5: Degeneracy screen map — retained/dropped layers per model with both criteria.
- FR-5.6: Per-layer entropy heatmap (examples × layers, correct vs incorrect groups, llama2) — mechanism intuition figure.
- FR-5.7: All figures saved to `h-e1/figures/`; figure generation logic included in experiment code (Phase 4 mandate).

### Ablations
None — EXISTENCE PoC. The layer × signal sweep itself IS the search space; Phase 2C defines no separate ablation variants.

## Non-Functional Requirements

- NFR-1: Single GPU; 7–8B fp16 ≈ 14–16 GB; batch size 1 (single-example streaming, v1-identical).
- NFR-2: Deterministic: single seed 42 (partition + example order), greedy decoding; 1 seed total (EXISTENCE PoC).
- NFR-3: Numerics: fp16 weights, float32 statistics; final RMSNorm before unembed; `log(p+1e-12)`-style guard; KL NaN at layer 1 excluded from grids.
- NFR-4: LIGHT infrastructure tier — argparse/hardcoded constants acceptable (v1 `constants.py` pattern), print + CSV logging, smoke test only (no unit-test suite, no WandB).
- NFR-5: Scale: 1,817 evaluation examples × 3 models = 5,451 example-model pairs; full standard splits, no subsampling (with llama2/TriviaQA cache reuse, ≈ 4,451 fresh generation+re-forward pairs).
- NFR-6: Resumability: any interruption of the sweep must lose at most the in-flight example (streamed CSV, RISK-6).

## Success Criteria

1. **Primary (Gate 1, MUST_WORK):** ≥ 1 screened (layer, signal) pair per model with selection-split corrected AUROC ≥ 0.55 on BOTH TriviaQA and TruthfulQA — all three models; LLaMA-2-7B is the binding case.
2. **A2 anchor (halt gate, checked FIRST):** all 6 final-layer entropy AUROCs within ±0.03 of v1 references.
3. **Screen health (secondary):** degeneracy screen retains ≥ 5 layers per model (RISK-1 early warning → tuned-lens pivot decision).
4. **PoC direction check:** best screened intermediate-layer corrected AUROC > final-layer entropy AUROC (same model/dataset, same sweep).
5. Code runs end-to-end without error; caches, per-cell reports, and figures produced.

**Failure semantics (MUST_WORK):** existence miss → STOP workflow, A1/A2 autopsy (lens degeneracy vs anchor break), block h-m1/h-m2/h-m3/h-c1. Anchor break → HALT before sweep, reconcile protocol. No statistical tests for PoC (direction-based).

## Dependencies

- Python: `torch`, `transformers`, `datasets`, `scikit-learn`, `numpy`, `matplotlib` (+ `tuned-lens` ONLY if A1 pivot triggered — not installed by default).
- HF access: `HF_TOKEN` with accepted licenses for meta-llama gated repos; weights already in local HF cache (v1-verified).
- v1 archive artifacts (primary path): `_archive/20260805T054934_routing_recovery/h-e1/code/` — `constants.py`, `model.py`, `data.py`, `analysis.py`, `run_h_e1.py`, `visualize.py` (658 lines, Serena-verified) copied into new `h-e1/code/`; `results/cache_llama2_triviaqa.csv` (1000 rows) reused after hash verification.
- Fallback path: rebuild from plain HF `transformers` per Devoto/mbrenndoerfer lens pattern; TransformerLens explicitly REJECTED (LayerNorm-folding risk to lens numerics).
- Downstream consumers: h-m1 reuses locked test split + per-layer scalar caches; h-m3/h-c1 reuse the same cache schema — cache format is a stability contract (5 + 96 columns, one row per example).
