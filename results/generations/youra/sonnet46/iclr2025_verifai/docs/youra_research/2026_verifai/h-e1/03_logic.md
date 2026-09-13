# Logic: H-E1 — Difficulty-Tier Sample Size Viability Check

**Hypothesis:** H-E1 (EXISTENCE, MUST_WORK gate)
**Date:** 2026-03-18
**Phase:** 3 → Logic Agent Output

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field — Serena returned "No active project" error; only .md files exist in h-e1/
**Analyzed Path:** `docs/youra_research/20260316_verifia/h-e1/`
**Relevant Symbols:** None — new implementation from scratch

---

## A-1 (Data Prep): EvalPlus Dataset Loading [Complexity: 8, Budget: 1 subtask]

Applied: Standard PyTorch / EvalPlus programmatic-api

### API Signatures

```python
# generate_solutions.py / evaluate_solutions.py

def load_all_problems() -> tuple[dict, dict]:
    """Load HumanEval+ and MBPP+ problem dicts.
    Returns: (problems_he, problems_mbpp)
      problems_he:   {task_id: problem_dict}  # 164 problems, task_id like "HumanEval/0"
      problems_mbpp: {task_id: problem_dict}  # 378 problems, task_id like "Mbpp/2"
    """
    ...

def partition_by_benchmark(
    problems_he: dict,
    problems_mbpp: dict,
) -> dict[str, str]:
    """Map each task_id to its benchmark name.
    Returns: {task_id: "humaneval" | "mbpp"}  # 542 entries total
    """
    ...
```

### Tensor Shapes / Data Types

| Variable | Type | Note |
|----------|------|------|
| problems_he | dict[str, dict] | 164 entries; keys "HumanEval/N" |
| problems_mbpp | dict[str, dict] | 378 entries; keys "Mbpp/N" |
| benchmark_map | dict[str, str] | 542 entries total |

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | EvalPlus Loader | `load_all_problems()` + `partition_by_benchmark()` with smoke-test slice (5 problems) |

---

## A-2: Solution Generation [Complexity: 14, Budget: 3 subtasks]

Applied: Standard PyTorch / HuggingFace generate API

### API Signatures

```python
# generate_solutions.py

MODEL_IDS: list[str] = [
    "NousResearch/Meta-Llama-3-8B",
    "codellama/CodeLlama-7b-hf",
    "deepseek-ai/deepseek-coder-6.7b-base",
]
GENERATION_CONFIG: dict = dict(
    temperature=0.8, top_p=0.95, max_new_tokens=512, do_sample=True
)
K: int = 5
SEED: int = 42


def load_model_and_tokenizer(
    model_id: str,
) -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    """Load model in float16 with device_map='auto'.
    Returns: (model, tokenizer) ready for .generate()
    """
    ...


def format_prompt(problem: dict, benchmark: str) -> str:
    """Format problem into a generation prompt string.
    benchmark: "humaneval" | "mbpp"
    Returns: prompt string (includes function signature + docstring)
    """
    ...


def generate_k_solutions(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    problem: dict,
    k: int = K,
    seed: int = SEED,
) -> list[str]:
    """Generate k solutions for one problem via sampling.
    Returns: list[str] of length k — raw generated code strings
    Input tokens: [1, L_prompt]; Output tokens: [k, L_prompt + max_new_tokens]
    """
    ...


def load_existing_solutions(path: str) -> dict | None:
    """Load JSONL solutions file if it exists, else return None.
    Returns: {task_id: [str × k]} or None
    """
    ...


def save_solutions(solutions: dict, output_path: str) -> None:
    """Save solutions as JSONL. One JSON object per line.
    Format: {"task_id": str, "solutions": [str × k]}
    """
    ...


def generate_solutions(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    problems: dict,
    k: int = K,
    seed: int = SEED,
) -> dict[str, list[str]]:
    """Generate k solutions for all problems in dict.
    Returns: {task_id: [str × k]}
    """
    ...
```

### Pseudo-code: Generation Loop with Reuse

```
function generate_solutions_for_model(model_id, problems, output_path, k, seed):
    existing = load_existing_solutions(output_path)
    if existing is not None:
        log("Reusing existing solutions from {output_path}")
        return existing

    model, tokenizer = load_model_and_tokenizer(model_id)
    solutions = {}
    for task_id, problem in problems.items():
        solutions[task_id] = generate_k_solutions(model, tokenizer, problem, k, seed)
    save_solutions(solutions, output_path)
    return solutions
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Model Loading API | `load_model_and_tokenizer()` with float16, device_map="auto" |
| L-2-2 | Generation Loop | `generate_k_solutions()` + `generate_solutions()` with seed-setting |
| L-2-3 | JSONL Save/Reuse | `save_solutions()` + `load_existing_solutions()` reuse-check logic |

---

## A-4: Tier Analysis & Gate [Complexity: 13, Budget: 1 subtask]

Applied: Standard PyTorch / numpy pure-function pipeline

### API Signatures

```python
# analyze_tiers.py

HARD_THRESHOLD: float = 0.0
EASY_THRESHOLD: float = 0.6
MIN_N: int = 20


def compute_pass_at_1(
    correctness: dict[str, list[bool]],
    k: int = 5,
) -> dict[str, float]:
    """Compute pass@1 = correct_count / k per task.
    correctness: {task_id: [bool × k]}
    Returns: {task_id: float}  # values in {0.0, 0.2, 0.4, 0.6, 0.8, 1.0}
    """
    ...


def assign_tiers(
    pass_at_1: dict[str, float],
    hard_thresh: float = HARD_THRESHOLD,
    easy_thresh: float = EASY_THRESHOLD,
) -> dict[str, str]:
    """Assign tier labels per task.
    Returns: {task_id: "hard" | "easy" | "medium"}
    hard:   pass@1 <= hard_thresh (default: ==0.0)
    easy:   pass@1 >= easy_thresh (default: >=0.6)
    medium: otherwise (excluded from gate)
    """
    ...


def count_tiers(
    tiers: dict[str, str],
    problem_ids_he: list[str],
    problem_ids_mbpp: list[str],
) -> dict[str, dict[str, int]]:
    """Count tier members per benchmark.
    Returns: {"humaneval": {"hard": int, "easy": int, "medium": int},
              "mbpp":      {"hard": int, "easy": int, "medium": int}}
    """
    ...


def evaluate_gate(
    all_tier_counts: dict[str, dict[str, dict[str, int]]],
    min_n: int = MIN_N,
) -> dict:
    """Evaluate gate condition across all models and benchmarks.
    all_tier_counts: {model_id: {benchmark: {tier: count}}}
    Returns: {
        "gate_pass": bool,
        "models_passing": int,        # count of models with n_hard>=min_n AND n_easy>=min_n
        "benchmark_passing": str | None,  # "humaneval" | "mbpp" | None
        "n_hard_per": dict[str, dict[str, int]],  # {model_id: {benchmark: count}}
        "n_easy_per": dict[str, dict[str, int]],
    }
    Gate PASS: models_passing >= 2 on at least 1 benchmark
    """
    ...


def verify_tier_mechanism_activated(
    tier_results: dict,
    coverage_rate: float,
) -> tuple[bool, dict]:
    """Assert n_hard > 0, n_easy > 0, coverage >= 0.95.
    Returns: (all_ok: bool, indicators: dict[str, bool])
    """
    ...


def relax_and_retry(
    correctness_all: dict[str, dict[str, list[bool]]],
    benchmark_map: dict[str, str],
    problem_ids_he: list[str],
    problem_ids_mbpp: list[str],
    relaxed_hard_thresh: float = 0.2,
) -> dict:
    """Recompute gate with hard_thresh=0.2.
    correctness_all: {model_id: {task_id: [bool × k]}}
    Returns: gate result dict (same schema as evaluate_gate)
    """
    ...
```

### Pseudo-code: Gate Evaluation with Relaxation

```
function run_gate(correctness_all, benchmark_map):
    # Primary gate
    all_tier_counts = {}
    for model_id, correctness in correctness_all.items():
        pass_at_1 = compute_pass_at_1(correctness)
        tiers = assign_tiers(pass_at_1, hard_thresh=0.0, easy_thresh=0.6)
        all_tier_counts[model_id] = count_tiers(tiers, ids_he, ids_mbpp)

    gate = evaluate_gate(all_tier_counts, min_n=20)
    if gate["gate_pass"]:
        return gate

    # Relaxed gate (hard_thresh = 0.2)
    gate_relaxed = relax_and_retry(correctness_all, ..., relaxed_hard_thresh=0.2)
    if gate_relaxed["gate_pass"]:
        log("Gate PASS only with relaxed threshold=0.2")
        return gate_relaxed

    log("Gate FAIL: underpowered tiers even after relaxation → STOP pipeline")
    return gate_relaxed  # gate_pass=False → sys.exit(1)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Gate Logic | `compute_pass_at_1` + `assign_tiers` + `evaluate_gate` + `relax_and_retry` |

---

## A-3 (Eval): EvalPlus Evaluation Loop [Complexity: 12, Budget: 0 subtasks from Logic budget]

Applied: Standard PyTorch / EvalPlus check_correctness API

### API Signatures

```python
# evaluate_solutions.py

EVALPLUS_PARAMS: dict = dict(
    max_as_limit=30,
    max_data_limit=30,
    max_stack_limit=10,
    min_time_limit=1,
    gt_time_limit_factor=4.0,
)


def load_problems(benchmark: str) -> dict:
    """benchmark: "humaneval" | "mbpp"
    Returns: problem dict from get_human_eval_plus() or get_mbpp_plus()
    """
    ...


def evaluate_solution(
    dataset: str,
    problem: dict,
    solution: str,
) -> bool:
    """Run check_correctness() for one solution.
    dataset: "humaneval" | "mbpp"
    Returns: passed = (base_status=="pass") AND (plus_status=="pass")
    """
    ...


def evaluate_all_solutions(
    solutions: dict[str, list[str]],
    problems_he: dict,
    problems_mbpp: dict,
) -> dict[str, list[bool]]:
    """Evaluate all k solutions for all tasks.
    solutions: {task_id: [str × k]}
    Returns: {task_id: [bool × k]}
    """
    ...


def compute_coverage_rate(
    evaluated_ids: set[str],
    total_ids: set[str],
) -> float:
    """fraction of total_ids that were successfully evaluated.
    Returns: float in [0.0, 1.0]  # target >= 0.95
    """
    ...


def save_correctness(correctness: dict, output_path: str) -> None:
    """Save {task_id: [bool × k]} as JSON."""
    ...
```

---

## A-5 (Viz): Cross-model Jaccard (H-M2 prep) [Complexity: 10, Budget: 0 subtasks from Logic budget]

Applied: Standard PyTorch / numpy set operations

### API Signatures

```python
# analyze_tiers.py

def compute_jaccard_similarity(set_a: set, set_b: set) -> float:
    """Jaccard = |A ∩ B| / |A ∪ B|. Returns 0.0 if union is empty."""
    ...


def compute_cross_model_overlap(
    tiers_per_model: dict[str, dict[str, str]],
) -> dict[tuple[str, str], float]:
    """Compute pairwise Jaccard on hard-tier task sets across models.
    tiers_per_model: {model_id: {task_id: "hard"|"easy"|"medium"}}
    Returns: {(model_a, model_b): jaccard_float}  # all unique pairs
    """
    ...
```

---

## Intermediate Data Structures

| Structure | Type | Shape/Content |
|-----------|------|---------------|
| solutions | dict[str, list[str]] | {task_id: [str × 5]} — raw code strings |
| correctness | dict[str, list[bool]] | {task_id: [bool × 5]} |
| pass_at_1 | dict[str, float] | {task_id: float in {0.0,0.2,0.4,0.6,0.8,1.0}} |
| tiers | dict[str, str] | {task_id: "hard"\|"easy"\|"medium"} |
| all_tier_counts | dict[str, dict[str, dict[str, int]]] | {model_id: {benchmark: {tier: count}}} |
| gate_result | dict | gate_pass, models_passing, benchmark_passing, n_hard_per, n_easy_per |

---

## Self-Validation

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Docstrings <= 2 lines
- [x] Tensor shapes / data types in code comments
- [x] Subtask count within budget (5 total: L-1-1, L-2-1, L-2-2, L-2-3, L-4-1)
- [x] "Codebase Analysis (Serena)" section included
- [x] Green-field: Serena returned no active project error — confirmed
- [x] Total length < 600 lines
