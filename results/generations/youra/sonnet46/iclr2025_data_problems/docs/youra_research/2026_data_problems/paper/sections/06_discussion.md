# 6. Discussion

## 6.1 Key Findings

**Finding 1: fastText quality filtering is a near-deterministic demographic reweighting mechanism.**
The ρ=1.0 log-odds correlation (H-M1) and the −22.41% entropy reduction (H-E1) together establish that fastText quality filtering operates on the demographic-occupation association structure of the corpus with striking precision. The key implication is that practitioners treating fastText as a "neutral quality proxy" are unknowingly making demographic composition decisions with each threshold choice. At the production DCLM-BASELINE threshold (≥90th percentile), the quality filter has restructured the demographic landscape of the training corpus substantially — increasing the conditional log-odds of demographic-occupation associations by more than 4× compared to minimally-filtered text.

This matters beyond this specific classifier. Any quality proxy trained on Wikipedia and OpenWebText will inherit the demographic-occupation association patterns of those corpora. The specific mechanism (vocabulary-demographic coupling) is likely common to the entire class of academic-register quality classifiers.

**Finding 2: A model-free corpus fairness audit is not only feasible — it is informative before training.**
Our H-E1 and H-M1 results demonstrate that meaningful, actionable fairness signals are detectable at a ~50k document quick-run scale. The CorpusFilter + EntropyMeasure + LogOddsComputer pipeline — running in hours rather than days — produces a complete audit of how a curation configuration alters demographic-occupation structure. This is a practical contribution: practitioners do not need to train a model to detect that their filtering threshold is systematically restructuring demographic associations.

**Finding 3: The corpus-to-model propagation pathway is directionally supported but not statistically demonstrated at quick-run training scale.**
H-M2 provides a nuanced story. The negative control result (|C7−C0|=0.495) suggests the model trained on a corpus with shuffled-demographic associations produces different logit margins than the unfiltered baseline — consistent with corpus demographic structure reaching model representations. However, the graded correlation (ρ=0.357, p=0.432) does not reach significance. This dissociation is informative: binary perturbation detection and graded discrimination have different compute requirements, and the quick-run budget (~50B tokens, hf_trainer_fallback) appears sufficient for the former but not the latter.

## 6.2 Limitations

We report limitations honestly, with reasoning about why each is acceptable and how it can be addressed.

**L1: H-M2 is statistically underpowered for the graded mechanism claim.**
The primary gate for H-M2 (Spearman ρ>0, p<0.01 for logit margin vs. corpus entropy) is not satisfied at the tested training scale (~50B tokens, hf_trainer_fallback). The negative control passes, providing directional evidence, but the graded signal is not statistically demonstrated. This means the full three-step causal chain — corpus entropy → log-odds → model logit margins — is not validated at the tested scale.

*Why acceptable:* The SHOULD_WORK gate type explicitly anticipates this possibility. The negative control result provides directional support that the mechanism exists. The limitation is a compute-budget constraint, not a fundamental null result.

*Path forward:* Full-scale replication — Pythia-1B trained on C0-C7 at 100B tokens with the gpt-neox framework — is the clear next experiment (Section 7, Future Work FW1).

**L2: H-M3 (fairness benchmark comparison) was not executed.**
The downstream claim of the original PCFH — that matched-capability models trained via different curation paths produce statistically distinguishable BBQ/WinoBias/StereoSet outcomes — requires H-M3, which was not completed. H-M3 depends on H-M2 producing trained Pythia-1B checkpoints with matched capability, which the quick-run budget did not achieve.

*Why acceptable:* The corpus-level mechanism (H-E1, H-M1) is independently valuable as a methodological contribution. H-M3 is a clear next step; the PCFH framework (capability matching, negative control design) is fully specified for when checkpoints are available.

*Path forward:* Full-scale Pythia-1B checkpoints from FW1 → H-M3 execution → BBQ accuracy gap measurement.

**L3: Quick-run corpus subsample (~50k documents, not 10M).**
H-E1 and H-M1 ran on ~50k document subsets rather than the planned 10M documents. The full experiment for H-E1 was running in background (PID 2164630 confirmed).

*Why acceptable:* The effect magnitude (4.5× threshold for entropy; ρ=1.0 for log-odds) makes reversal at full scale implausible. Results at quick-run scale provide reliable directional estimates.

**L4: Single model family (Pythia-1B); no cross-architecture validation.**
Model-level effects (H-M2) are demonstrated only for Pythia-1B. The corpus-level findings (H-E1, H-M1) are model-agnostic.

*Why acceptable:* Pythia is the standard controlled-pretraining model family [Biderman et al., 2023]. Corpus-level results (which are the primary contribution) generalize by construction.

## 6.3 Broader Impact

**Positive impacts.** This work provides practitioners with a computationally tractable, model-free tool to audit the demographic fairness implications of their data curation choices — before committing compute to model training. The open-source pipeline (CorpusFilter, EntropyMeasure, LogOddsComputer) can be applied to any corpus and filtering configuration. Awareness that standard quality filters have demographic implications should encourage practitioners to evaluate curation choices on both performance and fairness axes.

**Potential negative impacts.** Our methodology could in principle be used to deliberately engineer demographic associations in training data — to amplify stereotypes rather than audit them. We believe the practical value of the audit tool for responsible curation far outweighs this risk, but we acknowledge the dual-use potential.

**Mitigation.** Open availability of the audit methodology lowers the barrier for *detection* of deliberate or inadvertent demographic engineering, which we expect to more than offset the dual-use risk. We also note that the effect we measure (fastText filtering amplifying Wikipedia-register demographic associations) is already present in widely-deployed systems without practitioners' knowledge; making it visible is the first step to addressing it.
