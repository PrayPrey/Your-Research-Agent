# Logic Design: H-E1 Dose-Response Curation (EXISTENCE/PoC)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## L-1: Main Experiment Loop [Complexity: 3, Budget: 3]

**Applied**: Standard PyTorch training loop pattern

### API Signatures

```python
CONFIGS: List[Dict] = [
    {"id": "C0", "perplexity_pct": None, "dedup": "none"},
    {"id": "C1", "perplexity_pct": 10, "dedup": "none"},
    # ... C2-C9 at pct=20..90
    {"id": "D0", "perplexity_pct": 50, "dedup": "none"},
    {"id": "D1", "perplexity_pct": 50, "dedup": "fuzzy_0.7"},
    {"id": "D2", "perplexity_pct": 50, "dedup": "fuzzy_0.85"},
    {"id": "D3", "perplexity_pct": 50, "dedup": "exact"},
    {"id": "D4", "perplexity_pct": 50, "dedup": "exact_plus_fuzzy"},
]

def run_experiment(configs: List[Dict], out_dir: str) -> Dict[str, Dict]:
    """Runs all 15 configs, returns {config_id: benchmark_scores}."""
    ...
```

### Pseudo-code

```
1. results = {}
2. FOR config IN CONFIGS:
3.     ckpt_path = f"{out_dir}/checkpoints/{config.id}"
4.     IF checkpoint_exists(ckpt_path): SKIP training (resume support)
5.     data = build_dataset(config)                      # L-2
6.     model = build_model()                              # fresh GPT2LMHeadModel each run
7.     train(model, data, ckpt_path, config.id)            # L-3
8.     scores = evaluate(ckpt_path)                        # L-4
9.     results[config.id] = scores
10.    save_json(results, f"{out_dir}/benchmark_results.json")  # incremental save
11. analyze(results)                                       # L-5
12. RETURN results
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Config list | Define 15-config sweep table |
| L-1-2 | Loop driver | Sequential run with incremental result save |
| L-1-3 | Resume logic | Skip configs with existing checkpoint |

---

## L-2: Data Filtering Functions [Complexity: 2, Budget: 3]

**Applied**: Standard HuggingFace `datasets` filter/map pattern

### API Signatures

```python
def apply_perplexity_filter(dataset: IterableDataset, threshold_percentile: Optional[int]) -> IterableDataset:
    """Keep docs with ccnet_perplexity below given percentile. None = no filter."""
    ...

def apply_deduplication(dataset: IterableDataset, stringency_level: str) -> IterableDataset:
    """MinHash/exact dedup. stringency_level in {none, fuzzy_0.7, fuzzy_0.85, exact, exact_plus_fuzzy}."""
    ...

def build_dataset(config: Dict, target_tokens: int = 10_000_000_000, seq_len: int = 1024) -> Iterator[Tensor]:
    """Load RedPajama-v2, filter, dedup, tokenize, chunk to seq_len. Yields [seq_len] token id tensors."""
    ...

def tokenize_and_chunk(dataset: IterableDataset, tokenizer, seq_len: int = 1024) -> Iterator[Tensor]:
    """Tokenize text field, concat + split into fixed seq_len blocks."""
    ...
```

### Pseudo-code

```
apply_perplexity_filter(dataset, pct):
    IF pct is None: RETURN dataset
    sample = take_first_n(dataset, N=1_000_000)          # percentile estimated from subsample (streaming)
    threshold = np.percentile([x.ccnet_perplexity for x in sample], pct)
    RETURN dataset.filter(lambda x: x.ccnet_perplexity < threshold)

apply_deduplication(dataset, level):
    IF level == "none": RETURN dataset
    cfg = DEDUP_CONFIGS[level]   # {threshold, exact} per PRD table
    RETURN MinHashDeduplicator(**cfg).deduplicate(dataset)

build_dataset(config):
    ds = load_dataset("togethercomputer/RedPajama-Data-v2", split="train", streaming=True)
    ds = apply_perplexity_filter(ds, config.perplexity_pct)
    ds = apply_deduplication(ds, config.dedup)
    token_stream = tokenize_and_chunk(ds, gpt2_tokenizer, seq_len=1024)
    RETURN take_until_token_budget(token_stream, target_tokens)  # stop at 10B tokens
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| token_chunk | [1024] | Single training sequence (int64 ids) |
| batch | [512, 1024] | 524,288 tokens/batch |

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Perplexity filter | Percentile threshold via subsample estimate |
| L-2-2 | Dedup filter | MinHash config dispatch table |
| L-2-3 | Tokenize+chunk | Stream tokenize, pack to seq_len, cap at 10B tokens |

---

## L-3: Training Loop with Checkpointing [Complexity: 3, Budget: 3]

**Applied**: nanoGPT-style train loop with AdamW + cosine schedule

### API Signatures

```python
def build_model(seed: int = 42) -> GPT2LMHeadModel:
    """GPT2Config(vocab=50257, n_positions=1024, n_embd=768, n_layer=12, n_head=12)."""
    ...

def get_cosine_schedule(optimizer, warmup_steps: int = 2000, total_steps: int = 19000, min_lr_ratio: float = 0.1):
    ...

def train(
    model: GPT2LMHeadModel,
    data: Iterator[Tensor],
    ckpt_dir: str,
    config_id: str,
    batch_size: int = 512,
    total_steps: int = 19000,
    ckpt_every: int = 2000,
) -> None:
    """Trains and writes checkpoint every ckpt_every steps + final."""
    ...
```

### Pseudo-code

```
train(model, data, ckpt_dir, config_id):
    optim = AdamW(model.parameters(), lr=6e-4, betas=(0.9, 0.95), weight_decay=0.1)
    sched = get_cosine_schedule(optim, warmup_steps=2000, total_steps=19000)
    resume_step = load_latest_checkpoint_if_exists(ckpt_dir, model, optim, sched)  # resume support

    FOR step IN range(resume_step, 19000):
        batch = next_batch(data, batch_size=512)          # [512, 1024]
        logits = model(batch).logits                      # [512, 1024, 50257]
        loss = cross_entropy(logits[:, :-1], batch[:, 1:]) # next-token prediction
        loss.backward()
        clip_grad_norm(model.parameters(), 1.0)
        optim.step(); sched.step(); optim.zero_grad()

        IF step % ckpt_every == 0 OR step == 18999:
            save_checkpoint(ckpt_dir, model, optim, sched, step, config_id)
        log_metric(config_id, step, loss.item())
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| batch | [512, 1024] | Input ids |
| logits | [512, 1024, 50257] | Vocab logits |
| loss | scalar | Cross-entropy over shifted tokens |

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Model/optim setup | GPT2 init + AdamW + cosine schedule |
| L-3-2 | Train step loop | Forward/backward/step over 19000 steps |
| L-3-3 | Checkpointing | Periodic save + resume-on-restart |

---

## L-4: Evaluation Pipeline [Complexity: 2, Budget: 2]

**Applied**: lm-evaluation-harness standard eval

### API Signatures

```python
def evaluate(ckpt_path: str, tasks: List[str] = None) -> Dict[str, float]:
    """Runs lm-eval-harness, returns {task: accuracy}."""
    ...

def compute_ensemble_score(task_scores: Dict[str, float], pca_model=None) -> float:
    """PC1 of 4 benchmark accuracies. Fits PCA across all 15 configs' scores."""
    ...
```

### Pseudo-code

```
evaluate(ckpt_path):
    results = lm_eval.evaluator.simple_evaluate(
        model="hf", model_args=f"pretrained={ckpt_path}",
        tasks=["hellaswag", "arc_easy", "piqa", "winogrande"], batch_size=32)
    RETURN {
        "hellaswag": results["hellaswag"]["acc_norm"],
        "arc_easy": results["arc_easy"]["acc"],
        "piqa": results["piqa"]["acc"],
        "winogrande": results["winogrande"]["acc"],
    }

compute_ensemble_score(all_config_scores):            # called once after all 15 configs done
    X = matrix([scores[b] for b in BENCHMARKS] for scores in all_config_scores)  # [15, 4]
    pc1 = PCA(n_components=1).fit_transform(X)         # [15, 1]
    RETURN pc1.flatten()
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| X | [15, 4] | Per-config benchmark accuracy matrix |
| pc1 | [15] | Ensemble score per config |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Per-benchmark eval | lm-eval-harness call, 4 tasks |
| L-4-2 | PC1 ensemble | Cross-config PCA on accuracy matrix |

---

## L-5: Polynomial Regression + AIC Model Selection [Complexity: 2, Budget: 2]

**Applied**: sklearn PolynomialFeatures + AIC comparison

### API Signatures

```python
def fit_and_select(x: np.ndarray, y: np.ndarray, max_degree: int = 3) -> Dict:
    """Fit degree 1-3 polynomials, select by lowest AIC. x: [N], y: [N]."""
    ...

def find_peak(model, x_range: Tuple[float, float], degree: int) -> Optional[float]:
    """Locate interior maximum of fitted polynomial within x_range, else None."""
    ...

def analyze(results: Dict[str, Dict]) -> Dict:
    """Runs fit_and_select for perplexity-dim (C0-C9) and dedup-dim (D0-D4). Saves figures."""
    ...
```

### Pseudo-code

```
fit_and_select(x, y, max_degree=3):
    best = None
    FOR degree IN [1, 2, 3]:
        X_poly = PolynomialFeatures(degree).fit_transform(x.reshape(-1,1))  # [N, degree+1]
        model = LinearRegression().fit(X_poly, y)
        y_pred = model.predict(X_poly)
        n, k = len(y), degree + 1
        rss = sum((y - y_pred)**2)
        aic = n * log(rss/n) + 2*k
        IF best is None OR aic < best.aic: best = {degree, aic, model}
    RETURN best

find_peak(model, x_range, degree):
    IF degree < 2: RETURN None                          # linear has no interior max
    coeffs = model.coef_
    deriv_roots = roots(polyder(coeffs))
    interior = [r for r in deriv_roots IF x_range[0] < r < x_range[1] AND is_maximum(r)]
    RETURN interior[0] IF interior ELSE None

analyze(results):
    x_perp = [0, 10, 20, ..., 90]                        # C0-C9 percentile values (C0=0)
    y_perp = [ensemble_score(results[c]) for c in ["C0",...,"C9"]]
    perp_fit = fit_and_select(x_perp, y_perp)
    perp_peak = find_peak(perp_fit.model, (0, 90), perp_fit.degree)

    x_dedup = [0, 1, 2, 3, 4]                             # D0-D4 ordinal stringency
    y_dedup = [ensemble_score(results[c]) for c in ["D0",...,"D4"]]
    dedup_fit = fit_and_select(x_dedup, y_dedup)
    dedup_peak = find_peak(dedup_fit.model, (0, 4), dedup_fit.degree)

    plot_dose_response(x_perp, y_perp, perp_fit, save="figures/dose_response_perplexity.png")
    plot_dose_response(x_dedup, y_dedup, dedup_fit, save="figures/dose_response_dedup.png")
    RETURN {"perplexity": {fit: perp_fit, peak: perp_peak}, "dedup": {fit: dedup_fit, peak: dedup_peak}}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | AIC model selection | Degree 1-3 fit + AIC comparison per dimension |
| L-5-2 | Peak detection + plots | Interior maximum + dose-response figures |

---

## Total Budget Check: 3+3+3+2+2 = 13 subtasks across 5 tasks (within allocation)
