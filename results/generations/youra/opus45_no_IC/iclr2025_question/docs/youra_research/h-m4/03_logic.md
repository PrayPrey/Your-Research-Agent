# Logic: H-M4 (MECHANISM)

**Applied**: No relevant KB pattern (Archon returned unrelated diffusion/UniPC docs, same as H-M3); reusing H-M3's validated sklearn roc_curve + scipy bootstrap pattern, adding scipy.stats.mannwhitneyu for FR-5 (standard scipy API, no KB match needed).

Budget: 0 subtasks (all Epic tasks Low complexity, complexity < 9).

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M3 code fully reused; H-M4 only overrides config + adds Mann-Whitney comparison)
**Status**: API signatures verified from H-M3's `03_logic.md` (itself Serena-verified against H-M1 actual code). H-M3's `calibration.py`, `transfer.py`, `stats.py` functions confirmed present with exact signatures below.
**Analyzed Path**: `docs/youra_research/h-m3/code/` (via H-M3's `03_logic.md`, which is itself the actual-code-verified spec)
**Relevant Symbols**:
- `calibrate_threshold(entropies, labels, target_fpr) -> float`
- `evaluate_transfer(source_threshold, target_entropies, target_labels) -> dict`
- `compute_auroc_degradation(source_auroc, target_auroc) -> float`
- `run_pair_transfer(source, target, entropy_cache) -> dict`
- `bootstrap_ci(degradations, n_bootstrap, ci) -> tuple[float, float]`
- `get_or_compute_benchmark_entropy(name, calib_items, eval_items, generator, clusterer, cache_dir) -> tuple[np.ndarray x4]`

**Note**: `data.py`/`load_benchmark` not shown in H-M3's `03_logic.md` snippet but referenced in H-M4 architecture's External Dependencies table — assume `load_benchmark(name: str) -> list[dict]` and `split_calib_eval(items: list[dict], calib_frac: float = 0.7, seed: int = SEED) -> tuple[list[dict], list[dict]]` per H-M3 architecture convention. Verify at Phase 4 coding time if signature differs.

---

## External Dependencies API

```python
# From: h-m3/code/calibration.py (verified via H-M3 03_logic.md)
def calibrate_threshold(entropies: np.ndarray, labels: np.ndarray, target_fpr: float = TARGET_FPR) -> float: ...
def evaluate_transfer(source_threshold: float, target_entropies: np.ndarray, target_labels: np.ndarray) -> dict:
    """Returns {"auroc": float, "threshold_used": float}"""
def compute_auroc_degradation(source_auroc: float, target_auroc: float) -> float: ...

# From: h-m3/code/transfer.py
def run_pair_transfer(source: str, target: str, entropy_cache: dict) -> dict:
    """entropy_cache[name] = (calib_e, calib_l, eval_e, eval_l).
    Returns {"source","target","source_auroc","target_auroc","degradation","source_threshold"}"""

# From: h-m3/code/stats.py
def bootstrap_ci(degradations: list[float], n_bootstrap: int = N_BOOTSTRAP, ci: float = 0.95) -> tuple[float, float]: ...

# From: h-m3/code/entropy_pipeline.py
def get_or_compute_benchmark_entropy(
    name: str, calib_items: list[dict], eval_items: list[dict],
    generator: ResponseGenerator, clusterer: EntailmentClusterer, cache_dir: str = OUTPUTS_DIR,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Returns (calib_entropies, calib_labels, eval_entropies, eval_labels)"""

# From: h-m3/outputs/transfer_results.json (data, not code)
# list[dict] with same schema as run_pair_transfer output; H-M4 extracts "degradation" field per within-cluster pair
```

**Verified from**: `h-m3/03_logic.md` (itself Serena-verified against H-M1 actual code) and `h-m4/03_architecture.md` External Dependencies table.

---

## M4-1: Config override + loader verification [Complexity: 6, Budget: 0]

**Applied**: Standard Python — module-level constant override.

```python
# h-m4/code/config.py
from h_m3.code.config import SEED, CALIB_SPLIT, TARGET_FPR, GEN_MODEL, NLI_MODEL, N_GENERATIONS, TEMPERATURE, N_BOOTSTRAP

CROSS_CLUSTER_PAIRS: list[tuple[str, str]] = [("trivia_qa", "pop_qa"), ("trivia_qa", "halueval_qa")]
JS_DIVERGENCE: dict[tuple[str, str], float] = {("trivia_qa", "pop_qa"): 0.422, ("trivia_qa", "halueval_qa"): 0.526}
DEGRADATION_THRESHOLD: float = 0.15
H_M3_DEGRADATIONS_PATH: str = "h-m3/outputs/transfer_results.json"
OUTPUTS_DIR: str = "h-m4/outputs"
FIGURES_DIR: str = "h-m4/figures"
```

No new subtasks — verify `load_benchmark("pop_qa")` / `load_benchmark("halueval_qa")` return non-empty at Phase 4 runtime (assert in `run.py`'s `demo()`/self-check, not a separate module).

---

## M4-2: Cross-cluster entropy computation [Complexity: 8, Budget: 0]

**Applied**: Direct reuse of `get_or_compute_benchmark_entropy` — no new function.

```python
# h-m4/code/run.py (inline, not a separate module)
entropy_cache: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = {}
for name in {"trivia_qa", "pop_qa", "halueval_qa"}:
    items = load_benchmark(name)
    calib_items, eval_items = split_calib_eval(items, CALIB_SPLIT, SEED)
    entropy_cache[name] = get_or_compute_benchmark_entropy(
        name, calib_items, eval_items, generator, clusterer, cache_dir=OUTPUTS_DIR
    )
```

Tensor shapes: `calib_entropies [350]`, `eval_entropies [150]` per benchmark (500 samples * 0.7/0.3 split) — smaller than H-M3's 700/300 (1000-sample benchmarks), per PRD FR-1 `validation[:500]`.

---

## M4-3: Cross-cluster transfer wrapper [Complexity: 6, Budget: 0]

**Applied**: Thin wrapper over H-M3's `run_pair_transfer`.

```python
# h-m4/code/transfer_runner.py
from h_m3.code.transfer import run_pair_transfer

def run_cross_cluster_transfers(
    pairs: list[tuple[str, str]], entropy_cache: dict
) -> list[dict]:
    """Directional only (source->target), unlike H-M3's run_all_transfers (both directions).
    Returns: [run_pair_transfer(source, target, entropy_cache) for source, target in pairs]"""
    return [run_pair_transfer(source, target, entropy_cache) for source, target in pairs]
```

---

## M4-4: Statistical aggregation + gate check [Complexity: 5, Budget: 0]

**Applied**: Reuses H-M3's `bootstrap_ci`; gate direction inverted (`>` not `<=`).

```python
# h-m4/code/stats.py
from h_m3.code.stats import bootstrap_ci

def aggregate_results(transfer_results: list[dict]) -> dict:
    """degs = [r["degradation"] for r in transfer_results]
    Returns {"mean_degradation": float, "ci_lower": float, "ci_upper": float}"""
    ...

def check_gate(agg: dict) -> bool:
    """mean_degradation > DEGRADATION_THRESHOLD (0.15) -- inverted vs H-M3's <=."""
    return agg["mean_degradation"] > DEGRADATION_THRESHOLD
```

---

## M4-5: Mann-Whitney comparison vs H-M3 [Complexity: 6, Budget: 0]

**Applied**: scipy.stats.mannwhitneyu, one-sided (`alternative='greater'`) per PRD 6.3.

```python
# h-m4/code/stats.py (cont.)
import json
from scipy.stats import mannwhitneyu

def compare_to_h_m3(cross_degradations: list[float], h_m3_path: str = H_M3_DEGRADATIONS_PATH) -> dict:
    """Load H-M3 within-cluster degradations, test cross > within.
    Returns {"statistic": float, "p_value": float}"""
    with open(h_m3_path) as f:
        h_m3_results = json.load(f)
    within_degradations = [r["degradation"] for r in h_m3_results]
    stat, p_value = mannwhitneyu(cross_degradations, within_degradations, alternative="greater")
    return {"statistic": float(stat), "p_value": float(p_value)}
```

---

## M4-6: Visualization suite [Complexity: 7, Budget: 0]

**Applied**: matplotlib, same style as H-M3 (assumed consistent bar/box/scatter helpers, no KB pattern needed).

```python
# h-m4/code/visualize.py
def plot_gate_bar(mean_degradation: float, threshold: float, out_path: str) -> None: ...
def plot_within_vs_cross_box(within: list[float], cross: list[float], out_path: str) -> None: ...
def plot_per_pair_degradation(transfer_results: list[dict], out_path: str) -> None: ...
def plot_js_divergence_scatter(transfer_results: list[dict], js_map: dict, out_path: str) -> None:
    """x = js_map[(source,target)], y = r["degradation"] for r in transfer_results"""
```

---

## M4-7: Pipeline orchestration + gate logging [Complexity: 6, Budget: 0]

**Applied**: Sequential orchestration, mirrors H-M3's `run.py` control flow.

```python
# h-m4/code/run.py
def main() -> None:
    """
    1. generator = ResponseGenerator(GEN_MODEL); clusterer = EntailmentClusterer(NLI_MODEL)
    2. entropy_cache = {name: get_or_compute_benchmark_entropy(...) for name in benchmarks}  # M4-2
    3. transfer_results = run_cross_cluster_transfers(CROSS_CLUSTER_PAIRS, entropy_cache)     # M4-3
    4. agg = aggregate_results(transfer_results); gate_pass = check_gate(agg)                 # M4-4
    5. cross_degs = [r["degradation"] for r in transfer_results]
       mw = compare_to_h_m3(cross_degs, H_M3_DEGRADATIONS_PATH)                               # M4-5
    6. plot_gate_bar(...); plot_within_vs_cross_box(...); plot_per_pair_degradation(...); plot_js_divergence_scatter(...)  # M4-6
    7. json.dump(transfer_results, "h-m4/outputs/transfer_results.json")
    8. log agg, mw, gate_pass to 04_validation.md
    """
```

Self-check (assert-based, no framework): `assert len(transfer_results) == 2` (FR-6 minimum), `assert 0.0 <= agg["mean_degradation"] <= 1.0`.
