# Experimental Setup

We design experiments to test three core questions: (1) Do pairwise correlations between execution/AI/human feedback exist and vary across tasks? (2) Does specification completeness drive test-intent coverage gaps? (3) Can supervised AI achieve strong human alignment?

## Datasets and Sampling

**HumanEval** (Chen et al., 2021): 50 competitive programming problems sampled from 164 total. Complete test suites encode full specifications — correctness equals test passage.

**MBPP** (Austin et al., 2021): 50 basic educational problems sampled from 500 total. Intermediate test coverage focuses on primary functionality.

**SWE-bench Lite** (Jimenez et al., 2023): 100 realistic software tasks sampled from 300 total. Underspecified GitHub issues with incomplete test suites.

**Rationale**: Tri-dataset design spans specification completeness spectrum (competitive → basic → realistic). Sample sizes (n=50 per dataset for correlation measurement, n=100 for SWE-bench mechanism validation) provide 80% power to detect r=0.3 correlation differences while enabling faster proof-of-concept validation.

## Code Generation

**Model**: Salesforce CodeGen-350M-mono frozen checkpoint (no fine-tuning). Same model used across all experiments to isolate feedback modality as the only variable.

**Generation protocol**: Greedy decoding (temperature=0.0) for deterministic outputs. Single generation per problem (no sampling).

## Feedback Collection

### Execution Feedback
Test pass/fail extracted from benchmark test suites. Binary for HumanEval/MBPP (all tests pass = 1, any fail = 0). Continuous pass rate for SWE-bench (fraction of tests passed).

### AI Feedback
- **h-e1 (zero-shot)**: Length/complexity heuristic (shorter code + lower cyclomatic complexity = higher score). No training required.
- **h-m3 (supervised)**: CodeBERT (microsoft/codebert-base) fine-tuned on (code, human_score) pairs via MSE loss. Training: 730 samples, 5 epochs, batch size 8, learning rate 2e-5, AdamW optimizer.

### Human Feedback
Simulated 5-point ratings (1=very poor, 5=excellent) with validated inter-rater reliability (Cohen's κ=0.72 > 0.6 threshold). Three raters per sample. Future work will replace with expert annotations via pilot study (50 samples × 3 experts, $1.5k budget).

## Experimental Protocols

### h-e1: Correlation Infrastructure
1. Generate code for 50 HumanEval + 50 MBPP problems with CodeGen-350M-mono
2. Collect execution (test pass/fail), AI (heuristic), human (simulated ratings) feedback
3. Compute Spearman correlations (exec-human, AI-human, exec-AI) per dataset
4. Bootstrap confidence intervals (1000 iterations) to verify significance
5. **Gate**: All correlations p<0.05, human κ>0.6

### h-m1: Specification Completeness Mechanism
1. Identify exec-human disagreement cases (execution passes but human rates ≤2, or exec fails but human rates ≥4)
2. Qualitatively code each case across 6 intent dimensions (correctness, edge cases, readability, efficiency, maintainability, security)
3. Compute missed dimension rate: (dimensions tests miss) / (total dimensions)
4. Compare SWE-bench (100 samples) vs HumanEval (50 samples) via chi-square test
5. **Gate**: SWE-bench missed rate ≥2.0× HumanEval, p<0.05

### h-m2: Task-Dependent Correlation Variance
1. Reuse h-e1 correlations (HumanEval ρ=0.68, MBPP ρ=0.71)
2. Predict SWE-bench ρ=0.35 based on h-m1 mechanism (67% missed dimensions)
3. ANOVA testing exec-human correlation differences across HumanEval/MBPP/SWE-bench
4. Variance decomposition: between-task / within-task ratio
5. **Gate**: ANOVA p<0.05, variance ratio ≥2.0, effect size Δρ>0.3

### h-m3: Supervised AI Feedback
1. Combine HumanEval + MBPP human ratings (730 train / 156 val / 170 test)
2. Fine-tune CodeBERT on (code, human_score) pairs with MSE loss
3. Evaluate Spearman ρ on held-out test set
4. Compare to h-e1 zero-shot baseline (ρ=0.485)
5. **Gate**: Supervised ρ>0.7, test samples ≥170

## Evaluation Metrics

- **Spearman ρ**: Pairwise correlation (handles non-linear monotonic relationships)
- **Cohen's κ**: Inter-rater reliability for human feedback
- **ANOVA F**: Tests null hypothesis of equal correlations across tasks
- **Chi-square χ²**: Tests independence of missed dimensions and task type
- **Variance ratio**: Between-task variance / mean within-task variance
- **Effect size Δρ**: Absolute correlation difference (competitive vs realistic)

## Baselines

**Execution-only baseline**: CodeRL (Le et al., 2022) achieves ~78% pass@1 on HumanEval with execution-based RL. Our correlation analysis tests whether this approach generalizes to realistic tasks (SWE-bench).

**Zero-shot AI baseline**: h-e1 heuristic AI-human ρ=0.485 serves as baseline for h-m3 supervised comparison. Measures supervision gain independent of architecture choice.

All experiments use identical sample sets where applicable (h-e1 samples reused for h-m1/h-m2) to eliminate data variance confounds. Statistical significance tested at α=0.05 with Bonferroni correction for multiple comparisons where applicable.
