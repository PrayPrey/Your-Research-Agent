# Logic: h-e1 (EXISTENCE PoC)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design, Serena skipped
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-2: Response Generation [Complexity: 10, Budget: 10]

**Applied**: HF transformers `generate()` with `num_return_sequences` (standard sampling pattern)

### API Signatures

```python
class ResponseGenerator:
    def __init__(self, model_id: str = "meta-llama/Meta-Llama-3-8B-Instruct", seed: int = 42):
        """Load tokenizer + causal LM, set seed."""
        ...

    def generate_n(
        self, question: str, n: int = 10, temperature: float = 0.7, max_tokens: int = 256
    ) -> list[str]:
        """Sample n responses for a question. Returns n decoded strings (special tokens stripped)."""
        ...
```

### Pseudo-code

```
1. prompt = format_chat(question)                      # str
2. input_ids = tokenizer(prompt, return_tensors="pt")   # [1, L]
3. out = model.generate(input_ids, do_sample=True,
         num_return_sequences=n, temperature=temperature,
         max_new_tokens=max_tokens)                     # [n, L+T]
4. responses = tokenizer.batch_decode(out[:, L:], skip_special_tokens=True)  # list[str], len n
5. return responses
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | Model load | Load Llama-3-8B-Instruct + tokenizer, apply chat template |
| L-2-2 | Sampling | `generate_n` with `num_return_sequences=n`, temp/max_tokens passthrough |
| L-2-3 | Seeding | `torch.manual_seed(seed)` in `__init__` for reproducibility |

---

## A-3: Semantic Entropy Detector [Complexity: 13, Budget: 13]

**Applied**: lorenzkuhn/semantic_uncertainty — bidirectional NLI entailment clustering + discrete entropy

### API Signatures

```python
class SemanticEntropyDetector:
    def __init__(self, nli_model: str = "microsoft/deberta-v3-large-mnli"):
        """Load NLI sequence-classification model + tokenizer."""
        ...

    def _cluster_by_entailment(self, responses: list[str], threshold: float = 0.5) -> list[list[str]]:
        """Greedy clustering: two responses share a cluster iff bidirectionally entailed."""
        ...

    def compute_entropy(self, responses: list[str]) -> float:
        """Cluster responses, return Shannon entropy (nats) over cluster size distribution."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| nli_logits | [1, 3] | contradiction, neutral, entailment (deberta-mnli label order) |
| p_entail | scalar | softmax(nli_logits)[entailment_idx] |

### Pseudo-code

```
_cluster_by_entailment(responses, threshold):
  clusters = []
  for r in responses:
    placed = False
    for c in clusters:
      rep = c[0]
      p_fwd = nli_entail_prob(rep, r)   # P(rep entails r)
      p_bwd = nli_entail_prob(r, rep)   # P(r entails rep)
      if p_fwd > threshold and p_bwd > threshold:
        c.append(r); placed = True; break
    if not placed:
      clusters.append([r])
  return clusters

compute_entropy(responses):
  clusters = _cluster_by_entailment(responses)
  probs = [len(c) / len(responses) for c in clusters]
  return -sum(p * log(p) for p in probs)   # float, nats
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | NLI wrapper | `nli_entail_prob(premise, hypothesis) -> float` via forward pass, softmax |
| L-3-2 | Clustering | `_cluster_by_entailment` greedy bidirectional entailment grouping |
| L-3-3 | Entropy calc | `compute_entropy` cluster-size distribution -> Shannon entropy |
| L-3-4 | Edge cases | Single-cluster (entropy=0), single-response input handling |

---

## A-4: Self-Consistency Detector [Complexity: 8, Budget: 8]

**Applied**: potsawee/selfcheckgpt — pairwise BERTScore, exclude diagonal, mean F1

### API Signatures

```python
class SelfConsistencyDetector:
    def __init__(self, lang: str = "en"):
        """Configure bert_score scorer (roberta-large backbone via lang='en')."""
        ...

    def compute_consistency(self, responses: list[str]) -> float:
        """Mean pairwise BERTScore F1 (i != j) across all response pairs. Higher = more consistent."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| f1_matrix | [n, n] | pairwise BERTScore F1, diagonal excluded from mean |

### Pseudo-code

```
compute_consistency(responses):
  n = len(responses)
  pairs_a, pairs_b = all (i, j) with i != j
  _, _, F1 = bert_score.score(pairs_a, pairs_b, lang="en")  # [n*(n-1)]
  return F1.mean().item()
```

### Subtasks [3/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | Pair construction | Build all ordered (i,j) pairs excluding diagonal |
| L-4-2 | BERTScore call | Batch `bert_score.score(cands, refs, lang="en")` -> F1 tensor |
| L-4-3 | Aggregation | Mean F1 -> single float consistency score |

---

## Config Reference

Values pulled from `config.py` (SEED=42, N_SAMPLES=10, TEMPERATURE=0.7, MAX_TOKENS=256, GENERATOR_MODEL, NLI_MODEL) — no new constants introduced.
