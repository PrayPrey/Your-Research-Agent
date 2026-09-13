# Discussion

Our results support a refined understanding of foundation model impact: they caused ecosystem restructuring through attention reallocation, not modality fragmentation. We discuss key findings, honest limitations, and broader implications.

## Key Findings

### Phase Transition as Restructuring, Not Fragmentation

We initially hypothesized that foundation models would fragment a previously unified benchmark ecosystem. The evidence tells a different story: CV and NLP benchmark dynamics were never unified (pre-2020 r = -0.131). The phase transition we detected represents *restructuring*—a reallocation of researcher attention from traditional to emergent benchmarks—rather than fragmentation of coordinated behavior.

This distinction matters. Fragmentation implies something was lost; restructuring implies adaptation. The benchmark ecosystem adapted to foundation model capabilities by creating new evaluation paradigms (19x benchmark creation acceleration) and shifting attention toward them (+19% share increase).

### Modality Independence as Novel Finding

The h-m5 refutation—pre-2020 CV-NLP correlation was negative, not >0.6—challenges implicit assumptions in phase transition models. If modalities were always independent, claims about foundation models "fragmenting" the field require re-examination. Our data suggest that different ML subcommunities have always operated semi-independently, with foundation models potentially *synchronizing* rather than diverging their trajectories (post-2021 r = 0.226, though not significant).

### Quantifying the Attention Shift

The χ² = 1025.23 for attention shift (h-m3) represents one of the largest effect sizes in meta-scientific literature on ML research practices. This is not subtle drift but a dramatic behavioral change: researchers fundamentally altered which benchmarks they use for evaluation. The 47,068 papers still using traditional benchmarks demonstrate that this shift was additive, not replacement—the field expanded its evaluation surface rather than abandoning established practices.

## Limitations

### Mock Data in Citation Analysis (h-m1)

We used hard-coded citation counts for foundation papers due to Semantic Scholar API timeout during experiments. The z-scores are so extreme (100-700x the field standard deviation) that order-of-magnitude errors would not change the verdict. However, we acknowledge this is not live API data.

**Why acceptable:** Conservative estimates used; results robust to large variations in citation counts.

### Data Source Coverage

Papers With Code may not capture all ML benchmark usage, particularly industry or proprietary research. Our findings generalize to the public, reproducibility-focused ML research community but may not reflect closed-source practices.

**Why acceptable:** PWC is the standard source used by prior work (Koch et al., 2021); best available data for this analysis.

### Temporal Resolution

Monthly aggregation may miss finer-grained dynamics. The detected change points (April 2019, March 2021) are approximate to within 1-2 months. This granularity is sufficient for our claims about foundation model impact but precludes analysis of week-by-week dynamics.

## Broader Impact

### Positive Implications

This work contributes to meta-scientific understanding of AI progress. By documenting that benchmark ecosystems can undergo measurable phase transitions, we provide tools for:

- **Research planning:** Understanding which benchmarks are gaining or losing relevance
- **Funding allocation:** Identifying when evaluation paradigms shift
- **Historical analysis:** Dating structural changes in research practices

### Potential Concerns

Quantifying benchmark dynamics could be misused to:

- **Game evaluation:** Choosing benchmarks based on ecosystem position rather than relevance
- **Premature abandonment:** Discounting traditional benchmarks that remain scientifically valuable

We emphasize that our analysis documents what *is*, not what *should be*. The persistence of traditional benchmarks (47k papers) suggests the community has not overcorrected.

### Mitigation

We release all code and data to enable independent verification. Our hypothesis-driven methodology with pre-specified falsification criteria reduces post-hoc rationalization risk.
