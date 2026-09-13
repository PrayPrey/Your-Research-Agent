# Experimental Setup

We design experiments to test three core claims: (1) instruction embeddings are linearly separable by task family, (2) a linear probe can select the optimal adapter, and (3) zero-shot IPCR routing achieves near-oracle performance. We additionally test routing robustness to input perturbations.

## Research Questions

- **RQ1 (H-E0):** Are instruction prefix embeddings linearly separable by FLAN task family?
- **RQ2 (H-E1):** Can a linear probe predict the oracle adapter selection with high accuracy?
- **RQ3 (H-M1):** Does zero-shot IPCR routing achieve ≥90% of oracle adapter performance?
- **RQ4 (H-M2):** Is routing robust to paraphrase and keyword perturbations?

## Dataset

We evaluate on the FLAN instruction-tuning collection [Wei et al., 2022], accessed via the Open-Orca/FLAN HuggingFace repository.

| Property | Value |
|----------|-------|
| Total samples | 50,000 (streaming subset) |
| Task families | 9-18 (depending on experiment) |
| Embedding dimension | 384 (MiniLM-L6-v2) |
| Train/Test split | 70/15/15 (stratified) |

**Task families tested:** cot_gsm8k (math), cot_strategyqa (reasoning), cot_creak (verification), cot_qasc (science), cot_ecqa (commonsense), cot_sensemaking (logic), cot_esnli (NLI), cot_aqua_rat (algebra), stream_qed, and others.

**Why FLAN?** FLAN provides structured instruction prefixes across 62 task categories with consistent formatting, enabling systematic evaluation of prefix-based routing. Prior routing work (LoRAHub) evaluated on Big-Bench Hard; no existing work specifically targets FLAN's instruction taxonomy.

## Baselines

| Method | Description | Validation Required |
|--------|-------------|---------------------|
| Oracle | Task-specific LoRA for each sample | Yes (task labels) |
| IPCR (ours) | Linear probe on MiniLM embeddings | No (zero-shot) |
| Uniform | Equal weight to all adapters | No |
| Random | Uniformly random adapter | No |

**Why these baselines?** Oracle establishes the upper bound. Uniform and Random establish lower bounds, testing whether IPCR extracts meaningful routing signal versus naive aggregation.

## Implementation Details

**Encoder:** sentence-transformers/all-MiniLM-L6-v2 (frozen, 22M parameters)

**Classifier:** Scikit-learn LogisticRegression
- Solver: L-BFGS
- Max iterations: 2000
- Class weights: balanced

**Adapter configuration:**
- Base model: Mistral-7B-Instruct-v0.1
- LoRA rank: 16
- LoRA alpha: 32
- Target modules: q_proj, v_proj

**Compute:** Single NVIDIA A100 (40GB). Training time: ~2 hours for 8 adapters.

## Evaluation Metrics

**For separability (RQ1):**
- Macro-F1 score (threshold: ≥0.75)
- Per-family F1 scores
- Baseline: stratified random classifier

**For adapter selection (RQ2):**
- Top-1 accuracy (threshold: ≥70%)
- Top-3 accuracy (threshold: ≥85%)
- Improvement over random

**For end-to-end performance (RQ3):**
- Relative performance: IPCR accuracy / Oracle accuracy
- Threshold: ≥90% of oracle
- Statistical significance: paired t-test, p < 0.05

**For robustness (RQ4):**
- Cosine similarity under paraphrase (threshold: ≥0.90)
- Accuracy drop under keyword masking (threshold: <10%)
- Routing consistency across perturbations
