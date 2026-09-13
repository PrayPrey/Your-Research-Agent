# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-21T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Independent Controller Ablation)
- **Gap ID**: gap-2
- **Gap Title**: Variance-Guided vs Random Data Selection for Binary Execution Reward RLEF Has Not Been Directly Compared
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 12
- **Hypothesis ID**: H-VarianceGuidedRLEF-v1

---

## Research Dialogue Context

**Participants**: Dr. Nova (Creative Novelty Explorer), Prof. Vera (Rigorous Validation Architect), Dr. Sage (Research Impact Evaluator), Prof. Pax (Feasibility & Reality Checker), Dr. Ally (Hypothesis Strengthening Champion), Prof. Rex (Hypothesis Stress-Test Master)

**Total Exchanges**: 12

**Convergence Reason**: All 6 convergence criteria met at Exchange 12: SPECIFIC (clear core claim), MECHANISM (gradient variance concentration), PREDICTIONS (P1-P3 with success criteria), NOVELTY (offline binary code RLEF data selection), FEASIBILITY (13h H100, no new infrastructure), OBJECTIONS (measurement noise, confound control, efficiency threshold all addressed).

### Key Insights
1. The core novelty is the **offline vs online distinction** — all prior selection work (VIGOR, Sun et al., Prompt Replay, LZE) requires an active training loop; frozen-model profiling enables pre-training data curation.
2. The **σ = √(k(G-k))/G identity** makes p*(1-p) variance an exact (not heuristic) proxy for GRPO gradient magnitude — this formal connection is the theoretical anchor.
3. **Multi-checkpoint evaluation** (steps 10, 20, 50) is essential to control for HumanEval+ measurement noise (SE ≈ 3.9pp) and enables secondary learning dynamics analysis.
4. The experiment produces **publishable findings under any outcome** — positive, partial (mechanism works but pass@1 doesn't improve), or null.

### Breakthrough Moments
- **Exchange 4** (Prof. Pax): Scoped primary claim to "filtering near-zero-variance problems" rather than "variance predicts full training trajectory" — made hypothesis scientifically precise
- **Exchange 6** (Prof. Rex): Identified HumanEval+ measurement noise issue and proposed multi-checkpoint mitigation — essential for P1 validity
- **Exchange 8** (Prof. Vera): Formalized three-hypothesis structure (H1 effectiveness, H2 mechanism, H3 efficiency) — each independently falsifiable

---

## Final Hypothesis

### Title
Variance-Guided Offline Frozen-Model Profiling for Binary Execution Reward RLEF Data Selection

### Core Claim
Under short RLEF (20–50 GRPO steps, use_vllm=False, G=4, generation_batch_size=4) for code generation, if variance-guided subset selection is applied (top-50 MBPP training problems by frozen-model binary execution reward variance p_i*(1-p_i), computed via k=8 i.i.d. completions from frozen DeepSeek-Coder-7B-Instruct), then HumanEval+ pass@1 improvement per gradient step will exceed random-50 subset RLEF, because variance profiling concentrates GRPO gradient steps on problems with nonzero within-group reward variance while random selection includes ~69% zero-gradient problems that waste training capacity.

**Null Hypothesis (H0):** There is no significant difference in HumanEval+ pass@1 improvement between variance-selected and random-selected RLEF subsets of equal size (N=50) at 50 GRPO steps.

### Mechanism
Per-problem binary reward variance p*(1-p) is a monotone proxy for the GRPO group gradient magnitude σ = √(k(G-k))/G (mathematically exact identity). Frozen-model profiling with k=8 completions approximates p_i for each MBPP problem. Top-50 selection by p_i*(1-p_i) preferentially includes problems where k ∈ {1,2,3} of G=4 GRPO completions succeed — ensuring nonzero gradient contribution. With 69.25% of random GRPO groups producing zero gradient at G=4 (Gradient Starvation paper, arXiv:2605.07689), variance-guided selection eliminates the majority of wasted gradient steps, concentrating gradient signal across all 50 training steps on genuinely learnable problems.

---

## Predictions

### P1 — Primary Effectiveness
**Statement:** Variance-50 achieves ≥ 2 absolute pass@1 points improvement on HumanEval+ at 50 GRPO steps, and this improvement exceeds random-50's improvement by ≥ 1 absolute pass@1 point.

**Test Method:** EvalPlus correctness-based pass@1 on HumanEval+ (164 problems, k=8 generations) at step 50 checkpoint for variance-50 and random-50 conditions.

**Success Criterion:** `variance_50_improvement ≥ 2.0pp AND (variance_50_improvement - random_50_improvement) ≥ 1.0pp`

### P2 — Mechanism Validation
**Statement:** Mean TRL `frac_reward_zero_std` is lower for variance-50 than random-50 at all training checkpoints (steps 10, 20, 50).

**Test Method:** TRL built-in metric logged during GRPO training — zero additional implementation cost.

**Success Criterion:** `mean_frac_zero_std(variance-50) < mean_frac_zero_std(random-50)` at steps 10, 20, and 50.

### P3 — Efficiency Claim (Conditional)
**Statement:** If both variance-50 and full-374 achieve ≥ 2pp HumanEval+ improvement at 50 GRPO steps, variance-50's improvement is ≥ 80% of full-374's improvement using only ~13% of training problems.

**Test Method:** EvalPlus pass@1 at step 50 for variance-50 and full-374 conditions.

**Success Criterion:** `(variance_50_improvement / full_374_improvement) ≥ 0.80`, conditional on both achieving ≥ 2pp. P3 is declared **untestable** (not failed) if the condition is not met.

---

## Novelty

**Key Innovation:** Offline frozen-model variance profiling as a pre-training data selection mechanism for RLEF — "profile once, train anywhere." Distinct from all existing online selection methods.

**What's New:**
1. First application of offline frozen-model variance profiling to RLEF data selection (VIGOR, Sun et al., Prompt Replay, LZE are all online)
2. First characterization of per-problem binary execution reward variance distribution across MBPP for any 7B code LLM
3. First controlled comparison (variance-50 vs random-50 vs full-374) in binary execution reward code generation RLEF

**Closest Prior Work:** Sun et al. 2025 (arXiv:2506.05316, 55 citations) — difficulty-targeted online data selection for GRPO on math reasoning. Key differences: online vs offline, math vs code, scalar vs binary reward.

---

## Experimental Design

| Component | Specification |
|-----------|--------------|
| **Base Model** | DeepSeek-Coder-7B-Instruct (HuggingFace) |
| **Training Dataset** | MBPP training split (374 problems) |
| **Evaluation Benchmark** | HumanEval+ via EvalPlus (164 problems) |
| **Conditions** | variance-50, random-50, full-374 |
| **Training** | TRL GRPO, use_vllm=False, G=4, generation_batch_size=4, 50 steps |
| **Profiling** | k=8 i.i.d. completions per MBPP problem on frozen model, ~19 min |
| **Evaluation Checkpoints** | Steps 10, 20, 50 |
| **Mechanistic Metric** | TRL `frac_reward_zero_std` (built-in, zero extra cost) |
| **Total Compute** | ~13h H100 NVL (all 3 conditions + eval) |

---

## Limitations

- **k=8 profiling noise:** Variance estimates from k=8 samples are noisy at extreme pass rates (p close to 0 or 1). k=16 would reduce noise but doubles profiling compute. k=8 is architecturally justified (aligns with GRPO group size G=4-8).
- **Frozen-model proxy drift:** The frozen-model variance ranking may degrade as the model trains (problems at p≈0.5 may shift to p≈0.8 by step 20). Scoped to SHORT RLEF (20–50 steps) where this effect is minimal.
- **k=8 vs G=4 group-size mismatch:** Profiling uses k=8 completions; GRPO training uses G=4 per group. Ranking stability should be reported as a profiling diagnostic (check whether rankings change between k=4, k=8, k=16).
- **Single-run experiment:** HumanEval+ pass@1 has SE ≈ 3.9pp; single run at step 50 may be noisy. Mitigated by multi-checkpoint evaluation and P2 mechanistic metric as independent evidence.
- **Cross-architecture scope:** Code-LLaMA-7B (SQ4) is out of scope for primary hypothesis; stretch goal only.

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met at Exchange 12 (12 exchanges) |
| **Clarity Verified** | Yes |
| **Remaining Objections** | k=8 vs G=4 mismatch (mitigated by ranking stability diagnostic); Code-LLaMA-7B (deferred stretch goal) |
| **Phase 2B Ready** | YES |
| **Next Phase** | Phase 2B — Research Planning (Roadmap Creation) |

---

*Generated by Phase 2A Self-Contained Tikitaka Loop (Independent Controller Ablation)*
*All 6 personas participated: Dr. Nova (3×), Prof. Vera (2×), Dr. Sage (2×), Prof. Pax (2×), Dr. Ally (2×), Prof. Rex (2×)*
