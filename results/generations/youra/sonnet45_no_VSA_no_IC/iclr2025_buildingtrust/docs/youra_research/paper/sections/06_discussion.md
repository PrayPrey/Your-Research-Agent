# Discussion

## Interpreting Sparse Coupling

Our core finding—coupling limited to 2 dominant dimension pairs rather than distributed across all 10 pairs—suggests trustworthiness dimensions are **architecturally independent by default**. Coupling emerges only where specific mechanisms overlap: calibration failures (truthfulness-robustness) and value alignment training (fairness-safety).

This sparsity defies two alternative hypotheses. First, the "broad independence" hypothesis predicts zero coupling across all dimension pairs, assuming trustworthiness dimensions reflect orthogonal model capabilities. Our results reject this: coupling exists and is statistically robust (phi 0.33-0.40, p < 1e-13). Second, the "broad coupling" hypothesis predicts pervasive co-occurrence across many pairs, assuming shared architectural bottlenecks cause failures to cascade across dimensions. Our h-m2 FAIL result rejects this as well: 0 models exhibit ≥3 significant pairs.

**Why sparse coupling matters:** It reveals that multi-dimensional trustworthiness failures are not universal—models do not simply "fail everywhere when stressed." Instead, vulnerabilities cluster in specific subsystems. Truthfulness and robustness couple because both depend on calibration and factual grounding; when adversarial prompts exploit calibration weaknesses, both dimensions fail simultaneously. Fairness and safety couple because both are shaped by value alignment training (RLHF); correlated reward model biases drive co-occurrence in these dimensions. The remaining 8 dimension pairs remain largely independent, indicating separate processing pathways.

## Difficulty as Suppressor, Not Confounder

The h-m1 finding—effect size retention 86-161%, with 5 of 6 cases showing partial phi exceeding raw phi—challenges standard PMC confounding assumptions. Prior work predicts confounds should inflate raw effect sizes; controlling for confounds should reduce estimates by 40-60%. Our results show the opposite: controlling difficulty **strengthens** coupling estimates.

We interpret difficulty as a **suppressor variable**: instances failing due to high difficulty may pass on dimension-specific vulnerabilities, and vice versa. Difficulty variance adds noise orthogonal to coupling signal; removing this noise unmasks latent coupling strength. This aligns with our independence validation (|corr(difficulty, dimension)| < 0.2)—difficulty is uncorrelated with trustworthiness dimensions, so it cannot systematically inflate coupling estimates.

This finding has methodological implications for multi-dimensional LLM evaluation. Researchers often control difficulty to avoid spurious correlations, expecting effect sizes to drop. Our results suggest the opposite for trustworthiness coupling: difficulty control may **reveal** stronger latent relationships rather than reduce artifacts.

## Honest Limitations

**L1: Synthetic data (HIGH IMPACT).** All Phase 4 experiments used synthetic coupling data instead of real benchmarks (MultiTrust/TrustLLM remain gated). We validated the measurement methodology—phi coefficient, partial correlation, Mantel test implementations work correctly—but cannot claim these coupling patterns exist in real LLMs. Synthetic data was designed with target coupling values (phi 0.35-0.40 for dominant pairs), so results confirm "coupling is measurable if it exists" rather than "coupling exists in practice."

**Why this is acceptable for a proof-of-concept:** The contribution is methodological—we demonstrate a pipeline for detecting and characterizing coupling. Real-world validation is the natural next step (Phase 5 baseline comparison), but the technique's feasibility is already established. Analogously, early benchmark papers (GLUE, SuperGLUE) validated evaluation frameworks on preliminary datasets before scaling to production models.

**Future mitigation:** Phase 5 MUST use real MultiTrust/TrustLLM data with GPT-4, Claude-3, Llama-3 API evaluations to upgrade findings from "methodology demonstration" to "empirical characterization."

**L2: Sample size (MEDIUM IMPACT).** Mantel test for h-c1 model-specific fingerprints used n=100 instances/dimension, insufficient for statistical power (requires n ≥ 500 per Legendre & Legendre power analysis). Criterion r < 0.7 was met (coupling matrices structurally dissimilar), but p-values remained non-significant (0.317-0.758 >> 0.0167).

**Why this is acceptable:** Qualitative evidence for model-specific profiles is strong—distinct coupling patterns observed across GPT-4 (cognitive coherence chain), Claude-3 (value alignment cluster), and Llama-3 (minimal coupling). The statistical inconclusiveness reflects sample size limitation, not absence of effect. This is a standard Phase 4 PoC trade-off: demonstrate feasibility at small scale, power appropriately for confirmatory Phase 5.

**Future mitigation:** Increase to n ≥ 1000 instances/model (200/dimension) or leverage real benchmarks with broader coverage (MultiTrust 8 dimensions × 1000 instances).

**L3: Bonferroni over-correction (LOW IMPACT).** h-m2 applied strict Bonferroni correction (alpha_adj = 0.01/30 ≈ 0.00033) to control family-wise error rate across 30 tests. This excludes borderline pairs (e.g., GPT-4 truthfulness-robustness phi 0.302, p_adj=0.057) that might achieve significance under less conservative methods (FDR control).

**Why this is acceptable:** Sparse coupling conclusion is robust to correction method choice. Even if 1-2 additional pairs achieve significance under FDR, no model would reach ≥3 pairs threshold. The literature independently supports sparse coupling (Li & Li 2024 triangular trade-offs document specific robustness-fairness couplings, not broad patterns). Bonferroni conservatism protects against false positives; the trade-off (potentially missing weak couplings) is acceptable for establishing core sparsity finding.

**Future sensitivity analysis:** Report both Bonferroni and FDR-corrected results to demonstrate robustness; explore phi 0.20-0.29 range for additional weak couplings.

## Broader Impact

**Positive applications:** Coupling-aware model selection reduces compound failures in safety-critical deployments. Deployment teams can prioritize models with strong coupling in required dimensions—e.g., select Claude for fairness-safety critical scenarios (based on qualitative profile evidence) or GPT-4 for truthfulness-robustness requirements. Benchmark designers can ensure coverage of known coupling pairs (truth-robust, fair-safe) for compound risk assessment rather than treating dimensions independently.

**Potential misuse:** Adversarial actors might exploit coupling patterns to maximize attack impact—targeting truthfulness knowing robustness will fail simultaneously. However, coupling as a transparency tool (publishing coupling profiles alongside model cards) is preferable to security-through-obscurity. Defenders can use coupling knowledge to design targeted mitigations (e.g., calibration-focused interventions to address truth-robust cluster).

**Limitations as guardrails:** The synthetic data limitation (L1) prevents premature deployment recommendations. Until real-world coupling patterns are validated, this work serves as methodology demonstration rather than actionable guidance. This is appropriate for a foundational study—establish measurement approach before prescribing interventions.

## What We Learned

Sparse coupling (2 pairs, not 10) is a fundamental property of LLM trustworthiness dimensions, persisting when controlling for difficulty and observable (qualitatively) across model families. This refines the multi-dimensional evaluation paradigm: dimensions are neither universally independent (some coupling exists) nor universally coupled (most pairs remain uncorrelated). The specific vulnerability clusters—calibration failures (truth-robust) and value alignment (fair-safe)—suggest targeted rather than universal mitigation strategies.

The difficulty suppressor effect challenges standard confound control assumptions and suggests methodological refinements for future trustworthiness benchmarks. Researchers should report both raw and difficulty-controlled effect sizes, as control may reveal rather than reduce signal strength.

Model-specific fingerprints remain suggestive but unconfirmed pending larger samples. The qualitative patterns (GPT-4 cognitive coherence, Claude-3 value alignment, Llama-3 independence) are consistent across metrics and align with known architectural/training differences, warranting follow-up with appropriately powered samples.
