# Architecture: H-M2
## RLHF Representation Rigidity Reduces Adversarial Robustness

Applied: OLS residualization pattern (scipy + sklearn, identical to H-E1/H-M1)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-M1)
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Findings**: H-M1 has 4 files (config.py, analysis.py, visualization.py, main.py). H-M2 mirrors this exactly, swapping `ETHICS_IDX=5` for `ROBUSTNESS_IDX=3` and flipping the sign-test direction (≤0 instead of >0). Critical discovery: JSON key is `"rho_partial"` (not `"rho_partial_matrix"`); model names are `"LLaMA-2-7b-base"` / `"LLaMA-2-7b-chat"` (capitalized).

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_trustllm_scores | `from data_loader import load_trustllm_scores` | `h-e1/code/data_loader.py` |
| add_annotations | `from data_loader import add_annotations` | `h-e1/code/data_loader.py` |
| rho_partial matrix | JSON key `"rho_partial"` (list-of-lists, NOT `"rho_partial_matrix"`) | `h-e1/experiment_results_phase3.json` |

**Verified from**: `docs/youra_research/h-m1/code/` (actual implementation)

**Dimension index map** (from H-M1 config.py `DIMENSIONS` list):
- Index 0: truthfulness
- Index 1: safety  ← `SAFETY_IDX`
- Index 2: fairness
- Index 3: robustness  ← `ROBUSTNESS_IDX` (new for H-M2)
- Index 4: privacy
- Index 5: machine_ethics

---

## File Structure

```
h-m2/
├── code/
│   ├── config.py         # paths + constants (mirrors h-m1/code/config.py)
│   ├── analysis.py       # load → partial_spearman → sign_test → gate
│   ├── visualization.py  # 4 mandatory figures + optional cluster plot
│   └── main.py          # entrypoint: run_experiment()
├── figures/
│   ├── gate_metrics.png
│   ├── delta_robustness.png
│   ├── rho_heatmap.png
│   └── safety_rob_scatter.png
└── experiment_results_h_m2.json
```

---

## Module Definitions

### Config (`code/config.py`)

**Dependencies**: os (stdlib only)

```python
# Paths
_HERE: str          # os.path.abspath(__file__) directory
_HM2: str           # h-m2/
_RESEARCH: str      # youra_research/

HE1_CODE_DIR: str   # ../h-e1/code
HE1_RESULTS_DIR: str  # ../h-e1/code/TrustLLM/results
HE1_JSON: str       # ../h-e1/experiment_results_phase3.json

OUTPUT_DIR: str     # h-m2/
FIGURES_DIR: str    # h-m2/figures/
RESULTS_JSON: str   # h-m2/experiment_results_h_m2.json
LOG_PATH: str       # h-m2/experiment.log

# Analysis constants
DIMENSIONS: list    # ["truthfulness","safety","fairness","robustness","privacy","machine_ethics"]
SAFETY_IDX: int     # 1
ROBUSTNESS_IDX: int # 3  ← H-M2 specific (replaces ETHICS_IDX=5 from H-M1)
RHO_THRESHOLD: float  # -0.4  (negative threshold — sign flipped vs H-M1)
SECONDARY_GATE_MIN: int  # 2
BONFERRONI_ALPHA: float  # 0.0033

LLAMA2_SCALES: list       # ["7b", "13b", "70b"]
LLAMA2_BASE_NAMES: list   # ["LLaMA-2-7b-base", "LLaMA-2-13b-base", "LLaMA-2-70b-base"]
LLAMA2_CHAT_NAMES: list   # ["LLaMA-2-7b-chat", "LLaMA-2-13b-chat", "LLaMA-2-70b-chat"]
LLAMA2_PAIRS: list        # zip(BASE_NAMES, CHAT_NAMES, SCALES)
```

---

### Analysis (`code/analysis.py`)

**Dependencies**: config, numpy, scipy.stats, sklearn.linear_model, json, sys, pingouin

```python
def load_he1_data(
    he1_code_dir: str = HE1_CODE_DIR,
    he1_results_dir: str = HE1_RESULTS_DIR,
    he1_json: str = HE1_JSON,
) -> tuple:  # (scores_df [16,6], annotated_df [16,8], rho_partial [6,6 ndarray])
    ...

def extract_llama2_pairs(scores_df) -> dict:
    # Returns {scale: {"base": Series, "chat": Series}} for 7b/13b/70b
    ...

def compute_deltas(pairs: dict) -> dict:
    # Returns {scale: {"robustness": float, "safety": float}}
    # Δ = chat_score - base_score per dimension
    ...

def run_sign_test(deltas: dict) -> dict:
    # Returns {delta_values: list[float], n_nonpositive: int,
    #          secondary_gate_pass: bool, scale_results: dict}
    # Gate: n_nonpositive >= SECONDARY_GATE_MIN (≤0 means RLHF hurts robustness)
    ...

def compute_partial_spearman(
    annotated_df,
    dim_x: str = "safety",
    dim_y: str = "robustness",
    covariates: list = ["log_params", "is_RLHF"],
) -> tuple:  # (rho_partial: float, p_value: float)
    # OLS residualization pattern (identical to H-E1; t-dist df=n-2-k=12)
    ...

def verify_primary_gate(rho_partial_matrix: np.ndarray) -> dict:
    # Direct read: rho_partial_matrix[SAFETY_IDX][ROBUSTNESS_IDX]
    # Cross-validates vs compute_partial_spearman(); logs warning if diff > 0.001
    # Returns {rho_safety_robustness: float, p_value: float,
    #          primary_gate_pass: bool, gate_result: str}
    # gate_result: "PASS" | "FAIL/EXPLORE" (never raises on failure)
    ...

def run_pythia_control(he1_code_dir: str = HE1_CODE_DIR) -> dict | None:
    # Check h-e1 cache for Pythia lm-eval results; compute rho(robustness, log_scale)
    # Returns None if unavailable (skip gracefully)
    ...

def run_analysis(
    he1_code_dir: str = HE1_CODE_DIR,
    he1_results_dir: str = HE1_RESULTS_DIR,
    he1_json: str = HE1_JSON,
) -> dict:
    # Top-level: load → extract → compute → sign_test → gate → pythia_control
    # Returns full results dict; NEVER raises on gate failure
    ...
```

---

### Visualization (`code/visualization.py`)

**Dependencies**: config, matplotlib, seaborn, numpy, pandas

```python
def plot_gate_metrics(
    rho_sr: float,
    delta_values: list[float],
    scales: list[str],
    out_path: str,
) -> None:
    # FR-5.1: ρ_partial bar vs -0.4 threshold; Δ_robustness bars vs 0
    ...

def plot_within_family_deltas(
    deltas: dict,
    out_path: str,
) -> None:
    # FR-5.2: Δ_safety vs Δ_robustness side-by-side for 7B/13B/70B
    ...

def plot_rho_heatmap(
    rho_partial: np.ndarray,
    dimensions: list[str],
    highlight_cells: list[tuple],
    out_path: str,
) -> None:
    # FR-5.3: 6×6 heatmap; highlight (safety,robustness) and (safety,ethics) cells
    ...

def plot_safety_robustness_scatter(
    annotated_df,
    out_path: str,
) -> None:
    # FR-5.4: 16 models scatter, color by is_RLHF, partial regression lines
    ...

def generate_all_figures(results: dict, figures_dir: str = FIGURES_DIR) -> list[str]:
    # Calls all plot_* functions; returns list of saved figure paths
    ...
```

---

### Main (`code/main.py`)

**Dependencies**: analysis, visualization, config, json, os, logging

```python
def serialize_results(results: dict) -> dict:
    # Convert numpy types → JSON-serializable; format per FR-6.1 schema
    ...

def check_gate(results: dict) -> str:
    # Returns "PASS" | "PARTIAL_PASS" | "FAIL/EXPLORE"
    ...

def run_experiment() -> None:
    # 1. run_analysis() → results
    # 2. generate_all_figures(results)
    # 3. Serialize + write RESULTS_JSON
    # 4. Print gate verification messages (per FR-6.2)
    # Never raises — SHOULD_WORK gate compliance
    ...

if __name__ == "__main__":
    run_experiment()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config setup | Copy h-m1 config, swap ETHICS_IDX→ROBUSTNESS_IDX (=3), set RHO_THRESHOLD=-0.4, update output paths | 5 | 1+1+1+2 |
| A-2 | Data loading | Copy load_he1_data from h-m1; validate `"rho_partial"` key (not `"rho_partial_matrix"`) and model name format | 7 | 2+2+1+2 |
| A-3 | Primary gate — rho_partial | Direct matrix read [SAFETY_IDX][ROBUSTNESS_IDX]; cross-validate with OLS recompute; warn if diff >0.001 | 10 | 2+2+3+3 |
| A-4 | Sign test | compute_deltas + run_sign_test for robustness dim (≤0 direction, vs H-M1 >0); n_nonpositive≥2 gate | 8 | 2+2+2+2 |
| A-5 | Ablations | Uncontrolled Spearman (A1), single-covariate OLS (A2), pingouin cross-validation (A3) | 9 | 2+2+3+2 |
| A-6 | Pythia control | Check h-e1 cache; if unavailable skip gracefully; if available compute rho(robustness,log_scale) | 10 | 2+3+3+2 |
| A-7 | Visualization | 4 mandatory figures: gate_metrics, delta_robustness, rho_heatmap (highlight 2 cells), scatter | 12 | 3+2+4+3 |
| A-8 | Results persistence + main | serialize_results, check_gate (PASS/PARTIAL_PASS/FAIL), write JSON, SHOULD_WORK compliance | 8 | 2+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3, A-5, A-6, A-7], Low(4-8): [A-1, A-2, A-4, A-8]

**Total subtask budget**: 69 complexity points across 8 epics (well within 30-task combined limit)

---

## Key Continuity Notes (H-M1 → H-M2)

- `verify_primary_gate`: change index from `[SAFETY_IDX][ETHICS_IDX]` to `[SAFETY_IDX][ROBUSTNESS_IDX]`
- `run_sign_test`: change condition from `delta > 0` to `delta <= 0` (robustness penalty direction)
- `config.RHO_THRESHOLD`: `-0.4` (signed), gate is `rho < RHO_THRESHOLD` (not `abs(rho)`)
- `RESULTS_JSON`: output to `h-m2/experiment_results_h_m2.json` (not `experiment_results_phase3.json`)
- Gate failure must write JSON and print EXPLORE message — never raise or sys.exit
