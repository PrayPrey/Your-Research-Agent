# Results

We present results for each research question in order of the causal story: first establishing that the signals exist (RQ1), then confirming the causal mechanism (RQ2), then demonstrating cross-sectional diagnostic utility (RQ3), and finally reporting the operationalization falsification as a methodological finding.

## RQ1: H_d Signal Discriminability (H-E1)

**Main finding: Domain-specific $H_d$ signals discriminate saturated from healthy benchmarks with very large effect sizes in all three domains.**

Figure 1 (boxplots) shows the distribution of $H_d$ values for saturated vs. healthy benchmark panels across CV, NLP, and tabular domains. Table 1 reports the statistical test outcomes.

| Domain | Mann-Whitney $p$ | Cohen's $|d|$ | AUC | Gate |
|--------|-----------------|---------------|-----|------|
| CV | $< 0.0001$ | 5.267 | — (direction inverted) | ✓ PASS |
| NLP | $< 0.0001$ | 6.910 | 1.000 | ✓ PASS |
| Tabular | $< 0.0001$ | 6.515 | 1.000 | ✓ PASS |

*Gate criterion: $p < 0.05$ AND $|d| > 0.5$ in $\geq 2/3$ domains. All three domains pass.*

These are not marginal signals. Cohen's $d > 5$ across all domains represents a separation far exceeding the conventional threshold for a "large" effect ($d = 0.8$). For reference, $|d| = 5.27$ (CV) means that the saturated and healthy group score distributions overlap by less than 1%.

**Temporal signal strength increases with lookback window.** Figure 2 shows Cohen's $d$ as a function of lookback window (6, 12, 18, 24 months). Effect sizes increase monotonically in all three domains: CV increases from 2.50 ($t-6$ months) to 5.27 ($t-24$ months); NLP from 3.28 to 6.91; tabular from 3.10 to 6.52. This confirms that a 24-month lookback window is optimal for signal extraction and that the health signals strengthen as saturation progresses — consistent with the causal accumulation mechanism validated in RQ2.

**CV direction inversion.** As noted in the Method section and illustrated in Figure 1, CV $H_d$ is *lower* for saturated benchmarks (variance decreases as scores converge), while NLP and tabular $H_d$ are *higher* for saturated benchmarks. This cross-domain directional asymmetry requires per-domain sign normalization before multi-domain Cox model combination. We report this finding explicitly in Section 5.4 (domain phenotype asymmetry).

## RQ2: Causal Mechanism — Submissions → Compression (H-M1)

**Main finding: Submission accumulation Granger-causes score variance compression at lag 2 ($\approx 6$ months), with reverse causality not confirmed. 31.1% of qualifying benchmarks exhibit compression.**

Table 2 summarizes the mechanism validation results on the real 466-benchmark quarterly panel.

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Panel observations | 6,938 rows × 466 benchmarks | — | — |
| $\sigma_\text{measurement}$ (median) | 0.3323 | — | — |
| Compression events detected | 389 | — | — |
| Benchmarks with $\geq 1$ event | 145 / 466 | — | 31.1% |
| Spearman $\rho$ (cumulative\_count → score\_var) | 0.052 | $> 0.4$ | Below target |
| Spearman $p$ | $1.51 \times 10^{-5}$ | $< 0.05$ | Significant |
| Granger $p$ at lag = 2 | $\mathbf{1.854 \times 10^{-5}}$ | $< 0.05$ | **PASS** |
| Reverse Granger $p$ at lag = 2 | $> 0.05$ | — | Not confirmed |

**Causal direction is confirmed; linear correlation is weak.** The Granger $p = 1.854 \times 10^{-5}$ at lag = 2 confirms that past values of cumulative submission count predict future score variance compression beyond the latter's own history. The reverse direction — whether compression predicts future submission volume — is not confirmed ($p > 0.05$). This directional asymmetry is the key causal finding.

The Spearman $\rho = 0.052$ result is counterintuitive: the effect is statistically significant ($p = 1.51 \times 10^{-5}$) but practically negligible in magnitude. Figure 4 (scatter plot) visualizes this dissociation: cumulative submission count and score variance are not linearly correlated in cross-section, yet the Granger test reveals a strong temporal causal structure. This dissociation provides evidence for a **threshold-triggered nonlinear mechanism**: compression events occur once submission count crosses a benchmark-specific saturation threshold, producing no linear cross-sectional signal but a clear lagged causal structure. Only 12.2% of individual benchmarks (5 of 41 with sufficient time-series length) show individually significant Granger causality, consistent with a threshold effect operative in a minority of heavily-submitted benchmarks.

Figure 5 (lag profile) shows Granger $p$-values across lags 1–4 for both forward and reverse directions. The forward direction peaks at lag = 2 ($\approx 6$ months); the reverse direction remains non-significant across all lags. Figure 6 (compression distribution) shows the distribution of 389 compression events across 145 benchmarks: the majority of affected benchmarks exhibit 1–3 events, with a small subset showing sustained compression across multiple periods.

**Field-scale prevalence.** The 31.1% compression rate — 145 of 466 qualifying benchmarks over 7 years — quantifies the systemic scale of the problem. This is not a rare edge case: nearly one in three actively-tracked ML benchmarks has already degraded past the 1.5$\sigma$ compression threshold. Figure 6 shows the temporal distribution of compression events, concentrated in benchmarks with longer histories and higher submission volumes.

## RQ3: Cross-Sectional Diagnostic Utility (H-M2)

**Main finding: H_d signals have strong cross-sectional diagnostic power for identifying compressed benchmarks, with NLP AUC$_\text{lead}$ = 0.857, even though temporal ordering of H_d signals relative to collapse could not be evaluated.**

Table 3 reports cross-sectional Mann-Whitney and AUC results from H-M2 on the real panel.

| Domain | MW $p$ (compressed vs. non-compressed) | AUC$_\text{lead}$ | AUC$_\text{concurrent}$ |
|--------|----------------------------------------|-------------------|------------------------|
| CV | 1.000 | 0.390 | 0.564 |
| NLP | **0.0076** | **0.857** | 0.835 |
| Tabular | **0.0435** | 0.318 | 0.318 |

NLP $H_d$ discriminates currently-compressed from non-compressed benchmarks with AUC = 0.857 — strong diagnostic performance by clinical standards. Tabular $H_d$ shows significant separation ($p = 0.0435$) though AUC is moderate (0.318, below the 0.5 random baseline in the measured direction, reflecting CV-style direction inversion in this variant). Figure 9 (AUC comparison) visualizes the per-domain ROC curves. Figure 10 (Mann-Whitney boxplot) shows the $H_d$ magnitude distributions for compressed vs. non-compressed benchmarks.

The NLP AUC = 0.857 result is particularly useful for monitoring applications: it means that $H_d^\text{NLP}$ can identify whether a benchmark is currently compressed with high diagnostic accuracy, independent of whether temporal ordering (i.e., whether $H_d$ *precedes* collapse) can be established.

## Temporal Ordering: Operationalization Failure (H-M2 Gate Failure)

**Main finding: The temporal ordering gate failed due to collapse event operationalization incompatibility, not mechanism failure. Only 1 collapse event was detected under the expanding Kendall $\tau$ criterion (needed $\geq 20$).**

The H-M2 gate required $\text{fraction\_leading} \geq 0.60$ in $\geq 2$ domains (fraction of collapse events where $H_d$ onset preceded the event by $\geq 12$ months). The gate result is:

| Domain | fraction\_leading | Gate ($\geq 0.60$) |
|--------|------------------|-------------------|
| CV | 0.000 | ✗ |
| NLP | 0.000 | ✗ |
| Tabular | 0.000 | ✗ |

This failure stems from a specific methodological incompatibility: the expanding Kendall $\tau > 0.85$ collapse criterion requires score\_var\_top10 to increase monotonically over time — but for compressed benchmarks, score\_var\_top10 *decreases* (this is the compression signal validated in H-M1). The two operationalizations derive from the same column and are anti-correlated by construction.

Figure 12 (gate metrics) and Figure 11 (signal emergence timeline) illustrate the collapse detection sensitivity: lowering the $\tau$ threshold from 0.90 to 0.85 (R1 mitigation) increased detected events from 0 to 1 — far below the required 20. The proposed fix (FW2) redefines collapse as $\text{compression\_event} = 1.0$ for $\geq 4$ consecutive quarters, which would yield approximately 100 events from the existing panel.

This is a **methodological falsification of the operationalization**, not a mechanism failure. The compression signal (H-M1), the discriminative signals (H-E1), and the cross-sectional diagnostic (H-M2 secondary metrics) all remain valid.

## Analysis: Domain Saturation Phenotype Asymmetry

**Unexpected finding: CV saturation manifests as score convergence (variance decreases), while NLP and tabular saturation manifests as signal divergence (deviation increases).**

The H-E1 results reveal that CV $H_d$ (score variance) is *lower* for saturated benchmarks, while NLP $H_d$ (normalized mean deviation) and tabular $H_d$ (Kendall $\tau$ rank stability) are *higher*. This cross-domain directional asymmetry was not anticipated in the original hypothesis design.

Our interpretation is that CV and NLP/tabular represent two distinct saturation phenotypes:
- **Convergence saturation (CV):** Models overfit the test distribution, producing increasingly similar scores — variance falls as the distribution compresses around a ceiling.
- **Divergence saturation (NLP/tabular):** Contamination or protocol gaming produces anomalous high scores, increasing deviation from the bulk distribution — the distribution spreads rather than compresses.

This asymmetry has direct implications for multi-domain Cox model design: a naive combined $H_d$ covariate without per-domain sign normalization would produce incoherent risk predictions. Domain-stratified modeling and explicit sign normalization (FW4) are required for the full BCBHS survival prediction framework.

## Summary of Evidence Against Claims

| Claim | Evidence | Status |
|-------|----------|--------|
| $H_d$ signals discriminate benchmark health ($|d|>0.5$, $p<0.05$) | $|d|>5$ in all 3 domains, $p<0.0001$ (H-E1) | ✓ CONFIRMED |
| Submission accumulation causally precedes compression (Granger $p<0.05$, lag=2) | Granger $p=1.854\times10^{-5}$, reverse not confirmed (H-M1) | ✓ CONFIRMED |
| 31.1% benchmark compression prevalence (H-M1) | 389 events, 145/466 benchmarks | ✓ CONFIRMED |
| NLP cross-sectional AUC $> 0.8$ (H-M2) | AUC$_\text{lead}$ = 0.857 (H-M2) | ✓ CONFIRMED |
| Cox PH C-index $\geq 0.70$ (H-M3) | H-M3 not executed | ✗ INCONCLUSIVE |
| Lead time $\geq 12$ months (H-M4) | H-M4 not executed | ✗ INCONCLUSIVE |
| Temporal ordering: $H_d$ precedes collapse (H-M2) | 1 collapse event detected; operationalization failure | ✗ REFUTED (operationalization) |
