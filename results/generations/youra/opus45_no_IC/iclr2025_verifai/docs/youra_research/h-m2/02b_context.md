# Phase 2B Context: H-M2

**Hypothesis ID:** H-M2
**Type:** MECHANISM
**Statement:** Static analysis identifies semantic patterns (security, reliability) in syntactically valid code, reducing issues after feedback

## Gate Condition

**Type:** SHOULD_WORK
**Pass Condition:** Security/reliability issues decrease after static analysis feedback
**Fail Action:** Document limitation, explore overlap with grammar constraints

## Prerequisites

- H-M1: VALIDATED (Grammar constraints reduce compilation errors)
  - Result: 40% error reduction with SynCode
  - Proven: Prefix automata enforcement works

## Experimental Setup (from Phase 2B)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| Dataset | PythonSecurityEval | Security-sensitive tasks with test cases |
| Tools | Bandit (security), Pylint (reliability) | Established static analysis tools |
| Model | GPT-4o / CodeLlama-7B | Capability spectrum coverage |

## Success Criteria (PoC)

1. Security issues decrease after Bandit feedback
2. Reliability issues decrease after Pylint feedback
3. Issues detected are semantic (different from compilation errors)

## Continuation Context

H-M2 builds on H-M1's syntactically-valid outputs. Static analysis operates on code that passes syntax checks but may have:
- Security vulnerabilities (SQL injection, command injection, etc.)
- Reliability issues (unhandled exceptions, resource leaks)
- Code quality problems (naming, documentation)

The hypothesis tests whether this second filter catches errors orthogonal to syntax errors.

## Reference Literature

- Blyth et al. 2025: "Static Analysis as a Feedback Loop" - GPT-4o security 40%→13%, reliability 50%→11%
- Alrashedy et al. 2023: "Can LLMs Patch Security Issues?" - PythonSecurityEval benchmark
- cyb3rlab/CodeEnhancer: Bandit+Pylint iterative refinement framework
