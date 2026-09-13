# Introduction

RLHF-trained language models achieve high aggregate benchmark accuracy yet exhibit systematic calibration inversion—confidently predicting wrong answers—on specific task clusters. This paper traces this failure pattern to reward signal conflation during training, revealing a mechanism where annotator behavior propagates through reward models into model representations.

## The Calibration Paradox

Standard evaluation reports aggregate accuracy, masking task-level failure patterns. When we cluster benchmark tasks by calibration scores—measuring the gap between model confidence and correctness—we find non-random structure. Tasks where models show P(wrong) > P(correct) + 0.1 cluster with silhouette score 0.6016, far exceeding the 0.3 threshold indicating meaningful clustering. This systematic pattern suggests underlying causes beyond random error.

## The Problem: From Symptoms to Mechanisms

Surface-level observations note that RLHF models show overconfidence on certain tasks. The deeper problem is that existing evaluation provides no mechanism explanation—we know *what* fails but not *why*. The gap in current work is the absence of methods connecting calibration patterns to training dynamics.

We hypothesize that RLHF's reward modeling conflates distinct task dimensions. Specifically, annotators rate both "correct output" and "output requiring user-state modeling" with similar high confidence, creating a training signal that fails to distinguish task types. Models then optimize for this conflated signal, developing miscalibrated confidence on tasks requiring nuanced adaptation.

## Key Insight: The Conflation Chain

Our investigation reveals a four-step mechanism:

1. **Annotator Conflation:** Human annotators rate correctness and user-modeling tasks identically (rate_diff = 0.001), providing no distinguishing signal during preference data collection.

2. **Reward Model Inheritance:** The reward model learns this conflated signal, showing similar confidence across task types (overlap = 0.647 across three models).

3. **Representation Conflation:** Model hidden states fail to separate task types internally (separation = 0.024), indicating the conflation propagates to learned representations.

4. **Calibration Consequences:** These models exhibit systematic calibration inversion on specific task clusters.

We verify steps 1-3 empirically. Step 4's connection to bidirectional task features remains unverified with current keyword-based detection methods (2.3% feature prevalence), motivating semantic detection as future work.

## Contributions

This work makes three contributions:

- **Calibration clustering as diagnostic tool:** We demonstrate that clustering benchmark tasks by calibration inversion scores reveals systematic RLHF behavioral patterns (silhouette = 0.6016).

- **Empirical mechanism verification:** We provide first quantitative evidence that annotator conflation (rate_diff = 0.001), reward conflation (overlap = 0.647), and representation conflation (separation = 0.024) form a coherent mechanism chain.

- **Honest negative result:** We report that keyword-based bidirectional feature detection is insufficient (2.3% prevalence, r = -0.027), establishing methodological boundaries for future work.

The paper proceeds as follows. Section 2 reviews related work on RLHF evaluation and calibration. Section 3 presents our methodology for calibration clustering and mechanism verification. Section 4 describes experimental setup. Section 5 reports results including 4/5 hypothesis validations. Section 6 discusses implications and limitations. Section 7 concludes with future directions.
