# Methodology

We present a mechanism validation study of Fine-Grained Optimization (FGO) for code generation RL. Our approach decomposes FGO into three testable components and verifies each with explicit falsification criteria.

## Problem Setting

Consider a code generation model $\pi_\theta$ trained with PPO on execution feedback. Given a problem description $x$, the model generates a code solution $y = (y_1, \ldots, y_T)$ which is executed against test cases. The reward $r(y)$ is typically binary: 1 if all tests pass, 0 otherwise.

Standard PPO applies the reward uniformly across all tokens:
$$\mathcal{L}_{\text{PPO}} = -\mathbb{E}\left[\sum_{t=1}^{T} \min\left(\rho_t A_t, \text{clip}(\rho_t, 1-\epsilon, 1+\epsilon) A_t\right)\right]$$
where $\rho_t = \frac{\pi_\theta(y_t|y_{<t}, x)}{\pi_{\text{old}}(y_t|y_{<t}, x)}$ and $A_t$ is the advantage estimate.

This uniform treatment ignores a key observation: not all tokens influence the test outcome. Tokens in unreached branches, unused imports, or dead code never execute, yet receive identical gradient updates.

## Fine-Grained Optimization

FGO addresses this by masking non-executed tokens from gradient updates. Given an execution trace $\tau$ collected during test evaluation, we construct a binary mask $m \in \{0, 1\}^T$ where $m_t = 1$ if token $y_t$ corresponds to executed code and $m_t = 0$ otherwise.

The FGO loss modifies PPO to only update executed tokens:
$$\mathcal{L}_{\text{FGO}} = -\mathbb{E}\left[\frac{\sum_{t=1}^{T} m_t \cdot \min\left(\rho_t A_t, \text{clip}(\rho_t, 1-\epsilon, 1+\epsilon) A_t\right)}{\sum_{t=1}^{T} m_t + \epsilon}\right]$$

This concentrates gradients on tokens that actually influenced the outcome, providing denser credit assignment without additional reward shaping.

## Mechanism Decomposition

We decompose FGO into three components, each formulated as a testable hypothesis:

### Component 1: Trace Collection (H-M1)

**Claim**: Python's sys.settrace reliably captures execution traces during test evaluation.

**Implementation**: We instrument code execution with a trace function that records executed line numbers. Each test execution runs with a 5-second timeout to handle infinite loops. The trace function captures all executed lines, which are then mapped to token positions.

**Falsification Criterion**: If trace capture rate falls below 95%, the infrastructure is unreliable for FGO.

### Component 2: Token Classification (H-M1 continued)

**Claim**: Token-to-line mapping enables accurate classification of executed vs. non-executed tokens.

**Implementation**: We use the tokenizer's offset_mapping to determine which source characters each token spans, then map these to line numbers. A token is classified as "executed" if its line appears in the execution trace.

**Challenge**: Tokenizer boundaries do not always align with source line boundaries. Multi-line statements and tokenizer artifacts introduce mapping errors.

**Falsification Criterion**: If token classification F1 falls below 70%, the mapping is too noisy for effective masking.

### Component 3: Gradient Exclusion (H-M2)

**Claim**: FGO's token masking correctly excludes non-executed tokens from gradient computation.

**Implementation**: The FGO loss multiplies per-token losses by the mask before summing. Tokens with $m_t = 0$ contribute zero to the loss and thus receive zero gradient.

**Verification**: We compute gradient norms separately for executed ($m_t = 1$) and non-executed ($m_t = 0$) token positions and verify that non-executed gradients are exactly zero.

**Falsification Criterion**: If any non-executed token receives non-zero gradient, the masking implementation is incorrect.

### Component 4: Credit Assignment (H-M3)

**Claim**: Concentrating gradients on executed tokens improves learning efficiency.

**Metric**: Signal concentration, defined as the ratio of per-token gradient magnitude for executed tokens under FGO versus uniform distribution. If 80% of tokens are masked (non-executed), executed tokens receive 5x the per-token gradient signal.

**Falsification Criterion**: If FGO does not improve final pass@1 over standard PPO, the credit assignment benefit is not realized.

## Verification Protocol

We organize verification as a 4-hypothesis chain with explicit gate criteria:

| Hypothesis | Type | Gate | Pass Criterion |
|------------|------|------|----------------|
| H-E1 | Existence | MUST_WORK | FGO shows improvement across all content types |
| H-M1 | Mechanism | MUST_WORK | Trace capture >= 95%, Token F1 >= 70% |
| H-M2 | Mechanism | MUST_WORK | Non-executed gradient = 0 |
| H-M3 | Efficiency | SHOULD_WORK | FGO pass@1 > Standard pass@1 |

MUST_WORK gates block further investigation if failed. SHOULD_WORK gates document limitations but allow proceeding.

Figure 2 shows the token classification confusion matrix from our trace collection pipeline, demonstrating the mapping between execution traces and token-level labels.

## Implementation Details

We implement FGO on top of the TRL library's PPO trainer. Key implementation choices:

- **Trace timeout**: 5 seconds per execution to handle infinite loops
- **Sandbox**: RestrictedPython for safe execution of untrusted code
- **Tokenizer**: CodeLlama tokenizer with return_offsets_mapping=True
- **Mask caching**: Pre-compute masks during data loading for efficiency

The complete implementation is available in our supplementary materials.
