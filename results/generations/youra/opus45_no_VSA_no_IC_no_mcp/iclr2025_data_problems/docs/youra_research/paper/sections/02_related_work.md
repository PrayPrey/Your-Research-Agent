# Related Work

Our work sits at the intersection of data curation methodology and training dynamics analysis. We review prior work in three areas: data curation pipelines for foundation models, perplexity-based quality filtering, and systematic ablation studies in related domains.

## Data Curation Pipelines

The emergence of large-scale language models has driven substantial work on training data preparation. The Data Management for Training Large Language Models survey [Zha et al., 2023] provides a comprehensive overview of quality filtering, deduplication, and toxicity filtering techniques that underpin modern pipelines.

RedPajama [Together Computer, 2023] and Dolma [Soldaini et al., 2024] represent state-of-the-art open curation pipelines, processing 100B+ tokens with standardized recipes including perplexity filtering, MinHash deduplication, and domain mixing. These pipelines report benchmark improvements over raw data, but vary multiple factors simultaneously—data source, filtering threshold, mixing ratio—making it impossible to attribute gains to specific decisions.

C4 [Raffel et al., 2020], the foundational curation approach underlying T5, established perplexity filtering as standard practice but did not disclose specific thresholds or conduct systematic ablation. Subsequent work has largely inherited these choices without validation.

**Limitation:** Current pipelines compare final configurations holistically. No controlled study isolates individual curation parameters to quantify their effects independently.

## Perplexity-Based Quality Filtering

Perplexity as a quality signal has received recent theoretical attention. "How to Train Data-Efficient LLMs" [Tirumala et al., 2024] demonstrates that perplexity filtering improves training efficiency, but studies perplexity alongside other factors without isolation. "Perplexed by Perplexity" [Abbas et al., 2024] questions whether optimal thresholds vary by domain and model scale, finding that one-size-fits-all approaches may be suboptimal—but stops short of systematic sweep analysis.

The standard approach uses KenLM 5-gram models trained on Wikipedia to score samples [Wenzek et al., 2020], filtering those above a percentile threshold. This CCNet methodology underlies most modern pipelines. However, threshold selection remains largely heuristic: p30, p50, or p70 are common choices without empirical justification for specific values.

**Limitation:** While perplexity filtering is ubiquitous, no study has mapped the full dose-response curve across threshold levels to identify optima.

## Systematic Curation Studies

The DataComp benchmark [Gadre et al., 2023] provides the closest methodological precedent to our work. By systematically varying image curation strategies under controlled conditions, DataComp demonstrated that intermediate CLIP Score thresholds outperform both extremes—a finding analogous to our hypothesis in the text domain. This work establishes that dose-response relationships can be mapped in curation, though the specific mechanisms differ between vision and language.

In the language domain, contamination detection research [Shi et al., 2024; Xu et al., 2024] has developed rigorous methodology for validating benchmark integrity, including Min-K%++ for membership inference. While orthogonal to our curation focus, this work emphasizes the importance of controlled experimental design when measuring benchmark effects.

Data attribution methods including TRAK [Park et al., 2023] and influence functions enable tracing model behavior to training samples. These tools could, in principle, identify which filtered samples most affect performance—a direction for future work.

**Our Position:** We extend the DataComp methodology to LLM pretraining, treating curation parameters as continuous variables and mapping their effect surfaces with fixed-token experimental design. Unlike prior pipeline comparisons, we isolate individual parameters to quantify dose-response relationships. This enables principled threshold selection based on empirical evidence rather than heuristic choice.
