# Architecture: H-E1 (EXISTENCE / PoC)

**Hypothesis:** Higher bandwidth reward signals accelerate PPO convergence vs binary rewards
**Type:** EXISTENCE — minimal architecture to test "does it work?"

Applied: TRL PPOTrainer custom-reward-function pattern (Hugging Face RLHF recipes)
Applied: Graded/categorical reward mapping pattern (dense verifiable rewards for code gen)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No base_hypothesis folder or existing `src/`/`code/` directory present for h-e1.

---

## File Structure

```
h-e1/code/
├── config.py       # fixed hyperparameters, 3 reward conditions, 5 seeds
├── reward.py        # execute_tests + compute_reward (binary/categorical/high_bandwidth)
├── model.py          # load CodeLlama-7B-Instruct + PPOTrainer wiring
├── train.py           # PPO training loop over conditions x seeds
└── evaluate.py         # pass@1 on MBPP/HumanEval + figures
```

---

## Modules

### Config (`config.py`)

**Dependencies**: none

```python
REWARD_CONDITIONS = ["binary", "categorical", "high_bandwidth"]
SEEDS = [0, 1, 2, 3, 4]

@dataclass
class ExperimentConfig:
    model_id: str = "codellama/CodeLlama-7b-Instruct-hf"
    learning_rate: float = 1e-5
    batch_size: int = 4
    ppo_epochs: int = 4
    init_kl_coef: float = 0.05
    train_epochs: int = 3
    pass_at_1_threshold: float = 0.3
```

### RewardEngine (`reward.py`)

**Dependencies**: Config (implicit constants)

```python
@dataclass
class TestResult:
    passed: bool
    error_type: str  # "passed" | "assertion_error" | "runtime_error" | "syntax_error"
    expected: Any | None
    actual: Any | None

def execute_tests(code: str, test_cases: list[str], timeout: float = 5.0) -> list[TestResult]: ...

def compute_reward(code: str, test_cases: list[str], condition: str) -> float:
    """condition in {'binary','categorical','high_bandwidth'}"""
    ...
```

### PPOModel (`model.py`)

**Dependencies**: Config, transformers, trl

```python
def load_model_and_tokenizer(cfg: ExperimentConfig) -> tuple[AutoModelForCausalLMWithValueHead, AutoTokenizer]: ...

def build_ppo_trainer(cfg: ExperimentConfig, model, tokenizer, dataset) -> PPOTrainer: ...
```

### Trainer (`train.py`)

**Dependencies**: Config, RewardEngine, PPOModel, datasets

```python
def load_mbpp_train() -> Dataset: ...

def format_prompt(problem: dict) -> str: ...

def run_condition(condition: str, seed: int, cfg: ExperimentConfig) -> dict:
    """Trains one (condition, seed) run; returns metrics dict incl.
    per-step pass@1 samples for convergence tracking. Saves checkpoint
    to checkpoints/{condition}_{seed}/"""
    ...

def main() -> None:
    """Loop: for condition in REWARD_CONDITIONS: for seed in SEEDS: run_condition(...)"""
    ...
```

### Evaluator (`evaluate.py`)

**Dependencies**: RewardEngine (execute_tests), datasets

```python
def load_humaneval_test() -> Dataset: ...
def load_mbpp_test() -> Dataset: ...

def evaluate_pass_at_1(model, tokenizer, dataset) -> float: ...

def samples_to_threshold(metric_log: list[tuple[int, float]], threshold: float = 0.3) -> int | None: ...

def compare_conditions(results: dict[str, dict]) -> dict:
    """Aggregates mean±std across seeds, runs significance test (p<0.05),
    checks gate: samples_to_threshold(high_bandwidth) < samples_to_threshold(binary)"""
    ...

def make_figures(results: dict, out_dir: str) -> None:
    """learning curves, convergence bar chart, reward histograms,
    gate metrics comparison (mandatory)"""
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data pipeline | Load/format MBPP + HumanEval, prompt formatting | 8 | 2+2+2+2 |
| A-2 | Reward engine | Sandbox execution, error categorization, 3 reward modes | 14 | 3+2+5+4 |
| A-3 | Model + PPO wiring | Load CodeLlama-7B, configure PPOTrainer | 9 | 2+3+2+2 |
| A-4 | Training loop | Run 3 conditions x 5 seeds, checkpointing, metric logging | 12 | 3+3+3+3 |
| A-5 | Evaluation pipeline | pass@1 on MBPP/HumanEval, samples-to-threshold, stats | 10 | 2+3+3+2 |
| A-6 | Visualization | Learning curves, convergence bars, reward histograms, gate chart | 6 | 2+1+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-2], Medium(9-13): [A-3, A-4, A-5], Low(4-8): [A-1, A-6]

---

## Notes

- No external base-hypothesis code to reuse; "External Dependencies" section omitted (N/A for green-field).
- Sandbox execution (A-2) is highest complexity: subprocess isolation, timeout handling, syntax/runtime/assertion error classification, numeric partial-credit extraction.
- Single fixed config (no ablation matrix beyond the 3 required reward conditions) per EXISTENCE scope.
