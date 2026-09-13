---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Execution Feedback Density & Training Data Composition for Code LLM Post-Training"
---

# Research Brainstorm Session Results

**Session Date:** 2026-05-02
**Facilitator:** Research Question Architect
**Participant:** Anonymous
---

## Executive Summary

**Initial Interest:** Deep learning for code — post-training alignment for code LLMs, pivoting from reward-signal type comparison to training data composition effects on execution-feedback RL, informed by the ICLR 2025 DL4C workshop CFP and lessons from previous H-M1 failure

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode)

**Session Duration:** < 1 minute (automated extraction + failure-informed generation)

---

## Starting Context

The ICLR 2025 DL4C (Deep Learning for Code) workshop invites research on emergent possibilities and challenges in applying deep learning to code-related tasks. Key focus areas include: post-training and alignment for code (learning from execution/AI/human feedback), agentic methods, developer productivity, open science, and benchmarking/evaluation.

Previous pipeline attempt: "Execution vs. AI Feedback Signal Density in Code LLM Post-Training" — explored whether GRPO with execution reward outperforms DPO with AI feedback across task granularity (function-level vs. repo-level). H-E1 (GRPO improves function-level pass@1) was VALIDATED. H-M1 (repo-level GRPO advantage variance > function-level) FAILED due to inverted mechanism.

Source Type: Workshop CFP / Structured Input + ROUTE_TO_0 Failure Recovery

---

## Lessons from Previous Attempts

### What Was Tried Before
- **Research Direction:** Comparing execution-feedback GRPO vs. AI-feedback online DPO for code LLMs across task granularity levels (function-level HumanEval+/MBPP+ vs. repository-level SWE-bench Verified)
- **H-E1 (VALIDATED):** GRPO with unit-test execution reward measurably improves pass@1 on HumanEval+ and MBPP+ for DeepSeek-Coder-7B. The mechanism works at function level — dense execution signals yield consistent reward gradients.
- **H-M1 (FAILED — MUST_WORK gate):** Predicted that GRPO advantage variance would be *higher* at repo level than function level due to sparse rewards. Reality was the opposite: function-level advantage variance (mean=0.931) >> repo-level (mean=0.152). Root cause: ~85% of repo-level GRPO steps produce all-zero rewards across all G=8 generations, making advantages identically zero and collapsing variance — reward sparsity *suppresses* variance, it does not inflate it.

### Why It Failed
The H-M1 mechanism claim confused two distinct phenomena:
1. **Reward magnitude variance** (high when some steps get reward, others don't) — this increases with sparsity in theory
2. **GRPO advantage variance** (computed *within* a group of G completions) — this collapses to zero when ALL G completions get the same reward (0.0), which happens at ~85% of repo-level steps

The failure was a fundamental mechanism error, not an implementation bug. No parameter tuning can fix an inverted causal direction.

### How THIS New Direction Avoids Those Pitfalls
1. **No repo-level GRPO training claims**: SWE-bench Verified is kept only as an *evaluation* benchmark (not a training environment), avoiding the degenerate-step collapse issue entirely.
2. **No advantage variance predictions**: The new hypothesis focuses on observable benchmark metrics (pass@1, pass@k) rather than internal GRPO training dynamics.
3. **Pivot from feedback-type comparison to data composition**: Instead of asking "which feedback signal is better," we ask "how does the *composition* of training problems (by difficulty tier) affect execution-feedback RL gains?" — a question that is directly testable using existing datasets.
4. **Stays within H-E1's validated finding**: H-E1 confirmed that execution-feedback GRPO works at function level. The new direction builds on this, asking what makes it work *better* (data difficulty composition).

---

## Session Plan

ROUTE_TO_0 auto-generation — informed by H-E1 validation and H-M1 failure analysis. Research direction pivots to training data composition effects on execution-feedback RL for function-level code generation, using existing datasets and benchmarks only.

---

## Technique Sessions

ROUTE_TO_0 Mode — No interactive sessions. Research components extracted from DL4C workshop CFP and failure context analysis.

Key insight driving pivot: H-E1 proved execution-feedback GRPO works at function level with APPS+CodeContests training data. The open question is: *within* function-level training, does the difficulty distribution of training problems (easy vs. hard competitive programming problems) moderate the effectiveness of execution-feedback RL? This is a natural follow-up that is both unexplored and immediately testable.

---

## Research Question Development

### Initial Question

Does the difficulty composition of training problems (easy vs. hard competitive programming problems) in execution-feedback RL (GRPO) for code LLMs systematically affect pass@1 gains on existing function-level benchmarks (HumanEval+, MBPP+), and can curriculum ordering of problems by difficulty improve training efficiency?

### Refined Question

When applying GRPO with unit-test execution reward to open-weight code LLMs (DeepSeek-Coder-7B) trained on existing competitive programming datasets (APPS + CodeContests), does training on a difficulty-stratified curriculum (easy-first → hard-later ordering by APPS difficulty tiers) yield higher pass@1 on HumanEval+ and MBPP+ compared to training on uniform random sampling from the same dataset, and does the benefit of curriculum ordering interact with training compute budget (measured by gradient steps)?

### Detailed Sub-Questions

- **Q1 (Difficulty Composition Effect):** When training DeepSeek-Coder-7B with GRPO on existing APPS+CodeContests data, does a hard-problem-only training mix (APPS levels 3-4, CodeContests Div. 1) yield higher or lower pass@1 on HumanEval+ and MBPP+ compared to easy-problem-only (APPS levels 1-2, CodeContests Div. 2) and mixed uniform sampling, as measured on existing benchmarks?

- **Q2 (Curriculum Ordering):** Does easy-first curriculum ordering (start with APPS level 1-2, transition to level 3-4 within the same compute budget) outperform hard-first and random ordering in final pass@1 on HumanEval+ and MBPP+ when applied to GRPO training of DeepSeek-Coder-7B on existing APPS+CodeContests datasets?

- **Q3 (Reward Density Mediation):** Does the observed performance difference between difficulty compositions correlate with measurable reward density (fraction of non-degenerate GRPO steps, i.e., steps where at least one of G=8 completions passes a test), confirming that reward density — not problem semantic content — is the active mechanism?

- **Q4 (Generalization to Harder Benchmarks):** Does the curriculum ordering benefit observed on function-level benchmarks (HumanEval+, MBPP+) transfer to harder existing benchmarks (APPS test split, LiveCodeBench) without any architectural or algorithmic change?

- **Q5 (Compute Efficiency):** Does curriculum-ordered GRPO reach the same final HumanEval+ pass@1 as random-order GRPO in fewer gradient steps (measured on existing training infrastructure), indicating training efficiency gains from difficulty scheduling?

---

## Reference Papers

*No reference papers provided in input — will discover in Phase 1*

Key search targets for Phase 1:
- Curriculum learning for code generation (difficulty-based scheduling)
- GRPO/PPO training data composition effects for code LLMs
- APPS, CodeContests dataset difficulty tier analysis
- Reward density / non-degenerate step fraction in RL for code
- DeepSeek-Coder, CodeRL, RLEF training data analysis

---

## Validation Results

### So What Test

This research addresses a practical gap in the DL4C "Post-training and Alignment for Code" track: practitioners training code LLMs with execution-feedback RL (GRPO/PPO) must choose what problems to train on, but no systematic evidence exists on how difficulty composition affects benchmark gains. The finding directly guides dataset curation decisions for GRPO-based code LLM training — a high-value practical contribution. It builds on the confirmed H-E1 finding (execution-feedback GRPO works) to answer *why it works better in some configurations*, producing actionable guidance. All experiments use existing open datasets (APPS, CodeContests, HumanEval+, MBPP+) and open-weight models, satisfying open science requirements and the workshop's reproducibility emphasis.

### Feasibility Check

All sub-questions are testable immediately using existing resources:
- **Training Datasets:** APPS (difficulty tiers 0-4, ~5000 train problems), CodeContests (Div. 1/2 labels) — both publicly available with difficulty metadata
- **Eval Benchmarks:** HumanEval+ (164), MBPP+ (378), APPS test split, LiveCodeBench — all existing, execution-based, no human annotation needed
- **Model:** DeepSeek-Coder-7B-base (open weights, fits on single A100 80GB with gradient checkpointing)
- **Method:** GRPO via TRL GRPOTrainer (confirmed working in H-E1 validation) — no new framework needed
- **Difficulty Stratification:** APPS difficulty field (integers 0-4) and CodeContests division labels are already in the dataset metadata — no new labeling required
- **Metrics:** pass@1, pass@k — automated execution-based, no human raters
- **Constraint compliance:** No new benchmarks, no synthetic data, no human annotation — fully satisfied
- **Scope:** 4-5 training conditions (easy-only, hard-only, mixed, curriculum easy→hard, curriculum hard→easy) × 1-2 compute budgets; feasible as ablation on existing setup from H-E1

---

## Phase 1 Input Package

<phase1-input>

### research_question
When applying GRPO with unit-test execution reward to open-weight code LLMs (DeepSeek-Coder-7B) trained on existing competitive programming datasets (APPS + CodeContests), does training on a difficulty-stratified curriculum (easy-first → hard-later ordering by APPS difficulty tiers) yield higher pass@1 on HumanEval+ and MBPP+ compared to training on uniform random sampling from the same dataset, and does the benefit of curriculum ordering interact with training compute budget (measured by gradient steps)?

### detailed_question
1. When training DeepSeek-Coder-7B with GRPO on existing APPS+CodeContests data, does a hard-problem-only training mix (APPS levels 3-4) yield higher or lower pass@1 on HumanEval+ and MBPP+ compared to easy-problem-only (APPS levels 1-2) and mixed uniform sampling?
2. Does easy-first curriculum ordering outperform hard-first and random ordering in final pass@1 on HumanEval+ and MBPP+ at equal compute budget?
3. Does the performance difference between difficulty compositions correlate with reward density (fraction of non-degenerate GRPO steps where at least one of G=8 completions passes a test)?
4. Does the curriculum ordering benefit transfer to harder existing benchmarks (APPS test split, LiveCodeBench) without architectural change?
5. Does curriculum-ordered GRPO reach the same final HumanEval+ pass@1 as random-order GRPO in fewer gradient steps?

### reference_papers
*Not provided — will discover in Phase 1*

</phase1-input>

---

## Session Insights

### Key Discoveries

- H-E1 validation from previous run confirmed: GRPO with unit-test execution reward reliably improves function-level pass@1 for DeepSeek-Coder-7B. This is the bedrock finding to build on.
- H-M1 failure revealed a critical insight: GRPO reward density (fraction of non-degenerate training steps) is a key determinant of training effectiveness. When ~85% of steps are degenerate (all-zero reward), training effectively stalls.
- APPS difficulty tiers (0-4) and CodeContests division labels provide pre-existing difficulty metadata — no new annotation needed to stratify training data.
- Curriculum learning has strong theoretical backing (from general ML) and practical motivation (avoid degenerate steps early in training), but has not been systematically studied for execution-feedback RL on code.
- The pivot avoids all known failure modes: no repo-level GRPO training claims, no advantage variance predictions, no synthetic data, no new benchmarks.

### Techniques Used

ROUTE_TO_0 Mode (structured input extraction + failure-informed pivot from H-M1 failure analysis)

### Areas for Further Exploration

- Agentic methods: whether curriculum-ordered GRPO produces agents better at multi-step tool use (SWE-agent eval — as evaluation only, not training)
- Data for Code: interaction between difficulty composition and pretraining data (The Stack vs. StarCoderData)
- Reinforcement Learning for Code: whether reward shaping (partial credit for partial test pass) interacts with difficulty curriculum
- Pre-training Methods: does curriculum benefit depend on the base model's pretraining data distribution?
- Code Explanation / Summarization: whether alignment from execution feedback generalizes to understanding tasks (CodeXGLUE)

---

## Next Steps

Proceed to Phase 1 - Targeted Research

Use the Phase 1 Input Package above. Key search targets for Phase 1:
1. Curriculum learning for RL and LLM fine-tuning (difficulty scheduling literature)
2. GRPO / PPO training data composition for code LLMs (APPS, CodeContests difficulty analysis)
3. Reward density / degenerate-step analysis in execution-feedback RL for code
4. DeepSeek-Coder, StarCoder2 fine-tuning papers on competitive programming data
5. LiveCodeBench, APPS test split evaluation papers
6. Recent ICLR 2025 / NeurIPS 2024 papers on data curation for RL-based code training

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*
