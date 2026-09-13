# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-03-14T23:05:00Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap-1
- **Gap Title**: Lack of Systematic Multi-Family Paired ECE Comparison Across Model Families
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 16

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 16

**Convergence Reason**: Pre-registered mechanistically discriminating framework formalized (H1 scale distortion vs H2 boundary shift vs H3 framing susceptibility) with explicit falsifiable predictions; ATS integrated as diagnostic probe linking logit geometry, Brier decomposition, and alignment-method gradient (PPO >= DPO > SFT) into a coherent testable account.

### Key Insights

1. **The core finding** that RLHF degrades calibration [Xie et al. 2024] needs mechanistic explanation — three competing mechanisms were identified: (H1) monotonic logit scale inflation, (H2) decision-boundary restructuring, and (H3) framing susceptibility.

2. **Alignment-method heterogeneity** across families (SFT-only Mistral/Falcon vs PPO LLaMA-2) is a natural experiment, not a confound — it allows testing whether miscalibration is alignment-method-specific or general.

3. **ATS's hidden-state-based correction** [Xie et al. 2024: ECE reduced 58-82%] implies miscalibration is smooth and representationally encoded, supporting H1 (scale distortion) and providing a diagnostic tool.

4. **The Pythia SFT → DPO → PPO ladder** from Li et al. 2024 is the cleanest existing causal chain — same pretraining, different alignment objectives.

5. **Accuracy confound resolved**: Brier decomposition (reliability vs. resolution) + shared-argmax conditional reliability test separates overconfidence from accuracy collapse.

### Breakthrough Moments

- **Exchange 4** (Prof. Rex): Revealed Mistral/Falcon are SFT-only, not RLHF+PPO — reframed hypothesis from "RLHF-specific" to "alignment-general"
- **Exchange 6** (Dr. Sage): Embraced alignment-method heterogeneity as strengthening feature; proposed stratified result reporting by alignment method
- **Exchange 8** (Dr. Nova): Proposed distractor analysis as mechanistic probe (framing susceptibility) and multi-hypothesis pre-registration design
- **Exchange 13** (Prof. Rex): Demanded shared/changed-prediction split — converted ΔECE scalar into mechanistic discriminating test
- **Exchange 15** (Prof. Vera): Formalized three competing hypotheses (H1/H2/H3) with explicit Achilles' heels

---

## Final Hypothesis

### Title
Alignment-Induced Calibration Distortion: Mechanistic Discrimination Across SFT, DPO, and PPO

### Core Claim (Under-If-Then-Because)
Under conditions where instruction-tuned LLMs (SFT, DPO, PPO variants) are compared to their pretrained base counterparts using forced-choice lm-eval log-probability continuation on MMLU/TruthfulQA/HellaSwag, if alignment training increases with reward-optimization pressure (SFT < DPO < PPO), then the Brier reliability component of Expected Calibration Error will increase monotonically in the same order (PPO >= DPO > SFT), because alignment objectives systematically perturb logit distributions via scale inflation, boundary restructuring, or framing susceptibility — and these three mechanisms are empirically discriminable using pre-specified logit-space tests.

### Null Hypothesis (H0)
There is no significant difference in Brier reliability between instruction-tuned aligned models and their base counterparts, and no consistent gradient ordering PPO >= DPO > SFT in ΔReliability across model families and benchmarks.

### Mechanism
Alignment training pushes logit distributions toward higher-confidence, reward-preferred outputs. The mechanism takes one of three forms:
- **H1 (Scale Distortion)**: Monotonic logit temperature inflation — rank-preserving, Spearman ρ >= 0.9, margin inflation PPO >= DPO > SFT
- **H2 (Boundary Shift)**: Decision-boundary restructuring — argmax changes, ρ < 0.85, reliability degradation concentrated in changed-prediction items
- **H3 (Framing Susceptibility)**: Context-sensitive confidence reallocation — distractors disproportionately repair reliability in PPO vs SFT (Alignment × Distractor × Reliability interaction)

---

## Predictions

### P1 (Primary)
- **Statement**: ΔECE > 0 for PPO and DPO on MMLU; ΔReliability ordered PPO >= DPO > SFT
- **Test**: Paired Wilcoxon + bootstrap CI (n=1000) from lm-eval log-prob outputs
- **Success**: Bootstrap CI lower > 0 for PPO/DPO; gradient sign test holds across Pythia sizes
- **Falsification**: ΔECE ≤ 0 or gradient fails (DPO >= PPO or SFT >= DPO)

### P2 (Secondary — Conditional Reliability)
- **Statement**: Within shared-argmax items, aligned models (esp. PPO) show higher Brier reliability than base
- **Test**: Partition MMLU items by argmax agreement; Mann-Whitney U + Cohen's d
- **Success**: Cohen's d >= 0.1 within shared-argmax subset for PPO
- **Falsification**: Reliability degradation disappears within shared-argmax items

### P3 (Secondary — Mechanism Discrimination)
- **Statement**: If H1: ρ >= 0.9 AND margin inflation PPO >= DPO > SFT
- **Test**: Spearman ρ over 4-option log-prob vectors; pre-softmax margin = top-1 − top-2 logit
- **Success**: ρ >= 0.9 for all methods; margin increases with alignment pressure
- **Falsification**: ρ < 0.8 for PPO (implies H2 boundary shift dominates)

---

## Novelty

**What's New**: First systematic comparison of calibration change across alignment methods (SFT/DPO/PPO) on a shared pretraining lineage (Pythia), with mechanistic decomposition using Brier reliability/resolution and pre-specified H1/H2/H3 discriminating tests.

**How It Differs**:
- Xie 2024: One model family, proposes ATS fix; **our work**: explains WHY ATS works across methods
- Li 2024: RLHF trustworthiness study (no ECE); **our work**: uses their Pythia ladder for ECE/Brier
- Chhikara 2025: Verbal confidence, not softmax ECE; **our work**: log-prob ECE with full decomposition

---

## Experimental Design

**Primary Models**: Pythia 1.4B/2.8B/6.9B (SFT, DPO, PPO variants) — identical pretraining, cleanest causal chain

**Secondary Models**: LLaMA-2-7B/7B-chat, LLaMA-2-13B/13B-chat (RLHF), Mistral-7B/7B-Instruct (SFT-only), Falcon-7B/7B-Instruct (sensitivity check)

**Benchmarks**: MMLU (primary — 57 subjects), TruthfulQA MC1, HellaSwag

**Tooling**: lm-eval v0.4.11 with `--log_samples` for per-item log-prob extraction

**Evaluation**: Brier decomposition (reliability + resolution + uncertainty), logit rank correlation, pre-softmax margins, conditional reliability (shared vs. changed argmax)

---

## Limitations

- Falcon-7B-Instruct has heterogeneous training data vs. base; treated as sensitivity check, not primary causal chain
- Mistral-7B-Instruct is SFT-only; cannot test PPO-specific effects within Mistral family
- Chhikara distractor analysis measures verbal confidence, not softmax ECE; must be clearly labeled
- ATS diagnostic may have distribution overlap with MMLU; use as probe, not primary baseline
- Scale effects (1.4B vs 6.9B) may differ from 7B+ commercial models; cross-scale results need careful framing

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | Yes — all 6 criteria met after 16 exchanges |
| **Clarity Verified** | Yes |
| **All Personas Participated** | Yes — 3 exchanges each |
| **Falsifiers Pre-specified** | Yes — H1/H2/H3 each have explicit disconfirmation criteria |
| **Remaining Objections** | 4 (all mitigated: softmax artifact, stratum size, Falcon data, verbal ECE conflation) |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
