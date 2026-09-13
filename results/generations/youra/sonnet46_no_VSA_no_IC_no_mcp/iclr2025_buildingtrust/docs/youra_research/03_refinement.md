# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-25T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (independent-controller ablation)
- **Gap ID**: gap-1
- **Gap Title**: No Cross-Benchmark ECE Measurement Under Adversarial Perturbation
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 8

---

## Research Dialogue Context

**Participants**: Dr. Nova (Novelty), Prof. Vera (Falsifiability), Dr. Sage (Significance), Prof. Pax (Feasibility), Dr. Ally (Synthesis), Prof. Rex (Critique)

**Total Exchanges**: 8

**Convergence Reason**: All 4 perspective personas reached STRONG verdict; three testable predictions with quantitative success criteria; mechanism, falsification conditions, and experimental design fully specified across 8 exchanges.

### Key Insights
- The research gap is an *intersection gap*, not a methodology gap — calibration measurement and adversarial NLP evaluation are both mature; their combination for LLMs is the novel contribution
- ΔECE is publishable regardless of direction: positive (overconfidence confirmed), null (models adaptively uncertain), or negative (surprising robustness) — all three outcomes advance knowledge
- Including base vs. RLHF variants adds the alignment × calibration robustness study at marginal compute cost
- Label-preservation stratification converts a methodological concern into an additional analytical contribution

### Breakthrough Moments
- Prof. Pax confirmed technical feasibility: MC logit extraction is standard in lm-evaluation-harness, ~4-8 GPU-hours total — no compute bottleneck
- Prof. Vera operationalized the null: ΔECE ≤ 0 is a compelling null finding, not just experimental failure
- Dr. Nova reframed ΔECE as a "calibration stress test" (analogous to financial stress testing), resolving the MC ECE vs. deployment ECE concern

---

## Final Hypothesis

### Title
Calibration Collapse Under Adversarial Perturbation: Measuring ΔECE Across LLM Families on Existing NLP Benchmarks

### Hypothesis ID
H-DeltaECE-v1 | Confidence: 0.80

### Core Claim
Under adversarial text perturbation on existing NLP benchmarks (AdvGLUE, ANLI, BIG-Bench Hard MC), if open-weight LLMs (Llama-2-7B-base, Llama-2-7B-chat, Llama-2-13B-chat, Mistral-7B-instruct) are evaluated using logit-based 15-bin Expected Calibration Error on multiple-choice task formats, then ΔECE (ECE_adversarial − ECE_clean) will be positive (> 0.05) for ≥60% of model × task combinations, **because adversarial perturbation preserves ground-truth labels while changing surface features in ways that trigger high model confidence on incorrect answers — exposing systematic overconfidence invisible in clean-benchmark evaluation.**

### Null Hypothesis (H₀)
There is no significant increase in ECE between adversarial and clean benchmark splits (ΔECE ≤ 0 for ≥60% of model × task combinations), indicating LLMs appropriately reduce confidence under adversarial inputs.

### Mechanism
1. Adversarial perturbations preserve semantic labels while altering surface features (word substitutions, paraphrases, syntactic changes)
2. Perturbed inputs cause accuracy drops while model confidence remains high — softmax distribution does not flatten appropriately under uncertainty-inducing inputs
3. Gap between high confidence and lower accuracy manifests as elevated ECE: ΔECE > 0

---

## Predictions

| ID | Primary | Statement | Success Criterion |
|----|---------|-----------|-------------------|
| P1 | ✅ | ΔECE > 0.05 for ≥60% of model × task combinations | ≥60% threshold + mean ΔECE > 0 |
| P2 | ❌ | Llama-2-7B-base ΔECE significantly higher than Llama-2-7B-chat | Paired t-test p < 0.05 |
| P3 | ❌ | Per-model mean ΔECE correlates positively with AUROC(entropy) | Spearman r > 0.5 |

---

## Novelty
**What's new**: First systematic measurement of logit-based ECE on adversarial NLP benchmark splits for open-weight LLMs; first ΔECE computation as cross-family calibration stress test signal.

**Differentiation**:
- vs. Guo 2017/Minderer 2021: image domain only; no adversarial NLP; no LLMs
- vs. Kadavath 2022/Xiong 2023: clean benchmarks only; verbal elicitation; no adversarial conditions
- vs. AdvGLUE/ANLI papers: accuracy-only evaluation; calibration not measured — the gap being filled

---

## Experimental Design

**Models**: Llama-2-7B-base, Llama-2-7B-chat, Llama-2-13B-chat, Mistral-7B-instruct (HuggingFace Hub, 4-bit quantized)

**Adversarial datasets**: AdvGLUE (→ clean: GLUE), ANLI R1/R2/R3 (→ clean: MultiNLI), BBH-MC subset (→ clean: BIG-Bench)

**Metric**: ΔECE = ECE(adversarial) − ECE(clean), 15-bin logit-based ECE

**Compute**: ~4-8 GPU-hours on A100; tools: lm-evaluation-harness + robustness-metrics ECE

**Baselines**: Clean-split ECE, temperature-scaled ECE, random classifier ECE

---

## Limitations
- Multiple-choice ECE is a proxy for deployment calibration (real deployment uses free-text generation)
- Benchmark label noise in adversarial examples may partially confound ΔECE — mitigated by label-preservation stratification
- Results scoped to open-weight models with logit access (Llama-2, Mistral); not applicable to GPT-4/Claude without modified protocol
- English-only benchmarks; 4-bit quantization may slightly affect ECE vs. full precision

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Persona Verdicts** | 4× STRONG (Nova, Vera, Sage, Pax) |
| **Discussion Convergence** | 8 exchanges, qualitative convergence |
| **Clarity Verified** | Yes |
| **Remaining Objections** | 3 (all non-blocking, mitigated within experimental design) |
| **Phase 2B Ready** | READY |

---

*Phase: 2A — Dialogue & Hypothesis Generation*
*Generated by: Phase 2A Self-Contained Tikitaka Loop (independent-controller ablation)*
*Next: Phase 2B — Hypothesis Verification Planning*
