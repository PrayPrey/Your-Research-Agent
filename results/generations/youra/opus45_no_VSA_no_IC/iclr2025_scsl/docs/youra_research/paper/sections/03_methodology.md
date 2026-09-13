# Methodology

Building on our observation that efficiency claims require mechanism-level validation, we design both a temporal dynamic attention architecture and a verification framework for testing whether proposed mechanisms actually operate.

## Overview

Our approach has two components:

1. **Temporal Dynamic Attention:** An attention mechanism where weights evolve across T internal steps within each layer, with K and V projections computed once and Q reprojected at each step.

2. **Sub-Hypothesis Verification:** A framework decomposing the efficiency claim into four testable sub-hypotheses with explicit gates and falsification criteria.

## Temporal Dynamic Attention Architecture

### Design Rationale

Standard attention computes Q, K, V projections once per layer, applies softmax, and outputs. We hypothesize that allowing attention weights to *evolve* across internal time steps could reduce redundant computation—if temporal refinement converges toward task-relevant patterns, fewer full recomputations may be needed.

**Core architecture:**
```
Input: X ∈ R^{seq_len × d_model}

Q₁ = X·W_Q,  K = X·W_K,  V = X·W_V    # Initial projections

For t = 1 to T:
    A_t = softmax(Q_t · K^T / √d_k)    # Attention weights
    Q_{t+1} = gate(Q_t, A_t · V · W_Q') # Query refinement

Output = A_T · V · W_O
```

**Key design decisions:**

1. **K/V reuse:** K and V are computed once and reused across temporal steps. This amortizes projection cost.
   - *Rationale:* K/V capture input content; only Q (the query) needs refinement.

2. **Learned gating:** A gating mechanism controls how much each temporal step modifies Q.
   - *Rationale:* Prevents unbounded divergence; allows learning when refinement helps.

3. **Configurable T:** The number of temporal steps is a hyperparameter (T ∈ {1, 2, 3, ...}).
   - *Rationale:* Enables testing the efficiency-vs-quality tradeoff at different iteration counts.

### Computational Cost Analysis

```
Standard Attention:
  FLOPs = Q_proj + K_proj + V_proj + Attention + O_proj

Temporal (T steps):
  FLOPs = Q_proj + K_proj + V_proj + T × (Q_reproj + Attention) + O_proj
```

Reducing T from 3 to 2 removes 1/3 of the iterative overhead. Since Q reprojection (W_Q') is cheaper than full Q/K/V projection, overhead per step is bounded.

**Why this could work:** If temporal steps refine attention toward stable patterns, fewer steps might suffice after training. If convergence occurs, T can be reduced at inference time.

**Why this might not work:** If temporal overhead exceeds savings, or if convergence doesn't occur, the mechanism provides no benefit.

## Sub-Hypothesis Verification Framework

Rather than evaluating only end-to-end efficiency, we decompose our claim into four sub-hypotheses:

### H-E1: Existence (MUST_WORK Gate)

**Statement:** Temporal dynamic attention can be implemented and trains stably.

**Variables:**
- IV: Presence of temporal dynamics
- DV: Training convergence (loss decreases)
- CV: Model size, dataset, optimizer

**Success criteria:**
- Model perplexity within 10% of baseline
- No gradient explosion (norm < 100)
- Training completes without numerical instability

**If FAIL:** Core mechanism infeasible; STOP pipeline.

### H-M1: Mechanism - Efficiency (MUST_WORK Gate)

**Statement:** Reducing temporal steps decreases FLOPs while maintaining perplexity.

**Variables:**
- IV: Number of temporal steps T ∈ {2, 3}
- DV: FLOP count, perplexity
- CV: Sequence length, model architecture

**Success criteria:**
- FLOP reduction ≥ 10%
- Perplexity within ±5% of T=3 baseline

**If FAIL:** Efficiency claim not validated.

### H-M2: Mechanism - Convergence (SHOULD_WORK Gate)

**Statement:** Attention patterns converge (entropy decreases) across temporal steps.

**Variables:**
- IV: Temporal step index (1, 2, ..., T)
- DV: Attention entropy
- CV: Input sequence, layer

**Success criteria:**
- Entropy reduction > 5% from step 1 to final step
- Consistent convergence across sequences

**If FAIL:** Convergence hypothesis falsified, but efficiency may still hold through other mechanisms.

### H-C1: Condition - Scaling (SHOULD_WORK Gate)

**Statement:** Efficiency gains scale with sequence length.

**Variables:**
- IV: Sequence length (128, 512, 1024)
- DV: FLOP reduction percentage
- CV: Model architecture

**Success criteria:**
- Positive scaling coefficient (efficiency increases with seq_len)

**If FAIL:** Efficiency is constant, not scaling.

### Gate Hierarchy

```
MUST_WORK gates (H-E1, H-M1):
  Failure → Pipeline stops, core claim invalid

SHOULD_WORK gates (H-M2, H-C1):
  Failure → Continue with limitation noted
            Mechanism/condition falsified, but core may hold
```

This hierarchy allows distinguishing between *core* efficiency results and *proposed* mechanistic explanations.

## Implementation

We implement temporal dynamic attention in PyTorch, modifying the standard multi-head attention module:

```python
class TemporalAttention(nn.Module):
    def __init__(self, d_model, n_heads, T_steps=3):
        super().__init__()
        self.T_steps = T_steps
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_q_refine = nn.Linear(d_model, d_model)
        self.gate = nn.Sequential(
            nn.Linear(d_model * 2, d_model),
            nn.Sigmoid()
        )
        self.W_o = nn.Linear(d_model, d_model)

    def forward(self, x):
        Q = self.W_q(x)
        K = self.W_k(x)
        V = self.W_v(x)

        for t in range(self.T_steps):
            A = F.softmax(Q @ K.T / sqrt(d_k), dim=-1)
            context = A @ V
            Q_new = self.W_q_refine(context)
            g = self.gate(torch.cat([Q, Q_new], dim=-1))
            Q = g * Q_new + (1 - g) * Q

        A_final = F.softmax(Q @ K.T / sqrt(d_k), dim=-1)
        return self.W_o(A_final @ V)
```

Training uses standard language modeling on WikiText-103 with AdamW optimizer. FLOP profiling uses `thop` library. Attention entropy computed as H = -Σ p log p over attention distributions.

Figure 1 shows training loss curves demonstrating stable convergence of the temporal attention mechanism.
