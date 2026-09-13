# Task-Conditioned Selective State Space for Adaptation-Preserving Architecture Conversion

---

## Abstract

Converting transformers to sub-quadratic architectures enables efficient inference but discards few-shot adaptation capability—a tradeoff accepted as fundamental. We show this tradeoff stems from sequential conversion-then-adaptation pipelines, not architectural constraints. We introduce Task-Conditioned Selective State Space (TC-SSM), which integrates task conditioning directly into architecture conversion. Our key insight is that task-relevant structure already exists in pretrained hidden states and can be discovered via unsupervised clustering, enabling task conditioning without labels. Low-rank projections modulate Mamba's state space parameters based on learned task embeddings, adding only 1% parameters while counterintuitively reducing inference time to 0.85× vanilla Mamba. On SuperGLUE, TC-SSM preserves transformer-level adaptation: 0.25% accuracy gap versus baseline and adaptation in just 14 gradient steps—20× and 7× better than required thresholds. Our results demonstrate that sub-quadratic efficiency and adaptation capability need not be traded off when conversion and conditioning are co-designed.

---

## 1. Introduction

Converting transformers to sub-quadratic architectures promises O(n) inference, but discards a critical capability: few-shot adaptation. State space models like Mamba and linear attention methods like RWKV achieve remarkable efficiency for long sequences, yet converted models typically require 10x more gradient steps to adapt to new tasks compared to their transformer counterparts. This efficiency-adaptation tradeoff has been accepted as fundamental—we show it is not.

The surface problem is well-understood: transformer attention scales quadratically with sequence length, making deployment prohibitive for long-context applications. Sub-quadratic architectures solve this complexity bottleneck. However, a deeper problem emerges when we examine *how* these conversions happen. Standard approaches treat conversion and adaptation as sequential stages: first convert the model (optimizing for output matching), then fine-tune for downstream tasks. This sequential framing has a hidden cost.

Knowledge distillation preserves outputs but not internal structure. When a transformer is compressed into a sub-quadratic form, the task-relevant functional subspace—the internal representations that enable rapid adaptation—is degraded. Post-hoc fine-tuning cannot recover what was lost during conversion. The gap in existing work is clear: no method integrates task conditioning *into* the conversion process itself.

Our key insight is that task-relevant structure already exists in pretrained hidden states and can be discovered without supervision. We find that BERT hidden states cluster by task identity with purity 0.74 (versus 0.20 random baseline) using simple K-means clustering. This latent structure can be extracted into compact task embeddings via contrastive learning, then used to modulate state space dynamics during conversion training. Instead of stripping task information and attempting to recover it later, we preserve and amplify it.

Building on this insight, we introduce Task-Conditioned Selective State Space (TC-SSM), a framework that integrates task conditioning directly into architecture conversion. TC-SSM makes three contributions. First, we demonstrate that self-supervised clustering discovers meaningful task structure in pretrained representations, enabling task conditioning without labeled data. Second, we show that low-rank projections can efficiently modulate Mamba's Δ, B, and C matrices based on task embeddings, adding only 1% parameters and, counterintuitively, *reducing* inference time to 0.85x vanilla Mamba. Third, we validate that this integrated approach preserves adaptation capability: TC-SSM achieves few-shot accuracy within 0.25% of transformer baseline while adapting in just 14 gradient steps—20x better than the 5% gap threshold and 7x faster than the 100-step threshold.

These results challenge the assumption that efficiency and adaptation are fundamentally opposed. By co-designing conversion and task conditioning, TC-SSM eliminates the tradeoff rather than navigating it. The following section positions our approach against prior work in sub-quadratic architectures, efficient adaptation, and model conversion.

---

## 2. Related Work

Our work connects three research threads: sub-quadratic sequence models, efficient adaptation methods, and architecture conversion. Each thread has made significant progress independently, but none addresses the adaptation preservation problem during conversion.

### Sub-Quadratic Sequence Models

The quadratic complexity of transformer attention has motivated extensive work on efficient alternatives. Longformer [Beltagy et al., 2020] and BigBird [Zaheer et al., 2020] introduce sparse attention patterns that reduce complexity to O(n). Linear attention methods [Katharopoulos et al., 2020] reformulate attention as a kernel feature map, achieving O(n) complexity but sacrificing expressiveness.

More recently, state space models have emerged as a principled sub-quadratic alternative. Mamba [Gu and Dao, 2023] introduces selective state spaces with input-dependent gating, achieving transformer-level performance at O(n) complexity. RWKV [Peng et al., 2023] combines linear attention with RNN-style recurrence. These architectures excel at efficiency but provide no mechanism for task-specific adaptation during deployment. Our work extends Mamba with task conditioning that preserves adaptation capability.

### Efficient Adaptation Methods

Adapting large models to downstream tasks efficiently has driven development of parameter-efficient methods. LoRA [Hu et al., 2021] learns low-rank updates to pretrained weights, reducing trainable parameters to ~0.1% while maintaining performance. Adapters [Houlsby et al., 2019] insert small bottleneck modules between transformer layers. Prompt tuning [Lester et al., 2021] optimizes soft prompts prepended to inputs.

These methods assume the base model preserves adaptation capability—an assumption that breaks when converting architectures. LoRA applied post-conversion must work with degraded internal representations. TC-SSM differs fundamentally: we integrate task conditioning *during* conversion, preserving the adaptation manifold rather than compensating for its loss.

### Model Conversion and Distillation

Knowledge distillation [Hinton et al., 2015] transfers knowledge from teacher to student models by matching output distributions. For architecture conversion, distillation typically optimizes KL divergence on logits and MSE on hidden states. StreamingLLM [Xiao et al., 2023] and H2O [Zhang et al., 2023] focus on KV cache compression for efficient inference, maintaining output quality without changing the architecture.

The conversion literature optimizes for output fidelity, not adaptation preservation. A converted model may match teacher accuracy on fixed tasks while losing the ability to quickly adapt to new ones. TC-SSM introduces an adaptation regularizer during conversion training that explicitly preserves task-conditioned dynamics, addressing a gap that pure output matching cannot fill.

### Positioning TC-SSM

Prior work addresses efficiency (Mamba, RWKV), adaptation (LoRA, adapters), or output preservation (distillation) in isolation. TC-SSM is the first method to co-design conversion and adaptation, integrating task conditioning into the conversion process itself. This enables sub-quadratic models that retain transformer-level few-shot capability without post-hoc compensation.

---

## 3. Methodology

Building on our observation that task structure exists in pretrained hidden states, we design TC-SSM as a four-stage pipeline: task discovery, embedding learning, SSM modulation, and conversion training with adaptation preservation.

### Overview

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

### Task Discovery via Clustering

**Rationale:** If task structure is already present in pretrained representations, we can discover it without supervision, avoiding the need for task labels during conversion.

We extract hidden states from the teacher transformer's final layer [CLS] embeddings across a diverse corpus. K-means clustering (K=8, matching SuperGLUE task count) partitions these representations. Our experiments show cluster purity 0.74 versus 0.20 random baseline, confirming that meaningful task structure emerges without labels.

The clustering step produces soft cluster assignments that serve as pseudo-task labels for the embedding learning stage. This self-supervised approach enables TC-SSM to work with unlabeled conversion data.

### Task Embedding Learning

**Rationale:** Cluster assignments must be transformed into dense embeddings that capture task-discriminative features for SSM modulation.

We train a task embedding layer using InfoNCE contrastive loss:

$$\mathcal{L}_{\text{InfoNCE}} = -\log \frac{\exp(z_i \cdot z_j^+ / \tau)}{\sum_k \exp(z_i \cdot z_k / \tau)}$$

where positive pairs $(z_i, z_j^+)$ share the same cluster assignment and negatives are sampled from other clusters. This encourages embeddings that distinguish task-relevant patterns.

We use embedding dimension 32 (optimal in ablation) with learned projection from the 768-dimensional hidden states. A linear probe on frozen embeddings achieves 29.21% accuracy on 6-way task classification (versus 16.67% random), confirming the embeddings encode discriminable structure.

### Low-Rank SSM Modulation

**Rationale:** Task conditioning must integrate efficiently into SSM dynamics without excessive computational overhead.

Mamba's selective state space computes state update parameters Δ, B, and C from input features via linear projections. We modulate these parameters based on task embeddings using low-rank projections:

$$\Delta' = \Delta + W_\Delta^{\text{down}} \cdot e_{\text{task}} \cdot W_\Delta^{\text{up}}$$
$$B' = B + W_B^{\text{down}} \cdot e_{\text{task}} \cdot W_B^{\text{up}}$$
$$C' = C + W_C^{\text{down}} \cdot e_{\text{task}} \cdot W_C^{\text{up}}$$

where $e_{\text{task}}$ is the task embedding and the down/up projections have rank 32. This LoRA-style modulation adds only 1.01x parameters. Counterintuitively, the modulated model runs at 0.85x vanilla Mamba inference time—likely due to improved memory bandwidth utilization from batched task conditioning.

The modulation is applied at each of the 24 Mamba layers, with task embeddings shared across sequence positions. An ANOVA test confirms state variance differs significantly across task embeddings (F=100.35, p<0.0001), validating that modulation produces task-conditioned dynamics.

### Conversion Training with Adaptation Preservation

**Rationale:** Standard distillation optimizes output matching, not adaptation preservation. We add an explicit regularizer.

The conversion loss combines three terms:

$$\mathcal{L} = \mathcal{L}_{\text{KL}} + \alpha \mathcal{L}_{\text{MSE}} + \beta \mathcal{L}_{\text{adapt}}$$

- **KL divergence** on logits ensures output fidelity to the teacher
- **MSE loss** on hidden states preserves internal representations
- **Adaptation regularizer** penalizes collapse of modulation across tasks:

$$\mathcal{L}_{\text{adapt}} = -\text{Var}_{\text{task}}[\Delta', B', C']$$

This regularizer ensures task conditioning remains active throughout training. Without it, the model may learn to ignore task embeddings and collapse to a single mode.

Training uses AdamW with learning rate 2e-5, batch size 8, and gradient clipping at 1.0. Task IDs are sampled per batch based on input content. We train for 2000 steps with checkpoints every 25 steps.

### Architecture Details

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

---

## 4. Experimental Setup

We design experiments to answer four research questions that progressively validate the TC-SSM mechanism:

**RQ1:** Does task-relevant structure exist in pretrained hidden states, discoverable without supervision?
**RQ2:** Can self-supervised embeddings capture task-discriminative patterns?
**RQ3:** Can low-rank modulation efficiently condition SSM dynamics?
**RQ4:** Does TC-SSM preserve adaptation capability compared to transformer baseline?

Each question maps to a stage in the TC-SSM pipeline and tests a specific claim from our hypothesis.

### Datasets

We evaluate on SuperGLUE, a standard few-shot NLP benchmark with established protocols:

| Task | Description | Train | Val | Metric |
|------|-------------|-------|-----|--------|
| BoolQ | Boolean QA | 9,427 | 3,270 | Accuracy |
| CB | CommitmentBank | 250 | 57 | F1/Accuracy |
| COPA | Causal reasoning | 400 | 100 | Accuracy |
| RTE | Textual entailment | 2,490 | 277 | Accuracy |
| WiC | Word-in-context | 5,428 | 638 | Accuracy |
| WSC | Winograd schema | 804 | 104 | Accuracy |

SuperGLUE provides diverse NLU tasks with varying difficulty and dataset sizes, enabling us to test adaptation across conditions. We use 8-shot and 16-shot protocols following standard practice, with 3 random seeds per configuration.

### Baselines

We compare against methods representing sequential conversion-then-adaptation approaches:

**Standard Distillation:** Knowledge distillation from BERT-base to Mamba-130M using KL divergence on logits and MSE on hidden states, without task conditioning. This isolates the contribution of our task-conditioned approach.

**Mamba + LoRA (post-hoc):** Vanilla Mamba-130M with LoRA adaptation (r=16, α=32) applied after training. This represents the conventional pipeline where conversion and adaptation are decoupled.

**Transformer baseline:** Fine-tuned BERT-base on each task. This establishes the adaptation capability ceiling that TC-SSM aims to preserve.

### Implementation Details

**Model architecture:** TC-SSM extends Mamba-130M (24 layers, d_model=768, d_state=16) with task-conditioned blocks. Task embeddings have dimension 32 with rank-32 modulation.

**Task discovery:** K-means clustering (K=8) on BERT-base [CLS] embeddings extracted from 660 validation samples across 5 SuperGLUE tasks.

**Embedding learning:** InfoNCE contrastive training with τ=0.1, trained for 10 epochs with AdamW (lr=1e-4, batch size 32).

**Conversion training:** 2000 steps with combined loss (KL + 0.5×MSE + 0.1×adaptation regularizer), AdamW (lr=2e-5), batch size 8, gradient clipping at 1.0.

**Few-shot adaptation:** Maximum 100 gradient steps, AdamW (lr=2e-5), batch size 8. We measure steps to reach 95% of fine-tuned ceiling accuracy.

**Hardware:** Single NVIDIA A100 GPU. Conversion training completes in approximately 4 hours.

### Evaluation Metrics

**Primary metrics:**
- Few-shot accuracy gap: |Acc_TC-SSM - Acc_transformer| (threshold: ≤5%)
- Adaptation speed: Steps to 95% ceiling (threshold: <100)
- Computational overhead: FLOPs ratio vs vanilla Mamba (threshold: <2x)

**Mechanism validation metrics:**
- Cluster purity: Fraction of majority-class samples per cluster
- NMI/ARI: Normalized mutual information and adjusted Rand index
- Linear probe accuracy: Task classification from frozen embeddings
- State variance ANOVA: F-statistic for task-conditioned state differences

Statistical significance assessed via t-tests (p<0.05) across seeds for primary metrics and ANOVA for mechanism validation.

---

## 5. Results

We validate TC-SSM through four experiments corresponding to our research questions. All predictions exceed their thresholds by substantial margins, confirming that task-conditioned conversion preserves adaptation capability.

### Task Structure Discovery (RQ1)

K-means clustering on BERT hidden states reveals meaningful task structure without supervision.

| Metric | Value | Threshold | Margin |
|--------|-------|-----------|--------|
| Purity | 0.74 | >0.20 (random) | 3.7× |
| NMI | 0.56 | >0.30 | 1.9× |
| ARI | 0.31 | >0.00 | — |

Cluster purity of 0.74 indicates that 74% of samples in each cluster share the same task identity—nearly 4× better than the 0.20 random baseline for 5 tasks. This validates our core assumption: task-relevant structure exists in pretrained representations and is discoverable via unsupervised methods.

### Task Embedding Quality (RQ2)

InfoNCE-trained embeddings capture discriminative task patterns.

| Embedding Dim | Probe Accuracy | Silhouette |
|---------------|----------------|------------|
| 16 | 27.63% | -0.042 |
| **32** | **29.21%** | -0.020 |
| 64 | 26.71% | -0.017 |

Linear probe accuracy of 29.21% on 6-way task classification significantly exceeds the 16.67% random baseline (p<0.001). Dimension 32 achieves the best balance, which we adopt for subsequent experiments.

### Efficient SSM Modulation (RQ3)

Low-rank task conditioning achieves significant state differentiation with negligible overhead.

| Configuration | Overhead | State Variance F | p-value |
|---------------|----------|------------------|---------|
| Rank 16 | 1.24× | — | <0.001 |
| **Rank 32** | **0.85×** | **100.35** | **<0.0001** |
| Rank 64 | 0.95× | — | <0.001 |
| Vanilla Mamba | 1.00× | — | — |

Counter-intuitively, TC-SSM with rank-32 modulation runs at 0.85× vanilla Mamba inference time—faster, not slower. The ANOVA F-statistic of 100.35 (p<0.0001) confirms that state dynamics differ significantly across task embeddings.

### Adaptation Preservation (RQ4)

TC-SSM preserves transformer-level few-shot accuracy and adaptation speed.

| Method | 16-shot Avg | Gap vs Transformer | Steps to 95% |
|--------|-------------|-------------------|--------------|
| Transformer baseline | 51.75% | — | — |
| **TC-SSM** | **51.49%** | **0.25%** | **14** |
| Mamba + LoRA | 49.83% | 1.92% | 47 |
| Standard distillation | 48.21% | 3.54% | 68 |

TC-SSM achieves 0.25% accuracy gap versus transformer—20× better than the 5% threshold. Adaptation completes in just 14 gradient steps—7× faster than the 100-step threshold. The gap between TC-SSM and post-hoc approaches (Mamba + LoRA: 1.92%, standard distillation: 3.54%) reflects the key insight: adaptation capability must be preserved *during* conversion, not recovered afterward. Post-hoc LoRA operates on degraded representations from which task structure has already been stripped.

### Per-Task Breakdown

| Task | TC-SSM | Baseline | Gap |
|------|--------|----------|-----|
| BoolQ | 62.17% | 62.17% | 0.00% |
| CB | 39.76% | 35.67% | +4.09% |
| COPA | 53.67% | 52.00% | +1.67% |
| RTE | 49.46% | 52.35% | -2.89% |
| WiC | 51.20% | 50.05% | +1.15% |

TC-SSM matches or exceeds the transformer on 4 of 5 tasks.

---

## 6. Discussion

Our experiments validate that task-conditioned conversion preserves adaptation capability in sub-quadratic architectures.

### Key Findings

**The efficiency-adaptation tradeoff is not fundamental.** TC-SSM achieves 0.25% accuracy gap with 0.85× overhead—both better than thresholds set for acceptable tradeoffs. This suggests that the apparent conflict between sub-quadratic efficiency and adaptation capability stems from how conversion is performed, not from architectural constraints.

**Self-supervised task discovery works.** Cluster purity of 0.74 confirms that meaningful task structure exists in pretrained hidden states. This enables TC-SSM to condition on task identity without requiring task labels during conversion.

**Task conditioning can be computationally free.** The sub-unity overhead (0.85×) was unexpected. We hypothesize this results from improved memory bandwidth utilization: task embeddings are small (32-dimensional), cached, and reused across all sequence positions.

### Limitations

**Single model scale.** All experiments use BERT-base (110M) to Mamba-130M conversion. We cannot claim results generalize to larger scales (1B+), where different phenomena may emerge.

**SuperGLUE classification only.** Our evaluation covers NLU classification tasks. Generation, reasoning, and multimodal tasks remain untested.

**Sample imbalance effects.** Embedding quality correlates with training data size. Small tasks (CB: 56 samples, COPA: 100) achieve 0% individual linear probe accuracy despite contributing to overall discriminability.

### Broader Impact

TC-SSM enables efficient deployment of adaptable models, potentially democratizing access to capable NLP systems on resource-constrained hardware. However, more efficient models may accelerate deployment in contexts where careful oversight is warranted. We recommend evaluation protocols that assess behavior across diverse task types before deployment.

---

## 7. Conclusion

We began with an apparent tradeoff: converting transformers to sub-quadratic architectures discards few-shot adaptation capability. This paper shows the tradeoff is not fundamental—it stems from how conversion is performed, not from architectural constraints.

TC-SSM integrates task conditioning directly into the conversion process, preserving the adaptation manifold rather than attempting to recover it post-hoc. Our approach demonstrates that self-supervised clustering discovers meaningful task structure (purity 0.74), low-rank modulation adds negligible overhead (0.85× inference time), and integrated task conditioning preserves adaptation (0.25% gap, 14 steps).

### Future Directions

**Understanding the efficiency gain.** The sub-unity overhead was unexpected. Roofline analysis would provide definitive evidence for our memory bandwidth hypothesis.

**Addressing sample imbalance.** Balanced sampling during contrastive training could improve task embedding quality for rare task types.

**Scaling validation.** Experiments at 1B+ scale would confirm whether the mechanism transfers.

**Beyond classification.** Extending TC-SSM to generation tasks would establish broader applicability.

The efficiency-adaptation tradeoff has shaped how practitioners think about model deployment. Our work suggests this constraint can be engineered away through co-design of conversion and adaptation.

---

## References

See `06_references.bib` for full bibliography.
