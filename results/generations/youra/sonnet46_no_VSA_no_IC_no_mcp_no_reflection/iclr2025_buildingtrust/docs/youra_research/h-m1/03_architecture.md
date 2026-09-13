# H-M1 Architecture

**Type**: Post-hoc statistical analysis — no model training, no new inference  
**Input**: H-E1 `experiment_results.json` (already computed)  
**Output**: Sign test results, Fisher's criterion per dimension, 4 figures, gate verdict  
**Runtime**: <1 min on CPU

Applied: binomial sign test + Fisher's criterion pattern (standard nonparametric stats)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Patterns found from base code  
**Analyzed Path**: `docs/youra_research/h-e1/code/`  
**Findings**: H-E1 uses slug keys in `experiment_results.json` (e.g., `"mistralai-Mistral-7B-Instruct-v0.1"`); `model_pairs.json` uses HuggingFace IDs with `/`. H-M1 must translate between these formats.

---

## System Overview

Single-script pipeline:

```
H-E1 experiment_results.json
        ↓
  score_loader  →  extract per-model {bbq, winogender, truthfulqa, winogrande}
        ↓
  pair_builder  →  map model_pairs.json HF IDs → slug keys → [(sft_slug, dpo_slug), ...]×6
        ↓
  delta_computer →  per-pair Δ arrays shape [6] for each benchmark dim
        ↓
  stat_tester   →  binomtest (BBQ primary), Fisher's criterion (all 4 dims)
        ↓
  figure_generator → 4 matplotlib figures → figures/
        ↓
  report_writer  →  04_validation.md gate verdict + tables
```

---

## Component Diagram

```
score_loader ──→ pair_builder ──→ delta_computer
                                       │
                               ┌───────┴────────┐
                          stat_tester    figure_generator
                               │                │
                          report_writer ←────────┘
```

---

## Data Flow

| Stage | Shape / Type | Notes |
|-------|-------------|-------|
| H-E1 JSON → model_scores dict | `{slug: {bbq, winogender_all, truthfulqa_mc2, winogrande}}` | 12 entries |
| Pair list | `[(sft_slug, dpo_slug), ...]` len=6 | built from model_pairs.json slug translation |
| Delta arrays | `np.ndarray` shape `[6]` per dim | `dpo_score - sft_score` |
| Binomial test output | `{k: int, p: float}` per primary/secondary | scipy.stats.binomtest |
| Fisher's criterion | `{dim: float}` for 4 dims | scalar discriminative power |
| Figures | PNG files | 4 files → `figures/` |
| Gate verdict | `{pass: bool, k_bbq: int, p_bbq: float}` | written to 04_validation.md |

---

## File Structure

```
h-m1/
  run_hm1.py          # single analysis script — all logic here
  figures/            # output dir (created at runtime)
    fig1_bbq_paired_bars.png
    fig2_bbq_delta_signed.png
    fig3_fisher_criterion_bars.png
    fig4_winogender_delta_signed.png
  04_validation.md    # gate verdict + result tables (written by run_hm1.py)
```

**No separate modules.** Everything in `run_hm1.py` (~150 lines).

---

## Key Design Decisions

### 1. Score Loading — H-E1 JSON first, inline fallback

```python
H_E1_RESULTS_PATH = "docs/youra_research/h-e1/experiment_results.json"

# Fallback inline dict — extracted from H-E1 experiment_results.json
INLINE_SCORES = {
    "mistralai-Mistral-7B-Instruct-v0.1":        {"bbq": 0.43, "winogender_all": 0.55, "truthfulqa_mc2": 0.5588, "winogrande": 0.75},
    "HuggingFaceH4-zephyr-7b-alpha":             {"bbq": 0.38, "winogender_all": 0.65, "truthfulqa_mc2": 0.5492, "winogrande": 0.73},
    "teknium-OpenHermes-2.5-Mistral-7B":         {"bbq": 0.45, "winogender_all": 0.71, "truthfulqa_mc2": 0.4916, "winogrande": 0.74},
    "allenai-tulu-2-7b":                         {"bbq": 0.45, "winogender_all": 0.63, "truthfulqa_mc2": 0.4815, "winogrande": 0.71},
    "meta-llama-Llama-2-7b-chat-hf":             {"bbq": 0.42, "winogender_all": 0.66, "truthfulqa_mc2": 0.4954, "winogrande": 0.70},
    "mistralai-Mistral-7B-Instruct-v0.3":        {"bbq": 0.40, "winogender_all": 0.63, "truthfulqa_mc2": 0.5591, "winogrande": 0.76},
    "HuggingFaceH4-zephyr-7b-beta":              {"bbq": 0.39, "winogender_all": 0.65, "truthfulqa_mc2": 0.5140, "winogrande": 0.69},
    "allenai-tulu-2-dpo-7b":                     {"bbq": 0.47, "winogender_all": 0.63, "truthfulqa_mc2": 0.5782, "winogrande": 0.71},
    "openchat-openchat_3.5":                     {"bbq": 0.48, "winogender_all": 0.67, "truthfulqa_mc2": 0.4469, "winogrande": 0.77},
    "berkeley-nest-Starling-LM-7B-alpha":        {"bbq": 0.48, "winogender_all": 0.69, "truthfulqa_mc2": 0.4373, "winogrande": 0.77},
    "Intel-neural-chat-7b-v3-1":                 {"bbq": 0.47, "winogender_all": 0.67, "truthfulqa_mc2": 0.5924, "winogrande": 0.76},
    "Intel-neural-chat-7b-v3-3":                 {"bbq": 0.47, "winogender_all": 0.65, "truthfulqa_mc2": 0.6382, "winogrande": 0.73},
}
```

### 2. Model Name Mapping — HF ID to slug

H-E1 `experiment_results.json` keys are slugs (replace `/` with `-`).  
`model_pairs.json` uses HF IDs. Translation: `slug = hf_id.replace("/", "-")`.

```python
# 6 matched pairs — derived from h-e1/code/model_pairs.json
PAIRS = [
    ("mistralai-Mistral-7B-Instruct-v0.1",  "HuggingFaceH4-zephyr-7b-alpha"),
    ("teknium-OpenHermes-2.5-Mistral-7B",   "HuggingFaceH4-zephyr-7b-beta"),
    ("allenai-tulu-2-7b",                   "allenai-tulu-2-dpo-7b"),
    ("meta-llama-Llama-2-7b-chat-hf",       "Intel-neural-chat-7b-v3-1"),
    ("openchat-openchat_3.5",               "berkeley-nest-Starling-LM-7B-alpha"),
    ("mistralai-Mistral-7B-Instruct-v0.3",  "Intel-neural-chat-7b-v3-3"),
]
```

### 3. Statistical Tests

- **Primary**: `scipy.stats.binomtest(k_bbq, n=6, p=0.5, alternative='greater')` — one-sided H1: DPO>SFT
- **Secondary**: Same for WinoGender (exploratory, no gate)
- **Fisher's criterion**: `(mu_dpo - mu_sft)^2 / (var_dpo + var_sft + 1e-8)` for all 4 dims

---

## Interface Contracts

```python
def load_scores(results_path: str) -> dict[str, dict]:
    """
    Returns: {model_slug: {bbq, winogender_all, truthfulqa_mc2, winogrande}}
    Falls back to INLINE_SCORES if results_path not found.
    """

def build_delta_arrays(
    scores: dict[str, dict],
    pairs: list[tuple[str, str]],
    dim: str
) -> np.ndarray:
    """
    Returns: shape [6] float array of (dpo_score - sft_score) for given dim.
    Raises: KeyError if model slug missing from scores.
    """

def run_hm1_analysis(
    scores: dict[str, dict],
    pairs: list[tuple[str, str]]
) -> dict:
    """
    Returns:
      {
        'bbq_k': int,           # primary gate: count of DPO>SFT pairs on BBQ
        'bbq_p': float,         # primary gate: one-sided binomial p-value
        'wg_k':  int,           # secondary
        'wg_p':  float,
        'bbq_deltas':     list[float],   # len=6
        'wg_deltas':      list[float],
        'tqa_deltas':     list[float],
        'wgr_deltas':     list[float],
        'fisher': {             # Fisher's criterion per dim
            'bbq': float, 'winogender_all': float,
            'truthfulqa_mc2': float, 'winogrande': float
        }
      }
    """

def check_gate(results: dict) -> dict:
    """
    Returns: {'pass': bool, 'k_bbq': int, 'p_bbq': float, 'reason': str}
    Gate: k_bbq >= 4 AND p_bbq <= 0.125
    """

def generate_figures(
    scores: dict[str, dict],
    pairs: list[tuple[str, str]],
    results: dict,
    out_dir: str = "docs/youra_research/h-m1/figures"
) -> list[str]:
    """
    Generates 4 figures. Returns list of saved file paths.
    Fig1: Paired bar chart — BBQ and WinoGender DPO vs SFT per pair + group means
    Fig2: Signed bar chart — per-pair BBQ delta (dashed zero line)
    Fig3: Bar chart — Fisher's criterion for all 4 dims
    Fig4: Signed bar chart — per-pair WinoGender delta
    """

def write_validation_report(
    results: dict,
    gate: dict,
    out_path: str = "docs/youra_research/h-m1/04_validation.md"
) -> None:
    """Writes gate verdict + result tables to 04_validation.md."""
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Score loading + pair mapping | load_scores() with JSON→slug translation + fallback inline dict + PAIRS constant | 5 | 2+1+2 |
| A-2 | Delta computation + stat tests | build_delta_arrays() for all 4 dims, binomtest for BBQ+WinoGender, Fisher's criterion | 7 | 2+2+3 |
| A-3 | Figure generation | 4 matplotlib figures saved to figures/ | 8 | 2+2+2+2 |
| A-4 | Report writer + gate check | check_gate() + write 04_validation.md with tables | 5 | 2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3], Low(4-8): [A-1, A-2, A-4]

---

## Failure Modes

| Failure | Symptom | Fix |
|---------|---------|-----|
| H-E1 JSON not found | FileNotFoundError on load | Falls back to INLINE_SCORES automatically |
| Wrong slug key | KeyError in build_delta_arrays | Check slug = hf_id.replace("/", "-"); verify against INLINE_SCORES keys |
| scipy < 1.7 | AttributeError: `binomtest` not found | `binomtest` added in scipy 1.7.0; fallback: `from scipy.stats import binom; p = binom.sf(k-1, n, 0.5)` |
| All deltas ≈ 0 | fisher[dim] ≈ 0, signs random | Score loading returned same model twice — verify PAIRS sft/dpo ordering |
| figures/ not created | FileNotFoundError on save | `os.makedirs(out_dir, exist_ok=True)` at top of generate_figures() |

---

## External Dependencies (Base Hypothesis)

| Module | Key | File Location |
|--------|-----|---------------|
| Score data | `docs/youra_research/h-e1/experiment_results.json` | H-E1 root |
| Pair definitions | `docs/youra_research/h-e1/code/model_pairs.json` | H-E1 code dir |

**Score key in H-E1 JSON**: `model_scores[slug]["bbq"]`, `model_scores[slug]["winogender_all"]`  
**Verified from**: `docs/youra_research/h-e1/experiment_results.json` and `docs/youra_research/h-e1/code/model_pairs.json` (actual files)
