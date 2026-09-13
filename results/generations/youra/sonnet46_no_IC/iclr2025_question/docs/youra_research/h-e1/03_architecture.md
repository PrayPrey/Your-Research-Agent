# Architecture: h-e1 — Layer-Wise Logit-Lens Existence Sweep

**Hypothesis Type**: EXISTENCE (training-free, inference-only PoC) | **Tier**: LIGHT
**Date**: 2026-08-05

**Applied**: none — KB out-of-domain (null result recorded). Re-ran 2 Archon queries in Phase 3 ("DL experiment architecture inference pipeline", "logit lens hidden states hallucination"); all top hits are HuggingFace `diffusers` community-pipeline/attention-processor docs (source `8b1c7f40739544a6`, similarity ≤ 0.56) — zero interpretability/hallucination-detection content. Confirms Phase 2C's null Archon finding; no fabricated sources used.

---

## Codebase Analysis (Serena)

**Project Type**: existing_codebase (v1 archive — protocol-identical prior episode, mandated as primary reuse donor; not a prerequisite `base_hypothesis` in the verification chain)
**Status**: Complete, protocol-identical implementation found — reused near-verbatim
**Analyzed Path**: `docs/youra_research/_archive/20260805T054934_routing_recovery/h-e1/code/`
**Tools used**: `get_symbols_overview` (all 6 modules), `find_symbol`+body (`per_layer_lens_signals`, `degeneracy_screen`, `corrected_auroc`, `run_sweep`, `write_cache_row`), full `Read` (constants.py, data.py, analysis.py, run_h_e1.py, visualize.py, requirements.txt), cache CSV inspection (header + rows 1-2 + rows 998-1000).

**Findings**: 6 modules / 658 lines, structurally sound and directly reusable. `constants.py` holds all 17 protocol constants including `H_E1_REFERENCES`/`AUROC_GATE`/`BASELINE_TOLERANCE`. `model.py::per_layer_lens_signals` implements the exact lens path `model.lm_head(model.model.norm(h_l))` in float32 with a single `prev_logp` buffer (memory-safe, no 32-layer stack). `RESULTS_DIR`/`FIGURES_DIR` derive from `Path(__file__).resolve().parents[1]` — copying the files into the new `h-e1/code/` auto-resolves paths to `h-e1/results/` and `h-e1/figures/`, **zero path edits needed**.

**Spec-vs-code divergences found (code wins, per project rule):**
1. FR-1.3 calls `format_prompt` "few-shot" — actual code (`data.py:22-25`) is a plain zero-shot template `f"Q: {question}\nA:"`, already flagged in-code as a documented deviation. MUST reuse verbatim — it produced the `H_E1_REFERENCES` anchor numbers; changing it to match the PRD's prose description would break A2 reproduction.
2. FR-1.4 names one `data_splits.json` — actual `write_test_split_locked` writes per-cell `test_split_locked_{model_key}_{dataset_name}.json` (6 files total). Correctness labels (and therefore the stratified split) are generation-dependent — computed per model, not once globally — so a single global file is not the right shape. Keep the per-cell files.
3. FR-3.4 / NFR-6 require "resume by example_id on interruption — no recomputation." Actual `run_sweep` (`run_h_e1.py:66-122`) opens the cache path with mode `"w"` unconditionally and always iterates `range(len(dataset))` from 0 — **no resume logic exists in v1**. This is the one real functional gap; closed by Task A-2 below.
4. The reusable donor cache `cache_llama2_triviaqa.csv` (1000/1000 rows, verified via head+tail read) has `split="pending"` on every row — it is the **pre-finalization** snapshot, captured before `run_sweep`'s post-loop `stratified_split` + write-back ran. Reuse must run that finalization step on the copied cache, not assume splits are already assigned. (The 871-row interruption mentioned in the PRD problem statement is a different, older archive snapshot — this 1000-row file is complete.)

**Used for**: module structure below (near-verbatim interfaces), file organization, and the 3 tasks (A-2, A-3, A-7) that require genuinely new code beyond copy-paste.

---

## Module Structure

### constants.py (`h-e1/code/constants.py`) — copied verbatim, 0 edits

```python
SEED = 42
MODEL_IDS: dict[str, str]          # llama2/mistral/llama3 -> HF id; dict order = run order
N_LAYERS = 32; EXPECTED_HIDDEN_STATES = 33; MAX_NEW_TOKENS = 32
DEGENERACY_ENTROPY_PCT = 0.01; DEGENERACY_AGREEMENT_MIN = 0.05
AUROC_GATE = 0.55; BASELINE_TOLERANCE = 0.03
H_E1_REFERENCES: dict[tuple[str, str], float]   # (model_key, dataset) -> anchor AUROC
RESULTS_DIR: str; FIGURES_DIR: str   # auto-resolve to h-e1/{results,figures}/
SMOKE_N = 10; TRIVIAQA_N = 1000; TRUTHFULQA_N = 817
HF_TOKEN: str   # raises RuntimeError at import if unset
```

### model.py (`h-e1/code/model.py`) — copied verbatim, 0 edits

**Dependencies**: constants

```python
class LayoutError(Exception): ...

def load_model(model_key: str) -> tuple[PreTrainedModel, PreTrainedTokenizer]: ...
def validate_layout(model) -> None: ...   # raises LayoutError if model.model.norm / model.lm_head missing

@torch.no_grad()
def per_layer_lens_signals(model, hidden_states: tuple, answer_slice: slice) -> dict:
    """Returns {"entropy","maxprob","adj_kl","top1_match"}: each (32,) float.
    adj_kl[0]=NaN. Raises LayoutError if len(hidden_states) != 33."""
```

### data.py (`h-e1/code/data.py`) — copied verbatim, 0 edits

**Dependencies**: constants

```python
def load_triviaqa() -> Dataset: ...      # rc.nocontext, validation[:1000]
def load_truthfulqa() -> Dataset: ...    # generation, validation (817)
def format_prompt(example: dict, dataset_name: str) -> str: ...   # "Q: {q}\nA:" zero-shot, protocol-frozen
def label_response(example: dict, generated: str, dataset_name: str) -> int: ...  # 1=hallucination
def stratified_split(labels: list, seed: int = SEED) -> tuple[list[int], list[int]]: ...  # (selection_idx, test_idx)
def write_test_split_locked(test_idx: list, dataset_name: str, model_key: str) -> None: ...
```

### analysis.py (`h-e1/code/analysis.py`) — copied verbatim, 0 edits

**Dependencies**: constants

```python
def degeneracy_screen(entropy_grid, top1_agreement, vocab_size) -> list[int]: ...   # retained 0-idx layers
def corrected_auroc(labels, scores) -> tuple[float, bool]: ...   # (max(auc,1-auc), flipped)
def build_auroc_grid(cache_df, retained_layers: list[int]) -> np.ndarray: ...   # (n_retained,3), selection split only
def check_baseline_anchor(final_layer_entropy_auroc, model_key, dataset_name) -> bool: ...
def verify_mechanism_activated(signals: dict, auroc_grid, log_text: str) -> tuple[bool, dict]: ...
def evaluate_gate(auroc_grid, retained_layers: list[int]) -> dict: ...   # best_layer/signal/auroc/gate_pass/depth_beats_final
def write_cell_report(model_key, dataset_name, auroc_grid, retained_layers, counts) -> dict: ...
```

### visualize.py (`h-e1/code/visualize.py`) — copied verbatim + 1 new function

**Dependencies**: constants

```python
def plot_gate_bar_chart(gate_results: dict) -> Path: ...              # FR-5.2 mandatory
def plot_auroc_heatmap(auroc_grids: dict, retained_layers: dict) -> Path: ...   # FR-5.3
def plot_auroc_vs_depth(auroc_grids: dict, retained_layers: dict) -> Path: ...  # FR-5.4
def plot_degeneracy_report(retained_layers: dict) -> Path: ...        # FR-5.5

# NEW (Task A-7) — FR-5.6 has no v1 counterpart:
def plot_entropy_heatmap(cache_df, model_key: str = "llama2",
                          dataset_name: str = "triviaqa") -> Path: ...
    """examples x layers entropy heatmap, selection split, correct vs incorrect rows grouped."""
```

### run_h_e1.py (`h-e1/code/run_h_e1.py`) — patched (near-verbatim + 3 additions)

**Dependencies**: constants, data, model, analysis, visualize

```python
# UNCHANGED from v1:
def generate_and_extract(model, tokenizer, example, dataset_name, max_new_tokens=MAX_NEW_TOKENS) -> tuple[str, dict]: ...
def write_cache_row(writer, example_id, dataset_name, model_key, split_name, label, signals) -> None: ...
def smoke_test(model_key: str, n: int = SMOKE_N) -> bool: ...
def analyze_all(model_keys: list[str]) -> dict: ...
def build_parser() -> argparse.ArgumentParser: ...

# NEW (Task A-2 — closes the FR-3.4/NFR-6 resume gap):
def resume_from_cache(path: str) -> set[int]: ...
    """Existing cache at path -> set of already-written example_id (empty set if no file)."""

def verify_cache_reuse(model, tokenizer, cache_path: str, dataset, dataset_name: str,
                        n_check: int = 10) -> bool: ...
    """Regenerate the first n_check examples fresh; compare label_response() output to the
    cached row's label for the same example_id. All-match -> True (FR-3.5 hash/protocol check)."""

# MODIFIED (Task A-2): run_sweep gains resume + donor-cache-reuse params
def run_sweep(model, tokenizer, model_key, dataset, dataset_name,
              max_new_tokens=MAX_NEW_TOKENS, reuse_cache_path: str | None = None) -> None: ...
    """reuse_cache_path given + verify_cache_reuse() passes -> copy donor rows in place of
    generation (skips GPU work for those examples), then run the unchanged post-loop
    stratified-split finalization. Else -> open path in 'a' mode, skip example_id already in
    resume_from_cache(path), continue the loop (was: 'w' mode, always restarted at idx 0)."""

# NEW (Task A-3 — closes the FR-4.1 pre-sweep halt-gate gap):
def check_anchor_and_halt(model_key: str, dataset_name: str, cache_df) -> None: ...
    """Selection-split final-layer entropy AUROC vs check_baseline_anchor(); raises SystemExit
    with the mismatch delta if outside BASELINE_TOLERANCE. Called immediately after each cell's
    cache is finalized (reuse or fresh), not deferred to analyze_all()."""

# MODIFIED (Task A-3): orchestration calls check_anchor_and_halt per cell, llama2 first
def run_model(model_key: str) -> None: ...   # smoke -> sweep(s) -> check_anchor_and_halt per cell
def main() -> None: ...                       # model order = MODEL_IDS dict order (llama2 first: free anchor check via cache reuse before any GPU load)
```

Sequencing rationale (A-3): `llama2/triviaqa`'s anchor is checkable from the reused cache with zero GPU cost, so it runs first as a fast fail-fast gate before any model weights load; every subsequent cell (llama2/truthfulqa, then mistral x2, then llama3 x2) is anchor-checked immediately after its own sweep completes, halting before the next cell/model if broken — this satisfies "A2 anchor check BEFORE full sweep" without requiring all 6 sweeps to finish first.

---

## File Organization

```
h-e1/
  code/
    constants.py                 # copied verbatim (Task A-1)
    model.py                     # copied verbatim (Task A-1)
    data.py                      # copied verbatim (Task A-1)
    analysis.py                  # copied verbatim (Task A-1)
    visualize.py                 # copied verbatim + plot_entropy_heatmap (Task A-1, A-7)
    run_h_e1.py                  # copied + resume/reuse/anchor-gate patches (Task A-1, A-2, A-3)
    requirements.txt             # copied verbatim
    tests/
      test_data.py                    # copied verbatim (LIGHT tier: smoke coverage only)
      test_model_layout.py
      test_analysis.py
  results/
    cache_{model}_{dataset}.csv               # 6 files, 5+96 cols, one row/example (stability contract for h-m1/h-m3/h-c1)
    meta_{model}_{dataset}.json               # 6 files
    top1_agreement_{model}_{dataset}.npy      # 6 files
    test_split_locked_{model}_{dataset}.json  # 6 files, locked — never read by h-e1 analysis
    {model}_{dataset}_report.json             # 6 files, FR-5.1
  figures/
    gate_metrics_bar.png            # FR-5.2 (mandatory)
    auroc_heatmap.png               # FR-5.3
    auroc_vs_depth.png              # FR-5.4
    degeneracy_screen.png           # FR-5.5
    entropy_heatmap_llama2.png      # FR-5.6 (new)
  experiment_results.json     # overall MUST_WORK verdict (analyze_all output)
```

---

## Proposed Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Bootstrap codebase | Copy 6 v1 modules + tests/ + requirements.txt verbatim into `h-e1/code/`; verify `RESULTS_DIR`/`FIGURES_DIR` auto-resolve; confirm `HF_TOKEN` set and imports run | 6 | 2+1+1+2 |
| A-2 | Resume + cache-reuse patch | Add `resume_from_cache`, `verify_cache_reuse`; patch `run_sweep` for append-mode resume-by-example_id (FR-3.4/NFR-6) and donor-cache short-circuit for llama2/triviaqa (FR-3.5), incl. pending-split finalization on the copied donor cache | 13 | 3+3+3+4 |
| A-3 | A2 anchor pre-gate | Add `check_anchor_and_halt`; wire into `run_model`/`main` so llama2/triviaqa is checked first (cache-only, zero GPU) and each subsequent cell is checked immediately after its own sweep, halting before proceeding on tolerance breach (FR-4.1) | 11 | 2+3+2+4 |
| A-4 | Smoke test all models | Run unmodified `smoke_test` for llama2/mistral/llama3, SMOKE_N=10; assert 33 hidden states, finite signals, print peak memory (FR-3.6) | 4 | 1+1+1+1 |
| A-5 | Full sweep, remaining 5 cells | Run patched `run_model`/`run_sweep` for mistral x2, llama3 x2, llama2/truthfulqa (llama2/triviaqa short-circuited by A-2 reuse); 1,817 examples x models per NFR-5 | 10 | 2+3+2+3 |
| A-6 | Selection-split analysis | Run unmodified `degeneracy_screen` -> `build_auroc_grid` -> `evaluate_gate` -> `write_cell_report` -> `verify_mechanism_activated` per cell via `analyze_all`; write per-cell JSON reports (FR-4.2-4.5, FR-5.1) | 9 | 2+2+3+2 |
| A-7 | Figures | Run 4 unmodified `visualize.py` figures + add/run new `plot_entropy_heatmap` (FR-5.6); save all to `h-e1/figures/`, verify FR-5.2 gate-bar chart renders | 6 | 2+1+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-3, A-5, A-6], Low(4-8): [A-1, A-4, A-7]

**Dependency order**: A-1 -> A-2 -> A-3 -> A-4 -> A-5 -> A-6 -> A-7 (linear; A-4 smoke test gates A-5 full sweep per FR-3.6; A-3's per-cell halting is interleaved inside A-5's model loop, not a separate pass).
