# Figures for H-M1

## Status: PoC Mode - Figures Not Generated

The Phase 4 validation was executed in **PoC mode** (minimal sample size for batch processing). Full visualization generation requires the complete experiment:

### Expected Figures (Full Experiment)

1. **gate_metrics.png** - Bar chart showing entropy reduction % and Fisher increase % vs thresholds
2. **entropy_trajectory.png** - Line plot of entropy over training steps for 9 conditions
3. **fisher_trajectory.png** - Line plot of Fisher trace over training steps
4. **ablation_heatmap.png** - Heatmap showing dedup × filter × mix interaction effects
5. **entropy_vs_fisher.png** - Scatter plot of Fisher info vs Entropy (9 conditions labeled)
6. **perplexity_vs_curation.png** - Supplementary metric

### To Generate Figures

Run full-scale experiment:

```bash
cd /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet45/TEST_data_problems/docs/youra_research/h-m1/code
conda activate youra-h-m1
python run_experiment.py
```

This will:
1. Generate 9 curated C4 subsets (50GB each)
2. Train GPT-2 on each condition (50k steps)
3. Compute gate metrics
4. Generate all 6 figures in this directory

**Estimated Time:** 40-50 hours (sequential) or 5-10 hours (parallel on 9 GPUs)
**Storage Required:** ~545GB

---

**Note:** Code for figure generation is implemented in `code/evaluate.py` (plot_gate_metrics function). PoC results are available in `code/outputs/` but are not visualized due to insufficient sample size.
