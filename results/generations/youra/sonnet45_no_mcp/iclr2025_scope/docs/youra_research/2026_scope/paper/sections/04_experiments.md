# Experimental Setup

We design experiments to answer three core research questions that test our hypothesis about task heterogeneity and oracle gap existence.

## Research Questions

**RQ1: Does an oracle gap G_o ≥ 10% exist between per-task optimal adapter rank selection and the best fixed-rank baseline?**

This is our primary research question. If the gap is negligible (< 10%), task-aware routing adds complexity for marginal benefit. But if the gap exceeds 10%, it validates that multi-domain benchmarks exhibit sufficient heterogeneity to justify adaptive configuration strategies.

**RQ2: Do different tasks genuinely prefer different adapter ranks, or does one rank dominate across tasks?**

Even if an oracle gap exists, it could reflect noise rather than systematic heterogeneity. If oracle selections cluster on a single rank (e.g., 15 of 17 tasks prefer rank-8), the gap might be artifact rather than genuine task diversity. We analyze oracle selection distribution to test whether heterogeneity is real.

**RQ3: Does rank-32 overfit on small datasets despite having the highest capacity?**

Literature consensus suggests rank 4-16 is sufficient for most tasks. We test rank-32 to verify whether higher capacity improves performance or causes overfitting when adapter parameters exceed data complexity. This question validates practical rank selection guidelines.

## Datasets

### GLUE Benchmark

We evaluate on 9 tasks from the General Language Understanding Evaluation (GLUE) benchmark (Wang et al., 2018):

| Task | Type | Metric | Train Samples | Description |
|------|------|--------|---------------|-------------|
| CoLA | Binary Classification | Matthew's Corr | 8,551 | Grammatical acceptability judgment |
| SST-2 | Binary Classification | Accuracy | 67,349 | Sentiment analysis |
| MRPC | Binary Classification | F1/Accuracy | 3,668 | Paraphrase detection |
| QQP | Binary Classification | F1/Accuracy | 363,846 | Question pair similarity |
| STS-B | Regression | Pearson Corr | 5,749 | Semantic textual similarity |
| MNLI | 3-class Classification | Accuracy | 392,702 | Natural language inference |
| QNLI | Binary Classification | Accuracy | 104,743 | Question-answering NLI |
| RTE | Binary Classification | Accuracy | 2,490 | Recognizing textual entailment |
| WNLI | Binary Classification | Accuracy | 635 | Winograd Schema NLI |

**Why GLUE:** Designed explicitly for task diversity, GLUE spans multiple linguistic phenomena (sentiment, paraphrase, entailment, similarity) and dataset sizes (635 to 392,702 samples)—three orders of magnitude variation. This diversity enables testing whether task heterogeneity creates optimization opportunities.

### XTREME Subset

We evaluate cross-lingual transfer on tasks from the Cross-lingual TRansfer Evaluation of Multilingual Encoders (XTREME) benchmark (Hu et al., 2020):

| Task | Languages | Metric | Train Samples (en) | Description |
|------|-----------|--------|-------------------|-------------|
| XNLI | en, es, de, zh | Accuracy | 392,702 | Cross-lingual NLI (zero-shot transfer) |
| PAWS-X | en, es, de, zh | Accuracy | 49,401 | Cross-lingual paraphrase detection |

**Why XTREME subset:** Cross-lingual tasks test whether linguistic diversity (English vs Spanish vs German vs Chinese) creates heterogeneous capacity requirements. We train on English and evaluate zero-shot transfer to other languages, yielding 8 cross-lingual evaluation conditions (4 languages × 2 tasks).

**Total: 17 tasks** (9 GLUE + 8 XTREME evaluations)

This task suite spans:
- **Domains**: Sentiment, acceptability, paraphrase, similarity, natural language inference, cross-lingual transfer
- **Dataset sizes**: 635 to 392,702 samples (500× variation)
- **Task types**: Binary classification, 3-class classification, regression
- **Linguistic phenomena**: Surface patterns, lexical semantics, compositional semantics, cross-lingual generalization

## Baselines

**Fixed-Rank Baselines:** We train LoRA adapters with fixed ranks {4, 8, 16, 32} applied uniformly across all tasks. Each fixed rank serves as a baseline representing current practice (choose one rank globally).

- **Rank-4**: 32,768 parameters, lowest capacity
- **Rank-8**: 65,536 parameters, literature consensus choice
- **Rank-16**: 131,072 parameters, high capacity
- **Rank-32**: 262,144 parameters, tests overfitting hypothesis

The best-performing fixed rank (by average accuracy across all tasks) serves as the primary baseline for oracle gap computation.

**Oracle (Upper Bound):** For each task, we select the best-performing rank from {4, 8, 16, 32}. The oracle represents perfect task-aware rank selection with hindsight—an upper bound on what adaptive routing could achieve.

**Rationale:** Comparing oracle to best fixed rank quantifies the maximum performance improvement available through task-aware adapter selection, establishing whether the optimization opportunity is substantial (≥10%) or negligible.

## Implementation Details

**Base Model:** LLaMA-2-7B (Touvron et al., 2023), a decoder-only transformer with 7 billion parameters.

**LoRA Configuration:**
- Ranks tested: {4, 8, 16, 32}
- LoRA alpha: 16
- LoRA dropout: 0.1
- Target modules: q_proj, v_proj (attention query and value projections)
- Bias: none

**Training Hyperparameters:**
```
Optimizer: AdamW
Learning rate: 3e-4
Weight decay: 0.01
Scheduler: Cosine annealing with warmup
Warmup ratio: 0.1
Batch size: 16
Gradient accumulation steps: 2
Effective batch size: 32
Max sequence length: 512
Epochs: 3-5 (task-dependent, early stopping patience 2)
Random seed: 42
```

**Uniform Protocol Rationale:** We use identical hyperparameters across all 68 configurations (17 tasks × 4 ranks) to ensure performance differences reflect genuine capacity-data interactions rather than confounded tuning. This choice potentially underestimates the oracle gap (rank-32 might perform better with careful regularization), making our measurement conservative.

**Compute Resources:**
- Hardware: Single NVIDIA A100 GPU (80GB)
- Training time per configuration: ~20-30 minutes (varies by dataset size)
- Total compute: 68 configurations × 25 min avg ≈ 28 GPU hours

**Implementation:** HuggingFace PEFT library for LoRA integration, Transformers library for model and dataset loading, PyTorch 2.0 for training.

## Evaluation Metrics

**Primary Metric:** Task accuracy (or Pearson correlation for STS-B regression, Matthew's correlation for CoLA).

**Oracle Gap Metrics:**

*Absolute gap (percentage points):*
```
Gap_abs = Oracle_avg - Best_fixed
```

*Relative gap (percentage improvement):*
```
Gap_rel = (Oracle_avg - Best_fixed) / Best_fixed × 100%
```

**Success Criterion:** Gap_rel ≥ 10% (MUST_WORK gate from hypothesis verification plan).

**Heterogeneity Metrics:**
- Oracle selection distribution across ranks
- Task-rank correlation analysis
- Chi-squared test against uniform distribution

**Statistical Considerations:** This is an EXISTENCE proof-of-concept using single-seed (42) directional validation. Multi-seed statistical testing with confidence intervals is deferred to future work validating routing mechanisms. Large effect sizes (>10 percentage points) with systematic patterns provide strong directional evidence even without formal hypothesis testing.
