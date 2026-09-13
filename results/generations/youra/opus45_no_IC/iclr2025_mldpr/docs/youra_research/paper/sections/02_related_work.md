# Related Work

Our study connects three research streams: qualitative analyses of benchmark construction, quantitative reproducibility investigations, and concentration measurement in science. Each provides essential background but none addresses whether benchmark concentration creates temporal feedback loops.

## Benchmark Analysis and Construction

Sociological and ethnographic studies have examined how benchmarks become established standards. Engdahl (2024) provides a detailed qualitative account of benchmark construction in machine learning, documenting the community processes through which particular datasets become accepted evaluation standards. This work illuminates the social dynamics behind standardization—how workshops, competitions, and influential papers establish benchmarks—but does not quantify whether these dynamics create lock-in over time.

Technical work on benchmark design addresses quality and coverage. Holistic evaluation platforms such as Dynaboard (Ma et al., 2021) aim to provide richer assessment than single-metric leaderboards, while large-scale benchmark collections like HPO-B (Pineda-Arango et al., 2021) aggregate datasets from sources like OpenML to enable broader hyperparameter optimization research. These efforts recognize concentration as a concern and attempt to address it through expanded evaluation resources. However, they do not measure whether the field actually exhibits the self-reinforcing dynamics that would make expanded benchmarks difficult to adopt.

Critiques of benchmark validity appear throughout the literature. Arguments that standard datasets overfit to narrow test distributions, that leaderboard competition displaces substantive research questions, and that evaluation metrics poorly correlate with real-world performance all motivate concern about benchmark concentration. Yet these critiques typically assume lock-in rather than testing for it. A field could have concentrated benchmark use for coordination benefits without being trapped—and our temporal analysis suggests this is closer to the actual situation.

## Reproducibility and Replication Studies

A substantial literature examines whether machine learning results replicate. Olszewski et al. (2023) investigate the relationship between reproducibility and artifact evaluation committees, finding limited effects of formal review processes on subsequent replication success. This work tracks methodological practices but focuses on code and experiment availability rather than dataset selection dynamics.

Broader reproducibility initiatives document practical barriers to replication: missing code, unstated hyperparameters, and dataset preprocessing differences. These studies reveal that benchmark use involves more complexity than simply downloading standard splits. However, the reproducibility literature examines whether individual results replicate rather than whether aggregate dataset concentration creates feedback effects across the research community.

The distinction matters because reproducibility concerns and lock-in concerns have different implications. Reproducibility requires better documentation and artifact sharing; lock-in would require active intervention to break feedback cycles. Our finding that temporal feedback is absent suggests the community faces the former challenge more than the latter.

## Concentration Metrics in Science Studies

Science of science research has developed measures of concentration in research portfolios, citation patterns, and topic distributions. The Herfindahl-Hirschman Index (HHI), originally from industrial organization economics, has been applied to publication concentration across topics, author productivity distributions, and institutional research portfolios.

We adapt HHI to benchmark selection, computing concentration across datasets rather than across topics or authors. This operationalization enables direct measurement of whether evaluation practices are concentrated and whether concentration changes over time. Prior applications of HHI in science studies have typically examined cross-sectional patterns rather than temporal dynamics.

Bibliometric studies of citation networks document how influence propagates through scientific communities. The observation that highly cited papers share characteristics with their references appears across fields. Our analysis extends this finding to benchmark datasets specifically, showing that citation links carry evaluation choices as well as ideas. However, demonstrating propagation differs from demonstrating feedback—the key distinction our temporal analysis addresses.

## The Gap: No Temporal Causality Test

Existing work establishes that benchmark concentration exists, that benchmarks spread through community processes, and that citation patterns reveal intellectual influence. What no prior study provides is a quantitative test of whether concentration in one time period causally affects diversity in subsequent periods—the defining characteristic of lock-in.

Panel regression methods and Granger causality tests can identify such feedback effects when they exist. Our application of these methods to benchmark concentration represents the first temporal causality analysis of dataset selection dynamics. The absence of significant effects does not invalidate prior concerns about benchmark quality or coverage; it does indicate that the community is not trapped in a feedback loop that prevents evaluation practice from evolving.
