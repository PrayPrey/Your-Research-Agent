# H-M1 Logic: Cross-Benchmark Inversion Analysis

**Type**: MECHANISM (analysis-only, zero new training)
**Gate**: SHOULD_WORK
**Input**: H-E2 results; **Output**: `docs/youra_research/h-m1/results/h_m1_result.json`

---

## Codebase Analysis (Serena)

**Project Type**: existing_codebase (base hypothesis H-E2)
**Status**: API signatures verified from base code
**Analyzed Path**: `docs/youra_research/h-e2/code/`
**Relevant Symbols**:
- `load_results(results_csv)` — loads `all_results.csv` → `pd.DataFrame` with cols `[condition, seed, benchmark, pass1, n_problems]`
- `load_per_problem_results(results_dir)` — loads per-problem EvalPlus JSON → long DataFrame
- `_condition_from_filename(name)`, `_seed_from_filename(name)` — filename parsers

**Critical finding**: `all_results.csv` contains only `benchmark=humaneval` rows — no MBPP rows exist. MBPP+ evalplus re-evaluation is required before analysis (fallback path is mandatory, not optional).

---

## Data Schema

### Input: H-E2 `all_results.csv`

```
condition,seed,benchmark,pass1,n_problems
humaneval_only,42,humaneval,0.396,164
mbpp_only,42,humaneval,0.293,164
...
```

Columns: `condition` ∈ {humaneval_only, mbpp_only, leetcode_only, equal_mix}, `benchmark` ∈ {humaneval, mbpp}, `pass1` float, `seed` int.

**Note**: benchmark column uses `humaneval`/`mbpp` (not `humaneval_plus`/`mbpp_plus`). H-M1 treats these as the EvalPlus+ scores per H-E2 eval protocol (`Base+Extra`).

### Internal Key Schema

```python
# key: (condition: str, seed: int, benchmark: str) -> pass1: float
# benchmark values: 'humaneval' | 'mbpp'  (matches CSV, not 'humaneval_plus')
results: dict[tuple[str, int, str], float]
```

### Output: `h_m1_result.json`

```json
{
  "hypothesis": "H-M1",
  "success": true,
  "n_both_inverted": 1,
  "n_valid": 1,
  "threshold": 0.667,
  "seed_checks": [
    {
      "seed": 42,
      "valid": true,
      "he_on_he": 0.396,
      "mb_on_he": 0.293,
      "he_on_mb": 0.180,
      "mb_on_mb": 0.340,
      "inversion_he_plus": true,
      "inversion_mbpp_plus": true,
      "both_inverted": true
    }
  ],
  "missing_mbpp_seeds": [42, 123, 777],
  "gate": "SHOULD_WORK",
  "note": ""
}
```

---

## API Signatures

```python
# analysis_h_m1.py
import json
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

CONDITIONS = ["humaneval_only", "mbpp_only", "leetcode_only", "equal_mix"]
HE_SEEDS = [42, 123, 777]   # humaneval_only seeds present
MB_SEEDS = [42, 123, 777]   # mbpp_only seeds present
INVERSION_SEEDS = [42]      # seeds where BOTH conditions exist; seed 42 is confirmed shared
H_E2_RESULTS_CSV = "docs/youra_research/h-e2/results/all_results.csv"
H_E2_CHECKPOINTS = "docs/youra_research/h-e2/checkpoints"
H_E2_RESULTS_DIR = "docs/youra_research/h-e2/results"
OUT_DIR = "docs/youra_research/h-m1/results"
FIGURES_DIR = "docs/youra_research/h-m1/figures"


def load_h_e2_results(results_csv: str = H_E2_RESULTS_CSV) -> dict[tuple, float]:
    """Load CSV into {(condition, seed, benchmark): pass1}. Benchmark: 'humaneval'|'mbpp'."""
    df = pd.read_csv(results_csv)
    return {
        (row.condition, int(row.seed), row.benchmark): float(row.pass1)
        for row in df.itertuples()
    }


def run_evalplus_mbpp(checkpoint_dir: str, condition: str, seed: int) -> float | None:
    """Run evalplus CLI for MBPP on one checkpoint; return pass@1 or None on failure.

    checkpoint_dir: path to condition_<cond>_seed_<seed>/ folder
    Returns: float pass@1 (Base+Extra) or None if eval fails
    """
    samples_dir = Path(H_E2_RESULTS_DIR) / f"condition_{condition}_seed_{seed}_mbpp"
    samples_dir.mkdir(parents=True, exist_ok=True)
    samples_jsonl = samples_dir / "samples.jsonl"

    # Step 1: generate samples if not already present
    if not samples_jsonl.exists():
        gen_cmd = [
            "python", "-m", "evalplus.evaluate",
            "--model", checkpoint_dir,
            "--dataset", "mbpp",
            "--backend", "hf",
            "--greedy",
            "--root", str(samples_dir),
        ]
        result = subprocess.run(gen_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[WARN] evalplus failed for {condition} seed {seed}: {result.stderr[:200]}")
            return None

    # Step 2: parse pass@1 from evalplus stdout/result file
    eval_result_file = samples_dir / "eval_results.json"
    if eval_result_file.exists():
        data = json.loads(eval_result_file.read_text())
        return data.get("pass@1")

    # ponytail: fallback parse from stdout captured above; upgrade if evalplus changes output format
    for line in result.stdout.splitlines():
        if "pass@1" in line and "extra" in line.lower():
            try:
                return float(line.split("pass@1")[1].split(":")[1].strip().rstrip("}"))
            except Exception:
                pass
    return None


def ensure_mbpp_results(results: dict[tuple, float]) -> dict[tuple, float]:
    """Fill missing mbpp rows by running evalplus CLI on H-E2 checkpoints.

    Modifies results in-place; returns updated dict.
    """
    needs_eval = []
    for cond in CONDITIONS:
        seeds = _seeds_for_condition(cond)
        for seed in seeds:
            if (cond, seed, "mbpp") not in results:
                needs_eval.append((cond, seed))

    if not needs_eval:
        return results

    print(f"[H-M1] MBPP results missing for {len(needs_eval)} (condition, seed) pairs — running evalplus...")
    for cond, seed in needs_eval:
        ckpt = str(Path(H_E2_CHECKPOINTS) / f"condition_{cond}_seed_{seed}")
        if not Path(ckpt).exists():
            print(f"[WARN] Checkpoint missing: {ckpt} — skipping")
            continue
        pass1 = run_evalplus_mbpp(ckpt, cond, seed)
        if pass1 is not None:
            results[(cond, seed, "mbpp")] = pass1
            print(f"  {cond} seed {seed} MBPP pass@1 = {pass1:.4f}")
        else:
            print(f"  {cond} seed {seed} MBPP eval failed — will be excluded from inversion check")

    return results


def _seeds_for_condition(condition: str) -> list[int]:
    """Return seeds confirmed present for each condition (from H-E2 state)."""
    seed_map = {
        "humaneval_only": [42, 123, 777],
        "mbpp_only": [42, 123, 777],
        "leetcode_only": [42, 123, 777],
        "equal_mix": [42, 123, 777],
    }
    return seed_map.get(condition, [])


def check_inversion_per_seed(results: dict[tuple, float], seed: int) -> dict:
    """Check rank inversion for one seed. Returns validity dict."""
    he_on_he = results.get(("humaneval_only", seed, "humaneval"))
    mb_on_he = results.get(("mbpp_only", seed, "humaneval"))
    he_on_mb = results.get(("humaneval_only", seed, "mbpp"))
    mb_on_mb = results.get(("mbpp_only", seed, "mbpp"))

    if None in [he_on_he, mb_on_he, he_on_mb, mb_on_mb]:
        missing = [k for k, v in {
            "he_on_he": he_on_he, "mb_on_he": mb_on_he,
            "he_on_mb": he_on_mb, "mb_on_mb": mb_on_mb,
        }.items() if v is None]
        return {"valid": False, "seed": seed, "missing": missing}

    inversion_he = he_on_he > mb_on_he   # HE-only wins on HumanEval+
    inversion_mb = mb_on_mb > he_on_mb   # MBPP-only wins on MBPP+
    return {
        "valid": True,
        "seed": seed,
        "he_on_he": he_on_he,
        "mb_on_he": mb_on_he,
        "he_on_mb": he_on_mb,
        "mb_on_mb": mb_on_mb,
        "inversion_he_plus": inversion_he,
        "inversion_mbpp_plus": inversion_mb,
        "both_inverted": inversion_he and inversion_mb,
    }


def evaluate_h_m1_hypothesis(results: dict[tuple, float], seeds: list[int]) -> dict:
    """Test inversion across seeds. Success: n_both_inverted / n_valid >= 2/3."""
    seed_checks = [check_inversion_per_seed(results, s) for s in seeds]
    valid = [c for c in seed_checks if c["valid"]]
    n_both = sum(1 for c in valid if c["both_inverted"])

    if len(valid) < 2:
        # ponytail: only seed 42 is confirmed shared; if mbpp eval fails for other seeds,
        # success check degrades to 1 valid seed — report as limitation, don't raise
        note = f"Only {len(valid)} valid seed(s); <2 valid seeds weakens conclusion"
    else:
        note = ""

    threshold = 2 / 3
    success = (n_both / len(valid) >= threshold) if valid else False
    return {
        "hypothesis": "H-M1",
        "success": success,
        "n_both_inverted": n_both,
        "n_valid": len(valid),
        "threshold": threshold,
        "seed_checks": valid,
        "invalid_checks": [c for c in seed_checks if not c["valid"]],
        "gate": "SHOULD_WORK",
        "note": note,
    }
```

---

## Figure Generation

### Figure 1: 2x4 Transfer Heatmap

```python
def plot_transfer_heatmap(results: dict[tuple, float], out_dir: str) -> None:
    """2-row × 4-col heatmap: rows={HumanEval+, MBPP+}, cols=4 conditions, cell=mean pass@1."""
    rows = []
    for cond in CONDITIONS:
        seeds = _seeds_for_condition(cond)
        for bm in ["humaneval", "mbpp"]:
            vals = [results[(cond, s, bm)] for s in seeds if (cond, s, bm) in results]
            rows.append({"condition": cond, "benchmark": bm, "pass1": np.mean(vals) if vals else np.nan})
    df = pd.DataFrame(rows)
    pivot = df.pivot(index="benchmark", columns="condition", values="pass1")
    pivot = pivot.reindex(index=["humaneval", "mbpp"], columns=CONDITIONS)

    fig, ax = plt.subplots(figsize=(8, 3))
    sns.heatmap(pivot, annot=True, fmt=".3f", cmap="YlOrRd", vmin=0, vmax=0.6, ax=ax)
    ax.set_title("H-M1: Transfer Matrix — Training Source × Benchmark (mean pass@1)")
    ax.set_yticklabels(["HumanEval+", "MBPP+"], rotation=0)
    plt.tight_layout()
    path = Path(out_dir) / "transfer_heatmap.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")
```

### Figure 2: Per-Seed Strip Plot

```python
def plot_per_seed_strip(results: dict[tuple, float], seeds: list[int], out_dir: str) -> None:
    """One panel per seed: scatter rank of HE-only vs MBPP-only on each benchmark."""
    rows = []
    for seed in seeds:
        for cond in ["humaneval_only", "mbpp_only"]:
            for bm in ["humaneval", "mbpp"]:
                val = results.get((cond, seed, bm))
                if val is not None:
                    rows.append({"seed": seed, "condition": cond, "benchmark": bm, "pass1": val})
    if not rows:
        return
    df = pd.DataFrame(rows)

    n_seeds = len(seeds)
    fig, axes = plt.subplots(1, n_seeds, figsize=(5 * n_seeds, 4), sharey=False)
    if n_seeds == 1:
        axes = [axes]
    for ax, seed in zip(axes, seeds):
        sub = df[df["seed"] == seed]
        sns.stripplot(data=sub, x="benchmark", y="pass1", hue="condition", ax=ax,
                      dodge=True, jitter=False, size=10)
        ax.set_title(f"Seed {seed}")
        ax.set_xlabel("")
        ax.set_xticklabels(["HumanEval+", "MBPP+"])
    plt.suptitle("H-M1: Per-Seed Rank (HE-only vs MBPP-only)")
    plt.tight_layout()
    path = Path(out_dir) / "per_seed_strip.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")
```

### Figure 3: Delta Bar Chart

```python
def plot_delta_bars(results: dict[tuple, float], seeds: list[int], out_dir: str) -> None:
    """Bar chart: (HE-only − MBPP-only) pass@1 per benchmark, averaged over valid seeds.

    Inversion = positive bar on humaneval, negative bar on mbpp.
    """
    deltas = {"humaneval": [], "mbpp": []}
    for seed in seeds:
        for bm in ["humaneval", "mbpp"]:
            he = results.get(("humaneval_only", seed, bm))
            mb = results.get(("mbpp_only", seed, bm))
            if he is not None and mb is not None:
                deltas[bm].append(he - mb)

    bm_labels = ["HumanEval+", "MBPP+"]
    means = [np.mean(deltas["humaneval"]) if deltas["humaneval"] else 0,
             np.mean(deltas["mbpp"]) if deltas["mbpp"] else 0]
    colors = ["green" if m > 0 else "red" for m in means]

    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(bm_labels, means, color=colors, alpha=0.7)
    ax.axhline(0, color="black", lw=0.8)
    ax.set_ylabel("HE-only − MBPP-only (pass@1)")
    ax.set_title("H-M1: Transfer Asymmetry Delta\n(green=inversion direction)")
    plt.tight_layout()
    path = Path(out_dir) / "delta_bars.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")
```

---

## Main Entry Point

```python
def main():
    Path(OUT_DIR).mkdir(parents=True, exist_ok=True)
    Path(FIGURES_DIR).mkdir(parents=True, exist_ok=True)

    results = load_h_e2_results(H_E2_RESULTS_CSV)
    results = ensure_mbpp_results(results)   # fills missing MBPP via evalplus CLI

    # Inversion check uses only seeds where BOTH conditions (he_only + mbpp_only) have data
    candidate_seeds = [42, 123, 777]
    inversion_result = evaluate_h_m1_hypothesis(results, candidate_seeds)

    out_path = Path(OUT_DIR) / "h_m1_result.json"
    out_path.write_text(json.dumps(inversion_result, indent=2))
    print(f"Result: success={inversion_result['success']} "
          f"({inversion_result['n_both_inverted']}/{inversion_result['n_valid']} seeds)")

    valid_seeds = [c["seed"] for c in inversion_result["seed_checks"]]
    plot_transfer_heatmap(results, FIGURES_DIR)
    plot_per_seed_strip(results, valid_seeds or candidate_seeds, FIGURES_DIR)
    plot_delta_bars(results, valid_seeds or candidate_seeds, FIGURES_DIR)

    if not inversion_result["success"]:
        print("[H-M1] SHOULD_WORK gate: inversion pattern absent — logging as limitation.")
    return inversion_result


if __name__ == "__main__":
    result = main()
    assert isinstance(result["success"], bool)
    print("Self-check OK")
```

---

## Edge Cases

| Scenario | Handling |
|----------|----------|
| MBPP rows absent from CSV (current state) | `ensure_mbpp_results()` calls evalplus CLI per checkpoint |
| Checkpoint dir missing for a seed | Skip that seed; log warning |
| evalplus CLI fails / not installed | `run_evalplus_mbpp()` returns `None`; seed excluded |
| Fewer than 2 valid seeds | `note` field set; success computed on available seeds; gate still logs result |
| Only 1 shared seed (seed 42) | Success possible with 1/1 >= 2/3; note records limitation |
| Partial inversion (one direction only) | `both_inverted=False`; counted as non-supporting; reported in `seed_checks` |

---

## Subtasks

| ID | Subtask | Description |
|----|---------|-------------|
| L-M1-1 | load_and_ensure | `load_h_e2_results` + `ensure_mbpp_results` (evalplus fallback) |
| L-M1-2 | inversion_check | `check_inversion_per_seed` + `evaluate_h_m1_hypothesis` |
| L-M1-3 | figures | Three plot functions + save to FIGURES_DIR |
| L-M1-4 | main_and_output | `main()` orchestration + JSON write + self-check |
