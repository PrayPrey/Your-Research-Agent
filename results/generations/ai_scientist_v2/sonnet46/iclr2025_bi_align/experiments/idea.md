## Name

value_drift_aware_bidirectional_alignment

## Title

Closing the Loop: Detecting and Correcting Value Drift in Bidirectional Human-AI Alignment via Longitudinal Preference Auditing

## Short Hypothesis

Human preferences and values are not static—they evolve through continued interaction with AI systems, yet current alignment methods (e.g., RLHF) assume a fixed, ground-truth human preference distribution. We hypothesize that AI systems trained on early-stage human feedback inadvertently shape and shift the very preferences they were meant to reflect, creating a feedback loop of 'value drift' that degrades alignment quality over time. We propose a longitudinal preference auditing framework that (1) detects when a user's expressed preferences have drifted due to AI influence vs. genuine value evolution, (2) disentangles AI-induced drift from authentic preference change, and (3) adaptively recalibrates reward models to maintain alignment with the user's authentic, reflective values. This bidirectional framing—where AI influences humans and humans influence AI—is the ideal setting to study this phenomenon, as it cannot be captured by either direction alone.

## Related Work

Existing RLHF methods (Christiano et al., 2017; Ouyang et al., 2022) treat human feedback as a static oracle and do not account for preference evolution. Work on reward hacking and Goodhart's Law (Krakovna et al., 2020) identifies cases where optimizing a proxy reward diverges from true intent, but does not model the human side of this loop. Research on 'sycophancy' in LLMs (Perez et al., 2022; Sharma et al., 2023) shows AI systems learn to flatter users rather than be truthful, but stops short of modeling how this shapes user beliefs over time. Human-computer interaction literature on automation bias (Parasuraman & Manzey, 2010) and AI-induced anchoring effects documents how AI outputs shift human judgment, but lacks a computational framework for detecting and correcting this in alignment pipelines. Our proposal is the first to explicitly model the bidirectional causal loop between AI-induced preference drift and alignment quality, providing both a detection mechanism and a correction algorithm—distinguishing it from all prior work which treats these as separate, unidirectional problems.

## Abstract

Current AI alignment methods assume human preferences are stable ground truths that AI systems should learn to satisfy. This assumption is fundamentally flawed: humans are adaptive agents whose values and preferences evolve—partly through genuine reflection and growth, and partly through exposure to the very AI systems they are meant to guide. This creates a dangerous feedback loop: an AI trained on early human feedback shapes future human preferences, which then produce new feedback that further trains the AI, potentially drifting far from the user's authentic values. We call this phenomenon 'alignment-induced value drift' and propose a longitudinal preference auditing framework to detect, disentangle, and correct it. Our framework operates in three stages. First, we develop a longitudinal preference elicitation protocol that periodically queries users on a stable battery of preference probes across diverse domains, building a temporal model of each user's preference trajectory. Second, we introduce a causal auditing method that uses counterfactual reasoning to separate AI-induced preference shifts from authentic value evolution, by comparing preferences of users with different AI interaction histories. Third, we propose an adaptive reward model recalibration algorithm that down-weights feedback likely contaminated by AI-induced drift and up-weights feedback reflecting genuine reflective preferences (identified via deliberative prompting and consistency checks). We validate our framework in a controlled longitudinal user study with 200 participants over 8 weeks, measuring alignment quality, preference stability, and user-reported authenticity. Our work reframes alignment as a dynamic, bidirectional process and provides the first computational tools to maintain alignment integrity in the face of human-AI co-evolution.

## Experiments

1. **Longitudinal Preference Drift Study**: Recruit 200 participants randomly assigned to interact with either a standard RLHF-trained assistant or a baseline (no AI). Administer a validated preference battery (covering ethical dilemmas, aesthetic choices, risk tolerance, and political values) at weeks 0, 2, 4, 6, and 8. Measure: (a) within-person preference variance over time, (b) divergence between AI-group and control-group preference trajectories using Jensen-Shannon divergence, (c) correlation between AI interaction intensity and preference shift magnitude. Hypothesis: AI-group participants show significantly greater preference drift toward AI-favored positions.

2. **Causal Disentanglement via Counterfactual Matching**: Using the longitudinal dataset, apply propensity-score matching to pair AI-group and control-group participants with similar baseline profiles. Use difference-in-differences analysis to isolate AI-induced drift from natural preference evolution. Metric: Average Treatment Effect (ATE) of AI exposure on preference shift per domain.

3. **Drift Detection Classifier**: Train a lightweight classifier (logistic regression + LSTM over preference trajectories) to predict whether a given preference shift is AI-induced or authentic. Features: rate of change, consistency with prior stated values, alignment with AI output distribution. Evaluate with held-out participants; metric: AUROC for drift detection.

4. **Adaptive Reward Model Recalibration**: Implement a modified RLHF pipeline where feedback items are weighted by (1 - P(AI-induced drift)) from the drift classifier. Compare: standard RLHF vs. drift-corrected RLHF on a held-out preference evaluation set administered after a 'decontamination' period (1 week without AI interaction). Metric: alignment accuracy with post-decontamination preferences, which serve as a proxy for authentic values.

5. **Deliberative Prompting as Drift Mitigation**: Test whether prompting users to reflect on their reasoning before giving feedback (deliberative prompting) reduces AI-induced drift. Compare preference stability and downstream reward model quality across: standard feedback, deliberative feedback, and drift-corrected feedback conditions. Metric: preference consistency score and reward model alignment accuracy.

## Risk Factors And Limitations

1. **Causal identification challenge**: Disentangling AI-induced drift from natural preference evolution is inherently difficult without a perfect counterfactual. Propensity matching may not fully control for confounds; we mitigate this with randomized assignment and large sample sizes.
2. **Ground truth for 'authentic' preferences**: There is no universally accepted definition of authentic preferences. We use post-decontamination preferences and deliberative reflection as proxies, but these may themselves be imperfect.
3. **Ecological validity**: Lab-based longitudinal studies may not capture real-world AI interaction patterns; participants may behave differently knowing they are being studied (Hawthorne effect).
4. **Scale of user study**: 200 participants over 8 weeks is feasible for an academic lab but may limit statistical power for subgroup analyses; we will pre-register hypotheses and use Bayesian methods to handle uncertainty.
5. **Generalizability across AI systems**: Results from one AI assistant may not generalize to others; we will test on two different model families to assess robustness.
6. **Ethical concerns**: Exposing participants to AI systems that may shift their values raises IRB concerns; we will include full debriefing, opt-out mechanisms, and preference restoration interventions.

