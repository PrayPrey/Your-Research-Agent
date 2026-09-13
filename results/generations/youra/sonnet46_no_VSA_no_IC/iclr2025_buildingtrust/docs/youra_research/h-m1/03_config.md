# Config: H-M1
# Partial Spearman Correlation — BBQ Fairness Cross-Split Predictive Validity

**Date:** 2026-08-20
**Hypothesis Type:** MECHANISM (PoC statistical analysis)
**Applied:** Standard Python module-level constants (no neural hyperparameters)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: H-E1 actual config.py verified from `/docs/youra_research/h-e1/code/config.py`
**Config Files Found**: `h-e1/code/config.py`
**Pattern Used**: Module-level constants dict — matches H-E1 style (no dataclass needed, no training loop)

---

## Inherited Configuration (Base Hypothesis)

### Config Fields (Verified from H-E1 actual code)

```python
# From: h-e1/code/config.py (ACTUAL CODE — verified)
REQUIRED_COLS: list       # ["BBQ-Disambig", "BBQ-Ambig", "GLUE", "AdvGLUE", "ANLI-R1", "ANLI-R3", "MMLU"]
SOURCE_PRIORITY: list     # ["TrustLLM", "DecodingTrust", "GLUE-X", "OOD_NLP", "HF"]
BENCHMARK_PAIRS: list     # [("BBQ-Disambig","BBQ-Ambig"), ("GLUE","AdvGLUE"), ("ANLI-R1","ANLI-R3")]
N_COMMON_GATE: int        # 10
CANONICAL_MAP: dict       # ~40 alias → canonical model name entries
FIGURES_DIR: Path         # _HERE / "figures"
RESULTS_DIR: Path         # _HERE / "results"
```

H-M1 imports `CANONICAL_MAP` from H-E1 directly. It does **not** redefine it.

---

## A-7: Entry Point & Test [Complexity: 8, Budget: 1 subtask]

**Applied:** Standard argparse entry point + inline assert self-check

### config.py

```python
# h-m1/code/config.py
from pathlib import Path

# Gate thresholds (mechanism verification criteria)
GATE_RHO: float = 0.4
GATE_P: float = 0.05
N_COMMON_MIN: int = 10

# Analysis parameters
RANDOM_SEED: int = 1
ALTERNATIVE: str = "greater"  # one-tailed test

# Winogrande scores for sensitivity analysis (Open LLM Leaderboard)
WINOGRANDE_SCORES: dict[str, float] = {
    "LLaMA-2-7B":       0.674,
    "LLaMA-2-13B":      0.720,
    "LLaMA-2-70B":      0.783,
    "LLaMA-2-7B-Chat":  0.643,
    "LLaMA-2-13B-Chat": 0.699,
    "LLaMA-2-70B-Chat": 0.780,
    "Mistral-7B":       0.782,
    "Mistral-7B-Instruct": 0.747,
    "Falcon-7B":        0.662,
    "Falcon-40B":       0.823,
    "GPT-3.5-Turbo":    0.876,
    "GPT-4":            0.870,
    "Vicuna-13B":       0.702,
    "Alpaca-13B":       0.619,
}

# Paths
_HERE = Path(__file__).parent.parent
DATA_DIR = _HERE / "data"
FIGURES_DIR = _HERE / "figures"
RESULTS_DIR = _HERE / "results"
```

### run_experiment.py spec

```python
# h-m1/code/run_experiment.py
import argparse

def main() -> None:
    parser = argparse.ArgumentParser(description="H-M1: Partial Spearman BBQ analysis")
    parser.add_argument("--skip-figures", action="store_true", help="Skip figure generation")
    parser.add_argument("--dry-run", action="store_true", help="Self-check only (synthetic data)")
    args = parser.parse_args()

    if args.dry_run:
        _self_check()
        return

    from data import build_score_dataframe, verify_n_common
    from analysis import run_full_analysis
    from visualize import generate_all_figures

    df = build_score_dataframe()
    verify_n_common(df)
    results = run_full_analysis(df)
    if not args.skip_figures:
        from config import FIGURES_DIR
        generate_all_figures(df, results, FIGURES_DIR)

    status = "PASS" if results["gate_pass"] else "FAIL"
    print(f"Gate: {status} | partial_rho={results['partial_rho']:.3f} | p={results['p_value']:.4f}")


def _self_check() -> None:
    """Synthetic 5-row DataFrame self-check — verifies analysis pipeline runs end-to-end."""
    import pandas as pd
    from analysis import compute_raw_spearman, compute_partial_spearman, evaluate_gate

    df = pd.DataFrame({
        "model_name":   ["A", "B", "C", "D", "E"],
        "bbq_disambig": [0.9, 0.8, 0.7, 0.6, 0.5],
        "bbq_ambig":    [0.85, 0.75, 0.65, 0.55, 0.45],
        "mmlu":         [0.80, 0.70, 0.60, 0.50, 0.40],
        "winogrande":   [0.82, 0.72, 0.62, 0.52, 0.42],
    })

    raw = compute_raw_spearman(df)
    assert "raw_rho" in raw and "raw_p" in raw
    assert raw["n"] == 5

    partial = compute_partial_spearman(df, covar="mmlu")
    assert "partial_rho" in partial and "p_value" in partial

    gate = evaluate_gate(partial["partial_rho"], partial["p_value"])
    assert isinstance(gate, bool)

    print("Self-check PASSED")


if __name__ == "__main__":
    main()
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Entry Point & Self-Check | Implement `main()` with argparse (`--dry-run`, `--skip-figures`), pipeline orchestration, and `_self_check()` with 5-row synthetic DataFrame asserting raw/partial Spearman and gate outputs |
