# Phase 2B Verification Plan
## H-ScaleJudge-v1: Scale-Dependent Error Patterns in LLM Code Judges

Generated: 2026-08-24T05:14:00Z

---

## Main Hypothesis

**ID**: H-ScaleJudge-v1

**Statement**: Under standardized code correctness evaluation settings (fixed prompt, zero temperature, HumanEval+/MBPP+ benchmarks), if we compare LLM judges of varying scale (7B/70B/proprietary), then (1) judge-execution agreement increases with scale but with diminishing returns, (2) different scales exhibit systematically different FP/FN error patterns, (3) scale-ensemble outperforms the best individual judge, and (4) unanimous scale agreement indicates higher verdict reliability.

**Null Hypothesis (H0)**: No significant difference in judge-execution agreement patterns or error type distributions across model scales. Error types uniformly distributed; ensemble provides no improvement over best single judge.

---

## Sub-Hypotheses (Verification DAG)

### H-E1: Scale-Error Pattern Existence [MUST_WORK]
- **Type**: EXISTENCE
- **Statement**: Different model scales (7B/70B/proprietary) exhibit statistically different FP/FN error ratios when judging code correctness
- **Tests**: P2 - Chi-square test for independence (scale × error_type)
- **Success**: Chi-square p < 0.05
- **Falsification**: p > 0.10; FP/FN ratios identical across scales
- **Prerequisites**: None (entry point)

### H-M1: Scale-Accuracy Ordering [MUST_WORK]
- **Type**: MECHANISM
- **Statement**: Judge-execution agreement increases with model scale (7B < 70B < proprietary) with diminishing returns
- **Tests**: P1 - Kruskal-Wallis H-test for ordinal scale effect
- **Success**: 7B < 70B < proprietary; (70B - 7B) > (proprietary - 70B)
- **Falsification**: Linear or reversed ordering; proprietary shows >20% improvement over 70B
- **Prerequisites**: H-E1

### H-M2: Ensemble Outperformance [SHOULD_WORK]
- **Type**: MECHANISM
- **Statement**: Scale-ensemble (majority vote) outperforms the best individual judge by ≥3%
- **Tests**: P3 - McNemar test comparing ensemble vs best single judge
- **Success**: Ensemble accuracy > best single by ≥3%
- **Falsification**: Improvement < 2% or ensemble worse than best single
- **Prerequisites**: H-E1

### H-M3: Agreement-as-Confidence Signal [SHOULD_WORK]
- **Type**: MECHANISM
- **Statement**: Unanimous scale agreement indicates higher verdict reliability (≥10% more accurate than split verdicts)
- **Tests**: P4 - Two-proportion z-test
- **Success**: Unanimous verdict accuracy > split verdict accuracy by ≥10%
- **Falsification**: Difference < 5%
- **Prerequisites**: H-M2

---

## Dependency Graph (DAG)

```
H-E1 (MUST_WORK) ──┬──> H-M1 (MUST_WORK)
                   │
                   └──> H-M2 (SHOULD_WORK) ──> H-M3 (SHOULD_WORK)
```

**Critical Path**: H-E1 → H-M1 (both MUST_WORK, failure blocks Phase 5)

---

## Risk Analysis

| ID | Risk | Severity | Mitigation |
|----|------|----------|------------|
| R1 | Within-tier variance (DeepSeek vs CodeLlama at 7B) | Medium | Test both 7B models; report if divergent |
| R2 | Prompt sensitivity | Low | Pilot 3 prompts on 10% data |
| R3 | HumanEval+ not representative | Medium | Replicate on MBPP+ (500 problems) |
| R4 | API cost overrun | Low | Use fixed sample sizes; GPT-4 only on final runs |

---

## Timeline (Gantt)

| Phase | Hypothesis | Duration | Dependencies |
|-------|------------|----------|--------------|
| 2C | H-E1 experiment design | 1 day | - |
| 2C | H-M1 experiment design | 1 day | H-E1 design |
| 2C | H-M2 experiment design | 1 day | H-E1 design |
| 2C | H-M3 experiment design | 0.5 day | H-M2 design |
| 3 | Implementation planning | 2 days | All designs |
| 4 | PoC validation | 3 days | Implementation |
| 5 | Baseline comparison | 2 days | PoC validation |

**Estimated Total**: ~10 days

---

## Experimental Setup Summary

**Datasets**:
- HumanEval+ (164 problems, 80x test coverage)
- MBPP+ (500 problems, augmented tests)

**Models**:
- 7B tier: DeepSeek-Coder-7B-Instruct, CodeLlama-7B-Instruct
- 70B tier: CodeLlama-70B-Instruct
- Proprietary: GPT-4

**Baselines**:
- Random (50% expected)
- CodeBERTScore (~58%)
- MCTS-Judge (80% with expensive compute)

**Controlled Variables**:
- Fixed zero-shot prompt (pilot-selected)
- Temperature = 0
- EvalPlus execution ground truth

---

## Dialectical Analysis

### Thesis
Scale-dependent error patterns exist and can be exploited for ensemble benefit.

### Antithesis
Error patterns may be model-specific (architecture confound) rather than scale-dependent. GPT-4's different training regime may make scale comparison invalid.

### Synthesis
Test within-tier consistency (DeepSeek vs CodeLlama at 7B) to control for architecture. If 7B models show similar error patterns, scale effect is supported. GPT-4 serves as "proprietary ceiling" reference, not strict scale comparison.

---

## Phase 2B Completion Checklist

- [x] Parsed Phase 2A outputs (03_refinement.yaml, 02_synthesis.yaml, final_opinions.yaml)
- [x] Extracted main hypothesis and predictions
- [x] Generated 4 sub-hypotheses (1 EXISTENCE, 3 MECHANISM)
- [x] Assigned gate types (2 MUST_WORK, 2 SHOULD_WORK)
- [x] Built dependency DAG
- [x] Risk analysis completed
- [x] Timeline estimated
- [x] Dialectical analysis performed
- [x] Archon project created
- [x] Verification state initialized
