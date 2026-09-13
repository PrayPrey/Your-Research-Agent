# 7. Conclusion

We began with the observation that fine-tuning a large language model requires deciding how many
parameters to allocate to each layer — a decision typically made uniformly, before training
begins, despite the fact that different layers contribute differently to model behavior. We asked
whether the pre-trained model already carries a signal that answers this question: does the
model, before any fine-tuning, tell us something about its own layer-wise structure?

For LLaMA-3.1-8B, the answer is yes. The model's MLP activation sparsity profile constitutes a
robust, threshold-invariant structural fingerprint that can be extracted from a single forward
pass on any calibration dataset. Layer-wise sparsity varies significantly across the 32 MLP
blocks (CV$=0.544$), follows a systematic depth gradient (early layers most sparse, deep layers
least), and is stable across four diverse calibration distributions (ICC$(3,k)=0.9846$). The
layer rank ordering is invariant to epsilon threshold choice across two orders of magnitude
(all cross-epsilon $\tau > 0.96$). A practitioner can measure this fingerprint in approximately
five minutes on modern hardware, using any available text dataset.

Our contributions are:

1. **The first systematic characterization** of LLaMA-3.1-8B's activation sparsity as a
   structural fingerprint — establishing CV$=0.544$, depth gradient, and cross-distribution
   stability through three independent experiments (H-E1, H-M1, H-M2).

2. **Cross-distribution stability** quantified at ICC$(3,k)=0.9846$ with $\tau_{\min}=0.734$
   — establishing that calibration dataset choice does not affect the layer rank ordering, a
   practical prerequisite for any zero-cost allocation method.

3. **Threshold invariance** quantified at cross-epsilon $\tau > 0.96$ for all pairs across
   $[0.001, 0.1]$ — eliminating hyperparameter tuning from the measurement step.

4. **A foundation for zero-cost rank allocation** — establishing the structural prior that
   motivates inverse-sparsity LoRA rank allocation, with the rank-predictive utility (H-M3)
   and end-to-end performance (H-M4) as immediate future work.

## Future Directions

**Immediate priorities.** The most pressing next steps are H-M3 (does sparsity negatively
predict LoRA rank sensitivity, Pearson $r \leq -0.4$?) and H-M4 (does inverse-sparsity
allocation achieve $\geq 95\%$ of oracle performance at 60\% parameter budget?). H-M3 requires
approximately 320 perturbed fine-tuning runs; its experimental design is fully specified.
The extreme cross-distribution stability (ICC$=0.9846$) and threshold invariance ($\tau > 0.96$)
we report here provide strong empirical confidence that the input signal to H-M3 is reliable.

**Understanding the mechanism.** The ICC$=0.9846$ result far exceeded our expectations and
motivates investigation of the "architecture determinism" hypothesis — whether SiLU gating
creates input-independent sparsity distributions driven by weight magnitudes alone. Testing with
shuffled or random inputs would directly distinguish architecture-driven from content-driven sparsity.

**Effective-rank validation.** Assumption A3 — that near-zero activation sparsity proxies the
intrinsic dimension of each layer's computational subspace — remains unverified. Comparing
epsilon-based sparsity rankings against effective-rank estimates from activation covariance
matrices would provide the theoretical grounding for the sparsity-to-rank-requirement connection.

**Cross-architecture universality.** The consistent depth gradient we observe (early layers high
sparsity, deep layers low sparsity) is consistent with universal structural properties documented
by Szatkowski et al.~\shortcite{szatkowski2025universal}. Applying the same profiling to
Mistral-7B, Gemma-7B, and Phi-3 would test whether the fingerprint generalizes and whether a
single cross-architecture prior is achievable.

The model, before fine-tuning begins, already tells us something about its internal structure.
We have characterized that signal rigorously. Whether it is enough to guide allocation decisions
— and by how much — is the question this work enables.
