# Methodology

Our approach operationalizes a precondition-first view of formal repair: measure which failure modes are present before applying methods conditioned on those failure modes. The methodology has three components: (1) the Failure Mode Distribution (FMD) pipeline that classifies generated code failures into actionable strata, (2) three formal repair channels each gated on FMD-conditioned eligibility, and (3) a complementarity measurement framework (C_score) for evaluating failure-set orthogonality between repair channels.

## Overview

Given a set of HumanEval problems P and a code LLM M (CodeLlama-7B), we generate a frozen sample pool: N=20 independent completions per problem using fixed seeds (seed = problem_idx × 100 + sample_idx), at temperature T=0.8. The frozen pool isolates repair-method effects from sampling variance.

For each completion in the pool, we apply the FMD classifier to label its failure mode (syntax, type, functional, or success). We then compute repair channel eligibility based on FMD labels and apply each formal repair method to its eligible subset. Failure-to-success transition sets F_method→✓ are extracted for each method and used to compute pairwise C_scores.

**Rationale for Python-native, Docker-free design.** All tools (SynCode, z3-solver, mypy) are pip-installable with Python-native APIs. Docker-free deployment eliminates infrastructure dependencies, enables reproducibility on standard compute environments, and reduces the setup barrier for follow-up work.

## Failure Mode Distribution (FMD) Pipeline

The FMD pipeline classifies each generated completion into one of four categories via three independent checks applied in priority order:

1. **Syntax stratum** (`ast.parse` failure): The completion cannot be parsed as valid Python AST. This is the coarsest and most common failure mode.

2. **Type stratum** (`mypy.api.run` with type errors detected): The completion parses successfully but mypy reports explicit type mismatches or annotation violations.

3. **Functional/Arithmetic stratum** (test execution failure with Z3 eligibility): The completion is syntactically and type-structurally valid but fails test cases. Problems where test assertions follow the pattern `assert candidate(...) == <integer>` are flagged as Z3-eligible.

4. **Success** (all tests pass): The completion is functionally correct.

The priority order — syntax > type > functional — reflects the causal hierarchy: a completion with syntax errors cannot be evaluated for type or functional correctness. FMD classification runs in parallel across methods: `ast.parse`, `mypy.api.run`, and test execution are independent.

**Z3 Eligibility Criterion.** A problem is Z3-eligible if its canonical test function contains at least one assertion of the form `assert candidate(<integer arguments>) == <integer>`. We scan test function bodies using Python's `ast` module. This criterion is objective, reproducible, and requires no LLM involvement.

## Formal Repair Channels

### Channel 1: SynCode Grammar-Constrained Decoding

SynCode [Ugare et al., 2024] modifies the generation process by applying a Constrained LogitsProcessor that uses a pushdown automaton (PDA) tracking the Python Context-Free Grammar (CFG) to mask tokens that would produce syntactically invalid continuations. Unlike post-hoc repair, SynCode operates at generation time: it constrains the token distribution at each decoding step.

**Rationale.** SynCode directly addresses the syntax stratum — the dominant failure category in our FMD analysis (97.5% baseline). As a generation-time method, it does not require a feedback loop or access to test results, making it universally applicable regardless of problem type. It is the natural first stage in a cascade because it produces syntactically valid outputs that are more amenable to downstream methods.

**Configuration.** We use SynCode v0.4.16 with the Python grammar, integrated via `GrammarAlignedLogitsProcessor` as a `LogitsProcessorList` argument to CodeLlama-7B's `model.generate()`. The constraint operates at the token level during beam-free sampling.

**Activation condition.** None — SynCode is applied to all problems regardless of FMD. It shapes the generation distribution directly rather than requiring post-hoc eligibility screening.

### Channel 2: mypy/ast Iterative Feedback Repair

The mypy channel applies iterative static analysis feedback to fix type and structural errors in generated code. For each completion, `mypy.api.run()` is called with the temporary completion file path. If mypy reports type errors, the error messages are formatted as natural language feedback and passed to a repair LLM (same CodeLlama-7B checkpoint) for iterative revision, up to a maximum of 3 rounds.

**Rationale.** mypy provides structured, interpretable type error messages (error code, line number, description) that can be incorporated into a repair prompt. The method targets the type stratum — completions that are syntactically valid but have type annotation violations. In settings where LLMs generate typed code, this channel provides a distinct signal from SynCode (grammar structure) and Z3 (arithmetic constraints).

**Activation condition.** A completion is eligible for mypy repair if: (1) it parses successfully (`ast.parse` succeeds), and (2) mypy reports at least one type error. In our CodeLlama-7B experiments, condition (2) determines channel activation. As we report in Section 5, the type stratum is 0/134 problems in our experimental setting.

**Configuration.** `mypy.api.run([filepath, '--strict', '--no-error-summary'])` called via Python subprocess. Maximum 3 feedback rounds. Repair prompt appends mypy error messages to the original problem docstring.

### Channel 3: Z3 SMT Repair

For Z3-eligible problems, we encode the correctness requirement as an SMT constraint satisfaction problem. Given a test assertion `assert candidate(a1, ..., an) == v` where a1...an and v are integer constants, we define integer variables x1...xn and construct a Z3 formula asserting the candidate function's algebraic form produces the expected output.

**Rationale.** Z3 addresses a fundamentally different failure class than SynCode or mypy: arithmetic constraint satisfaction. While SynCode prevents syntax errors and mypy identifies type violations, Z3 operates by symbolic constraint solving — searching for code that provably satisfies integer-equality assertions. This targets the arithmetic/logical stratum and is structurally orthogonal to the other two channels.

**Activation condition.** A problem is Z3-eligible if its test function contains integer-equality assertions (confirmed by the Z3 eligibility criterion in the FMD pipeline). Our measurements confirm 54/164 HumanEval problems (33%) satisfy this criterion.

**Configuration.** z3-solver v4.16.0.0 Python API. Timeout: 60 seconds per problem. Integer arithmetic theory (QF_LIA). Each test assertion becomes a separate constraint; we solve for a satisfying assignment and synthesize a candidate function from the solution.

## Complementarity Measurement: C_score

To measure whether two repair channels address distinct failure subsets, we define the C_score (Complementarity Score) as the deviation from independence expectation in the Jaccard overlap of failure-to-success transition sets.

**Failure transition set** F_A→✓: the set of (problem, sample) pairs where method A converts a failing completion to a passing one.

**C_score definition:**
```
C_score(A, B) = E[J_indep] - J_obs(F_A→✓, F_B→✓)
```

Where J_obs is the observed Jaccard similarity between transition sets, and E[J_indep] is the expected Jaccard under the independence null (computed analytically from set sizes). A C_score > 0 indicates the methods address more distinct failures than expected by chance; C_score = 0 indicates independence; C_score < 0 indicates unexpected overlap.

**Statistical testing.** We use bootstrap resampling (10,000 iterations, paired by problem) to compute 95% confidence intervals on C_score. With Bonferroni correction for multiple pairs (α=0.05/3=0.0167 per pair). Significance is declared when the bootstrap CI lower bound exceeds 0 at the corrected α level.

**Eligibility conditioning.** C_score is computed within failure-type-stratified subsets: mypy-SynCode C_score is computed on problems in the type stratum; Z3-SynCode C_score is computed on problems in the arithmetic/Z3-eligible stratum. This conditioning is critical: comparing transition sets across strata conflates channel scope with complementarity.

## Experimental Protocol

**Data preparation.** We use HumanEval (164 problems) as the primary benchmark. For h-e1 (operationality check), we use a 20-problem subset (lexicographic sort, problems 0–19). For h-m1 (SynCode mechanism check) and h-m2 (FMD analysis), we use the full 134-problem baseline pool (30 problems excluded for infrastructure reasons).

**Frozen pool.** For each problem, we generate N=20 completions using fixed seeds. Seed scheme: seed_i = problem_idx × 100 + sample_idx. This ensures identical samples are evaluated across all repair methods, isolating method effects from sampling variance.

**Pipeline execution.** FMD classification runs first. Repair channel eligibility is determined per problem-sample pair. SynCode generates a separate pool; mypy and Z3 operate on the baseline pool. Metrics are computed on the final pass/fail status after repair.
