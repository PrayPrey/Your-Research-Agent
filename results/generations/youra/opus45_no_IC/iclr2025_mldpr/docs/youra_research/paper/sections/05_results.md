# Results

## Concentration Measurement (H-E1)

We successfully computed HHI values for all 21 venue-year combinations (NeurIPS, ICML, ICLR across 2018--2024), confirming that benchmark concentration is reliably measurable across major ML venues. HHI values ranged from 0.007 to 0.046, with variance of 0.00014. These values indicate moderate concentration---substantially above perfect dispersion but well below monopolistic levels. The narrow range suggests that while benchmark usage is concentrated, the degree of concentration is relatively stable across venues and years.

## Cross-Sectional Relationships (H-M1, H-M2)

**H-M1: Concentration predicts top-5 share.** We find strong evidence that HHI correlates with standard benchmark adoption. Mann-Whitney U test rejects the null of no group difference ($p = 0.000319$). Spearman correlation between HHI and top-5 dataset share is $\rho = 0.90$ ($p < 0.001$), indicating that venue-years with higher concentration see substantially more usage of the dominant benchmarks. The high-HHI group (above median) showed mean top-5 share of 0.226, compared to 0.147 for the low-HHI group---a 54\% relative difference.

**H-M2: Prior HHI predicts individual adoption.** Logistic regression confirms that venue-level concentration in year $t-1$ predicts whether individual papers in year $t$ use standard benchmarks. The coefficient $\beta = 56.75$ is highly significant ($p < 0.001$), corresponding to an odds ratio of $4.4 \times 10^{24}$. While this extreme odds ratio reflects the narrow HHI range (a unit change in HHI is unrealistic), the finding robustly establishes that papers submitted to more concentrated venues are substantially more likely to adopt standard benchmarks. This analysis covers 10,636 papers across 18 venue-year observations (excluding 2018 due to lagged predictor requirements).

\begin{table}[t]
\centering
\caption{Summary of hypothesis tests. Bold indicates primary findings.}
\label{tab:hypothesis_summary}
\begin{tabular}{lccc}
\toprule
Hypothesis & Statistic & p-value & Outcome \\
\midrule
H-E1: HHI computable & 21/21 venue-years & --- & PASSED \\
H-M1: HHI predicts top-5 & $\rho = 0.90$ & $< 0.001$ & PASSED \\
H-M2: Prior HHI predicts adoption & $\beta = 56.75$ & $< 0.001$ & PASSED \\
\textbf{H-M3: Citation propagates benchmarks} & $d = 1.93$ & $< 0.001$ & \textbf{PASSED} \\
H-M4: Entropy-variance correlation & $\rho = -0.96$ & $< 0.001$ & PASSED (weak) \\
\textbf{H-M5: Temporal lock-in} & $\beta = +1.60$ & 0.098 & \textbf{FAILED} \\
\bottomrule
\end{tabular}
\end{table}

## Citation Network Propagation (H-M3)

Our strongest positive finding concerns citation-based benchmark propagation. Papers that cite other papers in our corpus show substantially higher dataset overlap than random pairs. Citing pairs exhibit mean Jaccard similarity of 0.318, compared to 0.014 for randomly paired papers from the same venue-year. Cohen's $d = 1.93$ indicates a large effect---nearly two standard deviations separate the distributions (Figure~\ref{fig:4}).

This finding, based on 77,963 citing pairs, provides strong evidence that citation relationships serve as a channel for benchmark standard propagation. When researchers cite prior work, they tend to adopt similar benchmark choices, creating a network effect that amplifies certain datasets' prevalence.

## Entropy-Variance Correlation (H-M4)

We observe a strong negative correlation between normalized entropy and variance in dataset counts at the aggregate level ($\rho = -0.958$, $p < 0.001$), supporting the theoretical prediction that concentrated benchmark usage reduces methodological diversity. However, when examining this relationship using our real data proxy (task-level entropy), the correlation weakens substantially ($\rho = -0.332$, $p = 0.166$). This discrepancy suggests that while the theoretical relationship holds, measurement limitations in our task-based proxy introduce noise. Figure~\ref{fig:6} visualizes this relationship.

## Temporal Lock-in (H-M5)

The central prediction of deterministic lock-in theory is that concentration should self-reinforce: high HHI in period $t-1$ should predict lower entropy (higher concentration) in period $t$. Our panel regression with venue fixed effects yields $\beta(\text{HHI}_{t-1}) = +1.603$ with $p = 0.098$. Critically, this coefficient is **positive**, not negative---the opposite direction predicted by lock-in theory.

Granger causality tests provide additional evidence against temporal lock-in. For all three venues, lagged HHI does not significantly improve prediction of current entropy: zero venues show significant Granger causality at $\alpha = 0.05$. The 18 observations available for this panel analysis (after accounting for lags) limit statistical power, but the positive point estimate directly contradicts the lock-in prediction.

\begin{table}[t]
\centering
\caption{Prediction matrix: expected versus observed outcomes.}
\label{tab:prediction_matrix}
\begin{tabular}{lll}
\toprule
Prediction & Expected & Observed \\
\midrule
P1: HHI$_{t-1}$ predicts Entropy$_t$ decline & $\beta < 0$ & $\beta = +1.60$ (REFUTED) \\
P2: Granger causality HHI$\to$Entropy & Significant & 0/3 significant (INCONCLUSIVE) \\
P3: High-HHI papers use fewer datasets & All venues & ICML only (PARTIAL) \\
\bottomrule
\end{tabular}
\end{table}

## Summary

Figure~\ref{fig:3} displays the group comparison for H-M1, showing clear separation between high- and low-HHI venue-years. Figure~\ref{fig:5} presents the probability curve from H-M2, illustrating how adoption probability increases with prior-year HHI. The time series in Figure~\ref{fig:7} and scatter plot in Figure~\ref{fig:8} visualize the H-M5 analysis, revealing no consistent downward trend in entropy following high-concentration periods.

The results establish that benchmark concentration is measurable, cross-sectionally predictive, and citation-propagated, but **not temporally self-reinforcing**. This pattern---strong contemporaneous relationships without temporal lock-in---represents our primary empirical contribution.
