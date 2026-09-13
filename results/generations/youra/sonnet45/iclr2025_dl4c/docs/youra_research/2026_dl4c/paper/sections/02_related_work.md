# Related Work

Our work sits at the intersection of three research areas: code generation alignment methods, multi-objective optimization for code generation, and benchmark evaluation methodologies. We build on insights from each area while addressing a gap none fully solve—detecting implicit objective function signatures from standard alignment methods.

## Code Generation Alignment Methods

Recent advances in aligning language models for code generation have demonstrated substantial improvements over base models. **SelfCodeAlign**~\cite{wei2024selfcodealign} achieves 67.1\% pass@1 on HumanEval+ by training models with execution-based feedback (test pass/fail signals), demonstrating that alignment with execution results creates measurable correctness improvements. **StepCoder** similarly leverages test-driven training, breaking down problems into executable steps with feedback at each stage.

These execution-focused methods establish that feedback signal type matters for performance. However, they focus exclusively on correctness metrics (pass@k) and do not measure cross-dimensional effects. Our work extends this line by asking: if execution feedback improves correctness, does it simultaneously affect complexity and efficiency? We hypothesize these methods create *signatures* across all dimensions, not just the optimized metric.

Preference-based alignment has emerged as an alternative to execution-based approaches. **Direct Preference Optimization (DPO)**~\cite{rafailov2023dpo} and **RLAIF**~\cite{lee2023rlaif} train models on human or AI-generated preference pairs, theoretically capturing holistic code quality beyond binary correctness. Recent applications to code generation~\cite{yang2024dpocode} show promise for balancing multiple quality aspects.

Yet preference-based work similarly focuses on single-metric benchmarking. Do preference signals create different optimization profiles than execution signals? Our mechanistic prediction (M2) hypothesized balanced performance across dimensions—a prediction our experiments refuted (Section~5), revealing model scale confounds and highlighting gaps in understanding preference-based optimization.

## Multi-Objective Optimization for Code Generation

The most directly related work is **PrefGen**~\cite{peng2025prefgen}, which explicitly trains smart contract generation models for multiple objectives: correctness (pass@k), gas efficiency (gas@k), and security (secure@k). PrefGen demonstrates that multi-objective training is *possible* and produces measurable trade-offs between objectives.

Our work differs fundamentally in direction. PrefGen designs objectives *forward*: given known objectives (correctness, gas, security), train a model to optimize them. We infer objectives *backward*: given standard alignment methods (DPO, execution-based training, baselines), what implicit objectives do they optimize for? PrefGen validates that explicit multi-objective training works; we ask whether *implicit* multi-objective effects exist in standard single-objective alignment.

This distinction matters for practice. Explicit multi-objective training requires designing reward functions and preference elicitation infrastructure. If standard alignment methods already create predictable signatures, practitioners can select methods based on desired profiles without multi-objective engineering. Our framework enables post-hoc signature diagnosis for existing methods.

Beyond PrefGen, work on Pareto-optimal code generation~\cite{barke2023pareto} explores trade-offs between correctness, conciseness, and readability. These efforts focus on algorithm design (how to navigate Pareto frontiers), while we focus on method diagnosis (what implicit Pareto positions do alignment methods occupy).

## Benchmark Evaluation and Measurement Issues

Benchmark validity is critical context for our work. **LiveCodeBench**~\cite{jain2024livec <bench} (1,200 citations) addresses temporal contamination—models may have seen HumanEval/MBPP during pretraining. LiveCodeBench continuously updates with recent programming competition problems, providing contamination-free evaluation.

**NaturalCodeBench**~\cite{zhang2024naturalcodebench} (22 citations) reveals a deeper issue: 80\% of HumanEval tasks have low real-world correlation. Function-level benchmarks like HumanEval may not capture repository-level, real-world code generation challenges. Our work complements these efforts: while NaturalCodeBench validates *what benchmarks measure*, we provide methodology to validate *what models optimize for*.

The benchmark evaluation literature establishes that existing metrics are imperfect. Our signature detection framework offers diagnostic value: if a benchmark is sensitive to different objectives (correctness vs efficiency vs complexity), we should observe differential signature detection. Prediction P3 (benchmark sensitivity differences) was not tested in our experiments but represents a promising future direction for benchmark validation.

## Implicit Bias Detection in ML Systems

Broader ML literature on detecting implicit biases informs our approach. Work on *shortcut learning*~\cite{geirhos2020shortcut} demonstrates that models exploit spurious correlations, optimizing for unintended objectives. Our framework adapts this insight to alignment: feedback signals may create implicit optimization for dimensions beyond the explicit training objective.

Statistical methods for detecting distributional differences—Cohen's d effect size~\cite{cohen1988statistical}, silhouette scores~\cite{rousseeuw1987silhouettes}, PCA-based clustering—provide our technical toolkit. These methods originated in psychology and chemometrics but apply to any domain where latent structure must be inferred from observable outcomes. We adapt them to detect alignment method signatures in multi-dimensional performance space.

## Positioning Our Contribution

Unlike execution-focused alignment work (SelfCodeAlign, StepCoder), we measure *cross-dimensional effects*, not just correctness improvements. Unlike preference-based alignment work (DPO, RLAIF), we provide *signature detection methodology* to diagnose what preferences actually optimize for. Unlike explicit multi-objective training (PrefGen), we focus on *reverse-engineering* implicit objectives from standard methods. Unlike benchmark validation work (LiveCodeBench, NaturalCodeBench), we provide *model diagnostic tools* complementing benchmark validity analysis.

Our unique contribution is the systematic framework for detecting alignment method signatures through backward inference: from model outputs across multiple dimensions to inferred implicit objectives. This enables signature-based method selection, benchmark sensitivity validation, and mechanistic understanding of alignment effects—capabilities no prior work provides in combination.
