# Budget Allocation
# H-M2: Proof Depth Filtering Analysis

**Date**: 2026-08-20  
**Hypothesis ID**: h-m2  
**Complexity Level**: 1 (Post-processing Analysis)

---

## Budget Tier: MEDIUM (30,000 tokens)

**Justification**:
- Level 1 complexity (post-processing pipeline, no training)
- 5 Epic tasks, total complexity = 50 points
- Green-field implementation (no existing codebase)
- Single-file modules, straightforward integration

**Tier Mapping**: Level 1 → Medium → 30K tokens

---

## Task Breakdown

| Task ID | Description | Complexity | Allocated Budget |
|---------|-------------|------------|------------------|
| A-1 | Infrastructure Setup | 8 | 5,000 tokens |
| A-2 | Proof Collection (ProofRunner) | 14 | 8,000 tokens |
| A-3 | Tactic Extraction | 12 | 7,000 tokens |
| A-4 | Statistical Analysis | 10 | 6,000 tokens |
| A-5 | Report Generation | 6 | 4,000 tokens |
| **Total** | | **50** | **30,000 tokens** |

---

## Allocation Rationale

**A-1 (5K tokens)**: Infrastructure setup
- Clone miniF2F repo
- Install Lean 4 + Mathlib via elan
- Configure API credentials (LeanCopilot / DeepSeek-Prover)
- Validate environment (lean --version, API test call)
- Straightforward system setup, well-documented

**A-2 (8K tokens)**: Proof collection (highest complexity)
- Implement ProofRunner class (API client + retry logic)
- Handle pass@k=16 attempts per theorem
- Checkpoint/resume functionality (fault tolerance)
- Progress monitoring (244 theorems, ~6-8 hour runtime)
- API rate limiting + error handling
- Largest module, most integration points

**A-3 (7K tokens)**: Tactic extraction
- Primary: Lean 4 metaprogramming (AST traversal)
- Fallback: Regex-based proof script counting
- Validation: 10% manual spot-check (accuracy ≥80%)
- CSV output generation
- Moderate complexity: dual-path implementation

**A-4 (6K tokens)**: Statistical analysis
- Depth classification (shallow/medium/deep)
- Success rate computation (full vs shallow)
- McNemar test (scipy.stats)
- Bootstrap CI (10,000 resamples)
- Depth distribution histogram (matplotlib)
- Standard statistical methods, minimal custom logic

**A-5 (4K tokens)**: Report generation
- Aggregate results (success rates, Δ, statistics)
- Gate evaluation (5% < Δ < 30%)
- Write validation report (04_validation.md)
- Interpretation + limitations section
- Primarily text generation, minimal logic

---

## Risk Buffer

**Allocated**: 30,000 tokens (100% utilization)

**Contingency Strategy**:
- If A-3 AST parsing exceeds budget → use fallback (script counting) immediately
- If A-2 API integration complex → reduce pass@k from 16 to 8 (still valid)
- If A-4 statistical tests exceed budget → use scipy defaults (no custom tuning)

**Underspend Reallocation**:
- Surplus tokens → enhance A-5 (richer visualizations, additional depth strata analysis)
- Or → add confound control (lean-auto depth comparison, if H-E1 data available)

---

## Validation Against Guidelines

**Tier Selection**:
- ✓ Level 1 complexity → Medium budget (per standard mapping)
- ✓ Total complexity 50 points → within Medium range (30-60 points typical)
- ✓ No training/optimization loops → justifies Medium (not High)

**Task Distribution**:
- ✓ Highest allocation to highest-complexity task (A-2: 8K / 14 complexity)
- ✓ Budget proportional to complexity (correlation ~0.95)
- ✓ No task <10% or >30% of total (range: 13-27%)

**Feasibility**:
- ✓ 30K tokens sufficient for 5 Python modules (~500 LOC total estimated)
- ✓ Post-processing pipeline (vs end-to-end training) → lower token needs
- ✓ Comparable to other Level 1 hypotheses (h-e1, h-m1)

---

## Comparison with Other Hypotheses

| Hypothesis | Level | Tier | Budget | Tasks | Notes |
|------------|-------|------|--------|-------|-------|
| h-e1 | 1 | Medium | 30K | 5 | Baseline comparison (similar) |
| h-m1 | 1 | Medium | 30K | 5 | NL ablation (similar) |
| **h-m2** | **1** | **Medium** | **30K** | **5** | **Depth filtering (this)** |
| h-m3 | 1 | Medium | 30K | 5 | Corpus analysis (expected) |
| h-c1 | 2 | High | 60K | 8 | Combined intervention (higher) |

**Consistency**: All MECHANISM hypotheses (h-m1, h-m2, h-m3) allocated Medium budget.

---

## Implementation Guidance

**Token-Efficient Strategies**:
1. **Reuse stdlib**: Use scipy/pandas built-ins (no custom statistical implementations)
2. **Lean 4 subprocess**: Call Lean via subprocess (no custom AST parser in Python)
3. **Config-driven**: Single YAML config (no argparse boilerplate)
4. **Minimal error handling**: Log + skip failures (no elaborate retry frameworks)
5. **Simple checkpointing**: JSON dumps per stage (no database persistence)

**Budget Monitoring**:
- Track token usage per Epic task
- If any task exceeds allocation by >20%, trigger fallback strategy
- Report final utilization in 04_validation.md

---

**Budget Approved**: 30,000 tokens (Medium tier) for h-m2 implementation.
