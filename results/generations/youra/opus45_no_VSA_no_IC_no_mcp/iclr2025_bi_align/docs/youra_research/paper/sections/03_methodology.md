# 3. Methodology

## Experimental Design

We designed a five-hypothesis experiment to trace mechanistic differences from training dynamics through to benchmark-level evaluation:

| ID | Hypothesis | Gate Type | Purpose |
|----|------------|-----------|---------|
| H-E1 | Benchmark Independence | MUST_WORK | Validates experimental design |
| H-M1 | RLHF Reward Smoothing | MUST_WORK | Confirms RLHF mechanistic claim |
| H-M2 | DPO Boundary Sharpness | SHOULD_WORK | Confirms DPO mechanistic claim |
| H-M3 | Different Attractors | SHOULD_WORK | Tests landscape→attractor theory |
| H-M4 | Differential Profiles | SHOULD_WORK | Tests attractor→benchmark claim |

## Base Model and Data

**Model:** Llama-2-7B (meta-llama/Llama-2-7b-hf) with LoRA fine-tuning (r=16, alpha=32)

**Dataset:** Anthropic HH-RLHF (15k training subset). The same preference pairs were used for both RLHF reward model training and DPO policy optimization, ensuring controlled comparison.

## H-E1: Benchmark Independence Verification

We evaluated base Llama-2-7B on three benchmarks:
- TruthfulQA MC1 (817 questions)
- HHH-helpful (1000 examples)
- HHH-harmless (1000 examples)

Success criterion: All pairwise Pearson correlations |r| < 0.5, confirming benchmarks measure distinct dimensions.

## H-M1: RLHF Reward Model Training

Trained a reward model using Bradley-Terry loss with center_rewards regularization (coefficient=0.01). Key metrics:
- **Smoothness:** Reward output range (continuous distribution)
- **Learning signal:** Preference accuracy > 50%, positive margin

## H-M2: DPO Boundary Sharpness

Applied DPO training (beta=0.1) and computed:
- **Sharpness ratio:** DPO margin variance / RLHF margin variance (threshold: > 1.0)
- **Boundary accuracy:** Performance on cases where RLHF showed weak preferences (threshold: > 55%)

## H-M3: Attractor Clustering

Extracted behavior embeddings from models trained with multiple seeds (2 seeds × 2 methods). Computed:
- **Clustering gap:** Within-method similarity - cross-method similarity (threshold: > 0.05)
- **Silhouette score:** Cluster quality (threshold: > 0.1)

## H-M4: Differential Benchmark Profiles

Evaluated trained models on all three benchmarks. Primary success criterion:
- At least one benchmark shows |Cohen's d| > 0.3 (divergence)
- AND at least one shows |d| < 0.15 (similarity)

This "differential profile" pattern would indicate method-specific alignment signatures.

## Statistical Analysis

Effect sizes reported as Cohen's d with conventional thresholds (small: 0.2, medium: 0.5, large: 0.8). Permutation tests used for clustering significance (1000 permutations). Power analysis confirmed adequate sample sizes for effect detection (>95% power for d=0.3).
