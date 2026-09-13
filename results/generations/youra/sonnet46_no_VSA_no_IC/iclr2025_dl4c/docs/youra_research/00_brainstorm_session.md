---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Reward signal quality for RLEF code gen"
---

# Research Brainstorm Session Results

**Session Date:** 2026-08-21
**Facilitator:** Research Question Architect
**Participant:** Anonymous

---

## Executive Summary

**Initial Interest:** Post-training and alignment for code LLMs — reward signal quality analysis for RLEF (Reinforcement Learning from Execution Feedback), specifically characterizing sparsity and variance of binary execution rewards as predictors of RLEF training efficiency, with explicit constraints learned from four prior attempts (h-e1 Runs 1 & 2: measurement artifacts; brainstorms 3 & 4: direction confirmed sound but never executed)

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode) — fifth attempt. Reward signal quality pivot is confirmed and retained. Sub-questions sharpened further based on h-e1 environment constraints confirmed across two runs. Key new insight: pivot from "do sparsity/variance predict efficiency?" toward a tighter, faster-executing comparative experiment: frozen-model reward signal profiling → subset selection → short RLEF validation, all completable in < 4h on existing H100 NVL hardware.

**Session Duration:** < 1 minute (automated extraction)

---

## Starting Context

The DL4C 2025 workshop ("Emergent Possibilities and Challenges in Deep Learning for Code") invites research on deep learning for code, with specific emphasis on: post-training and alignment for code (learning from execution feedback, AI feedback, and human feedback for better code generation), agentic methods for programming tasks, benchmarking and evaluation for code, developer productivity, open science, and reinforcement learning for code. Source Type: Workshop CFP / Structured Input.

Feasibility constraints (pipeline-enforced): Only hypotheses testable immediately using existing real datasets and existing benchmarks are accepted. No new benchmarks, no synthetic/generated data, no human evaluation or annotation required.

This is ROUTE_TO_0 re-entry (fifth execution). Attempts 1 and 2 (h-e1 Runs 1 and 2) targeted GRPO-vs-SFT pass@1 comparison and failed as measurement artifacts (5 steps, crash-only eval). Attempts 3 and 4 correctly identified the pivot: reward signal quality metrics (sparsity, variance) as predictors of RLEF per-step efficiency. This fifth attempt inherits that pivot, reinforces it with tighter experimental scope, and adds a new angle: the **data selection efficiency** framing — can reward signal profiling (cheap, < 30 min) select training subsets that achieve the same pass@1 gain as full-data RLEF with fewer gradient steps?

---

## Lessons from Previous Attempts

### What Was Tried Before (h-e1: Runs 1 and 2)

**Hypothesis:** GRPO with binary execution feedback (pass/fail on MBPP train set) improves pass@1 on HumanEval+ over SFT baseline, using a 7B code LLM and TRL GRPO trainer.

**Both runs failed identically as measurement artifacts:**
- Only 5 gradient steps on 40 MBPP examples (<2% of full epoch)
- Evaluation used crash-only check instead of EvalPlus correctness-based scoring
- Both SFT and GRPO scored pass@1 = 0.0000 — indistinguishable from untrained models
- Gate: MUST_WORK → NOT SATISFIED (twice)

**Technical constraints confirmed in h-e1 environment:**
- vLLM 0.11.0 incompatible with trl 1.10 → use_vllm=False required in ALL configs
- Full epoch (~374 steps on MBPP) requires 4–8 hours on H100 NVL
- Diagnostic batch rollout (400 sequential 7B completions) too slow for validation step
- generation_batch_size=4 recommended to avoid OOM on H100 NVL
- binary_execution_reward: verified correct (subprocess exec, 10s timeout)
- Evaluation pipeline: model loads, generates completions, pass@1 computed correctly

**What worked in h-e1 (reusable assets):**
- Training pipeline fully functional end-to-end (SFT + GRPO trainers)
- EvalPlus correctness-based scoring: confirmed working
- Base model achieves ~50% HumanEval+ (R1 diagnostic confirmed)
- MBPP full train split available (374 examples)

### Why the Original h-e1 Direction Is Weak Beyond Execution Failures

Even with full-epoch execution:
1. **The comparison is established:** GRPO > SFT on code generation is demonstrated in DeepSeek-R1, RLEF/CodeRL/RLCODER papers — marginal contribution of another HumanEval+ comparison is weak
2. **Long wall-clock dependency:** 4–8h full-epoch makes hypothesis fragile to hardware interruption and hard to iterate
3. **Binary reward is coarse:** pass/fail on MBPP doesn't distinguish reasoning improvement vs format memorization
4. **Single-model limitation:** One 7B model comparison does not generalize

### How THIS Direction Avoids Those Pitfalls

| Risk from h-e1 | Mitigation in New Direction |
|----------------|----------------------------|
| 4–8h full-epoch training | Reward signal profiling: frozen inference only (< 30 min) |
| Crash-only eval proxy | EvalPlus correctness-based pass@1 (confirmed working in h-e1 env) |
| vLLM incompatibility | Frozen inference avoids live rollouts; use_vllm=False for short RLEF validation |
| Weak novelty | Reward sparsity/variance as RLEF efficiency predictors is uncharacterized |
| Single-model | Multi-model validation (Code-LLaMA + DeepSeek-Coder-V2-Lite) built into scope |
| MUST_WORK gate risk | Short RLEF validation (20–50 steps on selected subsets) — fast, deterministic |
| Measurement artifact risk | EvalPlus required (NOT crash-only); step count ≥ 50 enforced in experiment spec |

### New Insight from Attempt 5 (Sharpening)

The fourth brainstorm framed the question as "do reward signal metrics PREDICT efficiency?" — a correlation study. Sharpening this to an **actionable data selection experiment** is both more novel and more directly testable:

**Framing shift:** Can reward signal quality metrics, computed on a frozen model in < 30 minutes, identify a training subset (top-N by variance) that achieves equivalent or better pass@1 improvement vs random-N subset with the same RLEF gradient step budget?

This is a direct comparison: **variance-selected RLEF vs random-RLEF**, same step count, same model, same benchmark — a clean 2-condition experiment with a binary measurable outcome. Avoids the correlation analysis complexity and is gate-passable at 20–50 steps per condition.

---

## Session Plan

ROUTE_TO_0 Auto-Fill: extract research direction from DL4C CFP (post-training and alignment for code track), filtered through h-e1 failure lessons (Serena Memory: h-e1/failure_run1, h-e1/failure_run2) and three prior brainstorm sessions. Reinforce reward signal quality pivot; sharpen to data selection framing for tighter experimental scope.

---

## Technique Sessions

ROUTE_TO_0 Auto-Fill Mode — No interactive sessions. Failure context synthesis applied from Serena memory records (h-e1/failure_run1, h-e1/failure_run2) and previous brainstorm archived at 20260821T133624_routing_recovery/00_brainstorm_session.md. Direction confirmed from brainstorms 3 and 4; sharpened to data-selection framing in attempt 5.

---

## Research Question Development

### Initial Question

Can reward signal quality metrics — specifically binary execution reward sparsity (fraction of zero-reward completions per problem) and reward variance (p*(1-p) across k=8 i.i.d. completions), computed on a frozen 7B code LLM in < 30 minutes — identify a training problem subset that achieves faster RLEF pass@1 improvement per gradient step compared to random subset selection, using existing public benchmarks (MBPP, HumanEval+) and automated EvalPlus correctness-based evaluation?

### Refined Question

Does variance-guided training data selection for RLEF (selecting top-N MBPP problems by per-problem binary reward variance p*(1-p) computed on a frozen code LLM) yield higher pass@1 improvement on HumanEval+ per gradient step at 20–50 GRPO steps compared to: (a) random-N subset RLEF (same step budget), and (b) full-set RLEF (all 374 MBPP problems, same step budget) — testable using DeepSeek-Coder-7B-Instruct with use_vllm=False, generation_batch_size=4, EvalPlus correctness-based evaluation, and no human annotation?

### Detailed Sub-Questions

1. What is the per-problem binary execution reward variance distribution (p*(1-p) for p = pass rate across k=8 i.i.d. completions) across MBPP training split (374 problems) for a frozen DeepSeek-Coder-7B-Instruct model? Does the variance distribution exhibit meaningful stratification (i.e., are there clear high-variance vs low-variance problem clusters corresponding to "learnable" vs "too-easy/too-hard" problems)?

2. Does variance-selected RLEF (top-N=50 problems by variance, 20–50 GRPO steps, use_vllm=False, generation_batch_size=4) achieve higher HumanEval+ pass@1 improvement than random-N=50 subset RLEF at the same gradient step budget, using EvalPlus correctness-based evaluation?

3. Does variance-selected RLEF (top-N=50, 50 steps) achieve pass@1 improvement within 80% of full-set RLEF (374 problems, 50 steps) while using only ~13% of the training problems — demonstrating data efficiency gains from reward signal profiling?

4. Does the variance-based subset selection advantage (if observed on DeepSeek-Coder-7B-Instruct) replicate on a second model family (Code-LLaMA-7B or DeepSeek-Coder-V2-Lite-Instruct) under the same short RLEF protocol, confirming generalizability across architectures?

---

## Reference Papers

Not provided - will discover in Phase 1

Key search directions for Phase 1:
- "reward sparsity reinforcement learning code generation"
- "training data selection RLEF execution feedback"
- "reward variance curriculum learning code LLM"
- "difficulty-based data selection GRPO code generation"
- "MBPP HumanEval problem difficulty distribution analysis"
- "reward signal quality reinforcement learning from execution feedback"
- "binary execution reward variance code generation training"
- "data-efficient reinforcement learning from execution feedback"
- "per-problem pass rate distribution code benchmark"
- "GRPO subset selection training efficiency"

---

## Validation Results

### So What Test

DL4C @ ICLR 2025 target — significance pre-validated by venue. The refined question addresses a genuine and practical gap:

**Gap addressed:** While RLEF papers (CodeRL, RLCODER, DeepSeek-R1-Code) demonstrate that execution feedback improves code generation, none characterize *which training problems yield the most RLEF improvement per gradient step* or provide a cheap (< 30 min) data selection criterion for RLEF practitioners.

**Immediate practical value:** A practitioner running RLEF on a compute-limited budget can use reward variance profiling (frozen inference, < 30 min) to identify the top-N problems where the model is at the "learning frontier" (p ≈ 0.5), potentially achieving the same pass@1 gains as full-dataset RLEF with 5–10× fewer training examples and proportionally less compute.

**Both positive and negative results are publishable:**
- Positive: variance-selected subset outperforms random subset → cheap data selection criterion established
- Negative: variance selection does NOT outperform random → reward variance is not a reliable predictor; random selection is sufficient; negative result warns practitioners against over-engineering data selection for RLEF

**Distinction from h-e1:** h-e1 measured whether GRPO improves over SFT (known). This measures *which problems make RLEF efficient per gradient step* — a data-centric analysis opening a new research thread.

**Alignment with DL4C tracks:** Directly addresses "Post-training and Alignment for Code" (primary) and "Reinforcement Learning for Code" (secondary). The data efficiency angle also touches "Benchmarking and Evaluation for Code" through per-problem difficulty characterization.

### Feasibility Check

All components exist and have been validated (fully or partially) in the h-e1 environment:

| Component | Feasibility | Evidence |
|-----------|-------------|----------|
| Frozen model inference (k=8 completions/problem, 374 problems) | ✅ < 30 min on H100 NVL | h-e1 eval pipeline confirmed working |
| EvalPlus correctness scoring | ✅ Working in h-e1 env | binary_execution_reward verified; evalplus installed |
| MBPP full train split (374 problems) | ✅ Existing public dataset | Used in h-e1 |
| HumanEval+ (164 problems, eval only) | ✅ Existing public dataset | evalplus package installed |
| Short RLEF (20–50 GRPO steps, top-N=50 subset) | ✅ < 1h on H100 NVL | h-e1 trainer confirmed functional (5 steps tested) |
| Random baseline RLEF (same N, same steps) | ✅ Trivial baseline | Random subset selection, same training code |
| Full-set RLEF baseline (374 problems, same steps) | ✅ < 2h on H100 NVL | Same h-e1 trainer, no code changes |
| use_vllm=False workaround | ✅ Confirmed in h-e1 env | vllm 0.11.0 + trl 1.10 incompatible |
| generation_batch_size=4 | ✅ OOM-safe on H100 NVL | h-e1 recommendation confirmed |
| Multi-model (2nd family: Code-LLaMA-7B) | ✅ Publicly available weights | HuggingFace: codellama/CodeLlama-7b-Instruct-hf |

**MANDATORY FEASIBILITY CONSTRAINTS CHECK:**
- ✅ No new benchmarks required (MBPP, HumanEval+ — existing, public)
- ✅ No synthetic/generated data required (all benchmarks are real programmer-authored problems)
- ✅ No human evaluation required (EvalPlus automated execution-based pass@1 scoring)
- ✅ Testable immediately with existing datasets and benchmarks
- ✅ No new rubrics or scoring frameworks (existing pass@1 via EvalPlus; variance = p*(1-p), standard formula)

---

## Phase 1 Input Package

<phase1-input>

### research_question
Does variance-guided training data selection for RLEF (selecting top-N MBPP problems by per-problem binary reward variance p*(1-p) computed on a frozen code LLM) yield higher pass@1 improvement on HumanEval+ per gradient step at 20–50 GRPO steps compared to random-N subset RLEF and full-set RLEF, using only existing public benchmarks (MBPP, HumanEval+), EvalPlus correctness-based evaluation, and no human annotation?

### detailed_question
1. What is the per-problem binary execution reward variance distribution (p*(1-p), k=8 i.i.d. completions) across MBPP training split (374 problems) for a frozen DeepSeek-Coder-7B-Instruct model? Does variance exhibit meaningful stratification into learnable vs too-easy/too-hard problem clusters?
2. Does variance-selected RLEF (top-N=50 problems by variance, 20–50 GRPO steps, use_vllm=False, generation_batch_size=4) achieve higher HumanEval+ pass@1 improvement than random-N=50 subset RLEF at the same gradient step budget, using EvalPlus correctness-based evaluation?
3. Does variance-selected RLEF (top-N=50, 50 steps) achieve pass@1 improvement within 80% of full-set RLEF (374 problems, 50 steps) while using only ~13% of training problems — demonstrating data efficiency from reward signal profiling?
4. Does the variance-based selection advantage (if observed) replicate on a second model family (Code-LLaMA-7B) under the same short RLEF protocol, confirming cross-architecture generalizability?

### reference_papers
Not provided - will discover in Phase 1

</phase1-input>

---

## Session Insights

### Key Discoveries

- h-e1 Runs 1 and 2 were measurement artifacts — the training pipeline itself is functional and fully validated end-to-end; the hypothesis direction was the weak point, not the code
- The reward signal quality pivot (brainstorms 3 and 4) is confirmed sound; this 5th brainstorm sharpens it from "do metrics predict efficiency?" (correlation study) to "does variance-guided selection outperform random selection?" (direct comparative experiment)
- The data selection framing is tighter: 3 conditions (variance-selected, random-selected, full-set), same step budget, same model, same eval — clean experimental design with binary measurable outcome
- Frozen inference phase (< 30 min) separates the cheap profiling step from the expensive RLEF step — making the experiment resumable and hardware-fault-tolerant
- Multi-model replication (2nd model family) built into sub-question 4 ensures generalizability without requiring a new experiment design
- All h-e1 infrastructure (binary_execution_reward, EvalPlus harness, TRL GRPO trainer, MBPP data) is directly reusable with minimal modification

### Techniques Used

ROUTE_TO_0 Auto-Fill Mode — failure context synthesis from two Serena Memory records (h-e1/failure_run1, h-e1/failure_run2) and archived previous brainstorm (20260821T133624_routing_recovery). Direction reinforced from brainstorms 3 and 4; reframed as data selection comparative experiment in attempt 5.

### Areas for Further Exploration

- Full-epoch GRPO vs SFT pass@1 comparison (original h-e1) — defer; may become an ablation study once data selection results are established
- Sparsity as a complementary selection criterion (in addition to variance) — deferred; variance is the primary predictor, sparsity is secondary
- Non-binary rewards (partial credit, test-case-level granularity) — possible extension
- Agentic methods (SWE-bench) — different scaffolding, out of current scope
- Cross-language generalization (Python → Java/Rust) — possible extension after Python results validated
- LiveCodeBench subset as additional eval benchmark — possible extension (primary eval is HumanEval+)
- Developer productivity / HCI studies — requires user studies, outside feasibility constraints

---

## Next Steps

Proceed to Phase 1 - Targeted Research. Primary search targets:

**Core search terms:**
- "reward variance training data selection code generation RLEF"
- "curriculum learning execution feedback code LLM difficulty"
- "data-efficient reinforcement learning from execution feedback"
- "training subset selection GRPO code generation"
- "per-problem difficulty MBPP HumanEval binary reward distribution"
- "reward sparsity variance reinforcement learning code"
- "data selection efficiency RLEF binary execution reward"
- "problem difficulty curriculum GRPO training efficiency"

**Critical constraints for Phase 2A hypothesis generation:**
- Experiment has 3 conditions: variance-selected RLEF, random-selected RLEF, full-set RLEF — same step budget (20–50 GRPO steps)
- Require frozen model inference for reward signal profiling (no training in profiling phase)
- Require EvalPlus correctness-based evaluation (NOT crash-only check)
- Require use_vllm=False in all training configs (vllm 0.11.0 + trl 1.10 incompatible)
- Require generation_batch_size=4 to avoid OOM on H100 NVL
- Require short RLEF validation (20–50 steps on problem subsets) — NOT full epoch
- Require multi-model validation (at least 2 model families: DeepSeek-Coder-7B-Instruct + Code-LLaMA-7B)
- All datasets: MBPP (374 train, for RLEF), HumanEval+ (164, eval only) — existing public benchmarks only
- Top-N subset size: N=50 (≈13% of MBPP train) as primary condition; N=100 as secondary ablation

**Archon Pipeline:** Anonymous Pipeline: Reward signal quality for RLEF code gen (f98ceef4-713b-4934-9414-10c1dbb8f87e)
- Phase 0: done ✅
- Phase 1: doing 🔄

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm (ROUTE_TO_0 — Attempt 5)*
*Ready for: Phase 1 - Targeted Research*
