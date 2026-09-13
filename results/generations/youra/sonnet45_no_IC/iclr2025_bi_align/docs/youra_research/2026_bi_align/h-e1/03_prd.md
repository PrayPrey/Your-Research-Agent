# Product Requirements Document (PRD)
## H-E1: Joint Training Existence & Convergence

---

**Document Type:** Product Requirements Document (PRD)  
**Hypothesis:** H-E1 (EXISTENCE)  
**Created:** 2026-07-13  
**Author:** Anonymous  
**Status:** Draft

---

## Executive Summary

### Purpose
Validate the foundational feasibility of joint DPO (Direct Preference Optimization) and attribute conditioning training for LLM alignment. This PoC experiment tests whether combining two complementary objectives (preference optimization + attribute steering) can converge successfully without catastrophic interference.

### Hypothesis Statement
Under LLM alignment settings, if we train a model using joint optimization of DPO loss and attribute-conditioning loss (L_total = 0.7·L_DPO + 0.3·L_attr), then the training will converge successfully with both losses decreasing, producing a model that achieves preference win rate ≥50% and attribute steering accuracy ≥60% on held-out test data.

### Success Criteria (MUST_WORK Gate)
1. Both L_DPO and L_attr decrease monotonically without divergence
2. Preference win rate ≥50% (better than random)
3. Attribute steering accuracy ≥60% (better than chance)
4. Gradient angles <120° (no catastrophic interference)

### Expected Outcome
**PASS Condition:** Training completes 15,000 steps with convergent losses, achieving minimal viable performance on both dimensions (win rate >50%, steering >60%).

**FAIL Condition:** Training diverges, gradient conflict (angles >120°), or either metric falls below threshold → STOP entire research pipeline (MUST_WORK gate failure).

---

## Problem Statement

### Research Context
Current LLM alignment methods optimize either:
- **AI-to-Human** (preferences): DPO achieves 57.5% win rate vs SFT
- **Human-to-AI** (control): SteerLM achieves 87% steering accuracy

No existing work demonstrates whether these objectives can be jointly optimized without interference. This experiment tests the foundational question: **Can joint training work at all?**

### Technical Challenge
Multi-objective optimization risks:
- Gradient conflict (objectives push parameters in opposite directions)
- Loss divergence (one objective dominates, other collapses)
- Training instability (oscillation, NaN gradients)

### Stakeholders
- **Primary:** Research team validating H-BD1-v1 hypothesis chain
- **Secondary:** ML practitioners interested in multi-objective LLM training

---

## Functional Requirements

### FR-1: Dataset Preparation
**Priority:** P0 (Critical)  
**Description:** Load and preprocess Anthropic HH-RLHF dataset with attribute annotations

**Acceptance Criteria:**
- Load 161k preference pairs from HuggingFace (Anthropic/hh-rlhf)
- Load 88k attribute-annotated samples from OpenAssistant/oasst1
- Map attribute labels (helpfulness, verbosity, creativity) to HH-RLHF samples
- Split: 80% train (128,800 pairs), 20% test (32,200 pairs)
- Tokenize with GPT-2 tokenizer, max_length=512, left padding
- Verify dataset accessibility before training (prevent runtime failure)

**Data Schema:**
```python
{
    "prompt": str,
    "chosen_response": str,
    "rejected_response": str,
    "attributes": {
        "helpfulness": int (1-5),
        "verbosity": int (1-5),
        "creativity": int (1-5)
    }
}
```

### FR-2: Baseline Model Setup
**Priority:** P0 (Critical)  
**Description:** Initialize GPT-2 1.5B base model and reference policy

**Acceptance Criteria:**
- Load GPT-2-XL (1.5B parameters) from HuggingFace
- Create reference policy πref via SFT on high-quality demonstrations
- Freeze reference policy (no gradient updates)
- Verify model loads without errors on target GPU (A100 40GB)

**Model Configuration:**
- Architecture: gpt2-xl
- Vocabulary: 50,257 tokens
- Layers: 48 transformer blocks
- Hidden dim: 1600
- Attention heads: 25
- Context length: 1024 tokens

### FR-3: Joint Training Implementation
**Priority:** P0 (Critical)  
**Description:** Implement joint DPO + attribute conditioning training loop

**Acceptance Criteria:**
- Implement DPO loss: -log σ(β·log(πθ(y_w|x)/πref(y_w|x)) - β·log(πθ(y_l|x)/πref(y_l|x)))
- Implement attribute conditioning loss: Cross-entropy on attribute prediction
- Combine losses: L_total = 0.7·L_DPO + 0.3·L_attr
- Log both losses separately per step (for convergence monitoring)
- Save checkpoints every 1,000 steps
- Training duration: 15,000 steps (~92 epochs over 128k samples)

**Hyperparameters:**
- Optimizer: AdamW (lr=1e-5, betas=(0.9, 0.999), weight_decay=0.01)
- Batch size: 128 pairs (4 per GPU × 32 gradient accumulation)
- DPO beta (β): 0.1
- Loss weight (α): 0.7
- LR schedule: Linear warmup (500 steps) + cosine decay
- Seed: 42 (fixed)

### FR-4: Gradient Monitoring
**Priority:** P1 (High)  
**Description:** Monitor gradient angles to detect objective conflict

**Acceptance Criteria:**
- Compute gradient vectors for L_DPO and L_attr separately
- Calculate angle θ = arccos(⟨∇L_DPO, ∇L_attr⟩ / (||∇L_DPO|| · ||∇L_attr||))
- Log gradient angle every 100 steps
- Alert if angle >120° (catastrophic interference threshold)
- Store angle distribution for post-training analysis

### FR-5: Preference Evaluation
**Priority:** P0 (Critical)  
**Description:** Evaluate AI-to-Human alignment via preference win rate

**Acceptance Criteria:**
- Generate responses for 1,000 held-out prompts from test set
- Compare joint model outputs vs DPO baseline using GPT-4 judge
- Calculate win rate: % of joint model responses preferred over baseline
- Threshold: ≥50% (better than random)
- Expected baseline: 57.5% (DPO standalone)

**Evaluation Protocol:**
- Judge: GPT-4 (via OpenAI API)
- Prompt template: "Which response is more helpful and harmless? A or B?"
- Randomize order to avoid position bias
- Store per-sample judgments for error analysis

### FR-6: Attribute Steering Evaluation
**Priority:** P0 (Critical)  
**Description:** Evaluate Human-to-AI control via steering accuracy

**Acceptance Criteria:**
- Test 6 attribute combinations × 100 prompts = 600 evaluations
- For each test: Request specific attribute level (e.g., helpfulness=4)
- Measure predicted attribute level using pre-trained attribute predictor
- Calculate accuracy: % within ±0.5 of target (on 1-5 scale)
- Threshold: ≥60% (better than chance 20%)
- Expected baseline: 87% (SteerLM standalone)

**Attribute Combinations:**
- (helpfulness=5, verbosity=3, creativity=3)
- (helpfulness=3, verbosity=5, creativity=1)
- (helpfulness=4, verbosity=2, creativity=5)
- (helpfulness=2, verbosity=4, creativity=4)
- (helpfulness=5, verbosity=1, creativity=2)
- (helpfulness=1, verbosity=3, creativity=5)

### FR-7: Visualization & Reporting
**Priority:** P1 (High)  
**Description:** Generate required figures and experiment report

**Acceptance Criteria:**
- **Mandatory Figure:** Gate metrics comparison (target vs actual bar chart)
- **Training Loss Curves:** Dual y-axis plot (L_DPO, L_attr vs steps)
- **Gradient Angle Distribution:** Histogram with 120° threshold line
- **Attribute Steering Heatmap:** 3 attributes × 5 levels accuracy matrix
- **Preference Win Rate Scatter:** Per-sample win probability distribution
- All figures saved to `{hypothesis_folder}/figures/`
- Generate `04_validation.md` with pass/fail determination

---

## Non-Functional Requirements

### NFR-1: Performance
- Training completion: 3-5 days on single NVIDIA A100 40GB
- Memory usage: <35GB GPU memory (leave headroom for batch processing)
- Checkpoint size: <6GB per checkpoint (1.5B parameters × 2 bytes/param)

### NFR-2: Reproducibility
- Fixed seed: 42
- Deterministic operations where possible (CUDA determinism for training)
- Log all hyperparameters to config file
- Save dataset preprocessing steps
- Version control: PyTorch, Transformers, Datasets library versions

### NFR-3: Error Handling
- Pre-flight dataset accessibility check (fail fast if HuggingFace unavailable)
- Gradient NaN detection → stop training immediately
- GPU OOM handling → reduce batch size and retry
- Checkpoint corruption detection → revert to previous checkpoint

### NFR-4: Monitoring
- Real-time loss logging (both L_DPO and L_attr)
- Gradient statistics (mean, std, max norm)
- Training speed (samples/sec, estimated time remaining)
- GPU utilization tracking

---

## Dependencies & Constraints

### External Dependencies
- **Datasets:** Anthropic/hh-rlhf, OpenAssistant/oasst1 (HuggingFace)
- **Model:** gpt2-xl (HuggingFace Transformers)
- **Judge:** GPT-4 API access (OpenAI)
- **Hardware:** 1× NVIDIA A100 40GB GPU

### Technical Constraints
- No custom CUDA kernels (use standard PyTorch operations)
- No distributed training (single GPU experiment)
- No hyperparameter tuning (fixed values from Phase 2C)

### Assumptions
- HH-RLHF dataset format matches DPO training requirements
- GPT-4 judge provides consistent preference rankings
- Attribute predictor pre-trained on OpenAssistant is available
- Reference policy πref can be obtained via short SFT run

---

## Data Requirements

### Input Data
1. **Anthropic HH-RLHF**
   - Source: `datasets.load_dataset("Anthropic/hh-rlhf")`
   - Format: Preference pairs (prompt, chosen, rejected)
   - Size: 161,000 samples
   - License: MIT (verified)

2. **OpenAssistant/oasst1**
   - Source: `datasets.load_dataset("OpenAssistant/oasst1")`
   - Format: Conversations with attribute labels
   - Size: 88,000 samples
   - License: Apache 2.0

### Output Data
1. **Model Checkpoints**
   - Path: `{hypothesis_folder}/checkpoints/step_{N}.pt`
   - Frequency: Every 1,000 steps
   - Total: 15 checkpoints

2. **Training Logs**
   - Path: `{hypothesis_folder}/logs/training.jsonl`
   - Fields: step, loss_dpo, loss_attr, loss_total, gradient_angle, lr

3. **Evaluation Results**
   - Path: `{hypothesis_folder}/results/evaluation.json`
   - Fields: win_rate, steering_accuracy, per_sample_results

4. **Validation Report**
   - Path: `{hypothesis_folder}/04_validation.md`
   - Content: Pass/fail determination, gate metrics, figures

---

## Environment Requirements

### Hardware
- GPU: 1× NVIDIA A100 40GB (or equivalent >32GB VRAM)
- CPU: 16+ cores (for data loading parallelism)
- RAM: 64GB system memory
- Storage: 100GB free space (checkpoints + datasets)

### Software
- Python: 3.10+
- PyTorch: 2.0+
- Transformers: 4.30+
- Datasets: 2.12+
- CUDA: 11.8+

### Development Environment
- Version control: Git
- Experiment tracking: Local logs (no external tracking service)
- Code location: `{hypothesis_folder}/code/`

---

## Success Metrics & Validation

### Gate Metrics (MUST_WORK)
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Training Convergence | Both losses decrease | TBD | ⏳ |
| Preference Win Rate | ≥50% | TBD | ⏳ |
| Steering Accuracy | ≥60% | TBD | ⏳ |
| Gradient Angle | <120° | TBD | ⏳ |

**PASS Condition:** ALL four metrics meet targets  
**FAIL Condition:** ANY metric fails → STOP workflow (MUST_WORK gate)

### Monitoring Metrics
- L_DPO convergence trend (monotonic decrease expected)
- L_attr convergence trend (monotonic decrease expected)
- Gradient norm statistics (detect explosion/vanishing)
- Training stability (no NaN/Inf losses)

---

## Out of Scope

### Explicitly NOT Included
- Hyperparameter tuning (use fixed values from Phase 2C)
- Multi-seed runs (single seed PoC only)
- Distributed training / multi-GPU
- Model compression or quantization
- Deployment infrastructure
- Comparison with sequential training baseline (deferred to H-M3)
- Disentanglement analysis (deferred to H-M2)
- Representation learning analysis (deferred to H-M1)

---

## Appendix: Reference Information

### Baseline Performance (from Phase 2B)
- **DPO-only:** 57.5% win rate, 0% steering
- **SteerLM-only:** 0% win rate, 87% steering
- **Sequential (DPO→Attr):** Unknown (to be established in H-M3)

### Mathematical Specifications

**DPO Loss:**
```
L_DPO = -E[(x,y_w,y_l)~D] [log σ(β·log(πθ(y_w|x)/πref(y_w|x)) - β·log(πθ(y_l|x)/πref(y_l|x)))]
```

**Attribute Loss:**
```
L_attr = CrossEntropy(f_attr(h_final), A_target)
where h_final = final hidden state, f_attr = attribute prediction head
```

**Joint Loss:**
```
L_total = α·L_DPO + (1-α)·L_attr
where α = 0.7
```

### Key References
1. Rafailov et al. 2023 - "Direct Preference Optimization"
2. Dong et al. 2023 - "SteerLM: Attribute Conditioned SFT"
3. Bai et al. 2022 - "Training a Helpful and Harmless Assistant with RLHF"

---

**Document Status:** Ready for Phase 3 Architecture Design  
**Next Step:** Architecture Agent (Step 3)
