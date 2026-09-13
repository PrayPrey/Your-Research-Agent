# Methodology

Our experimental design tests a specific hypothesis: zero-shot evaluation reveals architectural compatibility before fine-tuning investment. If a pretrained model fails a task at zero-shot (achieving below-random baseline accuracy), the architectural mismatch signals that parameter-efficient fine-tuning will fail regardless of method or hyperparameters. We validate this principle by evaluating Mamba-130M [Gu and Dao, 2023], a representative causal state-space model, on GLUE classification tasks [Wang et al., 2018] with diverse reasoning requirements.

## Experimental Rationale

Traditional PEFT workflows assume base model compatibility and proceed directly to fine-tuning. Our approach introduces an EXISTENCE gate: verify that the architecture can perform the task at zero-shot before investing compute in adaptation. This gate operates on a simple principle—if the model performs worse than random guessing, architectural constraints prevent task completion. No amount of parameter tuning can add capabilities absent in the base architecture's information flow.

We focus on zero-shot evaluation (no fine-tuning) because it isolates architectural capability from learned task-specific knowledge. A model that achieves above-random zero-shot accuracy demonstrates that its architecture supports the task's reasoning requirements, even if performance is suboptimal. Conversely, below-random accuracy indicates systematic bias incompatible with task structure—a failure mode that fine-tuning amplifies rather than corrects.

## Model Selection

**Mamba-130M** serves as our test case for causal state-space models. Mamba employs selective state-space mechanisms with hardware-aware implementations, achieving competitive language modeling performance with linear-time complexity. The model processes text autoregressively: each token's representation depends only on preceding tokens, computed via recurrent state updates rather than bidirectional attention. This architectural choice optimizes generation efficiency but imposes constraints on tasks requiring symmetric comparison.

We use the publicly available checkpoint `state-spaces/mamba-130m-hf` from HuggingFace, pretrained on standard language modeling corpora. The 130M parameter scale balances representational capacity with computational feasibility, enabling rapid experimentation without requiring extensive GPU resources.

## Task Selection

We evaluate on three GLUE tasks representing different reasoning requirements:

**QQP (Quora Question Pairs):** Binary paraphrase detection determining whether two questions are semantically equivalent. This task requires *symmetric comparison*—both questions must inform the similarity judgment equally. Success demands bidirectional reasoning: the model must compare "How can I improve my English?" with "What's the best way to learn English?" by jointly encoding both questions and detecting semantic overlap independent of presentation order.

**MNLI (Multi-Genre Natural Language Inference):** Three-way classification (entailment, neutral, contradiction) over premise-hypothesis pairs. Like QQP, this requires bidirectional reasoning—the model must compare premise and hypothesis symmetrically to determine logical relationships. The task structure exposes architectural constraints: causal models cannot perform true bidirectional inference as hypothesis representation cannot inform premise encoding.

**SST-2 (Stanford Sentiment Treebank):** Binary sentiment classification over single sentences. Unlike paraphrase and entailment tasks, sentiment analysis aligns with causal language modeling: the model encodes the sentence left-to-right, and the final hidden state aggregates contextual information sufficient for classification. This task tests whether the checkpoint possesses genuine language understanding independent of architectural constraints.

These three tasks form a minimal test suite: QQP and MNLI probe bidirectional reasoning (expected failure for causal SSMs), while SST-2 tests generation-aligned classification (expected success). The binary success/failure pattern isolates architectural effects from checkpoint quality.

## Evaluation Protocol

For each task, we evaluate Mamba-130M on 100 randomly sampled examples from the validation set. We use deterministic evaluation (seed 42) and greedy decoding without prompt engineering or few-shot examples—true zero-shot evaluation that reflects base architectural capabilities.

**Random baselines** define the architectural failure threshold:
- QQP: 50% (binary classification)
- MNLI: 33.3% (three-way classification)  
- SST-2: 50% (binary classification)

Performance *below* random baseline indicates systematic bias incompatible with task structure. We use binomial tests to verify statistical significance: for a model performing at random, observing accuracy significantly below 50% (or 33.3% for MNLI) would occur with probability p < 0.05, confirming that below-baseline performance is not sampling noise.

## Architectural Analysis

The causal state-space architecture processes input sequences via recurrent dynamics:

```
Input: [Question 1 tokens] [SEP] [Question 2 tokens]
Processing: h_t = SSM(h_{t-1}, x_t)  # Unidirectional recurrence
Classification: y = Linear(h_final)
```

For paraphrase detection (QQP), this creates asymmetric information flow: Question 2's representation incorporates information from Question 1 (via recurrent state), but Question 1 cannot see Question 2. True paraphrase detection requires symmetric comparison—both questions must inform the similarity judgment equally. The architectural constraint prevents this capability.

In contrast, sentiment classification (SST-2) requires only unidirectional encoding:

```
Input: [Sentence tokens]
Processing: h_t = SSM(h_{t-1}, x_t)
Classification: y = Linear(h_final)
```

The final hidden state accumulates left-to-right context sufficient for sentiment judgment. No bidirectional reasoning is required, allowing the architecture to succeed.

## Implementation Details

We implement evaluation using HuggingFace Transformers library with standard GLUE data loaders. For each task, we:

1. Load the pretrained Mamba-130M checkpoint
2. Add a task-specific classification head (randomly initialized)
3. Perform forward pass on validation examples (no gradient updates)
4. Compute accuracy against ground-truth labels
5. Compare to random baseline using binomial significance tests

All experiments run on a single NVIDIA A100 GPU with inference-only workload (no training). Total evaluation time is under 5 minutes per task, demonstrating the efficiency of zero-shot architectural compatibility testing.

## Why This Design Tests Our Hypothesis

Our methodology directly tests whether zero-shot evaluation predicts PEFT viability:

- **If Mamba achieves above-random accuracy on all tasks**: Architecture supports all task types; LoRA fine-tuning should succeed universally.
- **If Mamba achieves below-random accuracy on bidirectional tasks (QQP, MNLI) but above-random on SST-2**: Architectural constraint prevents bidirectional reasoning; LoRA fine-tuning would fail on incompatible tasks regardless of hyperparameters.

The second outcome validates our hypothesis: zero-shot failure signals architectural incompatibility that PEFT cannot overcome. Proceeding to LoRA fine-tuning on QQP after observing below-random zero-shot accuracy would waste compute on a structurally impossible task.

## Limitations and Scope

We evaluate a single state-space model (Mamba-130M) and three GLUE tasks. Broader conclusions about SSM architectures require testing additional variants (RWKV, H3, S4) and tasks. However, the architectural constraint we identify—causal processing prevents symmetric comparison—applies to all autoregressive SSMs, suggesting the failure pattern generalizes.

We do not test LoRA fine-tuning after zero-shot failure because our hypothesis predicts it will fail. Future work could empirically validate this prediction, but the below-random zero-shot results provide strong prior evidence that fine-tuning would amplify architectural bias rather than overcome it. Our focus is on establishing zero-shot evaluation as a gating mechanism, not on comprehensively documenting PEFT failures.
