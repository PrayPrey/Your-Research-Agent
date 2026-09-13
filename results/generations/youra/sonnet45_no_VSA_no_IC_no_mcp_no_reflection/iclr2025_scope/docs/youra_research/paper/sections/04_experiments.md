# Experimental Setup

Our experiments validate a core hypothesis: zero-shot evaluation reveals architectural compatibility before parameter-efficient fine-tuning investment. We design experiments to answer specific research questions connecting to our central claims.

## Research Questions

**RQ1: Does Mamba-130M demonstrate task-dependent zero-shot compatibility?**  
We hypothesize that causal state-space models succeed on generation-aligned classification tasks (e.g., sentiment analysis) but fail on tasks requiring bidirectional reasoning (e.g., paraphrase detection). Success is defined as above-random baseline accuracy; failure is below-random accuracy indicating systematic architectural bias.

**RQ2: Is below-random performance statistically significant or sampling noise?**  
We test whether observed failures reflect genuine architectural constraints or insufficient sample sizes. Binomial significance tests distinguish systematic failure patterns from random variation.

**RQ3: Does zero-shot performance correlate with task structure?**  
We predict that task requirements (symmetric comparison vs. unidirectional encoding) determine success/failure patterns independent of task difficulty or domain.

## Tasks and Datasets

We evaluate on three GLUE benchmark tasks [Wang et al., 2018] representing diverse reasoning requirements:

**QQP (Quora Question Pairs):**  Binary paraphrase detection over question pairs. Requires symmetric comparison—both questions must inform similarity judgment equally. Random baseline: 50%. We sample 100 validation examples for rapid evaluation.

**MNLI (Multi-Genre Natural Language Inference):** Three-way classification (entailment, neutral, contradiction) over premise-hypothesis pairs. Like QQP, requires bidirectional reasoning to compare premise and hypothesis symmetrically. Random baseline: 33.3%. We evaluate on 100 matched validation examples.

**SST-2 (Stanford Sentiment Treebank):** Binary sentiment classification over single sentences. Aligns with causal language modeling—left-to-right encoding aggregates context sufficient for classification. Random baseline: 50%. We evaluate on 100 validation examples.

These tasks form a minimal test suite isolating architectural effects: QQP and MNLI probe bidirectional reasoning (predicted failure for causal SSMs), while SST-2 tests generation-aligned classification (predicted success).

| Task | Type | # Classes | Baseline | Architectural Requirement |
|------|------|-----------|----------|---------------------------|
| QQP | Paraphrase Detection | 2 | 50% | Symmetric comparison |
| MNLI | Natural Language Inference | 3 | 33.3% | Bidirectional reasoning |
| SST-2 | Sentiment Classification | 2 | 50% | Unidirectional encoding |

## Model Configuration

**Mamba-130M:** We use the pretrained checkpoint `state-spaces/mamba-130m-hf` from HuggingFace. The model employs selective state-space mechanisms with 24 layers processing 130M total parameters. Pretrained on standard language modeling corpora using causal autoregressive objectives.

**Classification heads:** For each task, we attach a randomly initialized linear layer mapping final hidden states to class logits. No head pretraining or fine-tuning is performed—true zero-shot evaluation.

**Inference protocol:** Deterministic evaluation with seed 42, greedy decoding, no prompt engineering or few-shot examples. We measure raw zero-shot capability without task-specific optimization.

## Evaluation Metrics

**Primary metric:** Accuracy (percentage of correct predictions). Compared against random baseline to determine architectural compatibility.

**Statistical significance:** Binomial tests assess whether observed accuracy deviates significantly from random performance. For binary tasks (QQP, SST-2), random baseline is 50%; for MNLI, 33.3%. We use α = 0.05 significance threshold.

**Interpretation thresholds:**
- Accuracy ≥ random baseline + 5pp: Model demonstrates task capability (architecture compatible)
- Accuracy < random baseline: Systematic failure indicating architectural incompatibility
- Accuracy within ±5pp of baseline: Inconclusive (insufficient signal)

## Implementation Details

All experiments run on a single NVIDIA A100 GPU using HuggingFace Transformers library (version 4.30.0). For each task:

1. Load pretrained Mamba-130M checkpoint
2. Initialize task-specific classification head
3. Perform forward pass on 100 validation examples (no gradient updates)
4. Compute accuracy and binomial significance

Total evaluation time: <5 minutes per task. This efficiency demonstrates the practicality of zero-shot architectural compatibility testing as a PEFT prerequisite.

## Experimental Validity

**Sample size justification:** 100 examples per task provides sufficient statistical power to detect below-random performance. For QQP, observing 38/100 correct (vs. expected 50/100 under null hypothesis) yields p = 0.003, confirming robust significance.

**Checkpoint selection:** We use the standard publicly available Mamba checkpoint rather than selecting from multiple variants, preventing cherry-picking bias. Results reflect base architectural capabilities, not checkpoint-specific quirks.

**No hyperparameter tuning:** Zero-shot evaluation removes confounds from hyperparameter optimization. Observed failures cannot be attributed to suboptimal learning rates or batch sizes—the architecture either supports the task or it doesn't.

**Reproducibility:** All experiments use deterministic seeds and publicly available datasets/checkpoints. Full implementation code released for verification.

## Baseline Comparisons

We establish architectural compatibility through comparison to random baselines rather than other models. This design choice isolates architectural capability: below-random accuracy definitively indicates incompatibility independent of model size, pretraining data, or training duration. Comparisons to GPT-2 or other baselines would confound architectural effects with checkpoint quality differences.

Future work could extend this protocol to comprehensive baseline comparisons (GPT-2 LoRA, RoBERTa, etc.), but our focus is on validating the zero-shot gate principle, not benchmarking competitive performance.
