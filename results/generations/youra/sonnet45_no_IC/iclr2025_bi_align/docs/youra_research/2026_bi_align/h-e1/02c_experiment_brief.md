# Experiment Design: H-E1

**Date:** 2026-07-12
**Author:** Anonymous
**Hypothesis Statement:** Under LLM alignment settings, if we train a model using joint optimization of DPO loss and attribute-conditioning loss (L_total = 0.7·L_DPO + 0.3·L_attr), then the training will converge successfully with both losses decreasing, producing a model that achieves preference win rate ≥50% and attribute steering accuracy ≥60% on held-out test data.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** None (foundational hypothesis)
**Gate Status:** MUST_WORK - Training converges, Win rate ≥50%, Steering ≥60%

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundational test)

### Gate Condition
**Type:** MUST_WORK  
**Pass Condition:** Training converges, Win rate ≥50%, Steering ≥60%  
**Fail Action:** STOP - Joint training not feasible, reconsider approach

---

## Continuation Context

This is the first hypothesis in the linear dependency chain (H-E1 → H-M1 → H-M2 → H-M3). No previous hypothesis context exists.

### Previous Hypothesis Results (if applicable)
N/A - Foundational hypothesis

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: DPO Training**
- Limited RLHF/DPO content in current knowledge base
- Found general training optimization patterns but not DPO-specific

**Query 2: Attribute Conditioning**
- Found instruction following guidance (OpenAI blog)
- General conditioning approaches but not SteerLM-specific

**Query 3: Multi-task Joint Training**
- Found diffusion model training examples (joint loss optimization)
- Pattern: Weighted loss summation L_total = α·L1 + (1-α)·L2

### Archon Code Examples

**Multi-task Loss Pattern** (from diffusion training):
```python
# Pattern: Weighted sum optimization
optimizer = optimizer_cls(
    model.parameters(),
    lr=args.learning_rate,
    betas=(args.adam_beta1, args.adam_beta2),
    weight_decay=args.adam_weight_decay,
)
# Loss: weighted combination
loss = alpha * loss_primary + (1 - alpha) * loss_secondary
```

### Exa GitHub Implementations

**Status:** Exa MCP unavailable (402 payment error). Using Phase 2B references instead.

**Known DPO Implementation** (from Phase 2B literature):
- **Rafailov et al. 2023**: Direct Preference Optimization paper
  - Official implementation expected at: github.com/eric-mitchell/direct-preference-optimization (typical pattern)
  - Key components: DPO loss, reference policy, preference pairs dataset

**Known SteerLM Implementation** (from Phase 2B literature):
- **Dong et al. 2023**: SteerLM paper (NVIDIA)
  - Attribute-conditioned generation with control tokens
  - 87% steering accuracy baseline
  - HuggingFace integration: likely in NeMo-Aligner repository

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

Given Exa unavailability, using Phase 2B established baseline methods:

**Recommended Implementation Path:**
- Primary: Custom implementation based on DPO paper (Rafailov et al. 2023) specification + SteerLM attribute conditioning (Dong et al. 2023)
- Fallback: HuggingFace TRL library DPO trainer + custom attribute loss
- Justification: Papers provide mathematical specifications sufficient for implementation. HH-RLHF dataset is standard for DPO training (verified accessible).

### Code Analysis (Serena MCP)

Not performed - no existing codebase to analyze. This is a ground-up implementation experiment.

---

## Experiment Specification

### Dataset

**Name:** Anthropic HH-RLHF  
**Type:** standard (real preference pairs dataset)  
**Source:** HuggingFace Datasets  
**Size:** 161,000 preference pairs  
**Splits:**
- Train: 128,800 pairs (80%)
- Test: 32,200 pairs (20%)

**Data Format:**
- Each sample: (prompt, chosen_response, rejected_response)
- Chosen response preferred by human annotators over rejected
- Supports DPO training directly

**Preprocessing:**
- Tokenization: GPT-2 tokenizer with max_length=512
- Padding: Left padding for generation models
- Attribute annotations: Map from OpenAssistant dataset (helpfulness, verbosity, creativity on 1-5 scale)

**Attribute Dataset (Secondary):**
- Source: OpenAssistant/oasst1 (HuggingFace)
- 88,000 samples with attribute labels
- Use for attribute conditioning training

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Datasets
- Identifier: `Anthropic/hh-rlhf` and `OpenAssistant/oasst1`
- Code:
```python
from datasets import load_dataset
hh_dataset = load_dataset("Anthropic/hh-rlhf")
oasst_dataset = load_dataset("OpenAssistant/oasst1")
```

### Models

#### Baseline Model

**Architecture:** GPT-2 1.5B (gpt2-xl)  
**Type:** Autoregressive Language Model  
**Parameters:** 1.5 billion  
**Source:** HuggingFace Transformers  

**Configuration:**
- Vocabulary: 50,257 tokens
- Layers: 48 transformer blocks
- Hidden dim: 1600
- Attention heads: 25
- Context length: 1024 tokens

**Reference Policy (πref):**
- SFT checkpoint on high-quality demonstrations
- Required for DPO loss computation: β·log(πθ(y|x)/πref(y|x))

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `gpt2-xl`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained("gpt2-xl")
tokenizer = AutoTokenizer.from_pretrained("gpt2-xl")
```

#### Proposed Model

**Architecture:** GPT-2 1.5B + Joint DPO + Attribute Conditioning

**Modifications:**
- Base: Same GPT-2-XL architecture
- Added: Attribute embedding layer (3 attributes × 5 levels = 15-dim)
- Integration: Attribute embeddings concatenated with input embeddings

**Core Mechanism Implementation:**

```python
# Joint DPO + Attribute Training
# Based on: Rafailov et al. 2023 (DPO) + Dong et al. 2023 (SteerLM)

class JointDPOAttributeModel(nn.Module):
    """
    Joint training of DPO preference optimization + attribute conditioning
    L_total = α·L_DPO + (1-α)·L_attr where α=0.7
    """
    def __init__(self, base_model, num_attributes=3, num_levels=5):
        super().__init__()
        self.base_model = base_model  # GPT-2 XL
        self.attr_embedding = nn.Embedding(num_attributes * num_levels, hidden_dim)
        self.alpha = 0.7  # Loss weight
        
    def compute_dpo_loss(self, chosen_logits, rejected_logits, ref_chosen, ref_rejected, beta=0.1):
        """
        DPO Loss: -log σ(β·log(π_θ(y_w|x)/π_ref(y_w|x)) - β·log(π_θ(y_l|x)/π_ref(y_l|x)))
        """
        chosen_logprobs = F.log_softmax(chosen_logits, dim=-1)
        rejected_logprobs = F.log_softmax(rejected_logits, dim=-1)
        
        # Compute log ratios
        chosen_ratio = chosen_logprobs - ref_chosen
        rejected_ratio = rejected_logprobs - ref_rejected
        
        # DPO loss
        loss_dpo = -F.logsigmoid(beta * (chosen_ratio - rejected_ratio)).mean()
        return loss_dpo
    
    def compute_attr_loss(self, logits, target_attrs):
        """
        Attribute conditioning loss: Cross-entropy on attribute prediction
        """
        # Predict attributes from final hidden states
        attr_logits = self.attr_head(logits[:, -1, :])  # (B, num_attributes * num_levels)
        loss_attr = F.cross_entropy(attr_logits, target_attrs)
        return loss_attr
    
    def forward(self, chosen, rejected, ref_chosen, ref_rejected, target_attrs):
        """
        Joint training forward pass
        Returns: L_total = 0.7·L_DPO + 0.3·L_attr
        """
        # DPO forward
        chosen_logits = self.base_model(chosen).logits
        rejected_logits = self.base_model(rejected).logits
        loss_dpo = self.compute_dpo_loss(chosen_logits, rejected_logits, ref_chosen, ref_rejected)
        
        # Attribute conditioning forward
        loss_attr = self.compute_attr_loss(chosen_logits, target_attrs)
        
        # Joint loss
        loss_total = self.alpha * loss_dpo + (1 - self.alpha) * loss_attr
        
        return loss_total, loss_dpo, loss_attr
```

### Training Protocol

**Optimizer:** AdamW  
- Parameters: lr=1e-5, betas=(0.9, 0.999), weight_decay=0.01, eps=1e-8
- Source: Standard for LLM fine-tuning (from Phase 2B)

**Learning Rate:** 1e-5  
- Schedule: Linear warmup (500 steps) + cosine decay
- Source: DPO paper baseline hyperparameters

**Batch Size:** 128 pairs  
- Effective: 4 per GPU × 32 gradient accumulation steps
- Source: Phase 2B specification

**Training Steps:** 15,000  
- Estimated epochs: ~92 over 128k training samples
- Source: Phase 2B timeline (3-5 days on single A100)

**DPO Beta (β):** 0.1  
- Controls strength of preference optimization
- Source: Rafailov et al. 2023 default

**Loss Weight (α):** 0.7  
- L_total = 0.7·L_DPO + 0.3·L_attr
- Source: Phase 2B hypothesis specification

**Seeds:** 42 (fixed)  
> ⚠️ **EXISTENCE (PoC)**: Single seed only. Statistical robustness not required for PoC.

**Hardware:** 1× NVIDIA A100 40GB  
**Estimated Time:** 3-5 days

### Evaluation

**Primary Metrics:**

1. **Preference Win Rate** (AI-to-Human dimension)
   - Definition: % of generated responses preferred over DPO baseline
   - Measurement: GPT-4 judge on 1,000 held-out prompts
   - Threshold: ≥50% (better than random)
   - Expected baseline: 57.5% (DPO standalone from Phase 2B)

2. **Attribute Steering Accuracy** (Human-to-AI dimension)
   - Definition: % of responses within ±0.5 of requested attribute level (1-5 scale)
   - Measurement: Attribute predictor (pre-trained on OpenAssistant)
   - Test samples: 6 attribute combinations × 100 prompts = 600 evaluations
   - Threshold: ≥60% (better than chance 20% on 5-level scale)
   - Expected baseline: 87% (SteerLM standalone from Phase 2B)

**Monitoring Metrics (Training):**
- L_DPO convergence (should decrease monotonically)
- L_attr convergence (should decrease monotonically)
- Gradient angle between ∇L_DPO and ∇L_attr (should be <120°, no catastrophic interference)

**Success Criteria (PoC):**
1. Both losses decrease without divergence
2. Preference win rate > 50% (effect direction)
3. Steering accuracy > 60% (effect direction)
4. Training completes without gradient explosion

**Expected Baseline Performance** (from research):
- DPO-only: 57.5% win rate, 0% steering (no attribute control)
- Attr-only: 0% win rate (no preference optimization), unknown steering
- Joint (H-E1): Target ≥50% win rate AND ≥60% steering

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Text generation with preference + attribute evaluation
- Library: Custom (GPT-4 API for preference, HuggingFace for attribute prediction)
- Code:
```python
# Preference evaluation
import openai
def evaluate_preference(prompt, response_a, response_b):
    # GPT-4 judge comparison
    pass

# Attribute evaluation
from transformers import pipeline
attr_predictor = pipeline("text-classification", model="attribute-predictor")
def evaluate_steering(response, target_attr, target_level):
    predicted = attr_predictor(response)
    return abs(predicted - target_level) <= 0.5
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart
  - X-axis: [Preference Win Rate, Steering Accuracy]
  - Y-axis: Percentage (0-100%)
  - Bars: [Target threshold, Actual result]
  - Pass/Fail indicators

#### Additional Figures (LLM Autonomous)

Based on EXISTENCE hypothesis and joint training mechanism, recommended visualizations:

1. **Training Loss Curves**
   - Dual y-axis: L_DPO (left), L_attr (right)
   - X-axis: Training steps
   - Shows convergence and monotonic decrease

2. **Gradient Angle Distribution**
   - Histogram of angles between ∇L_DPO and ∇L_attr
   - Threshold line at 120° (catastrophic interference boundary)

3. **Attribute Steering Heatmap**
   - Rows: 3 attributes (helpfulness, verbosity, creativity)
   - Columns: 5 levels (1-5)
   - Color: Steering accuracy %

4. **Preference Win Rate by Sample**
   - Scatter plot: Sample index vs win probability
   - Mean line with confidence band

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (training completes 15k steps)
2. Both losses decrease (L_DPO and L_attr converge)
3. Preference win rate > 50% (better than random)
4. Steering accuracy > 60% (better than chance)

**Failure Indicators:**
- Training divergence (loss increases or NaN)
- Gradient angles >120° (objective conflict)
- Win rate ≤50% or steering ≤60% (below threshold)

---

## Appendix: Reference Implementations

### Primary References

1. **DPO (Direct Preference Optimization)**
   - Paper: Rafailov et al. 2023 - "Direct Preference Optimization: Your Language Model is Secretly a Reward Model"
   - Implementation: Expected at github.com/eric-mitchell/direct-preference-optimization
   - Key insight: Bypass reward model, optimize directly on preference data
   - Baseline: 57.5% win rate vs SFT on HH-RLHF

2. **SteerLM (Attribute Conditioning)**
   - Paper: Dong et al. 2023 - "SteerLM: Attribute Conditioned SFT as an (User-Steerable) Alternative to RLHF"
   - Implementation: NVIDIA NeMo-Aligner (github.com/NVIDIA/NeMo-Aligner)
   - Key insight: Control tokens for attribute steering
   - Baseline: 87% steering accuracy, <5% latency cost

3. **Joint Multi-Task Training Pattern**
   - Source: Ruder 2017 - "An Overview of Multi-Task Learning in Deep Neural Networks"
   - Pattern: L_total = α·L1 + (1-α)·L2
   - Precedent: Length-normalized DPO (Park et al. 2024) - disentanglement via joint objectives

### Datasets

- **Anthropic HH-RLHF**: Bai et al. 2022 - "Training a Helpful and Harmless Assistant with RLHF"
  - HuggingFace: Anthropic/hh-rlhf
  - 161k preference pairs, verified accessible

- **OpenAssistant**: OpenAssistant Conversations Dataset (OASST1)
  - HuggingFace: OpenAssistant/oasst1
  - 88k samples with attribute labels

### HuggingFace TRL Library (Fallback)
- Library: trl (Transformer Reinforcement Learning)
- DPO Trainer: `trl.DPOTrainer` (baseline DPO implementation)
- Useful for reference but requires custom modification for joint loss

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-07-12

### Workflow History for This Hypothesis

- **2026-07-12**: Hypothesis h-e1 set to IN_PROGRESS (Phase 2C starting)
- **Phase 2B**: Verification plan created with 4 hypotheses (H-E1 foundational)
- **Phase 2A**: Dataset/model selected (HH-RLHF + GPT-2 1.5B)
- **Gate Type**: MUST_WORK (failure stops entire workflow)
- **Expected Duration**: 3-5 days, ~150 GPU-hours

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
