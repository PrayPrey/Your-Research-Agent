# 7. Conclusion

We began with an observation: professional medicine questions appear in The Pile v1 at 43 times the rate of high school mathematics questions. This differential is not an accident — it is a direct consequence of The Pile's deliberate inclusion of domain-aligned academic sources. And it is invisible to practitioners who report aggregate MMLU accuracy as if contamination were uniformly distributed across sub-tasks.

This work provides the map that was missing. We computed the first unified cross-corpus contamination atlas: a 59-sub-task × 3-corpus matrix of 13-gram containment rates for MMLU, HellaSwag, and BIG-Bench Hard against The Pile v1, C4 en.noclean, and RedPajama-v1. Our main contributions are:

1. **Existence of sub-task contamination variance**: Kruskal-Wallis H=590.82, p=2.73×10⁻⁸⁹, with a 40× differential between the most and least contaminated sub-tasks — confirming that aggregate benchmark scores mix sub-tasks with radically different contamination risks.

2. **Corpus composition as the predictor of contamination levels**: The Pile (6.53%) significantly exceeds C4 (4.05%) by 38%, while The Pile and RedPajama are statistically indistinguishable (Dunn p=0.810) due to shared CommonCrawl ancestry. Corpus scale does not predict contamination; source composition does.

3. **Directional domain stratification**: Academic MMLU sub-tasks are contaminated at 2–3× higher rates than commonsense benchmarks across all three corpora (Cohen's d=0.85), consistent with corpus source composition predictions — though full statistical confirmation awaits finer BBH sub-task granularity.

We close with three future directions, each grounded in our results:

**From our unexpected finding** (Pile≈RedPajama despite different curation): Full-corpus streaming for both corpora with the WIMBD endpoint configured would test whether this equivalence persists at full scale or is an artifact of 10% sampling. If it persists, CommonCrawl ancestry is confirmed as the dominant contamination predictor; if not, the detailed differences in RedPajama's curated components become the focus.

**From our underpowered test** (h-m2 with n=2 commonsense): Re-running h-m1 with individual BBH sub-tasks (23 sub-tasks instead of 1 aggregate) would expand the commonsense group to n=24, providing the statistical power needed for Mann-Whitney confirmation of the domain stratification pattern. With Cohen's d=0.85 already established, this is the most achievable high-impact extension.

**From our unverified claim** (metric consistency): Executing h-m3 — computing Spearman rank correlation between 13-gram containment and Jaccard similarity rankings across all 59 sub-tasks × 3 corpora — would complete the original hypothesis and establish whether the two most widely used contamination metrics produce consistent rankings.

The contamination atlas we provide is a first map, not a final answer. But it reveals that the terrain is far more varied than the field has assumed: contamination concentrates in predictable domains, follows corpus composition, and varies by 40× across the sub-tasks that practitioners average together. Understanding this structure is a prerequisite for contamination-aware evaluation — and contamination-aware evaluation is a prerequisite for trusting that benchmark improvements reflect genuine capability gains.
