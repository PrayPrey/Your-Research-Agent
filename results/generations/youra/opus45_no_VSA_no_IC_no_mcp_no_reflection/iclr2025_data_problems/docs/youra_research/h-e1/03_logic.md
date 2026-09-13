# Logic: h-e1 (E5-large Embedding Similarity — EXISTENCE PoC)

**Applied**: sentence-embedding-similarity-pipeline (encode → normalize → cosine-sim → aggregate)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze (no `src/`, no base hypothesis folder)
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-2: E5-large Embedding Pipeline [Complexity: 9, Budget: 1]

**Applied**: sentence-embedding-similarity-pipeline (Archon KB)

### API Signatures

```python
# code/model.py
from torch import Tensor
from sentence_transformers import SentenceTransformer

def load_embedder(model_name: str = MODEL_NAME) -> SentenceTransformer:
    """Load E5-large-v2 via sentence-transformers."""
    ...

def embed_domains(model: SentenceTransformer, texts: list[str], batch_size: int) -> Tensor:
    """Prefix 'passage: ', encode, L2-normalize. texts: N_d -> [N_d, 1024]"""
    ...

def embed_tasks(model: SentenceTransformer, texts: list[str], batch_size: int) -> Tensor:
    """Prefix 'query: ', encode, L2-normalize. texts: N_t -> [N_t, 1024]"""
    ...

def compute_domain_scores(domain_emb: Tensor, task_emb: Tensor, domain_labels: list[str]) -> dict[str, float]:
    """Cosine-sim matrix -> mean per domain sample -> per-domain mean score."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| domain_emb | [N_d, 1024] | N_d = 8 domains × 1000 samples = 8000 |
| task_emb | [N_t, 1024] | N_t = MMLU validation (~1500) |
| sim_matrix | [N_d, N_t] | cosine similarity, both inputs pre-normalized -> dot product |
| domain_scores | dict[str, float] | 8 keys (one per domain), mean sim over that domain's rows |

### Pseudo-code

```
1. model = load_embedder()
2. domain_emb = normalize(model.encode(["passage: " + t for t in domain_texts]))  # [N_d, 1024]
3. task_emb = normalize(model.encode(["query: " + t for t in task_texts]))        # [N_t, 1024]
4. sim_matrix = domain_emb @ task_emb.T          # [N_d, N_t], cosine sim (unit vectors)
5. per_sample_mean = sim_matrix.mean(dim=1)      # [N_d]
6. for domain in DOMAINS:
       domain_scores[domain] = per_sample_mean[labels == domain].mean()
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A2-1 | Embed + score | Implement embed_domains/embed_tasks/compute_domain_scores per signatures above (batch_size=32, model_name=e5-large-v2) |
