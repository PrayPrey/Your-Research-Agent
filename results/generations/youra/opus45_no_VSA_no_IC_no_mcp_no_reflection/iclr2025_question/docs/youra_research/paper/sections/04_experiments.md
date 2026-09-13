# Experimental Setup

We design experiments to answer the following research questions:

**RQ1:** Do uncertainty quantification methods discriminate hallucinations better than random chance?

**RQ2:** Does semantic entropy achieve the expected AUROC ≥ 0.70 based on prior work?

**RQ3:** Does semantic entropy's clustering mechanism function correctly on MC-format tasks?

These questions correspond to our hypotheses h-e1 (existence), h-m1 (mechanism), and the format-dependency investigation. RQ3 is critical: it separates implementation correctness from discrimination effectiveness.

## Dataset

We evaluate on **TruthfulQA mc1** (multiple-choice, single correct answer).

| Statistic | Value |
|-----------|-------|
| Format | Multiple choice (4 options: A/B/C/D) |
| Total questions | 817 (full), 50 (PoC validation) |
| Question types | Factual knowledge prone to imitative falsehoods |
| Label source | Ground-truth (correct answer known) |

**Rationale:** MC format provides binary ground-truth labels without human annotation. The model either selects the correct answer (correct) or an incorrect answer (hallucination). This enables clean AUROC computation for hallucination detection. We acknowledge this scopes results to MC format; the observed performance gap may differ on free-form generation.

## Model

We use **Llama-3-8B-Instruct** as our primary evaluation model.

| Parameter | Value |
|-----------|-------|
| Model | meta-llama/Meta-Llama-3-8B-Instruct |
| Parameters | 8 billion |
| Type | Decoder-only, instruction-tuned |
| Quantization | None (full precision) |

**Rationale:** Representative of the 7--13B instruction-tuned decoder class. Open weights enable reproducibility. Instruction tuning ensures appropriate handling of MC format without additional prompting engineering.

## UQ Methods

We compare three methods spanning token-level and semantic-level approaches:

### Token-Level Methods

**Max Probability:** $u = 1 - \max_c P(c)$ for $c \in \{A, B, C, D\}$
- Single forward pass
- Extracts confidence from answer token logits
- Higher uncertainty = predicted hallucination

**Choice Entropy:** $u = H(P) = -\sum_c P(c) \log P(c)$
- Single forward pass
- Entropy over answer choice distribution
- Captures distributional uncertainty

### Semantic-Level Method

**Semantic Entropy:** $u = H(P_{\text{cluster}})$
- Generate $N=5$ responses per question (temperature $T=0.7$)
- Cluster via NLI-based semantic equivalence (BART-large-mnli, threshold 0.7)
- Compute entropy over cluster assignment distribution

This method was selected because Kuhn et al. [2023] reported it substantially outperforms token entropy. Our goal is to test whether this finding transfers to MC format.

## Baselines

| Method | Type | Compute | Expected AUROC |
|--------|------|---------|----------------|
| Random | Reference | - | 0.50 |
| Max Prob | Token-level | 1 pass | Unknown |
| Choice Entropy | Token-level | 1 pass | Unknown |
| Semantic Entropy | Semantic | 5 passes + NLI | ≥ 0.70 (Kuhn et al.) |

**Random baseline** provides the lower bound (AUROC = 0.50). All methods must exceed this to demonstrate any discrimination capability.

## Implementation Details

| Parameter | Value |
|-----------|-------|
| Seed | 42 |
| Sample size | 50 questions (PoC) |
| Samples per question (semantic) | 5 |
| Temperature (semantic) | 0.7 |
| NLI model | facebook/bart-large-mnli |
| NLI threshold | 0.7 |

**Reproducibility:** All code available in the experiment repository. Fixed seed ensures reproducible results across runs.

## Evaluation Protocol

**Primary Metric:** AUROC (Area Under ROC Curve) for hallucination detection
- Higher uncertainty should correlate with incorrect answers
- AUROC > 0.5 indicates better than random
- AUROC > 0.55 threshold for h-e1 (existence validation)
- AUROC ≥ 0.70 threshold for h-m1 (mechanism validation)

**Mechanism Verification (RQ3):**
- Average clusters per question < N indicates clustering occurs
- Entropy standard deviation > 0 indicates signal variation

This separation is methodologically important: if AUROC is low but mechanism verification passes, the method is correctly implemented but unsuited to the task format.
