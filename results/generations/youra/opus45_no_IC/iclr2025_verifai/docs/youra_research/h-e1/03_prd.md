# Product Requirements Document: H-E1

**Date:** 2026-08-12
**Author:** Anonymous
**Hypothesis:** H-E1 - Error Class Independence Verification
**Type:** EXISTENCE (PoC)
**Gate:** MUST_WORK (Jaccard < 0.30)

---

## Executive Summary

This PRD defines requirements for validating the foundation hypothesis that error classes targeted by grammar constraints, static analysis, and SMT-guided repair are largely independent (overlap < 30% Jaccard index). Success enables the multiplicative error reduction model underpinning the full verification pipeline.

---

## Problem Statement

**Context:** The main hypothesis claims that combining formal verification strategies achieves synergistic pass@k improvement because each strategy targets independent error classes.

**Specific Problem:** Before investing in full pipeline implementation, we must verify the independence assumption by measuring pairwise Jaccard overlap between error classes fixed by each strategy.

**Success Condition:** All pairwise Jaccard indices < 0.30

---

## Functional Requirements

### FR-1: Dataset Preparation
- **FR-1.1:** Load HumanEval benchmark (164 problems) via `human_eval.data.read_problems()`
- **FR-1.2:** Generate n=10 code samples per problem per model
- **FR-1.3:** Support CodeLlama-7B-hf and GPT-4 as baseline models
- **FR-1.4:** Total samples: 164 × 10 × 2 = 3,280 code completions

### FR-2: Grammar Constraint Strategy
- **FR-2.1:** Implement syntax checking via Python AST parser
- **FR-2.2:** Apply grammar-constrained decoding (syncode or equivalent)
- **FR-2.3:** Track task_ids where constrained output fixes syntax errors
- **FR-2.4:** Output: Set of grammar-improved task_ids

### FR-3: Static Analysis Strategy
- **FR-3.1:** Run Bandit security analyzer on each code sample
- **FR-3.2:** Run Pylint code quality checker on each code sample
- **FR-3.3:** Apply feedback loop: regenerate with static analysis findings
- **FR-3.4:** Track task_ids where static feedback reduces issues
- **FR-3.5:** Output: Set of static-improved task_ids

### FR-4: SMT-Guided Repair Strategy
- **FR-4.1:** Identify problems with formal specifications (HumanEval-Verus subset)
- **FR-4.2:** Integrate Z3 SMT solver for specification verification
- **FR-4.3:** Apply SMT-guided repair for spec violations
- **FR-4.4:** Track task_ids where SMT repair achieves spec compliance
- **FR-4.5:** Output: Set of SMT-improved task_ids

### FR-5: Overlap Analysis
- **FR-5.1:** Compute Jaccard(grammar, static) index
- **FR-5.2:** Compute Jaccard(grammar, SMT) index
- **FR-5.3:** Compute Jaccard(static, SMT) index
- **FR-5.4:** Compute mean Jaccard across all pairs
- **FR-5.5:** Gate check: all indices < 0.30

### FR-6: Visualization
- **FR-6.1:** Generate bar chart: 3 pairwise Jaccard indices vs 0.30 threshold
- **FR-6.2:** Generate 3-circle Venn diagram of improved sets
- **FR-6.3:** Generate per-model comparison chart (CodeLlama vs GPT-4)
- **FR-6.4:** Save all figures to `{hypothesis_folder}/figures/`

---

## Non-Functional Requirements

### NFR-1: Performance
- Inference time: < 30 minutes for 3,280 samples (A100 GPU)
- Analysis time: < 10 minutes for overlap computation

### NFR-2: Reproducibility
- Fixed random seed for sampling
- Temperature = 0.2 for all generation
- Version-pinned dependencies

### NFR-3: Statistical Validity
- Sample size: Full HumanEval (164 problems)
- Samples per problem: 10 (statistically meaningful)
- Two model baselines for generalization

---

## Data Requirements

| Dataset | Source | Size | Usage |
|---------|--------|------|-------|
| HumanEval | openai/human-eval | 164 problems | Primary benchmark |
| HumanEval-Verus | secure-foundations/human-eval-verus | 23 problems | SMT specifications |

---

## Model Requirements

| Model | Source | Purpose |
|-------|--------|---------|
| CodeLlama-7B-hf | meta-llama/CodeLlama-7b-hf | Open-source baseline |
| GPT-4 | OpenAI API | Proprietary baseline |

---

## Evaluation Metrics

| Metric | Formula | Threshold |
|--------|---------|-----------|
| Jaccard(A,B) | \|A∩B\| / \|A∪B\| | < 0.30 |
| Mean Jaccard | avg(all pairs) | < 0.30 (< 0.25 preferred) |

---

## Dependencies

### External Libraries
- `human-eval`: HumanEval benchmark
- `transformers`: CodeLlama inference
- `openai`: GPT-4 API
- `bandit`: Security analysis
- `pylint`: Code quality
- `z3-solver`: SMT verification
- `matplotlib`: Visualization

### Hardware
- 1x A100 GPU (for CodeLlama inference)
- ~30GB VRAM for 7B model

---

## Success Criteria

### Primary (Gate)
- [ ] All pairwise Jaccard indices < 0.30

### Secondary
- [ ] Mean Jaccard < 0.25 (strong independence)
- [ ] Results consistent across both models
- [ ] Visualizations generated successfully

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| High overlap in one pair | Investigate which error types shared, may need strategy refinement |
| Insufficient SMT coverage | Limited to HumanEval-Verus subset (23/164 problems) |
| API rate limits (GPT-4) | Implement exponential backoff, batch requests |

---

## Output Artifacts

1. `04_validation.md` - Experiment results and gate decision
2. `figures/jaccard_comparison.png` - Bar chart with threshold
3. `figures/venn_overlap.png` - 3-circle Venn diagram
4. `figures/per_model_jaccard.png` - Model comparison
5. `results/overlap_data.json` - Raw overlap metrics

---

*Generated from Phase 2C experiment brief (02c_experiment_brief.md)*
*Next Phase: Architecture design via architecture-agent*
