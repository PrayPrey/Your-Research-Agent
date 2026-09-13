# Logic: H-E1 API Design

**Version:** 1.0
**Date:** 2026-08-02

Applied: Standard HuggingFace generate + scipy/sklearn statistical testing patterns

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No existing code found in h-e1/code/ (green-field)
**Analyzed Path**: `docs/youra_research/h-e1/code/` — directory does not exist
**Relevant Symbols**: None — new implementation

---

## E2-1: `generate_stochastic()` [Complexity: 14, Budget: E2]

**Applied**: HuggingFace batched generate with tqdm checkpoint-skip

### API Signatures

```python
def generate_stochastic(
    model,                          # PreTrainedModel, bfloat16, device_map="auto"
    tokenizer,                      # PreTrainedTokenizer
    questions: list[str],           # len = N_PROMPTS (2500)
    n_samples: int = N_SAMPLES,     # 5
    temperature: float = TEMPERATURE,  # 0.7
    top_p: float = TOP_P,           # 0.95
    batch_size: int = 8,
    existing: list[list[str]] | None = None,  # checkpoint data for skip logic
) -> list[list[str]]:               # shape (N_PROMPTS, n_samples)
    """Generate n_samples stochastic responses per question."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, L_in] | tokenized batch |
| output | [B, L_in + max_new_tokens] | generated token ids |
| return value | (2500, 5) list of str | |

### Pseudo-code

```
results = existing or []
start_idx = len(results)  # checkpoint-aware skip
for i in tqdm(range(start_idx, len(questions), batch_size)):
    batch_qs = questions[i : i + batch_size]
    try:
        inputs = tokenizer(batch_qs, return_tensors="pt", padding=True).to(model.device)
        with torch.no_grad():
            out = model.generate(
                **inputs,
                do_sample=True,
                temperature=temperature,
                top_p=top_p,
                max_new_tokens=MAX_NEW_TOKENS,
                num_return_sequences=n_samples,
            )
        # out shape: [B * n_samples, L_total]
        decoded = tokenizer.batch_decode(out[:, inputs.input_ids.shape[1]:], skip_special_tokens=True)
        # reshape: (B, n_samples)
        for j in range(len(batch_qs)):
            results.append(decoded[j * n_samples : (j + 1) * n_samples])
    except torch.cuda.OutOfMemoryError:
        torch.cuda.empty_cache()
        # retry with batch_size=1 per item
        for q in batch_qs:
            results.append(_generate_stochastic_single(model, tokenizer, q, n_samples, temperature, top_p))
return results  # (N_PROMPTS, n_samples)
```

### Key Notes

- OOM fallback retries single-item; do NOT skip silently.
- `num_return_sequences=n_samples` doubles the effective batch dim: out is `[B*n_samples, L]`.
- Strip prompt tokens by slicing `out[:, input_ids.shape[1]:]` before decode.

### Subtasks [1/3 used for E2]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E2-1 | stochastic_generate | Implement generate_stochastic with OOM retry + tqdm |

---

## E2-2: `generate_greedy()` [Complexity: 14, Budget: E2]

**Applied**: HuggingFace output_scores → log_softmax token logprob extraction

### API Signatures

```python
def generate_greedy(
    model,
    tokenizer,
    questions: list[str],           # len = N_PROMPTS
    batch_size: int = 8,
) -> tuple[list[str], list[list[float]]]:
    """Greedy decode with token log-probs. Fails fast if output_scores unavailable."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| scores | tuple of T tensors, each [B, vocab] | T = actual generated length |
| stacked | [T, B, vocab] | after torch.stack(scores, dim=0) |
| log_probs | [T, B] | after .log_softmax(-1).gather(-1, token_ids) |
| token_ids | [B, T] | output[:, prompt_len:] argmax (== greedy tokens) |
| per_prompt | list[list[float]] len=(N_PROMPTS, T_i) | T_i varies per prompt |

### Pseudo-code

```
assert hasattr(model, "generate"), "model must support generate()"
all_answers, all_logprobs = [], []
for i in tqdm(range(0, len(questions), batch_size)):
    batch_qs = questions[i : i + batch_size]
    inputs = tokenizer(batch_qs, return_tensors="pt", padding=True).to(model.device)
    prompt_len = inputs.input_ids.shape[1]
    with torch.no_grad():
        out = model.generate(
            **inputs,
            do_sample=False,
            max_new_tokens=MAX_NEW_TOKENS,
            output_scores=True,
            return_dict_in_generate=True,
        )
    assert out.scores is not None, "output_scores=True required; check model/transformers version"
    # out.scores: tuple[T tensors of shape (B, vocab)]
    stacked = torch.stack(out.scores, dim=0)           # [T, B, vocab]
    log_probs_full = stacked.log_softmax(-1)            # [T, B, vocab]
    gen_ids = out.sequences[:, prompt_len:]             # [B, T]
    # gather log-prob of the actually generated token
    token_lp = log_probs_full.gather(
        -1, gen_ids.T.unsqueeze(-1)                    # [T, B, 1]
    ).squeeze(-1)                                       # [T, B]
    token_lp = token_lp.T                              # [B, T]
    decoded = tokenizer.batch_decode(gen_ids, skip_special_tokens=True)
    for j in range(len(batch_qs)):
        all_answers.append(decoded[j])
        all_logprobs.append(token_lp[j].tolist())       # list[float] len=T
return all_answers, all_logprobs
```

### Key Notes

- `return_dict_in_generate=True` is required alongside `output_scores=True`.
- `out.scores` is a tuple of length T (number of generated tokens), NOT padded — each tensor is `(B, vocab)`.
- The assert on `out.scores` provides the fail-fast guarantee from spec.
- Padding tokens in batch may produce spurious log-probs; `skip_special_tokens` handles EOS.

### Subtasks [2/3 used for E2]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E2-2 | greedy_generate | Implement generate_greedy with scores extraction |

---

## E2-3: Checkpoint Strategy [Complexity: 14, Budget: E2]

**Applied**: pickle checkpoint with atomic-safe load_or_generate wrapper

### API Signatures

```python
def load_or_generate(
    force: bool = False,
) -> dict:
    """Load checkpoint if exists and not force, else generate and save."""
    ...
```

### Pickle Serialization Schema

```python
signals: dict = {
    "stochastic": list[list[str]],     # shape (2500, 5)
    "greedy_answers": list[str],        # shape (2500,)
    "token_logprobs": list[list[float]], # shape (2500, T_i) — ragged
}
```

### Pseudo-code

```
checkpoint = Path(CHECKPOINT_PATH)
if checkpoint.exists() and not force:
    with open(checkpoint, "rb") as f:
        data = pickle.load(f)
    # validate schema keys present
    assert {"stochastic", "greedy_answers", "token_logprobs"} <= data.keys()
    return data

# generate fresh
data = {}
questions, aliases = zip(*[(d["question"], d["aliases"]) for d in load_dataset_slice()])
model, tokenizer = load_llm()
data["stochastic"] = generate_stochastic(model, tokenizer, list(questions))
data["greedy_answers"], data["token_logprobs"] = generate_greedy(model, tokenizer, list(questions))
# free GPU before NLI model loads
del model, tokenizer; torch.cuda.empty_cache()

checkpoint.parent.mkdir(parents=True, exist_ok=True)
with open(checkpoint, "wb") as f:
    pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
return data
```

### Key Notes

- Delete LLM from GPU before loading NLI/judge models to avoid OOM.
- `force=True` re-runs all 15K inference calls — use only deliberately.

### Subtasks [3/3 used for E2]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E2-3 | checkpoint | Implement load_or_generate with pickle schema |

---

## E3-1: `check_implication()` + `get_semantic_ids()` [Complexity: 14, Budget: E3]

**Applied**: jlko/semantic_uncertainty bidirectional NLI union-find clustering

### API Signatures

```python
def check_implication(
    text1: str,
    text2: str,
    nli_model,          # sentence_transformers CrossEncoder
) -> int:
    """Returns 0=contradiction, 1=neutral, 2=entailment."""
    ...

def get_semantic_ids(
    responses: list[str],   # len = n_samples (5)
    nli_model,
) -> list[int]:             # len = n_samples; cluster id per response
    """Bidirectional NLI clustering, non-strict equivalence."""
    ...
```

### Tensor Shapes (Batch NLI)

| Variable | Shape | Note |
|----------|-------|------|
| pairs | list of (str, str) | all ordered pairs |
| nli_scores | [n_pairs, 3] | logits: contradiction/neutral/entailment |
| semantic_ids | (n_samples,) list[int] | cluster label per response |

### Pseudo-code

```python
# check_implication: single pair
def check_implication(text1, text2, nli_model) -> int:
    score = nli_model.predict([(text1, text2)])  # shape [1, 3]
    return int(np.argmax(score[0]))              # 0/1/2

# get_semantic_ids: bidirectional, non-strict
def get_semantic_ids(responses, nli_model) -> list[int]:
    n = len(responses)
    semantic_ids = list(range(n))   # initial: each own cluster
    for i in range(n):
        for j in range(i + 1, n):
            imp_ij = check_implication(responses[i], responses[j], nli_model)
            imp_ji = check_implication(responses[j], responses[i], nli_model)
            # non-strict: equivalent if no contradiction AND not both neutral
            no_contradiction = (imp_ij != 0) and (imp_ji != 0)
            not_both_neutral = not (imp_ij == 1 and imp_ji == 1)
            if no_contradiction and not_both_neutral:
                # merge: assign j's cluster to i's cluster id
                old_id = semantic_ids[j]
                new_id = semantic_ids[i]
                semantic_ids = [new_id if s == old_id else s for s in semantic_ids]
    # remap to contiguous 0..K-1
    unique = sorted(set(semantic_ids))
    remap = {v: k for k, v in enumerate(unique)}
    return [remap[s] for s in semantic_ids]
```

### Key Notes

- N=5 responses → 10 ordered pairs → 20 NLI calls per prompt. Batching across prompts in E3-2.
- The sequential merge (not union-find) is O(n²) but n=5 so irrelevant; matches jlko reference.
- `nli_model.predict()` accepts list of (str, str) tuples for batching.

### Subtasks [1/3 used for E3]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E3-1 | semantic_ids | Implement check_implication + get_semantic_ids |

---

## E3-2: `compute_se_n5()` [Complexity: 14, Budget: E3]

**Applied**: Per-prompt entropy over cluster distribution

### API Signatures

```python
def cluster_assignment_entropy(semantic_ids: list[int]) -> float:
    """SE = -sum(p_k * log(p_k)). Returns 0.0 for single cluster."""
    ...

def compute_se_n5(
    stochastic_responses: list[list[str]],  # shape (2500, 5)
    nli_model,
    batch_nli_size: int = 50,               # prompts per NLI batch
) -> np.ndarray:                            # shape (2500,)
    """Compute SE_N5 for all prompts. Asserts var > 0.01."""
    ...
```

### Pseudo-code

```python
def cluster_assignment_entropy(semantic_ids) -> float:
    counts = np.bincount(semantic_ids)
    probs = counts / counts.sum()
    return float(-np.sum(probs * np.log(probs + 1e-10)))

def compute_se_n5(stochastic_responses, nli_model, batch_nli_size=50) -> np.ndarray:
    se_scores = []
    for i in tqdm(range(len(stochastic_responses))):
        responses = stochastic_responses[i]   # list[str] len=5
        ids = get_semantic_ids(responses, nli_model)
        se_scores.append(cluster_assignment_entropy(ids))
    se = np.array(se_scores)                  # (2500,)
    assert np.var(se) > 0.01, f"SE degenerate: var={np.var(se):.4f}"
    return se
```

### Key Notes

- `batch_nli_size` parameter reserved for future batching across prompts; current impl is sequential per-prompt (simple, correct for 2500 prompts with N=5).
- `1e-10` epsilon prevents log(0) for degenerate single-cluster case.
- NLI call count: 2500 prompts × 10 directed pairs = 25,000 NLI calls total.

### Subtasks [2/3 used for E3]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E3-2 | se_n5 | Implement compute_se_n5 with entropy formula |

---

## E3-3: `compute_min_logprob()` [Complexity: 14, Budget: E3]

**Applied**: Direct index into ragged list[list[float]] from generate_greedy output

### API Signatures

```python
def compute_min_logprob(
    token_logprobs_per_prompt: list[list[float]],  # shape (2500, T_i) ragged
) -> np.ndarray:                                    # shape (2500,)
    """Min token log-prob per prompt. Asserts all values < 0."""
    ...
```

### Tensor Shape Trace (from HuggingFace generate)

```
out.scores           : tuple of T tensors, each (B, vocab_size)
torch.stack(scores)  : (T, B, vocab_size)
.log_softmax(-1)     : (T, B, vocab_size)
.gather(token_ids)   : (T, B, 1) → squeeze → (T, B)
.T                   : (B, T)
[j].tolist()         : list[float] len=T   ← stored as token_logprobs_per_prompt[i]

compute_min_logprob input: list of those lists, shape (2500, T_i)
```

### Pseudo-code

```python
def compute_min_logprob(token_logprobs_per_prompt) -> np.ndarray:
    min_lp = np.array([min(lp) for lp in token_logprobs_per_prompt])  # (2500,)
    assert np.all(min_lp < 0), \
        f"Expected all log-probs < 0; got {(min_lp >= 0).sum()} non-negative values"
    return min_lp
```

### Key Notes

- T_i varies per prompt (ragged); `min()` over Python list is correct.
- Log-probs from `log_softmax` are always ≤ 0; the assert catches upstream bugs (e.g., accidental raw logit passthrough).
- This function is intentionally trivial — the complexity lives in `generate_greedy`.

### Subtasks [3/3 used for E3]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E3-3 | min_logprob | Implement compute_min_logprob with assertion |

---

## E5-1: `run_conditional_lr()` [Complexity: 11, Budget: E5]

**Applied**: sklearn LogisticRegression + scipy log_loss for McFadden partial R²

### API Signatures

```python
def run_conditional_lr(
    se_scores: np.ndarray,          # (2500,)
    min_logprob_scores: np.ndarray, # (2500,)
    response_lengths: np.ndarray,   # (2500,) token counts
    correctness: np.ndarray,        # (2500,) dtype int {0, 1}
) -> dict:
    """Full vs reduced conditional LR. Returns stats dict."""
    ...
# Returns:
# {
#   "ll_full": float,        # log-likelihood full model (negated log_loss * N)
#   "ll_reduced": float,     # log-likelihood reduced model
#   "partial_r2_se": float,  # McFadden: 1 - ll_full / ll_reduced
#   "coefs_full": list[float],    # [β_min_lp, β_se, β_L, β_interaction]
#   "coefs_reduced": list[float], # [β_min_lp, β_L]
#   "lrt_chi2": float,
#   "lrt_p": float,
# }
```

### Pseudo-code

```python
def run_conditional_lr(se_scores, min_logprob_scores, response_lengths, correctness) -> dict:
    y = correctness                                # (2500,)
    interaction = se_scores * min_logprob_scores   # (2500,)
    # No standardization: LR coefficients interpretable on original scale
    X_full = np.column_stack([min_logprob_scores, se_scores,
                              response_lengths, interaction])    # (2500, 4)
    X_reduced = np.column_stack([min_logprob_scores,
                                 response_lengths])              # (2500, 2)

    lr_full = LogisticRegression(max_iter=1000, solver="lbfgs").fit(X_full, y)
    lr_red  = LogisticRegression(max_iter=1000, solver="lbfgs").fit(X_reduced, y)

    # log_loss returns mean negative log-likelihood; multiply by N for total
    N = len(y)
    ll_full    = -log_loss(y, lr_full.predict_proba(X_full)[:, 1],    normalize=False)
    ll_reduced = -log_loss(y, lr_red.predict_proba(X_reduced)[:, 1],  normalize=False)
    # McFadden partial R²: improvement of full over reduced
    partial_r2 = 1 - (ll_full / ll_reduced)

    # LRT: chi2 with df = n_extra_params = 2 (SE + interaction)
    lrt_stat = -2 * (ll_reduced - ll_full)        # chi2 statistic
    lrt_p    = scipy.stats.chi2.sf(lrt_stat, df=2)

    return {
        "ll_full": ll_full,
        "ll_reduced": ll_reduced,
        "partial_r2_se": partial_r2,
        "coefs_full": lr_full.coef_[0].tolist(),
        "coefs_reduced": lr_red.coef_[0].tolist(),
        "lrt_chi2": lrt_stat,
        "lrt_p": lrt_p,
    }
```

### Key Notes

- `log_loss(normalize=False)` returns sum of negative log-likelihoods, equivalent to `-ll`. Use `ll = -log_loss(...)` directly.
- McFadden partial R² compares full vs **reduced** (not null); valid because reduced is nested in full.
- LRT df=2: full adds SE + SE×min_logprob over reduced.
- No standardization: keeps coefficients on original scale for interpretability; LR convergence is fine with lbfgs at max_iter=1000.

### Subtasks [1/2 used for E5]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E5-1 | conditional_lr | Implement run_conditional_lr with McFadden R² and LRT |

---

## E5-2: `evaluate_gate()` [Complexity: 11, Budget: E5]

**Applied**: Decision tree gate → JSON result schema

### API Signatures

```python
def evaluate_gate(
    pearson_r: float,
    partial_r2: float,
    lrt_p: float,
) -> dict:
    """Gate decision tree. Returns result dict matching RESULTS_PATH schema."""
    ...
# Returns JSON-serializable dict (see schema below)
```

### Output JSON Schema

```json
{
  "gate_pass": true,
  "decision": "PASS",
  "pearson_r": -0.54,
  "abs_pearson_r": 0.54,
  "partial_r2_se": 0.043,
  "lrt_p": 0.001,
  "reason": "abs(r)=0.54 < 0.70 AND partial_r2=0.043 >= 0.02"
}
```

`"decision"` values: `"PASS"` | `"EXPLORE_N10"` | `"ABANDON"`

### Pseudo-code

```python
def evaluate_gate(pearson_r, partial_r2, lrt_p) -> dict:
    abs_r = abs(pearson_r)
    if abs_r > ABANDON_THRESHOLD:                                      # > 0.85
        decision = "ABANDON"
        gate_pass = False
        reason = f"abs(r)={abs_r:.3f} > {ABANDON_THRESHOLD} (SE is logprob reparameterization)"
    elif abs_r > PEARSON_R_THRESHOLD or partial_r2 < PARTIAL_R2_THRESHOLD:  # > 0.7 or < 0.02
        decision = "EXPLORE_N10"
        gate_pass = False
        reason = f"abs(r)={abs_r:.3f} or partial_r2={partial_r2:.4f} marginal — retry N=10"
    else:                                                              # abs_r < 0.7 AND r2 >= 0.02
        decision = "PASS"
        gate_pass = True
        reason = f"abs(r)={abs_r:.3f} < {PEARSON_R_THRESHOLD} AND partial_r2={partial_r2:.4f} >= {PARTIAL_R2_THRESHOLD}"

    result = {
        "gate_pass": gate_pass,
        "decision": decision,
        "pearson_r": pearson_r,
        "abs_pearson_r": abs_r,
        "partial_r2_se": partial_r2,
        "lrt_p": lrt_p,
        "reason": reason,
    }
    # save to RESULTS_PATH
    Path(RESULTS_PATH).parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "w") as f:
        json.dump(result, f, indent=2)
    return result
```

### Key Notes

- ABANDON check (>0.85) must be tested **before** EXPLORE check (>0.70) to avoid false EXPLORE.
- The function writes to `RESULTS_PATH` directly — caller (`run_all`) does not need to save again.
- `lrt_p` passed through for completeness in JSON; gate logic uses only `pearson_r` and `partial_r2`.

### Subtasks [2/2 used for E5]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E5-2 | gate_eval | Implement evaluate_gate with JSON output |

---

## Subtask Budget Summary

| Epic | Budget | Used | Subtasks |
|------|--------|------|----------|
| E2 | 3 | 3 | L-E2-1, L-E2-2, L-E2-3 |
| E3 | 3 | 3 | L-E3-1, L-E3-2, L-E3-3 |
| E5 | 2 | 2 | L-E5-1, L-E5-2 |
| **Total** | **8** | **8** | |
