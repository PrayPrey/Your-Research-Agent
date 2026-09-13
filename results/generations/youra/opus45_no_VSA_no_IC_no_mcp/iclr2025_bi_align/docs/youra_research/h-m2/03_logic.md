# Logic Design: H-M2 DPO Boundary Preservation

**Hypothesis ID:** h-m2 | **Type:** MECHANISM | **Gate:** SHOULD_WORK

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1)
**Status**: API signatures verified from actual H-M1 code (not spec)
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Relevant Symbols**: `model.get_reward`, `model.load_tokenizer`, `model.build_reward_model`, `data.load_hh_rlhf_splits`, `data.sample_test_pairs`, `metrics/distribution.analyze_reward_distribution`, `evaluate.run_evaluation`

**Key deviation from H-M2 brief spec**: brief uses `get_rlhf_reward(...)` — actual H-M1 function is `get_reward(model, tokenizer, text: str, device: str) -> float`. Use actual name.

---

## External Dependencies (Base Hypothesis: H-M1)

```python
# From: docs/youra_research/h-m1/code/model.py (ACTUAL CODE)
def load_tokenizer(cfg) -> "PreTrainedTokenizer": ...

def get_reward(model, tokenizer, text: str, device: str) -> float:
    """Scalar reward for one text. Pads/truncates to max_length=512."""
    ...

# From: docs/youra_research/h-m1/code/data.py
def load_hh_rlhf_splits(cfg, tokenizer) -> "DatasetDict":
    """90/5/5 train/val/test split of Anthropic/hh-rlhf."""
    ...

def sample_test_pairs(dataset, n: int, seed: int) -> list[tuple[str, str]]:
    """Returns list of (chosen_text, rejected_text)."""
    ...

# From: docs/youra_research/h-m1/code/metrics/distribution.py
def analyze_reward_distribution(model, tokenizer, test_pairs: list, device: str) -> dict:
    """Returns dict with keys: reward_range, reward_std, unique_reward_ratio,
    bimodality_coefficient, mean_chosen, mean_rejected, margin."""
    ...
```

H-M1 checkpoint (RLHF reward model, LoRA adapter): `docs/youra_research/h-m1/code/reward_model_h-m1_quick/final/`
H-M1 saved metrics (baseline numbers): `docs/youra_research/h-m1/code/smoothness_metrics.json`

---

## Module Layout

```
docs/youra_research/h-m2/code/
├── config.py         # HM2Config dataclass
├── data.py           # DPO-format loading, boundary case extraction
├── model.py          # policy/ref model + LoRA build
├── dpo_train.py       # TRL DPOTrainer wrapper
├── metrics/
│   ├── implicit_reward.py   # DPO implicit reward computation
│   ├── margin.py             # margin distribution comparison (DPO vs RLHF)
│   └── boundary.py           # boundary case analysis, win-rate
├── evaluate.py        # orchestration, PASS/FAIL check
└── run_experiment.py
```

---

## A-1: Config & Data [Complexity: Low]

**Applied**: Standard PyTorch / HuggingFace `datasets` pattern (mirrors H-M1 `data.py`)

### API Signatures

```python
# config.py
@dataclass
class HM2Config:
    base_model: str = "meta-llama/Llama-2-7b-hf"
    beta: float = 0.1
    per_device_train_batch_size: int = 2
    gradient_accumulation_steps: int = 8
    num_train_epochs: int = 1
    learning_rate: float = 5e-7
    max_length: int = 512
    max_prompt_length: int = 256
    bf16: bool = True
    gradient_checkpointing: bool = True
    seed: int = 42
    test_sample_size: int = 5000
    boundary_margin_threshold: float = 0.1  # RLHF margin cutoff
    output_dir: str = "./dpo_model_h-m2"
    metrics_output_path: str = "boundary_sharpness_metrics.json"
    threshold_sharpness_ratio: float = 1.0
    threshold_boundary_accuracy: float = 0.55
    threshold_confident_ratio: float = 0.3

# data.py
def load_hh_rlhf_dpo_splits(cfg: HM2Config) -> "DatasetDict":
    """Loads Anthropic/hh-rlhf, maps to prompt/chosen/rejected. 90/5/5 split (reuse H-M1 split logic/seed for consistency)."""
    ...

def find_common_prefix(chosen: str, rejected: str) -> str:
    """Char-level common prefix used as DPO prompt."""
    ...

def preprocess_hh_rlhf_dpo(example: dict) -> dict:
    """example: {"chosen": str, "rejected": str} -> {"prompt","chosen","rejected"}"""
    ...

def extract_boundary_cases(
    rlhf_model, tokenizer, test_pairs: list[tuple[str, str]],
    device: str, margin_threshold: float = 0.1,
) -> list[tuple[str, str, float]]:
    """Uses H-M1 get_reward() on each pair; keeps pairs with |margin| < threshold.
    Returns (chosen, rejected, rlhf_margin) list, ~500 pairs expected."""
    ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | Config | `HM2Config` dataclass |
| L-1-2 | DPO preprocessing | prompt/chosen/rejected extraction |
| L-1-3 | Boundary extraction | reuse H-M1 `get_reward` to tag boundary pairs |

---

## A-2: Model Setup [Complexity: Low]

**Applied**: HF `AutoModelForCausalLM` + PEFT LoRA (standard TRL pattern)

### API Signatures

```python
# model.py
def load_policy_and_ref(cfg: HM2Config) -> tuple["PreTrainedModel", "PreTrainedModel", "PreTrainedTokenizer"]:
    """Loads base_model twice: policy (LoRA-wrapped, trainable) + ref (frozen, eval mode).
    Returns (policy_model, ref_model, tokenizer)."""
    ...

def get_peft_config(cfg: HM2Config) -> "LoraConfig":
    """r=16, alpha=32, dropout=0.05, target_modules=[q,k,v,o]_proj, task_type=CAUSAL_LM"""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | Model+LoRA | policy/ref loading, freeze ref |

---

## A-3: DPO Training [Complexity: Medium, Budget: Medium]

**Applied**: TRL `DPOTrainer` (Rafailov et al. 2023)

### API Signatures

```python
# dpo_train.py
def build_dpo_trainer(
    cfg: HM2Config,
    policy_model, ref_model, tokenizer,
    train_dataset, eval_dataset,
) -> "DPOTrainer":
    """Wraps trl.DPOTrainer with DPOConfig(beta=cfg.beta, ...) and LoraConfig from model.get_peft_config."""
    ...

def train_dpo(cfg: HM2Config, trainer: "DPOTrainer") -> str:
    """Runs trainer.train(), saves adapter to cfg.output_dir/final. Returns checkpoint path."""
    ...
```

### Pseudo-code (DPO loss — reference only, TRL computes internally)

```
chosen_rewards  = beta * (policy_chosen_logps  - ref_chosen_logps)   # [B]
rejected_rewards = beta * (policy_rejected_logps - ref_rejected_logps) # [B]
loss = -logsigmoid(chosen_rewards - rejected_rewards).mean()
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | DPOTrainer wrapper | build + train + save adapter |

---

## A-4: Implicit Reward & Margin Metrics [Complexity: Medium, Budget: Medium]

**Applied**: Log-ratio implicit reward (DPO closed-form), reuse H-M1 `get_reward` for RLHF side

### API Signatures

```python
# metrics/implicit_reward.py
def get_sequence_logprobs(model, inputs: dict) -> "Tensor":
    """inputs: tokenized {input_ids, attention_mask} [1, T].
    Returns scalar summed log-prob tensor [1]."""
    ...

def compute_dpo_implicit_reward(
    policy_model, ref_model, tokenizer, text: str, beta: float, device: str,
) -> float:
    """r(x,y) = beta * (log pi(y|x) - log pi_ref(y|x)). Scalar."""
    ...

# metrics/margin.py
def compare_margin_distributions(
    dpo_model, rlhf_model, ref_model, tokenizer,
    test_pairs: list[tuple[str, str]], beta: float, device: str,
) -> dict:
    """RLHF side uses H-M1 model.get_reward(rlhf_model, tokenizer, text, device).
    Returns: dpo_margin_std, rlhf_margin_std, sharpness_ratio,
             dpo_margin_mean, rlhf_margin_mean."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [1, T] | single sequence, T <= max_length |
| logits (policy/ref) | [1, T, V] | V = vocab size |
| token_logprobs | [1, T-1, 1] | gathered log_softmax at target ids |
| implicit_reward | scalar | summed log-prob diff * beta |

### Pseudo-code (margin comparison)

```
for (chosen, rejected) in test_pairs:
    dpo_margin  = compute_dpo_implicit_reward(dpo, ref, chosen)  - compute_dpo_implicit_reward(dpo, ref, rejected)
    rlhf_margin = get_reward(rlhf, tokenizer, chosen, device)     - get_reward(rlhf, tokenizer, rejected, device)
sharpness_ratio = std(dpo_margins) / std(rlhf_margins)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | Implicit reward | logprob computation + reward fn |
| L-4-2 | Margin comparison | DPO vs RLHF std/mean, sharpness_ratio |

---

## A-5: Boundary Analysis & Win-Rate [Complexity: Medium, Budget: Medium]

**Applied**: Standard PyTorch generation + implicit-reward comparison

### API Signatures

```python
# metrics/boundary.py
def analyze_boundary_cases(
    dpo_model, ref_model, tokenizer,
    boundary_pairs: list[tuple[str, str, float]],  # (chosen, rejected, rlhf_margin)
    beta: float, device: str,
) -> dict:
    """Returns: boundary_accuracy, mean_confidence, confident_ratio (|margin|>0.1)."""
    ...

def generate(model, tokenizer, prompt: str, device: str, max_new_tokens: int = 128) -> str:
    """Greedy/sampled generation. Returns decoded continuation text."""
    ...

def compute_win_rates(
    policy_model, ref_model, tokenizer,
    eval_prompts: list[str], beta: float, device: str,
) -> dict:
    """Returns: win_rate (float, policy implicit-reward > ref implicit-reward)."""
    ...
```

### Pseudo-code (boundary decision)

```
for (chosen, rejected, rlhf_margin) in boundary_pairs:   # rlhf_margin < 0.1 by construction
    margin = dpo_reward(chosen) - dpo_reward(rejected)
    decision  = margin > 0          # correct-direction pick
    confidence = abs(margin)
boundary_accuracy = mean(decision)
confident_ratio    = mean(confidence > 0.1)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | Boundary case eval | accuracy/confidence on H-M1 boundary pairs |
| L-5-2 | Win-rate eval | generation + implicit-reward comparison |

---

## A-6: Evaluation Orchestration [Complexity: Low, Budget: Low]

**Applied**: Mirrors H-M1 `evaluate.run_evaluation` structure

### API Signatures

```python
# evaluate.py
def run_evaluation(cfg: HM2Config, checkpoint_path: str) -> dict:
    """Loads DPO policy (PeftModel.from_pretrained + merge_and_unload) + ref model.
    Loads H-M1 RLHF checkpoint + H-M1 boundary pairs.
    Runs compare_margin_distributions, analyze_boundary_cases, compute_win_rates.
    Checks thresholds (sharpness_ratio > 1.0, boundary_accuracy > 0.55,
    confident_ratio > 0.3). Dumps cfg.metrics_output_path. Returns results dict
    with 'pass' sub-dict and 'overall_pass' bool."""
    ...
```

### Data Flow

```
Anthropic/hh-rlhf --preprocess_hh_rlhf_dpo--> DPO train/val/test splits
train split --DPOTrainer(beta=0.1)--> dpo_model_h-m2/final (LoRA adapter)

H-M1 RLHF checkpoint + test_pairs --extract_boundary_cases--> boundary_pairs (~500)

dpo_model + ref_model + test_pairs  --> compare_margin_distributions --> sharpness_ratio
dpo_model + ref_model + boundary_pairs --> analyze_boundary_cases --> boundary_accuracy, confident_ratio
dpo_model + ref_model + eval_prompts --> compute_win_rates --> win_rate

all metrics --> boundary_sharpness_metrics.json --> 04_validation.md (PASS/FAIL)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | Orchestration | load models, run all metric suites, threshold check, JSON dump |

---

## Budget Summary

| Task | Complexity | Subtasks Used |
|------|-----------|----------------|
| A-1 Config & Data | Low | 3/3 |
| A-2 Model Setup | Low | 1/1 |
| A-3 DPO Training | Medium | 1/1 |
| A-4 Implicit Reward & Margin | Medium | 2/2 |
| A-5 Boundary & Win-Rate | Medium | 2/2 |
| A-6 Orchestration | Low | 1/1 |
