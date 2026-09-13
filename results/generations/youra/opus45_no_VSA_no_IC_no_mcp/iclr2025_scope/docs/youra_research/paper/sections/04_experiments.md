# Experimental Setup

We design experiments to answer four research questions that progressively validate the TC-SSM mechanism:

**RQ1:** Does task-relevant structure exist in pretrained hidden states, discoverable without supervision?
**RQ2:** Can self-supervised embeddings capture task-discriminative patterns?
**RQ3:** Can low-rank modulation efficiently condition SSM dynamics?
**RQ4:** Does TC-SSM preserve adaptation capability compared to transformer baseline?

Each question maps to a stage in the TC-SSM pipeline and tests a specific claim from our hypothesis.

## Datasets

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

## Baselines

We compare against methods representing sequential conversion-then-adaptation approaches:

**Standard Distillation:** Knowledge distillation from BERT-base to Mamba-130M using KL divergence on logits and MSE on hidden states, without task conditioning. This isolates the contribution of our task-conditioned approach.

**Mamba + LoRA (post-hoc):** Vanilla Mamba-130M with LoRA adaptation (r=16, α=32) applied after training. This represents the conventional pipeline where conversion and adaptation are decoupled.

**Transformer baseline:** Fine-tuned BERT-base on each task. This establishes the adaptation capability ceiling that TC-SSM aims to preserve.

## Implementation Details

**Model architecture:** TC-SSM extends Mamba-130M (24 layers, d_model=768, d_state=16) with task-conditioned blocks. Task embeddings have dimension 32 with rank-32 modulation.

**Task discovery:** K-means clustering (K=8) on BERT-base [CLS] embeddings extracted from 660 validation samples across 5 SuperGLUE tasks.

**Embedding learning:** InfoNCE contrastive training with τ=0.1, trained for 10 epochs with AdamW (lr=1e-4, batch size 32).

**Conversion training:** 2000 steps with combined loss (KL + 0.5×MSE + 0.1×adaptation regularizer), AdamW (lr=2e-5), batch size 8, gradient clipping at 1.0.

**Few-shot adaptation:** Maximum 100 gradient steps, AdamW (lr=2e-5), batch size 8. We measure steps to reach 95% of fine-tuned ceiling accuracy.

**Hardware:** Single NVIDIA A100 GPU. Conversion training completes in approximately 4 hours.

## Evaluation Metrics

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
