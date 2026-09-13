# 2. Related Work

## 2.1 Benchmark Lifecycle and Displacement Dynamics

The lifecycle of ML benchmarks has received increasing attention as the community grapples with benchmark saturation and the challenge of meaningful progress measurement. Ott et al. [CITATION:Ott2022] analyze 3,765 benchmarks in Nature Communications, finding that benchmark *breadth* (versatility across tasks) correlates with longevity at the population level. This population-level correlation motivates our investigation of whether individual-benchmark breadth predicts displacement timing — a finer-grained survival analysis question that Ott et al. do not address.

Koch et al. [CITATION:Koch2021] establish a 87-task taxonomy for Papers With Code (a subset of 133 core tasks) and measure *concentration* dynamics in benchmark adoption. Their methodology provides the h-e2 panel that underlies our analysis. Where Koch et al. characterize concentration trends across tasks, we use the same panel to test individual predictors of displacement events.

Paullada et al. [CITATION:Paullada2021] provide a qualitative governance framework for dataset lifecycles, arguing that benchmark datasets are sociotechnical artifacts whose trajectories are shaped by community norms, institutional pressures, and competitive incentives. Our work operationalizes their qualitative observations into a quantitative survival analysis framework — testing whether community participation breadth, a sociotechnical signal, predicts displacement timing.

## 2.2 Benchmark Overuse and Community Replacement

The ICLR 2025 workshop on benchmarking [CITATION:ICLR2025] explicitly foregrounds benchmark overuse as a driver of community-initiated replacement. Under this framing (our H2 saturation mechanism), a benchmark that has been widely adopted signals consensus that the task is "solved," incentivizing the community to propose harder successors. The GLUE → SuperGLUE transition is a canonical example: broad community adoption of GLUE (high diversity) was followed by recognition of GLUE's ceiling, driving rapid adoption of SuperGLUE [CITATION:Wang2019GLUE; CITATION:Wang2019SuperGLUE].

Our null result partially challenges this framing at the individual benchmark level: even if overuse is a driver of replacement in high-profile cases, submission count breadth at introduction year does not predict displacement timing across the broader population of 87 tasks. This suggests that either the mechanism operates through channels not captured by submission count (e.g., institutional concentration rather than breadth), or that the replacement dynamic is driven primarily by SOTA score velocity rather than adoption breadth.

## 2.3 Community Adoption and Lock-In Theory

Rogers' Diffusion of Innovations [CITATION:Rogers] provides the theoretical foundation for our H1 lock-in mechanism: early adopters become opinion leaders whose investment in a technology (or benchmark) creates network effects that slow transitions to alternatives. In the benchmark context, teams that publish results on a benchmark have reputational and computational investment in it, creating stickiness. Our null result suggests that this investment, at the aggregate level measured by submission count, does not translate into reduced displacement hazard.

## 2.4 Survival Analysis in Bibliometrics and Science of Science

Cox proportional hazards regression has been applied to publication lifetimes [CITATION:bibliometrics_survival], citation trajectories, and technology adoption. Our use of CoxPHFitter for benchmark displacement follows the methodology validated in prior h-m1 runs on the h-e2 panel (14/14 unit tests pass; EPV = 115 for the full panel). The key methodological challenge — identifying time-independent predictors that do not collapse into temporal proxies — is directly addressed by our FAIL FAST protocol.

## 2.5 Positioning

Our work differs from prior work in three ways. First, we use a survival model with a precisely defined displacement *event* (plurality handover), rather than population-level trends or qualitative case studies. Second, we introduce a pre-validation protocol that makes the null interpretable — ruling out data quality failure as a confound. Third, we provide a concrete negative result with adequate statistical power, contributing to the nascent literature on what does *not* predict benchmark displacement.
