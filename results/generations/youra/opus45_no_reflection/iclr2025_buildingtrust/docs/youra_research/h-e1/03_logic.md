# Logic: H-E1 (EXISTENCE)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code, designing new APIs
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-2: TruthfulQA MC1 Evaluation [Complexity: 10, Budget: 3 subtasks]

**Applied**: lm-evaluation-harness `simple_evaluate` wrapper pattern (no KB match; standard EleutherAI API)

### API Signatures

```python
def eval_truthfulqa_mc1(model_id: str, batch_size: int = 4) -> float:
    """Run lm-eval-harness truthfulqa_mc1 task. Returns MC1 accuracy in [0,1]."""
    ...

def load_hf_model(model_id: str, device: str = "cuda") -> tuple:
    """Loads HF model+tokenizer for lm-eval HFLM wrapper. Returns (model, tokenizer)."""
    ...
```

### Pseudo-code

```
1. lm = lm_eval.models.huggingface.HFLM(pretrained=model_id, batch_size=batch_size, device="cuda")
2. results = lm_eval.simple_evaluate(model=lm, tasks=["truthfulqa_mc1"])
3. return results["results"]["truthfulqa_mc1"]["acc,none"]
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | HFLM wrapper | Instantiate lm_eval HFLM with model_id, batch_size, device |
| L-2-2 | Run simple_evaluate | Call lm_eval.simple_evaluate(tasks=["truthfulqa_mc1"]) |
| L-2-3 | Extract accuracy | Parse `results["results"]["truthfulqa_mc1"]["acc,none"]` -> float |

---

## A-3: TextFooler Attack Evaluation [Complexity: 12, Budget: 3 subtasks]

**Applied**: TextAttack `Attacker` + `AttackArgs` pattern (no KB match; standard QData API)

### API Signatures

```python
def build_textattack_model(model_id: str) -> "textattack.models.wrappers.ModelWrapper":
    """Wrap HF model for TextAttack (HuggingFaceModelWrapper)."""
    ...

def eval_textfooler_asr(model_id: str, num_examples: int = 1000) -> float:
    """Run TextFooler recipe on SST-2 validation. Returns ASR in [0,1]."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| logits | [B, 2] | SST-2 binary classifier output (pos/neg) |

### Pseudo-code

```
1. model_wrapper = HuggingFaceModelWrapper(model, tokenizer)
2. dataset = HuggingFaceDataset("glue", "sst2", split="validation")
3. attack = TextFoolerJin2019.build(model_wrapper)
4. attack_args = AttackArgs(num_examples=num_examples, random_seed=SEED)
5. results = Attacker(attack, dataset, attack_args).attack_dataset()
6. n_success = count(r.__class__.__name__ == "SuccessfulAttackResult" for r in results)
7. n_total = count(r not skipped)  # excludes SkippedAttackResult (already misclassified)
8. asr = n_success / n_total
9. return asr
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | Model wrapper + dataset | Build HuggingFaceModelWrapper + SST-2 HuggingFaceDataset |
| L-3-2 | Run attack | TextFoolerJin2019.build + Attacker.attack_dataset() |
| L-3-3 | Compute ASR | Count success/skipped results -> asr = success / (total - skipped) |

---

## A-5: Correlation Statistics [Complexity: 9, Budget: 3 subtasks]

**Applied**: scipy.stats Pearson + bootstrap resampling + statsmodels partial correlation (no KB match; standard scipy/numpy pattern)

### API Signatures

```python
def pearson_correlation(x: list[float], y: list[float]) -> tuple[float, float]:
    """scipy.stats.pearsonr. Returns (r, p_value)."""
    ...

def bootstrap_ci(x: list[float], y: list[float], n_boot: int = 1000, seed: int = 42) -> tuple[float, float]:
    """Bootstrap resample pairs, recompute r each time. Returns (ci_low, ci_high) at 95%."""
    ...

def partial_correlation(x: list[float], y: list[float], control: list[float]) -> tuple[float, float]:
    """Residualize x,y on control via linear regression, correlate residuals."""
    ...

def evaluate_hypothesis(results: dict) -> dict:
    """Combines above. Returns {r, p_value, ci_95, partial_r, partial_p, pass}."""
    ...
```

### Pseudo-code (bootstrap_ci — non-trivial)

```
1. rng = np.random.default_rng(seed)
2. n = len(x)
3. boot_rs = []
4. for _ in range(n_boot):
5.     idx = rng.integers(0, n, size=n)  # sample with replacement
6.     r, _ = pearsonr(x[idx], y[idx])
7.     boot_rs.append(r)
8. ci_low, ci_high = np.percentile(boot_rs, [2.5, 97.5])
9. return (ci_low, ci_high), boot_rs
```

### Pseudo-code (partial_correlation — non-trivial)

```
1. control = np.array(control).reshape(-1, 1)  # log(params)
2. resid_x = x - LinearRegression().fit(control, x).predict(control)
3. resid_y = y - LinearRegression().fit(control, y).predict(control)
4. partial_r, partial_p = pearsonr(resid_x, resid_y)
5. return partial_r, partial_p
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | Pearson + partial corr | pearsonr(x,y) and residual-based partial_correlation(x,y,log_params) |
| L-5-2 | Bootstrap CI | 1000-resample loop with fixed seed, percentile CI extraction |
| L-5-3 | evaluate_hypothesis + gate | Combine r/p/ci/partial_r into dict; apply gate thresholds (r>0.5,p<0.05 pass) |

---

## Data Flow

```
config.py (MODEL_IDS, MODEL_PARAMS, SEED, N_BOOTSTRAP)
  -> run_eval.run_all(MODEL_IDS)
       calls eval_truthfulqa_mc1() [A-2] and eval_textfooler_asr() [A-3] per model
       -> results = {"model": [...], "mc1_acc": [...], "robustness": [...], "log_params": [...]}
  -> save_results(results, RESULTS_PATH) -> results.json
  -> analyze.evaluate_hypothesis(results) [A-5]
       uses pearson_correlation, bootstrap_ci, partial_correlation
       -> analysis = {r, p_value, ci_95, partial_r, partial_p, pass}
  -> save_analysis(analysis, path) -> analysis.json
  -> visualize.generate_all_figures(results, analysis) [A-6/A-7, out of budget scope]
```

**Non-obvious shapes**: none beyond textattack logits [B,2]; all H-E1 data is scalar-per-model (floats in flat lists), no tensor batching beyond internal model inference calls handled by lm_eval/textattack libraries.
