---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Post-training for Code LLMs via SFT Data Selection"
---

# Research Brainstorm Session Results

**Session Date:** 2026-08-02
**Facilitator:** Research Question Architect
**Participant:** Anonymous

---

## Executive Summary

**Initial Interest:** Training data selection and mix effects on code LLM SFT performance — a data-centric angle avoiding all previous RL and gradient-variance failure modes (4th attempt, ROUTE_TO_0)

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode — 4th attempt)

**Session Duration:** < 1 minute (automated extraction)

---

## Starting Context

The DL4C workshop (ICLR 2025) "Emergent Possibilities and Challenges in Deep Learning for Code" invites research on post-training and alignment for code, data for code, pre-training methods and representation, and benchmarking/evaluation. Previous three attempts targeted: (1) RL-based post-training with fractional reward (EvalPlus binary-only failure), (2) GRPO binary reward (degenerate rollouts from p_eff mismatch), (3) Curriculum SFT via gradient-variance signal (gradient clipping + accumulation eliminated signal; Mann-Whitney underpowered; 1.3B model shows no detectable variance reduction).

This fourth attempt pivots to **training data selection and mix composition effects** on code SFT — specifically, how the *proportion and source diversity* of training samples from existing code datasets affects pass@1 on standard benchmarks. No RL, no gradient-variance measurement, no curriculum ordering — purely a data mixture study measurable via standard binary execution-based evaluation.

Source Type: Workshop CFP / Structured Input (ROUTE_TO_0 — 4th attempt)

**Feasibility Constraints (Pipeline-Enforced):**
- ✅ Only existing real datasets and benchmarks permitted
- ❌ No new benchmarks, rubrics, or scoring frameworks
- ❌ No synthetic/generated data or future data
- ❌ No human evaluation or annotation

---

## Lessons from Previous Attempts

### Attempt 1 (Run 1 — 2026-08-02T08:00) — EvalPlus Fractional Reward
**What was tried:** RLEF/execution-feedback post-training comparison (RLEF vs RFT vs DPO using EvalPlus as reward signal with fractional/partial credit).

**Why it failed:** EvalPlus returns binary pass/fail per test case only. Fractional averaging of binary signals has zero variance when model scores 0 on all prompts. t-stat = NaN.

### Attempt 2 (Run 2 — 2026-08-02T10:12) — GRPO Binary Reward
**What was tried:** GRPO (binary execution reward) vs DPO vs RFT, explicitly scoped to binary reward. Used DeepSeek-Coder-7B on HumanEval+MBPP training pool.

**Why it failed (h-e1, Phase 4 MUST_WORK gate):** MBPP+ mixed into training pool made p_eff ≈ 0.12 (not 0.39 as assumed from HumanEval-only). At p_eff = 0.12, K=8: P(all-fail) = 0.88^8 ≈ 0.35 → 55% degenerate groups (threshold <30%). Reward variance = 0 universally.

### Attempt 3 (Run 3 — 2026-08-02T12:29) — Curriculum SFT via Gradient Variance
**What was tried:** Easy-to-hard curriculum SFT ordering for 1.3B model on LeetCodeDataset. Measured inter-batch gradient norm variance in early training (first 20% steps) via Mann-Whitney test.

**Why it failed (h-m1, Phase 4 MUST_WORK gate):**
- SFTTrainer gradient clipping (default) compresses norm differences between easy/hard examples — curriculum signal eliminated before measurement
- gradient_accumulation_steps=4 averages 4 micro-batches per optimizer step, reducing per-step variance regardless of ordering
- 33 early steps (20% of 1-epoch run) insufficient for Mann-Whitney statistical power (n_significant_seeds = 0/3; best p = 0.159)
- 1.3B model produces homogeneous gradient norms across LeetCode difficulty levels — ordering has negligible per-step variance impact

**What showed promise from Attempt 3:**
- h-e1 (prerequisite snapshot) PASSED: 1.3B model has 1.672× higher gradient magnitude on Easy problems than 6.7B (p=6.48e-14) — the capability-complexity differential is real
- Code infrastructure (data loading, SFT training loop, statistical testing) is reusable
- LeetCodeDataset deduplication pipeline (all-MiniLM-L6-v2, cosine sim > 0.95 vs HumanEval+ and MBPP+) validated and working

### How This New Direction Avoids All Previous Pitfalls

| Previous Failure Mode | This Direction's Mitigation |
|----------------------|-----------------------------|
| Fractional reward assumption (EvalPlus binary only) | No RL training — binary pass@1 used only for evaluation, not training signal |
| GRPO degenerate rollouts (p_eff << assumed) | No rollout-based training — pure SFT, model capability during training irrelevant |
| Gradient clipping eliminates curriculum variance signal | No gradient-variance measurement — outcome metric is final pass@1 only |
| gradient_accumulation averages per-step variance | No per-step gradient measurement at all |
| Mann-Whitney underpowered on 33 early steps | Final-checkpoint evaluation — no early-training statistical test required |
| 1.3B model gradient homogeneity across difficulty levels | Effect measured at final benchmark performance level, not gradient level |

**Core insight:** All three prior failure modes were measurement failures, not conceptual failures. Gradient-variance and reward-variance are fragile proxies. The cleanest measurement is final pass@1 on existing benchmarks after SFT — binary, well-defined, no capability-during-training dependency. The research question becomes: **does training data source composition (which existing datasets, in what proportion) affect final pass@1?**

---

## Session Plan

ROUTE_TO_0 auto-extraction — 4th attempt. Pivoted from curriculum gradient-variance (h-m1 FAIL) to training data mix/source composition effects on code SFT, measurable purely via binary pass@1 on existing benchmarks.

---

## Technique Sessions

ROUTE_TO_0 Mode — Automated failure-informed extraction. No interactive sessions.

---

## Research Question Development

### Initial Question

Does the composition of training data sources (which existing code datasets and in what proportions) affect pass@1 performance of code LLMs fine-tuned with SFT on standard execution-based benchmarks?

### Refined Question

When fine-tuning a code LLM (e.g., DeepSeek-Coder-1.3B/7B-Base) with SFT using only existing public code datasets (HumanEval training problems, MBPP training split, LeetCodeDataset, CodeContests), does varying the training data **source mix** — specifically the proportion of problem-solution pairs from each source dataset — produce statistically significant differences in pass@1 on held-out HumanEval and MBPP test sets, when all training uses identical hyperparameters, identical random ordering, and evaluation uses only existing execution-based benchmarks?

### Detailed Sub-Questions

1. **Source proportion effect:** Holding total training set size fixed, does training on HumanEval-only vs MBPP-only vs LeetCode-only vs an equal mix of all three produce significantly different pass@1 on held-out HumanEval and MBPP test sets for DeepSeek-Coder-1.3B-Base?
2. **Cross-benchmark transfer:** Does a model trained on HumanEval-style problems (short, algorithmic) transfer better to MBPP test set than a model trained on LeetCode problems (longer, interview-style), when evaluated on existing benchmarks only?
3. **Training set size sensitivity:** Within each source (e.g., MBPP training split), does doubling the number of training samples produce diminishing returns on pass@1 — is there a saturation point identifiable from existing dataset sizes?
4. **Model size interaction:** Does the source mix effect replicate across model sizes (1.3B vs 7B DeepSeek-Coder), i.e., does a larger model exhibit the same cross-benchmark transfer pattern as a smaller model under the same data mix?
5. **Deduplication impact:** Does deduplicating training data against test benchmarks (removing near-duplicates of HumanEval/MBPP test problems using cosine similarity ≥ 0.95, as validated in previous runs) change the source mix ranking — specifically, does deduplication disproportionately shrink one source over another, altering relative pass@1 outcomes?

---

## Reference Papers

Not provided - will discover in Phase 1

---

## Validation Results

### So What Test

**Significance:** Every practitioner fine-tuning a code LLM must choose which datasets to train on and in what proportion. Yet the empirical effect of training data source composition on benchmark pass@1 is not systematically documented for the current generation of code LLMs (DeepSeek-Coder, CodeLlama). DL4C's "Data for Code" and "Post-training and Alignment for Code" tracks directly cover this gap.

**Novelty angle:** While data mixture research exists for general LLMs (DoReMi, DOREMI, Data Selection for LLMs), its application to code-specific SFT with execution-based evaluation on standard code benchmarks is not yet documented. The code domain has unique properties: problem-solution pairs, benchmark contamination risk, and difficulty heterogeneity across sources. This study isolates source composition as the independent variable, using the validated deduplication pipeline from previous runs.

**Workshop fit:** DL4C 2025 specifically welcomes "Data for Code" submissions. A clean ablation study (N data sources × M mix proportions × 2 model sizes × 3 existing benchmarks) with strong execution-based evaluation fits the workshop profile exactly.

**Distinction from previous attempts:** Not a training method comparison (no RL). Not a data ordering study (no curriculum). Purely about *which data* and *how much from each source* — the most fundamental data-centric question.

**Avoids all previous pitfalls:**
- No reward variance requirement
- No gradient measurement
- No RL training loop
- No model capability dependency during training
- No partial credit assumption

### Feasibility Check

**Green — all components available immediately:**

| Component | Source | Status |
|-----------|--------|--------|
| Training data sources | HumanEval (164 problems + solutions), MBPP training split (374 problems), LeetCodeDataset (newfacade/LeetCodeDataset, ~10K problems), CodeContests (deepmind/code_contests) | Existing, public HuggingFace |
| Deduplication pipeline | all-MiniLM-L6-v2 cosine sim > 0.95 vs HumanEval+ and MBPP+ | Validated in previous runs, reusable |
| Base models | DeepSeek-Coder-1.3B-Base, DeepSeek-Coder-7B-Base (HuggingFace) | Existing, public |
| SFT framework | HuggingFace Trainer / trl SFTTrainer | Open-source, validated in previous runs |
| Evaluation | HumanEval pass@1 (164 problems), MBPP pass@1 (374 problems), HumanEval+ (EvalPlus) | Existing, execution-based, binary |
| Statistical test | Paired t-test or ANOVA over multiple seeds; final-checkpoint evaluation (no early-training required) | Standard, well-powered at dataset scale |
| Hardware | 5× H100 NVL (available from previous runs) | Available |
| No human annotation | All difficulty info and evaluation from existing metadata/benchmarks | Feasibility constraint satisfied |
| No new benchmarks | All evaluation on existing test suites | Feasibility constraint satisfied |

**No failure modes from previous attempts:**
- SFT with fixed random ordering is deterministic — no stochastic rollout collapse
- Pass@1 on held-out benchmarks is well-defined at any model capability level
- Binary execution-based evaluation: pass/fail per problem — no partial credit assumption
- No gradient measurement required — no clipping/accumulation sensitivity
- Final-checkpoint evaluation — no statistical power constraint from early training steps

---

## Phase 1 Input Package

<phase1-input>

### research_question
When fine-tuning a code LLM (DeepSeek-Coder-1.3B/7B-Base) with SFT on existing public code datasets (HumanEval training problems, MBPP training split, LeetCodeDataset, CodeContests), does varying the training data **source mix proportion** produce statistically significant differences in pass@1 on held-out HumanEval and MBPP test sets — using only existing execution-based benchmarks, no RL, no gradient-variance measurement, no human annotation, and no new benchmark construction?

### detailed_question
1. Holding total training size fixed, does source composition (HumanEval-only vs MBPP-only vs LeetCode-only vs equal mix) produce significantly different pass@1 on held-out HumanEval and MBPP for DeepSeek-Coder-1.3B-Base?
2. Does cross-benchmark transfer pattern differ by source: does HumanEval-trained model generalize better to MBPP than LeetCode-trained model (or vice versa), measured on existing test sets only?
3. Is there a saturation point within each source where doubling training samples yields diminishing pass@1 gains, identifiable from existing dataset sizes?
4. Does the source mix effect replicate across model sizes (1.3B vs 7B DeepSeek-Coder)?
5. Does deduplication (cosine sim ≥ 0.95 against test benchmarks, validated pipeline from prior runs) disproportionately shrink one source over another, altering the source mix ranking?

### reference_papers
Not provided - will discover in Phase 1

</phase1-input>

---

## Session Insights

### Key Discoveries

- Four ROUTE_TO_0 iterations reveal a clear pattern: attempts 1-3 all failed on *measurement* of training dynamics (reward variance, gradient variance), not on the final benchmark evaluation itself. The fix: measure only what is robust — final pass@1 on held-out benchmarks after SFT.
- Training data *source composition* (which datasets, what proportion) is the most fundamental data-centric question and has never been systematically ablated for current code LLMs on execution-based benchmarks.
- The deduplication pipeline (all-MiniLM-L6-v2 cosine sim > 0.95 vs HumanEval+ and MBPP+) was validated in prior runs — a reusable asset that directly addresses benchmark contamination concerns.
- h-e1 snapshot (PASSED): 1.3B model has significantly higher gradient magnitude on Easy problems than 6.7B (p=6.48e-14, 1.672× ratio) — confirms capability differential is real and reusable as motivation for model-size interaction sub-question.
- DL4C's "Data for Code" track is the perfect fit. A clean source-mix ablation with multiple model sizes and standard execution benchmarks fits workshop scope exactly.
- This direction requires zero new infrastructure beyond what was built in prior runs — SFT loop, deduplication, evaluation harness all reusable.

### Techniques Used

ROUTE_TO_0 Mode — 4th attempt. Failure-informed auto-extraction. Lessons from h-e1 (Phase 4 run 1: EvalPlus binary), h-e1 (Phase 4 run 2: GRPO degenerate rollouts), and h-m1 (Phase 4: gradient clipping eliminates curriculum variance signal) applied to redirect from training-dynamic measurement approaches to final-benchmark-only evaluation.

### Areas for Further Exploration

- Agentic methods for programming tasks (SWE-bench Lite with existing agent scaffolds — SWE-agent, Agentless; binary fix/no-fix signal)
- Program repair using existing bug datasets (Defects4J, BugsInPy) — binary fix/no-fix, no RL required
- Self-paced learning for code SFT (dynamic difficulty adjustment based on rolling model pass rate on training set, using existing binary execution signal)
- Code translation between languages using parallel corpora (existing CodeXGLUE translation pairs)
- Pre-training data mix effects for code (ordering/proportion of pre-training corpora by code type — Python/Java/C++ from The Stack)

---

## Next Steps

Proceed to Phase 1 - Targeted Research (`/phase1-targeted`)

Focus areas for Phase 1:
1. Search for data mixture papers for LLMs (DoReMi, DOREMI, Data Selection for LLMs) — find if code-specific version exists
2. Survey existing SFT for code papers — identify which ones vary training source and report pass@1 (establish baselines)
3. Find dataset contamination/deduplication papers for code benchmarks
4. Check DeepSeek-Coder, CodeLlama, StarCoder papers for their training data compositions and reported HumanEval/MBPP numbers
5. Search for existing training data ablation studies on HumanEval/MBPP (any paper that holds model fixed and varies data)
6. Identify accessible difficulty splits in existing datasets: MBPP Easy/Hard partition, EvalPlus difficulty metadata, LeetCode Easy/Medium/Hard tags — needed for Sub-Q5

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*
