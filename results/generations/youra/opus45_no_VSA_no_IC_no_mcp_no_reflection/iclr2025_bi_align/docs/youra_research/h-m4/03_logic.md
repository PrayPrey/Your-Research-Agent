# Logic: H-M4

Applied: eval-harness-wrapper-pattern (HFLM + simple_evaluate per checkpoint)
Applied: baseline-vs-treatment-gate-pattern (max-baseline delta threshold)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m3)
**Status**: API signatures verified from base code (per `03_architecture.md` Codebase Analysis / External Dependencies sections — Serena not invocable in this environment, findings reused from architecture doc's prior analysis of `h-m3/code/`)
**Analyzed Path**: `h-m3/code/alpha_sweep.py`, `h-m3/code/config.py`, `h-m3/code/evaluate.py`
**Relevant Symbols**: `ALPHA_SWEEP_CONFIGS` (dict-of-presets pattern), checkpoint output layout `{output_dir}/{name}/checkpoints/step_{total_steps}`, `run_checkpoint_eval(path: str) -> dict` interface convention

No training in H-M4 (pure evaluation) — new modules (`safety_eval.py`, `transfer_analysis.py`) have no prior implementation to match; they follow H-M3's `config.py` dataclass+dict style and `evaluate.py`'s path-in/dict-out interface convention.

---

## A-1: Config [Complexity: 2, Budget: 2]

**Applied**: flat-dataclass-plus-dict-of-presets (H-M3 convention)

```python
# config.py
from dataclasses import dataclass

CHECKPOINT_PATHS: dict[str, str] = {
    "b1": "checkpoints/b1_sft",                                   # external, not from H-M3
    "b2": "h-m3/code/checkpoints/B2/checkpoints/step_1000",
    "b3": "checkpoints/b3_quality_rlhf",                           # external, not from H-M3
    "t1": "h-m3/code/checkpoints/T1/checkpoints/step_1000",
    "t2": "h-m3/code/checkpoints/T2/checkpoints/step_1000",
    "t3": "h-m3/code/checkpoints/T3/checkpoints/step_1000",
    "t4": "h-m3/code/checkpoints/T4/checkpoints/step_1000",
}

TASKS: list[str] = ["truthfulqa_mc1", "truthfulqa_mc2", "bbq"]
GATE_THRESHOLD_PP: float = 2.0
BASELINES: list[str] = ["b1", "b2", "b3"]
TREATMENTS: list[str] = ["t1", "t2", "t3", "t4"]

@dataclass
class EvalConfig:
    batch_size: int = 8
    device: str = "cuda"
    bootstrap_n: int = 1000
    seed: int = 42
```

### Subtasks [used: n/a — config has no further breakdown]

---

## A-2 / M4-1: Checkpoint Resolution [Complexity: 5, Budget: 1+2+1+1]

**Applied**: fail-fast validation (no silent path guessing)

```python
def resolve_checkpoint(name: str, checkpoint_paths: dict[str, str]) -> str:
    """Return validated path; raise FileNotFoundError if missing (esp. b1/b3)."""
    ...
```

### Pseudo-code

```
1. path = checkpoint_paths.get(name)
2. if path is None or not os.path.isdir(path):
       raise FileNotFoundError(f"Checkpoint '{name}' not found at {path} "
                                f"(b1/b3 are external inputs, not H-M3 sweep outputs)")
3. return path
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | Lookup | Read `checkpoint_paths[name]`, handle missing key |
| L-1-2 | Existence check | `os.path.isdir` validation + informative error for b1/b3 |
| L-1-3 | Batch resolve | `resolve_all(names, checkpoint_paths) -> dict[str, str]` loop wrapper |
| L-1-4 | Logging | Log resolved path per model name (1 line each) |

---

## A-3 / M4-2: lm-eval-harness Wrapper [Complexity: 10, Budget: 3+3+2+2]

**Applied**: HFLM + `evaluator.simple_evaluate` wrapper (lm-evaluation-harness)

```python
# safety_eval.py
from lm_eval import evaluator
from lm_eval.models.huggingface import HFLM

def evaluate_model(name: str, path: str, cfg: "EvalConfig", tasks: list[str]) -> dict[str, float]:
    """Load HFLM(path), run simple_evaluate, extract acc per task. Returns {task: acc}."""
    ...

def evaluate_all(checkpoint_paths: dict[str, str], cfg: "EvalConfig",
                  tasks: list[str] = None) -> dict[str, dict[str, float]]:
    """Loop evaluate_model over all 7 models. Returns {model_name: {task: acc}}."""
    ...
```

### Pseudo-code

```
evaluate_model(name, path, cfg, tasks):
    1. model = HFLM(pretrained=path, batch_size=cfg.batch_size, device=cfg.device)
    2. raw = evaluator.simple_evaluate(model=model, tasks=tasks,
                                        batch_size=cfg.batch_size, random_seed=cfg.seed)
    3. scores = {}
    4. for task in tasks:
           scores[task] = raw["results"][task]["acc"]
           if task == "bbq":
               scores["bbq_bias_score"] = raw["results"][task].get("bias_score", nan)
    5. return scores

evaluate_all(checkpoint_paths, cfg, tasks=TASKS):
    1. for name, path in checkpoint_paths.items():
           resolved = resolve_checkpoint(name, checkpoint_paths)
           results[name] = evaluate_model(name, resolved, cfg, tasks)
    2. return results  # {name: {task: acc}}
```

### Tensor/Output Shapes

| Variable | Type | Note |
|----------|------|------|
| raw["results"] | dict[str, dict] | lm-eval-harness native output, keyed by task |
| results | dict[str, dict[str, float]] | 7 models x 3-4 metrics |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | HFLM init | Build HFLM wrapper from resolved path + EvalConfig |
| L-2-2 | simple_evaluate call | Invoke with tasks/batch_size/seed, catch OOM/task-registry errors |
| L-2-3 | Extraction | Pull `acc` (and `bias_score` for bbq) from results dict |
| L-2-4 | Loop + aggregate | `evaluate_all` orchestration over 7 checkpoints, per-model try/except continue-on-fail with logged skip |

---

## A-4 / M4-3: Bootstrap CI [Complexity: 4, Budget: 1+1+1+1]

```python
def bootstrap_ci(scores: list[float], n_bootstrap: int = 1000, ci: float = 0.95) -> tuple[float, float]:
    """Percentile bootstrap CI. scores: per-item 0/1 correctness list."""
    ...
```

### Pseudo-code

```
1. rng = np.random.default_rng(seed)
2. boots = [np.mean(rng.choice(scores, size=len(scores), replace=True)) for _ in range(n_bootstrap)]
3. lower, upper = np.percentile(boots, [(1-ci)/2*100, (1+ci)/2*100])
4. return (lower, upper)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | Resample loop | n_bootstrap iterations of `np.random.choice` mean |
| L-3-2 | Percentile calc | 2.5/97.5 percentile extraction |
| L-3-3 | Seeded RNG | Use `cfg.seed` for reproducibility |
| L-3-4 | Per-metric wrapper | Apply across all task metrics for all 7 models |

---

## A-5 / M4-4: Gate Verification [Complexity: 6, Budget: 2+2+1+1]

```python
# transfer_analysis.py
def verify_gate(results: dict[str, dict[str, float]], baselines: list[str],
                 treatments: list[str], threshold_pp: float = 2.0) -> dict:
    """Per-metric: baseline_max, best_treatment, improvement_pp, pass. gate_pass = any(pass)."""
    ...
```

### Pseudo-code

```
1. for metric in TASKS:
       baseline_max = max(results[b][metric] for b in baselines)
       best_t_name = argmax(treatments, key=lambda t: results[t][metric])
       best_t = results[best_t_name][metric]
       improvement_pp = (best_t - baseline_max) * 100
       verification[metric] = {
           "baseline_max": baseline_max, "best_treatment": best_t_name,
           "improvement_pp": improvement_pp, "pass": improvement_pp >= threshold_pp
       }
2. gate_pass = any(v["pass"] for v in verification.values())
3. return {"per_metric": verification, "gate_pass": gate_pass}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | Per-metric max | baseline_max / best_treatment computation loop |
| L-4-2 | Improvement + pass | pp delta + threshold comparison per metric |
| L-4-3 | Aggregation | `gate_pass = any(...)` across metrics |
| L-4-4 | Print summary | 1-line print per metric (mirrors `verify_h_m4` log format in brief) |

---

## A-6 / M4-5: Statistical Significance [Complexity: 4, Budget: 1+1+1+1]

```python
def statistical_significance(t_scores: list[float], b_scores: list[float],
                              alpha: float = 0.05) -> dict:
    """Two-tailed t-test. Returns t_statistic/p_value/significant."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | t-test call | `scipy.stats.ttest_ind(t_scores, b_scores)` |
| L-5-2 | Significance flag | `p_value < alpha` |
| L-5-3 | Result dict | Assemble `{t_statistic, p_value, significant}` |
| L-5-4 | Per-metric application | Run for each of TASKS, best-T vs pooled baselines |

---

## A-7 / M4-6: Correlation Analysis [Complexity: 7, Budget: 2+3+1+1]

```python
def correlate_transfer(ifeval_gains: dict[str, float],
                        safety_gains: dict[str, float]) -> dict:
    """Pearson r between IFEval Δ (H-M2 input) and safety Δ per treatment (t1-t4)."""
    ...
```

### Pseudo-code

```
1. keys = sorted(set(ifeval_gains) & set(safety_gains))  # expect t1-t4
2. x = [ifeval_gains[k] for k in keys]
3. y = [safety_gains[k] for k in keys]
4. r, p = scipy.stats.pearsonr(x, y)
5. interpretation = "positive" if r > 0 else "negative" if r < 0 else "none"
6. return {"correlation": r, "p_value": p, "interpretation": interpretation, "significant": p < 0.05}
```

`ifeval_gains`/`safety_gains` inputs: `{model: results[model][metric] - results["b2"][metric]}` for `model in TREATMENTS`, computed by caller (`run_experiment.py`) — `ifeval_gains` sourced from H-M2 output artifact, `safety_gains` computed from `evaluate_all` results (truthfulqa_mc1 by default, per brief).

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | Gain computation | Δ vs b2 for ifeval (external H-M2 input) and safety metric |
| L-6-2 | pearsonr call | Compute r, p over aligned t1-t4 vectors |
| L-6-3 | Interpretation | sign-based label + significance flag |
| L-6-4 | Multi-metric variant | Repeat for bbq gains alongside truthfulqa_mc1 |

---

## A-8 / M4-7: Gate Bar Chart [Complexity: 6, Budget: 2+1+1+2]

```python
# visualize.py
def plot_gate_bar(results: dict[str, dict[str, float]], out_dir: str) -> None:
    """T1-T4 vs B1-B3 grouped bar chart, TruthfulQA MC1 + BBQ, 95% CI error bars."""
    ...
```

### Pseudo-code

```
1. models = BASELINES + TREATMENTS
2. for metric in ["truthfulqa_mc1", "bbq"]:
       values = [results[m][metric] for m in models]
       cis = [bootstrap_ci(per_item_scores[m][metric]) for m in models]  # yerr
       subplot: bar(models, values, yerr=cis)
3. savefig(f"{out_dir}/gate_bar.png")
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | Data assembly | Collect values + CI half-widths per model/metric |
| L-7-2 | Bar plot | 2-subplot (MC1, BBQ) grouped bar with error bars |
| L-7-3 | Labeling | Baseline vs treatment color coding, legend, axis labels |
| L-7-4 | Save | `savefig` to `h-m4/figures/gate_bar.png` |

---

## A-9 / M4-8: Correlation + BBQ Figures [Complexity: 7, Budget: 3+1+1+2]

```python
def plot_correlation_scatter(ifeval_gains: dict[str, float],
                              safety_gains: dict[str, float], out_dir: str) -> None:
    """IFEval Δ (x) vs Safety Δ (y) scatter + regression line, t1-t4 points."""
    ...

def plot_bbq_category_breakdown(results: dict, out_dir: str) -> None:
    """Per-category (9 demographic) accuracy: model x category grouped bar or heatmap."""
    ...
```

BBQ per-category source: `raw["results"]` from lm-eval-harness `bbq` task subtasks (per-category keys, e.g. `bbq_age`, `bbq_gender` ...) — `evaluate_model` must retain these sub-scores in returned dict (extend beyond top-level `bbq` acc) for this figure to have data.

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-8-1 | Scatter + regression | scatter(x,y) + `np.polyfit` line, annotate r/p |
| L-8-2 | BBQ category extraction | Pull `bbq_<category>` keys per model from results |
| L-8-3 | Heatmap/grouped bar | model x category matrix plot |
| L-8-4 | Save both | `savefig` correlation_scatter.png, bbq_breakdown.png |

---

## A-10 / M4-9: Experiment Orchestration [Complexity: 8, Budget: 2+3+1+2]

```python
# run_experiment.py
def main(checkpoint_paths: dict[str, str] = None,
         ifeval_gains: dict[str, float] = None,
         subset_n: int | None = None) -> dict:
    """Load configs -> evaluate_all -> verify_gate -> correlate_transfer -> plots.
    subset_n: PoC cost-guard, limit eval samples if set. Returns full results dict, prints PASS/FAIL."""
    ...
```

### Pseudo-code

```
1. checkpoint_paths = checkpoint_paths or CHECKPOINT_PATHS
2. cfg = EvalConfig()
3. resolved = {n: resolve_checkpoint(n, checkpoint_paths) for n in checkpoint_paths}
4. results = evaluate_all(resolved, cfg, TASKS)  # may take subset_n -> lm-eval `limit=subset_n`
5. gate = verify_gate(results, BASELINES, TREATMENTS, GATE_THRESHOLD_PP)
6. sig = {m: statistical_significance([...t-scores...], [...b-scores...]) for m in TASKS}
7. safety_gains = {t: results[t]["truthfulqa_mc1"] - results["b2"]["truthfulqa_mc1"] for t in TREATMENTS}
8. corr = correlate_transfer(ifeval_gains, safety_gains) if ifeval_gains else None
9. plot_gate_bar(results, "h-m4/figures/")
10. if corr: plot_correlation_scatter(ifeval_gains, safety_gains, "h-m4/figures/")
11. plot_bbq_category_breakdown(results, "h-m4/figures/")
12. print(f"Gate: {'PASS' if gate['gate_pass'] else 'FAIL'}")
13. return {"results": results, "gate": gate, "significance": sig, "correlation": corr}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-9-1 | Wiring | Resolve checkpoints, build EvalConfig, call evaluate_all |
| L-9-2 | Analysis chain | verify_gate + statistical_significance + correlate_transfer |
| L-9-3 | PoC cost-guard | `subset_n` param -> `limit=subset_n` passed to `simple_evaluate` |
| L-9-4 | Report + return | print PASS/FAIL, call all 3 plot functions, return combined dict |

---

## External Dependencies (Base Hypothesis)

```python
# From: h-m3/code/alpha_sweep.py (ACTUAL CODE, not PRD path strings)
# Checkpoint layout convention: {output_dir}/{name}/checkpoints/step_{total_steps}
# T1-T4, B2 resolved via this pattern; B1/B3 are external (not in H-M3 sweep) -> FileNotFoundError if absent
```

**Verified from**: `h-m3/code/alpha_sweep.py`, referenced in `03_architecture.md` External Dependencies section (actual implementation, not PRD flat-path strings).

---

## Self-Validation

- No ASCII diagrams
- Docstrings <= 2 lines
- Shapes/types in comments where non-obvious (lm-eval result dicts)
- Subtask counts match architecture budgets exactly (M4-1..M4-9)
- Codebase Analysis section included (base_hypothesis scenario)
