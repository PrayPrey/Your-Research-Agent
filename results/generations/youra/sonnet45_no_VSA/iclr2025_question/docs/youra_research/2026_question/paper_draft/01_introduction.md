# 1. Introduction

Large language models generate fluent text that camouflages factual errors, posing risks for high-stakes applications from medical diagnosis to legal research [Huang et al., 2023]. Hallucination detection methods aim to flag unreliable outputs before they reach end users, with recent approaches leveraging Natural Language Inference (NLI) models to verify consistency between generated text and source context. Among these, the Constrained Category Probability (CCP) method [arxiv:2403.04696] proposes a principled uncertainty quantification framework based on claim-type mass ratio (ρ_j), reporting improvements of +0.05 to +0.10 ROC-AUC over baseline logit-based detectors on biography generation tasks.

We set out to extend CCP beyond its validated domain—factual text generation—to test whether the method exhibits ontology-dependent degradation when applied to creative text (metaphorical, speculative content). Our hypothesis posited that CCP's NLI-based conditioning embeds implicit factual-ontology assumptions: when verifying claims in a fictional narrative ("The dragon flew over the mountains"), the NLI model trained on factual corpora (SNLI, MNLI) would misclassify creative coherence as hallucination, causing ρ_j to degrade by >0.15 relative to factual domains.

**Instead, we could not reproduce the baseline.**

Implementing CCP on paired factual (TruthfulQA) and creative (WritingPrompts) datasets, we observed ρ_j values **50× lower than expected** across BOTH domains: median 0.0354 (factual) and 0.0103 (creative) versus expected range 0.75-0.85 inferred from CCP paper claims. Statistical tests revealed no significant separation between domains (p = 1.0000, Cohen's d = -0.0635), with effect direction inverted relative to hypothesis prediction.

Root cause analysis identified a **task-domain gap**: DeBERTa-v3-base NLI model, trained on SNLI/MNLI semantic similarity tasks (e.g., "A dog plays in a park" vs "A puppy runs outside" → ENTAILMENT), does not generalize to factual verification tasks (e.g., "Obama was born in 1980" vs biography context stating 1961 → CONTRADICTION). The model assigns ~90% probability mass to the "neutral" class for claim-context pairs, collapsing the ρ_j metric toward zero. This failure is uniform across factual AND creative domains, suggesting the issue is **task-agnostic** (SNLI/MNLI ≠ factual verification) rather than domain-specific (creative text confusing NLI).

**This is a measurement validity failure, not a hypothesis refutation.** When ρ_j is 50× lower than expected across all conditions, we cannot distinguish "hypothesis is wrong" from "measurement is broken"—analogous to testing a microscope's focus with a novel staining protocol on rare tissue samples without first validating it on common tissues.

Our contribution is threefold:

1. **Transparent documentation of replication failure**: We identify undocumented implementation details in CCP paper (NLI calibration diagnostics, claim decomposition methodology, context pairing strategies) that prevent reproducibility. Detailed failure logs enable future researchers to avoid repeating costly mistakes.

2. **Root cause hierarchy for hallucination detection**: We establish that NLI model selection/calibration is a **prerequisite** for CCP-based detection, with claim decomposition quality and context pairing as contributory factors. Literature triangulation (Himal-Badu: attention r < 0.1; Shaguns26: threshold tuning 50% → 30% for 95% recall) corroborates NLI calibration as common bottleneck.

3. **Methodological requirements for the field**: We derive concrete recommendations hallucination detection papers should adopt: (1) report raw metric distributions (not just aggregate ROC-AUC), (2) validate NLI calibration on known factual verification examples, (3) measure claim decomposition inter-annotator agreement, (4) provide reproducibility packages with baseline replication notebooks.

**Why publish a negative result?** Transparent failures improve field reproducibility standards. We provide actionable guidance (NLI fine-tuning on FEVER/HotpotQA, claim method comparison, baseline validation) that transforms a gate failure into methodological humility—recognizing measurement validity as prerequisite for hypothesis testing.

The paper is structured as follows: Section 2 surveys hallucination detection methods, NLI domain adaptation, and reproducibility challenges. Section 3 details our implementation (DeBERTa-v3-base NLI, NLTK claim decomposition, TruthfulQA/WritingPrompts datasets). Section 4 presents experimental results (gate failure, neutral-class dominance, inverted autocorrelation). Section 5 analyzes root causes via competing explanations framework. Section 6 discusses broader implications for reproducibility and future work. Section 7 concludes with lessons learned: replicate baseline on original domain BEFORE testing domain transfer.
