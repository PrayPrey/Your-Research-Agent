# Logic Design: H-M2
# Min vs. Mean Log-Prob Aggregation Sensitivity Across Distribution Types

**Hypothesis:** H-M2 (MECHANISM)
**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr

Applied: aggregation-ablation-pattern (single inference pipeline, three aggregation functions compared via rank-order correlation)
Applied: dual-path-data-loading (H-M1 cache-first with fallback to re-inference)
Applied: bootstrap-ci-comparison (paired bootstrap on Spearman ρ differential for direction confidence)

---

## External Dependencies API

### From `h-e1/code/inference.py` (verified in H-M1)

```python
def load_model(model_key: str) -> Tuple[PreTrainedModel, PreTrainedTokenizer]
# Loads frozen fp16 model in eval mode, device_map="auto"

def extract_token_logprobs(
    model, tokenizer, prompt: str, max_new_tokens: int = 20
) -> Tuple[List[float], str]
# Returns (token_logprobs: List[float], generated_text: str)
# token_logprobs: all <= 0.0, length = number of generated tokens
```

### From `scipy.stats`

```python
from scipy.stats import spearmanr, bootstrap
# spearmanr(x, y) -> SpearmanrResult(statistic, pvalue)
# bootstrap((x, y), statistic, n_resamples=1000, paired=True, method='percentile')
```

### From `sklearn.metrics`

```python
from sklearn.metrics import roc_auc_score
# roc_auc_score(y_true, y_score) -> float
# NOTE: pass -scores because lower score = more hallucinated
```

---

## L-3: Token Log-Prob Extraction

### API

```python
def extract_token_logprobs(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    prompt: str,
    max_new_tokens: int = 20,
) -> np.ndarray:
    """
    Single greedy forward pass. Returns per-token log-probs of generated answer.

    Returns:
        np.ndarray shape (T,), T = generated tokens, all values <= 0.0
        Returns empty array if T == 0.
    """
```

### Pseudo-code

```python
def extract_token_logprobs(model, tokenizer, prompt, max_new_tokens=20):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    input_len = inputs.input_ids.shape[1]

    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            return_dict_in_generate=True,
            output_scores=True,
        )

    # out.scores: tuple of (vocab_size,) logits, one per generated token
    # out.sequences[0]: full sequence including prompt
    generated_ids = out.sequences[0, input_len:]   # shape (T,)

    if len(generated_ids) == 0:
        return np.array([], dtype=np.float32)

    token_logprobs = []
    for score, tok_id in zip(out.scores, generated_ids):
        # score shape: (1, vocab_size) or (vocab_size,)
        logprob = torch.log_softmax(score[0], dim=-1)[tok_id].item()
        token_logprobs.append(logprob)

    result = np.array(token_logprobs, dtype=np.float32)
    # Invariant: all <= 0.0
    assert np.all(result <= 0.0), "log-prob > 0 detected — extraction bug"
    return result
```

### Tensor shapes

| Variable | Shape | Notes |
|----------|-------|-------|
| `inputs.input_ids` | `(1, L)` | L = prompt tokens |
| `out.scores` | `Tuple[(1, V), ...]` | V = vocab size; one per generated token |
| `out.sequences[0]` | `(L+T,)` | full sequence |
| `generated_ids` | `(T,)` | generated token IDs |
| return value | `(T,)` | float32, all ≤ 0.0 |

---

## L-4: Cache Load / Re-inference

### API

```python
def load_or_run_inference(
    dataset_name: str,       # "trivia_qa", "nq", "truthful_qa"
    model_key: str,          # "llama2", "mistral"
    config,                  # config module with all paths
) -> Tuple[List[np.ndarray], np.ndarray]:
    """
    Cache-first loading. Returns (logprob_arrays, labels).

    logprob_arrays: List of (T_i,) arrays, one per sample
    labels: np.ndarray shape (N,), dtype int, values 0 or 1

    Path A: Load from h-m2/results/logprobs_{model}_{dataset}.npy (own cache)
    Path B: Load from h-m1/results/ (LLaMA-2-7B TriviaQA/NQ only)
    Path C: Re-run inference via H-E1 pipeline, cache to h-m2/results/
    """
```

### Pseudo-code

```python
def load_or_run_inference(dataset_name, model_key, config):
    own_cache_lp = f"{config.RESULTS_DIR}/logprobs_{model_key}_{dataset_name}.npy"
    own_cache_lb = f"{config.RESULTS_DIR}/labels_{model_key}_{dataset_name}.npy"

    # Path A: own cache
    if os.path.exists(own_cache_lp) and os.path.exists(own_cache_lb):
        logprob_arrays = list(np.load(own_cache_lp, allow_pickle=True))
        labels = np.load(own_cache_lb)
        return logprob_arrays, labels

    # Path B: H-M1 cache (only LLaMA-2-7B on TriviaQA/NQ)
    if model_key == "llama2" and dataset_name in ("trivia_qa", "nq"):
        hm1_lp = f"{config.H_M1_RESULTS_DIR}/logprobs_llama2_{dataset_name}.npy"
        hm1_lb = f"{config.H_M1_RESULTS_DIR}/labels_llama2_{dataset_name}.npy"
        if os.path.exists(hm1_lp) and os.path.exists(hm1_lb):
            logprob_arrays = list(np.load(hm1_lp, allow_pickle=True))
            labels = np.load(hm1_lb)
            # Save to own cache
            np.save(own_cache_lp, np.array(logprob_arrays, dtype=object))
            np.save(own_cache_lb, labels)
            return logprob_arrays, labels

    # Path C: re-run inference
    samples = load_dataset_samples(dataset_name, config.N_SAMPLES[dataset_name], config.SEED)
    model, tokenizer = load_model(config.MODELS[model_key])
    few_shot_k = config.FEW_SHOT_K[dataset_name]

    logprob_arrays = []
    labels = []
    degenerate_count = 0

    for i, sample in enumerate(samples):
        prompt = build_prompt(sample, dataset_name, few_shot_k)
        lp = extract_token_logprobs(model, tokenizer, prompt, config.MAX_NEW_TOKENS)
        generated_text = tokenizer.decode(...)  # from out.sequences

        if len(lp) < config.MIN_GENERATED_TOKENS:
            degenerate_count += 1
        else:
            logprob_arrays.append(lp)
            label = score_sample(generated_text, sample, dataset_name)
            labels.append(label)

        print(f"[H-M2] sample {i}: min={lp.min():.4f}, mean={lp.mean():.4f}, sum={lp.sum():.4f}")

    # Fail-fast if too many degenerate
    if degenerate_count / len(samples) > config.DEGENERATE_FRACTION_MAX:
        raise RuntimeError(f"Degenerate fraction {degenerate_count/len(samples):.2%} exceeds threshold")

    labels_arr = np.array(labels, dtype=int)

    os.makedirs(config.RESULTS_DIR, exist_ok=True)
    np.save(own_cache_lp, np.array(logprob_arrays, dtype=object))
    np.save(own_cache_lb, labels_arr)

    return logprob_arrays, labels_arr
```

---

## L-5: Aggregation Functions

### API

```python
def min_score(lp: np.ndarray) -> float:
    """Most uncertain single generated token. Maximally sensitive to peaked distributions."""
    return float(np.min(lp))

def mean_score(lp: np.ndarray) -> float:
    """Average uncertainty across all generated tokens. Integrates flat distributions."""
    return float(np.mean(lp))

def raw_sum(lp: np.ndarray) -> float:
    """Joint log-prob; length-dependent baseline (penalizes longer outputs)."""
    return float(np.sum(lp))

def compute_all_scores(logprob_arrays: List[np.ndarray]) -> Dict[str, np.ndarray]:
    """
    Returns {
        "min":     (N,) array,
        "mean":    (N,) array,
        "raw_sum": (N,) array,
    }
    All values <= 0.0 (log-probs are negative).
    """
    n = len(logprob_arrays)
    mins    = np.zeros(n, dtype=np.float64)
    means   = np.zeros(n, dtype=np.float64)
    sums    = np.zeros(n, dtype=np.float64)
    for i, lp in enumerate(logprob_arrays):
        mins[i]  = np.min(lp)
        means[i] = np.mean(lp)
        sums[i]  = np.sum(lp)
    # Sanity check: min <= mean <= 0 for all samples
    assert np.all(mins <= means), "min > mean detected — aggregation bug"
    assert np.all(means <= 0.0), "mean > 0 detected — log-prob extraction bug"
    return {"min": mins, "mean": means, "raw_sum": sums}
```

---

## L-6: Statistical Analysis

### Spearman ρ with Bootstrap CI

```python
def compute_spearman_with_ci(
    scores: np.ndarray,
    labels: np.ndarray,
    n_resamples: int = 1000,
    ci: float = 0.95,
) -> Tuple[float, float, Tuple[float, float]]:
    """
    Returns (rho, p_value, (ci_low, ci_high)).
    rho: Spearman rank-order correlation between scores and labels.
    Positive rho = higher score correlates with correct (label=1).
    Since log-probs are negative (less negative = higher confidence),
    positive rho means higher (less negative) log-prob → correct.
    """
    rho, pval = spearmanr(scores, labels)

    def stat(data):
        s, l = data
        return spearmanr(s, l).statistic

    res = bootstrap(
        (scores, labels), stat,
        n_resamples=n_resamples,
        confidence_level=ci,
        paired=True,
        method='percentile',
    )
    return float(rho), float(pval), (res.confidence_interval.low, res.confidence_interval.high)
```

### AUROC

```python
def compute_auroc(scores: np.ndarray, labels: np.ndarray) -> float:
    """
    Lower scores (more negative log-probs) predict hallucination (label=0).
    Negate scores so that larger value → more hallucinated → better AUROC.
    """
    return float(roc_auc_score(labels, -scores))
```

### ρ Differential

```python
def compute_rho_differential(
    scores_min: np.ndarray,
    scores_mean: np.ndarray,
    labels: np.ndarray,
    n_resamples: int = 1000,
) -> Dict:
    """
    Returns {
        "rho_min": float,
        "rho_mean": float,
        "diff": float,          # rho(min) - rho(mean)
        "ci_low": float,
        "ci_high": float,
        "min_beats_mean": bool,
    }
    """
    rho_min, _, _ = compute_spearman_with_ci(scores_min, labels, n_resamples)
    rho_mean, _, _ = compute_spearman_with_ci(scores_mean, labels, n_resamples)

    def stat_diff(data):
        s_min, s_mean, l = data
        r_min = spearmanr(s_min, l).statistic
        r_mean = spearmanr(s_mean, l).statistic
        return r_min - r_mean

    res = bootstrap(
        (scores_min, scores_mean, labels), stat_diff,
        n_resamples=n_resamples,
        confidence_level=0.95,
        paired=True,
        method='percentile',
    )
    diff = rho_min - rho_mean
    return {
        "rho_min": rho_min,
        "rho_mean": rho_mean,
        "diff": diff,
        "ci_low": res.confidence_interval.low,
        "ci_high": res.confidence_interval.high,
        "min_beats_mean": diff > 0,
    }
```

---

## L-7: Gate Evaluation

```python
def gate_check(results: Dict) -> Dict:
    """
    results structure:
    {
        model_key: {
            dataset_name: {
                "rho_min": float,
                "rho_mean": float,
                "rho_raw_sum": float,
                "auroc_min": float,
                "auroc_mean": float,
                "auroc_raw_sum": float,
                "diff_min_mean": float,
                ...
            }
        }
    }

    P1: rho(min) > rho(mean) on TriviaQA or NQ for >= 1 model
    P2: rho(mean) > rho(min) on TruthfulQA for >= 1 model
    """
    p1_met = any(
        results[m][ds]["rho_min"] > results[m][ds]["rho_mean"]
        for m in results
        for ds in ("trivia_qa", "nq")
        if ds in results[m]
    )
    p2_met = any(
        results[m]["truthful_qa"]["rho_mean"] > results[m]["truthful_qa"]["rho_min"]
        for m in results
        if "truthful_qa" in results[m]
    )

    if p1_met and p2_met:
        gate = "PASS"
    elif p1_met:
        gate = "PARTIAL_PASS_P1_ONLY"
    elif p2_met:
        gate = "PARTIAL_PASS_P2_ONLY"
    else:
        gate = "FAIL"

    return {"gate": gate, "p1_met": p1_met, "p2_met": p2_met}
```

---

## L-8: Label Generation

### TriviaQA / NQ

```python
def score_triviaqa_nq(generated: str, reference_answers: List[str]) -> int:
    """Exact-match after normalization (lowercase, strip punct/articles)."""
    def normalize(s):
        s = s.lower().strip()
        s = re.sub(r'\b(a|an|the)\b', ' ', s)
        s = re.sub(r'[^\w\s]', '', s)
        return ' '.join(s.split())

    gen_norm = normalize(generated)
    return int(any(normalize(ref) == gen_norm for ref in reference_answers))
```

### TruthfulQA

```python
def score_truthfulqa(generated: str, best_answer: str) -> int:
    """
    Binary label from best_answer field.
    Use ROUGE-L >= 0.3 OR exact substring match.
    Truthful (label=1) if generated matches best_answer; hallucinated (label=0) otherwise.
    Note: TruthfulQA questions are adversarially designed — most model answers are wrong (label=0).
    """
    from rouge_score import rouge_scorer
    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    score = scorer.score(best_answer, generated)['rougeL'].fmeasure
    return int(score >= 0.3)
```

---

## Activation Indicators (Sanity Checks)

```python
# Before full experiment — verify mechanism fires correctly
sample_logprobs = logprob_arrays[:10]
assert all(lp.min() <= lp.mean() <= 0 for lp in sample_logprobs), \
    "Log-prob ordering violated — check extraction"

# Early Spearman check on 50 examples
min_scores_50 = np.array([lp.min() for lp in logprob_arrays[:50]])
mean_scores_50 = np.array([lp.mean() for lp in logprob_arrays[:50]])
labels_50 = labels[:50]
print(f"Sample rho(min, label): {spearmanr(min_scores_50, labels_50).statistic:.4f}")
print(f"Sample rho(mean, label): {spearmanr(mean_scores_50, labels_50).statistic:.4f}")

# Check min != mean (aggregation not degenerate)
assert not np.allclose(min_scores_50, mean_scores_50), \
    "min == mean for all samples — aggregation bug or 1-token outputs only"
```

---

## Tensor / Data Shapes

| Variable | Shape | Dtype | Notes |
|----------|-------|-------|-------|
| `token_logprobs` per sample | `(T_i,)` | float32 | all ≤ 0.0; T_i varies per sample |
| `logprob_arrays` | `List[(T_i,)]` | float32 | N elements, variable length |
| `scores["min"]` | `(N,)` | float64 | one min-score per sample |
| `scores["mean"]` | `(N,)` | float64 | one mean-score per sample |
| `scores["raw_sum"]` | `(N,)` | float64 | one sum-score per sample |
| `labels` | `(N,)` | int64 | 0=hallucinated, 1=correct |
| Spearman ρ | scalar | float64 | range [-1, 1] |
| Bootstrap CI | `(2,)` | float64 | (ci_low, ci_high) |
| AUROC | scalar | float64 | range [0, 1] |
| ρ differential | scalar | float64 | rho(min) − rho(mean) |

N per (dataset, model):
- TriviaQA: 400
- NQ-Open: 400
- TruthfulQA: 817
