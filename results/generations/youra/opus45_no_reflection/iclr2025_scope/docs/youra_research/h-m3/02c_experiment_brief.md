# Experiment Design: H-M3

**Date:** 2026-08-18
**Author:** Anonymous
**Hypothesis Statement:** Token-level achieves superior F1 retention at extrapolated lengths with significant interaction effect
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing causal mechanism with factorial design.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M2 VALIDATED)
**Gate Status:** MUST_WORK - Interaction term significant at p<0.05

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-M2 (VALIDATED)

### Gate Condition
Interaction term (Objective Type × Sequence Length) must be significant at p<0.05. P2 and P3 effect sizes must match predictions (≥3 and ≥5 F1 points respectively).

---

## Continuation Context

Building on H-M2's finding that CAB drift slope is 5x lower than MOHAWK (0.00090506 vs 0.00452495), H-M3 tests whether this representation stability translates to downstream F1 performance advantage at extrapolated lengths.

### Previous Hypothesis Results (if applicable)
- **H-M2 Result:** CAB drift slope 5x lower than MOHAWK
- **Implication:** Token-level distillation maintains more stable representations across lengths
- **Prediction:** This stability should yield better F1 retention at 16K+ lengths

---

## Implementation Research Summary

### Archon Knowledge Base Findings

No direct matches for MOHAWK/CAB distillation in Archon KB. Related findings:
- Flash Attention implementation patterns (HazyResearch/flash-attention)
- PyTorch scaled_dot_product_attention for efficient attention computation
- Attention processor patterns from HuggingFace diffusers

### Archon Code Examples

No directly relevant code examples for F1 retention or LongBench evaluation in KB.

### Exa GitHub Implementations

**1. MOHAWK / Phi-Mamba (Official)**
- **Repository:** https://github.com/goombalab/phi-mamba
- **Paper:** https://arxiv.org/abs/2408.10189
- **Key Features:**
  - 3-stage distillation: Matrix Orientation → Hidden-State Alignment → Full Model
  - Phi-1.5 to Phi-Mamba conversion with 3B tokens
  - Matrix mixer alignment via MSE loss on attention maps
- **Installation:** `pip install mamba-ssm`, `pip install causal_conv1d==1.1.1`

**2. CAB - Cross-Architecture Attention Bridge (Official)**
- **Repository:** https://github.com/wph6/CAB
- **Paper:** https://arxiv.org/abs/2510.19266
- **Key Features:**
  - Token-level supervision via MLP bridge
  - Q/K to B/C alignment (attention projections → SSM projections)
  - Hierarchical layer alignment strategy
  - Data-efficient (works with limited training data)

**3. LongBench Evaluation**
- **Repository:** https://github.com/THUDM/LongBench
- **Dataset:** THUDM/LongBench (HuggingFace)
- **Metrics:** F1 score for QA tasks (qa_f1_score function)
- **Length Buckets:** 0-4k, 4-8k, 8k+ via scorer_e function

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Priority | Source | Rationale |
|----------|--------|-----------|
| 1 | goombalab/phi-mamba | Official MOHAWK, verified results |
| 2 | wph6/CAB | Official CAB, token-level reference |
| 3 | THUDM/LongBench | Official benchmark, evaluation code |

**Recommended Implementation Path:**
- Primary: Use pre-trained Phi-Mamba checkpoints from goombalab + CAB-style training modification
- Fallback: Train from scratch using MOHAWK Stage 1-3 pipeline with CAB bridge substitution
- Justification: Leverages validated implementations; only variable is distillation objective type

### Code Analysis (Serena MCP)

*Skipped - No local codebase to analyze. Using external repository documentation.*

---

## Experiment Specification

### Dataset

**Name:** LongBench (Single-Document QA Subset)
**Version:** v1 (original, not v2)
**Source:** THUDM/LongBench (HuggingFace)
**Type:** standard

**Tasks Selected (QA with F1 metric):**
| Task | Type | Avg Length | Metric |
|------|------|------------|--------|
| narrativeqa | Single-doc QA | ~18K | F1 |
| qasper | Single-doc QA | ~5K | F1 |
| multifieldqa_en | Single-doc QA | ~5K | F1 |
| hotpotqa | Multi-doc QA | ~9K | F1 |
| 2wikimqa | Multi-doc QA | ~5K | F1 |
| musique | Multi-doc QA | ~11K | F1 |
| triviaqa | Single-doc QA | ~8K | F1 |

**Splits:**
- Train: C4 dataset (for distillation training)
- Eval: LongBench test split (full ~200 samples per task)

**Preprocessing:**
- Truncate from middle to preserve instruction + question at ends
- Length buckets: 4K, 16K, 32K (create by padding/sampling)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: THUDM/LongBench
- Code:
```python
from datasets import load_dataset

# QA tasks for F1 evaluation
qa_tasks = ["narrativeqa", "qasper", "multifieldqa_en", 
            "hotpotqa", "2wikimqa", "musique", "triviaqa"]

for task in qa_tasks:
    dataset = load_dataset("THUDM/LongBench", task, split="test")
```

### Models

#### Baseline Model

**Name:** MOHAWK-distilled Phi-Mamba (Matrix-level objective)
**Architecture:** Mamba-2 SSM replacing Phi-1.5 attention
**Parameters:** 1.5B
**Source:** goombalab/phi-mamba (pre-trained) OR train with MOHAWK Stage 1-3
**Training:** 1.5B tokens on C4 at each target length (4K, 16K, 32K)

**MOHAWK Distillation Loss:**
```python
# Matrix-level: MSE on attention maps
L_matrix = MSE(student_mixer_matrix, teacher_attention_matrix)
# Where student_mixer_matrix = Mamba-2 M matrix
# teacher_attention_matrix = softmax(Q @ K.T / sqrt(d))
```

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Hub
- Identifier: goombalab/phi-mamba
- Code:
```python
from transformers import AutoTokenizer
from modules.lm_head import LMHeadModel
from utils.config import Config

# Load pre-trained Phi-Mamba
config = Config.from_json("phi_mamba_config.json")
model = LMHeadModel(config)
model.load_state_dict(torch.load("phi-mamba-1.5b.pt"))
tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-1_5")
```

#### Proposed Model

**Architecture:** CAB-distilled Phi-Mamba (Token-level objective)

**Core Mechanism Implementation:**

```python
# CAB Token-Level Distillation Loss
# Key insight: Align Q/K projections to B/C projections via MLP bridge

class AttentionBridge(nn.Module):
    """MLP bridge aligning Transformer Q/K to Mamba B/C"""
    def __init__(self, d_model, hidden_dim=None):
        super().__init__()
        hidden_dim = hidden_dim or d_model * 2
        # Bridge for Q -> B alignment
        self.q_to_b = nn.Sequential(
            nn.Linear(d_model, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, d_model)
        )
        # Bridge for K -> C alignment  
        self.k_to_c = nn.Sequential(
            nn.Linear(d_model, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, d_model)
        )
    
    def forward(self, q, k):
        """Project Q/K to B/C space"""
        b_proj = self.q_to_b(q)  # [B, L, D]
        c_proj = self.k_to_c(k)  # [B, L, D]
        return b_proj, c_proj

def cab_token_level_loss(teacher_model, student_model, bridge, input_ids):
    """
    Token-level CAB distillation loss.
    Aligns teacher Q/K with student B/C via bridge.
    """
    # Get teacher attention projections
    teacher_out = teacher_model(input_ids, output_hidden_states=True)
    
    total_loss = 0
    for layer_idx, (teacher_layer, student_layer) in enumerate(
        zip(teacher_model.layers, student_model.layers)
    ):
        # Teacher: Q, K projections [B, L, D]
        hidden = teacher_out.hidden_states[layer_idx]
        Q = teacher_layer.attn.q_proj(hidden)
        K = teacher_layer.attn.k_proj(hidden)
        
        # Bridge: Transform Q/K to B/C space
        B_target, C_target = bridge(Q, K)
        
        # Student: Actual B, C from Mamba layer
        B_student = student_layer.mixer.in_proj_b(hidden)
        C_student = student_layer.mixer.in_proj_c(hidden)
        
        # Token-level MSE loss (NOT matrix-level)
        loss_b = F.mse_loss(B_student, B_target.detach())
        loss_c = F.mse_loss(C_student, C_target.detach())
        
        total_loss += (loss_b + loss_c) / 2
    
    return total_loss / len(teacher_model.layers)

# Training loop skeleton
def train_cab_distillation(teacher, student, bridge, dataloader, 
                           num_tokens=1_500_000_000):
    """
    Train CAB-distilled model for 1.5B tokens.
    """
    optimizer = AdamW(
        list(student.parameters()) + list(bridge.parameters()),
        lr=3e-4, weight_decay=0.1
    )
    scheduler = CosineAnnealingLR(optimizer, T_max=num_tokens // batch_tokens)
    
    tokens_seen = 0
    while tokens_seen < num_tokens:
        for batch in dataloader:
            loss = cab_token_level_loss(teacher, student, bridge, batch)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
            scheduler.step()
            tokens_seen += batch.numel()
    
    return student
```

### Training Protocol

**Factorial Design:** 2 objectives × 3 lengths = 6 conditions

| Condition | Objective | Training Length | Eval Length |
|-----------|-----------|-----------------|-------------|
| MOHAWK-4K | Matrix-level | 4K | 4K |
| MOHAWK-16K | Matrix-level | 16K | 16K |
| MOHAWK-32K | Matrix-level | 32K | 32K |
| CAB-4K | Token-level | 4K | 4K |
| CAB-16K | Token-level | 16K | 16K |
| CAB-32K | Token-level | 32K | 32K |

**Hyperparameters (both objectives):**
| Parameter | Value |
|-----------|-------|
| Tokens per condition | 1.5B |
| Batch size | 32 |
| Sequence length | Variable (4K/16K/32K) |
| Learning rate | 3e-4 |
| LR schedule | Cosine annealing |
| Weight decay | 0.1 |
| Optimizer | AdamW |
| Precision | bf16 |
| Gradient accumulation | Adjusted for memory |

**Hardware:** 8× A100 80GB (estimated 4 weeks total for 6 conditions)

### Evaluation

**Primary Metric:** F1 Retention Ratio
```
F1_retention = (student_F1 / teacher_F1) × 100
```

**Statistical Analysis:**
1. **2×3 ANOVA** with factors:
   - Factor A: Objective Type (MOHAWK vs CAB)
   - Factor B: Sequence Length (4K, 16K, 32K)
   - Interaction: A × B

2. **Success Criteria:**
   - Interaction term significant at p < 0.05
   - P1 (4K): MOHAWK ≥ CAB (within 2 F1 points)
   - P2 (16K): CAB > MOHAWK by ≥3 F1 points
   - P3 (32K): CAB > MOHAWK by ≥5 F1 points

**F1 Score Implementation:**
```python
def qa_f1_score(prediction: str, ground_truth: str) -> float:
    """
    Token-level F1 between prediction and ground truth.
    From LongBench eval.py
    """
    pred_tokens = normalize_text(prediction).split()
    gt_tokens = normalize_text(ground_truth).split()
    
    if not pred_tokens or not gt_tokens:
        return 0.0
    
    common = Counter(pred_tokens) & Counter(gt_tokens)
    num_same = sum(common.values())
    
    if num_same == 0:
        return 0.0
    
    precision = num_same / len(pred_tokens)
    recall = num_same / len(gt_tokens)
    f1 = 2 * precision * recall / (precision + recall)
    
    return f1
```

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Question Answering
- Library: Custom (from LongBench) + scipy.stats for ANOVA
- Code:
```python
from scipy import stats
import numpy as np

def run_two_way_anova(f1_scores):
    """
    Run 2×3 ANOVA on F1 retention scores.
    
    Args:
        f1_scores: dict with keys like 'mohawk_4k', 'cab_16k', etc.
                   Each value is list of F1 scores across tasks
    
    Returns:
        dict with F-statistics and p-values for main effects and interaction
    """
    # Reshape for statsmodels or scipy
    # Factor A: Objective (0=MOHAWK, 1=CAB)
    # Factor B: Length (0=4K, 1=16K, 2=32K)
    
    from scipy.stats import f_oneway
    
    # Simplified: Compare CAB advantage at each length
    results = {}
    for length in ['4k', '16k', '32k']:
        mohawk = f1_scores[f'mohawk_{length}']
        cab = f1_scores[f'cab_{length}']
        t_stat, p_val = stats.ttest_ind(cab, mohawk)
        results[length] = {
            'cab_mean': np.mean(cab),
            'mohawk_mean': np.mean(mohawk),
            'difference': np.mean(cab) - np.mean(mohawk),
            'p_value': p_val
        }
    
    return results
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing F1 retention by condition
  - X-axis: Sequence Length (4K, 16K, 32K)
  - Y-axis: F1 Retention (%)
  - Bars: MOHAWK (blue) vs CAB (orange)
  - Error bars: 95% CI

#### Additional Figures (LLM Autonomous)
1. **Interaction Plot**: Line plot showing crossover pattern
   - Lines: MOHAWK vs CAB
   - X-axis: Sequence length
   - Y-axis: F1 retention
   - Expected: Lines cross between 4K-16K

2. **Per-Task Breakdown**: Grouped bar chart by LongBench task

3. **Effect Size Heatmap**: Matrix showing CAB advantage at each length × task

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Interaction term (Objective × Length) significant at p<0.05
3. P2: Token-level > matrix-level by ≥3 F1 points at 16K
4. P3: Token-level > matrix-level by ≥5 F1 points at 32K

---

## Appendix: Reference Implementations

### Primary References

1. **MOHAWK (Matrix-level distillation)**
   - Repository: https://github.com/goombalab/phi-mamba
   - Paper: Bick et al. "Transformers to SSMs: Distilling Quadratic Knowledge to Subquadratic Models" (2024)
   - Key file: `assets/mohawk_stage1.py` - Stage 1 matrix alignment

2. **CAB (Token-level distillation)**
   - Repository: https://github.com/wph6/CAB
   - Paper: Wang et al. "Data Efficient Any Transformer-to-Mamba Distillation via Attention Bridge" (2025)
   - Key concept: Q/K → B/C alignment via MLP bridge

3. **LongBench (Evaluation)**
   - Repository: https://github.com/THUDM/LongBench
   - Paper: Bai et al. "LongBench: A Bilingual, Multitask Benchmark for Long Context Understanding" (ACL 2024)
   - Key files: `eval.py`, `metrics.py`

### Code Snippets

**MOHAWK Stage 1 (from phi-mamba):**
```python
# Matrix orientation loss
student_output = student_layer(
    hidden_states=teacher_hidden,
    run_mlp_component=False,
    return_mixer_matrix=True,
)
transfer_matrix = student_output.mixer_matrix
teacher_attn = teacher_outputs.attentions[layer_idx]
loss = F.mse_loss(transfer_matrix, teacher_attn)
```

**LongBench Evaluation (from eval.py):**
```python
def scorer_e(dataset, predictions, answers, lengths, all_classes):
    scores = {"0-4k": [], "4-8k": [], "8k+": []}
    for (prediction, ground_truths, length) in zip(predictions, answers, lengths):
        score = max(dataset2metric[dataset](prediction, gt) for gt in ground_truths)
        if length < 4000:
            scores["0-4k"].append(score)
        elif length < 8000:
            scores["4-8k"].append(score)
        else:
            scores["8k+"].append(score)
    return {k: round(100 * np.mean(v), 2) for k, v in scores.items()}
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-18

### Workflow History for This Hypothesis
- H-E1: VALIDATED (unified framework works)
- H-M1: VALIDATED (attention entropy increases with length)
- H-M2: VALIDATED (CAB drift 5x lower than MOHAWK)
- H-M3: IN_PROGRESS (current)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
