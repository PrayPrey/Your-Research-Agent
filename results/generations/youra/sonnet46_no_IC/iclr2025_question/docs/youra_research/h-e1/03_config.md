# Config: h-e1 — Layer-Wise Logit-Lens Existence Sweep

**Hypothesis Type**: EXISTENCE (PoC) | **Tier**: LIGHT — hardcoded constants + argparse, print + CSV logging, no YAML framework
**Date**: 2026-08-05
**Scope**: A-5 (Full sweep, remaining 5 cells) and A-6 (Selection-split analysis) only — 4 subtasks total, per allocation.

**Applied**: none — KB out-of-domain (null result). Re-ran `rag_search_knowledge_base("DL config patterns")`: top 3 hits are `latent-diffusion` README, `torch/_inductor/config.py`, and JAX/libtpu release notes (source `8b1c7f40739544a6`, similarity ≤ 0.35) — zero relevance to experiment-config/argparse/dataclass patterns for interpretability sweeps. Confirms Phase 3 architecture doc's null Archon finding; no fabricated pattern cited. Config below follows the v1 archive's own hardcoded-module-constants style (NFR-4 LIGHT tier).

---

## Codebase Analysis (Serena)

**Project Type**: existing_codebase (v1 archive, mandated reuse donor — see `03_architecture.md` Codebase Analysis for full provenance)
**Status**: `constants.py` and `run_h_e1.py` re-verified directly (Read, not Serena grep, since both files are short and already fully quoted in `03_architecture.md`) against archive path below. All 15 named constants confirmed present with exact names/values. `run_h_e1.py::build_parser` confirmed: 4 flags only (`--model {llama2,mistral,llama3,all}` required, `--smoke`, `--full`, `--analyze`), no YAML/config-file flag exists — LIGHT tier confirmed at the CLI surface, not just in constants.
**Analyzed Path**: `docs/youra_research/_archive/20260805T054934_routing_recovery/h-e1/code/{constants.py,run_h_e1.py,model.py,analysis.py,visualize.py}`
**Config Files Found**: `constants.py` (module-level hardcoded constants, no dataclass, no dict-of-config wrapper)
**Pattern Used**: Hardcoded module constants (plain `NAME = value` at module scope) — this doc follows the SAME format for consistency (Format Selection rule: hardcoded constants only, no dataclass introduced).

### Verified Constants Table

| Name | Value (verified) | Source line | PRD cross-ref | Drift? |
|---|---|---|---|---|
| `SEED` | `42` | constants.py:5 | NFR-2 | none |
| `MODEL_IDS` | `{"llama2":"meta-llama/Llama-2-7b-hf","mistral":"mistralai/Mistral-7B-v0.1","llama3":"meta-llama/Meta-Llama-3-8B-Instruct"}` | constants.py:7-11 | FR-2.1-2.3 | none |
| `N_LAYERS` | `32` | constants.py:12 | Exec Summary | none |
| `EXPECTED_HIDDEN_STATES` | `33` | constants.py:13 | FR-2.4 | none |
| `MAX_NEW_TOKENS` | `32` | constants.py:17 | FR-3.1 | none |
| `DEGENERACY_ENTROPY_PCT` | `0.01` | constants.py:19 | FR-4.2 | none |
| `DEGENERACY_AGREEMENT_MIN` | `0.05` | constants.py:20 | FR-4.2 | none |
| `AUROC_GATE` | `0.55` | constants.py:21 | FR-4.4 | none |
| `BASELINE_TOLERANCE` | `0.03` | constants.py:22 | FR-4.1 | none |
| `H_E1_REFERENCES` | 6 entries, llama2 0.5186/0.5153, mistral 0.5268/0.5886, llama3 0.6583/0.6161 | constants.py:24-28 | FR-4.1, Problem Statement | none |
| `RESULTS_DIR` / `FIGURES_DIR` | auto-resolved from `parents[1]` → `h-e1/results`, `h-e1/figures` | constants.py:30-32 | File Organization | none |
| `SMOKE_N` | `10` | constants.py:33 | FR-3.6 | none |
| `TRIVIAQA_N` | `1000` | constants.py:35 | FR-1.1 | none |
| `TRUTHFULQA_N` | `817` | constants.py:36 | FR-1.2 | none |
| `HF_TOKEN` | `os.environ.get("HF_TOKEN")`, raises `RuntimeError` at **import time** if unset | constants.py:38-43 | FR-2.4 | none — but see operational note below |

**PRD-vs-code drift found (2 items, both outside my A-5/A-6 scope but relevant to A-6.1/A-6.2 analysis correctness):**
1. `analysis.py:69` `verify_mechanism_activated` uses `nanstd(auroc_grid[:,0]) > 0.01` for the "depth_variation" check, but **PRD FR-4.5 states the threshold as `0.005`**. Code wins per project rule — A-6.2 uses `0.01` (no code change in my scope; flagging for the record since it affects mechanism-verification pass/fail).
2. `format_prompt` is zero-shot (`"Q: {q}\nA:"`), PRD FR-1.3 prose says "few-shot" — already logged in `03_architecture.md`; not an A-5/A-6 concern (data.py is out of my scope, unchanged).

**Operational note**: `HF_TOKEN` is required at **module import** of `constants.py` regardless of which CLI flag is used — `--analyze`-only invocations (A-6) still need `HF_TOKEN` set in the environment even though A-6 never loads a model, because `run_h_e1.py` imports `constants` (and transitively `model.py`) unconditionally at the top of the file.

---

## Constants Inventory — New Additions for A-2/A-3 Patches

Only **one** new constant is needed; everything else stays a function default (avoids a duplicate source of truth).

```python
# ADD to h-e1/code/constants.py (Task A-2 dependency; consumed by A-5.2)
DONOR_CACHE_LLAMA2_TRIVIAQA = str(
    _H_E1_ROOT.parent / "_archive" / "20260805T054934_routing_recovery"
    / "h-e1" / "results" / "cache_llama2_triviaqa.csv"
)
```
Reuses the existing `_H_E1_ROOT` variable already defined at constants.py:30 — no new path-resolution logic. Verified target exists: `docs/youra_research/_archive/20260805T054934_routing_recovery/h-e1/results/cache_llama2_triviaqa.csv`.

**Deliberately NOT added:**
- `n_check` global constant for `verify_cache_reuse` — architecture's own signature already defaults it (`n_check: int = 10`, mirrors `SMOKE_N`); promoting it to a module constant duplicates that default for no consumer. Skip; add only if a second caller needs a different value.
- `--force-restart` / `--resume` CLI flag — resume is a file-existence check (`resume_from_cache(path)` returns `set()` if no file), fully automatic. No flag needed for the A-5 run path. Skip; add if a manual "wipe and redo a cell" workflow is requested later.

---

## A-5.1: Full sweep — mistral x2 + llama3 x2 [Complexity: 5, Budget: 10 (shared w/ A-5.2)]

**Applied**: Standard PyTorch/HF defaults (fp16 + `device_map="auto"`, greedy decode) — same as v1, unchanged.

### Run Configuration

**CLI** (2 sequential invocations, one process per model — avoids holding two 7-8B models in VRAM):
```bash
export HF_TOKEN=<token>          # required at import, gated meta-llama repos (mistral is public but token param is harmless)
python run_h_e1.py --model mistral --full
python run_h_e1.py --model llama3 --full
```
`--full` → `run_model(mk)` = `smoke_test(mk)` (re-runs SMOKE_N=10, cheap) then `run_sweep` over `LOADERS` dict order (`triviaqa` then `truthfulqa`) — 4 cells total: `mistral/triviaqa`, `mistral/truthfulqa`, `llama3/triviaqa`, `llama3/truthfulqa`.

**Model load settings** (verified `model.py:13-18`, unchanged): `AutoModelForCausalLM.from_pretrained(MODEL_IDS[key], torch_dtype=torch.float16, device_map="auto", token=HF_TOKEN).eval()`; `validate_layout` asserts `model.model.norm` + `model.lm_head` present (raises `LayoutError` otherwise, FR-2.4).

**Cache file naming**: `{RESULTS_DIR}/cache_{model_key}_{dataset_name}.csv` → `cache_mistral_triviaqa.csv`, `cache_mistral_truthfulqa.csv`, `cache_llama3_triviaqa.csv`, `cache_llama3_truthfulqa.csv`. 5+96 columns (`example_id,dataset,model,split,label` + `entropy_L1..32,maxprob_L1..32,adj_kl_L1..32`).

**Resume**: automatic — `run_sweep` (A-2 patch) checks if the cache file already exists; if so, opens in `"a"` mode and skips `example_id in resume_from_cache(path)`, else `"w"` mode from idx 0. No flag; safe to re-invoke the same command after an interruption.

**Expected artifacts per cell**: `cache_{m}_{d}.csv`, `meta_{m}_{d}.json` (incl. `elapsed_s`, `n_written`, `n_skipped`, `n_selection`, `n_test`), `top1_agreement_{m}_{d}.npy`, `test_split_locked_{m}_{d}.json`.

**GPU/memory envelope** (NFR-1): single GPU, fp16 7-8B ≈ 14-16 GB, batch size 1 (single-example streaming). No fixed runtime target in PRD; `meta_*.json.elapsed_s` is the only timing record — expect a multi-hour run per model (1817 examples × greedy-32-token generate + teacher-forced re-forward, no batching).

**Cell order**: mistral fully (both datasets) before llama3, each model: triviaqa (1000) before truthfulqa (817) — matches `LOADERS` dict order, unchanged from v1.

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-5.1-1 | Run mistral sweep | `python run_h_e1.py --model mistral --full`; verify both cache CSVs + meta/report-precursor artifacts written, no `LayoutError`/`CUDA OOM` |
| C-5.1-2 | Run llama3 sweep | `python run_h_e1.py --model llama3 --full`; same verification; confirm `HF_TOKEN` gated-repo pull succeeds (meta-llama/Meta-Llama-3-8B-Instruct) |

---

## A-5.2: llama2 cells — donor-cache reuse (triviaqa) + fresh sweep (truthfulqa) [Complexity: 5, Budget: 10 (shared w/ A-5.1)]

**Applied**: Standard PyTorch/HF defaults; cache-reuse short-circuit is the one A-2-specific addition (documented in architecture, not a KB pattern).

### Run Configuration

**CLI** (single invocation covers both cells — the reuse routing is internal to `run_model`, not a CLI flag):
```bash
export HF_TOKEN=<token>          # required — gated meta-llama/Llama-2-7b-hf
python run_h_e1.py --model llama2 --full
```

**Recommended execution order relative to A-5.1**: run **A-5.2 before A-5.1** in practice, even though the subtask numbering is 5.1→5.2. Rationale (from `03_architecture.md` A-3 sequencing note): `llama2/triviaqa`'s anchor check is near-zero-GPU-cost via the reused cache, so running it first gives the fastest possible fail-fast signal on the A2 protocol-validity gate before the two other models' GPU time is spent. This is a sequencing recommendation only — both invocations are independent CLI commands and can run in either order without breaking correctness.

**Donor-cache reuse invocation detail** (internal to `run_model("llama2")` → `run_sweep(..., dataset_name="triviaqa", reuse_cache_path=DONOR_CACHE_LLAMA2_TRIVIAQA)`, hardcoded in `run_model`'s per-cell dispatch, not exposed as a flag):
1. Load llama2 model/tokenizer (needed anyway for the truthfulqa fresh sweep) — fp16, `device_map="auto"`.
2. `smoke_test("llama2")` — SMOKE_N=10, GPU.
3. `verify_cache_reuse(model, tokenizer, DONOR_CACHE_LLAMA2_TRIVIAQA, load_triviaqa(), "triviaqa", n_check=10)` — regenerates the first 10 examples fresh, compares `label_response()` output to the donor row's `label` for the same `example_id`. All-match → proceed; any mismatch → abort (FR-3.5 protocol-identity check). **This step still costs GPU** (10 generate+reforward passes) — "zero GPU cost" in the architecture doc refers only to the anchor-check math, not this verification step.
4. Copy donor CSV rows into `{RESULTS_DIR}/cache_llama2_triviaqa.csv`, then run the unchanged post-loop `stratified_split` + split-column write-back (donor rows are `split="pending"` — MUST be finalized here, per architecture Finding #4; do not assume splits are already assigned).
5. `check_anchor_and_halt("llama2", "triviaqa", finalized_df)` — zero additional GPU, reads the just-finalized cache.
6. Fresh `run_sweep(..., dataset_name="truthfulqa")` — full 817-example generation + re-forward, then `check_anchor_and_halt("llama2", "truthfulqa", ...)`.

**GPU savings**: this invocation costs GPU for smoke(10) + verify(10) + truthfulqa-fresh(817) = 837 examples, NOT the triviaqa 1000 — matches NFR-5's "≈4,451 fresh generation+re-forward pairs" total-campaign figure.

**Cache file naming**: `cache_llama2_triviaqa.csv` (donor copy, finalized), `cache_llama2_truthfulqa.csv` (fresh). Same 5+96 column schema as A-5.1.

**HF_TOKEN / gated-repo note**: `meta-llama/Llama-2-7b-hf` requires an HF account with the Llama 2 license accepted; `HF_TOKEN` must have read access to that gated repo (v1-verified already in local HF cache per PRD Dependencies, but token must still be valid for a cache-miss fallback).

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-5.2-1 | Donor reuse + finalize (triviaqa) | Load llama2, run `verify_cache_reuse` (n_check=10), copy+finalize donor cache, run `check_anchor_and_halt` — confirm 0.5186 ± 0.03 |
| C-5.2-2 | Fresh sweep (truthfulqa) | `run_sweep` 817 examples, `check_anchor_and_halt` — confirm 0.5153 ± 0.03; verify no orphaned "pending" split rows remain |

---

## A-6.1: Degeneracy screen + AUROC grid [Complexity: 5, Budget: 9 (shared w/ A-6.2)]

**Applied**: `sklearn.metrics.roc_auc_score` standard usage — Archon KB has no interpretability-specific pattern (see top-level Applied line).

### Run Configuration

**CLI** (analysis-only, no GPU, all 6 cells' caches must exist from A-4/A-5):
```bash
export HF_TOKEN=<token>          # still required — module import guard fires even for --analyze
python run_h_e1.py --model all --analyze
```
`--model` value is ignored by the `--analyze` branch of `main()` (`analyze_all(list(MODEL_IDS))` always uses all 3 keys) — `--model all` used for clarity/least-confusing invocation, not because it's functionally load-bearing.

**Degeneracy screen settings** (`degeneracy_screen`, unchanged, `analysis.py:17-24`):
- `DEGENERACY_ENTROPY_PCT = 0.01` — drop layer if `|mean_entropy[l] - ln(vocab_size)| / ln(vocab_size) < 0.01`.
- `DEGENERACY_AGREEMENT_MIN = 0.05` — drop layer if `top1_agreement[l] < 0.05` (loaded from `top1_agreement_{m}_{d}.npy`, written by A-5's `run_sweep`).
- Runs per cell on `entropy_grid` computed from the `selection`-split rows only (`sel = df[df["split"]=="selection"]` inside `analyze_all`, before `degeneracy_screen` is called — selection-split enforcement happens at the caller, not inside the screen function itself).

**AUROC grid settings** (`build_auroc_grid`, unchanged, `analysis.py:36-55`):
- **Selection-split-only enforcement**: `sel = cache_df[cache_df["split"] == "selection"]` — hard filter inside the function itself (second enforcement point, belt-and-suspenders with the caller's filter). `test` split rows are never touched by A-6 (locked for h-m1, per FR-1.4).
- **NaN handling**: `adj_kl_L1` is always NaN (`model.py` sets `adj_kl[0]=NaN` structurally, not a data-quality issue) — any column with `.isnan().any()` is skipped, grid cell stays `NaN`, logged `"skip AUROC L{l}/{sig}: NaN present"`. A second guard catches `ValueError` from `roc_auc_score` (single-class selection-split labels for a cell) — logged as a warning, grid cell stays `NaN`. Both cases propagate cleanly into `write_cell_report`'s `_nan_to_none` JSON serialization (A-6.2).
- `corrected_auroc` = `max(raw_auc, 1-raw_auc)`; raw direction always logged (`raw_auc={x:.4f} flipped={bool}`, FR-4.3/R8 diagnostic — print/log only, no separate config).

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-6.1-1 | Degeneracy screen, all 6 cells | Verify retained-layer count ≥ 5 per cell (Success Criterion #3, RISK-1 early warning) |
| C-6.1-2 | AUROC grid, all 6 cells | Verify grid shape `(n_retained, 3)`, confirm NaN-only at structural `adj_kl_L1` positions (no unexpected NaN from data issues) |

---

## A-6.2: Gate evaluation + report/figure output [Complexity: 4, Budget: 9 (shared w/ A-6.1)]

**Applied**: none beyond stdlib `json`/`pathlib` — no KB pattern relevant.

### Run Configuration

Same single `--model all --analyze` invocation as A-6.1 — `evaluate_gate` → `write_cell_report` → `verify_mechanism_activated` all execute inline inside the same `analyze_all()` call, plus the 4 `visualize.py` figures and the final `experiment_results.json`. No separate CLI step.

**`evaluate_gate` settings** (`analysis.py:77-98`, unchanged): excludes the final layer (idx 31) from the "best" search (`is_final` mask) — gate is evaluated on **intermediate retained layers only**, per architecture note. `gate_pass = best_auroc >= AUROC_GATE (0.55)`. `depth_beats_final = best_auroc > final_auroc` (Success Criterion #4, PoC direction check).

**Per-cell JSON report schema** (`write_cell_report`, unchanged) → `{RESULTS_DIR}/{model_key}_{dataset_name}_report.json`:
```python
{
  "model": str, "dataset": str,
  "retained_layers": list[int], "dropped_layers": list[int],   # 1-indexed
  "signals": ["entropy", "maxprob", "adj_kl"],
  "auroc_grid": list[list[float | None]],                       # NaN -> null
  "positive_cases": int, "negative_cases": int,
  "gate": {"best_layer": int|None, "best_signal": str|None, "best_auroc": float|None,
           "gate_pass": bool, "final_layer_entropy_auroc": float|None,
           "depth_beats_final": bool|None},
}
```
6 files: `llama2_triviaqa_report.json`, `llama2_truthfulqa_report.json`, `mistral_triviaqa_report.json`, `mistral_truthfulqa_report.json`, `llama3_triviaqa_report.json`, `llama3_truthfulqa_report.json`.

**`experiment_results.json` verdict shape** (written to `Path(RESULTS_DIR).parent / "experiment_results.json"` = `h-e1/experiment_results.json`):
```python
{
  "hypothesis_id": "h-e1", "gate_type": "MUST_WORK",
  "overall_pass": bool,                    # all 3 models pass gate on BOTH datasets
  "per_model_pass": {"llama2": bool, "mistral": bool, "llama3": bool},
  "cells": {"{model}/{dataset}": {"gate": {...}, "mechanism": {"all_true": bool, "log_found": bool,
            "layer_dim_correct": bool, "depth_variation": bool, "baseline_reproduced": bool},
            "retained_layers": list[int]} for each of 6 cells},
  "figures": [list of 4 figure paths],
}
```
Note `depth_variation` uses the code's `0.01` threshold, not PRD's stated `0.005` (see drift item #1 above).

**Figure filenames** (FR-5, 4 of the 5 total figures — 5th, `entropy_heatmap_llama2.png`, is A-7 scope, not mine): all written to `{FIGURES_DIR}` (`h-e1/figures/`) as a side effect of this same `analyze_all()` call:
- `gate_metrics_bar.png` (FR-5.2, mandatory — MUST render)
- `auroc_heatmap.png` (FR-5.3)
- `auroc_vs_depth.png` (FR-5.4)
- `degeneracy_screen.png` (FR-5.5)

**Handoff to A-7**: A-7 re-verifies these 4 figures render (they're a byproduct of A-6, not a separate generation step) and additionally runs the new `plot_entropy_heatmap` for the 5th figure — no config action needed from A-6.2 beyond confirming the 4 files exist and are non-empty PNGs.

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-6.2-1 | Gate + reports, all 6 cells | Verify all 6 `*_report.json` written, `gate_pass` computed correctly (intermediate layers only, excludes final) |
| C-6.2-2 | Verdict + figures | Verify `experiment_results.json` written with correct `overall_pass`/`per_model_pass`, and the 4 A-6-produced figures exist in `h-e1/figures/` |
