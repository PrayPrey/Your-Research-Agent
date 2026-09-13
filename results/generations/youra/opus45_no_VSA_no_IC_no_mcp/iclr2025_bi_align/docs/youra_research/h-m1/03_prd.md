# Product Requirements Document: H-M1 RLHF Reward Model Smoothing

**Hypothesis ID:** h-m1
**Type:** MECHANISM
**Gate:** MUST_WORK
**Generated:** 2026-08-26
**Phase:** 3 - Implementation Planning

---

## 1. Executive Summary

This experiment validates the MECHANISM hypothesis that RLHF reward model training produces smooth, interpolating reward predictions. We train a reward model on Anthropic HH-RLHF using TRL RewardTrainer and measure smoothness via gradient magnitudes, reward distribution continuity, and interpolation behavior.

**Success Criteria:**
- Mean gradient norm < 10.0
- Reward distribution is continuous (not bimodal)
- Interpolation error < 0.3

---

## 2. Problem Statement

Standard RLHF reward models are trained with Bradley-Terry loss on discrete preference pairs. The hypothesis claims this training produces smooth reward landscapes that interpolate between preferences, rather than discrete classifiers. Validating this mechanism is prerequisite for understanding RLHF behavior in downstream hypotheses.

---

## 3. Functional Requirements

### FR-1: Data Pipeline
- **FR-1.1:** Load Anthropic/hh-rlhf dataset via HuggingFace datasets
- **FR-1.2:** Create train/validation/test splits (90%/5%/5%)
- **FR-1.3:** Preprocess into chosen/rejected pairs for TRL RewardTrainer
- **FR-1.4:** Sample 5,000 test pairs for smoothness evaluation

### FR-2: Reward Model Training
- **FR-2.1:** Initialize Llama-2-7B with LoRA (r=16, alpha=32)
- **FR-2.2:** Add scalar reward head (num_labels=1)
- **FR-2.3:** Train with TRL RewardConfig:
  - batch_size=4, gradient_accumulation=4
  - learning_rate=1e-4, 1 epoch
  - center_rewards_coefficient=0.01
- **FR-2.4:** Save checkpoints at 1k, 5k, 10k steps
- **FR-2.5:** Track training metrics: loss, accuracy, margin

### FR-3: Gradient Smoothness Analysis
- **FR-3.1:** Compute input-space gradient norms for test samples
- **FR-3.2:** Calculate mean, std, max gradient statistics
- **FR-3.3:** Verify mean_gradient_norm < 10.0

### FR-4: Reward Distribution Analysis
- **FR-4.1:** Score all test pairs (chosen and rejected)
- **FR-4.2:** Compute reward range, std, unique ratio
- **FR-4.3:** Calculate bimodality coefficient
- **FR-4.4:** Verify continuous distribution (bimodality < 0.55)

### FR-5: Interpolation Testing
- **FR-5.1:** Implement embedding-space interpolation
- **FR-5.2:** Test interpolation on 500 preference pairs
- **FR-5.3:** Measure deviation from linear interpolation
- **FR-5.4:** Verify mean_interpolation_error < 0.3

### FR-6: Baseline Comparisons
- **FR-6.1:** Random baseline (untrained model)
- **FR-6.2:** Measure same smoothness metrics on baselines

### FR-7: Output Artifacts
- **FR-7.1:** Save trained reward model checkpoint
- **FR-7.2:** Generate smoothness_metrics.json
- **FR-7.3:** Create reward_distribution.png visualization
- **FR-7.4:** Produce 04_validation.md report

---

## 4. Non-Functional Requirements

### NFR-1: Compute
- Single A100 80GB or 2x A6000 48GB
- Training time: ~8-12 hours
- Evaluation time: ~2 hours

### NFR-2: Memory
- LoRA + gradient checkpointing + bf16 for memory efficiency
- Max sequence length: 512 tokens

### NFR-3: Storage
- ~50GB for checkpoints and dataset cache

### NFR-4: Reproducibility
- Fixed random seeds
- Deterministic training where possible
- All hyperparameters documented in config

---

## 5. Data Specifications

| Dataset | Source | Size | Purpose |
|---------|--------|------|---------|
| Anthropic HH-RLHF | HuggingFace | ~170k pairs | Training |
| Test split | 5% of above | ~8.5k pairs | Evaluation |
| Sampled test | Random sample | 5k pairs | Smoothness metrics |

---

## 6. Success Criteria

### Primary (MUST satisfy for PASS):
| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| mean_gradient_norm | < 10.0 | Bounded gradients indicate smooth landscape |
| bimodality_coefficient | < 0.55 | Unimodal distribution indicates continuity |
| mean_interpolation_error | < 0.3 | Smooth interpolation between preferences |

### Secondary (informational):
| Metric | Expected | Purpose |
|--------|----------|---------|
| validation_accuracy | > 65% | Model learns preferences |
| reward_std | > 0.5 | Rewards are differentiated |
| unique_reward_ratio | > 0.5 | Not collapsed to few values |

---

## 7. Dependencies

### Upstream:
- h-e1 (EXISTENCE): Validated distinct alignment dimensions

### Libraries:
- transformers >= 4.36.0
- trl >= 0.7.0
- peft >= 0.7.0
- torch >= 2.0
- datasets >= 2.14.0

### Models:
- meta-llama/Llama-2-7b-hf (requires HF access)

---

## 8. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Training instability | Medium | High | Gradient clipping, warmup, monitoring |
| Reward collapse | Low | High | center_rewards_coefficient regularization |
| Memory OOM | Medium | Medium | LoRA + gradient checkpointing |
| Discrete rewards | Low | High | Would falsify hypothesis (valid outcome) |

---

## 9. Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Data Setup | 2 hours | Preprocessed dataset |
| Training | 8-12 hours | Trained reward model |
| Evaluation | 2 hours | Smoothness metrics |
| Analysis | 2 hours | Validation report |
| **Total** | **~16 hours** | Complete validation |
