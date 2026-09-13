# Research Idea

## Title
**Probing What Time Series Foundation Models Actually Learn: A Systematic Analysis Through Synthetic Controlled Experiments**

## Motivation
Time series foundation models (TSFMs) have shown impressive empirical results, yet they remain black boxes compared to interpretable statistical models like ARIMA or exponential smoothing. We lack fundamental understanding of what temporal patterns these models capture, whether they truly learn generalizable time series concepts (trend, seasonality, regime changes) or merely memorize dataset-specific features. This opacity hinders trust in high-stakes applications and limits principled model improvement. Understanding *what* TSFMs learn is crucial before we can reliably deploy them.

## Main Idea
We propose a systematic probing framework using carefully designed synthetic time series with known, controllable properties. Our methodology involves:

1. **Controlled Synthetic Benchmarks**: Generate time series with isolated components (pure trends, single/multiple seasonalities, level shifts, varying noise distributions, long-range dependencies) and systematic combinations thereof.

2. **Probing Tasks**: Design diagnostic tasks testing whether TSFMs can (a) detect presence of specific patterns, (b) correctly extrapolate them, and (c) generalize across parameter variations (e.g., unseen seasonal periods).

3. **Comparative Analysis**: Benchmark multiple TSFMs (TimesFM, Chronos, Moirai, Lag-Llama) against classical methods to identify where foundation models excel versus fail.

**Expected Outcomes**: A taxonomy of TSFM capabilities/limitations, actionable insights for model architecture improvements, and an open-source diagnostic toolkit. This work bridges the gap between empirical success and mechanistic understanding of TSFMs.