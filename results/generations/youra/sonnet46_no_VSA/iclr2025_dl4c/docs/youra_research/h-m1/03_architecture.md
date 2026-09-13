# Architecture: H-M1 — Cross-Benchmark Rank Inversion Analysis

**Applied**: no relevant KB pattern (diffusion domain only, similarity < 0.48)

## Codebase Analysis (Serena)

**Project Type**: green-field (single analysis script, no prior code to extend)
**Status**: green-field - no code to analyze
**Analyzed Path**: N/A
**Findings**: H-E2 produced checkpoints and `fast_eval/*_mbpp/samples.jsonl` files; no reusable Python modules exist. MBPP+ pass@1 scores are absent from `all_results.csv` — the evalplus scoring step is required before analysis.

---

## Critical Data Status (Verified from Actual H-E2 Files)

| Data | Location | Status |
|------|----------|--------|
| HumanEval+ pass@1 | `h-e2/results/all_results.csv` | AVAILABLE (conditions x seeds) |
| MBPP+ raw solutions | `h-e2/results/fast_eval/*_mbpp/samples.jsonl` | AVAILABLE |
| MBPP+ pass@1 scores | — | MISSING — must run evalplus.evaluate |

The MBPP+ scoring step is **mandatory**, not optional. `samples.jsonl` files for all conditions and seeds exist but have not been scored.

**Available checkpoints** (relevant conditions only):
- `humaneval_only`: seeds 42, 123, 777
- `mbpp_only`: seeds 42, 123, 777

**Seeds used for inversion check** (both conditions must share the same seed):
- Seed 42: humaneval_only + mbpp_only (both available)
- Seed 123: humaneval_only + mbpp_only (both available)
- Seed 777: humaneval_only + mbpp_only (both available)
- All 3 seeds are valid candidates.

---

## File Structure

```
docs/youra_research/h-m1/
  code/
    analysis_h_m1.py      # single script: load + score + analyze + plot + report
  figures/
    heatmap_pass1.png
    per_seed_inversion.png
    delta_bar_chart.png
  h_m1_result.json
```

**Input paths** (read-only):
```
docs/youra_research/h-e2/results/all_results.csv
docs/youra_research/h-e2/results/fast_eval/{condition}_seed{seed}_mbpp/samples.jsonl
```

---

## Data Flow

```
all_results.csv
  └─> load HumanEval+ pass@1 per (condition, seed)
        |
fast_eval/*_mbpp/samples.jsonl
  └─> evalplus.evaluate (subprocess, CPU-only) -> mbpp_scores dict
        |
        v
  scores[(condition, seed, benchmark)] = pass@1
        |
        v
  check_inversion_per_seed(seed=42|123|777)
        |
        v
  evaluate_hypothesis() -> success bool + seed_checks
        |
        +-> h_m1_result.json
        +-> figures/ (heatmap, per-seed strip, delta bar)
```

---

## Module: `analysis_h_m1.py`

Single file. Five logical sections as top-level functions.

**Dependencies**: `pandas`, `matplotlib`, `subprocess`, `json`, `pathlib`

```python
# ---- Section 1: Constants ----
H_E2_RESULTS_CSV: str   # abs path to h-e2/results/all_results.csv
H_E2_FAST_EVAL_DIR: str # abs path to h-e2/results/fast_eval/
H_M1_OUT_DIR: str        # abs path to h-m1/
FIGURES_DIR: str         # abs path to h-m1/figures/
INVERSION_SEEDS: list[int]    # [42, 123, 777]
INVERSION_CONDITIONS: tuple   # ("humaneval_only", "mbpp_only")
ALL_CONDITIONS: list[str]     # all 4, for heatmap

# ---- Section 2: Data Loader ----
def load_humaneval_scores(csv_path: str) -> dict[tuple, float]:
    """
    Reads all_results.csv (columns: condition, seed, benchmark, pass1).
    Filters benchmark == 'humaneval' rows.
    Returns: {(condition, seed, 'humaneval_plus'): pass1}
    """
    ...

def score_mbpp_samples(fast_eval_dir: str, condition: str, seed: int) -> float | None:
    """
    Runs: python -m evalplus.evaluate --dataset mbpp
          --samples {fast_eval_dir}/{condition}_seed{seed}_mbpp/samples.jsonl
    Parses stdout for 'Base + Extra' line -> float.
    Returns None if samples file missing or evalplus call fails.
    """
    ...

def build_score_table(csv_path: str, fast_eval_dir: str,
                      conditions: list[str], seeds: list[int]
                      ) -> dict[tuple, float | None]:
    """
    Merges HumanEval+ scores (from CSV) and MBPP+ scores (from evalplus subprocess).
    Returns: {(condition, seed, benchmark): float | None}
      benchmark in {'humaneval_plus', 'mbpp_plus'}
    Prints warning for each None cell.
    """
    ...

# ---- Section 3: Inversion Checker ----
def check_inversion_per_seed(scores: dict, seed: int) -> dict:
    """
    Reads 4 cells from scores for the given seed:
      (humaneval_only, seed, humaneval_plus)  -> he_on_he
      (mbpp_only,      seed, humaneval_plus)  -> mb_on_he
      (humaneval_only, seed, mbpp_plus)       -> he_on_mb
      (mbpp_only,      seed, mbpp_plus)       -> mb_on_mb
    Returns:
      {
        'seed': int,
        'valid': bool,
        'missing': list[str],
        'he_on_he': float | None,
        'mb_on_he': float | None,
        'he_on_mb': float | None,
        'mb_on_mb': float | None,
        'inversion_he_plus': bool | None,   # he_on_he > mb_on_he
        'inversion_mbpp_plus': bool | None, # mb_on_mb > he_on_mb
        'both_inverted': bool,
      }
    """
    ...

def evaluate_hypothesis(seed_checks: list[dict]) -> dict:
    """
    Returns:
      {
        'hypothesis_supported': bool,   # n_both_inverted / n_valid >= 2/3
        'n_valid': int,
        'n_both_inverted': int,
        'fraction_inverted': float,
        'seed_checks': list[dict],
      }
    """
    ...

# ---- Section 4: Figure Generator ----
def plot_heatmap(scores: dict, all_conditions: list[str], out_path: str) -> None:
    """
    2x4 heatmap: rows=[HumanEval+, MBPP+], cols=all_conditions.
    Cell = mean pass@1 across seeds (None cells shown as gray / NaN).
    Saves PNG to out_path.
    """
    ...

def plot_per_seed_inversion(seed_checks: list[dict], out_path: str) -> None:
    """
    One panel per seed. Each panel: grouped bars for he_only vs mb_only
    on HumanEval+ and MBPP+. Skips panels where valid=False.
    Saves PNG to out_path.
    """
    ...

def plot_delta_bar(seed_checks: list[dict], out_path: str) -> None:
    """
    Per-benchmark delta (he_only - mb_only) pass@1, one bar per seed.
    HumanEval+ expected positive, MBPP+ expected negative if inversion holds.
    Saves PNG to out_path.
    """
    ...

# ---- Section 5: Reporter + Orchestrator ----
def save_result(hypothesis_result: dict, scores: dict, out_path: str) -> None:
    """Serializes hypothesis_result + scores to h_m1_result.json."""
    ...

def main() -> None:
    """
    1. build_score_table (loads CSV + runs evalplus subprocesses for MBPP+)
    2. [check_inversion_per_seed for each seed] -> seed_checks
    3. evaluate_hypothesis(seed_checks)
    4. plot_heatmap, plot_per_seed_inversion, plot_delta_bar
    5. save_result
    Exits 0 always (SHOULD_WORK gate — failure is logged, not raised).
    """
    ...
```

---

## Output Schema: `h_m1_result.json`

```json
{
  "hypothesis": "H-M1",
  "hypothesis_supported": true,
  "gate": "SHOULD_WORK",
  "n_valid_seeds": 3,
  "n_both_inverted": 2,
  "fraction_inverted": 0.667,
  "scores": {
    "humaneval_only": {
      "42":  {"humaneval_plus": 0.396, "mbpp_plus": 0.312},
      "123": {"humaneval_plus": 0.256, "mbpp_plus": 0.298},
      "777": {"humaneval_plus": 0.396, "mbpp_plus": 0.305}
    },
    "mbpp_only": {
      "42":  {"humaneval_plus": 0.293, "mbpp_plus": 0.381},
      "123": {"humaneval_plus": 0.274, "mbpp_plus": 0.369},
      "777": {"humaneval_plus": 0.262, "mbpp_plus": 0.374}
    }
  },
  "seed_checks": [
    {
      "seed": 42,
      "valid": true,
      "missing": [],
      "he_on_he": 0.396, "mb_on_he": 0.293,
      "he_on_mb": 0.312, "mb_on_mb": 0.381,
      "inversion_he_plus": true,
      "inversion_mbpp_plus": true,
      "both_inverted": true
    }
  ],
  "figures": [
    "figures/heatmap_pass1.png",
    "figures/per_seed_inversion.png",
    "figures/delta_bar_chart.png"
  ],
  "notes": ""
}
```

---

## Fallback Path: MBPP+ Scoring

MBPP+ raw solutions already exist in `fast_eval/`. `score_mbpp_samples()` runs evalplus as a subprocess against these files. No GPU or model loading required — evalplus scoring is pure Python test execution against pre-generated solutions.

Files consumed by the fallback (all present in H-E2 outputs):
```
fast_eval/humaneval_only_seed42_mbpp/samples.jsonl
fast_eval/humaneval_only_seed123_mbpp/samples.jsonl
fast_eval/humaneval_only_seed777_mbpp/samples.jsonl
fast_eval/mbpp_only_seed42_mbpp/samples.jsonl
fast_eval/mbpp_only_seed123_mbpp/samples.jsonl
fast_eval/mbpp_only_seed777_mbpp/samples.jsonl
```

If any file is missing, that seed is marked `valid=False` and excluded from the inversion count.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup | Create output dirs, verify input paths exist | 4 | 1+1+1+1 |
| A-2 | Load HumanEval+ scores | Parse `all_results.csv` into score dict | 5 | 1+2+1+1 |
| A-3 | Score MBPP+ via evalplus | Subprocess evalplus on all 6 `_mbpp/samples.jsonl`, parse stdout | 8 | 2+2+2+2 |
| A-4 | Inversion checker | `check_inversion_per_seed` x3 + `evaluate_hypothesis` | 7 | 2+2+2+1 |
| A-5 | Figure generation | heatmap + per-seed strip + delta bar | 9 | 3+3+2+1 |
| A-6 | Report + orchestration | `save_result`, `main`, error handling | 5 | 1+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-5], Low(4-8): [A-1, A-2, A-3, A-4, A-6]
