# Hypothesis Context: H-E1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-05-19
**Main Hypothesis:** Structural Efficiency of Policy Movement: Execution-RL vs DPO for Code Generation
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under controlled KL-matched conditions, if execution-feedback RL (GRPO) is applied instead of DPO on identical base model and data, then execution-RL exhibits ≥20% higher semantic-edit-per-KL than DPO, because execution reward forces probability mass toward control-flow and data-flow AST transformations.

### Type
EXISTENCE (H-E*)

### Rationale
This is the foundational existence check. Before investigating the mechanism, we must empirically demonstrate that structural efficiency (AST edit distance ÷ KL) is actually higher for execution-RL than DPO. This validates the PROVE_NEW claim #1 and establishes the metric itself as meaningful.

---

## Verification Protocol

### Conceptual Test
1. Train all alignment conditions (SFT-only, SFT+DPO, SFT+GRPO-binary, SFT+GRPO-error-type) with dense checkpoint saving
2. Compute per-checkpoint KL divergence (Monte Carlo, fixed held-out prompt set) and identify matched checkpoints (±5% tolerance)
3. Parse model outputs at matched checkpoints to compute AST semantic edit distance (zss library, control-flow + data-flow nodes only)
4. Compute semantic-edit-per-KL ratio and bootstrap 95% CI for execution-RL minus DPO differential
5. Evaluate gate: CI excludes zero AND magnitude ≥20%

### Success Criteria
- Primary: Bootstrap 95% CI for efficiency differential excludes zero and magnitude ≥20%
- Secondary: AST edit distance vs KL sanity plot shows positive correlation (validates KL as proxy)

### Variables (if applicable)
- **Independent Variable:** Alignment method (SFT+DPO vs SFT+GRPO-binary, SFT+GRPO-error-type)
- **Dependent Variable:** Semantic-edit-per-KL at KL-matched checkpoints (±5% tolerance)
- **Controlled Variables:** Base model (DeepSeek-Coder-7B), training prompts, total training tokens, evaluation harness

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** HumanEval+ / MBPP+ / LiveCodeBench
- **Type:** standard
- **Source:** evalplus (pip install evalplus); livecodebench/livecodebench
- **Path:** evalplus/evalplus; livecodebench/livecodebench
- **Hypothesis Fit:** Canonical function-level benchmarks used by all baselines; LiveCodeBench provides contamination-free OOD evaluation

### Selected Model
- **Name:** DeepSeek-Coder-7B-instruct
- **Type:** Decoder-only transformer, code-specialized
- **Source:** deepseek-ai/deepseek-coder-7b-instruct-v1.5 (HuggingFace)
- **Hypothesis Fit:** Open-weight SOTA code LLM, permissive license, 7B scale tractable for multi-condition fine-tuning

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
| Method | Performance | Dataset |
|--------|-------------|---------|
| TÜLU 3 RLVR (Lambert et al., 2024) | ~60-65% HumanEval+ pass@1 (est. 7B scale) | HumanEval, MBPP (combined) |
| CodeRL+ binary RLVR (Jiang et al., 2025) | +4.6% pass@1 over binary baseline | HumanEval, MBPP |
| PPOCoder (Shojaee et al., 2023) | Significant gains over SFT | MBPP, CodeContests |

### Baseline Performance
- SFT-only baseline on HumanEval+: ~45-50% pass@1 (DeepSeek-Coder-7B-instruct)
- DPO with execution-oracle preferences: comparable to SFT+ or slight improvement
- Expected execution-RL (GRPO): ≥20% higher structural efficiency metric than DPO

### Gap Analysis
Primary gap: No controlled comparison of execution-RL vs DPO under identical model+data+benchmark conditions. The structural efficiency metric (semantic-edit-per-KL) is novel and requires empirical validation of the ≥20% differential claim.

---

## Dependencies and Gate Conditions

### Prerequisites
None (H-E1 is the foundation hypothesis)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow

**Consequence if Fails:** STOP — reassess hypothesis. PIVOT option: reduce threshold to directional (CI excludes zero, any magnitude) or investigate AST classifier validity.

**Phase Assignment:** Phase 1 (Foundation)

**Estimated Duration:** 2 weeks

---

## Dependency Context

### Relationship to Other Hypotheses
H-E1 is the foundational hypothesis. H-M1, H-M2, H-M3, H-M4 all depend on H-E1 being satisfied. The entire causal chain (structural reallocation → efficiency metric → pass@1/calibration → OOD transfer) rests on H-E1 establishing the existence of the structural efficiency differential.

Dependency chain: **H-E1 → H-M1 → H-M2 → H-M3 → H-M4**

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS
**Workflow Status:** ACTIVE

---

## Phase 2C Usage Notes

**This context file provides:**
1. Complete hypothesis specification for experiment design
2. Gate conditions for prerequisite validation
3. Dependency information for controlled experiments
4. Success criteria for evaluation design
5. Baseline comparison targets for effect size estimation

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for implementation patterns (Archon, Exa MCP)
3. Use baseline metrics to set comparison targets
4. Design concrete experiment specification (Level 1.5)
5. Output: h-e1/02c_experiment_brief.md

---

*Generated by Phase 2C Workflow (JIT)*
*Optimized for single-hypothesis experiment design*
