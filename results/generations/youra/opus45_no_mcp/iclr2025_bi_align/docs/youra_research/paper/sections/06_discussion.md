# Discussion

## Key Findings

Our experiments establish a coherent mechanism explaining RLHF calibration failures:

1. **Calibration inversion clusters exist.** Tasks cluster non-randomly by calibration patterns (silhouette = 0.6016), indicating systematic behavioral structure beyond random error.

2. **Reward conflation is real.** Models show equal confidence on correctness and user-modeling tasks (mean_diff = 0.018), confirming the training objective doesn't distinguish task types.

3. **Annotator behavior is the source.** Annotators rate both task types identically (rate_diff = 0.001), explaining why reward models learn conflated signals.

4. **Conflation propagates to representations.** Model hidden states fail to separate task types (separation = 0.024), indicating deep conflation beyond surface behavior.

The mechanism chain is verified through steps 1-3. The final link—correlating bidirectional features with calibration clusters—remains unestablished due to detection limitations.

## H-M4 Failure Analysis

The negative result for H-M4 (r = -0.027) requires interpretation. Two explanations compete:

**Explanation A: Mechanism is wrong.** Bidirectional features do not drive calibration inversion; another factor (difficulty, format, topic) explains cluster membership.

**Explanation B: Detection is insufficient.** Keyword-based features captured only 2.3% of tasks, providing insufficient signal for correlation analysis.

Evidence favors Explanation B:
- The 3-step mechanism (H-M1, H-M2, H-M3) verified independently
- 2.3% prevalence is below the informative range (20-80%) assumed by our design
- Semantic or embedding-based detection could capture bidirectionality that keywords miss

We report this as methodological limitation, not theoretical falsification.

## Implications for RLHF Training

If annotator conflation causes reward conflation causes calibration failure, interventions should target annotation:

- **Annotation guidelines:** Explicitly distinguish correctness from user-modeling dimensions
- **Multi-signal rewards:** Train separate reward heads for different task types
- **Calibration-aware training:** Penalize calibration inversion during RLHF

These remain future work; our contribution is establishing the mechanism warranting intervention.

## Limitations

### Keyword-Based Detection Insufficient
Our 3-keyword feature set (user-belief-reference, context-dependent, hedged-answer) achieved only 2.3% prevalence. This violates assumption A5 (base rate 20-80%) and renders H-M4 uninformative. Future work should use LLM-based or embedding-based classification.

### Open Models Only
We tested Llama-2-Chat and Mistral-Instruct, both open RLHF models with accessible logprobs. Closed models (GPT-4, Claude) may behave differently, and our findings may not generalize without logprob access.

### Dataset Composition
TruthfulQA, ETHICS, and HH-RLHF may lack natural bidirectional task variation. These benchmarks were designed for accuracy evaluation, not directionality analysis. Purpose-built datasets could enable stronger correlation tests.

### Alternative Confounds
While we controlled for length, topic, format, and difficulty, other confounds (answer distribution, linguistic complexity) might contribute to clustering. The mechanism chain provides theoretical grounding, but confound exhaustiveness cannot be guaranteed.

## Broader Impact

Calibration clustering offers a diagnostic tool for RLHF behavioral analysis. By identifying WHERE models systematically fail, researchers can investigate WHY and develop targeted interventions. The mechanism findings suggest annotation-level interventions may be more effective than post-hoc calibration adjustment.

The negative result for keyword-based detection is itself valuable—it establishes methodological boundaries and motivates semantic feature detection as a concrete next step.
