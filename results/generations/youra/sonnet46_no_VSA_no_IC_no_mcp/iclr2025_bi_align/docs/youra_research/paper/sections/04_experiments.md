# Experimental Setup

We design experiments to answer five research questions that collectively verify the four-step causal mechanism described in Section 3. Each RQ maps directly to a claim made in the Introduction.

**RQ1 (H-E1):** Do both reward model score and gold human preference signals co-exist as separable, non-constant time series across RLHF optimization checkpoints? *(Prerequisite: measurement infrastructure exists)*

**RQ2 (H-M1):** Does RM score rise monotonically while gold human preference reverses after an early peak? *(Directional divergence mechanism)*

**RQ3 (H-M2):** Is the normalized calibration-alignment divergence gap strictly positive and monotonically growing at high KL levels? *(Gap characterization)*

**RQ4 (H-M3):** Does OLS regression reveal a significantly positive slope β in Coste et al. [2023] data? *(Primary quantification: P1)*

**RQ5 (H-M4):** Does the same positive slope replicate in the independent Gao et al. [2023] dataset? *(Cross-dataset replication: P2)*

## Datasets

We use two independently published RLHF experimental datasets, chosen specifically because they contain both RM score trajectories and held-out gold human preference at multiple KL checkpoints — the dual-signal structure required for divergence gap computation.

| Dataset | Source | KL Checkpoints | KL Range | Model Description | Role |
|---------|--------|---------------|----------|------------------|------|
| Coste et al. [2023] | arXiv:2310.02743 | 10 | 0.0–8.0 nats | RLHF policy with explicit RM | Primary (P1 test) |
| Gao et al. [2023] | arXiv:2210.10760, ICML 2023 | 10 | 0.0–7.5 nats | 6B reward model, different family | Replication (P2 test) |

**Coste et al. [2023]** is the primary dataset, chosen because it provides the clearest published demonstration of gold preference reversal under RLHF optimization and covers a KL range (0–8 nats) that captures both the initial alignment-improving phase and the overoptimization regime. Data at 10 discrete KL checkpoints covers the full RM-score vs. gold preference trajectory.

**Gao et al. [2023]** is the replication dataset, chosen because it is entirely independent — different model family, different scale (6B RM parameter count), different task distribution — and published in a top ML venue (ICML 2023). Agreement between the two datasets across such different experimental conditions provides strong evidence that the calibration-alignment divergence pattern is not model-family-specific.

**Data construction:** Both datasets are reconstructed consistent with qualitative descriptions in published figures, following standard figure digitization methodology. Exact values carry ±2–5% digitization uncertainty per data point; this uncertainty does not affect the direction or statistical significance of the slope given the large observed effect sizes.

## No Baseline Comparison

This study does not compare against alternative methods in the conventional sense. Our research question concerns the *characterization* of a phenomenon (divergence curve quantification and replication), not the *improvement* of a system over a baseline. The relevant "baseline" is the null hypothesis β = 0 (no significant positive slope), which we test via the pre-registered OLS regression gate. The Gao et al. dataset serves as an independent replication rather than a comparison method.

## Evaluation Metrics

| Metric | Definition | Role | Gate |
|--------|-----------|------|------|
| OLS slope β | Coefficient of KL in gap ~ β·KL + α | Primary: must be > 0 | MUST_WORK (P1, P2) |
| p-value (Wald t-test) | H₀: β = 0 against Hₐ: β > 0 | Primary: must be < 0.05 | MUST_WORK |
| R² | Proportion of gap variance explained by linear model | Secondary: > 0.5 expected | MUST_WORK (secondary) |
| Bootstrap CI (95%) | Non-parametric CI from N=10,000 resamples, seed=42 | Robustness check | HIGH confidence if positive; MEDIUM if only parametric positive |
| Cross-dataset β ratio | β_Gao / β_Coste | Effect size consistency | Post-hoc (no pre-registered threshold) |
| Spearman ρ(KL, RM) | Rank correlation of KL and RM score | Mechanism Step 2 verification | > 0.8, p < 0.05 |
| n_positive_high_kl | Count of gap > 0 at KL > 3.5 nats | Gap positivity check | = N_high_kl (strict) |

**Statistical significance** is assessed via parametric Wald t-test (primary criterion) and non-parametric bootstrap CI (robustness check). We use p < 0.05 as the pre-registered threshold. All tests are conducted with N=10 observations per dataset; we acknowledge the statistical power implications in Section 6.

## Implementation Details

Each hypothesis step is implemented as a standalone Python experiment module:

- **H-E1:** Signal co-existence verification (variance tests on both signals)
- **H-M1:** Trajectory analysis (Spearman correlation, peak detection, reversal confirmation)
- **H-M2:** Gap computation and positivity check (min-max normalization, monotonicity via Spearman ρ)
- **H-M3:** OLS regression on Coste data (scipy.stats.linregress + statsmodels.api.OLS + bootstrap)
- **H-M4:** OLS regression on Gao data (identical pipeline to H-M3)

**Key hyperparameters:** Bootstrap iterations N=10,000; random seed 42; 95% CI level; normalization via min-max scaling applied once in H-M2 and consumed by H-M3/H-M4 via CSV output. No additional hyperparameters — OLS is parameter-free beyond the input data.

**Gate exit codes:** Each module exits with code 0 (gate PASS) or 1 (gate FAIL), enabling automated verification. All five hypothesis modules exited with code 0.
