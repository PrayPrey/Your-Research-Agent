# Experiments

## Experimental Questions

Our experiments address five sequential questions, each corresponding to a hypothesis:

1. **H-E1**: Does SSI differ significantly between clean and contaminated models? (Existence)
2. **H-M1**: Does our contamination injection procedure create measurable training exposure? (Mechanism 1)
3. **H-M2**: Does paraphrase-augmented training produce more invariant representations than verbatim-only? (Mechanism 2)
4. **H-M3**: Do items with invariant representations show more uniform confidence? (Mechanism 3)
5. **H-M4**: Does SSI effectively discriminate contamination status? (Mechanism 4)

## Dataset

**MMLU** (Measuring Massive Multitask Language Understanding)
- 14,042 test items across 57 subjects
- Source: cais/mmlu (HuggingFace)
- Format: 4-way multiple choice

MMLU is selected as a standard FM evaluation benchmark with sufficient scale for statistical power and documented contamination vulnerability in prior work.

## Model Configuration

**Base model**: mistralai/Mistral-7B-v0.1
- Decoder-only transformer, 7B parameters
- bf16 precision
- Open weights enabling controlled contamination

**Contaminated variants** (5 total):
- 0% (clean baseline)
- 5% contamination (702 items)
- 10% contamination (1,404 items)
- 20% contamination (2,808 items)
- 50% contamination (7,021 items)

## Training Protocol

LoRA fine-tuning on contaminated subsets:
- Rank: 16, Alpha: 32
- Target modules: q_proj, v_proj, k_proj, o_proj
- Dropout: 0.05
- Learning rate: 2e-5
- Effective batch size: 32 (4 × 8 gradient accumulation)
- Epochs: 3
- Optimizer: AdamW with 0.1 warmup ratio

Training includes only question-answer pairs from selected contaminated items. Non-contaminated items are never seen during fine-tuning.

## Paraphrase Generation

K=20 paraphrases per item via:
1. **T5-paraphrase** (T5-large fine-tuned on paraphrase corpora)
2. **GPT-4** (with diversity-encouraging prompts)
3. **Rule-based** (synonym substitution, syntactic transformation)

Distribution: approximately 7 T5, 7 GPT-4, 6 rule-based per item. Total: 280,840 paraphrases.

## Inference

For each model variant:
- Inference on 14,042 original items
- Inference on 280,840 paraphrases
- ~295,000 forward passes per model
- Total: ~1.4M forward passes across 5 variants

Confidence extraction: softmax over answer logits (A/B/C/D).

## Evaluation Metrics

### H-E1: SSI Discrimination
- Compute SSI = 1/Var(confidence) for each item
- Evaluate AUC for clean vs. contaminated binary classification
- Success: AUC > 0.7

### H-M1: Contamination Verification
- Compare accuracy on contaminated vs. non-contaminated items
- Success: contaminated items accuracy > baseline; monotonic with level

### H-M2: Representation Invariance
- Extract hidden representations (final layer)
- Compute Mean Pairwise Similarity (MPS) across paraphrases
- Compare verbatim-only vs. paraphrase-augmented conditions
- Success: MPS difference > 0.05, Cohen's d > 0.3

### H-M3: Confidence Uniformity
- Correlate representation variance with confidence variance
- Success: Pearson r < −0.4

### H-M4: SSI Metric Validation
- AUC for SSI-based classification
- Pearson r between contamination level and mean SSI
- Success: AUC > 0.7, r > 0.6

## Baselines

**13-gram overlap** (GPT-3 style): Exact substring matching
- Expected: 0% detection on paraphrased contamination

**DCQ-style probe**: Completion accuracy on exact vs. paraphrased prompts
- Expected: Partial detection, binary output only

## Implementation Notes

Experiments executed on 4× NVIDIA A100 (40GB). Training: ~4 hours per variant. Inference: ~8 hours per variant.

Code implements SDD (Science-Driven Development) pattern with validation gates after each hypothesis.
