# Conclusion

We began with the observation that most machine learning datasets are invisible — not because they lack quality, but because they lack tags. This paper has demonstrated that the invisibility is quantifiable, structural, and remediable.

## 7.1 Summary of Contributions

In this work, we addressed the gap between the FAIR F1 (Findability) principle and its empirical consequences on ML dataset adoption by isolating binary keyword tag presence and tag count as independent variables in negative binomial regression. Our findings establish:

1. **Binary tag presence yields a 22.6% adoption advantage** (IRR=1.2263, 95% CI [1.1681, 1.2873], p<0.001, N=5,217) that is structural — surviving decade fixed effects with only 12.2% attenuation despite extreme era-tag collinearity (Cramér's V=0.823). Any tagging is the critical first step.

2. **Tag count magnitude amplifies the advantage log-linearly** within tagged datasets (IRR=1.5332 per log(tag_count+1), N=2,625, p<0.001), with essentially zero decade confounding (attenuation ratio=1.0007). The amplification mechanism operates through search pathway expansion, independent of platform era.

3. **Comprehensive tagging (6+ tags) is the dominant categorical tier** (IRR=1.2861, meaningfully distinct from 1-5 tags at p=5.54×10⁻¹⁰), while the 1-2 and 3-5 ranges produce statistically indistinguishable effects — a consequence of bimodal user tagging behavior on OpenML.

The informative negative result for uniform categorical dose-response (H-M3) is honest and informative: it reveals that OpenML users tag either comprehensively or not at all, making the 1-2 tag range a sparse middle ground. This does not weaken the primary finding — it refines the practical recommendation toward the 6+ tag target.

## 7.2 Future Directions

Three directions emerge directly from the evidence:

**From untested alternative explanations:** The most important open question is reverse causality — whether popular datasets attract tags rather than tags attracting tasks. Testing this requires OpenML API data with tag assignment timestamps and task creation timestamps to verify temporal ordering at the individual dataset level. A natural experiment around OpenML API changes that affected tagging permissions would provide stronger causal evidence.

**From unverified assumptions:** The tag-indexed search mechanism (Step 2 of the causal chain: search index membership → researcher discovery) is inferred from platform architecture and cross-domain corroboration, not directly observed via click-through logs. OpenML search API log analysis — tracing search query → click → task creation sequences — would verify or falsify this mechanism step directly.

**From scope extension:** Multi-platform replication (HuggingFace, Kaggle, UCI) would test whether the FAIR F1 threshold-plus-amplification structure generalizes beyond OpenML's specific tag-indexed search architecture. Yang et al.'s [2024] findings on HuggingFace suggest the direction is consistent, but the magnitude and shape may differ substantially across platform architectures.

## 7.3 Closing

As ML repositories grow and dataset proliferation accelerates — from thousands to millions of datasets — the structural advantages of keyword-indexed FAIR F1 compliance will compound. The ML community already struggles to find datasets appropriate for specific tasks; this challenge will not diminish as catalogs grow. A simple act at dataset upload — adding 6 or more descriptive keyword tags — may be among the highest-return investments a dataset creator can make for maximizing the reach and impact of their work. We hope this quantification motivates both individual creators and repository designers to treat FAIR F1 tagging not as a documentation checkbox, but as a discoverability mechanism with measurable adoption consequences.
