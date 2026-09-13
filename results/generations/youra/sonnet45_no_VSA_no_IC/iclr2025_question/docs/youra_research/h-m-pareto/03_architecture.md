# Architecture: h-m-pareto

**Date:** 2026-08-20  
**Author:** yoon303b@gmail.com  
**Phase:** 3 - Implementation Planning

**Applied:** Modular pipeline orchestration pattern

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase  
**Status:** UQ methods pattern found from h-e1  
**Analyzed Path:** docs/youra_research/h-e1/code/  
**Findings:** Temperature scaling, conformal prediction, MC dropout implementations exist. Reuse UQ pattern, add Pareto analysis module.

---

## System Overview

Standalone analysis pipeline with 4 modules:

1. **Calibration** - HaluEval calibration (temperature/conformal)
2. **UQ Methods** - Generate uncertainty scores (6 methods × 3 seeds)
3. **AUROC Evaluation** - Compute selective prediction metrics
4. **Pareto Analysis** - Frontier construction + statistical dominance

**Key Design:**
- Cache base model outputs (avoid 18× redundant inference)
- Modular UQ interface (add methods without pipeline changes)
- Statistical rigor via paired t-test

---

## Data Flow

```
HaluEval (cal) → Calibrate T_opt, τ
   ↓
TruthfulQA (test) → Generate base predictions + logits (1×)
   ↓                        ↓
Cache predictions     Apply 6 UQ methods → uncertainty scores (18 runs)
   ↓                        ↓
Correctness labels   Compute AUROC (18 values)
   ↓                        ↓
              Pareto frontier (dominance check)
                     ↓
              Visualizations (4 figures)
```

---

## Module Interfaces

### 1. Calibration (`calibration.py`)

**Dependencies:** torch, transformers

```python
class Calibrator:
    def __init__(self, model, tokenizer, device="cuda"): ...
    def calibrate_temperature(self, dataset: List[dict]) -> float: ...
    def calibrate_conformal(self, dataset: List[dict], alpha=0.1) -> float: ...
```

### 2. UQ Methods (`uq_methods.py`)

**Dependencies:** torch, numpy

```python
class UQMethod:
    def compute_uncertainty(self, logits: torch.Tensor) -> float: ...

class TemperatureScaling(UQMethod):
    def __init__(self, temperature: float): ...
    
class ConformalPrediction(UQMethod):
    def __init__(self, threshold: float): ...
    
class MCDropout(UQMethod):
    def __init__(self, k: int, model, tokenizer): ...
    def compute_uncertainty(self, question: str) -> float: ...
```

### 3. AUROC Evaluation (`evaluation.py`)

**Dependencies:** sklearn, scipy

```python
def label_correctness(prediction: str, correct_answers: List[str]) -> int: ...
def compute_auroc(labels: List[int], scores: List[float]) -> float: ...
def compute_spearman(labels: List[int], scores: List[float]) -> Tuple[float, float]: ...
```

### 4. Pareto Analysis (`pareto_analysis.py`)

**Dependencies:** numpy, scipy.stats

```python
class ParetoFrontier:
    def __init__(self, alpha=0.05, n_seeds=3): ...
    def add_method(self, name: str, cost: float, aurocs: List[float]): ...
    def construct_frontier(self) -> List[str]: ...
    def check_dominance(self, i: str, j: str) -> bool: ...
```

### 5. Orchestration (`main.py`)

**Dependencies:** All modules

```python
def run_calibration(model, cal_dataset): ...
def run_inference(model, test_dataset, cache_path): ...
def run_uq_pipeline(methods, test_data, cache): ...
def run_pareto_analysis(results): ...
def main(): ...
```

---

## File Organization

```
code/
├── calibration.py          # Temperature/conformal calibration
├── uq_methods.py           # 6 UQ method implementations
├── evaluation.py           # AUROC, Spearman, correctness labeling
├── pareto_analysis.py      # Frontier construction
├── visualization.py        # 4 figure generators
├── main.py                 # Pipeline orchestration
└── config.py               # Hyperparameters

results/
├── cache/
│   └── base_predictions.pkl   # Cached model outputs
├── calibration.json           # T_opt, threshold values
├── auroc_scores.json          # 18 (method, seed) pairs
└── pareto_frontier.json       # Pareto set + dominated methods

figures/
├── pareto_frontier.png
├── auroc_bar_chart.png
├── cost_vs_auroc_tradeoff.png
└── spearman_heatmap.png
```

---

## Integration Strategy

### Pipeline Orchestration

**3-Stage Sequential:**

1. **Calibration Stage** (HaluEval)
   - Load model once
   - Generate calibration predictions
   - Optimize T_opt (grid search), compute τ (quantile)
   - Save to `results/calibration.json`

2. **Inference Stage** (TruthfulQA)
   - Check cache: if exists, load from `results/cache/base_predictions.pkl`
   - Else: generate predictions + logits, save cache
   - Label correctness (fuzzy match vs correct_answers)
   - Apply 6 UQ methods × 3 seeds → 18 uncertainty score arrays
   - Compute AUROC for each (method, seed) pair
   - Save to `results/auroc_scores.json`

3. **Analysis Stage**
   - Load AUROC scores
   - Construct Pareto frontier (dominance check)
   - Generate 4 figures
   - Save frontier to `results/pareto_frontier.json`

### Caching Strategy

```python
def load_or_generate_predictions(model, dataset, cache_path):
    if os.path.exists(cache_path):
        return pickle.load(open(cache_path, "rb"))
    
    predictions = model.generate([q["question"] for q in dataset])
    pickle.dump(predictions, open(cache_path, "wb"))
    return predictions
```

**Rationale:** MC dropout k=10 requires 10× inference. Without cache, 6 methods × 3 seeds = 18 full passes. With cache, only 1 full pass + lightweight UQ computation.

### Modular UQ Methods

**Interface Pattern:**
```python
class UQMethod:
    def compute_uncertainty(self, logits: torch.Tensor) -> float:
        raise NotImplementedError
```

**Adding New Method:**
1. Subclass `UQMethod`
2. Implement `compute_uncertainty`
3. Register in `main.py` method list
4. No pipeline changes needed

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup | Project structure + dependencies | 6 | file_structure(1) + deps(1) + config(2) + cache_utils(2) |
| A-2 | Calibration | Temperature + conformal on HaluEval | 8 | temp_grid_search(3) + conformal_quantile(2) + data_loading(2) + save_results(1) |
| A-3 | UQ Methods | Implement 6 methods (reuse h-e1 patterns) | 10 | temp_scaling(2) + conformal(2) + mc_dropout_k1(2) + mc_k3(1) + mc_k5(1) + mc_k10(1) + testing(1) |
| A-4 | AUROC Eval | Correctness labeling + metric computation | 9 | fuzzy_match(3) + auroc_sklearn(2) + spearman(2) + multi_seed(2) |
| A-5 | Pareto Analysis | Frontier construction + paired t-test | 11 | dominance_check(3) + ttest_rel(3) + frontier_logic(3) + validation(2) |
| A-6 | Visualization | 4 figures (scatter, bar, tradeoff, heatmap) | 12 | pareto_scatter(3) + auroc_bars(3) + tradeoff_curves(3) + heatmap(3) |
| A-7 | Orchestration | Pipeline + cache management | 10 | main_loop(3) + cache_logic(3) + multi_seed(2) + error_handling(2) |
| A-8 | Validation | Run full pipeline + verify results | 8 | smoke_test(2) + gate_check(2) + pareto_verify(3) + debug(1) |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3, A-4, A-5, A-6, A-7], Low(4-8): [A-1, A-2, A-8]

**Total:** 74 points (8 tasks)

---

## External Dependencies

### From h-e1 (Pattern Reuse)

Reusing UQ method implementations pattern (not copying code directly):

| Pattern | Source Reference | Usage |
|---------|------------------|-------|
| Temperature Scaling | h-e1/code/uq/methods.py | LBFGS optimization, NLL loss |
| Conformal Prediction | h-e1/code/uq/methods.py | Quantile threshold, nonconformity scores |
| MC Dropout | h-e1/code/uq/methods.py | Enable dropout, k forward passes, entropy |
| AUROC Computation | h-e1/code/eval/metrics.py | sklearn.metrics.roc_auc_score |

**Note:** Not importing h-e1 code. Replicating pattern with Pareto-specific adaptations (cost tracking, multi-seed aggregation).

### Libraries

| Library | Purpose | Version Constraint |
|---------|---------|-------------------|
| transformers | Llama-3.1-8B loading | >=4.30 |
| torch | Model inference, dropout | >=2.0 |
| datasets | TruthfulQA, HaluEval | >=2.0 |
| sklearn | AUROC, metrics | >=1.0 |
| scipy | Paired t-test, Spearman | >=1.10 |
| matplotlib | Visualizations | >=3.5 |

---

## Configuration

### Hyperparameters (`config.py`)

```python
class Config:
    # Model
    model_name = "meta-llama/Llama-3.1-8B-Instruct"
    dtype = "bfloat16"
    device = "cuda"
    
    # Data
    cal_dataset = "halueval"
    test_dataset = "truthfulqa/truthful_qa"
    test_split = "validation"
    
    # UQ Methods
    uq_methods = ["temp_scaling", "conformal", "mc_k1", "mc_k3", "mc_k5", "mc_k10"]
    conformal_alpha = 0.1
    mc_dropout_rate = 0.1
    
    # Evaluation
    seeds = [42, 123, 456]
    batch_size = 8
    
    # Pareto Analysis
    pareto_alpha = 0.05  # Significance level for t-test
    
    # Paths
    cache_dir = "results/cache"
    results_dir = "results"
    figures_dir = "figures"
```

---

## Validation Checks

### Pre-execution Checks

```python
assert len(Config.seeds) == 3, "Exactly 3 seeds required"
assert Config.pareto_alpha == 0.05, "Alpha fixed at 0.05"
assert len(Config.uq_methods) == 6, "Expected 6 UQ methods"
```

### Runtime Validation

```python
# After calibration
assert 0.5 <= T_opt <= 5.0, f"Temperature out of range: {T_opt}"
assert 0.0 <= threshold <= 1.0, f"Threshold out of range: {threshold}"

# After AUROC computation
assert all(0 <= auroc <= 1.0 for auroc in auroc_scores.values()), "AUROC out of bounds"
assert len(auroc_scores) == 18, f"Expected 18 (method, seed) pairs, got {len(auroc_scores)}"

# After Pareto frontier
assert len(pareto_set) >= 1, "Empty Pareto set impossible"
assert len(pareto_set) <= 6, "Pareto set exceeds total methods"
```

### Success Criteria Verification

```python
def verify_hypothesis(pareto_set, auroc_scores):
    # H3: Trade-off exists
    h3_pass = len(pareto_set) >= 2
    
    # H1: MC k=5 highest AUROC
    mc_k5_aurocs = [auroc_scores[f"mc_k5_seed{s}"] for s in Config.seeds]
    mc_k5_mean = np.mean(mc_k5_aurocs)
    max_auroc = max(np.mean([auroc_scores[f"{m}_seed{s}"] for s in Config.seeds]) 
                    for m in ["temp_scaling", "conformal", "mc_k1", "mc_k3", "mc_k5", "mc_k10"])
    h1_pass = mc_k5_mean >= 0.70 and mc_k5_mean == max_auroc
    
    # H2: Temp scaling competitive
    temp_aurocs = [auroc_scores[f"temp_scaling_seed{s}"] for s in Config.seeds]
    temp_mean = np.mean(temp_aurocs)
    h2_pass = abs(temp_mean - mc_k5_mean) <= 0.05
    
    return {"H1": h1_pass, "H2": h2_pass, "H3": h3_pass}
```

---

## Risk Mitigation

### Low Statistical Power (n=3)

**Issue:** Paired t-test requires n~20 for 80% power  
**Mitigation:**
- Report visual inspection in scatter plot
- Add practical significance threshold (AUROC gap > 0.10)
- Include confidence intervals in bar chart

### Cache Invalidation

**Issue:** Cached predictions may become stale  
**Mitigation:**
- Hash config parameters (model name, seed, batch size)
- Include hash in cache filename
- Log cache hits/misses

### MC Dropout Variance

**Issue:** k=1,3 may have high variance  
**Mitigation:**
- Use 3 seeds for all methods (not just MC dropout)
- Report std dev in results
- Flag methods with std > 0.05

---

*Next Phase: 04_coding.md - Implementation with detailed task breakdown*
