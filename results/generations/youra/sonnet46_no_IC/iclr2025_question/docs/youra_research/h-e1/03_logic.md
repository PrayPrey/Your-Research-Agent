# Logic: h-e1 — Layer-Wise Logit-Lens Existence Sweep

**Scope**: A-2 (Resume + cache-reuse patch) and A-3 (A2 anchor pre-gate) only — the two highest-complexity Epic tasks. All other tasks (A-1, A-4..A-7) are copy-paste/unmodified reuse per `03_architecture.md`, out of scope here.

**Applied**: none — KB out-of-domain (null result). Queries `"resume checkpoint from cache CSV"` and `"DL API design patterns"` both returned only HuggingFace `diffusers` community-pipeline docs (source `8b1c7f40739544a6`, similarity ≤ 0.40), zero relevant hits. Confirms the architecture agent's prior null finding.

---

## Codebase Analysis (Serena)

**Project Type**: existing_codebase (v1 archive, reuse donor — not a `base_hypothesis` prerequisite)
**Status**: Actual signatures verified from code (specs may drift — code wins)
**Analyzed Path**: `docs/youra_research/_archive/20260805T054934_routing_recovery/h-e1/code/`
**Tools used**: `get_symbols_overview` (`run_h_e1.py`, `constants.py`), `find_symbol`+body (`run_sweep`, `write_cache_row`, `generate_and_extract`, `check_baseline_anchor`, `stratified_split`, `run_model`, `main`), full `Read` (`analysis.py`, `data.py`, `constants.py`, donor `results/cache_llama2_triviaqa.csv` header+rows).

**Relevant symbols verified**:
- `run_sweep(model, tokenizer, model_key, dataset, dataset_name, max_new_tokens=MAX_NEW_TOKENS)` — **v1 has NO `reuse_cache_path` param, opens cache in `"w"` mode unconditionally, always restarts `range(len(dataset))` from 0**. This is the exact gap A-2 closes.
- `write_cache_row(writer, example_id, dataset_name, model_key, split_name, label, signals)` — reused verbatim by both A-2 branches.
- `generate_and_extract(model, tokenizer, example, dataset_name, max_new_tokens=MAX_NEW_TOKENS) -> tuple[str, dict]` — returns `(generated_text, signals)`; `signals["entropy"]` all-NaN `(32,)` array signals an empty-answer-span skip.
- `check_baseline_anchor(final_layer_entropy_auroc, model_key, dataset_name) -> bool` — `analysis.py:57-59`, one-liner `abs(x - H_E1_REFERENCES[key]) <= BASELINE_TOLERANCE`. Reused verbatim by A-3.1.
- `corrected_auroc(labels, scores) -> tuple[float, bool]` — `analysis.py:27-33`, `(max(auc,1-auc), flipped)`, raises `ValueError` on single-class labels. Reused verbatim by A-3.1.
- `stratified_split(labels, seed=SEED) -> tuple[list[int], list[int]]` — `data.py:59-67`; used unchanged in the finalization tail both A-2 branches converge on.
- `run_model(model_key)` / `main()` — `run_h_e1.py:143-150, 251-262`. v1 has no anchor-check call anywhere; `main()` has no pre-flight branch. Both replaced by A-3.2.
- **`CACHE_FIELDS`** (`run_h_e1.py:22-27`) — `["example_id","dataset","model","split","label"] + entropy_L1..32 + maxprob_L1..32 + adj_kl_L1..32` (101 cols). Confirmed identical to the donor CSV header (byte-read).
- **Donor cache fact** (byte-read `cache_llama2_triviaqa.csv` rows 1-2): `split` column is literally the string `"pending"` on every row — pre-finalization snapshot, 1000/1000 rows, `example_id` = 0-indexed dataset position (not `question_id`).
- **No `top1_agreement_llama2_triviaqa.npy` or `meta_llama2_triviaqa.json` exist in the donor `results/` dir** (`Glob` confirmed only the CSV is present) — `top1_match` is never persisted per-row in `CACHE_FIELDS`, so it cannot be reconstructed from the donor CSV alone. Handled explicitly in A-2.2 below.

---

## A-2: Resume + cache-reuse patch [Complexity: 13, Budget: 13]

**Applied**: none — KB out-of-domain (see header).

### API Signatures

```python
# run_h_e1.py — NEW
def resume_from_cache(path: str) -> set[int]:
    """Existing cache at path -> set of already-written example_id. {} if missing/header-only."""
    ...

def verify_cache_reuse(model, tokenizer, cache_path: str, dataset, dataset_name: str,
                        n_check: int = 10) -> bool:
    """Regenerate first n_check dataset rows fresh; compare label to donor row. All-consistent -> True."""
    ...

# run_h_e1.py — MODIFIED (adds reuse_cache_path, kwarg-only extension — call sites unaffected)
def run_sweep(model, tokenizer, model_key, dataset, dataset_name,
              max_new_tokens: int = MAX_NEW_TOKENS,
              reuse_cache_path: str | None = None) -> None:
    ...

# run_h_e1.py — NEW module-level constant (near CACHE_FIELDS/LOADERS; constants.py stays 0-edit)
DONOR_CACHE_LLAMA2_TRIVIAQA = (
    "docs/youra_research/_archive/20260805T054934_routing_recovery/"
    "h-e1/results/cache_llama2_triviaqa.csv"
)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| A-2.1 | resume_from_cache + append patch | New helper + `run_sweep`'s non-donor branch: `'a'`-mode, skip written `example_id` |
| A-2.2 | verify_cache_reuse + donor short-circuit | New helper + `run_sweep`'s donor branch: copy rows in place of generation, finalize pending split |

---

#### A-2.1: `resume_from_cache` + append-mode patch [complexity 3]

**Integration**: called at the top of `run_sweep`'s non-donor branch; the returned `set[int]` gates the `for idx in range(len(dataset))` loop that already exists in v1.

**Pseudo-code**:
```
def resume_from_cache(path):
    if not Path(path).exists(): return set()
    with open(path, "r+", newline="") as f:
        header = f.readline()
        if header.rstrip("\n").split(",") != CACHE_FIELDS: return set()   # unrecognized/empty -> treat as no cache
        ids = set()
        while True:
            pos = f.tell(); line = f.readline()
            if not line: break                                            # clean EOF
            if not line.endswith("\n") or len(next(csv.reader([line]))) != len(CACHE_FIELDS):
                log.warning(f"resume_from_cache: truncating corrupt/partial tail row at byte {pos}")
                f.seek(pos); f.truncate(); break                          # drop unflushed interrupted row
            ids.add(int(line.split(",", 1)[0]))
    return ids
```

**run_sweep non-donor branch** (else of the A-2.2 donor check; unindented for readability):
```
resume_ids = resume_from_cache(path)
new_file = not Path(path).exists()
with open(path, "a" if not new_file else "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=CACHE_FIELDS)
    if new_file:
        writer.writeheader()
    for idx in range(len(dataset)):
        if idx in resume_ids:
            continue
        # --- unchanged v1 body: generate_and_extract -> write_cache_row -> f.flush() ---
# falls through to the unchanged finalization tail (stratified_split + write-back, see A-2.2)
```

**Edge cases**:
| Case | Handling |
|------|----------|
| No file at `path` | `resume_from_cache` -> `{}`; `new_file=True` -> `"w"` mode + header (v1-identical fresh start) |
| Header-only file (0 data rows) | Loop body never executes -> `{}`; `new_file=False` (file exists) -> `"a"` mode, header NOT rewritten (no dup header) |
| Partial/corrupt tail row (killed mid-`write`) | Length-mismatch / no-trailing-`\n` check truncates the file back to the last complete row via `f.seek(pos); f.truncate()` **before** `run_sweep` reopens in `"a"` mode — the corrupt example_id is re-generated cleanly on this pass, no duplicate/malformed row survives |
| File exists, header mismatches `CACHE_FIELDS` (e.g. stale schema) | `resume_from_cache` returns `{}` but `new_file` is still `False` -> **caller must additionally check** header validity before deciding `"a"` vs `"w"`; simplest fix: `resume_from_cache` itself already validated the header, so treat `header mismatch` the same as "missing" for mode selection too (`new_file = not Path(path).exists() or resume_ids_call_returned_due_to_bad_header`) — flag this coupling explicitly in the Phase 4 implementation so a stale-schema cache doesn't silently `"a"`-append mismatched columns |

---

#### A-2.2: `verify_cache_reuse` + donor short-circuit [complexity 3]

**Integration**: `run_model` (A-3.2) passes `reuse_cache_path=DONOR_CACHE_LLAMA2_TRIVIAQA` only for the `("llama2","triviaqa")` cell; all other 5 cells call `run_sweep` with `reuse_cache_path=None` (falls straight into A-2.1's branch).

**Pseudo-code — `verify_cache_reuse`**:
```
def verify_cache_reuse(model, tokenizer, cache_path, dataset, dataset_name, n_check=10):
    if not Path(cache_path).exists():
        log.warning(f"verify_cache_reuse: donor missing at {cache_path}"); return False
    donor = pd.read_csv(cache_path).set_index("example_id")
    for idx in range(min(n_check, len(dataset))):
        text, sig = generate_and_extract(model, tokenizer, dataset[idx], dataset_name)
        fresh_empty = bool(np.isnan(sig["entropy"]).all())
        if idx not in donor.index:
            if fresh_empty: continue                 # both sides: empty-answer skip -> consistent
            log.warning(f"idx={idx}: missing in donor, fresh regen produced an answer"); return False
        if fresh_empty:
            log.warning(f"idx={idx}: present in donor, fresh regen empty"); return False
        if label_response(dataset[idx], text, dataset_name) != int(donor.loc[idx, "label"]):
            log.warning(f"idx={idx}: label mismatch"); return False
    log.info(f"verify_cache_reuse: {n_check} examples consistent -> reuse OK")
    return True
```

**Pseudo-code — `run_sweep` donor branch** (precedes A-2.1's else branch; both converge on the unchanged finalization tail):
```
def run_sweep(model, tokenizer, model_key, dataset, dataset_name,
              max_new_tokens=MAX_NEW_TOKENS, reuse_cache_path=None):
    Path(RESULTS_DIR).mkdir(parents=True, exist_ok=True)
    path = f"{RESULTS_DIR}/cache_{model_key}_{dataset_name}.csv"

    if reuse_cache_path and verify_cache_reuse(model, tokenizer, reuse_cache_path, dataset, dataset_name):
        donor_df = pd.read_csv(reuse_cache_path)
        donor_df["split"] = "pending"                       # normalize, idempotent even if already finalized
        donor_df.to_csv(path, index=False)                  # copy into the NEW cell path; donor untouched
        n_written, n_skipped = len(donor_df), len(dataset) - len(donor_df)
        log.info(f"{model_key}/{dataset_name}: donor reused, {n_written} rows, 0 full-sweep GPU calls")

        # top1_match is NOT a CACHE_FIELDS column (see Codebase Analysis) -> cannot be
        # reconstructed from the donor CSV. Approximate top1_agreement.npy from the
        # n_check regenerations verify_cache_reuse already ran (free byproduct).
        # ponytail: n=10 sample not the full n=1000; upgrade to a full recompute pass
        # only if degeneracy_screen's dependence on this file becomes a measured issue.
        n_check = 10
        top1_sample = np.zeros(N_LAYERS, dtype=np.float64)
        for idx in range(min(n_check, len(dataset))):
            _, sig = generate_and_extract(model, tokenizer, dataset[idx], dataset_name)
            if not np.isnan(sig["entropy"]).all():
                top1_sample += sig["top1_match"]
        np.save(f"{RESULTS_DIR}/top1_agreement_{model_key}_{dataset_name}.npy", top1_sample / n_check)
    else:
        if reuse_cache_path:
            log.warning(f"{model_key}/{dataset_name}: donor verification FAILED -> fresh generation")
        # --- A-2.1 branch (resume_from_cache + append-mode loop) runs here ---
        # sets n_written, n_skipped, top1_sum, saves top1_agreement.npy from top1_sum/n_written

    # --- UNCHANGED v1 finalization (both branches converge) ---
    df = pd.read_csv(path)
    labels = df["label"].tolist()
    selection_idx, test_idx = stratified_split(labels, SEED)
    split_col = np.array(["test"] * len(df), dtype=object)
    split_col[selection_idx] = "selection"
    df["split"] = split_col
    df.to_csv(path, index=False)
    write_test_split_locked(df.iloc[test_idx]["example_id"].tolist(), dataset_name, model_key)
    # meta_{model}_{dataset}.json written as in v1, using n_written/n_skipped from whichever branch ran
```

**Edge cases**:
| Case | Handling |
|------|----------|
| Donor cache `split="pending"` on every row (verified fact) | `donor_df["split"] = "pending"` line is a no-op here but makes the copy idempotent if rerun against an already-finalized copy |
| `verify_cache_reuse` fails (label drift, missing file) | `run_sweep` logs a warning and falls through to the A-2.1 resume/append branch — **never silently drops the cell**, always produces a cache one way or another |
| Donor missing a row that fresh regen produces an answer for (or vice versa) | Treated as a mismatch -> `verify_cache_reuse` returns `False` (protocol drift signal, not silently ignored) |
| `top1_agreement_llama2_triviaqa.npy` for the reused cell | Approximated from `n_check=10` samples, not the full 1000 — flagged inline with a `ponytail:` comment; consumed downstream only by A-6's `degeneracy_screen` (out of this task's scope) |
| `run_sweep` called twice for the same donor cell (idempotency) | Second call: donor branch re-verifies (10 more regenerations, cheap), re-copies identical rows, re-finalizes split with the same seed -> same result, no accumulation/duplication |

---

## A-3: A2 anchor pre-gate [Complexity: 11, Budget: 11]

**Applied**: none — KB out-of-domain (see header).

### API Signatures

```python
# run_h_e1.py — NEW (imports analysis.check_baseline_anchor, analysis.corrected_auroc)
def check_anchor_and_halt(model_key: str, dataset_name: str, cache_df: pd.DataFrame) -> None:
    """Selection-split final-layer (L32) entropy AUROC vs H_E1_REFERENCES.
    Raises SystemExit with the delta if outside BASELINE_TOLERANCE. Returns None on pass."""
    ...

# run_h_e1.py — MODIFIED orchestration
def run_model(model_key: str) -> None: ...   # smoke -> per-dataset sweep -> anchor check right after each sweep
def main() -> None: ...                       # pre-flight zero-GPU anchor check for llama2/triviaqa if already finalized on disk
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| A-3.1 | check_anchor_and_halt | New standalone halt-gate function, self-contained (no degeneracy_screen dependency) |
| A-3.2 | run_model/main reorder | Wire the gate: llama2/triviaqa checked first (cache-only where possible), every other cell checked immediately post-sweep |

---

#### A-3.1: `check_anchor_and_halt` [complexity 2]

**Integration**: called by `run_model` (A-3.2) right after each cell's cache is finalized (either branch of A-2.2's `run_sweep`), and by `main`'s pre-flight check before any model loads.

**Note**: computes the AUROC directly from `entropy_L32`, independent of A-6's `degeneracy_screen`/`build_auroc_grid` pipeline (which needs `top1_agreement.npy` + `vocab_size` that may not exist yet at this point in the flow) — this keeps A-3 fully self-contained and runnable the moment a cache is finalized.

**Pseudo-code**:
```
def check_anchor_and_halt(model_key, dataset_name, cache_df):
    sel = cache_df[cache_df["split"] == "selection"]
    if sel.empty:
        raise ValueError(f"check_anchor_and_halt: no 'selection' rows for {model_key}/{dataset_name} "
                          f"-- split finalization must run before the anchor check")
    labels, scores = sel["label"].to_numpy(), sel["entropy_L32"].to_numpy()
    try:
        final_auroc, _ = corrected_auroc(labels, scores)        # analysis.py, verbatim reuse
    except ValueError as e:
        raise ValueError(f"check_anchor_and_halt: AUROC undefined for {model_key}/{dataset_name} "
                          f"(degenerate label split?): {e}") from e
    ref = H_E1_REFERENCES[(model_key, dataset_name)]
    delta = final_auroc - ref
    if not check_baseline_anchor(final_auroc, model_key, dataset_name):   # analysis.py, verbatim reuse
        raise SystemExit(
            f"A2 anchor BROKEN: {model_key}/{dataset_name} final-layer entropy AUROC={final_auroc:.4f} "
            f"vs reference={ref:.4f} (delta={delta:+.4f}, tolerance=+/-{BASELINE_TOLERANCE}). "
            f"HALT per FR-4.1 -- reconcile labels/prompts (RISK-2).")
    log.info(f"A2 anchor OK: {model_key}/{dataset_name} final_auroc={final_auroc:.4f} "
             f"ref={ref:.4f} delta={delta:+.4f}")
```

**Tensor/array shapes**:
| Variable | Shape | Note |
|----------|-------|------|
| `labels`, `scores` | `(n_selection,)` | 500 (triviaqa) or 408 (truthfulqa) |
| `final_auroc` | scalar float | `max(auc, 1-auc)`, matches `H_E1_REFERENCES` orientation (all values >= 0.5) |

**Edge cases**:
| Case | Handling |
|------|----------|
| Called before split finalization (all rows `"pending"`) | `sel.empty` -> `ValueError` (caller-contract violation, distinct from a real tolerance-breach `SystemExit`) |
| Selection split single-class (degenerate stratification) | `corrected_auroc`'s `roc_auc_score` `ValueError` re-raised with a clearer message, not swallowed |
| Tolerance breach | `SystemExit` with model/dataset/observed/reference/delta in the message — halts the whole process (`main`'s call stack), per FR-4.1's "HALT before proceeding" |
| Pass | Returns `None`, logs one INFO line; caller continues |

---

#### A-3.2: `run_model`/`main` reorder [complexity 4]

**Integration**: `run_model` gains one `check_anchor_and_halt` call per dataset loop iteration; `main` gains one pre-flight branch before the `if args.full:` model loop. Both reuse `DONOR_CACHE_LLAMA2_TRIVIAQA` (A-2.2) and `check_anchor_and_halt` (A-3.1).

**Pseudo-code**:
```
def run_model(model_key):
    smoke_test(model_key)
    model, tokenizer = load_model(model_key)
    validate_layout(model)
    for dataset_name, loader in LOADERS.items():
        reuse_path = (DONOR_CACHE_LLAMA2_TRIVIAQA
                      if (model_key, dataset_name) == ("llama2", "triviaqa") else None)
        run_sweep(model, tokenizer, model_key, loader(), dataset_name, reuse_cache_path=reuse_path)
        cache_path = f"{RESULTS_DIR}/cache_{model_key}_{dataset_name}.csv"
        check_anchor_and_halt(model_key, dataset_name, pd.read_csv(cache_path))   # halts before next cell
    del model
    torch.cuda.empty_cache()


def main():
    args = build_parser().parse_args()
    torch.manual_seed(SEED)
    model_keys = list(MODEL_IDS) if args.model == "all" else [args.model]

    if args.full and "llama2" in model_keys:
        # Fast pre-flight: zero GPU, no model load. Only fires on a RERUN where
        # cache_llama2_triviaqa.csv is already finalized on disk (split has "selection"
        # rows). On a first-ever run the file doesn't exist yet -> skipped, falls
        # through to run_model's per-cell check below (the reuse+verify path, which
        # does need the model loaded -- see A-2.2's ~10-regeneration cost).
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
        analyze_all(list(MODEL_IDS))
```

**Edge cases**:
| Case | Handling |
|------|----------|
| First-ever run (no `cache_llama2_triviaqa.csv` on disk yet) | Pre-flight `early_path.exists()` is `False` -> skipped entirely; anchor first checked inside `run_model("llama2")`'s loop, right after the triviaqa cell's `run_sweep` (donor-reuse path, A-2.2) finalizes |
| Rerun after a prior successful `--full` run | Pre-flight finds a finalized cache, halts/passes with **zero model load**; if it passes, `run_model("llama2")` still re-verifies redundantly inside its loop (harmless idempotent double-check, no extra GPU beyond the ~10 verify regenerations) |
| `--model mistral` (llama2 not in `model_keys`) | Pre-flight guarded by `"llama2" in model_keys` -> skipped; no anchor check runs for a model not being executed |
| `--smoke`-only run (no `--full`) | Pre-flight guarded by `args.full` -> skipped; anchor checking is only meaningful once caches exist |
| Tolerance breach on any cell (llama2/triviaqa pre-flight, or any cell inside `run_model`) | `SystemExit` propagates up through `run_model`/`main`, halting before the next cell/model loads — satisfies FR-4.1's "checked BEFORE the full sweep" for llama2/triviaqa and "immediately after its own sweep" for every other cell |
