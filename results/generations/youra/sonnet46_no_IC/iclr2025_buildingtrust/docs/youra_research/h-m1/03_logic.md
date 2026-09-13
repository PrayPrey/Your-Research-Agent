# Logic: H-M1
## RLHF Co-Optimization of Safety and Ethics — Within-Family Natural Experiment

**Date:** 2026-08-04
**Type:** MECHANISM (Incremental — extends H-E1)

Applied: Standard paired-delta sign test (scipy.stats.binomtest, matplotlib grouped bar)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m1 incrementally extends h-e1)
**Status**: API signatures verified from actual h-e1 code files
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Relevant Symbols**:
- `load_trustllm_scores(results_dir: str) -> pd.DataFrame` — returns [16, 6] DataFrame, index=MODEL_ORDER, columns=DIMENSIONS
- `add_annotations(scores_df: pd.DataFrame) -> pd.DataFrame` — adds `log10_params`, `is_RLHF` columns → [16, 8]
- `DIMENSIONS: list` — `["truthfulness","safety","fairness","robustness","privacy","machine_ethics"]`
- `MODEL_ORDER: list` — 16-element list, canonical order
- `MODEL_ANNOTATIONS: dict` — `{model_name: {"log10_params": float, "is_RLHF": int}}`
- `ols_residualize(scores_df, covariates_df) -> pd.DataFrame` — OLS residuals [16, 6]
- `partial_spearman_matrix(scores_df, covariates_df, alpha_bonferroni) -> tuple` — (rho [6,6], pval [6,6], sig_pairs)
- h-e1 JSON key: `rho_partial` (list-of-lists), NOT `rho_partial_matrix`
- Raw scores NOT in h-e1 JSON — load via `load_trustllm_scores(results_dir)`

---

## External Dependencies API

### Verified Signatures from h-e1/code/data_loader.py

```python
# From: h-e1/code/data_loader.py (ACTUAL CODE)

DIMENSIONS = [
    "truthfulness", "safety", "fairness",
    "robustness", "privacy", "machine_ethics",
]  # indices: safety=1, machine_ethics=5

MODEL_ORDER: list  # 16 canonical model names

MODEL_ANNOTATIONS: dict  # {model_name: {"log10_params": float, "is_RLHF": int}}

def load_trustllm_scores(results_dir: str = "TrustLLM/results") -> pd.DataFrame:
    """Returns DataFrame [16, 6], index=MODEL_ORDER, columns=DIMENSIONS."""
    ...

def add_annotations(scores_df: pd.DataFrame) -> pd.DataFrame:
    """Returns DataFrame [16, 8]: adds log10_params, is_RLHF columns."""
    ...
```

### Verified Signatures from h-e1/code/analysis.py

```python
# From: h-e1/code/analysis.py (ACTUAL CODE)

def ols_residualize(
    scores_df: pd.DataFrame,
    covariates_df: pd.DataFrame,
) -> pd.DataFrame:
    """Returns residuals DataFrame [16, 6]."""
    ...

def partial_spearman_matrix(
    scores_df: pd.DataFrame,
    covariates_df: pd.DataFrame,
    alpha_bonferroni: float = 0.0033,
) -> tuple:  # (rho_6x6 ndarray, pval_6x6 ndarray, significant_pairs list)
    ...
```

**Verified from**: `docs/youra_research/h-e1/code/` (actual files, not specs)

---

## A-4: Delta Computation & Sign Test [Complexity: 9, Budget: 2]

Applied: Standard paired-delta sign test (scipy.stats.binomtest)

### API Signatures

```python
# h-m1/code/analysis.py

SAFETY_IDX = 1   # DIMENSIONS.index("safety")
ETHICS_IDX = 5   # DIMENSIONS.index("machine_ethics")

LLAMA2_PAIRS = [
    ("LLaMA-2-7b-base",  "LLaMA-2-7b-chat",  "7b"),
    ("LLaMA-2-13b-base", "LLaMA-2-13b-chat", "13b"),
    ("LLaMA-2-70b-base", "LLaMA-2-70b-chat", "70b"),
]

def extract_llama2_pairs(scores_df: pd.DataFrame) -> list[dict]:
    """Extract 3 base/chat score pairs from scores_df [16, 6].
    Returns list of 3 dicts: {"scale", "base_scores", "chat_scores"}.
    """
    ...

def compute_deltas(pairs: list[dict]) -> list[dict]:
    """Compute per-dimension deltas for each LLaMA-2 pair.
    Returns list of 3 dicts.
    """
    ...

def run_sign_test(deltas: list[dict]) -> dict:
    """Binomial sign test on both-positive count.
    Returns {"n_both_positive", "secondary_gate_pass", "binom_pvalue"}.
    """
    ...
```

### Subtask L-4-1: compute_deltas()

```python
def extract_llama2_pairs(scores_df: pd.DataFrame) -> list[dict]:
    pairs = []
    for base_name, chat_name, scale in LLAMA2_PAIRS:
        if base_name not in scores_df.index or chat_name not in scores_df.index:
            raise ValueError(f"Missing model {base_name} or {chat_name} in scores_df")
        pairs.append({
            "scale": scale,
            "base_scores": scores_df.loc[base_name].values,  # shape [6]
            "chat_scores": scores_df.loc[chat_name].values,  # shape [6]
        })
    return pairs  # len=3


def compute_deltas(pairs: list[dict]) -> list[dict]:
    # pairs[i]["base_scores"]: np.ndarray [6] — all dimensions
    # pairs[i]["chat_scores"]: np.ndarray [6]
    deltas = []
    for p in pairs:
        all_deltas = p["chat_scores"] - p["base_scores"]  # [6] chat minus base
        deltas.append({
            "scale":        p["scale"],
            "all_deltas":   all_deltas,                   # np.ndarray [6]
            "delta_safety": float(all_deltas[SAFETY_IDX]),  # idx 1
            "delta_ethics": float(all_deltas[ETHICS_IDX]),  # idx 5
            "both_positive": bool(
                all_deltas[SAFETY_IDX] > 0 and all_deltas[ETHICS_IDX] > 0
            ),
        })
    return deltas  # len=3
```

### Subtask L-4-2: run_sign_test()

```python
from scipy.stats import binomtest  # NOT binom_test — deprecated in scipy>=1.12

def run_sign_test(deltas: list[dict]) -> dict:
    n_both_positive = sum(d["both_positive"] for d in deltas)
    # One-sided: P(X >= n_both_positive | n=3, p=0.5)
    result = binomtest(n_both_positive, n=3, p=0.5, alternative="greater")
    return {
        "n_both_positive":   n_both_positive,
        "secondary_gate_pass": n_both_positive >= 2,
        "binom_pvalue":      float(result.pvalue),
    }
```

### Data Shapes

| Variable | Shape/Type | Note |
|----------|-----------|------|
| scores_df | pd.DataFrame [16, 6] | index=MODEL_ORDER, columns=DIMENSIONS |
| base_scores / chat_scores | np.ndarray [6] | one row from scores_df |
| all_deltas | np.ndarray [6] | chat_scores - base_scores |
| delta_safety | float | all_deltas[1] |
| delta_ethics | float | all_deltas[5] |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | compute_deltas | extract_llama2_pairs + compute_deltas with exact array indexing |
| L-4-2 | run_sign_test | scipy.stats.binomtest (alternative="greater", n=3, p=0.5) |

---

## A-7: Within-Family Delta Figure [Complexity: 9, Budget: 2]

Applied: Standard matplotlib grouped bar with annotation

### API Signatures

```python
# h-m1/code/visualization.py

def plot_within_family_deltas(
    deltas: list[dict],    # len=3, each has "scale","delta_safety","delta_ethics","both_positive"
    sign_test: dict,       # {"n_both_positive","secondary_gate_pass","binom_pvalue"}
    out_path: str,
) -> None:
    """Grouped bar chart: Δ_safety (blue) and Δ_ethics (orange) per scale.
    Annotates sign test result. Saves PNG at 300 DPI.
    """
    ...
```

### Subtask L-7-1: plot_within_family_deltas() implementation

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_within_family_deltas(deltas, sign_test, out_path):
    scales = [d["scale"] for d in deltas]           # ["7b","13b","70b"]
    d_safety = [d["delta_safety"] for d in deltas]  # [float, float, float]
    d_ethics = [d["delta_ethics"] for d in deltas]  # [float, float, float]

    x = np.arange(len(scales))  # [0, 1, 2]
    width = 0.35

    fig, ax = plt.subplots(figsize=(7, 4))

    bars_s = ax.bar(x - width/2, d_safety, width, label="Δ Safety",
                    color=["#2196F3" if v > 0 else "#EF5350" for v in d_safety])
    bars_e = ax.bar(x + width/2, d_ethics, width, label="Δ Ethics",
                    color=["#FF9800" if v > 0 else "#9C27B0" for v in d_ethics])

    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([f"LLaMA-2\n{s}" for s in scales])
    ax.set_ylabel("Score Delta (Chat − Base)")
    ax.set_title("Within-Family RLHF Effect: Δ Safety and Δ Ethics per Scale")
    ax.legend()

    # Sign test annotation — see L-7-2 below
    _annotate_sign_test(ax, sign_test)

    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
```

### Subtask L-7-2: PASS/FAIL annotation logic

```python
def _annotate_sign_test(ax: plt.Axes, sign_test: dict) -> None:
    # Color by gate result
    gate_pass = sign_test["secondary_gate_pass"]
    label = (
        f"Sign test: {sign_test['n_both_positive']}/3 pairs both-positive\n"
        f"p = {sign_test['binom_pvalue']:.3f}  "
        f"{'PASS' if gate_pass else 'FAIL'}"
    )
    color = "#2E7D32" if gate_pass else "#C62828"  # dark green / dark red
    ax.text(
        0.97, 0.97, label,
        transform=ax.transAxes,
        ha="right", va="top",
        fontsize=9,
        color=color,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=color, linewidth=1.2),
    )
```

Color scheme:
- Safety bar: blue (#2196F3) if Δ>0, red (#EF5350) if Δ<0
- Ethics bar: orange (#FF9800) if Δ>0, purple (#9C27B0) if Δ<0
- Annotation box border: dark green (PASS) / dark red (FAIL)

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | plot_within_family_deltas | grouped bar, color by sign, x-axis scale labels |
| L-7-2 | _annotate_sign_test | PASS/FAIL text box, color-coded, top-right of axes |

---

## A-8: Safety-Ethics Scatter [Complexity: 10, Budget: 2]

Applied: Standard matplotlib scatter with FancyArrowPatch

### API Signatures

```python
# h-m1/code/visualization.py

def plot_safety_ethics_scatter(
    annotated_df: pd.DataFrame,   # [16, 8]: scores + log10_params + is_RLHF
    llama2_pairs: list[dict],     # len=3, each has "scale","base_scores","chat_scores"
    out_path: str,
) -> None:
    """16-model scatter: x=safety, y=ethics, colored by is_RLHF.
    Arrows from LLaMA-2 base->chat. Saves PNG at 300 DPI.
    """
    ...

def _annotate_arrows(
    ax: plt.Axes,
    llama2_pairs: list[dict],
    annotated_df: pd.DataFrame,
) -> None:
    """Draw arrows from (base_safety, base_ethics) to (chat_safety, chat_ethics)."""
    ...
```

### Subtask L-8-1: plot_safety_ethics_scatter() implementation

```python
def plot_safety_ethics_scatter(annotated_df, llama2_pairs, out_path):
    fig, ax = plt.subplots(figsize=(7, 6))

    # Split by RLHF status
    base_mask = annotated_df["is_RLHF"] == 0
    chat_mask = annotated_df["is_RLHF"] == 1

    ax.scatter(
        annotated_df.loc[base_mask, "safety"],
        annotated_df.loc[base_mask, "machine_ethics"],
        c="#1565C0", marker="o", s=60, label="Base (no RLHF)", zorder=3,
    )
    ax.scatter(
        annotated_df.loc[chat_mask, "safety"],
        annotated_df.loc[chat_mask, "machine_ethics"],
        c="#C62828", marker="s", s=60, label="Chat (RLHF)", zorder=3,
    )

    # Arrows for LLaMA-2 pairs
    _annotate_arrows(ax, llama2_pairs, annotated_df)

    ax.set_xlabel("Safety Score")
    ax.set_ylabel("Machine Ethics Score")
    ax.set_title("Safety vs. Ethics: All 16 Models (colored by RLHF)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
```

### Subtask L-8-2: Arrow geometry

```python
def _annotate_arrows(ax, llama2_pairs, annotated_df):
    # DIMENSIONS indices: safety=1, machine_ethics=5
    for p in llama2_pairs:
        base_row = annotated_df.loc[
            annotated_df.index.str.contains(f"LLaMA-2-{p['scale']}-base")
        ]
        chat_row = annotated_df.loc[
            annotated_df.index.str.contains(f"LLaMA-2-{p['scale']}-chat")
        ]
        # Coordinates from DataFrame columns (not array indices)
        x0 = float(base_row["safety"].iloc[0])
        y0 = float(base_row["machine_ethics"].iloc[0])
        x1 = float(chat_row["safety"].iloc[0])
        y1 = float(chat_row["machine_ethics"].iloc[0])

        dx, dy = x1 - x0, y1 - y0
        # arrowstyle: head visible even for small deltas
        ax.annotate(
            "",
            xy=(x1, y1),
            xytext=(x0, y0),
            arrowprops=dict(
                arrowstyle="-|>",
                color="#FF6F00",   # amber — visible on both blue/red points
                lw=1.5,
                mutation_scale=12,
            ),
            zorder=5,
        )
        # Scale label at midpoint
        ax.text(
            (x0 + x1) / 2, (y0 + y1) / 2,
            p["scale"],
            fontsize=7, color="#FF6F00", ha="center", va="bottom",
        )
```

Arrow visibility notes:
- Use `ax.annotate(..., arrowprops=dict(arrowstyle="-|>"))` — renders at any delta magnitude
- `mutation_scale=12` ensures arrowhead is visible even for Δ < 0.05
- Amber (#FF6F00) contrasts against both blue (base) and red (chat) markers
- Scale label ("7b"/"13b"/"70b") at midpoint of arrow for disambiguation

### Data Shapes

| Variable | Shape/Type | Note |
|----------|-----------|------|
| annotated_df | pd.DataFrame [16, 8] | columns include "safety","machine_ethics","is_RLHF" |
| llama2_pairs | list[dict], len=3 | keys: "scale","base_scores","chat_scores" |
| arrow start | (float, float) | (base_safety, base_ethics) |
| arrow end | (float, float) | (chat_safety, chat_ethics) |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | plot_safety_ethics_scatter | 16-model scatter, RLHF coloring, calls _annotate_arrows |
| L-8-2 | _annotate_arrows | ax.annotate arrowstyle="-|>", amber color, midpoint scale label |

---

## Summary

**Total subtasks used**: 6 of 6 budget

| Module | Subtasks | Key API |
|--------|----------|---------|
| A-4 | L-4-1, L-4-2 | compute_deltas(), run_sign_test() with binomtest |
| A-7 | L-7-1, L-7-2 | plot_within_family_deltas(), _annotate_sign_test() |
| A-8 | L-8-1, L-8-2 | plot_safety_ethics_scatter(), _annotate_arrows() |

**Critical implementation notes for Phase 4 Coder**:
1. `scipy.stats.binomtest` (not `binom_test`) — deprecated in scipy>=1.12
2. h-e1 JSON key: `rho_partial` (list-of-lists) → `np.array(data["rho_partial"])` for ndarray
3. Raw scores NOT in h-e1 JSON — must call `load_trustllm_scores(results_dir)` from h-e1/code/
4. Arrow geometry: use `ax.annotate` with `arrowstyle="-|>"`, NOT `ax.arrow` (which clips arrowheads)
5. DIMENSIONS indices: safety=1, machine_ethics=5 (verified from actual h-e1 code)
