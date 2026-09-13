# Logic Spec: H-M1 (Semantic Entropy / Error Correlation)

**Type:** MECHANISM | **Tier:** FULL

Applied: Farquhar 2024 semantic-entropy pipeline (generate → cluster → entropy → gate)
Applied: HuggingFace transformers generate() with output_scores for token logprobs
Applied: scipy.stats Mann-Whitney U + Cohen's d gate pattern

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze; designing new APIs
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Data Pipeline [Complexity: 8, Budget: 8]

**Applied**: Standard HF `datasets` loading

### API Signatures

```python
# data/loader.py
def load_triviaqa(seed: int = 42, n: int = 1000) -> list[dict]:
    """Returns [{"question": str, "answer": str, "aliases": list[str]}]"""
    ...

def normalize_answer(text: str) -> str:
    """Lowercase, strip punctuation/articles."""
    ...

def filter_single_answer(dataset) -> "Dataset":
    """Keep rows with exactly one canonical answer."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | HF load | `load_dataset("trivia_qa","rc",split="validation")`, shuffle(seed=42), select(1000) |
| L-1-2 | Extract fields | question, answer.value, answer.aliases |
| L-1-3 | Normalize | lowercase, strip punctuation via `re` |
| L-1-4 | Filter | drop multi-answer / empty rows |

---

## A-2: Response Generation [Complexity: 14, Budget: 14]

**Applied**: HF `generate()` with `return_dict_in_generate=True, output_scores=True` for token logprobs

### API Signatures

```python
# generation/generate.py
class ResponseGenerator:
    def __init__(self, model_id: str = "meta-llama/Llama-2-7b-chat-hf",
                 temperature: float = 0.7, max_new_tokens: int = 50,
                 device: str = "cuda", dtype: "torch.dtype" = None):
        """Loads model+tokenizer in fp16."""
        ...

    def generate_n(self, question: str, n: int = 10) -> list[dict]:
        """
        Sample n responses for one question.
        Returns: [{"text": str, "logprob": float, "token_logprobs": list[float]}]
        logprob = mean(token_logprobs)  # length-normalized, per Farquhar 2024
        """
        ...

    def generate_batch(self, questions: list[str], n: int = 10) -> list[list[dict]]:
        """Per-question loop calling generate_n; returns list of len(questions)."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [1, L_prompt] | tokenized prompt |
| generate() output.sequences | [n, L_prompt + T] | T ≤ max_new_tokens |
| output.scores | tuple(T) of [n, V] | per-step logits, V=vocab size |
| token_logprobs | [T_i] per sample | log_softmax(scores)[t, token_id] |

### Pseudo-code

```
1. prompt = format_chat(question)  # Llama-2-chat template
2. tokenize -> input_ids [1, L]
3. out = model.generate(input_ids.repeat(n,1), do_sample=True,
                         temperature=temperature, max_new_tokens=50,
                         return_dict_in_generate=True, output_scores=True)
4. for each sample i in range(n):
     token_lp = [log_softmax(out.scores[t][i])[out.sequences[i, L+t]] for t in range(T_i)]
     logprob_i = mean(token_lp)   # length-normalized
     text_i = tokenizer.decode(out.sequences[i, L:], skip_special_tokens=True)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | Model load | AutoModelForCausalLM fp16, device_map="auto" |
| L-2-2 | Prompt formatting | Llama-2-chat template wrapper |
| L-2-3 | Sampling + logprob capture | generate() with output_scores, length-norm mean |
| L-2-4 | Batch loop over questions | iterate 1000 questions, persist raw responses to disk |

---

## A-3: Entailment Clustering [Complexity: 15, Budget: 15]

**Applied**: DeBERTa-v3-large-mnli sequence classification, greedy bidirectional clustering

### API Signatures

```python
# entropy/clustering.py
class EntailmentClusterer:
    def __init__(self, model_id: str = "microsoft/deberta-v3-large-mnli",
                 threshold: float = 0.5, device: str = "cuda"):
        ...

    def check_entailment(self, premise: str, hypothesis: str, question: str) -> float:
        """
        Question prepended to both sides: f"{question} {premise}" / f"{question} {hypothesis}"
        Returns P(entailment) from softmax over [contradiction, neutral, entailment].
        """
        ...

    def check_entailment_batch(self, pairs: list[tuple[str, str]], question: str) -> "np.ndarray":
        """Batched NLI forward pass. Returns [P] shape [len(pairs)]."""
        ...

    def cluster(self, responses: list[str], question: str) -> list[list[int]]:
        """Greedy bidirectional entailment clustering. Returns list of index-clusters."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| nli_input | [B, L] | tokenized (premise, hypothesis) pairs, B=batch of pairs |
| logits | [B, 3] | [contradiction, neutral, entailment] |
| probs | [B] | softmax(logits)[:, entailment_idx] |

### Pseudo-code

```
cluster(responses, question):
  clusters = []
  for i, resp in enumerate(responses):
    assigned = False
    for cluster in clusters:
      rep = responses[cluster[0]]
      p_ab = check_entailment(resp, rep, question)
      p_ba = check_entailment(rep, resp, question)
      if p_ab > threshold and p_ba > threshold:
        cluster.append(i)
        assigned = True
        break
    if not assigned:
      clusters.append([i])
  return clusters
```

Batching note: for N=10 responses, precompute all ≤ N*(N-1) directed pairs in one
batched forward pass (`check_entailment_batch`), then run greedy assignment using
the cached probability matrix — avoids N^2 sequential model calls.

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | NLI model load | DeBERTa-v3-large-mnli, fp16 |
| L-3-2 | Question-prepended pair formatting | build (premise, hypothesis) strings |
| L-3-3 | Batched entailment probability matrix | precompute pairwise probs, [N,N] cache |
| L-3-4 | Greedy clustering using cached matrix | assign responses to clusters |

---

## A-4: Semantic Entropy Computation [Complexity: 9, Budget: 9]

**Applied**: scipy.stats.entropy (Shannon entropy in nats)

### API Signatures

```python
# entropy/semantic_entropy.py
def compute_cluster_probs(clusters: list[list[int]], logprobs: list[float]) -> "np.ndarray":
    """cluster_prob[c] = sum(exp(logprobs[i]) for i in cluster), normalized to sum=1."""
    ...

def compute_semantic_entropy(responses: list[str], logprobs: list[float],
                              clusterer: "EntailmentClusterer", question: str) -> float:
    """Full pipeline: cluster -> aggregate probs -> Shannon entropy (nats)."""
    ...
```

### Pseudo-code

```
compute_semantic_entropy(responses, logprobs, clusterer, question):
  clusters = clusterer.cluster(responses, question)
  probs = compute_cluster_probs(clusters, logprobs)   # [K], sums to 1
  return scipy.stats.entropy(probs)   # base=e -> nats
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | Cluster prob aggregation | sum exp(logprob) per cluster, normalize |
| L-4-2 | Shannon entropy | scipy.stats.entropy, nats |
| L-4-3 | Per-question orchestration | loop over 1000 questions, save entropy_values.npy |

---

## A-5: Correctness Labeling [Complexity: 6, Budget: 6]

**Applied**: Standard EM/F1 QA scoring

### API Signatures

```python
# eval/correctness.py
def token_f1(pred: str, gold: str) -> float:
    """Token-overlap F1 after normalize_answer()."""
    ...

def is_correct(response: str, gold_aliases: list[str], f1_threshold: float = 0.5) -> bool:
    """True if exact match OR max F1 over aliases > f1_threshold."""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | token_f1 + exact match | bag-of-words F1 vs normalized gold |
| L-5-2 | Per-response labeling loop | label all 10 responses/question |

---

## A-6: Statistical Evaluation [Complexity: 8, Budget: 8]

**Applied**: scipy.stats.mannwhitneyu (one-sided) + Cohen's d + sklearn roc_auc_score

### API Signatures

```python
# eval/statistics.py
def cohens_d(correct: "np.ndarray", incorrect: "np.ndarray") -> float:
    """Pooled-std effect size: (mean(incorrect)-mean(correct))/pooled_std."""
    ...

def mann_whitney_test(correct: "np.ndarray", incorrect: "np.ndarray") -> tuple[float, float]:
    """One-sided (incorrect > correct). Returns (statistic, p_value)."""
    ...

def compute_auroc(entropies: "np.ndarray", labels: "np.ndarray") -> float:
    """labels: 1=incorrect, 0=correct. Higher entropy -> predict incorrect."""
    ...

def evaluate_gate(entropy_correct: "np.ndarray", entropy_incorrect: "np.ndarray") -> dict:
    """Returns {p_value, cohens_d, auroc, mean_entropy_correct,
                mean_entropy_incorrect, gate_passed: bool}"""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | cohens_d | pooled std, ddof=1 |
| L-6-2 | mann_whitney_test | alternative='greater' |
| L-6-3 | compute_auroc | sklearn roc_auc_score |
| L-6-4 | evaluate_gate | combine, check p<0.05 and d>0.3 |

---

## A-7: Visualization Suite [Complexity: 7, Budget: 7]

**Applied**: matplotlib bar/violin, sklearn roc_curve

### API Signatures

```python
# eval/visualize.py
def plot_gate_bar_chart(results: dict, out_path: str) -> None:
    """REQUIRED. Bar chart: mean entropy correct vs incorrect, error bars (std),
    annotate p-value and Cohen's d."""
    ...

def plot_entropy_violin(entropy_correct: "np.ndarray", entropy_incorrect: "np.ndarray",
                         out_path: str) -> None:
    ...

def plot_roc_curve(entropies: "np.ndarray", labels: "np.ndarray", out_path: str) -> None:
    ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | Bar chart (required) | seaborn/matplotlib, error bars + stat annotations |
| L-7-2 | Violin plot | seaborn violinplot correct vs incorrect |
| L-7-3 | ROC curve | sklearn.metrics.roc_curve + matplotlib |

---

## A-8: Pipeline Orchestration [Complexity: 10, Budget: 10]

**Applied**: Standard sequential pipeline script

### API Signatures

```python
# run_experiment.py
def main() -> None:
    """
    1. data = load_triviaqa()
    2. for q in data: responses = generator.generate_n(q["question"], n=10)
    3. entropy = compute_semantic_entropy(responses, logprobs, clusterer, question)
    4. labels = [is_correct(r, q["aliases"]) for r in responses]
    5. entropy_correct/incorrect split by any-correct-in-sample-set label
    6. results = evaluate_gate(entropy_correct, entropy_incorrect)
    7. save figures + results.json
    """
    ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-8-1 | End-to-end loop | wire A-1..A-6 modules sequentially, checkpoint every 100 Q |
| L-8-2 | Result persistence | save entropy_values.npy, labels.npy, results.json |
| L-8-3 | Figure generation calls | invoke A-7 functions, save to h-m1/figures/ |

---

## A-9: Ablation Studies [Complexity: 12, Budget: 12]

**Applied**: Parameter sweep reusing A-2/A-3 modules (no new classes)

### API Signatures

```python
# ablations/run_ablations.py
def run_temperature_ablation(temps: list[float] = [0.5, 0.7, 1.0]) -> dict:
    """Re-run generation+entropy+gate per temp. Returns {temp: gate_result}."""
    ...

def run_sample_count_ablation(ns: list[int] = [5, 10, 15]) -> dict:
    """Re-run with varying N generations/question. Returns {n: gate_result}."""
    ...

def run_threshold_ablation(thresholds: list[float] = [0.3, 0.5, 0.7]) -> dict:
    """Re-run clustering+entropy at varying entailment thresholds. Returns {threshold: gate_result}."""
    ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-9-1 | Temperature sweep (A1) | reuse ResponseGenerator with varying temperature |
| L-9-2 | Sample count sweep (A2) | reuse generate_n with varying n |
| L-9-3 | Threshold sweep (A3) | reuse EntailmentClusterer with varying threshold |

(No 4th subtask needed — sweeps share a common `_run_pipeline_variant()` helper; budget left unused is acceptable.)

---

## Self-Validation

- [x] No ASCII diagrams
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes in comments/tables for non-obvious cases only
- [x] Subtask counts within budget
- [x] Green-field noted in Codebase Analysis
