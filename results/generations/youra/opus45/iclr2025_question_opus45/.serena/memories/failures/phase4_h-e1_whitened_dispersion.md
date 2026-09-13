# Phase 4 Failure Record: h-e1 Whitened Dispersion

## Hypothesis
**ID:** h-e1  
**Type:** EXISTENCE (Foundation)  
**Gate:** MUST_WORK

**Statement:** Under autoregressive transformer LLMs processing factual QA questions, whitened hidden state dispersion at layers 60-80% depth will show Spearman correlation rho >= 0.5 with semantic entropy, because hidden states encode semantic representations and uncertainty manifests as geometric spread after removing anisotropic artifacts.

## Experiment Results
- **Peak Spearman rho:** 0.188 (layer 29, 91% depth)
- **Threshold:** 0.5
- **Bootstrap 95% CI:** [0.117, 0.248]
- **Samples processed:** 500 questions
- **Runtime:** 1h41m (6065 seconds)

## Gate Outcome
**Result:** FAIL  
**Routing:** Phase 0 (new research direction required)

## Failed Checks
1. No layer achieves rho >= 0.5 (max: 0.188)
2. No contiguous interval >= 6 layers found (0 layers)
3. Peak layer 29 outside target range 19-26 (60-80% depth)

## Root Cause Analysis
1. **Fundamental assumption failure:** Whitened hidden state dispersion does NOT correlate strongly with semantic entropy
2. **Whitening helps but insufficient:** Raw correlation improved from -0.097 to +0.188, but still far below threshold
3. **Peak at wrong depth:** Correlation peaks at 91% depth (near output), not 60-80% as hypothesized
4. **Weak effect size:** Even best layer shows only weak correlation (rho=0.188)

## Lessons Learned
1. ZCA whitening improves correlations but cannot create a relationship that doesn't exist
2. Hidden state geometry may not directly encode uncertainty in the way hypothesized
3. Semantic entropy and hidden state dispersion may measure fundamentally different phenomena
4. Layer selection hypothesis (60-80% depth) was incorrect - if any relationship exists, it's at later layers

## Implications for Future Research
- The commitment layer / crystallization hypothesis built on h-e1 is invalidated
- Need fundamentally different approach to single-pass uncertainty quantification
- Consider alternative geometric measures or different theoretical framework
- May need to explore attention patterns or other architectural features instead

## Metadata
- **Phase:** Phase 4
- **Failure Type:** MUST_WORK_FAIL
- **Terminated At:** 2026-03-26T13:46:00Z
- **Model:** Mistral-7B-v0.1
- **Dataset:** TruthfulQA (817 questions, 500 processed)
