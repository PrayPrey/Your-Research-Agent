# Logic: h-e1 — Semantic-Structural UQ Existence Verification

**Hypothesis**: h-e1 | **Type**: EXISTENCE (PoC) | **Date**: 2026-05-20

Applied: modular-inference-pipeline, bootstrap-CI-evaluation, checkpoint-resume-pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project - designing new APIs. No existing codebase to analyze.
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## E4: UQ Method Implementations [Complexity: 16, Budget: 4 subtasks]

### API Signatures

```python
# uq_methods.py

def compute_token_probability(result: GenerationResult) -> float:
    """Negative log-likelihood of greedy decode. Higher = more uncertain."""
    # result.greedy_log_likelihood: scalar (sum of token log-probs)
    # result.greedy_text: str (decoded tokens)
    # returns: float (uncertainty score; negated NLL so higher = more uncertain)
    ...

def compute_semantic_entropy(
    result: GenerationResult,
    nli_model: AutoModelForSequenceClassification,
    nli_tokenizer: AutoTokenizer,
    entailment_threshold: float = 0.5,
) -> Tuple[float, int]:
    """NLI-based semantic clustering + entropy. Returns (se_score, cluster_count K)."""
    # result.sampled_texts: List[str], len=N (e.g. N=10)
    # nli_model output logits: [3] (contradiction, neutral, entailment)
    # cluster_assignments: List[int], len=N  (0-indexed cluster id)
    # cluster_probs: [K]  (probability mass per cluster, sum=1)
    # se_score: float  (entropy in nats)
    # K: int  (number of distinct semantic clusters, K <= N)
    ...

def compute_kle(
    result: GenerationResult,
    nli_model: AutoModelForSequenceClassification,
    nli_tokenizer: AutoTokenizer,
) -> Optional[float]:
    """EigValLaplacian via lm-polygraph; returns None if unavailable."""
    # nli_matrix: [N, N] float (pairwise entailment scores)
    # laplacian eigenvalues: [N] float
    # kle_score: float (sum of positive eigenvalues)
    ...

def compute_selfcheck_bertscore(result: GenerationResult) -> float:
    """BERTScore consistency across N samples vs greedy decode."""
    # result.sampled_texts: List[str], len=N
    # result.greedy_text: str
    # bertscore_matrix: [N] float (F1 per sample vs greedy)
    # returns: float (1 - mean_F1; higher = more uncertain)
    ...

def compute_selfcheck_nli(
    result: GenerationResult,
    nli_model: AutoModelForSequenceClassification,
    nli_tokenizer: AutoTokenizer,
) -> float:
    """NLI-based consistency of samples vs greedy. Higher = more uncertain."""
    # contradiction_scores: [N] float
    # returns: float (mean contradiction probability)
    ...

def compute_seps(
    result: GenerationResult,
    probe_model: Optional[Any] = None,
) -> Optional[float]:
    """Linear probe on hidden states. Optional; returns None if probe_model is None."""
    # result.hidden_states_last: Optional[np.ndarray]  # [n_layers, seq_len, hidden_dim]
    # returns: Optional[float]
    ...

def compute_all_uq(
    results: List[GenerationResult],
    nli_model: AutoModelForSequenceClassification,
    nli_tokenizer: AutoTokenizer,
) -> Dict[str, np.ndarray]:
    """Orchestrate all UQ methods for a list of GenerationResults.

    Returns dict: method_name -> uncertainty scores array of shape [Q]
    where Q = number of queries (len(results)).
    Keys: 'token_prob', 'semantic_entropy', 'kle', 'selfcheck_bertscore',
          'selfcheck_nli', 'seps' (seps may be None-masked).
    Also returns cluster_counts separately via verify_se_mechanism.
    """
    ...

def verify_se_mechanism(
    cluster_counts: List[int],
    n_samples: int = 10,
) -> Tuple[bool, Dict[str, Any]]:
    """Check mean cluster count K < N. Returns (ok, stats_dict)."""
    # stats_dict keys: 'mean_k', 'min_k', 'max_k', 'degenerate_fraction'
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| sampled_texts | List[str], len=N | N=10 samples per query |
| nli_logits | [3] | contradiction / neutral / entailment per pair |
| nli_matrix | [N, N] | pairwise entailment scores (used by KLE) |
| cluster_probs | [K] | mass per semantic cluster, K <= N |
| laplacian_eigvals | [N] | eigenvalues for KLE |
| scores array | [Q] | per-query uncertainty score, Q = dataset size |
| hidden_states_last | [n_layers, seq_len, hidden_dim] | last token's hidden states |

### Pseudo-code: compute_semantic_entropy

```
Input: N sampled texts, NLI model
1. Build NxN entailment matrix:
   for i in range(N):
     for j in range(N): if i != j:
       logits = nli_model(texts[i], texts[j])  # [3]
       entail_prob[i,j] = softmax(logits)[2]   # entailment class
2. Assign clusters via bidirectional entailment:
   cluster_id = [-1] * N
   next_id = 0
   for i in range(N):
     if cluster_id[i] == -1:
       cluster_id[i] = next_id; next_id += 1
     for j in range(i+1, N):
       if entail_prob[i,j] > threshold AND entail_prob[j,i] > threshold:
         cluster_id[j] = cluster_id[i]  # same cluster
3. K = len(unique clusters)
4. cluster_probs[k] = count(cluster_id == k) / N  # [K]
5. se_score = -sum(p * log(p) for p in cluster_probs if p > 0)
6. return (se_score, K)
```

### Pseudo-code: compute_kle

```
Input: N sampled texts, NLI model
1. Try: from lm_polygraph.estimators import EigValLaplacian
   If ImportError: return None
2. Build NxN entailment matrix (same as SE step 1)
3. Construct graph Laplacian L = D - A where:
   A[i,j] = entail_prob[i,j] (adjacency)
   D[i,i] = sum_j A[i,j] (degree)
4. eigvals = np.linalg.eigvalsh(L)  # [N] ascending
5. kle_score = sum(max(0, ev) for ev in eigvals)
6. return kle_score
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E4-1 | compute_token_probability | Return negated NLL from greedy_log_likelihood |
| L-E4-2 | compute_semantic_entropy | NLI clustering algorithm + entropy computation |
| L-E4-3 | compute_kle | EigValLaplacian with lm-polygraph + ImportError fallback |
| L-E4-4 | compute_all_uq | Orchestration: loop results, collect all method scores into [Q] arrays |

---

## E3: Answer Generation with Checkpointing [Complexity: 12, Budget: 2 subtasks]

### API Signatures

```python
# generate.py

@dataclass
class GenerationResult:
    question_id: str
    prompt: str
    greedy_text: str
    greedy_log_likelihood: float         # scalar: sum of token log-probs (greedy)
    sampled_texts: List[str]             # len=N (default 10)
    sampled_log_likelihoods: List[float] # len=N, per-sequence NLL
    hidden_states_last: Optional[np.ndarray]  # [n_layers, seq_len, hidden_dim] or None

def generate_for_query(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    prompt: str,
    cfg: SamplingConfig,
    extract_hidden: bool = False,
) -> GenerationResult:
    """Generate greedy + N samples for a single prompt.

    Greedy: do_sample=False, return logits for NLL computation.
    Sampling: temperature=cfg.temperature, top_p=cfg.top_p, seed=cfg.seed.
    hidden_states_last: extracted when extract_hidden=True and output_hidden_states=True.
    """
    # input_ids: [1, prompt_len]
    # greedy output logits: [1, prompt_len + max_new_tokens, vocab_size]
    # sampled sequences: [N, prompt_len + max_new_tokens]  (one call per sample or batched)
    # hidden_states tuple: n_layers * [1, seq_len, hidden_dim] -> stacked to [n_layers, seq_len, hidden_dim]
    ...

def generate_dataset(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    dataset: Dataset,
    cfg: SamplingConfig,
    batch_size: int,
    checkpoint_path: str,
    checkpoint_every: int = 500,
) -> List[GenerationResult]:
    """Batched generation over full dataset with checkpoint resume.

    Resumes from checkpoint if checkpoint_path exists.
    Saves checkpoint every `checkpoint_every` completed queries.
    batch_size: 16 for 8B, 4-8 for 70B (per NFR3.2).
    """
    ...

def load_checkpoint(checkpoint_path: str) -> Optional[List[GenerationResult]]:
    """Load pickled checkpoint; returns None if not found."""
    ...

def save_checkpoint(results: List[GenerationResult], checkpoint_path: str) -> None:
    """Pickle results to checkpoint_path (atomic write via temp file)."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [1, prompt_len] | Tokenized prompt |
| greedy logits | [1, prompt_len + max_new_tokens, vocab_size] | For NLL computation |
| sampled sequences | [1, prompt_len + max_new_tokens] | One per sample call |
| hidden_states_last | [n_layers, seq_len, hidden_dim] | Stacked from tuple; seq_len = prompt_len + max_new_tokens |

### Pseudo-code: generate_for_query

```
1. input_ids = tokenizer(prompt)  # [1, P]
2. Greedy decode:
   out = model.generate(input_ids, do_sample=False, max_new_tokens=50,
                        return_dict_in_generate=True, output_scores=True,
                        output_hidden_states=extract_hidden)
   greedy_text = decode(out.sequences[0, P:])
   greedy_nll = -sum(log_softmax(scores[t])[token_t] for t in range(T))
3. Sampled decodes (N iterations, each with generator seeded):
   for i in range(N):
     set seed(cfg.seed + i)
     out_i = model.generate(input_ids, do_sample=True,
                            temperature=cfg.temperature, top_p=cfg.top_p,
                            max_new_tokens=50, return_dict_in_generate=True,
                            output_scores=True)
     sampled_texts[i] = decode(out_i.sequences[0, P:])
     sampled_nll[i] = -sum(log_softmax(scores[t])[token_t])
4. If extract_hidden:
   hs_tuple = out.hidden_states  # n_layers * [1, seq_len, H]
   hidden_states_last = stack(hs_tuple)  # [n_layers, seq_len, H]
5. return GenerationResult(...)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E3-1 | generate_for_query | Single-query greedy + N-sample generation with log-likelihood + optional hidden states |
| L-E3-2 | generate_dataset | Batched loop with checkpoint save/resume every 500 queries |

---

## E5: AUROC Evaluation, Bootstrap CI, Gate Check [Complexity: 11, Budget: 2 subtasks]

### API Signatures

```python
# evaluate.py

def compute_auroc(
    uncertainty_scores: np.ndarray,  # [Q] float
    correctness_labels: np.ndarray,  # [Q] int (0/1)
) -> float:
    """Compute AUROC via sklearn.metrics.roc_auc_score."""
    ...

def bootstrap_auroc_ci(
    uncertainty_scores: np.ndarray,  # [Q] float
    correctness_labels: np.ndarray,  # [Q] int (0/1)
    n_resamples: int = 1000,
    alpha: float = 0.05,
    seed: int = 42,
) -> Tuple[float, float, float]:
    """Bootstrap AUROC CI. Returns (mean_auroc, ci_low, ci_high).

    Percentile CI: ci_low = percentile(alpha/2), ci_high = percentile(1-alpha/2).
    """
    # bootstrap_aurocs: [n_resamples] float
    # ci excludes zero iff ci_low > 0 (for difference scores)
    ...

def run_gate_check(
    auroc_results: Dict[str, Any],
) -> Tuple[bool, Dict[str, bool]]:
    """Check all 4 MUST_WORK gate conditions.

    auroc_results structure:
      {model_key: {dataset_name: {method: {'auroc': float, 'ci_low': float, 'ci_high': float}}}}

    4 conditions checked:
      1. SE AUROC_8B_trivia > TP AUROC_8B_trivia AND CI of (SE-TP) excludes zero
      2. SE AUROC_70B_trivia > TP AUROC_70B_trivia AND CI of (SE-TP) excludes zero
      3. SE AUROC_8B_nq > TP AUROC_8B_nq AND CI of (SE-TP) excludes zero
      4. SE AUROC_70B_nq > TP AUROC_70B_nq AND CI of (SE-TP) excludes zero

    Returns:
      gate_pass: bool (True iff all 4 pass)
      condition_results: Dict[str, bool] with keys like '8b_trivia', '70b_trivia', etc.
    """
    ...

def save_results(
    auroc_results: Dict[str, Any],
    uq_scores: Dict[str, np.ndarray],
    correctness_labels: np.ndarray,
    dataset_name: str,
    model_key: str,
    output_dir: str,
) -> None:
    """Save auroc_results.json, uncertainty_scores_{model}_{dataset}.pkl,
    correctness_labels_{dataset}.pkl."""
    ...

def evaluate_all(
    uq_scores: Dict[str, np.ndarray],  # method -> [Q]
    correctness_labels: np.ndarray,    # [Q]
    cfg: ExperimentConfig,
    dataset_name: str,
    model_key: str,
) -> Dict[str, Any]:
    """Run bootstrap_auroc_ci for each method. Returns nested results dict."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| uncertainty_scores | [Q] | Q = dataset size (17944 TriviaQA, 3610 NQ) |
| correctness_labels | [Q] | Binary int (0/1) |
| bootstrap_aurocs | [n_resamples] | One AUROC per bootstrap resample |

### Pseudo-code: bootstrap_auroc_ci

```
1. rng = np.random.default_rng(seed)
2. bootstrap_aurocs = []
3. for _ in range(n_resamples):
     idx = rng.integers(0, Q, size=Q)  # resample with replacement
     auroc_i = roc_auc_score(correctness_labels[idx], uncertainty_scores[idx])
     bootstrap_aurocs.append(auroc_i)
4. bootstrap_aurocs = np.array(bootstrap_aurocs)  # [n_resamples]
5. ci_low  = np.percentile(bootstrap_aurocs, 100 * alpha/2)
6. ci_high = np.percentile(bootstrap_aurocs, 100 * (1 - alpha/2))
7. mean_auroc = np.mean(bootstrap_aurocs)
8. return (mean_auroc, ci_low, ci_high)
```

### Pseudo-code: run_gate_check (CI difference method)

```
For each (model_key, dataset_name) combination in [(8b, trivia), (70b, trivia), (8b, nq), (70b, nq)]:
  se_scores  = uq_scores[model_key][dataset_name]['semantic_entropy']  # [Q]
  tp_scores  = uq_scores[model_key][dataset_name]['token_prob']        # [Q]
  labels     = correctness_labels[dataset_name]                        # [Q]
  # Bootstrap difference CI
  diff_samples = []
  for _ in range(1000):
    idx = resample(Q)
    diff = auroc(se_scores[idx], labels[idx]) - auroc(tp_scores[idx], labels[idx])
    diff_samples.append(diff)
  ci_low = percentile(diff_samples, 2.5)
  condition_pass = (mean(diff_samples) > 0) AND (ci_low > 0)
gate_pass = all(condition_pass values)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E5-1 | bootstrap_auroc_ci | Percentile bootstrap over [Q] arrays; return (mean, ci_low, ci_high) |
| L-E5-2 | run_gate_check | 4-condition CI-difference gate check; return (bool, Dict[str, bool]) |

---

## External Dependencies (Base Hypothesis)

None — green-field project. No base hypothesis code to import.

---

*Generated by Logic Agent — Phase 3 step-04*
*Hypothesis: h-e1 | Type: EXISTENCE (PoC) | Total subtasks: 8/8*
