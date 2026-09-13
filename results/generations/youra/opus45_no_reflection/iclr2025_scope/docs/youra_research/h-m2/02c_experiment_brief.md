# Experiment Design: H-M2

**Date:** 2026-08-18
**Author:** YouRA Research Pipeline
**Hypothesis Statement:** Token-level representations remain stable across lengths while matrix-level degrades
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing representation robustness across distillation objective types.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M1 PASS - Phi-1.5 has 2048 token hard limit confirmed)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (Training Distribution Bound)

### Gate Condition
Token-level drift slope < matrix-level drift slope across sequence lengths. If token-level representations are more robust to length extrapolation, drift should remain bounded while matrix-level drift increases.

---

## Continuation Context

H-M1 validated that Phi-1.5 cannot extrapolate beyond 2048 tokens due to fixed positional embeddings. This confirms the length extrapolation premise - teacher attention at training-length boundary (2048) represents the architectural limit for supervision quality.

### Previous Hypothesis Results (if applicable)
- **H-E1:** PASS - Unified framework implements both MOHAWK (matrix-level) and CAB (token-level) objectives
- **H-M1:** PASS - Phi-1.5 has hard 2048 token context limit; attention patterns measurable within valid range

---

## Implementation Research Summary

### Archon Knowledge Base Findings

1. **Hidden State Matching Techniques**
   - L2/MSE loss: `loss = F.mse_loss(model_pred.float(), target.float(), reduction="mean")`
   - Huber loss for robustness: `torch.sqrt((pred - target) ** 2 + huber_c**2) - huber_c`
   - Projection layers for dimension mismatch: `nn.Linear(student_dim, teacher_dim)`

2. **Attention State Caching**
   - T-GATE pattern: `cache = (hidden_uncond + hidden_pred_text) / 2` for attention caching

### Archon Code Examples

```python
# L2 Loss Pattern (from diffusers)
if args.loss_type == "l2":
    loss = F.mse_loss(model_pred.float(), target.float(), reduction="mean")
elif args.loss_type == "huber":
    loss = torch.mean(
        torch.sqrt((model_pred.float() - target.float()) ** 2 + args.huber_c**2) - args.huber_c
    )
```

### Exa GitHub Implementations

1. **MOHAWK (Matrix-Level Distillation)**
   - Repo: `goombalab/phi-mamba`, `goombalab/mohawk`
   - Method: Aligns attention mixing matrices between Transformer and Mamba
   - Stages: Matrix mixing → Hidden states → End-to-end predictions
   - Training: 3B tokens for Phi-Mamba distillation

2. **CAB (Token-Level Distillation)**
   - Repo: `wph6/CAB`
   - Method: Lightweight MLP bridge aligning Q/K (Transformer) with B/C (Mamba)
   - Key Feature: Token-level supervision via attention bridge
   - Advantage: Data-efficient, hierarchical layer alignment

3. **Hidden State Distillation Patterns**
   - `sarimahsan/distillation-hiddenstates-code`: MSE between projected hidden states
   - `EmbedDistillLoss`: Supports mse, l2, cosine distance metrics
   - Projection head: `nn.Linear(student_dim, projection_dim)` for dimension alignment

### 🎯 Implementation Priority Assessment

**CRITICAL: Use official MOHAWK and CAB implementations as baselines**

**Recommended Implementation Path:**
- Primary: Extend goombalab/phi-mamba with hidden state extraction hooks
- Fallback: Custom implementation with HuggingFace transformers + mamba-ssm
- Justification: MOHAWK repo is official, tested, and compatible with Phi-1.5/Phi-Mamba

### Code Analysis (Serena MCP)

*Serena available but not required for this experiment - implementation uses external repos*

---

## Experiment Specification

### Dataset

| Attribute | Value |
|-----------|-------|
| **Name** | C4 (Colossal Clean Crawled Corpus) |
| **Version** | en, validation split |
| **Source** | allenai/c4 (HuggingFace) |
| **Type** | standard |
| **Samples** | 500 documents per length condition |
| **Lengths** | 512, 1024, 1536, 2048 tokens (within Phi-1.5 valid range) |
| **Preprocessing** | Tokenize with Phi-1.5 tokenizer, truncate/pad to target length |
| **Splits** | N/A (analysis only, no training split needed) |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets (streaming)
- Identifier: `allenai/c4`
- Code:
```python
from datasets import load_dataset

dataset = load_dataset("allenai/c4", "en", split="validation", streaming=True)
filtered = dataset.filter(lambda x: len(x["text"]) >= 8192)  # Ensure sufficient length
samples = list(filtered.take(500))
```

### Models

#### Baseline Model

| Attribute | Value |
|-----------|-------|
| **Name** | Phi-1.5 (Teacher) |
| **Architecture** | Decoder-only Transformer |
| **Parameters** | 1.3B |
| **Context Length** | 2048 tokens (hard limit) |
| **Source** | microsoft/phi-1_5 (HuggingFace) |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `microsoft/phi-1_5`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

teacher = AutoModelForCausalLM.from_pretrained(
    "microsoft/phi-1_5",
    torch_dtype=torch.float16,
    device_map="auto",
    output_hidden_states=True
)
tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-1_5")
```

#### Proposed Model

**Architecture:** Phi-Mamba (Mamba-2 variant distilled from Phi-1.5)

| Variant | Distillation Type | Source |
|---------|-------------------|--------|
| Phi-Mamba-MOHAWK | Matrix-level (attention map alignment) | goombalab/phi-mamba |
| Phi-Mamba-CAB | Token-level (Q/K→B/C alignment) | wph6/CAB + phi-mamba |

**Core Mechanism Implementation:**

```python
# Hidden State Drift Measurement Core
def compute_hidden_drift(teacher_model, student_model, input_ids, layers=[8, 12, 16]):
    """
    Compute L2 drift between teacher and student hidden states per layer.
    
    Args:
        teacher_model: Phi-1.5 (frozen)
        student_model: Phi-Mamba (MOHAWK or CAB distilled)
        input_ids: Tokenized input [batch, seq_len]
        layers: Layer indices to extract (middle layers)
    
    Returns:
        drift_per_layer: Dict[layer_idx, float] - Mean L2 distance per layer
    """
    with torch.no_grad():
        # Extract teacher hidden states
        teacher_out = teacher_model(input_ids, output_hidden_states=True)
        teacher_hidden = teacher_out.hidden_states  # Tuple of [batch, seq, dim]
        
        # Extract student hidden states
        student_out = student_model(input_ids, output_hidden_states=True)
        student_hidden = student_out.hidden_states
    
    drift_per_layer = {}
    for layer_idx in layers:
        # Get hidden states for this layer
        t_h = teacher_hidden[layer_idx]  # [batch, seq, teacher_dim]
        s_h = student_hidden[layer_idx]  # [batch, seq, student_dim]
        
        # Project if dimensions differ (Phi-1.5: 2048, Phi-Mamba: may differ)
        if t_h.shape[-1] != s_h.shape[-1]:
            projection = nn.Linear(s_h.shape[-1], t_h.shape[-1]).to(s_h.device)
            s_h = projection(s_h)
        
        # Compute L2 distance per position, average across batch and sequence
        l2_dist = torch.norm(t_h - s_h, p=2, dim=-1)  # [batch, seq]
        drift_per_layer[layer_idx] = l2_dist.mean().item()
    
    return drift_per_layer


def measure_drift_across_lengths(
    teacher, student_mohawk, student_cab,
    dataset, lengths=[512, 1024, 1536, 2048], n_samples=500
):
    """
    Compare drift slopes: token-level (CAB) vs matrix-level (MOHAWK).
    
    Success Criteria:
        - CAB drift slope < MOHAWK drift slope
        - CAB drift remains bounded at max length
    """
    results = {"mohawk": {}, "cab": {}}
    
    for length in lengths:
        # Prepare samples at this length
        samples = prepare_samples(dataset, length, n_samples)
        
        mohawk_drifts = []
        cab_drifts = []
        
        for batch in samples:
            input_ids = batch["input_ids"]
            
            # MOHAWK (matrix-level) drift
            mohawk_drift = compute_hidden_drift(teacher, student_mohawk, input_ids)
            mohawk_drifts.append(np.mean(list(mohawk_drift.values())))
            
            # CAB (token-level) drift
            cab_drift = compute_hidden_drift(teacher, student_cab, input_ids)
            cab_drifts.append(np.mean(list(cab_drift.values())))
        
        results["mohawk"][length] = np.mean(mohawk_drifts)
        results["cab"][length] = np.mean(cab_drifts)
    
    # Compute drift slopes (linear regression)
    mohawk_slope = compute_slope(lengths, list(results["mohawk"].values()))
    cab_slope = compute_slope(lengths, list(results["cab"].values()))
    
    return {
        "mohawk_slope": mohawk_slope,
        "cab_slope": cab_slope,
        "gate_pass": cab_slope < mohawk_slope,
        "per_length": results
    }
```

### Training Protocol

**Note:** This is an ANALYSIS experiment, not a training experiment. No new models are trained.

| Parameter | Value |
|-----------|-------|
| **Pre-trained Models** | Use existing Phi-Mamba checkpoints |
| **MOHAWK Checkpoint** | goombalab/phi-mamba (3B token distillation) |
| **CAB Checkpoint** | wph6/CAB or custom 500M token training |
| **Analysis Batch Size** | 8 |
| **Precision** | float16 |
| **Hardware** | 1× A100 (40GB) |

**If CAB checkpoint unavailable:**
```python
# Minimal CAB training config (500M tokens)
training_config = {
    "teacher": "microsoft/phi-1_5",
    "student_base": "state-spaces/mamba-2.8b",  # or phi-mamba backbone
    "objective": "cab",  # Q/K→B/C alignment
    "tokens": 500_000_000,
    "batch_size": 32,
    "learning_rate": 1e-4,
    "warmup_steps": 1000,
    "data": "allenai/c4",
}
```

### Evaluation

| Metric | Description | Success Criterion |
|--------|-------------|-------------------|
| **L2 Drift** | Mean L2 distance between teacher/student hidden states | CAB < MOHAWK at each length |
| **Drift Slope** | Linear regression slope of drift vs length | CAB slope < MOHAWK slope |
| **Cosine Similarity** | 1 - cosine(teacher_h, student_h) | CAB similarity > MOHAWK similarity |
| **Per-Layer Drift** | Drift measured at layers 8, 12, 16 | Trend consistent across layers |

**PoC Success Criteria:**
1. Primary: `cab_slope < mohawk_slope` (token-level more robust)
2. Secondary: CAB drift remains bounded (< 2× minimum) at 2048 tokens

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Hidden state analysis
- Library: torch, numpy, scipy (for linear regression)
- Code:
```python
import torch
import numpy as np
from scipy import stats

def compute_slope(lengths, drifts):
    """Compute linear regression slope."""
    slope, _, _, _, _ = stats.linregress(lengths, drifts)
    return slope

def l2_drift(h_teacher, h_student):
    """L2 distance between hidden states."""
    return torch.norm(h_teacher - h_student, p=2, dim=-1).mean()

def cosine_similarity(h_teacher, h_student):
    """Cosine similarity between hidden states."""
    return F.cosine_similarity(h_teacher, h_student, dim=-1).mean()
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Drift vs Length Plot**: Line plot showing L2 drift for MOHAWK and CAB across lengths (512, 1024, 1536, 2048)
  - X-axis: Sequence length
  - Y-axis: Mean L2 drift
  - Two lines: MOHAWK (orange), CAB (blue)
  - Slope annotations for each line

#### Additional Figures (LLM Autonomous)

1. **Per-Layer Drift Heatmap**: Layers (8, 12, 16) × Lengths × Objective type
2. **Cosine Similarity Comparison**: Bar chart at each length
3. **Drift Distribution**: Violin plots showing drift variance per condition

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (hidden state extraction works for both model types)
2. `cab_slope < mohawk_slope` (primary gate condition)
3. Drift measurements are statistically meaningful (std < mean for each condition)

**Expected Outcome:**
- MOHAWK drift increases more steeply with sequence length (matrix-level captures length-specific patterns)
- CAB drift remains flatter (token-level Q/K alignment generalizes better)

---

## Appendix: Reference Implementations

### Primary References

1. **MOHAWK Paper & Code**
   - Paper: https://arxiv.org/abs/2408.10189
   - Code: https://github.com/goombalab/mohawk
   - Phi-Mamba: https://github.com/goombalab/phi-mamba
   - Key: Matrix-level distillation with progressive stages

2. **CAB Paper & Code**
   - Paper: https://arxiv.org/abs/2510.19266
   - Code: https://github.com/wph6/CAB
   - Key: Q/K→B/C alignment via attention bridge

3. **Hidden State Distillation**
   - HuggingFace seq2seq distillation: https://github.com/huggingface/transformers/blob/main/examples/seq2seq/distillation.py
   - `calc_hidden_loss`: MSE between student/teacher hidden states with masking
   - CKA-based matching: https://openreview.net/forum?id=IcVSKhVpKu

### Code Snippets

**Hidden Loss Calculation (HuggingFace):**
```python
def calc_hidden_loss(attention_mask, hidden_states, hidden_states_T, matches):
    mask = attention_mask.to(hidden_states[0])
    valid_count = mask.sum() * hidden_states[0].size(-1)
    # MSE loss with masking...
```

**Embedding Distillation Loss:**
```python
class EmbedDistillLoss(nn.Module):
    def forward(self, student_emb, teacher_emb):
        if self.distance_metric == "l2":
            loss = torch.norm(student_emb - teacher_emb, dim=-1).mean()
        elif self.distance_metric == "cosine":
            loss = 1 - F.cosine_similarity(student_emb, teacher_emb, dim=-1).mean()
        return loss
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-18T15:30:00Z

### Workflow History for This Hypothesis
- H-E1 PASS: Unified framework validated
- H-M1 PASS: Phi-1.5 2048 token limit confirmed
- H-M2 IN_PROGRESS: Designing representation robustness experiment

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
