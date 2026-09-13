# Logic: H-M2 (Entropy-Eviction Tolerance)

Applied: H2O heavy-hitter + recent-window ratio-controlled eviction (FMInference/H2O NeurIPS'23 pattern, KB found no direct H2O doc — using architecture-specified pattern)
Applied: HF `datasets` load pattern (reused from H-M1 `data.py`, verified via Serena)
Applied: scipy shapiro->ttest/mannwhitney branch pattern (reused from H-M1 `stats.py` convention)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1)
**Status**: API signatures verified from actual H-M1 code (not spec)
**Analyzed Path**: `docs/youra_research/h-m1/code/config.py`, `docs/youra_research/h-m1/code/data.py`
**Relevant Symbols**:
- `config.py`: `DOMAINS` (Constant), `DataConfig(dataset_name="THUDM/LongBench-v2", samples_per_domain=30, n_probe_tokens=100, seed=42)`, `ModelConfig(model_name="meta-llama/Llama-2-7b-hf", torch_dtype="float16", device_map="auto", output_attentions=True, n_layers=32, n_heads=32)`
- `data.py`: `load_longbench_v2() -> Dataset`, `sample_domain(dataset, domain: str, n: int, seed: int) -> list[str]` (returns **context strings only**, no reference/answer field), `tokenize_probe(text, tokenizer, n_tokens) -> dict`, `load_all_samples(config=None) -> dict[str, list[str]]`

**Discrepancy vs 03_architecture.md**: dataset name is `THUDM/LongBench-v2` (actual code) not `THUDM/LongBench` (PRD FR data spec / architecture text) — use `THUDM/LongBench-v2`, matches H-M1 `DataConfig.dataset_name`.

**Gap**: `sample_domain`/`load_all_samples` return raw context strings, not `{context, question, answer}` dicts. H-M2 `compute_accuracy` needs a reference answer — LongBench-v2 items carry `answer` field in the raw HF dataset row. H-M2's `data.py` must NOT reuse `sample_domain` as-is; wrap `load_longbench_v2()` directly and keep full item dicts (context+question+answer), preserving H-M1's domain-blocked sampling order/seed for stratification alignment.

---

## External Dependencies API

```python
# From: h-m1/code/config.py (ACTUAL CODE)
DOMAINS: list[str]                     # 6 domain names, fixed order
class DataConfig:
    dataset_name: str = "THUDM/LongBench-v2"
    samples_per_domain: int = 30
    n_probe_tokens: int = 100
    seed: int = 42
class ModelConfig:
    model_name: str = "meta-llama/Llama-2-7b-hf"
    torch_dtype: str = "float16"
    device_map: str = "auto"
    output_attentions: bool = True
    n_layers: int = 32
    n_heads: int = 32

# From: h-m1/code/data.py (ACTUAL CODE)
def load_longbench_v2() -> Dataset:
    """HF load_dataset('THUDM/LongBench-v2', split='train')"""

def sample_domain(dataset, domain: str, n: int, seed: int) -> list[str]:
    """Returns list of context strings (NOT dicts) — insufficient for H-M2, see below"""
```

**H-M2 uses `load_longbench_v2` directly**; does NOT call `sample_domain`/`load_all_samples` (they discard `answer`/`question` fields required for accuracy scoring).

---

## A-1: Reuse H-M1 config/data [Complexity: 5, Budget: 5]

**Applied**: Direct file copy + extend (Serena-verified signatures above)

### API Signatures

```python
# config.py — copy DOMAINS, DataConfig, ModelConfig verbatim from h-m1/code/config.py, then add:
@dataclass
class StratConfig:
    entropy_matrix_path: str = "../h-m1/code/entropy_matrix.npy"
    domain_means_path: str = "../h-m1/code/domain_means.json"

@dataclass
class EvictionConfig:
    retention_ratios: tuple = (1.0, 0.8, 0.4)
    heavy_ratio_frac: float = 0.5
    recent_ratio_frac: float = 0.5

# data.py — new function (H-M1's sample_domain NOT reused, see Gap above)
def sample_domain_full(dataset, domain: str, n: int, seed: int) -> list[dict]:
    """Same domain-blocked/seeded order as H-M1 sample_domain. Returns [{context, question, answer}]."""

def load_all_samples_full(config: DataConfig = None) -> list[dict]:
    """Flattened 180 samples, domain-blocked order (30/domain × 6), matches entropy_matrix.npy row order."""
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A1-1 | Copy config.py | DOMAINS, DataConfig, ModelConfig verbatim |
| L-A1-2 | Add StratConfig/EvictionConfig | new dataclasses |
| L-A1-3 | New sample_domain_full/load_all_samples_full | preserve context+question+answer, same seed/order as H-M1 |
| L-A1-4 | Sanity check | len(load_all_samples_full()) == 180 == entropy_matrix.shape[0] |

---

## A-2: Vendor H2O repo [Complexity: 8, Budget: 8]

**Applied**: git clone vendoring (no PyPI package)

### API Signatures

```python
# setup step only, no new Python API — clone into h-m2/code/external/h2o/
# subprocess: git clone https://github.com/FMInference/H2O external/h2o
# verify import: from external.h2o.h2o_hf.utils_hh.modify_llama import H2OKVCache_LayerWise
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A2-1 | Clone script | `git clone` into `external/h2o/`, pin commit hash |
| L-A2-2 | Verify import path | try/except import chain across candidate filenames in cloned repo |
| L-A2-3 | requirements merge | add H2O repo's own deps if any conflict |
| L-A2-4 | Fallback note | if import fails, document awslabs/keys_values fallback path |

---

## A-3: Entropy stratification [Complexity: 7, Budget: 7]

**Applied**: numpy/json artifact load + domain-blocked index reconstruction

### API Signatures

```python
def load_entropy_artifacts(strat_config: StratConfig) -> tuple[np.ndarray, dict]:
    """Returns (entropy_matrix [180, 32, 32], domain_means: dict[str, float])"""

def domain_median_split(domain_means: dict) -> tuple[list[str], list[str]]:
    """(high_entropy_domains, low_entropy_domains) split by median(domain_means.values())."""

def assign_sample_groups(domains_order: list[str], samples_per_domain: int,
                          high_domains: list[str]) -> np.ndarray:
    """bool[180], True=high-entropy group. domains_order == DOMAINS (H-M1 block order)."""

def per_sample_entropy(entropy_matrix: np.ndarray) -> np.ndarray:
    """Mean over layers/heads. [180, 32, 32] -> [180]"""
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| entropy_matrix | [180, 32, 32] | (sample, layer, head), domain-blocked rows |
| domain_means | dict[str,float] | 6 keys |
| group_mask | [180] bool | True = high-entropy |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A3-1 | load_entropy_artifacts | np.load + json.load |
| L-A3-2 | domain_median_split + assign_sample_groups | median split, block-index expand |
| L-A3-3 | per_sample_entropy | reduce [180,32,32]->[180] |
| L-A3-4 | Assert ~90/90 split | sanity check group sizes |

---

## A-4: H2O eviction wrapper [Complexity: 15, Budget: 15]

**Applied**: H2O heavy-hitter (top-k cumulative attention score) + recent-window sliding cache, hook-based per-layer

### API Signatures

```python
class H2OWrapper:
    def __init__(self, model: nn.Module, retention_ratio: float,
                 heavy_frac: float = 0.5, recent_frac: float = 0.5): ...

    def attach(self) -> None:
        """Register forward hooks on each self-attn layer. No-op if retention_ratio==1.0."""

    def detach(self) -> None:
        """Remove all registered hooks, restore original forward."""

    def generate(self, input_ids: Tensor, max_new_tokens: int) -> Tensor:
        """input_ids: [1, L] -> output_ids: [1, L+T]"""
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [1, L] | batch=1 |
| attn_scores | [1, H, L, L] | per-layer, used for heavy-hitter scoring |
| kv_cache (per layer) | [1, H, cache_len, D] | cache_len shrinks to `int(L * retention_ratio)` post-eviction |
| heavy_budget | int | `int(cache_len * retention_ratio * heavy_frac)` |
| recent_budget | int | `int(cache_len * retention_ratio * recent_frac)` |

### Pseudo-code (eviction step, per decode step)

```
1. score = cumulative_attn_score[layer]  # [H, cache_len], running sum of attn probs per KV position
2. heavy_idx = topk(score, heavy_budget).indices
3. recent_idx = last recent_budget positions (always kept)
4. keep_idx = union(heavy_idx, recent_idx)
5. kv_cache[layer] = kv_cache[layer][:, :, keep_idx, :]
6. score = score[:, keep_idx]
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A4-1 | Hook registration | attach/detach on `model.model.layers[i].self_attn` |
| L-A4-2 | Score tracking | maintain running cumulative attn score buffer per layer |
| L-A4-3 | Eviction step | topk heavy + recent window union, apply to KV cache tensors |
| L-A4-4 | generate() wrapper | wrap `model.generate` with hooks attached/detached |

---

## A-5: Mechanism verification [Complexity: 6, Budget: 6]

**Applied**: assertion-based sanity check on cache tensor size

### API Signatures

```python
def verify_h2o_mechanism(model: nn.Module, sample_input: dict, ratio: float) -> bool:
    """Runs one forward+generate at given ratio, asserts evicted cache_len <= full_len*(ratio+0.05).
    Raises AssertionError on failure. Returns True on pass."""
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A5-1 | Full-cache baseline run | capture cache_len at ratio=1.0 |
| L-A5-2 | Evicted run at 0.4/0.8 | capture post-eviction cache_len |
| L-A5-3 | Assertion | cache_len_evicted <= cache_len_full * (ratio + margin) |
| L-A5-4 | Call at pipeline start | run before full inference loop, fail fast |

---

## A-6: Inference pipeline [Complexity: 13, Budget: 13]

**Applied**: single-sample batch=1 generation loop (NFR-2)

### API Signatures

```python
def run_condition(model, tokenizer, samples: list[dict], retention_ratio: float,
                   eviction_config: EvictionConfig) -> list[float]:
    """One H2OWrapper attach/generate/detach cycle per sample. Returns 180 accuracies."""

def run_all_conditions(model, tokenizer, samples: list[dict],
                        eviction_config: EvictionConfig) -> dict[float, list[float]]:
    """{1.0: [...180], 0.8: [...180], 0.4: [...180]}"""
```

### Pseudo-code

```
for ratio in eviction_config.retention_ratios:
    wrapper = H2OWrapper(model, ratio, heavy_frac, recent_frac)
    wrapper.attach()
    accs = []
    for sample in samples:
        ids = tokenizer(sample["context"] + sample["question"], return_tensors="pt", truncation=True)
        out = wrapper.generate(ids.input_ids, max_new_tokens=50)
        text = tokenizer.decode(out[0, ids.input_ids.shape[1]:])
        accs.append(compute_accuracy(text, sample["answer"]))
    wrapper.detach()
    results[ratio] = accs
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A6-1 | run_condition loop | per-sample generate + score |
| L-A6-2 | run_all_conditions | iterate 3 ratios, reuse loaded model |
| L-A6-3 | Truncation/context window guard | cap tokenized length to model max_position_embeddings |
| L-A6-4 | Progress logging | print per-domain progress (reuse H-M1 log style) |

---

## A-7: Accuracy metric [Complexity: 8, Budget: 8]

**Applied**: LongBench convention F1 (QA-style) / ROUGE-L (summarization-style) per domain

### API Signatures

```python
def compute_accuracy(generated_text: str, reference: str, domain: str = None) -> float:
    """domain in summarization-type -> rouge_l_f1; else -> token_f1. Returns [0,1]."""

def token_f1(pred: str, ref: str) -> float: ...
def rouge_l_f1(pred: str, ref: str) -> float: ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A7-1 | token_f1 | normalize+split, precision/recall/F1 |
| L-A7-2 | rouge_l_f1 | LCS-based ROUGE-L |
| L-A7-3 | Domain->metric map | reuse DOMAIN_CATEGORIES from H-M1 config if present, else static dict |
| L-A7-4 | compute_accuracy dispatch | route by domain, default token_f1 |

---

## A-8: Retention + stats [Complexity: 9, Budget: 9]

**Applied**: shapiro normality gate -> ttest_ind else mannwhitneyu (H-M1 stats.py convention)

### API Signatures

```python
def compute_retention(acc_by_condition: dict[float, list[float]]) -> dict[float, np.ndarray]:
    """retention[ratio] = array(acc[ratio]) / array(acc[1.0]), elementwise. [180] per ratio."""

def compare_groups(high_retention: np.ndarray, low_retention: np.ndarray) -> dict:
    """{t_stat, p_value, cohens_d, test_used: str, normal: bool}"""

def evaluate_gate(p_value: float, high_mean: float, low_mean: float,
                   d: float, threshold: float = 0.05) -> bool:
    """PASS if p<threshold and high_mean>low_mean and d>0.5"""
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A8-1 | compute_retention | elementwise division per ratio, guard div-by-zero |
| L-A8-2 | shapiro test both groups | normal flag |
| L-A8-3 | compare_groups dispatch | ttest_ind vs mannwhitneyu + cohens_d (pooled std) |
| L-A8-4 | evaluate_gate | 3-condition AND gate |

---

## A-9: Visualization suite [Complexity: 7, Budget: 7]

**Applied**: matplotlib/seaborn (H-M1 visualize.py conventions)

### API Signatures

```python
def plot_gate_bar(high_retention: np.ndarray, low_retention: np.ndarray,
                   gate_result: dict, output_dir: str) -> str:  # mandatory
    """Bar chart, mean+SEM error bars, 2 groups. Saves PNG, returns path."""

def plot_boxplot(high_retention: np.ndarray, low_retention: np.ndarray, output_dir: str) -> str: ...
def plot_scatter_entropy_retention(entropy: np.ndarray, retention: np.ndarray, output_dir: str) -> str: ...
def plot_heatmap_domain_ratio(retention_by_domain_ratio: dict, output_dir: str) -> str:
    """retention_by_domain_ratio: dict[domain][ratio] -> mean retention. 6x2 heatmap."""
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A9-1 | plot_gate_bar (mandatory) | bar+error bars, save |
| L-A9-2 | plot_boxplot + plot_scatter | 2 plots |
| L-A9-3 | plot_heatmap_domain_ratio | domain x ratio grid |

---

## A-10: Pipeline orchestration [Complexity: 8, Budget: 8]

**Applied**: H-M1 run_experiment.py structure (load->compute->stats->visualize->save JSON)

### API Signatures

```python
def run_pipeline(strat_config: StratConfig = None, model_config: ModelConfig = None,
                  eviction_config: EvictionConfig = None) -> dict:
    """Full pipeline. Returns {p_value, cohens_d, gate_pass, high_mean, low_mean, test_used}."""

def main() -> None: ...
```

### Pseudo-code

```
1. entropy_matrix, domain_means = load_entropy_artifacts(strat_config)
2. high_domains, low_domains = domain_median_split(domain_means)
3. group_mask = assign_sample_groups(DOMAINS, 30, high_domains)
4. samples = load_all_samples_full()  # 180, domain-blocked, matches group_mask order
5. model, tokenizer = load_model(model_config)
6. verify_h2o_mechanism(model, samples[0], ratio=0.4)
7. acc_by_condition = run_all_conditions(model, tokenizer, samples, eviction_config)
8. retention = compute_retention(acc_by_condition)
9. high_ret, low_ret = retention[0.4][group_mask], retention[0.4][~group_mask]
10. stats = compare_groups(high_ret, low_ret)
11. gate_pass = evaluate_gate(**stats subset)
12. plot_gate_bar(...), plot_boxplot(...), plot_scatter_entropy_retention(...), plot_heatmap_domain_ratio(...)
13. json.dump(results, "results.json")
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A10-1 | Stage wiring | steps 1-7 above |
| L-A10-2 | Stats + gate | steps 8-11, use 0.4 (aggressive) as primary condition per PRD FR5 |
| L-A10-3 | Visualization calls | steps 12 |
| L-A10-4 | JSON save + main() | serialize results dict, CLI entrypoint |
