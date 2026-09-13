# Discussion

## Principal Finding: Propagation Without Lock-in

Our results reveal a nuanced picture of benchmark standardization in machine learning. Citation networks demonstrably propagate benchmark choices ($d = 1.93$), and venue-level concentration predicts individual adoption ($\beta = 56.75$, $p < 0.001$). Yet the temporal lock-in mechanism central to path-dependence theories fails to materialize: prior concentration does not predict subsequent concentration increases ($\beta = +1.60$, wrong sign). This pattern---strong cross-sectional relationships without intertemporal feedback---suggests that benchmark standardization reflects ongoing coordination rather than irreversible lock-in.

## Theoretical Implications

The absence of temporal lock-in challenges deterministic accounts of benchmark dominance. Our findings are more consistent with a **co-evolution model** wherein benchmark standards and research practices mutually adapt. Under this view, standard benchmarks emerge from researcher coordination (explaining the citation propagation effect) but remain responsive to field-level shifts in research priorities. The system exhibits inertia---citation-based propagation creates persistence---without the absorbing state dynamics that characterize true lock-in.

This distinction carries practical implications. If benchmark dominance were path-dependent and self-reinforcing, intervention would require overcoming increasing returns that compound over time. The co-evolution alternative suggests that the research community retains agency: new benchmarks can gain traction when they address recognized limitations, without confronting an ever-steepening coordination barrier.

## Limitations

Several limitations constrain interpretation. First, our panel comprises only 21 venue-year observations, limiting statistical power for temporal analysis. The non-significant Granger tests may reflect insufficient data rather than true absence of dynamics. Replication with extended time series or additional venues would strengthen conclusions.

Second, Papers with Code provides task-level rather than dataset-level annotations in some cases. Our HHI calculations use the available granularity, but conflating tasks with datasets may attenuate or distort concentration estimates. The weak real-data result for H-M4 ($\rho = -0.332$, $p = 0.166$) may partly reflect this measurement limitation.

Third, our design is observational. While we establish that citation predicts benchmark similarity, we cannot exclude confounding by research topic---papers may cite and share benchmarks because they address similar problems, not because citation causes adoption. The effect size ($d = 1.93$) substantially exceeds what topic overlap alone would plausibly explain, but causal claims require additional design elements.

## Broader Impact

The finding that citation propagates standards without temporal lock-in has implications beyond methodology. Debates over benchmark limitations---concerning diversity, representativeness, or incentive distortions---often assume that dominant benchmarks are entrenched. Our results suggest this entrenchment may be overstated. The research community appears capable of updating its standards, provided that alternatives address recognized limitations.

Figures~\ref{fig:7} and~\ref{fig:8} visualize the temporal dynamics underlying these conclusions, showing no systematic relationship between lagged concentration and subsequent entropy. Rather than deterministic trajectories toward ever-greater concentration, we observe fluctuation around stable levels---consistent with a system in dynamic equilibrium.

Future work should extend the temporal window to test whether lock-in operates at longer lags, examine whether specific benchmark transitions (e.g., ImageNet to newer datasets) exhibit different dynamics than steady-state maintenance, and develop interventions that leverage the citation propagation mechanism to accelerate beneficial benchmark evolution.
