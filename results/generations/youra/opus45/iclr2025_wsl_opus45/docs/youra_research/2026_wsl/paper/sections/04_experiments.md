# Experimental Setup

We design experiments to answer three research questions that map directly to our claims:

**RQ1 (Existence):** Do LoRA adapters trained on semantically similar tasks exhibit closer Grassmann distances than adapters trained on dissimilar tasks?

**RQ2 (Mechanism):** Does geometric similarity correlate with semantic similarity as defined by established task taxonomies?

**RQ3 (Layer Analysis):** Do specific transformer layer types (attention vs. MLP) show stronger task-similarity clustering?

## Tasks and Categories

We select 8 tasks spanning two FLAN categories to provide clear semantic separation:

| Category | Task | Description | # Train | Metric |
|----------|------|-------------|---------|--------|
| Reasoning | GSM8K | Grade school math | 7,473 | Accuracy |
| Reasoning | ARC-Challenge | Science QA | 1,119 | Accuracy |
| Reasoning | LogiQA | Logical reasoning | 7,376 | Accuracy |
| Reasoning | StrategyQA | Multi-hop reasoning | 2,290 | Accuracy |
| NLU | MNLI | Natural language inference | 392,702 | Accuracy |
| NLU | QQP | Paraphrase detection | 363,846 | F1 |
| NLU | SST-2 | Sentiment classification | 67,349 | Accuracy |
| NLU | MRPC | Semantic similarity | 3,668 | F1 |

**Task selection rationale:** These tasks represent well-established benchmarks with clear FLAN category assignments. Reasoning tasks require multi-step inference, while NLU tasks focus on linguistic understanding---providing distinct functional requirements that should manifest in adapter geometry if our hypothesis holds.

## Adapter Generation

### Base Model

We use TinyLlama-1.1B-Chat-v1.0 as our base model:
- **Architecture:** LLaMA-style transformer with 22 layers
- **Parameters:** 1.1B total, 4.2M trainable per adapter
- **Verification:** SHA-256 hash verified to ensure identical initialization across all adapters

**Model selection rationale:** TinyLlama provides a balance between computational tractability (enabling 40 adapter trainings) and architectural representativeness (standard LLaMA architecture used in larger models).

### Training Configuration

All adapters share identical LoRA and training configurations:

| Parameter | Value |
|-----------|-------|
| LoRA rank ($r$) | 32 |
| LoRA alpha ($\alpha$) | 64 |
| LoRA dropout | 0.05 |
| Target modules | q_proj, k_proj, v_proj, o_proj, up_proj, down_proj, gate_proj |
| Learning rate | $2 \times 10^{-4}$ |
| Batch size | 8 |
| Epochs | 3 |
| Optimizer | AdamW |
| Warmup ratio | 0.1 |
| Max sequence length | 512 |
| Gradient accumulation | 4 |

### Seed Variants

For each task, we train 5 adapters with different random seeds (42, 43, 44, 45, 46), yielding:
- **Total adapters:** 8 tasks $\times$ 5 seeds = 40 adapters
- **Within-category pairs:** $2 \times \binom{20}{2} = 380$ pairs
- **Between-category pairs:** $20 \times 20 = 400$ pairs
- **Within-task pairs:** $8 \times \binom{5}{2} = 80$ pairs (for P3 control)

### Compute Resources

- **Hardware:** NVIDIA H100 NVL (95,830 MiB)
- **Training time:** ~3.4 minutes per adapter
- **Total training time:** ~2 hours 14 minutes for all 40 adapters

## Evaluation Protocol

### Grassmann Distance Computation

For each adapter pair $(i, j)$:

1. Extract $B$ matrices for all 154 layer-module combinations (7 modules $\times$ 22 layers)
2. Compute Grassmann distance per layer using `scipy.linalg.subspace_angles`
3. Aggregate across layers using mean pooling

### Statistical Tests

**RQ1 (Existence):** Mann-Whitney U test comparing within-category vs. between-category distance distributions. Success criterion: $p < 0.05$ and Cohen's $d > 0.5$.

**RQ2 (Mechanism):** Spearman rank correlation between Grassmann distances and FLAN taxonomy distances (binary: 0 = same category, 1 = different category). Success criterion: $\rho > 0.3$ with $p < 0.05$.

**RQ3 (Layer Analysis):** Per-layer-type Cohen's $d$ computation. Success criterion: at least one layer type with $d > 0.8$.

### Control Condition (P3)

To verify that task signal exceeds training stochasticity, we compare:
- **Within-task distance:** Mean distance between adapters trained on the same task with different seeds
- **Within-category distance:** Mean distance between adapters trained on different tasks in the same category

Success criterion: within-task distance $< 0.5 \times$ within-category distance.

## Baselines and Reference Points

### Random Baseline

Expected Grassmann distance between random orthonormal subspaces of dimension $r$ in $\mathbb{R}^d$, computed analytically as a reference point.

### Uncontrolled Comparison

As context for our controlled results, we note that previous uncontrolled experiments using public HuggingFace adapters yielded $d = 0.91$ but $p = 0.127$ due to provenance confounds and insufficient sample size.
