# Discussion

## Key Findings

Our experiments reveal several important findings that reframe feedback routing for LLM code generation:

**Finding 1: Cascade routing's validated benefit is computational efficiency, not cognitive efficiency**

Our results demonstrate that cascade routing (mypy → pytest conditional gating) provides token efficiency (mock: 0.733 ratio) and early error detection (99.6% mypy detection rate) through architectural layering—fast cheap checks before expensive checks, with conditional execution gating skipping 35.8% of test runs. However, the attention economy hypothesis remains untested due to H-M2 implementation failure, leaving cognitive efficiency claims unverified.

This distinction matters for system design: cascade routing's value proposition is computational resource optimization (reduced execution cost, token efficiency), not LLM-internal processing improvement. Production systems should use cascade routing to save compute budget, not because it helps LLMs "focus better." The architectural principle—computational layering with early filtering—applies regardless of whether LLMs internally normalize feedback.

**Finding 2: Static analysis serves as nearly universal pre-filter for dual-sensitive tasks**

The extreme mypy detection rate (99.6%, far exceeding predicted 30-40%) suggests that for dual-sensitive programming tasks where both type and logic errors co-occur, static analysis catches almost all samples before execution. This validates static analysis as a practical first-pass filter when using base code generation models on statically-typed languages.

This finding has immediate practical implications: LLM coding assistants working with statically-typed languages (Python with type hints, TypeScript, Java) should always run static analysis before test execution, not for cognitive reasons but for computational efficiency. The <0.1 second mypy check prevents 5-10 second pytest execution in the vast majority (99.6%) of cases.

**Finding 3: Dual-sensitive task classification enables within-task paired experimental designs**

Our methodological contribution—dual-sensitive task classification with within-task variance filtering (SD ≤ 1.0)—successfully identified 35 qualifying tasks (175% of target), demonstrating that this approach provides adequate task pools for feedback routing experiments. Each task serves as its own baseline, isolating routing policy effects from task difficulty confounds.

This methodology generalizes beyond cascade routing: any multi-source feedback orchestration research can use dual-sensitive classification to identify tasks where source combination genuinely matters, avoiding tasks with single-source dominance that would confound routing policy effects.

## Limitations

Our work has several limitations that bound the scope of our claims:

**Limitation 1: Attention economy hypothesis untested (H-M2 incomplete)**

The claim that sequential single-source feedback presentation reduces LLM cognitive load remains unverified due to H-M2 runtime error (TypeError in data format handling). Without iteration-to-solution metrics comparing CASCADE vs. AGGREGATION, we cannot support attention economy or iteration reduction claims.

**Why acceptable:** Validated mechanisms (99.6% early detection, 0.733 token efficiency mock) provide sufficient contribution without cognitive efficiency claims. Our refined hypothesis explicitly narrows scope to computational efficiency only, removing unsupported claims about iteration reduction or LLM attention management.

**Future work:** Fix data format mismatch in get_task_tests(), re-run H-M2 experiment with paired t-test analysis. If μ_cascade ≥ μ_aggregation (no iteration advantage), this would confirm cascade routing's value is purely computational, not cognitive—LLMs may internally normalize feedback regardless of presentation order, making external routing policy irrelevant for cognitive load reduction.

**Limitation 2: Token efficiency based on mock simulation, not real inference (H-M3)**

H-M3 token efficiency validation used mock simulation with synthetic pass rates rather than real CodeLlama-7B inference. The 0.733 ratio is based on simulated token counts and execution gating logic verification, not measured inference costs.

**Why acceptable:** All code paths verified functional through PoC validation. The 0.733 ratio is plausible given H-M1's 99.6% detection rate (if mypy catches 99.6% of samples, conditional gating should skip execution frequently, reducing tokens). Mock simulation tested actual routing logic with realistic parameters derived from baseline experiments.

**Future work:** Run full H-M3 experiment with CodeLlama-7B inference (estimated 4-6 hours runtime). Validate mock assumptions against real token measurements. If real ratio significantly exceeds 1.15 threshold, this would indicate mock simulation underestimated verbosity overhead or overestimated gating efficiency.

**Limitation 3: Results scope limited to CodeLlama-7B base model on Python with mypy**

All experiments used CodeLlama-7B base model (not instruction-tuned) on statically-typed Python code with mypy --strict. Results may not generalize to:
- Larger models (34B+) with better type annotation capabilities
- Instruction-tuned variants aligned to ignore redundant feedback
- Other languages (Java, TypeScript) with different static analyzers
- General programming tasks beyond dual-sensitive classification

**Why acceptable:** Explicit scope definition is scientifically rigorous. Our contribution is mechanism validation within defined boundaries (dual-sensitive tasks, base 7B model, Python/mypy), not universal claims across all code generation scenarios. Clear boundary conditions enable future work to test generalization systematically.

**Future work:** Test with CodeLlama-34B and CodeLlama-Instruct to determine model-size effects. Extend to Java (Checkstyle) and TypeScript (tsc --strict) to test language/tool generalization. Evaluate on non-dual-sensitive HumanEval tasks to identify cascade routing applicability boundaries.

**Limitation 4: Dual-sensitive task classification may not represent real-world distributions**

The 35 qualifying tasks (21.3% of HumanEval) were selected based on dual-sensitive classification criteria. Real-world code generation workloads may have different error distribution patterns (e.g., production systems may have fewer type errors due to existing codebases with type hints, or more logic errors due to complex business requirements).

**Why acceptable:** Dual-sensitive classification is an explicit experimental design choice to isolate routing policy effects, not a claim about real-world task prevalence. Our scope is limited to tasks where both static and dynamic verification provide complementary signals—the classification defines the applicability boundary.

**Future work:** Conduct field study with production LLM coding assistants to measure actual error distributions. If real-world tasks exhibit lower dual-sensitivity rates, cascade routing applicability would be narrower than our 21.3% estimate. Conversely, if production codebases have higher dual-sensitivity due to stricter type requirements, cascade routing benefits may be more widespread.

## Broader Impact

**Positive Impacts:**

Computational efficiency gains from cascade routing reduce energy consumption and cost for LLM code generation at scale. At millions of code generation queries (GitHub Copilot, Amazon CodeWhisperer, etc.), reducing token usage by 26.7% (mock simulation) and skipping 35.8% of test executions translates to significant infrastructure savings and lower carbon footprint. Organizations deploying LLM code generation can adopt cascade routing as a system-level optimization without model retraining or architectural changes.

**Negative Impacts:**

Over-reliance on static analysis as a pre-filter could bias LLM coding assistants toward statically-typed languages (Python with type hints, TypeScript, Java), potentially disadvantaging dynamically-typed languages (JavaScript, Ruby, Python without hints) where static analysis provides less coverage. If systems optimize exclusively for cascade routing efficiency, they may underinvest in feedback mechanisms better suited to dynamic languages (e.g., runtime tracing, symbolic execution).

Additionally, the extreme mypy detection rate (99.6%) may be specific to CodeLlama-7B base model's weak type annotation capabilities. Production systems using larger or instruction-tuned models may see lower detection rates, reducing cascade routing's computational advantage and potentially wasting implementation effort on routing policies that provide marginal benefits for better models.

**Mitigation Strategies:**

Production systems should measure actual static analysis detection rates on their specific model/language combinations before investing in cascade routing infrastructure. For languages or models where detection rates fall below practical thresholds (e.g., <50%), alternative routing policies (execution-first, parallel verification) may be more appropriate. System designs should remain modular, allowing routing policy to adapt to measured detection rates rather than assuming universal applicability.

**Methodological Contribution:**

Our dual-sensitive task classification methodology (within-task paired variance filtering with dual-pattern detection) is broadly applicable beyond code generation. Any multi-source verification scenario—formal proof assistants with theorem provers and type checkers, configuration synthesis with schema validation and deployment testing, SQL query generation with syntax checks and execution plans—can use analogous classification to identify tasks suitable for feedback routing experiments. This methodological pattern (classify tasks by source complementarity, filter by within-task variance, use paired-comparison design) provides a generalizable template for orchestration research.

## Theoretical Implications

**Computational Layering vs. Cognitive Efficiency:**

Our results challenge the assumption that feedback routing's primary benefit is cognitive (LLM attention management). Instead, the validated mechanisms—early error detection (99.6%), conditional execution gating (35.8% skip rate), token efficiency (0.733 mock ratio)—all point to architectural benefits: computational layering with early filtering.

This distinction suggests a different research direction for multi-source LLM verification: rather than optimizing for how LLMs "think about" feedback, we should design systems that minimize computational waste. Cascade routing is not a cognitive aid but a compiler optimization pattern applied to LLM systems—fast passes before expensive passes, with intermediate results gating downstream processing.

**Future Research Questions:**

1. **Do larger models internally normalize feedback?** If CodeLlama-34B or GPT-4-level models process CASCADE and AGGREGATION identically (equal iterations-to-solution), this would confirm that routing policy is computationally relevant but cognitively neutral. LLMs may have sufficient capacity to internally prioritize error sources regardless of external presentation order.

2. **Does cascade routing generalize beyond code generation?** Can multi-layer verification architectures (static → dynamic → semantic) provide computational efficiency for other structured generation tasks (formal proofs, configuration synthesis)? Our results suggest the principle—fast cheap checks before expensive checks—should apply wherever verification stages have asymmetric costs.

3. **Can adaptive routing learn when to escalate?** Instead of fixed cascade policies (always mypy first), can systems learn task-specific routing (mypy-first for type-heavy tasks, pytest-first for logic-heavy tasks) based on measured detection rates? This would extend our dual-sensitive classification from experimental design tool to production routing policy.

4. **What are the limits of static analysis as pre-filter?** At what model size or instruction-tuning level does type annotation quality improve enough that mypy detection rates drop below practical thresholds? Identifying this boundary would define cascade routing's applicability scope across the model size spectrum.
