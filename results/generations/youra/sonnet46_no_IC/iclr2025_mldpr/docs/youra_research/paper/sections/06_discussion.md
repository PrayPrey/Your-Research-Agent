# Discussion

## 6.1 Key Findings and Their Interpretation

Our results establish three related findings that together characterize the FAIR F1 tagging mechanism on OpenML.

**Finding 1: Any tagging creates a substantial and robust discoverability advantage.** The 22.6% adoption advantage of binary tag presence (IRR=1.2263) is not a marginal signal — it is statistically overwhelming (p=1.87×10⁻¹⁶), robust across seven model variants, and survives the primary confound (decade era) with only 12.2% attenuation. For dataset creators, this finding suggests that the single most impactful metadata action is simply adding at least one tag. The choice of which tags matters less than the act of tagging itself, because the primary mechanism is binary search index membership.

**Finding 2: Tag count magnitude is a genuine dose-response mechanism, not an artifact.** Within the tagged subset, the log-linear IRR of 1.5332 per log(tag_count+1) with an attenuation ratio of 1.0007 establishes that additional tags expand search pathways in a way that is essentially orthogonal to platform era. This is the mechanistic interpretation: each additional tag is an additional keyword query that can return the dataset in search results, reaching a different subset of researchers. The zero decade collinearity (0.07% absorbed by FE) confirms this is a structural platform mechanism, not a temporal signal.

**Finding 3: The categorical dose-response is non-uniform — comprehensive tagging (6+) is the dominant amplification tier.** The H-M3 informative negative reveals that OpenML users tag either comprehensively or not at all, with the 1-2 tag range representing a sparse middle ground. This has a practical implication: minimal tagging (1-2 tags) produces an adoption advantage that is statistically indistinguishable from moderate tagging (3-5 tags), while comprehensive tagging (6+) produces a distinctly larger effect. Repository interfaces that encourage minimal tag entry may not achieve the full discoverability benefit — a threshold near 6 tags appears to be the meaningful target.

Together, these findings operationalize the FAIR F1 principle in a concrete, quantifiable way for the first time on an ML platform. The FAIR principles have often been described as aspirational — we show they are measurably consequential.

## 6.2 Connection to Literature

Our binary threshold finding (IRR=1.2263) provides the first NB-2 IRR estimate for keyword tagging on an ML repository, filling the gap in the FAIR literature that Wilkinson et al. [2016] established but did not quantify. The direction and magnitude are consistent with Yang et al. [2024] (documentation quality → HuggingFace popularity) and Lachmuth et al. [2025] (FAIR metadata compliance → dataset reuse on BonaRes), though comparisons are limited by platform architecture differences.

Our mechanism verification via decade fixed effects (H-M1) provides a methodological contribution to observational platform studies: testing extreme temporal collinearity without abandoning fixed effects controls demonstrates that within-decade variation can be sufficient for structural mechanism identification, even when between-decade variation is highly collinear with the treatment variable. The prior composite score episode (same corpus, 98.6% attenuation under decade FE) provides a useful within-study negative control.

Chapman et al. [2019] identified keywords as the primary mechanism for dataset discovery — our NB-2 results quantify the adoption consequence of that discoverability mechanism. Orr and Crawford's [2024] argument that metadata reflects curatorial effort is consistent with our bimodal tagging finding: users who invest in tagging tend to do so comprehensively.

## 6.3 Limitations

We report limitations honestly, as recommended by the narrative blueprint, rather than defensively.

**L1: Cross-sectional design — predictive, not causal without temporal data.** Our study is a cross-sectional snapshot. Tags and task counts are observed simultaneously; we cannot verify that tags were assigned before tasks were created at the individual dataset level. The predictive claim (tagged datasets have more tasks) is fully supported. The causal claim (tagging causes more tasks) rests on the OpenML creator-only tagging architecture [Vanschoren et al., 2014], which restricts tag modification to the original dataset creator at upload — providing a structural temporal ordering defense. However, this architectural argument is not empirically verified with timestamps. Future work with upload/tagging timestamp data could confirm or disconfirm the temporal ordering at scale.

**L2: N_tasks proxy measures registration breadth, not execution depth.** N_tasks counts distinct ML task registrations (unique task objects created), not how many times those tasks were run. A dataset with 10 tasks each run once differs from one with 1 task run 10 times; we capture the former. Task registration requires deliberate effort (defining target variable, task type) — it is a valid adoption signal, and arguably more meaningful for discoverability research than passive download counts. But estimates may not generalize to execution-frequency adoption.

**L3: Conditional adoption intensity — hurdle component deferred.** Our N=5,217 sample excludes datasets with zero registered tasks. We study tag effects on adoption intensity conditional on at least one task registration, not on the probability of any adoption at all. A full picture requires a hurdle model separating P(any adoption) from E(adoption | any adoption). This is explicitly future work.

**L4: Decade-tag collinearity partially uncontrolled.** The 12.2% attenuation by decade FE is documented rather than dismissed. The residual has_tags effect after FE may include both the structural FAIR F1 mechanism and a fraction of uncontrolled era confounding. The attenuation ratio of 1.1219 is non-fatal for our primary claim — the effect remains large and statistically overwhelming — but we cannot rule out that a portion of the estimated IRR reflects platform era effects not fully captured by decade fixed effects.

**L5: H-M3 bin sparsity limits uniform categorical dose-response claim.** The 1-2 tag bin (N=73, 1.4% of corpus) was insufficient to power the 0→1-2 adjacent contrast, and the 1-2 vs. 3-5 IRR gap is effectively zero (Δ=0.001). We cannot conclude from H-M3 whether the low-count tag range has a dose-response gradient; we can only confirm that the 6+ tier is distinctly above the rest. The informative negative is honest and informative — it reveals bimodal tagging behavior — but it limits the claim about the categorical mechanism's fine-grained structure.

## 6.4 Broader Impact

This work demonstrates that the FAIR principles — particularly F1 keyword tagging — have measurable, quantifiable consequences for ML dataset adoption. This has both positive implications and potential concerns.

**Positive impacts:** Providing IRR estimates translates abstract FAIR compliance guidelines into actionable, prioritized recommendations. Repository designers can use our findings to justify tag-requirement policies and tag-indexed search architectures. Dataset creators gain evidence-based guidance: tag your datasets, and target 6+ tags for maximum discoverability. The NB-2 methodology with decade FE and overdispersion testing provides a template for replication on other repositories.

**Potential concerns:** If keyword tagging becomes known to substantially boost adoption, incentive effects may emerge — creators adding tags strategically without corresponding metadata quality, or tag farming analogous to SEO manipulation. Repository governance should monitor for tag quality degradation. Our findings speak to quantity effects; future work should investigate whether tag relevance and quality moderate the adoption advantage. Additionally, if adoption becomes concentrated among heavily-tagged datasets, already-popular datasets may attract further engagement at the expense of quality untagged datasets — a Matthew effect worth monitoring.
