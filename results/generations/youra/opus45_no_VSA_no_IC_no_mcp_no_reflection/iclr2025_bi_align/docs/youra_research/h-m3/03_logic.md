# Logic Design: H-M3 — Alpha Sweep AlpacaEval Gate

Applied: reward-model-wrapper-pattern (reused CombinedRewardModel, no new wrapper)
Applied: sweep-orchestration-pattern (loop train+eval per config, aggregate + gate check)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m1, VALIDATED)
**Status**: API signatures verified from actual code — diverges from h-m1/03_logic.md and h-m3/03_architecture.md specs
**Analyzed Path**: `h-m1/code/{config,rewards,train_ppo,evaluate}.py` (read directly; Serena/Archon MCP tools unavailable this session — file-read verification used as equivalent, same guarantee: signature confirmed from actual code, not spec)
**Relevant Symbols/Divergences found**:
- `run_training(cfg: ExperimentConfig, output_dir: Path) -> tuple[list[dict], Dataset]` — takes `Path` not `str`, returns `(history, ifeval_test)`. Architecture doc's `run_training(cfg, output_dir) -> (history, ifeval_test)` matches this.
- `run_checkpoint_eval(checkpoint_path: str, ifeval_test_ds, device: str = "cuda") -> dict` — **does NOT take `step`/`model`/`tokenizer`** as h-m1/03_logic.md claims; it loads the model fresh from `checkpoint_path` internally. Returns `{"ifeval_acc": float, "total": int, "correct": int}` (no `step` key).
- `check_gate_metrics(history: list[dict]) -> dict` — takes only `history`, returns `{"pass": bool, "reason": str, "details": {...}}`.
- `CombinedRewardModel.set_weights(alpha, beta)` exists on the reward model instance, **not** on `RewardConfig`. H-M3 alpha sweep sets `cfg.reward.alpha/beta` directly (dataclass fields) before calling `run_training`, which internally constructs `CombinedRewardModel(alpha=cfg.reward.alpha, beta=cfg.reward.beta, ...)` — no `set_weights` call needed from sweep code.
- `ExperimentConfig` presets are plain `RewardConfig(alpha=.., beta=..)` instances (`T1_COMBINED`, `B2_HELPFULNESS_ONLY` etc.) assigned to `cfg.reward` — confirmed nested-dataclass pattern.
- `checkpoints` are saved at `{output_dir}/checkpoints/step_{N}`; final checkpoint at `step_{cfg.ppo.total_steps}` — H-M3 must read this path convention for `evaluate_alpaca_eval`.

---

## External Dependencies (Base Hypothesis)

```python
# From: h-m1/code/config.py (ACTUAL CODE)
@dataclass
class RewardConfig:
    alpha: float = 0.5
    beta: float = 0.5
    ifeval_soft_margin: float = 0.1

@dataclass
class ExperimentConfig:
    model: ModelConfig
    data: DataConfig
    reward: RewardConfig
    ppo: PPOConfig
    logging: LoggingConfig

# From: h-m1/code/train_ppo.py (ACTUAL CODE)
def run_training(cfg: ExperimentConfig, output_dir: Path) -> tuple[list[dict], "Dataset"]:
    """Runs PPO for cfg.ppo.total_steps. Saves checkpoints at
    output_dir/checkpoints/step_{N}, final at step_{cfg.ppo.total_steps}.
    Returns (history, ifeval_test_ds). Raises TrainingDivergenceError."""
    ...

# From: h-m1/code/evaluate.py (ACTUAL CODE)
def run_checkpoint_eval(checkpoint_path: str, ifeval_test_ds, device: str = "cuda") -> dict:
    """Loads model fresh from checkpoint_path, evals IFEval strict acc.
    Returns {'ifeval_acc': float, 'total': int, 'correct': int}. NO step/model/tokenizer args."""
    ...

def check_gate_metrics(history: list[dict]) -> dict:
    """Returns {'pass': bool, 'reason': str, 'details': dict}."""
    ...
```

**Verified from**: `h-m1/code/config.py`, `rewards.py`, `train_ppo.py`, `evaluate.py` (actual implementation, not specs)

---

## File Structure

```
h-m3/code/
├── config.py        # copied from h-m1 + ALPHA_SWEEP_CONFIGS presets (T1-T4, B2)
├── data.py           # copied verbatim
├── ifeval_signal.py   # copied verbatim
├── rewards.py           # copied verbatim
├── train_ppo.py           # copied verbatim
├── evaluate.py               # copied verbatim
├── alpaca_eval.py              # NEW
├── alpha_sweep.py                # NEW
└── visualize.py                    # NEW
```

---

## A-1: Config Presets [Complexity: 2, Budget: 2]

**Applied**: dataclass-instance-preset pattern (matches h-m1 `T1_COMBINED`/`B2_HELPFULNESS_ONLY`)

### API Signatures

```python
# config.py — appended to copied h-m1 file
T1 = RewardConfig(alpha=0.2, beta=0.8)
T2 = RewardConfig(alpha=0.4, beta=0.6)
T3 = RewardConfig(alpha=0.6, beta=0.4)
T4 = RewardConfig(alpha=0.8, beta=0.2)
B2 = RewardConfig(alpha=1.0, beta=0.0)

ALPHA_SWEEP_CONFIGS: dict[str, RewardConfig] = {"B2": B2, "T1": T1, "T2": T2, "T3": T3, "T4": T4}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | Copy h-m1 files | config/data/ifeval_signal/rewards/train_ppo/evaluate.py verbatim into h-m3/code/ |
| L-1-2 | Add presets | T1-T4/B2 RewardConfig instances + ALPHA_SWEEP_CONFIGS dict |

---

## A-2: AlpacaEval Module [Complexity: 6, Budget: 8]

**Applied**: greedy-decode-generation-pattern (mirrors `run_checkpoint_eval`'s model-load-per-checkpoint style)

### API Signatures

```python
# alpaca_eval.py
def generate_responses(
    checkpoint_path: str,
    eval_prompts: list[str],
    max_new_tokens: int = 256,
    device: str = "cuda",
) -> list[dict]:
    """Loads model from checkpoint_path (matches run_checkpoint_eval load pattern).
    Greedy-decodes (do_sample=False). Returns AlpacaEval format:
    [{'instruction': str, 'output': str, 'generator': str}]."""
    ...

def evaluate_alpaca_eval(
    checkpoint_path: str,
    output_dir: str,
    num_prompts: int | None = 100,  # PoC cost-guard; None = full 805
) -> float:
    """Loads tatsu-lab/alpaca_eval prompts (sliced to num_prompts), calls generate_responses,
    invokes alpaca_eval.evaluate(annotators_config='alpaca_eval_gpt4_turbo_fn').
    Requires OPENAI_API_KEY env var. Returns lc_win_rate (float, 0-1)."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| eval_prompts | list[str], len N | N=100 (PoC) or 805 (full) |
| model_outputs | list[dict], len N | AlpacaEval CLI input format |
| lc_win_rate | float | scalar result from judge |

### Pseudo-code

```
evaluate_alpaca_eval(checkpoint_path, output_dir, num_prompts=100):
  1. prompts_ds = load_dataset("tatsu-lab/alpaca_eval", "alpaca_eval")["eval"]
  2. if num_prompts: prompts_ds = prompts_ds.select(range(num_prompts))
  3. model_outputs = generate_responses(checkpoint_path, [r["instruction"] for r in prompts_ds])
  4. assert os.environ.get("OPENAI_API_KEY"), "OPENAI_API_KEY required"
  5. df_leaderboard, _ = alpaca_eval.evaluate(
       model_outputs=model_outputs,
       annotators_config="alpaca_eval_gpt4_turbo_fn",
       output_path=output_dir,
     )
  6. return float(df_leaderboard["length_controlled_winrate"].iloc[0]) / 100.0
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | generate_responses | Load checkpoint, greedy decode, format dicts |
| L-2-2 | Batch decode loop | Iterate prompts, `tokenizer.batch_decode` |
| L-2-3 | evaluate_alpaca_eval - load/slice | Load AlpacaEval prompts, apply `num_prompts` cost-guard |
| L-2-4 | evaluate_alpaca_eval - judge call | Wire `alpaca_eval.evaluate`, GPT-4 turbo annotator |

---

## A-3: Alpha Sweep Orchestration [Complexity: 8, Budget: 11]

**Applied**: sweep-orchestration-pattern (sequential train→eval→aggregate per config)

### API Signatures

```python
# alpha_sweep.py
def run_sweep(
    configs: dict[str, "RewardConfig"],   # ALPHA_SWEEP_CONFIGS
    base_cfg: "ExperimentConfig",
    output_dir: str,
    alpaca_num_prompts: int | None = 100,
) -> dict:
    """For each name, reward_cfg in configs:
      cfg = replace(base_cfg, reward=reward_cfg); run_training(cfg, Path(output_dir)/name);
      evaluate_alpaca_eval(final_ckpt_path, ...); run_checkpoint_eval(final_ckpt_path, ifeval_test);
      check_gate_metrics(history).
    Returns {name: {'alpaca_lc': float, 'ifeval_acc': float, 'gate': dict, 'history': list[dict]}}."""
    ...

def verify_gate(results: dict) -> bool:
    """FR-5: max(results[T].alpaca_lc for T in T1..T4) >= 0.95 * results['B2'].alpaca_lc.
    Prints B2 lc, best-T name+lc, threshold, PASS/FAIL. Returns bool."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| results | dict[str, dict] | keys: B2,T1,T2,T3,T4 |
| results[name]["history"] | list[dict] | from `run_training` (h-m1 log_entry schema) |

### Pseudo-code

```
run_sweep(configs, base_cfg, output_dir, alpaca_num_prompts=100):
  results = {}
  for name, reward_cfg in configs.items():
    cfg = dataclasses.replace(base_cfg, reward=reward_cfg)
    run_out_dir = Path(output_dir) / name
    history, ifeval_test = run_training(cfg, run_out_dir)          # may raise TrainingDivergenceError
    final_ckpt = run_out_dir / "checkpoints" / f"step_{cfg.ppo.total_steps}"
    alpaca_lc = evaluate_alpaca_eval(str(final_ckpt), str(run_out_dir), alpaca_num_prompts)
    ifeval_result = run_checkpoint_eval(str(final_ckpt), ifeval_test)
    gate = check_gate_metrics(history)
    results[name] = {
      "alpaca_lc": alpaca_lc, "ifeval_acc": ifeval_result["ifeval_acc"],
      "gate": gate, "history": history,
    }
  return results

verify_gate(results):
  b2_lc = results["B2"]["alpaca_lc"]
  t_scores = {k: v["alpaca_lc"] for k, v in results.items() if k != "B2"}
  best_name = max(t_scores, key=t_scores.get)
  threshold = 0.95 * b2_lc
  passed = t_scores[best_name] >= threshold
  print(f"B2={b2_lc:.3f} best={best_name}({t_scores[best_name]:.3f}) threshold={threshold:.3f} "
        f"{'PASS' if passed else 'FAIL'}")
  return passed
```

### Subtasks [11/11 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | Loop skeleton + cfg replace | Iterate configs, build per-run cfg/output_dir |
| L-3-2 | Wire run_training | Call, catch TrainingDivergenceError → log+skip |
| L-3-3 | Wire evaluate_alpaca_eval | Locate final checkpoint path, call |
| L-3-4 | Wire run_checkpoint_eval + gate | IFEval acc + check_gate_metrics, assemble dict |
| L-3-5 | verify_gate | Threshold compare, formatted print, return bool |

---

## A-4: Visualization [Complexity: 3, Budget: 6]

**Applied**: matplotlib (already-installed dependency, rung 5)

### API Signatures

```python
# visualize.py
def plot_baseline_vs_sweep_bar(results: dict, out_dir: str) -> None:
    """Bar chart: alpaca_lc for B2, T1-T4."""
    ...

def plot_pareto_frontier(results: dict, out_dir: str) -> None:
    """Scatter: x=ifeval_acc, y=alpaca_lc, one point per config, B2 marked distinctly."""
    ...

def plot_alpha_line(results: dict, configs: dict, out_dir: str) -> None:
    """Line chart: x=alpha (from configs[name].alpha), y=alpaca_lc, sorted by alpha."""
    ...
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | plot_baseline_vs_sweep_bar | Bar chart of alpaca_lc per config |
| L-4-2 | plot_pareto_frontier | Scatter ifeval_acc vs alpaca_lc |
| L-4-3 | plot_alpha_line | Sort by alpha, line plot |

skipped: separate `run_experiment.py`/`run_poc.py` entrypoints — reuse h-m1's copied versions with `ALPHA_SWEEP_CONFIGS` swapped in for the ablation dict; add only if h-m3 needs a distinct CLI.
