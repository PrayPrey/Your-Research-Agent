# Experiment Brief: H-M1 RLHF Reward Model Smoothing

**Hypothesis ID:** h-m1
**Type:** MECHANISM
**Gate:** MUST_WORK
**Generated:** 2026-08-26

---

## 1. Hypothesis Statement

Under standard RLHF training, if we train a reward model on HH-RLHF preference pairs, then the reward model will produce smooth, interpolating reward predictions, because explicit reward model training learns a continuous approximation of discrete preference labels.

## 2. Experimental Design

### 2.1 Core Approach

Train reward model on Anthropic HH-RLHF dataset using HuggingFace TRL `RewardTrainer`. Measure reward smoothness via:
1. Gradient magnitude statistics (input-space smoothness)
2. Reward distribution analysis (output continuity)
3. Interpolation behavior on held-out preference pairs

### 2.2 Variables

| Variable | Type | Values |
|----------|------|--------|
| Training method | Independent | RLHF reward model (Bradley-Terry) |
| Dataset | Controlled | Anthropic/hh-rlhf |
| Base model | Controlled | meta-llama/Llama-2-7b-hf |
| Smoothness metrics | Dependent | Gradient norms, reward variance, interpolation error |

### 2.3 Success Criteria

**Primary (MUST satisfy):**
- Reward gradients show bounded magnitude (mean gradient norm < 10.0)
- Reward predictions form continuous distribution (not bimodal/discrete)
- Interpolation error < 0.3 on convex combinations of preference pairs

**Secondary:**
- Validation accuracy > 65% on held-out pairs
- Margin statistics show gradual preference strength encoding

## 3. Dataset Specification

### 3.1 Source

| Field | Value |
|-------|-------|
| Name | Anthropic HH-RLHF |
| Type | standard |
| HuggingFace Path | Anthropic/hh-rlhf |
| Subsets | helpful-base, helpful-online, harmless-base |

### 3.2 Splits

| Split | Purpose | Size |
|-------|---------|------|
| Train | Reward model training | ~160k pairs |
| Validation | Hyperparameter tuning | 10% held-out |
| Test | Smoothness evaluation | 5k pairs (random sample) |

### 3.3 Preprocessing

```python
def preprocess_hh_rlhf(example):
    return {
        "chosen": example["chosen"],
        "rejected": example["rejected"]
    }
```

No additional filtering needed - TRL RewardTrainer handles format.

## 4. Model Configuration

### 4.1 Base Model

```python
base_model = "meta-llama/Llama-2-7b-hf"
```

### 4.2 Reward Model Architecture

- Base: Llama-2-7B with classification head (num_labels=1)
- Output: Scalar reward per sequence
- Training: LoRA for efficiency (r=16, alpha=32)

### 4.3 Training Configuration

```python
from trl import RewardConfig

config = RewardConfig(
    output_dir="./reward_model_h-m1",
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    num_train_epochs=1,
    learning_rate=1e-4,
    max_length=512,
    center_rewards_coefficient=0.01,  # Encourage mean-zero rewards
    bf16=True,
    gradient_checkpointing=True,
    logging_steps=50,
    eval_strategy="steps",
    eval_steps=500,
    save_strategy="steps",
    save_steps=1000,
)
```

### 4.4 PEFT Configuration

```python
from peft import LoraConfig

peft_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    modules_to_save=["score"],  # Train reward head
    task_type="SEQ_CLS",
)
```

## 5. Smoothness Metrics

### 5.1 Gradient Magnitude Analysis

Compute input-space gradients to measure reward landscape smoothness:

```python
def compute_gradient_stats(model, tokenizer, test_samples, device):
    gradients = []
    for sample in test_samples:
        inputs = tokenizer(sample, return_tensors="pt", padding=True, truncation=True)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Enable gradient computation for embeddings
        embeddings = model.get_input_embeddings()(inputs["input_ids"])
        embeddings.requires_grad_(True)
        
        # Forward pass with embeddings
        outputs = model(inputs_embeds=embeddings, attention_mask=inputs["attention_mask"])
        reward = outputs.logits.squeeze()
        
        # Backward pass
        reward.backward()
        grad_norm = embeddings.grad.norm().item()
        gradients.append(grad_norm)
    
    return {
        "mean_gradient_norm": np.mean(gradients),
        "std_gradient_norm": np.std(gradients),
        "max_gradient_norm": np.max(gradients),
    }
```

**Success threshold:** mean_gradient_norm < 10.0

### 5.2 Reward Distribution Analysis

```python
def analyze_reward_distribution(model, tokenizer, test_pairs, device):
    rewards_chosen = []
    rewards_rejected = []
    
    for chosen, rejected in test_pairs:
        r_c = get_reward(model, tokenizer, chosen, device)
        r_r = get_reward(model, tokenizer, rejected, device)
        rewards_chosen.append(r_c)
        rewards_rejected.append(r_r)
    
    # Check for continuity (not discrete clustering)
    all_rewards = rewards_chosen + rewards_rejected
    
    return {
        "reward_range": max(all_rewards) - min(all_rewards),
        "reward_std": np.std(all_rewards),
        "unique_reward_ratio": len(set(np.round(all_rewards, 2))) / len(all_rewards),
        "bimodality_coefficient": compute_bimodality(all_rewards),
    }
```

**Success threshold:** 
- unique_reward_ratio > 0.5 (not collapsed to few values)
- bimodality_coefficient < 0.55 (unimodal/continuous)

### 5.3 Interpolation Behavior

Test whether reward model produces smooth interpolations:

```python
def test_interpolation(model, tokenizer, preference_pairs, device, n_steps=10):
    interpolation_errors = []
    
    for chosen, rejected in preference_pairs:
        r_chosen = get_reward(model, tokenizer, chosen, device)
        r_rejected = get_reward(model, tokenizer, rejected, device)
        
        # Expected linear interpolation
        expected = np.linspace(r_rejected, r_chosen, n_steps)
        
        # Actual interpolation via token embedding mixing
        actual = []
        for alpha in np.linspace(0, 1, n_steps):
            mixed_reward = interpolate_embeddings(
                model, tokenizer, chosen, rejected, alpha, device
            )
            actual.append(mixed_reward)
        
        # Measure deviation from linear
        error = np.mean(np.abs(np.array(actual) - expected))
        interpolation_errors.append(error)
    
    return {
        "mean_interpolation_error": np.mean(interpolation_errors),
        "max_interpolation_error": np.max(interpolation_errors),
    }
```

**Success threshold:** mean_interpolation_error < 0.3 (normalized by reward range)

## 6. Baseline Comparison

For context, also measure smoothness on:
1. **Random baseline:** Untrained model with random classification head
2. **Margin baseline:** Model trained with large margin (hard boundaries)

This establishes whether observed smoothness is a property of training vs architecture.

## 7. Execution Plan

### Phase 1: Data Setup (Day 1)
- Download HH-RLHF dataset
- Create train/val/test splits
- Verify preprocessing pipeline

### Phase 2: Training (Days 2-3)
- Train reward model with TRL RewardTrainer
- Monitor: loss, accuracy, margin, reward statistics
- Save checkpoints at 1k, 5k, 10k steps

### Phase 3: Smoothness Evaluation (Day 4)
- Compute gradient statistics on test set
- Analyze reward distribution
- Run interpolation tests
- Compare against baselines

### Phase 4: Analysis (Day 5)
- Compile metrics into validation report
- Determine PASS/FAIL against criteria
- Document findings for downstream hypotheses

## 8. Compute Requirements

| Resource | Specification |
|----------|---------------|
| GPU | 1x A100 80GB (or 2x A6000 48GB) |
| Training time | ~8-12 hours (1 epoch, LoRA) |
| Evaluation time | ~2 hours |
| Storage | ~50GB (model checkpoints + dataset cache) |

## 9. Implementation References

### 9.1 Primary Reference

- **HuggingFace TRL RewardTrainer**
  - URL: https://huggingface.co/docs/trl/reward_trainer
  - Loss: Bradley-Terry negative log-likelihood
  - Key feature: `center_rewards_coefficient` for mean-zero rewards

### 9.2 Loss Function

```python
# From TRL RewardTrainer
loss = -nn.functional.logsigmoid(rewards_chosen - rewards_rejected).mean()

# With centering regularization
if center_rewards_coefficient:
    loss += center_rewards_coefficient * ((rewards_chosen + rewards_rejected) ** 2).mean()
```

### 9.3 Key Metrics (TRL built-in)

- `accuracy`: Proportion of correct preference orderings
- `margin`: Mean(r_chosen - r_rejected)
- `mean_reward`, `min_reward`, `max_reward`: Reward distribution stats

## 10. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Training instability | Use gradient clipping (max_grad_norm=1.0), warmup steps |
| Reward collapse | Enable center_rewards_coefficient, monitor reward variance |
| Memory constraints | LoRA + gradient checkpointing + bf16 |
| Evaluation noise | Use 5k test samples for statistical significance |

## 11. Output Artifacts

1. `reward_model_h-m1/` - Trained reward model checkpoint
2. `smoothness_metrics.json` - All computed metrics
3. `04_validation.md` - Validation report with PASS/FAIL determination
4. `reward_distribution.png` - Visualization of reward landscape

---

## Appendix A: Dataset Statistics

From Anthropic HH-RLHF:
- Total pairs: ~170k
- Average chosen length: ~150 tokens
- Average rejected length: ~140 tokens
- Domain: Helpfulness + harmlessness dialogues

## Appendix B: Expected Outcomes

If hypothesis holds:
- Gradient magnitudes bounded and consistent
- Reward predictions span continuous range
- Smooth interpolation between preferences

If hypothesis fails:
- Discrete reward clustering (bimodal distribution)
- Large gradient spikes (non-smooth landscape)
- Interpolation shows step-function behavior

Failure triggers PIVOT to alternative RLHF formulation per verification plan.
