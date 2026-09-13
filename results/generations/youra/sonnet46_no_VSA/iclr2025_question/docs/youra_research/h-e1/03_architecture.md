# Architecture: H-E1 Conditional Independence of SE_N5 and min_logprob

**Version:** 1.0
**Date:** 2026-08-02
**Hypothesis:** H-E1 (EXISTENCE / MUST_WORK)
**Type:** Diagnostic experiment — no model training

Applied: Standard ML inference + statistical testing pipeline

---

## Codebase Analysis (Serena)

**Project Type**: existing_codebase (archived prior h-e1 implementations)
**Status**: Patterns found from archived code
**Analyzed Path**: `docs/youra_research/_archive/20260802T151858_routing_recovery/h-e1/code/`
**Findings**: Prior archived attempt used `generate.py`, `compute_signals.py`, `analyze.py`, `config.py`, `run_experiment.py`. That version computed selfcheck (not min_logprob). New implementation reuses the same file layout and adapts for min_logprob + LM-judge correctness labeling.

---

## File Organization

```
docs/youra_research/h-e1/code/
├── config.py           # constants, paths, model IDs
├── generate.py         # stochastic N=5 + greedy generation
├── compute_signals.py  # SE_N5 + min_logprob computation
├── judge.py            # Qwen-2.5-7B-Instruct LM-as-a-judge labeling
├── stats_analysis.py   # Pearson r, conditional LR, partial R², gate eval
├── visualize.py        # 4 required figures
└── main.py             # orchestration entry point
```

Figures output: `docs/youra_research/h-e1/figures/`

---

## Modules

### config (`code/config.py`)

**Dependencies**: none

```python
DATASET_ID: str = "mandarjoshi/trivia_qa"
DATASET_CONFIG: str = "rc.nocontext"
DATASET_SPLIT: str = "validation"
N_PROMPTS: int = 2500
SEED: int = 42

LLM_ID: str = "meta-llama/Llama-3.1-8B-Instruct"
NLI_ID: str = "cross-encoder/nli-deberta-v3-small"
JUDGE_ID: str = "Qwen/Qwen2.5-7B-Instruct"

N_SAMPLES: int = 5          # stochastic samples for SE_N5
TEMPERATURE: float = 0.7
TOP_P: float = 0.95
MAX_NEW_TOKENS: int = 50

CHECKPOINT_PATH: str = "docs/youra_research/h-e1/results/signals.pkl"
RESULTS_PATH: str = "docs/youra_research/h-e1/results/stats.json"
FIGURES_DIR: str = "docs/youra_research/h-e1/figures"

# Gate thresholds
PEARSON_R_THRESHOLD: float = 0.7
PARTIAL_R2_THRESHOLD: float = 0.02
CIRCULARITY_THRESHOLD: float = 0.4
ABANDON_THRESHOLD: float = 0.85
```

---

### generate (`code/generate.py`)

**Dependencies**: config, transformers, datasets

```python
def load_dataset_slice(seed: int = SEED, n: int = N_PROMPTS) -> list[dict]: ...
# Returns list of {"question": str, "aliases": list[str]}

def load_llm(model_id: str = LLM_ID) -> tuple:
    # Returns (model, tokenizer) loaded with bfloat16, device_map="auto"
    ...

def generate_stochastic(
    model, tokenizer, questions: list[str],
    n_samples: int = N_SAMPLES,
    temperature: float = TEMPERATURE
) -> list[list[str]]: ...
# Returns shape (N_PROMPTS, N_SAMPLES) — 5 response strings per prompt

def generate_greedy(
    model, tokenizer, questions: list[str]
) -> tuple[list[str], list[list[float]]]: ...
# Returns (greedy_answers, token_logprobs_per_prompt)
# Asserts output_scores available; fails fast if not
```

---

### compute_signals (`code/compute_signals.py`)

**Dependencies**: config, numpy, transformers

```python
def load_nli_model(model_id: str = NLI_ID): ...
# Returns sentence_transformers CrossEncoder or HF pipeline

def check_implication(text1: str, text2: str, nli_model) -> int: ...
# Returns 0=contradiction, 1=neutral, 2=entailment

def get_semantic_ids(responses: list[str], nli_model) -> list[int]: ...
# Bidirectional NLI clustering; non-strict mode
# Adapted from jlko/semantic_uncertainty

def cluster_assignment_entropy(semantic_ids: list[int]) -> float: ...
# SE = -sum(p_k * log(p_k))

def compute_se_n5(
    stochastic_responses: list[list[str]], nli_model
) -> np.ndarray: ...
# shape (N_PROMPTS,); asserts var > 0.01

def compute_min_logprob(
    token_logprobs_per_prompt: list[list[float]]
) -> np.ndarray: ...
# shape (N_PROMPTS,); asserts all values < 0

def compute_response_lengths(greedy_answers: list[str]) -> np.ndarray: ...
# token count; shape (N_PROMPTS,)

def verify_signals(
    se_scores: np.ndarray,
    min_logprob_scores: np.ndarray
) -> None: ...
# Asserts: var(se) > 0.01, all(min_logprob < 0), len == N_PROMPTS; raises on fail
```

---

### judge (`code/judge.py`)

**Dependencies**: config, transformers

```python
def load_judge(model_id: str = JUDGE_ID) -> tuple: ...
# Returns (model, tokenizer); must differ from LLM_ID family

JUDGE_PROMPT: str = (
    "Is the following answer correct for the question? Answer YES or NO.\n"
    "Question: {question}\nAnswer: {answer}\nCorrect?"
)

def label_correctness(
    model, tokenizer,
    questions: list[str],
    greedy_answers: list[str],
    aliases_list: list[list[str]]
) -> np.ndarray: ...
# Returns binary labels shape (N_PROMPTS,) dtype int
# Primary: parses YES/NO from judge output
# Fallback: exact string match against aliases
```

---

### stats_analysis (`code/stats_analysis.py`)

**Dependencies**: numpy, scipy, scikit-learn

```python
def run_pearson(
    se_scores: np.ndarray, min_logprob_scores: np.ndarray
) -> tuple[float, float]: ...
# Returns (r, p_value)

def run_spearman_circularity(
    se_scores: np.ndarray, correctness: np.ndarray
) -> tuple[float, float]: ...
# Returns (rho, p_value)

def run_conditional_lr(
    se_scores: np.ndarray,
    min_logprob_scores: np.ndarray,
    response_lengths: np.ndarray,
    correctness: np.ndarray
) -> dict: ...
# Returns {ll_full, ll_reduced, partial_r2_se, coefs_full, coefs_reduced, lrt_p}
# Full model: [min_logprob, SE, L, SE*min_logprob]
# Reduced model: [min_logprob, L]
# partial_r2 = 1 - (ll_full / ll_reduced)  # McFadden-style

def evaluate_gate(pearson_r: float, partial_r2: float) -> dict: ...
# Returns {gate_pass, decision, pearson_r, partial_r2}
# decision in {"PASS", "EXPLORE_N10", "ABANDON"}

def run_all(
    se_scores: np.ndarray,
    min_logprob_scores: np.ndarray,
    response_lengths: np.ndarray,
    correctness: np.ndarray
) -> dict: ...
# Orchestrates pearson + circularity + conditional_lr + gate; returns merged dict
```

---

### visualize (`code/visualize.py`)

**Dependencies**: config, matplotlib, seaborn, numpy

```python
def plot_gate_metrics(pearson_r: float, partial_r2: float, out_dir: str) -> None: ...
# Bar chart: |r| vs 0.7 threshold, partial R² vs 0.02 threshold

def plot_scatter(
    se_scores: np.ndarray,
    min_logprob_scores: np.ndarray,
    correctness: np.ndarray,
    out_dir: str
) -> None: ...
# 2500-point scatter SE_N5 vs min_logprob, colored by correctness

def plot_correlation_heatmap(
    se_scores: np.ndarray,
    min_logprob_scores: np.ndarray,
    response_lengths: np.ndarray,
    correctness: np.ndarray,
    out_dir: str
) -> None: ...
# Seaborn heatmap of [SE_N5, min_logprob, response_length, correctness]

def plot_lr_coefficients(stats: dict, out_dir: str) -> None: ...
# Bar chart of β coefficients with 95% CI for full LR model

def save_all(
    se_scores: np.ndarray,
    min_logprob_scores: np.ndarray,
    response_lengths: np.ndarray,
    correctness: np.ndarray,
    stats: dict,
    out_dir: str = FIGURES_DIR
) -> None: ...
# Calls all four plot functions
```

---

### main (`code/main.py`)

**Dependencies**: all modules above, pickle, json, pathlib

```python
def load_or_generate(force: bool = False) -> dict: ...
# Loads checkpoint if exists, else runs generate + compute_signals + judge
# Saves to CHECKPOINT_PATH to avoid re-running 15K inference calls

def main() -> None: ...
# 1. load_or_generate()
# 2. verify_signals()
# 3. run_all() → stats
# 4. evaluate_gate()
# 5. save_all() figures
# 6. print gate result + decision

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

### Epic E1: Setup & Data Loading
**Complexity:** 5/20 (Module_Size=1 + Dependencies=1 + Algorithm=1 + Integration=2)
**Description:** Implement `config.py` with all constants, paths, and thresholds. Implement `load_dataset_slice()` in `generate.py`. Verify 2500 samples loaded correctly with seed=42. Create output directories.
**Files:** `code/config.py`, `code/generate.py` (load_dataset_slice only)
**Estimated effort:** 1h

---

### Epic E2: LLM Generation (Stochastic + Greedy)
**Complexity:** 14/20 (Module_Size=3 + Dependencies=3 + Algorithm=3 + Integration=5)
**Description:** Load Llama-3.1-8B-Instruct; run stochastic generation (N=5, temp=0.7) for all 2500 prompts; run greedy decode with `output_scores=True` to extract per-token log-probs. Checkpoint results. Fail fast if `output_scores` unavailable.
**Files:** `code/generate.py`
**Estimated effort:** 4h

---

### Epic E3: Signal Computation (SE_N5 + min_logprob)
**Complexity:** 14/20 (Module_Size=3 + Dependencies=3 + Algorithm=4 + Integration=4)
**Description:** Load `cross-encoder/nli-deberta-v3-small`; implement `get_semantic_ids()` (bidirectional NLI, non-strict) adapted from jlko/semantic_uncertainty; compute `cluster_assignment_entropy()` for SE_N5; compute `min_logprob` from greedy token scores. Run `verify_signals()` assertions.
**Files:** `code/compute_signals.py`
**Estimated effort:** 3h

---

### Epic E4: LM-Judge Correctness Labeling
**Complexity:** 10/20 (Module_Size=2 + Dependencies=2 + Algorithm=3 + Integration=3)
**Description:** Load Qwen-2.5-7B-Instruct; format judge prompt; parse YES/NO responses; fall back to alias string-match. Produce binary correctness labels for 2500 prompts. Assert judge family differs from generator family.
**Files:** `code/judge.py`
**Estimated effort:** 2h

---

### Epic E5: Statistical Analysis & Gate Evaluation
**Complexity:** 11/20 (Module_Size=2 + Dependencies=2 + Algorithm=4 + Integration=3)
**Description:** Compute Pearson r(SE_N5, min_logprob); Spearman ρ(SE, correctness) circularity check; conditional logistic regression (full vs reduced); McFadden partial R²; LRT p-value; gate decision (PASS / EXPLORE_N10 / ABANDON). Save results JSON.
**Files:** `code/stats_analysis.py`
**Estimated effort:** 2h

---

### Epic E6: Visualization & Orchestration
**Complexity:** 8/20 (Module_Size=2 + Dependencies=2 + Algorithm=1 + Integration=3)
**Description:** Implement all 4 figures (gate metrics bar, scatter, correlation heatmap, LR coefficient bar). Wire `main.py` orchestration with checkpoint load/save, signal verification, stats, figures, and printed gate decision.
**Files:** `code/visualize.py`, `code/main.py`
**Estimated effort:** 2h

---

**Distribution**: High(14-17): [E2, E3], Medium(9-13): [E4, E5], Low(4-8): [E1, E6]

**Total estimated effort:** ~14h
