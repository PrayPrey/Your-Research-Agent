# Logic: h-e1-v2 — A2-v2 Protocol-Internal Anchor (delta refinement of h-e1)

**Scope**: D-2 "A2-v2 anchor re-spec" (complexity 12) and D-5 "Full 6-cell sweep" (complexity 10) only — the two medium-complexity epics allocated to this agent. D-1, D-3, D-4, D-6, D-7 out of scope here (see `03_architecture.md`).

**Applied**: none — Archon KB out-of-domain (null result documented). Queries: `"DL API design patterns"` (top hits: HF `diffusers` llms.txt / PHILOSOPHY.md, source `8b1c7f40739544a6`, similarity ≤0.37), `"resume checkpoint CSV sweep orchestration"` (top hits: `diffusers` dreambooth/t2i_adapter training scripts, similarity ≤0.45). Zero LLM-interpretability or sweep-orchestration content. Identical null finding to h-e1's own `03_logic.md` and this hypothesis's `02c_experiment_brief.md`/`03_architecture.md` — governing knowledge source is `h-e1/code/` itself.

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1, prior episode, MUST_WORK PARTIAL 4/6 — SELF_MODIFY delta target)
**Status**: API signatures verified from actual code (not from architecture.md/PRD pseudo-code, which use non-fatal shorthand)
**Analyzed Path**: `docs/youra_research/h-e1/code/run_h_e1.py`, `docs/youra_research/h-e1/code/analysis.py`, `docs/youra_research/h-e1/code/constants.py`
**Tools used**: `get_symbols_overview` (run_h_e1.py: 12 functions + 3 constants; analysis.py: 8 functions + 1 constant; constants.py: 17 constants); `find_symbol` + body on `check_anchor_and_halt`, `verify_cache_reuse`, `run_model`, `run_sweep`, `resume_from_cache`, `main`, `analyze_all`, `smoke_test`, `DONOR_CACHE_LLAMA2_TRIVIAQA`, `verify_mechanism_activated`, `check_baseline_anchor`, `corrected_auroc`, `evaluate_gate`, `degeneracy_screen`, `write_cell_report`; `Read` on run_h_e1.py:1-48 (imports/module constants) and constants.py (full).

**Signature drift found vs `02c_experiment_brief.md`'s pseudo-code**: brief shows `check_anchor_and_halt` returning `None` implicitly with a bare `v1 = V1_DIRECTION_RECORD.get(...)  # {"direction": "inverted", ...}` comment (dict value); **actual `03_architecture.md` type annotation `V1_DIRECTION_RECORD: dict[tuple[str,str], bool]` is authoritative and used below** (bool, matching `corrected_auroc`'s 2nd return value convention, not a nested dict).

**Real value found for `V1_DIRECTION_RECORD`**: `h-e1/experiment_results.json` (`anchor_failure_analysis.positive_evidence`): *"Direction of the final-layer signal (inverted/anti-correlated) matches the v1 record"* for llama2/triviaqa — the only cell h-e1 measured before halting. This is the only code-verified entry; the other 5 cells were never swept in-protocol by h-e1 (halted after cell 1), so no verified v1-record direction exists for them.

---

## External Dependencies API (h-e1 verbatim-reused symbols D-2/D-5 call)

```python
# From: h-e1/code/analysis.py (ACTUAL CODE, verbatim in h-e1-v2, 0 edits)
def corrected_auroc(labels: np.ndarray, scores: np.ndarray) -> tuple[float, bool]:
    """(max(auc,1-auc), flipped). flipped = raw_auc < 0.5. Raises ValueError
    (via sklearn roc_auc_score) on single-class labels. Caller pre-filters NaN."""

def evaluate_gate(auroc_grid: np.ndarray, retained_layers: list[int]) -> dict:
    """best_auroc over INTERMEDIATE retained layers (excludes L32 idx 31);
    depth_beats_final = best_auroc > final_layer_entropy_auroc; gate_pass =
    best_auroc >= AUROC_GATE (0.55)."""

def degeneracy_screen(entropy_grid: np.ndarray, top1_agreement: np.ndarray,
                       vocab_size: int) -> list[int]:
    """entropy_grid: (n_selection, 32). top1_agreement: (32,). Returns
    0-indexed retained layers."""

def write_cell_report(model_key: str, dataset_name: str, auroc_grid: np.ndarray,
                       retained_layers: list[int], counts: dict) -> dict:
    """Writes results/{model}_{dataset}_report.json; internally calls
    evaluate_gate. Returns the report dict."""

# From: h-e1/code/run_h_e1.py (ACTUAL CODE, verbatim in h-e1-v2, 0 edits)
def verify_cache_reuse(model, tokenizer, cache_path: str, dataset, dataset_name: str,
                        n_check: int = 10) -> bool:
    """Regenerates first n_check rows fresh, compares label_response to donor
    row. All-consistent -> True; any drift -> False (caller falls through to
    fresh generation, never silently drops the cell)."""

def run_sweep(model, tokenizer, model_key: str, dataset, dataset_name: str,
              max_new_tokens: int = MAX_NEW_TOKENS,
              reuse_cache_path: str | None = None) -> None:
    """Donor branch (reuse_cache_path set + verify_cache_reuse True): copies
    donor CSV, 0 GPU calls except the 10-example verify. Else: resume_from_cache
    + append-mode generation loop. Both branches converge on stratified_split
    finalization + write_test_split_locked. Writes cache_{m}_{d}.csv,
    top1_agreement_{m}_{d}.npy, meta_{m}_{d}.json."""

def resume_from_cache(path: str) -> set[int]:
    """Already-written example_id at path. {} if missing/header-mismatch.
    Truncates a corrupt/partial tail row in place (NFR-6)."""

def smoke_test(model_key: str, n: int = SMOKE_N) -> bool:
    """10 examples, asserts entropy.shape == (32,), prints peak GPU memory."""
```

**Verified from**: `h-e1/code/analysis.py`, `h-e1/code/run_h_e1.py` (actual implementation, not `h-e1/03_logic.md`, which pre-dates the A-2/A-3 → D-2/D-5 rename and used `check_baseline_anchor`/`H_E1_REFERENCES` gates this delta retires).

---

## D-2: A2-v2 anchor re-spec [Complexity: 12, Budget: 12]

**Applied**: none — KB out-of-domain (see header).

**Subtasks [2/2 used]**

| ID | Subtask | Description |
|----|---------|--------------|
| D-2.1 | `check_anchor_and_halt` re-spec + `V1_DIRECTION_RECORD` + clause-c log | Strip `H_E1_REFERENCES`/`SystemExit`; keep `ValueError` guards; return `final_auroc`; add descriptive direction-consistency log |
| D-2.2 | Gap A + Gap B + run_model/main wiring | Patch `analysis.py::verify_mechanism_activated`'s `baseline_reproduced` key; add `verify_v2_run_complete`; capture `check_anchor_and_halt`'s return in `run_model`; wire `verify_v2_run_complete` into `main()` |

---

### D-2.1: `check_anchor_and_halt` re-spec [complexity 6]

**Integration**: called by `run_model` (D-2.2) once per cell, right after `run_sweep` finalizes the cache; also by `main()`'s pre-existing pre-flight branch (kept verbatim — see D-2.2).

#### API Signatures

```python
# run_h_e1.py — RE-SPECIFIED (was: -> None; now returns final_auroc)
def check_anchor_and_halt(model_key: str, dataset_name: str,
                           cache_df: pd.DataFrame) -> float:
    """A2-v2 (FR-4.1/4.2): protocol-internal validity only. ValueError on
    contract violation (empty selection split / single-class labels). NEVER
    raises SystemExit on any AUROC value. Returns final_auroc; logs clause-(c)
    direction-consistency report (ungated)."""
```

```python
# constants.py — NEW (A2-v2 clause-c input)
# bool convention matches corrected_auroc's 2nd return value (flipped =
# raw_auc < 0.5). Only llama2/triviaqa has a code-verified entry
# (h-e1/experiment_results.json: "direction ... matches the v1 record" ->
# inverted/flipped=True). Other 5 cells: h-e1 halted after cell 1, never
# measured in-protocol -- left absent by design; .get() -> None is safe
# (logs consistent=False, never gates -- see pseudo-code below).
V1_DIRECTION_RECORD: dict[tuple[str, str], bool] = {
    ("llama2", "triviaqa"): True,
}
```

```python
# run_h_e1.py imports — BEFORE (v1) / AFTER (v2), exact diff:
# BEFORE:
from constants import (BASELINE_TOLERANCE, H_E1_REFERENCES, MAX_NEW_TOKENS,
                       MODEL_IDS, N_LAYERS, RESULTS_DIR, SEED, SMOKE_N)
from analysis import check_baseline_anchor, corrected_auroc
# AFTER:
from constants import (MAX_NEW_TOKENS, MODEL_IDS, N_LAYERS, RESULTS_DIR, SEED,
                       SMOKE_N, V1_DIRECTION_RECORD)
from analysis import corrected_auroc
```

#### Tensor/array shapes

| Variable | Shape | Note |
|----------|-------|------|
| `labels`, `scores` | `(n_selection,)` | 500 (triviaqa) / 408 (truthfulqa); `scores` = `entropy_L32` column |
| `final_auroc` | scalar `float` | `max(auc, 1-auc)`; consumed by `run_model`'s log line and by `evaluate_gate`'s within-sweep grid (independently recomputed there — no shared state) |
| `direction` | scalar `bool` | `corrected_auroc`'s 2nd return; `True` = flipped (`raw_auc < 0.5`) |

#### Pseudo-code

```python
def check_anchor_and_halt(model_key, dataset_name, cache_df):
    sel = cache_df[cache_df["split"] == "selection"]
    if sel.empty:
        raise ValueError(                                            # KEPT verbatim from v1
            f"check_anchor_and_halt: no 'selection' rows for "
            f"{model_key}/{dataset_name} -- split finalization must run before "
            f"the anchor check")
    labels = sel["label"].to_numpy()
    scores = sel["entropy_L32"].to_numpy()
    if len(np.unique(labels)) < 2:
        raise ValueError(                                            # KEPT verbatim from v1
            f"check_anchor_and_halt: single-class selection split for "
            f"{model_key}/{dataset_name} -- AUROC undefined")
    final_auroc, direction = corrected_auroc(labels, scores)          # direction = flipped bool

    # clause (c): descriptive, ungated -- NO SystemExit, NO H_E1_REFERENCES
    v1 = V1_DIRECTION_RECORD.get((model_key, dataset_name))
    log.info(f"A2-v2 anchor: {model_key}/{dataset_name} within-sweep final L32 "
             f"entropy AUROC={final_auroc:.4f} direction={direction} "
             f"v1_record_direction={v1} consistent={direction == v1}")
    return final_auroc

# REMOVED vs v1: `ref = H_E1_REFERENCES[(model_key, dataset_name)]`, delta calc,
#                `check_baseline_anchor(...)` call, `SystemExit` numeric-breach
#                branch (unsatisfiable by construction, see PRD Problem Statement)
```

#### Acceptance criteria

- No `SystemExit` for any `final_auroc` value (property-checked across several deltas, incl. >0.55 away from any v1 reference).
- Both `ValueError` guards raised with byte-identical messages to v1 (empty selection; single-class labels).
- Return value `== corrected_auroc(labels, scores)[0]`.
- Log line contains substrings `"A2-v2 anchor:"` and `"consistent="`.
- `grep -c "H_E1_REFERENCES\|BASELINE_TOLERANCE\|check_baseline_anchor" run_h_e1.py` → `0` (Success Criterion 6 / NFR-7).

---

### D-2.2: Gap A patch + Gap B (`verify_v2_run_complete`) + run_model/main wiring [complexity 6]

**Integration**: `verify_mechanism_activated` patch has the identical call site inside `analyze_all` (0 edits to `analyze_all` itself). `verify_v2_run_complete` is called once from `main()`, after `analyze_all` returns — **not** inside `analyze_all` (keeps `analyze_all`'s body/return schema literally 0-edit per architecture.md Gap finding #7).

#### API Signatures

```python
# analysis.py — PATCHED (Gap A: closes 2nd residual H_E1_REFERENCES call site)
def verify_mechanism_activated(signals: dict, auroc_grid: np.ndarray,
                                log_text: str) -> tuple[bool, dict]:
    """Per-cell, called once from analyze_all per (model,dataset). SAME
    signature/call site as v1. detail['baseline_reproduced']
    (H_E1_REFERENCES-backed) REPLACED with detail['anchor_computed']
    (protocol-internal: final_layer_entropy_auroc is a real number)."""

# analysis.py — NEW (Gap B: FR-4.7 whole-run check, distinct name/signature
# from the per-cell function above -- no collision)
def verify_v2_run_complete(experiment_log: str, results: dict) -> tuple[bool, dict]:
    """5 indicators per FR-4.7: reuse_verified, anchor_reported,
    grid_nondegenerate, screen_healthy, all_cells_measured (==6). Called once
    from main() after analyze_all() returns, not per-cell."""

# run_h_e1.py — MODIFIED (captures new return value; no control-flow change)
def run_model(model_key: str) -> None:
    """smoke -> load -> per-dataset: run_sweep(...) -> final_auroc =
    check_anchor_and_halt(...) (was: bare call, return discarded)."""
```

#### Pseudo-code — `verify_mechanism_activated` (Gap A patch)

```python
def verify_mechanism_activated(signals, auroc_grid, log_text):
    detail = {
        "log_found": "Lens sweep: model=" in log_text,                    # UNCHANGED
        "layer_dim_correct": signals["entropy"].shape == (N_LAYERS,),     # UNCHANGED
        "depth_variation": bool(np.nanstd(auroc_grid[:, 0]) > 0.01),      # UNCHANGED
        "anchor_computed": not math.isnan(                                # WAS: "baseline_reproduced":
            signals["final_layer_entropy_auroc"]),                        #      check_baseline_anchor(...)
    }
    return all(detail.values()), detail
# check_baseline_anchor/H_E1_REFERENCES import in analysis.py: no longer
# referenced by this function; check_baseline_anchor itself stays defined
# (dead code, still exercised by test_analysis.py per NFR-7 dead-constant note)
```

#### Pseudo-code — `verify_v2_run_complete` (Gap B, new)

```python
def verify_v2_run_complete(experiment_log, results):
    indicators = {
        "reuse_verified": ("verify_cache_reuse: 10 examples consistent" in experiment_log
                           or "fresh generation" in experiment_log),
        "anchor_reported": all(f"A2-v2 anchor: {c}" in experiment_log
                               for c in results["completed_cells"]),
        "grid_nondegenerate": all(
            r["gate"]["best_auroc"] != r["gate"]["final_layer_entropy_auroc"]
            for r in results["cells"].values()),
        "screen_healthy": all(len(r["retained_layers"]) >= 5
                              for r in results["cells"].values()),
        "all_cells_measured": len(results["completed_cells"]) == 6,        # v1 stopped at 1
    }
    return all(indicators.values()), indicators
```

**`results` shape contract** — identical to `analyze_all`'s existing return dict (`summary`) plus one derived key added at the call site, NOT inside `analyze_all`:
`results = {**summary, "completed_cells": list(summary["cells"])}` where `summary["cells"][c] = {"gate": {...9 keys, None-safe}, "mechanism": {...}, "retained_layers": [int, ...]}`.

#### Pseudo-code — `run_model` + `main()` wiring

```python
def run_model(model_key):
    smoke_test(model_key)
    model, tokenizer = load_model(model_key)
    validate_layout(model)
    for dataset_name, loader in LOADERS.items():
        reuse_path = (DONOR_CACHE_LLAMA2_TRIVIAQA
                      if (model_key, dataset_name) == ("llama2", "triviaqa") else None)
        run_sweep(model, tokenizer, model_key, loader(), dataset_name,
                  reuse_cache_path=reuse_path)
        cache_path = f"{RESULTS_DIR}/cache_{model_key}_{dataset_name}.csv"
        final_auroc = check_anchor_and_halt(                          # CHANGED: capture return
            model_key, dataset_name, pd.read_csv(cache_path))
        log.info(f"{model_key}/{dataset_name}: cell complete, "        # NEW line
                 f"final_auroc={final_auroc:.4f}")
    del model
    torch.cuda.empty_cache()


def main():
    args = build_parser().parse_args()
    torch.manual_seed(SEED)
    model_keys = list(MODEL_IDS) if args.model == "all" else [args.model]

    # KEPT verbatim (harmless): check_anchor_and_halt no longer raises
    # SystemExit, so this pre-flight call is now a redundant idempotent
    # re-check on rerun; return value ignored, 0 control-flow change.
    if args.full and "llama2" in model_keys:
        early_path = Path(f"{RESULTS_DIR}/cache_llama2_triviaqa.csv")
        if early_path.exists():
            df = pd.read_csv(early_path)
            if "selection" in set(df["split"]):
                check_anchor_and_halt("llama2", "triviaqa", df)

    if args.smoke and not args.full:
        for mk in model_keys:
            smoke_test(mk)
    if args.full:
        for mk in model_keys:
            run_model(mk)
    if args.analyze or (args.full and args.model == "all"):
        summary = analyze_all(list(MODEL_IDS))                        # UNCHANGED call
        # NEW (Gap B wiring): whole-run verifier, log-only -- does NOT affect
        # summary["overall_pass"] (that verdict stays evaluate_gate-only)
        log_path = Path(__file__).parent / "experiment.log"
        exp_log = log_path.read_text() if log_path.exists() else ""
        v2_ok, v2_detail = verify_v2_run_complete(
            exp_log, {**summary, "completed_cells": list(summary["cells"])})
        log.info(f"verify_v2_run_complete: pass={v2_ok} detail={v2_detail}")
```

#### Acceptance criteria

- `verify_mechanism_activated` detail dict has NO `"baseline_reproduced"` key; HAS `"anchor_computed"` key; same call site/signature in `analyze_all` (`git diff` on `analyze_all`'s body is empty).
- `verify_v2_run_complete` importable from `analysis.py`, signature `(experiment_log: str, results: dict) -> tuple[bool, dict]` — does not collide with per-cell `verify_mechanism_activated(signals, auroc_grid, log_text)`.
- `run_model`'s cell loop contains `final_auroc = check_anchor_and_halt(...)` (grep-verifiable), followed by the new INFO log line.
- `main()` end-of-run log contains `"verify_v2_run_complete: pass="`.
- `test_verify_mechanism_activated_no_h_e1_references` (FR-6.1, D-3 scope) passes against this signature unmodified.

---

## D-5: Full 6-cell sweep [Complexity: 10, Budget: 10]

**Applied**: none — KB out-of-domain (see header).

**Subtasks [2/2 used]**

| ID | Subtask | Description |
|----|---------|--------------|
| D-5.1 | Donor-reuse binding-cell path + Gap C validation | Verify `DONOR_CACHE_LLAMA2_TRIVIAQA` resolves to sibling `h-e1/results/`; `verify_cache_reuse` 10/10; donor copy for llama2/triviaqa |
| D-5.2 | 5-fresh-cell sweep orchestration + resume + per-cell anchor report | `run_model` per remaining `MODEL_IDS` × `LOADERS` combos; resumability; completion gate for D-6 |

---

### D-5.1: Donor-reuse binding-cell path + Gap C validation [complexity 5]

**Integration**: runs once, before the fresh-cell sweep (D-5.2); reuses `verify_cache_reuse`, `run_sweep`'s donor branch, and D-2.1's `check_anchor_and_halt` (all unchanged by D-5 itself — D-5 is orchestration/validation, not new mechanism code). `DONOR_CACHE_LLAMA2_TRIVIAQA`'s 1-line path patch is D-1 scope (Gap C fix); this subtask's job is validating that patch under the real donor artifact.

#### API Signatures

```python
# run_h_e1.py — NEW (Gap C acceptance check; thin, no new state)
def verify_donor_cache_path() -> bool:
    """True iff DONOR_CACHE_LLAMA2_TRIVIAQA resolves to sibling
    h-e1/results/cache_llama2_triviaqa.csv (1000 rows, splits finalized),
    NOT the stale _archive/20260805T054934_routing_recovery path (Gap C)."""
```

#### Tensor/array shapes

| Variable | Shape | Note |
|----------|-------|------|
| donor `df` | `(1000, 101)` | 5 meta + 96 signal cols (`CACHE_FIELDS`); `split` already `{"selection","test"}` — pre-finalized by h-e1 |
| `verify_cache_reuse` regen loop | `n_check=10` iterations | free byproduct also seeds `top1_agreement_llama2_triviaqa.npy` (32,) via the donor branch in `run_sweep`, unchanged |

#### Pseudo-code

```python
def verify_donor_cache_path():
    p = Path(DONOR_CACHE_LLAMA2_TRIVIAQA)
    expected = (Path(RESULTS_DIR).resolve().parents[1] / "h-e1" / "results"
                / "cache_llama2_triviaqa.csv")
    if p.resolve() != expected.resolve() or not p.exists():
        return False
    df = pd.read_csv(p)
    return len(df) == 1000 and {"selection", "test"} <= set(df["split"])

# --- D-5.1 execution sequence ---
assert verify_donor_cache_path(), "Gap C regression: DONOR_CACHE_LLAMA2_TRIVIAQA misresolved"
model, tokenizer = load_model("llama2")
validate_layout(model)
ok = verify_cache_reuse(model, tokenizer, DONOR_CACHE_LLAMA2_TRIVIAQA,
                        load_triviaqa(), "triviaqa", n_check=10)
assert ok, "donor protocol-identity check failed -- FR-3.4 requires a WARNING log, not a silent drop"
del model; torch.cuda.empty_cache()

run_model("llama2")     # unchanged body (D-2.2); covers BOTH llama2/triviaqa
                         # (donor, this subtask) AND llama2/truthfulqa (fresh,
                         # counted in D-5.2's 5 remaining cells)

cache_df = pd.read_csv(f"{RESULTS_DIR}/cache_llama2_triviaqa.csv")
assert len(cache_df) == 1000 and set(cache_df["split"]) == {"selection", "test"}
assert Path(f"{RESULTS_DIR}/top1_agreement_llama2_triviaqa.npy").exists()
```

#### Acceptance criteria

- `verify_donor_cache_path()` → `True`; path string does NOT contain `"_archive"`.
- `verify_cache_reuse(...)` → `True`; log contains `"verify_cache_reuse: 10 examples consistent -> reuse OK"`.
- `cache_llama2_triviaqa.csv` in `h-e1-v2/results/`: 1000 rows, `split ∈ {selection,test}`, log contains `"donor cache reused, 1000 rows copied, 0 full-sweep GPU calls"`.
- `check_anchor_and_halt("llama2","triviaqa", ...)` returns a `float`, no `SystemExit`.
- `top1_agreement_llama2_triviaqa.npy` shape `(32,)` (n=10 sample — unchanged h-e1 approximation, `ponytail:` ceiling inherited verbatim, not re-litigated here).

---

### D-5.2: 5-fresh-cell sweep orchestration + resume + per-cell anchor report [complexity 5]

**Integration**: reuses `run_model` (D-2.2), `resume_from_cache` (verbatim), `check_anchor_and_halt` (D-2.1) unchanged. Entrypoint is the unchanged CLI (`run_experiment.sh` → `python run_h_e1.py --full --model all --analyze`) — no new orchestrator function needed (ladder rung 2: `main()` already does this).

#### API Signatures

```python
# run_h_e1.py — NEW (D-5 acceptance gate; feeds D-6's "all_cells_measured")
def sweep_status(model_keys: list[str]) -> dict[str, bool]:
    """{'{model}/{dataset}': bool} -- True iff cache_{m}_{d}.csv exists AND
    split column contains BOTH 'selection' and 'test' (finalized, not left
    mid-generation)."""
```

#### Pseudo-code — orchestration (CLI-level, unchanged entrypoint)

```python
def sweep_status(model_keys):
    status = {}
    for m in model_keys:
        for d in LOADERS:
            p = Path(f"{RESULTS_DIR}/cache_{m}_{d}.csv")
            status[f"{m}/{d}"] = (p.exists() and
                {"selection", "test"} <= set(pd.read_csv(p, usecols=["split"])["split"]))
    return status

# --- entrypoint (main(), MODEL_IDS dict order -- llama2 first, unchanged) ---
for mk in ["llama2", "mistral", "llama3"]:
    run_model(mk)
    # llama2:  triviaqa=donor (D-5.1, 0 GPU)      + truthfulqa=fresh
    # mistral: triviaqa=fresh                     + truthfulqa=fresh
    # llama3:  triviaqa=fresh                     + truthfulqa=fresh
    # = 5 fresh cells total, ~4,451 examples, ~2.5h H100 (NFR-1); each cell's
    # check_anchor_and_halt call (D-2.1) never halts -- fail-fast only on
    # ValueError contract violations (empty split / single-class labels)

status = sweep_status(list(MODEL_IDS))
assert all(status.values()), f"incomplete cells: {[c for c, ok in status.items() if not ok]}"
```

#### Pseudo-code — resumability acceptance check (NFR-6)

```python
# Simulated interruption: SIGKILL mid-loop during mistral/truthfulqa generation,
# rerun `python run_h_e1.py --full --model mistral`
resume_ids = resume_from_cache(f"{RESULTS_DIR}/cache_mistral_truthfulqa.csv")
assert len(resume_ids) > 0                       # picked up mid-cache, not restarted from 0
run_model("mistral")                             # unchanged; skips resume_ids rows internally
df = pd.read_csv(f"{RESULTS_DIR}/cache_mistral_truthfulqa.csv")
assert df["example_id"].is_unique                # no duplicate rows across interrupt+resume
assert set(df["split"]) == {"selection", "test"} # finalization tail still ran to completion
```

#### Acceptance criteria

- `sweep_status(list(MODEL_IDS))` → all `True` after the full run (6/6 cells, including D-5.1's).
- Each of the 5 fresh cells: `experiment.log` contains `"A2-v2 anchor: {model}/{dataset} within-sweep final L32 entropy AUROC="`; zero `SystemExit` occurrences in the log.
- `meta_{model}_{dataset}.json` written for all 5 fresh cells; `n_written + n_skipped == len(dataset)` per cell (1000 for triviaqa, 817 for truthfulqa).
- Interrupted+resumed cache: `example_id` unique, no truncated/corrupt tail row survives (`resume_from_cache`'s length-mismatch guard fires at most once).
- Total elapsed time for the 5 fresh cells reported and compared against the ~2.5h NFR-1 budget (informational, not a hard gate).
