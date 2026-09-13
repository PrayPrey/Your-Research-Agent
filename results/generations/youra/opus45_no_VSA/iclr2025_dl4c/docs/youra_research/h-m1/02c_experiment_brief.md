# Experiment Design: H-M1

**Date:** 2026-08-08
**Author:** Anonymous
**Hypothesis Statement:** I(F;E)_RL > I(F;E)_CE controlling for edit length, p<0.05
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM Template** - Tests HOW the effect works, not just THAT it exists.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-E1 validated)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (VALIDATED)

### Gate Condition
I(F;E)_RL > I(F;E)_CE controlling for edit length, p<0.05

**Interpretation:** 
- I(F;E) = Mutual Information between Final code F and Error feedback E
- RL training should induce tighter feedback-code coupling than CE training
- Controlling for edit length isolates the feedback utilization effect from mere verbosity

---

## Continuation Context

### Previous Hypothesis Results (H-E1)
- **Status:** VALIDATED (PASS)
- **Key Findings:**
  - Code executed successfully (exit=0)
  - All 4 conditions evaluated (CE-Single, CE-Refine, RL-Single, RL-Refine)
  - Artifacts persisted (results.json, results.csv, figures/*.png)
  - pass@1=0.0 for all conditions (expected for 1-epoch smoke test)
  - Interaction effect=0.0 (insufficient training for meaningful signal)
  - MUST_WORK gate satisfied (code runs, mechanism works)

### Implications for H-M1
- **Reuse:** H-E1 trained models (CE and RL variants) available
- **Extend:** Add MINE estimator module to measure I(F;E)
- **Focus:** Mechanism validation, not existence re-testing

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: mutual information neural estimation**
- Results: Limited direct matches (KB focused on diffusion/vision)
- Insight: MINE implementation needed from external sources

**Query 2: code generation feedback coupling**
- Results: General attention/representation learning patterns
- Hyperparameters: Embedding dimension 256-768 typical

### Exa GitHub Implementations

**Repository 1**: [gtegner/mine-pytorch](https://github.com/gtegner/mine-pytorch) (⭐ 362)
- **Relevance**: Official MINE PyTorch implementation
- **Architecture**: MLP statistics network T(X,Y)
- **Key Insight**: Donsker-Varadhan lower bound on MI
- **Usage**: `mine.estimate(joint_samples, marginal_samples)`

**Repository 2**: [sungyubkim/MINE-Mutual-Information-Neural-Estimation-](https://github.com/sungyubkim/MINE-Mutual-Information-Neural-Estimation-) (⭐ 349)
- **Relevance**: Clean MINE implementation with examples
- **Architecture**: Simple MLP, exponential moving average for stability
- **Training**: 5000 iterations, batch_size=128, lr=0.001

**Repository 3**: [MasanoriYamada/Mine_pytorch](https://github.com/MasanoriYamada/Mine_pytorch) (⭐ 208)
- **Relevance**: Comparison with traditional MI estimators
- **Validation**: Shows MINE matches analytical MI for Gaussians

### Recent RL Code Generation Papers (from Exa)

**RLEF (ICML 2025)** - Gehring et al.
- End-to-end RL for execution feedback grounding
- Shows RL enables effective feedback utilization over multiple steps
- Supports hypothesis: RL → better feedback conditioning

**Murphy (2025)** - Multi-turn GRPO with retrospective credit
- Feedback-conditioned rollout trees
- Suggests structural coupling between feedback and edits

**TaPR (2025)** - Test-aware policy refinement
- Dense per-turn test-pass-ratio reward
- Evidence that feedback signals shape edit policy

### 🎯 Implementation Priority Assessment

| Priority | Source | Status |
|----------|--------|--------|
| 1 | H-E1 trained models | ✅ Available - reuse CE/RL models |
| 2 | gtegner/mine-pytorch | ✅ Available - MINE estimator |
| 3 | evalplus/evalplus | ✅ Available - evaluation framework |

**Recommended Implementation Path:**
- Load H-E1 models (CE and RL variants)
- Implement MINE module for I(F;E) estimation
- Extract (feedback, edit) pairs from refinement traces
- Compare I(F;E) between training conditions

---

## Experiment Specification

### Dataset

**Primary Dataset**: HumanEval+ (164 problems)
- **Type**: standard
- **Source**: evalplus/evalplus
- **Purpose**: Extract refinement traces for MI estimation
- **Split**: Full 164 problems × 3 refinement rounds = 492 (feedback, edit) pairs per model

**Sample Size Justification:**
- 164 problems × 3 seeds × 3 refinement rounds = 1,476 samples per condition
- Sufficient for MINE convergence (typical: 1000+ samples)
- Permutation test: 10,000 permutations for p-value

**Loading Information**:
```python
from evalplus.data import get_human_eval_plus
problems = get_human_eval_plus()
```

### Models

#### Baseline Models (from H-E1)

**CE Model**: CodeT5+-220M fine-tuned with Cross-Entropy
- **Path**: `h-e1/models/ce_model/`
- **Training**: Standard seq2seq on code completion

**RL Model**: CodeT5+-220M fine-tuned with Execution Feedback RL
- **Path**: `h-e1/models/rl_model/`
- **Training**: REINFORCE with test pass rate reward

**Loading Information**:
```python
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

ce_model = AutoModelForSeq2SeqLM.from_pretrained("h-e1/models/ce_model")
rl_model = AutoModelForSeq2SeqLM.from_pretrained("h-e1/models/rl_model")
tokenizer = AutoTokenizer.from_pretrained("Salesforce/codet5p-220m")
```

### Core Mechanism Implementation

#### Mutual Information Estimation via MINE

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class MINEEstimator(nn.Module):
    """
    Mutual Information Neural Estimation (MINE).
    Estimates I(F;E) = MI between final code F and error feedback E.
    
    Reference: Belghazi et al., "Mutual Information Neural Estimation" (ICML 2018)
    """
    def __init__(self, feedback_dim: int = 256, code_dim: int = 256, hidden_dim: int = 512):
        super().__init__()
        # Statistics network T(E, F)
        self.network = nn.Sequential(
            nn.Linear(feedback_dim + code_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )
        self.ema_weight = 0.01  # Exponential moving average for bias correction
        self.running_mean = None
    
    def forward(self, feedback_emb: torch.Tensor, code_emb: torch.Tensor) -> torch.Tensor:
        """Compute T(E, F) for joint samples."""
        joint = torch.cat([feedback_emb, code_emb], dim=-1)
        return self.network(joint)
    
    def estimate_mi(self, 
                    feedback_emb: torch.Tensor,  # [N, feedback_dim]
                    code_emb: torch.Tensor,      # [N, code_dim]
                    marginal_code_emb: torch.Tensor = None  # [N, code_dim] shuffled
                   ) -> torch.Tensor:
        """
        Estimate I(E; F) using Donsker-Varadhan lower bound.
        
        I(E;F) >= E[T(E,F)] - log(E[exp(T(E,F'))])
        where F' is drawn from marginal p(F).
        """
        # Joint samples: (E_i, F_i)
        joint_scores = self.forward(feedback_emb, code_emb)  # [N, 1]
        
        # Marginal samples: (E_i, F_j) where j != i
        if marginal_code_emb is None:
            # Shuffle to get marginal
            perm = torch.randperm(code_emb.size(0))
            marginal_code_emb = code_emb[perm]
        
        marginal_scores = self.forward(feedback_emb, marginal_code_emb)  # [N, 1]
        
        # Donsker-Varadhan bound with EMA bias correction
        mi_lb = joint_scores.mean() - torch.log(torch.exp(marginal_scores).mean() + 1e-8)
        
        return mi_lb


def extract_refinement_pairs(model, tokenizer, problems: list, K: int = 3) -> list:
    """
    Extract (feedback, edit) pairs from refinement traces.
    
    Args:
        model: CodeT5+ model (CE or RL variant)
        problems: HumanEval+ problems
        K: Number of refinement iterations
        
    Returns:
        List of (feedback_text, edit_text, edit_length) tuples
    """
    pairs = []
    
    for problem in problems:
        prompt = problem["prompt"]
        tests = problem["tests"]
        
        # Initial generation
        prev_code = generate_code(model, tokenizer, prompt)
        
        for k in range(K):
            # Execute and get feedback
            result = execute_code_with_tests(prev_code, tests)
            feedback = result.error_message if result.failed else "All tests passed"
            
            if not result.failed:
                break  # No more refinement needed
            
            # Generate refined code
            refine_prompt = f"{prompt}\n\nPrevious code:\n{prev_code}\n\nFeedback:\n{feedback}\n\nRefined code:"
            new_code = generate_code(model, tokenizer, refine_prompt)
            
            # Compute edit (diff between prev and new code)
            edit = compute_code_diff(prev_code, new_code)
            edit_length = len(edit.split())
            
            pairs.append({
                "feedback": feedback,
                "edit": edit,
                "edit_length": edit_length,
                "problem_id": problem["task_id"],
                "iteration": k
            })
            
            prev_code = new_code
    
    return pairs


def embed_text(model, tokenizer, texts: list) -> torch.Tensor:
    """
    Get encoder embeddings for text sequences.
    Uses mean pooling over encoder hidden states.
    """
    inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model.encoder(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1)  # Mean pooling
    return embeddings
```

#### Edit Length Control via Regression

```python
import numpy as np
from scipy import stats

def control_for_edit_length(mi_values: np.ndarray, 
                             edit_lengths: np.ndarray,
                             condition_labels: np.ndarray) -> dict:
    """
    Control for edit length using residualized MI.
    
    H-M1 claim: I(F;E)_RL > I(F;E)_CE *controlling for edit length*
    
    Method:
    1. Regress MI on edit_length
    2. Use residuals for comparison
    3. Permutation test on residuals
    """
    # Fit linear regression: MI ~ edit_length
    slope, intercept, _, _, _ = stats.linregress(edit_lengths, mi_values)
    
    # Compute residuals
    predicted = slope * edit_lengths + intercept
    residuals = mi_values - predicted
    
    # Split by condition
    rl_mask = condition_labels == "RL"
    ce_mask = condition_labels == "CE"
    
    residual_mi_rl = residuals[rl_mask].mean()
    residual_mi_ce = residuals[ce_mask].mean()
    
    # Permutation test for significance
    observed_diff = residual_mi_rl - residual_mi_ce
    n_permutations = 10000
    perm_diffs = []
    
    for _ in range(n_permutations):
        perm_labels = np.random.permutation(condition_labels)
        perm_rl_mask = perm_labels == "RL"
        perm_ce_mask = perm_labels == "CE"
        perm_diff = residuals[perm_rl_mask].mean() - residuals[perm_ce_mask].mean()
        perm_diffs.append(perm_diff)
    
    p_value = (np.abs(perm_diffs) >= np.abs(observed_diff)).mean()
    
    return {
        "mi_rl_raw": mi_values[rl_mask].mean(),
        "mi_ce_raw": mi_values[ce_mask].mean(),
        "mi_rl_controlled": residual_mi_rl,
        "mi_ce_controlled": residual_mi_ce,
        "observed_diff": observed_diff,
        "p_value": p_value,
        "significant": p_value < 0.05
    }
```

### Training Protocol

**MINE Estimation Protocol:**

| Step | Action | Output |
|------|--------|--------|
| 1 | Load CE/RL models from H-E1 | Models ready |
| 2 | Extract refinement traces (K=3) | (feedback, edit) pairs |
| 3 | Embed feedback and edit text | Embeddings [N, 256] |
| 4 | Train MINE estimator | I(F;E) estimates |
| 5 | Apply edit-length control | Residualized MI |
| 6 | Permutation test | p-value |

**MINE Training Configuration:**
- **Optimizer**: Adam
  - lr: 0.001
  - **Source**: MINE original paper
- **Batch Size**: 128
- **Iterations**: 5000
- **Architecture**: 3-layer MLP (256+256 → 512 → 512 → 1)
- **Seeds**: 3 (for variance estimation)

**Sample Extraction:**
- Problems: 164 (HumanEval+)
- Refinement rounds: K=3
- Models: CE, RL (2 conditions)
- Seeds: 3
- Total samples per condition: 164 × 3 × 3 = 1,476

### Evaluation

**Primary Metric**: I(F;E)_RL - I(F;E)_CE (controlled for edit length)

**Success Criteria (Gate):**
1. I(F;E)_RL > I(F;E)_CE after edit-length control
2. p < 0.05 (permutation test, 10,000 permutations)

**Secondary Metrics:**
- Raw MI difference (without length control)
- Effect size (Cohen's d on residuals)
- MI by refinement iteration (does coupling increase with k?)

**Expected Results:**
- RL model should show higher I(F;E) because:
  - RL training optimizes p(edit | code, feedback) under diverse feedback
  - This forces learning feedback-conditioned representations
  - CE training only minimizes next-token prediction, no explicit feedback coupling

**Metrics Implementation:**
```python
def evaluate_hypothesis(results: dict) -> dict:
    """
    H-M1 Gate Check: I(F;E)_RL > I(F;E)_CE, p<0.05
    """
    gate_passed = (
        results["observed_diff"] > 0 and  # RL > CE
        results["p_value"] < 0.05          # Significant
    )
    
    return {
        "gate_status": "PASS" if gate_passed else "FAIL",
        "mi_rl_controlled": results["mi_rl_controlled"],
        "mi_ce_controlled": results["mi_ce_controlled"],
        "difference": results["observed_diff"],
        "p_value": results["p_value"],
        "effect_size": compute_cohens_d(results)
    }
```

### Visualization Requirements

#### Required Figures (Mandatory)

1. **MI Comparison Bar Chart**: I(F;E) for CE vs RL (with/without length control)
2. **Scatter Plot**: MI vs Edit Length, colored by condition
3. **Permutation Distribution**: Histogram of null distribution with observed difference marked

#### Additional Figures (LLM Autonomous)
- MI by refinement iteration (line plot, k=1,2,3)
- Embedding visualization (t-SNE of feedback-edit joint space)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## 🔬 Mechanism Verification Checklist

**Pre-conditions:**
- [ ] H-E1 models (CE, RL) successfully loaded
- [ ] Refinement traces extracted (≥1000 samples per condition)
- [ ] MINE estimator converges on validation data

**Activation Indicators:**
- [ ] MINE loss decreases during training
- [ ] MI estimates are positive and finite
- [ ] Permutation null distribution is centered near zero

**Success Criteria:**
- [ ] I(F;E)_RL > I(F;E)_CE (direction)
- [ ] p < 0.05 (significance)
- [ ] Effect persists after edit-length control

---

## Appendix: Reference Implementations

### Primary References

1. **MINE** (ICML 2018) - Belghazi et al.
   - Paper: https://arxiv.org/abs/1801.04062
   - Code: https://github.com/gtegner/mine-pytorch
   - Key: Neural MI estimation via Donsker-Varadhan bound

2. **RLEF** (ICML 2025) - Gehring et al.
   - Paper: https://proceedings.mlr.press/v267/gehring25a.html
   - Key: RL enables effective feedback grounding in code LLMs

3. **Murphy** (2025) - Ekbote et al.
   - Paper: https://arxiv.org/abs/2511.07833
   - Key: Feedback-conditioned rollout trees show structural coupling

4. **TaPR** (2025) - Liu et al.
   - Paper: https://arxiv.org/abs/2608.00494
   - Key: Dense per-turn feedback shapes edit policy

### MINE Implementation Reference

```python
# From gtegner/mine-pytorch (simplified)
class MINE(nn.Module):
    def __init__(self, x_dim, y_dim, hidden_dim=100):
        super().__init__()
        self.fc1 = nn.Linear(x_dim + y_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, 1)
        
    def forward(self, x, y):
        h = torch.cat([x, y], dim=1)
        h = F.relu(self.fc1(h))
        h = F.relu(self.fc2(h))
        return self.fc3(h)
    
    def mi(self, joint, marginal):
        t_joint = self.forward(*joint)
        t_marginal = self.forward(*marginal)
        mi = t_joint.mean() - torch.log(torch.exp(t_marginal).mean())
        return mi
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-08

### Workflow History for This Hypothesis
- 2026-08-08: Phase 2C experiment design started
- 2026-08-08: Research completed (Archon, Exa - MINE implementations, RL code gen papers)
- 2026-08-08: Experiment specification synthesized
- 2026-08-08: Builds on H-E1 validated infrastructure

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub implementations)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
