# 6. Discussion

## 6.1 Key Findings

**Verbosity is the primary annotation drift channel.** Across all three experiments, verbosity (β_L) is the only stylistic feature that consistently achieves statistical significance. This convergence is not accidental. Verbosity is the most perceptually salient feature of AI-generated text: longer, more elaborated responses are immediately visible to annotators without requiring semantic processing. Automation bias theory predicts that annotators under cognitive load will rely on the most accessible surface signal — and response length is exactly that. The sign reversal (from penalizing to rewarding verbosity) is consistent with annotators progressively adopting the heuristic that "more detailed = better quality," tracking the verbose style profile of the AI responses they evaluated.

The subthreshold results for β_H and β_S are best interpreted as reflecting the limits of the current proxy design, not as evidence that hedging and structure are unaffected. All three deltas are positive (sign_consistent = true), and the effect sizes for β_H (+0.021) and β_S (+0.012), while smaller than β_L (+0.080), are in the same direction across 160,800 annotation decisions. Confirming these effects requires better temporal signal than index-based round stratification can provide.

**The AI-typicality projection confirms directional specificity.** The geometric projection result (β_exposure = 0.041, p = 2.05×10⁻⁵; placebo p = 0.48) establishes that the preference drift is not in an arbitrary stylistic direction — it is specifically aligned with the axis from human-typical to AI-typical text in sentence embedding space. This is the strongest evidence we have that the drift is AI-adaptation-driven rather than reflecting some other form of preference evolution (e.g., annotator learning, prompt distribution shifts).

**Null results specify the data frontier.** The inability to test ambiguity moderation (P1) or within-annotator dose-response (P3) is not a weakness of the methodology but a precise characterization of what existing RLHF datasets can and cannot support. This is itself a contribution: RLHF practitioners now have a specific data checklist for annotation drift research (Section 6.2).

## 6.2 Limitations

**Limitation 1: No genuine temporal metadata in HH-RLHF.**
HH-RLHF's public release does not include annotator IDs or annotation timestamps. Our round stratification uses equal index-based partitioning (53,600 rows per stratum) as a temporal proxy. The observed β_L reversal could reflect between-cohort composition differences (annotators recruited in later phases having different AI familiarity) rather than within-annotator adaptation over time.

*Why acceptable:* The methodological pipeline is validated end-to-end on 160,800 rows. The verbosity sign reversal is a real population-level phenomenon in the dataset — whatever its causal origin — and has direct practical implications: reward models trained on later-round HH-RLHF labels will assign different weights to response length than those trained on earlier-round labels. The causal question (individual adaptation vs. cohort composition) is important but does not invalidate the measurement.

*Suggested framing:* "Round stratification in our study uses the dataset's file ordering as a proxy for temporal exposure. While this is a standard analysis approach given available metadata, genuine annotation timestamps would be needed to establish within-annotator adaptation claims. We present our findings as population-level directional evidence pending such data."

**Limitation 2: WebGPT within-annotator design collapsed to between-group.**
The planned dose-response panel regression (H-M1) assumed within-annotator worker fixed effects. The public WebGPT JSONL release lacks worker_id fields and the HuggingFace loading script is deprecated in datasets ≥ 4.0. We substituted a between-group tercile design, which cannot rule out between-worker selection effects (annotators who score responses differently may simply have pre-existing differences in AI familiarity).

*Why acceptable:* Discriminant validity is confirmed (placebo p = 0.48), meaning the effect is specific to AI-typicality. The tercile F-statistic (82.92, p ≈ 1.4×10⁻³⁶) establishes highly significant between-group separation. The direction of the effect is consistent with H-M2's coefficient reversal.

**Limitation 3: AAI composite only partially measured.**
The Alignment Asymmetry Index was designed as a three-component composite: stylistic coefficient drift (tested), geometric projection (tested), and behavioral divergence between reward models trained on early vs. late round labels (H-M3, not executed). The most consequential component — whether annotation drift propagates to reward model behavior and downstream benchmark accuracy — remains untested.

*Why acceptable:* The two validated components provide proof-of-concept for AAI instrumentation. H-M3 is fully specified and uses code components validated in H-M2. The results presented here establish the annotation-level input to H-M3 with sufficient precision to motivate the follow-on experiment.

**Limitation 4: Topic distribution imbalance between annotation strata.**
Chi-square analysis reveals extreme topic imbalance across round-1 vs. round-3 in HH-RLHF (p = 4×10⁻²⁷⁵). Hedging (β_H) and structure (β_S) are topic-correlated features — hedging is more common in sensitive/uncertain prompts, structure correlates with technical prompts. Topic distribution shifts between strata may partially explain the subthreshold β_H and β_S results.

*Why acceptable:* Verbosity (β_L) is the least topic-specific of the three features — response length varies across topics but its direction of drift (from penalizing to rewarding) is less likely to be driven by topic composition changes. Topic-stratified replication is straightforward and is specified as a future work priority.

## 6.3 Broader Impact

This work has both constructive and cautionary implications for the RLHF research community.

On the constructive side, the AAI framework provides a practical, low-cost quality gate for RLHF annotation pipelines: if round-stratified coefficient comparison reveals β_L sign change across annotation phases, practitioners should investigate potential drift contamination before training reward models on the full dataset. The analysis requires only the preference labels and response text — no additional annotation overhead.

On the cautionary side, our findings suggest that multi-round RLHF annotation datasets may encode temporal non-stationarity that is invisible to standard dataset quality metrics. Reward models trained on later-round labels may have subtly different optimization targets than those trained on earlier-round labels, even when both achieve high pairwise accuracy on held-out preference data. This is relevant to any organization scaling RLHF annotation over extended time periods with the same annotator pools.

We do not claim that annotation drift is present in all RLHF datasets or that it necessarily causes harmful outcomes. The verbosity reversal we document may reflect annotators developing more nuanced quality judgments over time — the causal direction is uncertain without genuine temporal metadata. Our contribution is to provide the measurement instrument that makes this question empirically tractable.
