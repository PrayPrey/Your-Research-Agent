# Logic: h-e1 (EXISTENCE PoC)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-3: SemanticEntropyBaseline [Complexity: 13, Budget: 3]

**Applied**: linear-probe-on-frozen-hidden-states pattern (OATML/semantic-entropy-probes); Archon KB had no directly relevant SE clustering results (top hits: QLoRA paper, bitsandbytes — unrelated), used reference methodology from PRD instead.

### API Signatures

```python
class SemanticEntropyBaseline:
    def __init__(self, nli_model_id: str):
        """Load DeBERTa-v3-large-mnli for entailment scoring."""

    def cluster_responses(self, responses: list[str]) -> list[int]:
        """Bidirectional NLI entailment clustering. len(responses)=N -> len(cluster_ids)=N."""

    def compute_entropy(self, cluster_ids: list[int]) -> float:
        """H = -sum p(c) log p(c) over cluster distribution."""

    def compute_se_scores(self, model: "ModelWrapper", questions: list[str]) -> list[float]:
        """generate(N_SAMPLES) -> cluster_responses -> compute_entropy, per question."""

    def binarize(self, se_scores: list[float]) -> list[int]:
        """1 if score > median(se_scores) else 0."""
```

### Pseudo-code

```
cluster_responses(responses):                      # N strings
  clusters = []                                     # list[list[int]] of response indices
  for i, r_i in enumerate(responses):
    assigned = False
    for cluster in clusters:
      j = cluster[0]
      # bidirectional entailment check via NLI model
      p_ij = nli_model.predict(premise=responses[j], hypothesis=r_i)  # [3] logits (entail/neutral/contra)
      p_ji = nli_model.predict(premise=r_i, hypothesis=responses[j])  # [3]
      if argmax(p_ij) == ENTAIL and argmax(p_ji) == ENTAIL:
        cluster.append(i); assigned = True; break
    if not assigned:
      clusters.append([i])
  cluster_ids = [0]*N
  for cid, cluster in enumerate(clusters):
    for i in cluster: cluster_ids[i] = cid
  return cluster_ids                                # N ints

compute_entropy(cluster_ids):
  counts = Counter(cluster_ids)
  probs = [c/len(cluster_ids) for c in counts.values()]
  return -sum(p * log(p) for p in probs)
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| responses | list[str], len=N_SAMPLES(5) | per question |
| nli logits | [3] | entail/neutral/contradiction, per pair |
| cluster_ids | list[int], len=5 | cluster assignment per response |
| se_scores | list[float], len=n_questions | one entropy value per question |

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | NLI clustering | `cluster_responses`: pairwise bidirectional entailment, union into clusters |
| L-3-2 | Entropy calc | `compute_entropy` + `binarize` (median threshold) |
| L-3-3 | SE pipeline | `compute_se_scores`: wire generate -> cluster -> entropy over question list |

---

## A-5: Pipeline Orchestration [Complexity: 11, Budget: 3]

**Applied**: Standard PyTorch train/eval loop pattern (no direct Archon KB match for orchestration).

### API Signatures

```python
def run_pipeline_for_model(
    model_key: str,
    train_data: "Dataset",
    val_data: "Dataset",
) -> dict:
    """Full per-model run. Returns {"auroc_sep": float, "auroc_se": float, "gap": float}."""

def main() -> None:
    """Loop MODELS -> run_pipeline_for_model -> aggregate -> save JSON -> visualize + check_success."""
```

### Pseudo-code

```
run_pipeline_for_model(model_key, train_data, val_data):
  cfg = MODELS[model_key]
  model = ModelWrapper(cfg["id"]); model.load()
  se_baseline = SemanticEntropyBaseline(NLI_MODEL_ID)

  # 1. SE labels (train+val)
  train_se = se_baseline.compute_se_scores(model, train_data["question"])   # list[float], len=|train|
  val_se   = se_baseline.compute_se_scores(model, val_data["question"])     # list[float], len=|val|
  train_labels = se_baseline.binarize(train_se)                            # list[int]
  val_labels   = se_baseline.binarize(val_se)

  # 2. hidden states at LAYER_FRACTION depth, last-token position
  layer_idx = int(cfg["n_layers"] * LAYER_FRACTION)
  probe = SemanticEntropyProbe(layer_idx, token_position="last")
  train_hidden = stack([probe.extract_hidden_state(model, *tokenize(q)) for q in train_data["question"]])
  # train_hidden: [n_train, hidden_dim]
  val_hidden = stack([probe.extract_hidden_state(model, *tokenize(q)) for q in val_data["question"]])
  # val_hidden: [n_val, hidden_dim]

  # 3. fit + predict
  probe.fit(train_hidden, train_labels)
  sep_proba = probe.predict_proba(val_hidden)[:, 1]        # [n_val]

  # 4. eval both methods vs ground truth (val_data["label"]: truthful/untruthful)
  auroc_sep = compute_auroc(val_data["label"], sep_proba)
  auroc_se  = compute_auroc(val_data["label"], val_se)
  gap = compute_gap(auroc_sep, auroc_se)
  return {"auroc_sep": auroc_sep, "auroc_se": auroc_se, "gap": gap}

main():
  results = {}
  train_data, val_data = split_train_val(load_truthfulqa(), TRAIN_SPLIT, SEED)
  for model_key in MODELS:
    results[model_key] = run_pipeline_for_model(model_key, train_data, val_data)
  save_json(results, f"{RESULTS_DIR}/results.json")
  plot_auroc_comparison(results, f"{FIGURES_DIR}/auroc_comparison.png")
  status = check_success({k: v["gap"] for k, v in results.items()})
  print(status)
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| train_hidden | [n_train, hidden_dim] | hidden_dim: 4096 (llama/mistral) or 3584 (qwen2) |
| val_hidden | [n_val, hidden_dim] | same hidden_dim |
| sep_proba | [n_val] | P(high_SE), positive class column |
| val_se | list[float], len=n_val | continuous entropy scores used directly for SE AUROC |

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | SE label generation | Compute train/val SE scores + binarize |
| L-5-2 | Hidden state extraction + probe fit | Extract [N, hidden_dim] states, fit LogisticRegression |
| L-5-3 | Dual evaluation + aggregation | AUROC for both methods, gap, JSON save, main() loop |

---

## External Dependencies

None — green-field project, no base hypothesis.
