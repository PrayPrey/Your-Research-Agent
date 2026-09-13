# Architecture: H-M2 DPO Boundary Preservation

**Applied**: DPO trainer pattern (TRL DPOTrainer + LoRA + frozen reference), reused from KB DL module conventions.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1)
**Status**: Patterns found from base code (`docs/youra_research/h-m1/code/`)
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Findings**: H-M1 uses dataclass `HM1Config`, `model.py::get_reward(model, tokenizer, text, device)` for scalar reward, `run_experiment.py` orchestrates train→evaluate→JSON metrics. H-M2 mirrors this structure. H-M1 checkpoint at `reward_model_h-m1_quick/final/` (adapter) and `smoothness_metrics.json` (margin=0.02308, accuracy=0.5352, range=0.83) are consumed directly as baseline inputs — no need to retrain H-M1.

## File Organization

- `code/config.py` - HM2Config dataclass + DPOConfig/LoraConfig builders
- `code/data.py` - HH-RLHF DPO-format loading, boundary case extraction from H-M1
- `code/model.py` - policy/reference model loading, implicit reward computation
- `code/train.py` - DPOTrainer wrapper
- `code/baselines.py` - load H-M1 RLHF metrics/model for comparison
- `code/metrics/sharpness.py` - margin distribution + variance ratio
- `code/metrics/boundary.py` - boundary case accuracy/confidence
- `code/metrics/winrate.py` - win-rate generation eval
- `code/evaluate.py` - orchestrates all metric modules, writes JSON
- `code/visualize.py` - margin comparison plot
- `code/run_experiment.py` - main entrypoint (train → evaluate → summary)

## Module Definitions

### HM2Config (`code/config.py`)

**Dependencies**: none

```python
@dataclass
class HM2Config:
    base_model: str = "meta-llama/Llama-2-7b-hf"
    ref_model: str = "meta-llama/Llama-2-7b-hf"
    dataset_name: str = "Anthropic/hh-rlhf"
    beta: float = 0.1
    max_length: int = 512
    max_prompt_length: int = 256
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: tuple = ("q_proj","v_proj","k_proj","o_proj")
    per_device_train_batch_size: int = 2
    gradient_accumulation_steps: int = 8
    learning_rate: float = 5e-7
    num_train_epochs: int = 1
    bf16: bool = True
    gradient_checkpointing: bool = True
    output_dir: str = "./dpo_model_h-m2"
    metrics_output_path: str = "./boundary_sharpness_metrics.json"
    plot_output_path: str = "./margin_comparison.png"
    hm1_metrics_path: str = "../../h-m1/code/smoothness_metrics.json"
    hm1_checkpoint_path: str = "../../h-m1/code/reward_model_h-m1_quick/final"
    seed: int = 42
    threshold_boundary_accuracy: float = 0.55
    threshold_confident_ratio: float = 0.3
    threshold_sharpness_ratio: float = 1.0

def get_dpo_config(cfg: HM2Config): ...  # -> trl.DPOConfig
def get_peft_config(cfg: HM2Config): ...  # -> peft.LoraConfig
def set_seed(seed: int): ...
```

### data.py (`code/data.py`)

**Dependencies**: HM2Config

```python
def load_hh_rlhf_dpo_splits(cfg) -> DatasetDict: ...  # prompt/chosen/rejected
def preprocess_hh_rlhf_dpo(example: dict) -> dict: ...
def find_common_prefix(chosen: str, rejected: str) -> str: ...
def load_boundary_cases(cfg, n: int = 500) -> list[tuple[str,str,float]]: ...  # (chosen,rejected,rlhf_margin) margin<0.1
def sample_test_pairs(dataset, n: int, seed: int) -> list[tuple[str,str]]: ...
```

### model.py (`code/model.py`)

**Dependencies**: HM2Config

```python
def load_tokenizer(cfg) -> PreTrainedTokenizer: ...
def build_policy_model(cfg, use_lora: bool = True) -> PreTrainedModel: ...
def build_reference_model(cfg) -> PreTrainedModel: ...  # frozen, no LoRA
def get_sequence_logprobs(model, inputs) -> Tensor: ...
def compute_dpo_implicit_reward(policy, ref_model, tokenizer, text: str, beta: float, device: str) -> float: ...
def generate(model, tokenizer, prompt: str, device: str) -> str: ...
```

### train.py (`code/train.py`)

**Dependencies**: config, data, model

```python
def run_training(cfg: HM2Config) -> str: ...  # returns checkpoint_path, uses trl.DPOTrainer
```

### baselines.py (`code/baselines.py`)

**Dependencies**: HM2Config

```python
def load_hm1_metrics(cfg) -> dict: ...  # reads smoothness_metrics.json
def get_rlhf_reward(model, tokenizer, text: str, device: str) -> float: ...  # reuses H-M1 model.get_reward pattern
def load_hm1_reward_model(cfg): ...  # optional, only if raw margins needed vs summary stats
```

### metrics/sharpness.py (`code/metrics/sharpness.py`)

**Dependencies**: model.compute_dpo_implicit_reward, baselines

```python
def compare_margin_distributions(dpo_model, ref_model, tokenizer, test_pairs, rlhf_margin_std, beta, device) -> dict: ...
    # -> {dpo_margin_std, rlhf_margin_std, sharpness_ratio, dpo_margin_mean, rlhf_margin_mean}
```

### metrics/boundary.py (`code/metrics/boundary.py`)

**Dependencies**: model.compute_dpo_implicit_reward

```python
def analyze_boundary_cases(dpo_model, ref_model, tokenizer, boundary_pairs, beta, device) -> dict: ...
    # -> {boundary_accuracy, mean_confidence, confident_ratio}
```

### metrics/winrate.py (`code/metrics/winrate.py`)

**Dependencies**: model.generate, model.compute_dpo_implicit_reward

```python
def compute_win_rates(policy, ref_model, tokenizer, eval_prompts, beta, device) -> dict: ...  # -> {win_rate}
```

### evaluate.py (`code/evaluate.py`)

**Dependencies**: all metrics/*, baselines, data

```python
def run_evaluation(cfg: HM2Config, checkpoint_path: str) -> dict: ...
    # loads policy+ref, runs sharpness/boundary/winrate, writes metrics JSON, returns results dict with "pass"/"overall_pass"
```

### visualize.py (`code/visualize.py`)

**Dependencies**: evaluate results

```python
def plot_margin_comparison(dpo_margins: list, rlhf_margin_mean: float, rlhf_margin_std: float, output_path: str) -> None: ...
```

### run_experiment.py (`code/run_experiment.py`)

**Dependencies**: config, train, evaluate

```python
def main() -> int: ...  # train -> evaluate -> print summary -> exit code
```

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config setup | HM2Config dataclass, DPOConfig/LoraConfig builders | 4 | 1+1+1+1 |
| A-2 | Data pipeline | Load HH-RLHF, DPO prompt/chosen/rejected preprocessing, splits | 8 | 2+2+3+1 |
| A-3 | Boundary case extraction | Load H-M1 metrics, identify/replicate margin<0.1 cases | 6 | 2+2+1+1 |
| A-4 | Model loading | Policy + frozen reference model, LoRA wiring, tokenizer | 7 | 2+2+2+1 |
| A-5 | Implicit reward computation | log-ratio reward fn, sequence logprobs | 6 | 2+1+2+1 |
| A-6 | DPO training loop | TRL DPOTrainer integration, checkpointing | 9 | 3+3+2+1 |
| A-7 | Baselines integration | Load H-M1 metrics/model, get_rlhf_reward reuse | 5 | 1+2+1+1 |
| A-8 | Sharpness metric | Margin distribution comparison, sharpness_ratio | 6 | 2+2+1+1 |
| A-9 | Boundary evaluation | Boundary accuracy/confidence on H-M1 ambiguous cases | 6 | 2+2+1+1 |
| A-10 | Win-rate evaluation | Generation + implicit reward comparison policy vs ref | 8 | 3+2+2+1 |
| A-11 | Evaluation orchestration | evaluate.py combining all metrics, JSON output, pass/fail | 7 | 2+2+2+1 |
| A-12 | Experiment runner + visualization | run_experiment.py, margin_comparison.png, summary printout | 6 | 2+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-6], Low(4-8): [A-1,A-2,A-3,A-4,A-5,A-7,A-8,A-9,A-10,A-11,A-12]

## Dependencies Between Epics

- A-1 → A-2, A-4, A-6
- A-2, A-3 → A-6 (training needs data)
- A-3 → A-9 (boundary eval needs cases)
- A-4, A-5 → A-6, A-8, A-9, A-10
- A-6 → A-8, A-9, A-10, A-11
- A-7 → A-8 (needs H-M1 baseline stats)
- A-8, A-9, A-10 → A-11 → A-12

## External Dependencies (Base Hypothesis: H-M1)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| get_reward | `from h_m1.model import get_reward` (or direct JSON read) | `docs/youra_research/h-m1/code/model.py` |
| HM1 metrics | JSON read, no import | `docs/youra_research/h-m1/code/smoothness_metrics.json` |
| HM1 reward checkpoint | LoRA adapter path | `docs/youra_research/h-m1/code/reward_model_h-m1_quick/final/` |

**Verified from**: `docs/youra_research/h-m1/code/` (actual implementation). H-M1's `smoothness_metrics.json` provides `distribution.margin` (0.02308) as `rlhf_margin` baseline for A-7/A-8 — avoids recomputation. Raw RLHF reward model checkpoint only needed if per-pair RLHF margins are required beyond summary stats; A-7 defaults to summary-stat comparison (simplest path satisfying success criteria).
