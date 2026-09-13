# Introduction

Machine learning researchers download datasets millions of times each year, yet we know remarkably little about the temporal dynamics of this collective behavior. While individual download counts are readily available on platforms like HuggingFace, the patterns of adoption over time—whether a dataset experiences sustained growth, sudden popularity spikes, or gradual revival—remain uncharacterized and taxonomically undefined. A dataset curator cannot predict whether their new contribution will follow a "flash-in-the-pan" trajectory or achieve sustained adoption, because these patterns have never been formally characterized.

This gap matters for three reasons. First, platform maintainers allocate maintenance resources blindly without understanding which datasets will sustain research interest. Second, researchers reinvent wheels by not discovering relevant older datasets that may be experiencing renewed utility. Third, the community lacks systematic insight into what drives sustained dataset impact versus transient popularity.

The surface-level problem is well-recognized: the ML community lacks systematic understanding of how datasets are adopted over time. Most researchers focus on dataset quality and benchmark performance, treating download statistics as simple popularity metrics rather than rich temporal signals. However, the deeper problem is that existing software ecosystem studies—which have successfully characterized package lifecycles in npm and PyPI—have not been transferred to ML dataset ecosystems, where different dynamics may apply. Benchmark designation effects, paper publication cycles, and domain-specific trends create adoption patterns that package managers do not exhibit.

The specific gap we address is the absence of a validated methodology for characterizing ML dataset lifecycle trajectories. npm studies used single-level clustering approaches that conflate a dataset's current phase (launch, growth, maturity, decline) with its underlying trajectory type. A young dataset in its growth phase cannot be distinguished from a mature dataset that happens to have similar current download rates. This phase-trajectory conflation prevents meaningful taxonomy development.

Our key insight is that download trajectories naturally partition into stable, interpretable clusters when analyzed with a two-level hierarchical approach that separates phase detection from trajectory classification. Level 1 applies PELT changepoint detection to identify discrete adoption phases within each trajectory. Level 2 applies DTW-based TimeSeriesKMeans clustering to group datasets by trajectory shape, independent of their current lifecycle phase. This separation reveals structure that single-level approaches obscure.

Building on this insight, we make the following contributions:

1. **Methodology:** We introduce a two-level hierarchical framework combining PELT changepoint detection (Level 1) with DTW-based trajectory clustering (Level 2), enabling phase-independent characterization of adoption patterns.

2. **Empirical Taxonomy:** We discover that HuggingFace dataset download trajectories partition into k=4 distinct clusters with silhouette score 0.35 (exceeding the 0.25 threshold) and exceptionally high bootstrap stability (Jaccard 0.82, exceeding the 0.65 threshold).

3. **Mechanistic Validation:** We validate that 81% of datasets exhibit statistically significant changepoints via PELT detection, confirming that adoption includes discrete phase transitions. Shape descriptors successfully differentiate clusters, with 3 of 4 descriptors exceeding variance ratio thresholds.

4. **Theoretical Insight:** We find that empirical adoption structure is simpler than theoretical taxonomies predict—two dominant behavioral archetypes (slow-burn and revival patterns) explain cluster differentiation, rather than the five archetypes originally hypothesized.

The remainder of this paper is organized as follows. Section 2 reviews related work on software ecosystem lifecycle analysis and time series clustering methods. Section 3 presents our two-level hierarchical methodology. Section 4 describes our experimental setup, and Section 5 presents results. Section 6 discusses implications and limitations, and Section 7 concludes with future directions.
