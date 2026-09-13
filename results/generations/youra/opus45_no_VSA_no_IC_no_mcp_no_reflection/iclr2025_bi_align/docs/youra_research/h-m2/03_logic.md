# Logic Design: H-M2 — 7-Variant IFEval Gate

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m1, VALIDATED)
**Status**: API signatures verified from actual h-m1 code (no Serena MCP available this session; verified via direct file read, same guarantee)
**Analyzed Path**: `h-m1/code/rewards.py`, `h-m1/code/train_ppo.py`, `h-m1/code/data.py`
**Relevant Symbols**: `CombinedRewardModel.__init__(helpfulness_model, helpfulness_tokenizer, ifeval_signal, alpha=0.5, beta=0.5, device="cuda")`, `CombinedRewardModel.compute_reward(prompts, responses, constraints) -> list[Tensor]`, `build_ppo_trainer(cfg) -> tuple[PPOTrainer, AutoTokenizer]`, `train_loop(trainer, tokenizer, reward_model, cfg) -> None`, `load_ultrafeedback() -> Dataset`, `load_ifeval_split(seed=42) -> tuple[Dataset, Dataset]`

**Correction vs h-m1/03_logic.md spec**: no `set_weights()` method exists on `CombinedRewardModel` — alpha/beta are constructor args only. h-m2 must construct a new `CombinedRewardModel` instance per variant with the desired alpha/beta, not mutate weights post-init.

---

## External Dependencies API (Verified from Actual Code)

```python
# From: h-m1/code/rewards.py (ACTUAL)
class CombinedRewardModel:
    def __init__(self, helpfulness_model, helpfulness_tokenizer,
                 ifeval_signal: "IFEvalRewardSignal", alpha: float = 0.5,
                 beta: float = 0.5, device: str = "cuda"): ...
    def compute_reward(self, prompts: list[str], responses: list[str],
                        constraints: list[list[dict]]) -> list[torch.Tensor]: ...

# From: h-m1/code/train_ppo.py (ACTUAL)
def build_ppo_trainer(cfg) -> tuple["PPOTrainer", "AutoTokenizer"]: ...
def train_loop(trainer, tokenizer, reward_model: "CombinedRewardModel | None", cfg) -> None: ...

# From: h-m1/code/data.py (ACTUAL)
def load_ultrafeedback() -> "Dataset": ...
def load_ifeval_split(seed: int = 42) -> tuple["Dataset", "Dataset"]: ...
def build_constraints(ifeval_row: dict) -> list[dict]: ...

# From: h-e1/code/model.py (ACTUAL, via h-m1 chain)
class IFEvalRewardSignal(nn.Module):
    def __init__(self, soft_margin: float = 0.1): ...
    def forward(self, response: str, constraints: list[dict]) -> torch.Tensor: ...
```

**Note**: `load_ifeval_split` must be called with `seed=1` (h-m2 NFR-2) to reproduce h-m1's held-out split; do not re-split independently.

---

## L-1: Variant Registry & Reward Model Builder [Complexity: 6, Budget: 4]

**Applied**: dataclass registry pattern (stdlib `dataclasses`, no new dependency)

### API Signatures

```python
# config.py
@dataclass
class ModelVariant:
    name: str          # "B1".."B3", "T1".."T4"
    alpha: float
    beta: float
    train: bool         # False only for B1
    reward_mode: str      # "none" | "helpfulness_only" | "quality_only" | "combined"

VARIANTS: list[ModelVariant] = [...]  # see architecture 03_architecture.md — reused verbatim

def build_config(variant: ModelVariant) -> "h_m1.code.config.Config":
    """Clone h-m1 Config, override alpha/beta from variant."""
    ...

# train_variants.py
def build_reward_model(variant: ModelVariant, cfg) -> "CombinedRewardModel | None":
    """B1 -> None. B3 -> CombinedRewardModel(beta=0.0), ifeval_signal passed but beta
    zeroes its contribution (quality-only via UltraFeedback pref score as helpfulness_model).
    B2/T1-T4 -> CombinedRewardModel(alpha=variant.alpha, beta=variant.beta)."""
    ...
```

### Pseudo-code

```
build_reward_model(variant, cfg):
  if variant.reward_mode == "none":
      return None                                    # B1: no PPO
  ifeval_signal = IFEvalRewardSignal(soft_margin=cfg.soft_margin)
  return CombinedRewardModel(
      helpfulness_model=load_helpfulness_model(cfg),
      helpfulness_tokenizer=load_helpfulness_tokenizer(cfg),
      ifeval_signal=ifeval_signal,
      alpha=variant.alpha, beta=variant.beta, device=cfg.device,
  )                                                    # constructor sets weights, no set_weights() call
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | ModelVariant + VARIANTS + build_config | Registry, per-variant Config clone |
| L-1-2 | build_reward_model | Branch on reward_mode, construct CombinedRewardModel or None |

---

## L-2: Variant Execution & Evaluation [Complexity: 10, Budget: 5]

**Applied**: sequential orchestration loop, held-out eval harness (reused from h-m1 `run_checkpoint_eval` pattern)

### API Signatures

```python
# train_variants.py
def run_variant(variant: ModelVariant, ifeval_train: "Dataset", uf_data: "Dataset") -> dict:
    """B1: load base policy, no PPO. Else: build_ppo_trainer + train_loop with
    variant's reward model. Returns {"variant": str, "history": list[dict], "checkpoint": str}."""
    ...

def run_all(variants: list[ModelVariant]) -> dict[str, dict]:
    """Sequential run_variant per config; per-variant try/except isolates failures
    (failed variant excluded from gate, logged, others continue)."""
    ...

# evaluate.py
def evaluate_variant(checkpoint_path: str, ifeval_test: list[dict]) -> dict:
    """Generate on ~500 held-out prompts (max_new_tokens=256), run official IFEval
    checkers per-prompt. Returns {'strict_accuracy': float, 'loose_accuracy': float,
    'per_constraint_type': dict[str, float]}."""
    ...

def evaluate_all(run_results: dict[str, dict], ifeval_test: list[dict]) -> dict[str, dict]:
    """variant name -> evaluate_variant(checkpoint) for each successful run."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| ifeval_test | list[dict], len ~500 | held-out 30% split, seed=1 |
| generated responses | list[str], len ~500 | one per test prompt |
| strict_accuracy, loose_accuracy | scalar float | fraction of prompts |
| per_constraint_type | dict[str, float] | 25 IFEval category keys |

### Pseudo-code

```
run_variant(variant, ifeval_train, uf_data):
  cfg = build_config(variant)
  if not variant.train:                                # B1
      model, tokenizer = load_base_model(cfg)
      return {"variant": variant.name, "history": [], "checkpoint": cfg.base_ckpt_path}
  trainer, tokenizer = build_ppo_trainer(cfg)
  reward_model = build_reward_model(variant, cfg)
  train_loop(trainer, tokenizer, reward_model, cfg)     # reused h-m1 loop, unmodified
  return {"variant": variant.name, "history": trainer.history,
          "checkpoint": f"{cfg.ckpt_dir}/{variant.name}/final"}

evaluate_variant(checkpoint_path, ifeval_test):
  model, tokenizer = load_checkpoint(checkpoint_path)
  responses = [generate(model, tokenizer, p["prompt"]) for p in ifeval_test]
  results = [run_ifeval_checkers(r, p["instruction_id_list"], p["kwargs"])
             for r, p in zip(responses, ifeval_test)]
  strict = mean(r["all_satisfied"] for r in results)
  loose = mean(r["any_satisfied"] for r in results)
  per_type = groupby_mean(results, key="constraint_type")
  return {"strict_accuracy": strict, "loose_accuracy": loose, "per_constraint_type": per_type}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | run_variant + run_all | B1 skip-train path, PPO path, failure isolation |
| L-2-2 | evaluate_variant | Generate + official checker scoring on held-out set |
| L-2-3 | evaluate_all | Map results across 7 checkpoints |

---

## L-3: Gate Computation & Results [Complexity: 4, Budget: 2]

**Applied**: threshold comparison (stdlib, no dependency)

### API Signatures

```python
# aggregate.py
def compute_gate(eval_results: dict[str, dict]) -> dict:
    """max(B1,B2,B3) strict_accuracy vs each Ti; gate passes if any Ti exceeds by >=0.02."""
    ...

def results_table(eval_results: dict[str, dict]) -> "pandas.DataFrame":
    """7-row: variant, strict_acc, loose_acc, alpha, beta. CSV export."""
    ...
```

### Pseudo-code

```
compute_gate(eval_results):
  baselines = {"B1", "B2", "B3"}
  baseline_max = max(eval_results[b]["strict_accuracy"] for b in baselines)
  ti_scores = {t: eval_results[t]["strict_accuracy"] for t in ("T1","T2","T3","T4")}
  best_ti = max(ti_scores, key=ti_scores.get)
  delta_pp = ti_scores[best_ti] - baseline_max
  return {"baseline_max": baseline_max, "best_ti": best_ti,
          "gate_passed": delta_pp >= 0.02, "delta_pp": delta_pp}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | compute_gate + results_table | Threshold check, DataFrame export |

---

**Total subtasks: 6** (budget note: architecture allocated per-task complexity across C-1..C-11; logic-level subtask IDs above map to the non-trivial algorithmic surfaces only — `visualize.py` signatures already fully specified in architecture, no additional logic needed, skipped here).
