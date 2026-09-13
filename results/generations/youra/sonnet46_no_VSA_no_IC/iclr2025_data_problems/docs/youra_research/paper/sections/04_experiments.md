# 4. Experimental Setup

## 4.1 Research Questions

We design experiments to answer the following questions, progressing from prerequisite to primary:

**RQ1:** Are The Pile's domains measurably distinguishable by automated cognitive task pattern proxies? (Prerequisite: domain content differentiation mechanism)

**RQ2:** Do domain exposure trajectories computed from Pythia's exact dataloaders show sufficient within-family variation to support panel regression analysis? (Prerequisite: covariate variation)

**RQ3:** Does domain-specific exposure predict benchmark-specific capability improvement, with Wikipedia exposure predicting MMLU more than HellaSwag and Books exposure predicting HellaSwag more than MMLU? (Primary hypothesis)

Each RQ maps to a pre-registered sub-hypothesis (h-m1, h-e1, h-m2/h-m3 respectively) with gates specified before data collection.

## 4.2 Dataset and Model Family

**Pre-training corpus:** The Pile [Gao et al., 2020] — 800GB of text across 22 domains. Domain proportions range from WebText2 (22%) to Enron Emails (<0.1%). The Pile's domain taxonomy and proportions are fully documented, enabling principled domain selection for analysis.

**Model family:** Pythia [Biderman et al., 2023] — 16 autoregressive GPT-NeoX models (70M–12B parameters) trained on The Pile with identical architecture and data, with 154 intermediate checkpoints each. We focus analysis on three representative model sizes: 70M, 1B, and 6.9B, spanning three decades of parameter scale.

**Why Pythia/Pile:** Pythia is the only publicly available model family with (a) exact dataloader documentation enabling domain exposure reconstruction, (b) a sufficient number of intermediate checkpoints (154) for trajectory analysis, and (c) identical architecture across model sizes eliminating cross-family confounds. No other model family satisfies all three criteria.

## 4.3 Sub-Hypothesis Experiments

### RQ1: Domain Content Differentiation (h-m1)

| Parameter | Value |
|-----------|-------|
| Documents per domain | 200 |
| Domains analyzed | 21 |
| Total documents | 4,200 |
| NLP model | spaCy `en_core_web_sm` |
| Statistical test | Welch's ANOVA + Tukey HSD |
| Effect size metric | η² (partial eta-squared) |
| Gate criterion | η² > 0.1, p < 0.05, for ≥1 proxy |

Three cognitive task pattern proxies are measured: entity density, narrative coherence, and formal syntax density. The gate tests whether between-domain differences explain a meaningful proportion of total variance.

### RQ2: Exposure Trajectory Non-Uniformity (h-e1)

| Parameter | Value |
|-----------|-------|
| Domain lookup size | 600,000 documents (shard 0) |
| Checkpoints analyzed | 154 |
| Model sizes | 70M, 1B, 6.9B (Spearman correlation check) |
| Tokens per step | 2,097,152 |
| Sequence length | 2,049 |
| Gate criterion | ≥10 of 22 domains with std > 0.001 |

The gate tests whether the within-family variation is sufficient for regression analysis. A threshold sensitivity analysis varies the std cutoff (0.0001, 0.001, 0.01) to characterize the variance distribution.

### RQ3: Domain-Benchmark Specificity (h-m2 + h-m3)

**h-m2 (Spearman analysis):**

| Parameter | Value |
|-----------|-------|
| Analysis | Spearman ρ(exposure_d, benchmark_b) |
| Floor filter | Exclude checkpoints with any benchmark < 0.20 |
| Minimum N | 100 checkpoints (pre-registered) |
| Primary test (P1) | Fisher z-test: ρ(Wiki,MMLU) > ρ(Wiki,HellaSwag), α=0.10 one-tailed |
| Secondary test (P2) | Fisher z-test: ρ(Books3,HellaSwag) > ρ(Books3,MMLU) |

**h-m3 (Panel OLS):**

| Parameter | Value |
|-----------|-------|
| Model | PanelOLS with entity fixed effects |
| Entities | Model sizes (70M, 1B, 6.9B) |
| Min entities | 3 (pre-registered for panel identification) |
| Primary tests (P1/P2) | Wald z-test for directional β comparison |
| P3 test | LRT + Benjamini-Hochberg FDR (α=0.05) |
| P4 test | Spearman rank correlation of β vectors (small vs large scale) |
| Books3 guard | Abort if Books3 std < 10⁻⁶ |

## 4.4 Baselines

The following baselines are defined as part of the pre-registered h-m3 panel regression framework and are implemented in the validated pipeline. Due to the data limitations documented in Section 5.4 (Books3 zero-exposure, insufficient evaluation cache), none of these baselines could be executed in the current study. They remain ready to run when the prerequisite data gaps are resolved.

**Scale-only model:** Panel regression using only log(model_params) as predictor — the null hypothesis that benchmark improvement is entirely explained by scale, with no additional domain contribution.

**Permutation null:** Domain labels permuted randomly across checkpoints (1,000 permutations) to establish the null distribution of R² gain from domain variables. Statistical significance of domain regression is assessed relative to this permutation distribution.

**Uniform-β model:** Constrain all domain coefficients to be equal across the four benchmarks — the null hypothesis that domains have identical effects on all benchmarks (no specificity). The LRT comparing benchmark-specific vs uniform-β models is the direct P3 test.

## 4.5 Evaluation Metrics

**For domain content differentiation (RQ1):**
- η² (proportion of variance explained by domain membership) — primary effect size
- F-statistic from Welch's ANOVA
- Tukey HSD p-values for pairwise domain comparisons

**For trajectory non-uniformity (RQ2):**
- Per-domain standard deviation of cumulative exposure fraction across 154 checkpoints
- N domains passing the std > 0.001 threshold
- Cross-model-size Spearman correlation (trajectory consistency check)

**For domain-benchmark specificity (RQ3):**
- Spearman ρ(domain exposure, benchmark score) at each model size
- Fisher z-test statistic and one-tailed p-value for directional comparisons
- Panel OLS β coefficients with standard errors and 95% confidence intervals
- Wald z-statistic for β_Wikipedia vs β_Books comparison per benchmark
- LRT χ² statistic for benchmark-specific vs shared-β model

## 4.6 Compute Resources

Benchmark evaluation was run on 5× H100 NVL GPUs. Approximate evaluation time: ~30 minutes per checkpoint for 6.9B models, ~5 minutes for 70M. The full 154-checkpoint × 3-model-size evaluation (462 total evaluations) was running in background at analysis time. Domain lookup construction (600K documents) completed in 3.5 minutes on standard CPU hardware.
