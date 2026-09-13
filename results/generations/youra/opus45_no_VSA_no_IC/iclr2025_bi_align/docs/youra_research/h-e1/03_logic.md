# Logic: H-E1 (EXISTENCE)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field - no existing codebase
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

KB search ("reward model inference batching pattern") returned no relevant matches (unrelated diffusion-model results). Using standard HF `transformers` + PyTorch patterns.

---

## A-1: Data pipeline [Complexity: 8, Budget: 8]

**Applied**: Standard pandas/HF datasets pattern

### API Signatures

```python
def load_battles(dataset_id: str) -> pd.DataFrame:
    """Load raw Arena battles via datasets.load_dataset."""
    ...

def filter_valid(df: pd.DataFrame) -> pd.DataFrame:
    """Keep rows where winner in {model_a, model_b, tie, tie (bothbad)}."""
    ...

def extract_prompt_response(row: dict) -> tuple[str, str, str]:
    """Returns (prompt, response_a, response_b)."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | load_battles | HF datasets.load_dataset(dataset_id, split="train") -> pd.DataFrame |
| L-1-2 | filter_valid | boolean mask on `winner` column, dropna on conversation fields |
| L-1-3 | extract_prompt_response | parse conversation_a/conversation_b turn lists -> first user turn + first assistant turns |
| L-1-4 | schema validation | assert non-null prompt/resp_a/resp_b post-extraction |

---

## A-2: RM wrapper + scoring loop [Complexity: 14, Budget: 14]

**Applied**: HF AutoModelForSequenceClassification single-score pattern; PairRM listwise pattern; ArmoRM multi-objective gating pattern (RewardBench-style unified interface)

### API Signatures

```python
class RewardModel:
    def __init__(self, model_id: str, model_type: str):
        """model_type: 'classifier' | 'pairwise' | 'moe'."""
        ...

    def score(self, prompt: str, response: str) -> float:
        """Single scalar reward. Internally dispatches by self.model_type."""
        ...

def score_all_battles(
    df: pd.DataFrame,
    models: dict[str, RewardModel],
) -> pd.DataFrame:
    """Adds columns {model_name}_score_a, {model_name}_score_b for each model. Resumes from cache."""
    ...

def cache_scores(df: pd.DataFrame, path: str) -> None: ...
def load_cached_scores(path: str) -> pd.DataFrame | None: ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [1, L] | single prompt+response pair, L = tokenizer max_length |
| classifier logits | [1, 1] | OpenAssistant deberta output |
| pairwise logits | [1, 2] | PairRM: prompt+resp_a vs prompt+resp_b -> softmax pick |
| moe reward | [1, 19] -> [1] | ArmoRM multi-objective vector, weighted-sum to scalar per RewardBench gating head |

### Pseudo-code (dispatch logic — non-trivial across 3 model types)

```
RewardModel.score(prompt, response):
    if model_type == "classifier":
        text = tokenizer(prompt, response, truncation=True)  # [1, L]
        logit = model(**text).logits  # [1, 1]
        return logit.item()

    if model_type == "pairwise":
        # PairRM requires both responses; score() called per-response is asymmetric.
        # Convention: score(prompt, response) returns response's win-logit vs empty baseline
        # via model.blender.rank([prompt], [[response]])[0]
        return pairrm_rank_score(prompt, response)

    if model_type == "moe":
        text = tokenizer(prompt, response, truncation=True)
        obj_scores = model(**text).rewards  # [1, 19]
        return (obj_scores * gating_weights).sum().item()
```

```
score_all_battles(df, models):
    cached = load_cached_scores(OUTPUT_DIR + "rm_scores.parquet")
    if cached is not None:
        df = merge(df, cached, on="battle_id", how="left")
    for name, rm in models.items():
        col_a, col_b = f"{name}_score_a", f"{name}_score_b"
        if col_a in df and df[col_a].notna().all():
            continue  # resume: skip fully-scored model
        for batch in chunks(df[df[col_a].isna()], BATCH_SIZE):
            df.loc[batch.index, col_a] = [rm.score(p, ra) for p, ra in zip(batch.prompt, batch.resp_a)]
            df.loc[batch.index, col_b] = [rm.score(p, rb) for p, rb in zip(batch.prompt, batch.resp_b)]
            cache_scores(df, OUTPUT_DIR + "rm_scores.parquet")  # periodic checkpoint
    return df
```

### Subtasks [4/4 used] (budget cap = 3 per task allocation note, using 4 per architecture breakdown "4+3+4+3" — see below)

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | RewardModel.__init__ | load tokenizer+model per model_type, .to(device), .eval() |
| L-2-2 | RewardModel.score dispatch | classifier/pairwise/moe branches per pseudo-code above |
| L-2-3 | score_all_battles + resume cache | batch loop, cache-aware skip, periodic parquet checkpoint |
| L-2-4 | cache_scores/load_cached_scores | parquet read/write, battle_id key merge |

---

## A-3: Score normalization [Complexity: 6, Budget: 6]

**Applied**: Standard z-score + sigmoid squashing

### API Signatures

```python
def zscore_sigmoid(scores: np.ndarray) -> np.ndarray:
    """z = (scores - mean) / std; return sigmoid(z) in [0,1]."""
    ...

def compute_rm_variance(row: dict, model_names: list[str]) -> float:
    """Variance across model_names' normalized scores for the chosen response."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | zscore_sigmoid | per-model z-score across full column, then torch/np sigmoid |
| L-3-2 | apply per model per response | normalize {model}_score_a/b columns independently per model |
| L-3-3 | compute_rm_variance | np.var([m1_norm, m2_norm, m3_norm]) per battle, per response side, then avg or per-winner |
| L-3-4 | attach rm_variance column to df | ...|

---

## A-4: Human entropy calculation [Complexity: 7, Budget: 7]

**Applied**: Standard Shannon entropy on categorical win-rate distribution

### API Signatures

```python
def compute_pair_entropy(df: pd.DataFrame) -> pd.DataFrame:
    """Groups by (model_a, model_b), computes P=[p_a,p_tie,p_b] win-rate, H=-sum(p*log2(p)). Adds human_entropy col (broadcast per row)."""
    ...

def compute_cluster_entropy_fallback(df: pd.DataFrame) -> pd.DataFrame:
    """FR-7: cluster prompts (embedding + kmeans or hash-based), entropy within cluster."""
    ...
```

### Pseudo-code

```
compute_pair_entropy(df):
    groups = df.groupby(["model_a", "model_b"])
    for (ma, mb), grp in groups:
        counts = grp.winner.value_counts(normalize=True)  # {model_a, model_b, tie, tie(bothbad)}
        p = [counts.get(k, 0) for k in ["model_a", "model_b", "tie"]]  # merge tie variants
        H = -sum(pi * log2(pi) for pi in p if pi > 0)
        df.loc[grp.index, "human_entropy"] = H
    return df
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | groupby model-pair win distribution | value_counts normalize per pair |
| L-4-2 | entropy formula | -sum(p*log2(p)), guard p=0 |
| L-4-3 | compute_cluster_entropy_fallback (FR-7) | TF-IDF/embedding cluster prompts, per-cluster entropy |
| L-4-4 | broadcast + median split flag prep | attach human_entropy col to all rows |

---

## A-5: Mode classification [Complexity: 5, Budget: 5]

**Applied**: Median-split quadrant assignment

### API Signatures

```python
def assign_modes(df: pd.DataFrame) -> pd.DataFrame:
    """Median split human_entropy & rm_variance -> mode in {1,2,3,4}. Mode 3 = High-H, Low-V."""
    ...

def mode_distribution(df: pd.DataFrame) -> dict:
    """Returns {mode: {"count": int, "proportion": float}} for modes 1-4."""
    ...
```

### Pseudo-code

```
assign_modes(df):
    h_med, v_med = df.human_entropy.median(), df.rm_variance.median()
    df["mode"] = 2*(df.human_entropy > h_med) + 1*(df.rm_variance <= v_med) + 1
    # mode 1: Low-H,Low-V | mode 2: Low-H,High-V | mode 3: High-H,Low-V | mode 4: High-H,High-V
    return df
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | median computation | df.median() on both axes |
| L-5-2 | mode assignment | vectorized boolean arithmetic per pseudo-code |
| L-5-3 | mode_distribution | value_counts(normalize=True) on mode col -> dict |
| L-5-4 | edge-case: exact-median ties | inclusive `<=` for variance per pseudo-code |

---

## A-6: Statistical testing [Complexity: 6, Budget: 6]

**Applied**: scipy.stats.binomtest one-sided pattern

### API Signatures

```python
def binomial_test_mode3(count: int, total: int, p0: float = 0.10) -> dict:
    """One-sided binomtest H1: p > p0. Returns {proportion, ci_95_lower, ci_95_upper, p_value, result}."""
    ...

def sensitivity_analysis(count: int, total: int, thresholds: list[float]) -> dict:
    """Re-runs binomial_test_mode3 at each threshold in thresholds. Returns {threshold: result_dict}."""
    ...
```

### Pseudo-code

```
binomial_test_mode3(count, total, p0=0.10):
    res = scipy.stats.binomtest(count, total, p0, alternative="greater")
    ci = res.proportion_ci(confidence_level=0.95, method="wilson")
    return {
        "proportion": count/total,
        "ci_95_lower": ci.low, "ci_95_upper": ci.high,
        "p_value": res.pvalue,
        "result": "SUCCESS" if (res.pvalue < 0.05 and count/total > p0) else "FAIL",
    }
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | binomial_test_mode3 core | scipy.stats.binomtest one-sided, wilson CI |
| L-6-2 | result labeling | SUCCESS/FAIL per PRD success criteria |
| L-6-3 | sensitivity_analysis loop | iterate thresholds [0.05, 0.08, 0.10], collect dict |
| L-6-4 | falsification check | flag if CI includes 0.10 per PRD falsification rule |

---

## A-7: Pipeline integration + outputs [Complexity: 5, Budget: 5]

**Applied**: Standard sequential orchestration script

### API Signatures

```python
def main() -> None:
    """load -> filter -> score (cache-aware) -> normalize -> entropy -> classify -> test -> serialize."""
    ...
```

### Pseudo-code

```
main():
    df = filter_valid(load_battles(DATASET_ID))
    models = {name: RewardModel(mid, TYPE_MAP[name]) for name, mid in RM_MODELS.items() if USE_ARMORM or name != "armorm"}
    df = score_all_battles(df, models)
    for name in models: df[f"{name}_norm_a"], df[f"{name}_norm_b"] = zscore_sigmoid(df[f"{name}_score_a"]), zscore_sigmoid(df[f"{name}_score_b"])
    df["rm_variance"] = df.apply(lambda r: compute_rm_variance(r, list(models)), axis=1)
    df = assign_modes(compute_pair_entropy(df))
    dist = mode_distribution(df)
    mode3 = dist[3]
    stats = binomial_test_mode3(mode3["count"], len(df))
    stats["sensitivity"] = sensitivity_analysis(mode3["count"], len(df), [0.05, 0.08, 0.10])
    json.dump(dist, open(OUTPUT_DIR+"mode_distribution.json","w"))
    json.dump(stats, open(OUTPUT_DIR+"statistical_results.json","w"))
    cache_scores(df, OUTPUT_DIR+"rm_scores.parquet")
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | wire pipeline stages | sequential calls per pseudo-code |
| L-7-2 | FR-6 fallback wiring | USE_ARMORM flag conditionally excludes armorm model |
| L-7-3 | serialize JSON/parquet | json.dump + cache_scores calls |
| L-7-4 | logging/progress | tqdm on batch loop, basic print checkpoints |
