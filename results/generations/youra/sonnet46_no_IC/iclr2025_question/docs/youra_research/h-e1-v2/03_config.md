# Config: h-e1-v2 — A2-v2 Analysis + Gate Verdict (D-6 delta)

**Hypothesis Type**: EXISTENCE (PoC) | **Tier**: LIGHT — hardcoded module constants, no dataclass/YAML
**Date**: 2026-08-05
**Scope**: D-6 "Analysis + gate verdict" (complexity 9) only, per task allocation — 2 subtasks.

Applied: none — Archon KB out-of-domain (null result). Query `"DL config patterns"` (match_count=3): top hits `CompVis/latent-diffusion` README, `torch/_inductor/config.py`, JAX/libtpu release notes (source `8b1c7f40739544a6`, similarity ≤ 0.35). Zero relevance to experiment-config/dataclass patterns for interpretability sweeps. Identical null finding to h-e1's own 03_config.md and h-e1-v2's 03_architecture.md/02c_experiment_brief.md. Config below follows the v1/h-e1 hardcoded-module-constants style (NFR-4 LIGHT tier), consistent with `constants.py`'s existing format.

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1, protocol-identical prior episode; D-6 reads its patched `constants.py`/`analysis.py`/`run_h_e1.py` symbols)
**Status**: Serena MCP tool not present in this agent's toolset for this run — verified equivalently via direct `Read` of the full actual source files (not specs): `h-e1/code/constants.py` (44 lines, all constants), `h-e1/code/run_h_e1.py` (442 lines, full `analyze_all`/`check_anchor_and_halt`/`CACHE_FIELDS`/`DONOR_CACHE_LLAMA2_TRIVIAQA` bodies), `h-e1/code/analysis.py` (122 lines, full `evaluate_gate`/`verify_mechanism_activated`/`write_cell_report`/`check_baseline_anchor` bodies). Field names and defaults below are transcribed from these files, not from `h-e1/03_config.md` prose.
**Config Files Found**: `h-e1/code/constants.py` (module-level hardcoded constants, no dataclass, no dict-of-config wrapper)
**Pattern Used**: Hardcoded module constants — this doc follows the same format (Format Selection rule: hardcoded constants only, no dataclass introduced).

---

## Inherited Configuration (Base Hypothesis h-e1)

### Verified from `h-e1/code/constants.py` (actual code, unchanged by v2 except the 1 addition in D-6.1)

```python
SEED = 42
MODEL_IDS = {
    "llama2": "meta-llama/Llama-2-7b-hf",
    "mistral": "mistralai/Mistral-7B-v0.1",
    "llama3": "meta-llama/Meta-Llama-3-8B-Instruct",
}
N_LAYERS = 32
EXPECTED_HIDDEN_STATES = 33
MAX_NEW_TOKENS = 32
DEGENERACY_ENTROPY_PCT = 0.01
DEGENERACY_AGREEMENT_MIN = 0.05
AUROC_GATE = 0.55
BASELINE_TOLERANCE = 0.03          # dead in v2 run path, D-6.1 verifies non-use
H_E1_REFERENCES = {                # dead in v2 run path, D-6.1 verifies non-use
    ("llama2", "triviaqa"): 0.5186, ("llama2", "truthfulqa"): 0.5153,
    ("mistral", "triviaqa"): 0.5268, ("mistral", "truthfulqa"): 0.5886,
    ("llama3", "triviaqa"): 0.6583, ("llama3", "truthfulqa"): 0.6161,
}
RESULTS_DIR = str(_H_E1_ROOT / "results")   # auto-resolves to h-e1-v2/results after copy
FIGURES_DIR = str(_H_E1_ROOT / "figures")   # auto-resolves to h-e1-v2/figures after copy
SMOKE_N = 10
TRIVIAQA_N = 1000
TRUTHFULQA_N = 817
HF_TOKEN = os.environ.get("HF_TOKEN")       # RuntimeError at import time if unset
```

### Verified from `h-e1/code/run_h_e1.py` (actual code — D-6 reads these)

```python
CACHE_FIELDS = (["example_id", "dataset", "model", "split", "label"]
    + [f"entropy_L{i}" for i in range(1, 33)]
    + [f"maxprob_L{i}" for i in range(1, 33)]
    + [f"adj_kl_L{i}" for i in range(1, 33)])          # 5 + 96 = 101 cols
LOADERS = {"triviaqa": load_triviaqa, "truthfulqa": load_truthfulqa}   # dict order = cell iteration order
```

### Verified from `h-e1/code/analysis.py` (actual code — D-6 calls these unchanged)

```python
SIGNALS = ["entropy", "maxprob", "adj_kl"]
# evaluate_gate(auroc_grid, retained_layers) -> dict with keys:
#   best_layer: int|None, best_signal: str|None, best_auroc: float,
#   gate_pass: bool, final_layer_entropy_auroc: float, depth_beats_final: bool|None
# write_cell_report(model_key, dataset_name, auroc_grid, retained_layers, counts) -> dict (report schema, D-6.2)
```

**Verified from**: `h-e1/code/{constants.py,run_h_e1.py,analysis.py}` (actual implementation, Read directly).

---

## D-6.1: Constants delta — V1_DIRECTION_RECORD + gating-path removal verification [Complexity: ~4-5, Budget: 2 (shared w/ D-6.2 within D-6's 9)]

**Applied**: Standard Python module-constant pattern (matches `constants.py`'s existing style) — no KB pattern relevant.

### Configuration (Hardcoded dict, added to `constants.py`)

```python
# NEW constant (architecture: "constants.py — verbatim + 1 new constant").
# (model_key, dataset) -> v1 Phase-4-record final-layer entropy "flipped" direction
# bool, same convention as analysis.corrected_auroc()'s 2nd return value.
# Descriptive input to clause-(c) only -- NEVER read by any gate/halt branch.
V1_DIRECTION_RECORD: dict[tuple[str, str], bool] = {
    ("llama2", "triviaqa"): True,     # weak/near-chance in v1 record (0.5186) -> treated as inverted
    ("llama2", "truthfulqa"): True,   # weak/near-chance in v1 record (0.5153) -> treated as inverted
    ("mistral", "triviaqa"): False,   # moderate (0.5268)
    ("mistral", "truthfulqa"): False, # moderate (0.5886)
    ("llama3", "triviaqa"): False,    # strongest, clearly non-inverted (0.6583)
    ("llama3", "truthfulqa"): False,  # strongest, clearly non-inverted (0.6161)
}
```

**Non-standard**: booleans are a best-available proxy derived from the qualitative v1-record descriptors in `02c_experiment_brief.md` ("llama2 final-layer weak/inverted, llama3 strongest") plus the archived `H_E1_REFERENCES` magnitudes (values near 0.5 -> `True`). No literal per-cell "flipped" bool exists in any prior artifact (v1's own Phase-4 run only reached 1/6 cells before halting). Since clause (c) is descriptive-only and never gates (FR-4.2, Success Criterion 5), an inaccurate value here cannot cause a false PASS/FAIL — Phase 4 may refine from the archived pre-h-e1 run log if it locates the raw `corrected_auroc` direction output, but is not required to.

### Retained thresholds (unchanged, verify present + imported only where allowed)

| Constant | Value | Allowed callers in v2 |
|---|---|---|
| `AUROC_GATE` | `0.55` | `analysis.evaluate_gate` only |
| `DEGENERACY_ENTROPY_PCT` | `0.01` | `analysis.degeneracy_screen` only |
| `DEGENERACY_AGREEMENT_MIN` | `0.05` | `analysis.degeneracy_screen` only |
| `H_E1_REFERENCES` | 6 entries (unchanged values) | `analysis.check_baseline_anchor` (now an orphaned/unused function in the run path) + `tests/test_analysis.py` ONLY |
| `BASELINE_TOLERANCE` | `0.03` | same as above — `check_baseline_anchor` + `tests/test_analysis.py` ONLY |

### Validation rules

1. `V1_DIRECTION_RECORD` has exactly 6 keys; keys == `{(m, d) for m in MODEL_IDS for d in LOADERS}` (no missing/extra cell).
2. All values are `bool` (not `None`, not numeric) — `check_anchor_and_halt`'s log line does `direction == v1` (bool equality); a missing key returns `None` from `.get(...)`, which is a valid "not established" state and must NOT raise.
3. Grep guard (belt-and-suspenders on the D-2 delta this subtask depends on): `H_E1_REFERENCES` must NOT appear inside `run_h_e1.check_anchor_and_halt` or inside `analysis.verify_mechanism_activated`'s returned `detail` dict keys (Gap A closure) — `grep -n "H_E1_REFERENCES" code/run_h_e1.py code/analysis.py` must show 0 hits outside `check_baseline_anchor`'s own body and any docstring/comment.
4. `BASELINE_TOLERANCE` must NOT appear inside `check_anchor_and_halt` (same grep pattern).

### Acceptance criteria

- [ ] `V1_DIRECTION_RECORD` importable from `constants.py`, 6/6 keys present, all-bool values.
- [ ] `check_anchor_and_halt` never raises `SystemExit` for any `final_auroc` value (validation rule 3 above holds transitively via D-2's re-spec; D-6.1 only re-confirms via grep before D-6.2's analysis run).
- [ ] `AUROC_GATE=0.55`, `DEGENERACY_ENTROPY_PCT=0.01`, `DEGENERACY_AGREEMENT_MIN=0.05` unchanged from h-e1 (byte-identical values, confirmed by the Inherited Configuration table above).
- [ ] `tests/test_analysis.py` (verbatim, unmodified) still passes — confirms `H_E1_REFERENCES`/`BASELINE_TOLERANCE` remain valid Python objects even though unused in the run path (NFR-7 "harmless dead constants").

### Subtasks [1/2 used]
| ID | Subtask | Description |
|----|---------|-------------|
| D-6.1-1 | Add + verify constants delta | Add `V1_DIRECTION_RECORD` (6-key dict above) to `constants.py`; run the grep guards (validation rules 3-4); confirm retained thresholds unchanged |

---

## D-6.2: experiment_results.json schema + MUST_WORK verdict + verify_v2_run_complete [Complexity: ~4-5, Budget: 1 (shared w/ D-6.1 within D-6's 9)]

**Applied**: stdlib `json`/`pathlib` only — no KB pattern relevant.

### Per-cell report schema (`write_cell_report`, unchanged, verified from `analysis.py:105-121`)

Written to `{RESULTS_DIR}/{model_key}_{dataset_name}_report.json`, 6 files:

```python
{
    "model": str, "dataset": str,
    "retained_layers": list[int],       # 1-indexed
    "dropped_layers": list[int],        # 1-indexed
    "signals": ["entropy", "maxprob", "adj_kl"],
    "auroc_grid": list[list[float | None]],   # NaN -> null (_nan_to_none)
    "positive_cases": int, "negative_cases": int,
    "gate": {"best_layer": int | None, "best_signal": str | None,
             "best_auroc": float | None, "gate_pass": bool,
             "final_layer_entropy_auroc": float | None,
             "depth_beats_final": bool | None},
}
```

### `experiment_results.json` schema (written by `analyze_all`, `Path(RESULTS_DIR).parent / "experiment_results.json"` = `h-e1-v2/experiment_results.json`)

```python
{
    "hypothesis_id": str,          # code literal is "h-e1" (verbatim analyze_all body,
                                    # architecture: 0 edits) -- NOT "h-e1-v2". Flag only,
                                    # do not patch: outside D-6 scope, cosmetic (path already
                                    # disambiguates h-e1 vs h-e1-v2), non-blocking for gate math.
    "gate_type": "MUST_WORK",
    "overall_pass": bool,          # all(per_model_pass.values())
    "per_model_pass": {"llama2": bool, "mistral": bool, "llama3": bool},
    "cells": {
        "{model}/{dataset}": {     # 6 keys required, e.g. "llama2/triviaqa"
            "gate": {...},         # same shape as per-cell report's "gate" above
            "mechanism": {"all_true": bool, "log_found": bool, "layer_dim_correct": bool,
                          "depth_variation": bool,
                          "anchor_computed": bool},   # D-2 renames baseline_reproduced -> anchor_computed (Gap A)
            "retained_layers": list[int],
        } for each of 6 cells
    },
    "figures": list[str],          # 4 paths from analyze_all's inline visualize.py calls
}
```

### MUST_WORK verdict aggregation config

```python
CELLS = [(m, d) for m in MODEL_IDS for d in LOADERS]   # 6, iteration order: model-major, dataset-minor
# per_model[m] = all(gate_results[f"{m}/{d}"]["gate_pass"] for d in LOADERS)
# overall = all(per_model.values())
```

### `verify_v2_run_complete` inputs (FR-4.7, Gap B — new function, distinct name from per-cell `verify_mechanism_activated`)

```python
def verify_v2_run_complete(experiment_log: str, results: dict) -> tuple[bool, dict]: ...
```

| Input | Type | Source | Notes |
|---|---|---|---|
| `experiment_log` | `str` | Concatenated stdout/log text across the FULL run (all cells) | NOT already assembled anywhere in v1 code — Phase 4 must capture it (e.g. accumulate `log.info`/`print` output to a string buffer, or read back the redirected stdout file written by `run_experiment.sh`) before calling this function at end of `analyze_all`/`main()` |
| `results` | `dict` | The `summary` dict already being built in `analyze_all` (same object about to be written to `experiment_results.json`) | Call after `summary` is fully constructed, before `results_path.write_text(...)` |

**Indicator dict** (5 keys, all must be `True` for `verify_v2_run_complete`'s first return value to be `True`):

| Key | Formula | Reads from |
|---|---|---|
| `reuse_verified` | `"verify_cache_reuse: 10 examples consistent" in experiment_log or "fresh generation" in experiment_log` | `experiment_log` |
| `anchor_reported` | `all(f"A2-v2 anchor: {c}" in experiment_log for c in results["cells"])` | `experiment_log`, `results["cells"]` keys |
| `grid_nondegenerate` | `all(r["gate"]["best_auroc"] != r["gate"]["final_layer_entropy_auroc"] for r in results["cells"].values())` | `results["cells"][c]["gate"]` |
| `screen_healthy` | `all(len(r["retained_layers"]) >= 5 for r in results["cells"].values())` | `results["cells"][c]["retained_layers"]` |
| `all_cells_measured` | `len(results["cells"]) == 6` | `results["cells"]` |

### Validation rules

1. `results["cells"]` must have exactly 6 keys before `verify_v2_run_complete` is called — call `all_cells_measured` will be `False` (not an exception) if fewer, per FR-4.6/Success Criterion 1 ("all 6 measured").
2. `per_model_pass` dict has exactly 3 keys (`llama2`, `mistral`, `llama3`), each `bool`.
3. `overall_pass` computed ONLY from `per_model_pass` (never short-circuited by `verify_v2_run_complete`'s result — the two verdicts are reported side by side, not merged; `verify_v2_run_complete` is a mechanism-activation check per FR-4.7, `overall_pass` is the MUST_WORK gate per FR-4.6).
4. Recommended integration point: `summary["verify_v2_run_complete"] = {"all_true": ok, **indicators}` before `results_path.write_text(...)` so the 5-indicator result is persisted alongside `overall_pass` (small, justified addition beyond verbatim `analyze_all`, per NFR-7 — required to satisfy FR-4.7's "called once at the end of analyze_all/main()").

### Acceptance criteria

- [ ] 6/6 `*_report.json` files written, one per cell, `gate` sub-schema matches table above.
- [ ] `experiment_results.json["cells"]` has exactly 6 keys, all of form `"{model}/{dataset}"` for `model in MODEL_IDS`, `dataset in LOADERS`.
- [ ] `overall_pass == all(per_model_pass.values())`, `per_model_pass[m] == all(gate_pass for d in LOADERS)`.
- [ ] `verify_v2_run_complete(experiment_log, summary)` returns `(True, {...5 True values...})` on a clean 6/6 run; any `False` indicator is individually inspectable in the returned detail dict (not just an aggregate bool).
- [ ] No `H_E1_REFERENCES` numeric value appears anywhere in `experiment_results.json` (Success Criterion 6 / NFR-7 literal reading).

### Subtasks [1/1 used — D-6 total 2/2]
| ID | Subtask | Description |
|----|---------|-------------|
| D-6.2-1 | Run analysis + write verdict | Run `analyze_all` (unmodified) across 6 cells; wire `verify_v2_run_complete(experiment_log, summary)` call before `experiment_results.json` write; verify schema + acceptance criteria above |

---

## Out of Scope (Not This Agent's Allocation)

`constants.py`'s `V1_DIRECTION_RECORD` addition and `analysis.py`'s `verify_mechanism_activated`/`verify_v2_run_complete` function bodies are implemented under Task D-2 (per `03_architecture.md` Proposed Tasks table); D-6 (this doc) only specifies the config VALUES those D-2 functions consume/produce and the aggregation config D-6's `analyze_all` run + verdict-write step needs. `check_anchor_and_halt`'s re-spec (D-2), the 6-cell sweep producing the input caches (D-5), and `generate_figures.py`'s 6-cell loop (D-7) are not covered here.
