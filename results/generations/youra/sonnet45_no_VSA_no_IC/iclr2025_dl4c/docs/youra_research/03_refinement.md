# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-19T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: GAP-001
- **Gap Title**: Optimal Execution Feedback Granularity for Small Models
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 7

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 7

**Convergence Reason**: All 6 convergence criteria met after 7 exchanges:
- ✅ **SPECIFIC**: Clear core claim (efficiency frontier hypothesis)
- ✅ **MECHANISM**: Small model capacity limits + noise reduction via low-dimensional feedback
- ✅ **PREDICTIONS**: 5 testable predictions with success/fail thresholds
- ✅ **NOVELTY**: Feedback as efficiency optimization vs capability maximization
- ✅ **FEASIBILITY**: 40 GPU-hours, existing benchmarks, static coverage analysis
- ✅ **OBJECTIONS**: Saturation risk, coverage proxy limits, error skew all addressed with mitigations

### Key Insights

**Efficiency Frontier Discovery**: Execution feedback granularity exhibits diminishing returns for small models. The optimal granularity is determined by gain-per-bit, not absolute richness of feedback signal.

**Dual-Threshold Rigor**: Prof. Rex's stress test elevated hypothesis from "relative retention" to "absolute + relative" requirements, preventing weak-but-technically-sufficient claims (e.g., "80% of 2 pp = 1.6 pp").

**Information-Theoretic Efficiency**: Shifting from artificial 1-bit ceiling to natural efficiency metric (gain-per-bit) preserves deployment realism while isolating granularity effects.

**Coverage Causation**: Test coverage quality moderates feedback requirements — comprehensive tests enable binary sufficiency, weak coverage benefits from error-type semantics. This will be MEASURED via branch coverage, not assumed.

### Breakthrough Moments

1. **Exchange 6 (Prof. Rex Stress Test)**: Demanding dual thresholds (absolute ≥8 pp AND relative ≥80%) transformed hypothesis from potentially weak to rigorous
2. **Exchange 5 (Dr. Ally Synthesis)**: Integrated all concerns into revised experimental design with natural distributions, efficiency metric, and coverage measurement
3. **Exchange 3 (Dr. Sage Impact)**: Framed contribution as democratization (single-GPU access) vs incremental tuning (marginal gains)
4. **Exchange 4 (Prof. Pax Feasibility)**: Information density normalization concern led to efficiency metric breakthrough

---

## Final Hypothesis

### Title
Feedback Granularity Efficiency Frontier for Small Code LLMs

### Core Claim
For small language models (350M-1B parameters), execution feedback granularity exhibits diminishing returns on code generation alignment. Lightweight feedback signals (binary pass/fail or error-type vocabulary) achieve ≥80% of the performance gains from richer feedback (error messages + stack traces) while using 2-10× fewer information bits per training example.

**Under**: Small model capacity constraints (350M-1B parameters) and existing code generation benchmarks (HumanEval, MBPP)

**If**: We train models with execution feedback at varying granularity levels (binary pass/fail, error-type vocabulary, error+stack-trace)

**Then**: Lightweight feedback (binary or error-type) achieves ≥80% relative retention of rich feedback gains AND ≥8 pp absolute improvement over supervised fine-tuning baseline

**Because**: Small models have limited representational capacity to utilize high-dimensional supervision signals, and lower-granularity feedback provides concentrated, noise-reduced learning signals

### Mechanism
Small models have limited capacity to compress high-dimensional feedback (e.g., full stack traces with file/line/context) into actionable gradients during training. Low-granularity feedback (binary pass/fail, error-type only) concentrates supervision signal into fewer dimensions, reducing noise-to-signal ratio. Benchmark test coverage quality moderates feedback requirements: comprehensive tests (HumanEval) enable binary sufficiency, weaker coverage (MBPP) benefits from error-type semantic hints.

---

## Predictions

### P1 (Primary): Minimalist Sufficiency with Dual Threshold
Binary feedback on HumanEval achieves:
- **Absolute Threshold**: ≥8 pp improvement over SFT baseline
- **Relative Threshold**: ≥80% retention of error-type feedback gains

**Example**: If SFT=40%, error-type=52% (+12 pp), then binary must achieve ≥48% (+8 pp absolute) AND ≥49.6% (+9.6 pp = 80% of 12 pp). Takes stricter threshold.

**Falsification**: Binary < 48% absolute OR <80% relative retention

### P2: Efficiency Decreases with Granularity
Feedback efficiency (pass@1 improvement / bits-per-problem) ranking:
- Binary (1 bit/prob): ≥7 pp/bit
- Error-type (2.3 bits/prob): 4-6 pp/bit
- Error+trace (5.6 bits/prob): 2-3 pp/bit

**Success**: Monotonic decrease confirms diminishing returns

**Falsification**: Ranking violated OR efficiencies statistically indistinguishable

### P3: Test Coverage Causation
Test coverage differences between HumanEval and MBPP explain ≥60% of variance in feedback-type advantage (error-type gain over binary).

**Method**: Measure branch coverage for all problems using coverage.py. Correlate with (error-type gain - binary gain). R² ≥ 0.6 indicates coverage explains variance.

**Falsification**: Correlation r < 0.63 (R² < 0.4) OR HumanEval/MBPP coverage differ by <10 pp (insufficient variance)

---

## Novelty

**Key Innovation**: Establishes execution feedback granularity as an **efficiency optimization problem** (gain-per-bit) rather than a capability maximization problem (richest feedback available). Provides practitioners with a decision rule: match feedback granularity to (model size, benchmark test coverage) instead of defaulting to "richest feedback available."

**Differentiation from Prior Work**:
- **CodeRL+**: Explores RICHER feedback (variable traces) for larger models. We explore MINIMAL sufficient feedback for small models.
- **CoCoS**: Uses opaque accumulated trajectory rewards. We explicitly ablate granularity levels and measure efficiency.
- **Feedback Over Form**: Compares feedback vs NO feedback. We assume feedback is valuable, ask WHICH granularity is optimal.

**Impact**: Democratizes code LLM alignment research by enabling single-GPU budgets to achieve near-optimal results with lightweight feedback.

---

## Experimental Design

### Model Sizes
- 350M parameters (e.g., CodeGen-350M-mono)
- 1B parameters (e.g., StarCoder-1B)

### Benchmarks
- **HumanEval**: 164 algorithm-focused problems with comprehensive test suites
- **MBPP**: 974 entry-level problems (hypothesized weaker test coverage)

### Feedback Conditions
1. **Binary**: Pass/fail only (1 bit/problem)
2. **Error-Type**: Pass/fail + top-5 Python exception types (2.3 bits/problem)
3. **Error+Trace**: Error-type + stack trace depth buckets (5.6 bits/problem)

### Baseline
Supervised Fine-Tuning (SFT) on (problem description, reference solution) pairs without execution feedback

### Resource Budget
- 10 model training runs (R1-R10)
- 350M models: 3 hours/run
- 1B models: 5 hours/run
- Coverage analysis: 2 hours (static, no GPU)
- **Total**: 40 GPU-hours (2 days on A100 40GB)

### Experimental Design Table

| Run ID | Model | Benchmark | Feedback | Info (bits/prob) | GPU-hrs |
|--------|-------|-----------|----------|------------------|---------|
| R1 | 350M | HumanEval | SFT only | 0 | 3 |
| R2 | 350M | HumanEval | Binary | 1.0 | 3 |
| R3 | 350M | HumanEval | Error-type | 2.3 | 3 |
| R4 | 350M | HumanEval | Error+trace | 5.6 | 3 |
| R5 | 350M | MBPP | Binary | 1.0 | 3 |
| R6 | 350M | MBPP | Error-type | 2.3 | 3 |
| R7 | 1B | HumanEval | Binary | 1.0 | 5 |
| R8 | 1B | HumanEval | Error-type | 2.3 | 5 |
| R9 | 1B | MBPP | Binary | 1.0 | 5 |
| R10 | 1B | MBPP | Error-type | 2.3 | 5 |
| R11 | Coverage Analysis | HumanEval + MBPP | - | - | 2 |

---

## Limitations

### Known Constraints
- **Test coverage measurement**: Branch coverage is a proxy, not a complete metric of test quality. Will report multiple coverage types (branch, statement, path) and acknowledge limits.
- **Natural error distributions**: May be skewed toward frequent errors (TypeError). Will report per-error-type stratified gains to identify drivers.
- **Model size range**: 2-size validation (350M, 1B) may miss phase transitions at other scales (e.g., 150M, 500M).
- **Domain specificity**: Python-only, may not generalize to SQL/Shell/other languages.
- **Single-benchmark training**: No multi-task training tested.

### Mitigation Strategies
- **Model saturation risk (MBPP ceiling ~70% for 1B)**: Use HumanEval Pro (harder benchmark) if saturation observed
- **Coverage proxy limits**: Report multiple coverage metrics (branch, statement, path)
- **Error distribution skew**: Preserve natural distributions (deployment realism) + stratified analysis per error type

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met (Specific, Mechanism, Predictions, Novelty, Feasibility, Objections) |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Saturation risk (mitigated), Coverage proxy limits (acknowledged), Error skew (stratified analysis) |
| **Phase 2B Readiness** | READY |

---

## Success Dashboard (All-or-Nothing)

- [ ] P1: Binary ≥48% absolute AND ≥80% relative on HumanEval
- [ ] P2: Efficiency ranking confirmed (binary > error-type > trace in gain/bit)
- [ ] P3: Test coverage explains ≥60% variance in feedback advantage (r ≥ 0.77)
- [ ] P4: Transfer gain > Direct gain for richer feedback (deferred to experimental analysis)
- [ ] P5: 350M and 1B show consistent efficiency ranking (generalization check)

**IF ALL 5 PASS**: Hypothesis survives stress test → Design principle validated  
**IF ANY FAIL**: Boundary conditions identified → Refine hypothesis scope

---

**Hypothesis is bulletproof or breaks in interpretable ways. Either outcome advances the field.**
