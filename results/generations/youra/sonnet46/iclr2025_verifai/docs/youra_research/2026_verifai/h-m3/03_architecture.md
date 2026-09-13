# Architecture: h-m3 — P(True) Confidence Elicitation via Logprob Extraction

**Hypothesis ID:** h-m3
**Type:** MECHANISM (MUST_WORK)
**Gate:** std(c) > 0.05 for ALL 3 models

Applied: inference-only sequential logprob extraction pattern (Kadavath 2022 / HF PR #28667)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code (Read fallback — Serena project activation not required)
**Analyzed Path**: `docs/youra_research/20260316_verifia/h-m2/code/src/h_m2/`
**Findings**: h-m2 uses `src/h_m2/` package layout with pyproject.toml + setuptools. Entry point is `run_hm2_stratification.py` (argparse CLI). Modules: `stratify.py`, `evaluate.py`, `jaccard.py`, `analyze.py`, `visualize_hm2.py`. Constants (`MODEL_IDS`, `MODEL_SHORT_NAMES`) defined in `stratify.py` — h-m3 reuses identical constants and path conventions.

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| MODEL_IDS | `from h_m2.stratify import MODEL_IDS` | `h-m2/code/src/h_m2/stratify.py` |
| MODEL_SHORT_NAMES | `from h_m2.stratify import MODEL_SHORT_NAMES` | `h-m2/code/src/h_m2/stratify.py` |

**Note**: h-m3 does NOT import h-m2 package directly. Constants are copied/redefined in `config.py`. Input files read from `../h-m2/results/` and `../h-m1/results/` via path arguments.

**Verified from**: `h-m2/code/src/h_m2/stratify.py`, `h-m2/code/src/h_m2/evaluate.py` (actual implementation)

---

## File Organization

```
h-m3/code/
  src/h_m3/
    __init__.py
    config.py          # constants, model IDs, paths, thresholds
    data_loader.py     # tier CSV + solution JSONL + EvalPlus loader
    ptrue_extractor.py # P(True) logprob extraction core
    evaluate.py        # gate metrics + secondary stats
    visualize.py       # 5 figures
    run_hm3_ptrue.py   # CLI orchestrator (entry point)
  tests/
    __init__.py
    test_data_loader.py
    test_ptrue_extractor.py
    test_evaluate.py
  pyproject.toml
  requirements.txt
results/
  ptrue_confidence_scores.json
  ptrue_hm3_verified.json
figures/
  fig1_gate_check.png
  fig2_c_histograms.png
  fig3_c_vs_pass_at_1.png
  fig4_c_by_tier.png
  fig5_c_cdf.png
```

---

## Module Definitions

### Config (`src/h_m3/config.py`)

**Dependencies**: none

```python
MODEL_IDS: list[str]           # 3 HF model IDs
MODEL_SHORT_NAMES: dict[str, str]  # model_id -> short name
HARD_THRESHOLD: float          # 0.0
EASY_THRESHOLD: float          # 0.6
STD_GATE_THRESHOLD: float      # 0.05
PTRUE_PROMPT_TEMPLATE: str     # zero-shot P(True) prompt
PTRUE_PROMPT_FALLBACK: str     # alternative prompt (FR-9)
MAX_NEW_TOKENS: int            # 1
SEED: int                      # 42
CHECKPOINT_INTERVAL: int       # 100
```

---

### DataLoader (`src/h_m3/data_loader.py`)

**Dependencies**: config

```python
def load_tier_assignments(hm2_results_dir: Path) -> pd.DataFrame:
    """Load tier_assignments.csv; returns DataFrame[problem_id, model, tier, pass_at_1]."""
    ...

def filter_hard_easy_tiers(df: pd.DataFrame) -> pd.DataFrame:
    """Filter rows where tier in {hard, easy}."""
    ...

def load_solutions_jsonl(hm1_results_dir: Path, model_short: str) -> dict[str, list[dict]]:
    """Load solutions_{model_short}.jsonl; returns {task_id: [solution_dict×5]}."""
    ...

def load_evalplus_problems() -> dict[str, dict]:
    """Load HumanEval+ and MBPP+ via evalplus; returns {task_id: {prompt, ...}}."""
    ...

def build_pair_iterator(
    tier_df: pd.DataFrame,
    solutions: dict[str, dict[str, list[dict]]],
    problems: dict[str, dict],
) -> list[dict]:
    """Build flat list of (model, task_id, tier, pass_at_1, solution_code, problem_prompt) dicts."""
    ...
```

---

### PtrueExtractor (`src/h_m3/ptrue_extractor.py`)

**Dependencies**: config

```python
def load_model_and_tokenizer(
    model_id: str,
    device: str,
) -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    """Load model in float16 with device_map='auto'."""
    ...

def get_true_false_token_ids(
    tokenizer: AutoTokenizer,
) -> tuple[int, int]:
    """Return (true_id, false_id) for ' True' and ' False' tokens."""
    ...

def extract_ptrue_confidence(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    problem_prompt: str,
    solution_code: str,
    device: str,
    true_id: int,
    false_id: int,
    prompt_template: str,
) -> float:
    """Return c in [0,1]: softmax([logp_true, logp_false])[0] via output_logits=True."""
    ...

def run_ptrue_inference_for_model(
    model_id: str,
    pairs: list[dict],
    device: str,
    checkpoint_path: Path,
    prompt_template: str,
    checkpoint_interval: int,
) -> dict[str, dict]:
    """Run P(True) extraction for all pairs of one model; returns {task_id: {tier, pass_at_1, confidence_scores, correctness_labels}}."""
    ...

def verify_ptrue_mechanism(
    confidence_scores_by_model: dict[str, list[float]],
    out_logits_sample: list,
) -> tuple[bool, dict]:
    """Check 4 mechanism activation indicators (FR-8)."""
    ...
```

---

### Evaluate (`src/h_m3/evaluate.py`)

**Dependencies**: config

```python
def compute_gate_metrics(
    confidence_scores_by_model: dict[str, list[float]],
) -> dict[str, dict]:
    """Compute std(c) and mean(c) per model; returns {model_short: {std_c, mean_c, n_pairs, gate_pass}}."""
    ...

def evaluate_gate(
    gate_metrics: dict[str, dict],
    threshold: float,
) -> tuple[bool, dict]:
    """MUST_WORK gate: std(c) > threshold for ALL 3 models."""
    ...

def compute_secondary_metrics(
    confidence_scores_by_model: dict[str, list[float]],
    correctness_by_model: dict[str, list[int]],
    tiers_by_model: dict[str, list[str]],
) -> dict[str, dict]:
    """Compute min/max(c), 20-bin histogram, tier-stratified mean/std, point-biserial correlation."""
    ...

def build_verified_results(
    gate_metrics: dict[str, dict],
    gate_pass: bool,
    gate_detail: dict,
    secondary_metrics: dict,
) -> dict:
    """Assemble ptrue_hm3_verified.json payload (FR-10 schema)."""
    ...
```

---

### Visualize (`src/h_m3/visualize.py`)

**Dependencies**: evaluate

```python
def plot_gate_check(
    gate_metrics: dict[str, dict],
    threshold: float,
    out_path: Path,
) -> None:
    """Fig 1: Bar chart std(c) per model vs. threshold line."""
    ...

def plot_c_histograms(
    confidence_scores_by_model: dict[str, list[float]],
    out_path: Path,
) -> None:
    """Fig 2: 3-subplot histogram (20 bins) per model."""
    ...

def plot_c_vs_pass_at_1(
    confidence_scores_by_model: dict[str, list[float]],
    correctness_by_model: dict[str, list[int]],
    out_path: Path,
) -> None:
    """Fig 3: Scatter c vs. correctness label per model."""
    ...

def plot_c_by_tier(
    confidence_by_model_tier: dict[str, dict[str, list[float]]],
    out_path: Path,
) -> None:
    """Fig 4: Box plots c by model × tier (hard vs. easy)."""
    ...

def plot_c_cdf(
    confidence_scores_by_model: dict[str, list[float]],
    out_path: Path,
) -> None:
    """Fig 5: CDF per model."""
    ...
```

---

### Orchestrator (`src/h_m3/run_hm3_ptrue.py`)

**Dependencies**: config, data_loader, ptrue_extractor, evaluate, visualize

```python
def parse_args() -> argparse.Namespace:
    """CLI: --hm1_results_dir, --hm2_results_dir, --output_dir, --figures_dir, --device, --smoke_test, --fallback_prompt."""
    ...

def main() -> int:
    """
    Entry point. Exit codes: 0=gate PASS, 1=gate FAIL, 2=runtime error.
    Steps:
      1. Load tier assignments + solutions + EvalPlus problems
      2. For each model: run_ptrue_inference_for_model()
      3. verify_ptrue_mechanism()
      4. compute_gate_metrics() + evaluate_gate()
      5. If gate FAIL and not fallback: retry with PTRUE_PROMPT_FALLBACK
      6. compute_secondary_metrics()
      7. Save ptrue_confidence_scores.json + ptrue_hm3_verified.json
      8. Generate 5 figures
    """
    ...

if __name__ == "__main__":
    sys.exit(main())
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | pyproject.toml, package structure, config.py constants, requirements.txt | 5 | 1+1+1+2 |
| A-2 | Data Loader | load_tier_assignments, load_solutions_jsonl, load_evalplus_problems, build_pair_iterator | 10 | 2+2+3+3 |
| A-3 | Model Loader | load_model_and_tokenizer float16, get_true_false_token_ids, startup logging | 9 | 2+2+3+2 |
| A-4 | P(True) Extractor Core | extract_ptrue_confidence via output_logits=True max_new_tokens=1, normalization | 14 | 3+3+4+4 |
| A-5 | Inference Loop + Checkpointing | run_ptrue_inference_for_model with progress save every 100 pairs, resume logic | 13 | 3+3+4+3 |
| A-6 | Mechanism Verification | verify_ptrue_mechanism 4 indicators, fallback prompt retry logic (FR-8/FR-9) | 11 | 2+3+3+3 |
| A-7 | Gate Evaluation | compute_gate_metrics, evaluate_gate MUST_WORK, build_verified_results FR-10 schema | 10 | 2+2+3+3 |
| A-8 | Secondary Metrics | point-biserial correlation, tier-stratified stats, min/max/histogram | 9 | 2+2+3+2 |
| A-9 | Visualization | 5 figures (fig1–fig5) with matplotlib | 9 | 2+2+2+3 |
| A-10 | CLI Orchestrator | run_hm3_ptrue.py argparse, full pipeline wiring, exit codes | 10 | 2+3+3+2 |
| A-11 | Tests | test_data_loader, test_ptrue_extractor (mock model), test_evaluate | 8 | 2+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-4], Medium(9-13): [A-2, A-3, A-5, A-6, A-7, A-8, A-9, A-10], Low(4-8): [A-1, A-11]

---

## Data Flow

- `tier_assignments.csv` (h-m2) → DataLoader → filtered pairs
- `solutions_{model}.jsonl` (h-m1) → DataLoader → solution strings
- EvalPlus API → DataLoader → problem prompts
- pairs + prompts + model → PtrueExtractor → `{task_id: {confidence_scores, correctness_labels}}`
- confidence_scores → Evaluate → gate_metrics → gate PASS/FAIL
- confidence_scores → Visualize → 5 figures
- gate_metrics + secondary_metrics → `ptrue_hm3_verified.json`

---

## NFR Notes

- float16, device_map="auto", single GPU (CUDA_VISIBLE_DEVICES set by caller)
- seed=42, greedy decoding (do_sample=False)
- transformers >= 4.38.0 required for output_logits=True
- Checkpoint every 100 pairs → resume on restart
- Smoke test mode: 2 problems × 1 solution per model
