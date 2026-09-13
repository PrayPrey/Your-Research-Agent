# Logic Specification: H-M3 Attractor Analysis

**Hypothesis ID:** h-m3
**Date:** 2026-08-26

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-M1 + H-M2)
**Status**: API signatures verified from actual code (not specs)
**Analyzed Path**: `docs/youra_research/h-m1/code/`, `docs/youra_research/h-m2/code/`

**Relevant Symbols**:
- `h-m2/code/model.py`: `build_policy_model`, `build_reference_model`, `load_trained_policy`, `generate`, `compute_dpo_implicit_reward`, `load_tokenizer`
- `h-m2/code/dpo_train.py`: `build_dpo_trainer`, `train_dpo`
- `h-m2/code/config.py`: `HM2Config`, `get_dpo_config`, `get_peft_config`, `set_seed`
- `h-m1/code/model.py`: `build_reward_model`, `get_reward`, `load_tokenizer` (reward model, **not generative**)
- `h-m1/code/train.py`: `run_training` (RewardTrainer — trains a scalar reward model, no PPO/policy)
- `h-m1/code/config.py`: `HM1Config`, `get_reward_config`, `get_peft_config`

**⚠️ Deviation from brief**: The 02c brief assumes an `h-m1` PPO/RLHF policy trainer (`train_rlhf_model`). Actual H-M1 code only trains a **reward model** (`AutoModelForSequenceClassification`, no `generate()`). There is no existing RLHF generative-policy pipeline to reuse.

**Resolution**: H-M3 implements its own minimal PPO loop (`trl.PPOTrainer`) using the H-M1 reward model checkpoint (`h-m1/code/reward_model_h-m1_quick/final`) as the reward signal, producing a generative RLHF policy comparable to H-M2's DPO policy. DPO arm reuses H-M2's pipeline unchanged.

---

## External Dependencies (Base Hypothesis)

```python
# From: h-m2/code/model.py (ACTUAL CODE)
def load_tokenizer(cfg) -> PreTrainedTokenizer: ...
def build_policy_model(cfg, use_lora: bool = True) -> PreTrainedModel: ...
def build_reference_model(cfg) -> PreTrainedModel: ...
def load_trained_policy(cfg, checkpoint_path: str) -> PreTrainedModel: ...
def generate(model, tokenizer, prompt: str, device: str, max_new_tokens: int = 128) -> str: ...

# From: h-m2/code/dpo_train.py (ACTUAL CODE)
def build_dpo_trainer(cfg, policy_model, ref_model, tokenizer, train_dataset, eval_dataset) -> DPOTrainer: ...
def train_dpo(cfg, trainer) -> str: ...  # returns final_path

# From: h-m2/code/config.py (ACTUAL CODE)
class HM2Config:
    base_model: str; ref_model: str; beta: float; output_dir: str; seed: int
def get_dpo_config(cfg: HM2Config) -> DPOConfig: ...
def get_peft_config(cfg: HM2Config) -> LoraConfig: ...
def set_seed(seed: int) -> None: ...

# From: h-m1/code/model.py (ACTUAL CODE) - reward model only
def build_reward_model(cfg, use_lora: bool = True) -> PreTrainedModel: ...
def get_reward(model, tokenizer, text: str, device: str) -> float: ...
```

**Verified from**: actual implementation, not `02c_experiment_brief.md` (which incorrectly assumes an RLHF policy pipeline exists in H-M1).

---

## A-1: Multi-Seed Training Loop [Complexity: 3, Budget: 3]

**Applied**: Standard PyTorch + TRL (PPOTrainer, DPOTrainer)

### API Signatures

```python
# config.py
@dataclass
class HM3Config:
    base_model: str = "meta-llama/Llama-2-7b-hf"
    seeds: List[int] = field(default_factory=lambda: [42, 137, 256, 512, 1024])
    hm1_reward_checkpoint: str = "../../../h-m1/code/reward_model_h-m1_quick/final"
    hm2_config_ref: str = "../../../h-m2/code/config.py"
    output_root: str = "./h-m3_models"

def train_all_seeds(cfg: HM3Config, methods: List[str] = ["dpo", "rlhf"]) -> Dict[str, str]:
    """Train all (method, seed) combos. Returns {model_id: checkpoint_path}."""
    ...

def train_dpo_seed(cfg: HM3Config, seed: int) -> str:
    """Reuse H-M2 pipeline with seed override. Returns checkpoint path."""
    ...

def train_rlhf_seed(cfg: HM3Config, seed: int) -> str:
    """PPOTrainer loop using H-M1 reward model as reward signal. Returns checkpoint path."""
    ...
```

### Pseudo-code

```
def train_all_seeds(cfg, methods):
    checkpoints = {}
    for method in methods:
        for seed in cfg.seeds:
            model_id = f"{method}_seed{seed}"       # naming convention
            set_seed(seed)                           # from h-m2/config.py
            if method == "dpo":
                path = train_dpo_seed(cfg, seed)
            else:
                path = train_rlhf_seed(cfg, seed)
            checkpoints[model_id] = path
            save_checkpoint_manifest(model_id, path)  # h-m3_models/manifest.json
    return checkpoints

def train_dpo_seed(cfg, seed):
    hm2_cfg = HM2Config(seed=seed, output_dir=f"{cfg.output_root}/dpo_seed{seed}")
    tokenizer = load_tokenizer(hm2_cfg)                       # h-m2/model.py
    policy = build_policy_model(hm2_cfg, use_lora=True)       # h-m2/model.py
    ref = build_reference_model(hm2_cfg)                      # h-m2/model.py
    train_ds, eval_ds = load_hh_rlhf_dpo_splits(hm2_cfg, tokenizer)
    trainer = build_dpo_trainer(hm2_cfg, policy, ref, tokenizer, train_ds, eval_ds)
    return train_dpo(hm2_cfg, trainer)   # returns final_path

def train_rlhf_seed(cfg, seed):
    # PPO loop: policy generates, H-M1 reward model scores, PPOTrainer updates policy
    tokenizer = load_tokenizer(hm2_cfg)                       # reuse H-M2 tokenizer setup
    policy = build_policy_model(hm2_cfg, use_lora=True)       # LoRA CAUSAL_LM, same config as DPO
    reward_model = build_reward_model(hm1_cfg, use_lora=False)
    reward_model.load_adapter(cfg.hm1_reward_checkpoint)
    ppo_trainer = PPOTrainer(config=ppo_config(seed), model=policy, tokenizer=tokenizer)
    for batch in train_ds:
        query_tensors = tokenize(batch["prompt"])
        response_tensors = ppo_trainer.generate(query_tensors)       # [B, L]
        rewards = [get_reward(reward_model, tokenizer, q+r, device) for q, r in zip(...)]
        ppo_trainer.step(query_tensors, response_tensors, rewards)
    output_path = f"{cfg.output_root}/rlhf_seed{seed}/final"
    ppo_trainer.save_pretrained(output_path)
    return output_path
```

### Checkpoint naming convention

`{output_root}/{method}_seed{seed}/final` -> model_id = `f"{method}_seed{seed}"`

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | DPO seed training | Loop `train_dpo_seed` over 5 seeds, reuse H-M2 pipeline |
| L-1-2 | RLHF seed training | PPOTrainer loop over 5 seeds using H-M1 reward model |
| L-1-3 | Checkpoint manifest | Write `h-m3_models/manifest.json` mapping model_id -> path |

---

## A-2: Embedding Extraction [Complexity: 2, Budget: 2]

**Applied**: Standard PyTorch (hidden-state mean pooling)

### API Signatures

```python
def extract_embeddings(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    prompts: List[str],
    device: str,
    batch_size: int = 8,
    max_length: int = 512,
) -> np.ndarray:
    """Batch-extract mean-pooled last-layer hidden states. Returns [n_prompts, hidden_dim]."""
    ...

def extract_all_model_embeddings(
    checkpoints: Dict[str, str],   # model_id -> path
    cfg: HM3Config,
    probe_prompts: List[str],
) -> Dict[str, np.ndarray]:
    """Loads each checkpoint via load_trained_policy, extracts embeddings, unloads. Returns {model_id: [1000, 4096]}."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, L] | B=batch_size, L<=max_length |
| hidden_states[-1] | [B, L, 4096] | Llama-2-7b hidden_dim=4096 |
| embedding (per prompt) | [4096] | mean over L (masked) |
| embeddings (per model) | [1000, 4096] | stacked over probe prompts |

### Pseudo-code

```
def extract_embeddings(model, tokenizer, prompts, device, batch_size=8, max_length=512):
    model.eval()
    all_embeds = []
    for batch_prompts in chunk(prompts, batch_size):
        inputs = tokenizer(batch_prompts, return_tensors="pt", padding=True,
                            truncation=True, max_length=max_length).to(device)
        with torch.no_grad():
            outputs = model(**inputs, output_hidden_states=True)
        last_hidden = outputs.hidden_states[-1]              # [B, L, 4096]
        mask = inputs["attention_mask"].unsqueeze(-1).float() # [B, L, 1]
        pooled = (last_hidden * mask).sum(1) / mask.sum(1)   # [B, 4096] masked mean pool
        all_embeds.append(pooled.cpu().numpy())
    return np.concatenate(all_embeds, axis=0)  # [n_prompts, 4096]

def extract_all_model_embeddings(checkpoints, cfg, probe_prompts):
    tokenizer = load_tokenizer(cfg)
    result = {}
    for model_id, path in checkpoints.items():
        model = load_trained_policy(cfg, path)   # merges LoRA, eval mode
        result[model_id] = extract_embeddings(model, tokenizer, probe_prompts, cfg.device)
        del model; torch.cuda.empty_cache()       # memory: unload between models
    np.save("behavior_embeddings.npy", result)
    return result
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | Single-model extraction | `extract_embeddings`, batched masked mean pool |
| L-2-2 | All-model orchestration | Loop over 10 checkpoints, load/unload for memory |

---

## A-3: Similarity Matrix Computation [Complexity: 2, Budget: 2]

**Applied**: Standard PyTorch/sklearn (cosine_similarity)

### API Signatures

```python
def compute_similarity_matrix(
    embeddings_dict: Dict[str, np.ndarray],  # model_id -> [1000, 4096]
) -> Dict:
    """Pairwise cosine similarity between model-level mean embeddings. Returns structured dict."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| model_means | [10, 4096] | per-model mean over 1000 probes |
| similarity_matrix | [10, 10] | cosine sim between model pairs |

### Pseudo-code

```
def compute_similarity_matrix(embeddings_dict):
    model_ids = list(embeddings_dict.keys())                        # 10 ids
    model_means = np.stack([embeddings_dict[m].mean(axis=0) for m in model_ids])  # [10, 4096]
    sim = cosine_similarity(model_means)                             # [10, 10]

    method_labels = ["dpo" if "dpo" in m else "rlhf" for m in model_ids]
    within, cross = [], []
    for i in range(10):
        for j in range(i+1, 10):
            (within if method_labels[i] == method_labels[j] else cross).append(sim[i, j])

    return {
        "model_ids": model_ids,
        "similarity_matrix": sim,           # [10, 10]
        "within_method_sims": within,
        "cross_method_sims": cross,
        "within_mean": np.mean(within),
        "cross_mean": np.mean(cross),
        "clustering_gap": np.mean(within) - np.mean(cross),
    }
```

### Subtasks [1/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | Similarity + split | Compute [10,10] matrix, split within/cross pairs |

---

## A-4: Clustering Analysis [Complexity: 2, Budget: 2]

**Applied**: sklearn.cluster.KMeans + silhouette_score/silhouette_samples

### API Signatures

```python
def analyze_clustering(
    embeddings: np.ndarray,        # [10, 4096] model-level means
    method_labels: List[str],      # len 10, values "dpo"/"rlhf"
) -> Dict:
    """K-means k=2, silhouette overall + per-method, cluster-label alignment."""
    ...
```

### Pseudo-code

```
def analyze_clustering(embeddings, method_labels):
    kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(embeddings)        # [10]

    score = silhouette_score(embeddings, method_labels)
    samples = silhouette_samples(embeddings, method_labels)  # [10]
    labels_arr = np.array(method_labels)

    # Alignment: best matching between {0,1} clusters and {dpo,rlhf}
    alignment = max(
        np.mean(cluster_labels[labels_arr == "dpo"] == 0),
        np.mean(cluster_labels[labels_arr == "dpo"] == 1),
    )

    return {
        "silhouette_score": score,
        "dpo_silhouette": np.mean(samples[labels_arr == "dpo"]),
        "rlhf_silhouette": np.mean(samples[labels_arr == "rlhf"]),
        "cluster_labels": cluster_labels.tolist(),
        "cluster_alignment": alignment,
    }
```

### Subtasks [1/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | KMeans + silhouette | k=2 clustering, overall/per-method silhouette, alignment |

---

## A-5: Permutation Test [Complexity: 2, Budget: 2]

**Applied**: Standard NumPy (label shuffling)

### API Signatures

```python
def permutation_test(
    embeddings: np.ndarray,        # [10, 4096]
    method_labels: List[str],      # len 10
    n_permutations: int = 1000,
) -> Dict:
    """Permutation test on clustering_gap statistic."""
    ...

def compute_clustering_gap(embeddings: np.ndarray, method_labels: List[str]) -> float:
    """Within-method mean cosine sim - cross-method mean cosine sim."""
    ...
```

### Pseudo-code

```
def compute_clustering_gap(embeddings, method_labels):
    sim = cosine_similarity(embeddings)                # [10, 10]
    labels = np.array(method_labels)
    n = len(labels)
    within, cross = [], []
    for i in range(n):
        for j in range(i+1, n):
            (within if labels[i] == labels[j] else cross).append(sim[i, j])
    return np.mean(within) - np.mean(cross)

def permutation_test(embeddings, method_labels, n_permutations=1000):
    observed_gap = compute_clustering_gap(embeddings, method_labels)
    labels_arr = np.array(method_labels)
    null_dist = np.empty(n_permutations)
    for k in range(n_permutations):
        shuffled = np.random.permutation(labels_arr)
        null_dist[k] = compute_clustering_gap(embeddings, shuffled)
    p_value = np.mean(null_dist >= observed_gap)
    return {
        "observed_gap": observed_gap,
        "null_distribution": null_dist.tolist(),
        "p_value": p_value,
        "significant": p_value < 0.05,
    }
```

### Subtasks [1/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | Permutation loop | 1000 shuffles, compare observed vs null gap distribution |

---

## A-6: Effect Size (Cohen's d) [Complexity: 1, Budget: 1]

**Applied**: Standard NumPy

### API Signatures

```python
def compute_cohens_d(within_sims: List[float], cross_sims: List[float]) -> Dict:
    """Cohen's d = (mean(within) - mean(cross)) / pooled_std."""
    ...
```

### Pseudo-code

```
def compute_cohens_d(within_sims, cross_sims):
    mean_diff = np.mean(within_sims) - np.mean(cross_sims)
    pooled_std = np.sqrt((np.var(within_sims) + np.var(cross_sims)) / 2)
    d = mean_diff / pooled_std
    return {"cohens_d": d, "effect_significant": abs(d) > 0.3}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | Cohen's d | Mean diff / pooled std, threshold check |

---

## Orchestration (main entry point)

```python
def run_h_m3_pipeline(cfg: HM3Config) -> Dict:
    checkpoints = train_all_seeds(cfg)                                   # A-1
    probe_prompts = load_behavior_probes(n=1000)                         # from h-m3 data.py
    embeddings_dict = extract_all_model_embeddings(checkpoints, cfg, probe_prompts)  # A-2
    sim_results = compute_similarity_matrix(embeddings_dict)             # A-3

    model_means = np.stack([embeddings_dict[m].mean(0) for m in sim_results["model_ids"]])
    method_labels = ["dpo" if "dpo" in m else "rlhf" for m in sim_results["model_ids"]]

    clustering = analyze_clustering(model_means, method_labels)          # A-4
    perm = permutation_test(model_means, method_labels)                  # A-5
    effect = compute_cohens_d(sim_results["within_method_sims"], sim_results["cross_method_sims"])  # A-6

    metrics = {**sim_results, **clustering, **perm, **effect}
    json.dump(metrics, open("clustering_metrics.json", "w"), default=list)
    return metrics
```

---

*Generated by Logic Agent (Phase 3)*
