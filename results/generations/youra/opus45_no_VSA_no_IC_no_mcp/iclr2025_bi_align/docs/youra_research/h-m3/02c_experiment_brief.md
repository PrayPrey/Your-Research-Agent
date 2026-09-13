# Experiment Brief: H-M3 Optimization Landscape Attractors

**Hypothesis ID:** h-m3
**Type:** MECHANISM
**Gate:** SHOULD_WORK
**Generated:** 2026-08-26

---

## 1. Hypothesis Statement

Under alignment training, if RLHF produces smooth and DPO produces sharp optimization landscapes, then models will converge to different stable configurations (attractors), because landscape geometry determines convergence behavior.

## 2. Experimental Design

### 2.1 Core Approach

Train multiple seeds of both RLHF and DPO models on identical data, then analyze final model behavior similarity. If methods converge to different attractors, within-method model similarity should exceed cross-method similarity. This bridges H-M1/H-M2 mechanistic findings to observable behavioral outcomes.

### 2.2 Variables

| Variable | Type | Values |
|----------|------|--------|
| Training method | Independent | DPO, RLHF |
| Random seed | Independent | 5 seeds per method |
| Dataset | Controlled | Anthropic/hh-rlhf |
| Base model | Controlled | meta-llama/Llama-2-7b-hf |
| Behavior clustering | Dependent | Within/cross-method similarity |

### 2.3 Success Criteria

**Primary (MUST satisfy):**
- Within-method similarity > cross-method similarity (Cohen's d > 0.3)
- Models cluster by training method, not by random seed
- Clear behavioral signature separation between DPO and RLHF groups

**Secondary:**
- Response embedding similarity aligns with method grouping
- Generation perplexity patterns distinguish methods

## 3. Dataset Specification

### 3.1 Source

| Field | Value |
|-------|-------|
| Name | Anthropic HH-RLHF |
| Type | standard |
| HuggingFace Path | Anthropic/hh-rlhf |
| Usage | Training all seeds, evaluation probes |

### 3.2 Splits

| Split | Purpose | Size |
|-------|---------|------|
| Train | Multi-seed training (shared across seeds) | ~160k pairs |
| Validation | Consistent hyperparameter selection | 10% held-out |
| Behavior probe | Consistent prompts for behavior extraction | 1000 prompts |
| Response eval | Generation consistency measurement | 500 prompts |

### 3.3 Behavior Probe Set

```python
def create_behavior_probe_set(dataset, n_probes=1000):
    """
    Select consistent prompts for behavior extraction across all seeds.
    Cover diverse dialogue types from HH-RLHF.
    """
    probes = []
    
    # Sample from different subsets
    for subset in ["helpful-base", "harmless-base"]:
        subset_data = dataset[subset]
        sampled = subset_data.shuffle(seed=42).select(range(n_probes // 2))
        
        for example in sampled:
            prompt = extract_prompt(example["chosen"])
            probes.append({
                "prompt": prompt,
                "subset": subset,
                "original_idx": example.get("idx", None)
            })
    
    return probes
```

## 4. Model Configuration

### 4.1 Multi-Seed Training Protocol

```python
SEEDS = [42, 137, 256, 512, 1024]  # 5 seeds per method

def train_multi_seed(method, seeds):
    models = {}
    for seed in seeds:
        set_seed(seed)
        
        if method == "dpo":
            model = train_dpo_model(seed)  # From H-M2
        else:  # rlhf
            model = train_rlhf_model(seed)  # From H-M1
        
        models[f"{method}_seed{seed}"] = model
    return models
```

### 4.2 Training Configuration (Consistent Across Seeds)

```python
# DPO config (from H-M2)
dpo_config = DPOConfig(
    output_dir="./h-m3_dpo_{seed}",
    beta=0.1,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    num_train_epochs=1,
    learning_rate=5e-7,
    max_length=512,
    bf16=True,
    gradient_checkpointing=True,
)

# RLHF config (from H-M1)
rlhf_config = PPOConfig(
    output_dir="./h-m3_rlhf_{seed}",
    batch_size=32,
    learning_rate=1.41e-5,
    ppo_epochs=4,
    mini_batch_size=4,
)
```

### 4.3 PEFT Configuration (Identical for Fair Comparison)

```python
peft_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    task_type="CAUSAL_LM",
)
```

## 5. Attractor Analysis Metrics

### 5.1 Response Embedding Similarity

Extract hidden state representations and measure clustering:

```python
def compute_response_embeddings(model, prompts, tokenizer, device):
    """
    Extract last-layer hidden states as behavior embeddings.
    """
    embeddings = []
    
    for prompt in prompts:
        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        
        with torch.no_grad():
            outputs = model(**inputs, output_hidden_states=True)
            # Use mean of last layer hidden states
            last_hidden = outputs.hidden_states[-1]
            embedding = last_hidden.mean(dim=1).squeeze()
        
        embeddings.append(embedding.cpu().numpy())
    
    return np.stack(embeddings)


def analyze_method_clustering(all_embeddings, method_labels, seed_labels):
    """
    Compute within-method vs cross-method similarity.
    """
    from scipy.spatial.distance import cosine
    from sklearn.metrics import silhouette_score
    
    n_models = len(all_embeddings)
    similarity_matrix = np.zeros((n_models, n_models))
    
    for i in range(n_models):
        for j in range(n_models):
            similarity_matrix[i, j] = 1 - cosine(
                all_embeddings[i].flatten(),
                all_embeddings[j].flatten()
            )
    
    # Within-method similarities
    within_dpo = []
    within_rlhf = []
    cross_method = []
    
    for i in range(n_models):
        for j in range(i+1, n_models):
            sim = similarity_matrix[i, j]
            if method_labels[i] == method_labels[j]:
                if method_labels[i] == "dpo":
                    within_dpo.append(sim)
                else:
                    within_rlhf.append(sim)
            else:
                cross_method.append(sim)
    
    # Silhouette score for method clustering
    silhouette = silhouette_score(
        np.vstack(all_embeddings),
        method_labels
    )
    
    return {
        "within_dpo_mean": np.mean(within_dpo),
        "within_rlhf_mean": np.mean(within_rlhf),
        "cross_method_mean": np.mean(cross_method),
        "within_method_mean": np.mean(within_dpo + within_rlhf),
        "clustering_gap": np.mean(within_dpo + within_rlhf) - np.mean(cross_method),
        "silhouette_score": silhouette,
    }
```

**Success threshold:**
- clustering_gap > 0.05 (within-method similarity exceeds cross-method)
- silhouette_score > 0.1 (meaningful method-based clustering)

### 5.2 Generation Distribution Comparison

Compare response generation patterns across seeds and methods:

```python
def compare_generation_distributions(models, prompts, tokenizer, device):
    """
    Generate responses from all models on same prompts.
    Measure consistency within vs across methods.
    """
    responses = {model_id: [] for model_id in models}
    
    for prompt in prompts:
        for model_id, model in models.items():
            response = generate_response(model, tokenizer, prompt, device)
            responses[model_id].append(response)
    
    # Compute response similarity using BLEU or semantic similarity
    return compute_response_similarity_matrix(responses, tokenizer)


def compute_response_consistency(responses, method_labels):
    """
    Measure response consistency within methods vs across methods.
    """
    # Use sentence embeddings for semantic similarity
    from sentence_transformers import SentenceTransformer
    
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    per_prompt_results = []
    
    for prompt_idx in range(len(list(responses.values())[0])):
        prompt_responses = {
            model_id: responses[model_id][prompt_idx]
            for model_id in responses
        }
        
        # Embed all responses
        embeddings = embedder.encode(list(prompt_responses.values()))
        
        # Compute within/cross similarities
        within_similarities = []
        cross_similarities = []
        
        model_ids = list(prompt_responses.keys())
        for i in range(len(model_ids)):
            for j in range(i+1, len(model_ids)):
                sim = 1 - cosine(embeddings[i], embeddings[j])
                
                if method_labels[model_ids[i]] == method_labels[model_ids[j]]:
                    within_similarities.append(sim)
                else:
                    cross_similarities.append(sim)
        
        per_prompt_results.append({
            "within_mean": np.mean(within_similarities),
            "cross_mean": np.mean(cross_similarities),
        })
    
    return {
        "response_within_mean": np.mean([r["within_mean"] for r in per_prompt_results]),
        "response_cross_mean": np.mean([r["cross_mean"] for r in per_prompt_results]),
        "response_consistency_gap": (
            np.mean([r["within_mean"] for r in per_prompt_results]) -
            np.mean([r["cross_mean"] for r in per_prompt_results])
        ),
    }
```

### 5.3 Implicit Reward Landscape Analysis

Analyze reward landscape geometry differences:

```python
def analyze_reward_landscapes(models, ref_model, prompts, tokenizer, device):
    """
    Compare reward landscape characteristics across methods.
    """
    landscapes = {}
    
    for model_id, model in models.items():
        rewards = []
        gradients = []
        
        for prompt in prompts:
            inputs = tokenizer(prompt, return_tensors="pt").to(device)
            
            # Compute reward
            if "dpo" in model_id:
                reward = compute_dpo_implicit_reward(model, ref_model, tokenizer, prompt, device)
            else:
                reward = get_rlhf_reward(model, tokenizer, prompt, device)
            
            rewards.append(reward.item())
        
        landscapes[model_id] = {
            "reward_mean": np.mean(rewards),
            "reward_std": np.std(rewards),
            "reward_range": np.max(rewards) - np.min(rewards),
        }
    
    # Compare landscape statistics by method
    dpo_stats = [v for k, v in landscapes.items() if "dpo" in k]
    rlhf_stats = [v for k, v in landscapes.items() if "rlhf" in k]
    
    return {
        "dpo_reward_std_mean": np.mean([s["reward_std"] for s in dpo_stats]),
        "rlhf_reward_std_mean": np.mean([s["reward_std"] for s in rlhf_stats]),
        "landscape_sharpness_gap": (
            np.mean([s["reward_std"] for s in dpo_stats]) -
            np.mean([s["reward_std"] for s in rlhf_stats])
        ),
    }
```

### 5.4 Convergence Pattern Analysis

Analyze training trajectory patterns:

```python
def analyze_convergence_patterns(training_logs_dpo, training_logs_rlhf):
    """
    Compare convergence characteristics between methods.
    """
    results = {
        "dpo_seeds": [],
        "rlhf_seeds": [],
    }
    
    for log in training_logs_dpo:
        results["dpo_seeds"].append({
            "final_loss": log["loss"][-1],
            "convergence_step": find_convergence_step(log["loss"]),
            "loss_variance_final": np.var(log["loss"][-100:]),
        })
    
    for log in training_logs_rlhf:
        results["rlhf_seeds"].append({
            "final_loss": log["loss"][-1],
            "convergence_step": find_convergence_step(log["loss"]),
            "loss_variance_final": np.var(log["loss"][-100:]),
        })
    
    # Compare final loss clustering
    dpo_final = [s["final_loss"] for s in results["dpo_seeds"]]
    rlhf_final = [s["final_loss"] for s in results["rlhf_seeds"]]
    
    return {
        "dpo_loss_within_std": np.std(dpo_final),
        "rlhf_loss_within_std": np.std(rlhf_final),
        "cross_method_loss_gap": abs(np.mean(dpo_final) - np.mean(rlhf_final)),
        "convergence_pattern_distinct": np.mean(dpo_final) != np.mean(rlhf_final),
    }
```

## 6. Statistical Analysis

### 6.1 Clustering Validation

```python
def validate_method_clustering(embeddings, method_labels):
    """
    Statistical validation of method-based clustering.
    """
    from sklearn.cluster import KMeans
    from scipy.stats import ttest_ind
    
    # K-means with k=2 (expecting two clusters by method)
    kmeans = KMeans(n_clusters=2, random_state=42)
    cluster_labels = kmeans.fit_predict(embeddings)
    
    # Check if clusters align with method labels
    alignment = compute_cluster_alignment(cluster_labels, method_labels)
    
    # Permutation test for significance
    observed_gap = compute_clustering_gap(embeddings, method_labels)
    null_distribution = []
    
    for _ in range(1000):
        shuffled_labels = np.random.permutation(method_labels)
        null_gap = compute_clustering_gap(embeddings, shuffled_labels)
        null_distribution.append(null_gap)
    
    p_value = np.mean(np.array(null_distribution) >= observed_gap)
    
    return {
        "cluster_alignment": alignment,
        "clustering_gap": observed_gap,
        "p_value": p_value,
        "significant": p_value < 0.05,
    }
```

### 6.2 Effect Size Computation

```python
def compute_effect_sizes(within_similarities, cross_similarities):
    """
    Compute Cohen's d for within vs cross-method similarity difference.
    """
    mean_diff = np.mean(within_similarities) - np.mean(cross_similarities)
    pooled_std = np.sqrt(
        (np.var(within_similarities) + np.var(cross_similarities)) / 2
    )
    
    cohens_d = mean_diff / pooled_std
    
    return {
        "cohens_d": cohens_d,
        "effect_significant": abs(cohens_d) > 0.3,
    }
```

## 7. Baseline Comparison (H-M1/H-M2 Reference)

From validated H-M1 and H-M2 results:
- H-M1: RLHF produces smooth reward landscapes
- H-M2: DPO produces sharper preference boundaries (sharpness_ratio > 1.0)

H-M3 must show:
- These mechanistic differences translate to distinct behavioral attractors
- Models cluster by method, not random variation
- Within-method behavioral consistency exceeds cross-method

## 8. Execution Plan

### Phase 1: Multi-Seed Training (Days 1-5)
- Train 5 DPO seeds (reuse H-M2 config, vary seed)
- Train 5 RLHF seeds (reuse H-M1 config, vary seed)
- Log training trajectories for convergence analysis

### Phase 2: Behavior Extraction (Day 6)
- Generate responses on 1000 behavior probe prompts
- Extract hidden state embeddings
- Compute response similarity matrices

### Phase 3: Clustering Analysis (Day 7)
- Compute within/cross-method similarities
- Run K-means and silhouette analysis
- Statistical validation (permutation tests)

### Phase 4: Reporting (Day 8)
- Compile metrics
- Generate visualizations (clustering plots, similarity heatmaps)
- Write validation report

## 9. Compute Requirements

| Resource | Specification |
|----------|---------------|
| GPU | 1x A100 80GB (sequential training) |
| Training time | ~5x (DPO + RLHF) hours × 5 seeds = ~50 hours total |
| Evaluation time | ~10 hours (embedding extraction + generation) |
| Storage | ~400GB (10 model checkpoints + logs) |

**Optimization:** Can parallelize seed training across multiple GPUs if available.

## 10. Implementation References

### 10.1 Multi-Seed Training

```python
# Standard seed setting for reproducibility
def set_seed(seed):
    import random
    import numpy as np
    import torch
    
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
```

### 10.2 Silhouette Analysis

```python
from sklearn.metrics import silhouette_score, silhouette_samples

def analyze_clusters(embeddings, method_labels):
    score = silhouette_score(embeddings, method_labels)
    samples = silhouette_samples(embeddings, method_labels)
    return {
        "silhouette_score": score,
        "dpo_silhouette": np.mean(samples[method_labels == "dpo"]),
        "rlhf_silhouette": np.mean(samples[method_labels == "rlhf"]),
    }
```

### 10.3 Visualization

```python
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

def visualize_attractors(embeddings, method_labels, seed_labels):
    tsne = TSNE(n_components=2, random_state=42)
    reduced = tsne.fit_transform(embeddings)
    
    plt.figure(figsize=(10, 8))
    
    for method in ["dpo", "rlhf"]:
        mask = method_labels == method
        plt.scatter(
            reduced[mask, 0], reduced[mask, 1],
            label=method.upper(),
            alpha=0.7, s=100
        )
    
    plt.legend()
    plt.title("Model Behavior Attractors by Training Method")
    plt.savefig("attractor_visualization.png")
```

## 11. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Training variance too high | Increase seeds (5 → 8) if needed |
| Embedding extraction memory | Batch processing, CPU offload |
| Clustering noise | Use robust metrics (silhouette), permutation tests |
| Confounding by seed | Ensure identical init for fair comparison |

## 12. Output Artifacts

1. `h-m3_models/` - 10 trained model checkpoints (5 DPO, 5 RLHF)
2. `behavior_embeddings.npy` - Extracted embeddings per model
3. `clustering_metrics.json` - All clustering and similarity metrics
4. `attractor_visualization.png` - t-SNE visualization
5. `04_validation.md` - Validation report with PASS/FAIL determination

---

## Appendix A: Expected Outcomes

If hypothesis holds:
- Clear method-based clustering (silhouette > 0.1)
- Within-method similarity > cross-method similarity (gap > 0.05)
- t-SNE shows two distinct clusters
- p-value < 0.05 on permutation test

If hypothesis fails:
- Models cluster by seed, not method
- No significant similarity gap
- Document as limitation per verification plan (SHOULD_WORK gate)

## Appendix B: Connection to Main Hypothesis

H-M3 bridges mechanistic findings (H-M1 smoothing, H-M2 sharpness) to behavioral outcomes. If different optimization landscapes lead to different attractors, this explains why methods might produce different benchmark profiles (H-M4). The attractor hypothesis is the causal link from "different training dynamics" to "different final behaviors."

---

*Generated by Phase 2C Experiment Design*
*Status: Complete*
*Date: 2026-08-26*
