# H-M1 Validation Report

**Gate Verdict: FAIL**  
k_BBQ = 3/6 (threshold ≥4)  
p_BBQ = 0.6562 (threshold ≤0.125)  

## Gate Criteria

| Criterion | Value | Threshold | Pass |
|-----------|-------|-----------|------|
| k_BBQ (DPO>SFT pairs) | 3/6 | ≥4 | ✗ |
| p_BBQ (one-sided binomial) | 0.6562 | ≤0.125 | ✗ |

## Per-Benchmark Statistics

| Benchmark | k_positive | mean_delta | std_delta | p_value | Fisher |
|-----------|-----------|------------|-----------|---------|--------|
| BBQ | 3/6 | +0.0050 | 0.0524 | 0.6562 | 0.0091 |
| WinoGender | 4/6 | +0.0150 | 0.0513 | 0.3438 | 0.0856 |
| WinoGrande | 1/6 | -0.0067 | 0.0378 | 0.9844 | 0.0312 |
| TruthfulQA MC2 | 4/6 | +0.0460 | 0.0510 | 0.3438 | 0.8122 |

## Per-Pair Delta Table

| Pair | SFT Model | DPO Model | BBQ Δ | WinoGender Δ | WinoGrande Δ | TruthfulQA Δ |
|------|-----------|-----------|-------|--------------|--------------|--------------|
| P1 | mistralai-Mistral-7B-Instruct-v0.1 | HuggingFaceH4-zephyr-7b-alpha | -0.0500 | +0.1000 | -0.0200 | -0.0096 |
| P2 | teknium-OpenHermes-2.5-Mistral-7B | HuggingFaceH4-zephyr-7b-beta | -0.0600 | -0.0600 | -0.0500 | +0.0223 |
| P3 | allenai-tulu-2-7b | allenai-tulu-2-dpo-7b | +0.0200 | +0.0000 | +0.0000 | +0.0967 |
| P4 | meta-llama-Llama-2-7b-chat-hf | Intel-neural-chat-7b-v3-1 | +0.0500 | +0.0100 | +0.0600 | +0.0970 |
| P5 | openchat-openchat_3.5 | berkeley-nest-Starling-LM-7B-alpha | +0.0000 | +0.0200 | +0.0000 | -0.0097 |
| P6 | mistralai-Mistral-7B-Instruct-v0.3 | Intel-neural-chat-7b-v3-3 | +0.0700 | +0.0200 | -0.0300 | +0.0792 |

## Figures

- `figures/fig1_bbq_winogender_paired_bar.png` — Signed delta bars: BBQ and WinoGender per pair
- `figures/fig2_bbq_scatter.png` — BBQ scatter: DPO vs SFT scores
- `figures/fig3_fisher_criterion.png` — Fisher's criterion all 4 benchmarks
- `figures/fig4_winogender_delta.png` — WinoGender signed delta per pair

## Interpretation

Gate FAILED. k_BBQ=3/6 or p_BBQ=0.6562 did not meet thresholds.
DPO advantage on bias benchmarks is not robustly demonstrated by this paired comparison.
WinoGender k=4/6 (p=0.3438).
