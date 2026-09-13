# Architecture: h-e1-v2 — A2-v2 Protocol-Internal Anchor (delta refinement of h-e1)

**Hypothesis Type**: EXISTENCE (training-free, inference-only PoC) | **Tier**: LIGHT
**Date**: 2026-08-05

**Applied**: none — Archon KB out-of-domain (null result). Queries: `"DL experiment architecture"`, `"code reuse delta refactoring experiment"` (match_count=3 each) — top hits are diffusion/vision docs (CompVis/latent-diffusion, LCM, compel, diffusers tests; source `8b1c7f40739544a6`, similarity ≤0.48). Zero LLM-interpretability content. Identical null finding to h-e1's own Phase 3 and Phase 2C runs — governing knowledge source is `h-e1/code/` itself (35/35 tests, validator PASS, REAL_MODEL check).

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1, protocol-identical prior episode — MUST_WORK PARTIAL, SELF_MODIFY delta target)
**Status**: Complete, validated 7-module implementation found; near-verbatim reuse confirmed, with 3 code-verified gaps beyond the PRD's stated "1-function re-spec"
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Tools used**: `get_symbols_overview` (run_h_e1.py, analysis.py, constants.py, visualize.py, generate_figures.py); `find_symbol`+body (`check_anchor_and_halt`, `verify_cache_reuse`, `run_model`, `run_sweep`, `evaluate_gate`, `check_baseline_anchor`, `verify_mechanism_activated`, `analyze_all`, `DONOR_CACHE_LLAMA2_TRIVIAQA`); full `Read` (constants.py, data.py, generate_figures.py, requirements.txt, run_experiment.sh).

**Findings — confirms PRD's 1-function delta, PLUS 3 code-level gaps the PRD doesn't name:**

1. `check_anchor_and_halt` (run_h_e1.py:260-294) — confirmed THE delta. Current body: `ref = H_E1_REFERENCES[(model_key, dataset_name)]`, `SystemExit` via `check_baseline_anchor` on breach; `ValueError` guards on empty selection split / single-class labels are already isolated in their own branches — clean to keep, clean to strip the `H_E1_REFERENCES`/`SystemExit` branch.
2. `verify_cache_reuse` (run_h_e1.py:77-106) and `evaluate_gate` (analysis.py:76-97) — confirmed zero-change, A2-v2(a)/(b) already implemented exactly as PRD describes.
3. **Gap A (residual cross-protocol gate, NOT flagged in PRD):** `analysis.py::verify_mechanism_activated(signals, auroc_grid, log_text)` (analysis.py:62-73, called once per cell inside `analyze_all`) has a `"baseline_reproduced": check_baseline_anchor(...)` detail key — this is a **second, separate** call site for `H_E1_REFERENCES`/`BASELINE_TOLERANCE` beyond `check_anchor_and_halt`. `constants.py:24-28` confirms `H_E1_REFERENCES` has entries for **all 6 cells** (not just the binding one), so this call would not crash for the other 5 — it would silently pass a cross-protocol numeric check into every cell's persisted `experiment_results.json["cells"][c]["mechanism"]` block. Doesn't gate the MUST_WORK verdict (that reads only `evaluate_gate`'s `gate_pass`) but violates NFR-7 / Success Criterion 6 ("no H_E1_REFERENCES numeric gate anywhere in the run path") on a literal reading. **Must be patched alongside `check_anchor_and_halt`.**
4. **Gap B (PRD names a function that doesn't exist yet):** FR-4.7's `verify_mechanism_activated(experiment_log, results)` — whole-run, 5 indicators (`reuse_verified`, `anchor_reported`, `grid_nondegenerate`, `screen_healthy`, `all_cells_measured`) — has a **different signature** than the existing per-cell `verify_mechanism_activated(signals, auroc_grid, log_text)` already called inside `analyze_all`. Same name, different function. Resolved by adding it under a distinct name (`verify_v2_run_complete`) rather than colliding with/overwriting the per-cell one that `analyze_all` already depends on.
5. **Gap C (hardcoded path breaks under copy, NOT flagged in PRD):** `DONOR_CACHE_LLAMA2_TRIVIAQA` (run_h_e1.py:35-38) is built as `Path(RESULTS_DIR).resolve().parents[1] / "_archive" / "20260805T054934_routing_recovery" / "h-e1" / "results" / "cache_llama2_triviaqa.csv"` — this is h-e1's OWN donor path (h-e1 reused from an even earlier archived episode). Copied verbatim into `h-e1-v2/code/`, `RESULTS_DIR` auto-resolves to `h-e1-v2/results`, so `.parents[1]` is still `docs/youra_research/`, and the hardcoded `_archive/.../h-e1/` suffix would silently point to the **stale pre-h-e1 archive cache**, not h-e1's Phase-4-finalized `h-e1/results/cache_llama2_triviaqa.csv` the brief requires. **One-line path patch required** (drop the `_archive/20260805T054934_routing_recovery` segment, point straight at sibling `h-e1/results/`).
6. `run_sweep` (run_h_e1.py:143-239) always calls `stratified_split(labels, SEED)` + `write_test_split_locked(...)` itself — it never reads any existing locked-split JSON as input (`write_test_split_locked` is write-only, confirmed by its own docstring: "NEVER read by analysis.py"). Given identical donor labels + identical seed 42, this **deterministically reproduces** the h-e1 locked split without needing to read `h-e1/results/test_split_locked_llama2_triviaqa.json` as an input — "reused, never recomputed" in the PRD is satisfied by determinism, not by a file-read. No code change needed here; documented so Phase 4 doesn't try to add a read path that doesn't exist in v1.
7. `analyze_all` (run_h_e1.py:315-397) already iterates `model_keys × LOADERS` generically (no cell hardcoding) and calls all 4 `visualize.py` figure functions once per full run — this is **already 6-cell-ready, 0 edits**. The single-cell hardcoding lives entirely in the separate ad-hoc `generate_figures.py` script (`CELL = ("llama2", "triviaqa")`, `REF`/`OBS_SEL`/`OBS_FULL` constants, breach-band chart) — that script, not `analyze_all`, is what needs the 6-cell + A2-v2-report patch for FR-5.4.

**Used for**: module structure, file organization, and the Proposed Tasks below.

---

## Module Structure

### constants.py (`code/constants.py`) — verbatim + 1 new constant

**Dependencies**: none

```python
# UNCHANGED: SEED, MODEL_IDS, N_LAYERS, EXPECTED_HIDDEN_STATES, MAX_NEW_TOKENS,
#            DEGENERACY_ENTROPY_PCT, DEGENERACY_AGREEMENT_MIN, AUROC_GATE,
#            H_E1_REFERENCES, BASELINE_TOLERANCE (kept, now unused in run path —
#            harmless dead constants; test_analysis.py still exercises them),
#            RESULTS_DIR, FIGURES_DIR (auto-resolve to h-e1-v2/{results,figures}
#            via Path(__file__).resolve().parents[1] — zero edits needed),
#            SMOKE_N, TRIVIAQA_N, TRUTHFULQA_N, HF_TOKEN

# NEW (clause-c input, A2-v2(c)):
V1_DIRECTION_RECORD: dict[tuple[str, str], bool]
# (model_key, dataset) -> v1 Phase-4-record final-layer "flipped" direction bool
# (same convention as analysis.corrected_auroc's 2nd return value), so
# check_anchor_and_halt can compare booleans, not strings, in the ungated log.
```

### model.py, data.py (`code/model.py`, `code/data.py`) — copied verbatim, 0 edits

Interfaces unchanged from h-e1 (`load_model`, `validate_layout`, `per_layer_lens_signals`, `load_triviaqa`, `load_truthfulqa`, `format_prompt`, `label_response`, `stratified_split`, `write_test_split_locked`).

### analysis.py (`code/analysis.py`) — copied + 2 small patches

**Dependencies**: constants

```python
# UNCHANGED: degeneracy_screen, corrected_auroc, build_auroc_grid,
#            check_baseline_anchor (kept, now unused in run path), evaluate_gate,
#            write_cell_report, _nan_to_none

# PATCHED (closes Gap A — removes 2nd residual H_E1_REFERENCES call site):
def verify_mechanism_activated(signals: dict, auroc_grid, log_text: str) -> tuple[bool, dict]: ...
    """Per-cell, called from analyze_all. detail["baseline_reproduced"]
    (= check_baseline_anchor(...)) REPLACED with detail["anchor_computed"]
    (= not isnan(signals["final_layer_entropy_auroc"])) — protocol-internal,
    same signature, same call site in analyze_all, 0 edits there."""

# NEW (closes Gap B — FR-4.7 whole-run check, distinct name to avoid
# colliding with the per-cell function above):
def verify_v2_run_complete(experiment_log: str, results: dict) -> tuple[bool, dict]: ...
    """5 indicators per PRD FR-4.7: reuse_verified, anchor_reported,
    grid_nondegenerate, screen_healthy, all_cells_measured (==6). Called once
    at the end of analyze_all / main(), not per-cell."""
```

### visualize.py (`code/visualize.py`) — copied verbatim, 0 edits

`plot_gate_bar_chart`, `plot_auroc_heatmap`, `plot_auroc_vs_depth`, `plot_degeneracy_report`, `plot_entropy_heatmap` — all already cell-agnostic (dict-keyed by `"{model}/{dataset}"`); `analyze_all` already calls all 4 core ones generically across whatever cells exist in `RESULTS_DIR`, so 6-cell figures fall out for free.

### run_h_e1.py (`code/run_h_e1.py`) — copied + delta patches

**Dependencies**: constants, data, model, analysis, visualize

```python
# UNCHANGED: _cache_header_ok, resume_from_cache, generate_and_extract,
#            write_cache_row, run_sweep, smoke_test, verify_cache_reuse,
#            build_parser, analyze_all (imports patched analysis.py symbols;
#            body unchanged — already 6-cell generic, see Gap finding #7)

# PATCHED (Gap C — 1-line path fix, verbatim copy would resolve to the
# wrong/stale pre-h-e1 archive cache):
DONOR_CACHE_LLAMA2_TRIVIAQA = str(
    Path(RESULTS_DIR).resolve().parents[1] / "h-e1" / "results"
    / "cache_llama2_triviaqa.csv")   # was: .../_archive/20260805T054934_routing_recovery/h-e1/results/...

# RE-SPECIFIED (THE delta, FR-4.1/4.2, A2-v2):
def check_anchor_and_halt(model_key: str, dataset_name: str, cache_df) -> float: ...
    """REMOVED: H_E1_REFERENCES lookup, BASELINE_TOLERANCE +/-0.03 compare,
    SystemExit numeric-breach branch.
    KEPT verbatim: ValueError on empty selection split; ValueError on
    single-class labels (undefined AUROC).
    ADDED: compute final_auroc, direction = corrected_auroc(labels, scores);
    return final_auroc (consumed by callers wanting the A2-v2(b) baseline
    without recomputing it); log clause-(c) ~15-line descriptive report:
      'A2-v2 anchor: {model}/{dataset} within-sweep final L32 entropy '
      'AUROC={final_auroc:.4f} direction={direction} '
      'v1_record_direction={v1} consistent={direction == v1}'
    where v1 = V1_DIRECTION_RECORD.get((model_key, dataset_name)) — log-only,
    never raises on any numeric value or direction mismatch."""

# MODIFIED (captures new return value for the log; no control-flow change):
def run_model(model_key: str) -> None: ...
    """smoke -> load -> per-dataset: run_sweep(...) -> final_auroc =
    check_anchor_and_halt(...) (was: bare call, no return used)."""
def main() -> None: ...   # unchanged: model order = MODEL_IDS dict order (llama2 first)
```

### generate_figures.py (`code/generate_figures.py`) — patched (loop + new figure)

**Dependencies**: analysis, constants, visualize

```python
# WAS (v1): hardcoded CELL = ("llama2","triviaqa"); REF/BASELINE_TOLERANCE
# breach-band bar chart ("A2 anchor check FAILED").
# NOW (v2): loop CELLS = [(m, d) for m in MODEL_IDS for d in LOADERS] (6 cells,
# skip any cache CSV not yet present); per cell: auroc_vs_depth (unchanged
# renderer logic) + degeneracy_screen scatter (unchanged); REPLACES the
# breach-band chart with:
def plot_anchor_v2_report(cells: dict) -> Path: ...
    """FR-5.4: per-cell within-sweep final-layer AUROC bar + direction-
    consistency marker (check-mark/x) vs V1_DIRECTION_RECORD — descriptive
    only, no gate line, no reference band, no BASELINE_TOLERANCE import."""
```

### tests/test_anchor_gate.py — rewritten (FR-6.1); other 5 test files verbatim, 0 edits

```python
# REMOVE: test_anchor_breach_systemexit_with_delta (asserted SystemExit on
#         H_E1_REFERENCES numeric breach — the exact behavior being retired)
# KEEP/ADAPT: test_anchor_pending_split_valueerror, test_anchor_single_class_valueerror
#             (ValueError guards retained verbatim)
# NEW:
def test_anchor_no_systemexit_on_any_auroc_value(): ...   # sweep several final_auroc values incl. >0.55 delta from any v1 ref -> no raise
def test_anchor_returns_final_auroc(): ...                  # return value == corrected_auroc(labels, scores)[0]
def test_anchor_clause_c_log_emitted(caplog): ...            # "A2-v2 anchor:" + "consistent=" in log output
def test_verify_mechanism_activated_no_h_e1_references(): ...  # analysis.verify_mechanism_activated detail has no "baseline_reproduced" key tied to H_E1_REFERENCES
```

---

## File Organization

```
h-e1-v2/
  code/
    constants.py            # verbatim + V1_DIRECTION_RECORD (Task D-1)
    model.py                # verbatim (Task D-1)
    data.py                 # verbatim (Task D-1)
    analysis.py             # verbatim + verify_mechanism_activated patch + verify_v2_run_complete (Task D-2)
    visualize.py             # verbatim (Task D-1)
    run_h_e1.py              # verbatim + DONOR_CACHE path fix + check_anchor_and_halt re-spec + run_model wiring (Task D-1, D-2)
    generate_figures.py      # patched: 6-cell loop + plot_anchor_v2_report (Task D-7)
    requirements.txt         # verbatim
    run_experiment.sh        # verbatim (cosmetic log-label rename optional, non-functional)
    tests/
      test_anchor_gate.py    # rewritten per FR-6.1 (Task D-3)
      test_data.py            # verbatim
      test_model_layout.py    # verbatim
      test_analysis.py        # verbatim (structurally unaffected — asserts all(detail.values()) is True, not key names)
      test_resume_reuse.py    # verbatim
      test_figures.py         # verbatim
  results/
    cache_{model}_{dataset}.csv                # 6 files, 5+96 cols (frozen schema, NFR-7)
    meta_{model}_{dataset}.json                # 6 files
    top1_agreement_{model}_{dataset}.npy       # 6 files
    test_split_locked_{model}_{dataset}.json   # 6 files (llama2/triviaqa deterministically reproduces h-e1's, see Gap #6)
    {model}_{dataset}_report.json              # 6 files, FR-5.1
  figures/
    gate_metrics_bar.png            # FR-5.2 (mandatory)
    auroc_heatmap.png               # FR-5.3
    auroc_vs_depth_{model}_{dataset}.png   # FR-5.3, x6
    degeneracy_screen.png           # FR-5.5
    entropy_heatmap_llama2.png      # FR-5.6
    anchor_v2_report.png            # FR-5.4 (new, replaces v1 breach-band chart)
  experiment_results.json     # overall MUST_WORK verdict, all 6 cells (analyze_all output)
```

---

## External Dependencies (Base Hypothesis h-e1)

### Module Paths (From Actual Code)

| Module | Import Path (unchanged after copy) | File Location |
|--------|-------------------------------------|----------------|
| All 7 modules | `import constants / model / data / analysis / visualize / run_h_e1` (flat package, sys.path insert in tests) | `h-e1-v2/code/*.py` (copied from `h-e1/code/*.py`) |

### Reused Artifacts (Not Imported — Filesystem Inputs)

| Artifact | Source Path (verified) | Consumed By |
|----------|------------------------|-------------|
| Donor cache (binding cell) | `docs/youra_research/h-e1/results/cache_llama2_triviaqa.csv` (1000 rows, splits finalized) | `run_sweep` via patched `DONOR_CACHE_LLAMA2_TRIVIAQA` (Gap C fix) |
| Locked test split | `docs/youra_research/h-e1/results/test_split_locked_llama2_triviaqa.json` | Reference only — never read by code (Gap #6); v2's own copy is deterministically re-derived, identical by construction (same donor labels + seed 42) |
| Conda env | `youra-h-e1` (python 3.10.20, torch 2.8.0+cu128, transformers 4.57.6) | unchanged, reused as-is |

**Verified from**: `h-e1/code/run_h_e1.py`, `h-e1/code/data.py`, `h-e1/code/constants.py` (actual implementation, not `h-e1/03_architecture.md` specs).

---

## Proposed Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| D-1 | Bootstrap + path fix | Copy all 7 modules + `tests/` (6 files) + `requirements.txt` + `run_experiment.sh` verbatim `h-e1/code/` -> `h-e1-v2/code/`; verify `RESULTS_DIR`/`FIGURES_DIR` auto-resolve to `h-e1-v2/{results,figures}`; patch `DONOR_CACHE_LLAMA2_TRIVIAQA` (Gap C, run_h_e1.py:35-38) to point at sibling `h-e1/results/`, not the archive; confirm `HF_TOKEN`/conda env | 6 | 2+1+1+2 |
| D-2 | A2-v2 anchor re-spec (THE delta) | Re-spec `check_anchor_and_halt` per FR-4.1/4.2: strip `H_E1_REFERENCES`/`BASELINE_TOLERANCE`/`SystemExit` branch, keep `ValueError` guards, return `final_auroc`, add clause-(c) log; add `V1_DIRECTION_RECORD` to constants.py; patch `analysis.py::verify_mechanism_activated`'s `baseline_reproduced` key (Gap A) to protocol-internal; add `verify_v2_run_complete` (Gap B, FR-4.7); wire `run_model` to capture the new return value | 12 | 2+3+3+4 |
| D-3 | Test suite update | Rewrite `tests/test_anchor_gate.py` per FR-6.1 (drop SystemExit-breach test, keep ValueError-guard tests, add no-SystemExit/return-value/clause-c-log/no-H_E1_REFERENCES-key tests); run full 6-file suite, confirm other 5 files pass unmodified | 8 | 2+2+2+2 |
| D-4 | Smoke test all 3 models | Run unmodified `smoke_test` for llama2/mistral/llama3, SMOKE_N=10; assert 33 hidden states, finite signals, peak memory | 4 | 1+1+1+1 |
| D-5 | Full 6-cell sweep | `run_model` per `MODEL_IDS` key; llama2/triviaqa zero-GPU via `verify_cache_reuse` 10/10 + donor copy (deterministic split re-derivation per Gap #6); remaining 5 cells fresh (~4,451 examples, ~2.5h H100); `check_anchor_and_halt` v2 semantics runs per cell, never halts on numeric value | 10 | 2+3+2+3 |
| D-6 | Analysis + gate verdict | Run unmodified `analyze_all` (degeneracy_screen -> build_auroc_grid -> evaluate_gate -> write_cell_report -> per-cell `verify_mechanism_activated`) across all 6 cells; call new `verify_v2_run_complete`; write `experiment_results.json` with overall MUST_WORK verdict (6/6 cells, FR-4.6) | 9 | 2+2+3+2 |
| D-7 | Figures | `analyze_all`'s 4 core figures fall out unchanged (0 edits, cell-agnostic); patch `generate_figures.py`: loop all 6 cells instead of hardcoded llama2/triviaqa, add `plot_anchor_v2_report` (FR-5.4, replaces breach-band chart); wire into `run_experiment.sh` | 8 | 2+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [D-2, D-5, D-6], Low(4-8): [D-1, D-3, D-4, D-7]

**Dependency order**: D-1 -> D-2 -> D-3 -> D-4 -> D-5 -> D-6 -> D-7 (linear; D-3 test rewrite gates D-4 smoke per LIGHT-tier "test before run" discipline; D-6/D-7 both read from D-5's finalized caches, run sequentially).
