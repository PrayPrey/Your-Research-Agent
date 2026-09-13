# Logic: H-M3 (MECHANISM)

**Hypothesis:** Amplification Index (AI) > 0 for perplexity filtering vs random, 95% CI excludes zero

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (h-m1)
**Status:** API signatures verified from actual h-m1 code (differ from h-m3 architecture doc's assumed signatures).
**Analyzed Path:** `docs/youra_research/h-m1/code/`
**Relevant Symbols:** `train_one_run` (train.py), `load_corpus`, `filter_by_strategy` (data.py), `Config` (config.py)

**Deviations found (architecture.md assumption vs actual code):**
| Architecture doc assumed | Actual code |
|---|---|
| `load_corpus(cfg) -> list[str]` | `load_corpus(cfg: Config) -> list[tuple[float, str]]` — returns `(ppl_proxy, text)` pairs, not plain strings |
| `filter_by_strategy(dataset, strategy, percentile, seed, target_tokens)` | `filter_by_strategy(samples: list[tuple[float,str]], strategy: str, percentile: int, target_size: int, seed: int) -> list[str]` — takes `load_corpus` output directly, `target_size` = doc count not tokens |
| — | `train_one_run(cfg, corpus: list[str], strategy: str, seed: int) -> tuple[model, tokenizer]` — matches architecture assumption, confirmed as-is |

**Applied:** accuracy-differential-with-bootstrap-CI pattern (mirrors h-m1 `bootstrap_ccr_diff`, generalized to paired group statistic). Archon KB search ("bootstrap confidence interval paired difference numpy") returned no domain-specific hits — pattern implemented directly from h-m1's own `bootstrap_ccr_diff`, not KB.

---

## External Dependencies (Base Hypothesis)

```python
# From: h-m1/code/data.py (ACTUAL CODE)
def load_corpus(cfg: Config) -> list[tuple[float, str]]:
    """Loads OpenWebText (fallback wikitext), returns [(ppl_proxy, text)]."""
    ...

def filter_by_strategy(samples: list[tuple[float, str]], strategy: str,
                        percentile: int, target_size: int, seed: int) -> list[str]:
    """strategy in {'perplexity','random','inverse_perplexity'}. Returns doc texts."""
    ...

# From: h-m1/code/train.py (ACTUAL CODE)
def train_one_run(cfg: Config, corpus: list[str], strategy: str, seed: int) -> tuple:
    """Trains cfg.model_id on corpus for cfg.train_steps steps. Returns (model, tokenizer)."""
    ...
```

**Verified from**: `docs/youra_research/h-m1/code/data.py`, `train.py` (actual implementation). Copy these 3 functions into `h-m3/code/models.py` or `sys.path`-extend to `h-m1/code/` (h-m1 has no package structure, same pattern h-m1 itself used for h-e1 reuse).

---

## M3-1: Config + MMLU/Redux Loading [Complexity: 5]

**Applied:** Standard HF `datasets` load pattern

```python
# config.py
@dataclass
class Config:
    model_id: str = "EleutherAI/pythia-70m"
    strategies: tuple = ("perplexity", "random")
    seeds: tuple = (42, 43, 44)
    percentile: int = 30
    corpus_size: int = 2000
    mmlu_subset: int = 500
    num_fewshot: int = 5
    batch_size: int = 32
    n_bootstrap: int = 10000
    out_dir: str = "figures/"

# data.py
def load_mmlu_eval(cfg: Config) -> list[dict]:
    """cais/mmlu test split, subset to cfg.mmlu_subset. dict keys: question, choices, answer(int)."""
    ...

def load_mmlu_redux_clean() -> list[dict]:
    """edinburgh-dawg/mmlu-redux-2.0 test split, filtered error_type=='ok'."""
    ...
```

---

## M3-2: Contamination Masks [Complexity: 6]

**Applied:** Standard PyTorch (set-based text match, no ML)

```python
def build_contamination_masks(mmlu: list[dict], clean: list[dict]) -> tuple[np.ndarray, np.ndarray]:
    """Aligned to mmlu index. contaminated_mask[i]=True if mmlu[i] NOT in clean set (question text match)."""
    ...
```

### Pseudo-code

```
1. clean_questions = {item['question'].strip().lower() for item in clean}
2. clean_mask = np.array([mmlu[i]['question'].strip().lower() in clean_questions for i in range(len(mmlu))])
3. contaminated_mask = ~clean_mask
4. return contaminated_mask, clean_mask
```

---

## M3-3: Model Training Reuse [Complexity: 8]

**Applied:** direct reuse of h-m1 `load_corpus` + `filter_by_strategy` + `train_one_run` (see External Dependencies)

```python
# models.py
def train_all_models(cfg: Config) -> dict:
    # {f"{strategy}_seed{seed}": (model, tokenizer)}  -- 2 strategies x 3 seeds = 6 models
    ...
```

### Pseudo-code

```
1. samples = load_corpus(cfg)                       # [(ppl, text), ...], loaded once
2. models = {}
3. for strategy in cfg.strategies:                   # perplexity, random
4.     for seed in cfg.seeds:                         # 42, 43, 44
5.         corpus = filter_by_strategy(samples, strategy, cfg.percentile,
                                        target_size=cfg.corpus_size, seed=seed)
6.         model, tokenizer = train_one_run(cfg, corpus, strategy, seed)
7.         models[f"{strategy}_seed{seed}"] = (model, tokenizer)
8. return models
```

---

## M3-4: 5-shot MCQ Log-likelihood Scorer [Complexity: 7]

**Applied:** log-likelihood MCQ scoring (standard lm-eval-harness pattern, implemented directly — h-m1 had no 5-shot impl to reuse)

```python
# evaluate.py
def build_fewshot_prompt(item: dict, fewshot_examples: list[dict], num_fewshot: int) -> str:
    """Concatenates num_fewshot Q/A examples + target question stem."""
    ...

def score_mcq_loglikelihood(model, tokenizer, item: dict, fewshot_examples: list[dict],
                             num_fewshot: int, device) -> int:
    """Returns predicted choice idx (argmax total log-prob per choice continuation)."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids (per choice) | [1, T] | prompt + choice text |
| logits | [1, T, V] | V = pythia-70m vocab (50304) |
| choice_logprobs | [4] | summed token log-probs per MCQ choice |

### Pseudo-code

```
1. prompt = build_fewshot_prompt(item, fewshot_examples, num_fewshot)
2. for choice_idx, choice_text in enumerate(item['choices']):
3.     full_text = prompt + choice_text
4.     input_ids = tokenizer(full_text, return_tensors='pt').input_ids.to(device)
5.     with torch.no_grad(): logits = model(input_ids).logits
6.     choice_token_ids = tokenizer(choice_text).input_ids
7.     logprob = sum(log_softmax(logits[0, -len(choice_token_ids)-1:-1]).gather(choice_token_ids))
8. return argmax(logprobs)
```

---

## M3-5: Batch MMLU Evaluation [Complexity: 6]

```python
def eval_model_on_mmlu(model, tokenizer, mmlu: list[dict], cfg: Config) -> np.ndarray:
    """Bool correctness array, len(mmlu). Uses score_mcq_loglikelihood per item (fewshot examples sampled from held-out mmlu subset)."""
    ...

def eval_all(models: dict, mmlu: list[dict], cfg: Config) -> dict:
    """{model_id: correctness_array}. Loops all 6 models."""
    ...
```

---

## M3-6: Delta + AI Computation [Complexity: 5]

```python
# metrics.py
def compute_deltas(correctness: dict, contaminated_mask: np.ndarray, clean_mask: np.ndarray) -> dict:
    # {model_id: acc_contaminated - acc_clean}
    ...

def amplification_index(deltas: dict, treatment: str = "perplexity", baseline: str = "random") -> float:
    # AI = mean(delta_perplexity) - mean(delta_random), across seeds
    ...
```

### Pseudo-code

```
1. for model_id, correct in correctness.items():
2.     acc_contam = correct[contaminated_mask].mean()
3.     acc_clean = correct[clean_mask].mean()
4.     deltas[model_id] = acc_contam - acc_clean
5. ppl_deltas = [deltas[f"perplexity_seed{s}"] for s in cfg.seeds]
6. rand_deltas = [deltas[f"random_seed{s}"] for s in cfg.seeds]
7. AI = mean(ppl_deltas) - mean(rand_deltas)
```

---

## M3-7: Paired Bootstrap CI [Complexity: 6]

**Applied:** paired cluster bootstrap over seed indices, same algorithm as h-m1 `bootstrap_ccr_diff`

```python
def bootstrap_ai_ci(perplexity_deltas: np.ndarray, random_deltas: np.ndarray,
                     n_bootstrap: int = 10000, confidence: float = 0.95) -> tuple[float, float]:
    """Returns (ci_lower, ci_upper). Resamples seed indices jointly (paired) for both arrays."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| perplexity_deltas, random_deltas | [3] | one per seed |
| ai_samples | [10000] | bootstrap resample AI values |

### Pseudo-code

```
1. n = len(perplexity_deltas)   # 3 seeds
2. ai_samples = []
3. for _ in range(n_bootstrap):
4.     idx = np.random.randint(0, n, size=n)   # paired: same idx for both arrays
5.     ai_samples.append(perplexity_deltas[idx].mean() - random_deltas[idx].mean())
6. ci_lower, ci_upper = np.percentile(ai_samples, [2.5, 97.5])
7. return ci_lower, ci_upper
```

---

## M3-8: Gate + Visualization [Complexity: 6]

```python
def gate_check(ai: float, ci_lower: float) -> bool:
    return ai > 0 and ci_lower > 0

# visualize.py
def plot_ai_bar_with_ci(ai: float, ci: tuple[float, float], out_dir: str) -> str:  # required
    ...
def plot_accuracy_heatmap(deltas: dict, out_dir: str) -> str:   # optional
    ...
def plot_delta_boxplot(deltas: dict, out_dir: str) -> str:      # optional
    ...
```

---

## M3-9: Orchestration [Complexity: 5]

```python
# main.py
def run_experiment(cfg: Config) -> dict:
    # {ai, ci, gate_pass, deltas, correctness_summary} + writes figures/experiment_summary.json
    ...

if __name__ == "__main__":
    run_experiment(Config())
```

### Pseudo-code

```
1. models = train_all_models(cfg)                          # M3-3
2. mmlu = load_mmlu_eval(cfg); clean = load_mmlu_redux_clean()  # M3-1
3. contaminated_mask, clean_mask = build_contamination_masks(mmlu, clean)  # M3-2
4. correctness = eval_all(models, mmlu, cfg)                # M3-4/5
5. deltas = compute_deltas(correctness, contaminated_mask, clean_mask)  # M3-6
6. ai = amplification_index(deltas)
7. ci_lower, ci_upper = bootstrap_ai_ci(ppl_deltas, rand_deltas, cfg.n_bootstrap)  # M3-7
8. gate = gate_check(ai, ci_lower)                          # M3-8
9. plot_ai_bar_with_ci(ai, (ci_lower, ci_upper), cfg.out_dir)
10. dump summary JSON; return results dict
```

---

## Self-Validation

- [x] Serena called on h-m1/code/ (base hypothesis exists) — signatures verified, deviations documented
- [x] "Codebase Analysis (Serena)" section included
- [x] Archon KB searched, "Applied:" line present (no domain hits, pattern sourced from h-m1 code)
- [x] No ASCII diagrams, docstrings <=2 lines
- [x] 0 subtasks used (all tasks low complexity, no breakdown needed)
- [x] External Dependencies API section included with actual code signatures
