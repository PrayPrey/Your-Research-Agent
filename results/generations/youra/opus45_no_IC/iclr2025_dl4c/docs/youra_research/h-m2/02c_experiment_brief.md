# Experiment Design: H-M2

**Date:** 2026-08-10
**Author:** Anonymous
**Hypothesis Statement:** Token masking excludes non-executed code from gradient updates
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M1 CONDITIONAL_PASS)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (Execution trace collection enables token-level classification)

### Gate Condition
- **Type:** MUST_WORK
- **Pass Condition:** Trace-based masking > Random masking (p < 0.05); Masked tokens gradient norm = 0
- **Fail Action:** PIVOT - Check masking threshold or implementation error

---

## Continuation Context

### From H-M1
H-M1 validated that Python `sys.settrace()` can capture line-level execution traces and map them to token positions:
- **Trace Capture Rate:** 100%
- **Token Classification:** 81% F1 (acceptable for PoC)
- **Overhead:** 21.55x (marginal, acceptable)

The trace collection mechanism works. H-M2 now tests whether using these traces to MASK non-executed tokens actually excludes them from gradient computation and improves learning.

### Previous Hypothesis Results
- **H-E1:** PASS - FGO improves across all content types (compile +2.15%, test +2.24%)
- **H-M1:** CONDITIONAL_PASS - Trace collection works; token mapping ~81% accurate

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct matches for FGO token masking in KB. Primary reference remains StepCoder paper (ACL 2024).

### Archon Code Examples

No direct FGO implementation examples in current KB. Implementation derived from paper description.

### Exa GitHub Implementations

**StepCoder Official Repository:** https://github.com/Ablustrund/APPS_Plus
- Dataset: APPS+ available (MIT License)
- Code: Training code not publicly released; paper provides algorithm pseudocode

**Key Algorithm (from StepCoder Paper):**
```
Algorithm 1: CCCS + FGO
For each training step:
  1. Generate code y_hat from policy π_θ
  2. Execute unit tests, collect trace
  3. Build mask m_ij = 1 if token j executed, else 0
  4. Compute masked PPO loss:
     L^PPO(θ) = E_t[min(r_t(θ)A_t, clip(r_t(θ), 1-ε, 1+ε)A_t) * m_t]
  5. Update policy only on executed tokens
```

### Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

StepCoder training code NOT publicly released. Must implement from paper specification.

**Recommended Implementation Path:**
- Primary: Implement FGO masking following Algorithm 1 from StepCoder paper
- Fallback: Use TRL/OpenRLHF PPO with custom loss masking
- Justification: Paper provides sufficient detail; standard PPO libraries support custom loss functions

### Code Analysis (Serena MCP)

Not applicable - no existing FGO implementation in codebase to analyze.

---

## Experiment Specification

### Dataset

| Component | Specification |
|-----------|---------------|
| **Name** | HumanEval + MBPP |
| **Version** | HumanEval v1.0, MBPP v1.0 |
| **Source** | OpenAI (HumanEval), Google (MBPP) |
| **Splits** | HumanEval: 164 test; MBPP: 374 train, 90 val, 500 test |
| **Size** | 664 total evaluation samples |
| **Preprocessing** | Standard prompt formatting per benchmark |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `openai_humaneval`, `mbpp`
- Code:
```python
from datasets import load_dataset
humaneval = load_dataset("openai_humaneval", split="test")
mbpp = load_dataset("mbpp", split="test")
```

### Models

#### Baseline Model

| Component | Specification |
|-----------|---------------|
| **Architecture** | CodeLlama-7B-Instruct |
| **Source** | meta-llama/CodeLlama-7b-Instruct-hf |
| **Parameters** | 7B |
| **Context Length** | 4096 tokens |
| **Training** | Standard PPO without FGO masking |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `meta-llama/CodeLlama-7b-Instruct-hf`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/CodeLlama-7b-Instruct-hf",
    torch_dtype=torch.float16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/CodeLlama-7b-Instruct-hf")
```

#### Proposed Model

**Architecture:** CodeLlama-7B-Instruct + FGO Token Masking

**Core Mechanism Implementation:**

```python
def compute_fgo_masked_loss(
    logits: torch.Tensor,          # [batch, seq_len, vocab]
    labels: torch.Tensor,           # [batch, seq_len]
    execution_mask: torch.Tensor,   # [batch, seq_len] - 1=executed, 0=not
    advantages: torch.Tensor,       # [batch, seq_len]
    old_log_probs: torch.Tensor,    # [batch, seq_len]
    clip_epsilon: float = 0.2
) -> torch.Tensor:
    """
    FGO: Only compute PPO loss for executed tokens.
    Non-executed tokens receive ZERO gradient.
    """
    # Compute current log probabilities
    log_probs = F.log_softmax(logits, dim=-1)
    action_log_probs = log_probs.gather(-1, labels.unsqueeze(-1)).squeeze(-1)
    
    # PPO ratio
    ratio = torch.exp(action_log_probs - old_log_probs)
    
    # Clipped objective
    surr1 = ratio * advantages
    surr2 = torch.clamp(ratio, 1 - clip_epsilon, 1 + clip_epsilon) * advantages
    ppo_loss = -torch.min(surr1, surr2)
    
    # FGO: Apply execution mask - non-executed tokens get zero loss
    masked_loss = ppo_loss * execution_mask
    
    # Average over executed tokens only
    num_executed = execution_mask.sum() + 1e-8
    loss = masked_loss.sum() / num_executed
    
    return loss


def verify_gradient_exclusion(
    model: nn.Module,
    logits: torch.Tensor,
    labels: torch.Tensor,
    execution_mask: torch.Tensor
) -> dict:
    """
    Verify masked tokens receive zero gradient.
    """
    # Compute loss with masking
    loss = compute_fgo_masked_loss(logits, labels, execution_mask, ...)
    loss.backward()
    
    # Check gradients at embedding layer
    embed_grad = model.get_input_embeddings().weight.grad
    
    # For non-executed positions, gradient should be zero
    # This is verified by checking token-specific gradient contribution
    return {
        "executed_grad_norm": ...,
        "non_executed_grad_norm": ...,  # Should be 0
        "gradient_exclusion_verified": ...
    }
```

### Training Protocol

| Parameter | Value | Justification |
|-----------|-------|---------------|
| **Algorithm** | PPO (Proximal Policy Optimization) | Standard for code RL |
| **Optimizer** | AdamW | Standard for transformers |
| **Learning Rate** | 1e-5 | Conservative for fine-tuning |
| **LR Schedule** | Cosine decay | Smooth convergence |
| **Batch Size** | 16 | Memory-efficient |
| **PPO Epochs** | 4 | Standard PPO setting |
| **Clip Epsilon** | 0.2 | Standard PPO |
| **GAE Lambda** | 0.95 | Standard advantage estimation |
| **Training Steps** | 1000 | PoC validation |
| **Seeds** | 3 (42, 123, 456) | Statistical reliability |

**Ablation Conditions:**
1. **No Masking (Baseline):** Standard PPO, all tokens contribute to loss
2. **Random Masking:** Mask random tokens (same sparsity as trace-based)
3. **Trace-Based Masking (FGO):** Mask only non-executed tokens

### Evaluation

| Metric | Description | Success Threshold |
|--------|-------------|-------------------|
| **pass@1** | Primary correctness metric | Trace > Random (p < 0.05) |
| **Gradient Norm (Masked)** | Verify zero gradient for masked tokens | = 0 |
| **Gradient Norm (Unmasked)** | Verify non-zero gradient for executed tokens | > 0 |
| **Effective Learning Rate** | Gradient updates per token | Higher for FGO |

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Code generation
- Library: Custom evaluation (execute-based)
- Code:
```python
def evaluate_pass_at_k(model, dataset, k=1, num_samples=1):
    """Execute generated code against test cases."""
    results = []
    for problem in dataset:
        generations = generate(model, problem["prompt"], n=num_samples)
        passed = any(execute_tests(gen, problem["tests"]) for gen in generations)
        results.append(passed)
    return sum(results) / len(results)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing pass@1 for No-Mask vs Random-Mask vs Trace-Mask

#### Additional Figures (LLM Autonomous)
1. **Gradient Distribution:** Histogram of gradient norms for executed vs non-executed tokens
2. **Learning Curves:** Training loss over steps for each masking condition
3. **Masking Coverage:** Percentage of tokens masked per sample

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Trace-based masking pass@1 > Random masking pass@1
3. Masked tokens have gradient norm = 0 (verified by logging)

**Statistical Test:**
- Paired t-test comparing trace-based vs random across 3 seeds
- Required: p < 0.05

---

## Appendix: Reference Implementations

### Primary Reference
- **Paper:** StepCoder: Improving Code Generation with Reinforcement Learning from Compiler Feedback
- **Venue:** ACL 2024
- **Authors:** Dou et al. (Fudan NLP Lab)
- **URL:** https://aclanthology.org/2024.acl-long.251/
- **Dataset:** https://github.com/Ablustrund/APPS_Plus

### Key Equations (from Paper)

**FGO Masked Loss:**
```
L^PPO(θ) = E_t[min(r_t(θ)A_t, clip(r_t(θ), 1-ε, 1+ε)A_t) · m_t]
```

Where:
- `m_t = 1` if token t was executed in unit tests
- `m_t = 0` if token t was NOT executed
- `r_t(θ) = π_θ(a_t|s_t) / π_θ_old(a_t|s_t)` (probability ratio)
- `A_t` = advantage estimate

**Mask Matrix Construction:**
```
m_ij = {
  1  if token j in sequence i was executed
  0  otherwise
}
```

### Related Code References
- **TRL PPOTrainer:** https://github.com/huggingface/trl (supports custom loss)
- **OpenRLHF:** https://github.com/OpenRLHF/OpenRLHF (PPO for LLMs)

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-10

### Workflow History for This Hypothesis
- 2026-08-10: H-M2 set to IN_PROGRESS
- 2026-08-10: Phase 2C experiment design initiated
- 2026-08-10: Archon/Exa research completed
- 2026-08-10: Experiment brief generated

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub/Paper search)*
*All specifications grounded in StepCoder ACL 2024 paper*
*Next Phase: Phase 3 - Implementation Planning*
