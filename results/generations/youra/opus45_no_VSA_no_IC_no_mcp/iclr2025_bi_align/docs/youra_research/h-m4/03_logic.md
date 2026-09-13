# Logic: H-M4 Differential Benchmark Profiles

**Hypothesis ID:** h-m4 | **Focus:** MC1 eval, preference eval, Cohen's d, profile shape

Applied: multi-model batch-evaluation pipeline pattern (load once, eval across benchmarks, aggregate + effect-size analysis)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual h-m3 code (Serena MCP unavailable in this run; `Read` tool used directly on source files per fallback rule)
**Analyzed Path**: `docs/youra_research/h-m3/code/model.py`, `docs/youra_research/h-m3/code/config.py`
**Relevant Symbols**: `load_tokenizer(cfg)`, `load_trained_policy(cfg, checkpoint_path)`, `get_sequence_logprobs(model, input_ids, attention_mask) -> Tensor`, `HM3Config`, `model_id(method, seed) -> str`

**Discrepancy found**: `HM3Config.output_root = "./h-m3_models"`, not `checkpoints/`. h-m4 `HM4Config.checkpoint_root` must point at actual save directory — verify at runtime, do not assume path from spec. No RLHF-specific loader in h-m3 code (`load_trained_policy` merges LoRA adapter via `PeftModel.from_pretrained` + `merge_and_unload`; assumes adapter-based checkpoint). If RLHF checkpoints were saved as full models (not LoRA adapters), `load_trained_policy` will fail — `model_loader.py` (owned by another task) must handle this; flagged here for A-2 owner.

---

## External Dependencies (Base Hypothesis)

```python
# From: h-m3/code/model.py (ACTUAL CODE)
def load_tokenizer(cfg) -> AutoTokenizer: ...
def load_trained_policy(cfg, checkpoint_path: str) -> AutoModelForCausalLM:
    """LoRA merge-and-unload. Returns eval-mode model."""

def get_sequence_logprobs(model, input_ids: Tensor, attention_mask: Tensor) -> Tensor:
    """Sum of token log-probs per sequence. input_ids: [B, T] -> [B]"""

# From: h-m3/code/config.py
def model_id(method: str, seed: int) -> str:
    """e.g. 'dpo_seed42'"""
```

**Verified from**: `docs/youra_research/h-m3/code/model.py`, `config.py` (actual implementation)

**Note**: h-m4's `eval_mc1.py` and `eval_preference.py` must call `get_sequence_logprobs` with pre-tokenized, padded `[1, T]` batches (batch_size=1 per choice/response since sequence lengths vary per choice) — reuse directly, no reimplementation needed for logprob summation.

---

## A-4: MC1 Evaluation [Complexity: 8, Budget: 8]

**Applied**: Standard PyTorch (log-softmax + gather scoring, no lm-eval-harness dependency to keep single-GPU sequential path simple)

### API Signatures

```python
def compute_sequence_logprob(model, tokenizer, prompt: str, choice: str, device: str) -> float:
    """Score log P(choice | prompt) using h-m3's get_sequence_logprobs on the answer span only."""
    ...

def evaluate_mc1(model, tokenizer, sample: dict, device: str) -> int:
    """sample: {'question': str, 'mc1_targets': {'choices': [str], 'labels': [int]}}
    Returns 1 if argmax(logprobs) == correct_idx else 0."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| full_input_ids | [1, T] | `prompt + choice` tokenized |
| answer_logprob | scalar | length-normalized NOT applied for MC1 (raw sum, per TruthfulQA convention) |

### Pseudo-code

```
1. for each choice in sample.mc1_targets.choices:
     text = f"Q: {question}\nA: {choice}"
     input_ids, attn_mask = tokenize(text)  # [1, T]
     prompt_len = len(tokenize(f"Q: {question}\nA:"))
     seq_logprob = get_sequence_logprobs(model, input_ids, attn_mask)  # [1] -> scalar
     # restrict to answer-token span: recompute using only choice token positions
     # (reuse get_sequence_logprobs on full seq; slice via prompt_len offset before summation
     #  OR call get_sequence_logprobs then subtract prompt-only logprob — simpler: mask attention
     #  to zero for prompt tokens before calling get_sequence_logprobs, since it sums masked positions)
     logprobs.append(answer_only_logprob)
2. predicted = argmax(logprobs)
3. correct_idx = sample.mc1_targets.labels.index(1)
4. return 1 if predicted == correct_idx else 0
```

**Implementation note**: `get_sequence_logprobs` sums over `attention_mask[:, 1:]`. To score only the answer span, build `attention_mask` with prompt-token positions zeroed (keep answer + trailing tokens = 1). This reuses h-m3's function without modification.

### Subtasks [3/3 used within A-4 budget of 8]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Answer-span masking | Build attention_mask that isolates choice tokens for logprob sum |
| L-4-2 | compute_sequence_logprob | Wraps h-m3 get_sequence_logprobs with masked call |
| L-4-3 | evaluate_mc1 | Argmax over choices, compare to correct_idx |

---

## A-5: Preference Evaluation [Complexity: 8, Budget: 8]

**Applied**: Standard PyTorch (length-normalized response logprob per experiment brief 6.2)

### API Signatures

```python
def parse_hh_conversation(conversation: str) -> tuple[str, str]:
    """Split HH-RLHF conversation on final '\\n\\nAssistant:' -> (prompt, response)."""
    ...

def compute_response_logprob(model, tokenizer, conversation: str, device: str, max_length: int) -> float:
    """Length-normalized sum log-prob of response tokens given prompt."""
    ...

def evaluate_preference(model, tokenizer, sample: dict, device: str) -> int:
    """sample: {'chosen': str, 'rejected': str} (raw HH-RLHF conversation strings)
    Returns 1 if chosen_logprob > rejected_logprob else 0."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [1, T] | `prompt + response`, truncated to `cfg.max_length` |
| response_tokens | [T - prompt_len] | slice used for length normalization |

### Pseudo-code

```
1. prompt, response = parse_hh_conversation(conversation)
2. input_ids, attn_mask = tokenize(prompt + response, truncation=max_length)  # [1, T]
3. prompt_len = len(tokenize(prompt))
4. build masked attention_mask: zero out prompt positions (same trick as A-4)
5. seq_logprob = get_sequence_logprobs(model, input_ids, masked_attn_mask)  # scalar
6. n_response_tokens = attn_mask.sum() - prompt_len  # post-truncation count
7. return seq_logprob / n_response_tokens  # length-normalized
```

### Subtasks [3/3 used within A-5 budget of 8]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | parse_hh_conversation | Split on last "Assistant:" turn marker |
| L-5-2 | compute_response_logprob | Masked call to get_sequence_logprobs + length norm |
| L-5-3 | evaluate_preference | Compare chosen vs rejected logprob |

---

## A-7: Differential Profile Analysis [Complexity: 7, Budget: 7]

**Applied**: scipy.stats.ttest_ind for independent-samples t-test; pooled-std Cohen's d (standard formula)

### API Signatures

```python
def compute_cohens_d(dpo_scores: np.ndarray, rlhf_scores: np.ndarray) -> float:
    """Pooled-std Cohen's d. dpo_scores, rlhf_scores: [N] binary arrays (concatenated across seeds)."""
    ...

def analyze_differential_profiles(dpo_results: list[dict], rlhf_results: list[dict], cfg: HM4Config) -> dict:
    """dpo_results/rlhf_results: list of 5 per-seed dicts, each {benchmark_name: {'scores': [int], 'accuracy': float, 'stderr': float}}.
    Returns per-benchmark effects + differential_profile bool per cfg.d_large_threshold/d_small_threshold."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| dpo_all / rlhf_all | [N] | scores concatenated across 5 seeds, per benchmark |

### Pseudo-code

```
1. for benchmark in ["truthfulqa", "hh_helpful", "hh_harmless"]:
     dpo_all = concat([m[benchmark]["scores"] for m in dpo_results])
     rlhf_all = concat([m[benchmark]["scores"] for m in rlhf_results])
     d = compute_cohens_d(dpo_all, rlhf_all)
     t_stat, p_value = ttest_ind(dpo_all, rlhf_all)
     effects[benchmark] = {dpo_mean, rlhf_mean, cohens_d: d, t_stat, p_value}
2. d_values = [abs(effects[b]["cohens_d"]) for b in benchmarks]
3. differential_profile = max(d_values) > cfg.d_large_threshold and min(d_values) < cfg.d_small_threshold
4. return {benchmark_effects: effects, differential_profile, max_d, min_d, hypothesis_supported: differential_profile}
```

### Subtasks [4/4 used within A-7 budget of 7]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | compute_cohens_d | Pooled-std effect size helper |
| L-7-2 | Per-benchmark loop | t-test + Cohen's d for all 3 benchmarks |
| L-7-3 | Differential criterion check | max(d)>0.3 AND min(d)<0.15 |
| L-7-4 | Result dict assembly | Match analysis.py return contract |

---

## A-8: Profile Shape + Correlation Analysis [Complexity: 6, Budget: 6]

**Applied**: numpy z-score normalization + Pearson correlation (np.corrcoef, scipy.stats.pearsonr)

### API Signatures

```python
def analyze_profile_shape(dpo_results: list[dict], rlhf_results: list[dict]) -> dict:
    """Mean accuracy per method per benchmark -> z-normalized profile vectors + correlation.
    Returns {dpo_profile, rlhf_profile, dpo_normalized, rlhf_normalized, profile_correlation, distinct_profiles}."""
    ...

def analyze_cross_benchmark_correlations(dpo_results: list[dict], rlhf_results: list[dict]) -> dict:
    """Pairwise (seed-level) correlation between benchmark accuracies, per method; compare across methods.
    Returns {dpo_correlations, rlhf_correlations, correlation_differences, distinct_correlation_patterns}."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| dpo_profile / rlhf_profile | [3] | mean accuracy per benchmark (truthfulqa, hh_helpful, hh_harmless) |
| dpo_b1, dpo_b2 | [5] | per-seed accuracy for one benchmark pair |

### Pseudo-code

```
# profile shape
1. benchmarks = ["truthfulqa", "hh_helpful", "hh_harmless"]
2. dpo_profile = [mean(m[b]["accuracy"] for m in dpo_results) for b in benchmarks]  # [3]
3. rlhf_profile = [mean(m[b]["accuracy"] for m in rlhf_results) for b in benchmarks]
4. dpo_norm = (dpo_profile - mean(dpo_profile)) / std(dpo_profile)
5. rlhf_norm = (rlhf_profile - mean(rlhf_profile)) / std(rlhf_profile)
6. profile_correlation = corrcoef(dpo_norm, rlhf_norm)[0,1]
7. distinct_profiles = profile_correlation < cfg.profile_corr_threshold

# cross-benchmark correlation (seed-level, N=5 pairs per benchmark-pair)
8. for (b1, b2) in [(tqa,helpful), (tqa,harmless), (helpful,harmless)]:
     dpo_corr, _ = pearsonr([m[b1]["accuracy"] for m in dpo_results], [m[b2]["accuracy"] for m in dpo_results])
     rlhf_corr, _ = pearsonr(same for rlhf_results)
     diff = dpo_corr - rlhf_corr
9. distinct_correlation_patterns = any(abs(diff) > 0.3 for diff in diffs)
```

**Caveat**: N=5 seeds per correlation is low power; `pearsonr` p-values will be wide — report `distinct_correlation_patterns` as descriptive signal only, not a hypothesis-test gate (matches PRD Secondary criteria, not Primary).

### Subtasks [3/3 used within A-8 budget of 6]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | analyze_profile_shape | z-norm profile vectors + correlation |
| L-8-2 | analyze_cross_benchmark_correlations | Pairwise seed-level correlation diffs |
| L-8-3 | run_full_analysis orchestration hook | Combine A-7/A-8 outputs, write cfg.analysis_path |

---

## Self-Validation

- [x] No ASCII diagrams
- [x] No KB search logs (Applied: lines only)
- [x] Docstrings <= 2 lines
- [x] Tensor shapes in comments/tables
- [x] Subtask counts within budget (A-4: 3, A-5: 3, A-7: 4, A-8: 3)
- [x] Codebase Analysis (Serena) section included
- [x] External Dependencies API section included (base hypothesis exists)
