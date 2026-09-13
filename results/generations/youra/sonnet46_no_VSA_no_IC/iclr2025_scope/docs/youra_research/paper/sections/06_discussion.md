# Discussion

## 6.1 Key Findings and Their Interpretation

Our confirmed results from h-e1 establish three findings with direct implications for the entropy-guided selective SWA framework.

**Finding 1: Attention concentration is a near-universal structural property of Llama-2-7B.** The 100% satisfaction rate (Gini > 0.5, top-10% share > 0.5 across all 200 evaluation examples) is more than a statistical confirmation — it suggests that heavy-hitter attention concentration is an architectural invariant trained into Llama-2-7B's weights, not an input-specific phenomenon. This has practical implications: practitioners can apply the entropy scoring criterion on any representative calibration set and expect to observe meaningful concentration structure.

*Broader implication:* If attention concentration is architecturally grounded rather than input-driven, then the entropy criterion may generalize across input domains (beyond WikiText-103 calibration). Cross-domain calibration stability remains an open question (see Limitations), but the near-universal in-domain finding is a strong signal.

**Finding 2: Head-mean pooling is a first-class methodological choice.** The 32% relative gap between head-mean Gini (0.681) and head-max Gini (0.466) is a methodological finding with consequences beyond this paper. Any attention analysis method that uses per-layer entropy as a signal — for pruning, routing, quantization, or structural modification — must explicitly justify its aggregation choice. Using head-max instead of head-mean risks systematically underestimating concentration and misidentifying layers as "not locally-biased" when they are.

*Broader implication:* This suggests a general principle: for layer-level characterization of multi-head attention, head-mean aggregation captures the layer's typical behavior across all heads, while head-max captures the outlier head in each layer. These are different quantities with different stabilities and different information content. The field should be explicit about which is intended.

**Finding 3: Entropy ranking stability (ρ ≥ 0.8) enables deterministic layer selection.** The high Spearman correlation across calibration subsets means that the top-k layer selection is not sensitive to the specific 100 sequences used for calibration. In practice, a practitioner can run the entropy scoring once on any available calibration data and trust that the selected layers would be the same with any other representative sample. This determinism is a practical advantage over methods that require repeated runs or ensemble selections.

## 6.2 Open Questions from Pending Experiments

The most important open questions are empirical, not theoretical:

**Does the entropy criterion's structural validity translate to accuracy preservation?** h-e1 confirms that high-entropy layers have diffuse attention patterns — but whether *constraining* those layers to a local window (SWA) causes accuracy degradation depends on whether those layers' diffuse patterns are globally necessary or incidentally broad. H-e2 directly tests this by converting the 4 highest-entropy layers and measuring WikiText-103 perplexity.

**Does entropy outperform random selection?** The preliminary QA F1 probe suggests entropy selection degrades QA performance less than random selection (0.43 pp vs 0.67 pp), but this is non-significant at p = 0.4507 with N = 200 and uses a different operation (top-k retention) and metric (QA F1) than the designed h-m1 experiment. H-m1 will provide the proper comparison with SWA masking and perplexity metric.

**Where is the k* boundary?** H-m2 tests k = 8 conversion. If k = 4 preserves perplexity within 2 points and k = 8 exceeds the threshold, the boundary characterizes how many layers can be converted before accuracy degrades. This k* characterization is publishable regardless of whether k = 4 passes: even if P1 fails (k = 4 causes > 2pt degradation), the degradation curve across k characterizes the zero-shot SWA feasibility boundary for Llama-2-7B.

## 6.3 Limitations

We state the following limitations explicitly, along with their impact on paper claims.

**L1: Core accuracy-preservation claims (P1, P2, P3) are untested.** H-e2, h-m1, and h-m2 have not been executed. All accuracy-preservation claims are explicitly conditional ("if h-e2 confirms...") or marked as pending. This is the primary limitation of this interim synthesis. The paper's contribution is the entropy criterion characterization (h-e1), which is meaningful independently of h-e2 outcomes — the heavy-hitter concentration finding and the pooling method ablation are standalone empirical contributions. However, the paper's main hypothesis (H-EntropySWA-v1) is not confirmed.

*Why acceptable:* The pipeline invoked Phase 4.5/6 before h-e2 execution. The h-e1 findings provide a meaningful checkpoint contribution. Both positive (P1 passes, validating the framework) and negative (P1 fails, characterizing the feasibility boundary) outcomes for h-e2 are publishable.

**L2: Single model and domain scope.** All confirmed findings apply to Llama-2-7B evaluated on WikiText-103. Generalizability to Llama-3-8B (which uses grouped-query attention, requiring adapted entropy computation), encoder-decoder models, or other calibration domains is untested. The entropy concentration finding may be model-family specific.

*Why acceptable:* Single-model EXISTENCE PoC is the stated scope of h-e1. Cross-model generalization is identified as future work with a clear path (GQA adaptation for Llama-3+; domain sensitivity test via re-running entropy scoring with SST-2 calibration sequences).

**L3: Preliminary P2 evidence uses proxy operation and metric.** The QA F1 comparison in h-e1 uses top-k attention score retention (a different operation from SWA masking) and F1 (a different metric from perplexity). The directional trend (0.43 pp vs 0.67 pp entropy advantage) cannot be cited as evidence for P2.

*Why acceptable:* Directional consistency is reported for transparency. H-m1, with the correct operation (SWA masking) and metric (perplexity), will provide definitive evidence.

**L4: Residual stream compensation mechanism is hypothesized, not empirically confirmed.** Steps 2 and 3 of the causal chain — that SWA layers do not lose needed functionality, and that 28 remaining full-attention layers compensate via residual stream — are theoretical motivations that require h-e2/h-m2 experimental evidence. The mechanism is supported by transformer architecture theory and consistent with SWARR findings, but not directly verified.

*Why acceptable:* Mechanism motivation is theory-grounded; h-e2 will provide the empirical test (Δperplexity ≤ 2.0 is the mechanistic falsifier). Depth-position analysis in h-m2 will test the residual stream compensation hypothesis directly.

## 6.4 Broader Impact

This work targets inference efficiency for large language models without fine-tuning. Positive impacts include: reducing compute cost for LLM deployment (lower energy, lower cost, broader access), enabling practitioners to apply SWA conversion on existing models without retraining infrastructure. The method requires only 100 calibration sequences and a single GPU, making it accessible to researchers with limited compute resources.

Potential negative impacts are limited: the method modifies model inference behavior without changing training data or outputs in ways that could introduce harmful biases. However, practitioners should validate that SWA conversion does not disproportionately affect performance on minority-group or low-resource language examples before deploying in sensitive settings — a general caution for any inference-time model modification.
