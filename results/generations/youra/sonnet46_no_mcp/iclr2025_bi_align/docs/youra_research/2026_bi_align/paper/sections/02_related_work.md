# 2. Related Work

Our work sits at the intersection of three research streams: reward misspecification and overoptimization in RLHF, annotation quality and variance, and automation bias in human judgment. Prior work in each stream addresses downstream symptoms of annotation drift — benchmark degradation, label noise, evaluation criterion shift — but not the upstream source in the annotation pipeline itself.

## 2.1 Reward Misspecification and RLHF Overoptimization

Reinforcement Learning from Human Feedback [Christiano et al. 2017; Ouyang et al. 2022] trains reward models on human preference labels and uses these to fine-tune language models via policy gradient methods. A central challenge is reward misspecification: reward models learn to optimize a proxy for quality rather than quality itself, leading to Goodhart's Law violations as optimization pressure increases [Gao et al. 2022].

Pan et al. [2022] provide a systematic framework for mapping reward misspecification to benchmark degradation, demonstrating that even small misspecification errors compound over RLHF training rounds to produce measurable accuracy drops on TruthfulQA and BIG-Bench tasks. Coste et al. [2023] show that annotation variance — disagreement between annotators — limits reward model reliability and contributes to overoptimization. Both lines of work treat annotator preferences as stationary noise rather than as potentially directionally drifting signals.

**Gap:** Neither Pan et al. nor Coste et al. ask whether the annotation signal itself shifts direction over time. They identify the consequence (reward misspecification, benchmark degradation) but do not trace it to a temporal source in the annotation process. Our work fills this gap by analyzing preference signal stationarity directly.

## 2.2 RLHF Annotation Dynamics and Dataset Structure

The datasets underlying our experiments have been documented by their creators. Bai et al. [2022] describe the Anthropic HH-RLHF dataset as a product of sequential annotation phases — helpful, harmless, and red-team phases — with annotators evaluating pairs of AI-generated responses. Stiennon et al. [2020] describe the OpenAI WebGPT comparisons dataset, collected via a multi-session crowdwork design intended to support within-annotator analysis. Neither paper analyzes whether annotator preferences shift directionally across phases.

Ziegler et al. [2019] study the effect of reward model scale on RLHF quality but assume preference stationarity throughout. Perez et al. [2022] analyze annotation quality in red-teaming datasets but focus on adversarial robustness rather than temporal drift. The temporal structure of these datasets — which is precisely what makes annotation drift detectable — has not been exploited for preference stationarity analysis.

**Gap:** Existing work takes multi-round annotation datasets as static corpora. Treating rounds as temporal strata and asking whether the preference signal changes direction across strata is a methodological contribution of this paper.

## 2.3 LLM-as-Judge and Evaluation Adaptation

The closest work to ours is Thakur et al. [2024], who document criterion shift in LLM-as-judge evaluation: language model evaluators adapt their assessment criteria when exposed to AI-generated text, becoming more favorable toward AI-typical stylistic features over time. This provides direct empirical grounding for our hypothesis that the adaptation effect extends to human annotators in RLHF training pipelines.

Our work differs from Thakur et al. [2024] in two important ways. First, we study human annotators providing training labels — the upstream source of the reward signal — rather than automated evaluators used downstream. Second, we connect the adaptation measurement to a specific causal pathway (verbosity coefficient drift → reward model contamination → potential benchmark degradation) rather than documenting the phenomenon in isolation.

Liang et al. [2023] and related work on position bias and verbosity bias in LLM evaluation document that AI evaluators prefer longer, more structured responses independent of quality. We show analogous preferences emerging in human annotation patterns across rounds, suggesting that the bias may originate in or be reinforced by the annotation process itself.

## 2.4 Automation Bias and Human-AI Interaction

Automation bias — defined as the tendency to favor suggestions from automated systems and to under-utilize other information sources [Skitka et al.; Parasuraman & Manzey 2010] — is one of the most replicated findings in human factors research. The effect is strongest under conditions of decision uncertainty, time pressure, and high cognitive load — conditions that characterize large-scale annotation work.

Lee & See [2004] provide a comprehensive review of trust in automation, documenting that criterion drift occurs even in high-stakes professional settings (aviation, medical diagnosis). Dietvorst et al. [2015] show that algorithmic aversion can reverse to algorithmic appreciation under repeated exposure, suggesting that initial human skepticism of AI style may erode across annotation rounds.

**Connection to our work:** Automation bias provides the mechanistic account for why annotation drift is directional (toward AI-typical features) rather than random noise, and why it is strongest under annotation uncertainty. Our null result on the round×ambiguity interaction (Section 5) does not falsify this mechanism — it reflects the absence of per-prompt disagreement labels in HH-RLHF rather than evidence against the theory (Section 6).

## 2.5 Positioning of This Work

Our work occupies a previously empty cell in the 2×2 defined by {training data vs. evaluation} × {measuring drift vs. correcting drift}. We measure drift in training data annotation — an axis orthogonal to all four lines of prior work described above. The AAI provides the first scalar, pre-registerable instrument for this measurement, enabling both retrospective auditing of existing RLHF datasets and prospective monitoring of ongoing annotation pipelines.
