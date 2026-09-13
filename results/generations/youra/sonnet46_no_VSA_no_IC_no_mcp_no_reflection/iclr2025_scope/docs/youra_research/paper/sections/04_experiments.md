# Experiments

This section describes the experimental design for h-e1, our MUST_WORK existence check for projection-only LoRA on Mamba-130m. The design gives LoRA every possible advantage: the most commonly used configuration, a conservative gate criterion, and the benchmark task where community literature claims high performance. Failure under these conditions is informative precisely because success was expected.

## Research Questions

We designed the experiment to answer three questions, each mapping directly to a claim in the Introduction:

**RQ1: Does standard projection-only LoRA produce any measurable classification learning on Mamba-130m?**
If the SSM scan gradient barrier hypothesis is correct, LoRA adapters should receive negligible task-discriminative gradient and produce no meaningful accuracy improvement over zero-shot. If the barrier is absent, we expect to observe the 90–92% SST-2 accuracy reported in the community reference (MambaPEFT, 2024).

**RQ2: Is the failure mode, if present, consistent across multiple classification tasks?**
A task-specific failure could have a task-specific explanation (prompt format, class imbalance, tokenization artifacts). A cross-task failure with the same signature points to an architectural cause. We evaluate on SST-2 (binary sentiment) and MNLI (three-class NLI) to distinguish these possibilities.

**RQ3: Is the failure detectable from training-time diagnostics without waiting for epoch-end accuracy?**
The loss oscillation pattern provides a practitioner-relevant early-stopping signal. If loss fails to converge monotonically while accuracy is flat, this combination characterizes the gradient barrier failure mode before full evaluation is required.

## Datasets

We evaluate on two GLUE tasks, chosen to test the main claim and rule out task-specific alternative explanations.

| Dataset | Task | Train Samples (used) | Validation | # Classes | Why Chosen |
|---------|------|---------------------|------------|-----------|------------|
| SST-2 | Binary sentiment | 4,000 | 872 | 2 | Primary gate criterion; community reference comparison point; binary task minimizes class-balance confounds |
| MNLI | Three-class NLI | 4,000 | 9,815 | 3 | Cross-task generalization check; structured reasoning differs from SST-2; MNLI degradation can reveal negative transfer (not just no learning) |

**SST-2** (Stanford Sentiment Treebank, binary) provides a clean binary classification task where the majority-class baseline is approximately 50.9%. This makes zero learning immediately visible: any model predicting the majority class will land near 50.9%, and flat accuracy at this level across training epochs is an unambiguous failure signal.

**MNLI** (Multi-Genre NLI, three-class) provides a structurally different task requiring understanding of entailment relationships between sentence pairs. The three-class structure shifts the majority-class baseline to approximately 33% and creates the possibility of *negative transfer*: a model whose prediction distribution collapses to a single class will score below random chance on the non-majority class sub-population. MNLI degradation below zero-shot baseline rules out the "needs more training" explanation — a model cannot get worse through learning.

We note that QNLI and QQP were planned but not evaluated. A GPU memory contention event (17.75 MiB free on an H100 NVL with concurrent processes) caused an out-of-memory failure before the v9 training loop began. This limitation is addressed in Section 6 (Discussion).

## Baselines

We compare the fine-tuned model against two reference points:

**Zero-shot Mamba-130m:** The pretrained base model evaluated on GLUE tasks using lm-evaluation-harness multiple-choice prompting, with no classification head and no fine-tuning. This is the primary reference — it establishes what the model achieves without any adaptation. Zero-shot baselines are evaluated from the same model and environment as the fine-tuning experiments to ensure comparability. Any LoRA fine-tuning improvement must be measurable above this baseline.

**Random baseline (expected):** For SST-2 binary classification, random guessing yields ~50%. The zero-shot result of 0.4908 sits just below this mark, consistent with a causal language model with no classification prior. For MNLI three-class classification, the theoretical random baseline is ~33%; the observed zero-shot of 0.3463 is marginally above chance.

The random baseline matters because it contextualizes the zero-shot score: Mamba-130m has no classification ability beyond what chance provides. Any LoRA improvement should therefore be visible clearly above 0.49 (SST-2) and 0.35 (MNLI).

## Implementation Details

All experiments use the HuggingFace `state-spaces/mamba-130m-hf` checkpoint. This is a pure Mamba-1 SSM with 24 MambaBlock layers, hidden dimension 768, inner dimension 1536, and the GPT-NeoX-20B tokenizer (50k vocabulary). The model has approximately 130M total parameters.

**LoRA Configuration:**

| Hyperparameter | Value | Rationale |
|---|---|---|
| Target modules | `in_proj`, `out_proj`, `x_proj` | Standard Mamba-1 projection LoRA; matches community reference |
| Rank (r) | 8 | Community reference value; standard for classification |
| Alpha (α) | 16 | 2r; standard scaling factor |
| Dropout | 0.05 | Standard regularization |
| Trainable parameters | 1,484,288 (1.14% of 130M) | Confirmed by PEFT `print_trainable_parameters()` |

The `dt_proj` layer (which controls SSM temporal dynamics) was excluded from Condition A as the standard community configuration. An attempt to include it (v9) caused CUDA out-of-memory on the shared cluster before any training steps.

**Training Configuration:**

| Hyperparameter | Value |
|---|---|
| Optimizer | AdamW |
| Learning rate | 3×10⁻⁴ |
| Weight decay | 0.01 |
| Batch size | 32 |
| Epochs | 3 |
| LR schedule | Linear warmup (6%) + linear decay |
| Seed | 42 |
| Training samples | 4,000 (subsampled from train split) |
| Max sequence length | 128 tokens |

**Classification head:** A single `nn.Linear(768, num_labels)` applied to the last-token hidden state from the final MambaBlock. The head is randomly initialized. No special initialization is applied.

**Compute:** Experiments were run on an H100 NVL (93 GiB total; GPU environment was shared with concurrent processes). v8 completed successfully. v9 was blocked by GPU memory contention.

## Evaluation Metrics

**Per-epoch accuracy:** Classification accuracy on the full validation split is computed at the end of each epoch. Accuracy is the standard GLUE metric for SST-2 (binary) and MNLI (three-class). We use the *full* validation split — not a subsample — to minimize noise in each epoch's measurement. Three consecutive identical accuracy values across epochs cannot be attributed to sampling variation.

**Per-batch cross-entropy loss:** Training loss is logged at every gradient step. This provides the training-time diagnostic signal: monotonically decreasing loss indicates convergence; oscillating loss without trend indicates gradient barrier failure.

**LoRA installation verification:** Before accepting any result, we confirm (1) LoRA keys (`lora_A`, `lora_B`) exist in the model state dictionary at expected module paths, (2) LoRA weight matrices are non-zero after training, and (3) the trainable parameter count matches the theoretical expectation for rank 8 on the targeted modules. All three checks pass in v8.

**Gate criterion:** The MUST_WORK gate is SST-2 accuracy > 0.70 after three epochs. This threshold is deliberately conservative — the community reference claims 90–92%, but the gate asks for only 70% to accommodate any training recipe differences. The 21 percentage-point gap between the zero-shot baseline (0.4908) and the gate (0.70) represents what we consider the minimum threshold for demonstrating that LoRA produces meaningful classification learning.
