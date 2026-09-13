# Logic: h-e1-v2
## Scale-Dependent Optimal Curation — Existence Test (Scope-Reduced)

Applied: config-override pattern (EXISTENCE tier)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (incremental from h-e1)
**Status**: API signatures verified from actual h-e1 code
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Relevant Symbols**:
- `analyze.py`: `gate_check`, `check_direction`, `run_ancova_interaction`, `run_full_analysis`
- `curate.py`: `get_corpus_stream`, `curate_all_variants`, `VARIANTS`
- `orchestrate.py`: `run_pipeline(stage, resume)`

---

## External Dependencies API

### Verified from `docs/youra_research/h-e1/code/` (actual code)

```python
# analyze.py
def check_direction(df: pd.DataFrame, dv: str = "mmlu_4shot") -> dict:
    # returns: {"tau_star_70m": int, "tau_star_160m": int, "direction_confirmed": bool}
    ...

def gate_check(analysis_results: dict) -> dict:
    # reads: "interaction_p", "interaction_eta2", "direction_confirmed"
    # checks: p<threshold AND eta2>=threshold AND direction
    # returns: {"passed": bool, "reason": str, "checks": dict, ...}
    ...

def run_full_analysis(csv_path: str) -> dict:
    # loads csv, runs ANCOVA + check_direction + gate_check
    # returns merged dict with "gate" key
    ...

# curate.py
def get_corpus_stream(corpus_name: str):
    # "fineweb" → load_dataset("HuggingFaceFW/fineweb", split="train", streaming=True)
    # already supports "fineweb" — no change needed
    ...

def curate_all_variants(corpus_name: str, base_stream, output_root: str) -> list:
    # iterates VARIANTS (module-level list of {ppl_threshold, dedup_j} dicts)
    # calls get_corpus_stream(corpus_name) internally per variant
    # returns list of variant_metadata dicts with keys:
    #   condition, corpus, ppl_threshold, dedup_j, output_path,
    #   token_count, ppl_retained, ppl_total, dedup_retained, dedup_total
    ...

# orchestrate.py
def run_pipeline(stage: str = "all", resume: bool = True) -> None:
    # passes CONFIG (global) to each stage
    # curate stage calls: curate_all_variants("dolma", ...) + curate_all_variants("fineweb", ...)
    ...
```

---

## L-1: Direction-based gate_check_v2() (for A-5)

**Applied**: Standard Python — patch existing function, no new module

### Actual h-e1 gate_check() checks (lines 99-131 of analyze.py):
1. `p < CONFIG.significance_threshold` (ANCOVA p-value)
2. `eta2 >= CONFIG.effect_size_threshold` (effect size)
3. `direction_confirmed` (tau*(70M) < tau*(160M))

### h-e1-v2 gate_check_v2() — direction + above-random only:

```python
def gate_check_v2(analysis_results: dict) -> dict:
    """Direction-based gate for EXISTENCE PoC. No ANCOVA required."""
    direction = analysis_results.get("direction_confirmed", False)
    above_random = analysis_results.get("above_random", False)
    interaction_exists = analysis_results.get("interaction_exists", False)

    checks = {
        "direction_passes": direction,                      # tau*(14M) <= tau*(31M)
        "above_random": above_random,                       # all acc_norm > 0.25
        "interaction_exists": interaction_exists,           # direction signal present
    }
    passed = checks["direction_passes"] and checks["above_random"] and checks["interaction_exists"]

    tau14 = analysis_results.get("tau_star_14m", "?")
    tau31 = analysis_results.get("tau_star_31m", "?")
    reason_parts = []
    if not checks["direction_passes"]:
        reason_parts.append(f"direction FAILED: tau*(14M)={tau14} > tau*(31M)={tau31}")
    if not checks["above_random"]:
        reason_parts.append("some conditions below random (acc_norm <= 0.25)")
    if not checks["interaction_exists"]:
        reason_parts.append("no interaction signal detected")

    return {
        "passed": passed,
        "reason": "PASS" if passed else "FAIL: " + "; ".join(reason_parts),
        "checks": checks,
        "tau_star_14m": tau14,
        "tau_star_31m": tau31,
        "direction_confirmed": direction,
    }
```

### check_direction_v2() — updated scale keys (14M/31M instead of 70M/160M):

```python
def check_direction_v2(df: pd.DataFrame, dv: str = "hellaswag_acc_norm") -> dict:
    """Compute tau*(14M) and tau*(31M) via argmax. direction_confirmed = tau*(14M) <= tau*(31M)."""
    df14 = df[df["scale"] == 14]
    df31 = df[df["scale"] == 31]
    tau_star_14m = df14.groupby("ppl_threshold")[dv].mean().idxmax()
    tau_star_31m = df31.groupby("ppl_threshold")[dv].mean().idxmax()
    # Note: <= (not strict <) per PRD gate definition
    direction_confirmed = bool(tau_star_14m <= tau_star_31m)

    results_14m = df14.groupby("ppl_threshold")[dv].mean().to_dict()  # {20: float, 35: float, 50: float}
    results_31m = df31.groupby("ppl_threshold")[dv].mean().to_dict()
    interaction_exists = (
        results_14m.get(20, 0) > results_14m.get(50, 0)   # 14M benefits from stricter filtering
        or results_31m.get(50, 0) >= results_31m.get(20, 0)  # 31M tolerates looser filtering
    )
    all_vals = list(results_14m.values()) + list(results_31m.values())
    above_random = all(v > 0.25 for v in all_vals) if all_vals else False

    return {
        "tau_star_14m": int(tau_star_14m),
        "tau_star_31m": int(tau_star_31m),
        "direction_confirmed": direction_confirmed,
        "interaction_exists": interaction_exists,
        "above_random": above_random,
        "results_14m": results_14m,
        "results_31m": results_31m,
    }
```

### run_full_analysis_v2() — drop ANCOVA, use check_direction_v2:

```python
def run_full_analysis_v2(csv_path: str) -> dict:
    """Direction-only analysis for h-e1-v2. No ANCOVA."""
    df = load_results(csv_path)          # reuse h-e1 load_results unchanged
    direction = check_direction_v2(df, dv="hellaswag_acc_norm")
    gate = gate_check_v2(direction)
    full_results = {**direction, "gate": gate}
    print(f"\n{'='*60}")
    print(f"GATE CHECK RESULT: {'PASS' if gate['passed'] else 'FAIL'}")
    print(f"  tau*(14M)={direction['tau_star_14m']}, tau*(31M)={direction['tau_star_31m']}")
    print(f"  direction: {'confirmed' if direction['direction_confirmed'] else 'NOT confirmed'}")
    print(f"  above_random: {direction['above_random']}")
    print(f"  interaction_exists: {direction['interaction_exists']}")
    print(f"  reason: {gate['reason']}")
    print(f"{'='*60}\n")
    return full_results
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Patch analyze.py | Add check_direction_v2, gate_check_v2, run_full_analysis_v2 to h-e1-v2/code/analyze_v2.py |

---

## L-2: FineWeb Streaming Corpus Pipeline (for A-2)

**Applied**: Standard Python — `get_corpus_stream` already handles "fineweb"; patch `curate_all_variants` for token budget enforcement

### Key findings from actual code:
- `get_corpus_stream("fineweb")` already calls `load_dataset("HuggingFaceFW/fineweb", split="train", streaming=True)` — no change needed
- `curate_all_variants(corpus_name, base_stream, output_root)` iterates module-level `VARIANTS` list
- Token count enforcement is NOT in h-e1 — must add repeat-sampling logic

### pad_to_token_budget() — new helper:

```python
def pad_to_token_budget(
    docs: list[dict],
    target_tokens: int,              # 1_000_000_000
    token_key: str = "text",
    seed: int = 1,
) -> list[dict]:
    """Repeat-sample docs (circular) until target_tokens reached. In-place."""
    import random
    rng = random.Random(seed)
    current = sum(len(d[token_key].split()) * 4 // 3 for d in docs)  # approx token count
    # ponytail: word-based token estimate, replace with tokenizer if off >10%
    if current >= target_tokens:
        return docs
    pool = docs[:]
    rng.shuffle(pool)
    idx = 0
    while current < target_tokens:
        doc = pool[idx % len(pool)]
        docs.append(doc)
        current += len(doc[token_key].split()) * 4 // 3
        idx += 1
    return docs
```

### curate_all_variants_v2() — adds token budget enforcement:

```python
def curate_all_variants_v2(
    corpus_name: str,               # "fineweb"
    output_root: str,
    target_tokens: int = 1_000_000_000,
    seeds: list[int] = [1, 2],
) -> list[dict]:
    """Produce 6 filtered+deduped variants, each padded to target_tokens.
    Returns list of variant_metadata dicts (same schema as h-e1).
    """
    # 1. stream = get_corpus_stream(corpus_name)
    # 2. for each variant in VARIANTS:
    #    a. score_and_filter_ppl(stream, tau, ppl_dir)
    #    b. apply_minhash_dedup(ppl_dir, j, dedup_dir, cache_dir)
    #    c. if token_count < target_tokens: pad_to_token_budget(docs, target_tokens, seed=seeds[0])
    #    d. write meta.json, touch _SUCCESS
    # 3. return results
    ...
```

### Pseudo-code for token enforcement:

```
for each variant (tau, J):
    filtered_docs = score_and_filter_ppl(stream, tau)
    deduped_docs  = apply_minhash_dedup(filtered_docs, J)
    token_count   = count_tokens(deduped_docs)
    if token_count < 1B:
        deduped_docs = pad_to_token_budget(deduped_docs, 1B, seed=1)
    write(deduped_docs, dedup_dir)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Add pad_to_token_budget + curate_all_variants_v2 | New functions in h-e1-v2/code/curate_v2.py; call from run_experiment.py |

---

## L-3: Parallel Experiment Runner (for A-6)

**Applied**: Standard Python — thin wrapper over h-e1 `run_pipeline`, pass CONFIG_V2

### Actual h-e1 orchestration entry point (orchestrate.py):
- `run_pipeline(stage: str = "all", resume: bool = True) -> None`
- Uses global `CONFIG` (imported at module top)
- Stage "curate" runs both dolma + fineweb; h-e1-v2 only needs fineweb

### run_experiment_v2() — config injection + fineweb-only curation:

```python
# h-e1-v2/code/run_experiment.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../h-e1/code"))

import analyze as _analyze_base
import curate as _curate_base
import orchestrate as _orch

from config_v2 import CONFIG_V2
from curate_v2 import curate_all_variants_v2
from analyze_v2 import run_full_analysis_v2

def run_experiment_v2(cfg=CONFIG_V2, stage: str = "all", resume: bool = True) -> dict:
    """24-run experiment: 2 scales × 6 conditions × 2 seeds.
    Monkey-patches CONFIG in h-e1 modules before calling run_pipeline.
    """
    # Inject CONFIG_V2 into h-e1 module globals
    import config as _cfg_mod
    _cfg_mod.CONFIG = cfg
    _analyze_base.CONFIG = cfg

    state_file = os.path.join(cfg.checkpoint_root, ".pipeline_state.json")

    # Override curate stage to use fineweb-only + token budget enforcement
    if stage in ("all", "curate"):
        _run_curate_stage(cfg)

    # Remaining stages delegate to h-e1 run_pipeline
    remaining = {"preprocess", "train", "evaluate", "visualize"} - {"curate"}
    for s in ["preprocess", "train", "evaluate", "visualize"]:
        if stage in ("all", s):
            _orch.run_pipeline(stage=s, resume=resume)

    # Analysis: use direction-based v2
    if stage in ("all", "analyze"):
        return run_full_analysis_v2(cfg.results_csv)

    return {}


def _run_curate_stage(cfg) -> None:
    """Curate fineweb only (not dolma) with token budget enforcement."""
    from curate import log_corpus_stats
    variants = curate_all_variants_v2(
        corpus_name="fineweb",
        output_root=cfg.corpus_root,
        target_tokens=cfg.total_tokens,   # 1_000_000_000
        seeds=cfg.seeds,                   # [1, 2]
    )
    log_corpus_stats(variants)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--stage", default="all")
    p.add_argument("--no-resume", action="store_true")
    args = p.parse_args()
    run_experiment_v2(stage=args.stage, resume=not args.no_resume)
```

### 24-run structure (handled by h-e1 train.py via CONFIG_V2):

```
scales = [14, 31]                    # 2 model scales
conditions = VARIANTS                # 6 {ppl_threshold, dedup_j} combos
seeds = [1, 2]                       # 2 seeds
total_runs = 2 × 6 × 2 = 24

for scale in scales:
    for variant in conditions:       # tau∈{20,35,50} × J∈{0.7,0.9}
        for seed in seeds:
            run_id = f"{scale}M_ppl{tau}_j{j}_seed{seed}"
            train(scale, variant, seed)        # ~500 steps, 1B tokens
            evaluate(run_id, ["hellaswag"])    # 10,003 examples, acc_norm
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | run_experiment_v2 entry point | h-e1-v2/code/run_experiment.py with CONFIG_V2 injection and fineweb-only curate stage |

---

## Summary: Files to Create

| File | Purpose | h-e1 Reuse |
|------|---------|------------|
| `h-e1-v2/code/config_v2.py` | CONFIG_V2 dataclass override | `dataclasses.replace(ExperimentConfig(), ...)` |
| `h-e1-v2/code/curate_v2.py` | `pad_to_token_budget`, `curate_all_variants_v2` | wraps h-e1 curate functions |
| `h-e1-v2/code/analyze_v2.py` | `check_direction_v2`, `gate_check_v2`, `run_full_analysis_v2` | wraps h-e1 `load_results` |
| `h-e1-v2/code/run_experiment.py` | `run_experiment_v2` entry point | delegates to h-e1 `run_pipeline` per stage |
