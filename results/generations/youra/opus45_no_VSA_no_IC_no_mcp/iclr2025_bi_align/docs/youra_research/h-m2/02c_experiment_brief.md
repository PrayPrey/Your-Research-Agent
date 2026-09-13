# Experiment Brief: H-M2 DPO Boundary Preservation

**Hypothesis ID:** h-m2
**Type:** MECHANISM
**Gate:** SHOULD_WORK
**Generated:** 2026-08-26

---

## 1. Hypothesis Statement

Under DPO training, if we directly optimize from preferences without intermediate reward model, then the policy will preserve sharper preference boundaries, because DPO's closed-form objective directly encodes preference rankings without smoothing.

## 2. Experimental Design

### 2.1 Core Approach

Train Llama-2-7B with DPO on Anthropic HH-RLHF dataset using HuggingFace TRL `DPOTrainer`. Compare preference boundary sharpness against H-M1 RLHF reward model by measuring:
1. Implicit reward margin distribution (DPO computes implicit rewards via log-ratio)
2. Decision sharpness on boundary cases (near-tie preferences)
3. Win-rate confidence on preference pairs

### 2.2 Variables

| Variable | Type | Values |
|----------|------|--------|
| Training method | Independent | DPO (direct preference optimization) |
| Dataset | Controlled | Anthropic/hh-rlhf |
| Base model | Controlled | meta-llama/Llama-2-7b-hf |
| Boundary sharpness | Dependent | Implicit reward margins, decision confidence |

### 2.3 Success Criteria

**Primary (MUST satisfy):**
- DPO implicit reward margins show higher variance than RLHF (sharper boundaries)
- Decision confidence on near-tie cases higher than RLHF baseline (>5% improvement)
- Win-rate on boundary cases (margin < 0.1 in RLHF) exceeds 55%

**Secondary:**
- β parameter (0.1) produces measurable sharpness effect
- Policy shows clear preference separation (KL divergence from reference < 1.0)

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
| Train | DPO policy training | ~160k pairs |
| Validation | Hyperparameter tuning | 10% held-out |
| Test | Boundary sharpness evaluation | 5k pairs |
| Boundary cases | Near-tie preferences (from H-M1) | ~500 pairs |

### 3.3 Preprocessing

```python
def preprocess_hh_rlhf_dpo(example):
    # DPO requires prompt/chosen/rejected format
    # HH-RLHF has dialogue format - extract prompt from common prefix
    chosen = example["chosen"]
    rejected = example["rejected"]
    
    # Find common prompt prefix
    prompt = find_common_prefix(chosen, rejected)
    
    return {
        "prompt": prompt,
        "chosen": chosen[len(prompt):],
        "rejected": rejected[len(prompt):]
    }
```

Alternative: Use pre-formatted `Trelis/hh-rlhf-dpo` from HuggingFace.

## 4. Model Configuration

### 4.1 Base Model

```python
base_model = "meta-llama/Llama-2-7b-hf"
ref_model = "meta-llama/Llama-2-7b-hf"  # DPO reference policy
```

### 4.2 DPO Training Configuration

```python
from trl import DPOConfig

config = DPOConfig(
    output_dir="./dpo_model_h-m2",
    beta=0.1,  # Temperature controlling preference sharpness
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    num_train_epochs=1,
    learning_rate=5e-7,
    max_length=512,
    max_prompt_length=256,
    bf16=True,
    gradient_checkpointing=True,
    logging_steps=50,
    eval_strategy="steps",
    eval_steps=500,
    save_strategy="steps",
    save_steps=1000,
)
```

### 4.3 PEFT Configuration

```python
from peft import LoraConfig

peft_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    task_type="CAUSAL_LM",
)
```

## 5. Boundary Sharpness Metrics

### 5.1 Implicit Reward Computation

DPO's implicit reward is computed as:

```python
def compute_dpo_implicit_reward(policy, ref_model, tokenizer, text, device):
    """
    r(x,y) = β * log(π(y|x) / π_ref(y|x))
    """
    inputs = tokenizer(text, return_tensors="pt").to(device)
    
    with torch.no_grad():
        policy_logprobs = get_sequence_logprobs(policy, inputs)
        ref_logprobs = get_sequence_logprobs(ref_model, inputs)
    
    implicit_reward = config.beta * (policy_logprobs - ref_logprobs)
    return implicit_reward


def get_sequence_logprobs(model, inputs):
    outputs = model(**inputs)
    logprobs = F.log_softmax(outputs.logits[:, :-1], dim=-1)
    token_logprobs = logprobs.gather(-1, inputs["input_ids"][:, 1:].unsqueeze(-1))
    return token_logprobs.sum()
```

### 5.2 Margin Distribution Comparison

Compare implicit reward margins (DPO) vs explicit reward margins (RLHF H-M1):

```python
def compare_margin_distributions(dpo_model, rlhf_model, ref_model, test_pairs, device):
    dpo_margins = []
    rlhf_margins = []
    
    for chosen, rejected in test_pairs:
        # DPO implicit margins
        dpo_r_chosen = compute_dpo_implicit_reward(dpo_model, ref_model, tokenizer, chosen, device)
        dpo_r_rejected = compute_dpo_implicit_reward(dpo_model, ref_model, tokenizer, rejected, device)
        dpo_margins.append(dpo_r_chosen - dpo_r_rejected)
        
        # RLHF explicit margins (from H-M1)
        rlhf_r_chosen = get_rlhf_reward(rlhf_model, tokenizer, chosen, device)
        rlhf_r_rejected = get_rlhf_reward(rlhf_model, tokenizer, rejected, device)
        rlhf_margins.append(rlhf_r_chosen - rlhf_r_rejected)
    
    return {
        "dpo_margin_std": np.std(dpo_margins),
        "rlhf_margin_std": np.std(rlhf_margins),
        "sharpness_ratio": np.std(dpo_margins) / np.std(rlhf_margins),
        "dpo_margin_mean": np.mean(dpo_margins),
        "rlhf_margin_mean": np.mean(rlhf_margins),
    }
```

**Success threshold:** sharpness_ratio > 1.0 (DPO margins more variable = sharper boundaries)

### 5.3 Boundary Case Analysis

Identify boundary cases from H-M1 (pairs where RLHF margin < 0.1) and evaluate DPO:

```python
def analyze_boundary_cases(dpo_model, ref_model, boundary_pairs, device):
    """
    Evaluate DPO on cases where RLHF showed weak preference.
    Sharper boundaries = clearer decisions on ambiguous cases.
    """
    dpo_decisions = []
    dpo_confidences = []
    
    for chosen, rejected, rlhf_margin in boundary_pairs:
        dpo_r_chosen = compute_dpo_implicit_reward(dpo_model, ref_model, tokenizer, chosen, device)
        dpo_r_rejected = compute_dpo_implicit_reward(dpo_model, ref_model, tokenizer, rejected, device)
        
        margin = dpo_r_chosen - dpo_r_rejected
        decision = margin > 0  # Correct if positive
        confidence = abs(margin)
        
        dpo_decisions.append(decision)
        dpo_confidences.append(confidence)
    
    return {
        "boundary_accuracy": np.mean(dpo_decisions),
        "mean_confidence": np.mean(dpo_confidences),
        "confident_ratio": np.mean([c > 0.1 for c in dpo_confidences]),
    }
```

**Success threshold:** 
- boundary_accuracy > 0.55 (better than RLHF on ambiguous cases)
- confident_ratio > 0.3 (DPO makes confident decisions on RLHF boundary cases)

### 5.4 Win-Rate Evaluation

Standard preference evaluation using reward/generation comparison:

```python
def compute_win_rates(policy, ref_model, eval_prompts, tokenizer, device):
    """
    Generate responses and compute win-rate via implicit reward.
    """
    wins = 0
    total = 0
    
    for prompt in eval_prompts:
        # Generate from policy
        policy_response = generate(policy, tokenizer, prompt, device)
        
        # Generate from reference
        ref_response = generate(ref_model, tokenizer, prompt, device)
        
        # Compare implicit rewards
        policy_reward = compute_dpo_implicit_reward(
            policy, ref_model, tokenizer, prompt + policy_response, device
        )
        ref_reward = compute_dpo_implicit_reward(
            policy, ref_model, tokenizer, prompt + ref_response, device
        )
        
        if policy_reward > ref_reward:
            wins += 1
        total += 1
    
    return {"win_rate": wins / total}
```

## 6. Baseline Comparison (H-M1 Reference)

From H-M1 validation results:
- RLHF reward range: [-0.47, 0.36] (0.83 units)
- RLHF margin: 0.023 (mean)
- RLHF accuracy: 53.5%

DPO must show:
- Higher margin variance (sharper preference encoding)
- Better boundary case handling
- Comparable or better accuracy

## 7. Execution Plan

### Phase 1: Data Setup (Day 1)
- Load HH-RLHF dataset in DPO format
- Identify boundary cases from H-M1 (margin < 0.1)
- Create test splits

### Phase 2: DPO Training (Days 2-3)
- Train DPO policy with TRL DPOTrainer
- Monitor: loss, reward margins, accuracies
- Save checkpoints

### Phase 3: Sharpness Evaluation (Day 4)
- Compute implicit rewards on test set
- Compare margin distributions to H-M1
- Analyze boundary cases
- Compute win-rates

### Phase 4: Analysis (Day 5)
- Statistical comparison (t-tests, effect sizes)
- Generate visualizations
- Compile validation report

## 8. Compute Requirements

| Resource | Specification |
|----------|---------------|
| GPU | 1x A100 80GB (DPO needs policy + ref model) |
| Training time | ~12-16 hours (1 epoch, LoRA) |
| Evaluation time | ~3 hours (includes generation) |
| Storage | ~80GB (two model checkpoints + dataset) |

## 9. Implementation References

### 9.1 Primary Reference

- **HuggingFace TRL DPOTrainer**
  - URL: https://huggingface.co/docs/trl/dpo_trainer
  - Key: `beta` parameter controls sharpness
  - Loss: DPO objective (Rafailov et al. 2023)

### 9.2 DPO Loss Function

```python
# From TRL DPOTrainer
def dpo_loss(policy_chosen_logps, policy_rejected_logps,
             reference_chosen_logps, reference_rejected_logps, beta):
    """
    DPO loss: -log(sigmoid(beta * (log(pi/ref)_chosen - log(pi/ref)_rejected)))
    """
    chosen_rewards = beta * (policy_chosen_logps - reference_chosen_logps)
    rejected_rewards = beta * (policy_rejected_logps - reference_rejected_logps)
    
    losses = -F.logsigmoid(chosen_rewards - rejected_rewards)
    return losses.mean()
```

### 9.3 Pre-formatted Dataset

```python
# Option: Use pre-formatted DPO dataset
from datasets import load_dataset

dataset = load_dataset("Trelis/hh-rlhf-dpo")
# Already has prompt/chosen/rejected format
```

## 10. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Memory constraints (2 models) | LoRA + gradient checkpointing + bf16 + CPU offload |
| KL divergence explosion | Monitor KL, use smaller β if needed |
| Training instability | Low learning rate (5e-7), gradient clipping |
| Reference model drift | Keep reference frozen, verify with periodic checks |

## 11. Output Artifacts

1. `dpo_model_h-m2/` - Trained DPO policy checkpoint (LoRA adapter)
2. `boundary_sharpness_metrics.json` - All computed metrics
3. `margin_comparison.png` - RLHF vs DPO margin distributions
4. `04_validation.md` - Validation report with PASS/FAIL determination

---

## Appendix A: Expected Outcomes

If hypothesis holds:
- DPO margin distribution shows higher variance than RLHF
- Clear decisions on boundary cases (confident margins)
- Sharpness ratio > 1.0

If hypothesis fails:
- DPO margins similar to or smoother than RLHF
- No improvement on boundary cases
- Document as limitation per verification plan (SHOULD_WORK gate)

## Appendix B: Connection to Main Hypothesis

H-M2 tests whether DPO preserves sharper preference boundaries than RLHF. Combined with H-M1 (RLHF smoothing validated), this establishes the mechanistic difference underlying the main hypothesis: different training objectives create different alignment signatures, potentially manifesting in differential benchmark profiles (H-M4).

---

*Generated by Phase 2C Experiment Design*
*Status: Complete*
*Date: 2026-08-26*
