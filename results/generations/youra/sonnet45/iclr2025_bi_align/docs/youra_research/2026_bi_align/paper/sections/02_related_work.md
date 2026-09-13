# Related Work

Our work bridges three established research domains—RLHF alignment evaluation, linguistic markers in psychology, and proxy validation in NLP—in a novel integration that exposes a critical gap: no prior work validates whether psychological linguistic markers transfer to AI-generated text for agency measurement.

## RLHF Alignment and Evaluation

Reinforcement Learning from Human Feedback (RLHF) has become the dominant paradigm for aligning large language models with human preferences. InstructGPT (Ouyang et al., 2022) demonstrated that fine-tuning with human feedback produces models that are more helpful, honest, and harmless than pure supervised learning or prompting-based approaches. The methodology involves training a reward model on human preference pairs (chosen vs. rejected responses) and using reinforcement learning to optimize model outputs toward higher reward. Anthropic's HH-RLHF dataset (Bai et al., 2022) established benchmark data for helpfulness and harmlessness alignment with 161K preference pairs across conversational contexts.

However, current RLHF evaluation focuses exclusively on AI-side metrics. Standard benchmarks (AlpacaEval, MT-Bench, TruthfulQA) measure response quality, safety, and factual accuracy—properties of the AI's output—but provide zero coverage of human-side effects such as agency preservation, critical thinking capacity, or decision autonomy (Shen et al., 2024). Constitutional AI (Bai et al., 2022) extends RLHF with AI-generated feedback based on constitutional principles, demonstrating that automated proxies can work for alignment properties, but similarly focuses on AI-side harmlessness rather than human-side agency.

**Limitations for Agency Measurement:** While RLHF papers document preference learning mechanisms, they do not measure whether the optimization process preserves or degrades linguistic markers associated with human autonomy. Shapira et al. (2026) identify sycophancy (over-agreement with users) as an emergent property of RLHF, suggesting the mechanism may systematically favor responses that reduce user agency in favor of efficiency. Our work provides the first empirical test of whether this theoretical mechanism manifests in measurable linguistic patterns.

## Linguistic Markers in Psychology

Psychological research has established that specific linguistic features correlate with cognitive and social constructs in human language. Juanchich et al. (2017) demonstrate through controlled experiments that modal verbs (could, might, should) and pronoun usage (I vs. you) systematically affect perceived autonomy attribution—readers exposed to text with more modal verbs rate scenarios as preserving greater decision autonomy (effect size d=0.42, p<0.001 across 6 experiments with N=1200 participants). Biber et al. (1999) document that hedging phrases (appears, seems, possibly, perhaps) mark epistemic stance in academic and conversational corpora, with frequency varying by genre and communicative intent. Hosman (1989) shows that linguistic devices presenting alternatives ("on the other hand", "another option") increase perceived message openness and reduce authoritarian tone.

These findings establish *in human language* that linguistic markers can indicate constructs related to agency, uncertainty, and option-awareness. However, this research analyzes human-authored text in psychology experiments or linguistic corpora—not AI-generated responses in preference learning contexts.

**Limitations for RLHF Transfer:** The cross-domain validity assumption—that markers validated in human psychology transfer to AI text—remains empirically untested. AI language models may use modal verbs, hedging, and alternative-framing for different functions (politeness, uncertainty management, stylistic variation) than humans do for autonomy preservation. Our work is the first to test this assumption empirically rather than accepting it theoretically.

## Proxy Validation in NLP

Natural language processing research frequently employs proxy measures when direct measurement is infeasible. Sentiment analysis uses lexicon-based features as proxies for emotional valence (Mohammad & Turney, 2013), readability metrics proxy comprehension difficulty (Crossley et al., 2017), and perplexity proxies language model quality (Radford et al., 2019). However, systematic validation of these proxies—testing whether they actually measure the target construct—is rare in NLP literature.

Recent work highlights cross-domain transfer failures for NLP proxies. Ribeiro et al. (2020) demonstrate that shortcuts learned on benchmark datasets (syntactic patterns correlating with sentiment) fail to generalize to out-of-distribution examples, revealing that statistical correlations in training data do not guarantee construct validity. Bender et al. (2021) argue that conflating form (linguistic patterns) with meaning (communicative intent) leads to systematic errors when NLP models encounter distribution shifts.

**Lack of Validation Standards:** Despite these documented failures, NLP research rarely applies construct validation methods from psychometrics (Cronbach & Meehl, 1955)—such as internal consistency testing (Cronbach's α), convergent/discriminant validity, or cross-context replication. Proxy measures are often assumed valid based on face validity (lexical overlap with target construct) or single-context correlation without rigorous validation.

Our work applies psychometric construct validation to NLP proxy testing: we require (1) effect size thresholds (not just p-values), (2) internal consistency across markers (Cronbach's α > 0.7), and (3) cross-split replication to establish robustness. This methodological rigor exposes proxy invalidity that would be masked by p-value-only testing, especially with massive samples (N=169K).

## Bidirectional Alignment Framework

Shen et al. (2024) introduce the bidirectional alignment framework through a systematic survey of 400+ interdisciplinary papers spanning machine learning, human-computer interaction, and social computing. They identify two complementary alignment directions: (1) AI→Human alignment (integrating human specifications into AI systems via training, steering, customization), and (2) Human→AI alignment (preserving human agency, empowering critical evaluation, enabling meaningful collaboration). While existing RLHF research extensively addresses AI→Human alignment through preference learning and safety metrics, the Human→AI dimension lacks computational operationalization.

**The Gap Our Work Addresses:** Shen et al. (2024) articulate the conceptual framework and identify the operationalization gap, but do not provide computational proxies for measuring agency preservation at scale. Our work attempts the first such operationalization via linguistic markers, discovering through comprehensive empirical testing that this particular proxy approach fails—a valuable negative result that establishes validation requirements for future operationalization efforts.

## Our Positioning

We are the first to: (1) apply linguistic agency markers from psychology to RLHF evaluation contexts, (2) treat proxy validity as an empirical hypothesis requiring multi-criterion validation (effect size, internal consistency, replication), and (3) demonstrate cross-domain generalization failure from human language to AI text for agency constructs. Our comprehensive refutation provides methodological lessons for AI alignment research: statistical significance (p<0.001) does not guarantee practical relevance with massive samples (N=169K), and cross-domain proxy transfer requires empirical validation rather than theoretical assumption.
