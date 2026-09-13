# Phase 2A Discussion Log

**Workflow:** phase2a-dialogue  
**Architecture:** Self-Contained Tikitaka Loop (Independent Controller Ablation — no external orchestrator)  
**Execution Mode:** UNATTENDED  
**Session:** no_MCP / no_IC / no_Reflection  
**Date:** 2026-08-31  

---

## Briefing Context

### Selected Gap
**Gap ID:** gap-1  
**Title:** No Systematic Ablation of Reward Signal Granularity in RLEF for Code LLMs  
**Priority:** HIGH + PRIMARY  
**Selection Rationale:** Highest priority gap; directly blocks the main research question; no published ablation exists; all infrastructure ready.

### Research Question
Does the granularity of execution-based reward signals (binary pass/fail vs. test-coverage-ratio vs. output similarity) differentially affect post-training effectiveness of code LLMs under RLEF, as measured on HumanEval, MBPP, LiveCodeBench, and SWE-bench-lite?

### Papers Available (Claude-authored summaries)
- **P1:** CodeRL (Le et al., 2022) — binary-reward RLEF baseline, actor-critic PPO on CodeT5
- **P2:** RLEF/Gehring et al. (2024) — large-scale RLEF on SWE-bench with binary reward
- **P3:** DAPO (Yu et al., 2025) — GRPO backbone, open-source, addresses reward hacking
- **P4:** LiveCodeBench (Jain et al., 2024) — contamination-resistant generalization benchmark

### Key Context from Phase 1
- All published RLEF papers use binary reward exclusively
- APPS dataset natively supports partial credit (k/n test cases)
- GRPO (via trl library) is the recommended RL algorithm — simpler, more stable than PPO
- Feasibility constraints: existing datasets only (HumanEval, MBPP, APPS, LiveCodeBench, SWE-bench-lite), no new benchmarks
- Key open question: does denser reward = better generalization or reward hacking/overfitting?

### Previous Failure / Routing Context
None — first Phase 2A attempt. No Serena memory files found.

---

## Research Personas

- 🔭 **Dr. Nova** — Creative Novelty Explorer
- 🔬 **Prof. Vera** — Rigorous Validation Architect
- 🎯 **Dr. Sage** — Research Impact Evaluator
- ⚙️ **Prof. Pax** — Feasibility & Reality Checker
- 🛡️ **Dr. Ally** — Hypothesis Strengthening Champion
- 🔍 **Prof. Rex** — Hypothesis Stress-Test Master

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

The gap here is deceptively simple on the surface — "does reward granularity matter in RLEF?" — but it conceals a richer question about the geometry of the reward landscape and how code LLMs navigate it. Let me propose three angles that go beyond the obvious binary-vs-ratio comparison.

First, consider that the APPS dataset's multi-test-case structure (often 10–30 test cases per problem) gives us something valuable: a natural curriculum signal embedded in the ratio reward. A model that passes 3/10 tests gets reward 0.3; next attempt passes 7/10 gets 0.7. This isn't just "denser reward" — it's a *gradient of difficulty* that the model can climb incrementally. Binary reward collapses this gradient entirely. The hypothesis I want to propose is: **ratio reward enables progressive policy refinement that binary reward structurally cannot provide, leading to better convergence and final performance**.

Second, there's a counter-intuitive angle worth raising: partial-credit rewards might *hurt* generalization. RL theory (Ng & Russell, 1999) tells us shaped rewards preserve the optimal policy only under potential-based shaping. Ratio reward is NOT potential-based — it's state-dependent on which specific test cases pass. A model trained with ratio reward might learn to "game" the test suite structure — e.g., learning that test case #1 is always the easy one, test case #5 is always the boundary case. LiveCodeBench's contamination-resistant problems would expose this reward hacking because the test suite structure is entirely novel.

Third, output-similarity reward (edit distance or token overlap to expected output) is conceptually different from both binary and ratio — it provides signal even for wrong answers that are "close". This could be valuable for SWE-bench-lite where patches that fix 90% of a bug are common but receive binary 0 reward. However, similarity-based reward might push models toward superficially similar but semantically incorrect code.

My initial hypothesis: **ratio reward improves in-distribution performance (HumanEval/MBPP) but the overfitting risk to training test suite structure is real and detectable on LiveCodeBench. Output-similarity reward may help SWE-bench-lite specifically.**

**Key Points:**
- Ratio reward creates an implicit curriculum via APPS's multi-test structure — testable prediction
- Reward hacking via test-suite-structure overfitting is the central risk for partial-credit rewards
- Output-similarity reward occupies a different niche (near-miss correction) than ratio reward
- LiveCodeBench is the critical discriminating benchmark — the one that separates real learning from reward hacking

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises the right questions but I want to tighten the experimental logic before we commit to a hypothesis. The "ratio reward as implicit curriculum" framing is attractive, but it conflates two distinct mechanisms that need to be separated for any claim to be falsifiable.

**Mechanism 1: Signal Density.** Ratio reward provides non-zero gradient signal for partially correct solutions. Binary reward gives 0 gradient for anything short of full pass. In GRPO specifically (which we're using per DAPO), this matters: the group-relative reward assignment normalizes rewards within a batch of completions. If all completions get binary 0 (common early in training when problems are hard), GRPO collapses — no gradient. Ratio reward prevents this collapse by providing relative signal even among all-failing completions. This is a **training stability** mechanism, not a curriculum mechanism.

**Mechanism 2: Policy Target Shift.** Ratio reward changes *what the optimal policy is*. Under binary reward, optimal policy = maximize P(all tests pass). Under ratio reward, optimal policy = maximize E[# tests passing / total]. These are related but not identical — a model could learn to reliably pass 8/10 tests (ratio=0.8) without ever achieving 10/10 (binary=1). This could explain why ratio reward improves HumanEval pass@k (via better partial solutions that eventually complete) but might plateau below binary reward's final ceiling.

For the hypothesis to be falsifiable, we need **predictions with specific directions and magnitudes**. I propose these operationalizations:

1. **P1 (in-distribution):** Models trained with ratio reward achieve ≥3pp higher pass@1 on HumanEval than binary-trained models of the same scale, after 1000 GRPO update steps. The 3pp threshold is based on CodeRL's ~5pp improvement over SFT — ratio should be meaningfully better than binary but we need a threshold, not just "better".

2. **P2 (generalization):** The gap between HumanEval performance and LiveCodeBench performance is *larger* for ratio-trained models than binary-trained models. If ratio-trained models improve 8pp on HumanEval but only 2pp on LiveCodeBench (vs. binary-trained: 5pp and 4pp), that's evidence of overfitting to APPS test structure.

3. **P3 (SWE-bench):** Binary reward transfers better to SWE-bench-lite than ratio reward, because SWE-bench uses holistic pytest pass/fail — ratio reward's training signal doesn't align with the test-time reward.

The key tension: Dr. Nova predicts ratio helps in-distribution but hurts generalization. I agree with P2 as stated but want to be precise — the overfitting is to *test case distribution* (APPS's specific difficulty progression), not to problem content. This is a distinguishable claim.

**Key Points:**
- Distinguish signal density mechanism (training stability) from policy target shift (different optimal policy)
- Predictions must have specific directions AND magnitudes to be falsifiable
- P3 (SWE-bench) is counter-intuitive: ratio reward may hurt SWE-bench precisely because SWE-bench uses binary evaluation — training/test reward mismatch
- The 3pp threshold for P1 is a concrete falsification criterion

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Vera's falsifiability precision is exactly right. Let me add the impact dimension: which prediction, if confirmed, would matter most to the DL4C workshop audience and to practitioners in the field?

The workshop explicitly targets post-training and alignment for code, so the audience is practitioners who need to design RLEF pipelines. The practical question is: **should I bother with ratio reward or just use binary?** The answer has real engineering consequences — ratio reward requires running all test cases even for partial credit (more compute per reward signal), while binary reward can short-circuit on first failure.

From an impact perspective, here's how I rank the predictions:

**Highest impact (counter-intuitive finding):** If P2 is confirmed — ratio reward causes *more* overfitting to training benchmarks than binary reward — that directly contradicts the intuition that "more signal = better generalization". This would be the central publishable result. The field assumes partial credit is better (as evidenced by APPS using ratio evaluation) but if ratio training reward leads to LiveCodeBench regression, practitioners should *not* use it without careful calibration. Counter-intuitive, surprising, and actionable.

**Medium impact (expected finding, still valuable):** If P1 is confirmed alone (ratio improves HumanEval without degrading LiveCodeBench), this validates ratio reward as a practical upgrade with no downside. Less surprising but directly actionable — practitioners switch to ratio reward.

**Lower impact but scientifically interesting:** The similarity reward comparison (vs. binary and ratio) on SWE-bench-lite. If output-similarity reward helps SWE-bench specifically (partial patches get credit), that's a niche but useful finding for the repository-level code community.

**Scale interaction (Gap 3, secondary):** If small models (1B) benefit more from ratio reward than large models (13B), that suggests reward granularity is a knob that matters most at low capacity — important for practitioners with compute constraints.

For a DL4C paper, I recommend the hypothesis focus on the **generalization vs. overfitting dynamic** as the primary claim, because:
1. It's testable with existing benchmarks (no new infrastructure)
2. The potential counter-intuitive finding (ratio hurts generalization) is high-impact
3. HumanEval + LiveCodeBench + SWE-bench-lite provides a clean narrative: in-distribution → OOD → transfer

The hypothesis should be centered on **reward granularity × generalization interaction**, with in-distribution performance as a secondary finding.

**Key Points:**
- The counter-intuitive finding (ratio hurts generalization) is highest impact if confirmed
- Focus on generalization vs. overfitting as primary claim — cleanest narrative for DL4C
- Scale interaction (Gap 3) is a secondary but valuable addition if compute permits
- Actionability for practitioners is key: the answer to "should I use ratio reward?" must be clear

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Dr. Sage's impact framing is sound, but I want to pressure-test the feasibility. The research question spans 3 reward variants × 4 benchmarks × (potentially 3 model scales) = a large factorial. Let me assess what's actually runnable within DL4C workshop constraints.

**Compute reality check:**
- GRPO training on APPS (~10k problems, ~10 test cases each) for 1000 steps with a 7B model: ~50-100 GPU-hours on A100s
- Per-reward-variant: 3 variants × 100 GPU-hours = 300 GPU-hours minimum for ONE model scale
- Three model scales: 900 GPU-hours — this is at the edge of what a single-PI lab can run for a workshop paper
- Recommendation: prioritize 1 model scale (7B — most informative midpoint) and 3 reward variants. Scale study as a 2-model (1B vs 7B) secondary experiment if compute allows.

**APPS partial credit reality check:**
APPS problems have variable test case counts (1 to 100+). Ratio reward = k/n where n varies per problem. This creates reward scale heterogeneity — a problem with 2 test cases gives reward in {0, 0.5, 1.0} while one with 20 test cases gives 21 possible values. Need to normalize by problem difficulty or cap at 10 test cases per problem for ratio stability. This is a **critical implementation detail** that affects hypothesis validity.

**LiveCodeBench timing constraint:**
LiveCodeBench uses problems published after a cutoff date. If we train in 2026, we need to use a LiveCodeBench snapshot from after our training data cutoff (pre-2024 APPS). This is feasible but requires careful date filtering to avoid contamination in either direction.

**SWE-bench-lite reality check:**
SWE-bench-lite requires Docker-based isolated execution per test case — slow (~5 min per task evaluation). 300 tasks × 3 reward variants × multiple evaluation checkpoints = significant wall-clock time. I recommend treating SWE-bench-lite as a one-shot final evaluation (not intermediate checkpoint evaluation) to keep compute tractable.

**Feasibility verdict:** The core experiment is feasible with one modification — **drop the scale study from the primary hypothesis and treat it as a secondary/extension experiment**. The primary hypothesis should be:

*"Reward signal granularity (binary vs. ratio vs. similarity) differentially affects RLEF post-training effectiveness and cross-benchmark generalization in 7B-class code LLMs (DeepSeek-Coder-6.7B or StarCoder2-7B), measurable on HumanEval, MBPP, LiveCodeBench, and SWE-bench-lite."*

This is runnable, falsifiable, and DL4C-appropriate.

**Key Points:**
- Feasible with one model scale (7B) as primary; 1B as secondary comparison
- APPS test case count normalization is a critical implementation detail — cap at 10 test cases for ratio stability
- SWE-bench-lite: final evaluation only (not checkpoint), due to Docker overhead
- Drop scale study from primary hypothesis; include as extension if compute allows

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

The discussion is converging well. Let me synthesize the strongest version of the hypothesis that addresses all the concerns raised.

The core claim that survives all four perspectives: **Reward signal granularity in RLEF creates a fundamental trade-off between in-distribution performance and out-of-distribution generalization.** Specifically, ratio reward provides denser gradient signal that improves training efficiency and in-distribution benchmark performance, but this same density enables test-suite-structure overfitting that degrades generalization to contamination-resistant benchmarks.

This is a falsifiable, mechanistically grounded, and practically impactful claim. Let me state it precisely:

**Hypothesis H-RewardGranularity-v1:**
> Under RLEF post-training with GRPO on APPS training data, if reward signal granularity is increased from binary (0/1) to ratio (k/n) to output-similarity (continuous), then:
> - In-distribution performance (HumanEval, MBPP) **increases** with granularity (ratio > binary > similarity or ratio ≈ similarity > binary)
> - Out-of-distribution performance (LiveCodeBench) shows a **non-monotonic** pattern: ratio reward may improve or match binary, but output-similarity degrades
> - Transfer to SWE-bench-lite **favors binary reward** because the evaluation is holistic pass/fail — training with reward that matches evaluation format generalizes better
>
> Because ratio reward changes the optimal policy target (maximize expected coverage rather than maximize P(all-pass)), models trained with ratio reward learn partial-solution strategies that underperform on binary evaluation metrics at test time when the margin between "good partial solution" and "full solution" is important.

**Strengthening the novelty:**
The novelty is not just "we compared reward variants" — it's the specific finding about **training-evaluation reward alignment**. When training reward matches test-time evaluation metric (binary RLEF → binary evaluation), transfer is better. This has a general implication: reward formulation should match the downstream evaluation metric, not just be "denser". This is a principled claim that goes beyond the specific results.

**On Dr. Nova's similarity reward niche:** I agree that output-similarity reward has a specific use case (SWE-bench partial patches). But for the primary hypothesis, I recommend including similarity as the third condition to complete the factorial and to demonstrate the boundary condition where the claim breaks down.

**Key Points:**
- Core claim: reward granularity creates a training-evaluation alignment issue, not just a density issue
- Non-monotonic OOD pattern is the key prediction: ratio may be fine on LiveCodeBench but similarity degrades
- Training-evaluation reward alignment is the mechanistic explanation — generalizable beyond this study
- Similarity reward as boundary condition: shows where denser reward definitively hurts

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally has synthesized a strong hypothesis. Let me stress-test it with the hardest objections.

**Objection 1: Confounded by GRPO's group-relative normalization.**
GRPO assigns rewards relative to the group mean, not absolute. For binary reward, if the entire group gets 0 (all fail), GRPO still produces meaningful gradients via group normalization (reward - mean_reward). This partially solves the sparse reward problem that motivated ratio reward. If GRPO with binary reward already handles sparsity well, ratio reward's signal density advantage may not manifest. The hypothesis assumes binary GRPO suffers from gradient collapse — this must be verified empirically.

*Mitigation:* Include a GRPO gradient norm monitoring experiment. If binary GRPO shows comparable gradient flow to ratio GRPO, the mechanism is wrong even if the performance results hold.

**Objection 2: APPS test case quality is not uniform.**
Some APPS test cases are redundant (same logic, different values). Ratio reward k/n over redundant tests is deceptive — passing 8/10 tests might mean passing the same underlying logic 8 times, not 8 distinct code paths. The hypothesis assumes ratio reward captures "how much of the problem is solved" — this requires non-redundant test cases, which APPS doesn't guarantee.

*Mitigation:* Analyze APPS test case diversity before using ratio reward. Alternatively, use a subset of problems where test cases are verified non-redundant (competitive programming problems with edge-case test suites).

**Objection 3: LiveCodeBench difficulty confound.**
LiveCodeBench is harder than APPS (competitive programming vs. mixed difficulty). If ratio-trained models underperform on LiveCodeBench, it could be because LiveCodeBench is harder, not because of reward hacking. Need to control for difficulty level.

*Mitigation:* Use LiveCodeBench "easy" tier problems. Or compare the *relative* improvement from RLEF (trained vs. SFT baseline) rather than absolute scores — this controls for problem difficulty.

**Objection 4: SWE-bench-lite sample size.**
300 issues, evaluated in docker containers, with high variance per issue. The difference between ratio and binary RLEF on SWE-bench-lite may not be statistically significant with n=300. The hypothesis predicts binary transfers better — this prediction may be unverifiable with the available sample size.

*Mitigation:* Run multiple sampling evaluations (pass@3 rather than pass@1) to increase effective sample size. Use bootstrap confidence intervals. Report effect sizes, not just p-values.

**Overall verdict:** The hypothesis is sound but three implementation details must be resolved before it can be tested:
1. GRPO gradient flow under binary vs. ratio reward (gradient norm monitoring)
2. APPS test case redundancy analysis (or switch to curated subset)
3. LiveCodeBench difficulty control (use relative improvement metric)

**Key Points:**
- GRPO's group normalization may already solve binary reward sparsity — ratio advantage not guaranteed
- APPS test case redundancy undermines ratio reward's information content assumption
- LiveCodeBench difficulty confound requires relative improvement (RLEF gain over SFT) as the metric
- SWE-bench-lite: use pass@3 + bootstrap CIs to handle small sample size variance

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The training-evaluation reward alignment framing is genuinely novel — prior work has studied reward shaping in RL generally but never the specific claim that reward format should match downstream evaluation metric in RLEF for code. The LiveCodeBench generalization test with contamination-resistant problems is the right discriminating experiment. The hypothesis opens a new design principle for RLEF practitioners.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The three predictions (P1: ratio improves HumanEval ≥3pp, P2: ratio widens HumanEval-LiveCodeBench gap, P3: binary transfers better to SWE-bench-lite) are specific, directional, and measurable with existing benchmarks. Prof. Rex's mitigation strategies address the main confounds. The hypothesis is well-operationalized.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** The DL4C audience will find this directly actionable. The answer to "should I use ratio reward?" has a nuanced, evidence-based answer that changes practice. The counter-intuitive prediction (ratio reward may hurt generalization) is the kind of finding that generates discussion and follow-up work. Workshop-appropriate scope with clear path to full paper extension.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** MODERATE
- **Assessment:** Feasible with scoping decisions: one primary model (7B), three reward variants, APPS training with test case cap, LiveCodeBench relative improvement metric, SWE-bench-lite one-shot final evaluation. The compute budget is tight (~300 GPU-hours) but achievable. Prof. Rex's APPS redundancy analysis is additional work but necessary.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on the following hypothesis: Under RLEF post-training with GRPO on the APPS dataset, the granularity of execution-based reward signals (binary pass/fail vs. test-coverage-ratio vs. output-similarity) creates a fundamental trade-off between in-distribution performance and out-of-distribution generalization in 7B-class code LLMs (DeepSeek-Coder-6.7B or StarCoder2-7B).

The mechanistic claim is that **training-evaluation reward alignment** — not just reward density — determines generalization: when training reward format matches test-time evaluation (binary training → binary evaluation), models learn strategies that directly optimize the test metric, while misaligned training rewards (ratio training → binary evaluation) cause models to learn partial-solution strategies that underperform at test time.

Testable predictions: (P1) ratio reward achieves ≥3pp higher HumanEval pass@1 than binary reward; (P2) the gap between HumanEval performance and LiveCodeBench performance is larger for ratio-trained than binary-trained models, measured as the differential RLEF gain (RLEF improvement over SFT baseline on each benchmark); (P3) binary reward shows better or equal transfer to SWE-bench-lite than ratio or similarity reward.

The experimental design is: GRPO post-training on APPS (with test case count capped at 10 for ratio stability), three reward conditions (binary, ratio, similarity), one primary model (DeepSeek-Coder-6.7B), evaluated on HumanEval, MBPP, LiveCodeBench (relative improvement metric), and SWE-bench-lite (pass@3, final evaluation only). Dataset is entirely existing; benchmarks are entirely existing; models are open-weight. Zero new infrastructure required.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- GRPO group normalization may already mitigate binary reward sparsity — ratio advantage may be smaller than expected; needs gradient norm monitoring to verify mechanism
- APPS test case redundancy may invalidate ratio reward's information content assumption — requires test case diversity analysis before finalizing reward computation
- **Mitigation Strategy:** (1) Add gradient norm monitoring as a diagnostic experiment; (2) Pre-screen APPS problems for test case diversity (use problems with ≥5 non-redundant test cases); (3) Use relative improvement (RLEF gain over SFT) as primary metric for cross-benchmark comparison to control for difficulty differences

