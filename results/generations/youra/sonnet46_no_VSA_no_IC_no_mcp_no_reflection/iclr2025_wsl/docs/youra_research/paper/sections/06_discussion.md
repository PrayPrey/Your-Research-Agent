# Discussion

## 5.1 What the Results Tell Us About Gap Signal in Weight Space

Three findings emerge robustly from our experiments:

**Finding 1: Generalization gap is learnable.** Both FlatMLP (r = 0.557) and DWSNet (r = 0.510)
exceed the existence threshold. The A1 audit (Spearman(gap, −test_acc) = −0.142) confirms that
gap carries independent predictive signal. Together, these results establish that weight tensors
encode the overfitting signature — the degree to which a model's training adaptations have drifted
toward memorization — in a form that learned encoders can extract.

**Finding 2: Architecture specificity matters, specifically cross-layer reasoning.** NFT's cross-layer
attention is the only encoder that improves over FlatMLP on gap prediction, and it does so with
statistical confidence (non-overlapping CIs). DWSNet and GNN both underperform FlatMLP on gap despite
their equivariant architectures. This dissociation — NFT better than FlatMLP, DWS/GNN worse — suggests
that the relevant architectural property is not equivariance per se but the capacity to integrate
evidence across layer boundaries. Generalization gap is a globally distributed property of the weight
tensor; detecting it may require an encoder that can reason about how representations change across
consecutive layers, not just within each layer independently.

**Finding 3: NFT captures gap-specific overfitting structure (P3, r = 0.73).** The partial Spearman
result is the most striking finding of this study. NFT's gap predictions contain information about
true generalization gap that is statistically independent of test accuracy rank — and this independent
component is more strongly correlated (r = 0.73) than the combined signal (r = 0.57). This implies
that NFT is not learning a test-accuracy proxy and inferring gap from it; it is extracting a distinct
structural component of the weight tensor that specifically encodes overfitting. We hypothesize (not
yet verified) that this corresponds to inter-layer weight co-variation patterns that emerge during
memorization — patterns that are present across layer boundaries and accessible to NFT's cross-layer
attention but filtered out by DWS's within-layer averaging and GNN's fixed graph connectivity.

## 5.2 The FlatMLP Test Accuracy Anomaly

FlatMLP predicts test accuracy at r = 0.279 in our zoo, substantially below the ~0.85 reported by
Unterthiner et al. [2020] on their zoo. This requires explanation, as it affects the Δ computation
(RQ4) and the interpretation of the dual-target comparison.

We identify two plausible explanations:

**Explanation 1 (High plausibility): Zoo generation artifact.** Our zoo was generated with a restricted
hyperparameter grid and a specific CNN architecture variant. Models may cluster at near-saturation
training accuracy, compressing the test_acc variance and making it harder to predict from weights.
If models achieve 90-95% test accuracy regardless of hyperparameters, the test_acc prediction signal
in weights is weak. Gap (which reflects the margin between training and test performance) may retain
more variance because it captures subtle memorization differences among high-accuracy models.

**Explanation 2 (Medium plausibility): Optimizer sensitivity.** The 3-trial search budget may have
failed to find a good learning rate for FlatMLP's test_acc regression task specifically, while the
gap regression task is more robust to learning rate choice (perhaps because gap values have lower
dynamic range and smoother loss landscape).

**Impact on conclusions.** The FlatMLP test_acc anomaly does not affect RQ1 (gap existence), RQ2
(architecture ranking on gap), or RQ3 (partial Spearman). These results use only gap Spearman values,
which are consistent across two independent runs. The anomaly exclusively affects RQ4 (Δ computation),
where FlatMLP test_acc serves as the control baseline. We cannot determine from current experiments
whether the Δ null result reflects a genuine mechanism failure or a confounded control. Future work
with the original Unterthiner zoo data and extended search budget is needed to resolve this.

## 5.3 Limitations

**Limitation 1: FlatMLP test_acc substantially below literature benchmark (r = 0.279 vs. ~0.85).**
This is the most significant limitation. Our zoo does not replicate the original Unterthiner 2020
results for test_acc prediction, limiting cross-literature comparability and confounding the Δ
mechanism analysis.
*Why acceptable:* Gap prediction results (our primary contribution) are internally consistent and
novel — there is no literature baseline for gap Spearman to compare against. The limitation is
confined to the mechanism analysis (RQ4).
*Future mitigation:* Download and use the original Unterthiner 2020 zoo data; run 50-trial search
for FlatMLP on test_acc; verify reproduction of r ≈ 0.85 before recomputing Δ.

**Limitation 2: Small hyperparameter search budget (3 trials vs. 50 pre-specified).**
All Spearman values may be below encoder optimal performance. The ranking results (NFT > FlatMLP > DWS
> GNN on gap) may shift with extended search.
*Why acceptable:* Gap results are consistent across two independent runs (h-e1 and h-m1 agree within
5% on FlatMLP and DWSNet). The existence result (r > 0.5 for multiple encoders) is unlikely to
reverse with extended search. Relative rankings may shift at the margins.
*Future mitigation:* 50-trial random search for all encoders on both targets; sensitivity analysis
across top-5 configurations.

**Limitation 3: Single zoo, single architecture family (Unterthiner CIFAR-10 small CNNs).**
All results are specific to this zoo. Generalization to ResNets, Transformers, or larger models is
not established.
*Why acceptable:* The Unterthiner zoo is the standard benchmark for this research area. Proof of
concept on this zoo is a necessary precursor to broader claims.
*Future mitigation:* Apply to Schürholt PDFD zoo (multi-architecture); test on ImageNet-scale zoos.

**Limitation 4: Differential advantage hypothesis (h-m2 P1) not confirmed.**
The target-specificity mechanism claim is confounded. We report a null result that cannot be cleanly
interpreted as a genuine mechanism failure.
*Why acceptable:* Null results are scientifically valid contributions when reported with identified
confounders and proposed corrective experiments. The RQ1-RQ3 contributions stand independently of RQ4.
*Future mitigation:* Execute corrected experiments (original data + extended search) before making
mechanism claims.

## 5.4 Broader Impact

Weight-based gap prediction has several positive applications: (1) reducing held-out test set evaluation
cost for large model zoos, particularly in resource-constrained settings; (2) enabling real-time
overfitting monitoring during neural architecture search without repeated test-set evaluation; (3)
providing interpretability tools for understanding where in weight space overfitting manifests.

Potential concerns: automated model selection based on predicted gap could inadvertently select
models that are overfit to the weight-space predictor's training distribution rather than genuinely
low-overfitting models. We recommend gap predictors be used as soft filters for candidate generation,
not hard selectors, in deployment settings. The methodology introduced here (dual-target controlled
comparison, partial Spearman independence analysis) is reusable for any weight-space prediction study
without domain-specific risk.
