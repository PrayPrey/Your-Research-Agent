# Related Work

Our work sits at the intersection of three research paradigms: isolated benchmark evaluation, multi-dimensional trustworthiness measurement, and multi-task learning theory. Each paradigm offers partial insight into trustworthiness dynamics, but none characterizes the cross-dimensional coupling patterns we investigate.

## Isolated Benchmark Evaluation

The trustworthiness evaluation literature has established robust benchmarks for individual dimensions. TruthfulQA measures factual accuracy and resistance to common misconceptions, with 817 questions across 38 categories testing whether models reproduce false beliefs. BBQ (Bias Benchmark for QA) evaluates social bias across nine demographic dimensions (age, gender, race, religion, etc.) through ambiguous-context question answering, while BOLD provides 23,679 open-ended prompts for bias evaluation in generation. For adversarial robustness, AdvGLUE and ANLI test model resilience to adversarially constructed inputs designed to exploit reasoning failures.

These benchmarks have driven substantial progress in measuring individual trustworthiness dimensions, with hundreds of papers reporting TruthfulQA scores, fairness metrics, and robustness evaluations. However, the evaluation paradigm treats dimensions independently—papers report separate scores for truthfulness, fairness, and robustness without characterizing relationships between them. This approach cannot reveal whether improving one dimension affects others, or whether trade-offs exist. Our work extends this paradigm by measuring all dimensions before and after each intervention, enabling correlation analysis.

## Multi-Dimensional Trustworthiness Frameworks

Recent work has recognized the need for comprehensive trustworthiness evaluation. MME (Multimodal LLM Evaluation) introduced the first large-scale evaluation spanning perception and cognition tasks, establishing that models exhibit varying performance across dimensions. TrustLLM and DecodingTrust frameworks provide systematic evaluation across six trustworthiness principles (truthfulness, safety, fairness, robustness, privacy, machine ethics), demonstrating that no model performs uniformly well across all dimensions.

While these frameworks measure multiple dimensions, they focus on comprehensive benchmarking rather than characterizing dynamics. MME reports aggregate scores; TrustLLM documents that models differ in their trustworthiness profiles. Neither framework investigates whether dimensions trade off or co-improve under interventions, nor whether patterns generalize architecturally. Our work complements these frameworks by using perturbation analysis to reveal the correlation structure between dimensions that multi-dimensional measurement alone cannot capture.

## Multi-Task Learning and Task Interference

The multi-task learning (MTL) literature provides theoretical grounding for understanding cross-dimensional effects. MTL research demonstrates that tasks sharing neural representations can exhibit negative transfer—improving one task degrades another when they compete for representational capacity. Gradient-based interference analysis shows that conflicting gradient directions in shared parameters create optimization trade-offs, requiring specialized methods (Pareto optimization, gradient surgery) to balance competing objectives.

Our work differs in two critical ways. First, MTL focuses on joint optimization during training with explicit multi-task losses, while we study single-task interventions' cross-dimensional impacts post-training. Second, MTL research primarily characterizes task interference in supervised settings, whereas we investigate trustworthiness dimensions as emergent capabilities rather than explicit training targets. The connection is that both settings involve shared representations creating coupling, but our perturbation-based approach reveals dimension relationships without requiring multi-objective training protocols.

## The Gap We Fill

No prior work systematically characterizes which trustworthiness dimension pairs exhibit trade-offs versus independence, or whether patterns replicate architecturally. Isolated evaluation measures dimensions separately. Multi-dimensional frameworks measure them together but do not analyze relationships. Multi-task learning provides theory for joint optimization but not post-hoc characterization of single-task interventions.

Our contribution is the first taxonomy of dimension relationships (trade-off, independent, architecture-specific) derived from perturbation-based correlation analysis. This fills the gap between isolated evaluation and multi-task optimization, providing practitioners with predictive knowledge about multi-dimensional consequences of targeted interventions. Where prior work asks "how trustworthy is this model?" we ask "how do trustworthiness dimensions interact when we intervene?"
