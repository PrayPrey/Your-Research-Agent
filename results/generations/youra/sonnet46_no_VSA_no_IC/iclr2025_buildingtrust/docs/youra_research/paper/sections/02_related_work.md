## 2. Related Work

Our work sits at the intersection of multi-dimensional LLM trustworthiness evaluation, adversarial robustness benchmarking, and cross-benchmark predictive validity methodology. We describe each line and explain what it leaves unanswered.

### 2.1 Multi-Dimensional LLM Trustworthiness Evaluation

**TrustLLM** [Huang et al., 2024] is the most comprehensive publicly available trustworthiness evaluation of open and proprietary LLMs, covering 16 models across six dimensions including fairness (BBQ), robustness (ANLI, OOD tasks), privacy, and safety. TrustLLM provides consistent single-source evaluation scores that enable our analysis, but does not compute rank correlation between in-distribution and OOD benchmark variants as a research question. It reports absolute scores, not predictive validity.

**DecodingTrust** [Wang et al., 2023] evaluates GPT-3.5 and GPT-4 on eight trustworthiness dimensions including adversarial robustness and fairness, finding that GPT-4 is more vulnerable to adversarial jailbreaking despite higher standard benchmark scores. This N=2 rank reversal observation motivated our adversarial disruption hypothesis — which our N=16 analysis falsifies. The lesson is that two-model anecdotes do not scale.

**HELM** [Liang et al., 2022] provides holistic multi-scenario evaluation across 42 models and 7 metrics, establishing the multi-benchmark multi-model evaluation paradigm. Like TrustLLM and DecodingTrust, HELM reports within-scenario scores rather than asking whether one scenario's rankings predict another's. Our predictive validity framing is orthogonal to — and enabled by — this evaluation infrastructure.

These evaluations collectively establish that trustworthiness is multi-dimensional and model-specific. What they do not provide is an analysis of whether evaluation results on in-distribution conditions transfer predictively to OOD conditions. That is the question we ask.

### 2.2 Adversarial Robustness Benchmarks

**AdvGLUE** [Wang et al., 2021] applies 14 adversarial attack methods (word-level and sentence-level) to GLUE tasks, producing a benchmark explicitly designed to defeat models that pass the in-distribution GLUE tasks. All tested models score far below benign accuracy. The design philosophy — iterative human-model adversarial data collection to maximally challenge current models — underpinned our initial hypothesis that rank stability would be disrupted. Our results show that AdvGLUE rank stability (ρ = 0.868) contradicts this intuition at the model-ranking level.

**ANLI** [Nie et al., 2020] constructs adversarial NLI rounds (R1, R2, R3) through iterative human-and-model-in-the-loop processes, with each round designed to defeat models that pass earlier rounds. ANLI R1→R3 is the canonical adversarial difficulty progression. Our finding that partial ρ_ANLI = 0.684 (p = 0.007) after MMLU control is positive — not near zero — indicates that the adversarial construction disrupts model performance but preserves relative model ordering.

A related result appears in **Wang et al.** [2023], evaluating ChatGPT on AdvGLUE and ANLI against baseline models. While they find ChatGPT advantages on OOD tasks, they do not compute cross-model rank correlations and do not control for capability. Our study extends this to 16 models with capability control.

The key insight from this literature: adversarial benchmark papers typically ask "how does performance degrade?" rather than "does the rank ordering of models change?" These are different questions with different answers.

### 2.3 Fairness Benchmark Design

**BBQ** [Parrish et al., 2021] constructs 50,000 QA items across 9 social bias categories, with disambiguated contexts (where factual information resolves the answer) and ambiguous contexts (where only stereotype-consistent or stereotype-inconsistent guessing is possible). BBQ documents that models rely on stereotypes under ambiguous conditions — 3.4pp accuracy advantage when answers align with social bias. The disambiguated→ambiguous shift constitutes a natural in-distribution/OOD pair for fairness, which we exploit.

BBQ does not compute whether model *rankings* on disambiguated items predict rankings on ambiguous items. Our finding that they do — with near-perfect partial ρ = 0.962 — validates BBQ's construct validity at the cross-model level while raising the question of whether this reflects stable model mechanisms or shared benchmark structure.

### 2.4 Cross-Benchmark Predictive Validity

**Gevers and Daelemans** [2026] provide the closest methodological predecessor: they compute rank correlations with leave-one-family-out cross-validation across 23 LLMs on commonsense benchmarks, finding task-dependent predictive validity. Their work establishes the applicability of the rank correlation approach to LLM evaluation research — we extend it to trustworthiness dimensions, which differ from commonsense tasks in two key ways: (1) higher safety stakes motivate the analysis, and (2) the ID/OOD structure reflects mechanistically distinct properties (stable latent biases for fairness vs. adversarial design for robustness).

**GLUE-X** [Yang et al., 2023] measures in-distribution to OOD accuracy gaps for encoder-only PLMs across 12 OOD test sets, finding systematic degradation. GLUE-X evaluates accuracy gaps, not rank correlations, and covers encoder-only PLMs — not the decoder-only LLMs in our study. The architectural divergence between GLUE-X's model population and TrustLLM's population is why GLUE→AdvGLUE was unavailable for our LLM analysis.

### 2.5 Summary of Gap

Existing work evaluates trustworthiness on individual benchmarks (TrustLLM, DecodingTrust, HELM), constructs adversarial benchmarks to challenge models (AdvGLUE, ANLI, BBQ), and demonstrates cross-benchmark rank correlation methodology for commonsense benchmarks (Gevers and Daelemans, 2026). No prior study computes capability-controlled partial Spearman ρ between in-distribution and OOD trustworthiness benchmark model rankings across multiple dimensions and 15+ models. We fill this gap.
