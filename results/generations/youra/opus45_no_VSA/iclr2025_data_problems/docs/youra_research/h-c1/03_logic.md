# Logic Design: H-C1 (PoC)

**Hypothesis:** IFR(contaminated) > IFR(non-contaminated), p<0.05; ρ(IFR, redundancy) < -0.5

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** No base_hypothesis/code/ or src/ found for H-C1 — new API design (Serena skipped per Scenario 3)
**Analyzed Path:** N/A
**Relevant Symbols:** None - new implementation

**Applied:** Standard PyTorch/sklearn/scipy (no KB pattern match beyond generic tensor dtype docs)

---

## A-1: Embedding Extraction [Complexity: Low]

### API Signatures

```python
def extract_embeddings(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    texts: List[str],
    batch_size: int = 32,
    max_length: int = 512,
) -> np.ndarray:
    """Mean-pool last hidden state per batch. texts -> [N, 2048]"""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| inputs.input_ids | [B, L] | B=batch_size, L<=max_length |
| last_hidden | [B, L, 2048] | Pythia-1B hidden dim |
| attention_mask | [B, L, 1] | unsqueezed for broadcast |
| pooled | [B, 2048] | mean over valid tokens |
| embeddings (out) | [N, 2048] | N=10000, concatenated batches |

### Pseudo-code

```
1. for batch in chunks(texts, batch_size):
2.     inputs = tokenizer(batch, pad=True, truncate=True, max_length)
3.     hidden = model(**inputs, output_hidden_states=True).hidden_states[-1]  # [B,L,2048]
4.     mask = inputs.attention_mask.unsqueeze(-1)  # [B,L,1]
5.     pooled = (hidden * mask).sum(1) / mask.sum(1)  # [B,2048]
6.     embeddings.append(pooled)
7. return concat(embeddings, axis=0)  # [N,2048]
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | extract_embeddings | Batched forward pass + mean pooling |

---

## A-2: IFRComputer [Complexity: Medium]

### API Signatures

```python
class IFRComputer:
    def __init__(self, embeddings: np.ndarray, trak_scores: np.ndarray, k: int = 50):
        """embeddings: [N,2048], trak_scores: [N]"""
        ...

    def compute_redundancy(self) -> np.ndarray:
        """1 - mean(cosine dist to k-NN). -> [N]"""
        ...

    def compute_ifr(self, redundancy: np.ndarray) -> np.ndarray:
        """|trak_score| / max(1-redundancy, 0.01). -> [N]"""
        ...

    def compute_correlation(self, ifr: np.ndarray, redundancy: np.ndarray) -> Tuple[float, float]:
        """Spearman(ifr, redundancy) -> (rho, pvalue)"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| embeddings | [10000, 2048] | k-NN fit input |
| distances | [10000, 51] | k+1 (incl. self at idx 0) |
| redundancy | [10000] | float in [0,1] |
| ifr | [10000] | float >= 0 |

### Pseudo-code

```
compute_redundancy:
1. distances, _ = NearestNeighbors(k+1, metric='cosine').fit(emb).kneighbors(emb)
2. redundancy = 1 - mean(distances[:, 1:], axis=1)  # skip self-neighbor
3. return redundancy  # [N]

compute_ifr:
1. replaceability = clip(1 - redundancy, min=0.01)
2. return abs(trak_scores) / replaceability  # [N]
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | IFRComputer | k-NN redundancy + IFR ratio + Spearman correlation |

---

## A-3: Statistics Pipeline [Complexity: Low]

### API Signatures

```python
def compute_ifr_statistics(
    embeddings: np.ndarray,
    trak_scores: np.ndarray,
    contaminated_mask: np.ndarray,
    k: int = 50,
) -> Dict[str, float]:
    """Full pipeline: redundancy -> ifr -> Mann-Whitney U + Spearman. All inputs [N]."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| contaminated_mask | [10000] | bool |
| ifr_contaminated | [~5000] | ifr[mask] |
| ifr_non_contaminated | [~5000] | ifr[~mask] |

### Pseudo-code

```
1. computer = IFRComputer(embeddings, trak_scores, k)
2. redundancy = computer.compute_redundancy()          # [N]
3. ifr = computer.compute_ifr(redundancy)               # [N]
4. ifr_c = ifr[contaminated_mask]; ifr_nc = ifr[~contaminated_mask]
5. stat, pval = mannwhitneyu(ifr_c, ifr_nc, alternative='greater')
6. rho, rho_pval = spearmanr(ifr, redundancy)
7. gate_1 = pval < 0.05 and mean(ifr_c) > mean(ifr_nc)
8. gate_2 = rho < -0.5
9. return {ifr_contaminated_mean, ifr_non_contaminated_mean, ifr_diff_pvalue,
           ifr_redundancy_correlation: rho, correlation_pvalue: rho_pval,
           gate_1_satisfied, gate_2_satisfied}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | compute_ifr_statistics | Orchestrates IFRComputer + Mann-Whitney U + Spearman |
| L-3-2 | validate_gate_conditions | Maps results dict -> gate_1/gate_2/overall pass booleans |

---

## Data Loading (top-level script glue)

```python
trak_scores = np.load("h-m2/trak_attribution_scores.npy")     # [~1e6]
top_1pct_idx = np.argsort(np.abs(trak_scores))[-int(len(trak_scores)*0.01):]  # [10000]
ccr_scores = np.load("h-m1/ccr_scores.npy")                    # [~1e6]
contaminated_mask = ccr_scores[top_1pct_idx] > np.median(ccr_scores)  # [10000] bool
model = AutoModelForCausalLM.from_pretrained("h-m2/checkpoint-final")
```

## Figures (required)

- Box plot: IFR by contamination status, p-value annotated (mandatory)
- Scatter: IFR vs redundancy with regression line, ρ annotated
- Distribution plots: redundancy and TRAK score by contamination status

Skipped: ablation variants, multiple IFR definitions — PoC uses single definition from experiment brief only.
