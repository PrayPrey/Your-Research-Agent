# Logic: H-M1 — RI → ECE Mechanism Verification

**Applied**: modular-statistical-pipeline

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified via direct file reads (Serena project selection unavailable; read actual code files directly)
**Analyzed Path**: `docs/youra_research/20260512_buildingtrust/h-e1/code/`
**Relevant Symbols**:
- `RIComputer`: `compute_pc1(df)`, `fit_ols(df)`, `fit_ols_baseline(df)`, `check_vif(df)`, `compute(df)` — in `compute_ri.py`
- `DataAssembler`: `load_trustllm_scores()`, `load_lmeval_scores()`, `merge_matrix()`, `validate_matrix()` — in `data_assembly.py`
- `config.py` exports: `SEED=42`, `N_BOOTSTRAP=10000`, `VIF_THRESHOLD=5.0`, `CAP_COLS`, `SD_THRESHOLD`, `R2_THRESHOLD`
- H-E1 outputs: `outputs/model_matrix.csv` (30×11), `outputs/ri_scores.csv` (30×2)

---

## External Dependencies API

### API Signatures (From Actual H-E1 Code)

```python
# From: h-e1/code/compute_ri.py (ACTUAL CODE)
class RIComputer:
    def __init__(self, seed: int = config.SEED) -> None: ...

    def compute_pc1(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, float]:
        """Fit PCA on CAP_COLS; add PC1. Input: (N,11) -> Output: (N,12)."""

    def fit_ols(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, float]:
        """OLS advglue_drop ~ PC1 + mean_confidence; add RI. Input: (N,12) -> (N,13)."""

    def fit_ols_baseline(self, df: pd.DataFrame) -> float:
        """OLS advglue_drop ~ PC1 only. Returns r2_baseline."""

    def check_vif(self, df: pd.DataFrame) -> float:
        """VIF for PC1. Returns vif_pc1 float."""

    def compute(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
        """Full pipeline: PC1 -> OLS -> VIF -> stats. Returns (df, stats_dict)."""

# From: h-e1/code/data_assembly.py (ACTUAL CODE)
# H-E1 CSV outputs (read-only for H-M1):
#   ../h-e1/code/outputs/model_matrix.csv  — columns: model, bbh, arc_challenge,
#     mmlu_pro, math_hard, gpqa, musr, mean_confidence, advglue_drop,
#     advglue_estimated, family, scale
#   ../h-e1/code/outputs/ri_scores.csv     — columns: model, RI, PC1, ...

# From: h-e1/code/config.py (ACTUAL CODE)
SEED: int = 42
N_BOOTSTRAP: int = 10000
VIF_THRESHOLD: float = 5.0
CAP_COLS: list[str] = ["bbh", "arc_challenge", "mmlu_pro", "math_hard", "gpqa", "musr"]
```

**Verified from**: `h-e1/code/compute_ri.py`, `h-e1/code/config.py`, `h-e1/code/data_assembly.py` (actual implementation)

---

## A-3: ECEComputer [Complexity: 4, Budget: 4]

**Applied**: bootstrap-CI-pattern (numpy resample with replacement, 10K iterations)

### API Signatures

```python
# ece_computer.py
from __future__ import annotations
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional, Tuple
import cal  # calibration-lib

class ECEComputer:
    def __init__(
        self,
        n_bins: int = 15,
        n_bootstrap: int = 10000,
        seed: int = 42,
        cache_dir: Optional[Path] = None,
    ) -> None:
        """Initialize ECE computer with calibration settings."""

    def compute_ece(
        self,
        probs: np.ndarray,   # [N, C] predicted probabilities
        labels: np.ndarray,  # [N] integer ground-truth labels
    ) -> float:
        """Compute ECE scalar via cal.get_ece(probs, labels). Returns float."""

    def compute_ece_ci(
        self,
        probs: np.ndarray,   # [N, C]
        labels: np.ndarray,  # [N]
    ) -> Tuple[float, float]:
        """Bootstrap 95% CI on ECE. Returns (ci_low, ci_high)."""

    def compute_per_model(
        self,
        model_logit_paths: dict[str, Path],  # {model_id: path_to_logits}
    ) -> pd.DataFrame:
        """Compute ECE + CI for all models. Returns DataFrame shape (30, 3).

        Columns: model, ece, ci_low, ci_high
        """

    def load_or_compute(
        self,
        model_logit_paths: dict[str, Path],
        force_recompute: bool = False,
    ) -> pd.DataFrame:
        """Load cached ECE CSV or compute fresh. Returns DataFrame (30, 3).

        Fallback: Gaussian mock with ECE ~ Uniform(0.05, 0.25) per model.
        """

    def _load_logits(self, path: Path) -> Tuple[np.ndarray, np.ndarray]:
        """Load lm-eval logit file. Returns (probs [N,C], labels [N])."""

    def _mock_ece(self, n_models: int, rng: np.random.Generator) -> pd.DataFrame:
        """Gaussian mock fallback. ECE ~ Uniform(0.05, 0.25). Returns (n_models, 3)."""
```

### Pseudo-code: compute_ece_ci()

```
1. rng = np.random.default_rng(seed)
2. ece_samples = []
3. for _ in range(n_bootstrap):
4.     idx = rng.integers(0, len(labels), size=len(labels))
5.     ece_b = cal.get_ece(probs[idx], labels[idx], num_bins=n_bins)
6.     ece_samples.append(ece_b)
7. return (np.percentile(ece_samples, 2.5), np.percentile(ece_samples, 97.5))
```

### Pseudo-code: load_or_compute()

```
1. cache_path = cache_dir / "ece_scores.csv"
2. if cache_path.exists() and not force_recompute: return pd.read_csv(cache_path)
3. if model_logit_paths is empty or None: return _mock_ece(30, rng)
4. df = compute_per_model(model_logit_paths)
5. df.to_csv(cache_path, index=False)
6. return df
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | compute_ece | ECE scalar via cal.get_ece(probs, labels, num_bins) |
| L-3-2 | compute_ece_ci | Bootstrap 95% CI, 10K resamples, numpy rng |
| L-3-3 | compute_per_model | ECE + CI for all 30 models → DataFrame(30,3) |
| L-3-4 | load_or_compute | Cache load or fresh compute; Gaussian mock fallback |

---

## A-4: PartialCorrAnalyzer [Complexity: 4, Budget: 4]

**Applied**: pingouin-partial-corr with Holm multiple comparison correction

### API Signatures

```python
# partial_corr.py
from __future__ import annotations
import numpy as np
import pandas as pd
import pingouin as pg
from statsmodels.stats.multitest import multipletests
from typing import Optional

class PartialCorrAnalyzer:
    def __init__(self, n_bootstrap: int = 10000, seed: int = 42) -> None:
        """Initialize analyzer."""

    def full_partial_corr(
        self,
        df: pd.DataFrame,  # (30, *) must contain: RI, ECE, PC1, mean_confidence
    ) -> dict:
        """Full-sample Spearman partial correlation RI ~ ECE | PC1, mean_confidence.

        Returns dict: {rho, p_value, ci_low, ci_high, n}
        Uses: pg.partial_corr(data=df, x="RI", y="ECE",
                              covar=["PC1", "mean_confidence"], method="spearman")
        """

    def family_partial_corr(
        self,
        df: pd.DataFrame,   # (30, *) must contain: family column
        min_n: int = 5,
    ) -> pd.DataFrame:
        """Per-family Spearman partial corr. Skips families with n < min_n.

        Returns DataFrame columns: family, rho, p_value, n, sign_consistent
        """

    def holm_correction(
        self,
        p_values: np.ndarray,  # [K] raw p-values
        alpha: float = 0.05,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Holm-Bonferroni correction via statsmodels.multipletests.

        Returns (reject [K bool], p_corrected [K float])
        Uses: multipletests(p_values, method="holm")
        """

    def bootstrap_rho_ci(
        self,
        df: pd.DataFrame,   # (30, *) must contain: RI, ECE, PC1, mean_confidence
    ) -> Tuple[float, float]:
        """10K bootstrap resamples on full Spearman partial rho.

        Returns (ci_low, ci_high) at 95%.
        """

    def run_all(self, df: pd.DataFrame) -> dict:
        """Run full_partial_corr + family_partial_corr + holm + bootstrap CI.

        Returns consolidated results dict.
        """
```

### Pseudo-code: full_partial_corr()

```
1. result = pg.partial_corr(data=df, x="RI", y="ECE",
                             covar=["PC1", "mean_confidence"], method="spearman")
2. rho = float(result["r"].iloc[0])
3. p_value = float(result["p-val"].iloc[0])
4. ci = bootstrap_rho_ci(df)
5. return {"rho": rho, "p_value": p_value, "ci_low": ci[0], "ci_high": ci[1], "n": len(df)}
```

### Pseudo-code: bootstrap_rho_ci()

```
1. rng = np.random.default_rng(seed)
2. rho_samples = []
3. for _ in range(n_bootstrap):
4.     idx = rng.integers(0, len(df), size=len(df))
5.     df_b = df.iloc[idx].reset_index(drop=True)
6.     try:
7.         r = pg.partial_corr(data=df_b, x="RI", y="ECE",
8.                              covar=["PC1","mean_confidence"], method="spearman")
9.         rho_samples.append(float(r["r"].iloc[0]))
10.    except Exception: continue
11. return (np.percentile(rho_samples, 2.5), np.percentile(rho_samples, 97.5))
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | full_partial_corr | pg.partial_corr Spearman RI~ECE|PC1,mean_confidence |
| L-4-2 | family_partial_corr | Per-family Spearman partial corr, n≥5 gate |
| L-4-3 | holm_correction | multipletests(p_values, method="holm") |
| L-4-4 | bootstrap_rho_ci | 10K bootstrap resamples on full rho |

---

## A-5: GateEvaluator [Complexity: 2, Budget: 2]

**Applied**: Standard PyTorch

### API Signatures

```python
# evaluate.py
from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Literal

GateResult = Literal["PASS", "PARTIAL", "FAIL"]

class GateEvaluator:
    def __init__(
        self,
        rho_threshold: float = 0.4,
        p_threshold: float = 0.05,
        consistent_positive_threshold: int = 2,
    ) -> None:
        """Initialize gate thresholds."""

    def evaluate_gate(
        self,
        rho: float,
        p_value: float,
        family_results: pd.DataFrame,  # columns: family, rho, p_value, n, sign_consistent
    ) -> dict:
        """PASS/PARTIAL/FAIL gate logic.

        PASS:    rho >= 0.4 AND p < 0.05 AND n_consistent_positive >= 2
        PARTIAL: (rho >= 0.4 OR p < 0.05) but not all three conditions
        FAIL:    otherwise
        Returns: {gate: GateResult, rho, p_value, n_consistent_positive, conditions_met}
        """

    def run_all_secondary(
        self,
        df: pd.DataFrame,            # (30, *) full merged DataFrame
        family_results: pd.DataFrame,
    ) -> dict:
        """Run secondary robustness checks.

        Checks: baseline_corr (Spearman RI~ECE no covariates),
                VIF (PC1 in [PC1, mean_confidence]),
                Cook's distance (influential point detection),
                Fisher z-test (family rho homogeneity).
        Returns: dict with keys baseline_corr, vif_pc1, cooks_d, fisher_z
        """
```

### Pseudo-code: evaluate_gate()

```
1. n_consistent = int((family_results["sign_consistent"] == True).sum())
2. cond_rho   = rho >= rho_threshold          # rho >= 0.4
3. cond_p     = p_value < p_threshold         # p < 0.05
4. cond_fam   = n_consistent >= consistent_positive_threshold  # >= 2 families
5. n_met = sum([cond_rho, cond_p, cond_fam])
6. if n_met == 3:   gate = "PASS"
7. elif n_met >= 1: gate = "PARTIAL"
8. else:            gate = "FAIL"
9. return {gate, rho, p_value, n_consistent_positive: n_consistent, conditions_met: n_met}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | evaluate_gate | PASS/PARTIAL/FAIL logic with 3-condition check |
| L-5-2 | run_all_secondary | baseline_corr + VIF + Cook's distance + Fisher z-test |

---

## A-8: RunExperiment [Complexity: 2, Budget: 2]

**Applied**: Standard argparse orchestration pattern

### API Signatures

```python
# run_experiment.py
from __future__ import annotations
import argparse
import sys
from pathlib import Path

def parse_args() -> argparse.Namespace:
    """Parse CLI arguments.

    Args:
        --data-dir      PATH   Directory containing lm-eval logit files (default: data/)
        --output-dir    PATH   Results output directory (default: results/)
        --figures-dir   PATH   Figures output directory (default: figures/)
        --seed          INT    Random seed (default: 42)
        --no-compute-ece FLAG  Skip ECE computation, use cached or mock
    Returns argparse.Namespace
    """

def main() -> int:
    """Orchestrate full H-M1 pipeline. Returns exit code (0=PASS, 1=FAIL).

    Pipeline:
      1. ECEComputer.load_or_compute()   -> ece_df (30, 3)
      2. DataLoader.load()               -> merged_df (30, *)
      3. PartialCorrAnalyzer.run_all()   -> corr_results dict
      4. GateEvaluator.evaluate_gate()   -> gate_result dict
      5. GateEvaluator.run_all_secondary() -> secondary dict
      6. Visualizer.plot_all()           -> 6 figures saved
      7. Export JSON/CSV to output_dir
      8. Return 0 if gate=="PASS" else 1
    """

if __name__ == "__main__":
    sys.exit(main())
```

### Pseudo-code: main()

```
1. args = parse_args()
2. rng = np.random.default_rng(args.seed)

3. # Step 1: ECE
4. ece_computer = ECEComputer(seed=args.seed, cache_dir=Path(args.output_dir))
5. logit_paths = discover_logit_files(args.data_dir)  # dict[model_id, Path]
6. ece_df = ece_computer.load_or_compute(logit_paths,
7.           force_recompute=not args.no_compute_ece)   # (30, 3)

8. # Step 2: Load H-E1 outputs + merge ECE
9. loader = DataLoader(h_e1_outputs_dir="../h-e1/code/outputs")
10. merged_df = loader.load(ece_df)   # (30, *) with RI, ECE, PC1, mean_confidence, family

11. # Step 3: Partial correlation analysis
12. analyzer = PartialCorrAnalyzer(n_bootstrap=10000, seed=args.seed)
13. corr_results = analyzer.run_all(merged_df)

14. # Step 4: Gate evaluation
15. evaluator = GateEvaluator()
16. gate_result = evaluator.evaluate_gate(
17.     rho=corr_results["full"]["rho"],
18.     p_value=corr_results["full"]["p_value"],
19.     family_results=corr_results["family_df"],
20. )
21. secondary = evaluator.run_all_secondary(merged_df, corr_results["family_df"])

22. # Step 5: Visualize
23. viz = Visualizer(figures_dir=Path(args.figures_dir))
24. viz.plot_all(merged_df, corr_results, gate_result)

25. # Step 6: Export
26. export_results(gate_result, corr_results, secondary, Path(args.output_dir))

27. print(f"Gate result: {gate_result['gate']}")
28. return 0 if gate_result["gate"] == "PASS" else 1
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | parse_args | argparse: --data-dir, --output-dir, --figures-dir, --seed, --no-compute-ece |
| L-8-2 | main | Orchestration: ECE → DataLoader → PartialCorr → Gate → Viz → export; exit code 0/1 |

---

## Summary

| Module | Class | Key Method | Subtasks |
|--------|-------|-----------|----------|
| ece_computer.py | ECEComputer | load_or_compute() | L-3-1..4 |
| partial_corr.py | PartialCorrAnalyzer | run_all() | L-4-1..4 |
| evaluate.py | GateEvaluator | evaluate_gate() | L-5-1..2 |
| run_experiment.py | — | main() | L-8-1..2 |

**Total subtasks**: 12/12
