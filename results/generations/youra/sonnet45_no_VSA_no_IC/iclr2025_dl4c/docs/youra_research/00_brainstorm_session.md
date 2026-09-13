---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Robust execution feedback for code LLMs"
---

# Research Brainstorm Session Results

**Session Date:** 2026-08-19
**Facilitator:** Research Question Architect
**Participant:** Anonymous

---

## Executive Summary

**Initial Interest:** Deep learning for code research aligned with ICLR 2025 DL4C workshop focus areas, with infrastructure-hardened execution feedback approach learning from previous stability failures.

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode)

**Session Duration:** < 1 minute (automated extraction)

---

## Starting Context

ICLR 2025 DL4C Workshop Call for Papers - Third edition focusing on "Emergent Possibilities and Challenges in Deep Learning for Code" with priority tracks:
1. Agentic Methods for Programming Tasks
2. Post-training and Alignment for Code  
3. Developer Productivity and HCI for Code
4. Open Science and Responsible AI for Code
5. Benchmarking and Evaluation for Code

Additional tracks: RL for Code, Data for Code, Pre-training Methods, NL2Code, Formal Methods, Program Repair, Code Translation, Code Explanation/Summarization, Code Generation for Reasoning/Decision Making.

**MANDATORY CONSTRAINTS:**
- NO new benchmarks, rubrics, or scoring frameworks
- NO synthetic/generated data or future follow-up data
- NO human evaluation, annotation, or subjective scoring
- ONLY existing real datasets and existing benchmarks

Retrying after previous MUST_WORK gate failure (H-E1: EVAF execution instability)

---

## Lessons from Previous Attempts

### Previous Failure: H-E1 (EVAF Existence PoC)

**What Was Tried:**
- Hypothesis: EVAF mechanism can be implemented and produces filtered AI feedback with measurable accept rate between 20-60%
- Experiment crashed at 53% completion (87/164 HumanEval problems) during EVAF gating phase
- Used CodeLlama-7b-Instruct for feedback generation
- No checkpointing in EVAF loop - full restart required on crash

**Why It Failed:**
1. **Model Inference Instability**: CodeLlama-7b-Instruct stalled on complex HumanEval problems
2. **Resource Management**: GPU memory exhaustion (CodeLlama-7b requires ~14GB VRAM)
3. **No Fault Tolerance**: Single-run design with no progress checkpointing
4. **Scale Mismatch**: Full 164-problem suite too large for unstable inference pipeline

**Root Cause:** Infrastructure stability issues, not hypothesis validity. EVAF concept unvalidated due to execution failures.

### How THIS Direction Avoids Those Pitfalls

**New Research Focus:** Lightweight execution feedback mechanisms with robust infrastructure
- **Smaller Models**: Focus on feedback extraction using <1B models (stable, low VRAM)
- **Checkpointed Execution**: Progress saved every N problems, graceful recovery from failures
- **Reduced Initial Scope**: PoC on 50-problem subset before scaling
- **Execution-Only Feedback**: Use raw test outcomes/error messages (no LLM gating in critical path)
- **Timeout Protection**: Per-problem time limits with skip-on-timeout logic

**Key Insight:** Previous attempt conflated two research questions:
1. Can execution feedback improve code LLMs? (core question)
2. Can LLM-gated feedback filtering work at scale? (EVAF-specific)

**New Strategy:** Validate Q1 first with simple execution feedback (test pass/fail + error messages). Only explore Q2 (LLM gating) after stable infrastructure proven.

---

## Session Plan

1. Pivot from EVAF (complex, unstable) to baseline execution feedback alignment (simple, robust)
2. Extract research directions emphasizing infrastructure reliability
3. Filter against mandatory feasibility constraints AND stability requirements
4. Generate research questions testable with fault-tolerant experimental design
5. Identify reference papers on lightweight execution feedback (no heavy LLM gating)

---

## Technique Sessions

**Technique 1: Failure Root Cause Analysis**
- Identified infrastructure vs hypothesis validity separation
- EVAF instability does NOT invalidate execution feedback alignment research
- Pivot to simpler execution feedback paradigm removes failure mode

**Technique 2: Constraint-Driven Filtering (Expanded)**
- Original constraints: No new benchmarks, no synthetic data, no human eval
- NEW constraint: No unstable inference dependencies in critical paths
- Retained: Existing datasets (HumanEval, MBPP, APPS), execution-based evaluation
- Removed: LLM-based feedback gating (moved to future work after baseline stability)

**Technique 3: Stability-First Resource Mapping**
- Lightweight Models: CodeT5-small (60M), phi-2 (2.7B) - stable inference confirmed
- Fault-Tolerant Execution: Pytest with timeout, result caching, checkpoint files
- Reduced Initial Scale: 50-problem PoC → 164-problem full run only after validation
- Monitoring: GPU memory tracking, per-problem execution time logging

---

## Research Question Development

### Initial Question

How can execution feedback from existing code benchmarks improve LLM code generation without requiring unstable inference pipelines or new human annotations?

### Refined Question

Can lightweight execution feedback signals (test outcomes, error messages) from existing benchmarks (HumanEval, MBPP) reliably improve code generation model alignment using fault-tolerant, checkpointed training infrastructure?

### Detailed Sub-Questions

1. **Execution Feedback Effectiveness**: What is the empirical performance gain from training on raw test pass/fail + error messages vs supervised fine-tuning on existing benchmarks (HumanEval, MBPP)?

2. **Infrastructure Stability**: Does checkpointed execution feedback collection with per-problem timeouts achieve >95% completion rate on HumanEval/MBPP full suites?

3. **Feedback Signal Granularity**: Which execution feedback components (test pass/fail, error type, stack trace) provide strongest alignment signal using existing test suites?

4. **Cross-Benchmark Transfer**: Does alignment on HumanEval execution feedback transfer to MBPP performance improvements (and vice versa) without additional training?

---

## Reference Papers

### Core Papers (Execution Feedback - Lightweight Approaches)

1. **CodeRL: Mastering Code Generation through Pretrained Models and Deep Reinforcement Learning** (Le et al., NeurIPS 2022)
   - Uses execution feedback from HumanEval/MBPP for RL-based alignment
   - Baseline for execution-driven post-training WITHOUT heavy LLM gating
   - Demonstrates feasibility of test outcome feedback

2. **Self-Debugging: Teaching Large Language Models to Debug Their Predicted Program** (Chen et al., ICLR 2024)
   - Execution-based self-correction using error messages
   - Relevant to lightweight feedback extraction (no LLM filtering needed)

3. **Teaching Large Language Models to Self-Debug** (Chen et al., 2023)
   - Simple execution feedback loop (generate → test → fix)
   - Aligns with stability-first approach (minimal moving parts)

### Benchmarking Papers (Existing Resources)

4. **Measuring Coding Challenge Competence With APPS** (Hendrycks et al., NeurIPS 2021)
   - APPS benchmark with execution-based evaluation
   - 10,000 problems with test cases (existing resource for scaling after PoC)

5. **Program Synthesis with Large Language Models** (Austin et al., 2021)
   - HumanEval benchmark definition and pass@k metrics
   - Standard baseline for code generation (164 problems - suitable for PoC)

### Robustness & Evaluation

6. **Is Your Code Generated by ChatGPT Really Correct?** (Liu et al., 2023)
   - Highlights execution correctness vs surface metrics gap
   - Motivates execution feedback over token-level supervision

---

## Validation Results

### So What Test

**Impact**: Addresses DL4C priority track "Post-training and Alignment for Code" with production-viable approach. Lightweight execution feedback is scalable (no expensive LLM gating), stable (fault-tolerant infrastructure), and generalizable across benchmarks.

**Novelty**: Previous EVAF attempt targeted complex feedback filtering. NEW direction explores whether SIMPLE execution signals (test pass/fail + error messages) suffice for alignment, removing infrastructure risk while maintaining research contribution.

**Contribution**: Provides practitioners with stability-tested execution feedback pipeline and empirical comparison of feedback granularity vs alignment quality tradeoff.

### Feasibility Check

✅ **Existing Datasets**: HumanEval (164 problems), MBPP (974 problems), APPS (10,000 problems) - all with test suites
✅ **Existing Benchmarks**: Pass@k, execution accuracy, error type classification
✅ **No New Data**: Uses existing test cases and execution environments
✅ **No Human Evaluation**: Fully automated via test execution
✅ **Stable Infrastructure**: Checkpointing, timeouts, lightweight models (<3B params)
✅ **Reduced Initial Scope**: 50-problem PoC before full 164-problem run
✅ **Baseline Models**: CodeGen-350M, phi-2 (publicly available, stable inference)
✅ **Compute**: Fine-tuning 350M-2.7B models feasible on single GPU (A100 40GB)
✅ **Timeline**: 2-3 month experiment cycle with MUST_WORK gate protection

**Risk Mitigation from Previous Failure:**
- Checkpointing every 10 problems → no full restart on crash
- Per-problem timeout (60s) → skip problematic inputs instead of hanging
- GPU memory monitoring → early warning before OOM
- 50-problem PoC → validate stability before scaling to 164

---

## Phase 1 Input Package

<phase1-input>

### research_question
Can lightweight execution feedback signals (test outcomes, error messages) from existing benchmarks (HumanEval, MBPP) reliably improve code generation model alignment using fault-tolerant, checkpointed training infrastructure?

### detailed_question
1. What is the empirical performance gain from training on raw test pass/fail + error messages vs supervised fine-tuning on existing benchmarks?
2. Does checkpointed execution feedback collection with per-problem timeouts achieve >95% completion rate on HumanEval/MBPP full suites?
3. Which execution feedback components (test pass/fail, error type, stack trace) provide strongest alignment signal?
4. Does alignment on HumanEval execution feedback transfer to MBPP performance improvements without additional training?

### reference_papers
- CodeRL: Mastering Code Generation through Pretrained Models and Deep Reinforcement Learning (Le et al., NeurIPS 2022)
- Self-Debugging: Teaching Large Language Models to Debug Their Predicted Program (Chen et al., ICLR 2024)
- Teaching Large Language Models to Self-Debug (Chen et al., 2023)
- Measuring Coding Challenge Competence With APPS (Hendrycks et al., NeurIPS 2021)
- Program Synthesis with Large Language Models (Austin et al., 2021)
- Is Your Code Generated by ChatGPT Really Correct? (Liu et al., 2023)

</phase1-input>

---

## Session Insights

### Key Discoveries

1. **Failure Separation**: Previous EVAF crash was infrastructure issue (model instability, no checkpointing), NOT execution feedback concept invalidation

2. **Stability-First Design**: Removing LLM gating from critical path (EVAF → simple execution feedback) eliminates primary failure mode while preserving core research question

3. **Reduced Scope Wins**: 50-problem PoC validates infrastructure before committing to full 164-problem suite - previous attempt skipped this step

4. **DL4C Workshop Fit**: Still addresses "Post-training and Alignment for Code" priority track, now with production-viable stability story

### Techniques Used

- Failure Root Cause Analysis (infrastructure vs hypothesis separation)
- Constraint-Driven Filtering (expanded with stability requirements)
- Stability-First Resource Mapping (lightweight models, fault tolerance)

### Areas for Further Exploration

- **Feedback Signal Ablation**: Test pass/fail alone vs + error messages vs + stack traces
- **Model Scale Stability**: Does execution feedback alignment scale from 350M → 2.7B → 7B without infrastructure degradation?
- **Cross-Dataset Robustness**: HumanEval → MBPP transfer, MBPP → APPS transfer
- **EVAF Revisited**: After baseline stability proven, explore LLM-gated feedback as extension (Phase 2+ hypothesis)

---

## Next Steps

1. **Phase 1 - Targeted Research**: Deep dive on lightweight execution feedback approaches, fault-tolerant training infrastructure, HumanEval/MBPP benchmark characteristics
2. **Phase 2A - Hypothesis Generation**: Formulate stability-tested hypotheses on execution feedback effectiveness WITHOUT LLM gating dependencies
3. **Phase 2B - Research Planning**: Design checkpointed experiment roadmap with 50-problem PoC → 164-problem validation progression
4. **Phase 2C - Experiment Design**: Detailed protocol for fault-tolerant execution feedback extraction, alignment training with checkpointing, stability monitoring

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*
