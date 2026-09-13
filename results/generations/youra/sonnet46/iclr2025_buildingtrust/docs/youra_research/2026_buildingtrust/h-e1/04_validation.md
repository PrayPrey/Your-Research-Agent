# H-E1 Validation Report

**Generated:** 2026-03-15 01:28:30 UTC
**Hypothesis:** H-E1 — Alignment-Induced Brier Reliability Overconfidence
**Gate Type:** MUST_WORK

---

## 1. Gate Result

**Gate Verdict:** ✅ PASS
**Passing Method:** BOTH
**Timestamp:** 2026-03-15T01:28:30.013938Z

**Gate Criteria:**
> `delta_rel > 0 AND ci_lower > 0` for PPO or DPO in ≥ 2/3 Pythia model sizes (1.4B, 2.8B, 6.9B)

- PPO sizes passing: ['1.4b', '2.8b']
- DPO sizes passing: ['1.4b', '2.8b', '6.9b']

---

## 2. Per-Model Metrics Table

| Model | N Samples | ECE | Brier REL | Brier RES | Brier UNC | Δ REL | CI Lower | CI Upper |
|-------|-----------|-----|-----------|-----------|-----------|-------|----------|----------|
| pythia-1.4b-base | 28654 | 0.0849 | 0.0190 | 0.0005 | 0.7492 | N/A | N/A | N/A |
| pythia-1.4b-sft | 14042 | 0.1415 | 0.0445 | 0.0005 | 0.7492 | 0.0289 | 0.0269 | 0.0309 |
| pythia-1.4b-dpo | 14042 | 0.2516 | 0.1151 | 0.0008 | 0.7492 | 0.1048 | 0.1009 | 0.1090 |
| pythia-1.4b-ppo | 14042 | 0.1923 | 0.0742 | 0.0002 | 0.7492 | 0.0406 | 0.0345 | 0.0464 |
| pythia-2.8b-base | 14042 | 0.0597 | 0.0093 | 0.0003 | 0.7492 | N/A | N/A | N/A |
| pythia-2.8b-sft | 14042 | 0.0694 | 0.0126 | 0.0004 | 0.7492 | 0.0033 | 0.0021 | 0.0045 |
| pythia-2.8b-dpo | 14042 | 0.1441 | 0.0531 | 0.0007 | 0.7492 | 0.0437 | 0.0407 | 0.0469 |
| pythia-2.8b-ppo | 14042 | 0.1577 | 0.0516 | 0.0004 | 0.7492 | 0.0423 | 0.0388 | 0.0456 |
| pythia-6.9b-base | 14042 | 0.0792 | 0.0128 | 0.0004 | 0.7492 | N/A | N/A | N/A |
| pythia-6.9b-sft | 14042 | 0.0830 | 0.0138 | 0.0006 | 0.7492 | 0.0010 | 0.0001 | 0.0018 |
| pythia-6.9b-dpo | 14042 | 0.1010 | 0.0227 | 0.0009 | 0.7492 | 0.0099 | 0.0090 | 0.0112 |
| pythia-6.9b-ppo | 14042 | 0.0609 | 0.0092 | 0.0007 | 0.7492 | -0.0036 | -0.0053 | -0.0018 |

---

## 3. Key Findings

- **MUST_WORK gate PASSED** via BOTH method.
- Alignment training (PPO/DPO) increases Brier reliability (overconfidence) with statistically significant CI lower > 0 in 5 model-size pairs.
- Existence of alignment-induced overconfidence confirmed.
- Phase 5 skipped (skip_baseline_comparison=true in module.yaml). h-m1 is now READY.

**Positive Δ REL cases (8):**
  - pythia-1.4b-sft (Δ=0.0289)
  - pythia-1.4b-dpo (Δ=0.1048)
  - pythia-1.4b-ppo (Δ=0.0406)
  - pythia-2.8b-sft (Δ=0.0033)
  - pythia-2.8b-dpo (Δ=0.0437)
  - pythia-2.8b-ppo (Δ=0.0423)
  - pythia-6.9b-sft (Δ=0.0010)
  - pythia-6.9b-dpo (Δ=0.0099)

**Negative/Zero Δ REL cases (1):**
  - pythia-6.9b-ppo (Δ=-0.0036)

---

## 4. Failure Analysis

No gate failure. Deviations and limitations:
- **Risk R1 ACTIVATED**: RLHFlow/pythia-* models require HuggingFace authentication and were inaccessible. Used public fallback alignment ladder: lomahony/pythia-*-helpful-sft (SFT), Leogrin/lomahony eleuther-pythia*-hh-dpo (DPO), usvsnsp/lomahony pythia-*-ppo (PPO). All trained on HH (Helpful/Harmless) preference data with Pythia base — comparable training regime.
- Results are specific to Pythia model family and MMLU benchmark.
- 1.4b-base yielded 28654 samples (2 lm-eval runs) vs 14042 for all others — delta_rel computed relative to same base logprobs.

---

## 5. Mechanism Activation Indicators

These indicators assess which alignment-induced logit perturbation mechanism is active (H1: scale distortion, H2: boundary shift, H3: framing susceptibility).

| Indicator | Description | Status |
|-----------|-------------|--------|
| H1: Logit scale inflation | PPO/DPO increase max logit margin | To be tested in H-M2 |
| H2: Decision boundary shift | Rank-order changes in logprobs | To be tested in H-M3 |
| H3: Framing susceptibility | TruthfulQA MC1 distractor interaction | To be tested in H-M3 |
| ECE monotonicity | PPO >= DPO > SFT across sizes | See metrics table |

- ⚠️ ECE monotonicity violated for 1.4b: PPO=0.1923, DPO=0.2516, SFT=0.1415
- ✅ ECE monotonicity holds for 2.8b: PPO=0.1577 >= DPO=0.1441 >= SFT=0.0694
- ⚠️ ECE monotonicity violated for 6.9b: PPO=0.0609, DPO=0.1010, SFT=0.0830

ECE monotonicity holds in 1/3 model sizes.
