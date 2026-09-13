# Conclusion

We opened by questioning the unexamined assumption that multiple code generation benchmarks—HumanEval, MBPP, APPS—measure distinct competencies. Through systematic empirical investigation using factor-analytic methods, we find this assumption is not supported for execution-based generation tasks: HumanEval and MBPP produce perfect model ranking correlation (ρ = 1.000, p < 0.0001) despite high distributional divergence (KL = 18.4), revealing they measure a single underlying evaluation dimension rather than independent competency constructs.

This negative result matters for benchmark design and model evaluation practices. The field's intuition that "more benchmarks equals more comprehensive evaluation" holds only when benchmarks measure independent dimensions. Our empirical methodology provides the tools to test this assumption, revealing that current execution-based benchmarks offer redundant ranking information. Resources spent evaluating models on multiple generation benchmarks could instead fund genuinely diverse task-type coverage—code understanding, repair, translation, optimization.

Our contributions extend beyond the specific negative finding:

**Methodological Framework:** We demonstrate that hypothesis decomposition with explicit gate conditions (h-e1: infrastructure validation, h-m1: distinctiveness testing) enables failure localization—when h-m1 fails, we know the distinctiveness assumption failed, not downstream factor analysis. This principled stopping point prevents wasted effort on analyses invalidated by failed prerequisites.

**Empirical Validation Protocol:** We show how to separate distributional divergence (do benchmarks have different statistical properties?) from dimensional independence (do benchmarks rank models differently?). These are empirically distinct questions with different answers—high KL with high ρ reveals difficulty modulation without competency separation.

**Theoretical Depth:** We analyze three competing explanations for perfect correlation (unidimensional competency, sample size limitation, benchmark design convergence), identifying the most plausible while acknowledging testable alternatives. This intellectual honesty strengthens scientific discourse around evaluation design.

The path forward is clear: evaluation diversity should come from task-type variety, not within-task-type redundancy. Future benchmark suites should prioritize cross-task coverage (one generation benchmark + one understanding benchmark + one repair benchmark) over multiple instances of the same task type (three generation benchmarks). Empirical validation of dimensional independence should become standard practice—claims that new benchmarks provide "complementary evaluation" should be backed by correlation analysis showing ρ < 0.8, not just design philosophy differences.

This work opens several productive research directions:

**Empirical Taxonomy of Code Task Space:** Apply our factor-analytic methodology across task types (generation, understanding, repair, translation, optimization) to map the dimensional structure of code evaluation space. Which task types measure independent constructs vs. which are redundant? The answer will guide principled benchmark suite design with provable dimensional coverage.

**Confirmatory Validation:** Test 1-factor vs. multi-factor models explicitly using confirmatory factor analysis. Apply item response theory (IRT) to separate difficulty variance from competency variance, testing whether distributional divergence fully explains benchmark differences or whether residual competency dimensions exist.

**Intervention Studies:** Test whether selective model improvements are possible. Can we improve runtime efficiency without affecting correctness? If factors are separable, targeted interventions should show selective effects. If inseparable, improvements propagate across correlated dimensions.

**Cross-Domain Application:** Our methodology applies beyond code generation to any evaluation domain with multiple benchmarks—vision (ImageNet, COCO, ADE20K), NLP (GLUE, SuperGLUE, XTREME), robotics (RLBench, Meta-World). Empirical validation of dimensional structure should become standard practice in benchmark design.

Beyond immediate applications, this work challenges how we think about evaluation. Benchmark diversity is not a design assumption to declare but an empirical property to validate. The existence of multiple benchmarks does not guarantee multi-dimensional evaluation—it creates an opportunity to test whether redundancy or orthogonality characterizes the evaluation landscape. Our negative result, while refuting the original multi-dimensional hypothesis, advances the field by replacing assumption with evidence.

We conclude where we began: code generation models are routinely evaluated on multiple benchmarks under the assumption that each measures distinct competencies. Our empirical investigation reveals this assumption is not supported for execution-based tasks—HumanEval and MBPP measure a shared competency construct with different difficulty calibrations. This finding informs benchmark selection (reduce redundancy), aggregate scoring (averaging is justified), and future benchmark design (prioritize task-type diversity over within-type redundancy). Evaluation practices should be grounded in empirical validation, not unexamined assumptions about dimensional structure.
