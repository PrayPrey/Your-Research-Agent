# Logic Design: H-M1 — Combined Reward PPO

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: API signatures verified from actual H-E1 code (not spec)
**Analyzed Path**: `docs/youra_research/h-e1/code/model.py`
**Relevant Symbols**: `IFEvalRewardSignal.forward(response: str, constraints: list[dict]) -> torch.Tensor` (scalar, per-sample), `BaselineChecker`, `load_generator`, `generate_responses`

No `find_symbol`/MCP tool available in this session; read file directly via file tool (equivalent verification, same guarantee: signature confirmed from actual code, not `02c`/PRD spec).

---

## External Dependencies (H-E1, Actual Code)

```python
# From: docs/youra_research/h-e1/code/model.py (ACTUAL CODE)
class IFEvalRewardSignal(nn.Module):
    def __init__(self, soft_margin: float = 0.1): ...

    def forward(self, response: str, constraints: list[dict]) -> torch.Tensor:
        """Per-sample soft constraint score. Returns scalar tensor (0-dim), NOT batched."""
        ...
```

**Integration note**: `forward` takes one `response: str` + its `constraints: list[dict]` and returns a 0-dim tensor. H-M1 must loop over the PPO batch and call this per-sample (no native batching in H-E1 API) — see `CombinedRewardModel.compute_reward` pseudo-code below.

---

## A-1: CombinedRewardModel [Complexity: 4, Budget: 4]

**Applied**: Standard PyTorch reward wrapper (KB unavailable this session — using TRL's documented custom-reward-callable pattern)

### API Signatures

```python
# rewards.py
class CombinedRewardModel:
    def __init__(
        self,
        helpfulness_model: AutoModelForSequenceClassification,
        helpfulness_tokenizer: PreTrainedTokenizer,
        ifeval_signal: IFEvalRewardSignal,  # from h-e1/code/model.py
        alpha: float = 0.5,
        beta: float = 0.5,
        device: str = "cuda",
    ):
        """Wraps H-E1 IFEvalRewardSignal + helpfulness RM for PPO reward callable."""
        ...

    def score_helpfulness(self, prompts: list[str], responses: list[str]) -> torch.Tensor:
        """RM forward pass. Returns [B] scalar rewards."""
        ...

    def score_ifeval(self, responses: list[str], constraints: list[list[dict]]) -> torch.Tensor:
        """Loops IFEvalRewardSignal.forward per-sample (no native batching). Returns [B]."""
        ...

    def compute_reward(
        self,
        prompts: list[str],
        responses: list[str],
        constraints: list[list[dict]],
    ) -> list[torch.Tensor]:
        """Returns list of B scalar tensors (trl.PPOTrainer.step expects list[Tensor])."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| prompts, responses | list[str], len B | raw text, not tensors |
| constraints | list[list[dict]], len B | per-sample constraint specs |
| R_helpfulness | [B] | from helpfulness RM logits |
| R_ifeval | [B] | stacked per-sample scalars from H-E1 module |
| R_combined | [B] | `alpha * R_helpfulness + beta * R_ifeval` |
| return | list of B `torch.Tensor` (0-dim) | trl PPO step API contract |

### Pseudo-code

```
compute_reward(prompts, responses, constraints):
  1. R_help = score_helpfulness(prompts, responses)          # [B]
  2. R_ifeval_list = [ifeval_signal(r, c) for r, c in zip(responses, constraints)]  # B x 0-dim
  3. R_ifeval = torch.stack(R_ifeval_list)                    # [B]
  4. R_combined = alpha * R_help + beta * R_ifeval            # [B]
  5. log(R_help.mean(), R_ifeval.mean(), R_combined.mean())   # for FR-2.4
  6. return list(R_combined.unbind(0))                        # list[Tensor] per trl contract
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | Init + helpfulness RM load | AutoModelForSequenceClassification load |
| L-1-2 | score_helpfulness | RM forward, sigmoid/logit → scalar |
| L-1-3 | score_ifeval | Loop-call H-E1 module, stack |
| L-1-4 | compute_reward + logging | Combine, log components |

---

## A-2: PPO Training Pipeline [Complexity: 5, Budget: 6]

**Applied**: trl.PPOTrainer standard training loop pattern

### API Signatures

```python
# train_ppo.py
def build_ppo_trainer(cfg: Config) -> tuple[PPOTrainer, AutoTokenizer]:
    """Loads policy (Llama-3-8B-Instruct), frozen ref model, PPOConfig. Returns trainer, tokenizer."""
    ...

def sample_batch(
    ultrafeedback_ds: Dataset,
    ifeval_ds: Dataset,
    batch_size: int,
    ifeval_ratio: float = 0.3,
) -> tuple[list[str], list[list[dict]]]:
    """Mixed sampling: prompts + constraints (empty list [] for non-IFEval prompts)."""
    ...

def train_loop(
    trainer: PPOTrainer,
    tokenizer: AutoTokenizer,
    reward_model: CombinedRewardModel,
    cfg: Config,
) -> None:
    """1000-step PPO loop, checkpoint every 250, log every 10."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| query_tensors | list of [T_prompt] (ragged) | tokenized prompts, per-sample len |
| response_tensors | list of [T_resp] (ragged) | trainer.generate output |
| input_ids (batched, padded) | [B, T] | B=64 (batch_size), T=max seq len |
| attention_mask | [B, T] | 1=real token, 0=pad |
| rewards | list of B scalar Tensor | from CombinedRewardModel.compute_reward |
| objective/kl | scalar (float) | logged per step, per FR-2.4 |
| stats["ppo/policy_loss"] | scalar | must be finite (NFR-1) |

### Pseudo-code

```
train_loop(trainer, tokenizer, reward_model, cfg):
  for step in range(1000):
    prompts, constraints = sample_batch(uf_ds, ifeval_ds, cfg.batch_size)   # B=64
    query_tensors = [tokenizer.encode(p, return_tensors="pt")[0] for p in prompts]

    response_tensors = trainer.generate(
        query_tensors, max_new_tokens=256, do_sample=True,
        pad_token_id=tokenizer.pad_token_id,
    )
    responses = tokenizer.batch_decode(response_tensors, skip_special_tokens=True)

    rewards = reward_model.compute_reward(prompts, responses, constraints)  # list[B] Tensor

    stats = trainer.step(query_tensors, response_tensors, rewards)

    # NFR-1: guard against divergence/NaN
    assert not math.isnan(stats["ppo/policy_loss"])
    if stats["objective/kl"] > 10.0:
        raise TrainingDivergenceError(step, stats["objective/kl"])  # triggers FR-8 failure response

    if step % 10 == 0:
        log_metrics(step, stats, reward_model.last_components)  # FR-2.4

    if step % 250 == 0 and step > 0:
        trainer.save_pretrained(f"{cfg.ckpt_dir}/step_{step}")
        run_checkpoint_eval(step, trainer.model, tokenizer, ifeval_test_ds)  # FR-4.1
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | build_ppo_trainer | Load policy/ref model, PPOConfig (lr=1.41e-5, kl_coef=0.05) |
| L-2-2 | sample_batch | Mix UltraFeedback + IFEval prompts |
| L-2-3 | Rollout generation | query/response tensor handling |
| L-2-4 | trainer.step + reward call | Wire CombinedRewardModel into loop |
| L-2-5 | Stability guards | NaN/KL divergence check → raise/PIVOT signal |
| L-2-6 | Checkpointing + logging | Save every 250, log every 10 |

---

## A-3: Data Pipeline [Complexity: 3, Budget: 4]

**Applied**: Standard HF `datasets` load/split pattern

### API Signatures

```python
# data.py (h-m1)
def load_ultrafeedback() -> Dataset:
    """openbmb/UltraFeedback train split, ~60k rows. Fields: prompt, response, etc."""
    ...

def load_ifeval_split(seed: int = 42) -> tuple[Dataset, Dataset]:
    """google/IFEval, 541 prompts, 70/30 split. Returns (train_ds, test_ds)."""
    ...

def build_constraints(ifeval_row: dict) -> list[dict]:
    """Parses IFEval instruction_id_list/kwargs into H-E1 constraint dict schema
    (type, keywords/target/op/unit/subtype/case_type — matches BaselineChecker/IFEvalRewardSignal)."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| ultrafeedback_ds | HF Dataset, ~60k rows | text fields only |
| ifeval_train/test | HF Dataset, ~379 / ~162 rows | 70/30 of 541 |
| constraints (per sample) | list[dict] | matches H-E1 `c_type` schema: keyword/length/format/structural/case |

### Subtasks [3/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | load_ultrafeedback | HF datasets.load_dataset |
| L-3-2 | load_ifeval_split | Load + seeded 70/30 split |
| L-3-3 | build_constraints | Map IFEval schema → H-E1 constraint dict format |

---

## A-4: Evaluation Pipeline [Complexity: 4, Budget: 5]

**Applied**: Standard held-out eval + train/eval correlation check

### API Signatures

```python
# evaluate.py
def run_checkpoint_eval(
    step: int,
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    ifeval_test_ds: Dataset,
) -> dict:
    """IFEval strict accuracy on held-out 30% (FR-4.1/4.2). Returns {'ifeval_acc': float, 'step': int}."""
    ...

class RewardHackingDetector:
    def __init__(self, corr_threshold: float = 0.7):
        ...

    def log_step(self, step: int, train_reward: float, eval_metric: float) -> None:
        """Records (train, eval) pair per checkpoint."""
        ...

    def check(self) -> dict:
        """Pearson r between train_reward history and eval_metric history.
        Returns {'correlation': float, 'hacking_suspected': bool}  (r < 0.7 → True, per FR-4.3)."""
        ...
```

### Pseudo-code

```
RewardHackingDetector.check():
  1. r, _ = scipy.stats.pearsonr(train_rewards, eval_metrics)
  2. hacking_suspected = r < self.corr_threshold
  3. return {"correlation": r, "hacking_suspected": hacking_suspected}
```

### Subtasks [4/5 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | run_checkpoint_eval | IFEval strict acc on held-out test |
| L-4-2 | RewardHackingDetector.log_step | Track train vs eval pairs |
| L-4-3 | RewardHackingDetector.check | Pearson correlation, threshold flag |
| L-4-4 | Final eval (step 1000) | Full IFEval test + AlpacaEval 100-sample spot check |

---

## A-5: Visualization [Complexity: 1, Budget: 2]

**Applied**: matplotlib line plot (already-installed dependency, rung 5)

### API Signatures

```python
# visualize.py
def plot_reward_trajectory(log_path: str, out_path: str) -> None:
    """Plots reward/mean, reward/helpfulness, reward/controllability, objective/kl vs step."""
    ...
```

### Subtasks [1/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | plot_reward_trajectory | 2x2 subplot: rewards + KL over steps |

---

## Config Additions Required (config.py — for Config Agent)

- `alpha: float = 0.5`, `beta: float = 0.5`
- `helpfulness_model_id: str = "OpenAssistant/reward-model-deberta-v3-large-v2"`
- `policy_model_id: str = "meta-llama/Meta-Llama-3-8B-Instruct"`
- `ppo_lr: float = 1.41e-5`, `batch_size: int = 64`, `mini_batch_size: int = 8`, `ppo_epochs: int = 4`
- `kl_coef: float = 0.05`, `cliprange: float = 0.2`, `cliprange_value: float = 0.2`
- `total_steps: int = 1000`, `ckpt_every: int = 250`, `log_every: int = 10`
- `kl_divergence_max: float = 5.0`, `kl_divergence_hard_limit: float = 10.0` (NFR-1)

skipped: ablation-variant (FR-6) separate module — reuse `alpha`/`beta` config overrides instead of new files, add dynamic scheduling only if T1-Combined run shows plateau.
