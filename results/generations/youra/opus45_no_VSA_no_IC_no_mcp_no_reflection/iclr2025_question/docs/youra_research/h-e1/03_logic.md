# Logic: h-e1 (EXISTENCE PoC)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field experiment - no existing codebase, no base hypothesis
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-4: Semantic Entropy [Complexity: 10, Budget: 1 subtask]

**Applied**: Semantic entropy via NLI-based bidirectional entailment clustering (Kuhn et al. 2023)

### API Signatures

```python
class UQMethodsWrapper:
    def __init__(self, model, tokenizer, nli_model_id: str = NLI_MODEL_ID,
                 num_samples: int = 10, device: str = "cuda"):
        """Loads NLI model (DeBERTa-v3-large) for clustering."""
        ...

    def semantic_entropy(self, prompt: str, temperature: float = 0.7) -> float:
        """N-sample generate -> NLI cluster -> cluster-prob entropy. Returns scalar H."""
        ...

    def _cluster_by_entailment(self, samples: list[str]) -> list[int]:
        """Assigns each sample a cluster id via bidirectional NLI entailment."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| samples | list[str], len=N | N=10 sampled generations |
| nli_logits | [N*(N-1), 3] | entail/neutral/contradict per ordered pair |
| cluster_ids | [N] | int cluster assignment per sample |
| cluster_probs | [K] | K=num clusters, sums to 1.0 |
| H | scalar float | -sum(p_k * log(p_k)) |

### Pseudo-code

```
1. samples = generate_samples(model, tokenizer, prompt, n=N, temperature=T)  # list[str], len N
2. clusters = []  # list of lists, semantic equivalence classes
3. for s in samples:
     placed = False
     for c in clusters:
         rep = c[0]
         # bidirectional check: entails(rep->s) AND entails(s->rep)
         if nli_entails(rep, s) and nli_entails(s, rep):
             c.append(s); placed = True; break
     if not placed:
         clusters.append([s])
4. cluster_probs = [len(c) / N for c in clusters]  # [K]
5. H = -sum(p * log(p) for p in cluster_probs)
6. return H
```

```python
def nli_entails(premise: str, hypothesis: str) -> bool:
    """DeBERTa NLI forward: logits [3] (contradict, neutral, entail); True if argmax == entail."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A4-1 | Semantic entropy algorithm | NLI bidirectional entailment clustering + cluster-distribution entropy (pseudo-code above) |

---

## A-1: Data Loading [Complexity: 6]

**Applied**: HF `datasets.load_dataset` standard loader

```python
def load_truthfulqa_mc1(cache_dir: str = ".cache") -> list[dict]:
    """Loads TruthfulQA mc1, returns parsed records."""
    ...
# returns [{"question": str, "choices": list[str], "correct_idx": int, "category": str}]
```

---

## A-2: Model Loading [Complexity: 8]

**Applied**: Standard HF `AutoModelForCausalLM` bf16 + device_map="auto"

```python
def load_model_and_tokenizer(model_id: str) -> tuple:  # (model, tokenizer)
    ...

def generate_greedy(model, tokenizer, prompt: str) -> tuple[str, "Tensor"]:
    """text, logits: [vocab_size] at final generated position"""
    ...

def generate_samples(model, tokenizer, prompt: str, n: int, temperature: float) -> list[str]:
    ...
```

---

## A-3: Token Entropy + P(True) [Complexity: 7]

**Applied**: Standard softmax entropy; Yes/No token-probability scoring

```python
def token_entropy(self, logits: "Tensor") -> float:
    """logits: [vocab_size] -> H = -sum(softmax(logits) * log_softmax(logits))"""
    ...

def p_true(self, question: str, response: str) -> float:
    """Prompts 'Is the above answer correct? (Yes/No)', returns P(Yes token)."""
    ...
```

### Pseudo-code (P(True))

```
1. prompt = f"{question}\nAnswer: {response}\nIs the above answer correct? (Yes/No)"
2. logits = model.forward(prompt)[-1]  # [vocab_size]
3. p_yes = softmax(logits)[yes_token_id]
4. return 1 - p_yes  # uncertainty score
```

---

## A-5: SelfCheckGPT [Complexity: 8]

**Applied**: `selfcheckgpt` package SelfCheckNLI

```python
def selfcheck_nli(self, response: str, sampled_responses: list[str]) -> float:
    """selfcheckgpt.SelfCheckNLI.predict(response, sampled_responses) -> mean inconsistency in [0,1]"""
    ...
```

---

## A-6: Evaluation Pipeline [Complexity: 6]

**Applied**: sklearn `roc_auc_score` / `average_precision_score`

```python
def compute_metrics(y_true: list[int], scores: dict[str, list[float]]) -> dict:
    ...
# returns {method: {"auroc": float, "auprc": float}}

def apply_gate(metrics: dict, threshold: float = 0.55) -> bool:
    """True if max(auroc) > threshold else STOP."""
    ...
```

---

## A-7: Visualization + Logging [Complexity: 6]

**Applied**: matplotlib standard ROC/histogram plots

```python
def plot_gate_comparison(metrics: dict, threshold: float, out_path: str) -> None: ...
def plot_roc_curves(y_true: list[int], scores: dict, out_path: str) -> None: ...
def plot_score_distributions(y_true: list[int], scores: dict, out_dir: str) -> None: ...
```

---

## A-8: End-to-End Integration [Complexity: 8]

**Applied**: Sequential pipeline orchestration

```python
def main() -> None:
    """load_truthfulqa_mc1 -> load_model_and_tokenizer -> per-question score_all_methods
    -> compute_metrics -> apply_gate -> visualize -> write results/scores.csv, metrics.json"""
    ...
```
