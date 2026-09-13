# Methodology

Building on our observation that task structure exists in pretrained hidden states, we design TC-SSM as a four-stage pipeline: task discovery, embedding learning, SSM modulation, and conversion training with adaptation preservation.

## Overview

TC-SSM converts a transformer to a task-conditioned Mamba model while preserving few-shot adaptation capability. The key insight is that instead of converting first and adapting later, we identify task structure in the teacher, encode it into compact embeddings, and use those embeddings to condition the student's state dynamics during conversion.

```
Transformer hidden states → K-means clustering → InfoNCE training → Task embeddings
                                                                           ↓
Mamba SSM ← Low-rank Δ/B/C modulation ← Task conditioning ← Task embeddings
    ↓
Conversion training (KL + MSE + adaptation regularizer)
    ↓
TC-SSM with preserved adaptation capability
```

## Task Discovery via Clustering

**Rationale:** If task structure is already present in pretrained representations, we can discover it without supervision, avoiding the need for task labels during conversion.

We extract hidden states from the teacher transformer's final layer [CLS] embeddings across a diverse corpus. K-means clustering (K=8, matching SuperGLUE task count) partitions these representations. Our experiments show cluster purity 0.74 versus 0.20 random baseline, confirming that meaningful task structure emerges without labels.

The clustering step produces soft cluster assignments that serve as pseudo-task labels for the embedding learning stage. This self-supervised approach enables TC-SSM to work with unlabeled conversion data.

## Task Embedding Learning

**Rationale:** Cluster assignments must be transformed into dense embeddings that capture task-discriminative features for SSM modulation.

We train a task embedding layer using InfoNCE contrastive loss:

$$\mathcal{L}_{\text{InfoNCE}} = -\log \frac{\exp(z_i \cdot z_j^+ / \tau)}{\sum_k \exp(z_i \cdot z_k / \tau)}$$

where positive pairs $(z_i, z_j^+)$ share the same cluster assignment and negatives are sampled from other clusters. This encourages embeddings that distinguish task-relevant patterns.

We use embedding dimension 32 (optimal in ablation) with learned projection from the 768-dimensional hidden states. A linear probe on frozen embeddings achieves 29.21% accuracy on 6-way task classification (versus 16.67% random), confirming the embeddings encode discriminable structure.

## Low-Rank SSM Modulation

**Rationale:** Task conditioning must integrate efficiently into SSM dynamics without excessive computational overhead.

Mamba's selective state space computes state update parameters Δ, B, and C from input features via linear projections. We modulate these parameters based on task embeddings using low-rank projections:

$$\Delta' = \Delta + W_\Delta^{\text{down}} \cdot e_{\text{task}} \cdot W_\Delta^{\text{up}}$$
$$B' = B + W_B^{\text{down}} \cdot e_{\text{task}} \cdot W_B^{\text{up}}$$
$$C' = C + W_C^{\text{down}} \cdot e_{\text{task}} \cdot W_C^{\text{up}}$$

where $e_{\text{task}}$ is the task embedding and the down/up projections have rank 32. This LoRA-style modulation adds only 1.01x parameters. Counterintuitively, the modulated model runs at 0.85x vanilla Mamba inference time—likely due to improved memory bandwidth utilization from batched task conditioning.

The modulation is applied at each of the 24 Mamba layers, with task embeddings shared across sequence positions. An ANOVA test confirms state variance differs significantly across task embeddings (F=100.35, p<0.0001), validating that modulation produces task-conditioned dynamics.

## Conversion Training with Adaptation Preservation

**Rationale:** Standard distillation optimizes output matching, not adaptation preservation. We add an explicit regularizer.

The conversion loss combines three terms:

$$\mathcal{L} = \mathcal{L}_{\text{KL}} + \alpha \mathcal{L}_{\text{MSE}} + \beta \mathcal{L}_{\text{adapt}}$$

- **KL divergence** on logits ensures output fidelity to the teacher
- **MSE loss** on hidden states preserves internal representations
- **Adaptation regularizer** penalizes collapse of modulation across tasks:

$$\mathcal{L}_{\text{adapt}} = -\text{Var}_{\text{task}}[\Delta', B', C']$$

This regularizer ensures task conditioning remains active throughout training. Without it, the model may learn to ignore task embeddings and collapse to a single mode.

Training uses AdamW with learning rate 2e-5, batch size 8, and gradient clipping at 1.0. Task IDs are sampled per batch based on input content. We train for 2000 steps with checkpoints every 25 steps.

## Architecture Details

TC-SSM builds on Mamba-130M with the following modifications:

| Component | Specification |
|-----------|---------------|
| Base model | state-spaces/mamba-130m |
| Task embedding dim | 32 |
| Modulation rank | 32 |
| Number of tasks | 8 (K-means clusters) |
| Modified layers | All 24 Mamba blocks |
| Parameter overhead | 1.01x vanilla Mamba |

The task-conditioned block wraps the standard Mamba mixer, intercepting the x_proj output (which produces Δ, B, C) and applying low-rank modulation before the selective scan. This minimal modification preserves Mamba's efficient CUDA kernels while enabling task conditioning.
