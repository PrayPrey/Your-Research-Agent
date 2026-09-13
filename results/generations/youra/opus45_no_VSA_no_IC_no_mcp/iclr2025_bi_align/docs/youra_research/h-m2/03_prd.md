# Product Requirements Document: H-M2 DPO Boundary Preservation

**Hypothesis ID:** h-m2
**Type:** MECHANISM
**Gate:** SHOULD_WORK
**Generated:** 2026-08-26

---

## 1. Executive Summary

Implement DPO (Direct Preference Optimization) training on Llama-2-7b-hf using Anthropic HH-RLHF dataset to test whether direct preference optimization preserves sharper preference boundaries than RLHF reward modeling. This builds on H-M1's validated RLHF smoothing mechanism.

## 2. Problem Statement

H-M1 demonstrated that RLHF reward models produce smooth, interpolating reward predictions. This experiment tests the mechanism hypothesis that DPO's closed-form objective directly encodes preference rankings without smoothing, resulting in sharper preference boundaries.

## 3. Goals & Success Criteria

### Primary Success Criteria (MUST satisfy)
- DPO implicit reward margin variance > RLHF margin variance (sharpness_ratio > 1.0)
- Boundary case accuracy > 55% (improvement over RLHF on ambiguous cases)
- Win-rate on boundary cases (RLHF margin < 0.1) exceeds 55%

### Secondary Criteria
- β=0.1 produces measurable sharpness effect
- KL divergence from reference < 1.0

## 4. Functional Requirements

### FR-1: Data Preparation
- Load Anthropic/hh-rlhf dataset in DPO format (prompt/chosen/rejected)
- Alternative: Use pre-formatted Trelis/hh-rlhf-dpo
- Create train/validation/test splits (~160k/16k/5k pairs)
- Extract boundary cases from H-M1 (RLHF margin < 0.1, ~500 pairs)

### FR-2: DPO Training
- Train Llama-2-7b-hf with TRL DPOTrainer
- Use LoRA (r=16, alpha=32) for efficiency
- β=0.1 temperature parameter
- Learning rate 5e-7, 1 epoch
- Gradient checkpointing + bf16 + CPU offload

### FR-3: Reference Model Management
- Load separate reference model (frozen Llama-2-7b-hf)
- Verify reference stays frozen throughout training

### FR-4: Implicit Reward Computation
- Compute r(x,y) = β * log(π(y|x) / π_ref(y|x))
- Calculate margins for all test pairs
- Compare variance to H-M1 RLHF margins

### FR-5: Boundary Sharpness Evaluation
- Load boundary cases (RLHF margin < 0.1)
- Compute DPO implicit rewards on boundary pairs
- Calculate boundary_accuracy, mean_confidence, confident_ratio

### FR-6: Win-Rate Evaluation
- Generate responses from policy and reference
- Compute win-rate via implicit reward comparison

### FR-7: Baseline Comparison
- Load H-M1 metrics: margin=0.023, accuracy=53.5%, range=0.83
- Compute sharpness_ratio = std(DPO margins) / std(RLHF margins)
- Generate margin distribution comparison plot

## 5. Non-Functional Requirements

### NFR-1: Compute
- 1x A100 80GB (DPO requires policy + reference)
- Training: 12-16 hours
- Evaluation: 3 hours

### NFR-2: Storage
- ~80GB (two model checkpoints + dataset)

### NFR-3: Memory Optimization
- LoRA adapters only
- Gradient checkpointing enabled
- bf16 precision
- CPU offload if needed

## 6. Technical Specifications

### Model Configuration
```python
base_model = "meta-llama/Llama-2-7b-hf"
ref_model = "meta-llama/Llama-2-7b-hf"  # Frozen

DPOConfig(
    beta=0.1,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    num_train_epochs=1,
    learning_rate=5e-7,
    max_length=512,
    max_prompt_length=256,
    bf16=True,
    gradient_checkpointing=True,
)

LoraConfig(
    r=16, lora_alpha=32, lora_dropout=0.05,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
)
```

## 7. Dependencies

- H-M1 validation results (boundary cases, RLHF metrics)
- HuggingFace TRL, PEFT, transformers
- PyTorch 2.0+, bitsandbytes

## 8. Output Artifacts

| Artifact | Description |
|----------|-------------|
| dpo_model_h-m2/ | LoRA adapter checkpoint |
| boundary_sharpness_metrics.json | All computed metrics |
| margin_comparison.png | RLHF vs DPO distribution |
| 04_validation.md | Validation report |

## 9. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Memory constraints | LoRA + gradient checkpointing + bf16 |
| KL divergence explosion | Monitor KL, reduce β if needed |
| Training instability | Low LR (5e-7), gradient clipping |

---

*Status: Complete*
*Phase 3 PRD Generated: 2026-08-26*
