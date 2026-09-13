# Discussion

## Key Findings and Interpretation

Our experiments reveal that per-sample loss trajectories during ERM training encode a strong, spurious-correlation-specific signal for identifying minority group samples.

**Finding 1: Trajectory divergence is highly discriminative.** The AUROC of 0.9452 demonstrates that loss trajectory features are not merely correlated with minority status—they are strongly predictive. This suggests that the process of learning spurious correlations leaves a distinctive signature that can be extracted without group labels during training.

**Finding 2: The signal is magnitude-based, detectable from epoch 1.** Contrary to our initial hypothesis about temporal dynamics (curvature timing), the discriminative signal comes primarily from initial loss (L₁). This finding has important practical implications: spurious correlation vulnerability can be assessed from a single training epoch, enabling efficient screening without extended training runs.

**Finding 3: The signal is spurious-specific, not generic difficulty.** The controlled comparison between GroupDRO and variance-matched random reweighting provides strong evidence that trajectory divergence reflects spurious feature conflict specifically. If the signal merely captured "hard samples," both interventions should affect it similarly. The 29× difference in attenuation (GroupDRO: 29%, Random: 1%) demonstrates specificity to spurious correlation dynamics.

**Theoretical interpretation.** Under ERM training with pretrained models, spurious correlations are encoded in early network layers. When minority samples (with conflicting spurious features) enter training, they immediately experience higher loss because the pretrained shortcut provides incorrect signal. This conflict manifests as distinctive L₁ values from epoch 1. GroupDRO reduces spurious reliance, thereby reducing the L₁ gap between groups; random reweighting only smooths gradients without affecting the underlying spurious encoding.

## Limitations

We acknowledge several limitations that scope our claims:

**L1: Single dataset.** Our evaluation focuses on Waterbirds, a standard benchmark but nonetheless a single dataset. While this demonstrates feasibility, generalization to other spurious correlation settings (CelebA, ColoredMNIST, real-world datasets) requires additional validation.
- *Why acceptable:* Waterbirds is the standard benchmark used across 100+ spurious correlation papers, enabling direct comparison with prior work.
- *Future mitigation:* Cross-dataset validation is a clear next step.

**L2: Pretrained models only.** We use ImageNet-pretrained ResNet-50. The finding that L₁ dominates may depend on pretrained features already encoding spurious patterns. Models trained from scratch may exhibit different dynamics.
- *Why acceptable:* Pretrained models are the dominant paradigm in practice; this is the setting most practitioners encounter.
- *Future mitigation:* Test with randomly initialized models to understand how pretraining affects trajectory signatures.

**L3: Detection, not intervention.** We demonstrate that trajectory features can *identify* spurious correlation-affected samples, but this does not guarantee successful *intervention*. Prior work has shown that detection and correction are distinct challenges.
- *Why acceptable:* Diagnosis is valuable even without guaranteed treatment—knowing which samples are affected enables targeted investigation and informed decisions about deployment.
- *Future mitigation:* Explore trajectory-guided sample selection for GroupDRO or curriculum learning.

**L4: Curvature mechanism refuted.** Our secondary hypothesis about delayed curvature stabilization was not supported. While this refines rather than invalidates our main contribution, it indicates that the temporal dynamics we initially hypothesized were incorrect.
- *Why acceptable:* The core insight (trajectory divergence exists and is spurious-specific) remains validated; we honestly report the mechanism refinement.
- *Future mitigation:* Investigate alternative temporal signatures beyond curvature.

**L5: Observational design.** Our specificity test uses GroupDRO as an intervention, but we cannot make strong causal claims—we observe correlation between reduced spurious reliance and reduced trajectory divergence.
- *Why acceptable:* The controlled comparison with variance-matched random reweighting provides stronger evidence than pure observation.
- *Future mitigation:* Causal intervention experiments with synthetic spurious correlations of known strength.

## Broader Impact

**Positive impacts.** This work provides tools for practitioners to identify spurious correlation vulnerability during training, before deployment. Early detection can prevent deployment of models with hidden failure modes, potentially avoiding harmful outcomes in high-stakes applications (medical diagnosis, autonomous systems, fairness-critical decisions). The single-epoch detection capability reduces computational cost for vulnerability assessment.

**Potential concerns.** We do not identify direct negative applications of this diagnostic technique. However, as with any detection method, there is risk that practitioners may use it as a "checkbox" without deeper investigation—detecting vulnerability does not automatically resolve it. We emphasize that detection should prompt careful analysis, not false confidence.

**Recommendations.** We encourage practitioners to use trajectory analysis as one component of a broader robustness evaluation pipeline, not as a sole determinant of deployment readiness.

## Future Directions

**Immediate extensions:**
- Cross-dataset validation on CelebA, ColoredMNIST, and NICO++
- Single-epoch (L₁-only) efficient detection protocol
- Trajectory-guided sample selection for GroupDRO

**Longer-term vision:**
- Training-integrated early warning systems that automatically flag spurious correlation vulnerability
- Extension to non-vision domains (NLP, tabular data)
- Connection to intervention—can trajectory information guide successful debiasing?

**Open questions:**
- Does the L₁ signal transfer across datasets without retraining the detector?
- What is the minimum compute budget needed for reliable detection?
- Can trajectory features identify novel spurious correlations not seen during training?
