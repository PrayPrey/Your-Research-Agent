# Logic: H-M2 DiD Semantic Sensitivity

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: API signatures verified from actual H-E1 code (not from PRD pseudo-code, which uses different field names)
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Relevant Symbols**: `load_base_model`, `wrap_lora` (model.py); `execute_and_get_feedback`, `single_shot` (refine.py); `load_humaneval_plus` (data.py); `compute_pass_at_1` (evaluate.py); `Config` (config.py)

**Key deviations from PRD pseudo-code**:
- Problems are `dict[task_id -> problem_dict]`, not objects with `.prompt`/`.tests`. Tests are built from `problem["base_input"]` + `problem["entry_point"]`, not a pre-built `tests` list.
- `execute_and_get_feedback(code, tests) -> (pass_rate: float, error_msg: str)`, not a `result` object with `.passed`/`.failed_test`.
- LoRA checkpoints loaded via `PeftModel.from_pretrained(base_model, checkpoint_dir)`, not `AutoModelForSeq2SeqLM.from_pretrained(checkpoint_dir)` directly (H-E1 uses adapters, not merged weights).
- `Config.refine_k` exists but H-M2 needs **K=1** override (PRD requirement) — pass `refine_k=1` explicitly, do not use H-E1 default of 3.

---

## External Dependencies (Base Hypothesis)

```python
# From: docs/youra_research/h-e1/code/model.py (ACTUAL CODE)
def load_base_model(cfg: Config) -> tuple[PreTrainedModel, PreTrainedTokenizerBase]: ...
def wrap_lora(model: PreTrainedModel, cfg: Config) -> PeftModel: ...

# From: docs/youra_research/h-e1/code/refine.py (ACTUAL CODE)
def execute_and_get_feedback(code: str, tests: list[str]) -> tuple[float, str]:
    """Returns (pass_rate, error_msg). error_msg = stderr[:500] or 'Timeout'/'No tests provided'."""
def single_shot(model, tokenizer, prompt: str, cfg: Config) -> str: ...

# From: docs/youra_research/h-e1/code/data.py (ACTUAL CODE)
def load_humaneval_plus(cfg: Config) -> dict[str, Any]:
    """task_id -> {'prompt':..., 'entry_point':..., 'base_input': [[args, expected], ...]}"""
```

Checkpoint loading pattern (PEFT adapters, verified from `checkpoints/{ce_final,rl_final}/adapter_config.json` presence — no merged model):
```python
from peft import PeftModel

def load_checkpoint(cfg: Config, adapter_dir: Path) -> PreTrainedModel:
    base, tok = load_base_model(cfg)
    model = PeftModel.from_pretrained(base, adapter_dir)
    model.eval()
    return model, tok
```

---

## A-1: Feedback Bank & Control Generation [Complexity: 3, Budget: 3]

**Applied**: Standard PyTorch / stdlib `random`, `re` (no KB pattern needed — simple matching logic)

### API Signatures

```python
def build_feedback_bank(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizerBase,
    problems: dict[str, Any],
    cfg: Config,
) -> dict[str, dict]:
    """Single-shot generate + execute for all problems. Returns task_id -> {code, pass_rate, error_msg, error_type}."""
    ...

def classify_error_type(error_msg: str) -> str:
    """Regex match first exception class name. 'AssertionError'|'TypeError'|'SyntaxError'|'Timeout'|'Other'."""
    ...

def get_control_feedback(
    task_id: str,
    feedback_bank: dict[str, dict],
    seed: int,
) -> str:
    """Pick donor error_msg from a DIFFERENT task_id, same error_type, len within +-20%. Fallback: random donor."""
    ...
```

### Pseudo-code (control matching — non-trivial selection logic)

```
1. actual = feedback_bank[task_id]
2. same_type = [f for tid, f in feedback_bank.items()
                 if tid != task_id and f.error_type == actual.error_type and f.pass_rate < 1.0]
3. len_matched = [f for f in same_type if abs(len(f.error_msg) - len(actual.error_msg)) <= 0.2 * len(actual.error_msg)]
4. pool = len_matched if len_matched else same_type
5. if not pool: pool = [f for tid, f in feedback_bank.items() if tid != task_id and f.pass_rate < 1.0]
6. rng = random.Random(seed + hash(task_id) % 10_000)
7. return rng.choice(pool).error_msg
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A1-1 | build_feedback_bank | Loop problems, single_shot + execute_and_get_feedback, store per-task result |
| L-A1-2 | classify_error_type | Regex on error_msg first line (`^(\w+Error)` / 'Timeout' literal / else 'Other') |
| L-A1-3 | get_control_feedback | Matched-donor sampling per pseudo-code above |

---

## A-2: Condition Evaluation Loop (Actual vs Control) [Complexity: 4, Budget: 4]

**Applied**: Standard PyTorch — reuses `single_shot`/`execute_and_get_feedback` from H-E1, K=1 fixed

### API Signatures

```python
def refine_with_feedback(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizerBase,
    prompt: str,
    tests: list[str],
    feedback_msg: str,
    cfg: Config,
) -> str:
    """Single refinement step (K=1) using injected feedback_msg instead of live error."""
    ...

def build_tests(problem: dict) -> list[str]:
    """['assert {entry_point}(*{args}) == {expected}' for args, expected in problem['base_input']]"""
    ...

def evaluate_condition(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizerBase,
    problems: dict[str, Any],
    feedback_bank: dict[str, dict],
    condition: str,        # "actual" | "control"
    model_name: str,       # "RL" | "CE"
    cfg: Config,
    seed: int,
) -> list[dict]:
    """Per-problem: reuse cached single-shot from feedback_bank, refine if failed, record result row."""
    ...
```

### Pseudo-code (condition loop)

```
for task_id, problem in problems.items():
    tests = build_tests(problem)                          # list[str]
    cached = feedback_bank[task_id]                        # from A-1 (per-model bank; RL/CE separate banks)
    if cached.pass_rate == 1.0:
        refined_pass = True
    else:
        fb = cached.error_msg if condition == "actual" \
             else get_control_feedback(task_id, feedback_bank, seed)
        refine_prompt = f"{problem['prompt']}\n# Previous:\n{cached.code}\n# Feedback:\n{fb}\n# Fixed code:"
        refined_code = single_shot(model, tokenizer, refine_prompt, cfg)   # cfg.refine_k unused here; K=1 by construction
        pass_rate, _ = execute_and_get_feedback(refined_code, tests)
        refined_pass = (pass_rate == 1.0)
    emit {task_id, model: model_name, condition, single_shot_pass: cached.pass_rate==1.0, refined_pass}
```

**Note**: `feedback_bank` must be built **separately per model** (RL bank from RL single-shot, CE bank from CE single-shot) since Actual feedback is model-specific; Control donors are drawn from the *same* model's bank to keep surface stats comparable within-model.

### Tensor Shapes

Not applicable — this task is text/control-flow only (no tensor ops beyond `single_shot`'s internal generation, already shaped `[1, seq_len] -> [1, out_len]`).

### Subtasks [3/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A2-1 | build_tests | Format assert statements from `base_input` |
| L-A2-2 | refine_with_feedback | One-shot refine prompt construction + generation |
| L-A2-3 | evaluate_condition | Full loop over problems for one (model, condition) cell |

---

## A-3: DiD Contrast + Bootstrap CI [Complexity: 3, Budget: 3]

**Applied**: Standard PyTorch/NumPy — `sklearn.utils.resample` pattern from diff-diff reference (per PRD Appendix)

### API Signatures

```python
def pass_rate(results: list[dict], model_name: str, condition: str) -> float:
    """mean(refined_pass) filtered by model/condition."""
    ...

def compute_did_contrast(results: list[dict]) -> float:
    """(RL_actual - RL_control) - (CE_actual - CE_control)"""
    ...

def bootstrap_did_ci(
    results: list[dict],
    n_bootstrap: int = 1000,
    alpha: float = 0.05,
    seed: int = 42,
) -> dict:
    """Resample rows (with replacement, stratified by task_id across all 4 cells) -> percentile CI."""
    ...
```

### Pseudo-code (stratified bootstrap — resample task_ids, not raw rows, to preserve 4-cell structure)

```
task_ids = sorted(set(r["problem_id"] for r in results))   # [N] where N=164
rng = np.random.RandomState(seed)
did_samples = []
for b in range(n_bootstrap):
    sampled_ids = rng.choice(task_ids, size=len(task_ids), replace=True)   # [N]
    boot_results = [r for tid in sampled_ids for r in results_by_task[tid]]  # 4 rows/task
    did_samples.append(compute_did_contrast(boot_results))                 # scalar
did_samples = np.array(did_samples)                                        # [n_bootstrap]
ci_lower, ci_upper = np.percentile(did_samples, [100*alpha/2, 100*(1-alpha/2)])
did_point = compute_did_contrast(results)
return {did_contrast: did_point, ci_lower, ci_upper, significant: ci_lower > 0,
        p_value_one_sided: mean(did_samples <= 0)}
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| task_ids | [164] | HumanEval+ problem ids |
| sampled_ids | [164] | bootstrap resample w/ replacement |
| did_samples | [n_bootstrap] | scalar DiD per bootstrap draw |

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A3-1 | pass_rate / compute_did_contrast | 4-cell mean + contrast formula |
| L-A3-2 | bootstrap_did_ci | Stratified-by-task_id resampling loop |
| L-A3-3 | results_by_task index | Precompute `task_id -> [4 rows]` dict for O(1) bootstrap lookup |

---

## A-4: Orchestration & Visualization [Complexity: 2, Budget: 2]

**Applied**: Standard matplotlib (reuse H-E1 `visualize.py` bar-chart style)

### API Signatures

```python
def run_did_experiment(cfg: Config) -> dict:
    """Load both checkpoints, build 2 feedback banks, run 4 evaluate_condition calls, return raw results + stats."""
    ...

def plot_2x2_bars(results: list[dict], out_path: Path) -> None:
    """Grouped bar: x=[RL,CE], hue=[Actual,Control], y=pass@1_refined."""
    ...

def plot_did_ci(did_stats: dict, out_path: Path) -> None:
    """Single bar at did_contrast with [ci_lower, ci_upper] error bar, hline at 0."""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A4-1 | run_did_experiment | Top-level orchestration: 2 models x 2 conditions x 164 problems |
| L-A4-2 | plot_2x2_bars / plot_did_ci | Two required figures (F8, F9) |
