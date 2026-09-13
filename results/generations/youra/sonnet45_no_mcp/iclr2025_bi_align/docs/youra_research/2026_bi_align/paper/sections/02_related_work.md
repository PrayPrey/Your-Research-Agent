# Related Work

Our work intersects three research areas: RLHF methods that use preference data for training, alignment evaluation approaches that assess safety, and embedding-based analysis techniques. We position our contribution as testing a fundamental assumption—whether preference data encodes exploitable geometric structure—that prior work has not examined.

## RLHF and Preference Learning

**Foundation.** Christiano et al. [2017] introduced deep reinforcement learning from human preferences, demonstrating that pairwise comparisons provide more scalable supervision than scalar reward engineering. Ziegler et al. [2019] applied this framework to language model fine-tuning, showing preference-based alignment outperforms supervised approaches. These foundational works established the paradigm of learning reward functions from human feedback, but treated preference data purely as training input.

**Production-scale RLHF.** Ouyang et al. [2022] scaled RLHF to InstructGPT with quality-controlled human annotations, introducing the "alignment tax" analysis showing performance vs. alignment tradeoffs. Bai et al. [2022] released the HH-RLHF dataset with 160K+ preference pairs and explicit helpfulness/harmlessness criteria, enabling reproducible alignment research. Critically, both works train Bradley-Terry reward models on preference data, then discard the data after model training—treating it as consumable rather than analyzable structure.

**Our positioning.** We differ fundamentally: instead of *using* preference data to train models, we test whether the data *itself* encodes geometric structure exploitable for evaluation. Our negative finding (no clustering in standard embeddings) does not invalidate reward modeling—rather, it establishes that preference data structure is implicit in learned reward representations, not manifest in general-purpose semantic embeddings. This clarifies when embedding-based approaches are viable (after safety-specialized training) vs. insufficient (pretrained encoders).

## Alignment Evaluation Methods

**Benchmark-based evaluation.** Hendrycks et al. [2020] introduced the ETHICS benchmark with validated human annotations across multiple moral scenarios, providing standardized alignment assessment. TruthfulQA [Lin et al., 2022] evaluates truthfulness through curated question-answer pairs with human verification. While effective, these approaches require manual curation for each evaluation dimension and don't leverage existing RLHF datasets.

**Our differentiation.** We test whether existing RLHF preference data could serve as reusable benchmarks *without* additional annotation. Our negative result shows this requires safety-specialized representations—pretrained embeddings are insufficient. However, our base-rate validation protocol (45.6% genuine violations) demonstrates that RLHF datasets like HH-RLHF contain quality ground truth for evaluation, just not in forms detectable by standard embeddings.

## Embedding-Based Safety Analysis

**Toxicity and harmful content detection.** Supervised classifiers fine-tuned on toxicity labels (Perspective API, OpenAI Moderation) achieve high accuracy for explicit violations. These systems use embedding-based features but require task-specific fine-tuning, not unsupervised geometric discovery.

**Geometric analysis of embeddings.** Prior work has explored geometric structure in embeddings for various tasks—syntactic parsing [Hewitt & Manning, 2019], factual knowledge [Petroni et al., 2019], and bias detection [Bolukbasi et al., 2016]. However, no prior work has tested whether *alignment failures* form geometric structure in pretrained embeddings, nor systematically validated base-rates of genuine violations in preference datasets.

**Our contribution.** We explicitly test the geometric manifold hypothesis for alignment failures: whether rejected responses cluster in interpretable patterns (distance=severity, direction=violation type). Our negative result (Cohen's d=0.034) demonstrates pretrained encoders miss safety-specific features despite human detection consistency (κ=0.724). This reveals a fundamental limitation: general-purpose semantic similarity does not capture alignment distinctions, requiring specialized representations.

**Positioning summary.** Prior RLHF work uses preference data for training reward models (black boxes). Prior alignment evaluation requires manual benchmark curation. Prior embedding analysis assumes geometric structure reflects semantic distinctions. We challenge the third assumption for safety tasks: we test and refute the hypothesis that aggregated human safety judgments induce geometric structure in standard embeddings, while establishing methodological foundations (base-rate validation, annotation consistency protocols) that remain valuable regardless of the negative finding. This work clarifies when embedding-based approaches require safety-specialized fine-tuning vs. failing entirely with pretrained models.
