# Methodology

Building on our observation that UQ method effectiveness may depend on task format, we design a controlled comparison methodology that enables fair evaluation while isolating format-specific effects.

## Overview

Our methodology has three components: (1) benchmark selection for ground-truth labels without annotation, (2) controlled variables ensuring fair comparison, and (3) mechanism verification separating implementation correctness from discrimination effectiveness.

**Rationale:** Prior comparisons conflated method differences with evaluation differences (different benchmarks, splits, models). Our design holds evaluation constant, varying only the UQ method under test.

## Benchmark Selection

We use TruthfulQA mc1 (multiple-choice, single correct answer) as our primary benchmark.

**Rationale:** MC format provides ground-truth labels without human annotation---the model's selected answer is either correct or incorrect. This enables AUROC computation for hallucination detection where "hallucination" = incorrect answer selection. We acknowledge this scopes our results to MC format; free-form generation evaluation is future work.

**Dataset Statistics:**
- Total questions: 817 (full), 50 (PoC validation)
- Format: 4 answer choices (A/B/C/D) per question
- Labels: Binary (correct / hallucination)
- Balance: Model-dependent (our setup yields ~56% correct)

## Model Selection

We use Llama-3-8B-Instruct as our primary evaluation model.

**Rationale:** Representative of the 7--13B decoder-only instruction-tuned model class. Open-weight availability enables reproducibility. Instruction tuning provides appropriate MC format handling.

## UQ Methods Under Test

We evaluate three UQ methods spanning token-level and semantic-level approaches:

### Max Probability (Token-Level)
Uncertainty score: $u = 1 - \max_c P(c)$ where $c \in \{A, B, C, D\}$

**Computation:** Single forward pass extracts logits for answer tokens. Higher $u$ = higher uncertainty = predicted hallucination.

### Choice Entropy (Token-Level)
Uncertainty score: $u = H(P) = -\sum_c P(c) \log P(c)$

**Computation:** Single forward pass computes entropy over answer choice distribution. Higher entropy = higher uncertainty.

### Semantic Entropy (Semantic-Level)
Uncertainty score: $u = H(P_{\text{cluster}})$

**Computation:**
1. Generate $N=5$ responses per question (temperature $T=0.7$)
2. Cluster responses via NLI-based semantic equivalence (BART-large-mnli)
3. Compute entropy over cluster assignment distribution

**NLI Clustering:** Two responses are semantically equivalent if NLI entailment score exceeds threshold (0.7). Responses form clusters; entropy is computed over cluster counts normalized to probabilities.

## Controlled Variables

| Variable | Setting | Rationale |
|----------|---------|-----------|
| Model | Llama-3-8B-Instruct | Fixed across all methods |
| Dataset split | Identical 50 samples | Same questions for all methods |
| Random seed | 42 | Reproducibility |
| Evaluation metric | AUROC | Standard for binary discrimination |
| Sample budget | 5 (for multi-sample methods) | Per Kuhn et al. baseline |

## Mechanism Verification

A key methodological contribution is separating mechanism verification from discrimination evaluation.

**Problem:** If semantic entropy achieves low AUROC, is the implementation broken or is the method unsuited to the task?

**Solution:** We verify that semantic clustering functions correctly independent of discrimination:
- **Cluster count check:** Average clusters < samples indicates clustering occurs (not all responses treated as unique)
- **Entropy variance check:** Standard deviation of entropy > 0 indicates signal variation (not constant output)

If mechanism verification passes but discrimination fails, the method is correctly implemented but unsuited to the task format.

## Evaluation Protocol

1. **Run each UQ method** on the same 50 TruthfulQA mc1 questions
2. **Collect uncertainty scores** and ground-truth labels
3. **Compute AUROC** for each method
4. **Mechanism verification** for semantic entropy
5. **Statistical comparison** across methods

**Success Threshold:** AUROC > 0.55 indicates better-than-random discrimination (h-e1 existence gate). AUROC ≥ 0.70 indicates strong discrimination (h-m1 mechanism gate).

## Limitations of Methodology

- **PoC sample size:** 50 questions limits statistical power; full validation requires 817 samples
- **Single model:** Results may not generalize across architectures
- **MC format only:** Results scope to MC; free-form may differ
- **Sample count:** 5 samples may underestimate multi-sample method potential

We report these as principled limitations rather than deficiencies, as they reflect intentional PoC scoping for mechanism validation before full-scale investment.
