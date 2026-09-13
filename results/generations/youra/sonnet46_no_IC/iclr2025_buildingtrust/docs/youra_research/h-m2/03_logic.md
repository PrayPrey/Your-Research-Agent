# Logic: H-M2 — RLHF Representation Rigidity Reduces Adversarial Robustness

Applied: OLS residualization pattern (scipy + sklearn, identical to H-E1/H-M1)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-M1)
**Status**: API signatures verified from actual h-m1 code
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Relevant Symbols**:
- `load_he1_data(he1_code_dir, he1_results_dir, he1_json) -> tuple` — analysis.py:15 — copy verbatim
- `extract_llama2_pairs(scores_df) -> list` — analysis.py:41 — copy verbatim
- `compute_deltas(pairs) -> list` — analysis.py:61 — change delta key from ethics→robustness, flip sign condition
- `run_sign_test(deltas) -> dict` — analysis.py:79 — count `nonpositive_robustness` not `both_positive`
- `verify_primary_gate(rho_partial) -> dict` — analysis.py:93 — change index [1][5]→[1][3], gate: rho < -0.4 signed
- `plot_rho_heatmap_highlighted(rho_partial, dimensions, out_path)` — visualization.py:180 — reuse pattern, update cells

---

## External Dependencies API

### API Signatures (From Actual H-M1 Code)

```python
# From: docs/youra_research/h-m1/code/analysis.py (ACTUAL CODE — verified)

def load_he1_data(
    he1_code_dir: str = HE1_CODE_DIR,
    he1_results_dir: str = HE1_RESULTS_DIR,
    he1_json: str = HE1_JSON,
) -> tuple:
    # Returns: (scores_df [16,6], annotated_df [16,8], rho_partial [6,6 ndarray])
    # CRITICAL: JSON key is "rho_partial" (list-of-lists), NOT "rho_partial_matrix"
    ...

def extract_llama2_pairs(scores_df: pd.DataFrame) -> list:
    # Returns list of 3 dicts: {"scale", "base_scores" [6,], "chat_scores" [6,]}
    # Model names verified: "LLaMA-2-7b-base", "LLaMA-2-7b-chat" (capitalized)
    ...

# From: docs/youra_research/h-m1/code/config.py (ACTUAL CODE — verified)
DIMENSIONS = ["truthfulness", "safety", "fairness", "robustness", "privacy", "machine_ethics"]
SAFETY_IDX = 1    # verified
ETHICS_IDX = 5    # H-M1 only — H-M2 uses ROBUSTNESS_IDX = 3
LLAMA2_BASE_NAMES = ["LLaMA-2-7b-base", "LLaMA-2-13b-base", "LLaMA-2-70b-base"]  # verified
LLAMA2_CHAT_NAMES = ["LLaMA-2-7b-chat", "LLaMA-2-13b-chat", "LLaMA-2-70b-chat"]  # verified

# From: docs/youra_research/h-m1/code/visualization.py (ACTUAL CODE — verified)
def plot_rho_heatmap_highlighted(
    rho_partial: np.ndarray,  # [6,6]
    dimensions: list,         # len=6
    out_path: str,
) -> None:
    # Uses sns.heatmap + mpatches.Rectangle; highlight pattern reused in H-M2
    ...

# From: h-e1/code/data_loader.py (called at runtime via sys.path insert — H-M1 pattern)
def load_trustllm_scores(results_dir: str) -> pd.DataFrame: ...   # [16,6], index=model_names
def add_annotations(scores_df: pd.DataFrame) -> pd.DataFrame: ... # [16,8], adds log_params, is_RLHF
```

**Verified from**: `docs/youra_research/h-m1/code/` (actual implementation, NOT spec)

**Critical H-M1 → H-M2 changes**:
- `ETHICS_IDX=5` → `ROBUSTNESS_IDX=3`
- `RHO_THRESHOLD=0.5` → `RHO_THRESHOLD=-0.4`
- Gate direction: `abs(rho) > threshold` → `rho < threshold` (signed, negative)
- Sign test direction: `delta > 0` → `delta <= 0`
- p-value: add explicit `df=n-2-k=12` t-distribution (H-M1 `verify_primary_gate` did not expose p-value)

---

## A-3: Primary Gate — rho_partial [Complexity: 10, Budget: 4 subtasks]

Applied: OLS residualization pattern (scipy + sklearn)

### API Signatures

```python
# analysis.py

def compute_partial_spearman(
    annotated_df: pd.DataFrame,           # [16, 8] with safety, robustness, log_params, is_RLHF
    dim_x: str = "safety",
    dim_y: str = "robustness",
    covariates: list[str] = ["log_params", "is_RLHF"],
) -> tuple[float, float]:
    """OLS residualize then spearmanr with t-dist(df=12) p-value. Returns (rho, p_value)."""
    ...


def verify_primary_gate(
    rho_partial: np.ndarray,              # [6, 6] float — from h-e1 JSON
    annotated_df: pd.DataFrame,           # [16, 8] float
    covariates: list[str] = ["log_params", "is_RLHF"],
) -> dict:
    """Direct matrix read [1][3], cross-validate vs OLS, warn if diff >0.001. Never raises.

    Returns: {rho_safety_robustness, rho_recomputed, p_value, primary_gate_pass, gate_result, mismatch_warned}
    gate_result: "PASS" | "FAIL/EXPLORE"
    """
    ...
```

### Array Shapes

| Variable | Shape | Note |
|----------|-------|------|
| rho_partial | (6, 6) | `np.array(he1_data["rho_partial"])` — key verified |
| x, y | (16,) | safety and robustness column values |
| Z | (16, 2) | [log_params, is_RLHF] covariates |
| x_res, y_res | (16,) | OLS residuals for spearmanr |

### Pseudo-code

```
# compute_partial_spearman:
1. x = annotated_df[dim_x].values        # (16,)
2. y = annotated_df[dim_y].values        # (16,)
3. Z = annotated_df[covariates].values   # (16, 2)
4. def residualize(v, Z):
       reg = LinearRegression(fit_intercept=True).fit(Z, v)
       return v - reg.predict(Z)
5. x_res, y_res = residualize(x, Z), residualize(y, Z)
6. rho, _ = scipy.stats.spearmanr(x_res, y_res)
7. n, k = 16, 2  →  df = n - 2 - k = 12
8. t_stat = rho * sqrt(df / (1 - rho**2))
9. p_val = 2 * scipy.stats.t.sf(abs(t_stat), df=df)
10. return rho, p_val

# verify_primary_gate:
1. rho_sr = float(rho_partial[SAFETY_IDX][ROBUSTNESS_IDX])   # direct read [1][3]
2. rho_recomp, p_val = compute_partial_spearman(annotated_df)
3. mismatch = abs(rho_sr - rho_recomp) > 0.001
4. if mismatch: log warning; rho_sr = rho_recomp  # NFR-3: use recomputed
5. gate_pass = rho_sr < RHO_THRESHOLD  # signed: rho < -0.4, NOT abs()
6. if not gate_pass:
       print(f"ρ_partial(safety,robustness)={rho_sr:.4f} — null finding for H-M2 mechanism")
7. return {rho_safety_robustness, rho_recomputed, p_value,
           primary_gate_pass, gate_result, mismatch_warned}
   # Never raises — SHOULD_WORK gate
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | compute_partial_spearman | OLS residualize + spearmanr + t-dist(df=12) p-value |
| L-3-2 | t-dist p-value formula | Explicit df=n-2-k=12; NOT scipy spearmanr default p |
| L-3-3 | verify_primary_gate matrix read | Direct read [SAFETY_IDX][ROBUSTNESS_IDX]; cross-validate; warn on mismatch |
| L-3-4 | SHOULD_WORK compliance | gate_result dict always returned; EXPLORE message printed; never raises |

---

## A-7: Visualization — 4 Mandatory Figures [Complexity: 12, Budget: 3 subtasks]

Applied: matplotlib/seaborn pattern from h-m1 visualization.py

### API Signatures

```python
# visualization.py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
import pandas as pd
from config import DIMENSIONS, SAFETY_IDX, ROBUSTNESS_IDX, ETHICS_IDX


def plot_gate_metrics(
    rho_sr: float,              # ρ_partial(safety, robustness)
    delta_values: list[float],  # (3,) [Δ_7b, Δ_13b, Δ_70b] robustness
    scales: list[str],          # ["7b", "13b", "70b"]
    out_path: str,
) -> None:
    """FR-5.1: dual-panel — rho bar vs -0.4 threshold; Δ_robustness bars vs 0."""
    ...


def plot_rho_heatmap(
    rho_partial: np.ndarray,       # (6, 6) float
    dimensions: list[str],         # len=6
    highlight_cells: list[tuple],  # [(SAFETY_IDX, ROBUSTNESS_IDX), (ROBUSTNESS_IDX, SAFETY_IDX),
                                   #  (SAFETY_IDX, ETHICS_IDX), (ETHICS_IDX, SAFETY_IDX)]
    out_path: str,
) -> None:
    """FR-5.3: 6x6 seaborn heatmap; highlight 2 pairs of symmetric cells with orange patches."""
    ...


def plot_within_family_deltas(
    deltas: list[dict],  # [{"scale", "delta_safety", "delta_robustness"}, ...]
    out_path: str,
) -> None:
    """FR-5.2: grouped bar Δ_safety vs Δ_robustness side-by-side for 7B/13B/70B."""
    ...


def plot_safety_robustness_scatter(
    annotated_df: pd.DataFrame,  # [16, 8] with safety, robustness, is_RLHF cols
    out_path: str,
) -> None:
    """FR-5.4: scatter 16 models colored by is_RLHF; linear trend lines per group."""
    ...


def generate_all_figures(
    results: dict,
    figures_dir: str = FIGURES_DIR,
) -> list[str]:
    """Call all 4 plot_* functions; return list of saved absolute paths."""
    ...
```

### Array Shapes

| Variable | Shape | Note |
|----------|-------|------|
| rho_partial | (6, 6) | passed directly from analysis results |
| delta_values | (3,) | [Δ_robustness_7b, Δ_13b, Δ_70b] |
| highlight_cells | list of 4 tuples | symmetric pairs for both cells |

### Pseudo-code (key figures)

**plot_gate_metrics** — dual panel:
```
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4))
# Panel 1: rho bar vs -0.4
rho_pass = rho_sr < -0.4
color1 = "#2E7D32" if rho_pass else "#C62828"
ax1.bar(["ρ_partial\n(safety, robustness)"], [rho_sr], color=color1, alpha=0.85)
ax1.axhline(-0.4, color="black", linestyle="--", linewidth=1, label="threshold=-0.4")
ax1.set_ylim(-1, 0.2)  # expected negative rho
ax1.text(0, rho_sr - 0.03, f"{rho_sr:.3f}", ha="center", fontsize=10)
ax1.set_title(f"Primary Gate: {'PASS' if rho_pass else 'FAIL/EXPLORE'}")
# Panel 2: delta_values bars vs 0
n_nonpositive = sum(1 for v in delta_values if v <= 0)
colors2 = ["#2E7D32" if v <= 0 else "#C62828" for v in delta_values]
ax2.bar(scales, delta_values, color=colors2, alpha=0.85)
ax2.axhline(0, color="black", linewidth=0.8, linestyle="--")
ax2.set_ylabel("Δ Robustness (Chat − Base)")
ax2.set_title(f"Δ_robustness: {n_nonpositive}/3 ≤ 0")
fig.suptitle("H-M2 SHOULD_WORK Gate Metrics", fontsize=12, fontweight="bold")
fig.tight_layout(); fig.savefig(out_path, dpi=300); plt.close(fig)
```

**plot_rho_heatmap** — highlight two cell pairs:
```
short_dims = [d.replace("machine_ethics","ethics").replace("truthfulness","truth") for d in dimensions]
sns.heatmap(rho_partial, annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1,
            xticklabels=short_dims, yticklabels=short_dims, ax=ax, linewidths=0.3)
for (row, col) in highlight_cells:  # 4 rects for 2 symmetric pairs
    rect = mpatches.Rectangle((col, row), 1, 1, linewidth=2.5, edgecolor="#FF6F00", facecolor="none")
    ax.add_patch(rect)
# highlight_cells = [(1,3),(3,1),(1,5),(5,1)]  ← safety-robustness and safety-ethics
ax.set_title("Partial Spearman Matrix (safety-robustness vs safety-ethics highlighted)")
```

**plot_safety_robustness_scatter** — trend lines per RLHF group:
```
for mask, color, label in [(base_mask,"#1565C0","Base"), (chat_mask,"#C62828","Chat (RLHF)")]:
    sub = annotated_df.loc[mask]
    ax.scatter(sub["safety"], sub["robustness"], c=color, s=60, label=label, zorder=3)
    m, b = np.polyfit(sub["safety"], sub["robustness"], 1)
    xs = np.linspace(sub["safety"].min(), sub["safety"].max(), 50)
    ax.plot(xs, m*xs+b, color=color, linewidth=1.2, linestyle="--", alpha=0.7)
ax.set_xlabel("Safety Score"); ax.set_ylabel("Robustness Score")
ax.set_title("Safety vs. Robustness: All 16 Models")
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | plot_gate_metrics | Dual-panel: rho bar vs -0.4 (signed y-axis ≤0); Δ_robustness bars vs 0 |
| L-7-2 | plot_rho_heatmap + plot_within_family_deltas | Heatmap 4-rect highlight; grouped bar Δ_safety vs Δ_robustness |
| L-7-3 | plot_safety_robustness_scatter + generate_all_figures | Scatter with per-group trend lines; orchestrate 4 saves |

---

## Supporting Modules (No Logic Budget — Straightforward Copies)

### config.py key changes from h-m1

```python
# h-m2/code/config.py
_HERE = os.path.dirname(os.path.abspath(__file__))
_HM2 = os.path.dirname(_HERE)
_RESEARCH = os.path.dirname(_HM2)

HE1_CODE_DIR = os.path.join(_RESEARCH, "h-e1", "code")
HE1_RESULTS_DIR = os.path.join(HE1_CODE_DIR, "TrustLLM", "results")
HE1_JSON = os.path.join(_RESEARCH, "h-e1", "experiment_results_phase3.json")

FIGURES_DIR = os.path.join(_HM2, "figures")
RESULTS_JSON = os.path.join(_HM2, "experiment_results_h_m2.json")

DIMENSIONS = ["truthfulness", "safety", "fairness", "robustness", "privacy", "machine_ethics"]
SAFETY_IDX = 1
ROBUSTNESS_IDX = 3        # ← H-M2 (was ETHICS_IDX=5 in H-M1)
ETHICS_IDX = 5            # kept for heatmap highlight only
RHO_THRESHOLD = -0.4      # ← signed negative (was 0.5 in H-M1)
SECONDARY_GATE_MIN = 2
BONFERRONI_ALPHA = 0.0033

LLAMA2_SCALES = ["7b", "13b", "70b"]
LLAMA2_BASE_NAMES = ["LLaMA-2-7b-base", "LLaMA-2-13b-base", "LLaMA-2-70b-base"]
LLAMA2_CHAT_NAMES = ["LLaMA-2-7b-chat", "LLaMA-2-13b-chat", "LLaMA-2-70b-chat"]
LLAMA2_PAIRS = list(zip(LLAMA2_BASE_NAMES, LLAMA2_CHAT_NAMES, LLAMA2_SCALES))
```

### analysis.py — full function list with delta changes

```python
def load_he1_data(he1_code_dir, he1_results_dir, he1_json) -> tuple:
    # copy verbatim from h-m1; reads he1_data["rho_partial"] (NOT "rho_partial_matrix")

def extract_llama2_pairs(scores_df: pd.DataFrame) -> list:
    # copy verbatim from h-m1

def compute_deltas(pairs: list) -> list:
    # change from h-m1:
    #   delta_robustness = float(all_deltas[ROBUSTNESS_IDX])
    #   nonpositive_robustness = bool(all_deltas[ROBUSTNESS_IDX] <= 0)  ← flipped direction
    # drop: delta_ethics, both_positive

def run_sign_test(deltas: list) -> dict:
    # n_nonpositive = sum(d["nonpositive_robustness"] for d in deltas)
    # gate: n_nonpositive >= SECONDARY_GATE_MIN
    # return {"n_nonpositive", "secondary_gate_pass", "delta_values": [float,...]}

def compute_partial_spearman(annotated_df, dim_x, dim_y, covariates) -> tuple[float, float]:
    # OLS residualize; t-dist df=n-2-k=12; return (rho, p_value)

def verify_primary_gate(rho_partial, annotated_df, covariates=["log_params","is_RLHF"]) -> dict:
    # direct read [SAFETY_IDX][ROBUSTNESS_IDX]; cross-validate; SHOULD_WORK (never raises)

def run_pythia_control(he1_code_dir) -> dict | None:
    # check h-e1 cache; return None if unavailable (graceful skip)

def run_analysis(he1_code_dir, he1_results_dir, he1_json) -> dict:
    # load → extract → deltas → sign_test → gate → pythia; never raises
```

### main.py — SHOULD_WORK compliance

```python
def serialize_results(results: dict) -> dict:
    # convert np.float64 → float, np.bool_ → bool; drop non-serializable (scores_df, etc.)

def check_gate(results: dict) -> str:
    # "PASS" if primary AND secondary
    # "PARTIAL_PASS" if exactly one passes
    # "FAIL/EXPLORE" if neither

def run_experiment() -> None:
    # try: run_analysis() → results
    # except Exception as e: log; write minimal error JSON; return  ← SHOULD_WORK
    # generate_all_figures(results); write RESULTS_JSON; print gate messages
```

### Results JSON schema (FR-6.1 — exact key names)

```python
{
    "hypothesis_id": "h-m2",
    "rho_partial_safety_robustness": float,
    "p_value_safety_robustness": float,
    "primary_gate_pass": bool,
    "delta_robustness": {"7b": float, "13b": float, "70b": float},  # lowercase keys
    "n_nonpositive_delta": int,
    "secondary_gate_pass": bool,
    "overall_gate": str,  # "PASS" | "PARTIAL_PASS" | "FAIL/EXPLORE"
    "pythia_rho_robustness_scale": float | None,
    "figure_paths": list[str],
}
```
