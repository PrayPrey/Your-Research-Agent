# Related Work

Our work builds on three areas: execution-based code generation benchmarks, multi-benchmark evaluation frameworks, and factor-analytic methods for validating measurement instruments. We position our contribution as the first empirical investigation of dimensional independence in code evaluation benchmarks.

## Execution-Based Code Generation Benchmarks

**HumanEval** [Chen et al., 2021] introduced a benchmark of 164 hand-crafted Python programming problems designed to test "algorithmic clarity and problem-solving ability." Each problem includes a function signature, docstring specification, and programmatic unit tests. The benchmark reports pass@k metrics (percentage of problems solved with k samples) as the primary evaluation criterion. Chen et al. emphasize HumanEval's focus on standalone algorithmic tasks that test core programming competencies without requiring domain-specific knowledge.

**MBPP** [Austin et al., 2021] presents 974 Python programming problems sourced from introductory programming exercises, designed to measure "practical programming patterns" used in everyday coding. Unlike HumanEval's algorithmic focus, MBPP emphasizes tasks representative of common programming scenarios—string manipulation, data structure operations, and basic algorithms appearing in real codebases. Austin et al. position MBPP as complementary to HumanEval, targeting "practical coding ability" rather than algorithmic problem-solving.

**APPS** [Hendrycks et al., 2021] provides 10,000 competitive programming problems from coding competition platforms, testing "competitive programming competence" across difficulty levels. APPS problems require complex algorithmic reasoning, advanced data structures, and optimization—significantly more challenging than HumanEval or MBPP.

**Our Finding:** While these benchmark papers emphasize different evaluation philosophies (algorithmic clarity vs. practical patterns vs. competitive programming), we find that HumanEval and MBPP produce perfect model ranking correlation (ρ = 1.000), suggesting they measure the same underlying competency despite documented design differences. This is the first empirical test of whether design philosophy differences translate to dimensional independence.

## Multi-Benchmark Evaluation Frameworks

The **BigCode Evaluation Harness** [BigCode Project, 2023] provides infrastructure for standardized evaluation across multiple code generation benchmarks. It reports pass@k scores independently for each benchmark but does not analyze structural relationships between benchmarks or test dimensional independence. Similarly, code LLM leaderboards (HuggingFace Code Models, PapersWithCode) aggregate multi-benchmark performance but treat each benchmark as an independent evaluation axis without empirical validation.

**Limitation:** Current multi-benchmark frameworks assume dimensional independence without testing it. They report performance on HumanEval, MBPP, and APPS as separate columns, implicitly treating them as measuring distinct competencies. Our work provides the empirical methodology to test this assumption, revealing that execution-based benchmarks offer redundant ranking information.

## Factor Analysis in Evaluation Methodology

Factor analysis is a standard psychometric tool for validating whether multiple measurements (test items, survey questions, evaluation criteria) capture independent dimensions or measure a shared underlying construct. In educational testing, confirmatory factor analysis validates whether reading comprehension, mathematical reasoning, and spatial reasoning represent independent cognitive abilities or load on a general intelligence factor (g).

**Application to ML Evaluation:** Despite widespread use in psychometrics, factor-analytic methods have seen limited application to machine learning benchmark validation. Benchmark design typically emphasizes face validity (does the benchmark appear to test the intended competency?) rather than empirical validation of dimensional structure (do benchmarks measure independent constructs?).

**Our Contribution:** We adapt factor-analytic hypothesis testing to code generation evaluation, providing a principled methodology for testing whether multiple benchmarks reveal independent evaluation dimensions. Our approach separates distributional differences (do benchmarks have different statistical properties?) from dimensional independence (do benchmarks rank models differently?), revealing these are empirically distinct questions with different answers.

## Gap in Existing Work

No prior work has empirically tested whether execution-based code generation benchmarks measure independent latent dimensions or a single shared competency. Benchmark papers assume design philosophy differences imply dimensional independence, but this assumption has never been validated through factor-analytic methods. Multi-benchmark evaluation frameworks report scores independently without analyzing correlation structure or testing whether multiple benchmarks provide genuinely multi-dimensional information.

Our work fills this gap by:
1. **Empirically testing** dimensional independence rather than assuming it from design philosophy
2. **Separating** distributional divergence (statistical properties) from ranking divergence (ordinal structure)
3. **Providing methodology** for rigorous hypothesis decomposition with clear failure localization
4. **Delivering evidence** that current execution-based benchmarks measure a unidimensional competency space

This empirical grounding informs benchmark selection practices and guides future benchmark design toward task-type diversity rather than within-task-type redundancy.
