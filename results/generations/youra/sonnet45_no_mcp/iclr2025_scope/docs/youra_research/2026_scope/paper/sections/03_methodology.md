# Methodology

To measure the oracle gap from task-specific adapter rank selection, we need systematic training of all rank-task configurations across a multi-domain benchmark. This section describes our experimental methodology: dataset selection, adapter configuration space, training protocol, and oracle gap computation.

## Overview

Our approach tests the hypothesis that multi-domain benchmarks exhibit sufficient task heterogeneity to create measurable optimization opportunities through per-task adapter rank selection. We train LoRA adapters with ranks {4, 8, 16, 32} on each of 17 tasks from GLUE and XTREME, creating 68 total configurations. For each task, we identify the best-performing rank (oracle) and compare the oracle average across tasks to the best fixed-rank baseline.

**Key insight:** If all tasks preferred the same rank, oracle selections would cluster on a single value and the gap would be negligible. But if optimal ranks distribute across the configuration space, it proves that different tasks genuinely require different capacity levels—validating the heterogeneity hypothesis and quantifying the cost of fixed configurations.

## Multi-Domain Benchmark Selection

We select tasks from GLUE (Wang et al., 2018) and XTREME (Hu et al., 2020) to span diverse domains, dataset sizes, and linguistic phenomena.

### GLUE Tasks

GLUE provides 9 standard NLP understanding tasks:

- **CoLA** (Acceptability): Binary grammatical acceptability judgment, 8,551 training samples
- **SST-2** (Sentiment): Binary sentiment classification, 67,349 training samples  
- **MRPC** (Paraphrase): Paraphrase detection, 3,668 training samples
- **QQP** (Paraphrase): Quora question pair similarity, 363,846 training samples
- **STS-B** (Similarity): Semantic textual similarity regression, 5,749 training samples
- **MNLI** (NLI): Multi-genre natural language inference, 392,702 training samples
- **QNLI** (NLI): Question-answering NLI, 104,743 training samples
- **RTE** (NLI): Recognizing textual entailment, 2,490 training samples
- **WNLI** (NLI): Winograd Schema Challenge NLI, 635 training samples

### XTREME Subset

To incorporate cross-lingual diversity without prohibitive computational cost, we select a representative XTREME subset:

- **XNLI** (Cross-lingual NLI): 4 languages (English, Spanish, German, Chinese), ~392K training samples each (English only for training, zero-shot transfer to others)
- **PAWS-X** (Cross-lingual Paraphrase): 4 languages (English, Spanish, German, Chinese), ~49K training samples each (English only for training, zero-shot transfer)

**Total: 17 tasks** (9 GLUE + 8 XTREME cross-lingual evaluations)

**Rationale:** This task suite spans:
- **Domains**: Sentiment, acceptability, paraphrase, similarity, natural language inference
- **Dataset sizes**: 635 samples (WNLI) to 392,702 samples (MNLI)—three orders of magnitude variation
- **Linguistic phenomena**: Surface patterns (sentiment), lexical semantics (paraphrase), compositional semantics (NLI), cross-lingual transfer
- **Task types**: Binary classification, multi-class classification, regression

If task heterogeneity creates optimization opportunities, this diversity should produce distributed oracle selections across ranks.

## Adapter Configuration Space

We test four LoRA ranks: **{4, 8, 16, 32}**.

**Rank selection rationale:**
- **Rank 4-16**: Literature consensus sweet spot (Hu et al., 2021). Most practitioners use this range.
- **Rank 32**: Tests overfitting hypothesis. If rank-32 performs poorly on small datasets despite having highest capacity (262,144 parameters vs rank-4's 32,768), it demonstrates capacity-data mismatch and validates need for task-adaptive selection.

### LoRA Configuration

We use standard LoRA hyperparameters across all experiments:

```
lora_alpha: 16
lora_dropout: 0.1  
target_modules: [q_proj, v_proj]  # Attention query and value projections
bias: none
task_type: sequence_classification
```

**Parameter scaling:** LoRA adds two matrices A ∈ R^(d×r) and B ∈ R^(r×d) per target module, where d=4096 (LLaMA-2-7B hidden dimension) and r=rank. With two target modules (q_proj, v_proj) across 32 layers:

- **Rank 4**: 32,768 parameters  
- **Rank 8**: 65,536 parameters
- **Rank 16**: 131,072 parameters
- **Rank 32**: 262,144 parameters

This O(d·r) scaling creates discrete capacity-efficiency trade-off points.

## Base Model and Training Protocol

**Base model:** LLaMA-2-7B (Touvron et al., 2023), a decoder-only transformer with 7 billion parameters, 32 layers, 4096 hidden dimensions, and 32 attention heads.

**Why LLaMA-2-7B:** Strong baseline performance on NLP benchmarks, widely used for LoRA experiments, sufficient capacity for multi-domain tasks without excessive compute requirements for exhaustive configuration training.

### Training Hyperparameters

We use a uniform training protocol across all 68 configurations to ensure fair comparison:

```
optimizer: AdamW
learning_rate: 3e-4
weight_decay: 0.01
scheduler: cosine annealing
warmup_ratio: 0.1
batch_size: 16
gradient_accumulation_steps: 2
effective_batch_size: 32
max_sequence_length: 512
epochs: 3-5 (task-dependent, early stopping with patience 2)
random_seed: 42
```

**Rationale for uniform protocol:** Using the same hyperparameters across all ranks and tasks ensures that performance differences reflect genuine capacity-data interactions, not confounded by rank-specific tuning. This choice potentially underestimates oracle gap (rank-32 might perform better with careful regularization), making our measurement conservative.

### Computational Requirements

- **Per configuration:** ~20-30 minutes on single A100 GPU (varies by dataset size)
- **Total compute:** 68 configurations × 25 min avg ≈ 28 GPU hours
- **Resource requirement:** Single GPU sufficient (sequential training acceptable for oracle gap measurement)

## Oracle Gap Computation

### Oracle Selection

For each task t, we define the **oracle rank** r*_t as the rank achieving highest validation accuracy:

```
r*_t = argmax_{r ∈ {4,8,16,32}} Accuracy_t(r)
```

The **oracle average** across all tasks is:

```
Oracle_avg = (1/|T|) Σ_{t ∈ T} Accuracy_t(r*_t)
```

where |T| = 17 tasks.

### Fixed-Rank Baselines

For each fixed rank r, we compute the **average accuracy** across all tasks:

```
Fixed_avg(r) = (1/|T|) Σ_{t ∈ T} Accuracy_t(r)
```

The **best fixed-rank baseline** is:

```
Best_fixed = max_{r ∈ {4,8,16,32}} Fixed_avg(r)
```

### Oracle Gap Metrics

We report both absolute and relative gap:

**Absolute gap (percentage points):**
```
Gap_abs = Oracle_avg - Best_fixed
```

**Relative gap (percentage improvement):**
```
Gap_rel = (Oracle_avg - Best_fixed) / Best_fixed × 100%
```

The relative gap quantifies how much performance fixed configurations leave on the table as a fraction of baseline performance.

### Heterogeneity Analysis

Beyond gap magnitude, we analyze the **distribution of oracle selections** across ranks. If optimal ranks cluster on a single value (e.g., 15 of 17 tasks prefer rank-8), the gap might reflect noise rather than systematic heterogeneity. But if selections distribute across the configuration space, it proves genuine task diversity in capacity requirements.

We report:
- **Oracle selection counts** per rank: {n_4, n_8, n_16, n_32}
- **Oracle selection distribution uniformity**: Chi-squared test against uniform distribution
- **Task-rank correlation analysis**: Which task characteristics (dataset size, domain, linguistic complexity) predict optimal rank?

## Evaluation Protocol

### Metrics

- **Primary metric:** Task accuracy (or Pearson correlation for STS-B regression task)
- **Reported values:** Mean validation accuracy across 5 epochs with early stopping
- **Oracle gap criterion:** Gap_rel ≥ 10% (MUST_WORK gate from hypothesis verification plan)

### Statistical Considerations

This is an **EXISTENCE proof-of-concept**, prioritizing directional validation over statistical rigor:

- **Single seed (42):** Sufficient for demonstrating oracle gap exists
- **No confidence intervals:** Multi-seed validation deferred to future work validating routing mechanisms
- **Simplified oracle:** Accuracy-only (not multi-objective Pareto considering FLOPs/latency)

**Rationale:** Before investing in complex routing mechanisms, we first need to know if the oracle gap exists and is substantial. A 15% gap with single-seed directional evidence is sufficient to justify further investigation. If the gap were 2-3% or inconsistent, statistical rigor would be critical. But large effect sizes (>10 percentage points) with systematic patterns (distributed oracle selections) provide strong directional evidence even without formal hypothesis testing.

## Implementation Details

All experiments implemented using:
- **PEFT library** (HuggingFace) for LoRA integration
- **Transformers library** (HuggingFace) for LLaMA-2-7B and dataset loading
- **PyTorch 2.0** for training infrastructure
- **Single NVIDIA A100 GPU** (80GB) for all experiments

Code and trained adapters will be released upon publication to enable reproduction and extension to other model families or adapter methods.
