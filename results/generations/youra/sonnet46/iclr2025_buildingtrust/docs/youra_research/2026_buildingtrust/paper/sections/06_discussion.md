# 6. Discussion

### 6.1 Key Findings and Their Implications

Our experiments reveal three findings that together reframe how alignment-induced miscalibration should be understood and addressed.

**Finding 1: Alignment-induced miscalibration is predominantly H2 (boundary restructuring), not H1 (scale inflation).** All 9 Spearman ρ values fall below the H1 threshold of 0.90; 8/9 fall below 0.85. This means that post-hoc correction methods designed for H1 — specifically, temperature scaling and ATS variants [Xie et al., 2024] — may be addressing the wrong mechanism. Temperature scaling rescales confidence magnitude on a fixed answer distribution. H2 restructuring changes the distribution itself: under 1.4B-PPO, 99.7% of MMLU items have a different top-ranked option after alignment. Rescaling the confidence of the *new* preferred options will not correct miscalibration caused by learning to prefer *wrong* options in the first place.

This suggests a new research direction: post-hoc calibration methods for H2-type miscalibration may need to target the hidden-state representations that encode the boundary redistribution — for example, learning to recover base-model answer rankings rather than just adjusting confidence magnitudes. ATS may partially succeed in this direction because hidden-state temperatures can be learned to undo token-level redistribution patterns, but this remains untested (H-M4, not executed).

**Finding 2: DPO produces larger calibration degradation than PPO.** This counter-intuitive result — DPO ΔReliability > PPO ΔReliability in all 3 Pythia sizes — is most likely explained by the difference in how each method shapes logit distributions. DPO's token-level direct preference reshaping directly adjusts per-option log-probability ratios without an explicit KL penalty constraining how far from the SFT reference the model can move. PPO's sequence-level reward optimization is constrained by a KL penalty to the SFT reference policy, which may moderate boundary shifts as a side effect. If this explanation is correct, it predicts that increasing PPO's KL coefficient should reduce calibration degradation — a testable hypothesis for future work.

This finding has practical implications: deploying DPO-aligned models without calibration monitoring may introduce larger miscalibration than equivalent PPO models, counter to intuitions based on reward optimization pressure.

**Finding 3: H3 (framing susceptibility) is definitively excluded in softmax ECE.** ΔECE_TruthfulQA / ΔECE_MMLU < 1.0 for all alignment types, meaning adversarially framed distractors do not amplify miscalibration. This cleanly distinguishes our result from Chhikara et al. [2025]'s verbal-confidence framing effects: the measurement modality determines whether H3 is observed. For softmax-based evaluation frameworks (lm-eval, standard benchmarking), calibration degradation under alignment is domain-general.

### 6.2 Why ATS May Work — A New Interpretation

Xie et al. [2024] observe that ATS reduces LLaMA-2-Chat ECE by 58–82% without retraining. Our H2 finding provides a new mechanistic interpretation: if alignment shifts decision boundaries in hidden-state space, then input-conditioned hidden-state temperature scaling can learn to identify and partially undo these boundary shifts at test time. ATS doesn't just rescale overall confidence — it learns per-input temperature adjustments that may be tracking which inputs have undergone H2-type redistribution. This interpretation predicts that ATS effectiveness should correlate with the degree of H2 boundary shift (lower Spearman ρ → greater expected ATS improvement) — a testable prediction for H-M4.

### 6.3 The Scale Threshold Question

The 6.9B-DPO model's ρ = 0.875 — just below the H1 threshold of 0.90 — raises the possibility of a mechanism transition as scale increases beyond 6.9B. If larger models (≥ 13B) exhibit ρ ≥ 0.90 under DPO alignment, the dominant mechanism would shift from H2 to H1, and standard temperature scaling would become effective. This is consistent with the intuition that larger models have stronger factual representations that resist H2-type redistribution under DPO's relatively soft preference reshaping.

Testing this prediction requires applying the Spearman ρ diagnostic to LLaMA-2-13B-Chat or Mistral-7B-Instruct — model families with more representative scale for practical deployment. Our framework is directly applicable via lm-eval without modification.

### 6.4 Limitations

**Limitation 1: Public fallback checkpoints (Risk R1).** The primary RLHFlow Pythia alignment checkpoints [Li et al., 2024] required authenticated HuggingFace access. We used publicly available fallback checkpoints (lomahony/Leogrin/usvsnsp) trained on HH data with Pythia base. These share the same pretraining checkpoint and approximate training regime. The H2 mechanism finding — 8/9 Spearman ρ values below 0.85 with zero values above 0.90 — would require implausibly consistent overtrained DPO versus undertrained PPO fallbacks to overturn. The DPO ≥ PPO ordering, however, is more sensitive to checkpoint training equivalence and should be interpreted as a checkpoint-level observation pending replication with matched checkpoints.

**Limitation 2: Single model family.** All results are restricted to Pythia 1.4B–6.9B. Pythia provides the cleanest controlled experiment (identical pretraining across all alignment variants), but is a research model family not widely deployed. Whether H2 dominates in LLaMA-2, Mistral, or Falcon is an open empirical question. The 6.9B-DPO near-threshold result (ρ = 0.875) suggests that cross-family replication may find H1/H2 mixed results even at the same scale.

**Limitation 3: Scale range 1.4B–6.9B.** No publicly available Pythia variants exceed 12B. The potential H1/H2 mechanism transition suggested by 6.9B-DPO is unresolvable within the Pythia family.

**Limitation 4: H-M4 not executed.** Testing whether ATS corrects H2-type boundary shifts (versus H1-type scale inflation it was designed for) was the final planned experiment. Pipeline execution stopped at 4/5 sub-hypotheses; H-M4 remains untested. The claim about ATS correctability is therefore removed from the core statement and framed as motivated future work.

### 6.5 Broader Impact

This work has implications for how deployed AI systems are evaluated and monitored. If RLHF-aligned models are miscalibrated via H2 boundary restructuring rather than H1 confidence inflation, then standard reliability calibration checks — which probe whether a model's confidence on its predicted class is accurate — may miss the actual problem: that the model's predicted class has changed in systematic and potentially harmful ways. Alignment-induced answer restructuring may be more concerning than overconfidence on stable predictions, as it implies the model has learned to prefer different answers across a wide range of inputs.

We do not anticipate direct misuse of our mechanistic framework. Understanding how alignment shapes logit distributions may inform attacks on aligned models, but the findings are more directly useful for improving calibration assessment and correction in deployed systems.
