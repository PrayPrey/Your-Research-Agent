# Methodology

## Theoretical Foundation

We ground SSI in learning theory: models trained on diverse phrasings of the same content develop representations invariant to surface form. This invariance should manifest as uniform confidence scores across paraphrases. The causal chain is:

1. **Contamination exposure**: Training includes benchmark items (verbatim or paraphrased)
2. **Representation invariance**: Diverse exposure creates robust semantic encoding
3. **Confidence uniformity**: Invariant representations yield consistent predictions
4. **SSI signal**: Low variance across paraphrases indicates potential contamination

We decompose this chain into five testable hypotheses, enabling isolation of failure points.

## SSI Formulation

For each benchmark item, we generate K paraphrases and extract model confidence scores. The Semantic Saturation Index is defined as:

$$\text{SSI}(x) = \frac{1}{\text{Var}(\{c(x_1), c(x_2), \ldots, c(x_K)\})}$$

where $c(x_i)$ is the model's confidence on paraphrase $x_i$ of item $x$, and Var denotes sample variance. High SSI indicates uniform confidence, hypothesized to signal contamination.

The inverse-variance formulation was chosen to transform low variance (the contamination signal) into high SSI values, enabling intuitive interpretation: "higher SSI = more likely contaminated."

## Controlled Contamination

We create contaminated model variants via LoRA fine-tuning of Mistral-7B-v0.1:

**Contamination levels**: 0% (clean), 5%, 10%, 20%, 50% of MMLU test items included in training

**Training configuration**:
- LoRA rank: 16, alpha: 32
- Target modules: q_proj, v_proj, k_proj, o_proj
- Learning rate: 2e-5, batch size: 4, gradient accumulation: 8
- Epochs: 3, warmup ratio: 0.1

This creates controlled ground truth for contamination—essential for validation experiments.

## Paraphrase Generation

We use multi-method paraphrase generation to ensure diversity:

1. **T5-paraphrase**: Neural paraphrasing via T5-large
2. **GPT-4**: LLM-based paraphrasing with explicit diversity prompting
3. **Rule-based**: Synonym substitution, syntactic restructuring

K=20 paraphrases per item balance statistical power against computational cost. ~1.4M forward passes per model variant.

## Hypothesis Decomposition

We structure verification as sequential hypothesis testing:

| ID | Type | Statement | Gate |
|----|------|-----------|------|
| H-E1 | Existence | SSI differs between clean and contaminated models | MUST_WORK |
| H-M1 | Mechanism | Contamination injection creates training exposure | MUST_WORK |
| H-M2 | Mechanism | Training develops representation invariance | SHOULD_WORK |
| H-M3 | Mechanism | Invariance manifests as confidence uniformity | SHOULD_WORK |
| H-M4 | Mechanism | SSI captures invariance as contamination signal | SHOULD_WORK |

MUST_WORK gates halt the pipeline if failed. SHOULD_WORK gates allow exploration of alternatives. This structure enables diagnosis of where the causal chain breaks.

## Evaluation Metrics

**Primary**: AUC for binary classification (clean vs. contaminated) using SSI

**Secondary**:
- Pearson correlation between contamination level and mean SSI
- Cohen's d effect size
- Mean Pairwise Similarity (MPS) for representation invariance

**Success criteria**: AUC > 0.7, r > 0.6, d > 0.5

## Dataset and Model

**Dataset**: MMLU (14,042 items across 57 subjects)
- Standard FM evaluation benchmark
- Multiple-choice format enables straightforward confidence extraction

**Model**: Mistral-7B-v0.1
- Open-weight decoder-only transformer
- Enables controlled fine-tuning and logit extraction
- 7B scale balances capability with computational tractability

## Experimental Protocol

1. Fine-tune 5 Mistral-7B variants at contamination levels 0–50%
2. Generate K=20 paraphrases per MMLU item
3. Run inference on original + paraphrases for each model
4. Compute SSI per item per model
5. Evaluate discrimination metrics (AUC, correlation, effect size)
6. Validate mechanism steps via intermediate metrics (MPS, confidence variance)
