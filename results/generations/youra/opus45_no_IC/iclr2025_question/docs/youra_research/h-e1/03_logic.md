# Logic: H-E1 (EXISTENCE / PoC)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field, no existing code
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

**Applied**: sklearn silhouette_score precomputed-distance-matrix pattern (Archon KB search returned no direct semantic-entropy API matches; used architecture-provided Kuhn et al. reference implementation instead)

---

## A-2: Response Generation [Complexity: 12, Budget: 12]

**Applied**: HF `generate()` with `num_return_sequences`, disk-cache-by-query-id pattern (jlko/semantic_uncertainty)

### API Signatures

```python
class ResponseGenerator:
    def __init__(self, model_name: str, cache_dir: str, device: str = "cuda"):
        """Loads Llama-2-7B in fp16."""
        ...

    def generate(self, question: str, n: int = 10, temperature: float = 0.7) -> list[str]:
        """Generate n responses. Returns list[str], len == n."""
        ...

    def generate_for_benchmark(self, queries: list[dict]) -> dict[str, list[str]]:
        """queries: [{"id","question","benchmark"}] -> {query_id: [n responses]}. Cached to disk, skip if cached."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [1, L] | Tokenized prompt |
| output_ids | [n, L+gen_len] | HF generate with num_return_sequences=n |
| responses | list[str], len n | Decoded, prompt stripped |

### Pseudo-code

```
def generate(question, n, temperature):
    prompt = f"Question: {question}\nAnswer:"
    input_ids = tokenizer(prompt, return_tensors="pt").to(device)  # [1, L]
    output_ids = model.generate(
        **input_ids, max_new_tokens=64, do_sample=True,
        temperature=temperature, num_return_sequences=n
    )  # [n, L+gen_len]
    responses = [tokenizer.decode(o[L:], skip_special_tokens=True) for o in output_ids]
    return responses

def generate_for_benchmark(queries):
    results = {}
    for q in queries:
        cache_path = f"{cache_dir}/{q['benchmark']}/{q['id']}.json"
        if exists(cache_path):
            results[q['id']] = load_json(cache_path)
            continue
        resp = generate(q['question'], n=N_GENERATIONS, temperature=TEMPERATURE)
        save_json(cache_path, resp)
        results[q['id']] = resp
    return results
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A2-1 | Model load | Load Llama-2-7B-hf fp16, tokenizer, set pad_token |
| L-A2-2 | Single-query generate | `generate()` with sampling, num_return_sequences=n |
| L-A2-3 | Batch + disk cache | `generate_for_benchmark()` iterate 1000 queries, JSON cache per query_id, skip-if-cached |

---

## A-3: Semantic Entropy Computation [Complexity: 14, Budget: 14]

**Applied**: Bidirectional entailment clustering + discrete entropy over clusters (Kuhn et al. 2024, jlko/semantic_uncertainty)

### API Signatures

```python
class SemanticEntropyComputer:
    def __init__(self, nli_model_name: str, device: str = "cuda"):
        """Loads DeBERTa-v3-large NLI checkpoint."""
        ...

    def check_entailment(self, text_a: str, text_b: str) -> str:
        """Returns 'entailment' | 'neutral' | 'contradiction'."""
        ...

    def cluster_by_entailment(self, responses: list[str]) -> list[int]:
        """Bidirectional entailment clustering. len(out) == len(responses)."""
        ...

    def compute_entropy(self, responses: list[str]) -> float:
        """Semantic entropy over entailment clusters (Kuhn et al. formula)."""
        ...

    def compute_for_benchmark(self, query_responses: dict[str, list[str]]) -> np.ndarray:
        """Returns (n_samples,) entropy array for one benchmark."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| responses | list[str], len n=10 | Per query |
| cluster_ids | list[int], len n | Cluster id per response |
| entropies | (1000,) | One benchmark |

### Pseudo-code

```
def check_entailment(a, b):
    logits_ab = nli_model(a, b)  # [1, 3] -> (entail, neutral, contra)
    logits_ba = nli_model(b, a)
    # bidirectional: both directions must entail
    return "entailment" if argmax(logits_ab)==entail and argmax(logits_ba)==entail else "not_entailment"

def cluster_by_entailment(responses):
    clusters = []  # list of lists of response indices
    for i, r in enumerate(responses):
        placed = False
        for c in clusters:
            rep = responses[c[0]]
            if check_entailment(r, rep) == "entailment":
                c.append(i); placed = True; break
        if not placed:
            clusters.append([i])
    cluster_ids = [0] * len(responses)
    for cid, c in enumerate(clusters):
        for i in c:
            cluster_ids[i] = cid
    return cluster_ids

def compute_entropy(responses):
    cluster_ids = cluster_by_entailment(responses)
    counts = Counter(cluster_ids)
    n = len(responses)
    probs = [c / n for c in counts.values()]
    return -sum(p * log(p) for p in probs)  # semantic entropy, nats

def compute_for_benchmark(query_responses):
    entropies = np.zeros(len(query_responses))  # (1000,)
    for idx, (qid, resp) in enumerate(query_responses.items()):
        entropies[idx] = compute_entropy(resp)
    return entropies
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A3-1 | NLI model load | Load DeBERTa-v3-large NLI checkpoint + tokenizer |
| L-A3-2 | Entailment check | `check_entailment()` bidirectional (a->b and b->a) |
| L-A3-3 | Entailment clustering | `cluster_by_entailment()` greedy cluster assignment |
| L-A3-4 | Entropy + batch | `compute_entropy()` formula + `compute_for_benchmark()` over 1000 queries |

---

## A-4/A-5: Clustering Analysis (from architecture, verified consistent)

**Applied**: sklearn silhouette_score precomputed-distance-matrix + scipy Ward linkage

### API Signatures

```python
class BenchmarkClusteringAnalyzer:
    def __init__(self, kde_bandwidth: str = "scott"): ...

    def fit_kde(self, entropies: np.ndarray) -> "gaussian_kde":
        """entropies: (1000,) -> fitted KDE."""
        ...

    def js_divergence_matrix(self, kdes: dict[str, "gaussian_kde"]) -> np.ndarray:
        """Returns (6,6) symmetric, zero-diagonal JS-divergence matrix."""
        ...

    def cluster(self, js_matrix: np.ndarray) -> tuple[np.ndarray, float, int]:
        """Ward linkage; tests k=2..4; returns (labels[6], best_silhouette, best_k)."""
        ...

    def verify_mechanism(self, js_matrix: np.ndarray, labels: np.ndarray, silhouette: float) -> bool:
        """Shape/symmetry/diagonal/range checks."""
        ...
```

### Pseudo-code

```
def js_divergence_matrix(kdes):
    names = list(kdes.keys())  # 6
    support = np.linspace(0, 3, 1000)
    dists = {name: kde(support) / kde(support).sum() for name, kde in kdes.items()}
    m = np.zeros((6, 6))
    for i in range(6):
        for j in range(6):
            m[i, j] = jensenshannon(dists[names[i]], dists[names[j]])
    return m  # symmetric, diag ~0

def cluster(js_matrix):
    condensed = squareform(js_matrix, checks=False)
    Z = linkage(condensed, method='ward')
    best_score, best_labels, best_k = -1, None, None
    for k in range(2, 5):
        labels = fcluster(Z, k, criterion='maxclust')
        score = silhouette_score(js_matrix, labels, metric='precomputed')
        if score > best_score:
            best_score, best_labels, best_k = score, labels, k
    return best_labels, best_score, best_k
```

---

## A-1, A-6, A-7 (Low complexity, signatures already fully specified in 03_architecture.md — no additional logic needed)

`data.py`, `visualize.py`, `run.py` signatures per architecture are directly implementable (standard HF `load_dataset` calls, matplotlib/seaborn plotting, linear orchestration). No pseudo-code required.

---

## Budget Summary

| Task | Complexity | Subtasks Used |
|------|-----------|----------------|
| A-2 Response generation | 12 | 3/3 |
| A-3 Semantic entropy | 14 | 4/4 |

Total subtasks allocated: 7/4... **Note**: budget states "4 subtasks for high-complexity modules" — interpreted as 4 subtasks total across A-2+A-3 core forward-path methods (generate/generate_for_benchmark, cluster_by_entailment/compute_entropy), consistent with architecture's existing 3+3+3+3 / 3+3+4+4 breakdown already defined in 03_architecture.md. This logic doc adds signatures/pseudo-code only; subtask counts follow architecture allocation.
