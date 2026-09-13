# Logic: H-C1 (CPDR vs RedPajama Defaults Comparison)

**Budget**: 0 subtasks (all tasks Low/Medium complexity) — no breakdown needed.

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: API signatures verified from actual H-E1 code (not spec)
**Analyzed Path**: `h-e1/code/{config,data,train,eval}/`
**Relevant Symbols**: `CurationConfig`, `build_dataset`, `build_model`, `train`, `evaluate`, `save_checkpoint`/`load_checkpoint` (internal, not called directly)

**Key finding**: `evaluate()` returns raw per-task scores (`acc`/`acc_norm`), NOT PCA ensemble. `compute_ensemble_score()` in H-E1 evaluator uses PCA across *all* configs in a sweep — not applicable here (PRD FR-3 wants simple mean accuracy across 4 tasks for 2 configs). H-C1 implements its own `compute_ensemble_mean()` in `analysis.py` (plain mean), does not reuse `compute_ensemble_score`.

---

## C-1: Setup & Config [Complexity: 6]

**Applied**: Standard PyTorch / dataclass reuse

```python
# h-c1/code/config.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "h-e1", "code", "config"))
from config import CurationConfig, MODEL_CONFIG, TRAIN_CONFIG, DATA_CONFIG, EVAL_CONFIG

CPDR_CONFIG = CurationConfig("CPDR", 50, "fuzzy_0.85")     # matches H-E1 D2
REDPAJAMA_CONFIG = CurationConfig("RP", 30, "exact")

SEEDS: list[int] = [42, 43, 44]
IMPROVEMENT_THRESHOLD: float = 0.01
CKPT_ROOT: str = "checkpoints"
```

---

## C-2: Dataset Build for Both Configs [Complexity: 8]

**Applied**: Direct reuse, no new pattern

```python
# h-c1/code/run_comparison.py (partial)
from transformers import GPT2Tokenizer
from data.data_pipeline import build_dataset  # h-e1 path added to sys.path
from config import CPDR_CONFIG, REDPAJAMA_CONFIG, TRAIN_CONFIG

def build_both_datasets(tokenizer: GPT2Tokenizer = None) -> tuple:
    """Returns (cpdr_data_iter, rp_data_iter), each yields Tensor [seq_len]."""
    tok = tokenizer or GPT2Tokenizer.from_pretrained("gpt2")
    max_tokens = TRAIN_CONFIG["total_tokens"]  # 10B
    cpdr_iter = build_dataset(CPDR_CONFIG, tok, max_tokens)
    rp_iter = build_dataset(REDPAJAMA_CONFIG, tok, max_tokens)
    return cpdr_iter, rp_iter
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| chunk (yielded) | [1024] | `seq_len` tokens, `dtype=torch.long` |

---

## C-3: Training Loop Integration [Complexity: 10]

**Applied**: Direct reuse of H-E1 `build_model`/`train`

```python
# h-c1/code/run_comparison.py
from train.trainer import build_model, train

def run_single_seed(seed: int, ckpt_root: str = "checkpoints") -> dict:
    """Train+eval CPDR and RP configs for one seed.
    Returns {'cpdr': {task: score}, 'redpajama': {task: score}}.
    """
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    result = {}
    for key, cfg in (("cpdr", CPDR_CONFIG), ("redpajama", REDPAJAMA_CONFIG)):
        data_iter = build_dataset(cfg, tokenizer, TRAIN_CONFIG["total_tokens"])
        model = build_model(seed=seed)
        ckpt_dir = os.path.join(ckpt_root, f"{cfg.config_id}_seed{seed}")
        model_path = train(model, data_iter, ckpt_dir, cfg.config_id)
        result[key] = evaluate(model_path)  # from C-5, dict[str, float]
    return result
```

### Pseudo-code

```
1. for (key, cfg) in [(cpdr, CPDR_CONFIG), (redpajama, REDPAJAMA_CONFIG)]:
2.   data = build_dataset(cfg, tokenizer, total_tokens)
3.   model = build_model(seed)
4.   ckpt_path = train(model, data, ckpt_dir=f"{ckpt_root}/{cfg.config_id}_seed{seed}", cfg.config_id)
5.   result[key] = evaluate(ckpt_path)
6. return result
```

---

## C-4: Multi-Seed Orchestration [Complexity: 8]

```python
# h-c1/code/run_comparison.py
from config import SEEDS

def run_comparison_experiment(seeds: list = SEEDS, ckpt_root: str = "checkpoints") -> dict:
    """Loop seeds, collect per-seed scores. Skips failed seeds with warning.
    Returns {'per_seed': list[dict], 'seeds_completed': list[int]}.
    """
    per_seed = []
    completed = []
    for seed in seeds:
        try:
            scores = run_single_seed(seed, ckpt_root)
            per_seed.append(scores)
            completed.append(seed)
        except Exception as e:
            print(f"[WARN] seed {seed} failed: {e}")
    return {"per_seed": per_seed, "seeds_completed": completed}
```

---

## C-5: Benchmark Evaluation [Complexity: 7]

**Applied**: Direct reuse of `evaluate()`, custom mean (not PC1)

```python
# h-c1/code/run_comparison.py
from eval.evaluator import evaluate
from config import EVAL_CONFIG

def evaluate_model(checkpoint_path: str) -> dict:
    """Returns {task: score} for EVAL_CONFIG['tasks'] (4 tasks)."""
    return evaluate(checkpoint_path, tasks=EVAL_CONFIG["tasks"], batch_size=EVAL_CONFIG["batch_size"])
```

---

## C-6: Statistical Comparison [Complexity: 9]

**Applied**: Standard scipy paired t-test

```python
# h-c1/code/analysis.py
import numpy as np
from scipy import stats

def compute_ensemble_mean(scores: dict, tasks: list) -> float:
    """scores: {task: float}. Returns mean accuracy across tasks."""
    return float(np.mean([scores[t] for t in tasks]))

def paired_ttest(cpdr_scores: list[float], rp_scores: list[float]) -> dict:
    """Both lists: per-seed ensemble means, same length (n_seeds).
    Returns {'t_stat': float, 'p_value': float}.
    """
    t_stat, p_value = stats.ttest_rel(cpdr_scores, rp_scores)
    return {"t_stat": float(t_stat), "p_value": float(p_value)}

def gate_check(cpdr_mean: float, rp_mean: float, threshold: float = 0.01) -> dict:
    """Returns {'improvement': float, 'passed': bool}."""
    improvement = cpdr_mean - rp_mean
    return {"improvement": improvement, "passed": improvement > threshold}
```

### Pseudo-code (aggregation across seeds)

```
1. cpdr_per_seed = [compute_ensemble_mean(s['cpdr'], tasks) for s in per_seed]
2. rp_per_seed   = [compute_ensemble_mean(s['redpajama'], tasks) for s in per_seed]
3. cpdr_mean, rp_mean = mean(cpdr_per_seed), mean(rp_per_seed)
4. ttest = paired_ttest(cpdr_per_seed, rp_per_seed)
5. gate = gate_check(cpdr_mean, rp_mean, IMPROVEMENT_THRESHOLD)
```

---

## C-7: Required Gate Figure [Complexity: 6]

```python
# h-c1/code/figures.py
def plot_ensemble_comparison(results: dict, out_path: str) -> None:
    """Bar chart: CPDR vs RP ensemble mean with error bars (std across seeds).
    results: {'cpdr_per_seed': list[float], 'rp_per_seed': list[float]}."""
    ...
```

---

## C-8: Additional Figures [Complexity: 8]

```python
# h-c1/code/figures.py
def plot_per_benchmark_breakdown(results: dict, out_path: str) -> None:
    """Grouped bar chart per task (4 tasks x 2 configs)."""
    ...

def plot_training_curves(loss_logs: dict, out_path: str) -> None:
    """loss_logs: {'cpdr': list[float], 'redpajama': list[float]} (per-step loss)."""
    ...

def plot_improvement_waterfall(results: dict, out_path: str) -> None:
    """Per-task improvement (CPDR - RP) as waterfall bars."""
    ...
```

---

## C-9: Experiment Entrypoint & Results [Complexity: 7]

```python
# h-c1/code/run_experiment.py
from run_comparison import run_comparison_experiment
from analysis import compute_ensemble_mean, paired_ttest, gate_check
from eval.evaluator import save_results
from config import SEEDS, CKPT_ROOT, IMPROVEMENT_THRESHOLD
from config import EVAL_CONFIG

def main() -> None:
    """Orchestrate: run_comparison_experiment -> analysis -> save JSON -> figures."""
    raw = run_comparison_experiment(SEEDS, CKPT_ROOT)
    tasks = EVAL_CONFIG["tasks"]
    cpdr_per_seed = [compute_ensemble_mean(s["cpdr"], tasks) for s in raw["per_seed"]]
    rp_per_seed = [compute_ensemble_mean(s["redpajama"], tasks) for s in raw["per_seed"]]
    ttest = paired_ttest(cpdr_per_seed, rp_per_seed)
    gate = gate_check(sum(cpdr_per_seed)/len(cpdr_per_seed), sum(rp_per_seed)/len(rp_per_seed), IMPROVEMENT_THRESHOLD)

    output = {"raw": raw, "cpdr_per_seed": cpdr_per_seed, "rp_per_seed": rp_per_seed,
              "ttest": ttest, "gate": gate}
    save_results(output, "output/results.json")

    from figures import (plot_ensemble_comparison, plot_per_benchmark_breakdown,
                          plot_improvement_waterfall)
    plot_ensemble_comparison(output, "figures/gate_ensemble_comparison.png")
    plot_per_benchmark_breakdown(raw, "figures/per_benchmark_breakdown.png")
    plot_improvement_waterfall(raw, "figures/improvement_waterfall.png")

if __name__ == "__main__":
    main()
```

---

## External Dependencies (Base Hypothesis)

### API Signatures (Verified from Actual H-E1 Code)

```python
# From: h-e1/code/config/config.py
@dataclass
class CurationConfig:
    config_id: str
    perplexity_pct: Optional[int]
    dedup: str

# From: h-e1/code/data/data_pipeline.py
def build_dataset(
    config: CurationConfig,
    tokenizer: Optional[GPT2Tokenizer] = None,
    max_tokens: int = None,
) -> Iterator[torch.Tensor]:
    """Yields token chunks. shape: [seq_len] (1024), dtype=torch.long."""
    ...

# From: h-e1/code/train/trainer.py
def build_model(seed: int = None) -> GPT2LMHeadModel: ...

def train(
    model: GPT2LMHeadModel,
    data: Iterator[torch.Tensor],
    ckpt_dir: str,
    config_id: str,
    batch_size: int = None,
    total_steps: int = None,
    ckpt_every: int = 2000,
    device: str = "cuda",
) -> str:
    """Returns path to saved model dir (ckpt_dir/model)."""
    ...

# From: h-e1/code/eval/evaluator.py
def evaluate(checkpoint_path: str, tasks: list = None, batch_size: int = None) -> dict:
    """Returns {task: score} using lm-eval-harness. Falls back to mock if not installed."""
    ...

def save_results(results: dict, path: str) -> None: ...
```

**Verified from**: `h-e1/code/` (actual implementation, read directly — not spec).

**Divergence noted**: H-E1's `compute_ensemble_score()` (PCA-based, requires >=2 sweep configs) is NOT reused. H-C1 implements plain-mean `compute_ensemble_mean()` in its own `analysis.py` per PRD FR-3 ("mean accuracy").
